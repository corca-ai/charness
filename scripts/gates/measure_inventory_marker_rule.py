#!/usr/bin/env python3
"""Measure what a VALUE-MARKER rule would cost the inventory-consumption floor.

`docs/deferred-decisions.md` D47 asks whether an inventory-field mention should have to
carry a value marker (`field=`, `field:`, or a backticked `` `field` ``) on top of the
residual-character floor `validate_inventory_consumption.py` already applies. The reason
is that a field whose NAME is an ordinary English word -- `scope`, `status`, `notes`,
`paths`, `ranking`, `advisory`, `command`, `families` -- clears the residual floor on
incidental prose that never cited the inventory at all.

D47 recorded two numbers for that question and said so plainly: they were measured BY
HAND, and `measure_inventory_consumption_floor.py` does not produce them ("Two numbers
cited in docs/deferred-decisions.md D47 are NOT produced here"). This script is what
produces them, so the next call on D47 rests on a re-runnable number rather than on a
sentence someone wrote once.

**What it does NOT license.** It measures THIS repo's checked-in quality artifacts and
says nothing about a consumer repo's corpus. It is evidence that arming costs this repo
N; it is not evidence that arming is free anywhere else.

**What it deliberately does not do.** It arms nothing. The operator's 2026-08-01 call was
that D47's own named repair -- per-field distinctiveness in
`inventory-consumer-fields.json` -- cannot be built as described: the fields the corpus
actually engages ARE the ordinary-English ones, so declaring them non-distinctive refuses
the cited reviews while declaring them distinctive makes the marker rule apply to nothing
and ship as a measured-zero no-op. Measuring is the move that makes the next decision
real.

Corpus scope is reported, never assumed. The gate's own sibling scans a NON-RECURSIVE
`*.md`, which silently excludes `charness-artifacts/quality/history/`; `--recursive`
includes it, and the report always states which denominator produced the numbers.

Exit codes: 0 measured, 2 the corpus resolved to no files (a clean result over an empty
corpus is not a measurement -- the class rule this repo applies to every measurement
script).
"""
from __future__ import annotations

import json
import re
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.gates import inventory_measurement_lib as corpus_lib  # noqa: E402
from scripts.gates import validate_inventory_consumption as gate  # noqa: E402

from scripts.yaml_output import emit_yaml  # noqa: E402

DEFAULT_CORPUS = corpus_lib.DEFAULT_CORPUS
# Every exemption state on which `validate_inventory_consumption` returns 0 without
# running a floor. Only `REFUSED-uncorroborated` and `not-claimed` reach the floors.
PRE_CONTRACT_SKIPPED_BY_THE_GATE = frozenset({"corroborated", "not-corroborated"})


def markers_for(line: str, field: str) -> list[str]:
    """EVERY value marker this line uses for ``field``; empty when it is bare prose.

    `field=` and `field:` are assignments; `` `field` `` cites the identifier itself.
    Anything else is an ordinary word in a sentence -- the shape D47 says the residual
    floor cannot tell apart from a real citation.

    The backtick test splits the line and looks ONLY inside code spans. A naive
    `` `[^`]*field[^`]*` `` regex matches the GAP BETWEEN two code spans, so any bare
    mention sitting between two unrelated spans scored as marked. That bias runs one way
    -- it inflates "marked" and deflates the measured cost -- and it did so on real corpus
    lines like "...when the `budgets` map is empty, so a slow label produces one advisory
    `HOTSPOT (unbudgeted)` line", where `advisory` is plain English. Found by the round-1
    bounded review, which noted the first executed number would otherwise have
    manufactured its own conclusion.

    All matching kinds are returned rather than the first: this corpus writes assignments
    INSIDE code spans almost universally, so a first-match-wins order reported zero
    `field=` usage over a corpus full of `` `prose_review_status=required` ``.
    """
    escaped = re.escape(field)
    segments = line.split("`")
    kinds: list[str] = []
    # Odd-indexed segments are INSIDE code spans; even-indexed are prose. An assignment
    # marker counts wherever it appears, so it is searched across all segments.
    if any(re.search(rf"\b{escaped}\b", s) for s in segments[1::2]):
        kinds.append("backtick")
    for kind, pattern in (("assign", rf"\b{escaped}\s*="), ("colon", rf"\b{escaped}\s*:")):
        if any(re.search(pattern, s) for s in segments):
            kinds.append(kind)
    return kinds


def _mentions(body: str, field: str) -> list[str]:
    pattern = re.compile(rf"\b{re.escape(field)}\b")
    return [line for line in body.splitlines() if pattern.search(line)]


