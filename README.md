# dotfiles

macOS のセットアップ用設定ファイル一式。Windows に近いキー操作を macOS で
再現する設定を中心に、シェル、ランタイム、Git、SSH、Claude Code の設定を含みます。

## 構成

- `.claude/` — Claude Code の設定、スキル、ステータスライン、スキルとプラグインの検査スクリプト
- `.ssh/` — SSH クライアント設定
- `curl/` — curl の設定（`.curlrc`）と、macOS の CA バンドルを修正するスクリプト
- `git/` — Git の設定とグローバル除外設定
- `homebrew/` — Brewfile（formula、cask、VS Code 拡張）
- `karabiner/` — Karabiner-Elements のキーマッピング
- `markdownlint/` — markdownlint の共通設定とカスタムルール
- `mise/` — mise で管理する言語・CLI ランタイムのバージョン定義
- `vscode/` — VS Code のキーバインドと設定断片
- `zsh/` — zsh の設定（`.zshrc` と `.zshenv`）

## セットアップ

手順は順番に実行してください。前の手順が後の手順の前提になっています。
コマンドはすべてリポジトリのルートで実行します。

### 1. リポジトリの取得

Git は Xcode Command Line Tools に含まれます。未導入の場合は初回実行時に
インストールを促されます。

```sh
xcode-select --install
git clone https://github.com/clifal/dotfiles.git ~/repo/personal/dotfiles
cd ~/repo/personal/dotfiles
```

SSH 鍵の設定は手順 7 で行うため、ここでは HTTPS で取得します。

### 2. Homebrew

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

インストール後、`brew` を PATH に通す手順が案内されます。案内どおりに
`~/.zprofile` へ `eval "$(/opt/homebrew/bin/brew shellenv)"` を追記してください。
この設定はマシン固有のため、このリポジトリには含めていません。手順 4 の
`.zshrc` が `brew` コマンドを前提にしているので、先に済ませておく必要があります。

### 3. Brewfile の適用

```sh
brew bundle install --file=homebrew/Brewfile
```

cask の導入で管理者パスワードを求められます。

VS Code 拡張は `code` コマンド経由で導入されるため、Visual Studio Code 自体が
未導入の初回実行では失敗することがあります。その場合はもう一度同じコマンドを
実行してください。

Rust のツールチェーンが必要な場合は、`rustup` の導入後に `rustup-init` を
別途実行します。

cask の `swift-quit` はウィンドウをすべて閉じたアプリを自動で終了させます。
Windows に近い挙動にするためのもので、初回起動時にアクセシビリティの許可と
ログイン時の自動起動を設定してください。

### 4. zsh と curl

```sh
cp zsh/.zshrc ~/.zshrc
cp zsh/.zshenv ~/.zshenv
cp curl/.curlrc ~/.curlrc
exec $SHELL -l
```

`.zshrc` には `mise` のシェル連携と、keg-only である `rustup` と `curl` の PATH
設定が含まれます。`.zshrc` は interactive shell でしか読まれないため、Claude Code の
ような non-interactive shell からは反映されません。そのため `.zshenv` で
`~/.cargo/bin`、`~/.local/bin`、mise の shims ディレクトリを PATH へ追加して
います。手順 8 のスキルが使う `ax` の解決に必要です。Homebrew の curl も
`.zshenv` で PATH の先頭へ置き、macOS 付属の `/usr/bin/curl` より先に解決させて
います。

`.curlrc` は、curl が証明書の検証に使う CA バンドルを Homebrew の
`ca-certificates` に固定します。Homebrew の curl は CA バンドルでの検証に
失敗すると、macOS の信頼ストアで検証し直します。macOS の信頼ストアは、
ブラウザが信頼を取り消した CA の証明書を受け入れることがあります。2026 年 10 月に
鍵の漏えいが判明した eMudhra の中間 CA がその例で、この設定がないと curl は
その CA が発行した証明書を受け入れます。次のコマンドが証明書エラー
（`curl: (60)`）で終われば、設定が効いています。

```sh
curl https://dv-g3b-emudhra.we-have-a-problem.com/
```

