"""Build a repo containing a real frozen source and crosswalk, for ingress tests.

Shared rather than stubbed on purpose. The ingress tests are about ORDER — that a
refusal lands before a temp file, a comment, or a bump — and a stubbed authorizer
would let those tests pass while the real one was never wired in. Building the actual
freeze/crosswalk artifacts means the ingress is exercised against the same code path
production uses.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.issue.issue_source_capture_lib import build_snapshot_and_receipt, capture_issues
from scripts.issue.validate_issue_source_freeze import run_freeze, stamp_inspection

PROTECTED = (514, 515, 518)
CROSSWALK_REL = "charness-artifacts/spec/2026-08-07-evidence-boundary-crosswalk.json"
SNAPSHOT_REL = "charness-artifacts/spec/source.json"
INSPECTION_REL = "charness-artifacts/spec/inspection.json"
FREEZE_REL = "charness-artifacts/spec/freeze.json"
CAPABILITY = {
    "enumeration": "cursor", "page_size": 2, "has_next_field": "hasNextPage",
    "cursor_field": "endCursor", "total_count_field": "totalCount",
    "normalization": "github-issue-v1", "declared": False, "supported": True,
}


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_protected_world(tmp_path: Path, *, matrix_state: str = "bootstrap") -> dict:
    """Write a valid frozen source + crosswalk into `tmp_path`.

    `bootstrap` is the default because it is the state this repo is actually in, and
    the state in which every protected close must refuse.
    """
    queue = [
        json.dumps(
            {"data": {"repository": {"issue": {
                "number": number, "title": f"i{number}", "body": f"- criterion for {number}",
                "state": "OPEN", "url": "u",
                "comments": {"totalCount": 0, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": []},
            }}}}
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
        capability=CAPABILITY, captured=captured, raw_dir_rel="charness-artifacts/spec/source-raw",
    )
    for rel, text in raw_files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _write_json(tmp_path / SNAPSHOT_REL, snapshot)
    _write_json(tmp_path / "charness-artifacts/spec/source-capture-receipt.json", receipt)
    (tmp_path / "owner.py").write_text("# owner\n", encoding="utf-8")
    _write_json(
        tmp_path / INSPECTION_REL,
        {"schema": "issue-source-owner-inspection/v2", "issues": list(PROTECTED),
         "locators": [{"role": "owner", "path": "owner.py", "note": "n"}],
         "inspection_identity": ""},
    )
    stamp_inspection(tmp_path, INSPECTION_REL)
    run_freeze(tmp_path, SNAPSHOT_REL, INSPECTION_REL, FREEZE_REL, list(PROTECTED))
    freeze = json.loads((tmp_path / FREEZE_REL).read_text(encoding="utf-8"))
    crosswalk = {
        "schema": "evidence-boundary-crosswalk/v1",
        "matrix_state": matrix_state,
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
        "shared_projection": {"status": "undecided"},
        "issues": [
            {"number": number, "owner": "Charness-owned", "projection_dependency": "undecided",
             "criteria": [], "coverage": [], "source_clauses": []}
            for number in PROTECTED
        ],
    }
    _write_json(tmp_path / CROSSWALK_REL, crosswalk)
    return crosswalk
