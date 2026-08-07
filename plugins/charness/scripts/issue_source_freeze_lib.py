"""Freeze verification for the captured issue source and its owner inspection.

A frozen snapshot is only worth anything if a later reader can prove it is the same
source the matrix was built against, and that it was produced by the capture
adapter rather than typed by hand. Both halves matter and they fail differently:

- Hand-authoring is the quiet one. A JSON file with the right shape and plausible
  bodies passes every schema check ever written. The defense is that the capture
  receipt asserts a digest for every raw backend response, the raw bodies are on
  disk, and this module RE-DERIVES the snapshot from those bodies plus re-proves
  completeness from them.

  BE PRECISE ABOUT WHAT THAT BUYS. Every link — raw page, receipt, snapshot — is a
  file the same agent can write, so this is not unforgeability. What it catches is a
  snapshot edited WITHOUT correspondingly editing the raw pages, a raw page edited
  after the fact, a receipt field edited outside the re-derivation path, and a capture
  that is internally consistent but demonstrably short. Forging all of them
  consistently is possible; it is simply no longer something that happens by accident
  or by a single convenient edit. The `hand_authored: false` flag is self-attestation
  and proves nothing on its own — it is a declaration, and the re-derivation is the
  check.
- Staleness is the loud one, and only if someone checks. The freeze receipt binds
  the snapshot digest, the clause-inventory identity, the normalization policy
  version, and the owner-inspection identity together. Change any one and the bind
  fails; nothing is allowed to drift alone.

The owner inspection is checked the same way: each declared locator carries the
digest of the file at inspection time, so "I read `closeout_bundle_lib.py`" becomes
falsifiable the moment that file changes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.closeout_refusal_lib import RefusalError
from scripts.issue_source_normalize_lib import (
    build_clause_inventory,
    clause_inventory_identity,
    sha256_payload,
    sha256_text,
)

SNAPSHOT_SCHEMA = "issue-source-snapshot/v1"
CAPTURE_RECEIPT_SCHEMA = "issue-source-capture-receipt/v1"
INSPECTION_SCHEMA = "issue-source-owner-inspection/v1"
FREEZE_RECEIPT_SCHEMA = "issue-source-freeze-receipt/v1"

# Fields the capture CLI stamps onto the receipt AFTER its identity is computed, so
# they cannot participate in it. They are excluded here too, or the recomputation
# below would fail on every honestly produced receipt.
_RECEIPT_IDENTITY_EXCLUDED = frozenset(
    {"receipt_identity", "snapshot_path", "snapshot_file_sha256", "raw_response_dir"}
)


class FreezeError(RefusalError):
    """A freeze that cannot be proven current, complete, or adapter-produced."""


def load_json(repo_root: Path, rel: str, expected_schema: str | None = None) -> dict[str, Any]:
    path = repo_root / rel
    if not path.is_file():
        raise FreezeError("missing_file", f"{rel} does not exist")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise FreezeError("invalid_json", f"{rel}: {exc}") from exc
    if expected_schema is not None and payload.get("schema") != expected_schema:
        raise FreezeError(
            "wrong_schema", f"{rel} declares schema {payload.get('schema')!r}, expected {expected_schema!r}"
        )
    return payload


def file_sha256(repo_root: Path, rel: str) -> str:
    path = repo_root / rel
    if not path.is_file():
        raise FreezeError("missing_file", f"{rel} does not exist")
    return sha256_text(path.read_text(encoding="utf-8"))


def _rederive_issue(receipt_issue: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Rebuild one issue's source from its captured raw responses.

    This is the anti-hand-authoring check. It reads the SAME parse path the capture
    used, from bytes on disk whose digests the receipt already committed to, so the
    only way to make the re-derivation agree with a snapshot is to have actually
    captured it.
    """
    comments: list[dict[str, Any]] = []
    issue_node: dict[str, Any] | None = None
    seen_ids: set[str] = set()
    last_has_next = True
    raw_dir = receipt_issue.get("raw_response_dir")
    for page in receipt_issue["pages"]:
        rel = page["raw_response_path"]
        _require_contained(repo_root, rel, raw_dir)
        raw = (repo_root / rel).read_text(encoding="utf-8") if (repo_root / rel).is_file() else None
        if raw is None:
            raise FreezeError("missing_raw_response", f"{rel} referenced by the capture receipt is absent")
        actual = sha256_text(raw)
        if actual != page["raw_response_sha256"]:
            raise FreezeError(
                "raw_response_digest_mismatch",
                f"{rel} digest {actual[:12]} != receipt {page['raw_response_sha256'][:12]}",
            )
        node = json.loads(raw).get("data", {}).get("repository", {}).get("issue")
        if node is None:
            raise FreezeError("raw_response_incomplete", f"{rel} carries no issue node")
        # Compare the WHOLE per-issue identity across pages, not just the number.
        # The derived body/title/state come from the LAST page, so a number-only check
        # let an attacker APPEND a page — same number, zero comments, matching
        # totalCount and hasNextPage=false, a forged body — and have it silently
        # override the honest page still sitting on disk beside it. Every other check
        # passed: real digests, real containment, no duplicate ids, counts agreeing.
        identity = {key: node.get(key) for key in ("number", "title", "state", "body")}
        identity["totalCount"] = (node.get("comments") or {}).get("totalCount")
        if issue_node is not None and identity != _page_identity(issue_node):
            raise FreezeError(
                "raw_response_issue_drift",
                f"{rel} carries a different issue snapshot than a previous page "
                f"(differing: {sorted(k for k, v in identity.items() if v != _page_identity(issue_node).get(k))}); "
                "the pages are not one enumeration of one issue",
            )
        issue_node = node
        page_info = node["comments"].get("pageInfo") or {}
        if "hasNextPage" not in page_info:
            raise FreezeError("raw_response_incomplete", f"{rel} reports no hasNextPage; completeness is unprovable")
        last_has_next = bool(page_info["hasNextPage"])
        for comment in node["comments"]["nodes"]:
            comment_id = comment["id"]
            if comment_id in seen_ids:
                raise FreezeError("duplicate_comment", f"{rel} repeats comment node {comment_id}")
            seen_ids.add(comment_id)
            comments.append(
                {
                    "id": comment_id,
                    "body": comment.get("body") or "",
                    "created_at": comment.get("createdAt") or "",
                    "author": ((comment.get("author") or {}).get("login")) or "",
                }
            )
    if issue_node is None:
        raise FreezeError("raw_response_incomplete", f"issue {receipt_issue['number']} has no captured page")
    # Completeness is re-proven FROM THE RAW BYTES, not re-read from the receipt's own
    # integers. Checking `captured_comment_count == comment_total_count` only proves two
    # receipt fields agree with each other, which a truncated capture can satisfy simply
    # by declaring both numbers equal — the exact failure this module exists to catch.
    total = issue_node["comments"]["totalCount"]
    if last_has_next:
        raise FreezeError(
            "incomplete_pagination",
            f"issue {issue_node['number']}'s final captured page still reports hasNextPage",
        )
    if len(comments) != total:
        raise FreezeError(
            "count_mismatch",
            f"issue {issue_node['number']}: raw responses carry {len(comments)} comments but "
            f"report totalCount={total}",
        )
    declared_ids = receipt_issue.get("comment_node_ids")
    if declared_ids is not None and list(declared_ids) != [comment["id"] for comment in comments]:
        raise FreezeError(
            "receipt_comment_set_mismatch",
            f"issue {issue_node['number']}: the receipt's comment node ids are not the ones the raw responses carry",
        )
    return {
        "number": issue_node["number"],
        "title": issue_node.get("title") or "",
        "state": issue_node.get("state") or "",
        "body": issue_node.get("body") or "",
        "comment_total_count": total,
        "comments": comments,
    }


