#!/bin/bash
# skill とプラグインを、導入や更新の前に NVIDIA SkillSpector で検査する。
# /skill-install と /skill-update が使い、PreToolUse フックとしても動く。
#
# usage:
#   skill-guard.sh scan <dir> --name <name> [--since <installed>]
#                                                検査して PASS / REVIEW / BLOCK を判定する。--since は
#                                                前に検査を通した記録があれば差分だけを検査する
#   skill-guard.sh approve <report.json>         利用者が承認した REVIEW にトークンを出す
#   skill-guard.sh baseline <dir> --name <name> --reason <text>
#                                                今ある指摘を受け入れる baseline を作る
#   skill-guard.sh fetch-plugin <catalog> <plugin> <out>
#                                                カタログの source からプラグインを取り出す
#   skill-guard.sh verify <scanned> <installed>  検査した中身と入った中身を突き合わせる
#   skill-guard.sh hook                          PreToolUse フック（stdin に JSON）
#
# scan の終了コード: 0 PASS、1 REVIEW、2 BLOCK、3 検査できなかった
set -uo pipefail

VERSION=2.13.2
IMAGE="skillspector:$VERSION"
GUARD_DIR="$HOME/.claude/skill-guard"
CACHE="$HOME/.cache/skill-guard"
TOKEN_TTL=3600

die() { echo "skill-guard: $*" >&2; exit 3; }

ensure_docker() {
  docker info >/dev/null 2>&1 && return
  command -v colima >/dev/null || die "Docker に接続できない"
  colima start >&2 || die "colima start に失敗した"
}

ensure_image() {
  docker image inspect "$IMAGE" >/dev/null 2>&1 && return
  local src="$CACHE/skillspector-src"
  rm -rf "$src"
  git clone -q --depth 1 --branch "v$VERSION" https://github.com/NVIDIA/SkillSpector.git "$src" 2>/dev/null \
    || die "SkillSpector の取得に失敗した"
  docker build -q -t "$IMAGE" "$src" >&2 || die "イメージのビルドに失敗した"
}

