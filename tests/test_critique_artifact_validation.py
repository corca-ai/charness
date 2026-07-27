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


def test_validate_critique_artifact_fail_fast_stops_at_first_violation(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script(
        str(ROOT / "scripts" / "validate_critique_artifacts.py"),
        "--repo-root",
        str(repo),
        "--paths",
        ARTIFACT_RELPATH,
        "--fail-fast",
    )
    assert result.returncode == 1
    assert "unknown bin `bogus-bin`" in result.stderr
    assert "rule violation(s)" not in result.stderr
    assert "host exposure state" not in result.stderr


def test_validate_critique_artifact_default_mode_lists_every_violation(tmp_path: Path) -> None:
    # D28 polarity unification: one-pass is now the DEFAULT here too.
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    result = run_script(
        str(ROOT / "scripts" / "validate_critique_artifacts.py"),
        "--repo-root",
        str(repo),
        "--paths",
        ARTIFACT_RELPATH,
    )
    assert result.returncode == 1
    assert "rule violation(s)" in result.stderr
    assert "unknown bin `bogus-bin`" in result.stderr
    assert "host exposure state `bogus-state`" in result.stderr


def test_validate_critique_artifact_report_all_is_accepted_no_op(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, _multi_violation_artifact())
    args = ("--repo-root", str(repo), "--paths", ARTIFACT_RELPATH)
    script = str(ROOT / "scripts" / "validate_critique_artifacts.py")
    default = run_script(script, *args)
    deprecated = run_script(script, *args, "--report-all")
    assert deprecated.returncode == default.returncode == 1
    assert deprecated.stderr == default.stderr


def test_empty_artifact_set_does_not_run_the_cross_surface_probe(tmp_path: Path) -> None:
    """A commit touching no critique artifact stays a cheap silent pass.

    The shared runner builds the per-run validate factory, and critique's factory
    resolves the cross-surface probe by shelling out to git. With zero artifacts
    that work is pure cost -- and an unresolvable base sha (shallow clone,
    grafted history) raises SurfaceError, which is not a ValidationError, so it
    would turn a silent pass into an uncaught traceback.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "."], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init"],
        cwd=repo,
        check=True,
    )
    result = run_script(
        str(ROOT / "scripts" / "validate_critique_artifacts.py"),
        "--repo-root",
        str(repo),
        "--changed-ref",
        "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef..HEAD",
    )
    assert result.returncode == 0, result.stderr
    assert "Validated 0 critique artifact(s)." in result.stdout
