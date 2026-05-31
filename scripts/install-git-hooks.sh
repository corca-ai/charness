#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_REPO="$SOURCE_ROOT"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      TARGET_REPO="$(cd "$2" && pwd)"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

HOOKS_DIR="$TARGET_REPO/.githooks"
SOURCE_HOOKS_DIR="$SOURCE_ROOT/.githooks"

mkdir -p "$HOOKS_DIR"

if [[ "$TARGET_REPO" == "$SOURCE_ROOT" ]]; then
  if [[ ! -d "$SOURCE_HOOKS_DIR" ]]; then
    echo "Missing source hook directory: $SOURCE_HOOKS_DIR" >&2
    exit 1
  fi
  for hook in "$SOURCE_HOOKS_DIR"/*; do
    [[ -f "$hook" ]] || continue
    chmod +x "$hook"
  done
else
  checker="$SOURCE_ROOT/scripts/check_issue_closeout_commit_msg.py"
  if [[ ! -f "$checker" ]]; then
    echo "Missing issue closeout commit-msg checker: $checker" >&2
    exit 1
  fi
  cat > "$HOOKS_DIR/commit-msg" <<EOF
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="\$(git rev-parse --show-toplevel)"
python3 "$checker" --repo-root "\$REPO_ROOT" --commit-msg-file "\$1"
EOF
  chmod +x "$HOOKS_DIR/commit-msg"
fi

git -C "$TARGET_REPO" config core.hooksPath "$HOOKS_DIR"
echo "Configured core.hooksPath -> $HOOKS_DIR"
echo "Installed hooks:"
find "$HOOKS_DIR" -maxdepth 1 -type f | sort
