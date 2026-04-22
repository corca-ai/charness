from __future__ import annotations

import json
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


def seed_repo(tmp_path: Path, *, debug_body: str, spec_body: str | None = None) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "spec").mkdir(parents=True)
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
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(debug_body, encoding="utf-8")
    if spec_body is not None:
        (repo / "charness-artifacts" / "spec" / "interrupt-demo.md").write_text(spec_body, encoding="utf-8")
    return repo


def debug_artifact(*, risk_class: str = "external-seam") -> str:
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
                "- Interrupt ID: seam-demo",
                f"- Risk Class: {risk_class}",
                "- Seam: slack-thread-activation",
                "- Disproving Observation: live host disproved local reasoning",
                "- What Local Reasoning Cannot Prove: thread visibility semantics",
                "- Generalization Pressure: factor-now",
                "",
                "## Interrupt Decision",
                "",
                "- Premortem Required: yes",
                "- Next Step: spec",
                "- Handoff Artifact: charness-artifacts/spec/interrupt-demo.md",
                "",
                "## Prevention",
                "",
                "prevention",
                "",
            ]
        )
        + "\n"
    )


def resolved_spec(*, chosen_next_step: str = "factor-first", impl_status: str = "blocked") -> str:
    return (
        "\n".join(
            [
                "# Problem",
                "",
                "problem",
                "",
                "# Premortem",
                "",
                "- Interrupt Source: seam-demo",
                "- Seam Summary: slack-thread-activation",
                f"- Chosen Next Step: {chosen_next_step}",
                f"- Impl Status: {impl_status}",
                "- Impl Status Reason: live seam still needs factor-first work",
                "- What Disproving Observation Is Resolved: spec now carries the host-visible risk forward",
                "",
            ]
        )
        + "\n"
    )


def test_plan_risk_interrupt_blocks_without_current_slice_spec_refresh(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, debug_body=debug_artifact(), spec_body=resolved_spec())
    result = run_script("scripts/plan_risk_interrupt.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "refresh `charness-artifacts/spec/interrupt-demo.md`" in payload["next_action"]


def test_plan_risk_interrupt_records_handoff_when_matching_spec_is_refreshed(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, debug_body=debug_artifact(), spec_body=resolved_spec())
    result = run_script(
        "scripts/plan_risk_interrupt.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/debug/latest.md",
        "charness-artifacts/spec/interrupt-demo.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "handoff-recorded"
    assert payload["chosen_next_step"] == "factor-first"
    assert payload["impl_status"] == "blocked"


def test_plan_risk_interrupt_ignores_stale_current_debug_for_unrelated_slice(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, debug_body=debug_artifact(), spec_body=resolved_spec())
    result = run_script(
        "scripts/plan_risk_interrupt.py",
        "--repo-root",
        str(repo),
        "--paths",
        "README.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "not-applicable"
    assert payload["reason"] == "current debug interrupt was not refreshed in this slice"