macOS 付属の `/usr/bin/curl` も `.curlrc` を読むため、この証明書を拒否します。
ただし `-q` を付けて `.curlrc` を読まずに実行すると、`/usr/bin/curl` は
`/etc/ssl/cert.pem` で検証し、この証明書を受け入れます。macOS 付属の git と
python3 も同じです。Apple は将来の macOS の更新でこのファイルを直すとしています。
それまでは次のスクリプトで、eMudhra の中間 CA につながるルート証明書を
このファイルから外してください。管理者パスワードを求められます。

```sh
curl/remove-emudhra-roots.sh
```

外すルート証明書のうち AAA Certificate Services は、問題のない CA にもつながって
います。そうした CA の証明書を使うサイトにも、macOS 付属のツールでは接続
できなくなることがあります。

macOS の更新でファイルが元に戻ることがあるため、更新後はスクリプトを
再実行してください。スクリプトの変更を取り消すときは
`sudo cp -p /etc/ssl/cert.pem.orig /etc/ssl/cert.pem` を実行します。

キーチェーンに社内 CA などを入れて
いる場合、Homebrew の curl はその CA を信頼しなくなります。社内 CA を含む
CA バンドルを別に用意し、`.curlrc` の `cacert` をそちらへ向けてください。

### 5. mise

```sh
mkdir -p ~/.config/mise
cp mise/config.toml ~/.config/mise/config.toml
mise install
```

Node.js、pnpm、Python、Terraform、kubectl、Helm、AWS CLI、TFLint、yq に加えて、
Colima、Lima、Docker CLI、Docker Compose を入れています。この手順を飛ばすと
これらのコマンドは利用できません。Colima は Docker Desktop を使わずにコンテナを
動かすためのもので、`colima start` で仮想マシンを起動してから `docker` コマンドを
使います。

バージョンはどれも `latest` を指定しており、固定していません。Node.js だけは `lts`
です。`latest` の解決結果はキャッシュされるため、`mise install` を実行しても
新しいバージョンへは上がりません。更新は `mise upgrade` で取り込み、差分は `mise outdated`
で確認します。

固定しない方針の代わりに、バージョンを揃える必要がある場面ではプロジェクト側の `mise.toml`
で指定してください。kubectl はクラスタのコントロールプレーンとのバージョン差に
制約があり、`latest` が先行しすぎることがあります。

このリポジトリの中でコマンドを実行すると、mise が `mise/config.toml` を未信頼の設定
ファイルとして検出し、エラーを出します。`mise trust mise/config.toml` で信頼すると
止まります。

Terraform だけは手順 3 の Brewfile でも `hashicorp/tap/terraform` を入れています。
PATH では `/opt/homebrew/bin` が mise の shims より先に来るため、`terraform` を
そのまま実行すると Homebrew 側が使われます。mise 側を使いたいときは
`mise exec terraform -- terraform ...` と書くか、`brew uninstall terraform`
で Homebrew 側を外してください。

### 6. Git

```sh
cp git/.gitconfig ~/.gitconfig
cp git/.gitignore-global ~/.gitignore-global
cp git/.gitconfig-for-COMPANY-NAME ~/.gitconfig-for-COMPANY-NAME
```

コピー後、プレースホルダを自分の値へ置き換えてください。置き換えないと
コミットの author が不正な値になります。

`~/.gitconfig`

- `USERNAME` — GitHub のユーザー名
- `123456789` — GitHub の数値 ID。`https://api.github.com/users/<ユーザー名>` の
  `id` フィールドで確認できます
- `COMPANY-NAME` — 会社名。`includeIf` のディレクトリ名とインクルード先の
  ファイル名の両方に現れます

`~/.gitconfig-for-COMPANY-NAME`

- `USERNAME`、`COMPANY-NAME` — 会社で使うユーザー名とメールアドレスのドメイン
- ファイル名の `COMPANY-NAME` も同じ値へリネームし、`~/.gitconfig` の
  `includeIf` の `path` と一致させます

`~/.gitconfig` の `includeIf` は `~/repo/<会社名>/` 配下のリポジトリにのみ
会社用の author 設定を適用します。会社のリポジトリはこのディレクトリ配下へ
clone してください。

### 7. SSH

鍵を生成し、GitHub へ公開鍵を登録します。

```sh
mkdir -p ~/.ssh
ssh-keygen -t ed25519 -C "<GitHub に登録したメールアドレス>" -f ~/.ssh/private-ssh-key
cp .ssh/config ~/.ssh/config
```

