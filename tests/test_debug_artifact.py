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
                "- cross-file: scripts/check_coverage.py is outside the subject tests/repo_copy.py",
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


def test_validate_debug_artifact_rejects_abstraction_up_diagnostic_only_unresolved_work(tmp_path: Path) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        (
            "- abstraction up: messenger side-effect durability | "
            "decision: same class, diagnostic-only for this slice | "
            "proof: static scan only | deferred repo-level structural work"
        ),
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "abstraction-up diagnostic-only" in result.stderr
    assert "follow-up:" in result.stderr


def test_validate_debug_artifact_rejects_abstraction_up_diagnostic_only_without_reason(tmp_path: Path) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        (
            "- abstraction-up axis: broad closeout posture | "
            "decision: same class, diagnostic-only for this slice | "
            "proof: static scan only"
        ),
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "proof-backed no-action reason" in result.stderr


def test_validate_debug_artifact_accepts_abstraction_up_diagnostic_only_with_no_action_reason(tmp_path: Path) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        (
            "- abstraction up: broad closeout posture | "
            "decision: same class, diagnostic-only for this slice | "
            "proof: static scan only | no action needed because the existing "
            "final closeout gate already owns this boundary"
        ),
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_debug_artifact_accepts_abstraction_up_diagnostic_only_with_followup(tmp_path: Path) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        (
            "- abstraction up: messenger side-effect durability | "
            "decision: same class, diagnostic-only for this slice | "
            "proof: static scan only | deferred repo-level structural work | "
            "follow-up: https://github.com/corca-ai/charness/issues/294"
        ),
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_debug_artifact_preserves_same_layer_diagnostic_only_without_reason(tmp_path: Path) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        (
            "- same layer: local helper naming | "
            "decision: same class, diagnostic-only for this slice | "
            "proof: static scan only"
        ),
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_debug_artifact_does_not_read_next_star_bullet_as_abstraction_up_reason(
    tmp_path: Path,
) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        (
            "- abstraction up: broad closeout posture | "
            "decision: same class, diagnostic-only for this slice | "
            "proof: static scan only\n"
            "* same layer: other checked surface | "
            "decision: same class, diagnostic-only for this slice | "
            "proof: no action needed because coverage is distinct"
        ),
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "proof-backed no-action reason" in result.stderr


