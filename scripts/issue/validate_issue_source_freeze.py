#!/usr/bin/env python3
"""Validate (or write) the issue-source freeze receipt.

`freeze` writes the receipt binding snapshot, capture receipt, and owner inspection
together. `validate` proves that bind still holds AND that the snapshot is
re-derivable from the captured raw responses — a hand-authored or edited snapshot
fails there, not at a schema check it would happily pass.

    python3 scripts/issue/validate_issue_source_freeze.py validate --repo-root . \\
        --snapshot charness-artifacts/spec/2026-08-07-issue-514-515-518-source.json \\
        --inspection charness-artifacts/spec/2026-08-07-issue-514-515-518-owner-inspection.json \\
        --freeze-receipt charness-artifacts/spec/2026-08-07-issue-514-515-518-freeze-receipt.json \\
        --require-issues 514 515 518
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_freeze_lib = import_repo_module(__file__, "scripts.issue.issue_source_freeze_lib")
_refusal_lib = import_repo_module(__file__, "scripts.review.closeout_refusal_lib")
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
DEFAULT_CROSSWALK = "charness-artifacts/spec/2026-08-07-evidence-boundary-crosswalk.json"
# The four fields the crosswalk copies from the freeze receipt. Named once so the
# rebind and the crosswalk's own staleness check cannot disagree about the set.
BOUND_IDENTITY_FIELDS = (
    "source_snapshot_sha256",
    "clause_inventory_identity",
    "reviewed_input_identity",
    "freeze_identity",
)


def capture_receipt_path_for(snapshot_rel: str) -> str:
    return f"{snapshot_rel.removesuffix('.json')}-capture-receipt.json"


def load_inputs(repo_root: Path, snapshot_rel: str, inspection_rel: str):
    snapshot = load_json(repo_root, snapshot_rel, SNAPSHOT_SCHEMA)
    capture_rel = capture_receipt_path_for(snapshot_rel)
    capture = load_json(repo_root, capture_rel, CAPTURE_RECEIPT_SCHEMA)
    inspection = _freeze_lib.load_inspection(repo_root, inspection_rel)
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


def preflight(
    repo_root: Path,
    snapshot_rel: str,
    inspection_rel: str,
    required: list[int],
    *,
    require_inspection_identity: bool = True,
):
    """Every read-only refusal a write path owes, run BEFORE the first byte is written.

    This exists because fixing one writer's ordering did not fix the class. `refreeze`
    writes three checked-in artifacts in sequence and each later step could still refuse
    after an earlier one had written — demonstrated: `refreeze --require-issues 514 515`
    stamped the inspection, wrote the freeze receipt, rebound the closeout-authorization
    crosswalk, and THEN raised `freeze_issue_set_mismatch`. A refusing command had mutated
    all three.

    The issue-set check is the one that has to move rather than merely run early: it lived
    only in `run_validate`, which is `refreeze`'s LAST step, so it was structurally
    incapable of protecting the writes that preceded it.

    `require_inspection_identity=False` is what `refreeze` needs, and the distinction is
    the whole reason this is a parameter rather than a fixed sequence. A STALE inspection
    identity is `refreeze`'s input condition — repairing it is the command's purpose — so
    enforcing it in the preflight would refuse every legitimate refreeze. The per-locator
    rules still run, because those are never something a refreeze is entitled to fix
    silently: a retired pin, an escaping path, or a missing file must stop the run before
    it launders them into a freshly stamped identity.
    """
    snapshot, capture_rel, capture, inspection = load_inputs(repo_root, snapshot_rel, inspection_rel)
    verify_issue_coverage(snapshot, required)
    verify_capture(repo_root, snapshot, capture)
    if require_inspection_identity:
        verify_inspection(repo_root, inspection)
    else:
        _freeze_lib.verify_locators(repo_root, inspection)
    requested = sorted(snapshot.get("requested_numbers") or [])
    if requested != sorted(required):
        raise FreezeError(
            "freeze_issue_set_mismatch",
            f"the snapshot covers {requested}, required {sorted(required)}; refusing before writing",
        )
    return snapshot, capture_rel, capture, inspection


def run_freeze(
    repo_root: Path, snapshot_rel: str, inspection_rel: str, freeze_rel: str, required: list[int]
) -> dict[str, object]:
    snapshot, capture_rel, capture, inspection = preflight(repo_root, snapshot_rel, inspection_rel, required)
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
    """Derive the inspection identity from the locator set.

    Under `#562` this no longer stamps a per-locator content digest — that pin is
    retired, so there is nothing per-file left to fill in.

    It enforces the SAME per-locator rules the reader does, via the shared
    `verify_locators`, and it enforces them BEFORE writing. Both halves of that matter: a
    writer holding a weaker rule than its reader exits 0 on an artifact `validate` will
    refuse, and a writer that checks after writing leaves `refreeze` having rewritten the
    file it then refused.
    """
    path = repo_root / inspection_rel
    inspection = _freeze_lib.load_inspection(repo_root, inspection_rel)
    _freeze_lib.verify_locators(repo_root, inspection)
    inspection["inspection_identity"] = inspection_identity(inspection)
    path.write_text(json.dumps(inspection, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"ok": True, "stamped": inspection_rel, "inspection_identity": inspection["inspection_identity"]}


def run_refreeze(
    repo_root: Path,
    snapshot_rel: str,
    inspection_rel: str,
    freeze_rel: str,
    required: list[int],
    crosswalk_rel: str,
) -> dict[str, object]:
    """Re-stamp, re-freeze, and re-bind the crosswalk in ONE command.

    Re-freezing is now RARE rather than routine. It used to fire on every code change,
    because the owner inspection pinned working-tree digests of the very files a slice
    edits; `#562` retired that pin after measuring 0 of 5 true positives, so what
    remains stales only when something real moves — the captured source, the
    normalization policy, or the locator set itself. The atomicity below is what still
    earns this subcommand: left as three separate steps, the third (copying four
    identity fields into the crosswalk) has no tool at all, and the session that built
    this validator performed it six times as an untested shell heredoc.

    That is the failure this subcommand exists to remove: a tool whose own maintenance
    ritual is hand-executed is unfinished, and the hand-executed step is the one that
    silently drifts. Atomic here means the crosswalk is never left bound to a
    superseded freeze — the rebind happens in the same run that produced the receipt.
    """
    # Read-only first, and NOT as a courtesy: everything below writes a checked-in
    # artifact, and a refusal discovered after the first write leaves the repo in a state
    # no command claimed to produce.
    preflight(repo_root, snapshot_rel, inspection_rel, required, require_inspection_identity=False)
    stamped = stamp_inspection(repo_root, inspection_rel)
    frozen = run_freeze(repo_root, snapshot_rel, inspection_rel, freeze_rel, required)
    rebound = rebind_crosswalk(repo_root, freeze_rel, crosswalk_rel)
    validated = run_validate(repo_root, snapshot_rel, inspection_rel, freeze_rel, required)
    return {
        "ok": True,
        "inspection_identity": stamped["inspection_identity"],
        "freeze_identity": frozen["freeze_identity"],
        "crosswalk_rebound": rebound,
        "validated": validated,
    }


def rebind_crosswalk(repo_root: Path, freeze_rel: str, crosswalk_rel: str) -> dict[str, object]:
    """Point the crosswalk's `source_identity` at the current freeze receipt.

    A no-op when the crosswalk is absent: `refreeze` must stay usable in a repo that
    has a freeze but no crosswalk yet, which is every repo before Slice 0.
    """
    path = repo_root / crosswalk_rel
    if not path.is_file():
        return {"rebound": False, "reason": f"{crosswalk_rel} does not exist"}
    freeze = load_json(repo_root, freeze_rel, FREEZE_RECEIPT_SCHEMA)
    crosswalk = json.loads(path.read_text(encoding="utf-8"))
    identity = crosswalk.setdefault("source_identity", {})
    changed = {}
    for field in BOUND_IDENTITY_FIELDS:
        if identity.get(field) != freeze[field]:
            changed[field] = freeze[field]
        identity[field] = freeze[field]
    path.write_text(json.dumps(crosswalk, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"rebound": True, "path": crosswalk_rel, "changed_fields": sorted(changed)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "freeze", "stamp-inspection", "refreeze"))
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--snapshot", default="charness-artifacts/spec/2026-08-07-issue-514-515-518-source.json")
    parser.add_argument(
        "--inspection", default="charness-artifacts/spec/2026-08-07-issue-514-515-518-owner-inspection.json"
    )
    parser.add_argument(
        "--freeze-receipt", default="charness-artifacts/spec/2026-08-07-issue-514-515-518-freeze-receipt.json"
    )
    parser.add_argument("--require-issues", type=int, nargs="+", default=list(DEFAULT_PROTECTED))
    parser.add_argument("--crosswalk", default=DEFAULT_CROSSWALK, help="Crosswalk rebound by `refreeze`")
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
        "refreeze": lambda: run_refreeze(
            repo_root, args.snapshot, args.inspection, args.freeze_receipt,
            list(args.require_issues), args.crosswalk,
        ),
    }
    return _refusal_lib.run_cli(
        "validate_issue_source_freeze", commands[args.command], refusals=(FreezeError,)
    )


if __name__ == "__main__":
    raise SystemExit(main())
