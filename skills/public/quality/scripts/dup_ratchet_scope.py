#!/usr/bin/env python3
"""One concept: what scope this dup-ratchet run covers, and how it says what it did
not judge.

Split out of `dup_ratchet_lib` (the coverage computation) and `check_dup_ratchet`
(the `did_not_judge` wording) when both crossed the skill-helper length cap. The
two halves are one question asked twice -- the resolver decides whether a declared
`scope_paths` can be compared literally against git-tracked paths at all, the
reporter says which unknown resulted -- and keeping them apart is what let the
reporter assert a cause the resolver had stopped being the only source of.
"""

from __future__ import annotations

import posixpath
from typing import Any, Iterable

#: Characters a literal path comparison cannot take at face value: the three glob
#: metacharacters, plus the one separator this matcher does not speak.
_NON_LITERAL_SCOPE_CHARS = frozenset("*?[\\")


def _is_literal_relative_prefix(normalized: str) -> bool:
    """Whether a normalized entry has the ONE shape ``scope_coverage`` can answer
    about: the form ``git ls-files`` emits -- repo-relative, ``/``-separated, every
    segment an ordinary name compared literally.

    Stated as what the comparison REQUIRES, not as a list of shapes to reject. The
    rejecting version was written twice and missed a different shape each time:
    first ``"."`` and ``"./src"``, then absolute paths, ``~``, ``\\``, and ``//``.
    Every miss published a real-looking number about a population it had not
    measured -- ``uncovered_file_count == tracked_file_count`` and "this scan never
    forms a CODE family from them" over files the scanner had read.
    """
    if posixpath.isabs(normalized) or normalized.startswith("~"):
        return False
    return all(
        segment not in {"", ".", ".."} and not (_NON_LITERAL_SCOPE_CHARS & set(segment))
        for segment in normalized.split("/")
    )


def resolve_scope_prefixes(scope_paths: Iterable[str]) -> tuple[list[str] | None, list[str]]:
    """``(prefixes, unresolvable)`` for a declared ``scope_paths``.

    ``prefixes`` is ``None`` when some entry covers the whole tree (``"."``, ``""``,
    ``"/"``): nothing sits outside it, and that stays true whatever the sibling
    entries mean, so a whole-tree entry settles the coverage question even next to an
    unresolvable one. ``unresolvable`` lists every entry that is not a literal
    repo-relative prefix -- returned rather than swallowed so a caller can say WHICH
    unknown it is reporting instead of asserting the only cause that used to exist.
    """
    prefixes: list[str] | None = []
    unresolvable: list[str] = []
    for raw in scope_paths:
        text = str(raw).strip()
        normalized = posixpath.normpath(text)
        if normalized in {".", "", "/"}:
            prefixes = None
            continue
        if not _is_literal_relative_prefix(normalized):
            unresolvable.append(text)
            continue
        if prefixes is not None:
            prefixes.append(normalized)
    return prefixes, unresolvable


def scope_coverage(tracked_files: set[str] | None, scope_paths: Iterable[str]) -> dict[str, Any] | None:
    """How many of this repo's git-tracked files sit outside ``scope_paths`` -- the
    population ``dup_ratchet_scan.scan_families`` never forms a family from,
    because it only ever reads ``scope_paths``. ``None`` when the count cannot be
    computed; the caller reports that un-knowledge honestly rather than reading an
    unasked population as zero.

    This over-counts relative to what nose would actually flag: every tracked
    file counts, including docs/config nose would never treat as a code clone.
    The gate does not own nose's own file-type filtering, and guessing at it here
    would invent a number rather than compute one -- this is the closest honest
    signal available without running a second, duplicate scan.

    Two distinct inputs produce ``None``: git could not answer, and ``scope_paths``
    carries a shape ``resolve_scope_prefixes`` cannot express as a literal prefix
    (a glob such as ``src/**/*.py``, which the adapter validator's own docstring
    calls legal, or an absolute path this function has no repo root to rebase). The
    caller distinguishes them by asking ``resolve_scope_prefixes`` itself -- it must
    not name one cause for both, which is how this arm first shipped: a glob-scoped
    consumer was told git had failed on a run where git answered fine.
    """
    if tracked_files is None:
        return None
    prefixes, unresolvable = resolve_scope_prefixes(scope_paths)
    if prefixes is None:
        return {
            "tracked_file_count": len(tracked_files),
            "uncovered_file_count": 0,
            "uncovered_top_level": [],
        }
    if unresolvable:
        return None

    def _covered(path: str) -> bool:
        return any(path == scope or path.startswith(f"{scope}/") for scope in prefixes)

    uncovered = sorted(path for path in tracked_files if not _covered(path))
    return {
        "tracked_file_count": len(tracked_files),
        "uncovered_file_count": len(uncovered),
        "uncovered_top_level": sorted({path.split("/", 1)[0] for path in uncovered}),
    }


DID_NOT_JUDGE = (
    "whether a clone below nose's own scan-cost size floor (FULL_SCAN_MIN_SIZE in "
    "dup_ratchet_scan.py) is duplication -- that floor is a scan-cost choice, not a "
    "duplication judgment",
    "whether a clone outside nose's own detection modes (syntax,semantic,near) "
    "exists -- a mode nose does not run is invisible to this gate by construction",
    "whether an overlay classification (intentional/fixable) in dup-review.json is "
    "still accurate -- the overlay's own claim is trusted here, never independently "
    "re-checked",
)