def test_validate_debug_artifact_rejects_star_abstraction_up_diagnostic_only_without_reason(
    tmp_path: Path,
) -> None:
    artifact = valid_current_artifact().replace(
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py",
        (
            "* abstraction up: broad closeout posture | "
            "decision: same class, diagnostic-only for this slice | "
            "proof: static scan only"
        ),
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "proof-backed no-action reason" in result.stderr


# --- #2b: cross-file sibling-scan marker (latest.md / forward-only) -----------

CROSS_FILE_LINE = "- cross-file: scripts/check_coverage.py is outside the subject tests/repo_copy.py"


def test_validate_debug_artifact_rejects_latest_sibling_search_without_cross_file_marker(
    tmp_path: Path,
) -> None:
    # A within-file-only `## Sibling Search` (no cross-file declaration) must FAIL
    # on the current `latest.md` form — the gap #2b closes.
    artifact = valid_current_artifact().replace(CROSS_FILE_LINE + "\n", "")
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "cross-file" in result.stderr
    assert "Invalid debug artifact charness-artifacts/debug/latest.md" in result.stderr


def test_validate_debug_artifact_accepts_no_cross_file_sibling_escape(tmp_path: Path) -> None:
    # The justified escape `no cross-file sibling: <reason>` PASSES.
    artifact = valid_current_artifact().replace(
        CROSS_FILE_LINE,
        "- no cross-file sibling: the fixture-root logic lives only in this test module",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_debug_artifact_rejects_empty_cross_file_marker(tmp_path: Path) -> None:
    # `cross-file:` with no value is not a declaration.
    artifact = valid_current_artifact().replace(CROSS_FILE_LINE, "- cross-file:")
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "cross-file" in result.stderr


def test_validate_debug_artifact_cross_file_marker_not_required_for_dated_records(
    tmp_path: Path,
) -> None:
    # The marker check is latest.md/forward-only: a dated artifact missing the
    # marker still passes, so the historical corpus is never retro-regressed.
    repo = seed_repo(tmp_path, valid_current_artifact())
    dated = valid_current_artifact().replace(CROSS_FILE_LINE + "\n", "")
    (repo / "charness-artifacts" / "debug" / "2026-04-01-dated.md").write_text(dated, encoding="utf-8")
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "Validated debug artifact charness-artifacts/debug/2026-04-01-dated.md" in result.stdout


def test_validate_debug_artifact_trivial_short_circuit_satisfies_cross_file(tmp_path: Path) -> None:
    # A trivial-fix `## Sibling Search` (no axes, no cross-file line) is satisfied
    # by the short-circuit alone, matching `validate_sibling_followups`.
    artifact = valid_current_artifact().replace(
        "- Mental model: synthetic copy fixtures treat runtime roots as input\n"
        "- same layer: tests/repo_copy.py and scripts/check_coverage.py\n"
        + CROSS_FILE_LINE
        + "\n",
        "- n/a — trivial fix; no plausible siblings\n",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def _multi_violation_current_artifact() -> str:
    # Breaks two independent checks at once: only two candidate causes and an
    # unknown `Risk Class` value. Used to exercise --report-all vs fail-fast.
    return valid_current_artifact(risk_class="bogus-class").replace("- three\n", "")


def test_validate_debug_artifact_default_mode_fails_fast(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_current_artifact())
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "at least three plausible causes" in result.stderr
    assert "rule violation(s)" not in result.stderr
    assert "Risk Class" not in result.stderr


def test_validate_debug_artifact_report_all_lists_every_violation(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_current_artifact())
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo), "--report-all")
    assert result.returncode == 1
    assert "rule violation(s)" in result.stderr
    assert "at least three plausible causes" in result.stderr
    assert "`Risk Class` contains unknown values" in result.stderr


# --- #366: dated Seam Risk enum parity with the closeout consumer -------------


def test_validate_debug_artifact_rejects_dated_off_taxonomy_risk_class(tmp_path: Path) -> None:
    # #366: a DATED record with an off-taxonomy `Risk Class` (valid heading shape,
    # value the `risk_interrupt_lib` consumer rejects) used to PASS the author-time
    # validator, then block `run_slice_closeout.py` repo-wide via the current-pointer
    # `latest.md`. It must now fail at write time, at the offending artifact.
    repo = seed_repo(tmp_path, valid_current_artifact())
    dated = valid_current_artifact(risk_class="host-state")
    (repo / "charness-artifacts" / "debug" / "2026-06-14-dated.md").write_text(dated, encoding="utf-8")
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Invalid debug artifact charness-artifacts/debug/2026-06-14-dated.md" in result.stderr
    assert "host-state" in result.stderr


def test_validate_debug_artifact_rejects_dated_off_taxonomy_generalization_pressure(tmp_path: Path) -> None:
    # #366: same gap for an off-taxonomy `Generalization Pressure` prose value.
    repo = seed_repo(tmp_path, valid_current_artifact())
    dated = valid_current_artifact().replace("- Generalization Pressure: none", "- Generalization Pressure: vibes")
    (repo / "charness-artifacts" / "debug" / "2026-06-14-dated.md").write_text(dated, encoding="utf-8")
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Invalid debug artifact charness-artifacts/debug/2026-06-14-dated.md" in result.stderr
    assert "Generalization Pressure" in result.stderr


def test_validate_debug_artifact_accepts_dated_in_taxonomy_seam_risk(tmp_path: Path) -> None:
    # In-taxonomy Seam Risk values on a dated record still pass; the historical
    # corpus (all in-taxonomy) is not retro-regressed.
    repo = seed_repo(tmp_path, valid_current_artifact())
    dated = valid_current_artifact(risk_class="operator-visible-recovery")
    (repo / "charness-artifacts" / "debug" / "2026-06-14-dated.md").write_text(dated, encoding="utf-8")
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "Validated debug artifact charness-artifacts/debug/2026-06-14-dated.md" in result.stdout


def test_validate_debug_artifact_seam_risk_enums_are_single_source_of_truth() -> None:
    # #366: the Seam Risk enums must be imported from risk_interrupt_lib (the
    # closeout consumer), never a hand copy that can silently drift below it.
    import importlib.util
    import sys

    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(
        "validate_debug_artifact_sst", ROOT / "scripts" / "validate_debug_artifact.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    consumer = module._scripts_risk_interrupt_lib_module
    assert module.ALLOWED_RISK_CLASSES is consumer.ALLOWED_RISK_CLASSES
    assert module.ALLOWED_GENERALIZATION_PRESSURE is consumer.ALLOWED_GENERALIZATION_PRESSURE
    assert module.FORCED_RISK_CLASSES is consumer.FORCED_RISK_CLASSES
