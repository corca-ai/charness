"""Tests for the #368 timing-layer completeness meta-gate.

The live guard (`test_real_repo_table_is_complete`) is the load-bearing one: it
proves every gate `run-quality.sh` runs carries a verdict in the classification
table, so the shift-left class cannot recur via an unclassified broad-only check.
The negative guard proves an unclassified label turns the gate red.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

from .support import ROOT

META = importlib.import_module("tools.check_timing_layer_completeness")


def test_real_repo_table_is_complete() -> None:
    missing, checked = META.unclassified_labels(ROOT)
    assert checked, "no run-quality labels parsed — parser or run-quality.sh drift"
    assert missing == [], f"run-quality validators with no timing verdict: {missing}"


def test_quality_core_runs_the_timing_completeness_gate_but_docs_pre_push_does_not() -> None:
    """Ruling 3 closes the hook-bypass gap in CI without widening the fast hook."""
    workflow = (ROOT / ".github" / "workflows" / "quality-core.yml").read_text(encoding="utf-8")
    pre_push = (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")

    assert re.search(
        r"^\s*- name: Validate timing-layer completeness\n"
        r"\s+run: python3 -m tools\.check_timing_layer_completeness --repo-root \.$",
        workflow,
        re.MULTILINE,
    )
    assert "--print-docs-only-labels" in pre_push
    assert '--gates "$REPO_ROOT/.agents/quality-gates.yaml"' in pre_push
    assert not re.search(r'^DOCS_ONLY_LABELS="[^"]*"$', pre_push, re.MULTILINE)


def test_run_quality_labels_dedupes_in_first_seen_order() -> None:
    text = 'queue_selected "b" foo\nqueue_selected "a" bar\nqueue_selected "b" baz\n'
    assert META.run_quality_labels(text) == ["b", "a"]


def test_declared_rows_replace_shell_text_for_timing_completeness(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / ".agents").mkdir()
    (repo / "scripts" / "run-quality.sh").write_text(
        'queue_selected "shell-only" foo\n', encoding="utf-8"
    )
    (repo / ".agents" / "quality-gates.yaml").write_text(
        "schema: charness/quality-gates/v1\n"
        "phases:\n"
        "  - id: main\n"
        "    isolation: concurrent\n"
        "    fail_fast: false\n"
        "    gates:\n"
        "      - label: declared-only\n"
        "        command:\n"
        "          - python3\n"
        "          - gate.py\n"
        "        lane: standard\n",
        encoding="utf-8",
    )
    (repo / "docs" / "validator-timing-layers.md").write_text(
        "## Classification table\n\n| Check | Ran | Verdict | Reason |\n"
        "| --- | --- | --- | --- |\n"
        "| declared-only | broad | stays | x |\n",
        encoding="utf-8",
    )
    (repo / ".githooks").mkdir()
    (repo / ".githooks" / "pre-push").write_text(
        'DOCS_ONLY_LABELS="shell-only"\n', encoding="utf-8"
    )

    missing, checked = META.unclassified_labels(repo)
    assert checked == ["declared-only"]
    assert missing == []
    assert META.stale_docs_only_labels(repo) == []


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
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts/run-quality.sh").write_text(
        'queue_selected "check-classified" foo\nqueue_selected "check-orphan" bar\n',
        encoding="utf-8",
    )
    (repo / "docs/validator-timing-layers.md").write_text(
        "## Classification table\n\n| check-classified | broad only | stays | reason |\n",
        encoding="utf-8",
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

    `check-links`, `check-doc`, `validate-surface` and `validate-skill` all read as
    present that way, so `queue_selected "check-links"` would have been waved through
    and the shift-left recurrence class (#314/#319/#332/#366/#368) would pass silently.
    A `\\b` word boundary does not fix it either: `-` is a non-word character, so
    `\\bcheck-links\\b` still matches inside `check-links-internal`.
    """
    region = META.classification_region(
        (ROOT / "docs" / "validator-timing-layers.md").read_text(encoding="utf-8")
    )
    classified = META.classified_labels(region)

    for prose_only in ("check-links", "check-doc", "validate-surface", "validate-skill"):
        assert prose_only not in classified, prose_only
        assert prose_only in region, (
            f"{prose_only} must still be a substring, or this test is vacuous"
        )

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
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts" / "run-quality.sh").write_text(
        'queue_selected "check-doc-links" x\nqueue_selected "check-markdown" y\n', encoding="utf-8"
    )
    (repo / "docs" / "validator-timing-layers.md").write_text(
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
    (repo / ".githooks" / "pre-push").write_text(
        'DOCS_ONLY_LABELS="check-doc-links"\n', encoding="utf-8"
    )
    assert META.stale_docs_only_labels(repo) == []

    # Degrades where the hook is not vendored.
    (repo / ".githooks" / "pre-push").unlink()
    assert META.stale_docs_only_labels(repo) == []


def _seed(tmp_path: Path, docs_only_line: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts" / "run-quality.sh").write_text(
        'queue_selected "check-doc-links" x\n', encoding="utf-8"
    )
    (repo / "docs" / "validator-timing-layers.md").write_text(
        "## Classification table\n\n| Check | Ran | Verdict | Reason |\n| --- | --- | --- | --- |\n"
        "| check-doc-links | broad | already earlier | x |\n",
        encoding="utf-8",
    )
    body = "#!/usr/bin/env bash\n" + (f"{docs_only_line}\n" if docs_only_line else "")
    (repo / ".githooks" / "pre-push").write_text(body, encoding="utf-8")
    return repo


def test_a_pre_push_without_the_docs_only_assignment_is_not_a_finding(tmp_path: Path) -> None:
    """A consumer repo can vendor the hook without the docs-only subset at all. No
    assignment is nothing to bind, never a stale label."""
    assert META.stale_docs_only_labels(_seed(tmp_path, None)) == []


def test_main_reports_the_stale_label_and_exits_nonzero(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The reporting branch is what the operator actually reads; asserting only the
    helper leaves the message that names the fix unproven."""
    repo = _seed(tmp_path, 'DOCS_ONLY_LABELS="check-doc-links,check-gone"')
    monkeypatch.setattr(
        sys, "argv", ["check_timing_layer_completeness.py", "--repo-root", str(repo)]
    )

    assert META.main() == 1

    err = capsys.readouterr().err
    assert "check-gone" in err
    assert "silently runs fewer checks than it claims" in err
    assert "Rename or drop each" in err


def test_main_is_silent_when_the_subset_matches(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = _seed(tmp_path, 'DOCS_ONLY_LABELS="check-doc-links"')
    monkeypatch.setattr(
        sys, "argv", ["check_timing_layer_completeness.py", "--repo-root", str(repo)]
    )

    assert META.main() == 0
    assert "carry a timing verdict" in capsys.readouterr().out


def test_labels_reach_the_table_through_every_queue_wrapper(tmp_path: Path) -> None:
    """The widening this gate got on 2026-08-10, pinned.

    Its reader saw only `queue_selected` for as long as it existed, so three opt-in
    gates queued through `queue_timed` / `queue_agent_browser_runtime_gate` were
    never required to carry a timing verdict -- an exhaustiveness gate that was not
    exhaustive. A stub runner is used rather than the real one so this stays true
    if those particular gates are retired.
    """
    text = (
        'queue_selected "via-selected" foo\n'
        'queue_timed "via-timed" bar\n'
        'queue_agent_browser_runtime_gate "via-browser-gate" baz\n'
    )
    assert META.run_quality_labels(text) == [
        "via-selected",
        "via-timed",
        "via-browser-gate",
    ]


def test_dispatcher_forwarding_is_not_read_as_a_gate_label(tmp_path: Path) -> None:
    """`queue_selected` forwards `queue_timed "$label"`; reading that as a label
    would put the literal string `$label` in the table's required set, which no
    row can ever satisfy -- a permanent red on a correct table."""
    text = 'queue_selected() {\n  queue_timed "$label" "$@"\n}\nqueue_selected "real-gate" foo\n'
    assert META.run_quality_labels(text) == ["real-gate"]


def test_an_unresolvable_queue_line_is_a_named_refusal_not_a_traceback(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """This gate is classified commit-time. The shared reader raises by design, so
    an uncaught exception here surfaces as a Python traceback inside the pre-commit
    hook, from a gate whose subject is the timing table."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts" / "run-quality.sh").write_text(
        'queue_selected "$computed" foo\n', encoding="utf-8"
    )
    (repo / "docs" / "validator-timing-layers.md").write_text(
        "## Classification table\n\n| a | b |\n", encoding="utf-8"
    )
    monkeypatch.setattr(sys, "argv", ["prog", "--repo-root", str(repo)])
    assert META.main() == 1
    captured = capsys.readouterr()
    assert "non-literal label" in captured.err
    assert "Traceback" not in captured.err
