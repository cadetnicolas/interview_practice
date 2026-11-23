#!/usr/bin/env bash
# 安装 credit-agent-interview-coach skill，无需交互确认。
#
# 用法：
#   bash scripts/install.sh                 # 自动装到已存在的 agent skills 目录
#   bash scripts/install.sh --target all    # 同时装到 workbuddy 和 cursor
#   bash scripts/install.sh --copy          # 复制而非符号链接（不随仓库更新）
#
# 从任意目录（脚本在 GitHub 上之后）：
#   curl -fsSL https://raw.githubusercontent.com/cadetnicolas/interview_practice/main/scripts/install.sh | bash
set -euo pipefail

REPO_URL="https://github.com/cadetnicolas/interview_practice.git"
SKILL_NAME="credit-agent-interview-coach"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/interview-practice"
MODE="link"
TARGET="auto"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:-auto}"; shift 2 ;;
    --copy) MODE="copy"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "未知参数：$1" >&2; exit 2 ;;
  esac
done

is_ephemeral() {
  case "$1" in
    /tmp/* | /private/tmp/* | "${TMPDIR:-/tmp}"/*) return 0 ;;
    *) return 1 ;;
  esac
}

skill_ready() {
  [[ -f "$1/SKILL.md" ]] && grep -q "^name: ${SKILL_NAME}$" "$1/SKILL.md"
}

sync_cache() {
  export GIT_TERMINAL_PROMPT=0
  mkdir -p "$(dirname "$CACHE_DIR")"
  if [[ -d "$CACHE_DIR/.git" ]]; then
    git -C "$CACHE_DIR" fetch --depth 1 origin >&2
    git -C "$CACHE_DIR" checkout --detach --force FETCH_HEAD >&2
  else
    rm -rf "$CACHE_DIR"
    git clone --depth 1 "$REPO_URL" "$CACHE_DIR" >&2
  fi
  skill_ready "$CACHE_DIR" || { echo "安装失败：缓存仓库里没有合法的 $SKILL_NAME" >&2; exit 1; }
  echo "$CACHE_DIR"
}

resolve_source() {
  local script_path candidate
  script_path="${BASH_SOURCE[0]:-}"
  if [[ -n "$script_path" && -f "$script_path" ]]; then
    candidate="$(cd "$(dirname "$script_path")/.." && pwd)"
    if skill_ready "$candidate" && ! is_ephemeral "$candidate"; then
      echo "$candidate"
      return
    fi
  fi
  sync_cache
}

# 决定装到哪些目录
resolve_targets() {
  local wb="$HOME/.workbuddy/skills" cu="$HOME/.cursor/skills"
  case "$TARGET" in
    workbuddy) echo "$wb" ;;
    cursor) echo "$cu" ;;
    all) echo "$wb"; echo "$cu" ;;
    auto)
      local found=0
      [[ -d "$HOME/.workbuddy" ]] && { echo "$wb"; found=1; }
      [[ -d "$HOME/.cursor" ]] && { echo "$cu"; found=1; }
      [[ $found -eq 0 ]] && echo "$wb"
      ;;
    *) echo "未知 target：$TARGET" >&2; exit 2 ;;
  esac
}

install_into() {
  local source="$1" base="$2"
  local dest="$base/$SKILL_NAME"
  mkdir -p "$base"

  if [[ -L "$dest" ]]; then
    rm "$dest"
  elif [[ -e "$dest" ]]; then
    # 目标已存在且不是链接：备份，不直接删除用户内容
    local backup="${dest}.bak.$(date +%Y%m%d%H%M%S)"
    mv "$dest" "$backup"
    echo "已备份原目录：$backup" >&2
  fi

  if [[ "$MODE" == "copy" ]]; then
    mkdir -p "$dest"
    cp -R "$source/." "$dest/"
  else
    ln -s "$source" "$dest"
  fi
  echo "$dest"
}

main() {
  local source
  source="$(resolve_source)"

  local installed=0
  while IFS= read -r base; do
    [[ -z "$base" ]] && continue
    local dest
    dest="$(install_into "$source" "$base")"
    echo "已安装：$dest"
    installed=$((installed + 1))
  done < <(resolve_targets)

  [[ $installed -eq 0 ]] && { echo "安装失败：没有可用的目标目录" >&2; exit 1; }

  echo "来源：$source"
  echo "模式：$([[ "$MODE" == copy ]] && echo 复制 || echo 符号链接)"
  echo "新开一轮对话，然后说「模拟面试」。"
}

main "$@"
