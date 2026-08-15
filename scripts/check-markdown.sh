#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root != lint-config-root. This block is the canonical statement of that
# rule; check-shell.sh, check-links-external.sh and install-git-hooks.sh carry the same guard
# with a pointer back here.
#
# `$(dirname "${BASH_SOURCE[0]}")/..` is this script's PACKAGE root -- the tree it shipped in.
# That is the RIGHT answer for module resolution (scripts/skill_runtime_bootstrap.py documents
# returning `plugins/<pkg>` in an installed tree as correct) and the WRONG answer for anything
# that measures a git population or resolves a config from cwd. The generated mirror at
# `plugins/charness/` is a plain subdirectory of this repo, so the mirrored copy of this script
# used to `cd` there and then measure from there: `git ls-files` is cwd-scoped, so `AGENTS.md`,
# `README.md`, `CLAUDE.md` and `docs/**` dropped out of the population (542 eligible files from
# the root, 240 from the mirror), the `:(exclude)` pathspecs became cwd-relative and silently
# matched nothing, and the repo's only `.markdownlint-cli2.jsonc` -- the file that sets
# `MD013: false` -- was never resolved, so the mirror run was RED on a clean tree. Issue #618.
#
# Switching unconditionally to `git rev-parse --show-toplevel` is not the fix. A genuinely
# installed plugin is often not in a git repo at all, or sits INSIDE a consumer's repo, where
# the toplevel is the CONSUMER root and this gate would lint the consumer's markdown. That is a
# different wrong answer, not a fix.
#
# So the rule is AGREEMENT, not preference: when git can name a toplevel for the script's own
# root and that toplevel is not the script's own root, this is an exported/mirrored copy and the
# script REFUSES loudly instead of measuring a scope narrower than the one its own comments
# claim. When git cannot name a toplevel (no repo, no git binary) nothing is claimed and the
# package root stands -- the downstream `git ls-files` failure is already loud. Refusing is the
# accepted precedent for the exported copy, recorded at scripts/check-python-lint.sh: the export
# is a tree where these gates cannot run, and that is not a regression.
#
# `CHARNESS_REPO_ROOT` is the escape hatch scripts/runtime_bootstrap.py already defines for the
# Python side; the shell gates reuse that name rather than inventing a second one.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${CHARNESS_REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(cd "$CHARNESS_REPO_ROOT" && pwd)"
else
  git_toplevel="$(git -C "$REPO_ROOT" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$git_toplevel" && "$(cd "$git_toplevel" && pwd -P)" != "$(cd "$REPO_ROOT" && pwd -P)" ]]; then
    {
      echo "check-markdown: refusing to run from an exported copy."
      echo "  script root:  $REPO_ROOT"
      echo "  git toplevel: $git_toplevel"
      echo "This gate measures a git-tracked markdown population and resolves"
      echo ".markdownlint-cli2.jsonc from its root, so a package root that is not the git root"
      echo "would silently lint a narrower tree with no config (issue #618)."
      echo "Run scripts/check-markdown.sh from the charness source checkout, or set"
      echo "CHARNESS_REPO_ROOT to that checkout."
    } >&2
    exit 1
  fi
fi
cd "$REPO_ROOT"

run_git_listing_to_file() {
  local context="$1"
  local output_path="$2"
  shift 2
  local stderr_path rc

  stderr_path="${output_path}.stderr"
  if "$@" >"$output_path" 2>"$stderr_path"; then
    return 0
  else
    rc=$?
  fi

  echo "check-markdown: git file listing failed ($context)" >&2
  printf 'command:' >&2
  printf ' %q' "$@" >&2
  printf '\nexit_code: %s\n' "$rc" >&2
  echo "STDOUT:" >&2
  cat "$output_path" >&2
  echo "STDERR:" >&2
  cat "$stderr_path" >&2
  return 1
}

# Three tiers, cheapest first, because the difference between them is the whole
# runtime of this gate. Measured in a consumer repo on a single 907-line file
# (#630): a direct binary invocation was instant, `npm exec --no` cost ~9.7s, and
# `npm exec` without `--no` cost ~14.8s -- the extra ~5s being npm deciding
# whether to fetch the package from the registry.
#
# So the `--no` matters twice over. It closes the registry path, which is what
# `check-secrets.sh` has always done with `--no-install` and this file did not,
# and it is the difference this gate can pay at commit time. The middle tier is
# what makes the expensive tier rare: a repo that has run `npm install` has the
# binary at `node_modules/.bin/` even when nothing put it on PATH, and reaching
# for npm to locate a file already sitting in the tree is the cost with none of
# the benefit.
#
# `--no` over `--no-install`: both refuse to install, `--no` is the documented
# current spelling, and check-secrets.sh's `--no-install` is the older alias.
# They are not unified here -- changing the secrets gate's invocation is a
# separate behavior change from fixing this one's, and it belongs in its own
# slice with its own proof.
if command -v markdownlint-cli2 >/dev/null 2>&1; then
  MARKDOWNLINT_CMD=(markdownlint-cli2)
