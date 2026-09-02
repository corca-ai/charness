"""Closeout authorization: who may close #514/#515/#518, through which carrier.

The tests are organised around the ways a close reaches GitHub *without* passing the
strictness someone thought they had installed: through a different carrier, through a
carrier that also closes something else, through a repository that merely looks like
this one, or through a matrix that does not yet exist. Each is a real path in this
repo, not a hypothetical.
"""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.evidence.evidence_boundary_crosswalk import (
    CrosswalkError,
    authorize_closeout,
    load_crosswalk,
    normalize_target,
    verify_frozen_source,
)
from scripts.evidence.evidence_boundary_crosswalk import main as crosswalk_main
from scripts.gates.validate_evidence_boundary_crosswalk import main as validate_main
from scripts.gates.validate_evidence_boundary_crosswalk import run as validate_crosswalk
from scripts.issue.issue_source_capture_lib import build_snapshot_and_receipt, capture_issues
from scripts.issue.validate_issue_source_freeze import run_freeze, stamp_inspection

REPO_ROOT = Path(__file__).resolve().parent.parent
CROSSWALK_REL = "spec/crosswalk.json"
SNAPSHOT_REL = "spec/source.json"
INSPECTION_REL = "spec/inspection.json"
FREEZE_REL = "spec/freeze.json"
PROTECTED = (514, 515, 518)
CAPABILITY = {
    "enumeration": "cursor", "page_size": 2, "has_next_field": "hasNextPage",
    "cursor_field": "endCursor", "total_count_field": "totalCount",
    "normalization": "github-issue-v1", "declared": False,
}


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _freeze_world(tmp_path: Path) -> dict:
    """A real frozen source, not a stub: the crosswalk binds to freeze identities and
    the validator resolves clause ids against the actual inventory."""
    queue = [
        json.dumps(
            {
                "data": {"repository": {"issue": {
                    "number": number, "title": f"i{number}",
                    "body": f"- first criterion for {number}\n- second criterion for {number}",
                    "state": "OPEN", "url": "u",
                    "comments": {"totalCount": 0, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": []},
                }}}
            }
        )
        for number in PROTECTED
    ]
    captured = capture_issues(
        repo="corca-ai/charness", numbers=list(PROTECTED),
        backend={"id": "gh", "binary": "gh", "commands": None}, capability=CAPABILITY,
        runner=lambda argv: subprocess.CompletedProcess(argv, 0, queue.pop(0), ""),
    )
    snapshot, receipt, raw_files = build_snapshot_and_receipt(
        repo="corca-ai/charness", numbers=list(PROTECTED),
        adapter={"path": "a", "found": True, "data": {"issue_backend": {"id": "gh"}}},
        capability=CAPABILITY, captured=captured, raw_dir_rel="spec/source-raw",
    )
    for rel, text in raw_files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _write_json(tmp_path / SNAPSHOT_REL, snapshot)
    _write_json(tmp_path / "spec/source-capture-receipt.json", receipt)
    (tmp_path / "owner.py").write_text("# owner\n", encoding="utf-8")
    _write_json(
        tmp_path / INSPECTION_REL,
        {"schema": "issue-source-owner-inspection/v2", "issues": list(PROTECTED),
         "locators": [{"role": "owner", "path": "owner.py", "note": "n"}], "inspection_identity": ""},
    )
    stamp_inspection(tmp_path, INSPECTION_REL)
    run_freeze(tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, list(PROTECTED))
    return json.loads((tmp_path / FREEZE_REL).read_text(encoding="utf-8"))


def _ensure_world(tmp_path: Path) -> dict:
    """Build the freeze world once; `_complete_rows` needs it before `_crosswalk` runs."""
    if not (tmp_path / FREEZE_REL).is_file():
        return _freeze_world(tmp_path)
    return json.loads((tmp_path / FREEZE_REL).read_text(encoding="utf-8"))


def _crosswalk(tmp_path: Path, *, state="bootstrap", rows=None) -> dict:
    freeze = _ensure_world(tmp_path)
    payload = {
        "schema": "evidence-boundary-crosswalk/v1",
        "matrix_state": state,
        "current_repository": "corca-ai/charness",
        "protected_issues": list(PROTECTED),
        "source_identity": {
            "snapshot_path": SNAPSHOT_REL,
            "freeze_receipt_path": FREEZE_REL,
            "source_snapshot_sha256": freeze["source_snapshot_sha256"],
            "clause_inventory_identity": freeze["clause_inventory_identity"],
            "reviewed_input_identity": freeze["reviewed_input_identity"],
            "freeze_identity": freeze["freeze_identity"],
        },
        "shared_projection": {"status": "undecided" if state == "bootstrap" else "no-shared-artifact"},
        "issues": rows if rows is not None else [
            {"number": number, "owner": "Charness-owned", "projection_dependency": "undecided",
             "criteria": [], "coverage": [], "source_clauses": []}
            for number in PROTECTED
        ],
    }
    _write_json(tmp_path / CROSSWALK_REL, payload)
    return payload


def _complete_rows(tmp_path: Path, *, owner="Charness-owned", dependency="local-consumer") -> list[dict]:
    """Rows that satisfy the complete-state floor, derived from the real clause ids."""
    _ensure_world(tmp_path)
    snapshot = json.loads((tmp_path / SNAPSHOT_REL).read_text(encoding="utf-8"))
    rows = []
    for issue in snapshot["clause_inventory"]["issues"]:
        clause_ids = [clause["source_clause_id"] for unit in issue["source_units"] for clause in unit["clauses"]]
        rows.append(
            {
                "number": issue["number"], "owner": owner, "projection_dependency": dependency,
                "source_clauses": [{"source_clause_id": cid, "disposition": "criterion"} for cid in clause_ids],
                "criteria": [
                    {"criterion_id": f"C{issue['number']}", "source_clause_ids": clause_ids,
                     "coverage_ids": [f"V{issue['number']}"], "producer": "p", "invocation": "i",
                     "expected": "e", "artifact_path": "a", "final_reader_route": "r", "non_claim": "n"}
                ],
                "coverage": [{"coverage_id": f"V{issue['number']}", "criterion_ids": [f"C{issue['number']}"], "shared": False}],
            }
        )
    return rows


def _authorize(tmp_path: Path, invoked, carrier, source="commit-msg"):
    return authorize_closeout(invoked, carrier, source, repo_root=tmp_path, crosswalk_path=CROSSWALK_REL)


def _patch_crosswalk(tmp_path: Path, mutate) -> dict:
    """Edit the written crosswalk the way a hand-edit of the artifact would."""
    path = tmp_path / CROSSWALK_REL
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    _write_json(path, payload)
    return payload


def _run_cli(main, monkeypatch, capsys, *argv: str):
    """Drive one entrypoint IN PROCESS, the way an operator drives it from a shell."""
    monkeypatch.setattr(sys, "argv", ["x", *argv])
    code = main()
    captured = capsys.readouterr()
    return code, captured


# --- target normalization -------------------------------------------------


def test_an_unqualified_ref_resolves_only_against_the_declared_current_repo() -> None:
    assert normalize_target("#514", "corca-ai/charness")["repository"] == "corca-ai/charness"
    assert normalize_target(514, "corca-ai/charness")["issue_number"] == 514


def test_a_qualified_ref_keeps_its_own_repository_and_is_never_rewritten() -> None:
    """The asymmetry that makes a foreign ref refusable rather than absorbed."""
    target = normalize_target("other-org/other-repo#514", "corca-ai/charness")

    assert target["repository"] == "other-org/other-repo"


def test_an_unreadable_target_raises_rather_than_defaulting() -> None:
    with pytest.raises(CrosswalkError) as excinfo:
        normalize_target("not-a-ref", "corca-ai/charness")

    assert excinfo.value.code == "unparsable_target"


def test_a_repo_number_pair_keeps_the_repository_it_names() -> None:
    """The `(repository, number)` shape callers already build must obey the same
    asymmetry as a qualified string: a foreign repo in the pair stays foreign, so it
    can be refused instead of being absorbed into this repo's protected target."""
    foreign = normalize_target(("other-org/other-repo", 514), "corca-ai/charness")
    local = normalize_target((None, 514), "corca-ai/charness")

    assert foreign == {"repository": "other-org/other-repo", "issue_number": 514, "source": "unknown"}
    assert local == {"repository": "corca-ai/charness", "issue_number": 514, "source": "unknown"}


@pytest.mark.parametrize("target", [None, 514.0, ("corca-ai/charness", 514, "extra"), []])
def test_a_target_of_an_unsupported_type_is_refused_rather_than_coerced(target) -> None:
    """No silent default. A shape this function does not understand must not become
    "the current repo's issue 0" or be dropped on the floor: an unreadable target that
    normalizes to nothing is a protected close that never appears in the aggregate."""
    with pytest.raises(CrosswalkError) as excinfo:
        normalize_target(target, "corca-ai/charness")

    assert excinfo.value.code == "unparsable_target"


@pytest.mark.parametrize("number", ["514", None, 51.4])
def test_a_non_integer_issue_number_is_refused(number) -> None:
    """The typed floor behind the gate.

    Protected issue numbers are compared as `int`s, so a target carrying `"514"` would
    match nothing and fall through the generic pass-through. Refusing here is what
    stops a quoted number in a dict-shaped target from disarming the gate silently.
    """
    with pytest.raises(CrosswalkError) as excinfo:
        normalize_target({"issue_number": number}, "corca-ai/charness")

    assert excinfo.value.code == "unparsable_target"


# --- scope: protected vs everything else ----------------------------------


def test_an_unrelated_issue_close_is_untouched_generic_pass_through(tmp_path: Path) -> None:
    """This gate adds teeth for three issues; it must not become a global floor.

    If every close in the repo suddenly needed a crosswalk row, the gate would be
    removed within a day and the three issues would lose their protection with it.
    """
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, [999], [999])

    assert result["applies"] is False
    assert result["authorized"] is True


