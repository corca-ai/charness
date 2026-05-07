#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.worktree_doctor_lib")
run_doctor = _lib.run_doctor
render_doctor_text = _lib.render_doctor_text
emit_payload = _lib.emit_payload
PASS = _lib.PASS


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a git worktree's readiness for mutate-phase work.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of human text.")
    args = parser.parse_args()

    payload = run_doctor(args.repo_root)
    emit_payload(payload, json_mode=args.json, renderer=render_doctor_text)
    return 0 if payload.get("status") == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