`~/.ssh/config` の `IdentityFile` は `~/.ssh/private-ssh-key` を指しています。
別のファイル名で鍵を作った場合は、この値を実際の鍵のパスへ書き換えてください。

先頭の `Include ~/.colima/ssh_config` は、Colima が作る仮想マシンへ `ssh` で入るための
設定を読み込みます。Colima を使わない場合は消してかまいません。

公開鍵 `~/.ssh/private-ssh-key.pub` の内容を GitHub の
Settings → SSH and GPG keys へ登録し、接続を確認します。

```sh
ssh -T git@github.com
```

### 8. Claude Code

Claude Code 本体は手順 3 の cask で導入されます。設定を配置します。

```sh
mkdir -p ~/.claude
cp .claude/settings.json ~/.claude/settings.json
cp .claude/CLAUDE.md ~/.claude/CLAUDE.md
cp .claude/statusline-command.sh ~/.claude/statusline-command.sh
cp -R .claude/skills ~/.claude/
cp -R .claude/skill-guard ~/.claude/
```

既に `~/.claude/settings.json` がある場合、上のコマンドは既存の設定を破棄します。
内容を確認し、必要な項目を手でマージしてください。

`settings.json` にはマーケットプレイス `genshijin` とプラグインの有効化設定が
含まれており、Claude Code の起動時に自動で導入されます。`genshijin` は
`SessionStart` フックから毎セッション起動し、応答を圧縮した口調へ切り替えます。

`mattpocock-skills` も `enabledPlugins` に入っています。公式のマーケットプレイスに
収録されているため、`extraKnownMarketplaces` への追記は要りません。更新は
`/skill-update mattpocock-skills` で、検査を通してから取り込みます（「スキルとプラグインの検査」を参照）。

`yomiyasu` は日本語の文章を読みやすく書き直すスキルのプラグインで、
`extraKnownMarketplaces` に登録した `nanaism/yomiyasu` から入ります。`CLAUDE.md` は
文章を書くときに `yomiyasu:yomiyasu` を `--full` 付きで使うよう指示しており、
`refine-doc`、`dev-workflow`、`slides`、`software-compare`、`software-guide` も
文章の推敲に使います。

プラグインのスキルは、取り込むと上流の更新が届かず自作スキルとの区別も付かなく
なるため、プラグインのまま使います。常時コンテキストを占める 27 スキルの description は
約 1,650 トークンで、内訳は `claude plugin details mattpocock-skills` で見られます。

ステータスラインは `statusline-command.sh` を呼び出し、その中で `jq` を
使います。`jq` は macOS 15 以降に標準搭載されているため、別途の導入は不要です。

`skillOverrides` は空です。自動起動させたくないスキルは `"<スキル名>": "user-invocable-only"` を
足すと、`/` からの明示的な呼び出しだけに限定できます。この指定が効くのはローカルスキル
だけで、プラグインとして導入したスキルでは無視されます。

`syncClaudeAiSkills` は `false` です。claude.ai で有効にしたスキルの同期を止めます。
手元から消しても次の同期で戻るため、同期そのものを切っています。claude.ai 側で
新しいスキルを有効にしても降りてこなくなるので、使いたくなったらこの項目を外してください。

`cleanupPeriodDays` は `30` です。既定と同じ値ですが、会話ログの保持期間として
明示しています。`~/.claude/projects/` の会話ログは放っておくと数百 MB まで育ちます。
短くしたいときは値を減らしてください。

`permissions.defaultMode` は `auto` です。ツールの実行許可を毎回確認せずに
進めます。共有マシンや業務用の環境へそのまま持ち込む場合は、この項目を
外すか `default` へ戻してください。

`model` は最新の Opus へ追従する別名の `opus` です。`switchModelsOnFlag` は `false` で、
長い会話でも別のモデルへ自動で切り替わりません。

`effortLevel` と、`modelSettings` で指定するモデルごとの `effortLevel` は環境ごとに
決めるため、`/env-audit` もリポジトリへ反映しません。値を上げるほど推論にかける
手数が増え、応答は遅く、消費トークンも増えます。軽い用途が中心の環境では
`medium` へ下げてください。

