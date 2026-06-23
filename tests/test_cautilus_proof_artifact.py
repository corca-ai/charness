from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from .charness_cli.support import ROOT
from .test_quality_artifact import run_script


def seed_repo(tmp_path: Path, artifact_body: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "cautilus-adapters").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "skills" / "public" / "impl").mkdir(parents=True)
    (repo / "charness-artifacts" / "cautilus").mkdir(parents=True)
    (repo / "docs" / "public-skill-validation.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "tiers": {
                    "smoke-only": [],
                    "hitl-recommended": [],
                    "evaluator-required": ["impl"],
                },
                "adapter_requirements": {
                    "required": ["impl"],
                    "adapter-free": [],
                },
                "fallback_policy": {
                    "allow": ["impl"],
                    "visible": [],
                    "block": [],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "skills" / "public" / "impl" / "SKILL.md").write_text("# Impl\n", encoding="utf-8")
    (repo / ".agents" / "cautilus-adapters" / "chatbot-proposals.yaml").write_text("version: 1\n", encoding="utf-8")
    if artifact_body is not None:
        (repo / "charness-artifacts" / "cautilus" / "latest.md").write_text(artifact_body, encoding="utf-8")
    return repo


def write_diagnostic_finding(
    bundle: Path,
    *,
    title: str = "# Demo diagnostic",
    source: str = "## What ran",
    verdict: str = "## Verdict",
    interpretation: str = "## Diagnosis",
    interpretation_item: str = "- follow-up: https://github.com/corca-ai/charness/issues/398",
    extra_lines: list[str] | None = None,
) -> None:
    lines = [
        title,
        "",
        source,
        "",
        "- `/demo`",
        "",
        verdict,
        "",
        "- recommendation: reject",
        "",
        interpretation,
        "",
        interpretation_item,
        "",
    ]
    if extra_lines:
        lines.extend(extra_lines)
    (bundle / "finding.md").write_text("\n".join(lines), encoding="utf-8")


def write_summary_evidence(bundle: Path, payload: object | None = None) -> None:
    if payload is None:
        payload = {
            "schemaVersion": "cautilus.skill_evaluation_summary.v1",
            "recommendation": "reject",
            "evaluations": [{"status": "failed"}],
        }
    (bundle / "summary.v1.json").write_text(json.dumps(payload), encoding="utf-8")


def run_diagnostic_validator(repo: Path, *paths: str, all_bundles: bool = False):
    args = ["--repo-root", str(repo)]
    if all_bundles:
        args.append("--all")
    else:
        args.append("--paths")
        args.extend(paths)
    return run_script("scripts/validate_cautilus_diagnostics.py", *args)


def test_validate_cautilus_proof_keeps_prompt_changes_deterministic_without_artifact(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
    )
    assert result.returncode == 0, result.stderr
    assert "deterministic validation owns 1 prompt-affecting path(s)" in result.stdout


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


def test_run_quality_uses_all_cautilus_diagnostics_mode() -> None:
    run_quality = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")

    assert (
        'queue_selected "validate-cautilus-diagnostics" '
        'python3 scripts/validate_cautilus_diagnostics.py --repo-root "$REPO_ROOT" --all'
    ) in run_quality


def test_validate_cautilus_proof_requires_ab_compare_for_improve_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Cautilus Dogfood",
                "Date: 2026-04-18",
                "",
                "## Trigger",
                "",
                "- slice: demo",
                "- claim: `improve`",
                "",
                "## Validation Goal",
                "",
                "- goal: `improve`",
                "- reason: demo",
                "",
                "## Change Intent",
                "",
                "- prompt_affecting_change",
                "- skill_core_change",
                "- scenario_review_change",
                "",
                "## Prompt Surfaces",
                "",
                "- `skills/public/impl/SKILL.md`",
                "",
                "## Behavior Source",
                "",
                "- source-kind: `failing-prompt`",
                "- source-ref: `charness-artifacts/debug/demo-transcript.md`",
                "",
                "## Commands Run",
                "",
                "- `cautilus evaluate fixture --repo-root . --adapter-name self-dogfood-eval`",
                "",
                "## Regression Proof",
                "",
                "- eval test result: 1 passed / 0 failed / 0 blocked",
                "",
                "## Scenario Review",
                "",
                "- scenario: impl request still routes through impl and keeps adapter-sensitive review visible",
                "",
                "## Outcome",
                "",
                "- recommendation: `accept-now`",
                "",
                "## Follow-ups",
                "",
                "- demo",
                "",
            ]
        )
        + "\n",
    )
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
    )
    assert result.returncode == 1
    assert "`## A/B Compare` is required when `goal: improve`" in result.stderr


