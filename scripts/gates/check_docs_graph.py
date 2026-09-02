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
   and `islands` are barred at 0. `link_only_lines` is barred at 0 too UNLESS
   this repo records its own ratchet, because awiki evaluates that rule per
   PHYSICAL line and a hard-wrapped prose tree trips it on links that do carry
   context in the sentence they belong to. Record a bar in
   `docs/docs-graph-checks.md` under the `## The `link_only_lines` ratchet
   record` heading: a `| date | bar | why |` table whose bars may only ever
   DECREASE, which this gate enforces by refusing a record that rises. No record
   means the strict default, never an inherited one — a threshold measured on
   somebody else's docs tree is not a bar, and the number that governs this run
   is echoed under `bars:` in the output.
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
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)
_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_monitored_phase = _subprocess_guard.run_monitored_phase
_quality_adapter = import_repo_module(__file__, "scripts.adapters.quality_adapter_lib")
load_quality_adapter = _quality_adapter.load_quality_adapter
_quality_universes = import_repo_module(__file__, "scripts.adapters.quality_universes_lib")
DEFAULT_UNIVERSES = _quality_universes.DEFAULT_UNIVERSES
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe

# The runner's shared "analyzed nothing, so this is not a pass" byte. It renders
# as UNPROVEN in the quality summary rather than as a silent success.
UNESTABLISHED_EXIT = 3


def _scan_root_from_patterns(patterns: tuple[str, ...]) -> str:
    """Choose the first directory-bearing root from a doc-surface pattern set."""
    for pattern in patterns:
        parts = Path(pattern).parts
        if (
            parts
            and not any(char in parts[0] for char in "*?[")
            and (len(parts) > 1 or Path(pattern).suffix.lower() != ".md")
        ):
            return parts[0]
    return "."


