from __future__ import annotations

import builtins
import importlib.util
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts import yaml_output
from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

OWNED_COMMAND_DOCS = (
    "AGENTS.md",
    "evals/cautilus/skill-experiment/README.md",
    "skills/public/quality/references/cautilus-on-demand.md",
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
        "skills/public/handoff/scripts/plan_handoff_run.py",
        "--repo-root",
        ".",
        "--intent",
        "refresh",
    ),
    (
        "skills/public/retro/scripts/plan_retro_run.py",
        "--repo-root",
        ".",
        "--invocation-text",
        "contract probe",
    ),
)

DETAIL_COMMANDS = (
    ("scripts/plan_cautilus_proof.py", "--repo-root", "."),
    ("skills/public/quality/scripts/plan_quality_run.py", "--repo-root", "."),
    ("skills/public/quality/scripts/render_runtime_summary.py", "--repo-root", "."),
    (
        "skills/public/quality/scripts/inventory_ci_recoverable_gates.py",
        "--repo-root",
        ".",
    ),
    ("skills/public/release/scripts/plan_release_run.py", "--repo-root", "."),
    ("scripts/plan_risk_interrupt.py", "--repo-root", "."),
    ("skills/public/setup/scripts/render_skill_routing.py", "--repo-root", "."),
    ("skills/public/prove/scripts/check_boundary_escalation.py", "--repo-root", "."),
    (
        "skills/public/quality/scripts/suggest_public_skill_dogfood.py",
        "--repo-root",
        ".",
        "--skill-id",
        "handoff",
    ),
)

SUMMARY_COMMANDS = (
    ("skills/public/quality/scripts/inventory_skill_ergonomics.py", "--repo-root", "."),
)
INVENTORY_DISPATCH = (
    ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
).read_text(encoding="utf-8")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    "skills_root",
    [ROOT / "skills" / "public", ROOT / "plugins" / "charness" / "skills"],
)
def test_public_skills_do_not_teach_json_output_commands(skills_root: Path) -> None:
    offenders: list[str] = []
    for skill_path in sorted(skills_root.glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        if re.search(
            r"python3[^\n`]*(?:plan_|render_skill_routing|check_boundary_escalation|suggest_public_skill_dogfood)[^\n`]*--json\b",
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
        summary = _run(command, *argv[1:])
        compatibility = _run(command, *argv[1:], "--json")
        help_result = _run(command, "--help")

        assert summary.returncode == compatibility.returncode, command
        assert yaml.safe_load(summary.stdout) == json.loads(compatibility.stdout), command
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
            compatibility = run_loaded_script_main(script_name, module, *args, "--json")
            help_result = run_loaded_script_main(script_name, module, "--help")

            assert summary.returncode == compatibility.returncode, script_name
            assert yaml.safe_load(summary.stdout) == json.loads(compatibility.stdout), script_name
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
    result = _run(command, "--repo-root", ".", "--summary", "--detail")

    assert result.returncode == 2
    assert "not allowed with argument" in result.stderr


@pytest.mark.parametrize("command", ALWAYS_STRUCTURED_COMMANDS)
def test_default_yaml_preserves_hidden_json_compatibility(command: tuple[str, ...]) -> None:
    default = _run(*command)
    legacy = _run(*command, "--json")
    help_result = _run(command[0], "--help")

    assert default.returncode == legacy.returncode == 0
    assert yaml.safe_load(default.stdout) == json.loads(legacy.stdout)
    assert "--json" not in help_result.stdout


@pytest.mark.parametrize("command", DETAIL_COMMANDS)
def test_detail_yaml_preserves_hidden_json_compatibility(command: tuple[str, ...]) -> None:
    detail = _run(*command, "--detail")
    legacy = _run(*command, "--json")
    help_result = _run(command[0], "--help")

    assert detail.returncode == legacy.returncode
    assert yaml.safe_load(detail.stdout) == json.loads(legacy.stdout)
    assert "--json" not in help_result.stdout


@pytest.mark.parametrize("command", SUMMARY_COMMANDS)
def test_summary_yaml_preserves_hidden_json_compatibility(command: tuple[str, ...]) -> None:
    summary = _run(*command, "--summary")
    legacy = _run(*command, "--summary", "--json")
    help_result = _run(command[0], "--help")

    assert summary.returncode == legacy.returncode == 0
    assert yaml.safe_load(summary.stdout) == json.loads(legacy.stdout)
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
