from __future__ import annotations

import ast
import builtins
import importlib.util
import inspect
import re
import shlex
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts import gate_report_emit, yaml_output
from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

OWNED_COMMAND_DOCS = (
    "AGENTS.md",
    "skills/public/quality/references/ci-recoverable-gate-triage.md",
    "skills/public/quality/references/inventory-dispatch.md",
    "skills/public/release/references/index.md",
    "skills/public/create-cli/references/command-surface.md",
    "skills/public/create-cli/references/command-conventions.md",
    "skills/public/create-cli/references/machine-readable-state.md",
    "skills/public/create-cli/references/quality-gates.md",
    "skills/public/create-cli/references/intent-first-grammar.md",
)

ALWAYS_STRUCTURED_COMMANDS = (
    ("skills/public/debug/scripts/plan_debug_run.py", "--repo-root", "."),
    (
        "skills/public/retro/scripts/plan_retro_run.py",
        "--repo-root",
        ".",
    ),
)

DETAIL_COMMANDS = (
    ("skills/public/quality/scripts/plan_quality_run.py", "--repo-root", "."),
    ("skills/public/quality/scripts/render_runtime_summary.py", "--repo-root", "."),
    (
        "skills/public/quality/scripts/inventory_ci_recoverable_gates.py",
        "--repo-root",
        ".",
    ),
    ("skills/public/release/scripts/plan_release_run.py", "--repo-root", "."),
    ("scripts/plan_risk_interrupt.py", "--repo-root", "."),
    (
        "skills/public/quality/scripts/suggest_public_skill_dogfood.py",
        "--repo-root",
        ".",
        "--skill-id",
        "achieve",
    ),
)

SUMMARY_COMMANDS = (
    ("skills/public/quality/scripts/inventory_skill_ergonomics.py", "--repo-root", "."),
)
INVENTORY_DISPATCH = (
    ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
).read_text(encoding="utf-8")

# --- the 2026-08-14 total `--json` removal ------------------------------------------
#
# The three assertions above ("`--json` is not in `--help`", "`--json` is not in the
# docs") were the whole contract while `--json` still existed as a deprecated flag.
# They cannot see the two shapes the total removal is actually about: a flag kept
# alive under `argparse.SUPPRESS` (absent from help, still accepted), and a repo-owned
# command whose stdout quietly went back to JSON. What follows pins the removal at the
# source, at the argv boundary, and at the parse.

# Where repo-owned commands live. `mutants/` and `.claude/worktrees/` are scratch
# copies of this tree, not surfaces anyone runs.
# `plugins` is gone from this list: it is the GENERATED export, byte-identical to
# `scripts` + `skills`, and it was 717 of the 1,434 files this contract parsed --
# exactly half the corpus spent re-parsing copies of files already parsed. The
# export transform copies bytes; it cannot introduce a `json.dump` to stdout that
# the source does not already have.
_OWNED_SOURCE_ROOTS = ("scripts", "skills", "hooks")

# One command per migrated family, with the minimum argv each needs, so a failure
# names WHICH surface regressed rather than "something somewhere takes --json".
# `--json` is rejected during parsing, before any of these does work, which is why a
# closeout runner and a release-adjacent tool are safe to probe here.
JSON_FLAG_MUST_BE_UNRECOGNIZED = (
    ("scripts/check_cli_skill_surface.py", "--repo-root", "."),
    ("scripts/check_command_docs.py", "--repo-root", "."),
    ("scripts/check_github_actions.py", "--repo-root", "."),
    ("scripts/check_issue_closeout_commit_msg.py", "--repo-root", ".", "--commit-msg-file", "README.md"),
    ("scripts/check_public_doc_coupling.py", "--repo-root", "."),
    ("scripts/check_skill_ownership_overlap.py", "--repo-root", "."),
    ("scripts/dup_ratchet_edit_advisory.py", "--repo-root", ".", "--path", "README.md"),
    ("scripts/init_lesson_ledger.py", "--repo-root", "."),
    ("scripts/inventory_skill_script_references.py", "--repo-root", ".", "--strict"),
    ("scripts/measure_inventory_consumption_floor.py", "--repo-root", "."),
    ("scripts/render_lesson_selection_preview.py", "--repo-root", ".", "--seed", "contract-probe"),
    ("skills/public/setup/scripts/seed_dependencies.py", "--repo-root", ".", "--tool-id", "ruff"),
    ("skills/shared/scripts/reviewer_boundary_fingerprint.py", "snapshot", "--repo-root", "."),
)

