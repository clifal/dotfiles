# すべての zsh 起動で読み込まれる。interactive shell 限定の .zshrc と違い、
# Claude Code などの non-interactive shell からも参照される。
# 重い処理は書かないこと。

# cargo でインストールしたバイナリを non-interactive でも解決させる。
# .zshrc にも同じ PATH 追加があるため、typeset -U で重複を排除する。
typeset -U path PATH
path=("$HOME/.cargo/bin" $path)

# ax など ~/.local/bin のバイナリを non-interactive でも解決させる。
path=("$HOME/.local/bin" $path)

# mise で入れたツール（pnpm など）を non-interactive でも解決させる。
# mise activate は .zshrc 側にあり interactive shell でしか走らないため、
# shims ディレクトリを直接 PATH に載せる。
path=("$HOME/.local/share/mise/shims" $path)

# brew の curl（keg-only）を non-interactive でも /usr/bin/curl より優先させる。
path=("/opt/homebrew/opt/curl/bin" $path)
