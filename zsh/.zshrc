# Display Terminal Information
export PS1='💻 @%m %1~ %# '

# Rust (rustup, keg-only)
export PATH="$(brew --prefix rustup)/bin:$PATH"
export PATH="$HOME/.cargo/bin:$PATH"

# Command Alias
alias ls='ls -a'
alias brewupf='brew update && brew upgrade --formula --yes && brew cleanup -s'
alias brewupc='brew update && brew upgrade --cask --greedy --yes && brew cleanup -s'

# Hook mise
eval "$(mise activate zsh)"
