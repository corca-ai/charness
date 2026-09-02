from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from scripts.mutation import suggest_mutation_coverage_command as sugg
from scripts.core.git_checkout import head_oid_from_files

from .repo_shapes import install_committed_repo

_SUGGEST_FILES = {
    "scripts/foo.py": "def value():\n    return 1\n",
    "scripts/bar.py": "def other():\n    return 1\n",
    "tests/quality_gates/test_foo.py": (
        "from scripts import foo\n\n\ndef test_value():\n    assert foo.value() == 1\n"
    ),
    "tests/test_top.py": (
        "import scripts.foo\n\n\ndef test_top_value():\n    assert scripts.foo.value() == 1\n"
    ),
}

_FOCUSED_COMMAND = (
    "python3 scripts/gates_support/run_standing_pytest.py --repo-root . --mode read-only "
    "--pytest-target tests/quality_gates/test_foo.py --pytest-target tests/test_top.py"
)

_DYNAMIC_LOADER_FILES = {
    "scripts/shape_lib.py": "def shape():\n    return 1\n",
    "scripts/decoy.py": "def decoy():\n    return 1\n",
    "tests/test_inproc.py": (
        "import importlib.util\n"
        "from pathlib import Path\n"
        "SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'\n"
        "def _load(name):\n"
        "    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f'{name}.py')\n"
        "    module = importlib.util.module_from_spec(spec)\n"
        "    spec.loader.exec_module(module)\n"
        "    return module\n"
        "sl = _load('shape_lib')\n\n\n"
        "def test_shape():\n    assert sl.shape() == 1\n"
    ),
}

_LOADER_EXPRESSIONS = (
    'runtime.load_local_skill_module("scripts/loader_target.py", "loader_target_lib")',
    'runtime.load_local_skill_module(str(SCRIPT_ROOT / "loader_target.py"), "loader_target_lib")',
    'runtime._load_sibling("loader_target")',
)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _write_files(root: Path, files: dict[str, str]) -> Path:
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def _seed_repo(tmp_path: Path) -> tuple[Path, str]:
    """Install the shared one-commit base and apply this test's changed line."""
    repo = install_committed_repo(tmp_path / "repo", _SUGGEST_FILES, message="base")
    base = head_oid_from_files(repo)
    assert base is not None
    (repo / "scripts" / "foo.py").write_text("def value():\n    return 2\n", encoding="utf-8")
    return repo, base


def _seed_dynamic_loader_repo(tmp_path: Path) -> tuple[Path, str]:
    """Install the shared stem-loader history and apply its changed line."""
    repo = install_committed_repo(tmp_path / "repo", _DYNAMIC_LOADER_FILES, message="base")
    base = head_oid_from_files(repo)
    assert base is not None
    (repo / "scripts" / "shape_lib.py").write_text("def shape():\n    return 2\n", encoding="utf-8")
    return repo, base


