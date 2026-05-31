#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GateCommand:
    label: str
    argv: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {"label": self.label, "argv": list(self.argv)}


def collect_staged_paths(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to list staged paths")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _matches(path: str, prefix: str | None = None, suffix: str | None = None) -> bool:
    return (prefix is None or path.startswith(prefix)) and (suffix is None or path.endswith(suffix))


def _any_starts(paths: list[str], prefix: str) -> bool:
    return any(path.startswith(prefix) for path in paths)


def staged_commit_gate_plan(
    repo_root: Path,
    staged_paths: list[str] | None = None,
    *,
    ruff_path: str | None = None,
) -> list[GateCommand]:
    paths = staged_paths if staged_paths is not None else collect_staged_paths(repo_root)
    staged_py = [path for path in paths if path.endswith(".py")]
    ruff = shutil.which("ruff") if ruff_path is None else ruff_path
    plan: list[GateCommand] = []

    if staged_py:
        plan.append(GateCommand("py_compile (staged)", ("python3", "-m", "py_compile", *staged_py)))
        if ruff:
            plan.append(GateCommand("ruff (staged)", ("ruff", "check", *staged_py)))
        plan.append(
            GateCommand(
                "check-python-lengths (staged)",
                (
                    "python3",
                    "scripts/check_python_lengths.py",
                    "--repo-root",
                    str(repo_root),
                    "--paths",
                    *staged_py,
                ),
            )
        )

    if any(path.endswith(".py") and (path.startswith("scripts/") or path.startswith("skills/")) for path in paths):
        plan.append(
            GateCommand(
                "validate-attention-state-visibility",
                (
                    "python3",
                    "scripts/validate_attention_state_visibility.py",
                    "--repo-root",
                    str(repo_root),
                    "--scan-root",
                    "scripts",
                    "--scan-root",
                    "skills",
                    "--scan-root-map",
                    "../charness-support=skills/support",
                ),
            )
        )

    if _any_starts(paths, "skills/"):
        plan.append(GateCommand("validate-skills", ("python3", "scripts/validate_skills.py", "--repo-root", str(repo_root))))
        plan.append(GateCommand("run-evals", ("python3", "scripts/run_evals.py", "--repo-root", str(repo_root))))
    if _any_starts(paths, "profiles/"):
        plan.append(GateCommand("validate-profiles", ("python3", "scripts/validate_profiles.py", "--repo-root", str(repo_root))))
    if _any_starts(paths, ".agents/"):
        plan.append(GateCommand("validate-adapters", ("python3", "scripts/validate_adapters.py", "--repo-root", str(repo_root))))
    if _any_starts(paths, "presets/"):
        plan.append(GateCommand("validate-presets", ("python3", "scripts/validate_presets.py", "--repo-root", str(repo_root))))
    if _any_starts(paths, "integrations/"):
        plan.append(GateCommand("validate-integrations", ("python3", "scripts/validate_integrations.py", "--repo-root", str(repo_root))))

    mirror_prefixes = (
        "scripts/",
        "skills/",
        "profiles/",
        "presets/",
        "integrations/",
        "plugins/",
        ".claude-plugin/",
        ".codex-plugin/",
        ".agents/plugins/",
    )
    if any(
        path.startswith(mirror_prefixes)
        or path == "README.md"
        or path in {"runtime_bootstrap.py", "skill_runtime_bootstrap.py"}
        for path in paths
    ):
        plan.append(
            GateCommand(
                "staged-plugin-mirror-drift",
                ("python3", "scripts/check_staged_mirror_drift.py", "--repo-root", str(repo_root)),
            )
        )

    if any(path.endswith(".md") for path in paths):
        plan.append(GateCommand("check-doc-links", ("python3", "scripts/check_doc_links.py", "--repo-root", str(repo_root))))
        plan.append(GateCommand("check-markdown", ("./scripts/check-markdown.sh",)))

    return plan


def run_predict_commit(
    repo_root: Path,
    *,
    paths: list[str] | None,
    as_json: bool,
    plan_only: bool,
    run_command,
    emit_payload,
) -> int:
    selected_paths = paths if paths is not None else collect_staged_paths(repo_root)
    command_plan = staged_commit_gate_plan(repo_root, selected_paths)
    payload: dict[str, object] = {
        "status": "planned" if plan_only else "completed",
        "changed_paths": selected_paths,
        "planned_commands": [
            {"phase": "pre-commit", "label": command.label, "argv": list(command.argv)}
            for command in command_plan
        ],
        "executed_commands": [],
    }
    if plan_only:
        if as_json:
            return emit_payload(payload, as_json=as_json)
        for command in command_plan:
            print(f"charness pre-commit: {command.label}")
        return 0
    if not command_plan and not as_json:
        return 0
    for command in command_plan:
        if not as_json:
            print(f"charness pre-commit: {command.label}")
        result = run_command(repo_root, shlex.join(command.argv), "pre-commit")
        payload["executed_commands"].append(result)
        if result["returncode"] != 0:
            payload["status"] = "failed"
            if as_json:
                return emit_payload(payload, as_json=as_json)
            if result["stdout"]:
                print(result["stdout"], end="" if result["stdout"].endswith("\n") else "\n")
            if result["stderr"]:
                print(result["stderr"], end="" if result["stderr"].endswith("\n") else "\n", file=sys.stderr)
            return 1
    if not as_json:
        print("charness pre-commit: ok")
        return 0
    return emit_payload(payload, as_json=as_json)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--paths", nargs="*")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-ruff", action="store_true", help="Plan as if ruff is unavailable.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    paths = args.paths if args.paths is not None else None
    ruff_path = "" if args.no_ruff else None
    plan = staged_commit_gate_plan(repo_root, paths, ruff_path=ruff_path)
    if args.json:
        print(json.dumps([command.as_dict() for command in plan], indent=2))
    else:
        for command in plan:
            print(command.label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
