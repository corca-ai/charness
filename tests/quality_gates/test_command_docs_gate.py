from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import runpy
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.script_loader import load_script_module

from .support import ROOT, run_script, write_executable


def _load_render_cli_reference():
    spec = importlib.util.spec_from_file_location(
        "render_cli_reference", ROOT / "scripts" / "gates_support" / "render_cli_reference.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parser_command_paths(
    parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()
) -> set[tuple[str, ...]]:
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


def _json_declarations(root: Path) -> list[str]:
    declarations: list[str] = []
    for path in [root / "charness", *sorted((root / "scripts").rglob("*.py"))]:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            if not (isinstance(function, ast.Attribute) and function.attr == "add_argument"):
                continue
            if any(isinstance(arg, ast.Constant) and arg.value == "--json" for arg in node.args):
                declarations.append(f"{path.relative_to(root)}:{node.lineno}")
    return declarations


def _command_doc_paths() -> set[tuple[str, ...]]:
    contract = yaml.safe_load((ROOT / ".agents" / "command-docs.yaml").read_text(encoding="utf-8"))
    return {
        tuple(shlex.split(entry["help_command"])[1:-1]) for entry in contract["commands"].values()
    }


def _command_registry_paths() -> set[tuple[str, ...]]:
    registry = json.loads((ROOT / ".agents" / "command-registry.json").read_text(encoding="utf-8"))
    return {tuple(entry["path"]) for entry in registry["commands"]}


def _side_effect_probe_commands() -> set[str]:
    contract = json.loads(
        (ROOT / ".agents" / "cli-side-effect-probes.json").read_text(encoding="utf-8")
    )
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
    # "Validated command docs for N command surface(s)" was the renderer's line;
    # `status` plus the command list is what carries the same claim AND its
    # population, so a pass over zero surfaces is not readable as a pass over all.
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "pass"
    assert payload["findings"] == []
    assert payload["commands"]


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
    # A skip has to say it skipped and WHY: an empty findings list alone reads as
    # a clean pass over a repo the gate never inspected.
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "skipped"
    assert payload["reason"] == "missing-contract"


def test_render_cli_reference_matches_checked_in_doc(tmp_path: Path) -> None:
    output = tmp_path / "cli-reference.md"

    result = run_script(
        "scripts/gates_support/render_cli_reference.py",
        "--repo-root",
        str(ROOT),
        "--output",
        str(output),
    )

    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == (ROOT / "docs" / "cli-reference.md").read_text(
        encoding="utf-8"
    )


def test_root_cli_command_contracts_cover_every_parser_path() -> None:
    expected = _root_cli_command_paths()
    rendered = {
        tuple(title.split()[1:])
        for title, _command in _load_render_cli_reference().commands_from_contract(ROOT)
    }

    assert _command_doc_paths() == {(), *expected}
    assert _command_registry_paths() == expected
    assert rendered == {(), *expected}


def test_render_cli_reference_rejects_duplicate_help_paths(monkeypatch) -> None:
    renderer = _load_render_cli_reference()
    contract = renderer._command_docs.load_contract(ROOT / ".agents" / "command-docs.yaml")
    contract["duplicate-root"] = dict(contract["root"])
    monkeypatch.setattr(renderer._command_docs, "load_contract", lambda _path: contract)

    with pytest.raises(SystemExit, match="duplicate command-docs help path"):
        renderer.commands_from_contract(ROOT)


def test_render_cli_reference_rejects_unsupported_help_command(monkeypatch) -> None:
    renderer = _load_render_cli_reference()
    contract = renderer._command_docs.load_contract(ROOT / ".agents" / "command-docs.yaml")
    contract["root"]["help_command"] = "charness --help"
    monkeypatch.setattr(renderer._command_docs, "load_contract", lambda _path: contract)

    with pytest.raises(SystemExit, match="unsupported CLI reference help command"):
        renderer.commands_from_contract(ROOT)


