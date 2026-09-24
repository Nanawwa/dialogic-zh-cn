#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步上游 dialogic 并更新翻译。

流程
----
1. 下载上游 main 分支源码（tarball，解压覆盖 upstream/dialogic）。
2. 保存上一版条目快照，重跑 extract.py 生成新 POT。
3. 重跑 build_po.py：用既有 zh_CN 译文对新 POT 重新合成 po/mo——
   上游未变更的条目自动保留译文，无需手工 merge。
4. 输出变更报告：新增条目、失效条目、覆盖率变化。

依赖：仅需 Python 3.10+ 标准库与 polib（build_po.py）。
用法：python tools/sync_upstream.py
"""

import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM_DIR = os.path.join(ROOT, "upstream", "dialogic")
TARBALL_URL = "https://codeload.github.com/dialogic-godot/dialogic/tar.gz/refs/heads/main"
ENTRIES = os.path.join(ROOT, "docs", "entries.json")
ENTRIES_PREV = os.path.join(ROOT, "docs", "entries_prev.json")
COVERAGE = os.path.join(ROOT, "docs", "coverage_report.json")

PY = sys.executable


def download() -> None:
    print("[1/4] 下载上游源码 ...")
    fd, path = tempfile.mkstemp(suffix=".tar.gz")
    os.close(fd)
    try:
        urllib.request.urlretrieve(TARBALL_URL, path)
        print(f"      已下载 {os.path.getsize(path) / 1e6:.1f} MB")
        if os.path.isdir(UPSTREAM_DIR):
            shutil.rmtree(UPSTREAM_DIR)
        os.makedirs(os.path.dirname(UPSTREAM_DIR), exist_ok=True)
        with tarfile.open(path) as tf:
            members = [m for m in tf.getmembers() if m.name.count("/") > 0]
            tf.extractall(os.path.dirname(UPSTREAM_DIR), members=members)
        extracted = os.path.join(os.path.dirname(UPSTREAM_DIR), "dialogic-main")
        if os.path.isdir(extracted) and extracted != UPSTREAM_DIR:
            os.rename(extracted, UPSTREAM_DIR)
        print(f"      已解压至 {os.path.relpath(UPSTREAM_DIR, ROOT)}")
    finally:
        os.remove(path)


def snapshot() -> None:
    if os.path.isfile(ENTRIES):
        shutil.copy2(ENTRIES, ENTRIES_PREV)
    else:
        if os.path.isfile(ENTRIES_PREV):
            os.remove(ENTRIES_PREV)


def run(cmd: list) -> None:
    print(f"[cmd] {' '.join(os.path.basename(c) if i == 0 else c for i, c in enumerate(cmd))}")
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(r.returncode)


def diff() -> None:
    print("[4/4] 变更报告")
    cur = {e["msgid"]: e for e in json.load(open(ENTRIES, encoding="utf-8"))}
    added = list(cur.keys())
    removed = []
    cov = None
    if os.path.isfile(ENTRIES_PREV):
        prev = {e["msgid"]: e for e in json.load(open(ENTRIES_PREV, encoding="utf-8"))}
        added = [k for k in cur if k not in prev]
        removed = [k for k in prev if k not in cur]
    if os.path.isfile(COVERAGE):
        cov = json.load(open(COVERAGE, encoding="utf-8"))

    print(f"      条目总数: {len(cur)}")
    if cov:
        print(f"      已翻译: {cov['translated']}  覆盖率: {cov['coverage']}%")
    if added:
        print(f"      新增条目 {len(added)} 条（待翻译）:")
        for k in added[:30]:
            print("        +", repr(k)[:100])
        if len(added) > 30:
            print(f"        ... 其余 {len(added) - 30} 条见 docs/entries.json")
    if removed:
        print(f"      失效条目 {len(removed)} 条（上游已删除/改动，对应译文作废）:")
        for k in removed[:30]:
            print("        -", repr(k)[:100])
    if not added and not removed:
        print("      上游无界面文案变化，译文全部有效。")


def main() -> None:
    download()
    snapshot()
    print("[2/4] 重新生成 POT ...")
    run([PY, "tools/extract.py"])
    print("[3/4] 合成 po 并编译 mo ...")
    run([PY, "tools/build_po.py"])
    diff()


if __name__ == "__main__":
    main()
