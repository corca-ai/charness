#!/usr/bin/env python3
"""Plan or execute the local phases of one opt-in closeout bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
_lib = import_repo_module(__file__, "scripts.closeout_bundle_lib")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Workflow:\n"
            "  1. Run the required-argument command without --execute to inspect the plan.\n"
            "  2. Confirm the manifest and critique path are the intended frozen inputs.\n"
            "  3. Rerun with --execute; a completed result is local verification only.\n"
            "\n"
            "Status and non-claims:\n"
            "  ready = plan readiness; completed = bounded local phases plus receipt.\n"
            "  Behavior channels are recorded, not run. Fresh-eye, provider, installed-\n"
            "  consumer, remote-CI, push, and release proof remain unclaimed.\n"
            "\n"
            "Example:\n"
            "  python3 scripts/closeout_bundle.py --manifest <slice-manifest.json> "
            "--bundle-id <bundle-id> --critique-path <critique.md> "
            "--behavior-channel 'behavior=<operator proof command>'"
        ),
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--critique-path", action="append", required=True)
    parser.add_argument("--behavior-channel", action="append", required=True)
    parser.add_argument("--execute", action="store_true", help="Run the bounded local phases; default is a no-write plan.")
    parser.add_argument(
        "--receipt-path",
        type=Path,
        help=(
            "Repository-relative JSON receipt path intended for check-in; only written after a completed execute. "
            "Default: charness-artifacts/goals/<bundle-id>.json."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else repo_root / args.manifest
    try:
        if args.execute:
            payload = _lib.execute(
                repo_root,
                manifest_path=manifest,
                critique_paths=args.critique_path,
                behavior_channels=args.behavior_channel,
                bundle_id=args.bundle_id,
            )
            if payload["status"] == "completed":
                receipt = args.receipt_path or Path("charness-artifacts/goals") / f"{args.bundle_id}.json"
                payload["receipt_path"] = str(_lib.write_receipt(repo_root, payload, output_path=receipt).relative_to(repo_root))
        else:
            payload = _lib.build_plan(
                repo_root,
                manifest_path=manifest,
                critique_paths=args.critique_path,
                behavior_channels=args.behavior_channel,
                bundle_id=args.bundle_id,
            )
    except (_lib.BundleError, OSError, ValueError) as exc:
        payload = {
            "kind": _lib.KIND,
            "schema_version": _lib.SCHEMA_VERSION,
            "status": "blocked",
            "mode": "execute" if args.execute else "dry-run",
            "bundle_id": args.bundle_id,
            "error": str(exc),
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("status") in {"ready", "completed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
