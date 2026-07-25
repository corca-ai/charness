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
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
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
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
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
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "under 70" in result.stderr


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


def run_on_state(tmp_path: Path, *state_lines: str) -> subprocess.CompletedProcess[str]:
    repo = seed_with_current_state(tmp_path, *state_lines)
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    return run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))


def test_validate_handoff_artifact_rejects_a_transcribed_release_version(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- Released through v2.7.0; the backlog is clear.")
    assert result.returncode == 1
    assert "v2.7.0" in result.stderr
    assert "regenerate" in result.stderr


def test_validate_handoff_artifact_rejects_a_transcribed_tool_version(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- The baseline was rewritten under nose 0.19.0.")
    assert result.returncode == 1
    assert "0.19.0" in result.stderr


def test_validate_handoff_artifact_rejects_a_transcribed_commit_sha(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- The rule landed in 1f7dece6 and has not moved.")
    assert result.returncode == 1
    assert "1f7dece6" in result.stderr


def test_validate_handoff_artifact_rejects_an_as_of_count(tmp_path: Path) -> None:
    result = run_on_state(tmp_path, "- The blocker is cleared: 66 tests across five files.")
    assert result.returncode == 1
    assert "66 tests" in result.stderr


def test_validate_handoff_artifact_allows_a_version_inside_a_link_target(tmp_path: Path) -> None:
    # A path that happens to contain a version is an address, not a claim about
    # current state, and the doc-link gate already keeps it honest.
    repo = seed_with_current_state(tmp_path, "- See the [release notes](docs/v2.5.0-notes.md).")
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (repo / "docs" / "v2.5.0-notes.md").write_text("# Notes\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_does_not_read_an_issue_id_as_a_count(tmp_path: Path) -> None:
    # Found by running the count rule across the other current-pointer artifacts:
    # `#371 issue disposition` is an identifier followed by a noun, not "371 issues".
    result = run_on_state(tmp_path, "- Closed with #371 issue disposition; nothing pending.")
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_allows_issue_ids_and_commands(tmp_path: Path) -> None:
    # An issue id is a stable identifier, not a snapshot; the command is the
    # replacement the rule asks for.
    result = run_on_state(
        tmp_path,
        "- #453 stays open; re-check with `gh issue list --state open`.",
        "- Released state: `git describe --tags --abbrev=0`.",
    )
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_accepts_the_optional_continuation_capability(tmp_path: Path) -> None:
    # The handoff skill's Output Shape lists this section; a repo validator that
    # rejects it makes following the skill a gate failure.
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
                "## Continuation Capability",
                "",
                "- the reader can pick a slice without re-deriving state",
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
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_handoff_artifact_rejects_an_empty_continuation_capability(tmp_path: Path) -> None:
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
                "## Continuation Capability",
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
                "- [guide](docs/guide.md)",
                "",
            ]
        )
        + "\n",
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Continuation Capability" in result.stderr


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
    result = run_script("scripts/validate_handoff_artifact.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "must not treat missing explicit subagent allowance" in result.stderr
