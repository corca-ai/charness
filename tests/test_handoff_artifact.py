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
    (repo / "docs").mkdir(parents=True)
    (repo / ".agents" / "handoff-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: docs",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "docs" / "handoff.md").write_text(artifact_body, encoding="utf-8")
    return repo
def test_validate_handoff_artifact_rejects_extra_top_level_section(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                "- state",
                "",
                "## Next Session",
                "",
                "- next",
                "",
                "## History",
                "",
                "- stale",
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate-handoff-artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "canonical sections" in result.stderr


def test_validate_handoff_artifact_rejects_missing_reference_link(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                "- state",
                "",
                "## Next Session",
                "",
                "- next",
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- docs/guide.md",
                "",
            ]
        )
        + "\n",
    )
    result = run_script("scripts/validate-handoff-artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "at least one markdown link" in result.stderr


def test_validate_handoff_artifact_rejects_overlong_handoff(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                *[f"- stale detail {index}" for index in range(65)],
                "",
                "## Next Session",
                "",
                "- next",
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate-handoff-artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "80 lines" in result.stderr


def test_validate_handoff_artifact_rejects_explicit_allowance_as_subagent_blocker(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Workflow Trigger",
                "",
                "- do the thing",
                "",
                "## Current State",
                "",
                "- The canonical subagent path was blocked because this session did not explicitly allow subagents.",
                "",
                "## Next Session",
                "",
                "- next",
                "",
                "## Discuss",
                "",
                "- discuss",
                "",
                "## References",
                "",
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate-handoff-artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must not treat missing explicit subagent allowance" in result.stderr
