from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

from scripts import record_usage_feedback
from scripts.usage_episode_feedback import (
    FEEDBACK_SIGNALS,
    FRICTION_SIGNALS,
    NEUTRAL_SIGNALS,
    SATISFACTION_SIGNALS,
    classification_counts,
    feedback_id_for,
    reconcile_feedback,
)
from scripts.usage_episode_records import (
    read_schema_valid_records,
    read_valid_records,
    resolve_records_path,
    schema_root,
)
from tests.test_usage_episodes_schema import acme_episode

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((REPO_ROOT / "integrations" / "usage-episodes" / "episode.schema.json").read_text(encoding="utf-8"))
VALIDATOR = REPO_ROOT / "scripts" / "validate_usage_episodes.py"
WRITER = REPO_ROOT / "scripts" / "record_usage_feedback.py"
PLUGIN_WRITER = REPO_ROOT / "plugins" / "charness" / "scripts" / "record_usage_feedback.py"
REPORTER = REPO_ROOT / "scripts" / "report_usage_episodes.py"
PLUGIN_REPORTER = REPO_ROOT / "plugins" / "charness" / "scripts" / "report_usage_episodes.py"


def feedback_record(**overrides: object) -> dict[str, object]:
    evidence_ref = {"kind": "review", "ref": "review-001"}
    record: dict[str, object] = {
        "schema_version": 1,
        "event_type": "usage_feedback",
        "timestamp": "2026-07-10T01:00:00Z",
        "product_id": "acme",
        "target_episode_id": "acme-episode-001",
        "feedback_signal": "accepted",
        "source_kind": "operator",
        "evidence_ref": evidence_ref,
    }
    record.update(overrides)
    if "feedback_id" not in overrides:
        record["feedback_id"] = feedback_id_for(
            product_id=str(record["product_id"]),
            target_episode_id=str(record["target_episode_id"]),
            feedback_signal=str(record["feedback_signal"]),
            source_kind=str(record["source_kind"]),
            evidence_ref=dict(record["evidence_ref"]),
        )
    return record


def write_adapter(repo: Path, *, events: str = "  - usage_episode\n  - usage_feedback\n") -> Path:
    adapter = repo / ".agents" / "usage-episodes-adapter.yaml"
    adapter.parent.mkdir(parents=True, exist_ok=True)
    adapter.write_text(f"version: 1\nenabled: true\nstorage_path: .charness/usage-episodes\nevents:\n{events}", encoding="utf-8")
    return adapter


def write_records(repo: Path, records: list[dict[str, object]]) -> Path:
    path = repo / ".charness" / "usage-episodes" / "usage_episode.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
    return path


def run(script: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    child_env = os.environ.copy()
    child_env.pop("CHARNESS_QUALITY_MODE", None)
    if env is not None:
        child_env.update(env)
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=child_env,
    )


def test_usage_feedback_schema_requires_closed_safe_fields() -> None:
    jsonschema.validate(feedback_record(), SCHEMA)
    for invalid in (
        feedback_record(feedback_signal="unknown"),
        feedback_record(target_episode_id=""),
        feedback_record(evidence_ref={"kind": "review", "ref": "operator said accepted"}),
        feedback_record(evidence_ref={"kind": "review", "ref": "review-001", "body": "raw body"}),
        feedback_record(user_identity="person@example.test"),
    ):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(invalid, SCHEMA)
    source_mismatch = feedback_record(source_kind="issue_lifecycle", feedback_signal="accepted")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(source_mismatch, SCHEMA)


def test_target_episode_id_accepts_every_schema_valid_episode_id() -> None:
    delivery = acme_episode()
    delivery["episode_id"] = "opaque target id with spaces"
    feedback = feedback_record(target_episode_id=delivery["episode_id"])
    jsonschema.validate(delivery, SCHEMA)
    jsonschema.validate(feedback, SCHEMA)


def test_feedback_writer_dry_run_execute_replay_and_privacy(tmp_path: Path) -> None:
    write_adapter(tmp_path)
    write_records(tmp_path, [acme_episode()])
    args = (
        "--repo-root", str(tmp_path), "--product-id", "acme", "--target-episode-id", "acme-episode-001",
        "--feedback-signal", "accepted", "--source-kind", "operator", "--evidence-kind", "review", "--evidence-ref", "review-001", "--json",
    )
    preview = run(WRITER, *args)
    assert preview.returncode == 0, preview.stderr
    assert json.loads(preview.stdout)["status"] == "dry_run"
    records_path = tmp_path / ".charness" / "usage-episodes" / "usage_episode.jsonl"
    assert len(records_path.read_text(encoding="utf-8").splitlines()) == 1

    appended = run(WRITER, *args[:-1], "--execute", "--json")
    assert appended.returncode == 0, appended.stderr
    assert json.loads(appended.stdout)["status"] == "appended"
    replay = run(WRITER, *args[:-1], "--execute", "--json")
    assert replay.returncode == 0, replay.stderr
    assert json.loads(replay.stdout)["status"] == "replay_noop"
    assert len(records_path.read_text(encoding="utf-8").splitlines()) == 2

    unsafe = run(WRITER, *args[:-1], "--evidence-ref", "operator said accepted", "--json")
    assert unsafe.returncode == 2
    assert json.loads(unsafe.stdout)["status"] == "invalid_feedback"


