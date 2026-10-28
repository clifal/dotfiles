# テンプレートと道具の癖

デッキを作るときに見つけた癖。`scripts/house.py` と `scripts/check.py` はここに書いたことを織り込んである。

## テンプレート

- テンプレートは `scripts/make_template.py` が python-pptx の白紙のテンプレートから作る。見本の表紙・章扉・本文を 1 枚ずつ持つが、`Builder` は開くときに外し、レイアウトから新しいページを足す
- python-pptx はレイアウトからページを作るとき、ページ番号の枠を写さない。`Builder.slide()` が本文のレイアウトの枠を写して足す
- タイトル、表紙の題、章扉の題はプレースホルダーに入れる。文字の箱にすると check_deck が「タイトルがプレースホルダーに入っていない」で FAIL にする
- 書体はテーマにも各 run にも BIZ UDGothic と書く。run に書くと、check_deck --house が skin の書体と照らせ、`preview.py` も大きさと色を run から読める
- `house.skin.json` は `measure_deck.py` で測らず、`make_template.py` の値から手で書いた。テンプレートを変えたら、そろえて直す
- 白紙のテンプレートの文書プロパティには、最終更新者の名前が入っている。`make_template.py` は作成者と最終更新者を空にし、出力の PPTX は `Builder.save` がもう一度空にする

## 書体

- BIZ UDGothic が無い Mac では、Keynote が別の書体に置き換えて描き、行の折り返しが変わる。Font Book で「BIZ UDGothic」をダウンロードしてから書き出す
- BIZ UDGothic は英数字も等幅で、Arial よりやや幅を取る。英字の多いセルは、溢れの候補が出なくても PDF で確かめる

## Keynote

- 渡す前の目視は Keynote で書き出した PDF で行う（`render.py`）
- Keynote は書き出したファイルの名前を PDF の文書のタイトルにする。`render.py` は PDF と同じ名前の一時ファイルに書き出してから置き換える
- Keynote は和文の行を高めに描く。詰まった箇条が下の罫線に重なったら、`pitch()` で行の間隔を固定する
- 矢羽（`d.chevrons`）の最後の 1 本は、両端の切り欠きの分だけ文字を置ける幅が狭い。ほかの矢羽に収まる長さの語でも割れるので、2 行に分ける
- 書き出しが AppleEvent の時間切れ（-1712）で止まると、文書が開いたまま残り、次の書き出しも止まる。`osascript -e 'tell application id "com.apple.Keynote" to close every document saving no'` で閉じてからやり直す。`render.py` は書き出しに成功したときだけ PDF を置き換えるので、失敗しても前の PDF は残る
- AppleScript の `open` は文書を開いても返事を返さず時間切れになることがある。`render.py` は `open` コマンドで開かせ、文書が開いたのを確かめてから `front document` を書き出す
- 初めて起動したときは、ダイアログで止まって応答しないことがある。`render.py` が「応答しない」と言ったら、Keynote の画面を見てダイアログを閉じてもらい、やり直す。Keynote の終了はユーザーに任せる
- Keynote が使えないときは、`preview.py` で図形と文字の位置を描き直して見る。書体と行の折り返しは実物と少し違うので、渡す前に Keynote か PowerPoint で必ず見る。macOS の Quick Look（qlmanage）のプレビューは、同じ形と見なした図形の画像を使い回し、ほかの図形を描いてしまうので、目視に使わない

## 検査の既知の WARN

`check.py` は次の 2 つを件数だけ出す。どちらも直さない。

- 「タイトル直下にサブタイトルらしき行」: check_deck は y 1.2〜1.75in の固定の位置で判定する。タイトルの罫が 0.77in にあるこのテンプレートでは、表や図の本文の行を拾う
- 章扉の「版面充填率」: 章扉は題と副題だけのページなので、本文の基準に届かない

`check_deck_layout` の「中身の無い箱」は棒、面、パネルなどの意図した塗り。「箱から溢れている」は英数字も全角 1 字と数える見積もりなので、数字のタイル、英字の多いセルと出典行に出る。出たページは PDF で収まっていることを確かめる。

区分の色はテーマの accent1〜5 で、`house.skin.json` のパレットに入れてある。それ以外の色を使うと、check_deck が「資料に無い色」の WARN を出す。

## 環境

- mise などで Python を上げると、python-pptx と lxml の入っていないバージョンに切り替わることがある。`build.py` が `No module named 'lxml'` や `No module named 'pptx'` で止まったら、「準備」の `pip3 install python-pptx pillow` で入れ直すか、入っているバージョンの Python で動かす

## 文言

- yomiyasu には `export_text.py` で書き出したテキストを渡す。タイトルは「タイトル　」を頭に付けた行にする。「#」の見出しにすると、yomiyasu が見出しとして短い項目名に直そうとするため
- 元の文書の項目名と依頼者の語は、言い換えずにそのまま使う（slide-rules §7.33）
- 文体は依頼者に合わせる。決まりがなければ、スライドの文は常体と体言止めで書く
- 用語は元の文書の表記に合わせる。製品名は製品の公式の表記にする
