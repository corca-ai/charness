#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_resolve_artifact_path = import_repo_module(__file__, "scripts.resolve_artifact_path")
load_adapter = _resolve_artifact_path.load_adapter

_artifact_naming = import_repo_module(__file__, "scripts.artifact_naming_lib")
ArtifactClassError = _artifact_naming.ArtifactClassError
artifact_class_from_adapter = _artifact_naming.artifact_class_from_adapter
current_artifact_filename = _artifact_naming.current_artifact_filename
record_artifact_supported = _artifact_naming.record_artifact_supported


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--record-artifact-path", type=Path, required=True)
    parser.add_argument("--strategy", choices=("auto", "copy", "symlink"), default="auto")
    parser.add_argument("--execute", action="store_true", help="Apply the pointer refresh. Defaults to dry-run.")
    parser.add_argument(
        "--replace-file",
        action="store_true",
        help="Allow symlink strategy to replace an existing regular current pointer file.",
    )
    return parser.parse_args()


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _blocked(payload: dict[str, object], reason: str) -> int:
    payload["status"] = "blocked"
    payload["reason"] = reason
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 1


def _current_path(repo_root: Path, skill_id: str, adapter: dict[str, object]) -> Path:
    data = adapter.get("data", {})
    if not isinstance(data, dict) or not isinstance(data.get("output_dir"), str):
        raise SystemExit("adapter data must include output_dir")
    artifact_filename = adapter.get("artifact_filename")
    filename = artifact_filename if isinstance(artifact_filename, str) else current_artifact_filename(skill_id)
    return repo_root / Path(data["output_dir"]) / filename


def _resolve_record_path(repo_root: Path, raw_path: Path) -> Path:
    return raw_path.resolve() if raw_path.is_absolute() else (repo_root / raw_path).resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _same_symlink_target(current_path: Path, record_path: Path) -> bool:
    if not current_path.is_symlink():
        return False
    raw_target = Path(os.readlink(current_path))
    target_path = raw_target if raw_target.is_absolute() else current_path.parent / raw_target
    try:
        return target_path.resolve() == record_path.resolve()
    except FileNotFoundError:
        return False


def _copy_pointer(
    *,
    repo_root: Path,
    current_path: Path,
    record_path: Path,
    execute: bool,
    payload: dict[str, object],
) -> int:
    if current_path.is_symlink():
        return _blocked(payload, "copy strategy would follow an existing symlink; use symlink strategy")
    if current_path.exists() and current_path.is_dir():
        return _blocked(payload, "current pointer path is a directory")
    if current_path.exists() and current_path.read_bytes() == record_path.read_bytes():
        payload["status"] = "noop"
        payload["reason"] = "current pointer content already matches the record artifact"
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    payload["would_update"] = True
    if execute:
        current_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(record_path, current_path)
        payload["status"] = "updated"
    else:
        payload["status"] = "planned"
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _symlink_pointer(
    *,
    current_path: Path,
    record_path: Path,
    execute: bool,
    replace_file: bool,
    payload: dict[str, object],
) -> int:
    if current_path.exists() and not current_path.is_symlink() and not replace_file:
        return _blocked(payload, "symlink strategy would replace an existing file; pass --replace-file")
    if current_path.exists() and current_path.is_dir():
        return _blocked(payload, "current pointer path is a directory")
    if _same_symlink_target(current_path, record_path):
        payload["status"] = "noop"
        payload["reason"] = "current pointer symlink already targets the record artifact"
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    relative_target = os.path.relpath(record_path, start=current_path.parent)
    payload["current_pointer_target_path"] = Path(relative_target).as_posix()
    payload["would_update"] = True
    if execute:
        current_path.parent.mkdir(parents=True, exist_ok=True)
        if current_path.exists() or current_path.is_symlink():
            current_path.unlink()
        current_path.symlink_to(relative_target)
        payload["status"] = "updated"
    else:
        payload["status"] = "planned"
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root, args.skill_id)
    try:
        artifact_class = artifact_class_from_adapter(adapter)
    except ArtifactClassError as exc:
        raise SystemExit(str(exc)) from exc
    current_path = _current_path(repo_root, args.skill_id, adapter)
    record_path = _resolve_record_path(repo_root, args.record_artifact_path)
    strategy = "symlink" if args.strategy == "auto" and current_path.is_symlink() else args.strategy
    if strategy == "auto":
        strategy = "copy"

    payload: dict[str, object] = {
        "skill_id": args.skill_id,
        "artifact_class": artifact_class,
        "strategy": strategy,
        "execute": args.execute,
        "would_update": False,
        "current_artifact_path": _portable_path(repo_root, current_path),
        "record_artifact_path": _portable_path(repo_root, record_path),
        "current_pointer_is_symlink": current_path.is_symlink(),
        "current_pointer_target_path": None,
    }

    if not record_artifact_supported(artifact_class):
        return _blocked(payload, f"artifact_class `{artifact_class}` does not support dated records")
    nominal_current_parent = current_path.parent.resolve()
    if not _is_relative_to(nominal_current_parent, repo_root):
        return _blocked(payload, "current pointer path is outside repo_root")
    if not _is_relative_to(record_path, repo_root):
        return _blocked(payload, "record artifact path is outside repo_root")
    if not _is_relative_to(record_path, nominal_current_parent):
        return _blocked(payload, "record artifact path is outside the skill output directory")
    if not record_path.is_file():
        return _blocked(payload, "record artifact path does not exist or is not a file")
    nominal_current_path = nominal_current_parent / current_path.name
    if record_path == nominal_current_path:
        return _blocked(payload, "record artifact path is already the current pointer path")

    if strategy == "copy":
        return _copy_pointer(
            repo_root=repo_root,
            current_path=current_path,
            record_path=record_path,
            execute=args.execute,
            payload=payload,
        )
    return _symlink_pointer(
        current_path=current_path,
        record_path=record_path,
        execute=args.execute,
        replace_file=args.replace_file,
        payload=payload,
    )


if __name__ == "__main__":
    raise SystemExit(main())
