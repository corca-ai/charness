from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from .support import run_script

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "skills/public/achieve/scripts/upsert_goal.py"


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_script(str(HELPER), "--repo-root", str(repo), *args)


def _path(repo: Path) -> Path:
    return repo / "charness-artifacts/goals/2026-08-07-g.md"


def test_fields_file_preserves_multiline_prose_and_shell_identifiers(tmp_path: Path) -> None:
    body = "Keep `Goal Binding` exact.\n\nUse `/goal #724` for pickup."
    fields = tmp_path / "fields.json"
    fields.write_text(json.dumps({"title": "T", "goal-body": body}), encoding="utf-8")

    result = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))

    assert result.returncode == 0, result.stderr
    assert body in _path(tmp_path).read_text(encoding="utf-8")


def test_goal_body_heading_and_unbalanced_fence_are_refused(tmp_path: Path) -> None:
    for body, message in (
        ("intro\n\n## Slice Log", "unfenced markdown heading"),
        ("intro\n\n```\nunfinished", "code fence unclosed"),
    ):
        fields = tmp_path / "fields.json"
        fields.write_text(json.dumps({"title": "T", "goal-body": body}), encoding="utf-8")
        result = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--fields-file", str(fields))
        assert result.returncode != 0
        assert message in result.stderr
        assert not _path(tmp_path).exists()


def test_existing_planning_record_is_updated_and_binding_freezes_it(tmp_path: Path) -> None:
    first = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--title", "Old", "--goal-body", "old")
    assert first.returncode == 0
    path = _path(tmp_path)
    before = path.read_text(encoding="utf-8")

    changed = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--title", "New", "--goal-body", "new")
    assert changed.returncode == 0
    assert "# Achieve Goal: New" in path.read_text(encoding="utf-8")
    assert "new" in path.read_text(encoding="utf-8")

    path.with_suffix(".binding.json").write_text("{}\n", encoding="utf-8")
    frozen = path.read_bytes()
    refused = _run(tmp_path, "--slug", "g", "--date", "2026-08-07", "--title", "Other")
    assert refused.returncode == 1
    assert yaml.safe_load(refused.stdout)["reason"] == "frozen-binding"
    assert path.read_bytes() == frozen
    assert before != frozen


def test_removed_status_surface_is_not_accepted(tmp_path: Path) -> None:
    result = _run(tmp_path, "--slug", "g", "--status", "active", "--title", "T")

    assert result.returncode != 0
    assert "unrecognized arguments: --status" in result.stderr
