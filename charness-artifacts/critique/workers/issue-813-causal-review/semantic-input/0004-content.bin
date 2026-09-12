#!/usr/bin/env bash
set -euo pipefail

# package-root != git-root != lint-config-root. The rule, why `git rev-parse --show-toplevel`
# alone is not the fix, and the one implementation of the refusal all live in
# scripts/exported-copy-guard.sh. What belongs HERE is this gate's own measured consequence:
# the mirrored copy used to `cd` into `plugins/charness` and measure from there, so `git
# ls-files` (cwd-scoped) dropped `AGENTS.md`, `README.md`, `CLAUDE.md` and `docs/**` from the
# population (542 eligible files from the root, 240 from the mirror), the `:(exclude)`
# pathspecs became cwd-relative and silently matched nothing, and the repo's only
# `.markdownlint-cli2.jsonc` -- the file that sets `MD013: false` -- was never resolved, so
# the mirror run was RED on a clean tree. Issue #618.
GATE_NAME="check-markdown"
GATE_CONSEQUENCE="This gate measures a git-tracked markdown population and resolves
.markdownlint-cli2.jsonc from its root, so a package root that is not the git root
would silently lint a narrower tree with no config."
# Builtin-only, no `dirname`: this is the FIRST thing every gate does, and a run with
# an empty PATH (a real fixture shape) would otherwise die on a missing external
# command before the gate could report anything of its own. The existence check is
# what keeps a relocated or symlinked copy refusing BY NAME instead of dying on a
# bash "No such file or directory". (A bare name from PATH is fine: execvp resolves
# it to an absolute path before bash runs, so BASH_SOURCE[0] carries a directory.)
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "check-markdown: cannot locate exported-copy-guard.sh beside this script" >&2
  echo "  looked in: $CHARNESS_GATE_DIR" >&2
  echo "The guard must sit beside this script. A copy relocated on its own, or a symlink" >&2
  echo "whose own directory has no guard, reaches this." >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=1
# shellcheck source-path=SCRIPTDIR
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

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
  # The VERDICT is authoritative; cleanup is best-effort. `set -e` is in force in an
  # EXIT trap on the ordinary exit path, so a bare `rm -rf` that fails aborts the trap
  # and the gate exits with the `rm`'s status instead of its own verdict. This is the
  # worst instance of that shape in the repo rather than a theoretical one: the two
  # `kill`s above are sent to children that are writing into `$listing_dir`, so racing
  # the removal against a still-flushing child is the DESIGNED teardown order, and the
  # result would be `FAIL check-markdown` on a clean tree.
  local rc=$?
  if [[ -n "$inline_code_pid" ]]; then
    kill "$inline_code_pid" 2>/dev/null || true
  fi
  if [[ -n "$markdownlint_pid" ]]; then
    kill "$markdownlint_pid" 2>/dev/null || true
  fi
  rm -rf "$listing_dir" ||
    echo "check-markdown: warning: could not remove $listing_dir" >&2 || :
  exit "$rc"
}
trap cleanup EXIT
tracked_markdown_list="$listing_dir/tracked-markdown.txt"
run_git_listing_to_file tracked-markdown "$tracked_markdown_list" \
  git ls-files -- '*.md' \
  ':(exclude)charness-artifacts/**' \
  ':(exclude).charness/**' \
  ':(exclude).pytest_cache/**'
mapfile -t tracked_markdown_files <"$tracked_markdown_list"

# Optional path arguments SCOPE the lint without changing which files are eligible: the
# candidate set is still the tracked, non-excluded listing above, and arguments only intersect
# with it. A path that the broad gate would not lint is not linted here either, so a scoped run
# can never render a verdict the unscoped run would not — it renders FEWER, never different.
# The commit-time layer passes the staged `.md` files; the broad gate and CI pass nothing and
# lint everything. See docs/validator-timing-layers.md.
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
  python3 "$REPO_ROOT/scripts/gates/check_markdown_inline_code.py" --repo-root "$REPO_ROOT" >"$inline_code_log" 2>&1 &
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
