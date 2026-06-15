#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_control_plane_lib_module = import_repo_module(__file__, "scripts.control_plane_lib")
load_lock_schema = _scripts_control_plane_lib_module.load_lock_schema
load_manifests = _scripts_control_plane_lib_module.load_manifests
load_manifests_for_discovery = _scripts_control_plane_lib_module.load_manifests_for_discovery
load_dependencies = _scripts_control_plane_lib_module.load_dependencies
load_support_capabilities = _scripts_control_plane_lib_module.load_support_capabilities
lock_paths = _scripts_control_plane_lib_module.lock_paths
validate_lock_data = _scripts_control_plane_lib_module.validate_lock_data
_agent_browser_probe_policy = import_repo_module(__file__, "scripts.agent_browser_probe_policy")
unsafe_agent_browser_probe_reason = _agent_browser_probe_policy.unsafe_agent_browser_probe_reason


class ValidationError(Exception):
    pass


ACCESS_MODE_ORDER = {
    "grant": 0,
    "binary": 1,
    "env": 2,
    "public": 3,
    "human-only": 4,
    "degraded": 5,
}

CONFIG_LAYER_ORDER = {
    "grant": 0,
    "authenticated-binary": 1,
    "env": 2,
    "operator-step": 3,
    "public-fallback": 4,
}

CAUTILUS_GENERIC_INTENT_TRIGGER_RE = re.compile(
    r"(^|\b)(verify|verification|evaluate|evaluation|review|closeout|"
    r"quality review|run quality|검증|평가|리뷰|검토)(\b|$)",
    re.IGNORECASE,
)
CAUTILUS_SPECIFIC_INTENT_RE = re.compile(
    r"(evaluator-backed|behavior|prompt|instruction|regression|baseline|"
    r"compare|operator reading|cautilus|프롬프트|동작)",
    re.IGNORECASE,
)
HELP_COMMAND_RE = re.compile(r"(^|\s)(--help|-help|help)(\s|$)")


def validate_access_mode_order(manifest: dict[str, object], path: Path) -> None:
    access_modes = manifest.get("access_modes", [])
    if not isinstance(access_modes, list):
        return
    ranks = [ACCESS_MODE_ORDER[mode] for mode in access_modes]
    if ranks != sorted(ranks):
        raise ValidationError(
            f"{path}: access_modes must stay in preferred runtime order "
            "(grant, binary, env, public, human-only, degraded)"
        )


def validate_capability_requirements(manifest: dict[str, object], path: Path) -> None:
    access_modes = manifest.get("access_modes", [])
    if not isinstance(access_modes, list):
        return
    requirements = manifest.get("capability_requirements")
    if not isinstance(requirements, dict):
        requirements = {}
    if "grant" in access_modes and not requirements.get("grant_ids"):
        raise ValidationError(f"{path}: grant access requires capability_requirements.grant_ids")
    if "env" in access_modes and not requirements.get("env_vars"):
        raise ValidationError(f"{path}: env access requires capability_requirements.env_vars")


def validate_config_layers(manifest: dict[str, object], path: Path) -> None:
    config_layers = manifest.get("config_layers", [])
    if not isinstance(config_layers, list):
        return
    layer_types = [layer["layer_type"] for layer in config_layers]
    ranks = [CONFIG_LAYER_ORDER[layer_type] for layer_type in layer_types]
    if ranks != sorted(ranks):
        raise ValidationError(
            f"{path}: config_layers must stay in preferred order "
            "(grant, authenticated-binary, env, operator-step, public-fallback)"
        )
    requirements = manifest.get("capability_requirements")
    if not isinstance(requirements, dict):
        requirements = {}
    if "grant" in layer_types and not requirements.get("grant_ids"):
        raise ValidationError(f"{path}: grant config layer requires capability_requirements.grant_ids")
    if "env" in layer_types and not requirements.get("env_vars"):
        raise ValidationError(f"{path}: env config layer requires capability_requirements.env_vars")


def validate_support_install_entrypoint(manifest: dict[str, object], path: Path) -> None:
    support = manifest.get("support_skill_source")
    if not isinstance(support, dict):
        return
    lifecycle = manifest.get("lifecycle")
    if not isinstance(lifecycle, dict):
        return
    install = lifecycle.get("install")
    if not isinstance(install, dict):
        return
    if install.get("mode") == "none":
        return
    install_url = install.get("install_url")
    if not isinstance(install_url, str) or not install_url:
        raise ValidationError(
            f"{path}: integrations with support_skill_source must declare lifecycle.install.install_url "
            "so agents have an exact install-doc entrypoint."
        )


def detect_missing_intent_triggers_for_external_binary_with_skill(
    manifest: dict[str, object], path: Path
) -> str | None:
    if manifest.get("kind") != "external_binary_with_skill":
        return None
    triggers = manifest.get("intent_triggers")
    if isinstance(triggers, list) and triggers:
        return None
    return (
        f"{path}: kind=external_binary_with_skill manifests should declare a non-empty "
        "intent_triggers list so find-skills --recommend-for-task can match natural-language "
        "queries against this support-bearing manifest. Advisory only; will not fail CI."
    )


def validate_cautilus_trigger_specificity(manifest: dict[str, object], path: Path) -> None:
    if manifest.get("tool_id") != "cautilus":
        return
    triggers = manifest.get("intent_triggers", [])
    if not isinstance(triggers, list):
        return
    generic = sorted(
        trigger
        for trigger in triggers
        if isinstance(trigger, str)
        and CAUTILUS_GENERIC_INTENT_TRIGGER_RE.search(trigger)
        and not CAUTILUS_SPECIFIC_INTENT_RE.search(trigger)
    )
    if generic:
        rendered = ", ".join(f"`{trigger}`" for trigger in generic)
        raise ValidationError(
            f"{path}: cautilus intent_triggers must not use generic review/closeout terms "
            f"({rendered}); use evaluator-backed behavior, prompt regression, or compare-specific triggers."
        )