def test_render_cli_reference_rejects_parser_contract_path_mismatch(monkeypatch) -> None:
    renderer = _load_render_cli_reference()
    contract = renderer._command_docs.load_contract(ROOT / ".agents" / "command-docs.yaml")
    contract.pop("catalog-list")
    monkeypatch.setattr(renderer._command_docs, "load_contract", lambda _path: contract)

    with pytest.raises(SystemExit, match="command-docs/parser mismatch"):
        renderer.commands_from_contract(ROOT)


def test_render_cli_reference_orders_commands_from_parser_and_contract(monkeypatch) -> None:
    renderer = _load_render_cli_reference()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    beta = subparsers.add_parser("beta")
    beta.add_subparsers().add_parser("nested")
    subparsers.add_parser("alpha")
    contract = {
        "root": {"help_command": "./charness --help"},
        "alpha": {"help_command": "./charness alpha --help"},
        "beta": {"help_command": "./charness beta --help"},
        "nested": {"help_command": "./charness beta nested --help"},
    }

    monkeypatch.setattr(renderer._command_docs, "load_contract", lambda _path: contract)
    monkeypatch.setattr(renderer.runpy, "run_path", lambda _path: {"build_parser": lambda: parser})

    assert renderer.commands_from_contract(Path("/contract-repo")) == (
        ("charness", ("./charness", "--help")),
        ("charness beta", ("./charness", "beta", "--help")),
        ("charness beta nested", ("./charness", "beta", "nested", "--help")),
        ("charness alpha", ("./charness", "alpha", "--help")),
    )


def test_render_cli_reference_renders_contract_order_and_examples(monkeypatch) -> None:
    renderer = _load_render_cli_reference()
    commands = (
        ("charness tool install", ("./charness", "tool", "install", "--help")),
        ("charness alpha", ("./charness", "alpha", "--help")),
    )
    monkeypatch.setattr(renderer, "commands_from_contract", lambda _repo_root: commands)
    monkeypatch.setattr(
        renderer,
        "run_help",
        lambda _repo_root, command: f"help for {' '.join(command[1:-1])}",
    )

    rendered = renderer.render_cli_reference(Path("/contract-repo"))

    assert rendered.index("## `charness tool install`") < rendered.index("## `charness alpha`")
    assert "help for tool install" in rendered
    assert "help for alpha" in rendered
    assert (
        "charness tool install --recommendation-role validation --next-skill-id quality" in rendered
    )


