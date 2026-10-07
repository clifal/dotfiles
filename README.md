# dotfiles

macOS のセットアップ用設定ファイル一式。Windows に近いキー操作を macOS で
再現する設定を中心に、シェル、ランタイム、Git、SSH、Claude Code の設定を含みます。

## 構成

- `.claude/` — Claude Code の設定、スキル、ステータスライン
- `.ssh/` — SSH クライアント設定
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

cask の `swift-quit` は、ウィンドウをすべて閉じたアプリを自動で終了させます。
Windows に近い挙動にするためのもので、初回起動時にアクセシビリティの許可と
ログイン時の自動起動を設定してください。

### 4. zsh

```sh
cp zsh/.zshrc ~/.zshrc
cp zsh/.zshenv ~/.zshenv
exec $SHELL -l
```

`.zshrc` には `mise` のシェル連携と、keg-only である `rustup` の PATH 設定が
含まれます。`.zshrc` は interactive shell でしか読まれないため、Claude Code の
ような non-interactive shell からは反映されません。そのため `.zshenv` で
`~/.cargo/bin`、`~/.local/bin`、mise の shims ディレクトリを PATH へ追加して
います。手順 8 のスキルが使う `ax` の解決に必要です。

### 5. mise

```sh
mkdir -p ~/.config/mise
cp mise/config.toml ~/.config/mise/config.toml
mise install
```

Node.js、pnpm、Python、Terraform、kubectl、Helm、AWS CLI、TFLint、yq の
バージョンを固定しています。この手順を飛ばすとこれらのコマンドは利用できません。

