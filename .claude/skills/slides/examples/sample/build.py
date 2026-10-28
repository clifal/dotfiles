#!/usr/bin/env python3
"""見本のデッキ（表紙・目次・章扉 3 枚＋本文 7 枚）。題材と数字は架空。design.md の「ページの形と部品」の例。

  python3 -I ~/.claude/skills/slides/examples/sample/build.py [出力先フォルダ]

出力先を省くと、この build.py と同じフォルダに「<TITLE>.pptx」ができる。新しいデッキはこのファイルを
デッキのフォルダへ写して始める。ページの並びは末尾の FRONT と CHAPTERS で決め、本文中の「P.n」は b.ref() が数える。
"""
import os
import sys
from pathlib import Path

SKILL = Path(os.environ.get("SLIDES_SKILL", Path.home() / ".claude" / "skills" / "slides"))
sys.path.insert(0, str(SKILL / "scripts"))
from house import (  # noqa: E402
    BLUE, BLUE_D, BLUE_T, GRAY, GREEN, LIGHT, ORANGE, P, PALE, TOP, TXT, WHITE, X0, X1,
    Builder, bl, deck_path, pitch,
)

# 題は SKILL.md の 1 で依頼者に確かめたもの。表紙の題とファイル名（<題>.pptx）はここから作る
TITLE = "社内ヘルプデスク 問い合わせ対応の改善計画（サンプル）"
ORG = "サンプル株式会社 様"
BY = "作成：業務改善チーム"
FOOTER = "© 2026 サンプル株式会社"
DOC = "改善計画"   # 出典の行に書く文書の名前


# ==================================================================== 前付け
def toc(b):
    d = b.d
    s = b.slide("改善計画は 3 章からなり、ご判断をお願いする点は 3 章にまとめた")
    cols = [0.55, 2.6, 5.0, X1 - X0 - 8.15]
    rh, top = 0.9, TOP + 0.25
    # 3 章の行に面を敷く（塗りの強調は 1 か所）
    d.panel(s, X0 - 0.05, top + 0.35 + rh * 2, X1 - X0 + 0.1, rh, fill=BLUE_T)
    rows = [[None, P(title, sz=11, b=True), P(lead, sz=10.5), P(b.ref(*pages), sz=10.5)] for _, title, lead, pages in CHAPTERS]
    t = d.table(s, X0, top, cols, ["章", "タイトル", "この章でわかること", "ページ"], rows, [rh] * len(rows),
                head_h=0.3, sz=10.5, x1=X1, anchor="m")
    for (no, *_), ry in zip(CHAPTERS, t["ys"]):
        b.circle(s, X0 + 0.05, ry + (rh - 0.26) / 2, no)
    b.source(s, "網掛けは、ご判断をお願いする点が多い章。数字はすべて見本のための架空の値")