def test_a_missing_crosswalk_passes_generic_closes_but_reports_its_absence(tmp_path: Path) -> None:
    result = _authorize(tmp_path, [999], [999])

    assert result["applies"] is False
    assert result["authorized"] is True
    assert result["crosswalk_status"] == "crosswalk_missing"


def test_an_unparsable_crosswalk_file_is_reported_as_invalid_not_as_absent(tmp_path: Path) -> None:
    """A truncated or half-written artifact must be NAMED.

    Collapsing it into "missing" would let a corrupted crosswalk read like a repo that
    simply has no gate installed, and the operator would never learn the file on disk
    is the problem.
    """
    path = tmp_path / CROSSWALK_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"schema": "evidence-boundary-crossw', encoding="utf-8")

    with pytest.raises(CrosswalkError) as excinfo:
        load_crosswalk(tmp_path, CROSSWALK_REL)
    assert excinfo.value.code == "crosswalk_invalid"
    assert _authorize(tmp_path, [999], [999])["crosswalk_status"] == "crosswalk_invalid"


def test_a_crosswalk_declaring_another_schema_is_not_read_as_this_one(tmp_path: Path) -> None:
    """Some other JSON file pointed at this flag must not be interpreted as a
    crosswalk; a schema mismatch is how a wrong `--crosswalk` path gets caught instead
    of being read as an empty protected set that protects nothing."""
    _crosswalk(tmp_path)
    _patch_crosswalk(tmp_path, lambda payload: payload.__setitem__("schema", "something-else/v1"))

    with pytest.raises(CrosswalkError) as excinfo:
        load_crosswalk(tmp_path, CROSSWALK_REL)

    assert excinfo.value.code == "crosswalk_invalid"


