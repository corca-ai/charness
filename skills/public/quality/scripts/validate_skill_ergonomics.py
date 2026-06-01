#!/usr/bin/env python3
"""Validate opt-in higher-noise skill ergonomics rules from the quality adapter."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
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

_inventory_skill_ergonomics_module = SKILL_RUNTIME.load_local_skill_module(__file__, "inventory_skill_ergonomics")
inventory_skill = _inventory_skill_ergonomics_module.inventory_skill
iter_skill_paths = _inventory_skill_ergonomics_module.iter_skill_paths
_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_scripts_quality_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_adapter_lib")
load_adapter = _scripts_quality_adapter_lib_module.load_quality_adapter_strict
_vendored_path_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.vendored_path_lib")

RULE_HEURISTICS = {
    "long_core": ("long_core",),
    "mode_option_pressure_terms": ("mode_pressure_terms_present", "option_pressure_terms_present"),
    "progressive_disclosure_risk": ("progressive_disclosure_risk",),
    "code_fence_without_helper_script": ("code_fence_without_helper_script",),
    "portable_helper_path_ambiguity": ("portable_helper_path_ambiguity",),
    "issue_anchor_in_core": ("issue_anchor_in_core",),
    "dated_incident_in_core": ("dated_incident_in_core",),
}

RULE_MESSAGES = {
    "long_core": "Skill core exceeds the configured core line budget. Move nuance into references or scripts.",
    "mode_option_pressure_terms": (
        "Public skill shows repeated `mode`/`option` pressure terms. "
        "Prefer stronger defaults and inference, or disable the opt-in rule."
    ),
    "progressive_disclosure_risk": (
        "Skill core is large while references/scripts stay absent. "
        "Move nuance into repo-owned references or scripts, or disable the opt-in rule."
    ),
    "code_fence_without_helper_script": (
        "Skill carries several bootstrap fences without a helper script. "
        "Extract repeated bootstrap or recovery behavior into a repo-owned helper."
    ),
    "portable_helper_path_ambiguity": (
        "Skill mentions helper paths that look cwd-relative. "
        "Use `$SKILL_DIR` or source-tree-qualified paths so installed bundles stay portable."
    ),
    "issue_anchor_in_core": (
        "Public skill core carries issue-number or dated incident anchors. "
        "Move provenance to references, tests, or retro artifacts and keep the core rule general."
    ),
    "dated_incident_in_core": (
        "Public skill core carries dated incident wording. "
        "Name the stable failure class in the core and keep date-specific provenance outside the trigger contract."
    ),
}


def _string_list(data: dict[str, Any], key: str) -> list[str]:
    values = data.get(key, [])
    return values if isinstance(values, list) and all(isinstance(item, str) for item in values) else []


def _iter_checked_skill_paths(repo_root: Path, requested_paths: list[str], vendored_prefixes_list: list[str]) -> list[Path]:
    return [
        skill_path
        for skill_path in iter_skill_paths(repo_root, requested_paths)
        if skill_path.is_file()
        and not _vendored_path_lib.is_vendored(repo_root, skill_path, vendored_prefixes_list)
    ]


def _empty_rules_warnings(skill_count: int, requested_paths: list[str]) -> list[dict[str, Any]]:
    if skill_count:
        return [
            {
                "warning_id": "skill_ergonomics_gate_rules_empty",
                "message": (
                    "skill_ergonomics_gate_rules is empty; skill ergonomics inventory "
                    "is advisory-only and no skill structure heuristics are enforced."
                ),
                "skill_count": skill_count,
                "next_action": (
                    "Run inventory_skill_ergonomics.py for advisory findings or configure "
                    "skill_ergonomics_gate_rules for standing enforcement."
                ),
            }
        ]
    if requested_paths:
        return [
            {
                "warning_id": "skill_ergonomics_requested_paths_empty",
                "message": (
                    "skill_ergonomics_skill_paths is configured but resolved no non-vendored skills; "
                    "skill ergonomics enforcement is disabled."
                ),
                "requested_paths": requested_paths,
                "skill_count": 0,
                "next_action": (
                    "Repair skill_ergonomics_skill_paths or remove the explicit paths so default "
                    "skill discovery can warn on the repo skill surface."
                ),
            }
        ]
    return []


def evaluate(repo_root: Path) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    adapter_errors = adapter.get("errors", []) if adapter.get("valid") is not True else []
    rules: list[str] = adapter["data"].get("skill_ergonomics_gate_rules", []) or []
    requested_paths = adapter["data"].get("skill_ergonomics_skill_paths") or adapter["data"].get(
        "cli_skill_surface_skill_paths"
    ) or []
    runtime_install_prefixes = _vendored_path_lib.vendored_prefixes(_string_list(adapter["data"], "skill_ergonomics_runtime_install_skill_paths"))
    vendored_prefixes_list = _vendored_path_lib.vendored_prefixes(_string_list(adapter["data"], "vendored_paths"))
    if adapter_errors:
        return {
            "adapter_path": adapter.get("path"),
            "adapter_errors": adapter_errors,
            "rules": rules,
            "checked_skills": [],
            "discovery_skipped_reason": "adapter_invalid",
            "discovery_errors": [],
            "violations": [],
            "warnings": [],
        }
    if not rules:
        discovered_skills = _iter_checked_skill_paths(repo_root, requested_paths, vendored_prefixes_list)
        return {
            "adapter_path": adapter.get("path"),
            "adapter_errors": [],
            "rules": [],
            "checked_skills": [],
            "discovery_skipped_reason": None,
            "discovery_errors": [],
            "violations": [],
            "warnings": _empty_rules_warnings(len(discovered_skills), requested_paths),
        }

    checked_skills: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    discovery_errors: list[dict[str, str]] = []
    for skill_path in iter_skill_paths(repo_root, requested_paths):
        if not skill_path.is_file():
            discovery_errors.append(
                {
                    "skill_path": str(skill_path.relative_to(repo_root) if skill_path.is_relative_to(repo_root) else skill_path),
                    "message": "configured skill ergonomics path does not contain SKILL.md",
                }
            )
            continue
        if _vendored_path_lib.is_vendored(repo_root, skill_path, vendored_prefixes_list):
            continue
        item = inventory_skill(repo_root, skill_path, max_core_lines=160, runtime_install_prefixes=runtime_install_prefixes)
        checked_skills.append(
            {
                "skill_id": item["skill_id"],
                "skill_type": item["skill_type"],
                "skill_path": item["skill_path"],
                "heuristics": item["heuristics"],
            }
        )
        if item["skill_type"] != "public":
            continue
        for rule in rules:
            rule_heuristics = RULE_HEURISTICS.get(rule, ())
            if not any(heuristic in item["heuristics"] for heuristic in rule_heuristics):
                continue
            violations.append(
                {
                    "rule": rule,
                    "skill_id": item["skill_id"],
                    "skill_path": item["skill_path"],
                    "heuristics": item["heuristics"],
                    "message": RULE_MESSAGES[rule],
                }
            )
    if rules and not checked_skills:
        discovery_errors.append(
            {
                "skill_path": "",
                "message": "skill_ergonomics_gate_rules are configured but no skills were checked",
            }
        )

    return {
        "adapter_path": adapter.get("path"),
        "adapter_errors": [],
        "rules": rules,
        "checked_skills": checked_skills,
        "discovery_skipped_reason": None,
        "discovery_errors": discovery_errors,
        "violations": violations,
        "warnings": [],
    }


def _format_human(report: dict[str, Any]) -> str:
    if report.get("adapter_errors"):
        return "\n".join(f"quality adapter: {message}" for message in report["adapter_errors"])
    if not report["rules"]:
        warnings = report.get("warnings", [])
        if not warnings:
            return "No skill_ergonomics_gate_rules configured; nothing to check."
        lines = ["No skill_ergonomics_gate_rules configured; nothing to check."]
        for warning in warnings:
            suffix = f" ({warning['skill_count']} skill(s) present)" if "skill_count" in warning else ""
            lines.append(f"WARNING: {warning['message']}{suffix}")
            if warning.get("next_action"):
                lines.append(f"next action: {warning['next_action']}")
        return "\n".join(lines)
    if report["discovery_errors"]:
        return "\n".join(f"skill discovery: {item['message']} {item['skill_path']}".rstrip() for item in report["discovery_errors"])
    if not report["violations"]:
        return (
            "Skill ergonomics gate passed for rules: "
            + ", ".join(report["rules"])
        )
    lines = []
    for violation in report["violations"]:
        lines.append(
            f"{violation['rule']}: {violation['skill_path']} "
            f"({', '.join(violation['heuristics'])})"
        )
    return "\n".join(lines)


def has_failures(report: dict[str, Any]) -> bool:
    return bool(report.get("adapter_errors") or report.get("violations") or report.get("discovery_errors"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root whose skill ergonomics gate rules should be evaluated")
    parser.add_argument("--json", action="store_true", help="Emit the full validation payload as JSON")
    args = parser.parse_args()

    report = evaluate(args.repo_root.resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_format_human(report))
    return 1 if has_failures(report) else 0


if __name__ == "__main__":
    sys.exit(main())
