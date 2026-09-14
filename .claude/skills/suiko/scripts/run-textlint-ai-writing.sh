#!/bin/sh
set -eu

if [ "$#" -eq 0 ]; then
    echo "usage: run-textlint-ai-writing.sh <file> [file ...]" >&2
    exit 2
fi

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    echo "textlint check skipped: Node.js and npm are required" >&2
    exit 3
fi

if ! node -e 'const [major, minor] = process.versions.node.split(".").map(Number); process.exit(major > 20 || (major === 20 && minor >= 18) ? 0 : 1)'; then
    echo "textlint check skipped: Node.js 20.18 or later is required" >&2
    exit 3
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
config="$script_dir/textlint-ai-writing.rc.json"

if [ ! -f "$config" ]; then
    echo "textlint check skipped: config not found at $config" >&2
    exit 3
fi

# The two --package lists below must stay identical: npm keys its temporary
# exec directory by the package set, so a mismatch would resolve the presets
# from a different directory than the one that gets linted.

# The presets live in that temporary directory, which textlint cannot find
# from the config file's own location, so resolve it here and pass it through
# --rules-base-directory.
rules_base=$(npm exec --yes \
    --package=textlint@15.8.0 \
    --package=@textlint-ja/textlint-rule-preset-ai-writing@1.7.0 \
    --package=textlint-rule-preset-ai-words-ja@1.2.0 \
    -- node -p 'require("path").resolve(process.env.PATH.split(require("path").delimiter)[0], "..")' \
    2>/dev/null) || rules_base=""

if [ -z "$rules_base" ]; then
    echo "textlint check skipped: could not resolve the textlint preset directory" >&2
    exit 3
fi

# --no-textlintrc is not used because it would cancel --config. Passing
# --config already disables discovery of a project .textlintrc, so the run
# stays isolated from project settings.
exec npm exec --yes \
    --package=textlint@15.8.0 \
    --package=@textlint-ja/textlint-rule-preset-ai-writing@1.7.0 \
    --package=textlint-rule-preset-ai-words-ja@1.2.0 \
    -- textlint \
    --config "$config" \
    --rules-base-directory "$rules_base" \
    --format json \
    -- "$@"
