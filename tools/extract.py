#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialogic 2 编辑器 UI 字符串提取器 (POT 生成器)

设计目标
--------
1. **确定性**：同一份上游源码，永远产出同一份 POT（排序稳定、无时间戳）。
   这是"规范同步上游"的前提——重跑提取再 msgmerge，diff 才有意义。
2. **分层**：按 Godot 的实际翻译机制给每条字符串打层，决定它由谁负责生效：
   - L0_AUTO   : 节点属性的 setter 内部会走翻译（已核实 Godot 源码），
                 只需把 .mo 加载进 TranslationServer 即生效，零侵入。
   - L1_HOOK   : setter/ getter 不走翻译（已核实），需由本插件在运行时注入。
   - L2_INSP   : inspector 属性名 / 枚举项，由 EditorInspector 生成，需注入。
3. **不加 msgctxt**：Godot 的自动翻译调用 `TranslationServer.translate(msg)`
   不带 context。一旦写入 msgctxt，L0 条目将永远命中不到。上下文一律
   放进 `#.` 译者注释，兼顾"自动翻译可命中"与"译者看得懂"。

已核实的 Godot 行为（读 godot master 源码，非推测）
--------------------------------------------------
- `Label::set_text`          -> atr()          : 自动翻译
- `Button::set_text`         -> _get_translated_text() : 自动翻译
- `RichTextLabel::set_text`  -> atr()          : 自动翻译
- `LineEdit::set_placeholder`-> atr()          : 自动翻译
- `PopupMenu::set_item_text` -> atr()          : 自动翻译
- `Control::set_tooltip_text`-> 直接赋值        : **不**翻译
- `Control::get_tooltip`     -> 直接返回       : **不**翻译
- `Node.auto_translate_mode` : 默认 INHERIT，根节点默认 ALWAYS
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import OrderedDict

# ---------------------------------------------------------------- 常量定义

# 字段名 -> (层级, 说明)
TSCN_FIELDS = {
    "text": ("L0_AUTO", "节点文本 (Label/Button/RichTextLabel 等 setter 走翻译)"),
    "placeholder_text": ("L0_AUTO", "输入框占位符 (LineEdit::set_placeholder 走翻译)"),
    "tooltip_text": ("L1_HOOK", "悬浮提示 (Control 存取均不走翻译，需注入)"),
    "title": ("L1_HOOK", "窗口/对话框标题 (保守归类，由注入层覆盖)"),
    "dialog_text": ("L1_HOOK", "对话框正文 (保守归类，由注入层覆盖)"),
}

# GDScript 中 'xxx' 与 "xxx" 等价，而 Dialogic 大量使用单引号。
# 只匹配双引号会漏掉整片字符串，故统一用该片段。
_STR = r"(?:\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')"


def unquote(s: str) -> str:
    """去掉成对引号并按 Godot 字符串规则反转义。

    .tscn 与 .gd 中 \\\" 是引号的转义、\\\\n 是换行。若不反转义，
    POT 的 msgid 会带上字面反斜杠，与 Godot 实际展示/翻译时使用的
    字符串不一致，导致整条永远命中不到。
    """
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1]
    return unescape_godot(s)


def unescape_godot(s: str) -> str:
    """Godot 字符串字面量反转义（保守处理常见序列）。"""
    if chr(92) not in s:
        return s
    s = s.replace(chr(92) * 2, chr(0))          # \\ -> 占位
    s = (s.replace(chr(92) + "n", "\n")
          .replace(chr(92) + "t", "\t")
          .replace(chr(92) + '"', '"')
          .replace(chr(92) + "'", "'"))
    return s.replace(chr(0), chr(92))


def _p(pattern: str) -> "re.Pattern":
    return re.compile(pattern.replace("<STR>", _STR))


# .gd 中的赋值/调用模式 -> 层级
GD_PATTERNS = [
    (_p(r"\.text\s*=\s*(<STR>)"), "L0_AUTO", "代码设置节点文本"),
    (_p(r"\bplaceholder_text\s*=\s*(<STR>)"), "L0_AUTO", "代码设置占位符"),
    (_p(r"\btooltip_text\s*=\s*(<STR>)"), "L1_HOOK", "代码设置悬浮提示"),
    (_p(r"\badd_item\(\s*(<STR>)"), "L0_AUTO", "下拉/菜单项"),
    (_p(r"\bset_item_text\([^,]+,\s*(<STR>)"), "L0_AUTO", "菜单项文本"),
    (_p(r"\bset_text\(\s*(<STR>)"), "L0_AUTO", "设置文本"),
    (_p(r"\bdialog_text\s*=\s*(<STR>)"), "L1_HOOK", "对话框正文"),
    (_p(r"\btitle\s*=\s*(<STR>)"), "L1_HOOK", "窗口标题"),
    (_p(r"\badd_header_button\(\s*(<STR>)"), "L0_AUTO", "事件头部按钮"),
    (_p(r"\bset_placeholder\(\s*(<STR>)"), "L0_AUTO", "占位符"),
    (_p(r"\bevent_name\s*=\s*(<STR>)"), "L2_INSP", "事件显示名(event_name)"),
    (_p(r"['\"]text['\"]\s*:\s*(<STR>)"), "L2_INSP", "快捷键说明(shortcut_popup)"),
]

