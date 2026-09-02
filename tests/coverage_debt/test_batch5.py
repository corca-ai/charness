"""Behaviors on changed-but-unmeasured lines across the pointer, gate, and CLI surfaces.

Every test here names one behavior an operator or a caller depends on. They were
written together because the same closeout range touched all of these files, but each
one stands alone: delete the production branch it names and the test fails with a
message about the behavior, not about a line number.

The `charness` CLI cases load the entrypoint in process (the `test_managed_install`
loader every other CLI test uses) rather than spawning it, because the contract under
test is the payload/refusal the function returns, so the in-process loader is the
smallest honest surface for these cases.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.charness_cli.test_managed_install import load_charness_module
from tests.quality_gates.support import ROOT
from tests.script_main import load_script_module, run_loaded_script_main

# ---------------------------------------------------------------------------
# scripts/refresh_current_pointer.py -- the two "already correct" verdicts
# ---------------------------------------------------------------------------

REFRESH_CURRENT_POINTER = load_script_module(
    "refresh_current_pointer_batch5", ROOT / "scripts" / "refresh_current_pointer.py"
)


def _refresh(repo: Path, record: Path, *extra: str) -> SimpleNamespace:
    return run_loaded_script_main(
        "refresh_current_pointer.py",
        REFRESH_CURRENT_POINTER,
        "--repo-root",
        str(repo),
        "--skill-id",
        "gather",
        "--record-artifact-path",
        f"charness-artifacts/gather/{record.name}",
        *extra,
    )


def _gather_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "gather").mkdir(parents=True)
    return repo


def test_a_copy_pointer_that_already_matches_is_a_noop_and_is_not_rewritten(tmp_path: Path) -> None:
    """Re-running the refresh must not churn a pointer whose bytes already match.

    The pointer is what other sessions read as "the current asset". Reporting
    `updated` for a run that changed nothing would make every closeout look like it
    moved the pointer, and rewriting the file would bump its mtime for downstream
    staleness checks that have no reason to fire. The `noop` verdict is the one
    signal that says "already correct" as distinct from "just fixed".
    """
    repo = _gather_repo(tmp_path)
    gather = repo / "charness-artifacts" / "gather"
    record = gather / "2026-05-10-record.md"
    record.write_text("# Gathered\n\nBody.\n", encoding="utf-8")
    pointer = gather / "latest.md"
    pointer.write_text("# Gathered\n\nBody.\n", encoding="utf-8")
    before = pointer.stat().st_mtime_ns

    result = _refresh(repo, record, "--execute")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "noop"
    assert payload["would_update"] is False
    assert "already matches" in payload["reason"]
    assert pointer.stat().st_mtime_ns == before, "a matching pointer was rewritten anyway"

    # Falsifiable counterpart: different bytes are still a real update, so the noop
    # above is about equality and not about the copy writer being dead.
    record.write_text("# Gathered\n\nDifferent body.\n", encoding="utf-8")
    updated = _refresh(repo, record, "--execute")
    assert yaml.safe_load(updated.stdout)["status"] == "updated"
    assert pointer.read_text(encoding="utf-8") == "# Gathered\n\nDifferent body.\n"


def test_a_symlink_pointer_already_aimed_at_the_record_is_a_noop_and_keeps_its_link(
    tmp_path: Path,
) -> None:
    """An idempotent re-run must not unlink and recreate a correct symlink.

    `_write_symlink` unlinks before it relinks. If "already pointing there" were
    treated as an update, a concurrent reader could observe the pointer as absent
    for a window, and the payload would claim a change nobody made.
    """
    repo = _gather_repo(tmp_path)
    gather = repo / "charness-artifacts" / "gather"
    record = gather / "2026-05-10-record.md"
    record.write_text("# Gathered\n\nBody.\n", encoding="utf-8")
    pointer = gather / "latest.md"
    pointer.symlink_to(record.name)

    result = _refresh(repo, record, "--execute")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "noop"
    assert payload["would_update"] is False
    assert "already targets" in payload["reason"]
    assert payload["strategy"] == "symlink"
    assert os.readlink(pointer) == record.name

    # Falsifiable counterpart: a DIFFERENT record still repoints the symlink.
    other = gather / "2026-05-11-other.md"
    other.write_text("# Other\n", encoding="utf-8")
    moved = _refresh(repo, other, "--execute")
    assert yaml.safe_load(moved.stdout)["status"] == "updated"
    assert os.readlink(pointer) == other.name


# ---------------------------------------------------------------------------
# scripts/check_seed_fixture_budget.py -- the exported-layout import fallback
# ---------------------------------------------------------------------------


def test_the_seed_budget_gate_still_finds_its_emitter_without_the_scripts_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The gate must import in the flattened export, where `scripts.` is not a package.

    This repo keeps the gate under `scripts/`, so `from scripts.yaml_output import
    emit_yaml` resolves; the exported plugin copy flattens the tree and that import
    raises. Without the bare-name fallback the gate would die at import time in every
    consuming install -- a gate that cannot load is a gate that never blocks, which is
    the same fail-open shape `classify_scan` exists to refuse.
    """
    # Both deletions are what makes the flattened layout real: with only `scripts`
    # blanked, an ALREADY-CACHED `scripts.yaml_output` would still satisfy the first
    # import and the fallback would never be reached.
    monkeypatch.setitem(sys.modules, "scripts", None)
    monkeypatch.delitem(sys.modules, "scripts.yaml_output", raising=False)
    monkeypatch.delitem(sys.modules, "check_seed_fixture_budget_flat_layout", raising=False)

    path = ROOT / "scripts" / "check_seed_fixture_budget.py"
    module = load_script_module("check_seed_fixture_budget_flat_layout", path)

    # Loaded is not enough: the name it bound has to be a live emitter, so the gate
    # can still produce the one YAML document its runner parses.
    monkeypatch.setattr(
        module,
        "_load_inventory",
        lambda: SimpleNamespace(
            _pytest_temp_footprint_quick=lambda: {"status": "available", "total_disk_bytes": 0}
        ),
    )
    result = run_loaded_script_main(
        "check_seed_fixture_budget.py", module, "--repo-root", str(ROOT)
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["scope_classification"] == "scanned"
    assert payload["breaches"] == []


# ---------------------------------------------------------------------------
# scripts/build_debug_seam_risk_index.py -- the --check and bare verdicts
# ---------------------------------------------------------------------------

DEBUG_SEAM_INDEX = load_script_module(
    "build_debug_seam_risk_index_batch5", ROOT / "scripts" / "build_debug_seam_risk_index.py"
)


def _seam_repo(tmp_path: Path) -> Path:
    from tests.quality_gates.test_debug_seam_risk_index import debug_artifact, seed_repo

    return seed_repo(tmp_path, ("2026-04-22-host-seam.md", debug_artifact()))


def _seam_index(repo: Path, *args: str) -> SimpleNamespace:
    return run_loaded_script_main(
        "build_debug_seam_risk_index.py",
        DEBUG_SEAM_INDEX,
        "--repo-root",
        str(repo),
        *args,
        cli_error_types=(DEBUG_SEAM_INDEX.ValidationError,),
    )


def test_check_reports_a_validated_index_and_names_the_file_it_validated(tmp_path: Path) -> None:
    """`--check` must say WHICH verdict it reached, not just exit 0.

    `--write` and `--check` emit the same payload shape; `status` is the only field
    separating "this run rewrote the index" from "this run only agreed with it".
    A `--check` arm that emitted nothing (or emitted `written`) would let a stale
    index pass a closeout review that reads the receipt rather than the diff.
    """
    repo = _seam_repo(tmp_path)
    written = _seam_index(repo, "--write")
    assert written.returncode == 0, written.stderr
    written_payload = yaml.safe_load(written.stdout)
    assert written_payload["status"] == "written"

    checked = _seam_index(repo, "--check")

    assert checked.returncode == 0, checked.stderr
    payload = yaml.safe_load(checked.stdout)
    assert payload["status"] == "validated"
    assert payload["index_path"] == written_payload["index_path"]
    assert (repo / payload["index_path"]).is_file()
    assert payload["indexed_artifact_count"] == written_payload["indexed_artifact_count"]
    assert payload["source_artifact_count"] == written_payload["source_artifact_count"]

    # Falsifiable counterpart: a drifted index is refused rather than validated.
    (repo / payload["index_path"]).write_text("# stale\n", encoding="utf-8")
    stale = _seam_index(repo, "--check")
    assert stale.returncode == 1
    assert "stale" in stale.stderr


def test_the_bare_invocation_emits_the_derived_index_without_touching_the_tree(
    tmp_path: Path,
) -> None:
    """With neither `--write` nor `--check` this is a read-only derivation.

    That is the mode a reviewer uses to see what the index WOULD say without
    mutating a tracked artifact mid-review. If the default arm wrote, inspecting
    the index would dirty the worktree it was inspecting.
    """
    repo = _seam_repo(tmp_path)
    index_dir = repo / "charness-artifacts" / "debug"
    before = sorted(path.name for path in index_dir.iterdir())

    result = _seam_index(repo)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["indexed_artifact_count"] >= 1
    assert "status" not in payload, "the read-only arm must not claim a write verdict"
    assert sorted(path.name for path in index_dir.iterdir()) == before


# ---------------------------------------------------------------------------
# scripts/lesson_score_outcome_lib.py -- three refusals on the score vocabulary
# ---------------------------------------------------------------------------


def test_a_non_object_score_event_has_no_outcome_rather_than_exploding() -> None:
    """`outcome_of` is called on unvalidated ledger JSON, so it must tolerate junk.

    `_replay_scores` reads events straight out of a hand-edited append-only file.
    If a stray scalar made `outcome_of` raise, the ledger validator would crash with
    an AttributeError instead of emitting its own "score event N is not an object"
    refusal, and the author would get no idea which event to fix.
    """
    from scripts import lesson_score_outcome_lib as outcome_lib

    for junk in ("changed-an-action", ["changed-an-action"], 3, None):
        assert outcome_lib.outcome_of(junk) is None
    # And it is not simply always None: a real event still reports its outcome.
    assert outcome_lib.outcome_of({"outcome": "not-consulted"}) == "not-consulted"


def test_a_retro_citation_that_is_not_a_clean_string_is_refused() -> None:
    """A citation is permanent once committed, so a padded or non-string one is refused.

    The ledger refuses to rewrite a score event, so `charness-artifacts/retro/x.md `
    with a trailing space becomes an unclearable gate: the reconciler looks for a
    retro at a path that does not exist and no later commit may repair the event.
    Refusing at write time is the only moment the mistake is cheap.
    """
    from scripts import lesson_score_outcome_lib as outcome_lib

    for bad in (
        None,
        7,
        ["charness-artifacts/retro/x.md"],
        "",
        "   ",
        " charness-artifacts/retro/x.md",
        "charness-artifacts/retro/x.md ",
        "charness-artifacts/retro/x.md\n",
    ):
        assert outcome_lib.canonical_retro_citation(bad) is False, bad
    assert outcome_lib.canonical_retro_citation("charness-artifacts/retro/x.md") is True


def test_an_unknown_outcome_word_is_refused_and_the_message_lists_the_vocabulary() -> None:
    """The refusal must name the four legal words, because the author is guessing.

    `outcome` is a closed vocabulary whose values each route to a different
    disposition. A refusal that only said "invalid outcome" would leave the author to
    grep the library for the spellings; naming them is what makes the shape check
    self-teaching at the one moment the author still remembers the encounter.
    """
    from scripts import lesson_score_outcome_lib as outcome_lib

    event = {
        "event_id": "e1",
        "source_retro": "charness-artifacts/retro/x.md",
        "lesson_id": "a",
        "outcome": "helped-a-bit",
        "anchor": "I would have gone elsewhere otherwise",
    }

    error = outcome_lib.score_event_error(event)

    assert error is not None
    for word in outcome_lib.SCORE_OUTCOMES:
        assert word in error
    # Falsifiable counterpart: the same event with a legal word validates, so the
    # refusal is about the vocabulary and not about the rest of the shape.
    assert outcome_lib.score_event_error({**event, "outcome": "changed-an-action"}) is None


def test_a_score_for_a_lesson_no_transition_ever_seeded_is_refused() -> None:
    """The replay must not credit a lesson that was never seeded.

    `lessons[...]` is rebuilt by replaying transitions. A score naming an id with no
    seeding transition would either KeyError during aggregation or silently
    manufacture a lesson row that no retro ever declared. This guard is defence in
    depth -- see the note in the module report -- so it is exercised at its own
    contract rather than through the full validator.
    """
    from scripts import lesson_ledger_lib as ledger_lib

    event = {
        "event_id": "e1",
        "source_retro": "charness-artifacts/retro/x.md",
        "lesson_id": "ghost",
        "outcome": "read-but-not-applied",
        "anchor": "it was open in the editor at the decision",
    }

    with pytest.raises(ValueError) as caught:
        ledger_lib._replay_scores([event], {}, {})

    assert "unseeded lesson" in str(caught.value)
    assert "e1" in str(caught.value)


# ---------------------------------------------------------------------------
# scripts/check_premise_preflight.py -- reason codes on a decision-level refusal
# ---------------------------------------------------------------------------

PREMISE_CLI = load_script_module(
    "check_premise_preflight_batch5", ROOT / "scripts" / "check_premise_preflight.py"
)


def test_a_stale_premise_refusal_lifts_its_reason_codes_onto_the_payload(tmp_path: Path) -> None:
    """A refusal the DECISION produced must surface its reason codes at the top level.

    A `PremiseError` refusal carries an `error` block; a decision-level refusal does
    not, and its reason codes sit one level down under `decision`. The operator
    reading the emitted document needs the same "why" in the same place for both, or
    a stale-issue refusal looks like a refusal with no stated cause.
    """
    from tests.quality_gates.test_premise_preflight import _seed, _write_issue

    repo, premise, issue, _ = _seed(tmp_path)
    original = json.loads(issue.read_text(encoding="utf-8"))
    _write_issue(issue, original, body="changed body\n")

    result = run_loaded_script_main(
        "check_premise_preflight.py",
        PREMISE_CLI,
        "--repo-root",
        str(repo),
        "--premise",
        str(premise),
        "--issue-readback",
        str(issue),
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "refused"
    assert "error" not in payload
    assert payload["refusal_detail"]["reason_codes"] == ["stale_issue"]
    assert payload["decision"]["reason_codes"] == ["stale_issue"]


# ---------------------------------------------------------------------------
# skills/public/issue/scripts/audit_brief.py -- shape error, verdict, and counts
# ---------------------------------------------------------------------------

AUDIT_BRIEF = load_script_module(
    "audit_brief_batch5", ROOT / "skills" / "public" / "issue" / "scripts" / "audit_brief.py"
)


def test_an_unreadable_transcript_is_exit_two_with_no_fix_unit_count(tmp_path: Path) -> None:
    """A transcript that could not be read must be distinguishable from a clean audit.

    Exit 2 (not 1) says "this run judged nothing", and `fix_unit_count` is absent on
    purpose: a `0` there reads as "zero fix units, all clean", which is exactly the
    absent-input-certifies-itself shape this checker exists to catch.
    """
    transcript = tmp_path / "transcript.json"
    transcript.write_text('{"events": []}', encoding="utf-8")

    result = run_loaded_script_main("audit_brief.py", AUDIT_BRIEF, "--transcript", str(transcript))

    assert result.returncode == 2
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "nothing to audit" in payload["error"]
    assert payload["transcript"] == str(transcript)
    assert "fix_unit_count" not in payload


def test_a_readable_transcript_reports_both_counts_beside_its_verdict(tmp_path: Path) -> None:
    """The reader must learn HOW MUCH was judged without length-counting nested maps.

    `fix_unit_count` and `violation_count` are the two numbers the deleted text lines
    carried. Without them a reader has to walk two nested collections to tell a
    one-issue audit from a twenty-issue one, and `ok: false` alone never says how
    much of the transcript was clean.
    """
    transcript = tmp_path / "transcript.json"
    transcript.write_text(
        json.dumps(
            {
                "events": [
                    {"kind": "classification", "issue": 143, "classification": "bug"},
                    {"kind": "mutation", "issue": 143, "tool": "Edit"},
                    {"kind": "close", "issue": 143},
                    {"kind": "mutation", "issue": 144, "tool": "Edit"},
                    {"kind": "close", "issue": 144},
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_loaded_script_main("audit_brief.py", AUDIT_BRIEF, "--transcript", str(transcript))

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert payload["fix_unit_count"] == 2 == len(payload["fix_units"])
    assert payload["violation_count"] == len(payload["violations"]) >= 1
    # 143 was classified before its mutation; 144 was not, and only 144 is flagged.
    assert {violation["issue"] for violation in payload["violations"]} == {144}
    assert payload["transcript"] == str(transcript)


def test_the_issue_audit_names_its_missing_bootstrap_instead_of_dying_on_none(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A skill script copied out of its tree must say WHAT it could not find.

    These scripts locate `skill_runtime_bootstrap.py` by walking their own ancestors.
    Outside a charness tree the walk finds nothing, and without this raise the next
    line would fail with `AttributeError: 'NoneType'` -- a message that names neither
    the missing file nor the fact that the script was run from the wrong place.
    """
    monkeypatch.setattr(AUDIT_BRIEF, "__file__", str(tmp_path / "elsewhere" / "audit_brief.py"))

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        AUDIT_BRIEF._load_skill_runtime_bootstrap()


# ---------------------------------------------------------------------------
# skills/public/release/scripts/release_claim_surfaces.py
# ---------------------------------------------------------------------------

CLAIM_SURFACES = load_script_module(
    "release_claim_surfaces_batch5",
    ROOT / "skills" / "public" / "release" / "scripts" / "release_claim_surfaces.py",
)


def test_the_release_surface_registry_names_its_missing_bootstrap(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Same contract as the issue script, at the surface release notes are checked with.

    A release-time import failure that said only `'NoneType' has no attribute` would
    read as a broken release tool rather than as "this file is not inside a charness
    checkout", and the operator would debug the wrong thing while a publish is held.
    """
    monkeypatch.setattr(
        CLAIM_SURFACES, "__file__", str(tmp_path / "elsewhere" / "release_claim_surfaces.py")
    )

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        CLAIM_SURFACES._load_skill_runtime_bootstrap()


def test_a_path_outside_the_scanned_root_is_reported_absolute_rather_than_mangled(
    tmp_path: Path,
) -> None:
    """A derived item must stay identifiable when it does not live under `repo_root`.

    `_rel` renders every derived item for the note comparison. A path outside the
    root has no relative spelling, and `Path.relative_to` raises rather than
    returning one. Falling back to the absolute path keeps the item quotable; a
    swallowed error here would print an empty or truncated name in a release note.
    """
    outside = tmp_path / "outside" / "thing.py"

    assert CLAIM_SURFACES._rel(tmp_path / "repo", outside) == str(outside)
    inside = tmp_path / "repo" / "scripts" / "thing.py"
    assert CLAIM_SURFACES._rel(tmp_path / "repo", inside) == "scripts/thing.py"


def test_an_unparseable_cli_entrypoint_yields_no_subcommands_and_says_why(
    tmp_path: Path,
) -> None:
    """A `charness` file that will not parse must declare the blind spot, not report zero.

    Reporting `count: 0` for a file the derivation could not read is the exact
    over-claim this whole mechanism refuses: a release note would then truthfully
    match a derivation that measured nothing. The empty list has to arrive with the
    reason attached.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "charness").write_text("def main(:\n", encoding="utf-8")

    names, unscanned = CLAIM_SURFACES._charness_subcommands(repo, require_git=False)

    assert names == []
    assert unscanned == ["`charness` did not parse, so no subcommand was derived from it"]

    # Falsifiable counterpart: a parseable entrypoint derives its top-level names and
    # declares no extra blind spot, so the branch above is about the parse failure.
    (repo / "charness").write_text(
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "subparsers = parser.add_subparsers()\n"
        "subparsers.add_parser('doctor')\n"
        "task = subparsers.add_parser('task')\n"
        "task_subparsers = task.add_subparsers()\n"
        "task_subparsers.add_parser('claim')\n",
        encoding="utf-8",
    )
    names, unscanned = CLAIM_SURFACES._charness_subcommands(repo, require_git=False)
    assert names == ["doctor", "task"], "nested groups must not flatten into the top level"
    assert unscanned == []


def test_the_items_field_renders_a_quotable_list_and_says_none_when_empty() -> None:
    """A release note quoting `items` needs a rendering that reads as prose.

    An empty surface rendered as `""` would be indistinguishable from a missing
    field in the note comparison, so an author could "match" the derivation by
    writing nothing at all. `(none)` is a value a note has to state on purpose.
    """
    derived = {"count": 2, "items": ["alpha", "beta"]}

    assert CLAIM_SURFACES.surface_field(derived, "items") == "alpha, beta"
    assert CLAIM_SURFACES.surface_field({"count": 0, "items": []}, "items") == "(none)"
    assert CLAIM_SURFACES.surface_field(derived, "count") == "2"
    assert CLAIM_SURFACES.surface_field(derived, "questions") is None


# ---------------------------------------------------------------------------
# skills/public/quality/scripts/check_standing_doc_provenance.py -- the ok verdict
# ---------------------------------------------------------------------------


def test_a_clean_scan_reports_how_many_standing_docs_it_actually_read(tmp_path: Path) -> None:
    """`ok: true` from a real scan must be distinguishable from `ok: true` from no scan.

    `inert` (nobody configured standing docs) and `ok` (docs were read and none
    drifted) are the same exit code and the same `ok` byte. The scanned COUNT is the
    only thing in the payload that tells a reviewer whether the check looked at
    anything, which is what stops an emptied `standing_docs` list from reading as a
    passing gate.
    """
    from tests.quality_gates.test_standing_doc_provenance import (
        CHECKER,
        STANDARD_BLOCK,
        _seed_repo,
        _write,
    )

    repo = _seed_repo(tmp_path, adapter_block=STANDARD_BLOCK)
    _write(
        repo / "docs" / "operating-rules.md",
        ["# Operating Rules", "", "Sync the mirror before validators.", "Prefer deleting drift."],
    )

    result = run_loaded_script_main(
        "check_standing_doc_provenance.py", CHECKER, "--repo-root", str(repo)
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is True
    assert payload["inert"] is False
    assert payload["verdict"] == "ok"
    assert len(payload["scanned"]) == 1
    assert payload["verdict_detail"].startswith("1 standing doc(s) scanned")
    assert "remedy" not in payload, "a clean run must not carry a repair instruction"


# ---------------------------------------------------------------------------
# charness -- payload parsing at two call sites, and the tool-install argv
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def charness_cli():
    return load_charness_module("charness_batch5_under_test")


def _script_repo(tmp_path: Path, name: str, source: str) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    (repo / name).write_text(source, encoding="utf-8")
    return repo


UNREADABLE_PAYLOAD_SCRIPT = (
    "import sys\nprint('a: [1,\\n  b: {')\nprint('cannot reach the ledger', file=sys.stderr)\n"
)


def test_an_unreadable_repo_script_payload_names_the_repo_and_the_child_stderr(
    charness_cli, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The parse refusal alone does not say WHICH checkout produced it.

    `invoke_repo_json_script` is called against a managed checkout the operator did
    not choose and may not know the path of. The bare parse error names only the
    script, so without this re-raise the operator sees an unreadable payload with no
    way to find the tree that emitted it, and the child's own diagnostic -- which is
    usually the real cause -- is discarded with the CompletedProcess.
    """
    repo = _script_repo(tmp_path, "emit.py", UNREADABLE_PAYLOAD_SCRIPT)
    monkeypatch.setattr(charness_cli, "resolve_repo_python", lambda _root: sys.executable)

    with pytest.raises(charness_cli.CharnessError) as caught:
        charness_cli.invoke_repo_json_script(repo, "emit.py")

    message = str(caught.value)
    assert "did not return a readable YAML payload" in message
    assert f"REPO ROOT: {repo}" in message
    assert "cannot reach the ledger" in message

    # Falsifiable counterpart: a readable payload comes back parsed, so the wrapper
    # is refusing bad output rather than refusing everything.
    ok_repo = _script_repo(tmp_path / "ok", "emit.py", "print('status: fine')\n")
    assert charness_cli.invoke_repo_json_script(ok_repo, "emit.py") == {"status": "fine"}


def test_the_repair_command_runner_carries_the_same_repo_and_stderr_context(
    charness_cli, tmp_path: Path
) -> None:
    """The repair path needs the same diagnosis, and it is a SECOND copy of the wrapper.

    `_run_repo_json_command` builds its own argv rather than going through
    `invoke_repo_json_script`, so it does not inherit that wrapper. A repair run that
    lost the repo root and the guard's stderr would leave an operator holding a parse
    error about a command they cannot locate.
    """
    repo = _script_repo(tmp_path, "guard.py", UNREADABLE_PAYLOAD_SCRIPT)

    with pytest.raises(charness_cli.CharnessError) as caught:
        charness_cli._run_repo_json_command(repo, [sys.executable, "guard.py"])

    message = str(caught.value)
    assert f"REPO ROOT: {repo}" in message
    assert "cannot reach the ledger" in message

    # Falsifiable counterpart: a readable payload returns with its exit code and
    # stderr instead of raising.
    ok_repo = _script_repo(
        tmp_path / "ok",
        "guard.py",
        "import sys\nprint('cleaned: 2')\nprint('note', file=sys.stderr)\nsys.exit(3)\n",
    )
    payload, code, stderr = charness_cli._run_repo_json_command(
        ok_repo, [sys.executable, "guard.py"]
    )
    assert (payload, code) == ({"cleaned": 2}, 3)
    assert "note" in stderr


def test_tool_install_hands_sync_support_the_plugin_root_and_the_selected_tools(
    charness_cli, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    """Support rematerialization is scoped by the SAME tool ids the install used.

    `sync_support.py` writes into the plugin root, so it needs both roots and the
    selected ids; an install that forwarded neither would rematerialize every tool's
    support skill (or none) regardless of what was installed. `--execute` must also
    track `--dry-run`, or a planning run would write support skills to disk.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    plugin_root = tmp_path / "plugins"
    monkeypatch.setattr(charness_cli, "resolve_tool_repo_root", lambda _args: (repo, False))
    calls: dict[str, tuple[str, ...]] = {}

    def fake_invoke(_repo_root, script, *script_args, allow_failure=False):
        calls[script] = script_args
        return []

    monkeypatch.setattr(charness_cli, "invoke_repo_json_script", fake_invoke)
    parser = charness_cli.build_parser()

    args = parser.parse_args(
        [
            "tool",
            "install",
            "demo-tool",
            "--repo-root",
            str(repo),
            "--plugin-root",
            str(plugin_root),
        ]
    )
    assert charness_cli.cmd_tool_install(args) == 0
    capsys.readouterr()

    assert calls["scripts/sync_support.py"] == (
        "--repo-root",
        str(repo),
        "--plugin-root",
        str(plugin_root),
        "--tool-id",
        "demo-tool",
        "--execute",
    )

    # `--dry-run` drops `--execute` from the SAME argv, and `--skip-sync-support`
    # removes the call entirely -- the two ways this branch is meant to be avoided.
    calls.clear()
    dry = parser.parse_args(
        [
            "tool",
            "install",
            "demo-tool",
            "--repo-root",
            str(repo),
            "--plugin-root",
            str(plugin_root),
            "--dry-run",
        ]
    )
    assert charness_cli.cmd_tool_install(dry) == 0
    capsys.readouterr()
    assert "--execute" not in calls["scripts/sync_support.py"]

    calls.clear()
    skipped = parser.parse_args(
        [
            "tool",
            "install",
            "demo-tool",
            "--repo-root",
            str(repo),
            "--plugin-root",
            str(plugin_root),
            "--skip-sync-support",
        ]
    )
    assert charness_cli.cmd_tool_install(skipped) == 0
    capsys.readouterr()
    assert "scripts/sync_support.py" not in calls
