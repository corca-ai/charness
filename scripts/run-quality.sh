#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

python3 scripts/validate-skills.py --repo-root "$REPO_ROOT"
python3 scripts/validate-profiles.py --repo-root "$REPO_ROOT"
python3 scripts/validate-presets.py --repo-root "$REPO_ROOT"
python3 scripts/validate-adapters.py --repo-root "$REPO_ROOT"
python3 scripts/validate-integrations.py --repo-root "$REPO_ROOT"
python3 scripts/validate-packaging.py --repo-root "$REPO_ROOT"
python3 scripts/validate-quality-artifact.py --repo-root "$REPO_ROOT"
python3 scripts/validate-maintainer-setup.py --repo-root "$REPO_ROOT"
python3 scripts/check-python-lengths.py --repo-root "$REPO_ROOT"
python3 scripts/check-skill-contracts.py --repo-root "$REPO_ROOT"
python3 scripts/check-doc-links.py --repo-root "$REPO_ROOT"
./scripts/check-markdown.sh
./scripts/check-secrets.sh
./scripts/check-shell.sh
./scripts/check-links-external.sh
shopt -s nullglob
python_files=(
  scripts/*.py
  skills/public/*/scripts/*.py
  skills/support/*/scripts/*.py
  skills/support/*/vendor/*.py
)
python3 -m py_compile "${python_files[@]}"
ruff check scripts tests skills/public/*/scripts skills/support/*/scripts
pytest -q
python3 scripts/run-evals.py --repo-root "$REPO_ROOT"
python3 scripts/check-duplicates.py --repo-root "$REPO_ROOT" --fail-on-match
