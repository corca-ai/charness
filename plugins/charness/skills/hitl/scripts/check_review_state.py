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
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter.load_adapter


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose HITL review state should be checked")
    parser.add_argument("--session-id", required=True, help="HITL session identifier")
    parser.add_argument("--phase", choices=("pre-edit", "cursor-advance"), required=True, help="Review phase to check")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    try:
        session = _hitl_lib.load_session(repo_root, adapter, args.session_id)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    errors = _hitl_lib.check_runtime_phase(session, args.phase)
    payload = {
        "status": "blocked" if errors else "pass",
        "phase": args.phase,
        "session_id": session["session_id"],
        "errors": errors,
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
