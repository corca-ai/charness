#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

run_timed() {
  local label="$1"
  shift
  local start_ns end_ns elapsed_ms rc status
  start_ns="$(date +%s%N)"
  if "$@"; then
    rc=0
    status="pass"
  else
    rc=$?
    status="fail"
  fi
  end_ns="$(date +%s%N)"
  elapsed_ms="$(((end_ns - start_ns) / 1000000))"
  python3 scripts/record_quality_runtime.py \
    --repo-root "$REPO_ROOT" \
    --label "$label" \
    --elapsed-ms "$elapsed_ms" \
    --status "$status" >/dev/null
  return "$rc"
}

run_timed "validate-skills" python3 scripts/validate-skills.py --repo-root "$REPO_ROOT"
run_timed "validate-profiles" python3 scripts/validate-profiles.py --repo-root "$REPO_ROOT"
run_timed "validate-presets" python3 scripts/validate-presets.py --repo-root "$REPO_ROOT"
run_timed "validate-adapters" python3 scripts/validate-adapters.py --repo-root "$REPO_ROOT"
run_timed "validate-integrations" python3 scripts/validate-integrations.py --repo-root "$REPO_ROOT"
run_timed "validate-packaging" python3 scripts/validate-packaging.py --repo-root "$REPO_ROOT"
run_timed "validate-quality-artifact" python3 scripts/validate-quality-artifact.py --repo-root "$REPO_ROOT"
run_timed "validate-maintainer-setup" python3 scripts/validate-maintainer-setup.py --repo-root "$REPO_ROOT"
run_timed "check-python-lengths" python3 scripts/check-python-lengths.py --repo-root "$REPO_ROOT"
run_timed "check-skill-contracts" python3 scripts/check-skill-contracts.py --repo-root "$REPO_ROOT"
run_timed "check-doc-links" python3 scripts/check-doc-links.py --repo-root "$REPO_ROOT"
run_timed "check-markdown" ./scripts/check-markdown.sh
run_timed "check-secrets" ./scripts/check-secrets.sh
run_timed "check-shell" ./scripts/check-shell.sh
run_timed "check-links-external" ./scripts/check-links-external.sh
shopt -s nullglob
python_files=(
  scripts/*.py
  skills/public/*/scripts/*.py
  skills/support/*/scripts/*.py
  skills/support/*/vendor/*.py
)
run_timed "py-compile" python3 -m py_compile "${python_files[@]}"
run_timed "ruff" ruff check scripts tests skills/public/*/scripts skills/support/*/scripts
run_timed "pytest" pytest -q
run_timed "run-evals" python3 scripts/run-evals.py --repo-root "$REPO_ROOT"
run_timed "check-duplicates" python3 scripts/check-duplicates.py --repo-root "$REPO_ROOT" --fail-on-match
