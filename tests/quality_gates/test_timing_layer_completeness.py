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


def test_a_label_mentioned_only_in_another_rows_prose_is_not_classified() -> None:
    """Substring containment over the whole table region made a label classified AT
    BIRTH if its name appeared inside another row's prose.

    `check-links`, `check-doc`, `validate-cautilus` and `validate-skill` all read as
    present that way, so `queue_selected "check-links"` would have been waved through
    and the shift-left recurrence class (#314/#319/#332/#366/#368) would pass silently.
    A `\\b` word boundary does not fix it either: `-` is a non-word character, so
    `\\bcheck-links\\b` still matches inside `check-links-internal`.
    """
    region = META.classification_region(
        (ROOT / "docs" / "conventions" / "validator-timing-layers.md").read_text(encoding="utf-8")
    )
    classified = META.classified_labels(region)

    for prose_only in ("check-links", "check-doc", "validate-cautilus", "validate-skill"):
        assert prose_only not in classified, prose_only
        assert prose_only in region, f"{prose_only} must still be a substring, or this test is vacuous"

    # real rows still resolve, including the one the substring test would alias onto
    for real in ("check-links-internal", "pytest", "dup-ratchet"):
        assert real in classified, real


def test_a_docs_only_push_label_that_names_no_gate_is_refused(tmp_path: Path) -> None:
    """Not a late verdict — a verdict that never arrives.

    `label_is_selected` compares exact names, so a renamed or retired label leaves the
    hook naming something nothing matches: `queue_selected` quietly queues nothing and
    the docs-only push reports a clean pass having run one fewer gate than it claims.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    (repo / "docs" / "conventions").mkdir(parents=True)
    (repo / "scripts" / "run-quality.sh").write_text(
        'queue_selected "check-doc-links" x\nqueue_selected "check-markdown" y\n', encoding="utf-8"
    )
    (repo / "docs" / "conventions" / "validator-timing-layers.md").write_text(
        "## Classification table\n\n| Check | Ran | Verdict | Reason |\n| --- | --- | --- | --- |\n"
        "| check-doc-links, check-markdown | broad | already earlier | x |\n",
        encoding="utf-8",
    )

    (repo / ".githooks" / "pre-push").write_text(
        'DOCS_ONLY_LABELS="check-doc-links,check-markdown"\n', encoding="utf-8"
    )
    assert META.stale_docs_only_labels(repo) == []

    (repo / ".githooks" / "pre-push").write_text(
        'DOCS_ONLY_LABELS="check-doc-links,check-markdownn"\n', encoding="utf-8"
    )
    assert META.stale_docs_only_labels(repo) == ["check-markdownn"]

    # Subset direction ONLY: a run-quality label absent from the curated docs-only set
    # is a deliberate judgment, not drift, so completeness here would be a false refusal.
    (repo / ".githooks" / "pre-push").write_text('DOCS_ONLY_LABELS="check-doc-links"\n', encoding="utf-8")
    assert META.stale_docs_only_labels(repo) == []

    # Degrades where the hook is not vendored.
    (repo / ".githooks" / "pre-push").unlink()
    assert META.stale_docs_only_labels(repo) == []
