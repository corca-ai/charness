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
_hitl_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.hitl_review_artifact_lib")
check_chunk_contract = _hitl_lib.check_chunk_contract


def _read_chunk(args: argparse.Namespace) -> str:
    if args.chunk_file is not None:
        return args.chunk_file.read_text(encoding="utf-8")
    if args.chunk_text is not None:
        return args.chunk_text
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Self-check that a HITL review chunk includes Agent Assessment and "
            "Recommended Disposition before asking the human to decide."
        )
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--chunk-file", type=Path)
    source.add_argument("--chunk-text")
    args = parser.parse_args()
    chunk_text = _read_chunk(args)
    errors = check_chunk_contract(chunk_text)
    payload = {
        "status": "blocked" if errors else "pass",
        "errors": errors,
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
