---
name: skill-update
description: 導入済みの skill とプラグインの新しいバージョンを、SkillSpector の検査に通してから更新する。
disable-model-invocation: true
---

# skill-update

起動: `/skill-update [名前 ...]`

名前を省くと、更新元が分かるものすべてが対象になる。新しいバージョンを作業用ディレクトリ `~/.cache/skill-guard/stage/update-<日時>/`（以下 `<stage>`）へ取り、検査に通ったものだけを入れる。

検査と判定は `~/.claude/skill-guard/skill-guard.sh`（以下 `guard`）が受け持つ。引数なしで実行すると使い方が出る。Colima は `$HOME` しかコンテナに見せないので、作業用ディレクトリは `$HOME` 配下に置く。

## 1. 対象を集める

更新元の種類は 4 つある。

- プラグイン
  - `claude plugin list --json` で列挙する
  - 同じ `id` が user と project の両方にあれば 1 件にまとめ、scope を控える
- git の skill
  - `~/.claude/skills/*/.git` があるもの
- skills CLI の skill
  - `~/.agents/.skill-lock.json` の `skills`。`sourceUrl` と `skillPath` が更新元
- 配布元を記録した skill
  - `~/.claude/skill-guard/sources.json` の `url` と `path`

どれにも当たらない `~/.claude/skills/` の skill は自作として対象から外し、報告の最後に名前だけ挙げる。

## 2. 新しいバージョンを取る

種類ごとに、新しいバージョンを `<stage>/<名前>` へ置く。

- プラグイン
  - マーケットプレイスごとに 1 回、`claude plugin marketplace update <マーケットプレイス>` を実行する
  - `guard fetch-plugin <installLocation> <プラグイン> <stage>/<プラグイン>` を実行する。`installLocation` は `~/.claude/plugins/known_marketplaces.json` にある
- git の skill
  - `git status --porcelain` に出力があれば、ローカルの変更を消さないよう更新せずに報告へ回す
  - `git -C <dir> fetch -q` のあと、`git -C <dir> rev-parse @{u}` を新しいバージョンの SHA とする
  - `git -C <dir> archive <SHA> | tar -x -C <stage>/<名前>` で取り出す
- skills CLI の skill と、配布元を記録した skill
  - `git clone --depth 1 <url> <stage>/<名前>.repo` で取る
  - skill のディレクトリ（`skillPath` の親ディレクトリか `path`）を新しいバージョンとする

`guard verify <新しいバージョン> <導入済みの場所>` で差分が無ければ「更新なし」とする。プラグインの導入済みの場所は `installPath`。

完了条件: すべての対象が「更新なし」「更新候補」「取得できず（理由付き）」のどれかに分かれている。

## 3. 検査する

更新候補ごとに `guard scan <新しいバージョン> --name <名前> --since <導入済みの場所>` を実行する。前に検査を通した記録（PASS、承認した REVIEW、baseline）があれば、導入済みから変わったファイルだけを検査する。記録が無ければ全体を検査する。出力の `scope:` でどちらだったかが分かる。`~/.claude/skill-guard/baselines/<名前>.yaml` があれば自動で効き、前に受け入れた指摘は数えない。

検査は 1 件で 1 コアを使い、大きいものは 10 分以上かかる。候補が複数あれば、1 回の Bash で `&` と `wait` を使って 4 件まで同時に走らせ、バックグラウンドで実行する。Colima の CPU は 4 つある。

出力の `verdict` で分岐する。

- PASS: `token:` を控えて 4 へ進む
- REVIEW: すべての候補の検査が終わってから、REVIEW のものをまとめて示し、1 件ずつ更新するかを聞く。承認されたものだけ `guard approve <report>` でトークンを取る
- BLOCK と終了コード 3: 更新しない。指摘を報告に載せる

指摘を示すときは、`report` の JSON にある箇所を開いて実際のコードや文面を読み、誤検知かどうかの見立てを添える。旧バージョンから何が変わったか（`diff -rq <導入済みの場所> <新しいバージョン>`）も判断の材料として添える。静的解析だけなので誤検知が多い。逆に SkillSpector は英語以外の文面を見落としやすいので、日本語などで書かれた指示は自分で読む。

baseline は、利用者が BLOCK や REVIEW の指摘を確かめたうえで受け入れると明言したときだけ作る。`guard baseline <新しいバージョン> --name <名前> --reason <理由>` を実行し、その候補の 3 をやり直す。

## 4. 更新する

コマンドには `SKILL_GUARD_TOKEN=<token>` を前置する。PreToolUse フックは、トークンが無いもの、発行から 1 時間を過ぎたもの、検査した名前をコマンドに含まないものを止める。

- プラグイン
  - `SKILL_GUARD_TOKEN=<token> claude plugin update <id> --scope <scope>` を、控えた scope ごとに実行する
- git の skill
  - `SKILL_GUARD_TOKEN=<token> git -C <dir> merge --ff-only <SHA>` を実行する
  - fast-forward できなければ止めて報告する
- skills CLI の skill
  - `SKILL_GUARD_TOKEN=<token> npx -y skills add <source> --skill <名前> --agent claude-code --global --yes` を実行する
  - lock ファイルとシンボリックリンクの構成を保つため、導入時と同じ CLI で入れ直す
- 配布元を記録した skill
  - `rsync -a --delete --exclude .git <新しいバージョン>/ ~/.claude/skills/<名前>/` で置き換える
  - `sources.json` の `commit` を新しいバージョンの SHA に書き換える

## 5. 照合する

- プラグイン: `claude plugin list --json` の新しい `installPath` に対して `guard verify <新しいバージョン> <installPath>` を実行する
- git の skill: `git -C <dir> rev-parse HEAD` が検査した SHA と一致するかを見る
- skills CLI の skill と、配布元を記録した skill: `guard verify <新しいバージョン> ~/.claude/skills/<名前>` を実行する

差分が出たら、検査していない中身が入っている。差分を示し、利用者の判断を仰ぐ。

`verify` は `node_modules` を比べない。導入時にキャッシュへ足されることがあり、SkillSpector が見ているのは `package.json` と lock ファイルの依存の宣言だけである。依存を持つプラグインは報告でそのことを伝える。

完了条件: 更新したものがすべて検査した中身と一致しているか、一致しないものについて利用者の判断を仰いでいる。

## 6. 片付けて報告する

作業用ディレクトリと、差分検査が作った `~/.cache/skill-guard/diff/<名前>-*` を消し、次を報告する。

- 更新したもの（旧バージョンから新バージョン、判定）
- 更新しなかったものと理由（BLOCK、REVIEW で断られた、取得できず、ローカルの変更あり）
- 更新なしのもの、自作で対象外のもの
- 利用者が `/reload-plugins`（プラグイン）と `/reload-skills`（skill）を実行すれば、再起動せずに今のセッションへ読み込めること