def validate_agent_browser_check_commands(manifest: dict[str, object], path: Path) -> None:
    checks = manifest.get("checks")
    if not isinstance(checks, dict):
        return
    for check_name, check in checks.items():
        if not isinstance(check, dict):
            continue
        commands = check.get("commands")
        if not isinstance(commands, list):
            continue
        for index, command in enumerate(commands):
            if not isinstance(command, str):
                continue
            reason = unsafe_agent_browser_probe_reason(command)
            if reason is None:
                continue
            raise ValidationError(
                f"{path}: checks.{check_name}.commands[{index}] uses unsafe agent-browser probe "
                f"`{command}`: {reason}"
            )


def detect_help_prose_healthcheck(manifest: dict[str, object], path: Path) -> str | None:
    healthcheck = manifest.get("checks", {}).get("healthcheck")
    if not isinstance(healthcheck, dict):
        return None
    commands = healthcheck.get("commands")
    criteria = healthcheck.get("success_criteria")
    if not isinstance(commands, list) or not any(isinstance(command, str) and HELP_COMMAND_RE.search(command) for command in commands):
        return None
    if not isinstance(criteria, list):
        return None
    prose_criteria = []
    for criterion in criteria:
        if not isinstance(criterion, str):
            continue
        if not (criterion.startswith("stdout_contains:") or criterion.startswith("stderr_contains:")):
            continue
        expected = criterion.split(":", 1)[1].strip()
        if " " in expected and len(expected) > 10:
            prose_criteria.append(criterion)
    if not prose_criteria:
        return None
    rendered = ", ".join(f"`{criterion}`" for criterion in prose_criteria)
    return (
        f"{path}: checks.healthcheck is coupled to help prose ({rendered}). "
        "Prefer no healthcheck, a repo-owned probe, or a machine-readable read-only consumer probe."
    )


def validate_agent_browser_readiness_commands(capability: dict[str, object], path: Path) -> None:
    checks = capability.get("readiness_checks")
    if not isinstance(checks, list):
        return
    for check_index, check in enumerate(checks):
        if not isinstance(check, dict):
            continue
        commands = check.get("commands")
        if not isinstance(commands, list):
            continue
        for command_index, command in enumerate(commands):
            if not isinstance(command, str):
                continue
            reason = unsafe_agent_browser_probe_reason(command)
            if reason is None:
                continue
            raise ValidationError(
                f"{path}: readiness_checks[{check_index}].commands[{command_index}] "
                f"uses unsafe agent-browser probe `{command}`: {reason}"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    try:
        repo_root = args.repo_root.resolve()
        manifests = load_manifests(repo_root)
        support_capabilities = load_support_capabilities(repo_root)
        advisories: list[str] = []
        for manifest_path in sorted((repo_root / "integrations" / "tools").glob("*.json")):
            if manifest_path.name in {"manifest.schema.json", "dependencies.json", "dependencies.schema.json"}:
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            validate_access_mode_order(manifest, manifest_path)
            validate_capability_requirements(manifest, manifest_path)
            validate_config_layers(manifest, manifest_path)
            validate_support_install_entrypoint(manifest, manifest_path)
            validate_cautilus_trigger_specificity(manifest, manifest_path)
            validate_agent_browser_check_commands(manifest, manifest_path)
            advisory = detect_help_prose_healthcheck(manifest, manifest_path)
            if advisory is not None:
                advisories.append(advisory)
            advisory = detect_missing_intent_triggers_for_external_binary_with_skill(manifest, manifest_path)
            if advisory is not None:
                advisories.append(advisory)
        for capability_path in sorted((repo_root / "skills" / "support").glob("*/capability.json")):
            capability = json.loads(capability_path.read_text(encoding="utf-8"))
            validate_access_mode_order(capability, capability_path)
            validate_capability_requirements(capability, capability_path)
            validate_config_layers(capability, capability_path)
            validate_agent_browser_readiness_commands(capability, capability_path)
        lock_schema = load_lock_schema()
        lock_files = lock_paths(repo_root)
        for path in lock_files:
            validate_lock_data(json.loads(path.read_text(encoding="utf-8")), lock_schema)
        dependencies = load_dependencies(repo_root)
        if dependencies is not None:
            known_ids = {manifest["tool_id"] for manifest in load_manifests_for_discovery(repo_root)}
            unknown = [tid for tid in dependencies["tool_dependencies"] if tid not in known_ids]
            if unknown:
                rendered = ", ".join(f"`{tid}`" for tid in unknown)
                raise ValidationError(
                    f"integrations/tools/dependencies.json references unknown tool_ids: {rendered}"
                )
    except Exception as exc:  # pragma: no cover - surfaced via CLI tests
        raise ValidationError(str(exc)) from exc
    dep_count = 0 if dependencies is None else len(dependencies["tool_dependencies"])
    for advisory in advisories:
        print(f"advisory: {advisory}", file=sys.stderr)
    print(
        f"Validated {len(manifests)} integration manifests, "
        f"{len(support_capabilities)} support capabilities, "
        f"{len(lock_files)} lock files, "
        f"{dep_count} declared tool dependencies."
        + (f" {len(advisories)} advisory note(s)." if advisories else "")
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