def test_validate_cautilus_proof_rejects_removed_instruction_surface_command(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Cautilus Dogfood",
                "Date: 2026-04-18",
                "",
                "## Trigger",
                "",
                "- slice: demo",
                "",
                "## Validation Goal",
                "",
                "- goal: `preserve`",
                "",
                "## Change Intent",
                "",
                "- prompt_affecting_change",
                "- skill_core_change",
                "- scenario_review_change",
                "",
                "## Prompt Surfaces",
                "",
                "- `skills/public/impl/SKILL.md`",
                "",
                "## Behavior Source",
                "",
                "- source-kind: `failing-prompt`",
                "- source-ref: `charness-artifacts/debug/demo-transcript.md`",
                "",
                "## Commands Run",
                "",
                "- `cautilus instruction-surface test --repo-root .`",
                "",
                "## Regression Proof",
                "",
                "- eval test result: 1 passed / 0 failed / 0 blocked",
                "",
                "## Scenario Review",
                "",
                "- scenario: demo",
                "",
                "## Outcome",
                "",
                "- recommendation: `accept-now`",
                "",
                "## Follow-ups",
                "",
                "- demo",
                "",
            ]
        )
        + "\n",
    )
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
    )
    assert result.returncode == 1
    assert "removed `cautilus instruction-surface test`" in result.stderr


def test_validate_cautilus_proof_requires_eval_result_not_generic_passed_line(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Cautilus Dogfood",
                "Date: 2026-04-18",
                "",
                "## Trigger",
                "",
                "- slice: demo",
                "",
                "## Validation Goal",
                "",
                "- goal: `preserve`",
                "",
                "## Change Intent",
                "",
                "- prompt_affecting_change",
                "- skill_core_change",
                "- scenario_review_change",
                "",
                "## Prompt Surfaces",
                "",
                "- `skills/public/impl/SKILL.md`",
                "",
                "## Behavior Source",
                "",
                "- source-kind: `failing-prompt`",
                "- source-ref: `charness-artifacts/debug/demo-transcript.md`",
                "",
                "## Commands Run",
                "",
                "- `cautilus evaluate fixture --repo-root . --adapter-name self-dogfood-eval`",
                "",
                "## Regression Proof",
                "",
                "- pytest passed",
                "",
                "## Scenario Review",
                "",
                "- scenario: demo",
                "",
                "## Outcome",
                "",
                "- recommendation: `accept-now`",
                "",
                "## Follow-ups",
                "",
                "- demo",
                "",
            ]
        )
        + "\n",
    )
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
    )
    assert result.returncode == 1
    assert "must record an eval result" in result.stderr


def test_validate_cautilus_proof_accepts_preserve_claim(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Cautilus Dogfood",
                "Date: 2026-04-18",
                "",
                "## Trigger",
                "",
                "- slice: demo",
                "- claim: `preserve`",
                "",
                "## Validation Goal",
                "",
                "- goal: `preserve`",
                "- reason: demo",
                "",
                "## Change Intent",
                "",
                "- prompt_affecting_change",
                "- skill_core_change",
                "- scenario_review_change",
                "",
                "## Prompt Surfaces",
                "",
                "- `skills/public/impl/SKILL.md`",
                "",
                "## Behavior Source",
                "",
                "- source-kind: `failing-prompt`",
                "- source-ref: `charness-artifacts/debug/demo-transcript.md`",
                "",
                "## Commands Run",
                "",
                "- `cautilus evaluate fixture --repo-root . --adapter-name self-dogfood-eval`",
                "",
                "## Regression Proof",
                "",
                "- eval test result: 1 passed / 0 failed / 0 blocked",
                "",
                "## Scenario Review",
                "",
                "- scenario: impl request still routes through impl and keeps adapter-sensitive review visible",
                "",
                "## Outcome",
                "",
                "- recommendation: `accept-now`",
                "",
                "## Follow-ups",
                "",
                "- demo",
                "",
            ]
        )
        + "\n",
    )
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
    )
    assert result.returncode == 0, result.stderr