def test_recommendation_statuses_and_cli_on_one_checkout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, base = _seed_repo(tmp_path)

    recommended = sugg.build_recommendation(repo, base_sha=base)
    assert recommended["status"] == "recommended"
    assert recommended["changed_pool_files"] == ["scripts/foo.py"]
    assert recommended["mapped_tests_by_file"] == {
        "scripts/foo.py": ["tests/quality_gates/test_foo.py", "tests/test_top.py"]
    }
    assert recommended["command"] == _FOCUSED_COMMAND
    assert sugg.main(["--repo-root", str(repo), "--base-sha", base]) == 0
    assert "python3 scripts/gates_support/run_standing_pytest.py" in capsys.readouterr().out
    assert sugg.main(["--repo-root", str(repo), "--base-sha", base, "--detail"]) == 0
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "recommended"

    original_read = Path.read_text

    def selective_read(self: Path, *args, **kwargs):
        if self.name == "test_top.py":
            raise OSError("unreadable")
        return original_read(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", selective_read)
    skipped = sugg.build_recommendation(repo, base_sha=base)
    mapped = skipped["mapped_tests_by_file"]["scripts/foo.py"]
    assert "tests/quality_gates/test_foo.py" in mapped
    assert "tests/test_top.py" not in mapped
    monkeypatch.setattr(Path, "read_text", original_read)

    (repo / "tests" / "quality_gates" / "test_foo.py").write_text(
        "def test_other():\n    assert True\n", encoding="utf-8"
    )
    (repo / "tests" / "test_top.py").write_text(
        "def test_top_other():\n    assert True\n", encoding="utf-8"
    )
    missing = sugg.build_recommendation(repo, base_sha=base)
    assert missing["status"] == "missing"
    assert missing["unmapped_changed_pool_files"] == ["scripts/foo.py"]
    assert "command" not in missing
    assert sugg.main(["--repo-root", str(repo), "--base-sha", base]) == 1
    missing_cli = capsys.readouterr()
    assert "no standing pytest target" in missing_cli.err
    assert "status: missing" in missing_cli.err
    assert "broad coverage fallback" in missing_cli.err

    (repo / "tests" / "quality_gates" / "test_foo.py").write_text(
        _SUGGEST_FILES["tests/quality_gates/test_foo.py"], encoding="utf-8"
    )
    (repo / "tests" / "test_top.py").write_text(_SUGGEST_FILES["tests/test_top.py"], encoding="utf-8")
    (repo / "scripts" / "bar.py").write_text("def other():\n    return 2\n", encoding="utf-8")
    partial = sugg.build_recommendation(repo, base_sha=base)
    assert partial["status"] == "partial"
    assert partial["changed_pool_files"] == ["scripts/bar.py", "scripts/foo.py"]
    assert partial["mapped_tests_by_file"] == {
        "scripts/foo.py": ["tests/quality_gates/test_foo.py", "tests/test_top.py"]
    }
    assert partial["unmapped_changed_pool_files"] == ["scripts/bar.py"]
    assert "only proves mapped files" in partial["reason"]
    assert "tests/quality_gates/test_foo.py" in partial["command"]
    assert sugg.main(["--repo-root", str(repo), "--base-sha", base]) == 0
    partial_cli = capsys.readouterr()
    assert "python3 scripts/gates_support/run_standing_pytest.py" in partial_cli.out
    assert "status: partial" in partial_cli.err
    assert "scripts/bar.py" in partial_cli.err
    assert "broad coverage fallback" in partial_cli.err

    (repo / "scripts" / "foo.py").write_text(_SUGGEST_FILES["scripts/foo.py"], encoding="utf-8")
    (repo / "scripts" / "bar.py").write_text(_SUGGEST_FILES["scripts/bar.py"], encoding="utf-8")
    (repo / "scripts" / "new_worker.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "tests" / "quality_gates" / "test_new_worker.py").write_text(
        "from scripts import new_worker\n\n\ndef test_value():\n    assert new_worker.VALUE == 1\n",
        encoding="utf-8",
    )
    untracked = sugg.build_recommendation(repo, base_sha=base)
    assert untracked["status"] == "recommended"
    assert untracked["changed_pool_files"] == ["scripts/new_worker.py"]
    assert untracked["mapped_tests_by_file"] == {
        "scripts/new_worker.py": ["tests/quality_gates/test_new_worker.py"]
    }

    (repo / "scripts" / "new_worker.py").unlink()
    (repo / "tests" / "quality_gates" / "test_new_worker.py").unlink()
    noop = sugg.build_recommendation(repo, base_sha=base)
    assert noop["status"] == "noop"
    assert "no eligible mutation-pool files" in noop["reason"]
    assert sugg.main(["--repo-root", str(repo), "--base-sha", base]) == 0
    noop_cli = capsys.readouterr()
    assert noop_cli.out == ""
    assert "status: noop" in noop_cli.err
    assert "no mutation coverage producer is needed" in noop_cli.err


def test_blocked_without_resolvable_base_is_named_by_function_and_cli(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")

    payload = sugg.build_recommendation(repo)
    assert payload["status"] == "blocked"
    assert "pass --base-sha" in payload["reason"]
    assert sugg.main(["--repo-root", str(repo)]) == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert "status: blocked" in output.err
    assert "pass --base-sha" in output.err


def test_cli_help_explains_statuses_and_closeout_workflow(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as caught:
        sugg.main(["--help"])
    assert caught.value.code == 0
    stdout = capsys.readouterr().out
    for fragment in (
        "recommended",
        "partial",
        "missing",
        "noop",
        "blocked",
        "--mutation-coverage-command",
        "--detail",
        "broad coverage fallback",
    ):
        assert fragment in stdout
    assert "--json" not in stdout


def test_mapper_shapes_on_one_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _write_files(tmp_path, _SUGGEST_FILES)

    assert sugg._local_loader_ancestor_levels(repo, "missing/worker.py") == []

    broken = repo / "tests" / "quality_gates" / "test_broken.py"
    broken.write_text("from scripts import foo\n", encoding="utf-8")
    original_read = Path.read_text

    def flaky_read_text(path: Path, *args, **kwargs):
        if path == broken:
            raise OSError("boom")
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", flaky_read_text)
    matches = sugg.tests_referencing_paths(repo, ["scripts/foo.py"])
    assert "tests/quality_gates/test_broken.py" not in matches["scripts/foo.py"]
    assert "tests/quality_gates/test_foo.py" in matches["scripts/foo.py"]
    monkeypatch.setattr(Path, "read_text", original_read)
    broken.unlink()

    worker = repo / "scripts" / "worker.py"
    entry = repo / "scripts" / "entry.py"
    worker.write_text("VALUE = 1\n", encoding="utf-8")
    entry.write_text('MODULE = _load_sibling("worker")\n', encoding="utf-8")

    def unreadable_entry(path: Path, *args, **kwargs):
        if path == entry:
            raise OSError("boom")
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", unreadable_entry)
    assert sugg._local_loader_ancestor_levels(repo, "scripts/worker.py") == []
    monkeypatch.setattr(Path, "read_text", original_read)

    (repo / "tests" / "quality_gates" / "test_split.py").write_text(
        'TARGET = ROOT / "scripts" / "foo.py"\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "support.py").write_text(
        'TARGET = "scripts/foo.py"\n', encoding="utf-8"
    )
    matches = sugg.tests_referencing_paths(repo, ["scripts/foo.py"])
    assert "tests/quality_gates/test_split.py" in matches["scripts/foo.py"]
    assert "tests/quality_gates/support.py" not in matches["scripts/foo.py"]

    (repo / "tests" / "quality_gates" / "release_fixture.py").write_text(
        'TARGET = "scripts/bar.py"\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_release.py").write_text(
        "from .release_fixture import TARGET\n\n\ndef test_target():\n    assert TARGET\n",
        encoding="utf-8",
    )
    assert sugg.tests_referencing_paths(repo, ["scripts/bar.py"]) == {
        "scripts/bar.py": ["tests/quality_gates/test_release.py"]
    }

    entry.write_text(
        'MODULE = load_local_skill_module(__file__, "worker")\n', encoding="utf-8"
    )
    (repo / "tests" / "quality_gates" / "test_entry.py").write_text(
        'TARGET = ROOT / "scripts" / "entry.py"\n', encoding="utf-8"
    )
    assert sugg.tests_referencing_paths(repo, ["scripts/worker.py"]) == {
        "scripts/worker.py": ["tests/quality_gates/test_entry.py"]
    }

    (repo / "scripts" / "loader_target.py").write_text("VALUE = 1\n", encoding="utf-8")
    decoy = repo / "tests" / "quality_gates" / "test_loader_decoy.py"
    decoy.write_text('LABEL = "loader_target.py"\n', encoding="utf-8")
    target_test = repo / "tests" / "quality_gates" / "test_loader_target.py"
    for loader_expression in _LOADER_EXPRESSIONS:
        target_test.write_text(f"MODULE = {loader_expression}\n", encoding="utf-8")
        assert sugg.tests_referencing_paths(repo, ["scripts/loader_target.py"]) == {
            "scripts/loader_target.py": ["tests/quality_gates/test_loader_target.py"]
        }

    for directory in (repo / "scripts" / "one", repo / "scripts" / "two"):
        directory.mkdir()
        (directory / "shared.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "tests" / "quality_gates" / "test_loader_shared.py").write_text(
        'MODULE = runtime.load_local_skill_module(str(ROOT / "shared.py"), "shared_lib")\n',
        encoding="utf-8",
    )
    (repo / "tests" / "quality_gates" / "test_plain_shared.py").write_text(
        'LABEL = "shared.py"\n', encoding="utf-8"
    )
    assert sugg.tests_referencing_paths(
        repo, ["scripts/one/shared.py", "scripts/two/shared.py"]
    ) == {
        "scripts/one/shared.py": ["tests/quality_gates/test_loader_shared.py"],
        "scripts/two/shared.py": ["tests/quality_gates/test_loader_shared.py"],
    }

    (repo / "scripts" / "artifact.py").write_text("VALUE = 1\n", encoding="utf-8")
    entry.write_text('MODULE = _load_local_release_module("artifact")\n', encoding="utf-8")
    assert sugg.tests_referencing_paths(repo, ["scripts/artifact.py"]) == {
        "scripts/artifact.py": ["tests/quality_gates/test_entry.py"]
    }

    entry.write_text('MODULE = _load_sibling(repo_root, "worker")\n', encoding="utf-8")
    assert sugg.tests_referencing_paths(repo, ["scripts/worker.py"]) == {
        "scripts/worker.py": ["tests/quality_gates/test_entry.py"]
    }

    entry.write_text('MODULE = _load_sibling(\n    "worker"\n)\n', encoding="utf-8")
    assert sugg.tests_referencing_paths(repo, ["scripts/worker.py"]) == {
        "scripts/worker.py": ["tests/quality_gates/test_entry.py"]
    }

    (repo / "tests" / "quality_gates" / "test_worker.py").write_text(
        'TARGET = ROOT / "scripts" / "worker.py"\n', encoding="utf-8"
    )
    entry.write_text(
        'MODULE = load_local_skill_module(__file__, "worker")\n', encoding="utf-8"
    )
    assert sugg.tests_referencing_paths(repo, ["scripts/worker.py"]) == {
        "scripts/worker.py": [
            "tests/quality_gates/test_entry.py",
            "tests/quality_gates/test_worker.py",
        ]
    }

    (repo / "scripts" / "leaf.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "scripts" / "middle.py").write_text(
        'MODULE = run_path(Path(__file__).with_name("leaf.py"))\n', encoding="utf-8"
    )
    entry.write_text('MODULE = _load_sibling("middle")\n', encoding="utf-8")
    assert sugg.tests_referencing_paths(repo, ["scripts/leaf.py"]) == {
        "scripts/leaf.py": ["tests/quality_gates/test_entry.py"]
    }


def test_mapper_contracts_without_a_tree() -> None:
    assert sugg._local_import_paths(
        "tests/quality_gates/broken.py",
        "from . import (\n",
        {"tests.quality_gates.support": "tests/quality_gates/support.py"},
    ) == set()
    assert sugg._loader_literal_tokens('load_local_skill_module(str(ROOT / "worker.py")') == set()
    assert sugg._loader_literal_tokens("(lambda: None)()") == set()
    path = "skills/public/quality/scripts/nose_report_lib.py"
    prefilter = sugg._reference_prefilter(path)
    assert prefilter == "nose_report_lib"
    samples = [
        "'skills/public/quality/scripts/nose_report_lib.py'",
        "import skills.public.quality.scripts.nose_report_lib",
        "from skills.public.quality.scripts.nose_report_lib import run_nose",
        "nr = _load('nose_report_lib')",
        "'skills' / 'public' / 'quality' / 'scripts' / 'nose_report_lib.py'",
    ]
    for text in samples:
        assert any(pattern.search(text) for pattern in sugg._reference_patterns(path)), text
        assert prefilter in text, f"prefilter would have dropped a matching text: {text}"


def test_stem_loader_maps_named_module_and_not_unnamed_decoy(tmp_path: Path) -> None:
    repo, base = _seed_dynamic_loader_repo(tmp_path)

    payload = sugg.build_recommendation(repo, base_sha=base)
    mapped = payload["mapped_tests_by_file"]
    assert mapped.get("scripts/shape_lib.py") == ["tests/test_inproc.py"]
    assert payload["status"] == "recommended"

    (repo / "scripts" / "decoy.py").write_text("def decoy():\n    return 2\n", encoding="utf-8")
    payload = sugg.build_recommendation(repo, base_sha=base)
    assert "scripts/decoy.py" in payload["unmapped_changed_pool_files"]
    assert payload["status"] == "partial"


def test_maps_a_module_reached_only_through_another_production_module(tmp_path: Path) -> None:
    """`test -> production_a -> production_b` maps `production_b`."""
    repo = install_committed_repo(
        tmp_path / "repo",
        {
            "scripts/leaf.py": "def leaf():\n    return 1\n",
            "scripts/mid.py": (
                "from scripts.leaf import leaf\n\n\ndef mid():\n    return leaf()\n"
            ),
            "tests/test_mid.py": (
                "from scripts import mid\n\n\ndef test_mid():\n    assert mid.mid() == 1\n"
            ),
        },
        message="base",
    )
    base = head_oid_from_files(repo)
    assert base is not None
    (repo / "scripts" / "leaf.py").write_text("def leaf():\n    return 2\n", encoding="utf-8")

    payload = sugg.build_recommendation(repo, base_sha=base)

    assert payload["mapped_tests_by_file"].get("scripts/leaf.py") == ["tests/test_mid.py"]
    assert payload["unmapped_changed_pool_files"] == []


def test_a_path_in_both_source_sets_is_read_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _write_files(tmp_path, _SUGGEST_FILES)
    reads: list[str] = []
    real_read = Path.read_text

    def counting_read(self: Path, *args, **kwargs):
        reads.append(self.as_posix())
        return real_read(self, *args, **kwargs)

    duplicated = "scripts/foo.py"
    monkeypatch.setattr(sugg, "_candidate_test_sources", lambda _root: [duplicated, "tests/test_top.py"])
    monkeypatch.setattr(sugg, "_candidate_module_sources", lambda _root: [duplicated])
    monkeypatch.setattr(Path, "read_text", counting_read)

    sugg.tests_referencing_paths(repo, [duplicated])

    assert reads.count((repo / duplicated).as_posix()) == 1