def test_a_crosswalk_naming_no_freeze_receipt_cannot_prove_its_source(tmp_path: Path) -> None:
    """Dropping the receipt path is the cheapest way to make the staleness check
    vacuous, so its absence is itself a `stale_source` refusal rather than a skip."""
    crosswalk = _crosswalk(tmp_path)
    crosswalk["source_identity"].pop("freeze_receipt_path")

    with pytest.raises(CrosswalkError) as excinfo:
        verify_frozen_source(tmp_path, crosswalk)

    assert excinfo.value.code == "stale_source"


def test_a_freeze_receipt_that_cannot_be_loaded_is_a_stale_source_refusal(tmp_path: Path) -> None:
    """A receipt path that does not resolve carries the freeze library's own detail up
    as `stale_source`: an unreadable receipt proves nothing, and must not be softer
    than a receipt whose identities disagree."""
    crosswalk = _crosswalk(tmp_path)
    crosswalk["source_identity"]["freeze_receipt_path"] = "spec/no-such-freeze.json"

    with pytest.raises(CrosswalkError) as excinfo:
        verify_frozen_source(tmp_path, crosswalk)

    assert excinfo.value.code == "stale_source"
    assert "spec/no-such-freeze.json" in excinfo.value.detail


def test_a_foreign_repository_ref_with_a_protected_number_is_refused(tmp_path: Path) -> None:
    """`other-org/other-repo#514` is not this repo's #514 and must not be treated as it."""
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, ["other-org/other-repo#514"], [])

    assert result["refusal"] == "foreign_repository"


# --- the aggregate singleton rule -----------------------------------------


def test_a_carrier_closing_a_protected_and_an_unrelated_issue_is_refused_whole(tmp_path: Path) -> None:
    """The aggregate rule.

    Split references cannot be evidenced independently: there is no way to attach
    #514's proof to half a carrier. So the combined carrier refuses rather than
    letting the protected half ride along on the unprotected half's looser bar.
    """
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, [514], [514, 999])

    assert result["refusal"] == "not_singleton"


def test_two_protected_issues_in_one_carrier_are_refused(tmp_path: Path) -> None:
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, [514, 515], [514, 515])

    assert result["refusal"] == "not_singleton"


def test_commit_message_targets_that_disagree_refuse_as_an_aggregate(tmp_path: Path) -> None:
    """Pinned to the EXACT code, because the hedge here hid unreachable code.

    This assertion used to read `in {"not_singleton", "target_disagreement"}` and always
    took the first arm -- the disagreement branch sat after the singleton check and could
    never fire, so a docstring promise outlived the code's ability to keep it.

    `not_singleton` is not a placeholder here. On the commit-hook path the two sets are
    halves of ONE carrier and GitHub auto-closes both numbers on push, so aggregation is
    the correct reading.
    """
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, [514], [518])

    assert result["refusal"] == "not_singleton"


def test_close_with_comment_singleton_declaration_and_cli_disagreement_is_distinct(tmp_path: Path) -> None:
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, [514], [518], source="close-with-comment")

    assert result["refusal"] == "target_disagreement"
    assert "manual-target-declaration" in result["detail"]
    assert "corca-ai/charness#514" in result["detail"]
    assert "corca-ai/charness#518" in result["detail"]


def test_a_carrier_that_is_a_superset_of_the_invoked_target_also_refuses_as_an_aggregate(
    tmp_path: Path,
) -> None:
    """The neighbouring case, pinned so a future disagreement refusal cannot quietly
    swallow it: invoked {514} with carrier {514, 999} is a carrier closing two issues,
    which is the split that cannot be evidenced independently."""
    _crosswalk(tmp_path)

    assert _authorize(tmp_path, [514], [514, 999])["refusal"] == "not_singleton"
    assert _authorize(tmp_path, [514], [514, 999], source="close-with-comment")["refusal"] == "not_singleton"


def test_carrier_content_alone_cannot_authorize_a_protected_close(tmp_path: Path) -> None:
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, [], [514])

    assert result["refusal"] == "missing_invoked_target"


# --- carriers that are out of scope for this goal -------------------------


@pytest.mark.parametrize("carrier", ["release", "release-resume", "release-resume-closeout", "publish-execute", "pr-body"])
def test_release_and_pr_carriers_may_never_close_a_protected_issue(tmp_path: Path, carrier: str) -> None:
    """Release/PR closure is outside this goal, so those paths refuse rather than
    becoming the unwatched route a protected close escapes through."""
    _crosswalk(tmp_path, state="complete", rows=_complete_rows(tmp_path))

    result = _authorize(tmp_path, [514], [514], source=carrier)

    assert result["refusal"] == "carrier_out_of_scope"


# --- matrix state and source identity -------------------------------------


def test_the_bootstrap_crosswalk_cannot_authorize_the_issues_it_protects(tmp_path: Path) -> None:
    """The slice that builds the gate must not be able to walk through it."""
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, [514], [514])

    assert result["refusal"] == "matrix_incomplete"


