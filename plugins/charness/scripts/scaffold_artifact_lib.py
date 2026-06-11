from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path


def validator_command(
    *,
    repo_root: Path,
    script_file: str | Path,
    script_names: Sequence[str],
    artifact_path: str | None = None,
) -> str:
    if not script_names:
        raise ValueError("script_names must not be empty")

    # Repo-local validators win so a consumer repo cites the same strict check
    # as its broad gate; installed-plugin validators are fallback-only.
    suffix = f" --paths {artifact_path}" if artifact_path else ""
    for script_name in script_names:
        repo_local = repo_root / "scripts" / script_name
        if repo_local.is_file():
            return f"python3 scripts/{script_name} --repo-root .{suffix}"
    for ancestor in Path(script_file).resolve().parents:
        for script_name in script_names:
            candidate = ancestor / "scripts" / script_name
            if candidate.is_file():
                return f"python3 {candidate} --repo-root .{suffix}"
    raise FileNotFoundError(f"{script_names[0]} not found in installed Charness layout")


def current_pointer_payload(
    *,
    repo_root: Path,
    output_dir: Path,
    date_text: str,
    title: str,
    template: str,
    validator_command: str,
) -> dict[str, object]:
    artifact_path = output_dir / "latest.md"
    write_path, write_role, symlink_target = current_pointer_write_path(repo_root, artifact_path)
    return {
        "artifact_path": str(artifact_path),
        "artifact_role": "current_pointer",
        "write_artifact_path": write_path,
        "write_artifact_role": write_role,
        "current_pointer_symlink_target": symlink_target,
        "date": date_text,
        "title": title,
        "template": template,
        "validator_command": validator_command,
    }


def portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def current_pointer_write_path(repo_root: Path, artifact_path: Path) -> tuple[str, str, str | None]:
    absolute_artifact_path = repo_root / artifact_path
    if not absolute_artifact_path.is_symlink():
        return str(artifact_path), "current_pointer", None
    raw_target = os.readlink(absolute_artifact_path)
    target_path = Path(raw_target)
    if not target_path.is_absolute():
        target_path = absolute_artifact_path.parent / target_path
    return portable_path(repo_root, target_path), "current_pointer_target", raw_target


def emit_payload_main(
    payload_for: Callable[..., dict[str, object]],
    *,
    artifact_label: str,
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help=f"Repo root to scaffold the {artifact_label} artifact into")
    parser.add_argument("--title", help=f"Title for the scaffolded {artifact_label} artifact")
    parser.add_argument("--json", action="store_true", help="Emit the payload as JSON instead of the rendered template")
    args = parser.parse_args()

    payload = payload_for(args.repo_root.resolve(), title=args.title)
    if args.json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(str(payload["template"]))
    return 0
