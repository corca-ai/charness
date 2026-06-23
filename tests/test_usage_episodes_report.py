from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.report_usage_episodes import NON_CLAIMS
from tests.test_usage_episodes_schema import ceal_episode, crill_episode

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "report_usage_episodes.py"
PLUGIN_SCRIPT = REPO_ROOT / "plugins" / "charness" / "scripts" / "report_usage_episodes.py"
PRODUCT_REVIEW_SCRIPT = REPO_ROOT / "scripts" / "report_usage_product_review.py"
PLUGIN_PRODUCT_REVIEW_SCRIPT = REPO_ROOT / "plugins" / "charness" / "scripts" / "report_usage_product_review.py"


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


def run_product_review(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PRODUCT_REVIEW_SCRIPT), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def run_plugin_product_review(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PLUGIN_PRODUCT_REVIEW_SCRIPT), *args],
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
    assert payload["non_claims"] == NON_CLAIMS


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
    assert payload["product_evidence"]["first_value_floor_count"] == 4
    assert payload["product_evidence"]["first_value_floor_rate"] == 1.0
    assert payload["product_evidence"]["first_value_kind"] == {
        "github_issue": 1,
        "product_artifact": 3,
    }
    assert payload["product_evidence"]["feedback_coverage_count"] == 3
    assert payload["product_evidence"]["feedback_coverage_rate"] == 0.75
    assert payload["product_evidence"]["satisfaction_signal_count"] == 2
    assert payload["product_evidence"]["satisfaction_signal_rate"] == 0.5
    assert payload["product_evidence"]["friction_or_followup_signal_count"] == 1
    assert payload["product_evidence"]["friction_or_followup_signal_rate"] == 0.25
    assert payload["product_evidence"]["missing_feedback_signal_count"] == 1
    assert payload["product_evidence"]["unclassified_feedback_signal_count"] == 0
    assert payload["product_evidence"]["veto_gaps"] == [
        "missing_feedback",
        "single_trigger_type",
    ]

    plain = run_report("--repo-root", str(tmp_path))
    assert plain.returncode == 0
    assert "ADVISORY: usage episode report is an engineering signal" in plain.stdout
    assert "Usage episodes: 4 record(s) across 3 session group(s)." in plain.stdout
    assert "Product evidence: first_value_floor=4/4 (100.0%)" in plain.stdout
    assert "feedback_coverage=75.0%" in plain.stdout
    assert "Product-success veto gaps: missing_feedback, single_trigger_type." in plain.stdout
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
    assert payload["product_evidence"]["first_value_floor_count"] == 1