# The human renderers the migration DELETED, per module that owned them, and the
# payload builder that replaced each where one was introduced. Pinned per module
# rather than repo-wide: a same-named helper elsewhere may be a legitimate payload
# builder, and a repo-wide ban would be a rule this contract cannot honestly make.
DELETED_RENDERERS = (
    ("scripts/check_command_docs.py", ("render_report",), None),
    (
        "scripts/check_issue_closeout_commit_msg.py",
        ("_emit_human_output", "_format_failure", "_stub_evidence_lines", "_ledger_field_lines"),
        "report_payload",
    ),
    ("scripts/check_github_actions.py", ("render_github_actions_report",), "report"),
    ("scripts/inventory_skill_script_references.py", ("render_text", "print_text"), "report"),
    ("scripts/check_documented_command_flags.py", ("render_report",), "report_payload"),
    ("scripts/check_documented_subcommands.py", ("render_report",), "report_payload"),
)


def _owned_python_sources() -> list[Path]:
    paths: list[Path] = []
    for root in _OWNED_SOURCE_ROOTS:
        paths.extend(sorted((ROOT / root).rglob("*.py")))
    # The root `charness` executable is Python with NO `.py` extension, so `rglob`
    # never reached the most public command surface in the repo -- the one CLAUDE.md
    # tells every agent to run. A contract about repo-owned command output that cannot
    # see `charness` is asserting less than it claims.
    paths.append(ROOT / "charness")
    assert paths
    return paths


def _module_level_names(path: Path) -> tuple[set[str], ast.Module]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    defined = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    return defined, tree


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _loaded(command: str) -> object:
    path = ROOT / command
    module_name = "yaml_output_contract_" + command.replace("/", "_").replace(".", "_")
    return load_script_module(module_name, path)


def _run_loaded(*args: str) -> SimpleNamespace:
    command, *script_args = args
    return run_loaded_script_main(command, _loaded(command), *script_args)


@pytest.mark.parametrize(
    "skills_root",
    [ROOT / "skills" / "public", ROOT / "plugins" / "charness" / "skills"],
)
def test_public_skills_do_not_teach_json_output_commands(skills_root: Path) -> None:
    offenders: list[str] = []
    for skill_path in sorted(skills_root.glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        if re.search(
            r"python3[^\n`]*(?:plan_|suggest_public_skill_dogfood)[^\n`]*--json\b",
            text,
        ):
            offenders.append(str(skill_path.relative_to(ROOT)))

    assert offenders == []


def test_create_cli_teaches_yaml_default_and_detail() -> None:
    text = (ROOT / "skills" / "public" / "create-cli" / "SKILL.md").read_text(encoding="utf-8")
    assert "Charness-style commands whose primary caller is an agent" in text
    assert "human-first" in text
    assert "`--detail`" in text


def test_owned_command_references_do_not_teach_json_output() -> None:
    for relative in OWNED_COMMAND_DOCS:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "--json" not in text, relative
    release_index = (ROOT / "skills/public/release/references/index.md").read_text(encoding="utf-8")
    assert "plan_release_run.py" in release_index
    assert "--detail" in release_index


def test_quality_catalog_declares_yaml_agent_packets() -> None:
    catalog_path = ROOT / "skills/public/quality/references/catalog.yaml"
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    commands = {gate["id"]: gate["command"] for gate in catalog["gates"]}

    assert "--json" not in "\n".join(commands.values())
    assert commands["runtime-summary"].endswith("--detail")
    assert commands["skill-ergonomics"].endswith("--summary")


def test_inventory_dispatch_commands_are_runnable_yaml_surfaces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(tmp_path / "pytest-debug-root"))
    snippets = re.findall(r"`\$SKILL_DIR/scripts/([^`]*)`", INVENTORY_DISPATCH)

    assert snippets
    assert len({snippet.split()[0] for snippet in snippets}) == len(snippets)
    for snippet in snippets:
        assert "--summary" in snippet
        argv = shlex.split(snippet)
        if argv[0].startswith("inventory_"):
            continue
        probe_root = ROOT if argv[0] == "suggest_public_skill_dogfood.py" else tmp_path
        argv = [
            {
                ".": str(probe_root),
                "<skill-id>": "quality",
                "<behavior-seam>": "contract-probe",
                "<subject-ref>": "artifact://contract-probe",
                "<risk-focus>": "output-contract",
                "<deterministic-gap>": "semantic-judgment",
            }.get(value, value)
            for value in argv
        ]
        command = f"skills/public/quality/scripts/{argv[0]}"
        summary = _run_loaded(command, *argv[1:])
        help_result = _run_loaded(command, "--help")

        assert summary.returncode == 0, command
        assert isinstance(yaml.safe_load(summary.stdout), dict), command
        assert "--summary" in help_result.stdout
        assert "--detail" in help_result.stdout
        assert "--json" not in help_result.stdout