DEFAULT_SCAN_ROOT = _scan_root_from_patterns(tuple(DEFAULT_UNIVERSES["doc_surfaces"]))
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
# HOW TO SIZE ONE, stated as the method rather than as anyone's answer. A repo
# measures its own two populations by reading each SOURCE LINE awiki flags --
# which its summary does not report and cannot corroborate. List entries whose
# link line carries no descriptor are the repairable population; links that land
# alone on a physical line inside ordinary wrapped prose are the population this
# rule over-reports on, and the bar is sized to THAT. Both are scoped to what
# awiki flagged: reading what was flagged cannot establish what would not be, so
# a list entry whose only link is an external URL falls outside both.
#
# So the bar is not "some context-free links are tolerated". It is the size of
# the population this rule over-reports on a hard-wrapped tree. Recount before
# changing it; it moves with every docs edit. Charness's own measurement, its
# 08-15 recount, and the P4 correction a reviewer made to how it was described
# live in this repo's ratchet record, not here -- a number measured on one docs
# tree has no meaning in a file every consuming repo installs.
#
# WHERE THE NUMBER LIVES, and why it is not a literal here (S6, 2026-08-15).
# It used to be a hard-coded `LINK_ONLY_LINES_BAR` on this line, in a file the
# plugin EXPORTS -- while the ratchet record and `tests/test_docs_graph_gate.py`,
# the ratchet record and the test that hold it to "may only decrease", are not
# exported at all. A consuming repo therefore inherited a threshold measured on
# charness's own 80-column docs tree, with neither of the two surfaces that give
# it meaning, and nothing told it so. Owner ruling 2026-08-15: the exported
# default is 0, and this repo's own bar is READ from its ratchet record.
#
# So the bar is now sourced, not declared. Absence falls to
# `DEFAULT_LINK_ONLY_LINES_BAR`, which is the STRICT direction: a repo with no
# record refuses every context-free link line rather than inheriting a foreign
# allowance. A malformed record falls the same way, for the same reason -- the
# failure is loud (this repo measures far above 0) rather than a quiet pass.
RATCHET_RECORD_PATH = "docs/docs-graph-checks.md"
RATCHET_SECTION_HEADING = "## The `link_only_lines` ratchet record"
DEFAULT_LINK_ONLY_LINES_BAR = 0
_RATCHET_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
# A GFM header row or its `| --- |` separator: skipped as structure rather than
# refused as a malformed data row.
_RATCHET_HEADER_OR_SEPARATOR = re.compile(
    r"^\|?[\s:|-]*\|[\s:|-]*$|^\|?\s*date\s*\|", re.IGNORECASE
)
# The metrics this gate JUDGES, each against the bar it may not exceed.
# `link_only_lines` carries the EXPORTED default; `resolve_bars` replaces it with
# the repo's own recorded bar when a ratchet record is present. Kept as a plain
# dict rather than resolved at import so that importing this module never reads
# the filesystem, and so `GATED_METRICS` stays a constant the completeness guard
# below can check at import time.
METRIC_BARS = {"orphans": 0, "islands": 0, "link_only_lines": DEFAULT_LINK_ONLY_LINES_BAR}
GATED_METRICS = tuple(METRIC_BARS)
# awiki names the offending pages under a block whose header differs from the
# metric name, so a failure can say WHICH page rather than only how many.
BLOCK_FOR_METRIC = {"orphans": "orphan", "islands": "island", "link_only_lines": "link_only_line"}
NOT_JUDGED = (
    "whether any link RESOLVES (that is check_doc_links.py, a different question)",
    "whether any page is ACCURATE or current (reachability is not accuracy)",
    "whether a link-only line is a bare link or wrapped prose -- the bar counts "
    "both, so a genuine bare link can hide under the wrapping residual (see "
    "`link_only_lines_slack` for how much room that residual currently has)",
)
# Sibling reason emitted when `link_only_lines_slack` is null on the one path
# where the gap is genuinely unknown rather than merely unfavourable: this run
# FAILED on some OTHER metric while `link_only_lines` itself went unobserved, so
# its count is neither printed nor licensed as zero.
LINK_ONLY_LINES_SLACK_NOT_COMPUTABLE = (
    "not computable this run: `link_only_lines` was not observed while a "
    "different metric failed, so its count is neither zero nor printed"
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


def _resolved_doc_scope(repo_root: Path):
    universe = resolve_universe(
        load_quality_adapter(repo_root),
        "doc_surfaces",
        default=DEFAULT_UNIVERSES["doc_surfaces"],
    )
    files = [path for path in matching_files(repo_root, universe) if path.suffix.lower() == ".md"]
    return universe, files


def _run_awiki(repo_root: Path, scan_root: str) -> tuple[int, str]:
    outcome = run_monitored_phase(
        ["awiki", "lint", "-root", scan_root, "-recursive"],
        cwd=repo_root,
        phase="docs-graph-awiki",
        timeout_seconds=AWIKI_TIMEOUT_SECONDS,
    )
    return outcome.returncode, f"{outcome.stdout}\n{outcome.stderr}"


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


def ratchet_rows(repo_root: Path) -> list[tuple[str, int]]:
    """The `(date, bar)` rows of this repo's ratchet record, oldest first.

    ONE parser, deliberately. The record was already parsed by
    `tests/test_docs_graph_gate.py` while the gate carried an independent
    literal, so the two could disagree and only the test would notice -- and the
    test is not exported, so for a consuming repo nothing noticed at all. The
    gate reads the record now and the test asserts properties of THESE rows, so
    the "second surface" the record exists to be is a record of history rather
    than a duplicated number.

    Returns `[]` when the record, its section, or its dated rows are absent,
    unreadable, or NOT NON-INCREASING. Every such case falls to
    `DEFAULT_LINK_ONLY_LINES_BAR`, which is stricter than any bar a record could
    name -- absence cannot buy allowance.

    THE MONOTONICITY CHECK IS ENFORCED HERE, not only in the test, and that is
    the whole point of this function for a consuming repo. This gate is exported;
    the ratchet record and `tests/test_docs_graph_gate.py` are not. A round-1
    reviewer showed that sourcing the bar from a consumer-controlled file while
    leaving "may only ever decrease" to a non-exported test meant a consumer
    could append `| 2026-08-20 | 99999 |` and go green with nothing red anywhere
    in the installed artifact -- while this module's own docstring still promised
    them a ratchet. Enforcing it in the parser makes the change a net
    strengthening for consumers instead of a weakening, and demotes the test to a
    redundant second surface, which is what a second surface should be.
    """
    try:
        text = (repo_root / RATCHET_RECORD_PATH).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # `UnicodeDecodeError` is a ValueError, not an OSError, so one stray
        # non-UTF-8 byte -- a bad merge, a mispasted smart quote -- used to
        # escape this handler and turn a docs verdict into a crash.
        return []
    if RATCHET_SECTION_HEADING not in text:
        return []
    section = text.split(RATCHET_SECTION_HEADING, 1)[1]
    # BOUNDED at the next H2. Unbounded this runs to EOF, so any later table in
    # the file whose rows happen to start `| 20` would silently become part of
    # the ratchet. The test that used to own this parse learned that in review.
    section = section.split("\n## ", 1)[0]
    rows: list[tuple[str, int]] = []
    for raw in section.splitlines():
        line = raw.strip()
        if "|" not in line or _RATCHET_HEADER_OR_SEPARATOR.match(line):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or not _RATCHET_DATE.fullmatch(cells[0]):
            continue
        try:
            rows.append((cells[0], int(cells[1])))
        except ValueError:
            # A row whose bar is not an integer makes the record unreadable as a
            # ratchet. Refuse the WHOLE record rather than silently skipping the
            # row: a skipped row is a missing history entry, and the monotonicity
            # below cannot be checked against a subset. Selecting rows by SHAPE
            # (a date-looking first cell) rather than by the literal prefix
            # `| 20` is what makes that promise true -- the prefix silently
            # skipped a leading-pipe-less or indented row, which is legal GFM,
            # and dropping a row is how a recorded DECREASE goes missing and the
            # bar silently stays high.
            return []
    bars = [bar for _, bar in rows]
    if bars != sorted(bars, reverse=True):
        return []
    return rows


def resolve_link_only_lines_bar(repo_root: Path) -> int:
    """This repo's recorded bar, or the strict exported default when it has none."""
    rows = ratchet_rows(repo_root)
    return rows[-1][1] if rows else DEFAULT_LINK_ONLY_LINES_BAR


def resolve_bars(repo_root: Path, override: int | None = None) -> dict[str, int]:
    """The bars one run judges against: exported defaults, then record, then flag."""
    bars = dict(METRIC_BARS)
    bars["link_only_lines"] = (
        resolve_link_only_lines_bar(repo_root) if override is None else override
    )
    return bars


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
    repo_root: Path,
    scan_root: str | None = None,
    bars: dict[str, int] | None = None,
    *,
    link_only_lines_bar: int | None = None,
) -> dict[str, object]:
    """Observe the docs graph, or say plainly that it was not observed.

    Every path out of here is pass, fail, or not-run. An unexpected exception
    would exit 1, which the runner renders as FAIL -- the gate asserting a broken
    docs graph on a run where it saw nothing -- so the whole body is guarded.
    """
    try:
        if scan_root is None:
            universe, files = _resolved_doc_scope(repo_root)
            scan_root = _scan_root_from_patterns(universe.patterns)
            refusal = refuse_if_declared_and_empty(universe, files, "docs-graph")
            if refusal:
                return _not_run(refusal, scan_root=scan_root)
            if not files:
                return _not_run(
                    f"docs-graph: discovered empty universe under `{scan_root}/`; "
                    "no documentation graph was established.",
                    scan_root=scan_root,
                )
        resolved = bars if bars is not None else resolve_bars(repo_root, link_only_lines_bar)
        return _evaluate(repo_root, scan_root, resolved)
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
        "named": {metric: named_pages(output, BLOCK_FOR_METRIC[metric]) for metric in failures},
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
        "Link it from a related page, or from the docs index at docs/index.md. "
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
    missing = missing_metric_table_entries(
        metrics, tables if tables is not None else _METRIC_TABLES
    )
    if not missing:
        return
    detail = "; ".join(
        f"{metric}: missing from {', '.join(names)}" for metric, names in sorted(missing.items())
    )
    raise RuntimeError(
        f"check_docs_graph is misconfigured: {detail}. A gated metric without these entries "
        "reports NOT-RUN on the failure it should have named, or crashes in the renderer. "
        "Add the block header, the failure label, and the remedy alongside the bar."
    )


