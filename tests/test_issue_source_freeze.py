"""What the source freeze must refuse before an acceptance matrix may bind to it.

The freeze exists to answer one question a later reader cannot otherwise answer:
"is this the source the matrix was built against, and did a tool actually fetch
it?" Every refusal below is a way of answering "no" that a schema check alone
would answer "yes" to — most importantly a hand-authored snapshot, which is
well-formed by construction and therefore invisible to every check except
re-derivation from captured bytes.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.issue_source_capture_lib import build_snapshot_and_receipt, capture_issues
from scripts.issue_source_freeze_lib import _RECEIPT_IDENTITY_EXCLUDED, FreezeError
from scripts.issue_source_normalize_lib import sha256_payload
from scripts.validate_issue_source_freeze import (
    run_freeze,
    run_refreeze,
    run_validate,
    stamp_inspection,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_REL = "spec/source.json"
CAPTURE_REL = "spec/source-capture-receipt.json"
INSPECTION_REL = "spec/inspection.json"
FREEZE_REL = "spec/freeze.json"
CAPABILITY = {
    "enumeration": "cursor",
    "page_size": 2,
    "has_next_field": "hasNextPage",
    "cursor_field": "endCursor",
    "total_count_field": "totalCount",
    "normalization": "github-issue-v1",
    "declared": False,
}


def _response(number: int, body: str, nodes: list[dict], total: int) -> str:
    return json.dumps(
        {
            "data": {
                "repository": {
                    "issue": {
                        "number": number,
                        "title": f"issue {number}",
                        "body": body,
                        "state": "OPEN",
                        "url": f"https://example.invalid/{number}",
                        "comments": {
                            "totalCount": total,
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                            "nodes": nodes,
                        },
                    }
                }
            }
        }
    )


def _build_world(tmp_path: Path, *, numbers=(514, 515, 518), bodies=None) -> None:
    """Write a complete, valid freeze world into `tmp_path`."""
    bodies = bodies or {number: f"- criterion for {number}\n- second criterion" for number in numbers}
    queue = [_response(number, bodies[number], [], 0) for number in sorted(numbers)]

    def runner(argv):
        return subprocess.CompletedProcess(argv, 0, queue.pop(0), "")

    captured = capture_issues(
        repo="corca-ai/charness",
        numbers=list(numbers),
        backend={"id": "gh", "binary": "gh", "commands": None},
        capability=CAPABILITY,
        runner=runner,
    )
    snapshot, receipt, raw_files = build_snapshot_and_receipt(
        repo="corca-ai/charness",
        numbers=list(numbers),
        adapter={"path": ".agents/issue-adapter.yaml", "found": True, "data": {"issue_backend": {"id": "gh", "binary": "gh"}}},
        capability=CAPABILITY,
        captured=captured,
        raw_dir_rel="spec/source-raw",
    )
    for rel, text in raw_files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _write_json(tmp_path / SNAPSHOT_REL, snapshot)
    _write_json(tmp_path / CAPTURE_REL, receipt)
    inspected = tmp_path / "owner.py"
    inspected.write_text("# inspected owner\n", encoding="utf-8")
    _write_json(
        tmp_path / INSPECTION_REL,
        {
            "schema": "issue-source-owner-inspection/v1",
            "issues": list(numbers),
            "locators": [{"role": "owner", "path": "owner.py", "sha256": "", "note": "n"}],
            "inspection_identity": "",
        },
    )
    stamp_inspection(tmp_path, INSPECTION_REL)
    run_freeze(tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, list(numbers))


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _validate(tmp_path: Path, numbers=(514, 515, 518)):
    return run_validate(tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, list(numbers))


def _edit_json(path: Path, mutate) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    _write_json(path, payload)


def _edit_receipt(tmp_path: Path, mutate) -> None:
    """Edit the capture receipt AND reseal its identity.

    Without the reseal, every receipt-tampering test would refuse at
    `capture_receipt_identity_mismatch` — a real check, but one that would shadow the
    specific check each of these tests exists to prove. Resealing hands the tamperer
    the best case and makes the deeper check do the work.
    """
    path = tmp_path / CAPTURE_REL
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutate(payload)
    payload["receipt_identity"] = sha256_payload(
        {key: value for key, value in payload.items() if key not in _RECEIPT_IDENTITY_EXCLUDED}
    )
    _write_json(path, payload)


def test_a_complete_freeze_validates_and_reports_rederivation(tmp_path: Path) -> None:
    _build_world(tmp_path)

    payload = _validate(tmp_path)

    assert payload["ok"] is True
    assert payload["snapshot_rederived_from_raw_responses"] is True
    assert payload["issues"] == [514, 515, 518]


def test_a_hand_edited_snapshot_body_fails_rederivation(tmp_path: Path) -> None:
    """The check that no schema can substitute for.

    The edited snapshot is still valid JSON, still the right schema, still has every
    field. Only rebuilding it from the captured raw responses exposes that the text
    the matrix will cite is not the text the backend returned.
    """
    _build_world(tmp_path)
    _edit_json(
        tmp_path / SNAPSHOT_REL,
        lambda payload: payload["source_document"]["issues"][0].__setitem__("body", "- a criterion nobody filed"),
    )

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "snapshot_not_rederivable"


def test_a_snapshot_with_no_captured_raw_responses_cannot_be_frozen(tmp_path: Path) -> None:
    _build_world(tmp_path)
    for raw in (tmp_path / "spec" / "source-raw").glob("*.json"):
        raw.unlink()

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "missing_raw_response"


def test_a_tampered_raw_response_is_caught_by_its_own_receipt_digest(tmp_path: Path) -> None:
    _build_world(tmp_path)
    raw = next((tmp_path / "spec" / "source-raw").glob("*.json"))
    raw.write_text(raw.read_text(encoding="utf-8").replace("criterion", "requirement"), encoding="utf-8")

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "raw_response_digest_mismatch"


def test_a_capture_receipt_claiming_hand_authorship_is_refused(tmp_path: Path) -> None:
    _build_world(tmp_path)
    _edit_receipt(tmp_path, lambda payload: payload.__setitem__("hand_authored", True))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "hand_authored_capture"


def test_an_incomplete_enumeration_is_refused_at_freeze_not_only_at_capture(tmp_path: Path) -> None:
    """Belt and braces on purpose.

    The capture adapter already refuses incomplete pagination, but the receipt is a
    file on disk that a later step could produce by other means. The freeze re-reads
    the assertion rather than assuming the only producer was the adapter.
    """
    _build_world(tmp_path)
    _edit_receipt(tmp_path, lambda payload: payload["issues"][0].__setitem__("pagination_complete", False))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "incomplete_pagination"


def test_a_receipt_whose_counts_disagree_is_refused(tmp_path: Path) -> None:
    _build_world(tmp_path)
    _edit_receipt(tmp_path, lambda payload: payload["issues"][0].__setitem__("comment_total_count", 3))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "count_mismatch"


def test_omitting_one_protected_issue_blocks_the_freeze(tmp_path: Path) -> None:
    """Dropping an issue is the cheapest way to make the lane look finished.

    With #518 never captured, nothing downstream has a #518 criterion to fail, so
    every validator downstream goes green on two-thirds of the work.
    """
    _build_world(tmp_path, numbers=(514, 515))

    with pytest.raises(FreezeError) as excinfo:
        run_validate(tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, [514, 515, 518])

    assert excinfo.value.code == "missing_protected_issue"
    assert "518" in excinfo.value.detail


def test_an_issue_whose_body_normalizes_to_nothing_is_refused(tmp_path: Path) -> None:
    """An issue with no clauses can never fail a criterion check, so it must never
    reach one. The refusal fires at `freeze`, before a matrix can be built on it."""
    with pytest.raises(FreezeError) as excinfo:
        _build_world(tmp_path, bodies={514: "", 515: "- x", 518: "- y"})

    assert excinfo.value.code in {"empty_clause_inventory", "empty_body_unit"}
    assert "514" in excinfo.value.detail


def test_an_inspection_whose_inspected_file_has_changed_is_stale(tmp_path: Path) -> None:
    """An owner map is a claim about content, and content moves.

    "I inspected the closeout planner" stays true forever. "I inspected it at this
    digest" stops being true exactly when the conclusions drawn from it stop being
    safe to build on.
    """
    _build_world(tmp_path)
    (tmp_path / "owner.py").write_text("# owner changed after inspection\n", encoding="utf-8")

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "stale_inspection"


def test_an_inspection_with_a_forged_identity_is_refused(tmp_path: Path) -> None:
    _build_world(tmp_path)
    _edit_json(tmp_path / INSPECTION_REL, lambda payload: payload.__setitem__("inspection_identity", "0" * 64))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "inspection_identity_mismatch"


def test_an_inspection_with_no_locators_is_not_an_inspection(tmp_path: Path) -> None:
    _build_world(tmp_path)
    _edit_json(tmp_path / INSPECTION_REL, lambda payload: payload.__setitem__("locators", []))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "empty_inspection"


def test_recapturing_changed_source_invalidates_the_existing_freeze_receipt(tmp_path: Path) -> None:
    """The staleness case the whole receipt exists for.

    Everything is internally consistent — new snapshot, new capture receipt, matching
    raw responses. Only the freeze receipt still names the OLD source, and that is
    what must refuse, because the matrix downstream is keyed to the old clause ids.
    """
    _build_world(tmp_path)
    frozen = json.loads((tmp_path / FREEZE_REL).read_text(encoding="utf-8"))
    _build_world_recapture(tmp_path)
    _write_json(tmp_path / FREEZE_REL, frozen)

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "stale_freeze_receipt"
    assert "source_snapshot_sha256" in excinfo.value.detail


def _build_world_recapture(tmp_path: Path) -> None:
    _build_world(tmp_path, bodies={514: "- edited criterion", 515: "- b", 518: "- c"})


def test_a_forged_freeze_identity_is_refused(tmp_path: Path) -> None:
    _build_world(tmp_path)
    _edit_json(tmp_path / FREEZE_REL, lambda payload: payload.__setitem__("freeze_identity", "0" * 64))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "freeze_identity_mismatch"


def test_a_freeze_receipt_covering_a_different_issue_set_is_refused(tmp_path: Path) -> None:
    """A caller may not narrow the protected set at validation time.

    The freeze covers three issues; asking it to authorize only two would let a
    consumer quietly drop #518 from the protected set at the last checkpoint, after
    every earlier gate had already agreed all three were in scope.
    """
    _build_world(tmp_path, numbers=(514, 515, 518))

    with pytest.raises(FreezeError) as excinfo:
        run_validate(tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, [514, 515])

    assert excinfo.value.code == "freeze_issue_set_mismatch"


def test_a_deleted_clause_record_is_caught_even_though_the_identity_scalar_matches(tmp_path: Path) -> None:
    """Round-1 review finding: the identity scalar was verified, the block was not.

    The crosswalk's matrix floor reads `snapshot["clause_inventory"]` directly to decide
    which clauses owe a disposition. Verifying only the summary digest meant one deleted
    clause record — identity string untouched — silently removed an inconvenient
    criterion from the set anything downstream could require, with every gate green.
    """
    _build_world(tmp_path)
    _edit_json(
        tmp_path / SNAPSHOT_REL,
        lambda payload: payload["clause_inventory"]["issues"][0]["source_units"][0]["clauses"].pop(),
    )

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "clause_inventory_mismatch"


def test_a_truncated_capture_that_declares_itself_complete_is_caught_by_the_raw_bytes(tmp_path: Path) -> None:
    """Round-1 review finding: completeness was re-read from the receipt's own integers.

    `captured_comment_count == comment_total_count` only proves two receipt fields agree
    with each other, which a truncated capture satisfies by declaring both numbers equal.
    Completeness is now re-proven from the raw responses.
    """
    _build_world(tmp_path)
    raw = next((tmp_path / "spec" / "source-raw").glob("*514*.json"))
    payload = json.loads(raw.read_text(encoding="utf-8"))
    payload["data"]["repository"]["issue"]["comments"]["totalCount"] = 40
    raw.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    digest = __import__("hashlib").sha256(raw.read_bytes()).hexdigest()

    def retotal(receipt):
        for issue in receipt["issues"]:
            if issue["number"] == 514:
                issue["comment_total_count"] = 40
                issue["captured_comment_count"] = 40
                issue["pages"][0]["raw_response_sha256"] = digest

    _edit_receipt(tmp_path, retotal)

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "count_mismatch"
    assert "raw responses carry" in excinfo.value.detail


def test_a_final_raw_page_still_claiming_another_page_is_refused(tmp_path: Path) -> None:
    _build_world(tmp_path)
    raw = next((tmp_path / "spec" / "source-raw").glob("*514*.json"))
    payload = json.loads(raw.read_text(encoding="utf-8"))
    payload["data"]["repository"]["issue"]["comments"]["pageInfo"]["hasNextPage"] = True
    raw.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    digest = __import__("hashlib").sha256(raw.read_bytes()).hexdigest()
    _edit_receipt(
        tmp_path,
        lambda receipt: [
            issue["pages"][0].__setitem__("raw_response_sha256", digest)
            for issue in receipt["issues"] if issue["number"] == 514
        ],
    )

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "incomplete_pagination"


def test_a_receipt_field_outside_the_rederivation_path_cannot_be_edited_silently(tmp_path: Path) -> None:
    """Round-1 review finding: `receipt_identity` was asserted and never recomputed.

    Which adapter/backend captured this, the normalization policy, the requested issue
    set, and the page cursors all sit outside re-derivation, so they were editable after
    the fact with the stale identity left in place and nothing noticing.
    """
    _build_world(tmp_path)
    _edit_json(tmp_path / CAPTURE_REL, lambda payload: payload["adapter"].__setitem__("backend_id", "forged"))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "capture_receipt_identity_mismatch"


def test_appending_a_page_with_a_forged_body_cannot_override_the_honest_page(tmp_path: Path) -> None:
    """Round-2 review finding: the drift check compared only the issue NUMBER.

    The derived body comes from the last page, so an appended page — same number, zero
    comments, matching totalCount, hasNextPage false, forged body — silently overrode the
    honest page sitting on disk beside it. Digests matched (the page is genuinely there),
    containment passed, counts agreed. Nothing else in the chain could see it.
    """
    _build_world(tmp_path)
    honest = next((tmp_path / "spec" / "source-raw").glob("*514*.json"))
    payload = json.loads(honest.read_text(encoding="utf-8"))
    payload["data"]["repository"]["issue"]["body"] = "- a criterion nobody filed"
    forged = honest.with_name("issue-514-page-1.json")
    forged.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    digest = __import__("hashlib").sha256(forged.read_bytes()).hexdigest()

    def append_page(receipt):
        for issue in receipt["issues"]:
            if issue["number"] == 514:
                issue["pages"].append(
                    {
                        "page_index": 1,
                        "raw_response_path": f"spec/source-raw/{forged.name}",
                        "raw_response_sha256": digest,
                    }
                )

    _edit_receipt(tmp_path, append_page)

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "raw_response_issue_drift"
    assert "body" in excinfo.value.detail


def test_a_receipt_omitting_its_raw_response_dir_is_refused_not_degraded(tmp_path: Path) -> None:
    """Round-2 review finding: absence switched off the stronger containment clause.

    The receipt is untrusted input, so deleting one key must not disarm a defense.
    """
    _build_world(tmp_path)
    _edit_receipt(tmp_path, lambda receipt: receipt["issues"][0].pop("raw_response_dir", None))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "missing_raw_response_dir"


def test_a_raw_response_path_escaping_the_repo_is_refused(tmp_path: Path) -> None:
    """The receipt is untrusted input; its paths must not reach outside the raw dir."""
    _build_world(tmp_path)
    _edit_receipt(
        tmp_path,
        lambda receipt: receipt["issues"][0]["pages"][0].__setitem__("raw_response_path", "../../../etc/hostname"),
    )

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "raw_response_escape"


def test_refreeze_restamps_refreezes_and_rebinds_the_crosswalk_in_one_command(tmp_path: Path) -> None:
    """The retro repair: the maintenance ritual is a tool, not a shell heredoc.

    Editing an inspected owner correctly stales the freeze, so re-freezing is routine
    rather than rare. As three separate steps the third — copying identity fields into
    the crosswalk — had no tool at all and was hand-executed six times in one session.
    """
    _build_world(tmp_path)
    crosswalk_rel = "spec/crosswalk.json"
    _write_json(
        tmp_path / crosswalk_rel,
        {
            "schema": "evidence-boundary-crosswalk/v1",
            "source_identity": {"freeze_receipt_path": FREEZE_REL, "source_snapshot_sha256": "stale"},
        },
    )
    (tmp_path / "owner.py").write_text("# the inspected owner changed\n", encoding="utf-8")

    # The staleness is real before the repair runs.
    with pytest.raises(FreezeError) as stale:
        _validate(tmp_path)
    assert stale.value.code == "stale_inspection"

    payload = run_refreeze(
        tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, [514, 515, 518], crosswalk_rel
    )

    assert payload["ok"] is True
    assert payload["validated"]["ok"] is True
    rebound = json.loads((tmp_path / crosswalk_rel).read_text(encoding="utf-8"))["source_identity"]
    freeze = json.loads((tmp_path / FREEZE_REL).read_text(encoding="utf-8"))
    assert rebound["source_snapshot_sha256"] == freeze["source_snapshot_sha256"]
    assert rebound["freeze_identity"] == freeze["freeze_identity"]
    assert "source_snapshot_sha256" in payload["crosswalk_rebound"]["changed_fields"]


def test_refreeze_is_usable_before_a_crosswalk_exists(tmp_path: Path) -> None:
    """Every repo has a freeze before it has a crosswalk; the rebind must no-op."""
    _build_world(tmp_path)

    payload = run_refreeze(
        tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, [514, 515, 518], "spec/absent.json"
    )

    assert payload["ok"] is True
    assert payload["crosswalk_rebound"]["rebound"] is False


def test_the_checked_in_charness_freeze_for_514_515_518_validates() -> None:
    """The real artifacts, not a fixture.

    A validator that only ever runs against synthetic worlds proves the validator.
    This proves the freeze this goal actually binds to.
    """
    payload = run_validate(
        REPO_ROOT,
        "charness-artifacts/spec/2026-08-07-issue-514-515-518-source.json",
        "charness-artifacts/spec/2026-08-07-issue-514-515-518-owner-inspection.json",
        "charness-artifacts/spec/2026-08-07-issue-514-515-518-freeze-receipt.json",
        [514, 515, 518],
    )

    assert payload["ok"] is True
    assert payload["snapshot_rederived_from_raw_responses"] is True
