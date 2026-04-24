from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file
from scripts.source_guard_scan_lib import DEFAULT_SOURCE_GUARD_SCAN_ROOTS, fixed_source_guard_rows

ADAPTER_CANDIDATES = (
    Path(".agents/init-repo-adapter.yaml"),
    Path(".codex/init-repo-adapter.yaml"),
    Path(".claude/init-repo-adapter.yaml"),
    Path("docs/init-repo-adapter.yaml"),
    Path("init-repo-adapter.yaml"),
)

def load_init_repo_adapter(repo_root: Path) -> tuple[dict[str, Any], str | None, list[dict[str, str]]]:
    adapter_path = next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        return {}, None, []
    text = adapter_path.read_text(encoding="utf-8")
    first = next((line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")), "")
    if first.startswith("- "):
        return (
            {},
            str(adapter_path),
            [{"type": "adapter_root_not_mapping", "message": "init-repo adapter root must be a mapping."}],
        )
    raw = load_yaml_file(adapter_path)
    if isinstance(raw, dict):
        return raw, str(adapter_path), _validate_recommendation_fields(raw)
    return (
        {},
        str(adapter_path),
        [{"type": "adapter_root_not_mapping", "message": "init-repo adapter root must be a mapping."}],
    )


def surface_overrides(adapter_data: dict[str, Any]) -> dict[str, Any]:
    surfaces = adapter_data.get("surfaces")
    return surfaces if isinstance(surfaces, dict) else {}


def _string_list(value: Any, field: str, warnings: list[dict[str, str]]) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list) and all(isinstance(item, str) and item for item in value):
        return list(value)
    warnings.append({"type": "invalid_adapter_field", "message": f"{field} must be a list of non-empty strings."})
    return []


def _acknowledged_ids(value: Any, field: str, warnings: list[dict[str, str]]) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        warnings.append({"type": "invalid_adapter_field", "message": f"{field} must be a list."})
        return []
    ids: list[str] = []
    for index, item in enumerate(value):
        if isinstance(item, str) and item:
            ids.append(item)
            continue
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]:
            ids.append(item["id"])
            continue
        warnings.append(
            {"type": "invalid_adapter_field", "message": f"{field}[{index}] must be a string or mapping with id."}
        )
    return ids


def _policy_sources(value: Any, warnings: list[dict[str, str]]) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        warnings.append({"type": "invalid_adapter_field", "message": "policy_sources must be a list."})
        return []
    sources: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        prefix = f"policy_sources[{index}]"
        if not isinstance(item, dict):
            warnings.append({"type": "invalid_adapter_field", "message": f"{prefix} must be a mapping."})
            continue
        path = item.get("path")
        if not isinstance(path, str) or not path:
            warnings.append({"type": "invalid_adapter_field", "message": f"{prefix}.path must be a non-empty string."})
            continue
        source_id = item.get("id", path)
        if not isinstance(source_id, str) or not source_id:
            warnings.append({"type": "invalid_adapter_field", "message": f"{prefix}.id must be a non-empty string."})
            continue
        terms = _string_list(item.get("evidence_terms"), f"{prefix}.evidence_terms", warnings)
        recommendations = _string_list(item.get("recommendations"), f"{prefix}.recommendations", warnings)
        sources.append({"id": source_id, "path": path, "evidence_terms": terms, "recommendations": recommendations})
    return sources


def _validate_recommendation_fields(adapter_data: dict[str, Any]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    defaults_version = adapter_data.get("defaults_version", adapter_data.get("recommendation_defaults_version"))
    if defaults_version is not None and not isinstance(defaults_version, str):
        warnings.append(
            {"type": "invalid_adapter_field", "message": "defaults_version must be a string."}
        )
    _string_list(adapter_data.get("source_guard_scan_roots"), "source_guard_scan_roots", warnings)
    _policy_sources(adapter_data.get("policy_sources"), warnings)
    recommendation_sets = adapter_data.get("recommendation_sets")
    if recommendation_sets is not None and not isinstance(recommendation_sets, dict):
        warnings.append({"type": "invalid_adapter_field", "message": "recommendation_sets must be a mapping."})
        return warnings
    if isinstance(recommendation_sets, dict):
        _string_list(recommendation_sets.get("enabled"), "recommendation_sets.enabled", warnings)
        _acknowledged_ids(recommendation_sets.get("acknowledged"), "recommendation_sets.acknowledged", warnings)
    return warnings


def recommendation_policy(adapter_data: dict[str, Any]) -> dict[str, Any]:
    warnings: list[dict[str, str]] = []
    recommendation_sets = adapter_data.get("recommendation_sets")
    sets = recommendation_sets if isinstance(recommendation_sets, dict) else {}
    defaults_version = adapter_data.get("defaults_version", adapter_data.get("recommendation_defaults_version"))
    return {
        "defaults_version": defaults_version if isinstance(defaults_version, str) else None,
        "policy_sources": _policy_sources(adapter_data.get("policy_sources"), warnings),
        "enabled": _string_list(sets.get("enabled"), "recommendation_sets.enabled", warnings),
        "acknowledged": _acknowledged_ids(sets.get("acknowledged"), "recommendation_sets.acknowledged", warnings),
    }


def _source_guard_scan_roots(adapter_data: dict[str, Any]) -> list[Path]:
    raw_roots = adapter_data.get("source_guard_scan_roots")
    if isinstance(raw_roots, list) and all(isinstance(item, str) and item for item in raw_roots):
        return [Path(item) for item in raw_roots]
    return list(DEFAULT_SOURCE_GUARD_SCAN_ROOTS)


def _source_guard_scan(
    repo_root: Path, adapter_data: dict[str, Any]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows, warnings = fixed_source_guard_rows(repo_root, _source_guard_scan_roots(adapter_data))
    return [
        {
            "spec_path": row["spec_path"],
            "line": int(row["line"]),
            "target_path": row["target_path"],
            "pattern_chars": len(row["pattern"]),
        }
        for row in rows
    ], warnings


def _matcher_normalizes(adapter_data: dict[str, Any]) -> bool:
    matcher = adapter_data.get("source_guard_matcher")
    if isinstance(matcher, dict) and matcher.get("normalize_whitespace") is True:
        return True
    return adapter_data.get("source_guard_normalizes_whitespace") is True


def prose_wrap_state(repo_root: Path, adapter_data: dict[str, Any]) -> dict[str, object]:
    raw_policy = adapter_data.get("prose_wrap_policy", "semantic")
    policy = raw_policy if raw_policy in {"semantic", "column"} else "invalid"
    guards, scan_warnings = _source_guard_scan(repo_root, adapter_data)
    normalizes = _matcher_normalizes(adapter_data)
    explicit_override = adapter_data.get("allow_column_wrap_fixed_guards") is True
    warnings: list[dict[str, object]] = [*scan_warnings]
    status = "ok" if policy != "invalid" else "invalid_policy"

    if policy == "column" and guards and not normalizes and not explicit_override:
        status = "requires_override"
        warnings.append(
            {
                "type": "column_wrap_fixed_guard_requires_override",
                "message": (
                    "Column-wrapped prose with fixed-string source guards requires "
                    "whitespace-normalized matching or allow_column_wrap_fixed_guards: true."
                ),
                "required_override": "source_guard_matcher.normalize_whitespace: true",
            }
        )

    return {
        "policy": policy,
        "source": "adapter" if "prose_wrap_policy" in adapter_data else "default",
        "source_guard_count": len(guards),
        "source_guards": guards,
        "matcher_normalizes_whitespace": normalizes,
        "explicit_override": explicit_override,
        "status": status,
        "warnings": warnings,
    }
