"""The not-run pass: rows the requested scope asked for that the run did not execute.

`scripts/run_quality_engine_selection.py` and `scripts/run_quality_engine_receipt.py`
are named here by path so the changed-line coverage mapper, which resolves a
production file to its standing tests through textual references, can see them.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from run_quality_engine_model import Gate, GateList, Phase

from tests.script_main import load_script_module

from .support import ROOT
from .test_run_quality_engine import ENGINE, _run, _seed

SELECTION = load_script_module(
    "tests.quality_gates.support_run_quality_engine_selection",
    ROOT / "scripts" / "run_quality_engine_selection.py",
)
RECEIPT = load_script_module(
    "tests.quality_gates.support_run_quality_engine_receipt",
    ROOT / "scripts" / "run_quality_engine_receipt.py",
)

PREDICATE_GATES = """schema: charness/quality-gates/v1
phases:
  - id: prerequisite
    isolation: alone
    fail_fast: true
    gates:
      - label: core
        command:
          - python3
          - tests/quality_gates/fixtures/engine_gate.py
          - core
        lane: core
      - label: profiled
        command:
          - python3
          - tests/quality_gates/fixtures/engine_gate.py
          - profiled
        lane: core
        condition:
          predicate: runtime_profile_present
      - label: dead-code
        command:
          - python3
          - tests/quality_gates/fixtures/engine_gate.py
          - dead-code
        lane: opt-in
        condition:
          env:
            QUALITY_OPT_IN: "1"