def test_every_quality_inventory_exposes_yaml_output_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(tmp_path / "inventory-pytest-temp"))
    source_dir = ROOT / "skills/public/quality/scripts"
    plugin_dir = ROOT / "plugins/charness/skills/quality/scripts"
    source_names = {path.name for path in source_dir.glob("inventory_*.py")}
    plugin_names = {path.name for path in plugin_dir.glob("inventory_*.py")}

    assert plugin_names == source_names
    assert source_names
    modules_before = set(sys.modules)
    monkeypatch.syspath_prepend(str(source_dir))
    try:
        for script_name in sorted(source_names):
            module = load_script_module(
                f"quality_inventory_yaml_contract_{Path(script_name).stem}",
                source_dir / script_name,
            )
            args = ("--repo-root", str(tmp_path), "--summary")
            summary = run_loaded_script_main(script_name, module, *args)
            help_result = run_loaded_script_main(script_name, module, "--help")

            assert summary.returncode != 2, script_name
            assert isinstance(yaml.safe_load(summary.stdout), dict), script_name
            assert "--summary" in help_result.stdout, script_name
            assert "--detail" in help_result.stdout, script_name
            assert "--json" not in help_result.stdout, script_name
    finally:
        for module_name in set(sys.modules) - modules_before:
            sys.modules.pop(module_name, None)
    assert set(sys.modules) == modules_before


def test_quality_inventory_keeps_one_real_subprocess_entrypoint_smoke(tmp_path: Path) -> None:
    result = _run(
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "--repo-root",
        str(tmp_path),
        "--summary",
    )

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["status"] == "unconfigured"
    assert result.stderr == ""


def test_quality_dispatch_plugin_commands_match_canonical_source() -> None:
    names = {
        shlex.split(snippet)[0]
        for snippet in re.findall(r"`\$SKILL_DIR/scripts/([^`]*)`", INVENTORY_DISPATCH)
    }
    names.update(
        path.name for path in (ROOT / "skills/public/quality/scripts").glob("inventory_*.py")
    )

    for script_name in sorted(names):
        source = ROOT / "skills/public/quality/scripts" / script_name
        plugin = ROOT / "plugins/charness/skills/quality/scripts" / script_name
        assert plugin.read_bytes() == source.read_bytes(), script_name


@pytest.mark.parametrize(
    "command",
    [
        "skills/public/quality/scripts/inventory_skill_ergonomics.py",
        "plugins/charness/skills/quality/scripts/inventory_skill_ergonomics.py",
    ],
)
def test_summary_and_detail_are_mutually_exclusive(command: str) -> None:
    result = _run_loaded(command, "--repo-root", ".", "--summary", "--detail")

    assert result.returncode == 2
    assert "not allowed with argument" in result.stderr


