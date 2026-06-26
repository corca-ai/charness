#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_artifact_naming_lib_module = import_repo_module(__file__, "scripts.artifact_naming_lib")
ArtifactClassError = _scripts_artifact_naming_lib_module.ArtifactClassError
artifact_class_from_adapter = _scripts_artifact_naming_lib_module.artifact_class_from_adapter
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


def _refresh_current_pointer_argv(skill_id: str, record_path: Path) -> list[str]:
    helper = Path(__file__).resolve().parent / "refresh_current_pointer.py"
    return [
        "python3",
        str(helper),
        "--repo-root",
        ".",
        "--skill-id",
        skill_id,
        "--record-artifact-path",
        str(record_path),
        "--execute",
    ]


def payload_for(
    repo_root: Path,
    skill_id: str,
    slug_text: str,
    *,
    intent: str = "current",
    artifact_date: date | None = None,
    adapter: dict[str, object] | None = None,
) -> dict[str, object]:
    repo_root = repo_root.resolve()
    adapter = adapter or load_adapter(repo_root, skill_id)
    data = adapter.get("data", {})
    if not isinstance(data, dict) or not isinstance(data.get("output_dir"), str):
        raise SystemExit("adapter data must include output_dir")
    artifact_date = artifact_date or date.today()
    slug = slugify(slug_text)
    record_name = dated_artifact_filename(slug, artifact_date=artifact_date)
    output_dir = Path(data["output_dir"])
    artifact_filename = adapter.get("artifact_filename")
    current_filename = (
        artifact_filename if isinstance(artifact_filename, str) else current_artifact_filename(skill_id)
    )
    current_path = output_dir / current_filename
    try:
        artifact_class = artifact_class_from_adapter(adapter)
    except ArtifactClassError as exc:
        raise SystemExit(str(exc)) from exc
    records_supported = record_artifact_supported(artifact_class)
    record_path = output_dir / record_name if records_supported else None
    absolute_current_path = repo_root / current_path
    pointer_state = _current_pointer_state(repo_root, absolute_current_path)
    if intent == "record" and record_path is not None:
        write_path = str(record_path)
        write_role = "durable_record"
        update_current_pointer_after_write = True
        refresh_argv = _refresh_current_pointer_argv(skill_id, record_path)
        refresh_command = shlex.join(refresh_argv)
    else:
        write_path = _current_write_path(repo_root, absolute_current_path, pointer_state)
        write_role = "current_pointer_target" if pointer_state["current_pointer_is_symlink"] else "current_pointer"
        update_current_pointer_after_write = False
        refresh_argv = None
        refresh_command = None
    payload = {
        "skill_id": skill_id,
        "artifact_class": artifact_class,
        "slug": slug,
        "date": artifact_date.isoformat(),
        "intent": intent,
        "artifact_path": str(current_path),
        "record_artifact_path": str(record_path) if record_path is not None else None,
        "record_artifact_supported": records_supported,
        "current_artifact_path": str(current_path),
        "write_artifact_path": write_path,
        "write_artifact_role": write_role,
        "update_current_pointer_after_write": update_current_pointer_after_write,
        "refresh_current_pointer_argv": refresh_argv,
        "refresh_current_pointer_command": refresh_command,
        "frontmatter": {
            "artifact_kind": "record",
            "status": "current",
            "created": artifact_date.isoformat(),
            "slug": slug,
        },
    }
    payload.update(pointer_state)
    return payload


def main() -> int:
    args = parse_args()
    artifact_date = date.fromisoformat(args.date) if args.date else None
    payload = payload_for(
        args.repo_root,
        args.skill_id,
        args.slug,
        intent=args.intent,
        artifact_date=artifact_date,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
