from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

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
    (repo / "scripts" / "foo.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (repo / "scripts" / "bar.py").write_text("def other():\n    return 1\n", encoding="utf-8")
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
        "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only "
        "--pytest-target tests/quality_gates/test_foo.py --pytest-target tests/test_top.py"
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


def test_reports_partial_when_only_some_changed_files_map_to_tests(tmp_path: Path) -> None:
    from scripts.suggest_mutation_coverage_command import build_recommendation

    repo, base = _seed_repo(tmp_path)
    (repo / "scripts" / "bar.py").write_text("def other():\n    return 2\n", encoding="utf-8")

    payload = build_recommendation(repo, base_sha=base)

    assert payload["status"] == "partial"
    assert payload["changed_pool_files"] == ["scripts/bar.py", "scripts/foo.py"]
    assert payload["mapped_tests_by_file"] == {
        "scripts/foo.py": ["tests/quality_gates/test_foo.py", "tests/test_top.py"]
    }
    assert payload["unmapped_changed_pool_files"] == ["scripts/bar.py"]
    assert "only proves mapped files" in payload["reason"]
    assert "tests/quality_gates/test_foo.py" in payload["command"]


def test_maps_untracked_pool_file_before_commit(tmp_path: Path) -> None:
    from scripts.suggest_mutation_coverage_command import build_recommendation

    repo, base = _seed_repo(tmp_path)
    (repo / "scripts" / "foo.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (repo / "scripts" / "new_worker.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "tests" / "quality_gates" / "test_new_worker.py").write_text(
        "from scripts import new_worker\n\n\ndef test_value():\n    assert new_worker.VALUE == 1\n",
        encoding="utf-8",
    )

    payload = build_recommendation(repo, base_sha=base)

    assert payload["status"] == "recommended"
    assert payload["changed_pool_files"] == ["scripts/new_worker.py"]
    assert payload["mapped_tests_by_file"] == {
        "scripts/new_worker.py": ["tests/quality_gates/test_new_worker.py"]
    }


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


def test_loader_ancestry_stops_when_changed_directory_is_missing(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)

    assert sugg._local_loader_ancestor_levels(repo, "missing/worker.py") == []


def test_loader_ancestry_skips_unreadable_sibling(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    worker = repo / "scripts" / "worker.py"
    entry = repo / "scripts" / "entry.py"
    worker.write_text("VALUE = 1\n", encoding="utf-8")
    entry.write_text('MODULE = _load_sibling("worker")\n', encoding="utf-8")
    original_read_text = Path.read_text

    def unreadable_entry(path: Path, *args, **kwargs):
        if path == entry:
            raise OSError("boom")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", unreadable_entry)

    assert sugg._local_loader_ancestor_levels(repo, "scripts/worker.py") == []


def test_matches_split_path_expression_and_ignores_non_test_helpers(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    (repo / "tests" / "quality_gates" / "test_split.py").write_text(
        'TARGET = ROOT / "scripts" / "foo.py"\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "support.py").write_text(
        'TARGET = "scripts/foo.py"\n', encoding="utf-8"
    )

    matches = sugg.tests_referencing_paths(repo, ["scripts/foo.py"])

    assert "tests/quality_gates/test_split.py" in matches["scripts/foo.py"]
    assert "tests/quality_gates/support.py" not in matches["scripts/foo.py"]


def test_maps_reference_in_imported_test_helper(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    (repo / "tests" / "quality_gates" / "release_fixture.py").write_text(
        'TARGET = "scripts/bar.py"\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_release.py").write_text(
        "from .release_fixture import TARGET\n\n\ndef test_target():\n    assert TARGET\n",
        encoding="utf-8",
    )

    matches = sugg.tests_referencing_paths(repo, ["scripts/bar.py"])

    assert matches == {"scripts/bar.py": ["tests/quality_gates/test_release.py"]}


def test_invalid_test_helper_syntax_has_no_import_dependencies() -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    assert sugg._local_import_paths(
        "tests/quality_gates/broken.py",
        "from . import (\n",
        {"tests.quality_gates.support": "tests/quality_gates/support.py"},
    ) == set()


def test_maps_changed_local_module_through_loader_parent(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    (repo / "scripts" / "worker.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "scripts" / "entry.py").write_text(
        'MODULE = load_local_skill_module(__file__, "worker")\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_entry.py").write_text(
        'TARGET = ROOT / "scripts" / "entry.py"\n', encoding="utf-8"
    )

    matches = sugg.tests_referencing_paths(repo, ["scripts/worker.py"])

    assert matches == {"scripts/worker.py": ["tests/quality_gates/test_entry.py"]}


def test_maps_release_local_module_through_loader_parent(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    (repo / "scripts" / "artifact.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "scripts" / "entry.py").write_text(
        'MODULE = _load_local_release_module("artifact")\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_entry.py").write_text(
        'TARGET = ROOT / "scripts" / "entry.py"\n', encoding="utf-8"
    )

    matches = sugg.tests_referencing_paths(repo, ["scripts/artifact.py"])

    assert matches == {"scripts/artifact.py": ["tests/quality_gates/test_entry.py"]}


def test_maps_two_argument_local_sibling_loader(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    (repo / "scripts" / "worker.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "scripts" / "entry.py").write_text(
        'MODULE = _load_sibling(repo_root, "worker")\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_entry.py").write_text(
        'TARGET = ROOT / "scripts" / "entry.py"\n', encoding="utf-8"
    )

    matches = sugg.tests_referencing_paths(repo, ["scripts/worker.py"])

    assert matches == {"scripts/worker.py": ["tests/quality_gates/test_entry.py"]}


def test_maps_whitespace_before_one_argument_local_sibling(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    (repo / "scripts" / "worker.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "scripts" / "entry.py").write_text(
        'MODULE = _load_sibling(\n    "worker"\n)\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_entry.py").write_text(
        'TARGET = ROOT / "scripts" / "entry.py"\n', encoding="utf-8"
    )

    matches = sugg.tests_referencing_paths(repo, ["scripts/worker.py"])

    assert matches == {"scripts/worker.py": ["tests/quality_gates/test_entry.py"]}


def test_keeps_direct_and_entrypoint_tests_for_loaded_module(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    (repo / "scripts" / "worker.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "scripts" / "entry.py").write_text(
        'MODULE = load_local_skill_module(__file__, "worker")\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_worker.py").write_text(
        'TARGET = ROOT / "scripts" / "worker.py"\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_entry.py").write_text(
        'TARGET = ROOT / "scripts" / "entry.py"\n', encoding="utf-8"
    )

    matches = sugg.tests_referencing_paths(repo, ["scripts/worker.py"])

    assert matches == {
        "scripts/worker.py": [
            "tests/quality_gates/test_entry.py",
            "tests/quality_gates/test_worker.py",
        ]
    }


def test_maps_with_name_loader_transitively(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    (repo / "scripts" / "leaf.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "scripts" / "middle.py").write_text(
        'MODULE = run_path(Path(__file__).with_name("leaf.py"))\n', encoding="utf-8"
    )
    (repo / "scripts" / "entry.py").write_text(
        'MODULE = _load_sibling("middle")\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_entry.py").write_text(
        'TARGET = ROOT / "scripts" / "entry.py"\n', encoding="utf-8"
    )

    matches = sugg.tests_referencing_paths(repo, ["scripts/leaf.py"])

    assert matches == {"scripts/leaf.py": ["tests/quality_gates/test_entry.py"]}


def test_main_prints_command_and_yaml_detail(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, base = _seed_repo(tmp_path)

    assert sugg.main(["--repo-root", str(repo), "--base-sha", base]) == 0
    assert "python3 scripts/run_standing_pytest.py" in capsys.readouterr().out

    assert sugg.main(["--repo-root", str(repo), "--base-sha", base, "--detail"]) == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["status"] == "recommended"


def test_main_warns_for_partial_focused_command(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, base = _seed_repo(tmp_path)
    (repo / "scripts" / "bar.py").write_text("def other():\n    return 2\n", encoding="utf-8")

    assert sugg.main(["--repo-root", str(repo), "--base-sha", base]) == 0
    output = capsys.readouterr()
    assert "python3 scripts/run_standing_pytest.py" in output.out
    assert "status: partial" in output.err
    assert "scripts/bar.py" in output.err
    assert "broad coverage fallback" in output.err


def test_main_reports_noop_text_next_step(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, base = _seed_repo(tmp_path)
    (repo / "scripts" / "foo.py").write_text("def value():\n    return 1\n", encoding="utf-8")

    assert sugg.main(["--repo-root", str(repo), "--base-sha", base]) == 0
    output = capsys.readouterr()
    assert output.out == ""
    assert "status: noop" in output.err
    assert "no mutation coverage producer is needed" in output.err


def test_main_reports_blocked_text_next_step(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")

    assert sugg.main(["--repo-root", str(repo)]) == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert "status: blocked" in output.err
    assert "pass --base-sha" in output.err


def test_cli_exits_nonzero_when_no_focused_command_exists(tmp_path: Path) -> None:
    repo, base = _seed_repo(tmp_path)
    (repo / "tests" / "quality_gates" / "test_foo.py").write_text("def test_other(): pass\n", encoding="utf-8")
    (repo / "tests" / "test_top.py").write_text("def test_top_other(): pass\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(repo), "--base-sha", base)

    assert result.returncode == 1
    assert "no standing pytest target" in result.stderr
    assert "status: missing" in result.stderr
    assert "broad coverage fallback" in result.stderr


def test_cli_help_explains_statuses_and_closeout_workflow() -> None:
    result = run_script(SCRIPT, "--help")

    assert result.returncode == 0
    assert "recommended" in result.stdout
    assert "partial" in result.stdout
    assert "missing" in result.stdout
    assert "noop" in result.stdout
    assert "blocked" in result.stdout
    assert "--mutation-coverage-command" in result.stdout
    assert "--detail" in result.stdout
    assert "--json" not in result.stdout
    assert "broad coverage fallback" in result.stdout
