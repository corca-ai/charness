#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_verification_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.gates_support.announcement_verification_lib")
DELIVERY_VERIFICATION_STATUSES = _verification_lib.DELIVERY_VERIFICATION_STATUSES
evaluate_delivery_verification = _verification_lib.evaluate_delivery_verification
evaluate_delivery_kind_agreement = _verification_lib.evaluate_delivery_kind_agreement
fail_delivery_kind_mismatch = _verification_lib.fail_delivery_kind_mismatch
fail_missing_delivery_verification = _verification_lib.fail_missing_delivery_verification
requires_delivery_kind_agreement = _verification_lib.requires_delivery_kind_agreement
requires_delivery_verification = _verification_lib.requires_delivery_verification
resolve_manual_disposition = _verification_lib.resolve_manual_disposition
run_readback_probe = _verification_lib.run_readback_probe

_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapters.announcement_adapter_lib")
DELIVERY_KINDS = _adapter_lib.DELIVERY_KINDS
load_announcement_adapter = _adapter_lib.load_announcement_adapter
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapters.adapter_version_verdict"
)
normalize_delivery_kind = _adapter_lib.normalize_delivery_kind


def _portable_path(repo_root: Path, value: str) -> str:
    path = Path(value)
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return f"external-path:{path.name}"


def _path_provenance(repo_root: Path, value: str) -> dict[str, str]:
    path = Path(value)
    if not path.is_absolute():
        return {"kind": "repo-relative"}
    try:
        path.resolve().relative_to(repo_root)
    except ValueError:
        return {"kind": "external-path", "basename": path.name}
    return {"kind": "repo-root-relative"}


def _resolve_delivery_kind_check(args: argparse.Namespace, *, repo_root: Path) -> dict[str, object]:
    # GUARDED BEFORE the `except Exception` fallback below, deliberately. That fallback is
    # correct for a resolution FAILURE -- it records `adapter_resolved: False` and keeps
    # the disagreement typed and visible. It is wrong for a resolution that SUCCEEDED
    # while honoring nothing: there the payload carries a `delivery_kind` the repo never
    # wrote, and `requires_delivery_kind_agreement` then compares the recorded kind
    # against a charness default and can pass a mismatch the repo's own declaration would
    # have refused. Refusing keeps the fallback for the case it was written for.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_announcement_adapter, repo_root, adapter_name="announcement-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    try:
        adapter_delivery_kind = load_announcement_adapter(repo_root)["data"]["delivery_kind"]
    except Exception:  # noqa: BLE001 -- adapter resolution failure falls back to typed, visible trust
        return evaluate_delivery_kind_agreement(
            recorded_kind=args.delivery_kind, adapter_delivery_kind=None, adapter_resolved=False
        )
    check = evaluate_delivery_kind_agreement(
        recorded_kind=args.delivery_kind, adapter_delivery_kind=adapter_delivery_kind, adapter_resolved=True
    )
    if requires_delivery_kind_agreement(adapter_delivery_kind) and not check["agrees_with_recorded_kind"]:
        fail_delivery_kind_mismatch(recorded_kind=args.delivery_kind, adapter_delivery_kind=adapter_delivery_kind)
    return check


def _resolve_verification(args: argparse.Namespace, *, repo_root: Path) -> dict[str, str] | None:
    if args.verification_status and args.verification_status not in DELIVERY_VERIFICATION_STATUSES:
        raise SystemExit(
            f"--verification-status must be one of: {', '.join(DELIVERY_VERIFICATION_STATUSES)}"
        )
    if args.readback_probe_template:
        return run_readback_probe(
            probe_template=args.readback_probe_template,
            delivery_target=args.delivery_target,
            delivery_handle=args.delivery_handle,
            repo_root=repo_root,
        )
    return resolve_manual_disposition(
        status=args.verification_status,
        channel=args.verification_channel,
        reason=args.verification_reason,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root that owns the announcement record log")
    parser.add_argument("--head-commit", required=True, help="HEAD commit sha covered by this announcement record")
    parser.add_argument(
        "--delivery-kind", default="none", type=normalize_delivery_kind, choices=DELIVERY_KINDS,
        help=f"Delivery channel kind for this announcement; one of: {', '.join(DELIVERY_KINDS)} (case-insensitive)",
    )
    parser.add_argument("--delivery-target", default="", help="Delivery target identifier such as a channel name, URL, or release tag")
    parser.add_argument("--delivery-handle", default="", help="Opaque delivery handle captured from the backend (e.g. a message ts/url/id), when available")
    parser.add_argument("--verification-status", default="", help=f"Typed delivery verification status; one of: {', '.join(DELIVERY_VERIFICATION_STATUSES)}. Required for delivery_kind=human-backend unless --readback-probe-template supplies one.")
    parser.add_argument("--verification-channel", default="", help="Verification channel identifier (e.g. adapter-probe, human-observation)")
    parser.add_argument("--verification-reason", default="", help="Free-text reason for a non-confirmed verification status")
    parser.add_argument("--readback-probe-template", default="", help="Adapter-declared post_delivery_readback_probe command template ({delivery_target}/{delivery_handle} substituted); when set, its result becomes the recorded verification and --verification-* flags are ignored")
    parser.add_argument("--artifact-path", default="charness-artifacts/announcement/latest.md", help="Path to the announcement artifact to record (repo-relative preferred)")
    parser.add_argument("--commits", nargs="*", default=[], help="Commit shas included in this announcement window")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    delivery_kind_check = _resolve_delivery_kind_check(args, repo_root=repo_root)
    verification = _resolve_verification(args, repo_root=repo_root)
    if requires_delivery_verification(args.delivery_kind) and not evaluate_delivery_verification(verification)["ok"]:
        fail_missing_delivery_verification(args.delivery_kind)

    state_dir = repo_root / ".charness" / "announcement"
    state_dir.mkdir(parents=True, exist_ok=True)
    record_path = state_dir / "announcements.jsonl"
    record = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "head_commit": args.head_commit,
        "delivery_kind": args.delivery_kind,
        "delivery_target": args.delivery_target,
        "delivery_handle": args.delivery_handle,
        "artifact_path": _portable_path(repo_root, args.artifact_path),
        "artifact_path_provenance": _path_provenance(repo_root, args.artifact_path),
        "commits": args.commits,
        "verification": verification,
        "delivery_kind_check": delivery_kind_check,
    }
    with record_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    sys.stdout.write(f"{record_path.relative_to(repo_root).as_posix()}\n")


if __name__ == "__main__":
    main()
