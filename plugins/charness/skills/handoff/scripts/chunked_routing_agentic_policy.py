"""Policy and prompt constants for agentic handoff chunk proposals."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

CHUNK_PROPOSAL_PACKET_VERSION = 2
DEFAULT_MAX_PACKAGE_SOURCES = 5
DEFAULT_BROAD_BOUNDARY_TOKENS = frozenset(
    {
        "label/bug",
        "label/enhancement",
        "label/future work",
        "label/future-work",
        "label/operations",
        "label/test",
    }
)
JUDGMENT_SUMMARY_FIELDS = (
    "semantic_fit",
    "implementation_boundary",
    "closeout_flow",
    "operator_value",
)

CHUNK_PROPOSER_PROMPT = (
    "Propose coherent work packages from the provided handoff sources. "
    "Do not return a ranked issue list. A package should group sources only "
    "when they share an implementation boundary, closeout/publication flow, "
    "test fixture risk, or downstream unlock. Treat deterministic merge hints "
    "as facts to re-judge, not as package decisions. Use every source exactly once. "
    "For each package, name included source_ids, excluded_source_ids when a "
    "nearby source might look related but should stay out, objective_summary, "
    "rationale, downstream_unlock, a judgment_summary with semantic_fit, "
    "implementation_boundary, closeout_flow, and operator_value, and "
    "basis_boundary_tokens when boundary tokens are part of the justification. "
    "Standalone packages are allowed when no honest grouping exists."
)


def _load_sibling(module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).resolve().parent / f"{module_name}.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            f"{module_name}.py not found beside chunked_routing_agentic_policy.py"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def default_chunk_policy() -> dict[str, Any]:
    return {
        "max_package_sources": DEFAULT_MAX_PACKAGE_SOURCES,
        "broad_boundary_tokens": tuple(sorted(DEFAULT_BROAD_BOUNDARY_TOKENS)),
        "allowed_broad_boundary_tokens": (),
    }


def _adapter_yaml_loader():
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "scripts" / "adapter_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "handoff_agentic_adapter_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.load_yaml_file
    return None


def load_chunk_policy_config(repo_root: Path) -> dict[str, Any]:
    """Read optional ``chunk_policy:`` settings from the handoff adapter."""
    config = default_chunk_policy()
    try:
        resolve = _load_sibling("resolve_adapter")
        adapter = resolve.load_adapter(repo_root)
        adapter_path = adapter.get("path")
        if not adapter_path:
            return config
        load_yaml_file = _adapter_yaml_loader()
        if load_yaml_file is None:
            return config
        raw = load_yaml_file(Path(adapter_path))
        block = raw.get("chunk_policy") if isinstance(raw, dict) else None
        if not isinstance(block, dict):
            return config
    except Exception:
        return config

    max_sources = block.get("max_package_sources")
    if isinstance(max_sources, int) and max_sources > 0:
        config["max_package_sources"] = max_sources
    for key in ("broad_boundary_tokens", "allowed_broad_boundary_tokens"):
        values = block.get(key)
        if isinstance(values, list):
            config[key] = tuple(str(v) for v in values if isinstance(v, str))
    return config
