#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()

_BOOTSTRAP_LIB = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.markdown_preview_bootstrap_lib"
)
DEFAULT_OUTPUT_PATH = _BOOTSTRAP_LIB.DEFAULT_OUTPUT_PATH
DEFAULT_WIDTHS = _BOOTSTRAP_LIB.DEFAULT_WIDTHS
scaffold_markdown_preview = _BOOTSTRAP_LIB.scaffold_markdown_preview
run_markdown_preview = _BOOTSTRAP_LIB.run_markdown_preview


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--width", action="append", type=int, default=[])
    parser.add_argument("--artifact-dir", default=_BOOTSTRAP_LIB.DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--changed-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.execute and args.dry_run:
        print("--execute cannot be combined with --dry-run", file=sys.stderr)
        return 1

    repo_root = args.repo_root.resolve()
    payload = scaffold_markdown_preview(
        repo_root,
        output_path=args.output,
        widths=args.width or list(DEFAULT_WIDTHS),
        artifact_dir=args.artifact_dir,
        on_change_only=args.changed_only,
        dry_run=args.dry_run,
        force=args.force,
    )

    if args.execute and payload["config_path"] is not None:
        returncode, preview_payload, stderr = run_markdown_preview(
            repo_root, config_path=str(payload["config_path"])
        )
        payload["execution"] = {
            "status": "ran" if returncode == 0 else "failed",
            "returncode": returncode,
            "preview": preview_payload,
            "stderr": stderr or None,
        }
        if returncode != 0:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return returncode

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
