#!/usr/bin/env python3
# ruff: noqa: T201

from __future__ import annotations

import argparse
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_init_repo_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "init_repo_adapter")
load_init_repo_adapter = _init_repo_adapter_module.load_init_repo_adapter
prose_wrap_state = _init_repo_adapter_module.prose_wrap_state
surface_overrides = _init_repo_adapter_module.surface_overrides

DEFAULT_SURFACES = {
    "readme": Path("README.md"),
    "agents": Path("AGENTS.md"),
    "roadmap": Path("docs/roadmap.md"),
    "operator_acceptance": Path("docs/operator-acceptance.md"),
    "install": Path("INSTALL.md"),
    "uninstall": Path("UNINSTALL.md"),
    "handoff": Path("docs/handoff.md"),
}

CORE_SURFACES = ("readme", "agents", "roadmap", "operator_acceptance")


@dataclass(frozen=True)
class SurfaceSpec:
    surface_id: str
    configured_path: Path
    path: Path
    source: str
    acknowledged_missing: bool = False


def _file_state(path: Path) -> dict[str, object]:
    if not path.exists() and not path.is_symlink():
        return {"exists": False, "kind": "missing"}
    if path.is_symlink():
        target = path.readlink()
        return {"exists": True, "kind": "symlink", "target": str(target)}
    if path.is_file():
        size = path.stat().st_size
        return {"exists": True, "kind": "file", "size": size}
    return {"exists": True, "kind": "other"}


def _text_present(path: Path) -> bool:
    return path.is_file() and path.read_text(encoding="utf-8", errors="replace").strip() != ""


def _case_insensitive_path(repo_root: Path, relative_path: Path) -> Path:
    current = repo_root
    for part in relative_path.parts:
        exact = current / part
        if exact.exists() or exact.is_symlink():
            current = exact
            continue
        if not current.is_dir():
            return exact
        matches = sorted(child for child in current.iterdir() if child.name.lower() == part.lower())
        current = matches[0] if matches else exact
    return current


def _surface_spec(repo_root: Path, surface_id: str, overrides: dict[str, Any]) -> SurfaceSpec:
    default_path = DEFAULT_SURFACES[surface_id]
    raw_override = overrides.get(surface_id, "__missing__")
    source = "default"
    configured_path = default_path
    acknowledged_missing = False

    if raw_override != "__missing__":
        source = "adapter"
        if raw_override is None:
            acknowledged_missing = True
        elif isinstance(raw_override, str):
            configured_path = Path(raw_override)
        elif isinstance(raw_override, dict):
            acknowledged_missing = raw_override.get("acknowledged_missing") is True
            raw_path = raw_override.get("path")
            if isinstance(raw_path, str):
                configured_path = Path(raw_path)

    path = _case_insensitive_path(repo_root, configured_path)
    return SurfaceSpec(
        surface_id=surface_id,
        configured_path=configured_path,
        path=path,
        source=source,
        acknowledged_missing=acknowledged_missing,
    )


def _surface_specs(repo_root: Path, overrides: dict[str, Any]) -> dict[str, SurfaceSpec]:
    return {surface_id: _surface_spec(repo_root, surface_id, overrides) for surface_id in DEFAULT_SURFACES}


def _surface_state(repo_root: Path, spec: SurfaceSpec) -> dict[str, object]:
    if spec.acknowledged_missing:
        state: dict[str, object] = {"exists": False, "kind": "acknowledged_missing"}
    else:
        state = _file_state(spec.path)
    state["path"] = _relative(spec.path, repo_root)
    if spec.configured_path != Path(state["path"]):
        state["configured_path"] = spec.configured_path.as_posix()
    state["source"] = spec.source
    return state


def _relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def detect_agent_docs(repo_root: Path) -> dict[str, object]:
    agents = _case_insensitive_path(repo_root, Path("AGENTS.md"))
    claude = _case_insensitive_path(repo_root, Path("CLAUDE.md"))
    agents_state = _file_state(agents)
    claude_state = _file_state(claude)

    if not agents.exists() and not claude.exists() and not claude.is_symlink():
        action = "create_agents_and_symlink"
    elif agents.exists() and not claude.exists() and not claude.is_symlink():
        action = "create_symlink_only"
    elif claude.is_symlink() and claude.resolve() == agents.resolve():
        action = "leave_as_is"
    elif claude.is_file() and not agents.exists():
        action = "ask_to_promote_claude_into_agents"
    elif claude.is_file() and agents.exists():
        action = "ask_to_merge_and_replace_with_symlink"
    else:
        action = "inspect_manually"

    return {
        "agents": agents_state,
        "claude": claude_state,
        "recommended_action": action,
        "agents_has_text": _text_present(agents),
        "claude_has_text": _text_present(claude),
    }


def _surface_present(spec: SurfaceSpec) -> bool:
    return spec.acknowledged_missing or spec.path.exists() or spec.path.is_symlink()


def detect_repo_mode(specs: dict[str, SurfaceSpec]) -> str:
    present = sum(1 for surface_id in CORE_SURFACES if _surface_present(specs[surface_id]))
    required = len(CORE_SURFACES)
    if present == 0:
        return "GREENFIELD"
    if present < required:
        return "PARTIAL"
    return "NORMALIZE"


def detect_missing_surfaces(specs: dict[str, SurfaceSpec]) -> list[str]:
    return [surface_id for surface_id in CORE_SURFACES if not _surface_present(specs[surface_id])]


def detect_partial_kind(specs: dict[str, SurfaceSpec], repo_mode: str) -> str | None:
    if repo_mode != "PARTIAL":
        return None
    missing_surfaces = detect_missing_surfaces(specs)
    if len(missing_surfaces) == 1:
        return "targeted_missing_surface"
    return "broad_partial"


def build_payload(repo_root: Path) -> dict[str, object]:
    adapter_data, adapter_path, adapter_warnings = load_init_repo_adapter(repo_root)
    specs = _surface_specs(repo_root, surface_overrides(adapter_data))
    repo_mode = detect_repo_mode(specs)
    return {
        "repo": repo_root.name,
        "repo_mode": repo_mode,
        "partial_kind": detect_partial_kind(specs, repo_mode),
        "missing_surfaces": detect_missing_surfaces(specs),
        "adapter": {
            "found": adapter_path is not None,
            "path": adapter_path,
            "valid": not adapter_warnings,
            "warnings": adapter_warnings,
        },
        "agent_docs": detect_agent_docs(repo_root),
        "prose_wrap": prose_wrap_state(repo_root, adapter_data),
        "surfaces": {surface_id: _surface_state(repo_root, spec) for surface_id, spec in specs.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload(args.repo_root.resolve())
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
