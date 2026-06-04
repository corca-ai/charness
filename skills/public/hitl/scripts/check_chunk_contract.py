#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


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
    source.add_argument("--chunk-file", type=Path, help="Path to chunk file to validate")
    source.add_argument("--chunk-text", help="Chunk text passed inline")
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