def test_close_with_comment_matching_singletons_reach_the_existing_next_floor(tmp_path: Path) -> None:
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, [514], [514], source="close-with-comment")

    assert result["refusal"] == "matrix_incomplete"


def test_a_complete_matrix_with_a_local_consumer_row_authorizes_the_close(tmp_path: Path) -> None:
    _crosswalk(tmp_path, state="complete", rows=_complete_rows(tmp_path))

    result = _authorize(tmp_path, [514], [514])

    assert result["authorized"] is True
    assert result["projection_dependency"] == "local-consumer"
    assert result["target"] == {"repository": "corca-ai/charness", "issue_number": 514}


def test_a_crosswalk_bound_to_a_superseded_freeze_refuses_every_protected_close(tmp_path: Path) -> None:
    """Everything else can be internally consistent while the source has moved on."""
    _crosswalk(tmp_path, state="complete", rows=_complete_rows(tmp_path))
    crosswalk_path = tmp_path / CROSSWALK_REL
    payload = json.loads(crosswalk_path.read_text(encoding="utf-8"))
    payload["source_identity"]["source_snapshot_sha256"] = "0" * 64
    _write_json(crosswalk_path, payload)

    result = _authorize(tmp_path, [514], [514])

    assert result["refusal"] == "stale_source"


def test_an_undecided_projection_dependency_blocks_the_close(tmp_path: Path) -> None:
    rows = _complete_rows(tmp_path, dependency="undecided")
    _crosswalk(tmp_path, state="complete", rows=rows)

    result = _authorize(tmp_path, [514], [514])

    assert result["refusal"] == "undecided_projection_dependency"


def test_a_consumer_owned_row_blocks_its_own_issue_close(tmp_path: Path) -> None:
    """Charness cannot close what Charness does not own, and cannot fabricate the
    external owner that could."""
    _crosswalk(tmp_path, state="complete", rows=_complete_rows(tmp_path, owner="consumer-owned"))

    result = _authorize(tmp_path, [515], [515])

    assert result["refusal"] == "consumer_owned"


def test_a_rescoped_row_is_not_completion(tmp_path: Path) -> None:
    rows = _complete_rows(tmp_path, owner="re-scoped")
    for row in rows:
        row["replacement"] = "corca-ai/charness#900"
    _crosswalk(tmp_path, state="complete", rows=rows)

    result = _authorize(tmp_path, [515], [515])

    assert result["refusal"] == "re_scoped"


def test_a_protected_issue_with_no_row_refuses_instead_of_falling_through(tmp_path: Path) -> None:
    """Deleting a row is the other way to disarm the gate for one issue.

    #514 stays in `protected_issues` — so the gate still applies and cannot pass
    through generically — but the row carrying its owner and seam decision is gone.
    Without this refusal, `row.get(...)` would read `None` for every field and the
    close would be authorized by absence of evidence.
    """
    rows = [row for row in _complete_rows(tmp_path) if row["number"] != 514]
    _crosswalk(tmp_path, state="complete", rows=rows)

    result = _authorize(tmp_path, [514], [514])

    assert result["refusal"] == "unmapped_issue"
    assert result["authorized"] is False
    assert result["target"] == {"repository": "corca-ai/charness", "issue_number": 514}


# --- validator ------------------------------------------------------------


def _expect_validation_error(tmp_path: Path, code: str) -> None:
    with pytest.raises(CrosswalkError) as excinfo:
        validate_crosswalk(tmp_path, CROSSWALK_REL)
    assert excinfo.value.code == code


def test_the_bootstrap_crosswalk_validates_and_reports_it_authorizes_nothing(tmp_path: Path) -> None:
    _crosswalk(tmp_path)

    payload = validate_crosswalk(tmp_path, CROSSWALK_REL)

    assert payload["ok"] is True
    assert payload["authorization_status"]["authorizes_protected_close"] is False
    assert payload["shared_projection_status"] == "undecided"


def test_a_protected_issue_without_a_row_is_an_incomplete_row_set(tmp_path: Path) -> None:
    rows = [{"number": 514, "owner": "Charness-owned", "projection_dependency": "undecided",
             "criteria": [], "coverage": [], "source_clauses": []}]
    _crosswalk(tmp_path, rows=rows)

    _expect_validation_error(tmp_path, "incomplete_row_set")


def test_a_bootstrap_crosswalk_carrying_half_a_matrix_is_refused(tmp_path: Path) -> None:
    """Half-built reads as either state depending on who is looking."""
    rows = _complete_rows(tmp_path)
    _crosswalk(tmp_path, state="bootstrap", rows=rows)

    _expect_validation_error(tmp_path, "bootstrap_carries_matrix")


def test_a_complete_matrix_missing_an_issues_criteria_is_refused(tmp_path: Path) -> None:
    rows = _complete_rows(tmp_path)
    rows[0]["criteria"] = []
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "empty_criteria")


def test_a_clause_id_that_is_not_in_the_frozen_inventory_is_dangling(tmp_path: Path) -> None:
    """Catches a matrix built against a superseded freeze, or against text nobody captured."""
    rows = _complete_rows(tmp_path)
    rows[0]["source_clauses"][0]["source_clause_id"] = "deadbeefdeadbeef"
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "dangling_source_clause")


def test_a_frozen_clause_with_no_disposition_is_refused(tmp_path: Path) -> None:
    """Every clause gets a verdict. Silence is how a criterion disappears."""
    rows = _complete_rows(tmp_path)
    dropped = rows[0]["source_clauses"].pop()
    rows[0]["criteria"][0]["source_clause_ids"].remove(dropped["source_clause_id"])
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "undispositioned_clause")