def scan(repo_root: Path, corpus: Path, fields_path: Path, *, recursive: bool) -> dict:
    inventories = json.loads(fields_path.read_text(encoding="utf-8")).get("inventories", {})
    paths = corpus_lib.corpus_paths(corpus, recursive=recursive)
    mentions_total = 0
    mentions_marked = 0
    mentions_presence_only = 0
    pre_contract_skipped: list[str] = []
    marker_kinds: dict[str, int] = {}
    rows: list[dict] = []
    refused: list[dict] = []
    for display, body, inventory, fields, exemption in corpus_lib.iter_citations(
        paths, inventories, repo_root
    ):
        if exemption in PRE_CONTRACT_SKIPPED_BY_THE_GATE:
            # The gate returns 0 without running any floor on all three of these arms,
            # not just the corroborated one, so counting them would report a cost on
            # artifacts the gate never judges. `not-corroborated` matters most off-git:
            # where `commit_state` is `unavailable` (a shallow clone, an exported corpus,
            # no git binary) EVERY pre-contract artifact lands there and the gate skips
            # them all.
            #
            # MEASURED-ZERO in this repo, in BOTH modes: the recorded probe's
            # `pre_contract_citations_skipped` is empty at top level and under
            # --recursive, because history/'s pre-contract artifacts were last committed
            # after the contract start. An earlier version of this comment claimed the
            # branch was "live under --recursive"; the probe recorded beside it said
            # otherwise, so the claim is retired rather than repeated.
            pre_contract_skipped.append(display)
            continue
        engaged_today: list[str] = []
        engaged_with_marker: list[str] = []
        for field in fields:
            rest = tuple(f for f in fields if f != field)
            mentions = _mentions(body, field)
            mentions_presence_only += len(mentions)
            clears_floor = [
                line for line in mentions
                if gate.residual_chars(line, field, rest) >= gate.MIN_ENGAGEMENT_RESIDUAL_CHARS
            ]
            if clears_floor:
                engaged_today.append(field)
            marked = [line for line in clears_floor if markers_for(line, field)]
            mentions_total += len(clears_floor)
            mentions_marked += len(marked)
            for line in marked:
                for kind in markers_for(line, field):
                    marker_kinds[kind] = marker_kinds.get(kind, 0) + 1
            if marked:
                engaged_with_marker.append(field)
        required = 2 if len(fields) >= 2 else 1
        row = {
            "path": display,
            "inventory": inventory,
            "required": required,
            "engaged_today": sorted(engaged_today),
            "engaged_with_a_marker": sorted(engaged_with_marker),
            "lost_to_the_marker_rule": sorted(set(engaged_today) - set(engaged_with_marker)),
        }
        rows.append(row)
        if len(engaged_today) >= required > len(engaged_with_marker):
            refused.append(row)
    return {
        "corpus": gate._display_path(corpus, repo_root),
        "recursive": recursive,
        "artifacts_scanned": len(paths),
        "artifacts_citing_a_declared_inventory": len({r["path"] for r in rows}),
        "pre_contract_citations_skipped": sorted(set(pre_contract_skipped)),
        # The PRESENCE-ONLY population, so the sibling script's `field_mention_residuals
        # .count` (the 169 D47's hand count used) is reproducible from here and the two
        # numbers can be compared on one denominator instead of across two.
        "field_mentions_presence_only": mentions_presence_only,
        "field_mentions_clearing_todays_floor": mentions_total,
        "field_mentions_carrying_a_value_marker": mentions_marked,
        "field_mentions_without_a_marker": mentions_total - mentions_marked,
        "marker_kinds": marker_kinds,
        "citations_refused_by_the_marker_rule": refused,
        "artifacts_refused_by_the_marker_rule": sorted({r["path"] for r in refused}),
        "rows": rows,
    }


def main() -> int:
    args = corpus_lib.build_parser(__doc__, recursive_flag=True).parse_args()

    repo_root, corpus, fields_path = corpus_lib.resolve_paths(args)
    if corpus_lib.refuse_empty_corpus(corpus, recursive=args.recursive):
        return 2

    report = scan(repo_root, corpus, fields_path, recursive=args.recursive)
    # Unconditional YAML. The retired human summary was a projection of this same
    # payload -- scope, the two mention counts, the marker-kind breakdown, and the
    # refused citations/artifacts are all fields below -- plus two counts it
    # computed inline, which are folded in so no number the summary stated is lost.
    report["citations_refused_count"] = len(report["citations_refused_by_the_marker_rule"])
    report["artifacts_refused_count"] = len(report["artifacts_refused_by_the_marker_rule"])
    report["scope"] = "recursive" if report["recursive"] else "top level only"
    emit_yaml(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
