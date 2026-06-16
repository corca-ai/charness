#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any


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
    skill_ids = {path.name for path in skills_root.iterdir() if path.is_dir()} if skills_root.is_dir() else set()
    artifact_root = repo_root / "charness-artifacts"
    artifact_ids = (
        {path.parent.name for path in artifact_root.glob("*/latest.md") if path.is_file() or path.is_symlink()}
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


def _run_resolver(repo_root: Path, skill_id: str, day: date) -> tuple[dict[str, Any] | None, str | None]:
    script = Path(__file__).resolve().parent / "resolve_artifact_path.py"
    completed = subprocess.run(
        [
            "python3",
            str(script),
            "--repo-root",
            str(repo_root),
            "--skill-id",
            skill_id,
            "--slug",
            "current-pointer-audit",
            "--intent",
            "current",
            "--date",
            day.isoformat(),
        ],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None, completed.stderr.strip() or completed.stdout.strip() or "resolver failed"
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return None, f"resolver returned invalid JSON: {exc}"
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


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


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
    path = repo_root / artifact_path
    if not path.is_symlink():
        return {
            "current_pointer_is_symlink": False,
            "current_pointer_target_path": None,
            "current_pointer_target_exists": None,
        }
    raw_target = os.readlink(path)
    target_path = Path(raw_target)
    if not target_path.is_absolute():
        target_path = path.parent / target_path
    return {
        "current_pointer_is_symlink": True,
        "current_pointer_target_path": _portable_path(repo_root, target_path),
        "current_pointer_target_exists": target_path.exists(),
    }


def _unresolved_status(error: str | None) -> tuple[str, str]:
    if error and (
        "No skill adapter resolver found" in error or "adapter data must include output_dir" in error
    ):
        return "adapter_unmanaged", "adapter_unmanaged"
    return "unresolved", "resolver_error"


def inventory(repo_root: Path, *, selected: list[str] | None = None, day: date | None = None) -> list[LayoutItem]:
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
                    current_pointer_is_symlink=_optional_bool(pointer_state["current_pointer_is_symlink"]),
                    current_pointer_target_path=_string(pointer_state["current_pointer_target_path"]),
                    current_pointer_target_exists=_optional_bool(pointer_state["current_pointer_target_exists"]),
                    on_disk_layout=layout,
                    discovery_source=discovery_source,
                    resolver_error=error,
                )
            )
            continue
        artifact_path = _string(payload.get("artifact_path")) or _string(payload.get("current_artifact_path"))
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
                current_pointer_is_symlink=_optional_bool(payload.get("current_pointer_is_symlink")),
                current_pointer_target_path=_string(payload.get("current_pointer_target_path")),
                current_pointer_target_exists=_optional_bool(payload.get("current_pointer_target_exists")),
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


def _markdown(items: list[LayoutItem]) -> str:
    lines = [
        "# Current Pointer Layout Inventory",
        "",
        "| Skill | Source | Class | On-Disk Layout | Artifact Path | Write Path | Target | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        target = item.current_pointer_target_path or ""
        if item.current_pointer_target_exists is False:
            target = f"{target} (missing)"
        status = item.status if item.resolver_error is None else f"{item.status}: {item.resolver_error}"
        lines.append(
            "| "
            + " | ".join(
                _md_cell(value)
                for value in (
                    item.skill_id,
                    item.discovery_source,
                    item.artifact_class or "",
                    item.on_disk_layout,
                    item.artifact_path or "",
                    item.write_artifact_path or "",
                    target,
                    status,
                )
            )
            + " |"
        )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for layout, count in _summary(items).items():
        lines.append(f"- `{layout}`: {count}")
    return "\n".join(lines) + "\n"


def _md_cell(value: str) -> str:
    escaped = value.replace("|", "\\|")
    return f"`{escaped}`" if escaped else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--skill-id", action="append", help="Limit inventory to one skill id; repeatable.")
    parser.add_argument("--date", help="ISO date used for resolver payloads.")
    parser.add_argument("--json", action="store_true")
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
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(_markdown(items), end="")
    if args.require_resolved and payload["status"] != "clean":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
