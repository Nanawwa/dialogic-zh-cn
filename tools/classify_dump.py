# -*- coding: utf-8 -*-
"""把 dump 字符串与上游源码反查，精确分类 Dialogic 文案 vs Godot 编辑器噪音。"""
import json
import os
import sys

UP = r"C:/Users/lteyo/WorkBuddy/2026-09-24-23-37-46/dialogic-zh-cn/upstream/dialogic"
DUMP = r"C:/Users/lteyo/Desktop/AIIIT/addons/dialogic_zh_cn/untranslated_dump.txt"
OUT = r"C:/Users/lteyo/WorkBuddy/2026-09-24-23-37-46/dialogic-zh-cn/docs/dump_classified.json"

# 1) 汇编上游源码大字符串（gd + tscn，剥离 .uid 引用行影响不大）
blob_parts = []
for dp, dn, fn in os.walk(UP):
    for f in fn:
        if f.endswith((".gd", ".tscn")):
            try:
                blob_parts.append(open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read())
            except OSError:
                pass
blob = "\n".join(blob_parts)
print("源码汇编大小:", len(blob) // 1024, "KB")

# 2) 读取 dump 唯一字符串
lines = open(DUMP, encoding="utf-8").read().splitlines()[1:]
items = []
seen = set()
for l in lines:
    m = None
    idx = l.find("] ")
    if l.startswith("[") and idx != -1:
        m = (l[1:idx], l[idx + 2:])
    if not m:
        continue
    ctx, text = m
    if text in seen:
        continue
    seen.add(text)
    items.append({"ctx": ctx, "text": text})
print("dump 唯一字符串:", len(items))

# 3) 反查分类
dialogic = []
godot = []
for it in items:
    t = it["text"]
    # 转储里的 ⏎ 是显示替换，还原成 \n 再查（多行字符串在源码中可能以
    # 转义 \n 或真实换行存在）
    probe_real = t.replace(" ⏎ ", "\n").replace("⏎ ", "\n").replace("⏎", "\n")
    probe_esc = probe_real.replace("\n", "\\n").replace("\t", "\\t")
    hit = (probe_real in blob) or (probe_esc in blob)
    # 片段式兜底：取中间一段 30 字符纯文本再查
    if not hit and len(probe_real) > 60:
        mid = probe_real[15:55].strip()
        if mid and mid in blob:
            hit = True
    it["hit"] = hit
    (dialogic if hit else godot).append(it)

print("Dialogic 文案:", len(dialogic), "| Godot 编辑器噪音:", len(godot))
json.dump({"dialogic": dialogic, "godot": godot}, open(OUT, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("分类结果 ->", OUT)
