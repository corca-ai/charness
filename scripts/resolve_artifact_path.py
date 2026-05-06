#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_artifact_naming_lib_module = import_repo_module(__file__, "scripts.artifact_naming_lib")
current_artifact_filename = _scripts_artifact_naming_lib_module.current_artifact_filename
dated_artifact_filename = _scripts_artifact_naming_lib_module.dated_artifact_filename
record_artifact_supported = _scripts_artifact_naming_lib_module.record_artifact_supported
slugify = _scripts_artifact_naming_lib_module.slugify


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--date")
    parser.add_argument(
        "--intent",
        choices=("record", "current"),
        help=(
            "`record` returns the dated durable artifact as the edit target when supported; "
            "`current` returns the current pointer or its symlink target as the edit target."
        ),
        default="current",
    )
    return parser.parse_args()


def load_adapter(repo_root: Path, skill_id: str) -> dict[str, object]:
    resolver = next(
        (
            candidate
            for candidate in (
                repo_root / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py",
                repo_root / "skills" / skill_id / "scripts" / "resolve_adapter.py",
                REPO_ROOT / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py",
                REPO_ROOT / "skills" / skill_id / "scripts" / "resolve_adapter.py",
            )
            if candidate.is_file()
        ),
        None,
    )
    if resolver is None:
        raise SystemExit(
            "No skill adapter resolver found in the consumer repo or installed Charness plugin "
            f"for skill `{skill_id}`"
        )
    completed = subprocess.run(
        ["python3", str(resolver), "--repo-root", str(repo_root)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or f"{resolver} failed")
    return json.loads(completed.stdout)


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


def _current_write_path(repo_root: Path, current_path: Path, pointer_state: dict[str, object]) -> str:
    target = pointer_state.get("current_pointer_target_path")
    if pointer_state.get("current_pointer_is_symlink") and isinstance(target, str):
        return target
    return str(current_path.relative_to(repo_root))


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root, args.skill_id)
    data = adapter.get("data", {})
    if not isinstance(data, dict) or not isinstance(data.get("output_dir"), str):
        raise SystemExit("adapter data must include output_dir")
    artifact_date = date.fromisoformat(args.date) if args.date else date.today()
    slug = slugify(args.slug)
    record_name = dated_artifact_filename(slug, artifact_date=artifact_date)
    output_dir = Path(data["output_dir"])
    current_path = output_dir / current_artifact_filename(args.skill_id)
    records_supported = record_artifact_supported(args.skill_id)
    record_path = output_dir / record_name if records_supported else None
    absolute_current_path = repo_root / current_path
    pointer_state = _current_pointer_state(repo_root, absolute_current_path)
    if args.intent == "record" and record_path is not None:
        write_path = str(record_path)
        write_role = "durable_record"
        update_current_pointer_after_write = True
    else:
        write_path = _current_write_path(repo_root, absolute_current_path, pointer_state)
        write_role = "current_pointer_target" if pointer_state["current_pointer_is_symlink"] else "current_pointer"
        update_current_pointer_after_write = False
    payload = {
        "skill_id": args.skill_id,
        "slug": slug,
        "date": artifact_date.isoformat(),
        "intent": args.intent,
        "record_artifact_path": str(record_path) if record_path is not None else None,
        "record_artifact_supported": records_supported,
        "current_artifact_path": str(current_path),
        "write_artifact_path": write_path,
        "write_artifact_role": write_role,
        "update_current_pointer_after_write": update_current_pointer_after_write,
        "frontmatter": {
            "artifact_kind": "record",
            "status": "current",
            "created": artifact_date.isoformat(),
            "slug": slug,
        },
    }
    payload.update(pointer_state)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
