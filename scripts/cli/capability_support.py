"""Capability templates and repo onboarding support."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import (  # noqa: E402
    CAPABILITY_LOCAL_GITIGNORE_LINE,
    REPO_URL,
    CharnessError,
    ensure_checkout,
    has_source_manifest,
    resolve_repo_root,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    default_home_root,
)
from scripts.cli.common import (  # noqa: E402
    parse_repo_script_payload,
    repo_capability_local_path,
    repo_gitignore_path,
)
from scripts.cli.install_delivery import (  # noqa: E402
    looks_like_repo_root,
)
from scripts.cli.process import (  # noqa: E402
    invoke_repo_script,
)


def read_json_mapping(path: Path, *, default: dict[str, object]) -> dict[str, object]:
    if not path.is_file():
        return dict(default)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(default)
    if not isinstance(payload, dict):
        return dict(default)
    merged = dict(default)
    merged.update(payload)
    return merged


def load_repo_capability_config(target_repo_root: Path) -> dict[str, object]:
    path = repo_capability_local_path(target_repo_root)
    payload = read_json_mapping(path, default={"schema_version": 1, "bindings": {}, "profiles": {}})
    bindings = payload.get("bindings", {})
    if not isinstance(bindings, dict):
        raise CharnessError(
            f"`{path}` must keep `bindings` as an object mapping logical ids to profile ids."
        )
    normalized_bindings: dict[str, str] = {}
    for logical_id, profile_id in bindings.items():
        if (
            not isinstance(logical_id, str)
            or not logical_id
            or not isinstance(profile_id, str)
            or not profile_id
        ):
            raise CharnessError(
                f"`{path}` `bindings` must map string capability ids to string profile ids."
            )
        normalized_bindings[logical_id] = profile_id
    profiles = payload.get("profiles", {})
    if not isinstance(profiles, dict):
        raise CharnessError(f"`{path}` must keep `profiles` as an object.")
    normalized_profiles: dict[str, dict[str, object]] = {}
    for profile_id, raw in profiles.items():
        if not isinstance(profile_id, str) or not profile_id:
            raise CharnessError(f"`{path}` contains an invalid profile id.")
        if not isinstance(raw, dict):
            raise CharnessError(f"`{path}` profile `{profile_id}` must be an object.")
        provider = raw.get("provider")
        if not isinstance(provider, str) or not provider:
            raise CharnessError(
                f"`{path}` profile `{profile_id}` must declare a non-empty `provider`."
            )
        access_mode_preference = raw.get("access_mode_preference", [])
        if not isinstance(access_mode_preference, list) or not all(
            isinstance(item, str) for item in access_mode_preference
        ):
            raise CharnessError(
                f"`{path}` profile `{profile_id}` has an invalid `access_mode_preference` list."
            )
        env_bindings = raw.get("env_bindings", {})
        if not isinstance(env_bindings, dict) or not all(
            isinstance(key, str) and key and isinstance(value, str) and value
            for key, value in env_bindings.items()
        ):
            raise CharnessError(f"`{path}` profile `{profile_id}` has invalid `env_bindings`.")
        normalized_profiles[profile_id] = {
            "provider": provider,
            "access_mode_preference": access_mode_preference,
            "env_bindings": env_bindings,
        }
    return {
        "schema_version": payload.get("schema_version", 1),
        "path": str(path),
        "exists": path.is_file(),
        "bindings": normalized_bindings,
        "profiles": normalized_profiles,
    }


def provider_index(repo_root: Path) -> dict[str, dict[str, object]]:
    providers: dict[str, dict[str, object]] = {}
    tools_dir = repo_root / "integrations" / "tools"
    if tools_dir.is_dir():
        for path in sorted(tools_dir.glob("*.json")):
            if path.name == "manifest.schema.json":
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            tool_id = data.get("tool_id")
            if isinstance(tool_id, str) and tool_id:
                providers[tool_id] = {
                    "provider_id": tool_id,
                    "kind": data.get("kind"),
                    "manifest_path": str(path.relative_to(repo_root)),
                }
    support_root = repo_root / "skills" / "support"
    if support_root.is_dir():
        for path in sorted(support_root.glob("*/capability.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            capability_id = data.get("capability_id")
            if isinstance(capability_id, str) and capability_id:
                providers[capability_id] = {
                    "provider_id": capability_id,
                    "kind": data.get("kind"),
                    "manifest_path": str(path.relative_to(repo_root)),
                }
    return providers


def build_repo_onboarding_payload(
    *,
    source_repo_root: Path,
    target_repo_root: Path,
) -> dict[str, object]:
    resolved_target = target_repo_root.resolve()
    payload: dict[str, object] = {
        "target_repo_root": str(resolved_target),
        "status": "not-applicable",
        "manual_action_required": False,
        "message": None,
        "source": "repo_onboarding",
    }
    if resolved_target == source_repo_root.resolve():
        payload["status"] = "source-checkout"
        return payload
    if not looks_like_repo_root(resolved_target):
        payload["status"] = "not-a-repo"
        return payload
    if not has_source_manifest(source_repo_root):
        payload["status"] = "source-missing"
        payload["manual_action_required"] = True
        payload["message"] = (
            "charness source checkout is missing, so repo onboarding could not be inspected yet. "
            "Run `charness init` first, then rerun `charness doctor` from the target repo."
        )
        return payload

    inspect_payload = parse_repo_script_payload(
        invoke_repo_script(
            source_repo_root,
            "skills/public/setup/scripts/inspect_repo.py",
            "--repo-root",
            str(resolved_target),
        ),
        "skills/public/setup/scripts/inspect_repo.py",
    )
    payload["inspection"] = inspect_payload
    repo_mode = inspect_payload.get("repo_mode")
    agent_docs = (
        inspect_payload.get("agent_docs")
        if isinstance(inspect_payload.get("agent_docs"), dict)
        else {}
    )
    reasons: list[str] = []
    if repo_mode in {"GREENFIELD", "PARTIAL"}:
        reasons.append("core_operating_surface")
    if agent_docs.get("recommended_action") != "leave_as_is":
        reasons.append("agent_docs")
    payload["reasons"] = reasons
    payload["skill_bearing_repo"] = any(
        (resolved_target / candidate).is_dir() for candidate in ("skills/public", "skills/support")
    )
    if reasons:
        payload["status"] = "required"
        payload["manual_action_required"] = True
        opener = (
            "This repo already carries repo-owned skills and should freeze skill intent/proof seams before later edits."
            if payload["skill_bearing_repo"]
            else "This repo does not look fully charness-onboarded yet."
        )
        payload["message"] = (
            f"{opener} After restarting the host, start a repo-root session and run the `setup` skill before broader work."
        )
        return payload
    payload["status"] = "ready"
    return payload


def capability_local_template() -> dict[str, object]:
    return {
        "version": 1,
        "$schema_note": "This file is gitignored. Replace `*.change-me` profiles with real provider identities for THIS machine. Source env names below are non-secret aliases that point at machine-local env vars holding the actual secret.",
        "bindings": {
            "github.default": "github.change-me",
        },
        "profiles": {
            "github.change-me": {
                "provider": "github-gh",
                "access_mode_preference": ["binary", "public"],
                "env_bindings": {},
            },
        },
    }


def capability_example_template() -> dict[str, object]:
    return {
        "version": 1,
        "$schema_note": "Committed example. The real config lives at `.charness/local/capability.json` (gitignored). `bindings` map skill-facing logical ids to local profile ids. `profiles` declare one reusable provider identity each. `env_bindings` map runtime env names to non-secret SOURCE env names this machine already exports; raw secret values must never appear here.",
        "bindings": {
            "github.default": "github.example-workspace",
        },
        "profiles": {
            "github.example-workspace": {
                "provider": "github-gh",
                "access_mode_preference": ["grant", "env"],
                "env_bindings": {
                    "GH_TOKEN": "GH_TOKEN_EXAMPLE_WORKSPACE",
                },
            },
        },
    }


def update_gitignore_for_capability_local(target_repo_root: Path) -> str:
    path = repo_gitignore_path(target_repo_root)
    line = CAPABILITY_LOCAL_GITIGNORE_LINE
    if path.is_file():
        existing = path.read_text(encoding="utf-8")
        existing_lines = existing.splitlines()
        if line in existing_lines:
            return "already-present"
        suffix = "" if existing.endswith("\n") or existing == "" else "\n"
        path.write_text(existing + suffix + line + "\n", encoding="utf-8")
        return "appended"
    path.write_text(line + "\n", encoding="utf-8")
    return "created"


def _resolve_charness_repo_root(args: argparse.Namespace) -> Path:
    home_root = getattr(args, "home_root", default_home_root()).resolve()
    charness_repo_root, managed_checkout = resolve_repo_root(home_root, args.repo_root)
    charness_repo_root = ensure_checkout(
        charness_repo_root,
        managed=managed_checkout,
        repo_url=getattr(args, "repo_url", REPO_URL),
        allow_clone=False,
        allow_pull=False,
    )["repo_root"]
    return Path(charness_repo_root)
