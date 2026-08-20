"""Regression contract for the documented impl adapter bootstrap sequence.

These tests drive the source skill entrypoint as an operator would.  The existing-file
cases are deliberately different: configured-valid state is a no-op, while a configured
invalid state remains a visible refusal.  Treating both as one existence error is the
recurrence class this issue is meant to remove.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_ENTRYPOINT = REPO_ROOT / "skills/public/impl/scripts/init_adapter.py"
RESOLVE_ENTRYPOINT = REPO_ROOT / "skills/public/impl/scripts/resolve_adapter.py"
ADAPTER_PATH = Path(".agents/impl-adapter.yaml")

VALID_ADAPTER = """\
version: 1
repo: consumer-customized
language: en
output_dir: custom-artifacts/impl
preset_id: team-defaults
customized_from: portable-defaults
verification_tools: []
ui_verification_tools: []
verification_install_proposals: []
truth_surfaces: []
"""

INVALID_ADAPTER = """\
version: 2
repo: consumer-customized
language: en
output_dir: custom-artifacts/impl
"""


def _run(entrypoint: Path, repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(entrypoint), "--repo-root", str(repo)],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_adapter(repo: Path, contents: str) -> Path:
    path = repo / ADAPTER_PATH
    path.parent.mkdir(parents=True)
    path.write_text(contents, encoding="utf-8")
    return path


def _file_state(path: Path) -> tuple[str, int, tuple[int, ...]]:
    data = path.read_bytes()
    metadata = os.stat(path)
    # These fields detect replacement, rewriting, chmod, and metadata changes without
    # treating a resolver's ordinary read as a mutation through atime.
    stat_fields = (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_uid,
        metadata.st_gid,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )
    return hashlib.sha256(data).hexdigest(), len(data), stat_fields


def test_valid_existing_adapter_is_idempotent_through_source_entrypoint(tmp_path: Path) -> None:
    adapter = _write_adapter(tmp_path, VALID_ADAPTER)
    before = _file_state(adapter)

    resolved_before = _run(RESOLVE_ENTRYPOINT, tmp_path)
    assert resolved_before.returncode == 0, resolved_before.stderr
    assert "valid: true" in resolved_before.stdout

    initialized = _run(INIT_ENTRYPOINT, tmp_path)
    assert initialized.returncode == 0, initialized.stderr
    assert "unchanged" in (initialized.stdout + initialized.stderr).lower()
    assert _file_state(adapter) == before

    resolved_after = _run(RESOLVE_ENTRYPOINT, tmp_path)
    assert resolved_after.returncode == 0, resolved_after.stderr
    assert "valid: true" in resolved_after.stdout


def test_missing_adapter_still_initializes_through_source_entrypoint(tmp_path: Path) -> None:
    assert not (tmp_path / ADAPTER_PATH).exists()

    resolved_before = _run(RESOLVE_ENTRYPOINT, tmp_path)
    assert resolved_before.returncode == 0, resolved_before.stderr
    assert "found: false" in resolved_before.stdout

    initialized = _run(INIT_ENTRYPOINT, tmp_path)
    assert initialized.returncode == 0, initialized.stderr
    assert (tmp_path / ADAPTER_PATH).is_file()

    resolved_after = _run(RESOLVE_ENTRYPOINT, tmp_path)
    assert resolved_after.returncode == 0, resolved_after.stderr
    assert "found: true" in resolved_after.stdout
    assert "valid: true" in resolved_after.stdout


def test_invalid_existing_adapter_remains_nonzero_and_unchanged(tmp_path: Path) -> None:
    adapter = _write_adapter(tmp_path, INVALID_ADAPTER)
    before = _file_state(adapter)

    resolved = _run(RESOLVE_ENTRYPOINT, tmp_path)
    assert resolved.returncode == 0, resolved.stderr
    assert "valid: false" in resolved.stdout

    initialized = _run(INIT_ENTRYPOINT, tmp_path)
    assert initialized.returncode != 0
    assert _file_state(adapter) == before
