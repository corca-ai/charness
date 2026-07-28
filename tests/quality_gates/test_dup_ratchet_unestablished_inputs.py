"""The dup-ratchet gate over an inventory that established nothing.

Every gate arm here was observed rendering `clean` / `baseline-written` over an input
that never produced a family set: a zero-byte injected inventory, a payload with no
`families` list, a payload whose own `status` reports a missing/broken scanner or a
baseline write, and a live scan of zero families used to overwrite the accepted baseline.

The rule these pin: **`[]` means the producer DECLARED zero families; anything else is a
reason the gate must name.** The asymmetry that made this class invisible is pinned too —
the doc arm has always degraded on a self-reported non-scan status while the code arm
checked shape only (triage sweep S29/S34, closed 2026-07-28).

Split out of `test_dup_ratchet.py` (length cap): those tests own the gate's evaluate
ladder and git seams; this file owns what the gate does when its inputs are unestablished.
Helpers are imported from that module so both files drive the same in-process seam.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from .test_dup_ratchet import (
    _code_inventory,
    _consumer_repo,
    _doc_inventory,
    _run_inproc,
    _write_json,
    baseline_lib,
    scan,
)


def test_inproc_families_from_text_handles_bad_inputs() -> None:
    # `[]` means the payload DECLARED zero families; every shape that does not establish
    # a family list is `None` so the caller degrades. A blank/zero-byte file (a crashed
    # or truncated producer) used to read as a declared-empty inventory, which the gate
    # then reported as a clean pass over a scan that never ran (sweep S29).
    assert scan.families_from_text(None) is None
    assert scan.families_from_text("not json{") is None
    assert scan.families_from_text("[1, 2]") is None  # not a dict
    assert scan.families_from_text('{"families": "x"}') is None  # families not a list
    assert scan.families_from_text("") is None
    assert scan.families_from_text("   \n") is None
    assert scan.families_from_text('{"families": []}') == []  # the declared-empty control


def test_inproc_empty_code_inventory_degrades_instead_of_clean(tmp_path: Path) -> None:
    # End-to-end S29: a zero-byte injected code inventory returned `status: clean,
    # ok: true, degraded_reasons: []`. The gate must name the unreadable inventory.
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    empty = tmp_path / "empty.json"
    empty.write_text("", encoding="utf-8")
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(empty), "--doc-inventory", str(doc_json))
    assert report["status"] == "degraded" and report["block"] is False
    assert any("code inventory unreadable" in reason for reason in report["degraded_reasons"])


def test_inproc_empty_doc_inventory_degrades_instead_of_clean(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    empty = tmp_path / "empty-doc.json"
    empty.write_text("", encoding="utf-8")
    code_json = _code_inventory(tmp_path / "code.json", ["known1"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(empty))
    assert report["status"] == "degraded"
    assert any("no output" in reason for reason in report["degraded_reasons"])


def test_inproc_doc_inventory_without_families_list_degrades(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    bad_doc = _write_json(tmp_path / "nofam.json", {"status": "ok"})
    code_json = _code_inventory(tmp_path / "code.json", ["known1"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(bad_doc))
    assert report["status"] == "degraded"
    assert any("declares no families list" in reason for reason in report["degraded_reasons"])


@pytest.mark.parametrize("status", ["missing", "version-too-old", "error", "baseline-written"])
def test_inproc_non_scan_inventory_status_degrades_on_both_arms(tmp_path: Path, status: str) -> None:
    # A payload reporting one of these statuses answered a different question than "what
    # drifted": the scanner was absent/old/broken, or it reported what was ACCEPTED. Reading
    # it as a declared-empty scan is a clean verdict over a scan that never happened. The
    # code arm checked shape only, so this asymmetry with the doc arm was the S29 class one
    # field over. The status set is shared by both arms BY DESIGN rather than by producer
    # symmetry: `inventory_nose_clones` emits only `missing`/`error` (plus `baseline-written`
    # from the baseline lib, which carries no `families` key at all) and `version-too-old` is
    # doc-only -- but `--code-inventory` accepts any injected file, so the code arm must
    # refuse every status that means "this did not scan".
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    bad = _write_json(tmp_path / f"{status}.json", {"status": status, "families": []})
    good_code = _code_inventory(tmp_path / "code.json", ["known1"])
    good_doc = _doc_inventory(tmp_path / "doc.json", [])

    code_report = _run_inproc(repo, "--code-inventory", str(bad), "--doc-inventory", str(good_doc))
    assert code_report["status"] == "degraded"
    assert any(f"code inventory degraded (status={status})" in r for r in code_report["degraded_reasons"])

    doc_report = _run_inproc(repo, "--code-inventory", str(good_code), "--doc-inventory", str(bad))
    assert doc_report["status"] == "degraded"
    assert any(f"doc inventory degraded (status={status})" in r for r in doc_report["degraded_reasons"])



def test_inproc_write_baseline_refuses_an_empty_scan_and_preserves_baseline(tmp_path: Path) -> None:
    # A zero-family scan wrote an EMPTY accepted baseline and reported success, which then
    # disarms the gate's own "0 families but the baseline has N" backstop (that check is
    # keyed on a non-empty baseline). nose exits 0 with `families: []` over a scope root
    # matching no supported files, so a mistyped scope_paths reaches here — and on
    # first-time bootstrap the large-delta guard is skipped entirely.
    repo = _consumer_repo(tmp_path, baseline_ids=("old1", "old2"))
    code_json = _code_inventory(tmp_path / "code.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--write-baseline")
    assert report["ok"] is False and report["status"] == "empty-scan-unconfirmed"
    preserved = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(preserved) == {"old1", "old2"}  # untouched


def test_inproc_write_baseline_empty_scan_proceeds_when_confirmed(tmp_path: Path) -> None:
    # DISCRIMINATING CONTROL (passes before and after): a genuinely clone-free scope is real,
    # so the new guard is a confirmation gate, not a refusal.
    repo = _consumer_repo(tmp_path, baseline_ids=("old1",))
    code_json = _code_inventory(tmp_path / "code.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--write-baseline",
                         "--confirm-baseline-delta")
    assert report["ok"] is True and report["status"] == "baseline-written"
    assert report["code_family_count"] == 0
