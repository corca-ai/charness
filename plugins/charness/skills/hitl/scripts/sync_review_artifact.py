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
_sync_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.hitl_review_artifact_lib")
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_current_pointer_writer = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.current_pointer_writer_lib")
# Command output is unconditionally YAML since the 2026-08-14 --json removal. SKILL.md
# teaches both of this script's invocations, so its stdout is a command surface, not an
# artifact -- the durable artifact it syncs is written by `_sync_lib`, not printed here.
_render_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output").render_yaml
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
    sys.stdout.write(_render_yaml(payload))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
