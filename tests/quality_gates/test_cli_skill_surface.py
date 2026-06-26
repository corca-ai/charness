from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module

from .support import ROOT, run_script, write_executable

_check_cli_skill_surface = import_repo_module(
    ROOT / "scripts/check_cli_skill_surface.py",
    "scripts.check_cli_skill_surface",
)


def run_cli_skill_surface(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_cli_skill_surface.py", *args])
    returncode = _check_cli_skill_surface.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def seed_repo(tmp_path: Path, *, adapter_body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "scripts").mkdir()
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(adapter_body, encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n# Demo\n\nUse `demo --help` and `demo doctor --json` for command details.\n",
        encoding="utf-8",
    )
    write_executable(
        repo / "demo",
        "#!/usr/bin/env bash\nset -euo pipefail\nprintf 'demo help --json doctor example registry\\n'\n",
    )
    return repo


def test_cli_skill_surface_is_not_applicable_without_product_combo_or_inferred_skill(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nproduct_surfaces:\n- installable_cli\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "not_applicable"


def test_cli_skill_surface_flags_inferred_combo_without_adapter_fields(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(tmp_path, adapter_body="version: 1\nproduct_surfaces: []\n")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["product_surface_source"] == "inferred"
    assert "adapter does not declare `installable_cli`" in "\n".join(payload["adapter_weaknesses"])
    assert "cli_skill_surface_probe_commands is empty" in "\n".join(payload["adapter_weaknesses"])


def test_cli_skill_surface_blocks_declared_combo_without_binary_delegation(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="version: 1\nproduct_surfaces:\n- installable_cli\n- bundled_skill\n",
    )
    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert "No command-docs file or `--help` probe" in "\n".join(payload["blockers"])


def test_cli_skill_surface_accepts_declared_combo_with_probes_and_docs(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- ./demo --help",
                "- ./demo doctor --json",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")
    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["status"] == "ok"
    assert payload["probe_commands"] == ["./demo --help", "./demo doctor --json"]


def test_cli_skill_surface_reports_probe_timeout(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- python3 scripts/hang.py",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")
    write_executable(repo / "scripts" / "hang.py", "#!/usr/bin/env python3\nimport time\ntime.sleep(2)\n")
    env = os.environ.copy()
    env["CHARNESS_CLI_SKILL_SURFACE_PROBE_TIMEOUT_SECONDS"] = "0.1"

    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--run-probes", "--json", env=env)
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["probe_results"][0]["returncode"] == 124
    assert "timed out after 0.1s" in payload["probe_results"][0]["stderr_preview"]


def test_cli_skill_surface_blocks_direct_agent_browser_runtime_probes(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- agent-browser open https://example.com",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert "Unsafe CLI plus skill probe `agent-browser open https://example.com`" in "\n".join(payload["blockers"])


def test_cli_skill_surface_blocks_wrapped_agent_browser_runtime_probes(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- env FOO=1 agent-browser open https://example.com",
                "- bash -c 'agent-browser screenshot /tmp/page.png'",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    blockers = "\n".join(payload["blockers"])
    assert "env FOO=1 agent-browser open https://example.com" in blockers
    assert "bash -c 'agent-browser screenshot /tmp/page.png'" in blockers


def test_cli_skill_surface_reports_missing_skill_path_adapter_weakness(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_probe_commands:",
                "- ./demo --help",
                "- ./demo doctor --json",
                "cli_skill_surface_command_docs:",
                "- .agents/command-docs.yaml",
                "",
            ]
        ),
    )
    (repo / ".agents" / "command-docs.yaml").write_text("commands:\n  root:\n    help_command: ./demo --help\n", encoding="utf-8")

    result = run_cli_skill_surface(monkeypatch, capsys, "--repo-root", str(repo), "--json")

    payload = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert payload["status"] == "ok"
    assert "cli_skill_surface_skill_paths is empty" in "\n".join(payload["adapter_weaknesses"])


def test_cli_skill_surface_skips_irrelevant_release_change(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="\n".join(
            [
                "version: 1",
                "product_surfaces:",
                "- installable_cli",
                "- bundled_skill",
                "cli_skill_surface_change_globs:",
                "- src/**",
                "",
            ]
        ),
    )
    result = run_cli_skill_surface(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--changed-path",
        "docs/notes.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "skipped"
