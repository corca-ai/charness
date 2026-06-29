from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from .cautilus_artifact_support import (
    run_diagnostic_validator,
    seed_repo,
    write_diagnostic_finding,
    write_summary_evidence,
    write_trace_digest,
)
from .charness_cli.support import ROOT


def test_validate_cautilus_diagnostics_accepts_negative_bundle(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    write_summary_evidence(bundle)

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/finding.md")

    assert result.returncode == 0, result.stderr
    assert "validated 1 cautilus diagnostic bundle" in result.stdout


def test_validate_cautilus_diagnostics_requires_machine_evidence(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle, source="## Fixture", verdict="## Deterministic Observed Packet", interpretation="## Non-Claims")

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/finding.md")

    assert result.returncode == 1
    assert "must include one machine evidence file" in result.stderr


def test_validate_cautilus_diagnostics_rejects_machine_evidence_without_finding(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    (bundle / "observed.v1.json").write_text(
        json.dumps(
            {
                "schemaVersion": "cautilus.skill_evaluation_inputs.v1",
                "evaluations": [{"outcome": "failed"}],
            }
        ),
        encoding="utf-8",
    )

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/observed.v1.json")

    assert result.returncode == 1
    assert "must include `finding.md`" in result.stderr


def test_validate_cautilus_diagnostics_ignores_latest_proof_pointer(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, "# Cautilus Dogfood\n")

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/latest.md")

    assert result.returncode == 0, result.stderr
    assert "no changed cautilus diagnostic bundles" in result.stdout


def test_validate_cautilus_diagnostics_ignores_unrelated_and_raw_changed_paths(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    (bundle / "raw.log").write_text("transcript\n", encoding="utf-8")

    result = run_diagnostic_validator(
        repo,
        "docs/noop.md",
        "charness-artifacts/cautilus/demo-diagnostic/raw.log",
    )

    assert result.returncode == 0, result.stderr
    assert "no changed cautilus diagnostic bundles" in result.stdout


def test_validate_cautilus_diagnostics_deduplicates_changed_paths(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    write_summary_evidence(bundle)

    result = run_diagnostic_validator(
        repo,
        "charness-artifacts/cautilus/demo-diagnostic/finding.md",
        "charness-artifacts/cautilus/demo-diagnostic/summary.v1.json",
    )

    assert result.returncode == 0, result.stderr
    assert "validated 1 cautilus diagnostic bundle" in result.stdout


def test_validate_cautilus_diagnostics_all_mode_scans_only_diagnostic_dirs(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    root = repo / "charness-artifacts" / "cautilus"
    (root / "latest.md").write_text("# pointer\n", encoding="utf-8")
    (root / "chatbot-proposals" / "demo").mkdir(parents=True)
    (root / "chatbot-proposals" / "demo" / "summary.v1.json").write_text("{}", encoding="utf-8")
    (root / "skill-experiment-demo").mkdir()
    (root / "skill-experiment-demo" / "report.json").write_text("{}", encoding="utf-8")
    bundle = root / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    write_summary_evidence(bundle)

    result = run_diagnostic_validator(repo, all_bundles=True)

    assert result.returncode == 0, result.stderr
    assert "validated 1 cautilus diagnostic bundle" in result.stdout


def test_validate_cautilus_diagnostics_all_mode_handles_missing_root(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    shutil.rmtree(repo / "charness-artifacts" / "cautilus")

    result = run_diagnostic_validator(repo, all_bundles=True)

    assert result.returncode == 0, result.stderr
    assert "no changed cautilus diagnostic bundles" in result.stdout


def test_validate_cautilus_diagnostics_rejects_invalid_json(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    (bundle / "summary.v1.json").write_text("{", encoding="utf-8")

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/summary.v1.json")

    assert result.returncode == 1
    assert "is not valid JSON" in result.stderr


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ([], "must contain a JSON object"),
        ({}, "must contain a non-empty `evaluations` list"),
        ({"evaluations": ["failed"]}, "evaluation 0 must be an object"),
        ({"evaluations": [{"outcome": "unknown"}]}, "must carry `outcome/status"),
    ],
)
def test_validate_cautilus_diagnostics_rejects_invalid_observed_evidence(
    tmp_path: Path, payload: object, expected: str
) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    (bundle / "observed.v1.json").write_text(json.dumps(payload), encoding="utf-8")

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/observed.v1.json")

    assert result.returncode == 1
    assert expected in result.stderr


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ([], "must contain a JSON object"),
        ({"recommendation": "maybe", "evaluations": [{"status": "failed"}]}, "`recommendation` must be one of"),
        ({"recommendation": "reject"}, "must contain `evaluations` or `evaluationRuns`"),
    ],
)
def test_validate_cautilus_diagnostics_rejects_invalid_summary_evidence(
    tmp_path: Path, payload: object, expected: str
) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    write_summary_evidence(bundle, payload)

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/summary.v1.json")

    assert result.returncode == 1
    assert expected in result.stderr


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ([], "must contain a JSON object"),
        ({}, "must carry a schema version"),
    ],
)
def test_validate_cautilus_diagnostics_rejects_invalid_report_evidence(
    tmp_path: Path, payload: object, expected: str
) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    (bundle / "report.json").write_text(json.dumps(payload), encoding="utf-8")

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/report.json")

    assert result.returncode == 1
    assert expected in result.stderr


def test_validate_cautilus_diagnostics_accepts_observed_and_report_evidence(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    (bundle / "observed.v1.json").write_text(
        json.dumps({"evaluations": [{"outcome": "failed"}, {"status": "blocked"}]}),
        encoding="utf-8",
    )
    (bundle / "report.json").write_text(json.dumps({"schema_version": 1}), encoding="utf-8")

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/observed.v1.json")

    assert result.returncode == 0, result.stderr
    assert "validated 1 cautilus diagnostic bundle" in result.stdout


@pytest.mark.parametrize(
    ("finding_kwargs", "expected"),
    [
        ({"title": "Demo diagnostic"}, "must start with an H1 title"),
        ({"source": "## Details"}, "must name the behavior source or fixture"),
        ({"verdict": "## Details"}, "must carry a verdict"),
        (
            {"interpretation": "## Details", "interpretation_item": "- details"},
            "must include diagnosis, non-claims, follow-up",
        ),
    ],
)
def test_validate_cautilus_diagnostics_rejects_invalid_finding_shape(
    tmp_path: Path, finding_kwargs: dict[str, str], expected: str
) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle, **finding_kwargs)
    write_summary_evidence(bundle)

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/finding.md")

    assert result.returncode == 1
    assert expected in result.stderr


def test_validate_cautilus_diagnostics_rejects_oversized_finding(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle, extra_lines=["- filler"] * 190)
    write_summary_evidence(bundle)

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/finding.md")

    assert result.returncode == 1
    assert "should stay concise" in result.stderr


def test_validate_cautilus_diagnostics_accepts_valid_trace_digest(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    write_summary_evidence(bundle)
    write_trace_digest(bundle)

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/trace-digest.jsonl")

    assert result.returncode == 0, result.stderr
    assert "validated 1 cautilus diagnostic bundle" in result.stdout


def test_validate_cautilus_diagnostics_rejects_malformed_trace_digest(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    bundle = repo / "charness-artifacts" / "cautilus" / "demo-diagnostic"
    bundle.mkdir()
    write_diagnostic_finding(bundle)
    write_summary_evidence(bundle)
    (bundle / "trace-digest.jsonl").write_text('{"step": 1}\n', encoding="utf-8")

    result = run_diagnostic_validator(repo, "charness-artifacts/cautilus/demo-diagnostic/finding.md")

    assert result.returncode == 1
    assert "must be an object with a string `name`" in result.stderr


def test_run_quality_uses_all_cautilus_diagnostics_mode() -> None:
    run_quality = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")

    assert (
        'queue_selected "validate-cautilus-diagnostics" '
        'python3 scripts/validate_cautilus_diagnostics.py --repo-root "$REPO_ROOT" --all'
    ) in run_quality
