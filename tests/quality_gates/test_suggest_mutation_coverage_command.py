from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from .support import run_script

SCRIPT = "scripts/suggest_mutation_coverage_command.py"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _seed_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests" / "quality_gates").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / "scripts" / "foo.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (repo / "tests" / "quality_gates" / "test_foo.py").write_text(
        "from scripts import foo\n\n\ndef test_value():\n    assert foo.value() == 1\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_top.py").write_text(
        "import scripts.foo\n\n\ndef test_top_value():\n    assert scripts.foo.value() == 1\n",
        encoding="utf-8",
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "scripts" / "foo.py").write_text("def value():\n    return 2\n", encoding="utf-8")
    return repo, base


def test_recommends_focused_command_for_changed_pool_file(tmp_path: Path) -> None:
    from scripts.suggest_mutation_coverage_command import build_recommendation

    repo, base = _seed_repo(tmp_path)

    payload = build_recommendation(repo, base_sha=base)

    assert payload["status"] == "recommended"
    assert payload["changed_pool_files"] == ["scripts/foo.py"]
    assert payload["mapped_tests_by_file"] == {
        "scripts/foo.py": ["tests/quality_gates/test_foo.py", "tests/test_top.py"]
    }
    assert payload["command"] == (
        "python3 -m pytest -q -m 'not release_only' tests/quality_gates/test_foo.py tests/test_top.py"
    )


def test_reports_missing_when_changed_pool_file_has_no_test_reference(tmp_path: Path) -> None:
    from scripts.suggest_mutation_coverage_command import build_recommendation

    repo, base = _seed_repo(tmp_path)
    (repo / "tests" / "quality_gates" / "test_foo.py").write_text(
        "def test_other():\n    assert True\n", encoding="utf-8"
    )
    (repo / "tests" / "test_top.py").write_text(
        "def test_top_other():\n    assert True\n", encoding="utf-8"
    )

    payload = build_recommendation(repo, base_sha=base)

    assert payload["status"] == "missing"
    assert payload["unmapped_changed_pool_files"] == ["scripts/foo.py"]
    assert "command" not in payload


def test_reports_noop_when_no_pool_file_changed(tmp_path: Path) -> None:
    from scripts.suggest_mutation_coverage_command import build_recommendation

    repo, base = _seed_repo(tmp_path)
    (repo / "scripts" / "foo.py").write_text("def value():\n    return 1\n", encoding="utf-8")

    payload = build_recommendation(repo, base_sha=base)

    assert payload["status"] == "noop"
    assert "no eligible mutation-pool files" in payload["reason"]


def test_reports_blocked_without_resolvable_base(tmp_path: Path) -> None:
    from scripts.suggest_mutation_coverage_command import build_recommendation

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")

    payload = build_recommendation(repo)

    assert payload["status"] == "blocked"
    assert "pass --base-sha" in payload["reason"]


def test_skips_unreadable_candidate_test(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    broken = repo / "tests" / "quality_gates" / "test_broken.py"
    broken.write_text("from scripts import foo\n", encoding="utf-8")
    original_read_text = Path.read_text

    def flaky_read_text(path: Path, *args, **kwargs):
        if path == broken:
            raise OSError("boom")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", flaky_read_text)

    matches = sugg.tests_referencing_paths(repo, ["scripts/foo.py"])

    assert "tests/quality_gates/test_broken.py" not in matches["scripts/foo.py"]
    assert "tests/quality_gates/test_foo.py" in matches["scripts/foo.py"]


def test_main_prints_command_and_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, base = _seed_repo(tmp_path)

    assert sugg.main(["--repo-root", str(repo), "--base-sha", base]) == 0
    assert "python3 -m pytest" in capsys.readouterr().out

    assert sugg.main(["--repo-root", str(repo), "--base-sha", base, "--json"]) == 0
    payload = capsys.readouterr().out
    assert '"status": "recommended"' in payload


def test_cli_exits_nonzero_when_no_focused_command_exists(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    (repo / "tests" / "quality_gates" / "test_foo.py").write_text("def test_other(): pass\n", encoding="utf-8")
    (repo / "tests" / "test_top.py").write_text("def test_top_other(): pass\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base)

    assert result.returncode == 1
    assert "no standing pytest target" in result.stderr
