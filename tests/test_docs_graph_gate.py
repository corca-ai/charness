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

import subprocess
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]
GATE = "scripts/check_docs_graph.py"
_gate = import_repo_module(__file__, "scripts.check_docs_graph")

# CAPTURED from awiki 0.5.0, not hand-written. The passing line is the one that
# matters: it OMITS `orphans`/`islands` entirely, which is what forced the
# absence-as-zero branch to exist, and a fixture invented from the author's
# belief would have proven that branch against the belief rather than the tool.
FIXTURES = ROOT / "tests" / "fixtures"
_CLEAN_OUTPUT = (FIXTURES / "awiki-0.5.0-connected-graph.stdout.txt").read_text(encoding="utf-8")
_EMPTY_ROOT_OUTPUT = (FIXTURES / "awiki-0.5.0-empty-root.stdout.txt").read_text(encoding="utf-8")
_ISLAND_OUTPUT = (FIXTURES / "awiki-0.5.0-island.stdout.txt").read_text(encoding="utf-8")
_ORPHAN_OUTPUT = (
    "// lint_failed documents=43 orphans=2 islands=0 link_only_lines=229 "
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


def test_link_only_lines_alone_do_not_fail_the_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    # The deliberate scope decision, pinned so it cannot be widened by accident:
    # awiki exits 1 on link-only lines, and this gate does not gate on them.
    _patch_awiki(
        monkeypatch,
        "// lint_failed documents=42 orphans=0 islands=0 link_only_lines=229 "
        "largest_component_ratio=1.0000 orphan_rate=0.0000 content_coverage=1.0000\n",
    )
    result = _gate.evaluate(ROOT)
    assert result["status"] == "pass"


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
    _patch_awiki(monkeypatch, "// lint_failed documents=42 link_only_lines=229\n")
    result = _gate.evaluate(ROOT)

    assert result["status"] == "not-run"
    assert "orphans, islands" in result["reason"]


def test_every_run_names_what_it_did_not_judge(monkeypatch: pytest.MonkeyPatch) -> None:
    # Including the PASSING run: a green here must never be read as a clean docs
    # verdict, because this gate cannot see a broken link or an inaccurate page.
    _patch_awiki(monkeypatch, _CLEAN_OUTPUT)
    rendered = _gate.format_human(_gate.evaluate(ROOT))

    assert "did NOT judge" in rendered
    assert "RESOLVES" in rendered
    assert "not accuracy" in rendered


def test_the_not_run_exit_code_is_the_runners_unestablished_byte() -> None:
    # Drift guard: the runner renders UNPROVEN off this exact byte. If they
    # disagree, a not-run reports as a hard failure or, worse, as a pass.
    runner = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
    assert f"UNESTABLISHED_EXIT={_gate.UNESTABLISHED_EXIT}" in runner
    assert "docs-graph" in runner
    unestablished_line = next(
        line for line in runner.splitlines() if line.startswith("UNESTABLISHED_CAPABLE_LABELS=")
    )
    assert "docs-graph" in unestablished_line


def test_the_gate_is_wired_into_the_quality_runner() -> None:
    runner = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")
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
    assert proc.stdout.startswith("docs-graph: ")


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
    rendered = _gate.format_human(result)

    assert result["failures"] == {"islands": 1}
    assert result["named"]["islands"], "the island block named no page"
    assert "islands=1" in rendered
    assert "cut off with: main" in rendered
    # And the advice must fit an island: a cluster is bridged, not retired.
    assert "bridge" in rendered
    assert "nobody decided to retire" not in rendered


def test_the_gate_does_not_hardcode_a_link_only_count() -> None:
    # It printed "229 here" while the captured fixture recorded 230. A magic count
    # inside the text a proof surface prints on every run drifts with every docs
    # edit, and a proof surface stating a stale number is the class under repair.
    source = (ROOT / "scripts" / "check_docs_graph.py").read_text(encoding="utf-8")
    assert "229" not in source
    assert "230" not in source
