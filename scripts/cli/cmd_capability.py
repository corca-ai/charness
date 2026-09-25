"""Capability commands."""

from __future__ import annotations

import argparse
import json
import os
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
    BLOCKING_DOCTOR_DISPOSITIONS,
    CharnessError,
    resolve_target_repo_root,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    emit_yaml,
)
from scripts.cli.capability_support import (  # noqa: E402
    _resolve_charness_repo_root,
    capability_example_template,
    capability_local_template,
    load_repo_capability_config,
    provider_index,
    update_gitignore_for_capability_local,
)
from scripts.cli.common import (  # noqa: E402
    repo_capability_example_path,
    repo_capability_local_path,
    repo_gitignore_path,
    shell_quote,
)
from scripts.cli.process import (  # noqa: E402
    invoke_repo_json_script,
)


def source_env_present(name: str) -> bool:
    return bool(os.environ.get(name, ""))


def capability_setup_guidance(target_repo_root: Path) -> list[str]:
    local_path = repo_capability_local_path(target_repo_root)
    example_path = repo_capability_example_path(target_repo_root)
    return [
        f"Run `charness capability init --target-repo-root {shell_quote(str(target_repo_root))}` to scaffold the repo-local capability files.",
        f"Edit `{local_path}` (gitignored) with real bindings and profiles for this machine.",
        f"`{example_path}` is committed and should describe the shape without secret-name leakage.",
        'Example: {"version":1,"bindings":{"github.default":"github.acme-dev"},"profiles":{"github.acme-dev":{"provider":"github-gh","access_mode_preference":["grant","env"],"env_bindings":{"GH_TOKEN":"GH_TOKEN_ACME_DEV"}}}}',
        "If you previously used the retired `~/.config/charness/capability-profiles.json` and `~/.config/charness/repo-bindings.json` layout, copy each binding/profile entry into the file above. The old machine-local config is no longer read.",
    ]


def resolve_capability(
    *,
    charness_repo_root: Path,
    target_repo_root: Path,
    logical_id: str,
) -> dict[str, object]:
    config = load_repo_capability_config(target_repo_root)
    bindings = config["bindings"]
    profiles = config["profiles"]
    profile_id = bindings.get(logical_id)
    if not profile_id:
        guidance = "\n".join(capability_setup_guidance(target_repo_root))
        if not config["exists"]:
            raise CharnessError(
                f"No repo-local capability config found at `{config['path']}`.\n{guidance}"
            )
        raise CharnessError(
            f"`{config['path']}` does not bind logical capability `{logical_id}`.\n{guidance}"
        )
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        guidance = "\n".join(capability_setup_guidance(target_repo_root))
        raise CharnessError(
            f"`{config['path']}` binds `{logical_id}` to unknown profile `{profile_id}`.\n{guidance}"
        )
    providers = provider_index(charness_repo_root)
    provider_id = profile["provider"]
    provider = providers.get(provider_id)
    if provider is None:
        raise CharnessError(
            f"Profile `{profile_id}` points at unknown provider `{provider_id}` in `{charness_repo_root}`."
        )
    env_bindings = profile.get("env_bindings", {})
    env_status = {
        target_env: {
            "source_env": source_env,
            "present": source_env_present(source_env),
        }
        for target_env, source_env in env_bindings.items()
    }
    return {
        "logical_id": logical_id,
        "target_repo_root": str(target_repo_root),
        "profile_id": profile_id,
        "provider_id": provider_id,
        "provider_kind": provider.get("kind"),
        "provider_manifest_path": provider.get("manifest_path"),
        "access_mode_preference": profile.get("access_mode_preference", []),
        "env_bindings": env_bindings,
        "env_binding_status": env_status,
        "capability_config_path": config["path"],
    }


def write_json_scaffold(path: Path, payload: dict[str, object], *, force: bool) -> str:
    if path.exists() and not force:
        return "exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return "written"


def load_skill_capability_needs(
    charness_repo_root: Path, skill_id: str
) -> dict[str, object] | None:
    path = charness_repo_root / "skills" / "public" / skill_id / "capability-needs.json"
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CharnessError(f"`{path}` must contain a JSON object.")
    return {"path": str(path), **payload}