elif [[ -x "$REPO_ROOT/node_modules/.bin/markdownlint-cli2" ]]; then
  MARKDOWNLINT_CMD=("$REPO_ROOT/node_modules/.bin/markdownlint-cli2")
elif command -v npm >/dev/null 2>&1; then
  MARKDOWNLINT_CMD=(npm exec --no -- markdownlint-cli2)
else
  echo "markdownlint-cli2 or npm is required for markdown linting." >&2
  exit 1
fi

listing_dir="$(mktemp -d)"
inline_code_pid=""
markdownlint_pid=""
# Invoked through the EXIT trap below; ShellCheck cannot follow that indirect call.
# shellcheck disable=SC2317
cleanup() {
  if [[ -n "$inline_code_pid" ]]; then
    kill "$inline_code_pid" 2>/dev/null || true
  fi
  if [[ -n "$markdownlint_pid" ]]; then
    kill "$markdownlint_pid" 2>/dev/null || true
  fi
  rm -rf "$listing_dir"
}
trap cleanup EXIT
tracked_markdown_list="$listing_dir/tracked-markdown.txt"
run_git_listing_to_file tracked-markdown "$tracked_markdown_list" \
  git ls-files -- '*.md' \
  ':(exclude)charness-artifacts/**' \
  ':(exclude).charness/**' \
  ':(exclude).cautilus/**' \
  ':(exclude).pytest_cache/**'
mapfile -t tracked_markdown_files <"$tracked_markdown_list"

# Optional path arguments SCOPE the lint without changing which files are eligible: the
# candidate set is still the tracked, non-excluded listing above, and arguments only intersect
# with it. A path that the broad gate would not lint is not linted here either, so a scoped run
# can never render a verdict the unscoped run would not — it renders FEWER, never different.
# The commit-time layer passes the staged `.md` files; the broad gate and CI pass nothing and
# lint everything. See docs/conventions/validator-timing-layers.md.
scoped_paths=("$@")
markdown_files=()
for path in "${tracked_markdown_files[@]}"; do
  if [[ ! -f "$path" ]]; then
    continue
  fi
  if [ "${#scoped_paths[@]}" -gt 0 ]; then
    requested=0
    for candidate in "${scoped_paths[@]}"; do
      if [[ "$candidate" == "$path" ]]; then
        requested=1
        break
      fi
    done
    if [ "$requested" -eq 0 ]; then
      continue
    fi
  fi
  markdown_files+=("$path")
done

if [ "${#markdown_files[@]}" -eq 0 ]; then
  echo "No tracked markdown files to lint."
  exit 0
fi

# Advisory (north-star P1): a wrapped inline-code span's rendered output is
# admittedly correct (see the check_markdown_inline_code.py docstring); it only
# risks a literal grep/assertion against the source, a reversible-work smell,
# not a commit-blocking defect. WARN instead of failing this gate so the
# commit boundary no longer bears that burden; the script itself keeps its own
# exit-code semantics for direct callers.
inline_code_log="$listing_dir/inline-code.log"
markdownlint_stdout_log="$listing_dir/markdownlint.stdout.log"
markdownlint_stderr_log="$listing_dir/markdownlint.stderr.log"

# These scans are independent.  Run them together, then emit their logs in a
# fixed advisory-then-blocking order so callers retain stable diagnostics.
# The inline-code scan is repo-wide and has no scoped mode, so a scoped run SKIPS it rather
# than paying a whole-tree scan for a one-file lint. It is already advisory (WARN, never
# blocking, per the P1 note above), and the unscoped broad-gate and CI runs still carry it —
# so skipping costs no verdict, only an earlier warning.
if [ "${#scoped_paths[@]}" -eq 0 ]; then
  python3 "$REPO_ROOT/scripts/check_markdown_inline_code.py" --repo-root "$REPO_ROOT" >"$inline_code_log" 2>&1 &
  inline_code_pid=$!
fi
"${MARKDOWNLINT_CMD[@]}" --no-globs "${markdown_files[@]}" >"$markdownlint_stdout_log" 2>"$markdownlint_stderr_log" &
markdownlint_pid=$!

if [[ -n "$inline_code_pid" ]]; then
  if wait "$inline_code_pid"; then
    cat "$inline_code_log"
  else
    echo "WARN: inline code span check found issue(s) (advisory; rendered output is correct, not blocking):"
    cat "$inline_code_log"
  fi
  inline_code_pid=""
else
  echo "check-markdown: scoped to ${#markdown_files[@]} file(s); repo-wide inline-code advisory not run."
fi

if wait "$markdownlint_pid"; then
  markdownlint_status=0
else
  markdownlint_status=$?
fi
markdownlint_pid=""
# The markdownlint-cli2 banner emits a single `Finding: <space-separated paths>`
# line listing every file it is about to lint. On this repo that line is
# ~50KB (485+ tracked markdown paths), which floods agent context on every
# commit and push without changing lint behavior. Filter it out; per-file
# error lines (`file.md:line:col error MDxxx ...`) do not start with
# `Finding: ` and continue to surface failing file names. See #230 Waste 2.
sed '/^Finding: /d' "$markdownlint_stdout_log"
cat "$markdownlint_stderr_log" >&2
exit "$markdownlint_status"
