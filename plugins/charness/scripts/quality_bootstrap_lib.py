from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file, render_yaml_mapping
from scripts.quality_bootstrap_detect import (
    detect_concept_paths,
    detect_gate_commands,
    detect_preflight_commands,
    detect_preset_lineage,
    detect_security_commands,
)
from scripts.quality_policy_defaults import (
    DEFAULT_COVERAGE_FLOOR_POLICY,
    DEFAULT_COVERAGE_FRAGILE_MARGIN_PP,
    DEFAULT_PROMPT_ASSET_POLICY,
    DEFAULT_SKILL_ERGONOMICS_GATE_RULES,
    DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
    default_specdown_smoke_patterns,
    merge_coverage_floor_policy,
    merge_prompt_asset_policy,
    validate_skill_ergonomics_gate_rules,
)

ADAPTER_CANDIDATES = (Path(".agents/quality-adapter.yaml"), Path(".codex/quality-adapter.yaml"), Path(".claude/quality-adapter.yaml"), Path("docs/quality-adapter.yaml"), Path("quality-adapter.yaml"))


class BootstrapValidationError(Exception):
    pass

def _merge_unique(existing: list[str], inferred: list[str]) -> list[str]:
    merged = list(existing)
    for item in inferred:
        if item not in merged:
            merged.append(item)
    return merged


def _classify_command_deferral(field: str, preset_lineage: list[str]) -> dict[str, Any]:
    if field == "gate_commands":
        families = ["repo-native test runner", "repo-native lint or typecheck gate"]
        if "python-quality" in preset_lineage:
            families = ["pytest or repo-native test runner", "ruff, mypy, or pyright"]
        elif "typescript-quality" in preset_lineage:
            families = ["vitest or jest", "eslint or tsc --noEmit"]
        elif "specdown-quality" in preset_lineage:
            families = ["specdown smoke", "overlap or adapter-depth guard"]
        reason = "No repo-owned quality gate command was detected."
    elif field == "preflight_commands":
        families = ["maintainer setup validation", "repo doctor or setup sanity"]
        reason = "No repo-owned maintainer setup or doctor command was detected."
    else:
        families = ["secret scan", "dependency or supply-chain audit"]
        reason = "No repo-owned security helper was detected."
    return {"field": field, "status": "deferred", "reason": reason, "suggested_families": families}


def _merge_existing_paths(existing: list[str], detected: list[str]) -> tuple[list[str], str]:
    if existing:
        merged = _merge_unique(existing, detected)
        return merged, "augmented" if merged != existing else "preserved"
    if detected:
        return detected, "inferred"
    return [], "deferred"


def _infer_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "skill-outputs/quality",
        "preset_id": "portable-defaults",
        "customized_from": "portable-defaults",
        "preset_lineage": [],
        "coverage_fragile_margin_pp": DEFAULT_COVERAGE_FRAGILE_MARGIN_PP,
        "coverage_floor_policy": dict(DEFAULT_COVERAGE_FLOOR_POLICY),
        "specdown_smoke_patterns": [],
        "spec_pytest_reference_format": DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT,
        "prompt_asset_roots": [],
        "prompt_asset_policy": dict(DEFAULT_PROMPT_ASSET_POLICY),
        "skill_ergonomics_gate_rules": list(DEFAULT_SKILL_ERGONOMICS_GATE_RULES),
        "concept_paths": [],
        "preflight_commands": [],
        "gate_commands": [],
        "security_commands": [],
    }