@pytest.mark.boundary_contract(
    reason="exact exit-code and stderr contract of the root charness CLI for a removed flag"
)
def test_root_cli_has_no_json_compatibility_flag() -> None:
    """The root CLI carries no `--json`, read off the CLI itself.

    This used to be measured as "no file under `tests/charness_cli/` mentions the
    string `--json`". That proxy inverted at the 2026-08-14 total removal: the
    tests that PROVE `--json` is now an argparse error have to name the flag to
    pass it, so the old spelling would fail precisely on the evidence that the
    removal landed. The subject was never the tests -- it is the CLI's own parser
    surface, so that is what is read here: no declaration anywhere the CLI
    dispatches, and a real invocation refused rather than ignored.
    """
    declarations = _json_declarations(ROOT)
    assert declarations == [], f"the root CLI surface still declares --json: {declarations}"

    # Behavioral half: a caller still passing the old flag is told it is gone,
    # rather than handed a payload they will read as the format they requested.
    # `worktree audit` is read-only, so the probe cannot mutate this tree -- and
    # `--json` is rejected during parsing, before the command does any work.
    completed = subprocess.run(
        [sys.executable, str(ROOT / "charness"), "worktree", "audit", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "unrecognized arguments: --json" in completed.stderr


def test_json_declaration_scan_includes_nested_scripts(tmp_path: Path) -> None:
    nested = tmp_path / "scripts" / "package"
    nested.mkdir(parents=True)
    (tmp_path / "charness").write_text("", encoding="utf-8")
    (nested / "check_json.py").write_text(
        "import argparse\nparser = argparse.ArgumentParser()\nparser.add_argument('--json')\n",
        encoding="utf-8",
    )

    assert _json_declarations(tmp_path) == ["scripts/package/check_json.py:3"]


def test_root_cli_mutating_modes_have_side_effect_probe_contracts() -> None:
    assert _side_effect_probe_commands() == {
        "./charness init",
        "./charness update",
        "./charness doctor --write-state",
        "./charness version --check",
        "./charness version --verbose",
        "./charness reset",
        "./charness uninstall",
        "./charness catalog refresh",
        "./charness capability init",
        "./charness tool doctor",
        "./charness tool repair --execute",
        "./charness tool sync-support",
        "./charness tool install",
        "./charness tool update",
        "./charness worktree create",
        "./charness worktree add",
        "./charness worktree prepare",
        "./charness task run",
        "./charness worktree exec",
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


@pytest.mark.boundary_contract(
    reason="exact exit-code contract of the target's help-command runner"
)
def test_run_help_raises_systemexit_on_nonzero_exit(tmp_path: Path) -> None:
    # A failing help command (positive non-zero exit) must surface as SystemExit:
    # pins `check=False` (check=True would raise CalledProcessError instead) and
    # the `!= 0` comparison against the `< 0` mutant (2 < 0 is False -> no raise).
    mod = _load_render_cli_reference()
    with pytest.raises(SystemExit):
        mod.run_help(tmp_path, ("bash", "-c", "echo out; echo err >&2; exit 2"))


@pytest.mark.boundary_contract(reason="exact signal behavior of the target's help-command runner")
def test_run_help_raises_systemexit_on_signal_death(tmp_path: Path) -> None:
    # A signal-killed help command yields a NEGATIVE returncode: `!= 0` is True
    # (raise) while the `> 0` mutant would be False (no raise). This is the case a
    # positive exit code cannot distinguish, so it pins the remaining comparison.
    mod = _load_render_cli_reference()
    with pytest.raises(SystemExit):
        mod.run_help(tmp_path, ("bash", "-c", "kill -9 $$"))


# --- the flag gate in a tree that does not own the CLI -----------------------
#
# `check_documented_command_flags.build_report` always builds a repo path index from
# this tree's own git listing, so the arm a CONSUMING repo takes -- no index, decide
# from the filesystem -- is only reachable through the collector itself.
FLAG_GATE = load_script_module(
    "tests.quality_gates.command_docs_flag_gate",
    ROOT / "scripts" / "check_documented_command_flags.py",
)


def _consumer_doc(tmp_path: Path, text: str) -> tuple[Path, Path]:
    root = tmp_path / "consumer"
    doc = root / "docs" / "guide.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(text, encoding="utf-8")
    return root, doc


def test_a_documented_cli_command_is_skipped_when_the_tree_has_no_cli(tmp_path: Path) -> None:
    """A consuming repo documents `charness ...` but does not ship the executable.

    The gate proves a flag claim by running the command's own `--help`, so with no CLI
    at the root there is nothing to run. Reporting drift would fail a doc that is
    correct about the INSTALLED command; accepting it silently is worse -- a pass
    claiming to have scanned a command this tree cannot execute. The counted skip is
    what keeps the pass from over-claiming its own coverage.
    """
    root, doc = _consumer_doc(tmp_path, "Run `charness quality run --json` in your repo.\n")

    found, skipped = FLAG_GATE.iter_documented_invocations(root, doc)

    assert found == []
    assert skipped == ["cli-not-in-this-tree"]


def test_a_documented_cli_command_is_scanned_when_the_tree_ships_the_cli(tmp_path: Path) -> None:
    """The same doc in a tree that owns the executable IS this gate's to prove.

    Identical call, identical carrier: the two tests differ only in whether the
    repo-root CLI exists, which is the whole question the index-free arm answers.
    """
    root, doc = _consumer_doc(tmp_path, "Run `charness quality run --json` in your repo.\n")
    (root / FLAG_GATE.CLI_NAME).write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    found, skipped = FLAG_GATE.iter_documented_invocations(root, doc)

    assert skipped == []
    assert [(script, flags) for _lineno, script, _tokens, flags in found] == [
        (FLAG_GATE.CLI_NAME, ("--json",))
    ]