def test_validate_cautilus_proof_rejects_legacy_route_only_fixture_as_behavior_proof(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Cautilus Dogfood",
                "Date: 2026-04-18",
                "",
                "## Trigger",
                "",
                "- slice: demo",
                "- claim: `preserve`",
                "",
                "## Validation Goal",
                "",
                "- goal: `preserve`",
                "- reason: demo",
                "",
                "## Change Intent",
                "",
                "- prompt_affecting_change",
                "- skill_core_change",
                "- scenario_review_change",
                "",
                "## Prompt Surfaces",
                "",
                "- `skills/public/impl/SKILL.md`",
                "",
                "## Behavior Source",
                "",
                "- source-kind: `failing-prompt`",
                "- source-ref: `charness-artifacts/debug/demo-transcript.md`",
                "",
                "## Commands Run",
                "",
                "- `cautilus evaluate fixture --repo-root . --adapter .agents/cautilus-adapter.yaml --fixture evals/cautilus/whole-repo-routing.fixture.json`",
                "",
                "## Regression Proof",
                "",
                "- eval test result: 5 passed / 0 failed / 0 blocked",
                "",
                "## Scenario Review",
                "",
                "- scenario: demo",
                "",
                "## Outcome",
                "",
                "- recommendation: `accept-now`",
                "",
                "## Follow-ups",
                "",
                "- demo",
                "",
            ]
        )
        + "\n",
    )
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
    )
    assert result.returncode == 1
    assert "legacy route-only fixture" in result.stderr


def test_validate_cautilus_proof_treats_named_cautilus_adapter_as_deterministic_without_artifact(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        ".agents/cautilus-adapters/chatbot-proposals.yaml",
    )
    assert result.returncode == 0, result.stderr
    assert "deterministic validation owns 1 prompt-affecting path(s)" in result.stdout


def test_validate_cautilus_proof_allows_disabled_adapter_without_artifact(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    (repo / ".agents" / "cautilus-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "run_mode: disabled",
                "disabled_reason: Cautilus is under active rework.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
    )

    assert result.returncode == 0, result.stderr
    assert "cautilus proof disabled by repo adapter" in result.stdout


def test_plan_cautilus_proof_recommends_skill_dogfood_and_scenario_followups() -> None:
    result = run_script(
        "scripts/plan_cautilus_proof.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/create-skill/SKILL.md",
        "charness-artifacts/cautilus/latest.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["run_mode"] == "ask"
    assert payload["status"] == "ready-for-validation"
    assert payload["recommended_commands"] == []
    assert payload["changed_public_skills"] == ["create-skill"]
    recommendation = payload["skill_validation_recommendations"][0]
    assert recommendation["skill_id"] == "create-skill"
    assert recommendation["validation_tier"] == "evaluator-required"
    assert any("docs/public-skill-dogfood.json" in note for note in recommendation["notes"])
    assert any(
        "python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id create-skill --json" == item
        for item in payload["recommended_followups"]
    )
    assert any("evals/cautilus/scenarios.json" in item for item in payload["recommended_followups"])


def test_plan_cautilus_proof_fails_closed_when_public_skill_policy_is_invalid(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "skills" / "public" / "demo").mkdir(parents=True)
    (repo / "docs" / "public-skill-validation.json").write_text("{not json\n", encoding="utf-8")
    (repo / "skills" / "public" / "demo" / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

    result = run_script(
        "scripts/plan_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/demo/SKILL.md",
        "--json",
    )

    assert result.returncode == 1
    assert "public-skill validation policy invalid while planning Cautilus proof" in result.stderr


def test_plan_cautilus_proof_adaptive_runs_without_ask_for_scenario_review(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, None)
    (repo / ".agents" / "cautilus-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "run_mode: adaptive",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/plan_cautilus_proof.py",
        "--repo-root",
        str(repo),
        "--paths",
        "skills/public/impl/SKILL.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["run_mode"] == "adaptive"
    assert payload["must_ask_before_running"] is False
    assert payload["scenario_registry_review_required"] is True
    assert payload["changed_public_skills"] == ["impl"]
    assert payload["next_action"] == "none"
