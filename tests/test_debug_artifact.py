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
                f"- Premortem Required: {'yes' if next_step == 'spec' else 'no'}",
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
            "## Seam Risk\n\n- Interrupt ID: demo-interrupt\n- Risk Class: none\n- Seam: none\n- Disproving Observation: none\n- What Local Reasoning Cannot Prove: none\n- Generalization Pressure: none\n\n## Interrupt Decision\n\n- Premortem Required: no\n- Next Step: impl\n- Handoff Artifact: none\n\n",
            "",
        ),
    )
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required section `## Seam Risk`" in result.stderr


def test_validate_debug_artifact_forced_interrupt_requires_spec_handoff(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        valid_current_artifact(next_step="impl", handoff_artifact="none", risk_class="external-seam"),
    )
    result = run_script("scripts/validate_debug_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "forced risk interrupt" in result.stderr