def test_excluding_a_clause_without_a_reason_and_owner_is_refused(tmp_path: Path) -> None:
    rows = _complete_rows(tmp_path)
    excluded = rows[0]["source_clauses"][0]
    excluded["disposition"] = "non-goal"
    rows[0]["criteria"][0]["source_clause_ids"].remove(excluded["source_clause_id"])
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "unowned_exclusion")


def test_a_criterion_clause_that_no_criterion_claims_is_refused(tmp_path: Path) -> None:
    rows = _complete_rows(tmp_path)
    rows[0]["criteria"][0]["source_clause_ids"] = rows[0]["criteria"][0]["source_clause_ids"][:1]
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "unclaimed_criterion_clause")


def test_a_criterion_without_executable_coverage_is_refused(tmp_path: Path) -> None:
    """A crosswalk alone cannot unlock implementation; every claim owes an invocation."""
    rows = _complete_rows(tmp_path)
    rows[0]["criteria"][0]["coverage_ids"] = []
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "uncovered_criterion")


def test_coverage_spanning_criteria_must_declare_that_it_is_shared(tmp_path: Path) -> None:
    rows = _complete_rows(tmp_path)
    rows[0]["criteria"].append(dict(rows[0]["criteria"][0], criterion_id="C-extra"))
    rows[0]["coverage"][0]["criterion_ids"] = [rows[0]["criteria"][0]["criterion_id"], "C-extra"]
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "unshared_multi_criterion_coverage")


def test_an_owner_value_outside_the_three_allowed_is_refused(tmp_path: Path) -> None:
    _crosswalk(tmp_path, rows=[
        {"number": number, "owner": "mine", "projection_dependency": "undecided",
         "criteria": [], "coverage": [], "source_clauses": []} for number in PROTECTED
    ])

    _expect_validation_error(tmp_path, "invalid_owner")


def test_a_rescoped_row_must_name_its_replacement_owner(tmp_path: Path) -> None:
    _crosswalk(tmp_path, rows=[
        {"number": number, "owner": "re-scoped", "projection_dependency": "undecided",
         "criteria": [], "coverage": [], "source_clauses": []} for number in PROTECTED
    ])

    _expect_validation_error(tmp_path, "unnamed_rescope")


# --- round-1 review repairs -----------------------------------------------


def test_a_criterion_may_not_be_sourced_from_a_clause_declared_out_of_scope(tmp_path: Path) -> None:
    """Round-1 review finding: disposition was never consulted for criterion sources.

    A matrix could mark its entire source `non-goal` — each with a tidy reason and owner
    — and then assert criteria "sourced" from those non-goals. The closure check only
    guarded the other direction, so nothing caught it and the matrix read `complete`,
    which is the exact state that switches the gate's refusal off.
    """
    rows = _complete_rows(tmp_path)
    excluded = rows[0]["source_clauses"][0]
    excluded.update({"disposition": "non-goal", "reason": "out of scope", "owner": "someone"})
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "dangling_criterion_source")


def test_shared_declared_as_zero_does_not_slip_past_the_boolean_guard(tmp_path: Path) -> None:
    """`0 in {True, False}` is True (0 == False) but `0 is False` is not.

    The presence check and the enforcement check disagreed about what counts as False,
    so `"shared": 0` declared nothing and was held to nothing.
    """
    rows = _complete_rows(tmp_path)
    rows[0]["criteria"].append(dict(rows[0]["criteria"][0], criterion_id="C-extra"))
    rows[0]["coverage"][0]["criterion_ids"] = [rows[0]["criteria"][0]["criterion_id"], "C-extra"]
    rows[0]["coverage"][0]["shared"] = 0
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "undeclared_sharing")


def test_string_typed_issue_numbers_cannot_silently_disarm_the_gate(tmp_path: Path) -> None:
    """Round-1 review finding, and the worst one: a quiet total bypass.

    Issue numbers are compared against ints, so quoting them in the artifact makes the
    protected set match nothing — every protected close falls through the generic
    pass-through while this validator reports ok. One character per line turns the whole
    gate off, which is precisely what this validator exists to prevent.
    """
    _crosswalk(tmp_path, rows=[
        {"number": str(number), "owner": "Charness-owned", "projection_dependency": "undecided",
         "criteria": [], "coverage": [], "source_clauses": []} for number in PROTECTED
    ])
    payload = json.loads((tmp_path / CROSSWALK_REL).read_text(encoding="utf-8"))
    payload["protected_issues"] = [str(number) for number in PROTECTED]
    _write_json(tmp_path / CROSSWALK_REL, payload)

    _expect_validation_error(tmp_path, "non_integer_protected_issue")


def test_the_validator_reports_authorization_by_asking_the_gate_not_by_restating_state(tmp_path: Path) -> None:
    """Round-1 review finding: the validator asserted a verdict the gate contradicts.

    `matrix_state == "complete"` is necessary, not sufficient. A complete crosswalk whose
    rows are all consumer-owned refuses every close, while the old surface printed
    `authorizes_protected_close: true`.
    """
    _crosswalk(tmp_path, state="complete", rows=_complete_rows(tmp_path, owner="consumer-owned"))

    payload = validate_crosswalk(tmp_path, CROSSWALK_REL)

    status = payload["authorization_status"]
    assert status["authorizes_protected_close"] is False
    # Consumer-owned refuses on every IN-SCOPE carrier, not just the one a single probe
    # happened to use. The out-of-scope carriers refuse earlier, for their own reason.
    by_carrier = status["per_issue"][514]["by_carrier"]
    assert by_carrier["commit-msg"]["refusal"] == "consumer_owned"
    assert by_carrier["close-with-comment"]["refusal"] == "consumer_owned"
    assert by_carrier["release"]["refusal"] == "carrier_out_of_scope"
    assert status["per_issue"][514]["authorized_by_any_carrier"] is False


