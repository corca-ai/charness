"""Shared handoff-artifact test fixtures.

One home for the seeding helpers so the ownership tests and the shape/budget
tests cannot drift into two different notions of a valid demo handoff.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Scaffolding bullets for `## Current State` / `## Next Session`. They exist to
# make the section non-empty for a test about some OTHER rule, so they carry a
# cheap owner: the ownership rule reads those two sections, and a bare `- state`
# would make every one of these fixtures fail for a reason it is not testing.
OWNED_STATE = "- state; recheck with `git status --short`"
OWNED_NEXT = "- next: [guide](docs/guide.md)"


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
        "\n".join(["version: 1", "repo: demo", "language: en", "output_dir: docs", ""]),
        encoding="utf-8",
    )
    (repo / "docs" / "handoff.md").write_text(artifact_body, encoding="utf-8")
    return repo


def seed_with_current_state(tmp_path: Path, *state_lines: str) -> Path:
    return seed_repo(
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
                *state_lines,
                "",
                "## Next Session",
                "",
                OWNED_NEXT,
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


def run_on_state(tmp_path: Path, *state_lines: str) -> subprocess.CompletedProcess[str]:
    repo = seed_with_current_state(tmp_path, *state_lines)
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    return run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