# Dialogic 事件编辑器：add_header_edit / add_body_edit 的第一个参数是字段键，
# extra_info 里的 left_text / right_text / placeholder 是直接显示给用户看的文案。
EVENT_EDIT_RE = _p(r"\b(?:add_header_edit|add_body_edit)\(\s*(<STR>)")
EVENT_INFO_RE = _p(r"['\"](left_text|right_text|placeholder)['\"]\s*:\s*(<STR>)")

# _get_property_list 中的键
PROP_NAME_RE = _p(r"['\"]name['\"]\s*:\s*(<STR>)")
PROP_HINT_RE = _p(r"['\"]hint_string['\"]\s*:\s*(<STR>)")

TSCN_NODE_RE = re.compile(r"^\[node\s+([^\]]*)\]")
TSCN_TYPE_RE = re.compile(r"type=\"([^\"]+)\"")
TSCN_ASSIGN_RE = re.compile(r"^\s*([A-Za-z_][\w/]*)\s*=\s*\"((?:[^\"\\]|\\.)*)\"\s*$")

EN_RE = re.compile(r"[A-Za-z]{2,}")
NON_UI_PREFIX = ("res://", "uid://", "[", "@", "_", "..", "#")

# 明显不是给人看的字符串
NOISE_FULL = re.compile(r"^(?:[\W\d_]+|[A-Za-z_]\w*)$")


def is_translatable(s: str) -> bool:
    """判断字符串是否值得进入 POT。宁可漏，不可噪声。"""
    if not s or len(s.strip()) < 2:
        return False
    if s.startswith(NON_UI_PREFIX):
        return False
    if not EN_RE.search(s):
        return False
    if NOISE_FULL.fullmatch(s):     # 单词标识符 / 纯符号
        return False
    if re.fullmatch(r"[A-Za-z_][\w/:\.\-]*", s):   # 路径式标识符
        return False
    # 排除 Godot 表达式 / BBCode / 格式化串中常见的纯占位
    if re.fullmatch(r"\{[^{}]*\}", s):
        return False
    # 跨行字符串拼接的碎片（如 '"""'+expr+'"""'）不是可翻译文案
    if '"""' in s:
        return False
    return True


def capitalize_godot(name: str) -> str:
    """近似 Godot String::capitalize()：下划线转空格，每个词首字母大写。"""
    out = []
    for word in name.replace("_", " ").split(" "):
        out.append(word[:1].upper() + word[1:] if word else word)
    return " ".join(out).strip()


# ---------------------------------------------------------------- 扫描实现

class Entry:
    __slots__ = ("msgid", "layer", "kind", "locations")

    def __init__(self, msgid: str, layer: str, kind: str):
        self.msgid = msgid
        self.layer = layer
        self.kind = kind
        self.locations: list[str] = []


class Catalog:
    def __init__(self):
        self.entries: "OrderedDict[str, Entry]" = OrderedDict()

    def add(self, msgid: str, layer: str, kind: str, loc: str):
        e = self.entries.get(msgid)
        if e is None:
            e = Entry(msgid, layer, kind)
            self.entries[msgid] = e
        else:
            # 同一 msgid 出现在多层：以"更需人工介入"的层为准，便于追踪
            order = {"L0_AUTO": 0, "L1_HOOK": 1, "L2_INSP": 2}
            if order.get(layer, 0) > order.get(e.layer, 0):
                e.layer, e.kind = layer, kind
        if loc not in e.locations:
            e.locations.append(loc)


def scan_tscn(path: str, rel: str, cat: Catalog):
    cur_type = None
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln, line in enumerate(f, 1):
            if line.startswith("["):
                m = TSCN_NODE_RE.match(line)
                if m:
                    tm = TSCN_TYPE_RE.search(m.group(1))
                    cur_type = tm.group(1) if tm else None
                continue
            m = TSCN_ASSIGN_RE.match(line)
            if not m:
                continue
            field, raw = m.group(1), m.group(2)
            leaf = field.split("/")[-1]
            if leaf not in TSCN_FIELDS:
                continue
            val = unescape_godot(raw)
            if not is_translatable(val):
                continue
            layer, kind = TSCN_FIELDS[leaf]
            node = f"{cur_type or '?'}.{field}"
            cat.add(val, layer, f"{kind} | {node}", f"{rel}:{ln}")


