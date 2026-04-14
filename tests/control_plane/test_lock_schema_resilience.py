from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.control_plane_lib import (  # noqa: E402
    load_lock_schema,
    read_lock,
    validate_lock_data,
)

from .support import run_script, seed_control_plane_repo


def _seed_tools_dir(repo: Path) -> None:
    (repo / "integrations" / "tools").mkdir(parents=True, exist_ok=True)
    (repo / "integrations" / "locks").mkdir(parents=True, exist_ok=True)


def test_read_lock_treats_schema_invalid_as_missing(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    _seed_tools_dir(repo)
    bad_lock = {
        "schema_version": "1",
        "tool_id": "demo",
        "manifest_path": "integrations/tools/demo.json",
        "support": {
            "synced_at": "2026-04-13T00:00:00Z",
            "support_state": "upstream-consumed",
            "source_type": "upstream_repo",
            "source_path": "skills/demo/SKILL.md",
            "ref": "main",
            "materialized_paths": [],
            "sync_strategy": "reference",
        },
    }
    (repo / "integrations" / "locks" / "demo.json").write_text(
        json.dumps(bad_lock), encoding="utf-8"
    )

    result = read_lock(repo, "demo")
    assert result is None
    stderr = capsys.readouterr().err
    assert "stale lock" in stderr
    assert "demo.json" in stderr


def test_read_lock_returns_valid_payload_unchanged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_tools_dir(repo)
    valid_lock = {
        "schema_version": "1",
        "tool_id": "demo",
        "manifest_path": "integrations/tools/demo.json",
    }
    (repo / "integrations" / "locks" / "demo.json").write_text(
        json.dumps(valid_lock), encoding="utf-8"
    )

    assert read_lock(repo, "demo") == valid_lock


def test_doctor_regenerates_over_stale_lock(tmp_path: Path) -> None:
    repo = seed_control_plane_repo(tmp_path)
    lock_path = repo / "integrations" / "locks" / "demo-tool.json"
    stale = {
        "schema_version": "1",
        "tool_id": "demo-tool",
        "manifest_path": "integrations/tools/demo-tool.json",
        "support": {"sync_strategy": "reference"},
    }
    lock_path.write_text(json.dumps(stale), encoding="utf-8")

    result = run_script(
        "scripts/doctor.py",
        "--repo-root",
        str(repo),
        "--json",
        "--write-locks",
    )
    assert result.returncode == 0, result.stderr
    assert "stale lock" in result.stderr

    fresh = json.loads(lock_path.read_text(encoding="utf-8"))
    validate_lock_data(fresh, load_lock_schema(), lock_path)
    assert "sync_strategy" not in fresh.get("support", {})
    assert fresh["doctor"]["doctor_status"]


def test_lock_schema_sections_reject_additional_properties() -> None:
    """Writer ↔ schema drift should fail schema validation — additionalProperties:false guards it."""
    schema = load_lock_schema()
    for section in (
        "supportSection",
        "doctorSection",
        "releaseSection",
        "provenanceSection",
        "installSection",
        "updateSection",
    ):
        assert schema["definitions"][section]["additionalProperties"] is False, (
            f"{section} must set additionalProperties:false so writer/schema drift "
            "fails validate_lock_data instead of silently accumulating stale keys."
        )
    assert schema["additionalProperties"] is False, (
        "Top-level lock schema must also reject unknown properties."
    )
