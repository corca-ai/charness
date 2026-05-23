#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


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







_scripts_control_plane_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.control_plane_lib")
load_manifest = _scripts_control_plane_lib_module.load_manifest

_resolve_adapter_module = importlib.util.spec_from_file_location(
    "gather_resolve_adapter",
    Path(__file__).resolve().parent / "resolve_adapter.py",
)
_gather_adapter = importlib.util.module_from_spec(_resolve_adapter_module)
_resolve_adapter_module.loader.exec_module(_gather_adapter)
load_gather_adapter = _gather_adapter.load_adapter

TOOL_ID = "gws-cli"
SOURCE_ID = "google_workspace"


def resolve_provider_mode(repo_root: Path) -> str:
    adapter = load_gather_adapter(repo_root)
    provider = adapter["data"].get("gather_provider") or {}
    entry = provider.get(SOURCE_ID) or {}
    return entry.get("mode", "direct-cli")


def run_doctor(repo_root: Path) -> dict[str, object]:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/doctor.py",
            "--repo-root",
            str(repo_root),
            "--tool-id",
            TOOL_ID,
            "--json",
            "--skip-release-probe",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode not in {0, 1}:
        raise RuntimeError(f"doctor failed for gws-cli: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    if not payload:
        raise ValueError("doctor returned no payload for gws-cli")
    return payload[0]


def build_next_steps(doctor: dict[str, object], manifest: dict[str, object]) -> list[str]:
    doctor_status = doctor["doctor_status"]
    if doctor_status == "ok":
        return [
            "Use the authenticated `gws` CLI path for private Google Workspace gather.",
            "Keep gathered artifacts free of credentials or copied auth material.",
        ]

    if doctor_status == "missing":
        return [*manifest["lifecycle"]["install"]["notes"], doctor["detect"]["failure_hint"]]

    if doctor_status == "not-ready":
        failed_checks = doctor["readiness"]["checks"]
        hints = [check["failure_hint"] for check in failed_checks if not check["ok"] and check.get("failure_hint")]
        return hints or [
            "Complete the documented `gws auth` setup step before relying on Google Workspace gather."
        ]

    if doctor_status == "unhealthy":
        return [doctor["healthcheck"]["failure_hint"]]

    if doctor_status == "version-mismatch":
        return [*manifest["degradation"]["when_version_mismatch"]]

    return ["Google Workspace gather cannot proceed until the `gws-cli` contract is satisfied."]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repository root path")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    mode = resolve_provider_mode(repo_root)
    manifest = load_manifest(REPO_ROOT / "integrations" / "tools" / f"{TOOL_ID}.json")
    if mode == "none":
        payload = {
            "provider": TOOL_ID,
            "provider_mode": mode,
            "doctor_status": "skipped",
            "summary": manifest["summary"],
            "operator_prompt": (
                "Adapter declares gather_provider.google_workspace.mode=none. "
                "Stop with a missing-capability explanation instead of invoking gws."
            ),
            "next_steps": [
                "Surface the missing google_workspace capability to the operator.",
                "If the operator has a Google Workspace path, update gather_provider.google_workspace.mode in .agents/gather-adapter.yaml.",
            ],
        }
    elif mode == "host-mediated":
        payload = {
            "provider": TOOL_ID,
            "provider_mode": mode,
            "doctor_status": "skipped",
            "summary": manifest["summary"],
            "operator_prompt": (
                "Adapter declares gather_provider.google_workspace.mode=host-mediated. "
                "Use the host's google_workspace capability command instead of invoking gws directly."
            ),
            "next_steps": [
                "Follow the host's documented google_workspace capability command shape.",
                "Do not substitute direct `gws` invocations under a host-mediated adapter mode.",
            ],
        }
    else:
        doctor = run_doctor(REPO_ROOT)
        next_steps = build_next_steps(doctor, manifest)
        payload = {
            "provider": TOOL_ID,
            "provider_mode": mode,
            "doctor_status": doctor["doctor_status"],
            "summary": manifest["summary"],
            "operator_prompt": next_steps[0],
            "next_steps": next_steps,
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
