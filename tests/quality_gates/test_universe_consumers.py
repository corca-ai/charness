from __future__ import annotations

import sys
from pathlib import Path

import pytest

from .seeding_support import write_quality_adapter


def test_standing_pytest_uses_adapter_pytest_targets(tmp_path: Path, monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "consumer"
    selected = repo / "tests" / "test_selected.py"
    selected.parent.mkdir(parents=True)
    selected.write_text("def test_selected(): pass\n", encoding="utf-8")
    write_quality_adapter(repo, ["universes:", "  pytest_targets:", "    - tests/test_*.py"])
    monkeypatch.setattr(
        runner, "choose_pytest_command", lambda env=None: [sys.executable, "-m", "pytest"]
    )
    monkeypatch.setattr(runner, "has_xdist", lambda command, env=None: False)

    command = runner.build_pytest_command(
        repo,
        basetemp=tmp_path / "pytest-tmp",
        include_release_only=True,
        env={},
    )

    assert "tests/test_selected.py" in command
    assert "tests/quality_gates" not in command


def test_standing_pytest_refuses_declared_empty_pytest_targets(tmp_path: Path) -> None:
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "consumer"
    repo.mkdir()
    write_quality_adapter(repo, ["universes:", "  pytest_targets: []"])

    with pytest.raises(SystemExit, match="pytest: refusing empty declared universe"):
        runner.expand_targets(repo)
