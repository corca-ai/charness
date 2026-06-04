#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import runpy
import shutil
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()

_resolve_adapter_module = importlib.util.spec_from_file_location(
    "gather_resolve_adapter",
    Path(__file__).resolve().parent / "resolve_adapter.py",
)
_gather_adapter = importlib.util.module_from_spec(_resolve_adapter_module)
_resolve_adapter_module.loader.exec_module(_gather_adapter)
load_gather_adapter = _gather_adapter.load_adapter

SOURCE_ID = "slack"
SUPPORT_ID = "gather-slack"
REQUIRED_BINARIES = ("node", "jq", "perl")


def resolve_provider_mode(repo_root: Path) -> str:
    adapter = load_gather_adapter(repo_root)
    provider = adapter["data"].get("gather_provider") or {}
    entry = provider.get(SOURCE_ID) or {}
    return entry.get("mode", "direct-cli")


def find_support_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        for candidate in (
            ancestor / "skills" / "support" / SUPPORT_ID,
            ancestor / "support" / SUPPORT_ID,
        ):
            if (candidate / "scripts" / "export-thread.sh").is_file():
                return candidate
    raise FileNotFoundError("support/gather-slack/scripts/export-thread.sh not found")


def portable(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def dependency_status() -> tuple[str, list[str]]:
    missing = [binary for binary in REQUIRED_BINARIES if shutil.which(binary) is None]
    if missing:
        return "not-ready", [f"Install or expose `{binary}` before using Slack gather." for binary in missing]
    return "ready", ["Runtime dependencies for the Slack gather wrapper are available."]


def payload_for(repo_root: Path) -> dict[str, object]:
    mode = resolve_provider_mode(repo_root)
    support_root = find_support_root()
    support_skill = support_root / "SKILL.md"
    runtime_contract = support_root / "references" / "runtime-contract.md"
    wrapper = support_root / "scripts" / "export-thread.sh"

    if mode == "none":
        return {
            "provider": SUPPORT_ID,
            "provider_mode": mode,
            "doctor_status": "skipped",
            "support_skill_path": portable(support_skill, repo_root),
            "runtime_contract_path": portable(runtime_contract, repo_root),
            "wrapper_path": portable(wrapper, repo_root),
            "operator_prompt": (
                "Adapter declares gather_provider.slack.mode=none. Stop with a "
                "missing-capability explanation instead of trying browser or unrelated helpers."
            ),
            "next_steps": [
                "Surface the missing Slack capability to the operator.",
                "If the operator has Slack access, update gather_provider.slack.mode in .agents/gather-adapter.yaml.",
            ],
        }

    if mode == "host-mediated":
        return {
            "provider": SUPPORT_ID,
            "provider_mode": mode,
            "doctor_status": "skipped",
            "support_skill_path": portable(support_skill, repo_root),
            "runtime_contract_path": portable(runtime_contract, repo_root),
            "wrapper_path": portable(wrapper, repo_root),
            "operator_prompt": (
                "Adapter declares gather_provider.slack.mode=host-mediated. Use the host's "
                "Slack capability command instead of invoking the direct gather-slack wrapper."
            ),
            "next_steps": [
                "Follow the host's documented Slack capability command shape.",
                "Do not substitute direct token or wrapper access under a host-mediated adapter mode.",
            ],
        }

    status, dependency_steps = dependency_status()
    return {
        "provider": SUPPORT_ID,
        "provider_mode": mode,
        "doctor_status": status,
        "support_skill_path": portable(support_skill, repo_root),
        "runtime_contract_path": portable(runtime_contract, repo_root),
        "wrapper_path": portable(wrapper, repo_root),
        "operator_prompt": (
            "Use the checked-in `gather-slack` wrapper for Slack thread gather before "
            "browser-mediated private-source fallbacks."
        ),
        "next_steps": [
            f"Read `{portable(support_skill, repo_root)}` and `{portable(runtime_contract, repo_root)}`.",
            "Let the wrapper resolve Slack access through a host grant, `charness capability env slack.default`, or ordinary operator-local `SLACK_BOT_TOKEN`.",
            f"Run `{portable(wrapper, repo_root)} <slack-url> <output.md> <title>` for the durable gather asset.",
            *dependency_steps,
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose Slack gather path advice should be computed")
    args = parser.parse_args()
    print(json.dumps(payload_for(args.repo_root.resolve()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
