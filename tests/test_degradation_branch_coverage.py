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
    import check_changed_line_mutation_coverage as gate

    def boom(*_args, **_kwargs):
        raise subprocess.CalledProcessError(128, ["git"])

    monkeypatch.setattr(gate, "changed_pool_fingerprint", boom)
    monkeypatch.setattr(gate, "_git_lines", lambda *_a, **_k: ["deadbeef"])
    pinned = gate._pin_run_state(tmp_path, "base", "head")
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
