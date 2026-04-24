#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

COMMANDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("charness", ("./charness", "--help")),
    ("charness init", ("./charness", "init", "--help")),
    ("charness update", ("./charness", "update", "--help")),
    ("charness doctor", ("./charness", "doctor", "--help")),
    ("charness version", ("./charness", "version", "--help")),
    ("charness uninstall", ("./charness", "uninstall", "--help")),
    ("charness reset", ("./charness", "reset", "--help")),
    ("charness task", ("./charness", "task", "--help")),
    ("charness capability", ("./charness", "capability", "--help")),
    ("charness tool", ("./charness", "tool", "--help")),
)


def run_help(repo_root: Path, command: tuple[str, ...]) -> str:
    result = subprocess.run(
        list(command),
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"help command failed: {' '.join(command)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return (result.stdout + result.stderr).rstrip()


def render_cli_reference(repo_root: Path) -> str:
    sections = [
        "# CLI Reference",
        "",
        "This file is generated from `./charness --help` and subcommand help output in the current checkout.",
        "Regenerate it with `python3 scripts/render_cli_reference.py --repo-root . --output docs/cli-reference.md`.",
        "",
    ]
    for title, command in COMMANDS:
        sections.extend(
            [
                f"## `{title}`",
                "",
                "```text",
                run_help(repo_root, command),
                "```",
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output", type=Path, default=Path("docs/cli-reference.md"))
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output = args.output if args.output.is_absolute() else repo_root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_cli_reference(repo_root) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
