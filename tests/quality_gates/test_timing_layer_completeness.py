"""Tests for the #368 timing-layer completeness meta-gate.

The live guard (`test_real_repo_table_is_complete`) is the load-bearing one: it
proves every gate `run-quality.sh` runs carries a verdict in the classification
table, so the shift-left class cannot recur via an unclassified broad-only check.
The negative guard proves an unclassified label turns the gate red.
"""

from __future__ import annotations

import importlib
from pathlib import Path

from .support import ROOT

META = importlib.import_module("scripts.check_timing_layer_completeness")


def test_real_repo_table_is_complete() -> None:
    missing, checked = META.unclassified_labels(ROOT)
    assert checked, "no run-quality labels parsed — parser or run-quality.sh drift"
    assert missing == [], f"run-quality validators with no timing verdict: {missing}"


def test_run_quality_labels_dedupes_in_first_seen_order() -> None:
    text = 'queue_selected "b" foo\nqueue_selected "a" bar\nqueue_selected "b" baz\n'
    assert META.run_quality_labels(text) == ["b", "a"]


def test_classification_region_is_table_only() -> None:
    doc = "# Title\n\nintro mentions ghost-label\n\n## Classification table\n\n| x | y |\nreal-label here\n\n## Next\nafter-label\n"
    region = META.classification_region(doc)
    assert "real-label" in region
    # a label mentioned only in prose BEFORE the table is not "classified"
    assert "ghost-label" not in region
    assert "after-label" not in region


def test_unclassified_label_is_detected(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "docs/conventions").mkdir(parents=True)
    (repo / "scripts/run-quality.sh").write_text(
        'queue_selected "check-classified" foo\nqueue_selected "check-orphan" bar\n', encoding="utf-8"
    )
    (repo / "docs/conventions/validator-timing-layers.md").write_text(
        "## Classification table\n\n| check-classified | broad only | stays | reason |\n", encoding="utf-8"
    )
    missing, checked = META.unclassified_labels(repo)
    assert checked == ["check-classified", "check-orphan"]
    assert missing == ["check-orphan"]


def test_degrades_when_files_absent(tmp_path: Path) -> None:
    missing, checked = META.unclassified_labels(tmp_path)
    assert (missing, checked) == ([], [])
