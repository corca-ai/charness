from __future__ import annotations

from pathlib import Path


def test_standing_pytest_command_uses_xdist_and_expands_globs(tmp_path: Path, monkeypatch) -> None:
    from scripts import run_standing_pytest as runner

    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_alpha.py").write_text("def test_alpha(): pass\n", encoding="utf-8")
    (tmp_path / "tests" / "quality_gates").mkdir()
    (tmp_path / "tests" / "control_plane").mkdir()
    (tmp_path / "tests" / "charness_cli").mkdir()
    monkeypatch.setattr(runner, "choose_pytest_command", lambda: ["python3", "-m", "pytest"])
    monkeypatch.setattr(runner, "has_xdist", lambda command: True)

    command = runner.build_pytest_command(
        tmp_path,
        basetemp=tmp_path.parent / "pytest-tmp",
        include_release_only=False,
    )

    assert command[:6] == ["python3", "-m", "pytest", "-q", "-m", "not release_only"]
    assert "-n" in command
    assert "auto" in command
    assert "tests/test_alpha.py" in command
    assert "tests/test_*.py" not in command
    assert "tests/charness_cli" in command


def test_standing_pytest_temp_root_stays_outside_repo(tmp_path: Path) -> None:
    from scripts import run_standing_pytest as runner

    repo = tmp_path / "repo"
    repo.mkdir()
    temp_root = runner.default_temp_root(repo, {"HOME": str(tmp_path / "home")})

    assert "/charness/pytest-tmp/" in str(temp_root)
    runner.ensure_external_temp_root(repo, temp_root)
