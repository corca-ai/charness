from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from .support import ROOT, run_script, write_executable


def _load_render_cli_reference():
    spec = importlib.util.spec_from_file_location(
        "render_cli_reference", ROOT / "scripts" / "render_cli_reference.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
