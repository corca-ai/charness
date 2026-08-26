"""The public adapter entrypoints share one first-use lifecycle contract."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
INIT_SCRIPTS = sorted((ROOT / "skills" / "public").glob("*/scripts/init_adapter.py"))
RECEIPT_KEYS = {
    "kind",
    "skill_id",
    "path",
    "relative_path",
    "state",
    "status",
    "ok",
    "dry_run",
    "force",
    "mutation_invoked",
    "before_sha256",
    "generated_sha256",
    "reason",
    "next_action",
}


def _run(script: Path, repo_root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--repo-root", str(repo_root), *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _receipt(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.stderr == ""
    documents = list(yaml.safe_load_all(result.stdout))
    assert len(documents) == 1
    payload = documents[0]
    assert isinstance(payload, dict)
    assert set(payload) == RECEIPT_KEYS
    assert payload["kind"] == "charness.adapter-bootstrap/v1"
    return payload


@pytest.mark.parametrize("script", INIT_SCRIPTS, ids=lambda path: path.parent.parent.name)
def test_every_public_adapter_bootstrap_has_absent_dry_run_receipt(script: Path, tmp_path: Path) -> None:
    result = _run(script, tmp_path, "--dry-run")

    assert result.returncode == 0
    payload = _receipt(result)
    assert payload["skill_id"] == script.parent.parent.name
    assert payload["state"] == "absent"
    assert payload["status"] == "would-initialize"
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["mutation_invoked"] is False
    assert not (tmp_path / ".agents").exists()


@pytest.mark.parametrize("script", INIT_SCRIPTS, ids=lambda path: path.parent.parent.name)
def test_every_public_adapter_bootstrap_is_idempotent_and_refuses_bad_version(
    script: Path, tmp_path: Path
) -> None:
    initialized = _run(script, tmp_path)
    assert initialized.returncode == 0
    first = _receipt(initialized)
    assert first["status"] == "initialized"
    assert first["mutation_invoked"] is True

    repeated = _run(script, tmp_path)
    assert repeated.returncode == 0
    second = _receipt(repeated)
    assert second["state"] == "valid"
    assert second["status"] == "unchanged"
    assert second["mutation_invoked"] is False

    adapter = tmp_path / ".agents" / f"{script.parent.parent.name}-adapter.yaml"
    adapter.write_text("version: 999\n", encoding="utf-8")
    refused = _run(script, tmp_path)
    assert refused.returncode == 1
    refusal = _receipt(refused)
    assert refusal["state"] == "invalid"
    assert refusal["status"] == "refused"
    assert refusal["mutation_invoked"] is False