assert_metric_tables_complete()


def link_only_lines_slack(result: dict[str, object]) -> int | None:
    """Bar minus the CURRENTLY MEASURED `link_only_lines` count, on a real verdict.

    The bar only ever moves on a recorded ratchet entry (`ratchet_rows` above);
    the measured count moves on its own with every docs edit -- a rewrap can
    LOWER the measured count while the bar stays where it was, and this is the
    width of the gap that opens between them. Nothing else in this module's
    output says how wide that gap currently is, so a growing one goes silent:
    the bar keeps passing while more room opens for the genuine bare link
    `NOT_JUDGED` already concedes can hide in the wrapping residual.

    Computable whenever `link_only_lines` was actually judged this run: printed
    directly in the summary, or read as zero off awiki's OWN passing verdict
    token in the licensed branch inside `_evaluate` (a `pass` where the field is
    absent can only be that license, never a genuine unknown). Returns
    ``None`` on the one path where the count is genuinely unknown: this run
    FAILED on some OTHER metric while `link_only_lines` itself was never printed
    and the zero-license branch was never reached. The sibling
    ``link_only_lines_slack_reason`` carries the human-readable explanation.
    """
    summary = result["summary"]
    bar = result["bars"]["link_only_lines"]
    if "link_only_lines" in summary:
        return bar - int(summary["link_only_lines"])
    if result["status"] == "pass":
        return bar
    return None


