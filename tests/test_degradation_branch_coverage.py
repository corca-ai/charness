"""Cover the DEGRADATION branches the mutation gate reported as uncovered (#457).

Root cause of the blocking signal, not just its symptom: #457's 14 changed-line
proof targets all sit in RARELY-TAKEN branches. Most are hardening branches -- an
`except Exception: return None` that degrades a hint to no hint, a not-found
`raise`, a ">3 offenders" truncation, a "nothing in scope" early return -- and a
couple are ordinary-but-unexercised alternates, such as a caller-selected
filesystem fallback and a renderer arm for one finding kind. (An earlier draft of
this docstring claimed all 14 were degradation branches; fresh-eye review checked
that against the source and it does not hold.) Either way, happy-path and
named-rule tests never reach them, so each hardening commit adds uncovered changed
lines and the NEXT mutation run blocks.

Covering the specific 14 lines would only retro-fit the report. What keeps the
class closed is testing the degradation branch as a first-class behavior: each test
below asserts what the tool DOES when the unusual thing happens, so the branch has
a named contract rather than only coverage.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
artifact_validator = load_script_module(
    "artifact_validator_degradation_test", ROOT / "scripts" / "artifact_validator.py"
)
preflight = load_script_module(
    "check_doc_authoring_preflight_degradation_test",
    ROOT / "scripts" / "gates" / "check_doc_authoring_preflight.py",
)
check_doc_links = load_script_module(
    "check_doc_links_degradation_test", ROOT / "scripts" / "gates" / "check_doc_links.py"
)

# `from scripts import ...`, not a bare `import artifact_violation_report`: the
# coverage mapper resolves a changed file to its tests by looking for the DOTTED
# module path, and a bare top-level import is invisible to it -- the gate reported
# this file as mapping to no standing test at all while these tests drove it.
artifact_violation_report = load_script_module(
    "artifact_violation_report_degradation_test", ROOT / "scripts" / "artifact_violation_report.py"
)

# --- artifact_violation_report: the scaffold hint must degrade, never raise ----
# The hint machinery moved out of `artifact_validator` when that file hit its length
# cap; these patch the OWNING module because monkeypatching a re-export leaves the
# real callee untouched, which is a green test proving nothing.


def test_scaffold_rel_returns_none_when_the_registry_import_fails(monkeypatch) -> None:
    """A hint must never change a verdict, so a broken registry import degrades.

    `_scaffold_rel` wraps the import in `except Exception: return None` precisely so
    a consuming repo that does not ship the skill tree still gets a verdict. If this
    raised instead, every validator failure in such a repo would become a crash.
    """

    def boom(_name: str):
        raise ImportError("no registry here")

    monkeypatch.setattr(artifact_violation_report.importlib, "import_module", boom)
    assert artifact_violation_report._scaffold_rel("quality") is None


def test_scaffold_hint_is_none_when_the_scaffold_is_unresolvable(monkeypatch) -> None:
    monkeypatch.setattr(artifact_violation_report, "_scaffold_rel", lambda _t: None)
    assert artifact_violation_report.scaffold_hint("quality") is None


def test_report_validation_failure_still_exits_one_without_a_hint(monkeypatch, capsys) -> None:
    """The exit code is the verdict; the hint is decoration that may be absent."""
    monkeypatch.setattr(artifact_violation_report, "_scaffold_rel", lambda _t: None)
    assert artifact_violation_report.report_validation_failure("broken", artifact_type="nope") == 1
    err = capsys.readouterr().err
    assert "broken" in err
    assert "hint:" not in err


def test_scaffold_rel_binds_the_registry_from_the_scripts_layout(monkeypatch) -> None:
    """The hint function binds the registry from the scripts layout.

    Covers the branch by removing the entry first, so the insert line runs rather
    than being skipped by the `not in sys.path` check. Assert the module that the
    function bound, not the test process's ambient path.
    """
    scripts_dir = str(Path(artifact_violation_report.__file__).resolve().parent)
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != scripts_dir])
    # quality is a registered surface with a real scaffold in this layout.
    assert artifact_validator._scaffold_rel("quality") is not None
    registry = artifact_validator._scaffold_rel.__globals__["importlib"].import_module(
        "check_artifact_surface_preflight"
    )
    assert (
        Path(registry.__file__).resolve()
        == Path(scripts_dir) / "check_artifact_surface_preflight.py"
    )


# --- check_changed_line_mutation_coverage: fingerprint degrades to "" ----------


def test_changed_pool_fingerprint_failure_degrades_to_empty(monkeypatch, tmp_path) -> None:
    """A git failure must not abort the coverage gate; the fingerprint goes empty.

    The fingerprint only decides whether a cached coverage JSON is reusable, so
    losing it should cost freshness, never the run.
    """
    # `_pin_run_state` and the git helper it calls both live in the run-trust module
    # now, so patch THAT module: patching the gate's re-exported names would leave the
    # real callee untouched and the test would pass while exercising nothing.
    # `from scripts import ...`, not a bare `import changed_line_run_trust`: the
    # coverage mapper resolves a changed file to its tests by looking for the DOTTED
    # module path, and a bare top-level import is invisible to it. Written that way,
    # this file covers the lines below while the gate still reports them uncovered.
    from scripts.gates_support import changed_line_run_trust as trust

    def boom(*_args, **_kwargs):
        raise OSError("git unavailable")

    monkeypatch.setattr(trust, "changed_pool_fingerprint", boom)
    monkeypatch.setattr(trust, "_resolve_pair", lambda *_a, **_k: ("deadbeef", "deadbeef"))
    pinned = trust._pin_run_state(tmp_path, "base", "head")
    assert pinned["pool_fingerprint"] == ""
    # The rest of the pin must still be usable, i.e. the failure is contained.
    assert pinned["resolved_head_sha"] == "deadbeef"


def test_pin_run_state_reads_literal_head_once(monkeypatch, tmp_path) -> None:
    from scripts.gates_support import changed_line_run_trust as trust

    calls: list[tuple[str, ...]] = []

    def git_lines(_root, args):
        calls.append(tuple(args))
        return ["deadbeef"]

    monkeypatch.setattr(trust, "_git_lines", git_lines)
    # `**_kwargs`, not `*_args` alone: the production call passes `checkout=` by keyword,
    # and a positional-only stub turns that into a TypeError inside the try/except that
    # DEGRADES the fingerprint -- so a stale stub here does not read as a stale stub, it
    # reads as the degradation branch this file is otherwise about.
    monkeypatch.setattr(trust, "changed_pool_fingerprint", lambda *_args, **_kwargs: "pool")

    pinned = trust._pin_run_state(tmp_path, "base", "HEAD")

    assert pinned["resolved_head_sha"] == "deadbeef"
    assert pinned["head_commit"] == "deadbeef"
    assert calls == [("rev-parse", "HEAD")]


# --- check_doc_links: truncation and the no-index fallback --------------------


def test_unresolved_command_message_truncates_after_three(tmp_path) -> None:
    """More than three offenders must summarize, not print an unbounded list.

    Drives `check_doc_links.main()` against a tmp `--repo-root` so the production
    truncation lines actually execute. An earlier version of this test called the
    iterator and then re-implemented the slice-and-append itself, which left the
    real `refs += ", ..."` lines uncovered -- i.e. it would have passed while the
    very lines #457 blocked on stayed untested.
    """
    root = tmp_path
    (root / "scripts").mkdir()
    # The doc must sit under a scanned glob (docs/**/*.md); a bare root-level
    # markdown file is not in DOC_GLOBS and the gate would pass vacuously.
    (root / "docs").mkdir()
    doc = root / "docs" / "doc.md"
    doc.write_text(
        "# D\n\n" + "\n".join(f"run `python3 scripts/absent{n}.py`" for n in range(5)) + "\n",
        encoding="utf-8",
    )
    result = _run("scripts/gates/check_doc_links.py", "--repo-root", str(root))
    assert result.returncode == 1, result.stdout
    assert ", ..." in result.stderr, result.stderr
    # Exactly three offenders are named before the ellipsis.
    named = result.stderr.count("scripts/absent")
    assert named == 3, f"expected 3 named offenders before truncation, got {named}"


def test_unresolved_command_message_lists_all_when_three_or_fewer(tmp_path) -> None:
    """The counterweight: at or below the cap there must be NO ellipsis.

    Without this, a mutant that always appended ", ..." would pass the test above.
    """
    root = tmp_path
    (root / "scripts").mkdir()
    (root / "docs").mkdir()
    doc = root / "docs" / "doc.md"
    doc.write_text(
        "# D\n\n" + "\n".join(f"run `python3 scripts/absent{n}.py`" for n in range(2)) + "\n",
        encoding="utf-8",
    )
    result = _run("scripts/gates/check_doc_links.py", "--repo-root", str(root))
    assert result.returncode == 1
    assert ", ..." not in result.stderr, result.stderr
    assert result.stderr.count("scripts/absent") == 2


def test_resolves_falls_back_to_the_filesystem_without_a_path_index(tmp_path) -> None:
    """With no pre-built index the checker must stat the filesystem instead.

    That fallback is what lets the preflight run on a single file without paying
    for a full repo path listing.
    """
    root = tmp_path
    (root / "scripts").mkdir()
    (root / "scripts" / "real.py").write_text("print()\n", encoding="utf-8")
    doc = root / "doc.md"
    doc.write_text(
        "# D\n\nrun `python3 scripts/real.py` and `python3 scripts/missing.py`\n",
        encoding="utf-8",
    )
    # known_repo_paths=None forces the `(root / rel_posix).exists()` branch.
    unresolved = list(check_doc_links.iter_unresolved_command_targets(root, doc, None))
    names = {candidate for _line, candidate in unresolved}
    assert "scripts/missing.py" in names
    assert "scripts/real.py" not in names


# --- check_doc_authoring_preflight: the rare row kind renders ------------------


def test_preflight_emits_the_unresolved_command_target_row_with_its_own_remedy(tmp_path) -> None:
    """The `unresolved-command-target` row is a distinct kind carrying its own remedy.

    It used to be a distinct human message. With output unconditionally YAML the
    row kind and the remedy text that named the `<repo-root>/...` placeholder are
    payload keys instead, so the same two facts are asserted there.

    Built through the real `build_report` rather than a hand-constructed Report, so
    the test cannot drift from the dataclass shape and it exercises the collector
    and the payload builder on one path.
    """
    root = tmp_path
    (root / "scripts").mkdir()
    doc = root / "doc.md"
    doc.write_text("# D\n\nrun `python3 scripts/absent.py`\n", encoding="utf-8")
    report = preflight.build_report(root, str(doc))
    payload = preflight.report_payload(report)
    row = next(r for r in payload["doc_links"] if r["kind"] == "unresolved-command-target")
    assert row["detail"] == "scripts/absent.py"
    assert row["reason"] == "missing-script"
    assert "placeholder" in payload["doc_link_remedies"]["unresolved-command-target"]
    assert report.blocked is True


def test_preflight_collects_an_unresolved_command_target_finding(tmp_path) -> None:
    """The collector side of the same row kind."""
    root = tmp_path
    (root / "scripts").mkdir()
    doc = root / "doc.md"
    doc.write_text("# D\n\nrun `python3 scripts/absent.py`\n", encoding="utf-8")
    findings = preflight.collect_doc_links(root, doc)
    kinds = {row["kind"] for row in findings}
    assert "unresolved-command-target" in kinds


# --- record_quality_runtime: the not-found raise ------------------------------


def test_quality_script_lookup_raises_when_absent(tmp_path) -> None:
    """A missing quality helper must name itself, not fail later as an AttributeError."""
    record_quality_runtime = load_script_module(
        "record_quality_runtime_degradation_test", ROOT / "scripts" / "gates_support" / "record_quality_runtime.py"
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        record_quality_runtime._quality_script_path(tmp_path, "definitely_absent.py")
    assert "definitely_absent.py" in str(excinfo.value)


# --- validate_debug_artifact: empty scope is a no-op, not a failure -----------


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    module = load_script_module(f"degradation_{Path(script).stem}", ROOT / script)
    result = run_loaded_script_main(script, module, *args)
    return subprocess.CompletedProcess(
        [script, *args], result.returncode, result.stdout, result.stderr
    )


def test_debug_validator_treats_no_artifacts_in_scope_as_success(tmp_path) -> None:
    """Most commits touch no debug artifact, so empty scope must exit 0.

    If this returned nonzero the gate would fail on nearly every commit; the branch
    exists for the common case, which is exactly why it needs a named test.
    """
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / ".agents").mkdir(parents=True)
    result = _run(
        "scripts/gates/validate_debug_artifact.py",
        "--repo-root",
        str(repo),
        "--paths",
        "scripts/unrelated.py",
    )
    assert result.returncode == 0, result.stderr
    assert "No debug artifacts in scope." in result.stdout


def test_debug_validator_reports_a_validation_error_through_the_scaffold_path(tmp_path) -> None:
    """The module-level handler must convert a ValidationError into exit 1 + hint."""
    repo = tmp_path / "repo"
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "2026-07-27-broken.md").write_text("# not a debug artifact\n", encoding="utf-8")
    result = _run("scripts/gates/validate_debug_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    # `returncode == 1` plus non-empty stderr is ALSO what an uncaught traceback
    # produces, so those two assertions cannot tell graceful handling from a crash.
    # These can.
    assert "Invalid debug artifact" in result.stderr, result.stderr
    assert "Traceback" not in result.stderr, result.stderr


def test_preflight_report_json_round_trips(tmp_path) -> None:
    """`to_dict` is the machine surface the affordance advertises; keep it honest."""
    root = tmp_path
    doc = root / "clean.md"
    doc.write_text("# Clean\n\nnothing to report here\n", encoding="utf-8")
    report = preflight.build_report(root, str(doc))
    payload = json.loads(json.dumps(report.to_dict()))
    assert payload["target"].endswith("clean.md")
    assert payload["status"] == "ok"


# --- the same class, on THIS branch's own changed lines ------------------------
#
# The CI changed-line gate flagged seven more files after the #457 fix landed,
# which is the class reasserting itself rather than a new problem: every target
# below is again a rarely-taken branch. Covering them here keeps the fix general
# instead of scoped to the 14 lines the issue happened to list.


def test_artifact_label_falls_back_when_the_path_escapes_the_repo(tmp_path) -> None:
    """`_artifact_label` must degrade to the raw path, not raise.

    `Path.relative_to` raises ValueError for a path outside repo_root, and
    `--artifact-path` deliberately accepts a draft in a temp dir, so this except
    is on the success path of a supported invocation.
    """
    outside = tmp_path / "elsewhere" / "draft.md"
    outside.parent.mkdir(parents=True)
    outside.write_text("x", encoding="utf-8")
    label = artifact_validator._artifact_label(outside, ROOT)
    assert label == str(outside)
    # And the repo-relative branch still wins when it applies.
    inside = ROOT / "AGENTS.md"
    assert artifact_validator._artifact_label(inside, ROOT) == "AGENTS.md"


def test_artifact_label_without_a_repo_root_returns_the_path() -> None:
    assert artifact_validator._artifact_label(Path("a/b.md"), None) == "a/b.md"


def test_lesson_that_is_only_a_class_tag_is_skipped(tmp_path) -> None:
    """A bullet whose entire content is the tag must not become an empty lesson.

    Covers the post-strip `continue`: stripping the marker can empty the text, and
    an empty lesson would otherwise be indexed with a blank display string.
    """
    lib = load_script_module(
        "recent_lessons_lib_degradation_test",
        ROOT / "scripts" / "lessons" / "recent_lessons_lib.py",
    )

    retro_dir = tmp_path / "charness-artifacts" / "retro"
    retro_dir.mkdir(parents=True)
    (retro_dir / "2026-07-27-demo.md").write_text(
        "# Session Retro: demo\nDate: 2026-07-27\nMode: session\n\n"
        "## Waste\n\n- recurrence-class: only-a-tag\n- a real lesson\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-07-27-demo.md\n",
        encoding="utf-8",
    )
    payload = lib.build_lesson_selection_index(
        repo_root=tmp_path, output_dir=retro_dir, summary_path=retro_dir / "recent-lessons.md"
    )
    lessons = [c["lesson"] for c in payload["candidates"]]
    assert "a real lesson" in lessons
    assert "" not in lessons, "a tag-only bullet must be skipped, not indexed blank"


def test_source_tree_marker_with_unreadable_manifest_is_not_a_source_tree(tmp_path) -> None:
    """A corrupt marker must read as 'not a source tree', never crash the guard."""
    lib = load_script_module(
        "helper_provenance_lib_degradation_test", ROOT / "scripts" / "core" / "helper_provenance_lib.py"
    )

    root = tmp_path / "repo"
    root.mkdir()
    marker = root / lib.SOURCE_TREE_MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("{not json", encoding="utf-8")
    assert lib.is_charness_source_tree(root) is False


def test_charness_version_skips_unreadable_and_non_dict_manifests(tmp_path) -> None:
    """Version lookup walks past a corrupt or wrong-shaped manifest to the next one."""
    lib = load_script_module(
        "helper_provenance_lib_version_degradation_test",
        ROOT / "scripts" / "core" / "helper_provenance_lib.py",
    )

    root = tmp_path / "repo"
    root.mkdir()
    sources = list(lib._VERSION_SOURCES)
    first = root / sources[0]
    first.parent.mkdir(parents=True, exist_ok=True)
    first.write_text("{broken", encoding="utf-8")
    # No readable manifest anywhere -> None rather than an exception.
    assert lib.charness_version(root) is None

    if len(sources) > 1:
        second = root / sources[1]
        second.parent.mkdir(parents=True, exist_ok=True)
        second.write_text('{"version": "9.9.9"}', encoding="utf-8")
        assert lib.charness_version(root) == "9.9.9"


def test_help_probe_readers_are_empty_when_the_probe_did_not_run_clean() -> None:
    """A depth that never probed clean contributes nothing, rather than raising.

    Moved here from `check_documented_command_flags._probed_options_with_values`
    when the probe was extracted into `argparse_help_probe`: both
    documented-command gates now inherit this branch from one owner, and the
    branch is what makes the walk descend exactly one level per round.
    """
    import subprocess as _sp

    probe_module = load_script_module(
        "argparse_help_probe_degradation_test", ROOT / "scripts" / "core" / "argparse_help_probe.py"
    )

    probe = probe_module.HelpProbe(ROOT)
    unprimed = ("demo",)
    assert probe.options_with_values(unprimed) == set()
    assert probe.accepted_options(unprimed) == set()
    assert probe.subcommand_choices(unprimed) == set()

    probe._results[unprimed] = _sp.CompletedProcess(args=["x"], returncode=2, stdout="", stderr="")
    assert probe.options_with_values(unprimed) == set()
    assert probe.accepted_options(unprimed) == set()
    assert probe.subcommand_choices(unprimed) == set()


def test_attention_scan_roots_include_skills_shared_when_present(tmp_path) -> None:
    """`skills/shared` must be scanned in the source layout, and skipped when absent.

    It sat outside every scan root, so its declarations could never be satisfied.
    """
    gate = load_script_module(
        "validate_attention_state_visibility_degradation_test",
        ROOT / "tools" / "validate_attention_state_visibility.py",
    )

    repo = tmp_path / "repo"
    for rel in ("skills/public", "skills/support"):
        (repo / rel).mkdir(parents=True)
    without = {str(root) for root in gate.default_scan_roots(repo)}
    (repo / "skills" / "shared").mkdir()
    with_shared = {str(root) for root in gate.default_scan_roots(repo)}
    assert len(with_shared) == len(without) + 1
    assert any("shared" in root for root in with_shared)
    assert not any("shared" in root for root in without)


def test_pin_run_state_survives_a_git_failure_in_the_fingerprint(monkeypatch, tmp_path) -> None:
    """`_pin_run_state` pins the run's identity BEFORE any expensive work, so a git
    failure while computing the changed-pool fingerprint must cost freshness only.
    Letting it propagate would turn a degraded input into a crash at the one point
    where the gate is deciding what it is even allowed to judge."""
    # `from scripts import ...`, not a bare `import changed_line_run_trust`: the
    # coverage mapper resolves a changed file to its tests by looking for the DOTTED
    # module path, and a bare top-level import is invisible to it. Written that way,
    # this file covers the lines below while the gate still reports them uncovered.
    from scripts.gates_support import changed_line_run_trust as trust

    def boom(*_args, **_kwargs):
        raise OSError("git not found")

    monkeypatch.setattr(trust, "changed_pool_fingerprint", boom)
    monkeypatch.setattr(trust, "_resolve_pair", lambda *_a, **_k: ("cafebabe", "cafebabe"))

    pinned = trust._pin_run_state(tmp_path, "base", "head")

    assert pinned["pool_fingerprint"] == ""
    assert pinned["resolved_head_sha"] == "cafebabe"


# --- the artifact line budget must degrade to its DEFAULT, never to "unlimited" ---
# The changed-line gate named every branch below by path:line after the #640 slice.
# They are hardening arms by construction: each one exists because the ceiling is now
# resolved across a seam (adapter file, or a validator loaded from a separate tree),
# and a seam that can fail must produce a number the gate agrees with rather than a
# traceback or a silently disarmed budget.


def test_an_unreadable_adapter_degrades_the_ceiling_to_the_default(tmp_path) -> None:
    """Failing OPEN here would disarm the budget entirely, which is the worse arm.

    `resolve_adapter_line_budget` swallows any `load_adapter` failure. The
    conservative result is the shipped default: the adapter failure is already
    reported by the caller's own artifact discovery, and inventing no ceiling would
    turn one broken YAML line into a gate that accepts anything.
    """

    def boom(_repo_root):
        raise RuntimeError("adapter unreadable")

    # `999`, not the shipped `180`: with the real default these tests could not tell
    # "returned the caller's default" from "returned a hardcoded 180".
    assert (
        artifact_validator.resolve_adapter_line_budget(
            boom, tmp_path, field="max_artifact_words", default=999
        )
        == 999
    )


@pytest.mark.parametrize(
    ("declared", "expected"),
    [(True, 999), ("240", 999), (0, 999), (-1, 999), (None, 999), (240, 240)],
    ids=["bool", "string", "zero", "negative", "absent", "honored"],
)
def test_a_value_the_resolver_should_have_refused_still_yields_the_default(
    tmp_path, declared, expected
) -> None:
    """The isinstance re-check is not redundant with the resolver.

    A consuming repo can vendor a resolver older than its validator, so this module
    must not turn that skew into a ceiling of `True` (which `isinstance(True, int)`
    would otherwise make 1, refusing every artifact past its title line).
    """
    adapter = {"data": {} if declared is None else {"max_artifact_words": declared}}

    # The last arm is the POSITIVE control: without it, deleting adapter resolution
    # entirely (`return default`) passes every case above, which is exactly the
    # both-tests-green-only-one-exercises-the-branch class this file exists for.
    assert (
        artifact_validator.resolve_adapter_line_budget(
            lambda _repo_root: adapter, tmp_path, field="max_artifact_words", default=999
        )
        == expected
    )


def test_a_scaffold_says_so_when_it_cannot_reach_the_gates_resolver(monkeypatch) -> None:
    """The forecast degrades to the default AND marks itself, rather than lying.

    Round-2 review found the first version of this guard silently returning the
    default, which re-enters the exact defect the adapter field exists to close: a repo
    declaring 300 would be handed a forecast of 180 with nothing red, and would write
    to fit a number its own gate does not enforce.
    """
    from scripts.core import scaffold_artifact_lib

    def boom(*_args, **_kwargs):
        raise AttributeError("resolver missing from a stale vendored validator")

    validator = SimpleNamespace(
        resolve_adapter_line_budget=boom, WORD_BUDGET_FIELD="max_artifact_words"
    )
    budget = scaffold_artifact_lib.size_budget(validator, 180, {"data": {}}, guidance="g")

    assert budget == {
        "max_words": 180,
        "source": "default (adapter ceiling unresolvable)",
        "guidance": "g",
    }


def test_a_scaffold_publishes_no_budget_at_all_when_the_validator_never_loaded() -> None:
    """A consuming repo without the repo-root `scripts/` tree has no ceiling to name.

    Distinct from the arm above: there the validator loaded and its resolver failed, so
    a default exists to fall back to. Here nothing loaded, and publishing the shipped
    literal would assert a ceiling this install cannot enforce.
    """
    from scripts.core import scaffold_artifact_lib

    assert scaffold_artifact_lib.size_budget(None, 180, {}, guidance="g") is None
    assert scaffold_artifact_lib.size_budget(object(), None, {}, guidance="g") is None


def test_read_lines_names_the_missing_artifact_rather_than_raising_oserror(tmp_path) -> None:
    """The gate's own error type, so a missing path reports as a violation, not a crash.

    `report_validation_failure` catches `ValidationError` and adds the scaffold hint; an
    `OSError` escaping here would bypass both and print a traceback where the author
    expects "start from the owning scaffold".
    """
    with pytest.raises(artifact_validator.ValidationError) as excinfo:
        artifact_validator.read_lines(tmp_path / "nope.md")

    assert "nope.md" in str(excinfo.value)


@pytest.mark.parametrize(
    ("scaffold_rel", "validator_module", "attr"),
    [
        (
            "skills/public/debug/scripts/scaffold_debug_artifact.py",
            "scripts.gates.validate_debug_artifact",
            "_debug_validator",
        ),
        (
            "skills/public/quality/scripts/scaffold_quality_artifact.py",
            "scripts.gates.validate_quality_artifact",
            "_quality_validator",
        ),
    ],
    ids=["debug", "quality"],
)
def test_a_scaffold_still_imports_when_the_repo_root_validator_is_absent(
    monkeypatch, scaffold_rel, validator_module, attr
) -> None:
    """An installed skill tree without the repo-root `scripts/` tree must still scaffold.

    This is the IMPORT-time arm of the degradation, distinct from a resolver that fails
    at call time: the whole module must load, because a consumer whose install ships
    only `skills/` would otherwise get a traceback instead of a template. The budget is
    additive guidance, so its absence must cost the budget and nothing else.

    Forced with a `meta_path` finder rather than by filtering `sys.path`: the loader is
    `importlib.import_module` after the scaffold puts the repo root on the path itself,
    so a path filter would be undone by the module under test. A finder refuses the one
    name regardless of how the path is arranged, which is the local fact being asserted.
    """

    class _Refuse:
        def find_spec(self, name, path=None, target=None):
            if name == validator_module:
                raise ImportError(f"no {name} in this layout")
            return None

    # `delitem` alone. A preceding `setitem(..., None)` sentinel would be deleted on
    # the next line before any import runs -- inert today, and a hazard the day someone
    # reorders the two: the sentinel would make `import` fail via `sys.modules`, the
    # finder would never be consulted, and the test would still pass while asserting
    # the degradation for a mechanism it no longer exercises.
    monkeypatch.delitem(sys.modules, validator_module, raising=False)
    monkeypatch.setattr(sys, "meta_path", [_Refuse(), *sys.meta_path])

    path = ROOT / scaffold_rel
    module = load_script_module(f"probe_{attr}", path)

    assert getattr(module, attr) is None
    assert module._MAX_ARTIFACT_WORDS is None
    # And the consequence the arm exists for: a payload with no ceiling claim at all,
    # rather than the shipped literal asserted against a gate this install cannot run.
    from scripts.core import scaffold_artifact_lib

    assert (
        scaffold_artifact_lib.size_budget(
            getattr(module, attr), module._MAX_ARTIFACT_WORDS, {"data": {}}, guidance="g"
        )
        is None
    )
