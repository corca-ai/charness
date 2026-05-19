from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.test_usage_episodes_schema import ceal_episode

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "validate_usage_episodes.py"
PLUGIN_SCRIPT = REPO_ROOT / "plugins" / "charness" / "scripts" / "validate_usage_episodes.py"


def run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def run_plugin_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PLUGIN_SCRIPT), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def write_adapter(repo: Path, body: str) -> Path:
    target = repo / ".agents" / "usage-episodes-adapter.yaml"
    target.parent.mkdir(parents=True)
    target.write_text(body, encoding="utf-8")
    return target


def test_validate_usage_episodes_reports_no_adapter(tmp_path: Path) -> None:
    result = run_validator("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "no_adapter"
    assert payload["valid"] is True
    assert payload["valid_count"] == 0
    assert payload["errors"] == []
    assert [warning["warning_id"] for warning in payload["warnings"]] == [
        "usage_episodes_adapter_missing"
    ]

    plain = run_validator("--repo-root", str(tmp_path))
    assert plain.returncode == 0
    assert "WARNING: no usage-episodes adapter found" in plain.stdout


def test_validate_usage_episodes_reports_no_adapter_with_incomplete_shadow_schema_dir(tmp_path: Path) -> None:
    (tmp_path / "integrations" / "usage-episodes").mkdir(parents=True)

    result = run_validator("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "no_adapter"
    assert payload["valid"] is True


def test_validate_usage_episodes_reports_disabled(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: false\n")

    result = run_validator("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "disabled"
    assert payload["valid"] is True
    assert payload["valid_count"] == 0
    assert payload["errors"] == []
    assert [warning["warning_id"] for warning in payload["warnings"]] == [
        "usage_episodes_adapter_disabled"
    ]

    plain = run_validator("--repo-root", str(tmp_path))
    assert plain.returncode == 0
    assert "WARNING: usage-episodes adapter at" in plain.stdout


def test_validate_usage_episodes_reports_malformed_adapter(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: [\n")

    result = run_validator("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid_adapter"
    assert payload["valid"] is False


def test_validate_usage_episodes_accepts_valid_jsonl(tmp_path: Path) -> None:
    write_adapter(
        tmp_path,
        "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n",
    )
    records = tmp_path / ".charness" / "usage-episodes"
    records.mkdir(parents=True)
    (records / "usage_episode.jsonl").write_text(
        json.dumps(ceal_episode()) + "\n",
        encoding="utf-8",
    )

    result = run_validator("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "valid"
    assert payload["valid_count"] == 1


def test_plugin_usage_episode_validator_smoke(tmp_path: Path) -> None:
    no_adapter = run_plugin_validator("--repo-root", str(tmp_path), "--json")
    assert no_adapter.returncode == 0, no_adapter.stderr
    no_adapter_payload = json.loads(no_adapter.stdout)
    assert no_adapter_payload["status"] == "no_adapter"
    assert [warning["warning_id"] for warning in no_adapter_payload["warnings"]] == [
        "usage_episodes_adapter_missing"
    ]

    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    records = tmp_path / ".charness" / "usage-episodes"
    records.mkdir(parents=True)
    (records / "usage_episode.jsonl").write_text(json.dumps(ceal_episode()) + "\n", encoding="utf-8")

    valid = run_plugin_validator("--repo-root", str(tmp_path), "--json")

    assert valid.returncode == 0, valid.stderr
    payload = json.loads(valid.stdout)
    assert payload["status"] == "valid"
    assert payload["valid_count"] == 1


def test_validate_usage_episodes_rejects_malformed_jsonl(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\n")
    records = tmp_path / ".charness" / "usage-episodes"
    records.mkdir(parents=True)
    (records / "usage_episode.jsonl").write_text('{"event_type": "usage_episode"}\n', encoding="utf-8")

    result = run_validator("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid_records"
    assert payload["errors"]


def test_validate_usage_episodes_rejects_bad_timestamp(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\n")
    records = tmp_path / ".charness" / "usage-episodes"
    records.mkdir(parents=True)
    episode = ceal_episode()
    episode["timestamp"] = "not-a-date"
    (records / "usage_episode.jsonl").write_text(json.dumps(episode) + "\n", encoding="utf-8")

    result = run_validator("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid_records"
    assert payload["errors"]


def test_validate_usage_episodes_rejects_records_path_outside_repo(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\n")
    outside = tmp_path.parent / "outside-usage-episode.jsonl"
    outside.write_text(json.dumps(ceal_episode()) + "\n", encoding="utf-8")

    result = run_validator("--repo-root", str(tmp_path), "--records-path", str(outside), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid_records_path"
    assert payload["valid"] is False