def link_only_lines_slack_reason(result: dict[str, object]) -> str | None:
    """Explain a null slack value without overloading the numeric field."""

    summary = result["summary"]
    if "link_only_lines" in summary or result["status"] == "pass":
        return None
    return LINK_ONLY_LINES_SLACK_NOT_COMPUTABLE


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
    # Additive only: computed from `result`, never fed back into `status` or the
    # exit code `main` derives from it. The monotone ratchet refuses a RISE and
    # is silent about a FALL, so this is the one number in the whole payload that
    # can shrink on a green run without anyone having recorded why.
    payload["link_only_lines_slack"] = link_only_lines_slack(result)
    slack_reason = link_only_lines_slack_reason(result)
    if slack_reason is not None:
        payload["link_only_lines_slack_reason"] = slack_reason
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
        default=None,
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
            "Override the link-only-lines bar for this run. Without it the bar comes from "
            f"the last row of this repo's `{RATCHET_RECORD_PATH}` ratchet record, and from "
            f"{DEFAULT_LINK_ONLY_LINES_BAR} when that record is absent -- a consuming repo "
            "inherits no threshold measured on someone else's docs tree. Calibrate by "
            "recording your own ratchet rather than by passing this flag on every run; the "
            "flag is a probe, and it leaves no history behind."
        ),
    )
    args = parser.parse_args(argv)

    # The override is passed THROUGH rather than resolved here. Resolving in
    # `main` put a filesystem read outside every guard, so an unreadable ratchet
    # record produced an uncaught traceback and exit 1 -- which the runner renders
    # as FAIL, the gate asserting a broken docs graph on a run where it observed
    # nothing. That is the precise anti-pattern `evaluate`'s docstring exists
    # against, and the two entry points disagreed about the same input (NOT-RUN
    # via `evaluate`, hard FAIL via `main`). Round-1 finding; keeping the
    # resolution inside the guard restores "every path out of here is pass, fail,
    # or not-run" as a structural property rather than a per-raiser audit.
    result = evaluate(
        args.repo_root.resolve(), args.scan_root, link_only_lines_bar=args.link_only_lines_bar
    )
    emit_yaml(report(result))
    if result["status"] == "not-run":
        return UNESTABLISHED_EXIT
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