def _load_existing_adapter_data(repo_root: Path) -> dict[str, Any]:
    defaults = _infer_defaults(repo_root)
    adapter_path = next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        defaults["_explicit_fields"] = set()
        return defaults
    raw = load_yaml_file(adapter_path)
    if not isinstance(raw, dict):
        defaults["_explicit_fields"] = set()
        return defaults
    skill_rule_errors: list[str] = []
    validated_skill_rules = validate_skill_ergonomics_gate_rules(
        raw.get("skill_ergonomics_gate_rules"),
        skill_rule_errors,
    )
    if "skill_ergonomics_gate_rules" in raw and skill_rule_errors:
        rendered = "; ".join(skill_rule_errors)
        raise BootstrapValidationError(
            f"{adapter_path}: invalid `skill_ergonomics_gate_rules`; {rendered}. "
            "Repair the adapter before rerunning bootstrap."
        )
    data = dict(defaults)
    data["_explicit_fields"] = set(raw.keys())
    for field in ("version", "repo", "language", "output_dir", "preset_id", "preset_version", "customized_from"):
        value = raw.get(field)
        if value is not None:
            data[field] = value
    coverage_fragile_margin_pp = raw.get("coverage_fragile_margin_pp")
    if isinstance(coverage_fragile_margin_pp, (int, float)):
        data["coverage_fragile_margin_pp"] = float(coverage_fragile_margin_pp)
    if isinstance(raw.get("coverage_floor_policy"), dict):
        data["coverage_floor_policy"] = merge_coverage_floor_policy(raw.get("coverage_floor_policy"))
    specdown_smoke_patterns = raw.get("specdown_smoke_patterns")
    if isinstance(specdown_smoke_patterns, list) and all(isinstance(item, str) for item in specdown_smoke_patterns):
        data["specdown_smoke_patterns"] = list(specdown_smoke_patterns)
    spec_pytest_reference_format = raw.get("spec_pytest_reference_format")
    if isinstance(spec_pytest_reference_format, str):
        data["spec_pytest_reference_format"] = spec_pytest_reference_format
    if isinstance(raw.get("prompt_asset_policy"), dict):
        data["prompt_asset_policy"] = merge_prompt_asset_policy(raw.get("prompt_asset_policy"))
    if validated_skill_rules is not None:
        data["skill_ergonomics_gate_rules"] = validated_skill_rules
    for field in ("preset_lineage", "prompt_asset_roots", "concept_paths", "preflight_commands", "gate_commands", "security_commands"):
        value = raw.get(field)
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            data[field] = list(value)
    return data


def build_bootstrap_state(repo_root: Path) -> tuple[dict[str, Any], dict[str, str], list[dict[str, Any]]]:
    existing = _load_existing_adapter_data(repo_root)
    explicit_fields = existing.get("_explicit_fields", set())
    detected_lineage = detect_preset_lineage(repo_root)
    field_statuses: dict[str, str] = {}
    deferred_setup: list[dict[str, Any]] = []
    final = {
        "version": 1,
        "repo": existing["repo"],
        "language": existing["language"],
        "output_dir": existing["output_dir"],
        "preset_id": existing.get("preset_id") or (detected_lineage[0] if detected_lineage else "portable-defaults"),
        "customized_from": existing.get("customized_from") or (detected_lineage[0] if detected_lineage else "portable-defaults"),
        "preset_version": existing.get("preset_version"),
    }

    existing_lineage = existing.get("preset_lineage", [])
    if existing_lineage:
        merged_lineage = _merge_unique(existing_lineage, detected_lineage)
        field_statuses["preset_lineage"] = "augmented" if merged_lineage != existing_lineage else "preserved"
    elif detected_lineage:
        merged_lineage = detected_lineage
        field_statuses["preset_lineage"] = "inferred"
    else:
        merged_lineage = []
        field_statuses["preset_lineage"] = "deferred"
    final["preset_lineage"] = merged_lineage

    preserve_coverage_margin = "coverage_fragile_margin_pp" in explicit_fields
    final["coverage_fragile_margin_pp"] = existing["coverage_fragile_margin_pp"] if preserve_coverage_margin else DEFAULT_COVERAGE_FRAGILE_MARGIN_PP
    field_statuses["coverage_fragile_margin_pp"] = "preserved" if preserve_coverage_margin else "defaulted"

    preserve_coverage_policy = "coverage_floor_policy" in explicit_fields
    final["coverage_floor_policy"] = dict(existing["coverage_floor_policy"] if preserve_coverage_policy else DEFAULT_COVERAGE_FLOOR_POLICY)
    field_statuses["coverage_floor_policy"] = "preserved" if preserve_coverage_policy else "defaulted"

    existing_patterns = existing.get("specdown_smoke_patterns", [])
    if "specdown_smoke_patterns" in explicit_fields:
        final["specdown_smoke_patterns"] = list(existing_patterns)
        field_statuses["specdown_smoke_patterns"] = "preserved"
    else:
        inferred_patterns = default_specdown_smoke_patterns(merged_lineage)
        final["specdown_smoke_patterns"] = inferred_patterns
        field_statuses["specdown_smoke_patterns"] = "inferred" if inferred_patterns else "defaulted"

    preserve_spec_format = "spec_pytest_reference_format" in explicit_fields
    final["spec_pytest_reference_format"] = existing["spec_pytest_reference_format"] if preserve_spec_format else DEFAULT_SPEC_PYTEST_REFERENCE_FORMAT
    field_statuses["spec_pytest_reference_format"] = "preserved" if preserve_spec_format else "defaulted"

    if "prompt_asset_roots" in explicit_fields:
        final["prompt_asset_roots"] = list(existing.get("prompt_asset_roots", []))
        field_statuses["prompt_asset_roots"] = "preserved"
    else:
        final["prompt_asset_roots"] = []
        field_statuses["prompt_asset_roots"] = "defaulted"

    if "prompt_asset_policy" in explicit_fields:
        final["prompt_asset_policy"] = dict(existing["prompt_asset_policy"])
        field_statuses["prompt_asset_policy"] = "preserved"
    else:
        final["prompt_asset_policy"] = dict(DEFAULT_PROMPT_ASSET_POLICY)
        field_statuses["prompt_asset_policy"] = "defaulted"

    if "skill_ergonomics_gate_rules" in explicit_fields:
        final["skill_ergonomics_gate_rules"] = list(existing.get("skill_ergonomics_gate_rules", []))
        field_statuses["skill_ergonomics_gate_rules"] = "preserved"
    else:
        final["skill_ergonomics_gate_rules"] = list(DEFAULT_SKILL_ERGONOMICS_GATE_RULES)
        field_statuses["skill_ergonomics_gate_rules"] = "defaulted"

    concept_paths = detect_concept_paths(repo_root)
    existing_concepts = [path for path in existing.get("concept_paths", []) if (repo_root / path).is_file()]
    merged_concepts, field_statuses["concept_paths"] = _merge_existing_paths(existing_concepts, concept_paths)
    final["concept_paths"] = merged_concepts

    for field, detected in (
        ("preflight_commands", detect_preflight_commands(repo_root)),
        ("gate_commands", detect_gate_commands(repo_root)),
        ("security_commands", detect_security_commands(repo_root)),
    ):
        existing_values = existing.get(field, [])
        if existing_values:
            final[field] = list(existing_values)
            field_statuses[field] = "preserved"
            continue
        if detected:
            final[field] = detected
            field_statuses[field] = "installed"
            continue
        final[field] = []
        field_statuses[field] = "deferred"
        deferred_setup.append(_classify_command_deferral(field, merged_lineage))

    return final, field_statuses, deferred_setup