"""


def _gate(
    label: str,
    *,
    lane: str = "core",
    condition: dict | None = None,
    variant_of: str | None = None,
) -> Gate:
    return Gate(
        label=label,
        command=("python3", "gate.py", label),
        lane=lane,
        condition=condition or {},
        variant_of=variant_of,
        unestablished_capable=False,
        native_preflight=False,
        timing_layer=None,
        docs_only=False,
        note=None,
    )


def _gate_list(*gates: Gate) -> GateList:
    phase = Phase(
        identifier="only",
        isolation="alone",
        fail_fast=False,
        fail_message=None,
        gates=gates,
    )
    return GateList(phases=(phase,), runner_variables=frozenset())


def _not_run(gate_list: GateList, selected: dict[str, tuple[Gate, ...]], **overrides):
    scope = {
        "repo_root": ROOT,
        "mode": "full",
        "full_queue": False,
        "release": False,
        "include_release_only": False,
        "labels": "",
        "environment": {},
    }
    scope.update(overrides)
    return SELECTION.not_run_gates(gate_list, selected, **scope)


def test_each_unrun_row_carries_the_reason_it_was_skipped() -> None:
    """The reason is the point: "not run" alone cannot be acted on.

    A non-claim was declined, a read-only run deferred a writing check, an opt-in
    was never switched on, and a condition did not hold. Those are four different
    situations for the reader, so they are four different words in the receipt.
    """
    ran = _gate("ran")
    gate_list = _gate_list(
        ran,
        _gate("declined"),
        _gate("writes", condition={"mode_in": ["full"]}),
        _gate("dead-code", lane="opt-in", condition={"env": {"QUALITY_OPT_IN": "1"}}),
        _gate("checker", condition={"file_exists": "scripts/absent-checker.py"}),
    )

    rows = _not_run(
        gate_list,
        {"only": (ran,)},
        mode="read-only",
        excluded_labels=frozenset({"declined"}),
    )

    assert rows == (
        ("declined", SELECTION.NOT_RUN_NON_CLAIM),
        ("writes", SELECTION.NOT_RUN_READ_ONLY),
        ("dead-code", SELECTION.NOT_RUN_OPT_IN),
        ("checker", SELECTION.NOT_RUN_CONDITION),
    )


def test_a_variant_sibling_that_ran_establishes_the_family_claim() -> None:
    """The release variant of a check is the same claim as its standard sibling.

    Naming the sibling as "not run" would report a gap the run does not have.
    """
    release_variant = _gate("pytest-release", lane="release-only", variant_of="pytest")
    gate_list = _gate_list(release_variant, _gate("pytest", lane="standard", variant_of="pytest"))

    rows = _not_run(
        gate_list,
        {"only": (release_variant,)},
        full_queue=True,
        release=True,
        include_release_only=True,
    )

    assert rows == ()


def test_a_matching_row_absent_from_the_selection_is_reported_as_no_reason() -> None:
    """Silence beats a fabricated reason when the two passes disagree.

    The not-run pass re-evaluates conditions; if a row's conditions hold, there is
    no reason to give for its absence, so it is omitted rather than labelled with a
    guess. Keeping both passes on one cached answer is what stops that disagreement
    from arising in the engine.
    """
    gate_list = _gate_list(_gate("core"), _gate("also-core"))

    assert _not_run(gate_list, {"only": ()}) == ()


def test_not_run_reads_the_process_environment_when_no_scope_is_supplied() -> None:
    gate_list = _gate_list(
        _gate("switched", lane="opt-in", condition={"env": {"QUALITY_OPT_IN": "1"}})
    )

    assert SELECTION.not_run_gates(
        gate_list,
        {"only": ()},
        repo_root=ROOT,
        mode="full",
        full_queue=False,
        release=False,
        include_release_only=False,
        labels="",
    ) == (("switched", SELECTION.NOT_RUN_OPT_IN),)


def test_a_cached_predicate_is_answered_once_for_both_selection_passes() -> None:
    """Selection and the not-run pass ask the same question of the same run.

    An uncached probe could answer differently the second time -- the working tree
    moves -- and the run would then claim a row was skipped for a condition that
    held when it was selected.
    """
    asked: list[int] = []
    probe = ENGINE._cached(lambda: asked.append(1) or "a non-empty answer")

    first, second = probe(), probe()

    assert (first, second) == (True, True)
    assert asked == [1]


def test_engine_reports_unrun_rows_in_its_summary_and_receipt(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    (repo / "quality-gates.yaml").write_text(PREDICATE_GATES, encoding="utf-8")

    result = _run(repo, env, CHARNESS_RUNTIME_PROFILE="")

    assert result.returncode == 0, result.stderr
    assert (
        "Quality summary: 1 passed, 0 failed, 2 not run "
        "(profiled: condition unmet; dead-code: opt-in unmet), total"
    ) in result.stdout
    receipt = json.loads((repo / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["measured_scope"] == ["core"]
    assert receipt["details"]["not_run"] == [
        {"label": "profiled", "reason": "condition unmet"},
        {"label": "dead-code", "reason": "opt-in unmet"},
    ]


def test_a_predicate_that_holds_moves_its_row_out_of_the_unrun_list(tmp_path: Path) -> None:
    repo, env = _seed(tmp_path)
    (repo / "quality-gates.yaml").write_text(PREDICATE_GATES, encoding="utf-8")

    result = _run(repo, env, CHARNESS_RUNTIME_PROFILE="fast")

    assert result.returncode == 0, result.stderr
    assert "PASS profiled" in result.stdout
    assert (
        "Quality summary: 2 passed, 0 failed, 1 not run (dead-code: opt-in unmet), total"
    ) in result.stdout


def test_receipt_fallback_summary_keeps_the_not_run_clause(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The fallback line is printed when the receipt CLI itself could not speak.

    That is exactly the moment the omission must survive: a summary that silently
    drops the unrun rows would read as a clean green.
    """
    # A forced elapsed reading: the claim here is the not-run clause, and a real
    # duration would make the assertion depend on how fast this machine is.
    monkeypatch.setattr(RECEIPT, "format_elapsed", lambda elapsed_ms: "7ms")
    context = RECEIPT.RuntimeContext(
        repo_root=tmp_path,
        environment=dict(os.environ),
        runtime_root=tmp_path / "runtime",
        state_args=(),
        temp_dir=tmp_path / "tmp",
        regime="",
    )

    RECEIPT.finish(
        context,
        RECEIPT.Ledger(passed=2, failed=1),
        started_at=0.0,
        mode="full",
        release=False,
        full_queue=False,
        non_claim="",
        receipt_json="",
        labels="core",
        overall_rc=1,
        not_run=(("dead-code", "opt-in unmet"), ("profiled", "condition unmet")),
    )

    captured = capsys.readouterr()
    assert captured.out.strip() == (
        "Quality summary: 2 passed, 1 failed, 2 not run "
        "(dead-code: opt-in unmet; profiled: condition unmet), total 7ms"
    )
