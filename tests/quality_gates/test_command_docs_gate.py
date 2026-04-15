from __future__ import annotations

from pathlib import Path

from .support import ROOT, run_script, write_executable


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
    result = run_script("scripts/check-command-docs.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert "Validated command docs" in result.stdout


def test_check_command_docs_reports_missing_required_doc_phrase(tmp_path: Path) -> None:
    repo = seed_command_docs_repo(tmp_path)
    (repo / "docs" / "demo.md").write_text("Run `demo` for text output.\n", encoding="utf-8")

    result = run_script("scripts/check-command-docs.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "docs/demo.md missing `demo --json`" in result.stderr


def test_check_command_docs_skips_repos_without_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script("scripts/check-command-docs.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "No command-docs contract found" in result.stdout
