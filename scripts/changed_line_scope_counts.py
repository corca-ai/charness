#!/usr/bin/env python3
"""The analyzed/changed COUNT PAIR every changed-line verdict carries.

`check_changed_line_mutation_coverage.py` already emits the two LISTS a careful
reader would need: `changed_pool_files` (the analyzed set) on the blocking path,
and `unanalyzed_changed_pool_files` (the remainder) when `--limit-to-file`
narrows the scope. Neither list is present on every verdict-emitting path, and
neither states the PAIR — so "49 of 51" was reconstructable only by `len()`-ing
two lists that are not both always present, and not reconstructable at all on
the paths that carry neither. A verdict that does not state its own denominator
reads exactly like one rendered over the whole tree.

This module owns the pair so every verdict states its scope in one shape. It
lives outside the gate because that file is at its length cap, and keeping the
disclosure here gives it one tested definition instead of one inlined per path.

Disclosure only: nothing here changes a verdict or an exit code. Whether a
partial denominator should REFUSE is D40's toll question and stays the
operator's. (Recorded because this pointer was wrong once: it said D45, which is
the CI/local parity gate — a different gate. D40 is the entry that owns which
pre-landing lane pays a toll, and it now carries the residual explicitly.)
"""

from __future__ import annotations

from collections.abc import Sequence

#: Payload key. Deliberately a sibling of the existing `changed_pool_files` /
#: `unanalyzed_changed_pool_files` list keys rather than a replacement: consumers
#: read those lists today, and the pair is additive disclosure.
COUNTS_KEY = "changed_pool_file_counts"


def apply_file_limit(args, changed_before_coverage: list[str]) -> tuple[list[str], list[str]]:
    """Split the changed pool set into (analyzed, unanalyzed) per ``--limit-to-file``.

    This is where the numerator and the denominator are actually decided, which is
    why it lives beside `scope_counts` rather than in the gate: one module computes
    the split, reports the split, and is tested as one unit.

    An EMPTY limit means "analyze everything", not "analyze nothing" — the flag is
    absent on every existing caller and its absence must not silently empty the
    blocking set. A limit naming a path that did not change in this range is not an
    error: the caller derives its list from a mapping that may be broader than the
    range, and intersecting is the honest read.
    """
    limit = [str(path).strip() for path in (getattr(args, "limit_to_file", None) or []) if str(path).strip()]
    if not limit:
        return changed_before_coverage, []
    allowed = set(limit)
    analyzed = [path for path in changed_before_coverage if path in allowed]
    unanalyzed = [path for path in changed_before_coverage if path not in allowed]
    return analyzed, unanalyzed


def scope_counts(analyzed: Sequence[str], unanalyzed: Sequence[str]) -> dict:
    """The pair for a run whose changed set IS known.

    `changed` is the denominator and `analyzed` is the numerator this run
    actually read. Both range over exactly one population: eligible
    mutation-pool files whose content `base_sha..resolved_head_sha` changed. Not
    changed LINES, not every changed file, and not the checked-out tree when the
    analyzed head differs from it — `resolved_head_sha` is the sibling key that
    says which tree this denominator describes.

    On an unlimited run the two are equal, and that equality states that
    `--limit-to-file` left nothing out. It does NOT state that nothing at all was
    left out: an `--allow-dirty` run derives its set from `base..head`, which
    cannot see uncommitted pool edits, so `2 of 2` there means "2 of the 2 this
    range could see". That gap is disclosed by the `dirty_pool_unverified` and
    `uncommitted_pool_files` keys on the same payload rather than by shrinking
    this pair, because the pair's population is the range's and stays comparable
    across runs. Read the pair together with those keys, never alone.
    """
    analyzed_count = len(analyzed)
    return {
        COUNTS_KEY: {
            "analyzed": analyzed_count,
            "changed": analyzed_count + len(unanalyzed),
        }
    }


def scope_counts_not_computed(reason: str) -> dict:
    """The pair for a verdict emitted BEFORE the changed set was computed.

    Nulls, not zeros. A refusal that never looked has no denominator, and
    `0 of 0` would assert a scope the run did not earn — a clean-looking pair
    over a set that was never read is the exact substitution this gate exists to
    refuse. The `not_computed` reason says which path returned before the
    changed set was ever derived,
    so the absence is a statement rather than a gap.
    """
    return {COUNTS_KEY: {"analyzed": None, "changed": None, "not_computed": reason}}