def scan_gd(path: str, rel: str, cat: Catalog):
    try:
        src = open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return
    lines = src.splitlines()

    in_block = False
    for ln, line in enumerate(lines, 1):
        st = line.strip()
        if st.startswith('"""'):
            in_block = not in_block
            continue
        if in_block or st.startswith("#"):
            continue
        for rx, layer, kind in GD_PATTERNS:
            for m in rx.finditer(line):
                val = unquote(m.group(1))
                # 事件显示名与快捷键说明是刻意的人工文案，单词形式
                # （Search/Copy 等）也要收录，不套用通用过滤
                if is_translatable(val) or kind.startswith("事件显示名") or kind.startswith("快捷键"):
                    cat.add(val, layer, kind, f"{rel}:{ln}")

        # 事件编辑器字段键：'character_identifier' -> "Character Identifier"
        for m in EVENT_EDIT_RE.finditer(line):
            key = unquote(m.group(1))
            if not key:
                continue
            if "/" in key:
                for seg in key.split("/"):
                    disp = capitalize_godot(seg.strip())
                    if disp and EN_RE.search(disp):
                        cat.add(disp, "L2_INSP", "事件编辑器字段名", f"{rel}:{ln}")
            else:
                disp = capitalize_godot(key.strip())
                if disp and EN_RE.search(disp):
                    cat.add(disp, "L2_INSP", "事件编辑器字段名", f"{rel}:{ln}")

        # 事件编辑器直接显示的文案：left_text / right_text / placeholder
        for m in EVENT_INFO_RE.finditer(line):
            val = unquote(m.group(2))
            kind = {"left_text": "事件编辑器左标签(left_text)",
                    "right_text": "事件编辑器右标签(right_text)",
                    "placeholder": "事件编辑器占位符(placeholder)"}[m.group(1)]
            # placeholder 常带括号标记如 "(No one)"，保留原样进 PO
            if val and EN_RE.search(val):
                layer = "L0_AUTO" if m.group(1) != "left_text" else "L1_HOOK"
                cat.add(val, layer, kind, f"{rel}:{ln}")

    # _get_property_list：inspector 属性名与枚举项
    #
    # 注意：这里**刻意不套用 is_translatable()**。_get_property_list 里的
    # "name" 一律是属性键，Godot 会 capitalize 后显示在检查器面板上——哪怕它是
    # 单词形式(如 "character" -> "Character")。用通用过滤会把这一大类整片漏掉。
    # 代价是会混入少量技术键名，翻译阶段再按 Godot 官方中文译法对齐即可。
    for ln, line in enumerate(lines, 1):
        for m in PROP_NAME_RE.finditer(line):
            name = unquote(m.group(1))
            if not name or not name.strip():
                continue
            if '"""' in name:      # 文档注释里的拼接示例，非真实属性
                continue
            if name.strip().lower() in {"button", "linebreak", "something"}:
                continue           # event.gd 基类注释区的示例键
            if "/" in name:  # "Section/Sub/Prop" 在面板上分段显示
                for seg in name.split("/"):
                    disp = capitalize_godot(seg.strip())
                    if disp and EN_RE.search(disp):
                        cat.add(disp, "L2_INSP",
                                "inspector 属性名(_get_property_list)", f"{rel}:{ln}")
            else:
                disp = capitalize_godot(name.strip())
                if disp and EN_RE.search(disp):
                    cat.add(disp, "L2_INSP",
                            "inspector 属性名(_get_property_list)", f"{rel}:{ln}")

        for m in PROP_HINT_RE.finditer(line):
            hint = unquote(m.group(1))
            if not hint or not EN_RE.search(hint):
                continue
            # 枚举提示：逗号分隔；每项可能是 "value:显示文本" 形式
            if "," in hint:
                for part in hint.split(","):
                    part = part.strip()
                    if ":" in part:          # 取显示部分，值是内部标识不能翻
                        part = part.split(":", 1)[1].strip()
                    if part and is_translatable(part):
                        cat.add(part, "L2_INSP", "inspector 枚举项(hint_string)",
                                f"{rel}:{ln}")
            elif is_translatable(hint):
                cat.add(hint, "L2_INSP", "inspector 提示串(hint_string)", f"{rel}:{ln}")


