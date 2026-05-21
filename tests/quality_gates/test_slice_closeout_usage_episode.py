from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def _write_closeout_fixture(repo: Path, adapter: str) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "demo-surface",
                        "description": "demo",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": ["python3 scripts/verify.py"],
                        "notes": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "usage-episodes-adapter.yaml").write_text(adapter, encoding="utf-8")
    (repo / "scripts" / "verify.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")


def _run_closeout(repo: Path):
    return run_script(
        "scripts/run_slice_closeout.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        "--json",
    )


def test_run_slice_closeout_emits_usage_episode_when_enabled(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_closeout_fixture(
        repo,
        "\n".join(
            [
                "version: 1",
                "repo: charness",
                "enabled: true",
                "storage_path: .charness/usage-episodes",
                "events:",
                "  - usage_episode",
                "",
            ]
        ),
    )

    result = _run_closeout(repo)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["usage_episode"]["status"] == "emitted"
    records_path = repo / ".charness" / "usage-episodes" / "usage_episode.jsonl"
    record = json.loads(records_path.read_text(encoding="utf-8"))
    assert record["selected_job"] == "implement_slice"
    assert record["core_action"] == "landed_verified_change"
    assert record["agent_action"] == {
        "surface": "quality_gate",
        "capability_ref": "run_slice_closeout",
    }
    assert record["first_value_ref"]["kind"] == "test_result"
    assert "raw_prompt" not in record
    assert "raw_transcript" not in record
    assert "user_identity" not in record

    valid = run_script("scripts/validate_usage_episodes.py", "--repo-root", str(repo), "--json")
    assert valid.returncode == 0, valid.stderr
    assert json.loads(valid.stdout)["valid_count"] == 1

    with records_path.open("a", encoding="utf-8") as handle:
        handle.write('{"event_type": "usage_episode"}\n')
    invalid = run_script("scripts/validate_usage_episodes.py", "--repo-root", str(repo), "--json")
    assert invalid.returncode == 1
    assert json.loads(invalid.stdout)["status"] == "invalid_records"


def test_run_slice_closeout_skips_usage_episode_when_disabled(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_closeout_fixture(repo, "version: 1\nenabled: false\n")

    result = _run_closeout(repo)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["usage_episode"]["status"] == "disabled"
    assert not (repo / ".charness" / "usage-episodes" / "usage_episode.jsonl").exists()


def test_run_slice_closeout_fails_usage_episode_invalid_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_closeout_fixture(repo, "version: 1\nenabled: true\nstorage_path: /tmp/outside\n")

    result = _run_closeout(repo)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed"
    assert payload["usage_episode"]["status"] == "invalid_adapter"
    assert payload["usage_episode"]["error"].endswith("ValidationError")


def test_run_slice_closeout_rotates_usage_episode_records(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_closeout_fixture(
        repo,
        "\n".join(
            [
                "version: 1",
                "enabled: true",
                "storage_path: .charness/usage-episodes",
                "rotation:",
                "  max_files: 2",
                "  max_size_mb: 1",
                "",
            ]
        ),
    )
    records_dir = repo / ".charness" / "usage-episodes"
    records_dir.mkdir(parents=True)
    (records_dir / "usage_episode.jsonl").write_text("x" * (1024 * 1024), encoding="utf-8")

    result = _run_closeout(repo)

    assert result.returncode == 0, result.stderr
    assert (records_dir / "usage_episode.1.jsonl").is_file()
    valid = run_script("scripts/validate_usage_episodes.py", "--repo-root", str(repo), "--json")
    assert valid.returncode == 0, valid.stderr
    assert json.loads(valid.stdout)["valid_count"] == 1
