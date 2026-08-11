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
from tests.probe_drift_support import MARKER_PROBE, probe_drift_message

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

    # `probe_field`, not `key`: see the note on the recursive loop below — the secret scanner's
    # generic-api-key rule matches the literal text `key, `, and both call sites had that shape.
    for probe_field in (
        "artifacts_scanned",
        "field_mentions_presence_only",
        "field_mentions_clearing_todays_floor",
        "field_mentions_carrying_a_value_marker",
        "field_mentions_without_a_marker",
        "marker_kinds",
        "artifacts_refused_by_the_marker_rule",
        "artifacts_citing_a_declared_inventory",
    ):
        assert live[probe_field] == recorded[probe_field], probe_drift_message(
            probe_field, probe=MARKER_PROBE
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

    # `probe_field`, not `key`: the secret scanner's generic-api-key rule matches the literal
    # text `key, ` and my first version of these call sites put a variable named `key` right
    # before a comma, so the repo's own secret gate flagged a test as a leak. Renaming is the
    # fix rather than an allowlist entry, which would have weakened a real scanner to accommodate
    # a variable name.
    for probe_field, expected in recorded.items():
        assert live[probe_field] == expected, probe_drift_message(
            probe_field, probe=MARKER_PROBE, variant="recursive variant"
        )


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


def test_the_human_render_names_every_refused_artifact(tmp_path):
    """The default (non-`--json`) output is what an operator actually reads."""
    repo, fields = _corpus(
        tmp_path,
        _CITING
        + "## Findings\n\n- the scope of this pass was every checked-in skill package\n"
        + "- runtime hotspot ranking excludes samples older than fourteen days\n",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo),
         "--corpus", str(repo / "charness-artifacts" / "quality"),
         "--consumer-fields-path", str(fields)],
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "top level only" in out
    assert "field mentions clearing today's floor: 2" in out
    assert "without a marker: 2" in out
    assert "citations a marker rule would refuse: 1 across 1 artifact(s)" in out
    assert "- charness-artifacts/quality/review.md" in out


def test_the_recursive_render_says_so_in_its_scope_line(tmp_path):
    repo, fields = _corpus(tmp_path, _CITING + "## Findings\n\n- `scope` covered everything\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo),
         "--corpus", str(repo / "charness-artifacts" / "quality"),
         "--consumer-fields-path", str(fields), "--recursive"],
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "(recursive)" in result.stdout


def test_a_corroborated_pre_contract_citation_is_skipped_and_named(tmp_path, monkeypatch):
    """The gate exits 0 on it without running a floor, so counting it would report a
    cost on an artifact the gate never judges. Measured-zero in this repo, so the
    branch is driven here rather than left to a corpus that happens not to have one."""
    repo, fields = _corpus(
        tmp_path,
        _CITING + "## Findings\n\n- the scope of this pass covered everything at the time\n",
    )
    monkeypatch.setattr(MEASURE.corpus_lib, "exemption_state", lambda *a, **k: "corroborated")

    report = MEASURE.scan(repo, repo / "charness-artifacts" / "quality", fields, recursive=False)

    assert report["pre_contract_citations_skipped"] == ["charness-artifacts/quality/review.md"]
    assert report["citations_refused_by_the_marker_rule"] == []
    assert report["field_mentions_clearing_todays_floor"] == 0


def test_main_renders_in_process_so_the_render_path_is_measurable(tmp_path, monkeypatch, capsys):
    """Driven through `main()` rather than a subprocess.

    The subprocess tests above prove the CLI contract, but in-process coverage cannot
    see them, so the human-render path read as uncovered to the changed-line gate.
    """
    repo, fields = _corpus(
        tmp_path,
        _CITING
        + "## Findings\n\n- the scope of this pass was every checked-in skill package\n"
        + "- runtime hotspot ranking excludes samples older than fourteen days\n",
    )
    monkeypatch.setattr(sys, "argv", [
        "measure_inventory_marker_rule.py", "--repo-root", str(repo),
        "--corpus", str(repo / "charness-artifacts" / "quality"),
        "--consumer-fields-path", str(fields),
    ])

    assert MEASURE.main() == 0
    out = capsys.readouterr().out
    assert "top level only" in out
    assert "citations a marker rule would refuse: 1 across 1 artifact(s)" in out
    assert "- charness-artifacts/quality/review.md" in out


def test_main_json_mode_returns_early_without_the_render(tmp_path, monkeypatch, capsys):
    repo, fields = _corpus(tmp_path, _CITING + "## Findings\n\n- `scope` covered everything\n")
    monkeypatch.setattr(sys, "argv", [
        "measure_inventory_marker_rule.py", "--repo-root", str(repo),
        "--corpus", str(repo / "charness-artifacts" / "quality"),
        "--consumer-fields-path", str(fields), "--json",
    ])

    assert MEASURE.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["artifacts_scanned"] == 1


def test_main_refuses_an_empty_corpus_in_process(tmp_path, monkeypatch, capsys):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(sys, "argv", [
        "measure_inventory_marker_rule.py", "--repo-root", str(tmp_path),
        "--corpus", str(empty),
    ])

    assert MEASURE.main() == 2
    assert "not a measurement" in capsys.readouterr().err
