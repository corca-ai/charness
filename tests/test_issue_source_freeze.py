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
import runpy
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.issue.issue_source_capture_lib import build_snapshot_and_receipt, capture_issues
from scripts.issue.issue_source_freeze_lib import _RECEIPT_IDENTITY_EXCLUDED, FreezeError
from scripts.issue.issue_source_normalize_lib import sha256_payload, sha256_text
from scripts.issue.validate_issue_source_freeze import (
    main,
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


def _build_world(tmp_path: Path, *, numbers=(514, 515, 518), bodies=None, comments=None) -> None:
    """Write a complete, valid freeze world into `tmp_path`."""
    bodies = bodies or {number: f"- criterion for {number}\n- second criterion" for number in numbers}
    comments = comments or {}
    queue = [
        _response(number, bodies[number], list(comments.get(number, [])), len(comments.get(number, [])))
        for number in sorted(numbers)
    ]

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
            "schema": "issue-source-owner-inspection/v2",
            "issues": list(numbers),
            "locators": [{"role": "owner", "path": "owner.py", "note": "n"}],
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


def _comment(node_id: str, body: str) -> dict:
    return {"id": node_id, "body": body, "createdAt": "2026-08-01T00:00:00Z", "author": {"login": "owner"}}


_TWO_COMMENTS = [_comment("C_a", "- criterion from comment a"), _comment("C_b", "- criterion from comment b")]


def _edit_raw_page(tmp_path: Path, number: int, mutate) -> None:
    """Edit one captured raw page AND reseal the receipt digest that commits to it.

    Same reason `_edit_receipt` reseals: without this every raw-page test would stop at
    `raw_response_digest_mismatch`, which is already proven above and would shadow the
    specific refusal each of these tests exists to prove. Resealing hands the tamperer
    the digest they would have had to forge anyway.
    """
    raw = next((tmp_path / "spec" / "source-raw").glob(f"*{number}*.json"))
    payload = json.loads(raw.read_text(encoding="utf-8"))
    mutate(payload)
    raw.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    digest = sha256_text(raw.read_text(encoding="utf-8"))
    _edit_receipt(
        tmp_path,
        lambda receipt: [
            i["pages"][0].__setitem__("raw_response_sha256", digest) for i in receipt["issues"] if i["number"] == number
        ],
    )


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


def test_an_edit_to_an_inspected_file_is_no_longer_a_refusal(tmp_path: Path) -> None:
    """`#562`: the content pin is retired, and this is the behaviour that replaced it.

    The pin refused on any change to an inspected file. Measured over the real
    `#514`/`#515`/`#518` freeze, that was 0 true positives in 5 refusals — a comment or
    a message string invalidated it exactly as loudly as a semantic change, and the
    one-command remedy trained the reflex that would have fired on a real change too.
    Asserting ACCEPTANCE here is the pin's grave marker: if someone reintroduces a
    whole-file digest check, this test is what goes red.
    """
    _build_world(tmp_path)
    (tmp_path / "owner.py").write_text("# owner changed after inspection\n", encoding="utf-8")

    assert _validate(tmp_path)["ok"] is True


def test_a_locator_still_carrying_a_retired_content_pin_is_refused(tmp_path: Path) -> None:
    """A leftover `sha256` is a DEAD claim, and dead claims are the repo's worst shape.

    It reads exactly like an enforced pin to anyone skimming the artifact while nothing
    enforces it, so the artifact's appearance and its teeth would disagree.
    """
    _build_world(tmp_path)
    _edit_json(
        tmp_path / INSPECTION_REL,
        lambda payload: payload["locators"][0].__setitem__("sha256", "0" * 64),
    )

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "retired_locator_pin"


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

    As three separate steps the third — copying identity fields into the crosswalk — had
    no tool at all and was hand-executed six times in one session. The staleness trigger
    here is a change to the locator SET, not an edit to an inspected file: `#562` retired
    the content pin, so an ordinary edit no longer stales anything.
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
    (tmp_path / "second_owner.py").write_text("# a second owner the map now claims\n", encoding="utf-8")
    _edit_json(
        tmp_path / INSPECTION_REL,
        lambda payload: payload["locators"].append({"role": "owner", "path": "second_owner.py", "note": "n"}),
    )

    # The staleness is real before the repair runs.
    with pytest.raises(FreezeError) as stale:
        _validate(tmp_path)
    assert stale.value.code == "inspection_identity_mismatch"

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


def test_a_freeze_receipt_that_was_never_written_is_refused_not_treated_as_absent_bind(tmp_path: Path) -> None:
    """No receipt is not "no objection".

    A validator that treats a missing bind file as nothing-to-check would authorize
    every consumer of a freeze that was never taken.
    """
    _build_world(tmp_path)

    with pytest.raises(FreezeError) as excinfo:
        run_validate(tmp_path, SNAPSHOT_REL, INSPECTION_REL, "spec/never-frozen.json", [514, 515, 518])

    assert excinfo.value.code == "missing_file"
    assert "spec/never-frozen.json" in excinfo.value.detail


def test_a_truncated_snapshot_file_is_refused_as_unreadable_not_crashed_on(tmp_path: Path) -> None:
    """A half-written artifact is a routine outcome of an interrupted capture.

    It must surface as this lane's refusal shape — a stable code an operator and a
    caller can branch on — rather than as a raw `JSONDecodeError` traceback that the
    CLI's `run_cli` would deliberately not catch.
    """
    _build_world(tmp_path)
    (tmp_path / SNAPSHOT_REL).write_text('{"schema": "issue-source-sna', encoding="utf-8")

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "invalid_json"
    assert SNAPSHOT_REL in excinfo.value.detail


def test_a_well_formed_file_of_the_wrong_kind_cannot_stand_in_for_the_snapshot(tmp_path: Path) -> None:
    """Every artifact in this lane is JSON with a digest-shaped field somewhere.

    Without the declared-schema check, pointing `--snapshot` at the freeze receipt (or
    at a future v2 snapshot) would fail deep inside re-derivation with a KeyError, or
    worse, coincidentally pass a check that never noticed it was reading the wrong file.
    """
    _build_world(tmp_path)
    _edit_json(tmp_path / SNAPSHOT_REL, lambda payload: payload.__setitem__("schema", "issue-source-snapshot/v2"))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "wrong_schema"
    assert "issue-source-snapshot/v2" in excinfo.value.detail


def test_an_inspected_file_that_has_been_deleted_is_refused_not_skipped(tmp_path: Path) -> None:
    """Deletion is the strongest form of the staleness the inspection exists to catch.

    If a missing locator merely dropped out of the recomputation, the cheapest way to
    keep an owner inspection "current" would be to delete the file it claims to have
    inspected — the inspection would stay green about a file that no longer exists.

    Both entry points are covered because `#562` left this the ONLY check that opens an
    inspected file. `stamp-inspection` is the one an operator runs by hand, and stamping
    an identity over an unopenable path would launder the unfalsifiable prose the whole
    inspection exists to replace.
    """
    _build_world(tmp_path)
    (tmp_path / "owner.py").unlink()

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "missing_file"
    assert "owner.py" in excinfo.value.detail

    with pytest.raises(FreezeError) as stamping:
        stamp_inspection(tmp_path, INSPECTION_REL)

    assert stamping.value.code == "missing_file"


def test_a_raw_page_whose_issue_node_is_null_is_refused(tmp_path: Path) -> None:
    """`{"data":{"repository":{"issue":null}}}` is what a backend returns for an issue the
    token cannot see. It is a syntactically perfect response carrying no source at all,
    so re-derivation must refuse it rather than fold an empty issue into the snapshot."""
    _build_world(tmp_path)
    _edit_raw_page(tmp_path, 514, lambda payload: payload["data"]["repository"].__setitem__("issue", None))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "raw_response_incomplete"
    assert "no issue node" in excinfo.value.detail


def test_a_raw_page_that_reports_no_has_next_page_cannot_prove_completeness(tmp_path: Path) -> None:
    """Absence must refuse, not default to "complete".

    `hasNextPage` is the ONLY field that distinguishes a full enumeration from a
    truncated one. Treating a missing `pageInfo` as a finished page would let a
    stripped-down response assert completeness by saying nothing.
    """
    _build_world(tmp_path)
    _edit_raw_page(tmp_path, 514, lambda p: p["data"]["repository"]["issue"]["comments"].pop("pageInfo"))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "raw_response_incomplete"
    assert "hasNextPage" in excinfo.value.detail


def test_a_repeated_comment_node_makes_a_short_capture_look_complete(tmp_path: Path) -> None:
    """Duplicating one comment is how a short capture reaches its declared `totalCount`.

    With comment B dropped and comment A returned twice, the collected length equals
    `totalCount` and the count check passes — so the criterion sitting in B disappears
    from the frozen source with every arithmetic check green. Only node identity sees it.
    """
    _build_world(tmp_path, comments={514: _TWO_COMMENTS})
    _edit_raw_page(tmp_path, 514, lambda p: p["data"]["repository"]["issue"]["comments"]["nodes"][1].__setitem__("id", "C_a"))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "duplicate_comment"
    assert "C_a" in excinfo.value.detail


def test_an_issue_the_receipt_claims_but_captured_no_page_for_is_refused(tmp_path: Path) -> None:
    """A page-less issue re-derives to nothing, and nothing compares equal to nothing.

    Every declared count for it is zero and self-consistent, so without this floor an
    issue could be listed in the receipt with no captured evidence behind it at all.
    """
    _build_world(tmp_path)
    _edit_receipt(tmp_path, lambda receipt: receipt["issues"][0].__setitem__("pages", []))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "raw_response_incomplete"
    assert "no captured page" in excinfo.value.detail


def test_a_receipt_advertising_a_comment_set_the_raw_bytes_do_not_carry_is_refused(tmp_path: Path) -> None:
    """`comment_node_ids` is the receipt's own summary of what it captured.

    It is what a reader diffs across freezes to see which comments are new, so it must
    be the set the raw responses actually carry. Dropping one id there is a quiet way to
    make a comment invisible to every consumer that reads the summary instead of the bytes.
    """
    _build_world(tmp_path, comments={514: _TWO_COMMENTS})
    _edit_receipt(
        tmp_path,
        lambda receipt: [i.__setitem__("comment_node_ids", ["C_a"]) for i in receipt["issues"] if i["number"] == 514],
    )

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "receipt_comment_set_mismatch"


def test_a_raw_response_path_inside_the_repo_but_outside_the_raw_dir_is_refused(tmp_path: Path) -> None:
    """Repo containment alone is not enough.

    `../../../etc/hostname` is the loud escape; aiming a page at another artifact in the
    same repo is the quiet one. Here the receipt points its "captured bytes" at the
    snapshot itself — fully inside the repo root, so the repo-containment clause passes —
    which would let a hand-authored snapshot be re-derived from itself.
    """
    _build_world(tmp_path)
    _edit_receipt(tmp_path, lambda r: r["issues"][0]["pages"][0].__setitem__("raw_response_path", SNAPSHOT_REL))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "raw_response_escape"
    assert "spec/source-raw" in excinfo.value.detail


def test_a_receipt_that_does_not_assert_a_complete_enumeration_overall_is_refused(tmp_path: Path) -> None:
    """The per-issue flags and the whole-capture flag are separate assertions.

    An issue the capture never reached has no per-issue record to mark incomplete, so
    only the top-level flag can report "this capture did not finish".
    """
    _build_world(tmp_path)
    _edit_receipt(tmp_path, lambda receipt: receipt.__setitem__("pagination_complete", False))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "incomplete_pagination"
    assert "complete enumeration" in excinfo.value.detail


def test_a_page_with_no_raw_response_path_is_refused_before_rederivation(tmp_path: Path) -> None:
    """A page that names no bytes is a page with no evidence behind it.

    Left unchecked it would surface as a `KeyError` from inside the re-derivation
    loop — an unhandled crash, which `run_cli` deliberately does not render as a
    refusal — instead of this lane's stable code.
    """
    _build_world(tmp_path)
    _edit_receipt(tmp_path, lambda receipt: receipt["issues"][0]["pages"][0].pop("raw_response_path"))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "missing_raw_response"
    assert "no raw response path" in excinfo.value.detail


def test_a_snapshot_declaring_a_digest_its_own_content_does_not_imply_is_refused(tmp_path: Path) -> None:
    """`source_snapshot_sha256` is the anchor every clause id is derived from.

    Consumers cite that scalar rather than re-digesting the document, so a snapshot
    whose declared digest is not its content's would let the whole inventory be bound
    to a source nobody can reproduce.
    """
    _build_world(tmp_path)
    _edit_json(tmp_path / SNAPSHOT_REL, lambda payload: payload.__setitem__("source_snapshot_sha256", "0" * 64))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "snapshot_digest_mismatch"


def test_a_forged_clause_inventory_identity_is_refused_even_with_the_inventory_intact(tmp_path: Path) -> None:
    """The identity scalar is the handle downstream artifacts bind to.

    The crosswalk copies `clause_inventory_identity` and later re-checks it to detect
    drift. Forging it in the snapshot is how a crosswalk bound to an OLD inventory could
    be made to look current, so the scalar must be recomputed rather than believed.
    """
    _build_world(tmp_path)
    _edit_json(tmp_path / SNAPSHOT_REL, lambda payload: payload.__setitem__("clause_inventory_identity", "0" * 64))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "clause_identity_mismatch"


def test_a_capture_receipt_pointing_at_a_different_snapshot_is_refused(tmp_path: Path) -> None:
    """The receipt and the snapshot are separate files that must name the same source.

    A receipt left over from an earlier capture is internally perfect — its own identity
    reseals, its raw pages are on disk — and would otherwise vouch for a snapshot it
    never produced.
    """
    _build_world(tmp_path)
    _edit_receipt(tmp_path, lambda receipt: receipt.__setitem__("source_snapshot_sha256", "0" * 64))

    with pytest.raises(FreezeError) as excinfo:
        _validate(tmp_path)

    assert excinfo.value.code == "receipt_snapshot_mismatch"


def test_an_issue_with_criteria_only_in_comments_and_an_empty_body_is_still_refused(tmp_path: Path) -> None:
    """The per-issue clause floor is not enough on its own.

    Here #514 has a real clause — it just lives in a comment — so the issue-level
    `clause_count >= 1` floor passes. The body is where an issue's acceptance criteria
    are stated, and an empty one that slipped through would leave the matrix binding to
    a source unit that can never carry a criterion.
    """
    with pytest.raises(FreezeError) as excinfo:
        _build_world(
            tmp_path,
            bodies={514: "", 515: "- x", 518: "- y"},
            comments={514: [_comment("C_a", "- criterion stated in a comment instead")]},
        )

    assert excinfo.value.code == "empty_body_unit"
    assert "514" in excinfo.value.detail


def test_a_tilde_fenced_paste_does_not_mint_criteria_out_of_its_bullet_lines(tmp_path: Path) -> None:
    """Pasted evidence is not acceptance criteria, and `~~~` is markdown's other fence.

    A tilde fence carries none of the backtick fence's info-string restriction, so it
    opens unconditionally. If it did not, the log lines below would each be normalized
    into a clause and the crosswalk's per-clause floor would demand a disposition for
    every line of somebody's pasted output.
    """
    fenced = "- a real criterion\n~~~\n- pasted log line\n- another pasted log line\n~~~"
    _build_world(tmp_path, bodies={514: fenced, 515: "- x", 518: "- y"})

    assert _validate(tmp_path)["ok"] is True
    snapshot = json.loads((tmp_path / SNAPSHOT_REL).read_text(encoding="utf-8"))
    body_unit = snapshot["clause_inventory"]["issues"][0]["source_units"][0]
    excerpts = [clause["excerpt"] for clause in body_unit["clauses"]]
    assert body_unit["source_unit_id"] == "514:body"
    assert excerpts[0] == "- a real criterion"
    assert excerpts[1].startswith("~~~")
    assert "another pasted log line" in excerpts[1]
    assert len(excerpts) == 2


def _cli(monkeypatch, *args: str) -> int:
    monkeypatch.setattr(sys, "argv", ["validate_issue_source_freeze.py", *args])
    return main()


def _cli_args(tmp_path: Path, command: str, *extra: str) -> list[str]:
    return [command, "--repo-root", str(tmp_path), "--snapshot", SNAPSHOT_REL,
            "--inspection", INSPECTION_REL, "--freeze-receipt", FREEZE_REL, *extra]


def test_the_cli_validate_command_exits_zero_and_prints_the_bound_identities(tmp_path, monkeypatch, capsys) -> None:
    """The CLI is what a gate actually invokes, so its exit code and its stdout payload
    are the contract — not `run_validate`'s return value, which no gate can see."""
    _build_world(tmp_path)

    code = _cli(monkeypatch, *_cli_args(tmp_path, "validate", "--require-issues", "514", "515", "518"))

    payload = yaml.safe_load(capsys.readouterr().out)
    assert code == 0
    assert payload["ok"] is True
    assert payload["issues"] == [514, 515, 518]
    assert payload["snapshot_rederived_from_raw_responses"] is True


def test_the_cli_renders_a_refusal_as_a_nonzero_exit_with_a_machine_readable_code(tmp_path, monkeypatch, capsys) -> None:
    """A refusal that exits 0 is worse than no validator: every gate downstream reads
    the exit code, and a tidy JSON body on stdout is invisible to all of them."""
    _build_world(tmp_path)
    (tmp_path / "owner.py").unlink()

    code = _cli(monkeypatch, *_cli_args(tmp_path, "validate", "--require-issues", "514", "515", "518"))

    captured = capsys.readouterr()
    payload = yaml.safe_load(captured.out)
    assert code == 1
    assert payload["ok"] is False
    assert payload["error"] == "missing_file"
    assert payload["detail"].startswith("owner.py does not exist")
    assert "REFUSED (missing_file)" in captured.err


def test_the_cli_defaults_cover_the_three_protected_issues_without_being_asked(tmp_path, monkeypatch, capsys) -> None:
    """`--require-issues` defaults to the protected set on purpose.

    If the default were empty, the ordinary invocation — the one a gate copies out of
    the module docstring — would validate a freeze while requiring no issue at all, and
    a snapshot missing #518 entirely would pass it.
    """
    _build_world(tmp_path, numbers=(514, 515))

    code = _cli(monkeypatch, *_cli_args(tmp_path, "validate"))

    assert code == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["error"] == "missing_protected_issue"
    assert "518" in payload["detail"]


def test_each_cli_subcommand_dispatches_to_its_own_action(tmp_path: Path, monkeypatch, capsys) -> None:
    """One dispatch table maps four command names to four different effects.

    A table that routed two names to the same action would still exit 0 on both, so the
    proof has to be each command's distinct observable effect: `stamp-inspection`
    rewrites the inspection identity and writes nothing else, `freeze` writes the receipt
    and leaves the crosswalk alone, `refreeze` also rebinds the crosswalk.
    """
    _build_world(tmp_path)
    crosswalk_rel = "spec/crosswalk.json"
    _write_json(tmp_path / crosswalk_rel, {"schema": "evidence-boundary-crosswalk/v1"})
    (tmp_path / FREEZE_REL).unlink()

    assert _cli(monkeypatch, *_cli_args(tmp_path, "stamp-inspection")) == 0
    stamped = yaml.safe_load(capsys.readouterr().out)
    assert stamped["stamped"] == INSPECTION_REL
    assert not (tmp_path / FREEZE_REL).exists(), "stamp-inspection must not write the freeze receipt"

    assert _cli(monkeypatch, *_cli_args(tmp_path, "freeze", "--require-issues", "514", "515", "518")) == 0
    frozen = yaml.safe_load(capsys.readouterr().out)
    assert frozen["written"] == FREEZE_REL
    assert (tmp_path / FREEZE_REL).is_file()
    assert "source_identity" not in json.loads((tmp_path / crosswalk_rel).read_text(encoding="utf-8"))

    args = _cli_args(tmp_path, "refreeze", "--require-issues", "514", "515", "518")
    assert _cli(monkeypatch, *args, "--crosswalk", crosswalk_rel) == 0
    refrozen = yaml.safe_load(capsys.readouterr().out)
    assert refrozen["crosswalk_rebound"]["rebound"] is True
    bound = json.loads((tmp_path / crosswalk_rel).read_text(encoding="utf-8"))["source_identity"]
    assert bound["freeze_identity"] == refrozen["freeze_identity"]


def test_the_script_entrypoint_propagates_the_refusal_exit_code(tmp_path: Path, monkeypatch) -> None:
    """Run as `__main__`, not imported — the guard itself is the thing under test.

    `raise SystemExit(main())` is one line, and dropping the `main()` result from it
    (`main()` alone, or `raise SystemExit(0)`) makes every refusal in this module exit 0
    while still printing a perfectly correct refusal body. No in-process call of `main()`
    can catch that, so this drives the file the way a shell does.
    """
    _build_world(tmp_path)
    (tmp_path / SNAPSHOT_REL).unlink()
    monkeypatch.setattr(sys, "argv", ["validate_issue_source_freeze.py", *_cli_args(tmp_path, "validate")])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(
            str(REPO_ROOT / "scripts" / "issue" / "validate_issue_source_freeze.py"),
            run_name="__main__",
        )

    assert excinfo.value.code == 1
