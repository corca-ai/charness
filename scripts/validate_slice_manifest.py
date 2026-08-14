#!/usr/bin/env python3
"""Validate a checked-in post-push slice manifest without remote side effects."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime_bootstrap import repo_root_from_script  # noqa: E402
from scripts.slice_manifest_lib import ManifestError, validate_manifest  # noqa: E402
from yaml_output import emit_yaml  # noqa: E402

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
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    manifest_path = (args.manifest or (repo_root / DEFAULT_MANIFEST)).resolve()
    try:
        result = validate_manifest(repo_root, manifest_path, verify_current=args.verify_current)
    except ManifestError as exc:
        result = {"status": "invalid", "manifest": str(manifest_path), "error": exc.as_dict()}
        if exc.code == "missing_manifest" and args.manifest is None:
            result["error"]["message"] += " The default baseline is source-checkout-only; supply --manifest from a source checkout."
        # The retired human line prefixed this with REFUSED; the `invalid` status plus
        # the error's own code/path/message carry the same refusal.
        emit_yaml(result)
        return 1
    result["manifest"] = str(manifest_path.relative_to(repo_root))
    # Unconditional YAML. The retired human line was a projection of `status`,
    # `slice_id`, `target_sha`, `reader_root_count`, and `parity_pair_count`.
    emit_yaml(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
