# Display Terminal Information
export PS1='💻 @%m %1~ %# '

# Rust (rustup, keg-only)
export PATH="$(brew --prefix rustup)/bin:$PATH"

# Command Alias
alias ls='ls -a'
alias brewupf="brew update && brew upgrade --formula && brew cleanup"'
alias brewupc="brew update && brew upgrade --cask && brew cleanup"'

# Hook mise
eval "$(mise activate zsh)"
