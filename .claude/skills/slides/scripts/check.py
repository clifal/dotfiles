#!/usr/bin/env python3
"""PPTX を consulting-pptx-skill の 3 つの検査にかけ、既知の WARN は件数だけを出す。

  python3 -I ~/.claude/skills/slides/scripts/check.py <pptx>

check_deck --house（規約）、check_deck --xml-only（PowerPoint が修復を求める不正）、check_deck_layout（溢れと隠れ）。
既知の WARN と「中身の無い箱」が何かは ../quirks.md にある。FAIL があれば終了コード 1。
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # -I でも house を読めるように
from house import CONSULTING, SKIN  # noqa: E402
from pptx import Presentation  # noqa: E402

# (WARN の形, 名前, 章扉のページだけで既知とするか)
KNOWN = [
    (re.compile(r"タイトル直下にサブタイトルらしき行"), "サブタイトル判定の誤検知", False),
    (re.compile(r"p(\d+): 版面充填率"), "章扉の版面充填率", True),
]
# check_deck_layout の溢れの見積もりのうち、章扉の番号（44pt の 2 桁）は house.py の箱で収まる
DIVIDER_NUM = re.compile(r"^p(\d+)\s+\[overflow\] 『\d\d』")


def known_label(line, dividers):
    for rx, label, divider_only in KNOWN:
        m = rx.search(line)
        if m and (not divider_only or int(m.group(1)) in dividers):
            return label
    return None


def run(*args):
    r = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    return (r.stdout + r.stderr).splitlines()


def main():
    pptx = sys.argv[1]
    scripts = CONSULTING / "scripts"
    dividers = {i for i, s in enumerate(Presentation(pptx).slides, 1) if s.slide_layout.name == "章扉"}
    known = {label: 0 for _, label, _ in KNOWN}
    fails = 0
    in_titles = False
    print("== check_deck --house")
    for line in run(scripts / "check_deck.py", pptx, "--house", SKIN):
        if line.startswith("=== タイトル一覧"):
            in_titles = True
        if in_titles:
            print(line)
            in_titles = bool(line.strip())
            continue
        if line.startswith(("WARN", "FAIL")):
            hit = known_label(line, dividers)
            if hit:
                known[hit] += 1
                continue
            fails += line.startswith("FAIL")
            print(line)
        elif re.match(r"\d+ FAIL / \d+ WARN", line):
            print(line, "（うち既知の WARN: " + "、".join(f"{k} {v} 件" for k, v in known.items()) + "）")
    print("== check_deck --xml-only")
    xml = run(scripts / "check_deck.py", pptx, "--xml-only")
    print(xml[-1] if xml else "(出力なし)")
    fails += sum(line.startswith("FAIL") for line in xml)
    print("== check_deck_layout")
    empty = flagged = nums = 0
    for line in run(scripts / "check_deck_layout.py", pptx):
        m = DIVIDER_NUM.match(line)
        if "[empty]" in line:
            empty += 1
        elif m and int(m.group(1)) in dividers:
            nums += 1
        elif line.startswith("p") and "[" in line:
            flagged += 1
            print(line)
    # overflow は英数字も全角 1 字と数える見積もり。出たページは render.py の PDF で必ず見る
    print(f"溢れ・隠れ・はみ出しの候補 {flagged} 件（中身の無い箱 {empty} 件は棒・面・パネル、章扉の番号の見積もり {nums} 件は既知）")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