#### スキル

`.claude/skills/` の中身は次のとおりです。

- `ax` — HTML の取得と構造化抽出を `ax` CLI で行う
- `commit-msg` — 変更内容の日本語説明から Conventional Commits のメッセージを作る
- `dev-workflow` — 理解から実装、コードレビューまで人手の確認を挟んで進める
- `en-comment` — 日本語をプログラミング用の英語コメントへ訳す
- `env-audit` — ローカルとリポジトリの差分を反映し、不要なキャッシュを掃除する
- `pair` — 開発者が手を動かす前提でペアプログラミングの相方を務める
- `refine-doc` — 日本語ドキュメントを、中身を残したまま再構成する
- `research-plan` — 調査エージェントへ渡す依頼書を 1 枚にまとめる
- `show-me` — 図やコードのスケッチで話題を視覚的に説明する
- `skill-install` — スキルやプラグインを、SkillSpector の検査に通してから導入する
- `skill-update` — 導入済みのスキルとプラグインの新しいバージョンを、SkillSpector の検査に通してから更新する
- `slides` — 文書から PPTX と PDF のスライドを、同梱のテンプレートの上に組む
- `software-compare` — 同じ役割のソフトウェア 2〜4 個の比較ガイドと図解を、一次情報の調査から作る
- `software-guide` — ソフトウェアの入門ガイドと図解を、一次情報の調査から作る
- `spec-doc` — 調査結果のディレクトリから要件定義書・基本設計書・実装計画の 3 文書を作る

`dev-workflow`、`env-audit`、`skill-install`、`skill-update`、`software-compare`、
`software-guide`、`spec-doc` は `disable-model-invocation: true` で、`/dev-workflow` や
`/software-guide <ソフトウェア名>`、`/software-compare <名前> <名前>`、`/spec-doc <ディレクトリ>`、
`/env-audit`、`/skill-install <配布元>`、`/skill-update [名前]` のように
明示的に呼んだときだけ動きます。

`dev-workflow` の各フェーズは `mattpocock-skills` プラグインのスキルへ渡します。
プラグインのスキルは名前空間付きで呼ぶため、`/mattpocock-skills:grill-with-docs`
の形で書いてあります。同名のローカルスキルがない限り `/grill-with-docs` でも通ります。
フェーズ 3 以降は `docs/agents/issue-tracker.md` が要ります。これは
`/mattpocock-skills:setup-matt-pocock-skills` が作ります。

`archify`（アーキテクチャ図の生成）は約 18 MB あるため `.gitignore` で除外し、
上のコピーには含まれません。

`ax` は外部の CLI に依存します。`curl -fsSL https://ax.yusuke.run/install | sh` で
`~/.local/bin` へ入り、PATH は手順 4 の `.zshenv` が通します。

#### スキルとプラグインの検査

`/skill-install` と `/skill-update` はスキルとプラグインを入れる前に
[NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) で検査します。検査は Colima の上の
Docker で静的解析だけ（`--no-llm`）を行うので、手順 5 の Colima と Docker CLI が要ります。
初回の検査でイメージ `skillspector:2.13.2`（約 730 MB）をビルドします。

判定は 3 段階です。PASS ならそのまま入れ、REVIEW は指摘を見て承認したときだけ入れ、
BLOCK なら止めます。静的解析だけなので誤検知が多く、`ax` や `archify` も BLOCK になります。
指摘を確かめて受け入れたものは `~/.claude/skill-guard/baselines/` に baseline を作り、
次の検査から数えません。baseline は検査した中身と SkillSpector のバージョンに紐づく
マシンごとの判断なので、`.gitignore` で除外しています。

`settings.json` の `hooks` にある PreToolUse フックは、Claude Code が検査を通さずに
`claude plugin install` や `claude plugin update`、`skills add`、`~/.claude/skills` への
`git clone` などを実行しようとすると止めます。止めるのは Claude Code が実行するコマンドだけで、
ターミナルで直接打ったコマンドは止まりません。検査とフックの本体は
`.claude/skill-guard/skill-guard.sh` です。

### 9. Karabiner-Elements

Karabiner-Elements 本体は手順 3 の cask で導入されます。初回起動時に
ドライバの承認と入力監視の許可を求められるので、画面の案内に従って
システム設定で許可してください。許可しない限りキーマッピングは動作しません。

