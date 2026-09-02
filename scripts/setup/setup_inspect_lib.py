from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.hooks.setup_hook_failure_visibility_lib import (
    inspect_hook_failure_visibility,  # noqa: E402
)
from scripts.setup import setup_inspect_quality_lib as quality_helpers  # noqa: E402
from scripts.setup.setup_agent_docs_lib import (  # noqa: E402
    FINDING_RECOMMENDATION_PRIORITIES,
    RECOMMENDATION_FINDING_TYPES,
    detect_agent_docs,
    finding_recommendation,
    sort_recommendations,
)

DEFAULT_SURFACES = {
    "readme": Path("README.md"),
    "agents": Path("AGENTS.md"),
    "docs_index": Path("docs/index.md"),
    "roadmap": Path("docs/roadmap.md"),
    "operator_acceptance": Path("docs/operator-acceptance.md"),
}
PROFILE_SURFACES = ("readme", "agents", "docs_index")
# Roadmap and operator acceptance are evidence-triggered additions, not setup
# prerequisites. Keep their states in the payload for planning without making a
# missing optional document look like an incomplete core operating surface.
CORE_SURFACES = PROFILE_SURFACES
CONDITIONAL_SURFACES = ("roadmap", "operator_acceptance")


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


def build_setup_inspection_payload(
    repo_root: Path,
    *,
    load_setup_adapter: Callable[[Path], tuple[dict[str, Any], str | None, list[dict[str, str]]]],
    prose_wrap_state: Callable[[Path, dict[str, Any]], dict[str, object]],
    surface_overrides: Callable[[dict[str, Any]], dict[str, Any]],
    operating_surface_profile: Callable[[dict[str, Any]], dict[str, object]] | None = None,
) -> dict[str, object]:
    adapter_data, adapter_path, adapter_warnings = load_setup_adapter(repo_root)
    specs = _surface_specs(repo_root, surface_overrides(adapter_data))
    repo_mode = detect_repo_mode(specs)
    profile_config = (
        operating_surface_profile(adapter_data)
        if operating_surface_profile is not None
        else {"id": "flat-wiki", "approval_required": True}
    )
    agent_docs = detect_agent_docs(repo_root)
    normalization = agent_docs["normalization"]
    findings = [
        finding
        for finding in normalization["findings"]
        if isinstance(finding, dict)
    ]
    recommendations = [
        finding_recommendation(
            finding,
            priority=FINDING_RECOMMENDATION_PRIORITIES.get(str(finding.get("type")), "advisory"),
        )
        for finding in findings
        if finding.get("type") in RECOMMENDATION_FINDING_TYPES
    ]
    extra = normalization.get("extra_recommendations") or []
    if isinstance(extra, list):
        recommendations.extend(item for item in extra if isinstance(item, dict))
    recommendations = sort_recommendations(recommendations)
    normalization["findings"] = findings
    normalization["recommendations"] = recommendations
    normalization.pop("extra_recommendations", None)
    normalization["status"] = "needs_normalization" if findings or recommendations else "ok"
    payload = {
        "repo": repo_root.name,
        "repo_mode": repo_mode,
        "partial_kind": detect_partial_kind(specs, repo_mode),
        "missing_surfaces": detect_missing_surfaces(specs),
        "profile": {
            "id": profile_config.get("id", "flat-wiki"),
            "approval_required": profile_config.get("approval_required", True),
            "profile_surfaces": {
                surface_id: _surface_state(repo_root, specs[surface_id])
                for surface_id in PROFILE_SURFACES
            },
            "missing_profile_surfaces": [
                surface_id for surface_id in PROFILE_SURFACES if not _surface_present(specs[surface_id])
            ],
            "plan_only": True,
            "approval_prompt": f"Apply the {profile_config.get('id', 'flat-wiki')} operating surface and the approved quality bootstrap plan?",
            "awiki": quality_helpers.probe_awiki(repo_root),
        },
        "docs_inventory": quality_helpers.docs_inventory(repo_root),
        "conditional_surfaces": {
            "roadmap": {
                **_surface_state(repo_root, specs["roadmap"]),
                "activation": "active ordered work is evidenced or requested",
                "applicability": "unproven — operator decision",
            },
            "operator_acceptance": {
                **_surface_state(repo_root, specs["operator_acceptance"]),
                "activation": "a real install, deployment, or takeover path exists",
                "applicability": "unproven — operator decision",
            },
        },
        "adapter": {
            "found": adapter_path is not None,
            "path": adapter_path,
            "valid": not adapter_warnings,
            "warnings": adapter_warnings,
        },
        "agent_docs": agent_docs,
        "hook_failure_visibility": inspect_hook_failure_visibility(repo_root),
        "quality_setup": quality_helpers.quality_setup_snapshot(repo_root),
        "recommendations": recommendations,
        "prose_wrap": prose_wrap_state(repo_root, adapter_data),
        "surfaces": {surface_id: _surface_state(repo_root, spec) for surface_id, spec in specs.items()},
    }
    payload["approval_plan"] = quality_helpers.approval_plan(repo_root, payload, DEFAULT_SURFACES)
    return payload
