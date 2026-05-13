"""Regression tests for scripts/validate_cautilus_call_provenance.py.

Post-hoc layer-3 guard: every cautilus run on or after the enforcement date
must leave a provenance trail in the proof artifact or in commit messages.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_cautilus_call_provenance.py"


def _init_git(repo: Path, *, commit_subject: str | None = None) -> None:
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", commit_subject or "seed"],
        check=True,
    )


def _run(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_passes_when_no_runs_directory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git(repo)
    result = _run(repo)
    assert result.returncode == 0, result.stderr
    assert "No .cautilus/runs/" in result.stdout


def test_passes_when_runs_directory_is_empty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".cautilus" / "runs").mkdir(parents=True)
    _init_git(repo)
    result = _run(repo)
    assert result.returncode == 0, result.stderr
    assert "no run directories" in result.stdout


def test_grandfathers_pre_enforcement_runs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".cautilus" / "runs" / "20260418T185808069Z-run").mkdir(parents=True)
    _init_git(repo)
    result = _run(repo)
    assert result.returncode == 0, result.stderr
    assert "grandfathered" in result.stdout


def test_fails_when_post_enforcement_run_is_uncited(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".cautilus" / "runs" / "20260601T120000000Z-run").mkdir(parents=True)
    _init_git(repo)
    result = _run(repo)
    assert result.returncode == 1, result.stdout
    assert "20260601T120000000Z-run" in result.stderr
    assert "structured provenance citation" in result.stderr


def test_passes_when_run_is_cited_in_artifact_source_ref(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    runs_dir = repo / ".cautilus" / "runs" / "20260601T120000000Z-run"
    runs_dir.mkdir(parents=True)
    artifact = repo / "charness-artifacts" / "cautilus" / "latest.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "# Cautilus Dogfood\n## Behavior Source\n- source-ref: .cautilus/runs/20260601T120000000Z-run/log\n",
        encoding="utf-8",
    )
    _init_git(repo)
    result = _run(repo)
    assert result.returncode == 0, result.stderr
    assert "1 cited" in result.stdout


def test_fails_when_artifact_mentions_run_only_in_prose(tmp_path: Path) -> None:
    # The pre-tighten validator passed this; the structured-citation rule rejects it.
    repo = tmp_path / "repo"
    (repo / ".cautilus" / "runs" / "20260601T120000000Z-run").mkdir(parents=True)
    artifact = repo / "charness-artifacts" / "cautilus" / "latest.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "# Cautilus Dogfood\n## Notes\nRan 20260601T120000000Z-run as a sanity probe.\n",
        encoding="utf-8",
    )
    _init_git(repo)
    result = _run(repo)
    assert result.returncode == 1, result.stdout
    assert "structured provenance citation" in result.stderr


def test_passes_when_commit_pairs_run_id_with_source_kind(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".cautilus" / "runs" / "20260601T120000000Z-run").mkdir(parents=True)
    _init_git(
        repo,
        commit_subject=(
            "Document cautilus dogfood\n\n"
            "Cited 20260601T120000000Z-run with source-kind: failing-prompt"
        ),
    )
    result = _run(repo)
    assert result.returncode == 0, result.stderr
    assert "1 cited" in result.stdout


def test_fails_when_commit_mentions_run_id_without_source_kind(tmp_path: Path) -> None:
    # The pre-tighten validator passed this; the source-kind pairing rule rejects it.
    repo = tmp_path / "repo"
    (repo / ".cautilus" / "runs" / "20260601T120000000Z-run").mkdir(parents=True)
    _init_git(
        repo,
        commit_subject="Land thing referencing 20260601T120000000Z-run for provenance",
    )
    result = _run(repo)
    assert result.returncode == 1, result.stdout
    assert "structured provenance citation" in result.stderr
