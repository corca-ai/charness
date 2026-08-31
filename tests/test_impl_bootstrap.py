"""Regression contract for the documented impl adapter bootstrap sequence.

These tests drive the source skill entrypoint as an operator would.  The existing-file
cases are deliberately different: configured-valid state is a no-op, while a configured
invalid state remains a visible refusal.  Treating both as one existence error is the
recurrence class this issue is meant to remove.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.support import run_script

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


def _load_init_adapter_lib():
    module_name = "adapter_init_lib_for_impl_bootstrap"
    spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / "scripts/adapter_init_lib.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(entrypoint: Path, repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return run_script(str(entrypoint), "--repo-root", str(repo), *extra, cwd=repo)


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


def test_shared_init_boundary_skips_only_resolver_valid_existing_state(tmp_path: Path, monkeypatch, capsys) -> None:
    module = _load_init_adapter_lib()
    output = Path(".agents/impl-adapter.yaml")
    adapter = _write_adapter(tmp_path, VALID_ADAPTER)
    original = adapter.read_bytes()
    monkeypatch.setattr(sys, "argv", ["init_adapter", "--repo-root", str(tmp_path)])

    result = module.run_init_adapter(
        default_output=output,
        build_items=lambda _repo_name, _args: [("version", 1)],
        existing_adapter_is_valid=lambda path: path == adapter,
    )

    assert result == adapter
    assert adapter.read_bytes() == original
    assert "unchanged" in capsys.readouterr().out


def test_shared_init_boundary_reports_dry_run_without_writing(tmp_path: Path) -> None:
    result = _run(INIT_ENTRYPOINT, tmp_path, "--dry-run")

    assert result.returncode == 0, result.stderr
    assert not (tmp_path / ADAPTER_PATH).exists()
    receipt = yaml.safe_load(result.stdout)
    assert receipt == {
        "kind": "charness.adapter-bootstrap/v1",
        "skill_id": "impl",
        "path": str(tmp_path / ADAPTER_PATH),
        "relative_path": ".agents/impl-adapter.yaml",
        "state": "absent",
        "status": "would-initialize",
        "ok": True,
        "dry_run": True,
        "force": False,
        "mutation_invoked": False,
        "before_sha256": None,
        "generated_sha256": receipt["generated_sha256"],
        "reason": "adapter is absent",
        "next_action": "rerun without --dry-run to initialize the adapter",
    }


def test_shared_init_boundary_emits_one_idempotent_receipt(tmp_path: Path) -> None:
    first = _run(INIT_ENTRYPOINT, tmp_path)
    assert first.returncode == 0, first.stderr
    first_receipt = yaml.safe_load(first.stdout)
    assert first_receipt["state"] == "absent"
    assert first_receipt["status"] == "initialized"
    assert first_receipt["mutation_invoked"] is True

    before = _file_state(tmp_path / ADAPTER_PATH)
    second = _run(INIT_ENTRYPOINT, tmp_path)
    assert second.returncode == 0, second.stderr
    second_receipt = yaml.safe_load(second.stdout)
    assert second_receipt["state"] == "valid"
    assert second_receipt["status"] == "unchanged"
    assert second_receipt["mutation_invoked"] is False
    assert second_receipt["before_sha256"] == first_receipt["generated_sha256"]
    assert _file_state(tmp_path / ADAPTER_PATH) == before


def test_shared_init_boundary_refuses_invalid_version_with_typed_receipt(tmp_path: Path) -> None:
    adapter = _write_adapter(tmp_path, INVALID_ADAPTER)

    result = _run(INIT_ENTRYPOINT, tmp_path)

    assert result.returncode == 1
    receipt = yaml.safe_load(result.stdout)
    assert receipt["state"] == "invalid"
    assert receipt["status"] == "refused"
    assert receipt["mutation_invoked"] is False
    assert receipt["before_sha256"] == _file_state(adapter)[0]


def test_shared_init_boundary_requires_explicit_force_for_replacement(tmp_path: Path) -> None:
    adapter = _write_adapter(tmp_path, INVALID_ADAPTER)

    preview = _run(INIT_ENTRYPOINT, tmp_path, "--dry-run", "--force")
    assert preview.returncode == 0, preview.stderr
    preview_receipt = yaml.safe_load(preview.stdout)
    assert preview_receipt["state"] == "invalid"
    assert preview_receipt["status"] == "would-overwrite"
    assert preview_receipt["mutation_invoked"] is False
    assert _file_state(adapter)[0] == preview_receipt["before_sha256"]

    replaced = _run(INIT_ENTRYPOINT, tmp_path, "--force")
    assert replaced.returncode == 0, replaced.stderr
    replaced_receipt = yaml.safe_load(replaced.stdout)
    assert replaced_receipt["state"] == "invalid"
    assert replaced_receipt["status"] == "overwritten"
    assert replaced_receipt["mutation_invoked"] is True
    assert yaml.safe_load(adapter.read_text(encoding="utf-8"))["version"] == 1


def test_shared_init_boundary_reports_unestablished_resolver_state(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    module = _load_init_adapter_lib()
    adapter = _write_adapter(tmp_path, VALID_ADAPTER)
    monkeypatch.setattr(sys, "argv", ["init_adapter", "--repo-root", str(tmp_path)])

    def unavailable(_path: Path) -> bool:
        raise RuntimeError("resolver unavailable")

    with pytest.raises(SystemExit) as raised:
        module.run_init_adapter(
            default_output=ADAPTER_PATH,
            build_items=lambda _repo_name, _args: [("version", 1)],
            existing_adapter_is_valid=unavailable,
        )

    assert raised.value.code == 1
    receipt = yaml.safe_load(capsys.readouterr().out)
    assert receipt["state"] == "unestablished"
    assert receipt["status"] == "refused"
    assert receipt["mutation_invoked"] is False
    assert _file_state(adapter)[0] == receipt["before_sha256"]


def test_shared_init_boundary_refuses_outside_and_symlink_targets(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-impl-adapter.yaml"

    outside_result = _run(INIT_ENTRYPOINT, tmp_path, "--output", str(outside))
    assert outside_result.returncode == 2
    outside_receipt = yaml.safe_load(outside_result.stdout)
    assert outside_receipt["status"] == "refused"
    assert outside_receipt["state"] == "unestablished"
    assert outside_receipt["relative_path"] is None
    assert outside.exists() is False

    target = tmp_path / ".agents" / "real.yaml"
    target.parent.mkdir()
    target.write_text("version: 1\n", encoding="utf-8")
    link = tmp_path / ".agents" / "impl-link.yaml"
    link.symlink_to(target)
    symlink_result = _run(INIT_ENTRYPOINT, tmp_path, "--output", str(link.relative_to(tmp_path)))
    assert symlink_result.returncode == 2
    symlink_receipt = yaml.safe_load(symlink_result.stdout)
    assert symlink_receipt["status"] == "refused"
    assert symlink_receipt["state"] == "unestablished"
    assert target.read_text(encoding="utf-8") == "version: 1\n"