# Colima は $HOME しかマウントしないので、実体が $HOME 配下にあるか確かめる
resolve_dir() {
  local dir
  dir=$(cd "$1" 2>/dev/null && pwd -P) || die "ディレクトリが無い: $1"
  case "$dir" in "$HOME"/*) ;; *) die "\$HOME 配下に置く: $dir" ;; esac
  echo "$dir"
}

issue_token() {
  local token
  token=$(od -An -tx1 -N16 /dev/urandom | tr -d ' \n')
  mkdir -p "$CACHE/tokens"
  printf '%s\t%s\n' "$1" "$2" >"$CACHE/tokens/$token"
  echo "token: $token"
}

# reference_missing は SKILL.md 内の ~/.claude などのパスでほぼ必ず出るので、不完全の理由から外す
VERDICT_JQ='
def high: .severity == "HIGH" or .severity == "CRITICAL";
(.analysis_completeness.ledger_exceptions // []) as $ex
| if .execution_successful == false then "BLOCK"
  elif .risk_assessment.score > 50 then "BLOCK"
  elif any($ex[]; .fatal) then "BLOCK"
  elif any(.issues[]; high) then "REVIEW"
  elif .risk_assessment.score > 20 then "REVIEW"
  elif any($ex[]; .reason_code != "reference_missing") then "REVIEW"
  else "PASS" end'

SUMMARY_JQ='
def high: .severity == "HIGH" or .severity == "CRITICAL";
"score: \(.risk_assessment.score) (\(.risk_assessment.recommendation))",
"issues: \(.issues | length)（baseline で抑止: \(.suppressed_count // 0)）",
(.issues | group_by(.id) | sort_by(-(.[0].severity | {"CRITICAL":4,"HIGH":3,"MEDIUM":2,"LOW":1}[.] // 0))
  | .[] | "  \(.[0].severity) \(.[0].id) x\(length) \(.[0].pattern // .[0].category)"),
(if any(.issues[]; high) then "HIGH 以上の箇所（先頭 20 件）:" else empty end),
(.issues | map(select(high)) | .[0:20][]
  | "  \(.severity) \(.id) \(.location.file):\(.location.start_line)"),
((.analysis_completeness.ledger_exceptions // []) | select(length > 0)
  | "incomplete: " + (group_by(.reason_code) | map("\(.[0].reason_code) x\(length)") | join(", ")))'

# 前に PASS、承認済みの REVIEW、baseline のどれかがあれば、導入済みの中身は検査を通したとみなす
vetted() {
  local v
  [ -f "$GUARD_DIR/baselines/$1.yaml" ] && return 0
  for v in "$CACHE/reports/$1"-[0-9]*.json.verdict; do
    [ -f "$v" ] || continue
    [ "$(cut -f1 "$v")" = PASS ] && return 0
    [ -f "${v%.verdict}.approved" ] && return 0
  done
  return 1
}

# 導入済みから変わったファイルと、判定に要るマニフェストと SKILL.md だけを写す
stage_diff() {
  local new=$1 old=$2 out=$3
  local ex=(--exclude .git --exclude .in_use --exclude node_modules --exclude __pycache__ --exclude .DS_Store)
  rm -rf "$out"
  mkdir -p "$out"
  {
    rsync -rcn "${ex[@]}" --out-format='%n' "$new/" "$old/" | grep -v '/$'
    (cd "$new" && find . -name .git -prune -o \( -path './.claude-plugin/*' -o -path './hooks/*' -o -name SKILL.md \) \
      -type f -print | sed 's#^\./##')
  } | sort -u >"$out.list"
  rsync -a --files-from="$out.list" "$new/" "$out/" || die "差分の写しに失敗した"
}

cmd_scan() {
  local dir="" name="" since=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --name) name=${2:-}; shift 2 ;;
      --since) since=${2:-}; shift 2 ;;
      *) dir=$1; shift ;;
    esac
  done
  [ -n "$dir" ] && [ -n "$name" ] || die "usage: scan <dir> --name <name> [--since <installed>]"
  dir=$(resolve_dir "$dir")
  ensure_docker
  ensure_image

  mkdir -p "$CACHE/reports"
  local stamp scope="full"
  stamp=$(date +%Y%m%d-%H%M%S)
  if [ -n "$since" ]; then
    if [ -d "$since" ] && vetted "$name"; then
      stage_diff "$dir" "$since" "$CACHE/diff/$name-$stamp"
      scope="diff（$(wc -l <"$CACHE/diff/$name-$stamp.list" | tr -d ' ') / $(find "$dir" -type f | wc -l | tr -d ' ') ファイル）"
      dir="$CACHE/diff/$name-$stamp"
    else
      scope="full（前に検査を通した記録が無い）"
    fi
  fi
  local report="$CACHE/reports/$name-$stamp.json"
  local baseline="$GUARD_DIR/baselines/$name.yaml"
  local mounts=(-v "$dir:/scan/target:ro") extra=()
  if [ -f "$baseline" ]; then
    mounts+=(-v "$baseline:/scan/baseline.yaml:ro")
    extra+=(--baseline /scan/baseline.yaml)
  fi

  docker run --rm "${mounts[@]}" "$IMAGE" scan ./target/ --no-llm --format json \
    ${extra[@]+"${extra[@]}"} >"$report" 2>"$report.log"
  local rc=$?
  if [ "$rc" -gt 1 ] || ! jq -e . "$report" >/dev/null 2>&1; then
    tail -5 "$report.log" >&2
    die "検査できなかった（終了コード ${rc}）。log: $report.log"
  fi

  local verdict
  verdict=$(jq -r "$VERDICT_JQ" "$report")
  printf '%s\t%s\t%s\n' "$verdict" "$name" "$dir" >"$report.verdict"

  echo "verdict: $verdict"
  echo "target: $dir"
  echo "scope: $scope"
  [ -f "$baseline" ] && echo "baseline: $baseline"
  jq -r "$SUMMARY_JQ" "$report"
  echo "report: $report"
  case "$verdict" in
    PASS)
      issue_token "$name" "$dir"
      exit 0 ;;
    REVIEW)
      echo "次: 指摘を利用者に示して承認を求める。承認されたら approve $report でトークンを取る"
      exit 1 ;;
    BLOCK)
      echo "次: 中止して指摘を報告する。利用者が指摘を確かめたうえで受け入れると明言した場合だけ baseline を作って検査し直せる"
      exit 2 ;;
  esac
}

cmd_approve() {
  local report=${1:-} verdict name dir
  [ -f "$report.verdict" ] || die "検査結果が無い: $report"
  IFS=$'\t' read -r verdict name dir <"$report.verdict"
  [ "$verdict" = REVIEW ] || die "approve できるのは REVIEW だけ（${verdict}）"
  touch "$report.approved"
  issue_token "$name" "$dir"
}

cmd_baseline() {
  local dir="" name="" reason=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --name) name=${2:-}; shift 2 ;;
      --reason) reason=${2:-}; shift 2 ;;
      *) dir=$1; shift ;;
    esac
  done
  [ -n "$dir" ] && [ -n "$name" ] && [ -n "$reason" ] || die "usage: baseline <dir> --name <name> --reason <text>"
  dir=$(resolve_dir "$dir")
  ensure_docker
  ensure_image
  mkdir -p "$GUARD_DIR/baselines"
  docker run --rm --user "$(id -u):$(id -g)" -v "$dir:/scan/target:ro" -v "$GUARD_DIR/baselines:/out" \
    "$IMAGE" baseline ./target/ -o "/out/$name.yaml" --no-llm --reason "$reason" >&2 \
    || die "baseline の作成に失敗した"
  echo "baseline: $GUARD_DIR/baselines/$name.yaml"
}

# 対応する source は相対パス、github、url、git-subdir。npm などは扱わない
cmd_fetch_plugin() {
  local catalog=${1:-} plugin=${2:-} out=${3:-}
  [ -n "$catalog" ] && [ -n "$plugin" ] && [ -n "$out" ] || die "usage: fetch-plugin <catalog> <plugin> <out>"
  local manifest="$catalog/.claude-plugin/marketplace.json" src kind
  src=$(jq -c --arg p "$plugin" '.plugins[] | select(.name == $p) | .source' "$manifest" 2>/dev/null)
  [ -n "$src" ] || die "カタログに無い: $plugin"
  kind=$(jq -r 'if type == "string" then "path" else .source end' <<<"$src")
  rm -rf "$out" "$out.repo"
  mkdir -p "$out"
  case "$kind" in
    path)
      local rel root
      rel=$(jq -r . <<<"$src")
      root=$(jq -r '.metadata.pluginRoot // empty' "$manifest")
      case "$rel" in ./* | ../*) ;; *) [ -n "$root" ] && rel="$root/$rel" ;; esac
      rsync -a --exclude .git "$catalog/$rel/" "$out/" || die "コピーに失敗した: $catalog/$rel"
      ;;
    github | url | git-subdir)
      local url ref sub
      url=$(jq -r 'if .source == "github" then "https://github.com/\(.repo).git" else .url end' <<<"$src")
      ref=$(jq -r '.sha // .ref // empty' <<<"$src")
      sub=$(jq -r '.path // empty' <<<"$src")
      git clone -q --filter=blob:none "$url" "$out.repo" 2>/dev/null || die "clone に失敗した: $url"
      if [ -n "$ref" ]; then
        git -C "$out.repo" checkout -q "$ref" 2>/dev/null || die "checkout に失敗した: $ref"
      fi
      rsync -a --exclude .git "$out.repo/${sub:+$sub/}" "$out/" || die "コピーに失敗した: $sub"
      echo "commit: $(git -C "$out.repo" rev-parse HEAD)" >&2
      rm -rf "$out.repo"
      ;;
    *) die "未対応の source: $kind" ;;
  esac
  echo "$out"
}

# node_modules は Claude Code が導入時に入れるもので、検査した中身には無い
cmd_verify() {
  [ $# -eq 2 ] || die "usage: verify <scanned> <installed>"
  diff -rq -x .git -x .in_use -x node_modules -x __pycache__ -x .DS_Store "$1" "$2"
}

# skill とプラグインを入れるコマンドを、有効なトークンが付いていなければ止める
cmd_hook() {
  local input cmd cwd
  input=$(cat)
  cmd=$(jq -r '.tool_input.command // empty' <<<"$input")
  cwd=$(jq -r '.cwd // empty' <<<"$input")
  [ -n "$cmd" ] || exit 0

  local installed='(~|\$HOME|\$\{HOME\}|'"$HOME"')/\.(claude|agents)/skills'
  local hit=""
  grep -Eq 'claude +plugins? +(install|i|update)( |$)' <<<"$cmd" && hit=1
  grep -Eq '(^|[ /;&|(])skills(@[^ ]*)? +(add|update)( |$)' <<<"$cmd" && hit=1
  # git は区切り（&& || ; |）ごとに、導入先を指すか、導入先へ cd した後かで判定する
  local seg incd=""
  case "$cwd" in "$HOME"/.claude/skills* | "$HOME"/.agents/skills*) incd=1 ;; esac
  while IFS= read -r seg; do
    grep -Eq "^[[:space:]]*cd[[:space:]].*$installed" <<<"$seg" && incd=1
    grep -Eq '(^|[ (])git .*(clone|pull|merge|reset|checkout|switch|rebase)( |$)' <<<"$seg" || continue
    { [ -n "$incd" ] || grep -Eq "$installed" <<<"$seg"; } && hit=1
  done < <(sed -E 's/(&&|\|\||;|\|)/\n/g' <<<"$cmd")
  [ -n "$hit" ] || exit 0

  local token file name
  token=$(grep -Eo 'SKILL_GUARD_TOKEN=[0-9a-f]{32}' <<<"$cmd" | head -1 | cut -d= -f2)
  file="$CACHE/tokens/$token"
  if [ -n "$token" ] && [ -f "$file" ] \
    && [ $(($(date +%s) - $(stat -f %m "$file"))) -le "$TOKEN_TTL" ]; then
    name=$(cut -f1 "$file")
    grep -Fq -- "$name" <<<"$cmd" && exit 0
  fi

  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny",
    permissionDecisionReason: "skill とプラグインの導入・更新は SkillSpector の検査を通す。利用者に /skill-install <配布元> か /skill-update [名前] の実行を頼む。skill の手順の中なら、skill-guard.sh が発行した 1 時間以内のトークンを SKILL_GUARD_TOKEN=<token> としてコマンドの先頭に付け、対象の名前をコマンドに含める。"}}'
  exit 0
}

case "${1:-}" in
  scan) shift; cmd_scan "$@" ;;
  approve) shift; cmd_approve "$@" ;;
  baseline) shift; cmd_baseline "$@" ;;
  fetch-plugin) shift; cmd_fetch_plugin "$@" ;;
  verify) shift; cmd_verify "$@" ;;
  hook) shift; cmd_hook "$@" ;;
  *) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 3 ;;
esac