def explain_skill_capabilities(
    *,
    charness_repo_root: Path,
    target_repo_root: Path,
    skill_id: str,
) -> dict[str, object]:
    payload = load_skill_capability_needs(charness_repo_root, skill_id)
    if payload is None:
        return {
            "skill_id": skill_id,
            "skill_path": str(charness_repo_root / "skills" / "public" / skill_id),
            "capability_needs": [],
            "notes": ["No explicit capability requirements are recorded for this skill."],
        }
    capability_needs = payload.get("capability_needs", [])
    if not isinstance(capability_needs, list):
        raise CharnessError(f"`{payload['path']}` must keep `capability_needs` as a list.")
    notes = payload.get("notes", [])
    if not isinstance(notes, list):
        raise CharnessError(f"`{payload['path']}` must keep `notes` as a list.")
    response = {
        "skill_id": skill_id,
        "skill_path": str(charness_repo_root / "skills" / "public" / skill_id),
        "metadata_path": payload["path"],
        "capability_needs": capability_needs,
        "notes": notes,
    }
    if skill_id == "announcement":
        adapter_payload = invoke_repo_json_script(
            charness_repo_root,
            "skills/public/announcement/scripts/resolve_adapter.py",
            "--repo-root",
            str(target_repo_root),
        )
        adapter_data = adapter_payload["data"]
        delivery_contract = adapter_payload.get("delivery_contract", {})
        delivery_kind = adapter_data.get("delivery_kind")
        delivery_capability = adapter_data.get("delivery_capability")
        response["announcement_delivery"] = {
            "delivery_kind": delivery_kind,
            "delivery_capability": delivery_capability,
            "status": delivery_contract.get("status"),
            "blocking_issues": delivery_contract.get("blocking_issues", []),
        }
        if delivery_kind == "human-backend" and delivery_contract.get("status") == "executable":
            if isinstance(delivery_capability, str) and delivery_capability:
                response["capability_needs"] = [
                    *capability_needs,
                    {
                        "logical_id": delivery_capability,
                        "summary": "Repo-configured human-backend delivery capability for announcement.",
                        "when": "when announcement delivers through the current repo adapter backend",
                    },
                ]
            else:
                response["notes"] = [
                    *notes,
                    "The current announcement adapter uses `human-backend` delivery but does not set `delivery_capability` yet.",
                ]
        elif delivery_kind == "human-backend":
            response["notes"] = [
                *notes,
                "The current announcement adapter is draft-only until its delivery contract is executable.",
            ]
    return response


def capability_doctor_payload(
    *,
    charness_repo_root: Path,
    resolved: dict[str, object],
) -> dict[str, object]:
    provider_id = resolved["provider_id"]
    doctor_results = invoke_repo_json_script(
        charness_repo_root,
        "scripts/doctor.py",
        "--repo-root",
        str(charness_repo_root),
        "--tool-id",
        str(provider_id),
        allow_failure=True,
    )
    provider_result = None
    if isinstance(doctor_results, list):
        for item in doctor_results:
            if isinstance(item, dict) and item.get("tool_id") == provider_id:
                provider_result = item
                break
    if provider_result is None:
        raise CharnessError(
            f"Provider `{provider_id}` did not resolve to a doctor payload in `{charness_repo_root}`."
        )
    missing_env_sources = [
        status["source_env"]
        for status in resolved["env_binding_status"].values()
        if isinstance(status, dict) and status.get("present") is False
    ]
    return {
        **resolved,
        "provider_doctor": provider_result,
        "missing_env_sources": missing_env_sources,
    }


def print_capability_summary(payload: dict[str, object]) -> None:
    print(f"LOGICAL_ID: {payload['logical_id']}")
    print(f"TARGET_REPO_ROOT: {payload['target_repo_root']}")
    print(f"CONFIG: {payload['capability_config_path']}")
    print(f"PROFILE: {payload['profile_id']}")
    print(f"PROVIDER: {payload['provider_id']} ({payload['provider_kind']})")
    print(f"PROVIDER_MANIFEST: {payload['provider_manifest_path']}")
    env_bindings = payload.get("env_bindings", {})
    if isinstance(env_bindings, dict) and env_bindings:
        for target_env, source_env in env_bindings.items():
            status = payload.get("env_binding_status", {}).get(target_env, {})
            present = "present" if isinstance(status, dict) and status.get("present") else "missing"
            print(f"ENV_BINDING: {target_env} <- {source_env} ({present})")
    else:
        print("ENV_BINDING: none")
    doctor = payload.get("provider_doctor")
    if isinstance(doctor, dict):
        print(f"PROVIDER_DOCTOR: {doctor.get('doctor_status')} ({doctor.get('support_state')})")


