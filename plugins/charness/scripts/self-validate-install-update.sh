#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

python3 scripts/run_standing_pytest.py \
  --repo-root "$REPO_ROOT" \
  --mode read-only \
  --include-release-only \
  --pytest-target tests/charness_cli/test_managed_install.py \
  --pytest-target tests/charness_cli/test_codex_cache_refresh.py \
  --pytest-target tests/charness_cli/test_update_propagation.py
