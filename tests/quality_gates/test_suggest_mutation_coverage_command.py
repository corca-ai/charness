from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from scripts.git_checkout import head_oid_from_files

from .repo_shapes import install_committed_repo
from .support import run_script

SCRIPT = "scripts/suggest_mutation_coverage_command.py"

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


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _seed_repo(tmp_path: Path) -> tuple[Path, str]:
    """Install the shared one-commit base and apply this test's changed line."""
    repo = install_committed_repo(tmp_path / "repo", _SUGGEST_FILES, message="base")
    base = head_oid_from_files(repo)
    assert base is not None
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


@pytest.mark.parametrize(
    "loader_expression",
    [
        'runtime.load_local_skill_module("scripts/loader_target.py", "loader_target_lib")',
        'runtime.load_local_skill_module(str(SCRIPT_ROOT / "loader_target.py"), "loader_target_lib")',
        'runtime._load_sibling("loader_target")',
    ],
    ids=["full-path", "filename", "stem"],
)
def test_maps_literal_token_inside_supported_loader_call(
    tmp_path: Path, loader_expression: str
) -> None:
    """Resolve the exact alias-plus-``str(...)`` shape that escaped locally.

    The old regex stopped at the nested closing parenthesis, so an existing test
    was reported as absent and deliberate mapper policy let the push continue.
    The unrelated quoted filename is the discriminating control: filenames are
    evidence only inside a supported loader boundary.
    """
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
    (repo / "scripts" / "loader_target.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "tests" / "quality_gates" / "test_loader_target.py").write_text(
        f"MODULE = {loader_expression}\n",
        encoding="utf-8",
    )
    (repo / "tests" / "quality_gates" / "test_loader_decoy.py").write_text(
        'LABEL = "loader_target.py"\n', encoding="utf-8"
    )

    matches = sugg.tests_referencing_paths(repo, ["scripts/loader_target.py"])

    assert matches == {
        "scripts/loader_target.py": ["tests/quality_gates/test_loader_target.py"]
    }


def test_loader_basename_can_safely_overselect_but_plain_string_cannot(tmp_path: Path) -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    repo, _base = _seed_repo(tmp_path)
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

    matches = sugg.tests_referencing_paths(
        repo, ["scripts/one/shared.py", "scripts/two/shared.py"]
    )

    assert matches == {
        "scripts/one/shared.py": ["tests/quality_gates/test_loader_shared.py"],
        "scripts/two/shared.py": ["tests/quality_gates/test_loader_shared.py"],
    }


def test_invalid_loader_source_has_no_literal_tokens() -> None:
    from scripts import suggest_mutation_coverage_command as sugg

    assert sugg._loader_literal_tokens('load_local_skill_module(str(ROOT / "worker.py")') == set()
    assert sugg._loader_literal_tokens("(lambda: None)()") == set()


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


# --------------------------------------------------------------------------- #
# D40 mapper repair: the mapper fed a BLOCKING pre-push gate a confidently wrong
# answer. Both gaps below produced the same observable — a changed file mapped to
# a test that does not cover it — and a false block is how a gate gets bypassed.
# --------------------------------------------------------------------------- #
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


def _seed_dynamic_loader_repo(tmp_path: Path) -> tuple[Path, str]:
    """Install the shared stem-loader history and apply its changed line."""
    repo = install_committed_repo(tmp_path / "repo", _DYNAMIC_LOADER_FILES, message="base")
    base = head_oid_from_files(repo)
    assert base is not None
    (repo / "scripts" / "shape_lib.py").write_text("def shape():\n    return 2\n", encoding="utf-8")
    return repo, base


def test_maps_a_module_loaded_by_bare_stem(tmp_path: Path) -> None:
    from scripts.suggest_mutation_coverage_command import build_recommendation

    repo, base = _seed_dynamic_loader_repo(tmp_path)

    payload = build_recommendation(repo, base_sha=base)

    mapped = payload["mapped_tests_by_file"]
    assert mapped.get("scripts/shape_lib.py") == ["tests/test_inproc.py"]
    assert payload["status"] == "recommended"