def render_bootstrap_adapter(data: dict[str, Any]) -> str:
    items: list[tuple[str, Any]] = [
        ("version", data["version"]),
        ("repo", data["repo"]),
        ("language", data["language"]),
        ("output_dir", data["output_dir"]),
        ("preset_id", data["preset_id"]),
        ("customized_from", data["customized_from"]),
    ]
    if data.get("preset_version"):
        items.append(("preset_version", data["preset_version"]))
    items.extend(
        [
            ("preset_lineage", data["preset_lineage"]),
            ("coverage_fragile_margin_pp", data["coverage_fragile_margin_pp"]),
            ("coverage_floor_policy", data["coverage_floor_policy"]),
            ("specdown_smoke_patterns", data["specdown_smoke_patterns"]),
            ("spec_pytest_reference_format", data["spec_pytest_reference_format"]),
            ("prompt_asset_roots", data["prompt_asset_roots"]),
            ("prompt_asset_policy", data["prompt_asset_policy"]),
            ("skill_ergonomics_gate_rules", data["skill_ergonomics_gate_rules"]),
            ("concept_paths", data["concept_paths"]),
            ("preflight_commands", data["preflight_commands"]),
            ("gate_commands", data["gate_commands"]),
            ("security_commands", data["security_commands"]),
        ]
    )
    return render_yaml_mapping(items)


def bootstrap_quality_adapter(
    *, repo_root: Path, output_path: Path, report_path: Path, dry_run: bool
) -> dict[str, Any]:
    adapter_path = output_path if output_path.is_absolute() else repo_root / output_path
    resolved_report_path = report_path if report_path.is_absolute() else repo_root / report_path
    final_data, field_statuses, deferred_setup = build_bootstrap_state(repo_root)
    adapter_text = render_bootstrap_adapter(final_data)
    existing_text = adapter_path.read_text(encoding="utf-8") if adapter_path.is_file() else None

    if dry_run:
        adapter_status = "dry-run"
    elif existing_text is None:
        adapter_path.parent.mkdir(parents=True, exist_ok=True)
        adapter_path.write_text(adapter_text, encoding="utf-8")
        adapter_status = "written"
    elif existing_text == adapter_text:
        adapter_status = "unchanged"
    else:
        adapter_path.write_text(adapter_text, encoding="utf-8")
        adapter_status = "updated"

    report = {
        "adapter_path": str(adapter_path),
        "adapter_status": adapter_status,
        "artifact_path": str(Path(final_data["output_dir"]) / "quality.md"),
        "report_path": str(resolved_report_path),
        "preset_lineage": final_data["preset_lineage"],
        "field_statuses": field_statuses,
        "deferred_setup": deferred_setup,
    }
    if not dry_run:
        resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