# ==================================================================== 1 現状と課題
def today(b):
    """数字で見る現状: 数字を大きく書いたタイルを 2 行 3 列に並べ、下に流れを矢羽で示す。"""
    d = b.d
    s = b.slide("問い合わせは月 1,200 件あり、半分はパスワードと権限の定型の依頼")
    tiles = [("月 1,200 件", "問い合わせの数（直近 6 か月の平均）"), ("52%", "パスワードの再設定と権限の申請の割合"),
             ("平均 9.5 時間", "受付から一次回答までの時間"), ("4 人", "対応する担当者の数（兼務を含む）"),
             ("3 種類", "受付の窓口（メール、チャット、電話）"), ("18%", "同じ人からの 2 回目以降の問い合わせの割合")]
    gap = 0.15
    tw, th = (X1 - X0 - 2 * gap) / 3, 0.9
    for i, (num, cap) in enumerate(tiles):
        x, y = X0 + (i % 3) * (tw + gap), TOP + (i // 3) * (th + gap)
        d.box(s, x, y, tw, th, fill=BLUE_T)
        pitch(d.text(s, x + 0.15, y + 0.1, tw - 0.3, th - 0.15, [P(num, sz=18, b=True, sa=3), P(cap, sz=9)]), 1.2)
    y = b.head(s, X0, TOP + 2 * (th + gap) + 0.05, X1 - X0, "対応の流れ（担当者が 5 段階で処理する）")
    # 最後の矢羽は切り欠きの分だけ文字の幅が狭いので、2 行に分ける
    steps = ["受付", "振り分け", "一次回答", "調査と対応", "完了の\n連絡"]
    d.chevrons(s, X0, y + 0.05, X1 - X0, 0.48, [P(t, sz=9.5, b=True, c=WHITE, al="c") for t in steps],
               fills=[BLUE_D] * len(steps), depth=0.14, pad_left=0.16)
    pitch(d.text(s, X0, y + 0.64, X1 - X0, 0.8, bl([
        "振り分けは担当者が受付の順に手で行い、窓口ごとに記録の形が違う",
        f"定型の依頼も一次回答までの待ちは他の問い合わせと同じで、長い待ちが再問い合わせを生む（{b.ref(issue)}）",
    ], 10)), 1.35)
    b.source(s, "出典：サンプルの数字（架空）。直近 6 か月（2026/4〜9）の問い合わせ記録から集計したという想定")


def issue(b):
    """事実と帰結の 2 列: 左に事実の表、右に課題のつながり。列の間に三角を 1 つ置く。"""
    d = b.d
    s = b.slide("窓口と記録の形がばらばらで、定型の依頼にも人の手がかかっている")
    lw, rx = 4.45, 5.15
    y = b.head(s, X0, TOP, lw, "記録から見えた事実")
    rows = [("窓口", ["メール、チャット、電話の 3 つがあり、\n受付の記録が別々に残る"]),
            ("振り分け", ["担当者が受付の順に手で振り分け、\n定型の依頼も同じ列に並ぶ"]),
            ("回答", ["回答の文面は担当者ごとに違い、\n過去の回答を探して使い回している"]),
            ("記録", ["対応にかかった時間は記録がなく、\nどの依頼が重いかを比べられない"])]
    rh = 0.9
    d.table(s, X0, y - 0.07, [1.0, lw - 1.0], None, [[P(n, sz=10, b=True), bl(it, 10)] for n, it in rows],
            [rh] * 4, x1=X0 + lw, anchor="m")
    d.triangle(s, X0 + lw + 0.12, y + 1.5, 0.16, 0.34, direction="right", fill=BLUE)
    rw = X1 - rx
    y2 = b.head(s, rx, TOP, rw, "課題どうしのつながり")
    chain = ["窓口と記録の形がばらばら", "定型の依頼も人が振り分けて答える", "一次回答までの待ちが長い",
             "待ちきれずに再び問い合わせる", "担当者の手がさらに埋まる"]
    bw, bh, gap = 2.75, 0.48, 0.24
    for i, txt in enumerate(chain):
        by = y2 + 0.02 + i * (bh + gap)
        key = i == 1
        d.tbox(s, rx, by, bw, bh, P(txt, sz=10, b=key, c=WHITE if key else None, al="c"),
               fill=BLUE_D if key else PALE)
        if i < len(chain) - 1:
            d.triangle(s, rx + bw / 2 - 0.09, by + bh + 0.06, 0.18, 0.12, fill=BLUE)
    ky = y2 + 0.02 + (bh + gap)
    d.line(s, rx + bw + 0.05, ky + bh / 2, rx + bw + 0.25, ky + bh / 2, stroke=TXT, lw=1.0)
    d.text(s, rx + bw + 0.3, ky - 0.4, rw - bw - 0.3, 1.3,
           [P("定型の依頼を\n人の列から外し、\nここで連鎖を断つ", sz=10, b=True, sa=4),
            P(f"手段は {b.ref(classify)}", sz=9)], anchor="m")
    b.source(s, "出典：サンプルの記述（架空）。問い合わせ記録と担当者への聞き取りから整理したという想定")


# ==================================================================== 2 打ち手
def classify(b):
    """構成比: 100% 積み上げの横棒。名前と数を棒の下に直接書き、上に括りを付ける。"""
    d = b.d
    s = b.slide("1,200 件のうち 620 件は自動で返し、380 件は AI の下書きで手間を減らす")
    lw = 6.45
    d.text(s, X0, TOP - 0.02, lw, 0.25, P("月 1,200 件の問い合わせを、減らす手段で分けた内訳（件数）", sz=9.5, b=True))
    segs = [("パスワード", 380, GREEN), ("権限", 240, GREEN), ("使い方", 220, ORANGE), ("不具合", 160, ORANGE),
            ("調達・相談", 120, GRAY), ("その他", 80, GRAY)]
    total = sum(n for _, n, _ in segs)
    unit, by, bh = lw / total, TOP + 0.78, 0.48
    xs, x = [], X0
    for name, n, fill in segs:
        w = n * unit
        d.box(s, x, by, w - 0.02, bh, fill=fill)
        d.text(s, x - 0.1, by + bh + 0.04, w + 0.18, 0.4, [P(name, sz=8.5, b=True, al="c"), P(str(n), sz=9.5, al="c")])
        xs.append((x, w))
        x += w
    for (a, z), label in [((0, 1), "自動で返す：620 件"), ((2, 3), "AI が下書き：380 件")]:
        x0, x1 = xs[a][0], xs[z][0] + xs[z][1] - 0.02
        ly = by - 0.1
        d.line(s, x0, ly, x1, ly, stroke=TXT, lw=0.75)
        d.line(s, x0, ly, x0, ly + 0.07, stroke=TXT, lw=0.75)
        d.line(s, x1, ly, x1, ly + 0.07, stroke=TXT, lw=0.75)
        d.text(s, x0, ly - 0.27, x1 - x0, 0.25, P(label, sz=9.5, b=True, al="c"), anchor="b")
    cols = [1.5, lw - 1.5]
    rows = [("自動で返す", "申請の画面から受け付け、確認と実行まで自動で行う"),
            ("AI が下書き", "AI が過去の回答から下書きを作り、担当者が確かめて送る"),
            ("人が対応", "調達や相談など、判断が要る依頼は今のまま担当者が受ける")]
    cells = [[P(m, sz=9.5, b=True), P(e, sz=9.5)] for m, e in rows]
    d.table(s, X0, by + bh + 0.6, cols, ["手段", "やり方"], cells, [0.4] * len(rows),
            head_h=0.26, sz=9.5, x1=X0 + lw, anchor="m")
    rx = X0 + lw + 0.3
    y = b.head(s, rx, TOP, X1 - rx, "内訳から分かること")
    pitch(d.text(s, rx, y + 0.05, X1 - rx, 3.4, bl([
        "パスワードと権限の\n620 件は手順が決まっており、\n自動で返せる",
        "使い方と不具合の 380 件は\n過去の回答が使え、\nAI の下書きが効く",
        "残る 200 件は判断が要り、\n担当者の時間を\nここに回す",
    ], 10)), 1.3)
    b.source(s, "出典：サンプルの数字（架空）。件数は直近 6 か月の月平均。手段の分け方は担当者と決めた仮のもの")


def roadmap(b):
    """段階の進み方: 矢羽と、段階ごとの列の表。"""
    d = b.d
    s = b.slide("3 か月ごとに区切り、効果を確かめてから次の段階へ広げる")
    lx, lw = X0, 1.3
    cx0 = X0 + lw + 0.05
    cw = (X1 - cx0) / 3
    cy = TOP + 0.1
    stages = [("準備", "2027/1〜3"), ("試行", "2027/4〜6"), ("展開", "2027/7〜")]
    d.chevrons(s, cx0, cy, X1 - cx0, 0.52,
               [P([(a, {}), ("\n" + z, dict(sz=8.5, b=False))], sz=10.5, b=True, c=WHITE) for a, z in stages],
               fills=[BLUE_D] * 3, depth=0.16, pad_left=0.2)
    rows = [
        ("主な成果", [["窓口を 1 つにまとめ、\n記録の形をそろえる"], ["2 つの手段を 1 チームで試し、\n効果と品質を測る"],
                   ["全部門の窓口に広げる"]], 0.62),
        ("次の段階へ\n進む条件", [["新しい窓口の受付が\n全体の 8 割を超えた", "基準値（今の対応時間）を\n測った"],
                         ["一次回答までの時間が\n半分になった", "誤った回答を\n人の確認で止められた"], None], 1.15),
        ("担い手", [["情報システム部"], ["情報システム部と\n試行のチーム"], ["各部門の窓口担当"]], 0.62),
    ]
    y = cy + 0.65
    for ri, (label, cells, rh) in enumerate(rows):
        if ri:
            d.rule(s, y, x0=lx, x1=X1)
        d.text(s, lx, y, lw, rh, P(label, sz=10, b=True), anchor="m")
        for ci, items in enumerate(cells):
            x = cx0 + ci * cw
            if items is None:
                d.text(s, x + 0.05, y, cw - 0.15, rh, P("—", sz=10, al="c"), anchor="m")
            elif len(items) == 1:
                pitch(d.text(s, x + 0.05, y, cw - 0.15, rh, P(items[0], sz=10), anchor="m"), 1.2)
            else:
                pitch(d.text(s, x + 0.05, y, cw - 0.28, rh, bl(items, 9.5), anchor="m"), 1.2)
        y += rh
    b.source(s, f"出典：サンプルの計画（架空）。時期は目安。試行のチームは {b.ref(decide)} で決めていただく")


# ==================================================================== 3 進め方
def gantt(b):
    """日程のガント: 日付から x を計算して棒を置く。区分の名前は、その区分の行をまとめた高さの中央に置く。"""
    d = b.d
    s = b.slide("1〜3 月に窓口をまとめ、4 月から 2 つの手段を 1 チームで試す")
    gx0, tx0, tx1 = X0, X0 + 3.45, X1
    starts = {1: 0, 2: 31, 3: 59, 4: 90, 5: 120, 6: 151}
    days = 181   # 2027/1/1〜6/30

    def xd(m, dd):
        return tx0 + (tx1 - tx0) * (starts[m] + dd - 1) / days
    rows = [("準備", "窓口の一本化と記録の形を決める", (1, 5), (2, 26), GRAY),
            ("自動で返す", "パスワード再設定の自動化を作る", (2, 1), (3, 31), GREEN),
            ("", "1 チームで試す", (4, 1), (5, 31), GREEN),
            ("AI が下書き", "回答の下書きをテストデータで試す", (2, 15), (3, 31), ORANGE),
            ("", "1 チームで試す", (4, 1), (5, 31), ORANGE),
            ("評価", "効果を測り、展開を判断する", (6, 1), (6, 30), GRAY)]
    b.legend(s, X1, TOP - 0.05, [(GREEN, "自動で返す"), (ORANGE, "AI が下書き")])
    hy = TOP + 0.15
    d.text(s, gx0, hy, 1.1, 0.24, P("区分", sz=9.5, b=True), anchor="b")
    d.text(s, gx0 + 1.2, hy, 2.2, 0.24, P("作業", sz=9.5, b=True), anchor="b")
    for m in starts:
        d.text(s, xd(m, 1) + 0.04, hy, 0.9, 0.24, P(f"{m} 月", sz=9.5, b=True), anchor="b")
    y = hy + 0.28
    d.rule(s, y, x0=gx0, x1=tx1, heavy=True)
    rh = 0.32
    for m in list(starts)[1:]:
        d.line(s, xd(m, 1), y, xd(m, 1), y + rh * len(rows), stroke=LIGHT, lw=0.75)
    heads = [i for i, r in enumerate(rows) if r[0]] + [len(rows)]
    for a, z in zip(heads, heads[1:]):
        if a:
            d.rule(s, y + a * rh, x0=gx0, x1=tx1)
        d.text(s, gx0, y + a * rh, 1.15, rh * (z - a), P(rows[a][0], sz=9.5, b=True), anchor="m")
    for i, (_, task, a, z, fill) in enumerate(rows):
        ry = y + i * rh
        d.text(s, gx0 + 1.2, ry, 2.2, rh, P(task, sz=9), anchor="m")
        x_a, x_z = xd(*a), xd(z[0], z[1] + 1)
        d.box(s, x_a, ry + 0.07, x_z - x_a, rh - 0.14, fill=fill)
    ey = y + rh * len(rows) + 0.2
    cols = [1.6, (X1 - X0 - 1.6) / 2, (X1 - X0 - 1.6) / 2]
    erows = [("効果", "一次回答までの時間を基準値と比べる", "回答 1 件にかかる時間を基準値と比べる"),
             ("品質", "誤った実行と取り消しの件数を数える", "誤り、抜け、直した量を採点する"),
             ("必ず満たす条件", "誤った権限の付与が 0 件", "誤った回答を人の確認で止める")]
    d.table(s, X0, ey, cols, ["評価の観点", "自動で返す", "AI が下書き"],
            [[P(a, sz=9.5, b=True), P(x, sz=9.5), P(z, sz=9.5)] for a, x, z in erows], [0.3] * 3,
            head_h=0.25, sz=9.5, x1=X1, anchor="m")
    b.source(s, "出典：サンプルの計画（架空）。灰色の棒は準備と評価。基準値は準備の期間に今の対応で測る")


def org(b):
    """体制: カードと線の組織図。右に連携先を並べる。"""
    d = b.d
    s = b.slide("推進責任者のもと、情報システム部と試行のチームで進める")
    b.card(s, 1.45, 0.9, 3.7, 0.65, "推進責任者（情報システム部長）", "方針と優先度、段階の区切りでの判断",
           fill=BLUE_D, c=WHITE)
    d.line(s, 3.3, 1.55, 3.3, 1.75, stroke=TXT, lw=1.0)
    d.box(s, X0, 1.75, 5.8, 1.55, fill=BLUE_T)
    d.text(s, X0 + 0.15, 1.8, 5.5, 0.5, [P("推進チーム", sz=10, b=True, al="c", sa=1),
                                        P("計画と評価、窓口の一本化、週次の報告", sz=8.5, al="c")])
    b.card(s, 0.55, 2.3, 2.7, 0.85, "ヘルプデスクの担当者", "振り分けの決まり、回答の確認")
    b.card(s, 3.35, 2.3, 2.7, 0.85, "業務改善チーム", "自動化と AI の下書きの仕組みづくり、\n評価の設計")
    for x in (1.8, 4.8):
        d.line(s, x, 3.3, x, 3.5, stroke=TXT, lw=1.0)
    b.card(s, X0, 3.5, 2.8, 0.95, "試行のチーム", "試行の期間に新しい窓口を使い、\n使い勝手の意見を出す", stroke=GRAY)
    b.card(s, 3.4, 3.5, 2.8, 0.95, "各部門の窓口担当（展開から）", "部門からの問い合わせの取りまとめ",
           fill=PALE)
    rx, rw = 6.55, X1 - 6.55
    d.line(s, X0 + 5.8, 2.5, rx, 2.5, stroke=TXT, lw=1.0)
    y = b.head(s, rx, 1.6, rw, "連携先")
    for i, (name, desc) in enumerate([("情報セキュリティの担当", "権限の付与の決まり"),
                                      ("人事の担当", "入社と異動の連絡"), ("購買の担当", "機器とライセンスの調達")]):
        b.card(s, rx, y + i * 0.65, rw, 0.55, name, desc, stroke=GRAY)
    b.source(s, "出典：サンプルの体制（架空）。人数と時間の割き方は、準備の期間に決める")


def decide(b):
    """決めてほしいこと: 番号つきの表。列は「決めていただきたいこと」「推奨と判断の材料」「時期」。"""
    d = b.d
    s = b.slide("12 月末までに、対象の範囲と試行のチームを決めていただきたい")
    cols = [3.1, 4.6, X1 - X0 - 7.7]
    rows = [("最初に対象にする問い合わせ", f"パスワードと権限の 620 件から始める（{b.ref(classify)}）", "12 月末"),
            ("試行のチーム", "問い合わせが多く、窓口の担当がいる\n営業部のチームで試す", "12 月末"),
            ("AI に渡してよい情報の範囲", "個人情報を除いた過去の回答だけを渡し、\nテストデータで先に試す", "1 月末"),
            ("展開へ進む条件", f"一次回答までの時間が半分になり、\n誤った回答を人の確認で止められたら進む（{b.ref(roadmap)}）",
             "3 月末")]
    rh = 0.62
    t = d.table(s, X0, TOP + 0.05, cols, ["決めていただきたいこと", "推奨と判断の材料", "時期"],
                [[None, P(r, sz=10), P(z, sz=10)] for _, r, z in rows], [rh] * len(rows), head_h=0.28, sz=10.5,
                x1=X1, anchor="m")
    for i, ((q, *_), ry) in enumerate(zip(rows, t["ys"])):
        b.circle(s, X0, ry + (rh - 0.26) / 2, i + 1)
        d.text(s, X0 + 0.36, ry, cols[0] - 0.5, rh, P(q, sz=10, b=True), anchor="m")
    b.source(s, "出典：サンプルの論点（架空）。時期は、2027 年 1 月に準備を始められるよう逆算したもの")


# ==================================================================== 並び
FRONT = [toc]   # 表紙のあと、章の前に置く。章扉と同じく本文の枚数に数えない
CHAPTERS = [
    (1, "現状と課題", "問い合わせの量と中身、対応が遅れる理由", [today, issue]),
    (2, "打ち手", "どの問い合わせを、どの手段で減らすか", [classify, roadmap]),
    (3, "進め方", "いつ・どの体制で進め、何を決めていただくか", [gantt, org, decide]),
]


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    b = Builder(footer=FOOTER)
    b.plan(["cover", *FRONT] + [x for no, _, _, pages in CHAPTERS for x in [no, *pages]])
    b.cover(ORG, TITLE, by=BY)
    for f in FRONT:
        f(b)
    for no, title, lead, pages in CHAPTERS:
        b.divider(no, title, lead)
        for f in pages:
            f(b)
    print("saved", b.save(deck_path(folder, TITLE), TITLE))


if __name__ == "__main__":
    main()
