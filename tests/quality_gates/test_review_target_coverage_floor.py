"""Explicit --expected-target declarations reach the lane worker's coverage floor.

Split from `test_semantic_review_command.py` for the file-length cap; the lane
harness (`_repo`, `_run`, `_fake_codex`, `_payload`) stays where it was.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from .test_semantic_review_command import _fake_codex, _payload, _repo, _run

pytestmark = pytest.mark.boundary_contract(
    reason="observe the semantic review command's real backend child while the coverage floor judges its result"
)


def _durable_worker_report(tmp_path: Path, attempt: str) -> dict:
    report_path = (
        tmp_path / "charness-artifacts" / "critique" / "workers" / attempt / "worker-report.yaml"
    )
    return yaml.safe_load(report_path.read_text(encoding="utf-8"))


def test_declared_targets_refuse_an_unobserving_lane_result(tmp_path: Path) -> None:
    """An explicit --expected-target opts the run into the worker floor: a
    verdict-pass result that observes no declared target fails coverage
    instead of approval."""
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(
        tmp_path,
        bin_dir,
        "floor-refusal",
        prepared_targets=["item-a"],
        expected_targets=["item-a"],
    )
    payload = _payload(result)

    assert result.returncode == 1
    assert payload["approval_eligible"] is False
    report = _durable_worker_report(tmp_path, "floor-refusal")
    assert report["coverage_ok"] is False
    assert report["expected_targets"] == ["item-a"]
    assert "expected targets" in report["reason"]
    assert "item-a" in report["reason"]


def test_declared_targets_pass_when_each_is_observed_once(tmp_path: Path) -> None:
    """One substantive observation per declared target keeps the lane eligible,
    so the floor only ever fires on dropped inputs, never on observed ones."""
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(
        tmp_path,
        bin_dir,
        "floor-pass",
        prepared_targets=["item-a"],
        expected_targets=["item-a"],
        observations=[
            {
                "target": "item-a",
                "verdict": "pass",
                "summary": "item-a reviewed against the packet",
                "evidence": ["reviewed.txt line 1"],
            }
        ],
    )
    payload = _payload(result)

    assert result.returncode == 0, result.stderr
    assert payload["approval_eligible"] is True
    assert _durable_worker_report(tmp_path, "floor-pass")["coverage_ok"] is True


def test_packet_labels_without_a_declaration_keep_shape_only(tmp_path: Path) -> None:
    """Prepared-target labels stay opaque membership data: without an explicit
    --expected-target the same thin result still passes, so lanes that use
    labels for membership (like issue closeout) are unaffected by the floor."""
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(tmp_path, bin_dir, "floor-opaque", prepared_targets=["item-a"])
    payload = _payload(result)

    assert result.returncode == 0, result.stderr
    assert payload["approval_eligible"] is True
    assert _durable_worker_report(tmp_path, "floor-opaque")["coverage_ok"] is None


def test_dry_run_prompt_names_the_declared_targets_for_observation(tmp_path: Path) -> None:
    """A production backend only learns the target strings from the prompt, so
    the instruction to emit one observation per target is load-bearing."""
    _repo(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_codex(bin_dir / "codex")

    result = _run(
        tmp_path,
        bin_dir,
        "floor-prompt",
        dry_run=True,
        prepared_targets=["item-a"],
        expected_targets=["item-a"],
    )
    payload = _payload(result)

    assert result.returncode == 0, result.stderr
    prompt = (tmp_path / payload["paths"]["prompt"]).read_text(encoding="utf-8")
    assert "exactly one" in prompt
    assert '"item-a"' in prompt
