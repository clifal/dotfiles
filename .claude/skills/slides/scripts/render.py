#!/usr/bin/env python3
"""PPTX を Keynote で PDF に書き出し、4 ページずつ並べた目視用の画像を作る。

  python3 -I ~/.claude/skills/slides/scripts/render.py <pptx> <画像の出力先フォルダ>

PDF は PPTX と同じ場所に同じ名前で出る。Keynote が応答しないときと、Keynote が使えないときは ../quirks.md を見る。
"""
import glob
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from house import CONSULTING  # noqa: E402

KEYNOTE = "com.apple.Keynote"


def osa(script, timeout):
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=timeout)


def keynote_ready():
    for _ in range(12):
        try:
            r = osa(f'with timeout of 5 seconds\ntell application id "{KEYNOTE}" to get name of every document\nend timeout', 15)
            if r.returncode == 0:
                return True
        except subprocess.TimeoutExpired:
            pass
        time.sleep(1)
    return False


def main():
    pptx, sheets = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    pdf = Path(unicodedata.normalize("NFC", str(pptx.with_suffix(".pdf"))))   # 日本語のファイル名を NFC に
    # 不正な PPTX を開くと修復のダイアログが残るので、開く前に確かめる（slide-rules §8.7）
    xml = subprocess.run([sys.executable, str(CONSULTING / "scripts" / "check_deck.py"), str(pptx), "--xml-only"],
                         capture_output=True, text=True).stdout
    m = re.search(r"(\d+) FAIL /", xml)
    if not m or int(m.group(1)):
        sys.exit("check_deck --xml-only が FAIL。直してから書き出す\n" + xml)
    was_running = subprocess.run(["pgrep", "-x", "Keynote"], capture_output=True).returncode == 0
    subprocess.run(["open", "-g", "-b", KEYNOTE], check=True)
    if not keynote_ready():
        sys.exit("Keynote が応答しない。初回のダイアログが出ていないかを画面で見て、閉じてからやり直す（quirks.md）")
    # AppleScript の open は、文書を開いても返事を返さず時間切れになることがある（quirks.md）。
    # open コマンドで開かせ、文書が開いたのを確かめてから、最前面の文書を書き出す
    osa(f'tell application id "{KEYNOTE}" to close every document saving no', 30)
    subprocess.run(["open", "-g", "-b", KEYNOTE, str(pptx)], check=True)
    for _ in range(60):
        r = osa(f'with timeout of 5 seconds\ntell application id "{KEYNOTE}" to count documents\nend timeout', 15)
        if r.returncode == 0 and r.stdout.strip() not in ("", "0"):
            break
        time.sleep(1)
    else:
        sys.exit("Keynote で PPTX が開かなかった。画面にダイアログが出ていないかを見る（quirks.md）")
    time.sleep(3)
    # 一時フォルダへ書き出させ、成功したときだけ前の PDF と置き換える
    # Keynote は書き出したファイルの名前を PDF の文書のタイトルにするので、PDF と同じ名前で書き出す
    tmp = Path(tempfile.mkdtemp(prefix="slides-")) / pdf.name
    script = f'''with timeout of 120 seconds
tell application id "{KEYNOTE}"
  set d to front document
  export d to POSIX file "{tmp}" as PDF
  close d saving no
  {"" if was_running else "quit"}
end tell
end timeout'''
    r = osa(script, 180)
    if r.returncode != 0 or not tmp.exists():
        sys.exit("Keynote の書き出しに失敗した（前の PDF はそのまま）: " + r.stderr.strip())
    shutil.move(str(tmp), str(pdf))
    sheets.mkdir(parents=True, exist_ok=True)
    for old in glob.glob(str(sheets / "p-*.png")) + glob.glob(str(sheets / "sheet*.png")):
        Path(old).unlink()
    subprocess.run(["pdftoppm", "-png", "-r", "110", str(pdf), str(sheets / "p")], check=True)
    from PIL import Image
    pages = sorted(glob.glob(str(sheets / "p-*.png")))
    ims = [Image.open(f) for f in pages]
    w, h = ims[0].size
    for k in range(0, len(ims), 4):
        sheet = Image.new("RGB", (w * 2 + 10, h * 2 + 10), "white")
        for j, im in enumerate(ims[k:k + 4]):
            sheet.paste(im, ((j % 2) * (w + 10), (j // 2) * (h + 10)))
        out = sheets / f"sheet{k // 4 + 1}.png"
        sheet.save(out)
        print(out, f"（{k + 1}〜{min(k + 4, len(ims))} ページ）")
    print("PDF:", pdf, f"{len(ims)} ページ")


if __name__ == "__main__":
    main()
