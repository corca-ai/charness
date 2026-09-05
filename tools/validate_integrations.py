#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_control_plane_lib_module = import_repo_module(__file__, "scripts.adapters.control_plane_lib")
load_lock_schema = _scripts_control_plane_lib_module.load_lock_schema
load_manifests = _scripts_control_plane_lib_module.load_manifests
load_manifests_for_discovery = _scripts_control_plane_lib_module.load_manifests_for_discovery
load_dependencies = _scripts_control_plane_lib_module.load_dependencies
load_support_capabilities = _scripts_control_plane_lib_module.load_support_capabilities
lock_paths = _scripts_control_plane_lib_module.lock_paths
validate_lock_data = _scripts_control_plane_lib_module.validate_lock_data
_agent_browser_probe_policy = import_repo_module(__file__, "scripts.evidence.agent_browser_probe_policy")
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
        raise ValidationError(
            f"{path}: grant config layer requires capability_requirements.grant_ids"
        )
    if "env" in layer_types and not requirements.get("env_vars"):
        raise ValidationError(f"{path}: env config layer requires capability_requirements.env_vars")


def validate_shared_declaration_schema(document: dict, path: Path) -> None:
    """The rules an integration manifest and a support capability BOTH declare.

    One home so the two callers cannot drift apart: a rule added for manifests and
    silently not applied to capabilities is a gate whose coverage depends on which
    of two copies the author happened to edit.
    """
    validate_access_mode_order(document, path)
    validate_capability_requirements(document, path)
    validate_config_layers(document, path)


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
        "intent_triggers list so the capability catalog can expose support-bearing manifest intent "
        "queries against this support-bearing manifest. Advisory only; will not fail CI."
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
    if not isinstance(commands, list) or not any(
        isinstance(command, str) and HELP_COMMAND_RE.search(command) for command in commands
    ):
        return None
    if not isinstance(criteria, list):
        return None
    prose_criteria = []
    for criterion in criteria:
        if not isinstance(criterion, str):
            continue
        if not (
            criterion.startswith("stdout_contains:") or criterion.startswith("stderr_contains:")
        ):
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
        owned_manifest_paths = [
            path
            for path in sorted((repo_root / "integrations" / "tools").glob("*.json"))
            if path.name
            not in {"manifest.schema.json", "dependencies.json", "dependencies.schema.json"}
        ]
        if not owned_manifest_paths:
            # Every per-manifest and per-capability rule below iterates a hardcoded
            # glob under this root. Zero repo-owned manifests means those rules ran
            # over nothing while the summary line still read as a validation, so the
            # scope was never established (see the empty-scope family critique). The
            # plugin-fallback manifests `load_manifests` merges in do NOT count: they
            # are not what a `--repo-root` run was asked to validate.
            raise ValidationError(
                f"no integration manifests found under {repo_root / 'integrations' / 'tools'}; "
                "nothing was validated. Check --repo-root."
            )
        for manifest_path in owned_manifest_paths:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            validate_shared_declaration_schema(manifest, manifest_path)
            validate_support_install_entrypoint(manifest, manifest_path)
            validate_agent_browser_check_commands(manifest, manifest_path)
            advisory = detect_help_prose_healthcheck(manifest, manifest_path)
            if advisory is not None:
                advisories.append(advisory)
            advisory = detect_missing_intent_triggers_for_external_binary_with_skill(
                manifest, manifest_path
            )
            if advisory is not None:
                advisories.append(advisory)
        for capability_path in sorted((repo_root / "skills" / "support").glob("*/capability.json")):
            capability = json.loads(capability_path.read_text(encoding="utf-8"))
            validate_shared_declaration_schema(capability, capability_path)
            validate_agent_browser_readiness_commands(capability, capability_path)
        lock_files = lock_paths(repo_root)
        # Zero locks is the SANCTIONED discovered-empty answer, not an unestablished
        # scope: `integrations/locks/*.json` is gitignored, so every fresh clone and
        # every consumer repo that has installed no tool yet has none. Refusing here
        # measured green in this checkout and exited 1 on a fresh clone, and this
        # validator runs in both `run-quality.sh` and the staged commit gate -- so the
        # refusal would have broken every consumer's commit. The count line below is
        # what keeps the empty case honest: it says `0 lock files`, not `validated`.
        lock_schema = load_lock_schema()
        validated_lock_count = 0
        # The lock's reference must resolve to a DISCOVERED owner and carry that
        # owner's identity. `is_file()` plus a successful JSON parse is neither: the
        # lock schema constrains `manifest_path` to any non-empty string, so a stale
        # lock naming `integrations/tools/manifest.schema.json` -- a file this
        # validator explicitly EXCLUDES from the owned set -- existed, parsed, and
        # counted as validated. Nothing bound `tool_id` to anything either.
        owned_by_path: dict[Path, str] = {
            manifest_path: json.loads(manifest_path.read_text(encoding="utf-8"))["tool_id"]
            for manifest_path in owned_manifest_paths
        }
        owned_by_path.update(
            {
                (repo_root / capability["_manifest_path"]).resolve(): capability["tool_id"]
                for capability in support_capabilities
                if capability.get("_manifest_path")
            }
        )
        for path in lock_files:
            lock_data = json.loads(path.read_text(encoding="utf-8"))
            validate_lock_data(lock_data, lock_schema)
            manifest_reference = lock_data["manifest_path"]
            manifest_path = (repo_root / manifest_reference).resolve()
            if not manifest_path.is_file():
                raise ValidationError(
                    f"{path}: referenced manifest {manifest_reference} is missing; "
                    "remove the stale lock or restore the manifest."
                )
            owner_id = owned_by_path.get(manifest_path)
            if owner_id is None:
                raise ValidationError(
                    f"{path}: referenced manifest {manifest_reference} exists but is not a "
                    "discovered tool manifest or support capability; remove the stale lock "
                    "or point it at a declared owner."
                )
            if owner_id != lock_data["tool_id"]:
                raise ValidationError(
                    f"{path}: lock tool_id `{lock_data['tool_id']}` does not match the identity "
                    f"`{owner_id}` declared by {manifest_reference}; the lock names a different owner."
                )
            validated_lock_count += 1
        dependencies = load_dependencies(repo_root)
        if dependencies is not None:
            known_ids = {
                manifest["tool_id"] for manifest in load_manifests_for_discovery(repo_root)
            }
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
        f"{validated_lock_count} lock files, "
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
