"""The docs-graph gate is a PROOF SURFACE, so these tests exist to prove it can
report the things it exists to report -- especially the ones that are silent by
construction.

The failure this gate is built against: `check_doc_links.py` was green while
seven pages were unreachable, because it answers a different question. The
failure THIS gate could introduce is the same shape one level up -- passing when
it observed nothing at all. So the not-run paths get more coverage than the
happy path.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
GATE = "scripts/check_docs_graph.py"
_gate = import_repo_module(__file__, "scripts.check_docs_graph")
_RUN_QUALITY_SCRIPT = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")

# CAPTURED from awiki 0.5.0, not hand-written. The passing line is the one that
# matters: it OMITS `orphans`/`islands` entirely, which is what forced the
# absence-as-zero branch to exist, and a fixture invented from the author's
# belief would have proven that branch against the belief rather than the tool.
FIXTURES = ROOT / "tests" / "fixtures"
_CLEAN_OUTPUT = (FIXTURES / "awiki-0.5.0-connected-graph.stdout.txt").read_text(encoding="utf-8")
_EMPTY_ROOT_OUTPUT = (FIXTURES / "awiki-0.5.0-empty-root.stdout.txt").read_text(encoding="utf-8")
_ISLAND_OUTPUT = (FIXTURES / "awiki-0.5.0-island.stdout.txt").read_text(encoding="utf-8")
# `link_only_lines` sits UNDER the bar here on purpose: this fixture is about
# orphans, and a value over the bar would make every assertion on it depend on a
# second failing metric.
_ORPHAN_OUTPUT = (
    "// lint_failed documents=43 orphans=2 islands=0 link_only_lines=12 "
    "largest_component_ratio=0.9767 orphan_rate=0.0233 content_coverage=1.0000\n"
    "// orphan\n"
    "// why: no resolved links connect these pages to the wiki graph.\n"
    "// fix: add a contextual link to or from a related page.\n"
    "// example: add \"Compare with [[Related page]] ...\" from the orphan.\n"
    "[[agent-task-envelope]]: `charness task` provides a small repo-local contract\n"
    "[[proof-semantics-adapter]]: The portable Charness residual ledger\n"
    "// link_only_line\n"
    "// why: a line with only one link gives no local context.\n"
    "[[artifact-policy]]:23: - [deferred-decisions.md](./deferred-decisions.md)\n"
)


def _patch_awiki(
    monkeypatch: pytest.MonkeyPatch, output: str, *, present: bool = True, returncode: int = 1
) -> None:
    monkeypatch.setattr(_gate.shutil, "which", lambda _name: "/usr/bin/awiki" if present else None)
    monkeypatch.setattr(_gate, "_run_awiki", lambda _repo_root, _scan_root: (returncode, output))


def test_a_connected_graph_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    # The captured `ok` line omits `orphans`/`islands`, so a gate that required
    # them present would report UNPROVEN forever on a healthy repo.
    assert "orphans=" not in _CLEAN_OUTPUT, "the captured passing line is expected to omit the counts"
    _patch_awiki(monkeypatch, _CLEAN_OUTPUT, returncode=0)
    result = _gate.evaluate(ROOT)
    assert result["status"] == "pass"


def test_an_empty_scan_root_is_not_run_rather_than_a_vacuous_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    # CAPTURED: an empty root prints `ok ... documents=0 orphan_rate=0.0000` and
    # EXITS 0. An empty graph is trivially connected, so every ratio reads clean.
    # Without the documents floor, a consuming repo whose docs live elsewhere gets
    # a clean docs verdict over a graph that was never read.
    _patch_awiki(monkeypatch, _EMPTY_ROOT_OUTPUT, returncode=0)
    result = _gate.evaluate(ROOT)

    assert result["status"] == "not-run"
    assert "no graph to judge" in result["reason"]


def test_a_zero_document_scan_with_explicit_counts_is_still_not_run(monkeypatch: pytest.MonkeyPatch) -> None:
    # The case the documents floor uniquely catches. With explicit `orphans=0
    # islands=0` the run skips the missing-metrics branch entirely and would
    # compute `failures={}` -> pass, so the floor has to run FIRST. The captured
    # empty-root fixture cannot prove this: its ratios already fail corroboration.
    _patch_awiki(
        monkeypatch,
        "// ok connected_graph documents=0 orphans=0 islands=0 "
        "largest_component_ratio=1.0000 orphan_rate=0.0000\n",
        returncode=0,
    )
    result = _gate.evaluate(ROOT)

    assert result["status"] == "not-run"
    assert "no graph to judge" in result["reason"]


def test_an_unexpected_awiki_exit_code_is_not_run(monkeypatch: pytest.MonkeyPatch) -> None:
    # 0 and 1 are the codes awiki uses for clean and findings. Anything else means
    # it did not finish scanning, so a summary it printed on the way out describes
    # a graph it did not finish reading -- even if that summary looks clean.
    _patch_awiki(monkeypatch, _CLEAN_OUTPUT, returncode=2)
    result = _gate.evaluate(ROOT)

    assert result["status"] == "not-run"
    assert "did not complete a scan" in result["reason"]


def test_a_crash_reports_not_run_rather_than_failing_the_docs_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    # An uncaught exception exits 1, which the runner renders as FAIL -- the gate
    # asserting a broken docs graph on a run where it observed nothing.
    def _boom(_repo_root, _scan_root):
        raise OSError("awiki is not executable")

    monkeypatch.setattr(_gate.shutil, "which", lambda _name: "/usr/bin/awiki")
    monkeypatch.setattr(_gate, "_run_awiki", _boom)
    result = _gate.evaluate(ROOT)

    assert result["status"] == "not-run"
    assert "OSError" in result["reason"]
    assert "not a clean docs verdict" in result["reason"]


def test_an_unreadable_metric_value_is_not_run(monkeypatch: pytest.MonkeyPatch) -> None:
    # `[0-9.]+` matches strings float() rejects. Uncaught, that is a FAIL verdict
    # on an unobserved graph.
    _patch_awiki(monkeypatch, "// ok connected_graph documents=1.2.3 orphan_rate=0.0000\n")
    result = _gate.evaluate(ROOT)
    assert result["status"] == "not-run"


def test_orphans_fail_and_the_pages_are_named(monkeypatch: pytest.MonkeyPatch) -> None:
    # Naming the pages is the whole operator value of a failure. An earlier
    # version of the block parser treated awiki's `// why:` annotation as the end
    # of the orphan block, so it reported `orphans=2` and named nothing.
    _patch_awiki(monkeypatch, _ORPHAN_OUTPUT)
    result = _gate.evaluate(ROOT)

    assert result["status"] == "fail"
    assert result["failures"] == {"orphans": 2}
    assert result["named"]["orphans"] == ["agent-task-envelope", "proof-semantics-adapter"]
    # The link-only block that follows must not leak into the orphan list.
    assert "artifact-policy" not in result["named"]["orphans"]


def test_an_unknown_block_annotation_does_not_silence_the_page_names() -> None:
    # The earlier parser keyed on a literal list of awiki's three annotations, so
    # a new one upstream would end the block early and report a count naming
    # nothing -- reintroducing the exact bug the list was added to fix.
    output = (
        "// lint_failed documents=9 orphans=1 islands=0\n"
        "// orphan\n"
        "// why: unreachable.\n"
        "// note: an annotation this gate has never seen before.\n"
        "[[still-named]]: the excerpt\n"
    )
    assert _gate.named_pages(output, "orphan") == ["still-named"]


def test_islands_fail_even_with_zero_orphans(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_awiki(
        monkeypatch,
        "// lint_failed documents=5 orphans=0 islands=1 link_only_lines=0 "
        "largest_component_ratio=0.6000 orphan_rate=0.0000 content_coverage=0.8000\n",
    )
    result = _gate.evaluate(ROOT)
    assert result["status"] == "fail"
    assert result["failures"] == {"islands": 1}


# RETRACTED: `test_link_only_lines_alone_do_not_fail_the_gate` stood here, pinning
# "awiki exits 1 on link-only lines, and this gate does not gate on them" as a
# deliberate scope decision so it could not be widened by accident. It is widened
# ON PURPOSE now, and the pin is retracted rather than deleted quietly, because a
# decision reversed without a record reads as an oversight to the next reader.
#
# What changed: the scope decision was made when adopting the rule meant adopting
# awiki's exit code wholesale, which bundles every rule it has and cannot be
# selected down. Gating a NAMED metric against a declared bar is a different
# instrument -- it adopts the count without adopting the exit code, and it can sit
# above 0 where the rule over-reports. What did NOT change is the measurement the
# pin rested on: most link-only lines here are hard-wrapped prose, a reflow sweep
# is still not the remedy, and the bar's residual is exactly that population.
def test_link_only_lines_above_the_bar_fail_the_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    over = _gate.LINK_ONLY_LINES_BAR + 1
    _patch_awiki(
        monkeypatch,
        f"// lint_failed documents=42 orphans=0 islands=0 link_only_lines={over} "
        "largest_component_ratio=1.0000 orphan_rate=0.0000 content_coverage=1.0000\n"
        "// link_only_line\n"
        "// why: a line with only one link gives no local context.\n"
        "[[artifact-policy]]:23: - [deferred-decisions.md](./deferred-decisions.md)\n",
    )
    result = _gate.evaluate(ROOT)
    payload = _gate.report(result)

    # A RENDERED verdict, which is the half that was silent by construction: a
    # metric added to the gated set without its block header reports NOT-RUN
    # instead, and NOT-RUN is not a failure an operator acts on.
    assert result["status"] == "fail"
    assert result["failures"] == {"link_only_lines": over}
    assert result["named"]["link_only_lines"] == ["artifact-policy"]
    assert payload["failure_label"]["link_only_lines"] == "context-free on"
    # The remedy must refuse the cheapest wrong move, which is re-baselining.
    assert "only decreases" in payload["remedies"]["link_only_lines"]


def test_link_only_lines_at_the_bar_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    # The bar is a ceiling, not a target: AT it is clean. Written because `> 0`
    # was the previous failure computation, and `>= bar` would refuse the very
    # tree that set the bar.
    _patch_awiki(
        monkeypatch,
        f"// lint_failed documents=42 orphans=0 islands=0 link_only_lines={_gate.LINK_ONLY_LINES_BAR} "
        "largest_component_ratio=1.0000 orphan_rate=0.0000 content_coverage=1.0000\n",
    )
    result = _gate.evaluate(ROOT)
    assert result["status"] == "pass"
    assert result["failures"] == {}


def test_every_real_verdict_echoes_the_bars_it_judged_against(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A count without its bar does not say whether it was judged against 0 or
    # against the ratchet, and a bar nobody can see is one nobody notices being
    # raised. Both the counted and the absence-as-zero pass paths carry it.
    _patch_awiki(
        monkeypatch,
        "// lint_failed documents=42 orphans=0 islands=0 link_only_lines=1 "
        "largest_component_ratio=1.0000 orphan_rate=0.0000 content_coverage=1.0000\n",
    )
    counted = _gate.evaluate(ROOT)
    _patch_awiki(monkeypatch, _CLEAN_OUTPUT)
    absent = _gate.evaluate(ROOT)

    for result in (counted, absent):
        assert result["status"] == "pass"
        assert result["bars"] == dict(_gate.METRIC_BARS)
        assert result["bars"]["link_only_lines"] == _gate.LINK_ONLY_LINES_BAR


def test_a_gated_metric_without_its_tables_fails_loudly() -> None:
    # The negative case the acceptance check names. Adding a metric to the gated
    # set without these entries fails in the two worst available ways:
    # `BLOCK_FOR_METRIC[metric]` raises inside `_evaluate`, where the blanket
    # `except Exception` renders it as NOT-RUN -- the gate reporting it observed
    # nothing on a run where it observed a failure -- while the label and remedy
    # are read from `report()`, outside that guard, and crash uncaught.
    with pytest.raises(RuntimeError) as excinfo:
        _gate.assert_metric_tables_complete(
            ("orphans", "newly_added_metric"),
            {"BLOCK_FOR_METRIC": {"orphans": "orphan"}, "_REMEDY": {"orphans": "..."}},
        )
    message = str(excinfo.value)
    assert "newly_added_metric" in message
    assert "BLOCK_FOR_METRIC" in message and "_REMEDY" in message
    assert "orphans: " not in message, "a metric with every entry must not be reported"


def test_the_shipped_metric_tables_are_complete() -> None:
    # Against the SHIPPED tables via the default argument, and with a metric the
    # tables do not carry. Calling it with a hand-built `tables` dict proved the
    # function and nothing about the gate; and because
    # `missing_metric_table_entries` iterates whatever the registry contains,
    # DELETING a table from `_METRIC_TABLES` makes the check strictly weaker and
    # still returns `{}` -- so the registry's membership is pinned by name.
    assert set(_gate._METRIC_TABLES) == {"BLOCK_FOR_METRIC", "_FAILURE_LABEL", "_REMEDY"}
    assert _gate.missing_metric_table_entries(_gate.GATED_METRICS, _gate._METRIC_TABLES) == {}
    _gate.assert_metric_tables_complete()
    with pytest.raises(RuntimeError) as excinfo:
        _gate.assert_metric_tables_complete((*_gate.GATED_METRICS, "newly_added_metric"))
    assert "newly_added_metric" in str(excinfo.value)


def test_the_completeness_guard_runs_at_import() -> None:
    # A guard nobody invokes is the state the guard exists against: the next
    # metric added to `METRIC_BARS` would degrade to NOT-RUN or crash uncaught,
    # silently. Deleting the module-level call leaves every other assertion in
    # this file passing, so the call SITE is what gets pinned -- by AST, not by
    # text. A text scan matches the same characters inside a docstring, which is
    # a false pass in the one direction that matters, and reddens on a trailing
    # comment, which is a false failure that makes the pin annoying rather than
    # durable.
    import ast

    source = (ROOT / "scripts" / "check_docs_graph.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    calls = [
        node.value
        for node in module.body
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "assert_metric_tables_complete"
    ]
    assert len(calls) == 1, "the completeness guard must run once at import, at module level"
    assert not calls[0].args and not calls[0].keywords, (
        "the import-time call must use the shipped defaults, not narrowed arguments"
    )

    # And the defaults it relies on. Retargeting `metrics` to `()` leaves the call
    # site, both explicit-argument tests, and the whole suite green while the
    # import-time guard checks nothing at all.
    import inspect

    defaults = inspect.signature(_gate.assert_metric_tables_complete).parameters
    assert defaults["metrics"].default == _gate.GATED_METRICS
    assert defaults["tables"].default is None


def test_the_import_time_guard_would_catch_an_incomplete_shipped_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # End-to-end through the no-argument call, which is the one that runs at
    # import. The other negative tests pass their own metrics, so none of them
    # exercises the composition of call site and defaults.
    monkeypatch.setitem(_gate._METRIC_TABLES, "_REMEDY", {"orphans": "..."})
    with pytest.raises(RuntimeError) as excinfo:
        _gate.assert_metric_tables_complete()
    assert "_REMEDY" in str(excinfo.value)


def test_the_bar_matches_its_ratchet_record_and_never_rose() -> None:
    # The ratchet's executable half. "May only decrease" lived in comments and a
    # remedy string, so the cheapest repair for a red lane was editing one
    # three-digit literal -- the zero-work move the release contract's Fixed
    # Decision names. Raising the bar now also needs a row in the record whose
    # value the parse below refuses.
    record = (ROOT / "docs" / "docs-graph-checks.md").read_text(encoding="utf-8")
    section = record.split("## The `link_only_lines` ratchet record", 1)[1]
    # BOUNDED at the next H2. Unbounded, the slice ran to EOF, so any later table
    # in the file whose rows happen to start `| 20` would silently become the
    # ratchet -- the test would then compare the bar against an unrelated table.
    section = section.split("\n## ", 1)[0]
    rows = [
        line for line in section.splitlines()
        if line.startswith("| 20")  # data rows only; the header and separator are not dated
    ]
    assert rows, "the ratchet record has no dated rows"
    bars = [int(row.split("|")[2].strip()) for row in rows]

    # The FOUNDING row is an immutable anchor. Without it the record's history can
    # be rewritten rather than appended to: with a single row present, "never
    # increases downward" is vacuous, so raising the bar needed only an in-place
    # edit of that row plus the literal in the gate -- two files, no test, green.
    # Anchoring row zero means a raise must APPEND, and an appended higher row is
    # what the ordering assertion below refuses.
    assert rows[0].startswith("| 2026-08-15 |"), "the founding ratchet row was rewritten"
    assert bars[0] == 167, "the founding bar was rewritten; the ratchet records history"

    assert bars[-1] == _gate.LINK_ONLY_LINES_BAR, (
        "the gate's bar disagrees with the last row of its ratchet record"
    )
    assert bars == sorted(bars, reverse=True), f"the ratchet record rose: {bars}"


def test_named_pages_collapses_repeats_into_a_count() -> None:
    # `link_only_line` is per LINE, so one page appears once per finding. The raw
    # list named a single page dozens of times in a row, which is a list an
    # operator scrolls past rather than reads.
    output = (
        "// link_only_line\n"
        "[[artifact-policy]]:23: - [a](a.md)\n"
        "[[artifact-policy]]:24: - [b](b.md)\n"
        "[[handoff]]:13: - [c](c.md)\n"
    )
    assert _gate.named_pages(output, "link_only_line") == ["artifact-policy x2", "handoff"]


def test_a_missing_binary_is_not_run_rather_than_a_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_awiki(monkeypatch, "", present=False)
    result = _gate.evaluate(ROOT)

    assert result["status"] == "not-run"
    assert "not on PATH" in result["reason"]
    assert "are not zero" in result["reason"]


def test_an_unparseable_summary_is_not_run_rather_than_a_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    # The format is not a declared stable interface upstream. A version bump that
    # changes it must report UNPROVEN; resolving to a pass is how this gate would
    # start lying while looking green.
    _patch_awiki(monkeypatch, "awiki: something entirely different\n")
    result = _gate.evaluate(ROOT)

    assert result["status"] == "not-run"
    assert "no parseable summary line" in result["reason"]


def test_a_summary_without_the_gated_metrics_is_not_run(monkeypatch: pytest.MonkeyPatch) -> None:
    # A subtler drift than an unparseable line: the summary parses, but the
    # fields this gate judges are gone. Silently passing would mean gating on
    # nothing while reporting a clean docs verdict.
    #
    # The one metric this line DOES carry sits under its bar on purpose. With a
    # value over the bar the gate now fails on it -- correctly, and proven in
    # `test_an_observed_failure_is_judged_even_when_another_metric_is_missing` --
    # which would make this test pass or fail for the other reason.
    _patch_awiki(monkeypatch, "// lint_failed documents=42 link_only_lines=12\n")
    result = _gate.evaluate(ROOT)

    assert result["status"] == "not-run"
    assert "orphans, islands" in result["reason"]


def test_an_observed_failure_is_judged_even_when_another_metric_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Deciding `missing` first discarded measurements the tool actually printed.
    # An `ok` line carrying `orphans=2` with `islands` omitted resolved through
    # the absence-as-zero branch to `pass, failures: {}`; the same line under
    # `lint_failed` resolved to NOT-RUN, which is the one verdict SC8 says this
    # gate must not return when a count exceeds its bar.
    #
    # SYNTHETIC, and labelled so rather than passed off as captured: awiki prints
    # finding blocks only on a `lint_failed` run, so an `ok` line followed by an
    # `// orphan` block is a contradiction it does not emit. It is written that
    # way to hold the ordering and the naming in one case; the shape awiki could
    # actually produce is the next test.
    _patch_awiki(
        monkeypatch,
        "// ok connected_graph documents=100 orphans=2 "
        "largest_component_ratio=1.0000 orphan_rate=0.0000\n"
        "// orphan\n"
        "[[stranded]]: an excerpt\n",
        returncode=0,
    )
    result = _gate.evaluate(ROOT)

    assert result["status"] == "fail"
    assert result["failures"] == {"orphans": 2}
    assert result["named"]["orphans"] == ["stranded"]
    # And the verdict must not read as a verdict over all three metrics.
    assert result["not_observed"] == ["islands", "link_only_lines"]
    assert result["named_unavailable"] == []


def test_a_failure_with_no_finding_block_says_the_block_was_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The realistic form of the same path, and the one the naming repair could
    # regress into: a printed count now outranks the verdict token, and an `ok`
    # run prints no finding blocks at all. `named: {orphans: []}` alone reads as
    # "the block was empty" rather than "there was no block", which is the
    # difference between a docs defect and a tool-output surprise.
    _patch_awiki(
        monkeypatch,
        "// ok connected_graph documents=100 orphans=2 "
        "largest_component_ratio=1.0000 orphan_rate=0.0000\n",
        returncode=0,
    )
    result = _gate.evaluate(ROOT)

    assert result["status"] == "fail"
    assert result["named"]["orphans"] == []
    assert result["named_unavailable"] == ["orphans"]


def test_the_bar_can_be_overridden_for_a_repo_that_calibrated_its_own(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The built-in bar measures THIS repo's 80-column tree and travels with the
    # exported plugin, while the ratchet record and the test enforcing it do not.
    # A consuming repo has to be able to say its own number -- or 0.
    _patch_awiki(
        monkeypatch,
        "// lint_failed documents=42 orphans=0 islands=0 link_only_lines=3 "
        "largest_component_ratio=1.0000 orphan_rate=0.0000 content_coverage=1.0000\n",
    )
    assert _gate.evaluate(ROOT)["status"] == "pass"

    strict = dict(_gate.METRIC_BARS, link_only_lines=0)
    result = _gate.evaluate(ROOT, _gate.DEFAULT_SCAN_ROOT, strict)
    assert result["status"] == "fail"
    assert result["failures"] == {"link_only_lines": 3}
    assert result["bars"]["link_only_lines"] == 0


def test_every_run_names_what_it_did_not_judge(monkeypatch: pytest.MonkeyPatch) -> None:
    # Including the PASSING run: a green here must never be read as a clean docs
    # verdict, because this gate cannot see a broken link or an inaccurate page.
    _patch_awiki(monkeypatch, _CLEAN_OUTPUT)
    payload = _gate.report(_gate.evaluate(ROOT))
    rendered = "\n".join(payload["did_not_judge"])

    assert payload["did_not_judge"]
    assert "RESOLVES" in rendered
    assert "not accuracy" in rendered


def test_the_not_run_exit_code_is_the_runners_unestablished_byte() -> None:
    # Drift guard: the runner renders UNPROVEN off this exact byte. If they
    # disagree, a not-run reports as a hard failure or, worse, as a pass.
    runner = _RUN_QUALITY_SCRIPT
    assert f"UNESTABLISHED_EXIT={_gate.UNESTABLISHED_EXIT}" in runner
    assert "docs-graph" in runner
    unestablished_line = next(
        line for line in runner.splitlines() if line.startswith("UNESTABLISHED_CAPABLE_LABELS=")
    )
    assert "docs-graph" in unestablished_line


def test_the_gate_is_wired_into_the_quality_runner() -> None:
    runner = _RUN_QUALITY_SCRIPT
    assert 'queue_selected "docs-graph" python3 scripts/check_docs_graph.py' in runner


def test_the_live_repo_lane_runs_and_reports_a_real_verdict() -> None:
    # End-to-end against the real binary when it is installed. Skipped rather
    # than faked when absent -- a test that pretends to have run the tool is the
    # same defect the gate exists to prevent.
    import shutil as _shutil

    if _shutil.which("awiki") is None:
        pytest.skip("awiki is not installed on this machine; the lane reports UNPROVEN there")
    proc = subprocess.run(
        ["python3", GATE, "--repo-root", str(ROOT)],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    assert proc.returncode in {0, 1}, proc.stdout + proc.stderr
    payload = yaml.safe_load(proc.stdout)
    assert payload["status"] in {"pass", "fail"}
    assert payload["scan_root"] == "docs"
    assert payload["did_not_judge"]


def test_an_ok_verdict_contradicted_by_its_own_ratios_is_not_run(monkeypatch: pytest.MonkeyPatch) -> None:
    # The counts are absent, so the pass is read off awiki's `ok` token -- but only
    # when the ratios corroborate it. A summary that says `ok` while reporting a
    # non-zero orphan rate is contradictory, and picking the convenient half is how
    # a gate reports a verdict it did not observe.
    _patch_awiki(
        monkeypatch,
        "// ok connected_graph documents=42 largest_component_ratio=0.8250 "
        "orphan_rate=0.1750 content_coverage=1.0000\n",
    )
    result = _gate.evaluate(ROOT)

    assert result["status"] == "not-run"
    assert "connectivity question was NOT answered" in result["reason"]


def test_a_non_ok_verdict_missing_the_counts_is_not_run(monkeypatch: pytest.MonkeyPatch) -> None:
    # Only awiki's own passing token licenses reading absence as zero. A failing
    # verdict that drops the counts is format drift, not a pass.
    _patch_awiki(
        monkeypatch,
        "// lint_failed documents=42 largest_component_ratio=1.0000 orphan_rate=0.0000\n",
    )
    result = _gate.evaluate(ROOT)
    assert result["status"] == "not-run"


def test_an_islands_only_failure_names_the_pages_too(monkeypatch: pytest.MonkeyPatch) -> None:
    # Naming was wired to orphans alone, so an islands-only failure printed a bare
    # count and then orphan-specific advice about a page it never named.
    #
    # CAPTURED, not invented: the header form is `// island=1` (a header carrying a
    # VALUE, unlike `// orphan`), which is exactly the shape that decides whether
    # `_block_header` and `BLOCK_FOR_METRIC` are right. Asserting it against a
    # hand-written guess would prove the code against the author's belief.
    _patch_awiki(monkeypatch, _ISLAND_OUTPUT)
    result = _gate.evaluate(ROOT)
    payload = _gate.report(result)

    assert result["failures"] == {"islands": 1}
    assert result["named"]["islands"], "the island block named no page"
    assert payload["failures"]["islands"] == 1
    assert payload["failure_label"]["islands"] == "cut off with"
    assert "main" in payload["named"]["islands"]
    # And the advice must fit an island: a cluster is bridged, not retired.
    remedy = payload["remedies"]["islands"]
    assert "bridge" in remedy
    assert "nobody decided to retire" not in remedy


def test_the_gate_does_not_print_a_live_link_only_count() -> None:
    # NARROWED, not dropped. The original refused any hardcoded count anywhere in
    # the source, after the docstring printed "229 here" while the captured
    # fixture recorded 230. The bar is now a deliberate hardcoded number, so the
    # blanket form would refuse the fix -- but the reason survives intact for the
    # surface it was really about: `--help` renders this docstring, so a live
    # measurement inside it is a proof surface stating a number that drifts with
    # every docs edit. The bar belongs in code as a required value, where the
    # ratchet governs it; a snapshot of the current tree belongs in neither.
    source = (ROOT / "scripts" / "check_docs_graph.py").read_text(encoding="utf-8")
    docstring = _gate.__doc__ or ""
    assert docstring, "the module docstring is the --help text; it must not be empty"
    # Three digits or more: every count this docstring has ever carried is that
    # shape (229, 230, 255), while the ordinals of its numbered properties and
    # the `awiki 0.5.0` version it names are not. Known erosion, stated rather
    # than papered over: the bar only ever decreases, so once it falls below a
    # hundred a live two-digit count pasted here would slip past this pattern.
    import re as _re

    assert _re.search(r"\d{3,}", docstring) is None, (
        "the --help docstring carries a live count; bars belong in code, measurements in comments"
    )
    # The bar is a VALUE, not a comment: a comment can be deleted with nothing red.
    assert isinstance(_gate.LINK_ONLY_LINES_BAR, int)
    assert _gate.METRIC_BARS["link_only_lines"] == _gate.LINK_ONLY_LINES_BAR
    assert f"LINK_ONLY_LINES_BAR = {_gate.LINK_ONLY_LINES_BAR}" in source


def test_the_not_run_verdict_is_rendered_and_exits_unestablished(monkeypatch: pytest.MonkeyPatch) -> None:
    # The not-run RENDERING and its exit code, not just the dict. This is the
    # operator-facing half: the runner prints this line and reads that byte, and a
    # not-run that rendered as nothing would be indistinguishable from a pass.
    _patch_awiki(monkeypatch, "", present=False)
    payload = _gate.report(_gate.evaluate(ROOT))

    assert payload["status"] == "not-run"
    assert "not on PATH" in payload["reason"]
    # A not-run says nothing about what it did not judge, because it judged nothing.
    assert "did_not_judge" not in payload

    monkeypatch.setattr(_gate.sys, "argv", ["check_docs_graph.py"])
    assert _gate.main(["--repo-root", str(ROOT)]) == _gate.UNESTABLISHED_EXIT


# --- the wired path -------------------------------------------------------
#
# Everything above patches `_run_awiki` out, which is correct for verdict logic and
# is also why four lines of this gate had never executed: the function that actually
# invokes the tool, and the exit-code mapping the CI runner reads. Coverage and
# reachability-from-the-caller are different questions (#586, #572); these tests ask
# the second one.


def _stub_awiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, script: str) -> Path:
    """Put a real executable named `awiki` first on PATH, ahead of any installed one.

    A stub on PATH rather than a patched `subprocess.run`: the argv order, the `cwd`,
    the stdout/stderr merge and the timeout are contract with an external process, and
    a patched runner would prove them against the patch.
    """
    binary = tmp_path / "awiki"
    binary.write_text(script, encoding="utf-8")
    binary.chmod(0o755)
    # The stub directory goes FIRST, so it shadows a real awiki if one is installed,
    # and `os.defpath` follows so the stub can still reach `sh`'s usual utilities --
    # a PATH holding only the stub silently breaks the stub itself.
    # `os.defpath` opens with an empty element, which POSIX reads as "the current
    # directory" -- stripped, because a proof-surface test should not put cwd on the
    # search path even where the stub would win the lookup anyway.
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.defpath.lstrip(os.pathsep)}")
    return binary


def test_run_awiki_invokes_the_binary_with_the_argv_and_cwd_the_gate_declares(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    recorder = tmp_path / "argv.txt"
    _stub_awiki(
        tmp_path,
        monkeypatch,
        # Shell BUILTINS only (`printf`, `$*`, `$PWD`): the stub must not depend on
        # PATH resolution to record what it was asked, or a lookup failure would read
        # as the gate calling it wrong.
        f'#!/bin/sh\nprintf \'%s\\n\' "$*" > "{recorder}"\n'
        f'printf \'%s\\n\' "$PWD" >> "{recorder}"\n'
        'printf "out\\n"\nprintf "err\\n" >&2\nexit 3\n',
    )
    scan_dir = tmp_path / "work"
    scan_dir.mkdir()

    returncode, output = _gate._run_awiki(scan_dir, "docs/wiki")

    recorded = recorder.read_text(encoding="utf-8").splitlines()
    assert recorded[0] == "lint -root docs/wiki -recursive"
    assert Path(recorded[1]).resolve() == scan_dir.resolve()
    assert returncode == 3
    # stdout and stderr are MERGED, and stderr is not dropped: awiki writes its
    # diagnostics there, and a summary parser reading only stdout would report
    # not-run for a run that told it exactly what went wrong.
    assert output == "out\n\nerr\n"


def test_a_hung_awiki_times_out_rather_than_hanging_the_whole_quality_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The declared reason `AWIKI_TIMEOUT_SECONDS` exists, executed for the first time.
    # `evaluate` already renders a raised TimeoutExpired as NOT-RUN; what was never
    # proven is that the timeout FIRES, so the guard the comment promises was resting
    # on a keyword argument nothing had exercised.
    _stub_awiki(tmp_path, monkeypatch, "#!/bin/sh\nsleep 30\n")
    monkeypatch.setattr(_gate, "AWIKI_TIMEOUT_SECONDS", 0.25)

    with pytest.raises(subprocess.TimeoutExpired):
        _gate._run_awiki(tmp_path, "docs/wiki")


def test_main_exits_nonzero_on_fail_and_zero_on_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    # The verdict-to-exit-code mapping the CI runner reads. Every prior test that
    # reached `main` returned through the not-run branch, so neither half of this line
    # had ever run: a failing docs-graph had never been shown to exit nonzero, and a
    # passing one had never been shown to exit zero.
    _patch_awiki(monkeypatch, _ORPHAN_OUTPUT, returncode=1)
    assert _gate.main(["--repo-root", str(ROOT)]) == 1

    _patch_awiki(monkeypatch, _CLEAN_OUTPUT, returncode=0)
    assert _gate.main(["--repo-root", str(ROOT)]) == 0


def test_the_module_main_guard_executes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # `sys.exit(main())` -- the line every operator invocation goes through and no
    # test had. PATH is emptied so `awiki` is definitely absent, which makes the
    # verdict deterministic rather than dependent on the machine.
    import runpy
    import sys

    monkeypatch.setenv("PATH", str(tmp_path))  # empty dir: `awiki` is definitely absent
    monkeypatch.setattr(sys, "argv", ["check_docs_graph.py", "--repo-root", str(ROOT)])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(ROOT / GATE), run_name="__main__")

    assert excinfo.value.code == _gate.UNESTABLISHED_EXIT
