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


def payload_for(repo_root: Path) -> dict[str, object]:
    data = load_gather_adapter(repo_root)["data"]
    entry = (data.get("gather_provider") or {}).get(SOURCE_ID) or {}
    mode = str(entry.get("mode") or "direct-cli")
    if mode == "none":
        return _skipped_payload(
            mode,
            operator_prompt=(
                "Adapter declares gather_provider.google_workspace.mode=none. "
                "Stop with a missing-capability explanation."
            ),
            next_steps=[
                "Surface the missing google_workspace capability to the operator.",
                "If the operator has a Google Workspace path, update gather_provider.google_workspace.mode in .agents/gather-adapter.yaml.",
            ],
        )
    if mode == "host-mediated":
        return _skipped_payload(
            mode,
            operator_prompt=(
                "Adapter declares gather_provider.google_workspace.mode=host-mediated. "
                "Use the host's google_workspace capability command."
            ),
            next_steps=[
                "Follow the host's documented google_workspace capability command shape.",
                "Do not substitute direct Google Workspace CLI invocations under a host-mediated adapter mode.",
            ],
        )
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


def _skipped_payload(mode: str, *, operator_prompt: str, next_steps: list[str]) -> dict[str, object]:
    return {
        "provider": PROVIDER_ID,
        "provider_mode": mode,
        "doctor_status": "skipped",
        "summary": "Google Workspace gather has no repo-owned direct CLI provider.",
        "operator_prompt": operator_prompt,
        "next_steps": next_steps,
    }


def _selected_repo_root() -> Path:
    parser = argparse.ArgumentParser(prog="advise-google-workspace-path")
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root whose Google Workspace gather path advice should be computed",
    )
    return parser.parse_args().repo_root.resolve()


def main() -> None:
    payload = payload_for(_selected_repo_root())
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    print(rendered)


if __name__ == "__main__":
    main()
