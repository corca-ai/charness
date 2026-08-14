#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root. The full rule, and why `git rev-parse --show-toplevel` alone is not
# the fix, is written out in scripts/check-markdown.sh; keep the two guards in step.
#
# This copy's failure was worse than #618's because it was GREEN. The whole population comes
# from `find` against the cwd, so the mirrored copy at `plugins/charness/scripts/` found no
# top-level `*.sh` (no `init.sh` there), found the ten mirrored `scripts/*.sh`, and skipped both
# the `tests/` and `.githooks/` branches because neither directory exists in the mirror. It then
# linted ten files and exited 0 while never seeing `init.sh`, `tests/**/*.sh`, or `.githooks/*`.
# A silent scope shrink under a passing verdict is strictly worse than a red one: nothing looks
# wrong. `REPO_ROOT_VERIFIED` below exists so the empty-population exit can tell "we know this
# root and discovery came back empty" (a broken discovery list) from "we could not confirm the
# root" (the pre-existing, deliberately tolerant behavior).
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT_VERIFIED=0
if [[ -n "${CHARNESS_REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(cd "$CHARNESS_REPO_ROOT" && pwd)"
  REPO_ROOT_VERIFIED=1
else
  git_toplevel="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$git_toplevel" ]]; then
    if [[ "$(cd "$git_toplevel" && pwd -P)" != "$(cd "$REPO_ROOT" && pwd -P)" ]]; then
      {
        echo "check-shell: refusing to run from an exported copy."
        echo "  script root:  $REPO_ROOT"
        echo "  git toplevel: $git_toplevel"
        echo "This gate discovers shell files by walking its own root, so a package root that is"
        echo "not the git root lints a narrower tree and still exits 0 (issue #618 class)."
        echo "Run scripts/check-shell.sh from the charness source checkout, or set"
        echo "CHARNESS_REPO_ROOT to that checkout."
      } >&2
      exit 1
    fi
    REPO_ROOT_VERIFIED=1
  fi
fi
cd "$REPO_ROOT"

if ! command -v shellcheck >/dev/null 2>&1; then
  echo "shellcheck unavailable; skipping shell lint." >&2
  exit 0
fi

listing_dir="$(mktemp -d)"
trap 'rm -rf "$listing_dir"' EXIT
listing_path="$listing_dir/shell-files.txt"
listing_stderr_path="$listing_dir/shell-files.stderr"

collect_shell_files() {
  find . -maxdepth 1 -type f -name '*.sh' || return "$?"
  find scripts -maxdepth 1 -type f -name '*.sh' || return "$?"
  if [[ -d tests ]]; then
    find tests -type f -name '*.sh' || return "$?"
  fi
  if [[ -d .githooks ]]; then
    find .githooks -maxdepth 1 -type f || return "$?"
  fi
}

if collect_shell_files 2>"$listing_stderr_path" | sort >"$listing_path"; then
  mapfile -t sh_files <"$listing_path"
else
  rc=$?
  echo "check-shell: shell file discovery failed." >&2
  echo "command: { find . -maxdepth 1 -type f -name '*.sh'; find scripts -maxdepth 1 -type f -name '*.sh'; find tests -type f -name '*.sh' when present; find .githooks -maxdepth 1 -type f when present; } | sort" >&2
  printf 'exit_code: %s\n' "$rc" >&2
  echo "STDOUT:" >&2
  cat "$listing_path" >&2
  echo "STDERR:" >&2
  cat "$listing_stderr_path" >&2
  exit 1
fi

if [ "${#sh_files[@]}" -eq 0 ]; then
  # An empty population is only honestly green when the root is unconfirmed -- a tree that may
  # simply have no shell files, which is why `shellcheck` is not invoked with zero arguments.
  # From a root we KNOW (git toplevel, or an operator-asserted CHARNESS_REPO_ROOT) an empty
  # result cannot mean "no shell files": this script is itself `scripts/check-shell.sh`, so the
  # discovery list found nothing where it must find at least itself. Reporting 0 there would be
  # the same false green the root guard above was added to close.
  if [ "$REPO_ROOT_VERIFIED" -eq 1 ]; then
    echo "check-shell: no shell files discovered under $REPO_ROOT." >&2
    echo "The discovery list cannot see this script itself; it is wrong, not the tree." >&2
    exit 1
  fi
  exit 0
fi

shellcheck -x "${sh_files[@]}"
