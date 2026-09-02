"""The runner's queue-time label-universe assertion (#546).

Split out of `test_quality_runner.py` by topic, not to dodge the length cap: these
two tests are about ONE mechanism -- the runner refusing to queue a gate whose label
`quality_label_universe` could not find -- and they are the coverage that lets a
regex over bash be load-bearing on a proof surface. They belong together and away
from the runner's summary/receipt/exit-code behavior.

The two refusal paths are owned by different components, and the docstrings say
which is which: an unresolvable label is refused by the READER before any gate
runs, an invisible call site is refused by the ASSERTION at the gate that queues it.
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


def test_declared_gate_rows_are_nonempty_and_match_the_shell_migration_source() -> None:
    universe = _quality_universe_module()
    rows = universe.quality_gate_rows(ROOT)
    assert rows
    comparison = universe.parity(ROOT)
    assert comparison["symmetric_difference"] == set()


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


def test_runner_consumes_labels_only_without_an_inline_parser(
    seeded_quality_runner_repo: Path,
) -> None:
    runner = (seeded_quality_runner_repo / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    assert (
        'python3 scripts/quality_label_universe.py --repo-root "$REPO_ROOT" --labels-only'
    ) in runner
    assert "python3 -c" not in runner


def test_a_gate_label_the_universe_reader_cannot_see_refuses_the_run(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """The queue-time assertion (#546), which is the whole reason a regex over bash
    is allowed to be load-bearing here.

    A queue call the reader's line-anchored regex cannot SEE is the miss the
    assertion exists for -- here a one-line `if ...; then queue_timed ...; fi`. The
    reader does not refuse it (there is nothing unresolvable to refuse); the label
    simply never enters the universe, and every budget naming it would then read as
    orphaned, with the budget gate telling the operator to delete a correct bar.
    The assertion turns that silent shrink into a refusal at the gate that caused
    it, naming the label.

    Note the neighbouring case is covered by the OTHER test: an unregistered wrapper
    forwarding `"$1"` is caught by the reader itself, because a non-literal label at
    a call site is unresolvable rather than invisible.
    """
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    runner = repo / "scripts" / "run-quality.sh"
    text = runner.read_text(encoding="utf-8")
    marker = 'queue_selected "validate-skills"'
    assert marker in text, "runner shape changed; pick another insertion point"
    runner.write_text(
        text.replace(marker, 'if true; then queue_timed "ghost-gate" true; fi\n' + marker, 1),
        encoding="utf-8",
    )
    result = run_shell_script(runner, cwd=repo, env=env)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ghost-gate" in result.stderr
    assert "did not find it in this file" in result.stderr


def test_a_runner_the_reader_cannot_parse_stops_before_any_gate(
    tmp_path: Path, seeded_quality_runner_repo: Path
) -> None:
    """The reader raises on a call site it cannot resolve. The runner surfaces the
    reader's OWN message rather than a traceback or a second, different failure."""
    repo, env = clone_quality_runner_repo(tmp_path, seeded_quality_runner_repo)
    runner = repo / "scripts" / "run-quality.sh"
    runner.write_text(
        runner.read_text(encoding="utf-8") + '\nqueue_selected "$computed" true\n',
        encoding="utf-8",
    )
    result = run_shell_script(runner, cwd=repo, env=env)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "the gate-label reader refused this runner" in result.stderr
    assert "non-literal label" in result.stderr
    assert "Traceback" not in result.stderr