def _page_identity(node: dict[str, Any]) -> dict[str, Any]:
    identity = {key: node.get(key) for key in ("number", "title", "state", "body")}
    identity["totalCount"] = (node.get("comments") or {}).get("totalCount")
    return identity


def _require_contained(repo_root: Path, rel: str, raw_dir: str | None) -> None:
    """Refuse a raw-response path that escapes the repo or its declared raw directory.

    The path comes from the receipt, which is a file under review — so it is untrusted
    input. Without this, a receipt could point its "captured bytes" at any readable file
    on the machine and the re-derivation would faithfully verify against whatever it
    found there.
    """
    candidate = (repo_root / rel).resolve()
    root = repo_root.resolve()
    if not candidate.is_relative_to(root):
        raise FreezeError("raw_response_escape", f"{rel} resolves outside the repo root")
    if not raw_dir:
        # Absence REFUSES rather than degrading. The receipt is untrusted input, so
        # omitting the key would otherwise switch off the stronger containment clause
        # with no refusal anywhere — a defense disarmed by deleting one field.
        raise FreezeError(
            "missing_raw_response_dir",
            "the capture receipt declares no raw_response_dir for this issue, so its raw "
            "response paths cannot be contained",
        )
    if not candidate.is_relative_to((repo_root / raw_dir).resolve()):
        raise FreezeError("raw_response_escape", f"{rel} resolves outside the declared raw response dir {raw_dir}")


