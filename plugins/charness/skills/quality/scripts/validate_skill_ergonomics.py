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
load_adapter = _resolve_adapter_module.load_adapter


def evaluate(repo_root: Path) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    rules: list[str] = adapter["data"].get("skill_ergonomics_gate_rules", []) or []
    if not rules:
        return {
            "adapter_path": adapter.get("path"),
            "rules": [],
            "checked_skills": [],
            "violations": [],
        }

    checked_skills: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for skill_path in iter_skill_paths(repo_root, []):
        if not skill_path.is_file():
            continue
        item = inventory_skill(repo_root, skill_path, max_core_lines=160)
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
        if "mode_option_pressure_terms" in rules and (
            "mode_pressure_terms_present" in item["heuristics"]
            or "option_pressure_terms_present" in item["heuristics"]
        ):
            violations.append(
                {
                    "rule": "mode_option_pressure_terms",
                    "skill_id": item["skill_id"],
                    "skill_path": item["skill_path"],
                    "heuristics": item["heuristics"],
                    "message": (
                        "Public skill shows repeated `mode`/`option` pressure terms. "
                        "Prefer stronger defaults and inference, or disable the opt-in rule."
                    ),
                }
            )
        if "progressive_disclosure_risk" in rules and (
            "progressive_disclosure_risk" in item["heuristics"]
        ):
            violations.append(
                {
                    "rule": "progressive_disclosure_risk",
                    "skill_id": item["skill_id"],
                    "skill_path": item["skill_path"],
                    "heuristics": item["heuristics"],
                    "message": (
                        "Skill core is large while references/scripts stay absent. "
                        "Move nuance into repo-owned references or scripts, or disable the opt-in rule."
                    ),
                }
            )

    return {
        "adapter_path": adapter.get("path"),
        "rules": rules,
        "checked_skills": checked_skills,
        "violations": violations,
    }


def _format_human(report: dict[str, Any]) -> str:
    if not report["rules"]:
        return "No skill_ergonomics_gate_rules configured; nothing to check."
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = evaluate(args.repo_root.resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_format_human(report))
    return 1 if report["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
