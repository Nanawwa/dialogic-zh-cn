#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建 zh_CN.po 与 zh_CN.mo

流程
----
1. 读取 POT（条目顺序、译者注释的唯一定义源）。
2. 读取 tools/parts/batch*.po 中的人工译文，做转义修复与校验：
   - batch 中出现的每个 msgid 必须存在于 POT，否则报错退出（防手误漂移）；
   - batch 中重复的 msgid 视为错误（防止批次间覆盖）。
3. 按 POT 顺序合成最终 zh_CN.po：保留 # 注释，填入 msgstr。
4. 编译 zh_CN.mo。
5. 输出翻译覆盖率报告。

未翻译条目**不会**写入 po（回落英文原文），保持文件干净。
"""

import glob
import json
import os
import sys

import polib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POT = os.path.join(ROOT, "addons/dialogic_zh_cn/translations/dialogic.pot")
OUT_PO = os.path.join(ROOT, "addons/dialogic_zh_cn/translations/zh_CN.po")
OUT_MO = os.path.join(ROOT, "addons/dialogic_zh_cn/translations/zh_CN.mo")
REPORT = os.path.join(ROOT, "docs/coverage_report.json")

BS = chr(92)


def fix_escapes(text: str) -> str:
    """批次文件书写时误用了 \\\\"，统一修正为 \\"。"""
    return text.replace(BS + BS + BS + '"', BS + '"')


def load_parts():
    """读取 batch 文件 -> {msgid: msgstr}，带重复检测。"""
    trans = {}
    dups = []
    files = sorted(glob.glob(os.path.join(ROOT, "tools/parts/batch*.po")))
    if not files:
        print("[错误] 未找到 tools/parts/batch*.po", file=sys.stderr)
        sys.exit(1)
    for f in files:
        po = polib.pofile(f, wrapwidth=0)
        for e in po:
            if e.msgid in trans:
                dups.append(e.msgid)
            trans[e.msgid] = fix_escapes(e.msgstr)
    if dups:
        print("[错误] 批次间存在重复 msgid：", file=sys.stderr)
        for d in dups:
            print("  -", repr(d), file=sys.stderr)
        sys.exit(1)
    return trans


def load_translations():
    """读取既有译文。

    zh_CN.po 是唯一权威译文源（标准 gettext 工作流，译者直接改它）。
    tools/parts/batch*.po 仅在首次构建（尚无 zh_CN.po）时作为种子。
    """
    if os.path.isfile(OUT_PO):
        po = polib.pofile(OUT_PO, wrapwidth=0)
        return {e.msgid: e.msgstr for e in po if e.msgstr.strip()}
    return load_parts()


def main():
    pot = polib.pofile(POT, wrapwidth=0)
    trans = load_translations()

    po = polib.POFile(wrapwidth=0)
    po.metadata = {
        "Project-Id-Version": f"Dialogic {pot.metadata.get('Project-Id-Version', '').split(' ', 1)[-1]}",
        "Report-Msgid-Bugs-To": "",
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
        "Language": "zh_CN",
        "Plural-Forms": "nplurals=1; plural=0;",
    }

    unknown = []
    done = 0
    for e in pot:
        zh = trans.pop(e.msgid, None)
        if zh is None:
            continue
        if not zh.strip():
            continue
        entry = polib.POEntry(
            msgid=e.msgid,
            msgstr=zh,
            comment=e.comment,
            occurrences=e.occurrences,
        )
        po.append(entry)
        done += 1

    if trans:
        unknown = list(trans.keys())
        print(f"[错误] {len(unknown)} 条译文在 POT 中不存在（疑似上游文案已变更或 msgid 抄写错误）：",
              file=sys.stderr)
        for u in unknown[:20]:
            print("  -", repr(u), file=sys.stderr)
        sys.exit(1)

    po.save(OUT_PO)
    po.save_as_mofile(OUT_MO)

    total = len(pot)
    cov = {"total": total, "translated": done, "untranslated": total - done,
           "coverage": round(done * 100.0 / total, 1)}
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(cov, f, ensure_ascii=False, indent=2)

    print(f"POT 条目     : {total}")
    print(f"已翻译并写入 : {done}")
    print(f"未翻译(留英文): {total - done}")
    print(f"覆盖率       : {cov['coverage']}%")
    print(f"PO           : {os.path.relpath(OUT_PO, ROOT)}")
    print(f"MO           : {os.path.relpath(OUT_MO, ROOT)}")


if __name__ == "__main__":
    main()
