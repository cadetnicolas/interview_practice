#!/usr/bin/env bash
# Install the interview-practice skill for Cursor without prompts.
# Usage:
#   bash scripts/install.sh
# From any directory, after this file is on GitHub:
#   curl -fsSL https://raw.githubusercontent.com/cadetnicolas/interview_practice/main/scripts/install.sh | bash
set -euo pipefail

REPO_URL="https://github.com/cadetnicolas/interview_practice.git"
SKILL_NAME="interview-practice"
SKILL_REL="plugins/interview-practice/skills/interview-practice"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/interview-practice"

is_ephemeral() {
  case "$1" in
    /tmp/* | /private/tmp/* | "${TMPDIR:-/tmp}"/*) return 0 ;;
    *) return 1 ;;
  esac
}

skill_ready() {
  [[ -f "$1/$SKILL_REL/SKILL.md" ]]
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
  if ! skill_ready "$CACHE_DIR"; then
    echo "安装失败：缓存仓库里没有 $SKILL_REL/SKILL.md" >&2
    exit 1
  fi
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

link_skill() {
  local source="$1"
  local dest="$HOME/.cursor/skills/$SKILL_NAME"
  local skill_dir="$source/$SKILL_REL"

  mkdir -p "$HOME/.cursor/skills"
  if [[ -L "$dest" ]]; then
    rm "$dest"
  elif [[ -e "$dest" ]]; then
    if [[ -f "$dest/SKILL.md" ]] && grep -q '^name: interview-practice$' "$dest/SKILL.md"; then
      rm -rf "$dest"
    else
      echo "安装失败：$dest 已存在，且不是 interview-practice。" >&2
      exit 1
    fi
  fi
  ln -s "$skill_dir" "$dest"
  echo "$dest"
}

main() {
  local source dest
  source="$(resolve_source)"
  dest="$(link_skill "$source")"
  echo "已安装 interview-practice"
  echo "来源：$source/$SKILL_REL"
  echo "位置：$dest"
  echo "请新开一轮对话，然后说「模拟面试」。"
}

main "$@"
