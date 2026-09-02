#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

_scaffold_artifact_lib = import_repo_module(__file__, "scripts.core.scaffold_artifact_lib")
_resolver = import_repo_module(__file__, "scripts.artifacts.resolve_artifact_path")


@dataclass(frozen=True)
class LayoutItem:
    skill_id: str
    status: str
    artifact_class: str | None
    artifact_path: str | None
    current_artifact_path: str | None
    write_artifact_path: str | None
    write_artifact_role: str | None
    record_artifact_supported: bool | None
    current_pointer_is_symlink: bool | None
    current_pointer_target_path: str | None
    current_pointer_target_exists: bool | None
    on_disk_layout: str
    discovery_source: str
    resolver_error: str | None = None


def _skill_ids(repo_root: Path, selected: list[str] | None) -> list[str]:
    if selected:
        return sorted(set(selected))
    skills_root = repo_root / "skills" / "public"
    skill_ids = (
        {path.name for path in skills_root.iterdir() if path.is_dir()}
        if skills_root.is_dir()
        else set()
    )
    artifact_root = repo_root / "charness-artifacts"
    artifact_ids = (
        {
            path.parent.name
            for path in artifact_root.glob("*/latest.md")
            if path.is_file() or path.is_symlink()
        }
        if artifact_root.is_dir()
        else set()
    )
    return sorted(skill_ids | artifact_ids)


def _discovery_source(repo_root: Path, skill_id: str) -> str:
    is_public_skill = (repo_root / "skills" / "public" / skill_id).is_dir()
    has_current_artifact = (repo_root / "charness-artifacts" / skill_id / "latest.md").exists() or (
        repo_root / "charness-artifacts" / skill_id / "latest.md"
    ).is_symlink()
    if is_public_skill and has_current_artifact:
        return "public_skill+artifact_family"
    if is_public_skill:
        return "public_skill"
    if has_current_artifact:
        return "artifact_family"
    return "selected"


def _run_resolver(
    repo_root: Path, skill_id: str, day: date
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = _resolver.payload_for(
            repo_root,
            skill_id,
            "current-pointer-audit",
            intent="current",
            artifact_date=day,
        )
    except (OSError, SystemExit, ValueError) as exc:
        return None, str(exc) or "resolver failed"
    return payload, None


def _path_layout(repo_root: Path, artifact_path: str | None) -> str:
    if not artifact_path:
        return "adapter_unmanaged"
    path = repo_root / artifact_path
    if path.is_symlink():
        return "symlink_current_pointer"
    if path.is_file():
        if Path(artifact_path).name == "latest.md":
            return "regular_current_pointer"
        return "rolling_file"
    if path.exists():
        return "non_file_current_pointer"
    return "missing_current_pointer"


# The fourth copy of the pointer rule used this; it is now the owner's `portable_path`
# rather than a byte-identical private duplicate, kept under the old name because two tests
# reach for it directly.
_portable_path = _scaffold_artifact_lib.portable_path


def _fallback_artifact_path(repo_root: Path, skill_id: str) -> str | None:
    current = repo_root / "charness-artifacts" / skill_id / "latest.md"
    if current.exists() or current.is_symlink():
        return str(current.relative_to(repo_root))
    return None


def _fallback_pointer_state(repo_root: Path, artifact_path: str | None) -> dict[str, object]:
    if artifact_path is None:
        return {
            "current_pointer_is_symlink": None,
            "current_pointer_target_path": None,
            "current_pointer_target_exists": None,
        }
    # A FOURTH copy of the pointer-resolution rule used to live here, found by the
    # duplicate-ratchet gate while the other three were being consolidated. It answered the
    # same question this inventory reports on, so a drift between them would have made the
    # inventory of pointer layouts disagree with the payloads it inventories.
    return _scaffold_artifact_lib.published_pointer_state(repo_root, Path(artifact_path))


def _unresolved_status(error: str | None) -> tuple[str, str]:
    if error and (
        "No skill adapter resolver found" in error
        or "adapter data must include output_dir" in error
    ):
        return "adapter_unmanaged", "adapter_unmanaged"
    return "unresolved", "resolver_error"


def inventory(
    repo_root: Path, *, selected: list[str] | None = None, day: date | None = None
) -> list[LayoutItem]:
    artifact_date = day or date.today()
    items: list[LayoutItem] = []
    for skill_id in _skill_ids(repo_root, selected):
        discovery_source = _discovery_source(repo_root, skill_id)
        payload, error = _run_resolver(repo_root, skill_id, artifact_date)
        if payload is None:
            status, layout = _unresolved_status(error)
            artifact_path = _fallback_artifact_path(repo_root, skill_id)
            pointer_state = _fallback_pointer_state(repo_root, artifact_path)
            if artifact_path is not None and status == "adapter_unmanaged":
                layout = _path_layout(repo_root, artifact_path)
            items.append(
                LayoutItem(
                    skill_id=skill_id,
                    status=status,
                    artifact_class=None,
                    artifact_path=artifact_path,
                    current_artifact_path=artifact_path,
                    write_artifact_path=None,
                    write_artifact_role=None,
                    record_artifact_supported=None,
                    current_pointer_is_symlink=_optional_bool(
                        pointer_state["current_pointer_is_symlink"]
                    ),
                    current_pointer_target_path=_string(
                        pointer_state["current_pointer_target_path"]
                    ),
                    current_pointer_target_exists=_optional_bool(
                        pointer_state["current_pointer_target_exists"]
                    ),
                    on_disk_layout=layout,
                    discovery_source=discovery_source,
                    resolver_error=error,
                )
            )
            continue
        artifact_path = _string(payload.get("artifact_path")) or _string(
            payload.get("current_artifact_path")
        )
        items.append(
            LayoutItem(
                skill_id=skill_id,
                status="resolved",
                artifact_class=_string(payload.get("artifact_class")),
                artifact_path=artifact_path,
                current_artifact_path=_string(payload.get("current_artifact_path")),
                write_artifact_path=_string(payload.get("write_artifact_path")),
                write_artifact_role=_string(payload.get("write_artifact_role")),
                record_artifact_supported=_optional_bool(payload.get("record_artifact_supported")),
                current_pointer_is_symlink=_optional_bool(
                    payload.get("current_pointer_is_symlink")
                ),
                current_pointer_target_path=_string(payload.get("current_pointer_target_path")),
                current_pointer_target_exists=_optional_bool(
                    payload.get("current_pointer_target_exists")
                ),
                on_disk_layout=_path_layout(repo_root, artifact_path),
                discovery_source=discovery_source,
            )
        )
    return items


def _string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _optional_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _summary(items: list[LayoutItem]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item.on_disk_layout] = counts.get(item.on_disk_layout, 0) + 1
    return dict(sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--skill-id", action="append", help="Limit inventory to one skill id; repeatable."
    )
    parser.add_argument("--date", help="ISO date used for resolver payloads.")
    parser.add_argument("--require-resolved", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    artifact_date = date.fromisoformat(args.date) if args.date else date.today()
    items = inventory(repo_root, selected=args.skill_id, day=artifact_date)
    payload = {
        "status": "clean" if all(item.status != "unresolved" for item in items) else "unresolved",
        "summary": _summary(items),
        "items": [asdict(item) for item in items],
    }
    # Unconditional YAML. The retired markdown table was a strict projection of the
    # `LayoutItem` fields each row already carries (`resolver_error` was folded into
    # its Status cell, and the `(missing)` marker restated
    # `current_pointer_target_exists`), plus the same `summary` counts.
    emit_yaml(payload)
    if args.require_resolved and payload["status"] != "clean":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
