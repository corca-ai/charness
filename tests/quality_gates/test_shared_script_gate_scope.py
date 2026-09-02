"""Shared exported skill scripts participate in the repo lint/length gates.

Regression pin for the scope gap where skills/shared/scripts/*.py (exported,
consuming-repo-facing Python) escaped the ruff, py-compile, length,
and runtime-inheritance gate scopes that already covered
public and support skill scripts.
"""

from __future__ import annotations

import importlib

import quality_label_universe

from .support import ROOT

CHECK_PYTHON_LENGTHS = importlib.import_module("scripts.gates.check_code_lengths")
CHECK_PYTHON_RUNTIME_INHERITANCE = importlib.import_module(
    "scripts.gates.check_python_runtime_inheritance"
)

REPO_ROOT = ROOT
SHARED_GLOB = "skills/shared/scripts/*.py"
SENTINEL = REPO_ROOT / "skills" / "shared" / "scripts" / "reviewer_boundary_fingerprint.py"


def test_shared_scripts_in_length_gate_scope() -> None:
    targets = CHECK_PYTHON_LENGTHS.iter_python_targets(REPO_ROOT)
    assert SENTINEL in targets


def test_shared_scripts_in_runtime_inheritance_scope() -> None:
    assert SHARED_GLOB in CHECK_PYTHON_RUNTIME_INHERITANCE.DEFAULT_SCAN_GLOBS


LINT_SCRIPT_REL = "./scripts/check-python-lint.sh"


def test_run_quality_ruff_and_py_compile_cover_shared_scripts() -> None:
    """The pin MOVED with the path list; it was not relaxed.

    The ruff path list now lives in one place, so asserting `skills/shared/scripts`
    appears on `run-quality.sh`'s ruff line would be asserting a tautology about a line
    that no longer carries a path. The obligation is unchanged and split in two: the
    runner must invoke the owning entrypoint, and that entrypoint must cover the shared
    scripts. Deleting either half restores the gap this module is the regression pin for.
    """
    rows = quality_label_universe.quality_gate_rows(REPO_ROOT) or []
    ruff_rows = [row for row in rows if row["label"] == "ruff"]
    assert ruff_rows
    assert all(LINT_SCRIPT_REL in row["command"] for row in ruff_rows)

    lint = (REPO_ROOT / LINT_SCRIPT_REL).read_text(encoding="utf-8")
    assert "skills/shared/scripts" in lint
    assert "--key python_sources" in lint
    assert "--format lines" in lint
    assert 'ruff check "${python_files[@]}"' in lint

    compile_rows = [row for row in rows if row["label"] == "py-compile"]
    assert compile_rows
    assert "${python_files[@]}" in compile_rows[0]["command"]


def test_ci_invokes_the_lint_entrypoint_rather_than_retyping_its_path_list() -> None:
    """The actual defect: CI retyped the command and the copy drifted.

    `quality-core.yml` declares `local-gate-subset-mirror`, whose claim is that every
    step verbatim re-runs a repo-owned validator. A retyped path list cannot keep that
    claim -- sameness of invocation is not checkable while the invocation is a string
    typed twice -- and this one omitted `skills/shared/scripts` from 2026-07-10 until it
    was found. The workflow's own parity validator could not catch it: the file grants
    itself the exemption, so the parity lane evaluates zero jobs here (D45/S31).
    """
    workflow = (REPO_ROOT / ".github" / "workflows" / "quality-core.yml").read_text(
        encoding="utf-8"
    )

    assert LINT_SCRIPT_REL in workflow
    # No CI step may spell out a ruff path list again, whatever paths it happens to name.
    assert "ruff check charness" not in workflow


def test_no_surface_or_integration_note_restates_the_lint_path_list() -> None:
    """Three of the four copies were stale, and two were not in CI at all.

    `.agents/surfaces.json` and `integrations/tools/ruff.json` each carried their own
    transcription with no gate reading it for currency. They now name the entrypoint, so
    a path change cannot leave them behind.
    """
    for rel in (".agents/surfaces.json", "integrations/tools/ruff.json"):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "ruff check charness" not in text, f"{rel} restates the lint path list"


def test_shared_scripts_in_scope_under_git_file_listing() -> None:
    assert SENTINEL in CHECK_PYTHON_LENGTHS.iter_python_targets(REPO_ROOT, require_git=True)
