#!/usr/bin/env python3
"""2 つの版のスライドの PDF を比べ、文言が変わった行に枠を付けて左右に並べた PDF と、差分の Markdown を作る。

  python3 -I ~/.claude/skills/pptx-slides/scripts/pdfdiff.py <前の版.pdf> <後の版.pdf> <出力フォルダ> [前の版の名前] [後の版の名前]

ページは文言の近さで対応づけるので、ページを足したり消したりしても、後ろのページはずれない。
文言は PDF の文字と位置（pdftotext -bbox-layout）で比べ、書体や行の間隔だけの差は「見た目だけ」に分ける。
出力は <出力フォルダ>/deck-diff.pdf と deck-diff.md。手順と読み方は ../diff.md にある。
"""
import functools
import glob
import html
import pathlib
import re
import subprocess
import sys
import unicodedata

from PIL import Image, ImageChops, ImageDraw, ImageFont

DPI = 120
SCALE = DPI / 72  # PDF の pt を画素に直す
RED, BLUE, GRAY = (215, 25, 32), (0, 90, 200), (150, 150, 150)
FRAME = 2  # 行に付ける枠の線の太さと、行との間の余白（画素）
GAP = 0.3  # 対にしないページ 1 枚ごとの減点。書き直したページは対になり、足した・消したページだけが外れる
BOILER = 0.5  # これより多くのページに出る行（コピーライトなど）は、ページの対応づけに使わない
PAGE = re.compile(r'<page width="[\d.]+" height="([\d.]+)">(.*?)</page>', re.S)
LINE = re.compile(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>', re.S)
WORD = re.compile(r"<word [^>]*>(.*?)</word>", re.S)


@functools.lru_cache(maxsize=None)
def font(size):
    for weight in ("W6", "W3"):
        for f in glob.glob("/System/Library/Fonts/*.ttc"):
            if f"ヒラギノ角ゴシック {weight}" in unicodedata.normalize("NFC", f):
                return ImageFont.truetype(f, size)
    return ImageFont.load_default(size=size)


def render(pdf, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    for png in outdir.glob("p-*.png"):  # 前に作った画像が残ると、ページ数の違う版と取り違える
        png.unlink()
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", str(pdf), str(outdir / "p")], check=True)
    return sorted(outdir.glob("p-*.png"))


def read_pages(pdf):
    """ページごとの (行の一覧, ページの高さ)。行は (文字列, 位置)。"""
    out = subprocess.run(["pdftotext", "-bbox-layout", "-enc", "UTF-8", str(pdf), "-"],
                         check=True, capture_output=True, text=True).stdout
    pages = []
    for height, content in PAGE.findall(out):
        lines = [(" ".join(html.unescape(w) for w in WORD.findall(inner)), tuple(map(float, box)))
                 for *box, inner in LINE.findall(content)]
        pages.append((lines, float(height)))
    return pages


def norm(s):
    return re.sub(r"\s+", "", s)


def is_page_number(text, box, height):
    """上下 10% の余白にある、3 桁までの数字だけの行。"""
    t = norm(text)
    return t.isdigit() and len(t) <= 3 and (box[1] > height * 0.9 or box[3] < height * 0.1)


def body(page):
    """比べる行。空の行とページ番号を除く。"""
    lines, height = page
    return [(t, b) for t, b in lines if norm(t) and not is_page_number(t, b, height)]


def boilerplate(pages):
    """多くのページに出る行。ページを見分ける役に立たないので、対応づけから外す。"""
    count = {}
    for page in pages:
        for t in {norm(t) for t, _ in body(page)}:
            count[t] = count.get(t, 0) + 1
    limit = max(3, BOILER * len(pages))
    return {t for t, c in count.items() if c >= limit}


def shingles(page, boiler):
    text = "".join(norm(t) for t, _ in body(page) if norm(t) not in boiler)
    return {text[k:k + 3] for k in range(len(text) - 2)} or ({text} if text else set())


def similarity(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b) if a and b else 0.0


def align(olds, news):
    """順序を保ち、文言の近さの合計から対にしないページの減点を引いた値が最も大きくなるように、ページを対にする。

    (前のページの番号, 後のページの番号) の並びを返す。消したページは後が None、足したページは前が None。
    大きく書き直したページは関係のないページと同じくらい遠くなるので、近さの閾値では対にするかを決めない。
    """
    n, m = len(olds), len(news)
    score = [[-GAP * (i + j) for j in range(m + 1)] for i in range(n + 1)]
    move = [["ins" if i == 0 else "del" for j in range(m + 1)] for i in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            score[i][j], move[i][j] = max(
                (score[i - 1][j - 1] + similarity(olds[i - 1], news[j - 1]), "match"),
                (score[i - 1][j] - GAP, "del"), (score[i][j - 1] - GAP, "ins"), key=lambda o: o[0])
    pairs, i, j = [], n, m
    while i or j:
        if move[i][j] == "match":
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif move[i][j] == "del":
            pairs.append((i - 1, None))
            i -= 1
        else:
            pairs.append((None, j - 1))
            j -= 1
    return pairs[::-1]


def only_in(lines, other_lines):
    """相手のページのどこにもない行。改行の位置だけが変わった行は、相手の文字列の一部になるので拾わない。"""
    other = "".join(norm(t) for t, _ in other_lines)
    return [(t, b) for t, b in lines if norm(t) not in other]


def mask_page_numbers(img, page):
    lines, height = page
    d = ImageDraw.Draw(img)
    for t, (x0, y0, x1, y1) in lines:
        if is_page_number(t, (x0, y0, x1, y1), height):
            d.rectangle((x0 * SCALE - 4, y0 * SCALE - 4, x1 * SCALE + 4, y1 * SCALE + 4), fill="white")
    return img


def looks_changed(a, b, page_a, page_b):
    a, b = mask_page_numbers(a.copy(), page_a), mask_page_numbers(b.copy(), page_b)
    if a.size != b.size:
        b = b.resize(a.size)
    return ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 40 else 0).getbbox() is not None


def mark(img, lines, color):
    img = img.copy()
    d = ImageDraw.Draw(img)
    for _, (x0, y0, x1, y1) in lines:
        d.rectangle((x0 * SCALE - FRAME, y0 * SCALE - FRAME, x1 * SCALE + FRAME, y1 * SCALE + FRAME),
                    outline=color, width=FRAME)
    return img


def absent(size):
    img = Image.new("RGB", size, (240, 240, 240))
    ImageDraw.Draw(img).text((size[0] // 2, size[1] // 2), "（この版にはないページ）", fill=GRAY, font=font(32), anchor="mm")
    return img


def label(i, j):
    if j is None:
        return f"前 P.{i + 1}"
    if i is None or i == j:
        return f"P.{j + 1}"
    return f"P.{j + 1}（前 P.{i + 1}）"


def side_by_side(title, old, new, gone, added, names):
    if old is None:
        old = absent(new.size)
    if new is None:
        new = absent(old.size)
    if new.size != old.size:
        new = new.resize(old.size)
    f = font(24)
    gap, head = 24, 56
    w, h = old.size
    canvas = Image.new("RGB", (w * 2 + gap * 3, h + head + gap), "white")
    d = ImageDraw.Draw(canvas)
    d.text((gap, 14), f"{title}　変更前：{names[0]}（赤：消した・変えた行 {len(gone)}）", fill=RED, font=f)
    d.text((w + gap * 2, 14), f"変更後：{names[1]}（青：足した・変えた行 {len(added)}）", fill=BLUE, font=f)
    for x, img in ((gap, mark(old, gone, RED)), (w + gap * 2, mark(new, added, BLUE))):
        canvas.paste(img, (x, head))
        d.rectangle((x - 1, head - 1, x + w, head + h), outline=GRAY)
    return canvas


def cover(size, names, groups, shifted):
    rows = [("スライドの PDF の差分", 44, "black", 80), (f"変更前：{names[0]}　→　変更後：{names[1]}", 28, "black", 80),
            ("", 20, "black", 80),
            ("赤の枠：変更前にだけある行（消した・変えた）　青の枠：変更後にだけある行（足した・変えた）", 24, "black", 80),
            ("改行の位置だけが変わった行と、書体や行の間隔だけの差には枠を付けない", 24, GRAY, 80)]
    if shifted:
        rows.append(("ページ番号は変更後の版のもの。消したページだけ、変更前の番号（前 P.n）で示す", 24, GRAY, 80))
    rows.append(("", 20, "black", 80))
    for name, items in groups:
        rows.append((f"{name}（{len(items)} ページ）", 28, "black", 80))
        items = items or ["なし"]
        for k in range(0, len(items), 16):  # ページ番号の途中で折り返さない
            rows.append(("、".join(items[k:k + 16]), 24, "black", 110))
    height = 60 + sum(sz + 24 for _, sz, _, _ in rows) + 40
    page = Image.new("RGB", (size[0], max(size[1], height)), "white")
    d = ImageDraw.Draw(page)
    y = 60
    for text, sz, color, x in rows:
        if text:
            d.text((x, y), text, fill=color, font=font(sz))
        y += sz + 24
    return page


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    old_pdf, new_pdf, out = (pathlib.Path(a) for a in sys.argv[1:4])
    names = (sys.argv[4] if len(sys.argv) > 4 else old_pdf.name, sys.argv[5] if len(sys.argv) > 5 else new_pdf.name)
    old_imgs, new_imgs = render(old_pdf, out / "old"), render(new_pdf, out / "new")
    old_pages, new_pages = read_pages(old_pdf), read_pages(new_pdf)
    if (len(old_imgs), len(new_imgs)) != (len(old_pages), len(new_pages)):
        sys.exit("ページの画像と文字のページ数が合わない。PDF が壊れていないか確かめる")
    boiler = boilerplate(old_pages + new_pages)
    pairs = align([shingles(p, boiler) for p in old_pages], [shingles(p, boiler) for p in new_pages])

    groups = {"wording": [], "looks": [], "same": [], "added": [], "removed": []}
    sheets, details = [], []
    for i, j in pairs:
        a = Image.open(old_imgs[i]).convert("RGB") if i is not None else None
        b = Image.open(new_imgs[j]).convert("RGB") if j is not None else None
        gone = body(old_pages[i]) if i is not None else []
        added = body(new_pages[j]) if j is not None else []
        if i is None or j is None:
            kind, title = ("added", f"{label(i, j)}（足したページ）") if i is None else ("removed", f"{label(i, j)}（消したページ）")
        else:
            gone, added = only_in(gone, added), only_in(added, gone)
            kind = "wording" if gone or added else "looks" if looks_changed(a, b, old_pages[i], new_pages[j]) else "same"
            title = label(i, j)
        groups[kind].append(label(i, j) if kind == "removed" else f"P.{j + 1}")
        if kind in ("wording", "added", "removed"):
            sheets.append(side_by_side(title, a, b, gone, added, names))
            details.append((title, gone, added))

    shifted = any(i != j for i, j in pairs)
    titled = [("文言が変わったページ", groups["wording"]), ("見た目だけ変わったページ（書体や行の間隔）", groups["looks"]),
              ("変わっていないページ", groups["same"])]
    titled += [(n, groups[k]) for n, k in (("足したページ", "added"), ("消したページ", "removed")) if groups[k]]
    first = cover(sheets[0].size if sheets else (2400, 760), names, titled, shifted)
    first.save(out / "deck-diff.pdf", save_all=True, append_images=sheets, resolution=DPI)

    md = [f"# スライドの PDF の差分（{names[0]} → {names[1]}）", ""]
    md += [f"- {n}（{len(p)} ページ）: {'、'.join(p) or 'なし'}" for n, p in titled]
    md += ["", "`-` は変更前にだけある行、`+` は変更後にだけある行。改行の位置だけが変わった行は出さない。"]
    if shifted:
        md += ["ページ番号は変更後の版のもの。消したページだけ、変更前の番号（前 P.n）で示す。"]
    md += [""]
    for title, gone, added in details:
        md += [f"## {title}", "", "```diff", *(f"- {t}" for t, _ in gone), *(f"+ {t}" for t, _ in added), "```", ""]
    (out / "deck-diff.md").write_text("\n".join(md), encoding="utf-8")
    print(", ".join(f"{k} {len(v)}" for k, v in groups.items()), "->", out / "deck-diff.pdf")


if __name__ == "__main__":
    main()
