#!/usr/bin/env python3
"""Validate a checked-in post-push slice manifest without remote side effects."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime_bootstrap import repo_root_from_script  # noqa: E402
from scripts.slice_manifest_lib import ManifestError, validate_manifest  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)
DEFAULT_MANIFEST = "charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a captured Charness slice manifest offline. The default baseline artifact is "
            "source-checkout-only; installed/provider execution is not claimed. In a plugin-only "
            "layout, supply a source-checkout manifest with --manifest."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--verify-current", action="store_true", help="Also compare captured reader/parity identities with current files.")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable result.")
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    manifest_path = (args.manifest or (repo_root / DEFAULT_MANIFEST)).resolve()
    try:
        result = validate_manifest(repo_root, manifest_path, verify_current=args.verify_current)
    except ManifestError as exc:
        result = {"status": "invalid", "manifest": str(manifest_path), "error": exc.as_dict()}
        if args.json:
            if exc.code == "missing_manifest" and args.manifest is None:
                result["error"]["message"] += " The default baseline is source-checkout-only; supply --manifest from a source checkout."
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        else:
            detail = str(exc)
            if exc.code == "missing_manifest" and args.manifest is None:
                detail += " The default baseline is source-checkout-only; supply --manifest from a source checkout."
            print(f"slice-manifest: REFUSED [{exc.code}] {exc.path}: {detail}", file=sys.stderr)
        return 1
    result["manifest"] = str(manifest_path.relative_to(repo_root))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(
            "slice-manifest: structurally-valid-captured-record "
            f"{result['slice_id']} target={result['target_sha']} "
            f"reader_roots={result['reader_root_count']} parity_pairs={result['parity_pair_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
