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
                "- falsifiable claim: the gate skips volatile roots | disconfirmer: add `.cautilus` to a fixture and assert it is excluded",
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
            "## Verification\n\nverification\n\n",
            "## Verification\n\nverification\n\n## Session Log\n\n- log\n\n",
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


# --- Plan A: falsifiable-hypothesis disconfirmer marker (latest.md / forward-only) -

HYPOTHESIS_LINE = (
    "- falsifiable claim: the gate skips volatile roots | "
    "disconfirmer: add `.cautilus` to a fixture and assert it is excluded"
)


def test_validate_debug_artifact_rejects_latest_hypothesis_without_disconfirmer(
    tmp_path: Path,
) -> None:
    # A `## Hypothesis` with no `disconfirmer:` marker must FAIL on latest.md — the
    # static-only-RCA gap Plan A closes by internalizing the rule into structure.
    artifact = valid_current_artifact().replace(
        HYPOTHESIS_LINE, "- the gate skips volatile roots"
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "disconfirmer" in result.stderr
    assert "Invalid debug artifact charness-artifacts/debug/latest.md" in result.stderr


def test_validate_debug_artifact_accepts_disconfirmer_na_escape(tmp_path: Path) -> None:
    # The justified escape `disconfirmer: n/a — <why>` PASSES (some bug classes have
    # no cheap local repro); the OUTCOME assertion, not this marker, is the real bar.
    artifact = valid_current_artifact().replace(
        HYPOTHESIS_LINE,
        "- falsifiable claim: the gate skips volatile roots | "
        "disconfirmer: n/a — only reproduces in CI, no cheap local refutation",
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_debug_artifact_rejects_empty_disconfirmer_marker(tmp_path: Path) -> None:
    # `disconfirmer:` with no value is not a declaration.
    artifact = valid_current_artifact().replace(
        HYPOTHESIS_LINE, "- falsifiable claim: the gate skips volatile roots | disconfirmer:"
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "disconfirmer" in result.stderr


def test_validate_debug_artifact_disconfirmer_marker_not_required_for_dated_records(
    tmp_path: Path,
) -> None:
    # latest.md/forward-only: a dated artifact missing the disconfirmer marker still
    # passes, so the historical corpus is never retro-regressed.
    repo = seed_repo(tmp_path, valid_current_artifact())
    dated = valid_current_artifact().replace(HYPOTHESIS_LINE, "- the gate skips volatile roots")
    (repo / "charness-artifacts" / "debug" / "2026-04-01-dated.md").write_text(dated, encoding="utf-8")
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "Validated debug artifact charness-artifacts/debug/2026-04-01-dated.md" in result.stdout


def test_validate_debug_artifact_trivial_short_circuit_satisfies_disconfirmer(
    tmp_path: Path,
) -> None:
    # A trivial-fix `## Hypothesis` is satisfied by the short-circuit alone, matching
    # validate_cross_file_sibling_marker.
    artifact = valid_current_artifact().replace(
        HYPOTHESIS_LINE, "- n/a — trivial fix; no plausible siblings"
    )
    repo = seed_repo(tmp_path, artifact)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def _multi_violation_current_artifact() -> str:
    # Breaks two independent checks at once: only two candidate causes and an
    # unknown `Risk Class` value. Used to exercise the one-pass default vs
    # --fail-fast.
    return valid_current_artifact(risk_class="bogus-class").replace("- three\n", "")


def test_validate_debug_artifact_default_mode_lists_every_violation(tmp_path: Path) -> None:
    # D28 polarity unification: one-pass is now the DEFAULT here, matching the
    # handoff/retro/ideation/quality siblings.
    repo = seed_repo(tmp_path, _multi_violation_current_artifact())
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "rule violation(s)" in result.stderr
    assert "at least three plausible causes" in result.stderr
    assert "`Risk Class` contains unknown values" in result.stderr


def test_validate_debug_artifact_fail_fast_stops_at_first_violation(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_current_artifact())
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo), "--fail-fast")
    assert result.returncode == 1
    assert "at least three plausible causes" in result.stderr
    assert "rule violation(s)" not in result.stderr
    assert "Risk Class" not in result.stderr


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


def test_missing_output_directory_reports_no_misleading_scaffold_hint(tmp_path: Path) -> None:
    """A wrong --repo-root is not an artifact rule violation.

    Routing it through report_validation_failure would append "start from the
    owning scaffold" -- telling the operator to author a stub when the real fix
    is to point at the right root.
    """
    repo = tmp_path / "repo"
    (repo / "charness-artifacts").mkdir(parents=True)
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "No debug output directory" in result.stderr
    assert "scaffold" not in result.stderr


def test_a_scoped_run_isolates_a_fresh_artifact_from_legacy_corpus_debt(tmp_path: Path) -> None:
    """The reported defect, as the three-artifact case that distinguishes the two modes.

    A corpus validator run unscoped answers "is the whole history clean", and the debug
    planner emitted exactly that while calling it a current-artifact gate. A consumer
    wrote a VALID new record, saw it reported validated, and still got exit 1 -- because
    an unrelated older record carried legacy-schema debt. Nothing in the exit code said
    which artifact was at fault, and the repo's own changed-scope gate passed, so the two
    surfaces answered different questions with the same word.

    The fixture below is the minimum that can tell a real fix from a fake one: scoping to
    a clean corpus would pass for the wrong reason, so the corpus here is deliberately
    red.
    """
    repo = seed_repo(tmp_path, valid_current_artifact())
    debug_dir = repo / "charness-artifacts" / "debug"
    fresh = debug_dir / "2026-08-17-debug-review.md"
    fresh.write_text(valid_current_artifact(), encoding="utf-8")
    legacy = debug_dir / "2026-01-02-legacy-shape.md"
    legacy.write_text("# Legacy\nDate: 2026-01-02\n\n## Problem\n\nno other sections\n", encoding="utf-8")

    # Whole corpus: red, and correctly so -- the legacy record IS out of schema.
    corpus = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo), "--all")
    assert corpus.returncode == 1
    assert "2026-01-02-legacy-shape.md" in corpus.stdout + corpus.stderr

    # Scoped to the artifact just authored: green, and it does NOT reach the legacy record.
    scoped = run_script(
        "scripts/validate_debug_artifact.py",
        "--repo-root", str(repo),
        "--paths", "charness-artifacts/debug/2026-08-17-debug-review.md",
    )
    assert scoped.returncode == 0, scoped.stdout + scoped.stderr
    assert "2026-01-02-legacy-shape.md" not in scoped.stdout + scoped.stderr

    # And a scoped run still REFUSES a malformed artifact -- scoping narrows the
    # population, never the rules. Without this the fix could be "always pass".
    fresh.write_text("# Broken\nDate: 2026-08-17\n\n## Problem\n\nmissing the rest\n", encoding="utf-8")
    scoped_broken = run_script(
        "scripts/validate_debug_artifact.py",
        "--repo-root", str(repo),
        "--paths", "charness-artifacts/debug/2026-08-17-debug-review.md",
    )
    assert scoped_broken.returncode == 1
    assert "2026-08-17-debug-review.md" in scoped_broken.stdout + scoped_broken.stderr


