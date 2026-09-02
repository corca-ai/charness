#!/usr/bin/env bash
set -u

# One operator-facing docs gate. The component scripts remain directly callable
# for focused diagnosis, but this is the single contract used by quality and
# pre-push: Markdown syntax, current-doc graph, command contracts, repo-local
# references, and lychee link checks are one verdict.
GATE_NAME="check-docs"
GATE_CONSEQUENCE="This gate runs the maintained docs population through syntax,
graph, command-contract, reference, and link checks as one receipt; a component failure is never
hidden behind a passing sibling."
CHARNESS_GATE_DIR="${BASH_SOURCE[0]%/*}"
if [[ "$CHARNESS_GATE_DIR" == "${BASH_SOURCE[0]}" ]]; then CHARNESS_GATE_DIR="."; fi
if [[ ! -f "$CHARNESS_GATE_DIR/exported-copy-guard.sh" ]]; then
  echo "check-docs: cannot locate exported-copy-guard.sh beside this script" >&2
  exit 2
fi
GATE_ACCEPTS_REPO_ROOT_HATCH=1
# shellcheck source=scripts/exported-copy-guard.sh
source "$CHARNESS_GATE_DIR/exported-copy-guard.sh"

run_component() {
  case "$1" in
    check-last-verified)
      python3 -m tools.check_last_verified --repo-root "$REPO_ROOT" ;;
    check-markdown) "$CHARNESS_GATE_DIR/check-markdown.sh" ;;
    check-doc-links) python3 "$REPO_ROOT/scripts/check_doc_links.py" --repo-root "$REPO_ROOT" --require-git-file-listing ;;
    check-plugin-doc-links) python3 -m tools.check_plugin_doc_links --repo-root "$REPO_ROOT" ;;
    check-command-docs) python3 "$REPO_ROOT/scripts/check_command_docs.py" --repo-root "$REPO_ROOT" ;;
    docs-graph)
      # Exit 3 is soft only when awiki is genuinely unavailable. Once awiki is
      # present, a 3 means the observer failed to establish a graph verdict.
      python3 "$REPO_ROOT/scripts/check_docs_graph.py" --repo-root "$REPO_ROOT"
      rc=$?
      if command -v awiki >/dev/null 2>&1 && (( rc == 3 )); then return 1; fi
      return "$rc"
      ;;
    check-links-internal) "$CHARNESS_GATE_DIR/check-links-internal.sh" ;;
    check-links-external) "$CHARNESS_GATE_DIR/check-links-external.sh" ;;
    *) echo "check-docs: unknown component $1" >&2; return 2 ;;
  esac
}

declare -a checks=(
  check-markdown
  check-doc-links
  check-command-docs
  docs-graph
  check-links-internal
  check-links-external
)
if [[ -d "$REPO_ROOT/tools" ]]; then
  checks=(check-last-verified check-plugin-doc-links "${checks[@]}")
fi

status=0
unproven=0
for label in "${checks[@]}"; do
  echo "== $label =="
  run_component "$label"
  rc=$?
  if (( rc != 0 )); then
    echo "FAIL $label (exit $rc)" >&2
    if (( rc == 3 )); then
      unproven=1
    else
      status=1
    fi
  fi
done

if (( status == 0 )); then
  if (( unproven )); then
    echo "UNPROVEN check-docs (a docs component could not establish its scope)" >&2
    exit 3
  fi
  echo "PASS check-docs (markdown, graph, command contracts, references, and links)"
else
  echo "FAIL check-docs (one or more docs components failed)" >&2
fi
exit "$status"
