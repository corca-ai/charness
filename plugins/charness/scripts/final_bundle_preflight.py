#!/usr/bin/env python3
"""Plan the final local proof bundle without executing or writing it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
_lib = import_repo_module(__file__, "scripts.final_bundle_preflight_lib")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--critique-path", action="append", default=[])
    parser.add_argument("--behavior-channel", action="append", default=[])
    parser.add_argument("--paths", nargs="*", default=None, help="Diagnostic-only explicit paths; never certifies a full bundle.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else repo_root / args.manifest
    payload = _lib.build_plan(
        repo_root,
        manifest_path=manifest,
        critique_paths=args.critique_path,
        behavior_channels=args.behavior_channel,
        explicit_paths=args.paths,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(_lib.render_text(payload), end="")
    return 0 if payload["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
