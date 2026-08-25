#!/usr/bin/env python3

from __future__ import annotations

import argparse
import runpy
import shlex
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_command_docs = import_repo_module(__file__, "scripts.check_command_docs")


def commands_from_contract(repo_root: Path) -> tuple[tuple[str, tuple[str, ...]], ...]:
    contract = _command_docs.load_contract(repo_root / ".agents" / "command-docs.yaml")
    commands_by_path: dict[tuple[str, ...], tuple[str, ...]] = {}
    for command_id, config in contract.items():
        argv = tuple(shlex.split(str(config["help_command"])))
        if len(argv) < 2 or argv[0] != "./charness" or argv[-1] != "--help":
            raise SystemExit(f"unsupported CLI reference help command: {' '.join(argv)}")
        path = argv[1:-1]
        if path in commands_by_path:
            raise SystemExit(
                f"duplicate command-docs help path for `{command_id}`: {' '.join(argv)}"
            )
        commands_by_path[path] = argv

    def ordered_paths(
        parser: argparse.ArgumentParser,
        prefix: tuple[str, ...] = (),
    ) -> list[tuple[str, ...]]:
        paths: list[tuple[str, ...]] = []
        for action in parser._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            for name, child in action.choices.items():
                current = (*prefix, name)
                paths.append(current)
                paths.extend(ordered_paths(child, current))
        return paths

    cli_namespace = runpy.run_path(str(repo_root / "charness"))
    parser_paths = [(), *ordered_paths(cli_namespace["build_parser"]())]
    if set(parser_paths) != set(commands_by_path):
        missing = sorted(set(parser_paths) - set(commands_by_path))
        extra = sorted(set(commands_by_path) - set(parser_paths))
        raise SystemExit(f"command-docs/parser mismatch: missing={missing}, extra={extra}")
    return tuple((" ".join(("charness", *path)), commands_by_path[path]) for path in parser_paths)


EXAMPLES: dict[str, tuple[str, ...]] = {
    "charness tool install": (
        "charness tool install --recommendation-role validation --next-skill-id quality",
    ),
}


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
    commands = commands_from_contract(repo_root)
    with ThreadPoolExecutor(max_workers=len(commands)) as executor:
        help_futures = {
            title: executor.submit(run_help, repo_root, command) for title, command in commands
        }
        help_outputs = {title: future.result() for title, future in help_futures.items()}
    sections = [
        "<!-- GENERATED: do not edit. Regenerate via `python3 scripts/render_cli_reference.py --repo-root .` -->",
        "",
        "# CLI Reference",
        "",
        "> Status: generated",
        "> Source of truth: `charness` parser and command-doc contract",
        "",
        "This file is generated from `./charness --help` and subcommand help output in the current checkout.",
        "Operational command payloads, including structured command failures, are emitted as a single YAML document on stdout; progress and unstructured fatal errors use stderr. Default operational responses are compact summaries: aggregate tool operations report counts and attention tool ids, not every tool record. This replaces the former aggregate `results` payload: automation that consumes individual tool records must request `--detail`. Commands with aggregated host or tool diagnostics expose the full evidence only through `--detail`, which still emits one YAML document.",
        "Payloads that can name a follow-up carry it as an in-band affordance instead of relying on out-of-band knowledge: `next_step` is a single human-readable follow-up string on command payloads (task, tool, and worktree surfaces; on `charness task` it appears on success and on structured `rejected` failures alike), `next_steps` is a list of human-readable follow-up strings (tool doctor, `capability init`, gather advise), `host_next_steps` maps host ids to per-host status messages on runtime doctor/update output, and `next_action` is a structured object (`kind` plus context) on runtime doctor payloads and skill plan envelopes. Human-readable summaries print the affordance line with the `NEXT:` prefix. `charness task` also persists `next_step` into `.charness/tasks/<task-id>.json`, so the state file carries the same continuation affordance as the original response.",
        "Regenerate it with `python3 scripts/render_cli_reference.py --repo-root . --output docs/cli-reference.md`.",
        "",
    ]
    for title, command in commands:
        sections.extend(
            [
                f"## `{title}`",
                "",
                "```text",
                help_outputs[title],
                "```",
                "",
            ]
        )
        examples = EXAMPLES.get(title, ())
        if examples:
            sections.extend(["Examples", "", "```bash", *examples, "```", ""])
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
