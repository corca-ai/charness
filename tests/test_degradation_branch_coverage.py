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

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import artifact_validator  # noqa: E402
import check_doc_authoring_preflight as preflight  # noqa: E402
import check_doc_links  # noqa: E402

# --- artifact_validator: the scaffold hint must degrade, never raise -----------


def test_scaffold_rel_returns_none_when_the_registry_import_fails(monkeypatch) -> None:
    """A hint must never change a verdict, so a broken registry import degrades.

    `_scaffold_rel` wraps the import in `except Exception: return None` precisely so
    a consuming repo that does not ship the skill tree still gets a verdict. If this
    raised instead, every validator failure in such a repo would become a crash.
    """

    def boom(_name: str):
        raise ImportError("no registry here")

    monkeypatch.setattr(artifact_validator.importlib, "import_module", boom)
    assert artifact_validator._scaffold_rel("handoff") is None


def test_scaffold_hint_is_none_when_the_scaffold_is_unresolvable(monkeypatch) -> None:
    monkeypatch.setattr(artifact_validator, "_scaffold_rel", lambda _t: None)
    assert artifact_validator.scaffold_hint("handoff") is None


def test_report_validation_failure_still_exits_one_without_a_hint(monkeypatch, capsys) -> None:
    """The exit code is the verdict; the hint is decoration that may be absent."""
    monkeypatch.setattr(artifact_validator, "_scaffold_rel", lambda _t: None)
    assert artifact_validator.report_validation_failure("broken", artifact_type="nope") == 1
    err = capsys.readouterr().err
    assert "broken" in err
    assert "hint:" not in err


def test_scaffold_rel_puts_the_scripts_dir_on_sys_path(monkeypatch) -> None:
    """The `sys.path.insert` guard is what makes the registry importable at all.

    Covers the branch by removing the entry first, so the insert line runs rather
    than being skipped by the `not in sys.path` check.
    """
    scripts_dir = str(Path(artifact_validator.__file__).resolve().parent)
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != scripts_dir])
    # handoff is a registered surface with a real scaffold in this layout.
    assert artifact_validator._scaffold_rel("handoff") is not None
    assert scripts_dir in sys.path


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
    from scripts import changed_line_run_trust as trust

    def boom(*_args, **_kwargs):
        raise subprocess.CalledProcessError(128, ["git"])

    monkeypatch.setattr(trust, "changed_pool_fingerprint", boom)
    monkeypatch.setattr(trust, "_git_lines", lambda *_a, **_k: ["deadbeef"])
    pinned = trust._pin_run_state(tmp_path, "base", "head")
    assert pinned["pool_fingerprint"] == ""
    # The rest of the pin must still be usable, i.e. the failure is contained.
    assert pinned["resolved_head_sha"] == "deadbeef"


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
        "# D\n\n"
        + "\n".join(f"run `python3 scripts/absent{n}.py`" for n in range(5))
        + "\n",
        encoding="utf-8",
    )
    result = _run("scripts/check_doc_links.py", "--repo-root", str(root))
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
    result = _run("scripts/check_doc_links.py", "--repo-root", str(root))
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


def test_preflight_renders_the_unresolved_command_target_row(tmp_path) -> None:
    """The `unresolved-command-target` elif is a distinct human message.

    Built through the real `build_report` rather than a hand-constructed Report, so
    the test cannot drift from the dataclass shape and it exercises the collector
    and the renderer on one path.
    """
    root = tmp_path
    (root / "scripts").mkdir()
    doc = root / "doc.md"
    doc.write_text("# D\n\nrun `python3 scripts/absent.py`\n", encoding="utf-8")
    report = preflight.build_report(root, str(doc), None)
    text = preflight.format_human(report)
    assert "documented command names a missing script `scripts/absent.py`" in text
    assert "placeholder" in text
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
    import record_quality_runtime

    with pytest.raises(FileNotFoundError) as excinfo:
        record_quality_runtime._quality_script_path(tmp_path, "definitely_absent.py")
    assert "definitely_absent.py" in str(excinfo.value)


# --- validate_debug_artifact: empty scope is a no-op, not a failure -----------


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", script, *args], cwd=ROOT, check=False, capture_output=True, text=True
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
        "scripts/validate_debug_artifact.py",
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
    result = _run("scripts/validate_debug_artifact.py", "--repo-root", str(repo), "--all")
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
    report = preflight.build_report(root, str(doc), None)
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


def test_handoff_artifact_path_accepts_a_repo_relative_value(tmp_path) -> None:
    """A relative `--artifact-path` resolves against `--repo-root`.

    Covers the `artifact_path = repo_root / artifact_path` branch, which only runs
    for a non-absolute value and is the ergonomic form an operator would type.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nlanguage: en\noutput_dir: docs\n", encoding="utf-8"
    )
    (repo / "docs" / "handoff.md").write_text("# broken\n", encoding="utf-8")
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    good = "\n".join(
        [
            "# Candidate Handoff",
            "",
            "## Workflow Trigger",
            "",
            "- run it",
            "",
            "## Current State",
            "",
            "- state",
            "",
            "## Next Session",
            "",
            "- next",
            "",
            "## Discuss",
            "",
            "- discuss",
            "",
            "## References",
            "",
            "- [guide](docs/guide.md)",
            "",
        ]
    )
    (repo / "docs" / "candidate.md").write_text(good + "\n", encoding="utf-8")
    result = _run(
        "scripts/validate_handoff_artifact.py",
        "--repo-root",
        str(repo),
        "--artifact-path",
        "docs/candidate.md",  # relative on purpose
    )
    assert result.returncode == 0, result.stderr
    assert "candidate.md" in result.stdout


def test_lesson_that_is_only_a_class_tag_is_skipped(tmp_path) -> None:
    """A bullet whose entire content is the tag must not become an empty lesson.

    Covers the post-strip `continue`: stripping the marker can empty the text, and
    an empty lesson would otherwise be indexed with a blank display string.
    """
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "scripts"))
    import recent_lessons_lib as lib

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
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "scripts"))
    import helper_provenance_lib as lib

    root = tmp_path / "repo"
    root.mkdir()
    marker = root / lib.SOURCE_TREE_MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("{not json", encoding="utf-8")
    assert lib.is_charness_source_tree(root) is False


def test_charness_version_skips_unreadable_and_non_dict_manifests(tmp_path) -> None:
    """Version lookup walks past a corrupt or wrong-shaped manifest to the next one."""
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "scripts"))
    import helper_provenance_lib as lib

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
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "scripts"))
    import argparse_help_probe as probe_module

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
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "scripts"))
    import validate_attention_state_visibility as gate

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
    from scripts import changed_line_run_trust as trust

    def boom(*_args, **_kwargs):
        raise OSError("git not found")

    monkeypatch.setattr(trust, "changed_pool_fingerprint", boom)
    monkeypatch.setattr(trust, "_git_lines", lambda *_a, **_k: ["cafebabe"])

    pinned = trust._pin_run_state(tmp_path, "base", "head")

    assert pinned["pool_fingerprint"] == ""
    assert pinned["resolved_head_sha"] == "cafebabe"