def test_a_named_debug_path_that_resolves_to_nothing_refuses_instead_of_passing(tmp_path: Path) -> None:
    """Scoping without an owned prefix is a silent pass, which is worse than no scoping.

    `unresolvable_named_paths` owns nothing unless the validator declares a prefix, and
    debug declared none -- so `--paths <path that does not exist>` printed "No debug
    artifacts in scope." and exited 0 having validated nothing. Harmless while every
    emitted command was unscoped; a silent green the moment the planner and scaffold
    started NAMING the artifact being authored, because running the emitted gate before
    writing the file (or after writing it elsewhere) is the ordinary case, not an exotic
    one. `retro`, `ideation` and `critique` all declare theirs.
    """
    repo = seed_repo(tmp_path, valid_current_artifact())

    missing = run_script(
        "scripts/validate_debug_artifact.py",
        "--repo-root", str(repo),
        "--paths", "charness-artifacts/debug/2026-08-17-never-written.md",
    )
    assert missing.returncode == 1
    assert "resolve to nothing" in missing.stdout + missing.stderr

    # The two no-ops the refusal must NOT swallow, both load-bearing because `--paths` is
    # fed by tools passing a slice of the changed set.
    unowned = run_script(
        "scripts/validate_debug_artifact.py", "--repo-root", str(repo), "--paths", "docs/handoff.md"
    )
    assert unowned.returncode == 0, unowned.stdout + unowned.stderr

    real = run_script(
        "scripts/validate_debug_artifact.py",
        "--repo-root", str(repo),
        "--paths", "charness-artifacts/debug/latest.md",
    )
    assert real.returncode == 0, real.stdout + real.stderr


def test_the_owned_prefix_comes_from_the_adapter_not_a_literal(tmp_path: Path) -> None:
    # Debug is the one family whose output directory is adapter-declared, so a constant
    # prefix would refuse correct paths in any repo that declares a different directory.
    # This repo declares one, and the refusal must key on THAT.
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "artifacts" / "debugs").mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nlanguage: en\noutput_dir: artifacts/debugs\n", encoding="utf-8"
    )
    (repo / "artifacts" / "debugs" / "latest.md").write_text(valid_current_artifact(), encoding="utf-8")

    missing = run_script(
        "scripts/validate_debug_artifact.py",
        "--repo-root", str(repo),
        "--paths", "artifacts/debugs/2026-08-17-never-written.md",
    )
    assert missing.returncode == 1, missing.stdout + missing.stderr
    assert "resolve to nothing" in missing.stdout + missing.stderr