@pytest.mark.parametrize("command", ALWAYS_STRUCTURED_COMMANDS)
def test_default_yaml_is_structured(command: tuple[str, ...]) -> None:
    default = _run_loaded(*command)
    help_result = _run_loaded(command[0], "--help")

    assert default.returncode == 0
    assert isinstance(yaml.safe_load(default.stdout), dict)
    assert "--json" not in help_result.stdout


@pytest.mark.parametrize("command", DETAIL_COMMANDS)
def test_detail_yaml_is_structured(command: tuple[str, ...]) -> None:
    detail = _run_loaded(*command, "--detail")
    help_result = _run_loaded(command[0], "--help")

    assert detail.returncode != 2
    assert isinstance(yaml.safe_load(detail.stdout), dict)
    assert "--json" not in help_result.stdout


@pytest.mark.parametrize("command", SUMMARY_COMMANDS)
def test_summary_yaml_is_structured(command: tuple[str, ...]) -> None:
    summary = _run_loaded(*command, "--summary")
    help_result = _run_loaded(command[0], "--help")

    assert summary.returncode == 0
    assert isinstance(yaml.safe_load(summary.stdout), dict)
    assert "--json" not in help_result.stdout


def test_yaml_renderer_falls_back_to_json_syntax_valid_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def import_without_yaml(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "yaml":
            raise ImportError("simulated missing PyYAML")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_yaml)
    rendered = yaml_output.render_yaml({"message": "안녕하세요", "items": [1, 2]})

    assert rendered.startswith("{")
    assert yaml.safe_load(rendered) == {"message": "안녕하세요", "items": [1, 2]}


def test_no_repo_owned_command_declares_a_json_flag() -> None:
    """The removal, read off the parsers themselves rather than off `--help`.

    `--help` cannot see an `argparse.SUPPRESS`ed flag, and a suppressed `--json`
    is exactly the shape a "deprecate quietly" instinct produces: invisible in
    help, still accepted, still selecting a second output format. The AST scan is
    the only spelling that catches it. `plugins/` is included on purpose -- the
    exported mirror is what installs run, and a mirror that lags the source is a
    surface where `--json` is still live.
    """
    offenders: list[str] = []
    for path in _owned_python_sources():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            if not (isinstance(function, ast.Attribute) and function.attr == "add_argument"):
                continue
            if any(
                isinstance(arg, ast.Constant) and arg.value == "--json" for arg in node.args
            ):
                offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")

    assert offenders == [], f"repo-owned commands still declare --json: {offenders}"


# stdout that is deliberately NOT this repo's output contract. Each entry is a wire
# protocol some OTHER program parses, so rendering it as YAML would break that reader.
JSON_STDOUT_EXEMPT = {
    "skills/critique/scripts/record_round_findings.py": (
        "portable critique writer uses scripts/yaml_output.py when the packaged helper "
        "exists and deliberately falls back to JSON-as-YAML when an isolated skill "
        "copy has no renderer; tests pin that fallback because it is the bootstrap "
        "contract, not a report-format migration gap."
    ),
    "scripts/post_edit_skill_anchor_guard.py": (
        "the Claude PostToolUse hook envelope ({'hookSpecificOutput': ...}), parsed as "
        "JSON by the HOST. Rendering it as YAML silently stops the advisory reaching "
        "the agent -- the host does not report a parse failure."
    ),
    "charness": (
        "the root CLI's own inlined `render_yaml`, whose PyYAML-absent branch returns "
        "compact JSON so a copied standalone CLI stays usable before the managed "
        "bootstrap provisions PyYAML. Same renderer-fallback case as "
        "scripts/yaml_output.py below; every command path in this file emits through "
        "it, and no other site here writes JSON to stdout."
    ),
    "scripts/yaml_output.py": (
        "the renderer ITSELF. `render_yaml` falls back to compact JSON when PyYAML is "
        "absent, and `emit_yaml` prints it -- that fallback IS the output contract "
        "(JSON is valid YAML, so every consumer still parses it). Flagging the emitter "
        "for emitting its own documented fallback would make the gate refuse the thing "
        "it exists to enforce."
    ),
}


