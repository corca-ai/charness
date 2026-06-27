"""Regression test for the `seed_t_events_adapter.py` sibling of #181.

The same `relative_to` ValueError pattern existed in this seed script; this
file pins the documented `--repo-root .` invocation to exit 0.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "public" / "setup" / "scripts" / "seed_t_events_adapter.py"
TEMPLATE = (
    ROOT
    / "skills"
    / "public"
    / "setup"
    / "scripts"
    / "templates"
    / "t_events_adapter.yaml"
)


def _run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def test_repo_root_dot_invocation_exits_zero(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = _run(repo, "--repo-root", ".")

    assert result.returncode == 0, result.stderr
    assert "wrote .agents/t-events-adapter.yaml" in result.stdout
    target = repo / ".agents" / "t-events-adapter.yaml"
    assert target.is_file()
    assert target.read_text(encoding="utf-8") == TEMPLATE.read_text(encoding="utf-8")


def test_dry_run_emits_source_template() -> None:
    result = _run(ROOT, "--dry-run")

    assert result.returncode == 0, result.stderr
    assert result.stdout == TEMPLATE.read_text(encoding="utf-8")


def test_existing_file_refuses_without_force(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    target = repo / ".agents" / "t-events-adapter.yaml"
    target.write_text("preserved\n", encoding="utf-8")

    result = _run(repo, "--repo-root", ".")

    assert result.returncode == 1
    assert "already exists" in result.stderr
    assert target.read_text(encoding="utf-8") == "preserved\n"
