#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

pytest -q \
  tests/charness_cli/test_managed_install.py \
  tests/charness_cli/test_codex_cache_refresh.py \
  tests/charness_cli/test_update_propagation.py