def _json_stdout_sites(tree: ast.Module) -> list[int]:
    """Every spelling that puts JSON on stdout, not just the one a grep finds first.

    This exists because the 2026-08-14 migration was declared complete three times and
    was not: the first scan matched `print(json.dumps(...))`, the second also matched
    `sys.stdout.write(json.dumps(...))`, and `json.dump(payload, sys.stdout)` still hid
    four more commands after that -- including `gather/write_record.py`, whose own
    consumer already read it with `yaml.safe_load`.
    """
    sites: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if (
            isinstance(function, ast.Attribute)
            and function.attr == "dump"
            and isinstance(function.value, ast.Name)
            and function.value.id == "json"
        ):
            # `node.keywords` as well as positionals: `fp` is json.dump's real parameter
            # name, so `json.dump(payload, fp=sys.stdout)` is the idiomatic keyword form
            # of the exact spelling that hid four commands through two prior "complete"
            # claims. Pinning only the positional form leaves that one keystroke open.
            streams = list(node.args[1:]) + [kw.value for kw in node.keywords]
            if any("stdout" in ast.unparse(stream) for stream in streams):
                sites.append(node.lineno)
            continue
        writes_stdout = (
            isinstance(function, ast.Name) and function.id == "print"
        ) or (
            isinstance(function, ast.Attribute)
            and function.attr in {"write", "writelines"}
            and "stdout" in ast.unparse(function.value)
        )
        if not writes_stdout:
            continue
        # `print(..., file=sys.stderr)` is NOT a stdout site. Machine-readable stderr
        # diagnostics are a different channel, and flagging them pushes a legitimate
        # design onto an exempt list documented as being about stdout wire protocols.
        redirected = next(
            (kw.value for kw in node.keywords if kw.arg == "file"), None
        )
        if redirected is not None and "stdout" not in ast.unparse(redirected):
            continue
        for argument in node.args:
            for inner in ast.walk(argument):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "dumps"
                    and isinstance(inner.func.value, ast.Name)
                    and inner.func.value.id == "json"
                ):
                    sites.append(node.lineno)
    return sites


def _json_text_producers(tree: ast.Module) -> set[str]:
    """Names bound to a `json.dumps(...)` result, and functions that return one.

    The scan matched only `print(json.dumps(x))`, so BOTH live survivors of the fourth
    completeness pass hid behind one hop: `rendered = json.dumps(...); print(rendered)`
    and a `render_output()` helper whose dict of lambdas holds the dumps. Following one
    level of indirection is what turns this from a spelling check into a claim about
    what reaches stdout.
    """
    producers: set[str] = set()

    def _holds_dumps(node: ast.AST) -> bool:
        return any(
            isinstance(inner, ast.Call)
            and isinstance(inner.func, ast.Attribute)
            and inner.func.attr == "dumps"
            and isinstance(inner.func.value, ast.Name)
            and inner.func.value.id == "json"
            for inner in ast.walk(node)
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _holds_dumps(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    producers.add(target.id)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _holds_dumps(node):
            producers.add(node.name)
    return producers


def _indirect_json_stdout_sites(tree: ast.Module) -> list[int]:
    """stdout writes whose argument is a name this module bound to JSON text."""
    producers = _json_text_producers(tree)
    if not producers:
        return []
    sites: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        writes_stdout = (
            isinstance(function, ast.Name) and function.id == "print"
        ) or (
            isinstance(function, ast.Attribute)
            and function.attr in {"write", "writelines"}
            and "stdout" in ast.unparse(function.value)
        )
        if not writes_stdout:
            continue
        redirected = next((kw.value for kw in node.keywords if kw.arg == "file"), None)
        if redirected is not None and "stdout" not in ast.unparse(redirected):
            continue
        for argument in node.args:
            for inner in ast.walk(argument):
                if isinstance(inner, ast.Name) and inner.id in producers:
                    sites.append(node.lineno)
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Name)
                    and inner.func.id in producers
                ):
                    sites.append(node.lineno)
    return sites


