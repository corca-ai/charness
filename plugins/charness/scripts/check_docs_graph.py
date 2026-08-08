#!/usr/bin/env python3
"""Gate the docs graph on REACHABILITY: are any pages orphaned or islanded?

This is the question no other gate in this repo asks. `check_doc_links.py`
validates that each link RESOLVES, which is a different question and stayed
correctly green while seven pages were unreachable. The measured split between
the two lives in `<repo-root>/docs/docs-graph-checks.md`.

Three deliberate properties, because this is a proof surface and a fail-open
gate is silent by construction:

1. It gates on the CONNECTIVITY metrics (`orphans`, `islands`), not on awiki's
   exit code. The exit code also fails on `link_only_lines`, most of which here
   are this repo's own 80-column prose wrapping putting a link alone on a
   physical line. Adopting that rule is a separate decision from adopting
   reachability, and awiki 0.5.0 offers no way to select rules. The live count is
   echoed from the summary this gate already parses, never typed here: a number
   inside a proof surface's own output drifts with every docs edit.
2. It reports NOT-RUN rather than passing when it could not observe. A missing
   binary and an unparseable summary line both exit UNESTABLISHED, never 0: an
   unobserved orphan count is not zero, and a parse failure against an interface
   upstream has not declared stable is exactly how a gate starts lying.
3. It NAMES what it did not judge on every run, including the passing one, so a
   green here is never read as a clean docs verdict.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

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
# The metrics this gate JUDGES. Everything else awiki reports is observed and
# echoed, never gated on.
GATED_METRICS = ("orphans", "islands")
# awiki names the offending pages under a block whose header differs from the
# metric name, so a failure can say WHICH page rather than only how many.
BLOCK_FOR_METRIC = {"orphans": "orphan", "islands": "island"}
NOT_JUDGED = (
    "link-only-line style (awiki's own rule, reported above and not gated on here)",
    "whether any link RESOLVES (that is check_doc_links.py, a different question)",
    "whether any page is ACCURATE or current (reachability is not accuracy)",
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
    """The pages awiki listed under `block`, so a failure says WHICH."""
    names: list[str] = []
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
            names.append(stripped.split("]]", 1)[0].lstrip("["))
    return names


def _not_run(reason: str, **extra: object) -> dict[str, object]:
    return {"status": "not-run", "reason": reason, **extra}


def evaluate(repo_root: Path, scan_root: str = DEFAULT_SCAN_ROOT) -> dict[str, object]:
    """Observe the docs graph, or say plainly that it was not observed.

    Every path out of here is pass, fail, or not-run. An unexpected exception
    would exit 1, which the runner renders as FAIL -- the gate asserting a broken
    docs graph on a run where it saw nothing -- so the whole body is guarded.
    """
    try:
        return _evaluate(repo_root, scan_root)
    except Exception as exc:  # noqa: BLE001 -- see docstring: a crash must not read as a verdict
        return _not_run(
            f"the docs-graph observation raised {type(exc).__name__}: {exc}. Nothing was "
            "established about the graph; this is not a clean docs verdict."
        )


def _evaluate(repo_root: Path, scan_root: str) -> dict[str, object]:
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
    missing = [metric for metric in GATED_METRICS if metric not in summary]
    if missing:
        # awiki OMITS the per-rule counts on a fully passing run -- its `ok` line
        # carries only the ratios. Absent must not silently mean zero (that is the
        # fail-open shape this gate exists against), so the pass is read off
        # awiki's OWN verdict token, and only when the ratios it does print
        # corroborate it. A contradictory summary reports NOT-RUN.
        if verdict == PASSING_VERDICT and _corroborates_clean(summary):
            return {"status": "pass", "summary": summary, "failures": {}, "named": {}}
        return _not_run(
            f"`awiki lint` reported no {', '.join(missing)} field on a `{verdict}` line, so the "
            "connectivity question was NOT answered. The summary format changed; re-read it "
            "before trusting this lane again.",
            summary=summary,
        )
    failures = {metric: int(summary[metric]) for metric in GATED_METRICS if summary[metric] > 0}
    return {
        "status": "fail" if failures else "pass",
        "summary": summary,
        "failures": failures,
        # Both failing metrics name their pages. Naming only orphans left an
        # islands-only failure reporting a bare count.
        "named": {
            metric: named_pages(output, BLOCK_FOR_METRIC[metric])
            for metric in failures
        },
    }


_UNREACHABLE_LABEL = {"orphans": "unreachable", "islands": "cut off with"}
# The two failures need DIFFERENT remedies. An island is a cluster that links
# internally and is cut off from the rest; telling its author to retire a page
# misdescribes it, which is the half of the naming repair that survived the first
# pass.
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
}


def format_human(result: dict[str, object]) -> str:
    lines: list[str] = []
    status = result["status"]
    if status == "not-run":
        lines.append(f"docs-graph: NOT RUN -- {result['reason']}")
        return "\n".join(lines)

    summary = result["summary"]
    observed = " ".join(
        f"{key}={int(value) if float(value).is_integer() else value}"
        for key, value in sorted(summary.items())
    )
    if status == "fail":
        lines.append(f"docs-graph: FAIL ({observed})")
        for metric, count in sorted(result["failures"].items()):
            lines.append(f"  - {metric}={count}")
            for name in result["named"].get(metric, []):
                lines.append(f"    {_UNREACHABLE_LABEL[metric]}: {name}")
        for metric in sorted(result["failures"]):
            lines.append("  " + _REMEDY[metric])
    else:
        lines.append(f"docs-graph: PASS ({observed})")
    lines.append("  did NOT judge: " + "; ".join(NOT_JUDGED))
    return "\n".join(lines)


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
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = evaluate(args.repo_root.resolve(), args.scan_root)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else format_human(result))
    if result["status"] == "not-run":
        return UNESTABLISHED_EXIT
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
