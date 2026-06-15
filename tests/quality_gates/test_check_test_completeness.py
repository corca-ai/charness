from __future__ import annotations

from pathlib import Path

from scripts import check_test_completeness as checker


def _write(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("def test_demo():\n    assert True\n", encoding="utf-8")


def _run_checker(repo: Path, targets: list[str], monkeypatch) -> int:
    monkeypatch.setattr(
        "sys.argv",
        ["check_test_completeness.py", "--repo-root", str(repo), "--", *targets],
    )
    return checker.main()


def test_check_test_completeness_accepts_directory_and_glob_targets(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    _write(repo / "tests" / "quality_gates" / "test_gate.py")
    _write(repo / "tests" / "test_top.py")
    _write(repo / "tests" / "charness_cli" / "test_cli.py")

    result = _run_checker(repo, ["tests/quality_gates", "tests/test_*.py", "tests/charness_cli"], monkeypatch)

    assert result == 0


def test_check_test_completeness_reports_missing_test_files(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    _write(repo / "tests" / "quality_gates" / "test_gate.py")
    _write(repo / "tests" / "integration" / "test_missing.py")

    result = _run_checker(repo, ["tests/quality_gates"], monkeypatch)

    stderr = capsys.readouterr().err
    assert result == 1
    assert "1 test file(s) not covered" in stderr
    assert "tests/integration/test_missing.py" in stderr


def test_relative_test_files_ignores_missing_targets(tmp_path: Path) -> None:
    repo = tmp_path / "repo"

    assert checker.relative_test_files(repo, repo / "tests" / "missing") == set()
