"""Tests for the fixture script-closure deriver.

This module exists because a hand-listed closure drifts silently. An UNTESTED
deriver is the same hazard wearing a better hat: its failure mode is
under-inclusion, and under-inclusion looks exactly like success until some
unrelated fixture dies with `ModuleNotFoundError`. So each spelling it claims to
recognise is pinned here, and the spellings it CANNOT see are pinned too --
declared limits rather than discovered ones.
"""

from __future__ import annotations

import pytest

import tests.script_closure as closure
from tests.script_closure import _referenced, script_import_closure


def test_dotted_package_import_is_seen() -> None:
    assert "yaml_output" in _referenced("import scripts.yaml_output\n")


def test_nested_dotted_package_import_is_seen_in_a_fixture(tmp_path, monkeypatch) -> None:
    scripts = tmp_path / "scripts" / "pkg"
    scripts.mkdir(parents=True)
    (scripts / "entry.py").write_text("VALUE = 1\n", encoding="utf-8")
    (scripts / "consumer.py").write_text("from scripts.pkg.entry import VALUE\n", encoding="utf-8")
    monkeypatch.setattr(closure, "SCRIPTS", tmp_path / "scripts")

    assert closure.script_import_closure("pkg/consumer.py") == (
        "pkg/consumer.py",
        "pkg/entry.py",
    )


def test_from_package_import_is_seen() -> None:
    assert "yaml_output" in _referenced("from scripts.yaml_output import emit_yaml\n")


def test_the_bare_flat_import_is_seen() -> None:
    """`import quality_adapter_lib` -- nine modules under `scripts/` spell it this way.

    Missed while the `ast.Import` branch accepted only the dotted `scripts.x` form.
    """
    assert "quality_adapter_lib" in _referenced("import quality_adapter_lib\n")


def test_from_scripts_import_name_is_seen() -> None:
    """`from scripts import task_run_completion` -- the NAMES carry the modules here.

    Reading only `node.module` (which is just `"scripts"`) returned nothing, so
    `task_run.py`'s derived closure silently omitted `task_run_completion.py` --
    under-inclusion, the direction this module calls fatal.
    """
    source = "from scripts import task_run_completion as _completion\n"

    assert "task_run_completion" in _referenced(source)


def test_the_regression_cases_a_reviewer_traced_are_all_reached() -> None:
    assert "task_run_completion.py" in script_import_closure("task_run.py")
    assert "check_mutation_score_summary_lib.py" in script_import_closure("check_mutation_score.py")
    assert "claude_session_jsonl_audit.py" in script_import_closure(
        "evidence/host_log_probe_lib.py"
    )


def test_the_portable_dual_path_fallback_is_seen() -> None:
    """`except ModuleNotFoundError: from yaml_output import emit_yaml`.

    Resolved by asking whether `scripts/<stem>.py` exists, not by a prefix match,
    because in this spelling there is no `scripts.` prefix to match on.
    """
    assert "yaml_output" in _referenced("from yaml_output import emit_yaml\n")


def test_the_dynamic_import_repo_module_string_is_seen() -> None:
    """Not optional: `build_retro_lesson_selection_index` reaches its deps ONLY here."""
    source = 'm = import_repo_module(__file__, "scripts.lessons.recent_lessons_lib")\n'
    assert "recent_lessons_lib" in _referenced(source)


def test_the_spec_from_file_location_filename_is_seen() -> None:
    """How `classify_push_diff.py` reaches its own lib."""
    source = 'p = Path(__file__).with_name("classify_push_diff_lib.py")\n'
    assert "classify_push_diff_lib" in _referenced(source)


def test_an_ordinary_english_string_is_not_mistaken_for_a_module() -> None:
    """The `.py` suffix requirement is what keeps this from dragging in the repo.

    `support`, `quality` and `release` are all real `scripts/` stems AND ordinary
    words; matching bare words would pull half of `scripts/` into every closure.
    """
    assert _referenced('label = "support"\nnote = "quality"\n') == set()


def test_a_relative_import_is_not_treated_as_a_scripts_module() -> None:
    assert _referenced("from .support import helper\n") == set()


def test_the_closure_is_transitive_and_includes_the_entry() -> None:
    closure = script_import_closure("build_retro_lesson_selection_index.py")

    assert "build_retro_lesson_selection_index.py" in closure
    # Reached only through the dynamic spelling, two hops down.
    assert "recent_lessons_lib.py" in closure
    assert "helper_provenance_lib.py" in closure


def test_the_regression_that_motivated_this_module() -> None:
    """`helper_provenance_lib` gained an `env_bypass` import; the hand list did not."""
    assert "env_bypass.py" in script_import_closure("build_retro_lesson_selection_index.py")


def test_a_misspelled_entry_refuses_instead_of_returning_a_short_closure() -> None:
    """Silently skipping a bad entry returns a closure short by everything it imports."""
    with pytest.raises(FileNotFoundError):
        script_import_closure("no_such_script_exists_here.py")


def test_entry_names_are_accepted_with_or_without_the_suffix() -> None:
    assert script_import_closure("yaml_output.py") == script_import_closure("yaml_output")


# --- declared blind spots ------------------------------------------------------
# Pinned so they are known limits rather than surprises. A fixture whose script
# reaches a dependency by one of these spellings still needs that name passed as
# an explicit ENTRY, which is how `adapter_lib.py` is handled in
# `test_retro_persistence.py`.


def test_a_runtime_composed_module_name_is_a_known_blind_spot() -> None:
    source = (
        'name = "recent_" + "lessons_lib"\nm = import_repo_module(__file__, "scripts." + name)\n'
    )

    assert _referenced(source) == set(), (
        "if this now resolves, the blind-spot note in tests/script_closure.py is stale"
    )


def test_a_shelled_out_script_is_a_known_blind_spot() -> None:
    """A gate that SUBPROCESSES a sibling does not import it, so no closure reaches it."""
    source = 'subprocess.run([sys.executable, "scripts/gates/check_issue_closeout_commit_msg.py"])\n'

    # The bare path string carries no `.py`-suffixed BASENAME and no `scripts.`
    # dotted form, so it is invisible here by construction.
    assert "check_issue_closeout_commit_msg" not in _referenced(source)
