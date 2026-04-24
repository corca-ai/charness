from __future__ import annotations

import json
from pathlib import Path

from .support import run_script, write_executable


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


def test_cli_skill_surface_is_not_applicable_without_product_combo(tmp_path: Path) -> None:
    repo = seed_repo(tmp_path, adapter_body="version: 1\nproduct_surfaces:\n- installable_cli\n")
    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "not_applicable"


def test_cli_skill_surface_blocks_declared_combo_without_binary_delegation(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        adapter_body="version: 1\nproduct_surfaces:\n- installable_cli\n- bundled_skill\n",
    )
    result = run_script("scripts/check_cli_skill_surface.py", "--repo-root", str(repo), "--json")
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


def test_cli_skill_surface_skips_irrelevant_release_change(tmp_path: Path) -> None:
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
    result = run_script(
        "scripts/check_cli_skill_surface.py",
        "--repo-root",
        str(repo),
        "--changed-path",
        "docs/notes.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "skipped"
