#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
_scripts_cautilus_adapter_lib_module = import_repo_module(__file__, "scripts.cautilus_adapter_lib")
ARTIFACT_PATH = _scripts_cautilus_adapter_lib_module.ARTIFACT_PATH
load_cautilus_adapter = _scripts_cautilus_adapter_lib_module.load_cautilus_adapter
_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
dedupe_preserve_order = _scripts_surfaces_lib_module.dedupe_preserve_order
normalize_repo_path = _scripts_surfaces_lib_module.normalize_repo_path

INSTRUCTION_SURFACE_COMMAND = "cautilus instruction-surface test --repo-root ."
COMPARE_COMMANDS = [
    "cautilus workspace prepare-compare",
    "cautilus mode evaluate --baseline-ref <ref>",
]
SKILL_CORE_PATTERNS = ("skills/public/*/SKILL.md", "skills/support/*/SKILL.md")
ADAPTER_PATTERNS = (".agents/*-adapter.yaml", ".agents/cautilus-adapters/*.yaml")
TRUTH_SURFACE_FALLBACKS = (
    "README.md",
    "docs/roadmap.md",
    "docs/operator-acceptance.md",
    "docs/handoff.md",
)


def _match_any(path: str, patterns: list[str] | tuple[str, ...]) -> bool:
    normalized = normalize_repo_path(path)
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def _matched_paths(changed_paths: list[str], patterns: list[str] | tuple[str, ...]) -> list[str]:
    return [path for path in changed_paths if _match_any(path, patterns)]


def _intent_tags(
    changed_paths: list[str],
    prompt_paths: list[str],
    scenario_paths: list[str],
    truth_surface_paths: list[str],
    cross_repo_paths: list[str],
) -> list[str]:
    tags: list[str] = []
    if prompt_paths:
        tags.append("prompt_affecting_change")
    if _matched_paths(changed_paths, SKILL_CORE_PATTERNS):
        tags.append("skill_core_change")
    if _matched_paths(changed_paths, ADAPTER_PATTERNS):
        tags.append("adapter_contract_change")
    if truth_surface_paths:
        tags.append("truth_surface_change")
    if scenario_paths:
        tags.append("scenario_review_change")
    if cross_repo_paths:
        tags.append("cross_repo_communication_change")
    return dedupe_preserve_order(tags)


def plan_cautilus_proof(repo_root: Path, changed_paths: list[str]) -> dict[str, object]:
    adapter_payload = load_cautilus_adapter(repo_root)
    if not adapter_payload["valid"]:
        raise SurfaceError("; ".join(adapter_payload["errors"]))

    normalized_paths = dedupe_preserve_order([normalize_repo_path(path) for path in changed_paths])
    data = adapter_payload["data"]
    prompt_paths = _matched_paths(normalized_paths, data["prompt_affecting_patterns"])
    scenario_paths = _matched_paths(normalized_paths, data["scenario_review_patterns"])
    truth_surface_patterns = data.get("truth_surface_patterns") or list(TRUTH_SURFACE_FALLBACKS)
    truth_surface_paths = _matched_paths(normalized_paths, truth_surface_patterns)
    cross_repo_paths = _matched_paths(normalized_paths, data.get("cross_repo_issue_patterns", []))
    required = bool(prompt_paths)
    proof_kinds: list[str] = []
    if required:
        proof_kinds.append("regression")
    if scenario_paths or truth_surface_paths or cross_repo_paths:
        proof_kinds.append("scenario_review")
    artifact_changed = ARTIFACT_PATH in normalized_paths
    run_mode = data["run_mode"]
    must_ask_before_running = run_mode == "ask" or (run_mode == "adaptive" and "scenario_review" in proof_kinds)
    recommended_commands = [INSTRUCTION_SURFACE_COMMAND] if required else []
    if not required:
        status = "not-required"
    elif artifact_changed:
        status = "ready-for-validation"
    else:
        status = "needs-proof"
    next_action = "none"
    if status == "needs-proof":
        next_action = "ask-before-running" if must_ask_before_running else "run-proof-and-refresh-artifact"
    notes: list[str] = []
    if run_mode == "ask":
        notes.append("Repo policy is ask-before-run: closeout must stop before any cautilus execution.")
    elif run_mode == "adaptive" and "scenario_review" in proof_kinds:
        notes.append("Repo policy is adaptive: high-leverage prompt changes require explicit confirmation before cautilus runs.")
    elif run_mode == "adaptive":
        notes.append("Repo policy is adaptive: low-cost regression proof is eligible for autonomous execution, but closeout still waits for the refreshed artifact.")
    elif run_mode == "auto":
        notes.append("Repo policy is auto: cautilus proof may run without an extra confirmation step when the operator workflow chooses to execute it.")
    if "scenario_review" in proof_kinds:
        notes.append("This slice needs a scenario review, not only regression proof.")

    return {
        "required": required,
        "status": status,
        "artifact_path": ARTIFACT_PATH,
        "artifact_changed": artifact_changed,
        "run_mode": run_mode,
        "must_ask_before_running": must_ask_before_running,
        "goal": "preserve",
        "proof_kinds": proof_kinds,
        "prompt_affecting_paths": prompt_paths,
        "scenario_review_paths": scenario_paths,
        "truth_surface_paths": truth_surface_paths,
        "cross_repo_issue_paths": cross_repo_paths,
        "intent_tags": _intent_tags(normalized_paths, prompt_paths, scenario_paths, truth_surface_paths, cross_repo_paths),
        "recommended_commands": recommended_commands,
        "recommended_followups": (
            ["review one or two representative scenarios and record what changed"]
            if "scenario_review" in proof_kinds
            else []
        ),
        "next_action": next_action,
        "notes": notes,
        "adapter": {
            "found": adapter_payload["found"],
            "path": adapter_payload["path"],
            "warnings": adapter_payload["warnings"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to current git diff.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    changed_paths = [normalize_repo_path(path) for path in args.paths] if args.paths else collect_changed_paths(repo_root)
    plan = plan_cautilus_proof(repo_root, changed_paths)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(f"status: {plan['status']}")
        if plan["required"]:
            print(f"run_mode: {plan['run_mode']}")
            print(f"proof_kinds: {', '.join(plan['proof_kinds'])}")
            print(f"next_action: {plan['next_action']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
