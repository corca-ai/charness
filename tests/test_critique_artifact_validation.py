from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARTIFACT_RELPATH = "charness-artifacts/critique/2026-06-12-demo-critique.md"


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
    (repo / "charness-artifacts" / "critique").mkdir(parents=True)
    (repo / ARTIFACT_RELPATH).write_text(artifact_body, encoding="utf-8")
    return repo


def _multi_violation_artifact() -> str:
    # Breaks two independent checks at once: an unknown structured-finding bin
    # and an unknown reviewer-tier host exposure state. Used to exercise
    # --report-all vs the fail-fast default.
    return (
        "\n".join(
            [
                "# Critique Review",
                "Date: 2026-06-12",
                "",
                "## Decision Under Review",
                "",
                "demo decision",
                "",
                "## Structured Findings",
                "",
                "- F1 | bin: bogus-bin | evidence: strong | ref: scripts/demo.py | action: fix | note: demo",
                "",
                "## Reviewer Tier Evidence",
                "",
                "- Requested tier: high-leverage",
                "- Requested spawn fields: none sent",
                "- Host exposure state: bogus-state",
                "- Application state: pending",
                "",
                "## Fresh-Eye Satisfaction",
                "",
                "parent-delegated; reviewer completed the assigned lens.",
                "",
            ]
        )
        + "\n"
    )


def test_validate_critique_artifact_default_mode_fails_fast(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script(
        str(ROOT / "scripts" / "validate_critique_artifacts.py"),
        "--repo-root",
        str(repo),
        "--paths",
        ARTIFACT_RELPATH,
    )
    assert result.returncode == 1
    assert "unknown bin `bogus-bin`" in result.stderr
    assert "rule violation(s)" not in result.stderr
    assert "host exposure state" not in result.stderr


def test_validate_critique_artifact_report_all_lists_every_violation(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script(
        str(ROOT / "scripts" / "validate_critique_artifacts.py"),
        "--repo-root",
        str(repo),
        "--paths",
        ARTIFACT_RELPATH,
        "--report-all",
    )
    assert result.returncode == 1
    assert "rule violation(s)" in result.stderr
    assert "unknown bin `bogus-bin`" in result.stderr
    assert "host exposure state `bogus-state`" in result.stderr