def test_does_not_map_a_module_the_stem_search_never_names(tmp_path: Path) -> None:
    """The discriminating control: the stem pattern widened the match, it did not
    make everything match. `decoy.py` is never named by any test, so it must stay
    unmapped — otherwise the previous test passes for the wrong reason."""
    from scripts.suggest_mutation_coverage_command import build_recommendation

    repo, base = _seed_dynamic_loader_repo(tmp_path)
    (repo / "scripts" / "decoy.py").write_text("def decoy():\n    return 2\n", encoding="utf-8")

    payload = build_recommendation(repo, base_sha=base)

    assert "scripts/decoy.py" in payload["unmapped_changed_pool_files"]
    assert payload["status"] == "partial"


def test_maps_a_module_reached_only_through_another_production_module(tmp_path: Path) -> None:
    """`test -> production_a -> production_b` maps `production_b`.

    Before the closure spanned production modules, `production_b` was reachable only
    when a test mentioned it textually. Running that one test DOES cover it, so
    leaving it unmapped made the focused producer report its changed lines as
    uncovered — a block on a file the suite actually covers.
    """
    from scripts.suggest_mutation_coverage_command import build_recommendation

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
    # Only the LEAF changes, and no test names it.
    (repo / "scripts" / "leaf.py").write_text("def leaf():\n    return 2\n", encoding="utf-8")

    payload = build_recommendation(repo, base_sha=base)

    assert payload["mapped_tests_by_file"].get("scripts/leaf.py") == ["tests/test_mid.py"]
    assert payload["unmapped_changed_pool_files"] == []


def test_reference_prefilter_admits_every_pattern_it_gates(tmp_path: Path) -> None:
    """The prefilter is a performance guard on a correctness path, so it has to be a
    SOUND one: skipping a text that the regexes would have matched silently unmaps a
    file. Every pattern anchors on the stem, which is what makes the single `in` check
    safe — assert that directly rather than trusting the claim."""
    from scripts.suggest_mutation_coverage_command import _reference_patterns, _reference_prefilter

    path = "skills/public/quality/scripts/nose_report_lib.py"
    prefilter = _reference_prefilter(path)
    assert prefilter == "nose_report_lib"
    samples = [
        "'skills/public/quality/scripts/nose_report_lib.py'",
        "import skills.public.quality.scripts.nose_report_lib",
        "from skills.public.quality.scripts.nose_report_lib import run_nose",
        "nr = _load('nose_report_lib')",
        "'skills' / 'public' / 'quality' / 'scripts' / 'nose_report_lib.py'",
    ]
    for text in samples:
        assert any(pattern.search(text) for pattern in _reference_patterns(path)), text
        assert prefilter in text, f"prefilter would have dropped a matching text: {text}"


def test_a_path_in_both_source_sets_is_read_once(tmp_path: Path, monkeypatch) -> None:
    """The test targets and the mutation pool can name the SAME file, and each source
    is read from disk. Re-reading it would be waste; letting the second read overwrite
    the first would be worse if the two lists ever disagreed about the path. The dedup
    guard is asserted by counting reads rather than by inspecting the result, because
    the mapping looks identical either way."""
    from scripts import suggest_mutation_coverage_command as suggester

    repo, base = _seed_repo(tmp_path)
    reads: list[str] = []
    real_read = Path.read_text

    def counting_read(self: Path, *args, **kwargs):
        reads.append(self.as_posix())
        return real_read(self, *args, **kwargs)

    duplicated = "scripts/foo.py"
    monkeypatch.setattr(suggester, "_candidate_test_sources", lambda _root: [duplicated, "tests/test_top.py"])
    monkeypatch.setattr(suggester, "_candidate_module_sources", lambda _root: [duplicated])
    monkeypatch.setattr(Path, "read_text", counting_read)

    suggester.tests_referencing_paths(repo, [duplicated])

    assert reads.count((repo / duplicated).as_posix()) == 1


def test_an_unreadable_source_is_skipped_rather_than_fatal(tmp_path: Path, monkeypatch) -> None:
    """A source file the mapper cannot read must not abort the mapping: the mapper
    feeds a BLOCKING gate, and a crash there is a push blocked by an unrelated
    filesystem problem. The remaining sources still map."""
    from scripts import suggest_mutation_coverage_command as suggester

    repo, base = _seed_repo(tmp_path)
    real_read = Path.read_text

    def selective_read(self: Path, *args, **kwargs):
        if self.name == "test_top.py":
            raise OSError("unreadable")
        return real_read(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", selective_read)

    payload = suggester.build_recommendation(repo, base_sha=base)

    mapped = payload["mapped_tests_by_file"]["scripts/foo.py"]
    assert "tests/quality_gates/test_foo.py" in mapped
    assert "tests/test_top.py" not in mapped
