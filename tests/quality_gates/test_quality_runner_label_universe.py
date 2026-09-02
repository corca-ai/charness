"""The declared gate-list label universe (#546).

The shell queue is retired. The migration reader still supports consumer repos
with shell runners, while this repository's engine refuses malformed declared data
before any gate can run.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

from .support import clone_quality_runner_repo, run_shell_script

ROOT = Path(__file__).resolve().parents[2]


def _quality_universe_module():
    scripts_dir = ROOT / "scripts"
    saved_path = list(sys.path)
    sys.path.insert(0, str(scripts_dir))
    try:
        return load_script_module(
            "quality_label_universe_declaration_under_test",
            scripts_dir / "quality_label_universe.py",
        )
    finally:
        sys.path[:] = saved_path


def test_declared_gate_rows_are_nonempty_and_data_is_authoritative() -> None:
    universe = _quality_universe_module()
    rows = universe.quality_gate_rows(ROOT)
    assert rows
    comparison = universe.parity(ROOT)
    assert comparison["symmetric_difference"] == set()
    assert comparison["pair_symmetric_difference"] == set()


def test_parity_compares_label_and_argv_pairs_not_only_labels(tmp_path: Path) -> None:
    universe = _quality_universe_module()
    (tmp_path / ".agents").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / ".agents" / "quality-gates.yaml").write_text(
        "schema: charness/quality-gates/v1\n"
        "phases:\n"
        "  - id: main\n"
        "    isolation: concurrent\n"
        "    fail_fast: false\n"
        "    gates:\n"
        "      - label: same-label\n"
        "        command:\n"
        "          - python3\n"
        "          - new.py\n"
        "        lane: core\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts" / "run-quality.sh").write_text(
        'queue_selected "same-label" python3 old.py\n', encoding="utf-8"
    )

    comparison = universe.parity(tmp_path)
    assert comparison["symmetric_difference"] == set()
    assert comparison["pair_symmetric_difference"]


def test_present_but_empty_gate_declaration_is_a_loud_refusal(tmp_path: Path) -> None:
    universe = _quality_universe_module()
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "quality-gates.yaml").write_text(
        "schema: charness/quality-gates/v1\nphases:\n  - id: empty\n    gates:\n",
        encoding="utf-8",
    )
    with pytest.raises(universe.UniverseError, match="declares zero gates"):
        universe.label_universe(tmp_path)


def test_missing_gate_declaration_reports_the_shell_source(tmp_path: Path) -> None:
    universe = _quality_universe_module()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "run-quality.sh").write_text(
        'queue_selected "shell-gate" true\n', encoding="utf-8"
    )
    payload = universe.label_universe(tmp_path)
    assert payload["source"] == "shell"
    assert payload["sources"]["queue_call_sites"] == ["shell-gate"]


def test_runner_passes_the_declared_data_file_without_a_queue_or_inline_parser(
    seeded_quality_runner_repo: Path,
) -> None:
    runner = (seeded_quality_runner_repo / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    assert '--gates "$REPO_ROOT/.agents/quality-gates.yaml"' in runner
    assert "queue_selected" not in runner
    assert "bash -c" not in runner


def test_malformed_declared_gate_data_refuses_the_run(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """The engine schema check replaces the retired queue-time assertion."""
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    (repo / ".agents" / "quality-gates.yaml").write_text("schema: wrong\n", encoding="utf-8")
    runner = repo / "scripts" / "run-quality.sh"
    result = run_shell_script(runner, cwd=repo, env=env)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "gate list schema" in result.stderr
