#!/bin/bash
# Claude Code status line: model name, git branch, context usage

input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name')
cwd=$(echo "$input" | jq -r '.workspace.current_dir')

branch=""
if git -C "$cwd" --no-optional-locks rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)
  [ -z "$branch" ] && branch=$(git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
fi

used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
if [ -n "$used" ]; then
  context_str=$(printf "Ctx: %.0f%%" "$used")
else
  context_str="Ctx: N/A"
fi

# ANSI colors (dim-friendly)
COLOR_MODEL="\033[2;36m"   # dim cyan
COLOR_BRANCH="\033[2;33m"  # dim yellow
COLOR_CTX="\033[2;32m"     # dim green
RESET="\033[0m"
SEP="\033[2;37m|\033[0m"

if [ -n "$branch" ]; then
  printf "${COLOR_MODEL}%s${RESET} ${SEP} ${COLOR_BRANCH}%s${RESET} ${SEP} ${COLOR_CTX}%s${RESET}\n" "$model" "$branch" "$context_str"
else
  printf "${COLOR_MODEL}%s${RESET} ${SEP} ${COLOR_CTX}%s${RESET}\n" "$model" "$context_str"
fi
