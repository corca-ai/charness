#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

python3 scripts/validate-skills.py --repo-root "$REPO_ROOT"
python3 scripts/validate-profiles.py --repo-root "$REPO_ROOT"
python3 scripts/validate-adapters.py --repo-root "$REPO_ROOT"
python3 scripts/validate-integrations.py --repo-root "$REPO_ROOT"
python3 scripts/validate-packaging.py --repo-root "$REPO_ROOT"
python3 scripts/check-skill-contracts.py --repo-root "$REPO_ROOT"
python3 scripts/check-doc-links.py --repo-root "$REPO_ROOT"
./scripts/check-markdown.sh
./scripts/check-secrets.sh
./scripts/check-shell.sh
./scripts/check-links-external.sh
python3 -m py_compile scripts/*.py skills/public/*/scripts/*.py
ruff check scripts tests skills/public/*/scripts
pytest -q
python3 scripts/run-evals.py --repo-root "$REPO_ROOT"
python3 scripts/check-duplicates.py --repo-root "$REPO_ROOT" --fail-on-match