def _strict_only_violation(body: str) -> str:
    """Remove the falsifiable-hypothesis marker: a CURRENT-schema rule with no legacy analogue."""
    return body.replace(
        " | disconfirmer: add `.cautilus` to a fixture and assert it is excluded", ""
    )


def test_the_same_bytes_get_the_same_verdict_under_either_name(tmp_path: Path) -> None:
    """Ruleset keyed on ROLE, not filename -- the defect scoping the emitted command exposed.

    `latest.md` is a symlink in real repos, so the artifact being authored is reached by
    two names. Keyed on filename, `--paths <pointer>` ran the strict current-schema checks
    and `--paths <its target>` ran only the legacy dated ones -- two verdicts for one file.
    Invisible while every emitted command was unscoped, because the corpus glob yields
    `latest.md` too and the strict checks always ran under SOME name. Scoping removed the
    other name, so a current-shaped artifact was judged by legacy rules and a missing
    `disconfirmer:` passed.

    The fixture violates a rule the CURRENT schema has and the legacy one does not, which
    is what makes the two rulesets distinguishable at all.
    """
    repo = seed_repo(tmp_path, valid_current_artifact())
    debug_dir = repo / "charness-artifacts" / "debug"
    record = debug_dir / "2026-08-17-debug-review.md"
    record.write_text(_strict_only_violation(valid_current_artifact()), encoding="utf-8")
    # The real layout: the pointer is a symlink onto the record being authored.
    (debug_dir / "latest.md").unlink()
    (debug_dir / "latest.md").symlink_to(record.name)

    by_pointer = run_script(
        "scripts/validate_debug_artifact.py", "--repo-root", str(repo),
        "--paths", "charness-artifacts/debug/latest.md",
    )
    by_target = run_script(
        "scripts/validate_debug_artifact.py", "--repo-root", str(repo),
        "--paths", "charness-artifacts/debug/2026-08-17-debug-review.md",
    )
    assert by_pointer.returncode == 1, by_pointer.stdout + by_pointer.stderr
    assert by_target.returncode == by_pointer.returncode, (
        "the same bytes were judged differently depending on which name reached them:\n"
        f"pointer rc={by_pointer.returncode} target rc={by_target.returncode}\n"
        f"target output: {by_target.stdout + by_target.stderr}"
    )

    # And a record the pointer does NOT reference stays on the legacy ruleset -- the fix
    # widens strictness to the current artifact's other name, not to the whole corpus.
    unreferenced = debug_dir / "2026-01-02-old-record.md"
    unreferenced.write_text(_strict_only_violation(valid_current_artifact()), encoding="utf-8")
    legacy = run_script(
        "scripts/validate_debug_artifact.py", "--repo-root", str(repo),
        "--paths", "charness-artifacts/debug/2026-01-02-old-record.md",
    )
    assert legacy.returncode == 0, legacy.stdout + legacy.stderr


def test_an_adapter_that_cannot_vouch_for_itself_owns_nothing(tmp_path: Path) -> None:
    """Both adapter-derived resolvers degrade together, and only when the adapter says so.

    `load_adapter` does not raise on a malformed file, so a try/except would never fire:
    an invalid `version` still returns a payload. Keying on `valid` is what stops a
    garbage prefix from silently disabling the named-path refusal -- which would
    reintroduce the silent pass through the back door. A MISSING adapter is not a
    failure; it resolves to the documented default, a real directory this validator owns.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "validate_debug_artifact_degraded", ROOT / "scripts" / "validate_debug_artifact.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def seed(name: str, body: str) -> Path:
        repo = tmp_path / name
        (repo / ".agents").mkdir(parents=True)
        (repo / ".agents" / "debug-adapter.yaml").write_text(body, encoding="utf-8")
        return repo

    invalid = seed("invalid", "version: 9\nrepo: demo\nlanguage: en\n")
    assert module._owned_prefix(invalid) is None
    assert module._current_pointer(invalid) is None

    # A missing adapter is the documented default, NOT a degradation.
    absent = tmp_path / "absent"
    absent.mkdir()
    assert module._owned_prefix(absent) == "charness-artifacts/debug/"
    assert module._current_pointer(absent) is not None

    # A valid adapter is honoured as declared -- the property a constant prefix breaks.
    declared = seed("declared", "version: 1\nrepo: demo\nlanguage: en\noutput_dir: artifacts/debugs\n")
    assert module._owned_prefix(declared) == "artifacts/debugs/"
    assert module._current_pointer(declared) == declared / "artifacts/debugs" / "latest.md"