設定ファイルを配置します。

> **注意:** 次のコマンドは既存の Karabiner 設定をすべて置き換えます。
> 既に自分のルールを設定している場合は、先に `~/.config/karabiner/karabiner.json`
> を退避してください。上書き中に Karabiner が設定を書き戻さないよう、
> Karabiner-Elements を終了した状態で実行します。

```sh
mkdir -p ~/.config/karabiner/assets/complex_modifications
cp karabiner/karabiner.json ~/.config/karabiner/karabiner.json
cp karabiner/assets/complex_modifications/windows-like-karabiner.json \
   ~/.config/karabiner/assets/complex_modifications/
```

`karabiner.json` には 7 つのルールが有効な状態で入っているため、コピー後に
Karabiner-Elements を起動すればそのまま動作します。`Complex Modifications` から
個別に有効・無効を切り替えたい場合は、`assets/complex_modifications/` へ置いた
ファイルが `Add predefined rule` の一覧に `Windows-like key mappings for macOS`
として現れます。

### 10. 入力ソースとキーボードショートカット

Google 日本語入力は手順 3 の cask で導入されます。macOS の「システム設定」→
「キーボード」→「入力ソース」で日本語の入力ソースを追加してください。
Karabiner のかな／英数切り替えは、現在の入力ソースが日本語かどうかで
送出するキーを変えるため、この登録が前提になります。

続けて `Command + Space` を空けます。Karabiner はこのキーをかな／英数の
切り替えとして消費し、macOS 側の割り当てより先に処理します。

「システム設定」→「キーボード」→「キーボードショートカット」を開き、
次の 2 箇所を確認します。

- 「Spotlight」→ `Spotlightの検索を表示`
  初期状態で `Command + Space` が割り当てられています。Karabiner が先に
  このキーを処理するため、Spotlight は反応しなくなります。別のキーへ
  変更するか、Raycast など別のランチャーへ移行してください。
- 「入力ソース」→ `前の入力ソースを選択`
  `Command + Space` または `Control + Space` が設定されている場合は
  無効にします。

### 11. Visual Studio Code

Visual Studio Code 本体と拡張は手順 3 の cask および `vscode` エントリで
導入されます。キーバインドと設定を追加します。

#### keybindings.json

コマンドパレットを開き、`Preferences: Open Keyboard Shortcuts (JSON)` を
実行します。既存の配列 `[...]` の中へ `vscode-keybindings.json` の項目を
追加してください。既存設定がない場合は、ファイルの内容をそのまま使用できます。

#### settings.json

`Preferences: Open User Settings (JSON)` を開き、次を既存の JSON オブジェクトへ
追加します。

```json
"keyboard.dispatch": "keyCode",
"[markdown]": {
  "editor.defaultFormatter": "DavidAnson.vscode-markdownlint",
  "editor.formatOnSave": true
},
"markdownlint.configFile": "${userHome}/.config/markdownlint/.markdownlint-cli2.jsonc"
```

`vscode-settings-fragment.json` は、これらの設定だけを収めた参考ファイルです。
既存の settings.json を丸ごと置き換えないでください。

#### markdownlint

Markdown を保存すると、markdownlint が自動で直せる指摘を直します。共通の設定と
カスタムルールを配置します。

```sh
mkdir -p ~/.config/markdownlint
cp markdownlint/.markdownlint-cli2.jsonc markdownlint/ja-space.cjs ~/.config/markdownlint/
```

- `MD013`（行の長さ）は無効にしています
- `ja-space.cjs` は、日本語と半角英数字の間に半角スペースを入れるカスタムルールです。
  コード、URL、HTML の中と、句読点や括弧の隣は対象外です
- カスタムルールは JavaScript を実行するため、VS Code で信頼したワークスペースでだけ
  動きます

コマンドで直すときは次を実行します。

```sh
npx markdownlint-cli2 --config ~/.config/markdownlint/.markdownlint-cli2.jsonc --fix <file>
```

## キーマッピング一覧

### Karabiner-Elements

