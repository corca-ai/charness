"""The D47 value-marker counterfactual is hash-bound evidence, not a live corpus pin.

D47 recorded "51 of 169 field mentions carry no value marker" and "arming would refuse
5 checked-in reviews" and said plainly that both were measured by hand and that
`measure_inventory_consumption_floor.py` does not produce them. This module verifies the
dated snapshot's hash, provenance, rendered headlines, and measurement invariants without
recomputing a later corpus.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.script_main import load_script_module, run_loaded_script_main

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "gates" / "measure_inventory_marker_rule.py"
MEASURE = load_script_module("scripts.gates.measure_inventory_marker_rule", SCRIPT)


def run_measure(*args: str):
    return run_loaded_script_main("measure_inventory_marker_rule.py", MEASURE, *args)


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

    result = run_measure("--repo-root", str(tmp_path), "--corpus", str(empty))

    assert result.returncode == 2
    assert "not a measurement" in result.stderr


PROBE = REPO_ROOT / "charness-artifacts" / "probe" / "2026-08-12-inventory-marker-rule-snapshot.json"
PROBE_SHA256 = "ac63f8a54a558217cebde320f02d4915d10e6bab538c3df22ff6e1397083f62d"
DECISION_RECORD = REPO_ROOT / "docs" / "deferred-decisions.md"
HEADLINE_PATTERN = re.compile(
    r"dated: \*\*(?P<presence>\d+)\*\* presence-only field mentions; "
    r"\*\*(?P<clearing>\d+)\*\* clear the then-current residual\n"
    r"  floor; \*\*(?P<marked>\d+)\*\* carry a value marker; and \*\*(?P<unmarked>\d+)\*\* do not\."
)


def _assert_measurement_invariants(measurement: dict[str, object]) -> None:
    """Validate what a dated D47 snapshot means without pinning a live corpus."""
    clearing = measurement["field_mentions_clearing_todays_floor"]
    marked = measurement["field_mentions_carrying_a_value_marker"]
    unmarked = measurement["field_mentions_without_a_marker"]
    refused_artifacts = measurement["artifacts_refused_by_the_marker_rule"]
    refused_citations = measurement["citations_refused_by_the_marker_rule"]

    assert isinstance(clearing, int)
    assert isinstance(marked, int)
    assert isinstance(unmarked, int)
    assert clearing == marked + unmarked
    assert measurement["field_mentions_presence_only"] >= clearing
    assert measurement["artifacts_scanned"] >= measurement["artifacts_citing_a_declared_inventory"]
    assert set(refused_artifacts) == {citation["path"] for citation in refused_citations}
    assert all(count >= 0 for count in measurement["marker_kinds"].values())


def test_d47_uses_a_hash_bound_dated_measurement_snapshot():
    """The snapshot stays immutable; ordinary quality-corpus growth is not test drift."""
    snapshot_bytes = PROBE.read_bytes()
    snapshot = json.loads(snapshot_bytes)

    assert hashlib.sha256(snapshot_bytes).hexdigest() == PROBE_SHA256
    assert snapshot["schema_version"] == "charness.inventory_marker_rule_snapshot.v1"
    assert snapshot["captured_at"] == "2026-08-12"
    assert "immutable historical evidence" in snapshot["scope"]
    assert snapshot["measurement_command"] == (
        "python3 scripts/gates/measure_inventory_marker_rule.py --repo-root . --json"
    )
    assert snapshot["recursive_measurement_command"] == (
        "python3 scripts/gates/measure_inventory_marker_rule.py --repo-root . --recursive --json"
    )
    source_commit = snapshot["source_commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", source_commit)
    assert subprocess.run(
        ["git", "cat-file", "-e", f"{source_commit}^{{commit}}"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    ).returncode == 0
    decision = DECISION_RECORD.read_text(encoding="utf-8")
    assert "2026-08-12-inventory-marker-rule-snapshot.json" in decision
    assert PROBE_SHA256 in decision
    headline = HEADLINE_PATTERN.search(decision)
    assert headline is not None
    assert {name: int(value) for name, value in headline.groupdict().items()} == {
        "presence": snapshot["shallow"]["field_mentions_presence_only"],
        "clearing": snapshot["shallow"]["field_mentions_clearing_todays_floor"],
        "marked": snapshot["shallow"]["field_mentions_carrying_a_value_marker"],
        "unmarked": snapshot["shallow"]["field_mentions_without_a_marker"],
    }


def test_the_d47_snapshot_payload_obeys_its_measurement_invariants():
    snapshot = json.loads(PROBE.read_text(encoding="utf-8"))
    shallow = snapshot["shallow"]
    recursive = snapshot["recursive"]

    _assert_measurement_invariants(shallow)
    _assert_measurement_invariants(recursive)
    assert recursive["artifacts_scanned"] >= shallow["artifacts_scanned"]
    assert set(shallow["artifacts_refused_by_the_marker_rule"]).issubset(
        recursive["artifacts_refused_by_the_marker_rule"]
    )


def test_the_emitted_payload_names_every_refused_artifact(tmp_path):
    """The refused artifacts must be NAMED, not just counted.

    The retired human summary printed one line per refused artifact under a count.
    Output is unconditionally YAML now, so the same duty falls on the payload: a
    count alone would tell an operator how much was refused and never which file
    to open. `artifacts_refused_by_the_marker_rule` carries the names and
    `artifacts_refused_count` the tally the summary computed inline.
    """
    repo, fields = _corpus(
        tmp_path,
        _CITING
        + "## Findings\n\n- the scope of this pass was every checked-in skill package\n"
        + "- runtime hotspot ranking excludes samples older than fourteen days\n",
    )
    result = run_measure(
        "--repo-root",
        str(repo),
        "--corpus",
        str(repo / "charness-artifacts" / "quality"),
        "--consumer-fields-path",
        str(fields),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["scope"] == "top level only"
    assert payload["field_mentions_clearing_todays_floor"] == 2
    assert payload["field_mentions_without_a_marker"] == 2
    assert payload["citations_refused_count"] == 1
    assert payload["artifacts_refused_count"] == 1
    assert payload["artifacts_refused_by_the_marker_rule"] == ["charness-artifacts/quality/review.md"]


def test_the_recursive_run_says_so_in_its_scope_field(tmp_path):
    """The scope word survived the render's deletion: `recursive` vs `top level only`.

    Without it a reader cannot tell a clean shallow pass from a clean deep one,
    and `recursive: true` alone is a flag the retired summary spelled out.
    """
    repo, fields = _corpus(tmp_path, _CITING + "## Findings\n\n- `scope` covered everything\n")
    result = run_measure(
        "--repo-root",
        str(repo),
        "--corpus",
        str(repo / "charness-artifacts" / "quality"),
        "--consumer-fields-path",
        str(fields),
        "--recursive",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["scope"] == "recursive"
    assert payload["recursive"] is True


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


def test_main_emits_in_process_so_the_emit_path_is_measurable(tmp_path, monkeypatch, capsys):
    """Driven through `main()` rather than a subprocess.

    The subprocess tests above prove the CLI contract, but in-process coverage cannot
    see them, so the emit path (the counts `main` folds in around `scan`) read as
    uncovered to the changed-line gate.
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
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["scope"] == "top level only"
    assert payload["citations_refused_count"] == 1
    assert payload["artifacts_refused_count"] == 1
    assert payload["artifacts_refused_by_the_marker_rule"] == ["charness-artifacts/quality/review.md"]


