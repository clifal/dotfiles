---
name: skill-install
description: skill やプラグインを、作業用ディレクトリで SkillSpector の検査に通してから導入する。
disable-model-invocation: true
---

# skill-install

起動: `/skill-install <配布元> [名前]`

配布元は次のどちらか。

- `<プラグイン>@<マーケットプレイス>`
- GitHub の `owner/repo` か git の URL。中身がマーケットプレイスならプラグインを、skill ならその skill を入れる

配布元を作業用ディレクトリ `~/.cache/skill-guard/stage/<名前>-<日時>/` へ取り、そこで検査した中身を入れる。検査したものと入ったものが同じであることを、最後に照合して確かめる。

検査と判定は `~/.claude/skill-guard/skill-guard.sh`（以下 `guard`）が受け持つ。引数なしで実行すると使い方が出る。Colima は `$HOME` しかコンテナに見せないので、作業用ディレクトリは `$HOME` 配下に置く。

## 1. 中身を取る

### プラグインを取る

1. マーケットプレイスが登録済みかを `claude plugin marketplace list --json` で確かめる
   - 登録済み: `claude plugin marketplace update <マーケットプレイス>` で最新にする。カタログは `~/.claude/plugins/known_marketplaces.json` の `installLocation`
   - 未登録: 利用者に配布元を確かめ、`git clone --depth 1` で作業用ディレクトリへ取ってカタログにする。`marketplace add` は検査に通るまでしない
2. `guard fetch-plugin <カタログ> <プラグイン> <作業用ディレクトリ>/plugin` を実行する。出力されたパスがプラグインのルートで、これを検査する

### skill を取る

1. `git clone` で作業用ディレクトリへ取り、`git rev-parse HEAD` を控える
2. `SKILL.md` を持つディレクトリを探す（`.git` の中は除く）。複数あって名前の指定が無ければ、一覧を示して選んでもらう
3. `~/.claude/skills/<名前>` が既にあれば止めて、`/skill-update` を案内する

完了条件: 検査するディレクトリが 1 つに決まっている。

## 2. 検査する

`guard scan <ディレクトリ> --name <名前>` を実行する。名前はプラグイン名か skill 名で、baseline の選択とトークンの照合に使う。大きい skill は 10 分以上かかるので、Bash の timeout を 600000 にし、それでも足りなければバックグラウンドで実行する。

出力の `verdict` で分岐する。

- PASS: `token:` を控えて 3 へ進む
- REVIEW: 指摘を利用者に示し、導入するかを聞く。承認されたら `guard approve <report>` でトークンを取る。断られたらここで終える
- BLOCK と終了コード 3: 指摘を報告して終える

指摘を示すときは、`report` の JSON にある箇所を開いて実際のコードや文面を読み、誤検知かどうかの見立てを添える。静的解析だけなので誤検知が多い。逆に SkillSpector は英語以外の文面を見落としやすいので、日本語などで書かれた指示は自分で読む。

baseline は、利用者が BLOCK や REVIEW の指摘を確かめたうえで受け入れると明言したときだけ作る。`guard baseline <ディレクトリ> --name <名前> --reason <理由>` を実行し、2 をやり直す。

## 3. 導入する

導入コマンドには `SKILL_GUARD_TOKEN=<token>` を前置する。PreToolUse フックは、トークンが無いもの、発行から 1 時間を過ぎたもの、検査した名前をコマンドに含まないものを止める。

### プラグインを入れる

1. 未登録のマーケットプレイスなら `claude plugin marketplace add <配布元>` を実行する
2. `SKILL_GUARD_TOKEN=<token> claude plugin install <プラグイン>@<マーケットプレイス>` を実行する。マーケットプレイスが宣言したコマンドの確認を求められたら、そのコマンドを利用者に見せて判断を仰ぐ

### skill を入れる

- skill がリポジトリのルートにある: 作業用ディレクトリの clone を `mv` で `~/.claude/skills/<名前>` へ移す。`.git` が残るので、`/skill-update` が git で更新を追える
- サブディレクトリにある: `rsync -a --exclude .git <skill のディレクトリ>/ ~/.claude/skills/<名前>/` で写す。`~/.claude/skill-guard/sources.json` に `"<名前>": {"url": ..., "path": ..., "commit": ...}` を足し、`/skill-update` が更新元を引けるようにする

## 4. 照合する

- プラグイン: `claude plugin list --json` から `installPath` を取り、`guard verify <プラグインのルート> <installPath>` を実行する
- skill: `guard verify <skill のディレクトリ> ~/.claude/skills/<名前>` を実行する

差分が出たら、検査していない中身が入っている。差分を示し、プラグインなら `claude plugin uninstall`、skill ならディレクトリの削除を提案して承認を待つ。

`verify` は `node_modules` を比べない。導入時にキャッシュへ足されることがあり、SkillSpector が見ているのは `package.json` と lock ファイルの依存の宣言だけである。依存を持つプラグインは報告でそのことを伝える。

完了条件: 入れたものがすべて検査した中身と一致しているか、一致しないものについて利用者の判断を仰いでいる。

## 5. 片付けて報告する

作業用ディレクトリを消し、次を報告する。

- 入れたもの、そのコミットか version、判定
- REVIEW なら、承認を受けた指摘
- 利用者が `/reload-plugins`（プラグイン）と `/reload-skills`（skill）を実行すれば、再起動せずに今のセッションへ読み込めること
- 外部の skill を足したなら、dotfiles の README の「スキルの配布元」に追記が要ること
