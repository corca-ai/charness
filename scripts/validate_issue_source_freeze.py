#!/usr/bin/env python3
"""Validate (or write) the issue-source freeze receipt.

`freeze` writes the receipt binding snapshot, capture receipt, and owner inspection
together. `validate` proves that bind still holds AND that the snapshot is
re-derivable from the captured raw responses — a hand-authored or edited snapshot
fails there, not at a schema check it would happily pass.

    python3 scripts/validate_issue_source_freeze.py validate --repo-root . \\
        --snapshot charness-artifacts/spec/2026-08-07-issue-514-515-518-source.json \\
        --inspection charness-artifacts/spec/2026-08-07-issue-514-515-518-owner-inspection.json \\
        --freeze-receipt charness-artifacts/spec/2026-08-07-issue-514-515-518-freeze-receipt.json \\
        --require-issues 514 515 518
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_freeze_lib = import_repo_module(__file__, "scripts.issue_source_freeze_lib")
_refusal_lib = import_repo_module(__file__, "scripts.closeout_refusal_lib")
CAPTURE_RECEIPT_SCHEMA = _freeze_lib.CAPTURE_RECEIPT_SCHEMA
FREEZE_RECEIPT_SCHEMA = _freeze_lib.FREEZE_RECEIPT_SCHEMA
INSPECTION_SCHEMA = _freeze_lib.INSPECTION_SCHEMA
SNAPSHOT_SCHEMA = _freeze_lib.SNAPSHOT_SCHEMA
FreezeError = _freeze_lib.FreezeError
build_freeze_receipt = _freeze_lib.build_freeze_receipt
inspection_identity = _freeze_lib.inspection_identity
load_json = _freeze_lib.load_json
reviewed_input_identity = _freeze_lib.reviewed_input_identity
verify_capture = _freeze_lib.verify_capture
verify_freeze_receipt = _freeze_lib.verify_freeze_receipt
verify_inspection = _freeze_lib.verify_inspection
verify_issue_coverage = _freeze_lib.verify_issue_coverage

DEFAULT_PROTECTED = (514, 515, 518)


def capture_receipt_path_for(snapshot_rel: str) -> str:
    return f"{snapshot_rel.removesuffix('.json')}-capture-receipt.json"


def load_inputs(repo_root: Path, snapshot_rel: str, inspection_rel: str):
    snapshot = load_json(repo_root, snapshot_rel, SNAPSHOT_SCHEMA)
    capture_rel = capture_receipt_path_for(snapshot_rel)
    capture = load_json(repo_root, capture_rel, CAPTURE_RECEIPT_SCHEMA)
    inspection = load_json(repo_root, inspection_rel, INSPECTION_SCHEMA)
    return snapshot, capture_rel, capture, inspection


def run_validate(
    repo_root: Path, snapshot_rel: str, inspection_rel: str, freeze_rel: str, required: list[int]
) -> dict[str, object]:
    snapshot, capture_rel, capture, inspection = load_inputs(repo_root, snapshot_rel, inspection_rel)
    verify_issue_coverage(snapshot, required)
    capture_identity = verify_capture(repo_root, snapshot, capture)
    verify_inspection(repo_root, inspection)
    freeze = load_json(repo_root, freeze_rel, FREEZE_RECEIPT_SCHEMA)
    verify_freeze_receipt(freeze=freeze, snapshot=snapshot, capture_receipt=capture, inspection=inspection)
    declared = sorted(freeze.get("issues") or [])
    if declared != sorted(required):
        raise FreezeError("freeze_issue_set_mismatch", f"freeze receipt covers {declared}, required {sorted(required)}")
    return {
        "ok": True,
        "snapshot_path": snapshot_rel,
        "capture_receipt_path": capture_rel,
        "inspection_path": inspection_rel,
        "freeze_receipt_path": freeze_rel,
        "issues": declared,
        "source_snapshot_sha256": capture_identity["source_snapshot_sha256"],
        "clause_inventory_identity": capture_identity["clause_inventory_identity"],
        "reviewed_input_identity": freeze["reviewed_input_identity"],
        "snapshot_rederived_from_raw_responses": True,
    }


def run_freeze(
    repo_root: Path, snapshot_rel: str, inspection_rel: str, freeze_rel: str, required: list[int]
) -> dict[str, object]:
    snapshot, capture_rel, capture, inspection = load_inputs(repo_root, snapshot_rel, inspection_rel)
    verify_issue_coverage(snapshot, required)
    verify_capture(repo_root, snapshot, capture)
    verify_inspection(repo_root, inspection)
    receipt = build_freeze_receipt(
        snapshot_path=snapshot_rel,
        snapshot=snapshot,
        capture_receipt_path=capture_rel,
        capture_receipt=capture,
        inspection_path=inspection_rel,
        inspection=inspection,
        reviewed_input_identity=reviewed_input_identity(snapshot, inspection),
    )
    path = repo_root / freeze_rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"ok": True, "written": freeze_rel, "freeze_identity": receipt["freeze_identity"]}


def stamp_inspection(repo_root: Path, inspection_rel: str) -> dict[str, object]:
    """Fill in each locator's current digest and the derived inspection identity.

    Digests are STAMPED, never hand-typed. A hand-typed digest is a number an agent
    can produce without opening the file, which is precisely the claim the digest is
    supposed to make falsifiable.
    """
    path = repo_root / inspection_rel
    inspection = load_json(repo_root, inspection_rel, INSPECTION_SCHEMA)
    for locator in inspection["locators"]:
        locator["sha256"] = _freeze_lib.file_sha256(repo_root, locator["path"])
    inspection["inspection_identity"] = inspection_identity(inspection)
    path.write_text(json.dumps(inspection, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"ok": True, "stamped": inspection_rel, "inspection_identity": inspection["inspection_identity"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "freeze", "stamp-inspection"))
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--snapshot", default="charness-artifacts/spec/2026-08-07-issue-514-515-518-source.json")
    parser.add_argument(
        "--inspection", default="charness-artifacts/spec/2026-08-07-issue-514-515-518-owner-inspection.json"
    )
    parser.add_argument(
        "--freeze-receipt", default="charness-artifacts/spec/2026-08-07-issue-514-515-518-freeze-receipt.json"
    )
    parser.add_argument("--require-issues", type=int, nargs="+", default=list(DEFAULT_PROTECTED))
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    commands = {
        "stamp-inspection": lambda: stamp_inspection(repo_root, args.inspection),
        "freeze": lambda: run_freeze(
            repo_root, args.snapshot, args.inspection, args.freeze_receipt, list(args.require_issues)
        ),
        "validate": lambda: run_validate(
            repo_root, args.snapshot, args.inspection, args.freeze_receipt, list(args.require_issues)
        ),
    }
    return _refusal_lib.run_cli(
        "validate_issue_source_freeze", commands[args.command], refusals=(FreezeError,)
    )


if __name__ == "__main__":
    raise SystemExit(main())