def test_no_repo_owned_command_writes_json_to_stdout() -> None:
    """The half `--json`-absence cannot prove: that stdout is RENDERED as YAML.

    JSON is valid YAML, so every `yaml.safe_load` assertion in this suite passes over a
    command that never migrated. That is not hypothetical -- it is how 29 commands kept
    emitting JSON through a green suite after the flag was gone from all 100 declaring
    scripts. A flag-absence scan and a behavioral `--json`-is-rejected probe both report
    clean on those commands, because neither asks what the bytes look like.
    """
    offenders: list[str] = []
    for path in _owned_python_sources():
        relative = path.relative_to(ROOT).as_posix()
        if relative.removeprefix("plugins/charness/") in JSON_STDOUT_EXEMPT:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for line in _json_stdout_sites(tree) + _indirect_json_stdout_sites(tree):
            offenders.append(f"{relative}:{line}")

    assert offenders == [], (
        "repo-owned commands still write JSON to stdout; command output is "
        f"unconditionally YAML: {offenders}"
    )


@pytest.mark.parametrize("command", JSON_FLAG_MUST_BE_UNRECOGNIZED, ids=lambda c: c[0])
def test_a_json_flag_is_an_argparse_error_on_every_migrated_command(
    command: tuple[str, ...],
) -> None:
    """Behavioral half of the removal: passing `--json` must FAIL, not be ignored.

    A flag `argparse` merely does not know about and a flag it silently accepts
    are indistinguishable from the source scan above if anything ever reaches for
    `parse_known_args`. Exit 2 with `unrecognized arguments: --json` is what tells
    a caller still passing the old flag that it is gone, instead of handing them a
    payload they will read as the format they asked for.
    """
    result = _run_loaded(*command, "--json")

    assert result.returncode == 2, f"{command[0]}: {result.stdout}{result.stderr}"
    assert "unrecognized arguments: --json" in result.stderr, command[0]


@pytest.mark.parametrize("case", DELETED_RENDERERS, ids=lambda c: c[0])
def test_the_deleted_human_renderers_do_not_come_back(
    case: tuple[str, tuple[str, ...], str | None],
) -> None:
    """The renderers stay deleted, and their replacement stays present.

    Half of this contract is a deletion, and a deletion nothing pins is a
    deletion that gets re-added by the next person who misses the prose. The
    other half is the reason the deletion was safe: each renderer's content moved
    INTO the payload, so the payload builder that received it has to still exist.
    """
    relative, deleted, replacement = case
    defined, _tree = _module_level_names(ROOT / relative)

    assert defined.isdisjoint(deleted), f"{relative} re-added {sorted(defined & set(deleted))}"
    if replacement is not None:
        assert replacement in defined, f"{relative} lost its payload builder `{replacement}`"


def test_emit_findings_report_takes_only_the_report() -> None:
    """The shared emitter's format switch is gone, not defaulted.

    `emit_findings_report(report, as_json=..., render=...)` let one caller keep a
    second output mode for the whole findings-shaped gate family. A parameter left
    in place with a default would look retired while still being reachable, which
    is the residue that made the previous migration look finished when it was not.
    """
    parameters = list(inspect.signature(gate_report_emit.emit_findings_report).parameters)

    assert parameters == ["report"]


def test_summary_output_reports_missing_canonical_renderer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper_path = ROOT / "skills/public/quality/scripts/summary_output_lib.py"
    spec = importlib.util.spec_from_file_location("summary_output_missing_renderer", helper_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    missing_path = SimpleNamespace(resolve=lambda: SimpleNamespace(parents=[]))
    monkeypatch.setattr(module, "Path", lambda _: missing_path)

    with pytest.raises(RuntimeError, match="scripts/yaml_output.py not found"):
        module._load_yaml_output()
