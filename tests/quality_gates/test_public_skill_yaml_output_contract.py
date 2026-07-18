from __future__ import annotations

import builtins
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts import yaml_output

from .support import ROOT

OWNED_COMMAND_DOCS = (
    "AGENTS.md",
    "evals/cautilus/skill-experiment/README.md",
    "skills/public/quality/references/cautilus-on-demand.md",
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
