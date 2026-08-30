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

# package-root != git-root. The full rule is written out in scripts/exported-copy-guard.sh. Here it
# is not a measurement bug but a DESTRUCTIVE one, because `git config` is repo-scoped and not
# directory-scoped.
#
# `SOURCE_ROOT` above is a package root and is used correctly as one -- it locates `.githooks/`
# and `check_issue_closeout_commit_msg.py` inside the tree this script shipped in. `TARGET_REPO`
# is a GIT root, and defaulting it to the package root is what broke: run bare from the
# generated mirror, this script took the same-root branch and ran
# `git -C plugins/charness config core.hooksPath plugins/charness/.githooks`, which DISABLES THE
# WHOLE REPO'S pre-commit/pre-push hooks -- `git config` writes to the enclosing repository's
# config no matter which subdirectory `-C` names -- while printing a success line and an empty
# `find` listing. With `--repo-root <consumer>` it was correct, which is exactly why the failure
# was silent.
#
# So `TARGET_REPO` must BE the toplevel of the repository it is about to reconfigure, whether it
# came from the default or from `--repo-root`. Validating both branches is what removes the
# class rather than the one reported path. This is checked before `mkdir -p "$HOOKS_DIR"` so a
# refused run leaves no `.githooks/` behind in a tree it should not have touched. No
# `CHARNESS_REPO_ROOT` hatch here: `--repo-root` is already the explicit way to name the target.
TARGET_TOPLEVEL="$(git -C "$TARGET_REPO" rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$TARGET_TOPLEVEL" ]]; then
  {
    echo "install-git-hooks: refusing to configure hooks for a non-repository."
    echo "  target: $TARGET_REPO"
    echo "git config core.hooksPath needs a git repository. Run this from a charness clone, or"
    echo "pass --repo-root <path-to-a-git-repository>."
  } >&2
  exit 1
fi
if [[ "$(cd "$TARGET_TOPLEVEL" && pwd -P)" != "$(cd "$TARGET_REPO" && pwd -P)" ]]; then
  {
    echo "install-git-hooks: refusing to configure hooks from a subdirectory of a repository."
    echo "  target:       $TARGET_REPO"
    echo "  git toplevel: $TARGET_TOPLEVEL"
    echo "git config is repo-scoped, not directory-scoped: configuring core.hooksPath here would"
    echo "repoint the ENTIRE repository at $HOOKS_DIR and disable its real hooks (issue #618"
    echo "class; the exported copy under plugins/charness is not meant to run)."
    echo "Run scripts/install-git-hooks.sh from the charness source checkout, or pass"
    echo "--repo-root $TARGET_TOPLEVEL."
  } >&2
  exit 1
fi

mkdir -p "$HOOKS_DIR"

if [[ "$TARGET_REPO" == "$SOURCE_ROOT" ]]; then
  if [[ ! -d "$SOURCE_HOOKS_DIR" ]]; then
    echo "Missing source hook directory: $SOURCE_HOOKS_DIR" >&2
    exit 1
  fi
  for hook in "$SOURCE_HOOKS_DIR"/*; do
    [[ -f "$hook" ]] || continue
    # Only direct Git hook entrypoints need execute permission. `runtime-env.sh`
    # is sourced by those hooks; chmodding every helper dirtied a clean source
    # clone during the maintainer setup that release quality itself requires.
    case "$(basename "$hook")" in
      commit-msg|pre-commit|pre-push) chmod +x "$hook" ;;
    esac
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
source "$SOURCE_ROOT/.githooks/runtime-env.sh"
python3 "$checker" --repo-root "\$REPO_ROOT" --commit-msg-file "\$1"
EOF
  chmod +x "$HOOKS_DIR/commit-msg"
fi

git -C "$TARGET_REPO" config core.hooksPath "$HOOKS_DIR"
echo "Configured core.hooksPath -> $HOOKS_DIR"
echo "Installed hooks:"
find "$HOOKS_DIR" -maxdepth 1 -type f | sort