def test_report_usage_episodes_vetoes_single_emitter_and_no_satisfaction(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    first = crill_episode()
    first["feedback_signal"] = "follow_up_requested"
    second = crill_episode()
    second["episode_id"] = "crill-episode-002"
    second["trigger_type"] = "correction"
    second["entry_point"] = "api"
    second["feedback_signal"] = "retried"
    write_records(tmp_path, [first, second])

    result = run_report("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["product_evidence"]["first_value_floor_count"] == 2
    assert payload["product_evidence"]["feedback_coverage_rate"] == 1.0
    assert payload["product_evidence"]["satisfaction_signal_count"] == 0
    assert payload["product_evidence"]["friction_or_followup_signal_count"] == 2
    assert payload["product_evidence"]["veto_gaps"] == [
        "no_satisfaction_signal",
        "single_emitter",
    ]


def test_report_usage_episodes_flags_unclassified_feedback(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    record = crill_episode()
    record["feedback_signal"] = "edited"
    write_records(tmp_path, [record])

    result = run_report("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["product_evidence"]["feedback_coverage_rate"] == 1.0
    assert payload["product_evidence"]["unclassified_feedback_signal_count"] == 1
    assert "unclassified_feedback" in payload["product_evidence"]["veto_gaps"]


def test_product_review_report_exposes_last_seen_without_actioning_inactivity(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    first = crill_episode()
    first["timestamp"] = "2026-06-01T10:00:00Z"
    second = crill_episode()
    second["episode_id"] = "crill-episode-002"
    second["timestamp"] = "2026-06-02T12:30:00Z"
    write_records(tmp_path, [first, second])

    result = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--release-version",
        "0.14.0",
        "--update-prompt-state",
        "prompted",
        "--corca-internal",
        "--repo-ref",
        "corca-ai/charness",
        "--user-ref",
        "spilist",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    summary = payload["review_summary"]
    assert summary["first_seen_at"] == "2026-06-01T10:00:00Z"
    assert summary["last_seen_at"] == "2026-06-02T12:30:00Z"
    assert summary["usage_count"] == 2
    assert summary["update_context"]["update_prompt_state"] == "prompted"
    assert summary["target_refs"] == {
        "repo_ref": "corca-ai/charness",
        "user_ref": "spilist",
    }
    assert payload["actionable_packet_count"] == 0
    assert [packet["signal_type"] for packet in payload["reporter_packets"]] == [
        "usage_observed"
    ]
    rendered = json.dumps(payload)
    assert "stopped_using_candidate" not in rendered
    assert "churn or stop-using classifiers" in rendered


def test_product_review_report_builds_thresholded_reporter_packets(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    first = crill_episode()
    first["feedback_signal"] = "retried"
    second = crill_episode()
    second["episode_id"] = "crill-episode-002"
    second["feedback_signal"] = "corrected"
    second["t_status"] = "none"
    write_records(tmp_path, [first, second])

    result = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--friction-threshold",
        "2",
        "--missed-detection-threshold",
        "1",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["actionable_packet_count"] == 2
    packets = {packet["signal_type"]: packet for packet in payload["reporter_packets"]}
    assert packets["friction_threshold"]["threshold"] == {
        "metric": "friction_or_followup_count",
        "observed_count": 2,
        "threshold": 2,
    }
    assert packets["missed_detection_candidate"]["threshold"] == {
        "metric": "missed_detection_candidate_count",
        "observed_count": 2,
        "threshold": 1,
    }
    body = packets["friction_threshold"]["body"]
    assert "### Triage Questions" in body
    assert "recommended fix" not in body.lower()


def test_product_review_window_filtering_and_empty_window_are_neutral(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    old = crill_episode()
    old["timestamp"] = "2026-05-31T23:00:00Z"
    old["feedback_signal"] = "retried"
    current = crill_episode()
    current["episode_id"] = "crill-episode-002"
    current["timestamp"] = "2026-06-02T12:00:00Z"
    write_records(tmp_path, [old, current])

    result = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--window-start",
        "2026-06-01T00:00:00Z",
        "--window-end",
        "2026-06-03T00:00:00Z",
        "--friction-threshold",
        "1",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["review_summary"]["usage_count"] == 1
    assert payload["review_summary"]["first_seen_at"] == "2026-06-02T12:00:00Z"
    assert payload["review_summary"]["last_seen_at"] == "2026-06-02T12:00:00Z"
    assert payload["actionable_packet_count"] == 0

    empty = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--window-start",
        "2026-06-04T00:00:00Z",
        "--window-end",
        "2026-06-05T00:00:00Z",
        "--json",
    )
    assert empty.returncode == 0, empty.stderr
    empty_payload = json.loads(empty.stdout)
    assert empty_payload["review_summary"]["usage_count"] == 0
    assert empty_payload["reporter_packets"][0]["signal_type"] == "no_usage_observed"
    assert "no_usage_records_in_window" in empty_payload["reporter_packets"][0]["confidence_gaps"]


def test_product_review_classification_skipped_alone_is_not_actionable(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    record = crill_episode()
    record["classification_skipped"] = "diff_unavailable"
    write_records(tmp_path, [record])

    result = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--missed-detection-threshold",
        "1",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["review_summary"]["missed_detection_candidate_count"] == 0
    assert payload["actionable_packet_count"] == 0


def test_product_review_rejects_bad_window_as_structured_payload(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    write_records(tmp_path, [crill_episode()])

    result = run_product_review("--repo-root", str(tmp_path), "--window-start", "not-a-date", "--json")

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid_window"
    assert payload["valid"] is False

    reversed_window = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--window-start",
        "2026-06-03T00:00:00Z",
        "--window-end",
        "2026-06-01T00:00:00Z",
        "--json",
    )
    assert reversed_window.returncode == 2
    assert json.loads(reversed_window.stdout)["status"] == "invalid_window"


def test_product_review_execute_refuses_without_threshold_packet(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    write_records(tmp_path, [crill_episode()])

    result = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--execute",
        "--github-repo",
        "corca-ai/charness",
        "--issue-number",
        "280",
        "--json",
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "no_actionable_packets"
    assert payload["executed"] is False


def test_product_review_execute_comments_threshold_packets_with_fake_gh(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    record = crill_episode()
    record["feedback_signal"] = "retried"
    write_records(tmp_path, [record])
    capture_path = tmp_path / "gh-call.json"
    fake_gh = tmp_path / "gh"
    fake_gh.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                f"open({str(capture_path)!r}, 'w', encoding='utf-8').write(json.dumps(sys.argv[1:]))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)

    result = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--corca-internal",
        "--repo-ref",
        "corca-ai/charness",
        "--user-ref",
        "spilist",
        "--friction-threshold",
        "1",
        "--execute",
        "--github-repo",
        "corca-ai/charness",
        "--issue-number",
        "280",
        "--gh-bin",
        str(fake_gh),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["executed"] is True
    assert payload["github_target"] == {
        "repo": "corca-ai/charness",
        "issue_number": 280,
        "comment_count": 1,
        "packet_count": 1,
        "target_refs_included": False,
    }
    call = json.loads(capture_path.read_text(encoding="utf-8"))
    assert call[:5] == ["issue", "comment", "280", "--repo", "corca-ai/charness"]
    assert "friction_threshold" in call[-1]
    assert "filing_mode: `executed`" in call[-1]
    assert "redacted for mutating GitHub comment" in call[-1]
    assert "spilist" not in call[-1]


def test_product_review_execute_combines_multiple_threshold_packets(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    record = crill_episode()
    record["feedback_signal"] = "retried"
    record["t_status"] = "none"
    write_records(tmp_path, [record])
    capture_path = tmp_path / "gh-call.json"
    fake_gh = tmp_path / "gh"
    fake_gh.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                f"open({str(capture_path)!r}, 'w', encoding='utf-8').write(json.dumps(sys.argv[1:]))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)

    result = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--friction-threshold",
        "1",
        "--missed-detection-threshold",
        "1",
        "--execute",
        "--github-repo",
        "corca-ai/charness",
        "--issue-number",
        "280",
        "--gh-bin",
        str(fake_gh),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["github_target"]["comment_count"] == 1
    assert payload["github_target"]["packet_count"] == 2
    call = json.loads(capture_path.read_text(encoding="utf-8"))
    assert call[-1].count("## Charness Usage Product-Review Packet") == 2
    assert "signal_type: `friction_threshold`" in call[-1]
    assert "signal_type: `missed_detection_candidate`" in call[-1]


def test_product_review_execute_reports_missing_gh_as_json(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    record = crill_episode()
    record["feedback_signal"] = "retried"
    write_records(tmp_path, [record])

    result = run_product_review(
        "--repo-root",
        str(tmp_path),
        "--friction-threshold",
        "1",
        "--execute",
        "--github-repo",
        "corca-ai/charness",
        "--issue-number",
        "280",
        "--gh-bin",
        str(tmp_path / "missing-gh"),
        "--json",
    )

    assert result.returncode == 127
    payload = json.loads(result.stdout)
    assert payload["status"] == "gh_unavailable"
    assert payload["executed"] is False


def test_product_review_requires_corca_internal_for_target_refs(tmp_path: Path) -> None:
    result = run_product_review("--repo-root", str(tmp_path), "--repo-ref", "corca-ai/charness", "--json")

    assert result.returncode != 0
    assert "--repo-ref requires --corca-internal" in result.stderr


def test_plugin_usage_product_review_smoke(tmp_path: Path) -> None:
    write_adapter(tmp_path, "version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\n")
    write_records(tmp_path, [crill_episode()])

    result = run_plugin_product_review("--repo-root", str(tmp_path), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "valid"
    assert payload["review_summary"]["last_seen_at"] == "2026-05-17T04:05:00Z"
