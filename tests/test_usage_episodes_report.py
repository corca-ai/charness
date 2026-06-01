from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.test_usage_episodes_schema import ceal_episode, crill_episode

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "report_usage_episodes.py"
PLUGIN_SCRIPT = REPO_ROOT / "plugins" / "charness" / "scripts" / "report_usage_episodes.py"


def run_report(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def run_plugin_report(*args: str) -> subprocess.CompletedProcess[str]:
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


def write_records(repo: Path, records: list[dict]) -> Path:
    records_dir = repo / ".charness" / "usage-episodes"
    records_dir.mkdir(parents=True)
    target = records_dir / "usage_episode.jsonl"
    target.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
    return target


def test_report_usage_episodes_reports_no_adapter(tmp_path: Path) -> None:
    result = run_report("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "no_adapter"
    assert payload["valid"] is True
    assert payload["episode_count"] == 0
    assert [warning["warning_id"] for warning in payload["warnings"]] == [
        "usage_episodes_adapter_missing"
    ]
    assert any("not product-success proof" in non_claim for non_claim in payload["non_claims"])


def test_report_usage_episodes_reports_disabled(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: false\n")

    result = run_report("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "disabled"
    assert payload["valid"] is True
    assert payload["episode_count"] == 0
    assert [warning["warning_id"] for warning in payload["warnings"]] == [
        "usage_episodes_adapter_disabled"
    ]


def test_report_usage_episodes_reports_no_records(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")

    result = run_report("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "no_records"
    assert payload["valid"] is True
    assert payload["records_path"] == ".charness/usage-episodes/usage_episode.jsonl"
    assert [warning["warning_id"] for warning in payload["warnings"]] == [
        "usage_episodes_no_records"
    ]


def test_report_usage_episodes_aggregates_counts_sessions_and_gaps(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    first = ceal_episode()
    first["session_id"] = "session-1"
    first["timestamp"] = "2026-05-17T04:00:00Z"
    second = crill_episode()
    second["session_id"] = "session-1"
    second["timestamp"] = "2026-05-17T04:10:00Z"
    third = crill_episode()
    third["episode_id"] = "crill-episode-002"
    third["timestamp"] = "2026-05-17T08:00:00Z"
    third.pop("feedback_signal", None)
    fourth = crill_episode()
    fourth["episode_id"] = "crill-episode-003"
    fourth["timestamp"] = "2026-05-17T11:00:00Z"
    write_records(tmp_path, [first, second, third, fourth])

    result = run_report("--repo-root", str(tmp_path), "--gap-minutes", "90", "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "valid"
    assert payload["episode_count"] == 4
    assert payload["session_count"] == 3
    assert payload["sessions"]["explicit_count"] == 1
    assert payload["sessions"]["inferred_gap_count"] == 2
    assert payload["sessions"]["session_id_present_count"] == 2
    assert payload["sessions"]["session_grouping_rate"] == 0.5
    assert payload["counts"]["t_status"] == {"candidate": 1, "none": 3}
    assert payload["t_signal_count"] == 1
    assert payload["t_signal_rate"] == 0.25
    assert payload["capture_gaps"]["ungrouped_episode_count"] == 2
    assert payload["capture_gaps"]["inferred_gap_session_count"] == 2
    assert payload["capture_gaps"]["missing_feedback_signal_count"] == 1
    assert payload["capture_gaps"]["explicit_request_only"] is True

    plain = run_report("--repo-root", str(tmp_path))
    assert plain.returncode == 0
    assert "ADVISORY: usage episode report is an engineering signal" in plain.stdout
    assert "Usage episodes: 4 record(s) across 3 session group(s)." in plain.stdout
    assert "Non-claims:" in plain.stdout


def test_report_usage_episodes_rejects_malformed_jsonl(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\n")
    records_dir = tmp_path / ".charness" / "usage-episodes"
    records_dir.mkdir(parents=True)
    (records_dir / "usage_episode.jsonl").write_text('{"event_type": "usage_episode"}\n', encoding="utf-8")

    result = run_report("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid_records"
    assert payload["valid"] is False
    assert payload["errors"]


def test_plugin_usage_episode_report_smoke(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    write_records(tmp_path, [ceal_episode()])

    result = run_plugin_report("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "valid"
    assert payload["episode_count"] == 1
    assert payload["t_signal_count"] == 1
