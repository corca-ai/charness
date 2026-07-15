from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import runpy
import shlex
import sys
from pathlib import Path

import pytest
import yaml

from .support import ROOT, run_script, write_executable


def _load_render_cli_reference():
    spec = importlib.util.spec_from_file_location(
        "render_cli_reference", ROOT / "scripts" / "render_cli_reference.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parser_command_paths(parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()) -> set[tuple[str, ...]]:
    paths: set[tuple[str, ...]] = set()
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        for name, child in action.choices.items():
            current = (*prefix, name)
            paths.add(current)
            paths.update(_parser_command_paths(child, current))
    return paths


def _root_cli_command_paths() -> set[tuple[str, ...]]:
    return _parser_command_paths(runpy.run_path(str(ROOT / "charness"))["build_parser"]())


def _command_doc_paths() -> set[tuple[str, ...]]:
    contract = yaml.safe_load((ROOT / ".agents" / "command-docs.yaml").read_text(encoding="utf-8"))
    return {
        tuple(shlex.split(entry["help_command"])[1:-1])
        for entry in contract["commands"].values()
    }


def _command_registry_paths() -> set[tuple[str, ...]]:
    registry = json.loads((ROOT / ".agents" / "command-registry.json").read_text(encoding="utf-8"))
    return {tuple(entry["path"]) for entry in registry["commands"]}


def _side_effect_probe_commands() -> set[str]:
    contract = json.loads((ROOT / ".agents" / "cli-side-effect-probes.json").read_text(encoding="utf-8"))
    return {entry["command"] for entry in contract["commands"]}


def seed_command_docs_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / "scripts").mkdir()
    write_executable(
        repo / "demo",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "${1:-}" == "--help" ]]; then',
                '  echo "usage: demo [--json]"',
                "  exit 0",
                "fi",
                "exit 2",
                "",
            ]
        ),
    )
    (repo / "docs" / "demo.md").write_text(
        "Run `demo --json` when machine-readable output is needed.\n",
        encoding="utf-8",
    )
    (repo / ".agents" / "command-docs.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "commands:",
                "  demo:",
                "    help_command: ./demo --help",
                "    doc_paths:",
                "      - docs/demo.md",
                "    required_help_contains:",
                "      - --json",
                "    required_doc_contains:",
                "      - demo --json",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return repo


def test_check_command_docs_passes_current_repo_contract() -> None:
    result = run_script("scripts/check_command_docs.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert "Validated command docs" in result.stdout


def test_check_command_docs_reports_missing_required_doc_phrase(tmp_path: Path) -> None:
    repo = seed_command_docs_repo(tmp_path)
    (repo / "docs" / "demo.md").write_text("Run `demo` for text output.\n", encoding="utf-8")

    result = run_script("scripts/check_command_docs.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "docs/demo.md missing `demo --json`" in result.stderr


def test_check_command_docs_skips_repos_without_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script("scripts/check_command_docs.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "No command-docs contract found" in result.stdout


def test_render_cli_reference_matches_checked_in_doc(tmp_path: Path) -> None:
    output = tmp_path / "cli-reference.md"

    result = run_script(
        "scripts/render_cli_reference.py",
        "--repo-root",
        str(ROOT),
        "--output",
        str(output),
    )

    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == (ROOT / "docs" / "generated" / "cli-reference.md").read_text(encoding="utf-8")


def test_root_cli_command_contracts_cover_every_parser_path() -> None:
    expected = _root_cli_command_paths()
    rendered = {
        tuple(title.split()[1:])
        for title, _command in _load_render_cli_reference().COMMANDS
    }

    assert _command_doc_paths() == {(), *expected}
    assert _command_registry_paths() == expected
    assert rendered == {(), *expected}


def test_root_cli_legacy_json_flag_appears_only_in_compatibility_tests() -> None:
    cli_test_dir = ROOT / "tests" / "charness_cli"
    files_with_legacy_flag = {
        path.name
        for path in cli_test_dir.glob("test_*.py")
        if any(
            isinstance(node, ast.Constant) and node.value == "--json"
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        )
    }

    assert files_with_legacy_flag == {
        "test_task_envelope.py",
        "test_version_surface.py",
    }


def test_root_cli_mutating_modes_have_side_effect_probe_contracts() -> None:
    assert _side_effect_probe_commands() == {
        "./charness init",
        "./charness update",
        "./charness doctor --write-state",
        "./charness version --check",
        "./charness version --verbose",
        "./charness reset",
        "./charness uninstall",
        "./charness task claim",
        "./charness task submit",
        "./charness task abort",
        "./charness catalog refresh",
        "./charness capability init",
        "./charness tool doctor",
        "./charness tool repair --execute",
        "./charness tool sync-support",
        "./charness tool install",
        "./charness tool update",
        "./charness session-capture install",
        "./charness session-capture uninstall",
        "./charness worktree create",
        "./charness worktree add",
        "./charness worktree prepare",
        "./charness worktree audit --prune",
        "./charness worktree cleanup --yes",
    }


# --- #260 score-path survivors in render_cli_reference -----------------------
#
# The checked-in-doc test above always passes an ABSOLUTE --output, so main()'s
# line-102 else-branch (`repo_root / args.output`) and its Path-division mutants
# never execute, and run_help's failure path never runs. The in-process tests
# below pin those exact mutated behaviors.


def test_render_cli_reference_resolves_relative_output_under_repo_root(
    tmp_path: Path, monkeypatch
) -> None:
    # Relative --output resolves as `repo_root / args.output` (line 102 else
    # branch): any non-`/` operator on two Paths raises TypeError, killing the
    # whole Div_* cluster. The nested, not-yet-existing parent also pins
    # mkdir(parents=True) (parents=False would FileNotFoundError here). The heavy
    # render is stubbed so no real ./charness subprocess fan-out is needed.
    mod = _load_render_cli_reference()
    monkeypatch.setattr(mod, "render_cli_reference", lambda repo_root: "STUB")
    monkeypatch.setattr(
        sys,
        "argv",
        ["render_cli_reference.py", "--repo-root", str(tmp_path), "--output", "sub/dir/out.md"],
    )

    assert mod.main() == 0
    assert (tmp_path / "sub" / "dir" / "out.md").read_text(encoding="utf-8") == "STUB\n"


def test_run_help_raises_systemexit_on_nonzero_exit(tmp_path: Path) -> None:
    # A failing help command (positive non-zero exit) must surface as SystemExit:
    # pins `check=False` (check=True would raise CalledProcessError instead) and
    # the `!= 0` comparison against the `< 0` mutant (2 < 0 is False -> no raise).
    mod = _load_render_cli_reference()
    with pytest.raises(SystemExit):
        mod.run_help(tmp_path, ("bash", "-c", "echo out; echo err >&2; exit 2"))


def test_run_help_raises_systemexit_on_signal_death(tmp_path: Path) -> None:
    # A signal-killed help command yields a NEGATIVE returncode: `!= 0` is True
    # (raise) while the `> 0` mutant would be False (no raise). This is the case a
    # positive exit code cannot distinguish, so it pins the remaining comparison.
    mod = _load_render_cli_reference()
    with pytest.raises(SystemExit):
        mod.run_help(tmp_path, ("bash", "-c", "kill -9 $$"))