def test_a_complete_crosswalk_that_really_does_authorize_says_so(tmp_path: Path) -> None:
    """The counterpart: the honest surface must still report True when it is True."""
    _crosswalk(tmp_path, state="complete", rows=_complete_rows(tmp_path))

    payload = validate_crosswalk(tmp_path, CROSSWALK_REL)

    status = payload["authorization_status"]
    assert status["authorizes_protected_close"] is True
    assert status["per_issue"][518]["by_carrier"]["commit-msg"]["refusal"] is None
    # ...and the out-of-scope carriers still refuse, which a single-probe surface hid:
    # the old field said "authorized" while every release and PR carrier refused.
    assert status["per_issue"][518]["by_carrier"]["release"]["refusal"] == "carrier_out_of_scope"
    assert status["per_issue"][518]["by_carrier"]["pr-body"]["refusal"] == "carrier_out_of_scope"


# --- validator: the shape floor -------------------------------------------


def test_an_unknown_matrix_state_is_refused(tmp_path: Path) -> None:
    """`bootstrap` and `complete` carry two different bars; a third word would be
    routed to the `complete` branch by the `else`, so an invented state must be
    refused rather than silently promoted."""
    _crosswalk(tmp_path)
    _patch_crosswalk(tmp_path, lambda payload: payload.__setitem__("matrix_state", "half-built"))

    _expect_validation_error(tmp_path, "invalid_matrix_state")


def test_a_crosswalk_without_a_current_repository_is_refused(tmp_path: Path) -> None:
    """Every unqualified `#514` resolves against this field. Empty, and the protected
    keys are built from `""`, which no real target can ever match."""
    _crosswalk(tmp_path)
    _patch_crosswalk(tmp_path, lambda payload: payload.__setitem__("current_repository", ""))

    _expect_validation_error(tmp_path, "missing_current_repository")


def test_an_empty_protected_set_is_refused_because_it_authorizes_nothing(tmp_path: Path) -> None:
    """Emptying `protected_issues` turns every protected close into the generic
    pass-through while the artifact still reads like an installed gate."""
    _crosswalk(tmp_path)
    _patch_crosswalk(tmp_path, lambda payload: payload.__setitem__("protected_issues", []))

    _expect_validation_error(tmp_path, "empty_protected_set")


def test_a_string_typed_row_number_is_refused_even_when_the_protected_set_is_typed(tmp_path: Path) -> None:
    """The other half of the type floor.

    Quoting the number on the ROW alone leaves the protected set matching, so the gate
    still applies — and then no row is ever found for it. Refusing at validation is
    what keeps that from being discovered at close time.
    """
    _crosswalk(tmp_path)
    _patch_crosswalk(tmp_path, lambda payload: payload["issues"][0].__setitem__("number", "514"))

    _expect_validation_error(tmp_path, "non_integer_row_number")


def test_a_row_for_an_unprotected_issue_is_refused(tmp_path: Path) -> None:
    """A row nothing protects reads as coverage that the gate will never consult; it
    is either a typo'd number or a protection someone forgot to declare."""
    _crosswalk(tmp_path)
    _patch_crosswalk(
        tmp_path,
        lambda payload: payload["issues"].append(
            {"number": 999, "owner": "Charness-owned", "projection_dependency": "undecided",
             "criteria": [], "coverage": [], "source_clauses": []}
        ),
    )

    _expect_validation_error(tmp_path, "unprotected_row")


def test_a_projection_dependency_outside_the_allowed_values_is_refused(tmp_path: Path) -> None:
    """The gate branches on this value; an unrecognised one is treated as "not
    undecided" and would wave the close through on a seam nobody decided."""
    _crosswalk(tmp_path)
    _patch_crosswalk(tmp_path, lambda payload: payload["issues"][0].__setitem__("projection_dependency", "maybe"))

    _expect_validation_error(tmp_path, "invalid_projection_dependency")


def test_a_complete_crosswalk_without_a_snapshot_path_cannot_resolve_clause_ids(tmp_path: Path) -> None:
    """Without a snapshot there is no frozen inventory to check clause ids against, so
    every `dangling_source_clause` check would pass vacuously."""
    _crosswalk(tmp_path, state="complete", rows=_complete_rows(tmp_path))
    _patch_crosswalk(tmp_path, lambda payload: payload["source_identity"].pop("snapshot_path"))

    _expect_validation_error(tmp_path, "missing_source_identity")


# --- validator: a bootstrap crosswalk must stay inert ----------------------


def test_a_bootstrap_row_may_not_decide_the_projection_seam(tmp_path: Path) -> None:
    """A decided dependency is one of the two things the gate requires. Setting it
    while no matrix exists is the bootstrap artifact acquiring a tooth it has not
    earned, by the row rather than by the state."""
    _crosswalk(tmp_path)
    _patch_crosswalk(tmp_path, lambda payload: payload["issues"][0].__setitem__("projection_dependency", "local-consumer"))

    _expect_validation_error(tmp_path, "bootstrap_decides_dependency")


def test_a_bootstrap_crosswalk_may_not_declare_the_shared_projection_decided(tmp_path: Path) -> None:
    """The shared projection is the decision this whole goal exists to stop being
    invented early; declaring it settled before the matrix exists is that failure."""
    _crosswalk(tmp_path)
    _patch_crosswalk(tmp_path, lambda payload: payload["shared_projection"].__setitem__("status", "no-shared-artifact"))

    _expect_validation_error(tmp_path, "bootstrap_decides_projection")


