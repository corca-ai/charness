#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

if command -v markdownlint-cli2 >/dev/null 2>&1; then
  MARKDOWNLINT_CMD=(markdownlint-cli2)
elif command -v npm >/dev/null 2>&1; then
  MARKDOWNLINT_CMD=(npm exec -- markdownlint-cli2)
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