- Mac内蔵キーボードだけ `Caps Lock → 左Command`
- USBキーボードだけ `左Control → 左Command`
- USBキーボードではCaps Lockを変更しない
- `Command + Space` で「かな／英数」を切り替える
- `Shift + Space` は Karabiner では変更しない
- `Home / End` で行頭／行末へ移動する
- `Control + Home / End` で文書の先頭／末尾へ移動する
- `Command + Y` でやり直し
- `F2` でファイル名変更
- Chromeで `F5 → Command + R`

### Visual Studio Code

- `Shift + Space` で入力候補を表示する
- `Command + ;` でエディタを拡大する（既定の `Command + テンキーの +` は外す）
- キーの物理位置を基準に判定する設定を追加する

## 動作確認

Karabiner-EventViewerで次を確認できます。

- 内蔵キーボードのCaps Lockが `left_command` になる
- USBキーボードのCaps Lockは `caps_lock` のまま
- USBキーボードの左Controlが `left_command` になる
- Command+Spaceで `japanese_kana` または `japanese_eisuu` が送られる
- Home、End、Control+Home、Control+Endが変換される

## 注意

- `F5`が画面輝度などとして動くMacでは、`fn + F5`が必要な場合があります。
  macOSの「F1、F2などのキーを標準のファンクションキーとして使用」を有効にすると、
  F5を単独で使いやすくなります。
- Home／Endの変換は多くのテキスト編集アプリでWindowsに近い動作になります。
  アプリ独自のキー処理がある場合は動作が異なることがあります。
- USBキーボードでは左Controlが左Commandになります。Windowsキーボードの
  `Ctrl + C` などを、指の位置を変えずにmacOSの `Command + C` として
  使えるようにするためです。
- この変換のため、USBキーボードの左ControlではターミナルのControl+Cを
  送れません。右Controlを使ってください。
- USBキーボードのWindowsキー、AltキーはKarabinerでは変更していません。

## スキルの配布元

`.claude/skills/` のうち次のものは外部のリポジトリが配布元です。入っているのは
取り込み時点の内容で、上流の更新は反映されません。更新時は配布元と差分を
確認してください。

- `ax` — https://github.com/yusukebe/ax
  （CLI も同じリポジトリ。`~/.claude/skills/ax` はシンボリックリンクではなく実体なので、
  配布元から取り直すときは `npx -y skills add yusukebe/ax --skill ax --agent claude-code --global --copy --yes` を実行する）
- `show-me` — https://github.com/humanlayer/skills
  （`ax` と `show-me` の配布元は `.claude/skill-guard/sources.json` にも記録しており、
  `/skill-update` が差分を取る。どちらも手元で書き換えているので、差分は手元の変更として出る）
- `archify` — https://github.com/tt-a1i/archify
  （MIT。`Cocoon-AI/architecture-diagram-generator` から派生している。手順 8 の
  とおり収録していないので、次のコマンドで配布元から取得する）

```sh
npx -y skills add tt-a1i/archify --skill archify --agent claude-code --global --yes
```

`--copy` を付けないと実体は `~/.agents/skills/` へ置かれ、`~/.claude/skills/archify` は
そこへのシンボリックリンクになります。

残る `commit-msg`、`dev-workflow`、`en-comment`、`env-audit`、`pair`、`refine-doc`、
`research-plan`、`skill-install`、`skill-update`、`slides`、`software-compare`、`software-guide`、
`spec-doc` は自作で、配布元はありません。

`slides` は、スライドの規約と検査に
<https://github.com/carnot-tech/jinba-consulting-pptx-skill>（MIT）を使います。
`.claude/skills/` には収録していないので、次のコマンドで取得します。PDF を画像に
する `poppler` は Brewfile に入っています。書体と Keynote の準備は `slides` の
`SKILL.md` の「準備」にあります。

```sh
git clone https://github.com/carnot-tech/jinba-consulting-pptx-skill.git ~/.claude/skills/consulting-pptx-skill
```

https://github.com/mattpocock/skills （MIT）の 27 スキルは `.claude/skills/` へは
置きません。手順 8 の `enabledPlugins` にある `mattpocock-skills` プラグインとして
入れています。実体は `~/.claude/plugins/cache/` にあり、リポジトリには入りません。
`dev-workflow` が渡す `grill-with-docs`、`to-spec`、`to-tickets`、`implement`、
`code-review`、`setup-matt-pocock-skills` はここから来ます。