# --- validator: the complete-state row floor -------------------------------


def test_an_issue_with_no_coverage_row_is_refused(tmp_path: Path) -> None:
    """Criteria without any executable coverage cannot fail; the matrix would read
    complete while nothing in it is ever run."""
    rows = _complete_rows(tmp_path)
    rows[0]["coverage"] = []
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "empty_coverage")


def test_a_repeated_criterion_id_is_refused(tmp_path: Path) -> None:
    """Ids are the only handle coverage rows have on criteria. Two criteria sharing
    one id means a coverage row silently claims to cover both, and dropping either is
    invisible."""
    rows = _complete_rows(tmp_path)
    rows[0]["criteria"].append(dict(rows[0]["criteria"][0]))
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "duplicate_criterion_id")


def test_a_repeated_coverage_id_is_refused(tmp_path: Path) -> None:
    """The same ambiguity from the other side: a criterion citing the duplicated id
    cannot be told which invocation actually proves it."""
    rows = _complete_rows(tmp_path)
    rows[0]["coverage"].append(dict(rows[0]["coverage"][0]))
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "duplicate_coverage_id")


def test_a_complete_matrix_may_not_leave_the_seam_undecided(tmp_path: Path) -> None:
    """`complete` is the state that switches the gate's refusal off, so a row still
    carrying `undecided` there would ship a close on an undecided seam."""
    _crosswalk(tmp_path, state="complete", rows=_complete_rows(tmp_path, dependency="undecided"))

    _expect_validation_error(tmp_path, "undecided_dependency")


def test_dispositioning_one_clause_twice_is_refused(tmp_path: Path) -> None:
    """Two verdicts on one clause means the `undispositioned_clause` count is
    satisfied by a duplicate while some other clause quietly has none."""
    rows = _complete_rows(tmp_path)
    rows[0]["source_clauses"].append(dict(rows[0]["source_clauses"][0]))
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "duplicate_clause_disposition")


def test_a_disposition_outside_the_three_allowed_is_refused(tmp_path: Path) -> None:
    """An unrecognised word is neither `criterion` nor an exclusion, so it would skip
    both the owner/reason requirement and the criterion-closure check."""
    rows = _complete_rows(tmp_path)
    rows[0]["source_clauses"][0]["disposition"] = "maybe"
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "invalid_disposition")


def test_a_criterion_sourced_from_nothing_is_refused(tmp_path: Path) -> None:
    """A criterion with no source clause is an acceptance claim nobody in the frozen
    issue text actually asked for — invented scope that then counts as evidence."""
    rows = _complete_rows(tmp_path)
    rows[0]["criteria"][0]["source_clause_ids"] = []
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "unsourced_criterion")


def test_a_criterion_citing_an_unknown_coverage_id_is_refused(tmp_path: Path) -> None:
    """A typo'd coverage id looks exactly like real coverage in the artifact while
    pointing at an invocation that does not exist."""
    rows = _complete_rows(tmp_path)
    rows[0]["criteria"][0]["coverage_ids"] = ["V-does-not-exist"]
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "dangling_criterion_coverage")


@pytest.mark.parametrize(
    "field", ["producer", "invocation", "expected", "artifact_path", "final_reader_route", "non_claim"]
)
def test_a_criterion_missing_any_execution_field_is_refused(tmp_path: Path, field: str) -> None:
    """Each field is what makes the criterion runnable and readable by someone other
    than its author. An empty one leaves a criterion that cannot be executed or whose
    result nobody is routed to read, while the matrix still counts it as covered."""
    rows = _complete_rows(tmp_path)
    rows[0]["criteria"][0][field] = ""
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "incomplete_criterion")


def test_a_coverage_row_serving_no_criterion_is_refused(tmp_path: Path) -> None:
    """Coverage that maps to nothing is work that runs but proves nothing; counting it
    inflates the matrix's apparent completeness."""
    rows = _complete_rows(tmp_path)
    rows[0]["coverage"][0]["criterion_ids"] = []
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "orphan_coverage")


def test_a_coverage_row_citing_an_unknown_criterion_is_refused(tmp_path: Path) -> None:
    """The mapping must close in both directions; a coverage row pointing at a
    criterion id that no longer exists is a rename nobody finished."""
    rows = _complete_rows(tmp_path)
    rows[0]["coverage"][0]["criterion_ids"] = ["C-does-not-exist"]
    _crosswalk(tmp_path, state="complete", rows=rows)

    _expect_validation_error(tmp_path, "dangling_coverage_criterion")


# --- the operator-facing entrypoints --------------------------------------


def test_the_crosswalk_cli_prints_the_authorization_record_and_exits_zero(tmp_path, monkeypatch, capsys) -> None:
    """Driven in process, the way an operator drives it from a shell."""
    _crosswalk(tmp_path, state="complete", rows=_complete_rows(tmp_path))

    code, captured = _run_cli(
        crosswalk_main, monkeypatch, capsys,
        "--repo-root", str(tmp_path), "--crosswalk", CROSSWALK_REL,
        "--carrier-source", "commit-msg", "--invoked", "514", "--carrier", "514",
    )

    assert code == 0
    payload = yaml.safe_load(captured.out)
    assert payload["authorized"] is True
    assert payload["target"] == {"repository": "corca-ai/charness", "issue_number": 514}


