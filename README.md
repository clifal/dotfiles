# dotfiles

## Windowsに近いmacOSキー設定

### Karabiner-Elements

- Mac内蔵キーボードだけ `Caps Lock → 左Command`
- USBキーボードではCaps Lockを変更しない
- `Command + Space` で「かな／英数」を切り替える
- `Shift + Space` は Karabiner では変更しない
- `Home / End` で行頭／行末へ移動する
- `Command + Home / End` で文書の先頭／末尾へ移動する
- `Command + Y` でやり直し
- `F2` でファイル名変更
- Chromeで `F5 → Command + R`

### Visual Studio Code

- `Shift + Space` で入力候補を表示する
- キーの物理位置を基準に判定する設定を追加する

## 1. Karabiner設定の導入

`windows-like-karabiner.json` を次の場所へコピーします。

```text
~/.config/karabiner/assets/complex_modifications/
```

ターミナルからコピーする場合:

```sh
mkdir -p ~/.config/karabiner/assets/complex_modifications
cp windows-like-karabiner.json ~/.config/karabiner/assets/complex_modifications/
```

その後、Karabiner-Elementsを開きます。

1. `Complex Modifications` を開く
2. `Add predefined rule` を押す
3. `Windows-like key mappings for macOS` 内のルールをすべて有効にする

## 2. macOS側のControl+Spaceを空ける

macOSの「システム設定」→「キーボード」→
「キーボードショートカット」→「入力ソース」を開きます。

`前の入力ソースを選択` などに `Control + Space` が設定されている場合は、
無効にするか別のキーへ変更します。

Spotlightに `Control + Space` を割り当てている場合も解除します。
通常のSpotlightは `Command + Space` なので、必要がなければ解除しなくても構いません。

## 3. Visual Studio Code

### keybindings.json

Visual Studio Codeでコマンドパレットを開き、
`Preferences: Open Keyboard Shortcuts (JSON)` を実行します。

既存の配列 `[...]` の中へ、
`vscode-keybindings.json` の項目を追加してください。

既存設定がない場合は、ファイルの内容をそのまま使用できます。

### settings.json

`Preferences: Open User Settings (JSON)` を開き、
次を既存のJSONオブジェクトへ追加します。

```json
"keyboard.dispatch": "keyCode"
```

`vscode-settings-fragment.json` は、この設定だけを収めた参考ファイルです。
既存のsettings.jsonを丸ごと置き換えないでください。

## 動作確認

Karabiner-EventViewerで次を確認できます。

- 内蔵キーボードのCaps Lockが `left_control` になる
- USBキーボードのCaps Lockは `caps_lock` のまま
- Control+Spaceで `japanese_kana` または `japanese_eisuu` が送られる
- Home、End、Control+Home、Control+Endが変換される

## 注意

- `F5`が画面輝度などとして動くMacでは、`fn + F5`が必要な場合があります。
  macOSの「F1、F2などのキーを標準のファンクションキーとして使用」を有効にすると、
  F5を単独で使いやすくなります。
- Home／Endの変換は、多くのテキスト編集アプリでWindowsに近い動作になります。
  アプリ独自のキー処理がある場合は動作が異なることがあります。
- USBキーボードのControl、Windows、Altキー自体は入れ替えていません。
  これはControl+SpaceやターミナルのControl+Cを壊さないためです。