def verify_capture(repo_root: Path, snapshot: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    """Re-derive the snapshot from captured raw responses and compare."""
    from scripts.issue_source_normalize_lib import build_source_document

    expected_identity = sha256_payload(
        {key: value for key, value in receipt.items() if key not in _RECEIPT_IDENTITY_EXCLUDED}
    )
    if receipt.get("receipt_identity") != expected_identity:
        raise FreezeError(
            "capture_receipt_identity_mismatch",
            "the capture receipt's declared identity is not its own content's; a field outside the "
            "re-derivation path (adapter, normalization policy, requested numbers, page cursors) "
            "has been edited since capture",
        )
    if receipt.get("hand_authored") is not False:
        raise FreezeError("hand_authored_capture", "the capture receipt does not assert adapter authorship")
    if not receipt.get("pagination_complete"):
        raise FreezeError("incomplete_pagination", "the capture receipt does not assert a complete enumeration")
    for issue in receipt["issues"]:
        if not issue.get("pagination_complete"):
            raise FreezeError("incomplete_pagination", f"issue {issue['number']} enumeration is incomplete")
        if issue["captured_comment_count"] != issue["comment_total_count"]:
            raise FreezeError(
                "count_mismatch",
                f"issue {issue['number']} captured {issue['captured_comment_count']} of "
                f"{issue['comment_total_count']} comments",
            )
        for page in issue["pages"]:
            if "raw_response_path" not in page:
                raise FreezeError("missing_raw_response", f"issue {issue['number']} page has no raw response path")

    rederived = [_rederive_issue(issue, repo_root) for issue in receipt["issues"]]
    document = build_source_document(receipt["repository"], rederived)
    inventory = build_clause_inventory(document)
    if document != snapshot["source_document"]:
        raise FreezeError(
            "snapshot_not_rederivable",
            "the snapshot does not match the document rebuilt from the captured raw responses",
        )
    if inventory["source_snapshot_sha256"] != snapshot["source_snapshot_sha256"]:
        raise FreezeError("snapshot_digest_mismatch", "the snapshot digest is not the one its content implies")
    # The WHOLE inventory, not just its identity scalar. The crosswalk's matrix floor
    # reads `snapshot["clause_inventory"]` directly to decide which clauses must carry a
    # disposition, so verifying only the summary digest left the block a reader actually
    # consumes unchecked: deleting one clause record from it (identity scalar untouched)
    # silently removed that clause from the set anything downstream could require.
    if inventory != snapshot["clause_inventory"]:
        raise FreezeError(
            "clause_inventory_mismatch",
            "the snapshot's clause inventory is not the one its source document implies",
        )
    identity = clause_inventory_identity(inventory)
    if identity != snapshot["clause_inventory_identity"]:
        raise FreezeError("clause_identity_mismatch", "the clause inventory identity does not match the source")
    if receipt["source_snapshot_sha256"] != snapshot["source_snapshot_sha256"]:
        raise FreezeError("receipt_snapshot_mismatch", "the capture receipt names a different snapshot digest")
    return {"source_snapshot_sha256": snapshot["source_snapshot_sha256"], "clause_inventory_identity": identity}


def verify_issue_coverage(snapshot: dict[str, Any], required: list[int]) -> None:
    """Every protected issue must be present with a non-empty clause inventory.

    Omitting one is the cheapest way to make the whole lane look complete: the
    matrix validates, the crosswalk authorizes, and the issue that was never
    captured simply has no criteria to fail. A per-issue floor is what makes the
    omission louder than the work.
    """
    present = {issue["number"] for issue in snapshot["source_document"]["issues"]}
    missing = sorted(set(required) - present)
    if missing:
        raise FreezeError("missing_protected_issue", f"snapshot omits required issues {missing}")
    for issue in snapshot["clause_inventory"]["issues"]:
        if issue["number"] not in required:
            continue
        if issue["clause_count"] < 1:
            raise FreezeError("empty_clause_inventory", f"issue {issue['number']} normalized to zero clauses")
        for unit in issue["source_units"]:
            if unit["empty"] and unit["kind"] == "body":
                raise FreezeError("empty_body_unit", f"issue {issue['number']} body normalized to zero clauses")


def verify_inspection(repo_root: Path, inspection: dict[str, Any]) -> str:
    """Recompute every inspected locator's digest and the inspection identity.

    "I inspected the closeout planner" is unfalsifiable prose; "I inspected it at
    this digest" stops being true the moment the file changes, which is exactly when
    the inspection's conclusions stop being safe to build on.
    """
    locators = inspection.get("locators") or []
    if not locators:
        raise FreezeError("empty_inspection", "the owner inspection declares no locators")
    for locator in locators:
        actual = file_sha256(repo_root, locator["path"])
        if actual != locator["sha256"]:
            raise FreezeError(
                "stale_inspection",
                f"{locator['path']} is now {actual[:12]}, inspected at {locator['sha256'][:12]}",
            )
    identity = inspection_identity(inspection)
    if inspection.get("inspection_identity") != identity:
        raise FreezeError("inspection_identity_mismatch", "the declared inspection identity is not its content's")
    return identity


def inspection_identity(inspection: dict[str, Any]) -> str:
    return sha256_payload(
        {
            "schema": inspection.get("schema"),
            "issues": sorted(inspection.get("issues") or []),
            "locators": sorted(
                ({"path": item["path"], "role": item["role"], "sha256": item["sha256"]} for item in inspection["locators"]),
                key=lambda item: item["path"],
            ),
        }
    )


def build_freeze_receipt(
    *,
    snapshot_path: str,
    snapshot: dict[str, Any],
    capture_receipt_path: str,
    capture_receipt: dict[str, Any],
    inspection_path: str,
    inspection: dict[str, Any],
    reviewed_input_identity: str,
) -> dict[str, Any]:
    receipt = {
        "schema": FREEZE_RECEIPT_SCHEMA,
        "repository": snapshot["repository"],
        "issues": sorted(snapshot["requested_numbers"]),
        "snapshot_path": snapshot_path,
        "source_snapshot_sha256": snapshot["source_snapshot_sha256"],
        "clause_inventory_identity": snapshot["clause_inventory_identity"],
        "normalization_policy": snapshot["source_document"]["normalization_policy"],
        "capture_receipt_path": capture_receipt_path,
        "capture_receipt_identity": capture_receipt["receipt_identity"],
        "inspection_path": inspection_path,
        "inspection_identity": inspection["inspection_identity"],
        "inspected_locators": sorted(item["path"] for item in inspection["locators"]),
        "reviewed_input_identity": reviewed_input_identity,
    }
    receipt["freeze_identity"] = sha256_payload(receipt)
    return receipt


def reviewed_input_identity(snapshot: dict[str, Any], inspection: dict[str, Any]) -> str:
    """One identity over everything a reviewer of this freeze actually read.

    Deliberately spans BOTH the source and the owner inspection. Binding only the
    source would let the owner map go stale under an unchanged snapshot — the
    reviewed inputs are the pair, so the identity has to be over the pair.
    """
    return sha256_payload(
        {
            "source_snapshot_sha256": snapshot["source_snapshot_sha256"],
            "clause_inventory_identity": snapshot["clause_inventory_identity"],
            "normalization_policy": snapshot["source_document"]["normalization_policy"],
            "inspection_identity": inspection["inspection_identity"],
        }
    )


def verify_freeze_receipt(
    *, freeze: dict[str, Any], snapshot: dict[str, Any], capture_receipt: dict[str, Any], inspection: dict[str, Any]
) -> None:
    expected_identity = sha256_payload({key: value for key, value in freeze.items() if key != "freeze_identity"})
    if freeze.get("freeze_identity") != expected_identity:
        raise FreezeError("freeze_identity_mismatch", "the freeze receipt identity is not its own content's")
    checks = (
        ("source_snapshot_sha256", freeze.get("source_snapshot_sha256"), snapshot["source_snapshot_sha256"]),
        ("clause_inventory_identity", freeze.get("clause_inventory_identity"), snapshot["clause_inventory_identity"]),
        ("normalization_policy", freeze.get("normalization_policy"), snapshot["source_document"]["normalization_policy"]),
        ("capture_receipt_identity", freeze.get("capture_receipt_identity"), capture_receipt["receipt_identity"]),
        ("inspection_identity", freeze.get("inspection_identity"), inspection["inspection_identity"]),
        (
            "reviewed_input_identity",
            freeze.get("reviewed_input_identity"),
            reviewed_input_identity(snapshot, inspection),
        ),
    )
    for field, declared, actual in checks:
        if declared != actual:
            raise FreezeError("stale_freeze_receipt", f"{field} is {declared!r} but the current inputs imply {actual!r}")
