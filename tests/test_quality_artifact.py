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
    (repo / "skill-outputs" / "quality" / "history").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: skill-outputs/quality",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "skill-outputs" / "quality" / "quality.md").write_text(artifact_body, encoding="utf-8")
    (repo / "skill-outputs" / "quality" / "history" / "one.md").write_text("# One\n", encoding="utf-8")
    return repo


def test_validate_quality_artifact_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-quality-artifact.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_quality_artifact_rejects_missing_history_section(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-10",
                "",
                "## Scope",
                "",
                "- demo",
                "",
                "## Current Gates",
                "",
                "- gate",
                "",
                "## Healthy",
                "",
                "- healthy",
                "",
                "## Weak",
                "",
                "- weak",
                "",
                "## Missing",
                "",
                "- missing",
                "",
                "## Deferred",
                "",
                "- deferred",
                "",
                "## Commands Run",
                "",
                "- cmd",
                "",
                "## Recommended Next Gates",
                "",
                "- next",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate-quality-artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required section `## History`" in result.stderr


def test_validate_quality_artifact_rejects_missing_history_link(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Quality Review",
                "Date: 2026-04-10",
                "",
                "## Scope",
                "",
                "- demo",
                "",
                "## Current Gates",
                "",
                "- gate",
                "",
                "## Healthy",
                "",
                "- healthy",
                "",
                "## Weak",
                "",
                "- weak",
                "",
                "## Missing",
                "",
                "- missing",
                "",
                "## Deferred",
                "",
                "- deferred",
                "",
                "## Commands Run",
                "",
                "- cmd",
                "",
                "## Recommended Next Gates",
                "",
                "- next",
                "",
                "## History",
                "",
                "- archive pending",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate-quality-artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "history/*.md" in result.stderr
