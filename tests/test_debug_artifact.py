from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def seed_repo(tmp_path: Path, artifact_body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/debug",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(artifact_body, encoding="utf-8")
    return repo


def valid_current_artifact(*, next_step: str = "impl", handoff_artifact: str = "none", risk_class: str = "none") -> str:
    return (
        "\n".join(
            [
                "# Debug Review",
                "Date: 2026-04-22",
                "",
                "## Problem",
                "",
                "problem",
                "",
                "## Correct Behavior",
                "",
                "correct",
                "",
                "## Observed Facts",
                "",
                "- fact",
                "",
                "## Reproduction",
                "",
                "repro",
                "",
                "## Candidate Causes",
                "",
                "- one",
                "- two",
                "- three",
                "",
                "## Hypothesis",
                "",
                "hypothesis",
                "",
                "## Verification",
                "",
                "verification",
                "",
                "## Root Cause",
                "",
                "root cause",
                "",
                "## Invariant Proof",
                "",
                "- Invariant: n/a - not a workflow-boundary propagation bug",
                "- Producer Proof: n/a",
                "- Final-Consumer Proof: n/a",
                "- Interface-Shape Sibling Scan: n/a",
                "- Non-Claims: n/a",
                "",
                "## Detection Gap",
                "",
                "- test suite | did not assert volatile root exclusion | add `.cautilus` to ignore set",
                "",
                "## Sibling Search",
                "",
                "- Mental model: synthetic copy fixtures treat runtime roots as input",
                "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
                "",
                "## Seam Risk",
                "",
                "- Interrupt ID: demo-interrupt",
                f"- Risk Class: {risk_class}",
                "- Seam: none",
                "- Disproving Observation: none",
                "- What Local Reasoning Cannot Prove: none",
                "- Generalization Pressure: none",
                "",
                "## Interrupt Decision",
                "",
                f"- Critique Required: {'yes' if next_step == 'spec' else 'no'}",
                f"- Next Step: {next_step}",
                f"- Handoff Artifact: {handoff_artifact}",
                "",
                "## Prevention",
                "",
                "prevention",
                "",
            ]
        )
        + "\n"
    )


def test_validate_debug_artifact_rejects_extra_top_level_section(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_current_artifact().replace(
            "## Hypothesis\n\nhypothesis\n\n",
            "## Hypothesis\n\nhypothesis\n\n## Session Log\n\n- log\n\n",
        ),
    )
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "canonical sections" in result.stderr


def test_validate_debug_artifact_requires_three_candidate_causes(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_current_artifact().replace("- three\n", ""),
    )
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "at least three plausible causes" in result.stderr


def test_validate_debug_artifact_requires_interrupt_sections_for_latest(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_current_artifact().replace(
            "## Seam Risk\n\n- Interrupt ID: demo-interrupt\n- Risk Class: none\n- Seam: none\n- Disproving Observation: none\n- What Local Reasoning Cannot Prove: none\n- Generalization Pressure: none\n\n## Interrupt Decision\n\n- Critique Required: no\n- Next Step: impl\n- Handoff Artifact: none\n\n",
            "",
        ),
    )
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required section `## Seam Risk`" in result.stderr
    assert "Invalid debug artifact charness-artifacts/debug/latest.md" in result.stderr


def test_validate_debug_artifact_requires_invariant_proof_for_latest(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_current_artifact().replace(
            "## Invariant Proof\n\n- Invariant: n/a - not a workflow-boundary propagation bug\n- Producer Proof: n/a\n- Final-Consumer Proof: n/a\n- Interface-Shape Sibling Scan: n/a\n- Non-Claims: n/a\n\n",
            "",
        ),
    )
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required section `## Invariant Proof`" in result.stderr


def test_validate_debug_artifact_requires_invariant_proof_fields(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_current_artifact().replace("- Final-Consumer Proof: n/a\n", ""),
    )
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required line `- Final-Consumer Proof: ...`" in result.stderr


def test_validate_debug_artifact_allows_legacy_extra_sections_for_dated_records(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, valid_current_artifact())
    latest = repo / "charness-artifacts" / "debug" / "latest.md"
    latest.unlink()
    legacy = valid_current_artifact().replace(
        "## Seam Risk\n\n- Interrupt ID: demo-interrupt\n- Risk Class: none\n- Seam: none\n- Disproving Observation: none\n- What Local Reasoning Cannot Prove: none\n- Generalization Pressure: none\n\n## Interrupt Decision\n\n- Critique Required: no\n- Next Step: impl\n- Handoff Artifact: none\n\n",
        "## Legacy Notes\n\nlegacy detail\n\n",
    )
    (repo / "charness-artifacts" / "debug" / "2026-04-01-legacy.md").write_text(legacy, encoding="utf-8")

    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "Validated debug artifact charness-artifacts/debug/2026-04-01-legacy.md" in result.stdout


def test_validate_debug_artifact_rejects_latest_legacy_extra_sections(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_current_artifact().replace(
            "## Seam Risk\n\n- Interrupt ID: demo-interrupt\n- Risk Class: none\n- Seam: none\n- Disproving Observation: none\n- What Local Reasoning Cannot Prove: none\n- Generalization Pressure: none\n\n",
            "## Legacy Notes\n\nlegacy detail\n\n",
        ),
    )

    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Invalid debug artifact charness-artifacts/debug/latest.md" in result.stderr
    assert "canonical sections" in result.stderr


def test_validate_debug_artifact_reports_failing_historical_artifact_path(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, valid_current_artifact())
    broken = valid_current_artifact().replace("## Candidate Causes", "## Candidates")
    (repo / "charness-artifacts" / "debug" / "2026-04-01-broken.md").write_text(broken, encoding="utf-8")

    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Invalid debug artifact charness-artifacts/debug/2026-04-01-broken.md" in result.stderr
    assert "missing required section `## Candidate Causes`" in result.stderr


def test_validate_debug_artifact_forced_interrupt_requires_spec_handoff(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_current_artifact(next_step="impl", handoff_artifact="none", risk_class="external-seam"),
    )
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "forced risk interrupt" in result.stderr


def test_validate_debug_artifact_rejects_followup_sibling_without_identifier(tmp_path: Path) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        "- same layer: tests/repo_copy.py:12 | decision: valid follow-up outside the slice | proof: static scan only",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "follow-up:" in result.stderr


def test_validate_debug_artifact_accepts_followup_sibling_with_issue_url(tmp_path: Path) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        "- same layer: tests/repo_copy.py:12 | decision: valid follow-up outside the slice | proof: static scan only | follow-up: https://example.com/issues/42",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_debug_artifact_accepts_followup_sibling_with_handoff_anchor(tmp_path: Path) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        "- same layer: tests/repo_copy.py:12 | decision: valid follow-up outside the slice | proof: static scan only | follow-up: deferred docs/handoff.md#cleanup-backlog",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_debug_artifact_ignores_prose_mention_of_decision_phrase(tmp_path: Path) -> None:
    # A prose paragraph (no leading `- ` bullet and no `decision:` token) that
    # quotes the decision phrase must not trip the validator.
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        (
            "- same layer: tests/repo_copy.py and scripts/check_coverage.py\n"
            "Authors may discuss the `valid follow-up outside the slice` rule "
            "in commentary without surfacing a fileable sibling."
        ),
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_debug_artifact_rejects_title_case_decision(tmp_path: Path) -> None:
    # Title-case must not silently bypass enforcement.
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        "- same layer: tests/repo_copy.py:12 | decision: Valid Follow-Up Outside The Slice | proof: static scan only",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "follow-up:" in result.stderr


def test_validate_debug_artifact_accepts_ascii_dash_short_circuit(tmp_path: Path) -> None:
    # The trivial-bug short-circuit must accept ASCII `-` as well as em-dash.
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        "- n/a - trivial fix; no plausible siblings",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_debug_artifact_reports_first_invalid_with_offender_text(tmp_path: Path) -> None:
    # Mixed bullets: the validator should surface the offending bullet snippet.
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        (
            "- same layer: tests/repo_copy.py:12 | decision: same bug, fix now | proof: static scan only\n"
            "- abstraction up: lib/foo.py:42 | decision: valid follow-up outside the slice | proof: not inspected"
        ),
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "abstraction up: lib/foo.py:42" in result.stderr


def test_validate_debug_artifact_rejects_bare_deferred_followup(tmp_path: Path) -> None:
    # `follow-up: deferred` with no anchor must not satisfy the rule.
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        "- same layer: tests/repo_copy.py:12 | decision: valid follow-up outside the slice | proof: not inspected | follow-up: deferred",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "follow-up:" in result.stderr


def test_validate_debug_artifact_rejects_deferred_with_whitespace_only_anchor(tmp_path: Path) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        "- same layer: tests/repo_copy.py:12 | decision: valid follow-up outside the slice | proof: not inspected | follow-up: deferred   ",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1


def test_validate_debug_artifact_rejects_deferred_with_trailing_punctuation(tmp_path: Path) -> None:
    # `deferred.` / `deferred,` are still a bare deferred with no anchor.
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        "- same layer: tests/repo_copy.py:12 | decision: valid follow-up outside the slice | proof: not inspected | follow-up: deferred.",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "follow-up:" in result.stderr


def test_validate_debug_artifact_accepts_short_non_deferred_identifier(tmp_path: Path) -> None:
    # A non-deferred identifier (e.g., a bare issue number) is acceptable.
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        "- same layer: tests/repo_copy.py:12 | decision: valid follow-up outside the slice | proof: not inspected | follow-up: #199",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
