#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
emit_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.yaml_output"
).emit_yaml
run_process = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.subprocess_guard"
).run_process


def has_match(pattern: str, repo_root: Path) -> bool:
    result = run_process(
        ["rg", "-n", pattern, "README.md", "docs", "scripts", "skills", "profiles"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    return result.returncode == 0


def infer_tags(repo_root: Path) -> list[dict[str, str]]:
    tags: list[dict[str, str]] = []
    if has_match(r"user|usage|cli|command", repo_root):
        tags.append({"tag": "user", "reason": "docs or commands describe a human-usable surface."})
    if has_match(r"setup|deploy|operator|maintenance|doctor", repo_root):
        tags.append(
            {
                "tag": "operator",
                "reason": "the repo exposes setup, maintenance, or operator-facing flows.",
            }
        )
    if has_match(r"test|ruff|pytest|scripts/run-quality|development", repo_root):
        tags.append(
            {
                "tag": "developer",
                "reason": "the repo exposes direct source and validation workflows.",
            }
        )
    return tags


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root to scan for user, operator, and developer audience signals",
    )
    args = parser.parse_args()
    emit_yaml({"candidates": infer_tags(args.repo_root.resolve())})


if __name__ == "__main__":
    main()