def print_capability_explain_summary(payload: dict[str, object]) -> None:
    print(f"SKILL: {payload['skill_id']}")
    metadata_path = payload.get("metadata_path")
    if isinstance(metadata_path, str):
        print(f"METADATA: {metadata_path}")
    capability_needs = payload.get("capability_needs", [])
    if isinstance(capability_needs, list) and capability_needs:
        for need in capability_needs:
            if not isinstance(need, dict):
                continue
            logical_id = need.get("logical_id")
            summary = need.get("summary")
            when = need.get("when")
            print(f"NEEDS: {logical_id} - {summary}")
            if isinstance(when, str) and when:
                print(f"  WHEN: {when}")
    else:
        print("NEEDS: none")
    notes = payload.get("notes", [])
    if isinstance(notes, list):
        for note in notes:
            if isinstance(note, str):
                print(f"NOTE: {note}")
    announcement_delivery = payload.get("announcement_delivery")
    if isinstance(announcement_delivery, dict):
        print(
            "ANNOUNCEMENT_DELIVERY: "
            f"{announcement_delivery.get('delivery_kind')} "
            f"{announcement_delivery.get('status') or ''} "
            f"{announcement_delivery.get('delivery_capability') or ''}".rstrip()
        )


def cmd_capability_init(args: argparse.Namespace) -> int:
    target_repo_root = resolve_target_repo_root(args.target_repo_root)
    local_path = repo_capability_local_path(target_repo_root)
    example_path = repo_capability_example_path(target_repo_root)
    local_status = write_json_scaffold(local_path, capability_local_template(), force=args.force)
    example_status = write_json_scaffold(
        example_path, capability_example_template(), force=args.force
    )
    gitignore_status = update_gitignore_for_capability_local(target_repo_root)
    payload = {
        "target_repo_root": str(target_repo_root),
        "capability_local_path": str(local_path),
        "capability_example_path": str(example_path),
        "capability_local_status": local_status,
        "capability_example_status": example_status,
        "gitignore_path": str(repo_gitignore_path(target_repo_root)),
        "gitignore_status": gitignore_status,
        "next_steps": [
            f"Edit `{local_path}` to replace `*.change-me` bindings/profiles with real values for THIS machine.",
            f"`{example_path}` is committed and should describe the shape without leaking real source env names.",
            "Run `charness capability explain gather` or `charness capability explain announcement` to see skill-facing logical capability expectations.",
        ],
    }
    emit_yaml(payload)
    return 0


def cmd_capability_resolve(args: argparse.Namespace) -> int:
    charness_repo_root = _resolve_charness_repo_root(args)
    resolved = resolve_capability(
        charness_repo_root=charness_repo_root,
        target_repo_root=resolve_target_repo_root(args.target_repo_root),
        logical_id=args.logical_id,
    )
    emit_yaml(resolved)
    return 0


def cmd_capability_doctor(args: argparse.Namespace) -> int:
    charness_repo_root = _resolve_charness_repo_root(args)
    resolved = resolve_capability(
        charness_repo_root=charness_repo_root,
        target_repo_root=resolve_target_repo_root(args.target_repo_root),
        logical_id=args.logical_id,
    )
    payload = capability_doctor_payload(charness_repo_root=charness_repo_root, resolved=resolved)
    emit_yaml(payload)
    doctor = payload["provider_doctor"]
    if doctor.get("doctor_disposition") in BLOCKING_DOCTOR_DISPOSITIONS:
        return 1
    if payload["missing_env_sources"]:
        return 1
    return 0


def cmd_capability_env(args: argparse.Namespace) -> int:
    charness_repo_root = _resolve_charness_repo_root(args)
    resolved = resolve_capability(
        charness_repo_root=charness_repo_root,
        target_repo_root=resolve_target_repo_root(args.target_repo_root),
        logical_id=args.logical_id,
    )
    env_bindings = resolved["env_bindings"]
    if not env_bindings:
        raise CharnessError(
            f"Profile `{resolved['profile_id']}` for `{args.logical_id}` does not declare any `env_bindings`."
        )
    missing_sources = [
        status["source_env"]
        for status in resolved["env_binding_status"].values()
        if isinstance(status, dict) and status.get("present") is False
    ]
    if missing_sources:
        raise CharnessError(
            f"Profile `{resolved['profile_id']}` is missing source env vars: {', '.join(missing_sources)}."
        )
    shell_lines = [
        f'export {target_env}="${{{source_env}}}"'
        for target_env, source_env in env_bindings.items()
    ]
    emit_yaml({**resolved, "shell_exports": shell_lines})
    return 0


def cmd_capability_explain(args: argparse.Namespace) -> int:
    charness_repo_root = _resolve_charness_repo_root(args)
    payload = explain_skill_capabilities(
        charness_repo_root=charness_repo_root,
        target_repo_root=resolve_target_repo_root(args.target_repo_root),
        skill_id=args.skill_id,
    )
    emit_yaml(payload)
    return 0