def test_plugin_feedback_writer_smoke(tmp_path: Path) -> None:
    write_adapter(tmp_path)
    write_records(tmp_path, [acme_episode()])
    result = run(
        PLUGIN_WRITER,
        "--repo-root", str(tmp_path), "--product-id", "acme", "--target-episode-id", "acme-episode-001",
        "--feedback-signal", "accepted", "--source-kind", "operator", "--evidence-kind", "review", "--evidence-ref", "review-001", "--execute", "--json",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "appended"
    report = run(PLUGIN_REPORTER, "--repo-root", str(tmp_path), "--json")
    assert report.returncode == 0, report.stderr
    payload = json.loads(report.stdout)
    assert payload["delivery_episode_count"] == 1
    assert payload["feedback_event_count"] == 1
    assert payload["product_evidence"]["feedback_coverage_rate"] == 1.0
    assert payload["product_evidence"]["satisfaction_signal_count"] == 1


def test_feedback_writer_rejects_missing_target_disabled_event_and_quality_mode(tmp_path: Path) -> None:
    write_adapter(tmp_path)
    base = (
        "--repo-root", str(tmp_path), "--product-id", "acme", "--target-episode-id", "missing",
        "--feedback-signal", "accepted", "--source-kind", "operator", "--evidence-kind", "review", "--evidence-ref", "review-001", "--json",
    )
    missing = run(WRITER, *base)
    assert missing.returncode == 2
    assert "unlinked target_episode_id" in json.loads(missing.stdout)["errors"][0]

    write_adapter(tmp_path, events="  - usage_episode\n")
    disabled = run(WRITER, *base)
    assert disabled.returncode == 2
    assert json.loads(disabled.stdout)["status"] == "disabled"

    write_adapter(tmp_path)
    write_records(tmp_path, [acme_episode()])
    quality_args = (
        "--repo-root", str(tmp_path), "--product-id", "acme", "--target-episode-id", "acme-episode-001",
        "--feedback-signal", "accepted", "--source-kind", "operator", "--evidence-kind", "review", "--evidence-ref", "review-001", "--json",
    )
    quality_env = {"CHARNESS_QUALITY_MODE": "read-only"}
    preview = run(WRITER, *quality_args, env=quality_env)
    assert preview.returncode == 0
    assert json.loads(preview.stdout)["status"] == "dry_run"
    quality = run(WRITER, *quality_args[:-1], "--execute", "--json", env=quality_env)
    assert quality.returncode == 2
    assert json.loads(quality.stdout)["status"] == "readonly_quality_run"
    assert len((tmp_path / ".charness" / "usage-episodes" / "usage_episode.jsonl").read_text(encoding="utf-8").splitlines()) == 1

    incompatible = run(WRITER, *base[:-1], "--source-kind", "issue_lifecycle", "--json")
    assert incompatible.returncode == 2
    assert json.loads(incompatible.stdout)["status"] == "invalid_feedback"


def test_feedback_writer_renders_plain_errors_and_portable_fallback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    outside = tmp_path.parent / "outside-feedback.jsonl"
    assert record_usage_feedback._portable_path(tmp_path, outside) == str(outside)

    record_usage_feedback._print(
        {"status": "no_adapter", "executed": False, "errors": ["adapter required"]},
        False,
    )
    output = capsys.readouterr().out
    assert "no_adapter: feedback_id=<none>" in output
    assert "- adapter required" in output


def test_feedback_writer_adapter_error_and_relative_path_branches(tmp_path: Path) -> None:
    args = (
        "--repo-root", str(tmp_path), "--product-id", "acme", "--target-episode-id", "acme-episode-001",
        "--feedback-signal", "accepted", "--source-kind", "operator", "--evidence-kind", "review", "--evidence-ref", "review-001", "--json",
    )
    missing = run(WRITER, *args)
    assert missing.returncode == 2
    assert json.loads(missing.stdout)["status"] == "no_adapter"

    plain_missing = run(WRITER, *args[:-1])
    assert plain_missing.returncode == 2
    assert "no_adapter: feedback_id=<none>" in plain_missing.stdout
    assert "usage-episodes adapter is required" in plain_missing.stdout

    adapter_path = write_adapter(tmp_path)
    write_records(tmp_path, [acme_episode()])
    relative = run(WRITER, *args[:-1], "--adapter-path", ".agents/usage-episodes-adapter.yaml", "--json")
    assert relative.returncode == 0, relative.stderr
    assert json.loads(relative.stdout)["status"] == "dry_run"

    adapter_path.write_text("- not-a-mapping\n", encoding="utf-8")
    wrong_shape = run(WRITER, *args)
    assert wrong_shape.returncode == 2
    assert "must be a mapping" in json.loads(wrong_shape.stdout)["errors"][0]

    adapter_path.write_text("version: [\n", encoding="utf-8")
    malformed = run(WRITER, *args)
    assert malformed.returncode == 2
    assert json.loads(malformed.stdout)["status"] == "invalid_adapter"


def test_feedback_writer_rejects_symlinked_storage_escape(tmp_path: Path) -> None:
    adapter = write_adapter(tmp_path)
    adapter.write_text(
        "version: 1\nenabled: true\nstorage_path: escape\nevents:\n  - usage_episode\n  - usage_feedback\n",
        encoding="utf-8",
    )
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    (tmp_path / "escape").symlink_to(outside, target_is_directory=True)
    result = run(
        WRITER,
        "--repo-root", str(tmp_path), "--product-id", "acme", "--target-episode-id", "acme-episode-001",
        "--feedback-signal", "accepted", "--source-kind", "operator", "--evidence-kind", "review", "--evidence-ref", "review-001", "--json",
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "invalid_records_path"


def test_feedback_writer_rejects_conflicting_existing_feedback_id(tmp_path: Path) -> None:
    write_adapter(tmp_path)
    conflicting = feedback_record()
    conflicting["feedback_signal"] = "corrected"
    write_records(tmp_path, [acme_episode(), conflicting])
    result = run(
        WRITER,
        "--repo-root", str(tmp_path), "--product-id", "acme", "--target-episode-id", "acme-episode-001",
        "--feedback-signal", "accepted", "--source-kind", "operator", "--evidence-kind", "review", "--evidence-ref", "review-001", "--json",
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "conflicting_feedback_id"
    assert any("non-deterministic feedback_id" in error for error in payload["errors"])


def test_feedback_writer_rejects_schema_invalid_existing_stream_without_mutating_it(tmp_path: Path) -> None:
    write_adapter(tmp_path)
    records_path = write_records(tmp_path, [acme_episode()])
    original = records_path.read_bytes() + b'{"event_type":"usage_feedback"}\n'
    records_path.write_bytes(original)

    result = run(
        WRITER,
        "--repo-root", str(tmp_path), "--product-id", "acme", "--target-episode-id", "acme-episode-001",
        "--feedback-signal", "accepted", "--source-kind", "operator", "--evidence-kind", "review", "--evidence-ref", "review-001", "--execute", "--json",
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid_feedback"
    assert any("schema error" in error for error in payload["errors"])
    assert records_path.read_bytes() == original


def test_validator_rejects_unlinked_and_duplicate_feedback_ids(tmp_path: Path) -> None:
    write_adapter(tmp_path)
    base = acme_episode()
    unlinked = feedback_record(target_episode_id="missing")
    write_records(tmp_path, [base, unlinked])
    result = run(VALIDATOR, "--repo-root", str(tmp_path), "--json")
    assert result.returncode == 1
    assert "unlinked target_episode_id" in json.loads(result.stdout)["errors"][0]

    linked = feedback_record()
    write_records(tmp_path, [base, linked, dict(linked)])
    duplicate = run(VALIDATOR, "--repo-root", str(tmp_path), "--json")
    assert duplicate.returncode == 1
    assert "duplicate feedback_id" in json.loads(duplicate.stdout)["errors"][0]

    mismatched = feedback_record(feedback_id="feedback-" + "0" * 64)
    write_records(tmp_path, [base, mismatched])
    deterministic = run(VALIDATOR, "--repo-root", str(tmp_path), "--json")
    assert deterministic.returncode == 1
    assert "non-deterministic feedback_id" in json.loads(deterministic.stdout)["errors"][0]


def test_shared_record_reader_returns_records_and_semantic_errors(tmp_path: Path) -> None:
    records_path = write_records(tmp_path, [acme_episode(), feedback_record(), feedback_record()])
    structural_records, structural_errors = read_schema_valid_records(records_path, SCHEMA)
    assert len(structural_records) == 3
    assert structural_errors == []
    records, errors = read_valid_records(records_path, SCHEMA)
    assert len(records) == 3
    assert any("duplicate feedback_id" in error for error in errors)


def test_shared_record_reader_handles_schema_fallback_blanks_and_invalid_json(tmp_path: Path) -> None:
    assert schema_root(tmp_path) == REPO_ROOT / "integrations" / "usage-episodes"
    local_schema_root = tmp_path / "integrations" / "usage-episodes"
    local_schema_root.mkdir(parents=True)
    for schema_name in ("manifest.schema.json", "episode.schema.json"):
        (local_schema_root / schema_name).write_text("{}\n", encoding="utf-8")
    assert schema_root(tmp_path) == local_schema_root

    relative_records_path = Path("custom") / "records.jsonl"
    assert resolve_records_path(tmp_path, {}, relative_records_path) == (tmp_path / relative_records_path).resolve()
    absolute_records_path = tmp_path.parent / "absolute-records.jsonl"
    assert resolve_records_path(tmp_path, {}, absolute_records_path) == absolute_records_path.resolve()

    records_path = tmp_path / "usage_episode.jsonl"
    records_path.write_text(f"\n{json.dumps(acme_episode())}\n\n", encoding="utf-8")
    records, errors = read_valid_records(records_path, SCHEMA)
    assert records == [acme_episode()]
    assert errors == []

    records_path.write_text("{not-json\n", encoding="utf-8")
    records, errors = read_valid_records(records_path, SCHEMA)
    assert records == []
    assert any("invalid JSON" in error for error in errors)

    invalid_timestamp = acme_episode()
    invalid_timestamp["timestamp"] = "2026-07-10T01:00:60Z"
    records_path.write_text(json.dumps(invalid_timestamp) + "\n", encoding="utf-8")
    records, errors = read_valid_records(records_path, SCHEMA)
    assert records == []
    assert any("schema error at timestamp" in error for error in errors)


def test_reconcile_feedback_counts_duplicate_and_unlinked_events() -> None:
    linked = feedback_record()
    unlinked = feedback_record(target_episode_id="missing")
    reconciliation = reconcile_feedback([acme_episode(), linked, dict(linked), unlinked])
    assert reconciliation["duplicate_feedback_id_count"] == 1
    assert reconciliation["unlinked_feedback_count"] == 1


def test_reconcile_feedback_keeps_duplicate_deliveries_in_the_denominator() -> None:
    delivery = acme_episode()
    delivery.pop("feedback_signal")
    reconciliation = reconcile_feedback([delivery, dict(delivery), feedback_record()])

    assert reconciliation["delivery_episode_count"] == 2
    assert reconciliation["feedback_coverage_count"] == 1
    assert reconciliation["feedback_coverage_rate"] == 0.5


def test_report_reconciles_one_delivery_and_one_feedback_event(tmp_path: Path) -> None:
    write_adapter(tmp_path)
    delivery = acme_episode()
    delivery.pop("feedback_signal")
    write_records(tmp_path, [delivery, feedback_record()])
    result = run(REPORTER, "--repo-root", str(tmp_path), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["delivery_episode_count"] == 1
    assert payload["feedback_event_count"] == 1
    assert payload["product_evidence"]["feedback_coverage_rate"] == 1.0
    assert payload["product_evidence"]["satisfaction_signal_count"] == 1
    assert payload["feedback_reconciliation"] == {
        "linked_count": 1,
        "unlinked_count": 0,
        "duplicate_feedback_id_count": 0,
        "inline_feedback_count": 0,
    }


def test_reconciled_explicit_feedback_uses_its_delivery_dimensions() -> None:
    delivery = acme_episode()
    delivery.pop("feedback_signal")
    reconciliation = reconcile_feedback([delivery, feedback_record(feedback_signal="retried")])

    assert reconciliation["signal_records"] == [
        {
            **delivery,
            "feedback_signal": "retried",
        }
    ]


@pytest.mark.parametrize(
    "feedback_rows, error_text",
    [
        ([feedback_record(), feedback_record()], "duplicate feedback_id"),
        ([feedback_record(target_episode_id="missing")], "unlinked target_episode_id"),
        ([feedback_record(feedback_id="feedback-" + "0" * 64)], "non-deterministic feedback_id"),
    ],
)
def test_report_rejects_semantically_invalid_feedback(
    tmp_path: Path,
    feedback_rows: list[dict[str, object]],
    error_text: str,
) -> None:
    write_adapter(tmp_path)
    write_records(tmp_path, [acme_episode(), *feedback_rows])
    result = run(REPORTER, "--repo-root", str(tmp_path), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid_records"
    assert any(error_text in error for error in payload["errors"])
    assert "product_evidence" not in payload


def test_feedback_signal_classification_covers_the_closed_vocabulary() -> None:
    assert FEEDBACK_SIGNALS == SATISFACTION_SIGNALS | FRICTION_SIGNALS | NEUTRAL_SIGNALS
    assert NEUTRAL_SIGNALS == {"edited"}
    classified = classification_counts([{"feedback_signal": signal} for signal in FEEDBACK_SIGNALS])
    assert classified == {"satisfaction": 4, "friction": 4, "neutral": 1, "unclassified": 0}
