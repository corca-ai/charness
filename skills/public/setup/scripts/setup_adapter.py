from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file, validate_adapter_version
from scripts.gates_support.source_guard_scan_lib import DEFAULT_SOURCE_GUARD_SCAN_ROOTS, fixed_source_guard_rows

ADAPTER_CANDIDATES = (
    Path(".agents/setup-adapter.yaml"),
)

def load_setup_adapter(repo_root: Path) -> tuple[dict[str, Any], str | None, list[dict[str, str]]]:
    adapter_path = next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        return {}, None, []
    text = adapter_path.read_text(encoding="utf-8")
    first = next((line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")), "")
    if first.startswith("- "):
        return (
            {},
            str(adapter_path),
            [{"type": "adapter_root_not_mapping", "message": "setup adapter root must be a mapping."}],
        )
    raw = load_yaml_file(adapter_path)
    if isinstance(raw, dict):
        version_errors: list[str] = []
        validate_adapter_version(raw, {}, version_errors)
        if version_errors:
            return (
                {},
                str(adapter_path),
                [
                    {"type": "invalid_adapter_version", "message": message}
                    for message in version_errors
                ],
            )
        return raw, str(adapter_path), _validate_adapter_fields(raw)
    return (
        {},
        str(adapter_path),
        [{"type": "adapter_root_not_mapping", "message": "setup adapter root must be a mapping."}],
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


def _validate_adapter_fields(adapter_data: dict[str, Any]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    profile = adapter_data.get("operating_surface_profile", "flat-wiki")
    if profile != "flat-wiki":
        warnings.append(
            {
                "type": "unsupported_operating_surface_profile",
                "message": "operating_surface_profile must be `flat-wiki`",
            }
        )
    approval_required = adapter_data.get("approval_required", True)
    if approval_required is not True:
        warnings.append(
            {
                "type": "invalid_adapter_field",
                "message": "approval_required must remain true for setup mutations",
            }
        )
    _string_list(adapter_data.get("source_guard_scan_roots"), "source_guard_scan_roots", warnings)
    return warnings


def operating_surface_profile(adapter_data: dict[str, Any]) -> dict[str, object]:
    profile = adapter_data.get("operating_surface_profile", "flat-wiki")
    return {
        "id": profile if profile == "flat-wiki" else "flat-wiki",
        "approval_required": True,
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