def test_main_emits_exactly_one_payload_document_and_nothing_else(tmp_path, monkeypatch, capsys):
    """What is left of the old json-mode test after the output modes collapsed.

    There is no longer a mode that skips a render, so the original premise (early
    return past the human summary) is gone. The surviving, still-distinct fact is
    that a successful run puts exactly ONE parseable document on stdout and no
    prose beside it -- the property that lets any caller pipe this straight into a
    parser.
    """
    repo, fields = _corpus(tmp_path, _CITING + "## Findings\n\n- `scope` covered everything\n")
    monkeypatch.setattr(sys, "argv", [
        "measure_inventory_marker_rule.py", "--repo-root", str(repo),
        "--corpus", str(repo / "charness-artifacts" / "quality"),
        "--consumer-fields-path", str(fields),
    ])

    assert MEASURE.main() == 0
    captured = capsys.readouterr()
    documents = list(yaml.safe_load_all(captured.out))
    assert len(documents) == 1, captured.out
    assert documents[0]["artifacts_scanned"] == 1
    assert captured.err == ""


def test_main_refuses_an_empty_corpus_in_process(tmp_path, monkeypatch, capsys):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(sys, "argv", [
        "measure_inventory_marker_rule.py", "--repo-root", str(tmp_path),
        "--corpus", str(empty),
    ])

    assert MEASURE.main() == 2
    assert "not a measurement" in capsys.readouterr().err