def _scope_did_not_judge(
    scope_paths: list[str], coverage: dict | None, *, tracked_known: bool
) -> tuple[list[str], list[str]]:
    """The scope-coverage half of ``did_not_judge``, as ``(entries, message_lines)``.

    The one genuinely countable gap in ``DID_NOT_JUDGE``: how much of this repo
    ``scope_paths`` never reaches. Computed fresh from ``coverage`` (this run's own
    ``dup_ratchet_lib.scope_coverage()`` result) every call -- never a number fixed
    at authoring time.

    Says NOTHING about whether the code scan ran, and takes no ``code_reason``. Two
    drafts tried: the first asserted the scanner fell back to its own DEFAULT_PATHS
    whenever ``scope_paths`` was empty, the second flipped that on ``code_reason``
    being set. Both were false, because ``code_reason`` is a FAILURE STRING and not
    scan provenance -- its producers sit on BOTH SIDES of the fallback line (a missing
    nose binary returns before it; a nose scan error and an unreadable member span
    return after it, having scanned; the injected-inventory route never reaches it at
    all). No count of them here on purpose: a draft that said "four" was off by one
    against the return sites, which is the same restated-count defect this file removed
    from the comment below. Whether the scan produced a result is the CALLER's entry,
    keyed on the fact rather than inferred from a string.
    """
    if coverage is None:
        # Ordered before the empty-`scope_paths` arm and therefore reachable WITH an
        # empty scope, where "files outside scope_paths" is the entire repo. Naming
        # the whole tree as the unjudged population is exactly the overstatement the
        # arm below refuses to make, so the two states are phrased separately rather
        # than letting guard order decide which claim gets made.
        if not scope_paths:
            entry = (
                "which files this run reached -- scope_paths is empty AND git could "
                "not be asked, so neither the scanned set nor the tracked set is known"
            )
        else:
            # `coverage is None` has more than one cause, and naming the wrong one is
            # worse than naming none: a glob-scoped consumer was told "git could not be
            # asked" on a run where git answered fine, which sends an operator to debug
            # their checkout instead of their scope config. Each cause is asked for
            # separately and every true one is reported, so adding a third cause to
            # `scope_coverage` cannot silently inherit this sentence.
            causes = []
            if not tracked_known:
                causes.append("git could not be asked for the tracked file list")
            _, unresolvable = resolve_scope_prefixes(scope_paths)
            if unresolvable:
                causes.append(
                    "scope_paths carries "
                    + ", ".join(repr(item) for item in unresolvable)
                    + ", which this gate cannot compare literally against a "
                    "repo-relative path"
                )
            if not causes:
                # Unreachable against today's `scope_coverage`, which returns None only
                # for the two causes above. Kept because the failure mode of a future
                # third cause is an empty join -- a sentence naming no cause at all,
                # which reads as a formatting bug rather than as the unknown it is.
                causes.append("this gate could not resolve the question this run")
            entry = (
                "how many tracked files sit outside scope_paths -- "
                + " and ".join(causes)
                + ", so even that count is unknown (not zero)"
            )
        return [entry], [f"SCOPE: scope_paths={scope_paths}; {entry}."]
    if not scope_paths:
        # Reporting the whole tree as uncovered here would be the opposite of this
        # field's job: a gate added to say honestly what it did not cover, overstating
        # its own gap. So the entry names the gap that IS real -- this gate cannot name
        # the file set the code scan reached -- and stops there.
        #
        # It deliberately does not say whether the scanner fell back to its own
        # DEFAULT_PATHS. That is scan provenance, it is not visible from this function,
        # and both drafts that claimed it shipped a falsehood. The message prefix said
        # "(scanner defaults used)" for the same reason and is gone with it.
        entry = (
            "which files the code scan reached -- scope_paths is empty, so this gate "
            "cannot name the set"
        )
        return [entry], [f"SCOPE: scope_paths=[]; {entry}."]
    uncovered = coverage["uncovered_file_count"]
    total = coverage["tracked_file_count"]
    outside = ", ".join(coverage["uncovered_top_level"]) or "none"
    # "CODE family", not "family". The DOC arm does not read scope_paths at all --
    # inventory_doc_duplicates scans from DEFAULT_SCAN_PATH = "." -- and a new doc
    # family sets hard_block just as a code family does. The unqualified sentence was
    # false, and false in the direction that gets a REAL block dismissed: an operator
    # reading "never forms a family from them" next to a doc finding under `docs/`
    # concludes the finding is out of scope or a gate bug.
    entry = (
        f"any of the {uncovered} tracked file(s) outside scope_paths (top-level: "
        f"{outside}) -- this scan never forms a CODE family from them (the doc arm "
        f"scans the repo root and its findings do block)"
    )
    return [entry], [
        # "admits ... by path", not "covers". The numerator is tracked files whose path
        # sits under a scope prefix; it is NOT the count the scanner parsed, which is
        # smaller by an unknown margin (size floors, non-source files, parseability).
        # The over-count is conservative on the uncovered side and flattering on this
        # one, so the flattering side gets the qualifier.
        f"SCOPE: scope_paths={scope_paths} admits {total - uncovered}/{total} "
        f"tracked file(s) by path (not all are parsed); {entry}."
    ]