def test_the_crosswalk_cli_exits_nonzero_on_a_refused_close(tmp_path, monkeypatch, capsys) -> None:
    """The exit code is what a shell caller branches on: a refusal that printed its
    reason and still exited 0 would be a close that proceeds."""
    _crosswalk(tmp_path)

    code, captured = _run_cli(
        crosswalk_main, monkeypatch, capsys,
        "--repo-root", str(tmp_path), "--crosswalk", CROSSWALK_REL,
        "--carrier-source", "commit-msg", "--invoked", "corca-ai/charness#514",
    )

    assert code == 1
    assert yaml.safe_load(captured.out)["refusal"] == "matrix_incomplete"


def test_the_crosswalk_module_main_guard_executes(monkeypatch) -> None:
    # cover `raise SystemExit(main())` (the __main__ guard) in-process via runpy.
    monkeypatch.setattr(sys, "argv", ["x", "--carrier-source", "commit-msg", "--invoked", "999"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(
            str(REPO_ROOT / "scripts" / "evidence" / "evidence_boundary_crosswalk.py"),
            run_name="__main__",
        )

    assert excinfo.value.code == 0


def test_the_validator_cli_prints_the_validation_payload_and_exits_zero(tmp_path, monkeypatch, capsys) -> None:
    _crosswalk(tmp_path)

    code, captured = _run_cli(
        validate_main, monkeypatch, capsys, "--repo-root", str(tmp_path), "--crosswalk", CROSSWALK_REL
    )

    assert code == 0
    payload = yaml.safe_load(captured.out)
    assert payload["ok"] is True
    assert payload["matrix_state"] == "bootstrap"


def test_the_validator_cli_renders_a_refusal_on_both_channels_and_exits_one(tmp_path, monkeypatch, capsys) -> None:
    """A refusal that only reached stdout would be invisible to a human watching a
    terminal, and one that only reached stderr would be invisible to a caller piping
    JSON. Both, plus a nonzero exit, is the contract."""
    _crosswalk(tmp_path)
    _patch_crosswalk(tmp_path, lambda payload: payload.__setitem__("protected_issues", []))

    code, captured = _run_cli(
        validate_main, monkeypatch, capsys, "--repo-root", str(tmp_path), "--crosswalk", CROSSWALK_REL
    )

    assert code == 1
    assert yaml.safe_load(captured.out) == {
        "ok": False, "error": "empty_protected_set",
        "detail": "the crosswalk protects no issues, so it authorizes nothing",
    }
    assert "REFUSED (empty_protected_set)" in captured.err


def test_the_validator_module_main_guard_executes(tmp_path, monkeypatch) -> None:
    # cover `raise SystemExit(main())` (the __main__ guard) in-process via runpy.
    # Argv points at a built tmp world on purpose: this repo checks in no crosswalk,
    # so bare argv would exercise the `crosswalk_missing` refusal instead of the
    # success path this test exists to cover.
    _crosswalk(tmp_path)
    monkeypatch.setattr(sys, "argv", ["x", "--repo-root", str(tmp_path), "--crosswalk", CROSSWALK_REL])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(REPO_ROOT / "scripts" / "gates" / "validate_evidence_boundary_crosswalk.py"), run_name="__main__")

    assert excinfo.value.code == 0


# --- this repo checks in no crosswalk instance -----------------------------

RETIRED_CROSSWALK_REL = "charness-artifacts/spec/2026-08-07-evidence-boundary-crosswalk.json"


def test_this_repo_checks_in_no_crosswalk_instance() -> None:
    """The #514/#515/#518 instance was retired on 2026-08-10; the capability was not.

    Asserted rather than merely deleted, because the failure mode of a retirement is
    a file quietly reappearing — a checked-in crosswalk is load-bearing the moment it
    exists, and nothing else in this suite reads the checked-in path.
    """
    assert not (REPO_ROOT / RETIRED_CROSSWALK_REL).exists()
    record = REPO_ROOT / "charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md"
    assert record.is_file(), "a retired proof surface must leave a record naming what carries the boundary"


def test_absent_instance_is_reported_as_inapplicable_not_as_a_pass() -> None:
    """`applies=false` with a status, never a bare authorized=true.

    This is the whole safety property of the retirement: every former target now
    takes the ordinary closeout floor, and the authorization record SAYS it did not
    apply rather than implying it approved.
    """
    for number in PROTECTED:
        result = authorize_closeout(
            [{"repository": "corca-ai/charness", "issue_number": number, "source": "cli"}],
            [],
            "close-with-comment",
            repo_root=REPO_ROOT,
        )
        assert result["applies"] is False
        assert result["authorized"] is True
        assert result["refusal"] is None
        # Pinned to the exact code, not `!= "loaded"`. A differently-broken crosswalk
        # (`crosswalk_invalid`, `stale_source`) also reports non-`loaded` while meaning
        # something this test is not claiming, so the loose form would keep passing
        # through a state it never checked.
        assert result["crosswalk_status"] == "crosswalk_missing"


def test_the_installed_plugin_projection_exposes_the_same_authorization_entrypoint(
    exported_plugin_tree: Path,
) -> None:
    """The installed copy must carry the gate too.

    A gate that exists only in the source tree is not a gate for anyone running the
    plugin, which is every consumer.
    """
    projection = exported_plugin_tree / "scripts" / "evidence" / "evidence_boundary_crosswalk.py"

    assert projection.is_file(), "export_plugin.py must carry the authorization projection"
    source = projection.read_text(encoding="utf-8")
    assert "def authorize_closeout(" in source
    assert source == (
        REPO_ROOT / "scripts" / "evidence" / "evidence_boundary_crosswalk.py"
    ).read_text(encoding="utf-8")
