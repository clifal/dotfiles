# dotfiles

macOS のセットアップ用設定ファイル一式。Windows に近いキー操作を macOS で
再現する設定を中心に、シェル、ランタイム、Git、SSH、Claude Code の設定を含みます。

## 構成

- `.claude/` — Claude Code の設定、スキル、ステータスライン
- `.ssh/` — SSH クライアント設定
- `git/` — Git の設定とグローバル除外設定
- `homebrew/` — Brewfile（formula、cask、VS Code 拡張）
- `karabiner/` — Karabiner-Elements のキーマッピング
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
います。手順 8 のスキルが使う `suiko` や `ax` の解決に必要です。

### 5. mise

```sh
mkdir -p ~/.config/mise
cp mise/config.toml ~/.config/mise/config.toml
mise install
```

Node.js、Python、Terraform、kubectl、Helm、AWS CLI、TFLint のバージョンを
固定しています。Homebrew ではなく mise 側で管理しているため、この手順を
飛ばすとこれらのコマンドは利用できません。

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

`settings.json` には 4 つのマーケットプレイス（`genshijin`、`context7`、
`understand-anything`、`mattpocock`）とプラグインの有効化設定が含まれており、
Claude Code の起動時に自動で導入されます。ステータスラインは
`statusline-command.sh` を呼び出し、その中で `jq` を使います。`jq` は
macOS 15 以降に標準搭載されているため、別途の導入は不要です。

#### スキル

`.claude/skills/` には次のスキルが入っています。

- `ax` — HTML の取得と構造化抽出を `ax` CLI で行う
- `commit-msg` — 変更内容の日本語説明から Conventional Commits のメッセージを作る
- `dev-workflow` — 理解から実装、コードレビューまでを人手の確認を挟んで進める
- `en-comment` — 日本語をプログラミング用の英語コメントへ訳す
- `pair` — 開発者が手を動かす前提でペアプログラミングの相方を務める
- `sanitize-artifacts` — 生成物からプロンプトや会話の痕跡を取り除く
- `suiko` — 日本語文書の不自然さと読解負荷を診断して直す
- `tech-research` — 一次ソースを検証しながら技術動向のレポートを作る

`archify`（アーキテクチャ図の生成）は約 7 MB あるため `.gitignore` で
除外しており、上のコピーには含まれません。必要な場合は個別に取得してください。

スキルのうち `suiko` と `ax` は外部の CLI に依存します。`suiko` は
`cargo install suiko` で導入し（手順 3 で `rustup` を入れた前提）、`ax` は
`~/.local/bin` へ配置します。どちらも手順 4 の `.zshenv` が PATH を通します。
CLI がない場合、スキルは手動チェックへ縮退します。

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
"keyboard.dispatch": "keyCode"
```

`vscode-settings-fragment.json` は、この設定だけを収めた参考ファイルです。
既存の settings.json を丸ごと置き換えないでください。

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
