#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)







_resolve_adapter_module = importlib.util.spec_from_file_location(
    "gather_resolve_adapter",
    Path(__file__).resolve().parent / "resolve_adapter.py",
)
_gather_adapter = importlib.util.module_from_spec(_resolve_adapter_module)
_resolve_adapter_module.loader.exec_module(_gather_adapter)
load_gather_adapter = _gather_adapter.load_adapter

PROVIDER_ID = "google-workspace"
SOURCE_ID = "google_workspace"


def resolve_provider_mode(repo_root: Path) -> str:
    adapter = load_gather_adapter(repo_root)
    provider = adapter["data"].get("gather_provider") or {}
    entry = provider.get(SOURCE_ID) or {}
    return entry.get("mode", "direct-cli")


def payload_for(repo_root: Path) -> dict[str, object]:
    mode = resolve_provider_mode(repo_root)
    if mode == "none":
        return {
            "provider": PROVIDER_ID,
            "provider_mode": mode,
            "doctor_status": "skipped",
            "summary": "Google Workspace gather has no repo-owned direct CLI provider.",
            "operator_prompt": (
                "Adapter declares gather_provider.google_workspace.mode=none. "
                "Stop with a missing-capability explanation."
            ),
            "next_steps": [
                "Surface the missing google_workspace capability to the operator.",
                "If the operator has a Google Workspace path, update gather_provider.google_workspace.mode in .agents/gather-adapter.yaml.",
            ],
        }
    if mode == "host-mediated":
        return {
            "provider": PROVIDER_ID,
            "provider_mode": mode,
            "doctor_status": "skipped",
            "summary": "Google Workspace gather has no repo-owned direct CLI provider.",
            "operator_prompt": (
                "Adapter declares gather_provider.google_workspace.mode=host-mediated. "
                "Use the host's google_workspace capability command."
            ),
            "next_steps": [
                "Follow the host's documented google_workspace capability command shape.",
                "Do not substitute direct Google Workspace CLI invocations under a host-mediated adapter mode.",
            ],
        }
    return {
        "provider": PROVIDER_ID,
        "provider_mode": mode,
        "doctor_status": "missing",
        "summary": "Google Workspace gather has no repo-owned direct CLI provider.",
        "operator_prompt": (
            "No repo-supported direct Google Workspace CLI provider is configured. "
            "Use host-mediated access, an operator-provided export, or browser-mediated fallback when appropriate."
        ),
        "next_steps": [
            "For private Google Workspace content, prefer a host-mediated google_workspace capability when one exists.",
            "If the operator can export the source, gather the exported artifact instead of invoking an untracked local CLI.",
            "If only an authenticated browser session is available, use the browser-mediated private-source ladder.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose Google Workspace gather path advice should be computed")
    args = parser.parse_args()

    print(json.dumps(payload_for(args.repo_root.resolve()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
