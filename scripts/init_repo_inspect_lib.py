from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from scripts.init_repo_agent_docs_lib import (
    FINDING_RECOMMENDATION_PRIORITIES,
    RECOMMENDATION_FINDING_TYPES,
    detect_agent_docs,
    detect_policy_source_recommendations,
    finding_recommendation,
    is_acknowledged,
    sort_recommendations,
)

DEFAULT_SURFACES = {
    "readme": Path("README.md"),
    "agents": Path("AGENTS.md"),
    "roadmap": Path("docs/roadmap.md"),
    "operator_acceptance": Path("docs/operator-acceptance.md"),
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
        return {"exists": True, "kind": "symlink", "target": str(path.readlink())}
    if path.is_file():
        return {"exists": True, "kind": "file", "size": path.stat().st_size}
    return {"exists": True, "kind": "other"}


def _case_insensitive_path(repo_root: Path, relative_path: Path) -> Path:
    current = repo_root
    for part in relative_path.parts:
        if not current.is_dir():
            return current / part
        matches = sorted(child for child in current.iterdir() if child.name.lower() == part.lower())
        current = matches[0] if matches else current / part
    return current


def _relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


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

    return SurfaceSpec(
        surface_id=surface_id,
        configured_path=configured_path,
        path=_case_insensitive_path(repo_root, configured_path),
        source=source,
        acknowledged_missing=acknowledged_missing,
    )


def _surface_specs(repo_root: Path, overrides: dict[str, Any]) -> dict[str, SurfaceSpec]:
    return {surface_id: _surface_spec(repo_root, surface_id, overrides) for surface_id in DEFAULT_SURFACES}


def _surface_state(repo_root: Path, spec: SurfaceSpec) -> dict[str, object]:
    state = {"exists": False, "kind": "acknowledged_missing"} if spec.acknowledged_missing else _file_state(spec.path)
    state["path"] = _relative(spec.path, repo_root)
    if spec.configured_path != Path(state["path"]):
        state["configured_path"] = spec.configured_path.as_posix()
    state["source"] = spec.source
    return state


def _surface_present(spec: SurfaceSpec) -> bool:
    return spec.acknowledged_missing or spec.path.exists() or spec.path.is_symlink()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def detect_repo_mode(specs: dict[str, SurfaceSpec]) -> str:
    present = sum(1 for surface_id in CORE_SURFACES if _surface_present(specs[surface_id]))
    if present == 0:
        return "GREENFIELD"
    if present < len(CORE_SURFACES):
        return "PARTIAL"
    return "NORMALIZE"


def detect_missing_surfaces(specs: dict[str, SurfaceSpec]) -> list[str]:
    return [surface_id for surface_id in CORE_SURFACES if not _surface_present(specs[surface_id])]


def detect_partial_kind(specs: dict[str, SurfaceSpec], repo_mode: str) -> str | None:
    if repo_mode != "PARTIAL":
        return None
    return "targeted_missing_surface" if len(detect_missing_surfaces(specs)) == 1 else "broad_partial"


def build_init_repo_inspection_payload(
    repo_root: Path,
    *,
    load_init_repo_adapter: Callable[[Path], tuple[dict[str, Any], str | None, list[dict[str, str]]]],
    prose_wrap_state: Callable[[Path, dict[str, Any]], dict[str, object]],
    recommendation_policy: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    surface_overrides: Callable[[dict[str, Any]], dict[str, Any]],
    skill_routing_payload: Callable[[Path], dict[str, Any]] | None = None,
) -> dict[str, object]:
    adapter_data, adapter_path, adapter_warnings = load_init_repo_adapter(repo_root)
    specs = _surface_specs(repo_root, surface_overrides(adapter_data))
    repo_mode = detect_repo_mode(specs)
    policy = recommendation_policy(adapter_data) if recommendation_policy is not None else {}
    acknowledged = set(policy.get("acknowledged", []))
    agent_docs = detect_agent_docs(repo_root, skill_routing_payload=skill_routing_payload)
    normalization = agent_docs["normalization"]
    findings = [
        finding
        for finding in normalization["findings"]
        if isinstance(finding, dict) and not is_acknowledged(str(finding.get("type")), acknowledged)
    ]
    recommendations = [
        finding_recommendation(
            finding,
            priority=FINDING_RECOMMENDATION_PRIORITIES.get(str(finding.get("type")), "advisory"),
        )
        for finding in findings
        if finding.get("type") in RECOMMENDATION_FINDING_TYPES
    ]
    recommendations.extend(detect_policy_source_recommendations(repo_root, _read_text(repo_root / "AGENTS.md"), policy))
    recommendations = [
        recommendation
        for recommendation in sort_recommendations(recommendations)
        if not is_acknowledged(str(recommendation.get("id")), acknowledged)
    ]
    for recommendation in recommendations:
        acknowledgement = recommendation.get("acknowledgement")
        if isinstance(acknowledgement, dict):
            acknowledgement["adapter_path"] = adapter_path
    normalization["findings"] = findings
    normalization["recommendations"] = recommendations
    normalization["status"] = "needs_normalization" if findings or recommendations else "ok"
    normalization["recommendation_policy"] = {
        "defaults_version": policy.get("defaults_version"),
        "policy_source_count": len(policy.get("policy_sources", [])),
        "enabled": list(policy.get("enabled", [])),
        "acknowledged": sorted(acknowledged),
    }
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
        "agent_docs": agent_docs,
        "recommendations": recommendations,
        "prose_wrap": prose_wrap_state(repo_root, adapter_data),
        "surfaces": {surface_id: _surface_state(repo_root, spec) for surface_id, spec in specs.items()},
    }
