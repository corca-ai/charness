#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
_hitl_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.review.hitl_review_artifact_lib")
emit_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output").emit_yaml
check_chunk_contract = _hitl_lib.check_chunk_contract


class ChunkInputError(Exception):
    """The chunk could not be read at all — an invocation error, not a verdict."""


def _read_chunk(args: argparse.Namespace) -> str:
    if args.chunk_file is not None:
        try:
            return args.chunk_file.read_text(encoding="utf-8")
        except OSError as exc:
            # An unreadable path used to escape as a traceback with exit 1 — the
            # same code a well-formed `blocked` verdict returns, so "you gave me
            # nothing" and "the chunk violates the contract" were indistinguishable.
            raise ChunkInputError(f"chunk file could not be read: {exc}") from exc
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
    try:
        chunk_text = _read_chunk(args)
    except ChunkInputError as exc:
        emit_yaml({"status": "error", "errors": [str(exc)]})
        return 2
    errors = check_chunk_contract(chunk_text)
    payload = {
        "status": "blocked" if errors else "pass",
        "errors": errors,
    }
    emit_yaml(payload)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
