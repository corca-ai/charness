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
_sync_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.hitl_review_artifact_lib")
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_current_pointer_writer = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.current_pointer_writer_lib")
load_adapter = _resolve_adapter.load_adapter
write_current_pointer_text = _current_pointer_writer.write_current_pointer_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose HITL review artifact should be synced")
    parser.add_argument("--session-id", required=True, help="HITL session identifier")
    parser.add_argument("--check", action="store_true", help="Check artifact freshness without writing")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    try:
        session = _sync_lib.load_session(repo_root, adapter, args.session_id)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    artifact_path = repo_root / adapter["artifact_path"]
    errors = _sync_lib.check_artifact(repo_root, artifact_path, session) if args.check else []
    if not args.check:
        write_current_pointer_text(artifact_path, _sync_lib.render_artifact(repo_root, artifact_path, session))

    payload = {
        "status": "stale" if errors else ("current" if args.check else "synced"),
        "artifact_path": _sync_lib.portable_path(repo_root, artifact_path),
        "session_id": session["session_id"],
        "runtime_updated_at": session["runtime_updated_at"],
        "errors": errors,
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
