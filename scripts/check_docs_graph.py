#!/usr/bin/env python3
"""Gate the docs graph on REACHABILITY: are any pages orphaned or islanded?

This is the question no other gate in this repo asks. `check_doc_links.py`
validates that each link RESOLVES, which is a different question and stayed
correctly green while seven pages were unreachable. The measured split between
the two lives in `<repo-root>/docs/docs-graph-checks.md`.

Three deliberate properties, because this is a proof surface and a fail-open
gate is silent by construction:

1. It gates on NAMED METRICS against declared BARS, not on awiki's exit code.
   awiki 0.5.0 offers no way to select rules, so its exit code bundles every rule
   it has; this gate says which metrics it judges and at what value. `orphans`
   and `islands` are barred at 0. `link_only_lines` is barred at a RATCHET above
   0 — a bar that may only ever decrease — because awiki evaluates that rule per
   PHYSICAL line, so this repo's 80-column prose wrapping trips it on links that
   do carry context in the sentence they belong to. The bar is a required value
   below, not a comment: a comment can be deleted with nothing turning red.
2. It reports NOT-RUN rather than passing when it could not observe. A missing
   binary and an unparseable summary line both exit UNESTABLISHED, never 0: an
   unobserved orphan count is not zero, and a parse failure against an interface
   upstream has not declared stable is exactly how a gate starts lying.
3. It NAMES what it did not judge on every run, including the passing one, so a
   green here is never read as a clean docs verdict.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

# The runner's shared "analyzed nothing, so this is not a pass" byte. It renders
# as UNPROVEN in the quality summary rather than as a silent success.
UNESTABLISHED_EXIT = 3

DEFAULT_SCAN_ROOT = "docs"
# awiki exits 0 on a clean graph and 1 on lint findings. This gate does not read
# the code as its verdict -- findings are why it parses the summary instead --
# but a code OUTSIDE this set means awiki did not complete a scan, and a summary
# it may have printed on the way out describes a graph it did not finish reading.
OBSERVED_EXIT_CODES = frozenset({0, 1})
# The `link_only_lines` RATCHET. It may only ever decrease, and only with a
# recorded decision; raising it to whatever the tree currently measures is how a
# bar satisfies its criterion with zero work, so a raise is a contract change and
# not an edit. The residual it allows is NOT "some bare links are fine" -- it is
# awiki's per-PHYSICAL-line evaluation over-reporting hard-wrapped prose.
#
# Measured 2026-08-15. ONE observer: `awiki lint -root docs -recursive` reported
# `link_only_lines=255` -- the field this bar is compared against, not the
# bundled finding total, which is a different number whenever another rule fires.
# (An earlier draft of this comment called that two channels
# agreeing -- the gate's own parse of the same stdout was counted as a second
# one. It is the same observer read twice, which is what P4 in the design north
# star refuses, and it was caught in review rather than by anything executable.)
# The split below came from reading each flagged SOURCE LINE, which awiki's
# summary does not report and cannot corroborate:
#
#   88 were LIST ENTRIES whose link line carried no descriptor -- 83 bare, and 5
#   more whose descriptor had wrapped onto the following line, which reads fine
#   to a human and still leaves a physical line that is only a link. Every one of
#   those was repaired.
#   167 were links that landed alone on a physical line inside ordinary wrapped
#   prose, and they are what this bar allows.
#
# `docs/docs-graph-checks.md` records the measured decision that a reflow sweep
# across the docs tree is not the way, and reflowing prose to satisfy a
# line-based linter is churn no reader gains from.
#
# Both populations are scoped to what awiki FLAGGED, which is measured by
# construction -- the split came from reading the lines it flagged. That a list
# entry whose only link is an external URL falls outside both is INFERRED from
# awiki modelling markdown pages inside its root, and is NOT separately
# reproduced: reading what was flagged cannot establish what would not be.
#
# So the bar is not "some context-free links are tolerated". It is the size of
# the population this rule over-reports on an 80-column tree. Recount before
# changing it; it moves with every docs edit.
LINK_ONLY_LINES_BAR = 167
# The metrics this gate JUDGES, each against the bar it may not exceed.
# Everything else awiki reports is observed and echoed, never gated on.
METRIC_BARS = {"orphans": 0, "islands": 0, "link_only_lines": LINK_ONLY_LINES_BAR}
GATED_METRICS = tuple(METRIC_BARS)
# awiki names the offending pages under a block whose header differs from the
# metric name, so a failure can say WHICH page rather than only how many.
BLOCK_FOR_METRIC = {"orphans": "orphan", "islands": "island", "link_only_lines": "link_only_line"}
NOT_JUDGED = (
    "whether any link RESOLVES (that is check_doc_links.py, a different question)",
    "whether any page is ACCURATE or current (reachability is not accuracy)",
    "whether a link-only line is a bare link or wrapped prose -- the bar counts "
    "both, so a genuine bare link can hide under the wrapping residual",
)
_SUMMARY_RE = re.compile(r"^//\s*(?P<verdict>\w+)\s+(?P<fields>.*)$")
_FIELD_RE = re.compile(r"(?P<key>[a-z_]+)=(?P<value>[0-9.]+)")
# awiki's own token for "every rule passed". It is the only thing that licenses
# reading an ABSENT orphan/island count as zero, and even then only alongside the
# ratios below.
PASSING_VERDICT = "ok"
# Present on both the passing and failing summary lines (captured at 0.5.0 in
# tests/fixtures/), so they can corroborate a passing verdict that omits the
# counts themselves.
_CLEAN_COROBORATION = {"orphan_rate": 0.0, "largest_component_ratio": 1.0}
# A scan that read nothing is trivially "connected": an empty root reports
# `ok ... documents=0 orphan_rate=0.0000` and EXITS 0 (measured). Without this
# floor, a consuming repo whose docs live somewhere else gets a clean docs
# verdict over a graph that was never read.
MIN_SCANNED_DOCUMENTS = 1


def _corroborates_clean(summary: dict[str, float]) -> bool:
    """Do the ratios awiki always prints agree that nothing is orphaned or split?

    Required before an absent count is read as zero. If awiki ever says `ok` while
    printing a non-zero orphan rate, that is a contradiction, and the gate reports
    NOT-RUN rather than picking whichever half it prefers.
    """
    return all(summary.get(key) == expected for key, expected in _CLEAN_COROBORATION.items())


# A hung `awiki` would hang the whole quality run with no verdict at all. The
# timeout turns that into a TimeoutExpired, which the guard in `evaluate` renders
# as NOT-RUN -- the honest answer for a scan that never finished.
AWIKI_TIMEOUT_SECONDS = 120


def _run_awiki(repo_root: Path, scan_root: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["awiki", "lint", "-root", scan_root, "-recursive"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=AWIKI_TIMEOUT_SECONDS,
    )
    return proc.returncode, f"{proc.stdout}\n{proc.stderr}"


def parse_summary(output: str) -> tuple[str, dict[str, float]] | None:
    """Read awiki's `// <verdict> documents=.. orphans=.. ...` summary line.

    Returns `(verdict, fields)`, or None when no summary line is present, which
    the caller treats as NOT-RUN. The format is not a declared stable interface
    upstream, so failing to parse it must never resolve to a pass.
    """
    for line in output.splitlines():
        match = _SUMMARY_RE.match(line.strip())
        if not match:
            continue
        fields: dict[str, float] = {}
        for field in _FIELD_RE.finditer(match.group("fields")):
            try:
                fields[field.group("key")] = float(field.group("value"))
            except ValueError:
                # `[0-9.]+` accepts strings float() rejects (`1.2.3`, `.`). A
                # value this gate cannot read is drift, and drift must reach the
                # NOT-RUN path -- an uncaught ValueError would exit 1, which the
                # runner renders as FAIL: the gate asserting a broken docs graph
                # on a run where it observed nothing.
                return None
        if fields:
            return match.group("verdict"), fields
    return None


# awiki annotates each finding block with guidance lines (`// why:`, `// fix:`,
# `// example:`). They are NOT section headers, and treating them as such ends the
# block immediately -- which made a failing run report the count while naming no
# page, the one thing an operator needs from it.
#
# The rule is STRUCTURAL rather than a list of the annotations seen so far: a
# header is a bare token or `token=value` (`// orphan`, `// link_only_line`,
# `// island=1`, all captured in tests/fixtures/), while an annotation carries a
# COLON before any `=`. Keyed on an allowlist, a new `// note:` upstream would
# silently reintroduce the bug this replaced; keyed on `[a-z_]+:` alone, so would
# a multi-word `// see also:` or a capitalised `// Note:`.
_ANNOTATION_RE = re.compile(r"^//[^=]*:")


def _block_header(line: str) -> str | None:
    """The block name for an awiki section header line, else None."""
    if not line.startswith("//") or _ANNOTATION_RE.match(line):
        return None
    return line[2:].strip().split("=", 1)[0].strip() or None


def named_pages(output: str, block: str) -> list[str]:
    """The pages awiki listed under `block`, so a failure says WHICH.

    Deduplicated in first-seen order, with ` x<n>` appended when a page carries
    more than one finding. A connectivity block names each page once, so this is
    a no-op there; `link_only_line` is PER LINE and named one page 41 times in a
    row on the tree that added it, which is a list an operator scrolls past
    rather than reads.
    """
    counts: dict[str, int] = {}
    in_block = False
    for line in output.splitlines():
        stripped = line.strip()
        header = _block_header(stripped)
        if header is not None:
            in_block = header == block
            continue
        if stripped.startswith("//"):
            continue
        if in_block and stripped.startswith("[["):
            name = stripped.split("]]", 1)[0].lstrip("[")
            counts[name] = counts.get(name, 0) + 1
    return [name if count == 1 else f"{name} x{count}" for name, count in counts.items()]


def _not_run(reason: str, **extra: object) -> dict[str, object]:
    return {"status": "not-run", "reason": reason, **extra}


def evaluate(
    repo_root: Path, scan_root: str = DEFAULT_SCAN_ROOT, bars: dict[str, int] | None = None
) -> dict[str, object]:
    """Observe the docs graph, or say plainly that it was not observed.

    Every path out of here is pass, fail, or not-run. An unexpected exception
    would exit 1, which the runner renders as FAIL -- the gate asserting a broken
    docs graph on a run where it saw nothing -- so the whole body is guarded.
    """
    try:
        return _evaluate(repo_root, scan_root, METRIC_BARS if bars is None else bars)
    except Exception as exc:  # noqa: BLE001 -- see docstring: a crash must not read as a verdict
        return _not_run(
            f"the docs-graph observation raised {type(exc).__name__}: {exc}. Nothing was "
            "established about the graph; this is not a clean docs verdict."
        )


def _evaluate(repo_root: Path, scan_root: str, bars: dict[str, int]) -> dict[str, object]:
    if shutil.which("awiki") is None:
        return _not_run(
            "the `awiki` binary is not on PATH, so the docs graph was NOT observed. "
            "Install it via `charness tool install awiki`, or accept that orphan and "
            "island counts are unknown for this run -- they are not zero."
        )
    returncode, output = _run_awiki(repo_root, scan_root)
    if returncode not in OBSERVED_EXIT_CODES:
        return _not_run(
            f"`awiki lint` exited {returncode}, which is neither its clean (0) nor its "
            "findings (1) code, so it did not complete a scan. Any summary it printed "
            "describes a graph it did not finish reading.",
            output=output.strip()[:500],
        )
    parsed = parse_summary(output)
    if parsed is None:
        return _not_run(
            "`awiki lint` produced no parseable summary line, so the docs graph was "
            "NOT observed. Its summary format is not a declared stable interface; "
            "re-read it against the installed version before trusting this lane again.",
            output=output.strip()[:500],
        )
    verdict, summary = parsed
    scanned = summary.get("documents")
    if scanned is None or scanned < MIN_SCANNED_DOCUMENTS:
        return _not_run(
            f"`awiki lint` scanned {int(scanned) if scanned is not None else 'an unreported number of'} "
            f"documents under `{scan_root}/`, so there was no graph to judge. An empty scan is "
            "trivially connected and reports every ratio as clean; that is not a clean docs verdict. "
            "Point --scan-root at the tree that holds the docs.",
            summary=summary,
        )
    # JUDGE WHAT WAS OBSERVED FIRST. A metric awiki printed is a measurement, and
    # a measurement over its bar is a failure whether or not some OTHER metric was
    # omitted from the same line. Deciding `missing` first meant a summary
    # carrying `orphans=2` alongside an omitted `islands` resolved through the
    # absence-as-zero branch to `pass, failures: {}` -- the observed failure
    # discarded -- or, on a non-`ok` line, to NOT-RUN, which is the one verdict
    # SC8 says this gate must not return when a count exceeds its bar.
    #
    # So a printed COUNT outranks the verdict token, and `ok` alongside a
    # non-zero gated count resolves to FAIL. That is narrower than
    # `_corroborates_clean`'s docstring reads: the RATIO contradiction is the only
    # one that returns NOT-RUN, because a ratio is the thing being used as a proxy
    # for an absent count, while a count is the measurement itself.
    failures = {
        metric: int(summary[metric])
        for metric in GATED_METRICS
        if metric in summary and summary[metric] > bars[metric]
    }
    missing = [metric for metric in GATED_METRICS if metric not in summary]
    if missing and not failures:
        # awiki OMITS the per-rule counts on a fully passing run -- its `ok` line
        # carries only the ratios. Absent must not silently mean zero (that is the
        # fail-open shape this gate exists against), so the pass is read off
        # awiki's OWN verdict token, and only when the ratios it does print
        # corroborate it. A contradictory summary reports NOT-RUN.
        #
        # `ok` is awiki's token for EVERY rule passing, `link_only_line` included,
        # which is what licenses reading an absent count as zero for a metric the
        # ratios say nothing about. MEASURED and checked in at
        # `charness-artifacts/goals/2026-08-09-make-proof-surfaces-report-what-they-observed.md`:
        # a two-page wiki with zero orphans and one bare bullet link still exits 1.
        # That license is version-scoped -- an awiki that demotes `link_only_line`
        # to a warning while still printing `ok` would make this branch read an
        # unbounded count as zero, and `_corroborates_clean` cannot see it.
        if verdict == PASSING_VERDICT and _corroborates_clean(summary):
            return {
                "status": "pass",
                "summary": summary,
                "bars": dict(bars),
                # Read as zero off awiki's own passing token, not printed by it.
                # A reader deserves to know which half of that this pass rests on.
                "not_observed": missing,
                "failures": {},
                "named": {},
                "scan_root": scan_root,
            }
        return _not_run(
            f"`awiki lint` reported no {', '.join(missing)} field on a `{verdict}` line, so the "
            "connectivity question was NOT answered. The summary format changed; re-read it "
            "before trusting this lane again.",
            summary=summary,
        )
    return {
        "status": "fail" if failures else "pass",
        "summary": summary,
        "scan_root": scan_root,
        # A metric the summary never carried was NOT judged, and a verdict that
        # does not say so reads as a verdict over all three.
        "not_observed": missing,
        # A failing metric whose finding block awiki did not print. Reachable
        # because a printed count now outranks the verdict token: an `ok` line
        # carrying a non-zero count fails, and `ok` runs print no finding blocks.
        # Without this the payload shows `named: {metric: []}`, which reads as
        # "the block was empty" rather than "there was no block".
        "named_unavailable": sorted(
            metric for metric in failures if not named_pages(output, BLOCK_FOR_METRIC[metric])
        ),
        # Echoed on every real verdict, passing included. A bar a reader cannot
        # see is one nobody notices being raised, and the count alone does not
        # say whether it was judged against 0 or against the ratchet.
        "bars": dict(bars),
        "failures": failures,
        # Both failing metrics name their pages. Naming only orphans left an
        # islands-only failure reporting a bare count.
        "named": {
            metric: named_pages(output, BLOCK_FOR_METRIC[metric])
            for metric in failures
        },
    }


_FAILURE_LABEL = {
    "orphans": "unreachable",
    "islands": "cut off with",
    "link_only_lines": "context-free on",
}
# Each failure needs a DIFFERENT remedy. An island is a cluster that links
# internally and is cut off from the rest; telling its author to retire a page
# misdescribes it, which is the half of the naming repair that survived the first
# pass. A link-only line is not a graph defect at all.
_REMEDY = {
    "orphans": (
        "Link it from a related page, or from the docs index at docs/README.md. "
        "A page nobody can reach is one nobody decided to retire."
    ),
    "islands": (
        "Add a bridge link between one page in this cluster and a relevant page in "
        "the main component. The cluster is internally connected; it is the bridge "
        "that is missing."
    ),
    "link_only_lines": (
        "The count rose above its ratchet, so this run ADDED link-only lines. Find "
        "them with `awiki lint -root docs -recursive` and give each new one a short "
        "phrase on the link's OWN physical line saying what the target holds, "
        "wrapping after those words rather than before them. Do NOT lower the bar to "
        "the new count and do not reflow the tree; the bar only decreases, and "
        "docs/docs-graph-checks.md records why a reflow sweep is not the remedy."
    ),
}
# Adding a metric to `METRIC_BARS` without its entries here used to fail SILENTLY
# in the worst available way: `BLOCK_FOR_METRIC[metric]` raises `KeyError` inside
# `_evaluate`, where the blanket `except Exception` renders it as NOT-RUN -- a
# gate reporting that it observed nothing, on a run where it observed a failure
# it could not name -- while `_FAILURE_LABEL`/`_REMEDY` are read from `report()`,
# outside that guard, and crash uncaught. Checked at import so the mistake is a
# loud startup failure rather than either of those.
_METRIC_TABLES = {
    "BLOCK_FOR_METRIC": BLOCK_FOR_METRIC,
    "_FAILURE_LABEL": _FAILURE_LABEL,
    "_REMEDY": _REMEDY,
}


def missing_metric_table_entries(
    metrics: tuple[str, ...], tables: dict[str, dict[str, str]]
) -> dict[str, list[str]]:
    """Gated metrics with no entry in a table a failure path will index into."""
    return {
        metric: sorted(name for name, table in tables.items() if metric not in table)
        for metric in metrics
        if any(metric not in table for table in tables.values())
    }


def assert_metric_tables_complete(
    metrics: tuple[str, ...] = GATED_METRICS,
    tables: dict[str, dict[str, str]] | None = None,
) -> None:
    missing = missing_metric_table_entries(metrics, tables if tables is not None else _METRIC_TABLES)
    if not missing:
        return
    detail = "; ".join(f"{metric}: missing from {', '.join(names)}" for metric, names in sorted(missing.items()))
    raise RuntimeError(
        f"check_docs_graph is misconfigured: {detail}. A gated metric without these entries "
        "reports NOT-RUN on the failure it should have named, or crashes in the renderer. "
        "Add the block header, the failure label, and the remedy alongside the bar."
    )


assert_metric_tables_complete()


def report(result: dict[str, object]) -> dict[str, object]:
    """Fold the verdict-explaining text into the payload the gate actually emits.

    Output is unconditionally YAML, so anything a reader needs has to live in the
    payload. The remedies and the did-NOT-judge list used to exist only inside a
    human renderer; emitting the bare result would have deleted them from the
    gate's output while leaving it green, which is the fail-quiet shape the module
    docstring's property 3 exists against.
    """
    payload = dict(result)
    if result["status"] == "not-run":
        # A not-run says nothing about what it did NOT judge, because it judged
        # nothing. Listing exclusions here would dress an unobserved run up as a
        # scoped verdict.
        return payload
    # The scanned population belongs on every real verdict, not only the not-run
    # branch: a PASS that does not say WHICH tree it read is a verdict over a scope
    # it never stated, and everything outside this root is ungraphed.
    payload["did_not_judge"] = [
        *NOT_JUDGED,
        f"any page outside {result.get('scan_root', '?')}/, which this run never read",
    ]
    failures = result["failures"]
    if failures:
        payload["failure_label"] = {metric: _FAILURE_LABEL[metric] for metric in failures}
        payload["remedies"] = {metric: _REMEDY[metric] for metric in sorted(failures)}
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--scan-root",
        default=DEFAULT_SCAN_ROOT,
        help=(
            "Directory holding the wiki, relative to --repo-root. A consuming repo whose "
            "docs live elsewhere points this there; a scan that reads nothing reports "
            "NOT-RUN rather than a clean verdict."
        ),
    )
    parser.add_argument(
        "--link-only-lines-bar",
        type=int,
        default=None,
        help=(
            "Override the link-only-lines bar for this run. The built-in default is a "
            "measurement of THIS repo's own 80-column docs tree, and it travels with the "
            "exported plugin while the ratchet record and the test that enforce it do not. "
            "A consuming repo should calibrate its own -- pass 0 to refuse every "
            "context-free link line, or its own measured wrapped-prose count."
        ),
    )
    args = parser.parse_args(argv)

    bars = dict(METRIC_BARS)
    if args.link_only_lines_bar is not None:
        bars["link_only_lines"] = args.link_only_lines_bar
    result = evaluate(args.repo_root.resolve(), args.scan_root, bars)
    emit_yaml(report(result))
    if result["status"] == "not-run":
        return UNESTABLISHED_EXIT
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