def scan_tree(root: str) -> Catalog:
    cat = Catalog()
    for dp, dn, fn in os.walk(root):
        if ".git" in dp or os.sep + "Tests" in dp:
            continue
        dn.sort()
        for f in sorted(fn):
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root).replace("\\", "/")
            if f.endswith(".tscn"):
                scan_tscn(p, rel, cat)
            elif f.endswith(".gd"):
                scan_gd(p, rel, cat)
    return cat


# ---------------------------------------------------------------- POT 输出

def po_escape(s: str) -> str:
    return (s.replace("\\", "\\\\")
             .replace('"', '\\"')
             .replace("\t", "\\t")
             .replace("\r", "\\r")
             .replace("\n", "\\n"))


def write_pot(cat: Catalog, out_path: str, project: str, version: str) -> None:
    lines = [
        "# Dialogic 2 编辑器界面——简体中文翻译模板",
        "#",
        "# 本文件由 tools/extract.py 从上游源码自动生成，请勿手工编辑。",
        "# 上游变更后请重跑 `python tools/sync_upstream.py`，再用 msgmerge 合并。",
        "#",
        "# 层级说明：",
        "#   L0_AUTO  Godot 节点 setter 内部即走翻译，加载 .mo 后自动生效",
        "#   L1_HOOK  setter/getter 不走翻译，由 dialogic_zh_cn 插件运行时注入",
        "#   L2_INSP  inspector 属性名与枚举项，由插件注入层处理",
        "#",
        "# 注意：这里刻意不使用 msgctxt。Godot 的自动翻译调用不带 context，",
        "# 写了 msgctxt 反而会导致 L0 条目永远命中不到。上下文放在 #. 注释里。",
        "#",
        "msgid \"\"",
        "msgstr \"\"",
        f"\"Project-Id-Version: {project} {version}\\n\"",
        "\"Report-Msgid-Bugs-To: \\n\"",
        "\"MIME-Version: 1.0\\n\"",
        "\"Content-Type: text/plain; charset=UTF-8\\n\"",
        "\"Content-Transfer-Encoding: 8bit\\n\"",
        "\"Language: \\n\"",
        "",
    ]
    for msgid, e in cat.entries.items():
        for loc in e.locations:
            lines.append(f"#: {loc}")
        lines.append(f"#. [{e.layer}] {e.kind}")
        lines.append(f"msgid \"{po_escape(msgid)}\"")
        lines.append("msgstr \"\"")
        lines.append("")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def write_report(cat: Catalog, out_path: str) -> dict:
    by_layer = {}
    for e in cat.entries.values():
        by_layer.setdefault(e.layer, []).append(e)
    report = {"total": len(cat.entries), "by_layer": {}}
    for layer in sorted(by_layer):
        items = by_layer[layer]
        files = set()
        for e in items:
            for loc in e.locations:
                files.add(loc.rsplit(":", 1)[0])
        report["by_layer"][layer] = {"count": len(items), "files": len(files)}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report


def main():
    ap = argparse.ArgumentParser(description="从 dialogic 源码提取可翻译字符串并生成 POT")
    ap.add_argument("source", nargs="?", default="upstream/dialogic",
                    help="dialogic 源码根目录")
    ap.add_argument("-o", "--out", default="addons/dialogic_zh_cn/translations/dialogic.pot")
    ap.add_argument("--report", default="docs/extract_report.json")
    ap.add_argument("--json-out", default="docs/entries.json",
                    help="导出条目明细，供翻译流程消费")
    args = ap.parse_args()

    if not os.path.isdir(args.source):
        print(f"[错误] 源码目录不存在: {args.source}", file=sys.stderr)
        print("       先运行 tools/sync_upstream.py 拉取上游源码", file=sys.stderr)
        return 1

    version = ""
    cfg = os.path.join(args.source, "addons", "dialogic", "plugin.cfg")
    if os.path.isfile(cfg):
        m = re.search(r"version=\"([^\"]+)\"", open(cfg, encoding="utf-8").read())
        if m:
            version = m.group(1)

    cat = scan_tree(args.source)
    write_pot(cat, args.out, "Dialogic", version)

    entries = [
        {"msgid": e.msgid, "layer": e.layer, "kind": e.kind, "locations": e.locations}
        for e in cat.entries.values()
    ]
    os.makedirs(os.path.dirname(args.json_out) or ".", exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)

    rep = write_report(cat, args.report)
    print(f"源码      : {args.source}")
    print(f"上游版本  : {version or '(未识别)'}")
    print(f"条目总数  : {rep['total']}")
    for layer, d in rep["by_layer"].items():
        print(f"  {layer:8s}: {d['count']:4d} 条 / 涉及 {d['files']} 个文件")
    print(f"POT       : {args.out}")
    print(f"条目明细  : {args.json_out}")
    print(f"统计报告  : {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
