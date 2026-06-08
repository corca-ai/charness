"""Tests for the #339 proof-mismatch closeout floor.

Drives the three blocking conditions (missing proof entry / reached < required /
gap lacks disposition) with a SYNTHETIC adapter, the degradation path, and the
achieve-CLI integration. No domain concept is involved — the adapter supplies the
proof semantics.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path

from scripts import proof_mismatch as pm

_ROOT = Path(__file__).resolve().parents[2]
_CLI_PATH = _ROOT / "skills" / "public" / "achieve" / "scripts" / "check_goal_artifact.py"


def _load_cli():
    # In-process load of the achieve CLI (NOT a subprocess) so the proof-mismatch
    # wiring is exercised through `main()` without adding a delivery-boundary spawn
    # (the boundary-bypass ratchet's intended in-process form).
    spec = importlib.util.spec_from_file_location("check_goal_artifact_under_test", _CLI_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CLI = _load_cli()

_ADAPTER = (
    "proof_levels:\n  - lint\n  - smoke\n  - integration\n  - live\n"
    "incomparable:\n  - lint, smoke\n"
    "acceptance_map:\n  reliability: integration\n  safety: live\n"
)


def _repo(tmp_path: Path, adapter: str | None = _ADAPTER) -> Path:
    if adapter is not None:
        target = tmp_path / ".agents" / "proof-semantics-adapter.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(adapter, encoding="utf-8")
    return tmp_path


def _ledger(rows: str) -> str:
    return (
        "# Goal\n\n## Proof Ledger\n\n"
        "| Acceptance Class | Reached Proof | Disposition |\n| --- | --- | --- |\n" + rows
    )


# --- parsing ---------------------------------------------------------------


def test_parse_proof_ledger_columns_by_header() -> None:
    body = (
        "| Reached Proof | Acceptance Class | Disposition |\n| --- | --- | --- |\n"
        "| smoke | reliability | accepted-risk: x |\n"
    )
    rows = pm.parse_proof_ledger(body)
    assert rows[0]["acceptance_class"] == "reliability"
    assert rows[0]["reached"] == "smoke"
    assert rows[0]["disposition"] == "accepted-risk: x"


def test_parse_requires_class_and_reached_columns() -> None:
    # No reached/proof column -> not a proof ledger table (no fire).
    assert pm.parse_proof_ledger("| Acceptance Class | Note |\n| --- | --- |\n| reliability | x |\n") == []


def test_parse_groups_tables_and_masks_fences() -> None:
    body = (
        "| Phase | Status |\n| --- | --- |\n| build | done |\n\n"
        "| Acceptance Class | Reached Proof |\n| --- | --- |\n| reliability | smoke |\n\n"
        "```\n| Acceptance Class | Reached Proof |\n| --- | --- |\n| safety | live |\n```\n"
    )
    rows = pm.parse_proof_ledger(body)
    # the leading non-proof table is passed over; the fenced table is inert.
    assert [r["acceptance_class"] for r in rows] == ["reliability"]


# --- evaluate_row: the three conditions + satisfies + degraded ----------------


def _data(tmp_path: Path) -> dict:
    return pm.load_adapter(_repo(tmp_path))["data"]


def test_row_satisfies_no_gap(tmp_path: Path) -> None:
    data = _data(tmp_path)
    row = pm.evaluate_row({"acceptance_class": "reliability", "reached": "live", "disposition": ""}, data, True)
    assert row["gap"] is False and row["disposition_ok"] is True


def test_row_condition_i_no_proof_entry(tmp_path: Path) -> None:
    data = _data(tmp_path)
    for reached in ("", "<reached>", "TODO"):
        row = pm.evaluate_row({"acceptance_class": "reliability", "reached": reached, "disposition": ""}, data, True)
        assert row["gap"] is True and row["gap_kind"] == "no-proof-entry", reached


def test_row_condition_ii_proof_below_acceptance(tmp_path: Path) -> None:
    data = _data(tmp_path)
    row = pm.evaluate_row({"acceptance_class": "reliability", "reached": "smoke", "disposition": ""}, data, True)
    assert row["gap"] is True and row["gap_kind"] == "proof-below-acceptance"
    # incomparable reached (lint vs integration via the chain) also fails to satisfy
    row2 = pm.evaluate_row({"acceptance_class": "reliability", "reached": "lint", "disposition": ""}, data, True)
    assert row2["gap"] is True


def test_row_unmapped_class_is_a_gap(tmp_path: Path) -> None:
    data = _data(tmp_path)
    row = pm.evaluate_row({"acceptance_class": "mystery", "reached": "live", "disposition": ""}, data, True)
    assert row["gap"] is True and row["gap_kind"] == "unmapped-class"


def test_row_degraded_when_no_map() -> None:
    row = pm.evaluate_row({"acceptance_class": "reliability", "reached": "live", "disposition": ""}, {}, False)
    assert row["gap"] is True and row["gap_kind"] == "degraded"


def test_gap_disposition_must_be_real_not_placeholder_or_prose(tmp_path: Path) -> None:
    data = _data(tmp_path)
    base = {"acceptance_class": "reliability", "reached": "smoke"}
    assert pm.evaluate_row({**base, "disposition": "accepted-risk: monitored"}, data, True)["disposition_ok"] is True
    assert pm.evaluate_row({**base, "disposition": "issue #340"}, data, True)["disposition_ok"] is True
    for bad in ("", "<reason>", "TODO later", "defer", "recorded in retro", "none — n/a"):
        assert pm.evaluate_row({**base, "disposition": bad}, data, True)["disposition_ok"] is False, bad


# --- proof_mismatch_report: end-to-end verdicts ----------------------------


def test_report_mismatch_then_dispositioned(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    bad = _ledger("| reliability | smoke | |\n")
    rep = pm.proof_mismatch_report(repo, bad)
    assert rep["problem"] == "mismatch"
    assert rep["undispositioned"][0]["gap_kind"] == "proof-below-acceptance"
    good = _ledger("| reliability | smoke | accepted-risk: monitored, low impact |\n")
    assert pm.proof_mismatch_report(repo, good)["problem"] is None


def test_report_satisfies_and_inert_without_ledger(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    assert pm.proof_mismatch_report(repo, _ledger("| reliability | integration | |\n"))["problem"] is None
    inert = pm.proof_mismatch_report(repo, "# Goal\n\nno ledger here\n")
    assert inert["problem"] is None and inert["present"] is False


def test_report_degraded_missing_adapter_requires_disposition(tmp_path: Path) -> None:
    repo = _repo(tmp_path, adapter=None)  # no adapter
    rep = pm.proof_mismatch_report(repo, _ledger("| reliability | live | |\n"))
    assert rep["problem"] == "mismatch" and rep["degraded"] is True
    ok = pm.proof_mismatch_report(repo, _ledger("| reliability | live | applied: verified live this run |\n"))
    assert ok["problem"] is None


def test_report_invalid_adapter_fails_closed(tmp_path: Path) -> None:
    repo = _repo(tmp_path, adapter="acceptance_map:\n  reliability: integration\n")  # no proof_levels -> invalid
    rep = pm.proof_mismatch_report(repo, _ledger("| reliability | live | |\n"))
    assert rep["problem"] == "invalid-adapter"
    assert rep["adapter_valid"] is False


def test_apply_proof_mismatch_floor_mutates_report(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    report = {"ok": True}
    pm.apply_proof_mismatch_floor(report, repo, _ledger("| reliability | smoke | |\n"))
    assert report["ok"] is False
    assert report["proof_mismatch"]["problem"] == "mismatch"
    assert report["proof_mismatch_scope"]["present"] is True
    # dispositioned -> no block, scope still recorded
    report2 = {"ok": True}
    pm.apply_proof_mismatch_floor(report2, repo, _ledger("| reliability | smoke | out-of-scope: tracked in #338 |\n"))
    assert report2["ok"] is True and "proof_mismatch" not in report2


# --- achieve CLI integration (differential: gap blocks, dispositioned passes) ---


def _complete_goal(proof_rows: str) -> str:
    # A status:complete goal carrying a proof ledger. Other closeout evidence is
    # intentionally absent, so the run is non-zero regardless; the DIFFERENTIAL
    # assertion (proof-mismatch reason present vs absent) isolates this floor.
    return (
        "# Achieve Goal: T\n\nStatus: complete\nCreated: 2026-06-10\n"
        "Activation: `/goal @charness-artifacts/goals/2026-06-10-x.md`\n\n"
        "## Proof Ledger\n\n"
        "| Acceptance Class | Reached Proof | Disposition |\n| --- | --- | --- |\n" + proof_rows + "\n"
    )


def _run_cli(repo: Path, goal_path: Path) -> dict:
    buf = io.StringIO()
    old_argv = sys.argv
    sys.argv = ["check_goal_artifact.py", "--repo-root", str(repo), "--goal-path", str(goal_path)]
    try:
        with contextlib.redirect_stdout(buf):
            _CLI.main()
    finally:
        sys.argv = old_argv
    return json.loads(buf.getvalue())


def test_cli_blocks_undispositioned_proof_gap(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    goal = tmp_path / "goal.md"
    goal.write_text(_complete_goal("| reliability | smoke | |\n"), encoding="utf-8")
    payload = _run_cli(repo, goal)
    assert payload["ok"] is False
    joined = " ".join(payload.get("issues", []))
    assert "proof-mismatch floor" in joined


def test_cli_passes_dispositioned_proof_gap(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    goal = tmp_path / "goal.md"
    goal.write_text(_complete_goal("| reliability | smoke | accepted-risk: monitored this run |\n"), encoding="utf-8")
    payload = _run_cli(repo, goal)
    # other closeout evidence may still fail, but the proof-mismatch floor must NOT.
    joined = " ".join(payload.get("issues", []))
    assert "proof-mismatch floor" not in joined
    assert "proof_mismatch" not in payload.get("closeout_evidence", {})
