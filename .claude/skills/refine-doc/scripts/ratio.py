#!/usr/bin/env python3
"""節ごとの文字数・長さの帯・保持域の一致を機械的に判定する。

usage:
  ratio.py measure <file>
  ratio.py compare <before> <after> [--mode compress|keep]
  ratio.py verify  <before> <after>

モード:
  compress  85〜90% の帯へ収める（既定）
  keep      105% を上限とし、下限は課さない
"""
import re
import sys

FENCE = re.compile(r"^\s*(```+|~~~+)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
INLINE_CODE = re.compile(r"`[^`\n]+`")
NUMBER = re.compile(r"\d+(?:\.\d+)?")
SPACE = re.compile(r"\s+")

# (下限, 上限)。下限 None は「短くなる分は問わない」。
BANDS = {
    "compress": (0.85, 0.90),
    "keep": (None, 1.05),
}


def split_sections(text):
    """(見出し, 本文行, コードブロック行) の節リストへ分割する。"""
    sections = [{"title": "(preamble)", "body": [], "code": []}]
    fence = None
    for line in text.splitlines():
        m = FENCE.match(line)
        if fence:
            sections[-1]["code"].append(line)
            if m and line.strip().startswith(fence):
                fence = None
            continue
        if m:
            fence = m.group(1)
            sections[-1]["code"].append(line)
            continue
        h = HEADING.match(line)
        if h:
            sections.append({"title": h.group(2).strip(), "body": [], "code": []})
        else:
            sections[-1]["body"].append(line)
    return [s for s in sections if s["title"] != "(preamble)" or "".join(s["body"]).strip()]


def countable(body_lines):
    """対象の文字数。インラインコードと空白は数えない。"""
    text = "\n".join(body_lines)
    text = INLINE_CODE.sub("", text)
    return len(SPACE.sub("", text))


def measure(path):
    with open(path, encoding="utf-8") as f:
        sections = split_sections(f.read())
    total = 0
    print(f"{'chars':>7}  {'target':>6}  section")
    for s in sections:
        n = countable(s["body"])
        total += n
        print(f"{n:>7}  {'yes' if n > 500 else '-':>6}  {s['title']}")
    print(f"\ntotal countable chars: {total}")
    print(f"target sections (>500): {sum(1 for s in sections if countable(s['body']) > 500)}")


def index(sections):
    idx = {}
    for i, s in enumerate(sections):
        idx.setdefault(s["title"], []).append((i, s))
    return idx


def band_label(mode):
    lo, hi = BANDS[mode]
    if lo is None:
        return f"<= {hi*100:.0f}%"
    return f"{lo*100:.0f}-{hi*100:.0f}%"


def compare(before_path, after_path, mode="compress"):
    if mode not in BANDS:
        print(f"unknown mode: {mode} (expected: {', '.join(BANDS)})")
        return 2
    lo, hi = BANDS[mode]
    with open(before_path, encoding="utf-8") as f:
        before = split_sections(f.read())
    with open(after_path, encoding="utf-8") as f:
        after = split_sections(f.read())
    after_idx = index(after)
    ng = 0
    print(f"mode: {mode}  band: {band_label(mode)}")
    print(f"{'before':>7} {'after':>7} {'ratio':>7}  {'verdict':<10} section")
    for s in before:
        b = countable(s["body"])
        if b <= 500:
            continue
        hits = after_idx.get(s["title"])
        if not hits:
            print(f"{b:>7} {'-':>7} {'-':>7}  {'MISSING':<10} {s['title']}")
            ng += 1
            continue
        a = countable(hits.pop(0)[1]["body"])
        ratio = a / b
        if ratio > hi:
            verdict = "OVER"
        elif lo is not None and ratio < lo:
            verdict = "UNDER"
        else:
            verdict = "OK"
        if verdict != "OK":
            ng += 1
        print(f"{b:>7} {a:>7} {ratio*100:>6.1f}%  {verdict:<10} {s['title']}")
    print(f"\nsections outside the {band_label(mode)} band: {ng}")
    return 1 if ng else 0


def preserved(text):
    code = []
    fence = None
    for line in text.splitlines():
        m = FENCE.match(line)
        if fence:
            if m and line.strip().startswith(fence):
                fence = None
            else:
                code.append(line.rstrip())
            continue
        if m:
            fence = m.group(1)
    body = "\n".join(
        line for line in text.splitlines() if not FENCE.match(line)
    )
    return {
        "code": code,
        "inline": sorted(INLINE_CODE.findall(body)),
        "numbers": sorted(NUMBER.findall(INLINE_CODE.sub("", body))),
    }


def verify(before_path, after_path):
    with open(before_path, encoding="utf-8") as f:
        b = preserved(f.read())
    with open(after_path, encoding="utf-8") as f:
        a = preserved(f.read())
    ng = 0
    for key in ("code", "inline", "numbers"):
        lost = [x for x in b[key] if a[key].count(x) < b[key].count(x)]
        added = [x for x in a[key] if b[key].count(x) < a[key].count(x)]
        if lost or added:
            ng += 1
            print(f"[{key}] lost={lost} added={added}")
        else:
            print(f"[{key}] identical ({len(b[key])} items)")
    print(f"\npreserve-zone diffs: {ng}")
    return 1 if ng else 0


def parse_mode(args):
    """--mode <name> / --mode=<name> を取り出し、残りの引数を返す。"""
    mode = "compress"
    rest = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--mode":
            if i + 1 >= len(args):
                return None, rest
            mode = args[i + 1]
            i += 2
            continue
        if a.startswith("--mode="):
            mode = a.split("=", 1)[1]
            i += 1
            continue
        rest.append(a)
        i += 1
    return mode, rest


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip())
        return 2
    cmd = sys.argv[1]
    mode, rest = parse_mode(sys.argv[2:])
    if mode is None:
        print(__doc__.strip())
        return 2
    if cmd == "measure" and len(rest) >= 1:
        measure(rest[0])
        return 0
    if cmd == "compare" and len(rest) >= 2:
        return compare(rest[0], rest[1], mode)
    if cmd == "verify" and len(rest) >= 2:
        return verify(rest[0], rest[1])
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main())
