"""The D47 value-marker counterfactual must be re-runnable, not hand-counted.

D47 recorded "51 of 169 field mentions carry no value marker" and "arming would refuse
5 checked-in reviews" and said plainly that both were measured by hand and that
`measure_inventory_consumption_floor.py` does not produce them. This module pins the
script that does.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "measure_inventory_marker_rule.py"
MEASURE = import_repo_module(SCRIPT, "scripts.measure_inventory_marker_rule")


@pytest.mark.parametrize(
    ("line", "field", "expected"),
    [
        ("- `scope` is repo-wide", "scope", ["backtick"]),
        ("- scope: repo-wide, 105 artifacts", "scope", ["colon"]),
        ("- scope=repo-wide across the corpus", "scope", ["assign"]),
        ("- `scope=repo-wide` this pass", "scope", ["backtick", "assign"]),
        ("Runtime hotspot ranking excludes samples older than 14 days", "ranking", []),
        ("the advisory families were reviewed and accepted this pass", "advisory", []),
        # The round-1 blocker: `[^`]*field[^`]*` matches the GAP BETWEEN two code spans,
        # so this real corpus shape scored as backtick-marked while `advisory` is plain
        # English. The bias ran one way -- it deflated the measured cost.
        (
            "when the `budgets` map is empty a slow label produces one advisory "
            "`HOTSPOT (unbudgeted)` line",
            "advisory",
            [],
        ),
    ],
)
def test_markers_separate_a_citation_from_incidental_prose(line, field, expected):
    """The bare cases are real corpus lines: they clear the residual floor on prose."""
    assert MEASURE.markers_for(line, field) == expected


def _corpus(tmp_path: Path, body: str) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    corpus = repo / "charness-artifacts" / "quality"
    corpus.mkdir(parents=True)
    (corpus / "review.md").write_text(body, encoding="utf-8")
    fields = repo / "fields.json"
    fields.write_text(
        json.dumps({"inventories": {"inventory_demo.py": {"non_headline_fields": ["scope", "ranking"]}}}),
        encoding="utf-8",
    )
    return repo, fields


_CITING = "## Commands Run\n\n- `python3 skills/public/quality/scripts/inventory_demo.py`\n\n"


def test_prose_only_engagement_is_counted_as_refused_by_the_marker_rule(tmp_path):
    repo, fields = _corpus(
        tmp_path,
        _CITING
        + "## Findings\n\n- the scope of this pass was every checked-in skill package\n"
        + "- runtime hotspot ranking excludes samples older than fourteen days\n",
    )

    report = MEASURE.scan(repo, repo / "charness-artifacts" / "quality", fields, recursive=False)

    assert report["field_mentions_carrying_a_value_marker"] == 0
    assert len(report["citations_refused_by_the_marker_rule"]) == 1
    assert report["citations_refused_by_the_marker_rule"][0]["lost_to_the_marker_rule"] == [
        "ranking", "scope",
    ]


def test_marked_engagement_survives_the_marker_rule(tmp_path):
    repo, fields = _corpus(
        tmp_path,
        _CITING
        + "## Findings\n\n- `scope` was every checked-in skill package this pass\n"
        + "- ranking: hotspots sorted by measured wall-clock, not by file size\n",
    )

    report = MEASURE.scan(repo, repo / "charness-artifacts" / "quality", fields, recursive=False)

    assert report["citations_refused_by_the_marker_rule"] == []
    assert report["field_mentions_without_a_marker"] == 0


def test_recursive_reaches_history_which_the_default_glob_cannot_see(tmp_path):
    repo, fields = _corpus(tmp_path, _CITING + "## Findings\n\n- `scope` covered everything\n")
    history = repo / "charness-artifacts" / "quality" / "history"
    history.mkdir()
    (history / "old.md").write_text(
        _CITING
        + "## Findings\n\n- the scope of that pass was narrower than this one\n"
        + "- runtime hotspot ranking excludes samples older than fourteen days\n",
        encoding="utf-8",
    )
    corpus = repo / "charness-artifacts" / "quality"

    shallow = MEASURE.scan(repo, corpus, fields, recursive=False)
    deep = MEASURE.scan(repo, corpus, fields, recursive=True)

    assert shallow["artifacts_scanned"] == 1
    assert deep["artifacts_scanned"] == 2
    assert deep["citations_refused_by_the_marker_rule"]
    assert not shallow["citations_refused_by_the_marker_rule"]


def test_an_empty_corpus_exits_2_rather_than_reporting_a_clean_measurement(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(tmp_path), "--corpus", str(empty)],
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 2
    assert "not a measurement" in result.stderr


PROBE = REPO_ROOT / "charness-artifacts" / "probe" / "2026-08-01-inventory-marker-rule.json"


def test_the_recorded_probe_still_matches_todays_tree():
    """D47 now cites these numbers, so they must not drift silently.

    The first version of this test asserted only `total == marked + unmarked`, which is
    how `unmarked` is COMPUTED -- it could not fail for any implementation, including a
    marker test stubbed to always-true. Pinning the recorded probe is what the sibling
    measurement already does, and it is what forces D47 to be updated when the corpus or
    the rule moves.
    """
    recorded = json.loads(PROBE.read_text(encoding="utf-8"))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(REPO_ROOT), "--json"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    live = json.loads(result.stdout)

    for key in (
        "artifacts_scanned",
        "field_mentions_presence_only",
        "field_mentions_clearing_todays_floor",
        "field_mentions_carrying_a_value_marker",
        "field_mentions_without_a_marker",
        "marker_kinds",
        "artifacts_refused_by_the_marker_rule",
        "artifacts_citing_a_declared_inventory",
    ):
        assert live[key] == recorded[key], (
            f"{key} drifted from the recorded probe; update D47 and the probe together"
        )
    # D47's headline figure is the CITATION count, not the artifact list, and pinning only
    # the list would let a merge or split of two citations inside one artifact go green
    # while the entry's stated number went stale.
    assert len(live["citations_refused_by_the_marker_rule"]) == len(
        recorded["citations_refused_by_the_marker_rule"]
    )


def test_the_recursive_variant_recorded_in_the_probe_is_reproducible():
    """D47 publishes the recursive numbers too; an unrecorded number reads as proven."""
    recorded = json.loads(PROBE.read_text(encoding="utf-8"))["_provenance"]["recursive_variant"]
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(REPO_ROOT), "--recursive", "--json"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    live = json.loads(result.stdout)

    for key, expected in recorded.items():
        if key == "refused_citation_count":
            assert len(live["citations_refused_by_the_marker_rule"]) == expected
        else:
            assert live[key] == expected, f"{key} drifted from the recorded recursive run"


def test_the_presence_only_count_reproduces_the_denominator_d47_cited():
    """169 was NOT a hand count -- the sibling script produced it as its loose-mention
    total, and D47's 51-of-169 used that population. Reproducing it here is what makes
    the marker numbers comparable on one denominator instead of across two."""
    sibling_probe = json.loads(
        (REPO_ROOT / "charness-artifacts" / "probe" / "2026-08-01-inventory-consumption-floor.json")
        .read_text(encoding="utf-8")
    )
    recorded = json.loads(PROBE.read_text(encoding="utf-8"))

    assert recorded["field_mentions_presence_only"] == (
        sibling_probe["field_mention_residuals"]["count"]
    )