Terraform だけは手順 3 の Brewfile でも `hashicorp/tap/terraform` を入れています。
PATH では `/opt/homebrew/bin` が mise の shims より先に来るため、`terraform` を
そのまま実行すると Homebrew 側が使われます。mise で固定したバージョンを使いたい
ときは `mise exec terraform -- terraform ...` と書くか、`brew uninstall terraform`
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
```

既に `~/.claude/settings.json` がある場合、上のコマンドは既存の設定を破棄します。
内容を確認し、必要な項目を手でマージしてください。

`settings.json` にはマーケットプレイス `genshijin` とプラグインの有効化設定が
含まれており、Claude Code の起動時に自動で導入されます。`genshijin` は
`SessionStart` フックから毎セッション起動し、応答を圧縮した口調へ切り替えます。
このフックがスキル本文をそのままコンテキストへ流すので、`CLAUDE.md` では
Skill ツールからの二重の読み込みを禁じています。

`mattpocock-skills` も `enabledPlugins` に入っています。公式のマーケットプレイスに
収録されているため、`extraKnownMarketplaces` への追記は要りません。更新は
`claude plugin update mattpocock-skills` で取り込めます。

ただし公式のマーケットプレイスは配布元のコミットを固定しており、追従が遅れます。
2026 年 10 月 7 日の時点で固定されているのは 1.2.3 で、配布元 `mattpocock/skills` は
1.3.1、70 コミット先行しています。`claude plugin update` が「already at the latest」と
答えるのはこのためです。配布元を `extraKnownMarketplaces` へ直接足せば先行分も
入りますが、公式のマーケットプレイスへ切り替えた方針を戻すことになるので、
固定が進むのを待ちます。

`yomiyasu` は日本語の文章を読みやすく書き直すスキルのプラグインで、
`extraKnownMarketplaces` に登録した `nanaism/yomiyasu` から入ります。`CLAUDE.md` は
文章を書くときに `yomiyasu:yomiyasu` を `--full` 付きで使うよう指示しており、
`refine-doc` と `dev-workflow` も仕上げで呼び出します。以前は `suiko` を使って
いましたが、2 つの日本語校正スキルが同時に有効だと指示が干渉するため、`suiko` の
スキルと CLI を削除して `yomiyasu` に一本化しました。

以前は使う 10 スキルを `.claude/skills/` へ取り込んでいました。上流の更新が届かず、
自作スキルとの区別も付かなくなるため、プラグインへ戻しています。取り込んだ分は
消しました。常時コンテキストを占める 25 スキルの description は約 1,600 トークンです。
内訳は `claude plugin details mattpocock-skills` で見られます。

`understand-anything` も入れていましたが、使わないスキルの description が毎ターンの
コンテキストを占めていたため、プラグインとマーケットプレイスの登録ごと削除して
います。取り込んでもいないので、使いたくなったら配布元から入れ直してください。
キャッシュに残っていた旧バージョンが 510 MB の `node_modules` を抱えていたため、
削除で 590 MB ほど空いています。

ステータスラインは `statusline-command.sh` を呼び出し、その中で `jq` を
使います。`jq` は macOS 15 以降に標準搭載されているため、別途の導入は不要です。

`skillOverrides` は現在すべて既定のままです。スキルの description は常にコンテキストへ
読み込まれるため、自動起動させたくないものは `"<スキル名>": "user-invocable-only"` を
足して `/` からの明示的な呼び出しだけに限定できます。この指定が対象にするのは
ローカルスキルだけで、プラグインとして導入したスキルでは無視されます。

`syncClaudeAiSkills` は `false` です。claude.ai で有効にしたスキルの同期を止めます。
`docs` や `docx` など 8 つが同期されていましたが、一度も使わないまま毎ターンの
コンテキストを占めていました。手元から消しても次の同期で戻るため、同期そのものを
切っています。既に降りてきた分は次回の起動で `~/.claude/skills/.trash` へ移り、
`cleanupPeriodDays` の経過後に消えます。claude.ai 側で新しいスキルを有効にしても
降りてこなくなるので、使いたくなったらこの項目を外してください。

`cleanupPeriodDays` は `30` です。既定と同じ値ですが、会話ログと
`~/.claude/skills/.trash` の保持期間として明示しています。`~/.claude/projects/` の
会話ログは放っておくと数百 MB まで育ちます。短くしたいときは値を減らしてください。

`permissions.defaultMode` は `auto` です。ツールの実行許可を毎回確認せずに
進めます。共有マシンや業務用の環境へそのまま持ち込む場合は、この項目を
外すか `default` へ戻してください。

`model` は `claude-opus-5` です。以前は 1M コンテキストの `opus[1m]` を指定して
いましたが、通常の指定へ戻しています。`switchModelsOnFlag` は `false` で、長い会話でも
別のモデルへ自動で切り替わりません。

`effortLevel` は `high` です。これは既定値で、`modelSettings` にモデルごとの指定が
ない場合に使われます。`modelSettings` では `claude-opus-5-5` を `xhigh`、
`claude-opus-5` を `high` にしています。推論にかける手数が増えるぶん応答は遅く、
消費トークンも増えるため、軽い用途が中心なら `medium` へ下げてください。

#### スキル

`.claude/skills/` の中身は次のとおりです。

- `ax` — HTML の取得と構造化抽出を `ax` CLI で行う
- `commit-msg` — 変更内容の日本語説明から Conventional Commits のメッセージを作る
- `dev-workflow` — 理解から実装、コードレビューまで人手の確認を挟んで進める
- `en-comment` — 日本語をプログラミング用の英語コメントへ訳す
- `pair` — 開発者が手を動かす前提でペアプログラミングの相方を務める
- `refine-doc` — 日本語ドキュメントを、中身を残したまま再構成する
- `research-plan` — 調査エージェントへ渡す依頼書を 1 枚にまとめる
- `show-me` — 図やコードのスケッチで話題を視覚的に説明する
- `software-compare` — 同じ役割のソフトウェア 2〜4 個の比較ガイドと図解を、一次情報の調査から作る
- `software-guide` — ソフトウェアの入門ガイドと図解を、一次情報の調査から作る
- `spec-doc` — 調査結果のディレクトリから要件定義書・基本設計書・実装計画の 3 文書を作る

`dev-workflow`、`software-compare`、`software-guide`、`spec-doc` は
`disable-model-invocation: true` で、`/dev-workflow` や `/software-guide <ソフトウェア名>`、
`/software-compare <名前> <名前>`、`/spec-doc <ディレクトリ>` のように明示的に呼んだときだけ
動きます。

`dev-workflow` の各フェーズは `mattpocock-skills` プラグインのスキルへ渡します。
プラグインのスキルは名前空間付きで呼びます。そのため `/mattpocock-skills:grill-with-docs`
の形で書いてあります。同名のローカルスキルがない限り `/grill-with-docs` でも通ります。
フェーズ 3 以降は `docs/agents/issue-tracker.md` が要ります。これは
`/mattpocock-skills:setup-matt-pocock-skills` が作ります。

`archify`（アーキテクチャ図の生成）は約 7 MB あるため `.gitignore` で除外し、
上のコピーには含まれません。

`ax` は外部の CLI に依存します。`curl -fsSL https://ax.yusuke.run/install | sh` で
`~/.local/bin` へ入り、PATH は手順 4 の `.zshenv` が通します。

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
- Home／Endの変換は、多くのテキスト編集アプリでWindowsに近い動作になります。
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
  （`npx skills add yusukebe/ax` で導入。CLI も同じリポジトリ）
- `show-me` — https://github.com/humanlayer/skills
- `archify` — https://github.com/tt-a1i/archify
  （MIT。`Cocoon-AI/architecture-diagram-generator` から派生している。手順 8 の
  とおり収録していないので、次のコマンドで配布元から取得する）

```sh
npx -y skills add tt-a1i/archify --skill archify --agent claude-code --global --copy --yes
```

残る `commit-msg`、`dev-workflow`、`en-comment`、`pair`、`refine-doc`、
`research-plan`、`software-guide` は自作で、配布元はありません。

https://github.com/mattpocock/skills （MIT）の 25 スキルは `.claude/skills/` へは
置きません。手順 8 の `enabledPlugins` にある `mattpocock-skills` プラグインとして
入れています。実体は `~/.claude/plugins/cache/` にあり、リポジトリには入りません。
`dev-workflow` が渡す `grill-with-docs`、`to-spec`、`to-tickets`、`implement`、
`code-review`、`setup-matt-pocock-skills` はここから来ます。
