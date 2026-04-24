#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
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
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter.load_adapter


def _contains_any(text: str, patterns: list[str]) -> list[str]:
    lowered = text.lower()
    return [pattern for pattern in patterns if pattern.lower() in lowered]


def _run_review_commands(repo_root: Path, commands: list[str]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for command in commands:
        result = subprocess.run(
            command,
            cwd=repo_root,
            shell=True,
            executable="/bin/bash",
            check=False,
            capture_output=True,
            text=True,
        )
        results.append(
            {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "ok": result.returncode == 0,
            }
        )
    return results


def build_payload(repo_root: Path, *, artifact_path: Path | None = None, run_commands: bool = True) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    data = adapter["data"]
    resolved_artifact = artifact_path or (repo_root / adapter["artifact_path"])
    patterns = list(data.get("review_unavailable_patterns", []))
    waiver_phrases = list(data.get("review_waiver_phrases", []))
    commands = list(data.get("requested_review_commands", []))
    artifact_text = resolved_artifact.read_text(encoding="utf-8", errors="replace") if resolved_artifact.is_file() else ""
    unavailable_hits = _contains_any(artifact_text, patterns) if artifact_text else []
    waiver_hits = _contains_any(artifact_text, waiver_phrases) if artifact_text else []
    command_results = _run_review_commands(repo_root, commands) if run_commands else []
    failed_commands = [item for item in command_results if item.get("ok") is not True]
    blockers: list[str] = []
    if unavailable_hits and not waiver_hits:
        blockers.append(
            "release artifact records requested review unavailability without an explicit review waiver: "
            + ", ".join(unavailable_hits)
        )
    for item in failed_commands:
        blockers.append(f"requested review command failed ({item['exit_code']}): {item['command']}")
    status = "blocked" if blockers else "ok"
    if unavailable_hits and waiver_hits and not failed_commands:
        status = "waived"
    return {
        "status": status,
        "artifact_path": str(resolved_artifact.relative_to(repo_root)) if resolved_artifact.is_relative_to(repo_root) else str(resolved_artifact),
        "artifact_exists": resolved_artifact.is_file(),
        "unavailable_hits": unavailable_hits,
        "waiver_hits": waiver_hits,
        "requested_review_commands": commands,
        "command_results": command_results,
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--skip-commands", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    artifact_path = args.artifact.resolve() if args.artifact else None
    payload = build_payload(repo_root, artifact_path=artifact_path, run_commands=not args.skip_commands)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif payload["status"] == "blocked":
        for blocker in payload["blockers"]:
            print(f"BLOCKED: {blocker}")
    else:
        print(f"requested release review gate: {payload['status']}")
    return 1 if payload["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
