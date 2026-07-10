"""Shared exported skill scripts participate in the repo lint/length gates.

Regression pin for the scope gap where skills/shared/scripts/*.py (exported,
consuming-repo-facing Python) escaped the ruff, py-compile, length,
export-safe-import, and runtime-inheritance gate scopes that already covered
public and support skill scripts.
"""
from __future__ import annotations

import importlib

from .support import ROOT

CHECK_PYTHON_LENGTHS = importlib.import_module("scripts.check_python_lengths")
CHECK_EXPORT_SAFE_IMPORTS = importlib.import_module("scripts.check_export_safe_imports")
CHECK_PYTHON_RUNTIME_INHERITANCE = importlib.import_module("scripts.check_python_runtime_inheritance")

REPO_ROOT = ROOT
SHARED_GLOB = "skills/shared/scripts/*.py"
SENTINEL = REPO_ROOT / "skills" / "shared" / "scripts" / "reviewer_boundary_fingerprint.py"


def test_shared_scripts_in_length_gate_scope() -> None:
    targets = CHECK_PYTHON_LENGTHS.iter_python_targets(REPO_ROOT)
    assert SENTINEL in targets


def test_shared_scripts_in_export_safe_import_scope() -> None:
    targets = CHECK_EXPORT_SAFE_IMPORTS.iter_python_targets(REPO_ROOT)
    assert SENTINEL in targets


def test_shared_scripts_in_runtime_inheritance_scope() -> None:
    assert SHARED_GLOB in CHECK_PYTHON_RUNTIME_INHERITANCE.DEFAULT_SCAN_GLOBS


def test_run_quality_ruff_and_py_compile_cover_shared_scripts() -> None:
    text = (REPO_ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    ruff_lines = [ln for ln in text.splitlines() if ln.startswith('queue_selected "ruff"')]
    assert ruff_lines
    assert all("skills/shared/scripts" in ln for ln in ruff_lines)
    py_files_block = text.split("python_files=(", 1)[1].split(")", 1)[0]
    assert "skills/shared/scripts/*.py" in py_files_block


def test_shared_scripts_in_scope_under_git_file_listing() -> None:
    assert SENTINEL in CHECK_PYTHON_LENGTHS.iter_python_targets(REPO_ROOT, require_git=True)
    assert SENTINEL in CHECK_EXPORT_SAFE_IMPORTS.iter_python_targets(REPO_ROOT, require_git=True)
