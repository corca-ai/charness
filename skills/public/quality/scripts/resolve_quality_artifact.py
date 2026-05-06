#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
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
            sys.modules.setdefault(spec.name, module)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter.load_adapter
_artifact_naming = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.artifact_naming_lib")
dated_artifact_filename = _artifact_naming.dated_artifact_filename
slugify = _artifact_naming.slugify


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def _current_pointer_state(repo_root: Path, current_path: Path) -> dict[str, object]:
    if not current_path.is_symlink():
        return {
            "current_pointer_is_symlink": False,
            "current_pointer_target_path": None,
            "current_pointer_target_exists": None,
        }
    raw_target = os.readlink(current_path)
    target_path = Path(raw_target)
    if not target_path.is_absolute():
        target_path = current_path.parent / target_path
    return {
        "current_pointer_is_symlink": True,
        "current_pointer_target_path": _portable_path(repo_root, target_path),
        "current_pointer_target_exists": target_path.exists(),
    }


def payload_for(repo_root: Path, *, slug: str, intent: str, artifact_date: dt.date) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    output_dir = Path(adapter["data"]["output_dir"])
    current_path = output_dir / "latest.md"
    record_path = output_dir / dated_artifact_filename(slugify(slug), artifact_date=artifact_date)
    pointer_state = _current_pointer_state(repo_root, repo_root / current_path)
    if intent == "record":
        write_path = str(record_path)
        write_role = "durable_record"
        update_current = True
    else:
        target = pointer_state.get("current_pointer_target_path")
        write_path = target if pointer_state["current_pointer_is_symlink"] and isinstance(target, str) else str(current_path)
        write_role = "current_pointer_target" if pointer_state["current_pointer_is_symlink"] else "current_pointer"
        update_current = False
    payload = {
        "skill_id": "quality",
        "intent": intent,
        "slug": slugify(slug),
        "date": artifact_date.isoformat(),
        "record_artifact_path": str(record_path),
        "record_artifact_supported": True,
        "current_artifact_path": str(current_path),
        "write_artifact_path": write_path,
        "write_artifact_role": write_role,
        "update_current_pointer_after_write": update_current,
    }
    payload.update(pointer_state)
    return payload


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="quality resolve_quality_artifact")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--slug", default="quality-review")
    parser.add_argument("--intent", choices=("current", "record"), default="current")
    parser.add_argument("--date")
    try:
        args = parser.parse_args()
        artifact_date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
        payload = payload_for(
            args.repo_root.resolve(),
            slug=args.slug,
            intent=args.intent,
            artifact_date=artifact_date,
        )
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
