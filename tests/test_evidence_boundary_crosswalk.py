"""Closeout authorization: who may close #514/#515/#518, through which carrier.

The tests are organised around the ways a close reaches GitHub *without* passing the
strictness someone thought they had installed: through a different carrier, through a
carrier that also closes something else, through a repository that merely looks like
this one, or through a matrix that does not yet exist. Each is a real path in this
repo, not a hypothetical.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.evidence_boundary_crosswalk import (
    CrosswalkError,
    authorize_closeout,
    normalize_target,
)
from scripts.issue_source_capture_lib import build_snapshot_and_receipt, capture_issues
from scripts.validate_evidence_boundary_crosswalk import run as validate_crosswalk
from scripts.validate_issue_source_freeze import run_freeze, stamp_inspection

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
        {"schema": "issue-source-owner-inspection/v1", "issues": list(PROTECTED),
         "locators": [{"role": "owner", "path": "owner.py", "sha256": "", "note": "n"}], "inspection_identity": ""},
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


def test_invoked_and_carrier_targets_that_disagree_are_named_as_a_disagreement(tmp_path: Path) -> None:
    """A distinct refusal from `not_singleton` on purpose.

    "the CLI said #514 and the body said #518" is a different operator mistake from
    "this carrier closes two issues", and collapsing them would hand the author the
    wrong remedy.
    """
    _crosswalk(tmp_path)

    result = _authorize(tmp_path, [514], [518])

    assert result["refusal"] in {"not_singleton", "target_disagreement"}


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


# --- the real checked-in artifact -----------------------------------------


def test_the_checked_in_charness_crosswalk_validates_in_bootstrap_state() -> None:
    payload = validate_crosswalk(REPO_ROOT, "charness-artifacts/spec/2026-08-07-evidence-boundary-crosswalk.json")

    assert payload["ok"] is True
    assert payload["matrix_state"] == "bootstrap"
    assert payload["protected_issues"] == [514, 515, 518]
    assert payload["authorization_status"]["authorizes_protected_close"] is False


def test_the_installed_plugin_projection_exposes_the_same_authorization_entrypoint() -> None:
    """The installed copy must carry the gate too.

    A gate that exists only in the source tree is not a gate for anyone running the
    plugin, which is every consumer.
    """
    projection = REPO_ROOT / "plugins" / "charness" / "scripts" / "evidence_boundary_crosswalk.py"

    assert projection.is_file(), "run scripts/sync_root_plugin_manifests.py"
    source = projection.read_text(encoding="utf-8")
    assert "def authorize_closeout(" in source
    assert source == (REPO_ROOT / "scripts" / "evidence_boundary_crosswalk.py").read_text(encoding="utf-8")
