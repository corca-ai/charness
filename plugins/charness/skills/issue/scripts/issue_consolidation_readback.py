#!/usr/bin/env python3
"""The four facts a consolidated close needs from the TRACKER, not from its own prose.

`issue_consolidated_closeout` owns the body grammar and listed these four as
`not_checked_here`. Bounded review named that honestly-scoped list for what it also
was: four checks implemented nowhere, whose only effect was to appear in a payload no
consumer read. To a downstream operator that reads like handled work. This module is
the implementation, so the list stops being a promise.

WHY EACH ONE, AND WHAT IT COSTS TO SKIP IT. A consolidated close asserts exactly one
thing -- the content moved to a destination -- and every way that assertion can be
false is a way the work silently evaporates:

1. THE DESTINATION EXISTS. Consolidating into a number nobody created loses the issue
   outright, and a typo in an anchor is one keystroke.
2. THE DESTINATION IS OPEN AT CLOSE TIME. Moving work into an already-closed issue is
   the same evaporation with a plausible-looking trail: both issues now read `closed`
   and nothing says the second one absorbed the first.
3. THE DESTINATION'S BODY NAMES THIS ISSUE. This is the load-bearing one. It forces
   the question "does the content actually live somewhere?" without answering
   "therefore this is resolved", and prose in the CLOSING issue cannot satisfy it --
   only an edit to the destination can. Without it, twenty issues can point at an
   umbrella that never mentions any of them.
4. THE DESTINATION IS NOT ITSELF A CONSOLIDATION. Chains defeat the whole point: A
   into B into C leaves a reader following pointers, and a cycle leaves them looping.

WHAT THIS MODULE WILL NOT DO. It renders findings and stops. It never closes an
issue, never edits a destination to make check 3 pass, and never downgrades a failed
readback to a warning. A readback that could not RUN is reported as `unknown`, never
as satisfied -- the distinction the sibling premise-state seam had to learn twice.
"""
from __future__ import annotations

import re

# `Consolidated into:` in a DESTINATION's body means that destination is itself a
# consolidation, which is check 4. Deliberately the same spelling the closing side
# writes, so a chain is detected by the marker the contract already defines rather
# than by guessing at wording.
_CHAIN_RE = re.compile(
    r"^[ \t]*[-*+]?[ \t]*[`*_~]*consolidated\s+into[`*_~]*[ \t]*:[ \t]*\S",
    re.IGNORECASE | re.MULTILINE,
)

OPEN_STATE = "OPEN"


def _anchor_re(number: int) -> "re.Pattern[str]":
    """The forms a destination body may use to name the issue that moved into it."""
    return re.compile(rf"(?:#{number}(?!\d)|issues/{number}(?!\d))")


def evaluate_destination(
    payload: dict | None,
    *,
    source_number: int,
    destination_number: int,
    expected_repo: str | None = None,
    answer_repo=None,
) -> dict:
    """The four checks, over a destination payload already fetched from the backend.

    Pure: the caller owns the backend call, so this is testable without a tracker and
    a host with a different backend gets the same verdict logic. `payload` is `None`
    when the fetch could not run -- which yields `unknown`, not `ok`.
    """
    if payload is None:
        return {
            "ok": False,
            "state": "unknown",
            "problems": [
                f"could not read destination #{destination_number} from the backend, so none "
                "of the four consolidation facts were checked -- a readback that did not RUN "
                "is not a readback that passed"
            ],
        }

    if not isinstance(payload, dict):
        # A backend that answered with a list or a bare string is a backend problem,
        # not a destination problem. Previously this reached `.get` and escaped as an
        # AttributeError traceback, which contradicts this module's own rule that any
        # backend failure is "did not run".
        return {
            "ok": False,
            "state": "unknown",
            "problems": [
                f"the backend answered about destination #{destination_number} with a "
                f"{type(payload).__name__}, not an issue payload, so none of the four "
                "consolidation facts were checked -- a readback that did not RUN is not a "
                "readback that passed"
            ],
        }

    problems: list[str] = []
    exists = bool(payload) and payload.get("number") is not None
    if not exists:
        problems.append(
            f"destination #{destination_number} does not exist -- consolidating into a "
            "number nobody created loses the issue outright"
        )
        return {"ok": False, "state": "missing", "problems": problems}

    # BEING TOLD IS NOT OBEYING. The sibling expected-state loop already learned this:
    # a backend can answer with the right shape about the wrong issue, and a wrong-repo
    # answer carries the RIGHT number. Without these two checks a destination anchor
    # qualified with another `owner/repo` would still be fetched against the SOURCE
    # repo, and an unrelated local issue of the same number whose body happens to
    # mention the source would pass all four checks.
    answered_number = payload.get("number")
    if answered_number is not None and int(answered_number) != destination_number:
        problems.append(
            f"the backend answered about #{answered_number} when asked for destination "
            f"#{destination_number} -- an answer about a different issue is not evidence "
            "about this one"
        )
    if expected_repo and answer_repo is not None:
        answered_repo = answer_repo(payload)
        if answered_repo and answered_repo != expected_repo:
            problems.append(
                f"the backend answered about {answered_repo}#{destination_number} when "
                f"asked for {expected_repo} -- a wrong-repo answer carries the right number"
            )

    state = str(payload.get("state") or "").upper()
    if state != OPEN_STATE:
        problems.append(
            f"destination #{destination_number} is {state or 'of unknown state'}, not OPEN -- "
            "moving work into an already-closed issue evaporates it while leaving a "
            "plausible trail, because both issues then read closed and nothing says one "
            "absorbed the other"
        )

    body = payload.get("body") or ""
    if not _anchor_re(source_number).search(body):
        problems.append(
            f"destination #{destination_number}'s body does not name #{source_number} -- "
            "this is the check that forces 'does the content actually live somewhere?', and "
            "only an edit to the DESTINATION can satisfy it; prose in the closing issue "
            "cannot"
        )

    if _CHAIN_RE.search(body):
        problems.append(
            f"destination #{destination_number} is itself consolidated into something else "
            "-- chains leave a reader following pointers and a cycle leaves them looping, so "
            "consolidate into the issue that will actually hold the work"
        )

    return {
        "ok": not problems,
        "state": state or "unknown",
        "names_source": bool(_anchor_re(source_number).search(body)),
        "is_chain": bool(_CHAIN_RE.search(body)),
        "problems": problems,
    }


def verify_consolidation(
    *,
    source_number: int,
    destination_number: int,
    fetch,
) -> dict:
    """Fetch the destination and render the four facts.

    `fetch(number) -> dict | None` is injected so this module needs no backend wiring
    of its own and a caller can pass the `issue` skill's existing view helper. A fetch
    that raises is caught and reported as a readback that did not run, because the one
    thing this must never do is let a backend problem read as a satisfied check.
    """
    try:
        payload = fetch(destination_number)
    except Exception as exc:  # noqa: BLE001 - any backend failure is "did not run"
        return {
            "ok": False,
            "state": "unknown",
            "problems": [
                f"reading destination #{destination_number} failed ({exc}), so none of the "
                "four consolidation facts were checked -- a readback that did not RUN is not "
                "a readback that passed"
            ],
        }
    return evaluate_destination(
        payload, source_number=source_number, destination_number=destination_number
    )


def readbacks_for_closeout(
    *,
    numbers: list[int],
    destinations: list[int],
    fetch,
    applies: bool = True,
    expected_repo: str | None = None,
    answer_repo=None,
) -> list[dict]:
    """Every (source, destination) verdict for one consolidated closeout body.

    Lives here rather than in the verifier for two reasons: this module owns
    consolidation readbacks, and the verifier is at its complexity and length ceiling
    -- a proof surface is the wrong place to spend the last of either. `fetch` is
    injected so the backend stays the verifier's business and this stays testable
    without a tracker.

    `applies` is False for every classification but `consolidated`, and it is a
    PARAMETER rather than a caller-side `if` so the empty result is this module's
    answer rather than something a caller can forget to ask for.

    The destination is fetched ONCE and evaluated per source. A carrier closing twenty
    issues into one umbrella would otherwise make twenty identical backend calls for the
    same payload.
    """
    if not applies:
        return []
    readbacks: list[dict] = []
    seen_destination_problems: set[str] = set()
    for destination_number in destinations:
        fetch_error = None
        try:
            payload = fetch(destination_number)
        except Exception as exc:  # noqa: BLE001 - any backend failure is "did not run"
            payload = None
            fetch_error = str(exc)
        for number in numbers:
            report = evaluate_destination(
                payload,
                source_number=number,
                destination_number=destination_number,
                expected_repo=expected_repo,
                answer_repo=answer_repo,
            )
            if fetch_error and report["problems"]:
                report["problems"][0] += f" ({fetch_error})"
            # Three of the four facts are DESTINATION-scoped, so re-emitting them per
            # source produced ~40 byte-identical lines for twenty closes and buried every
            # other finding. Each distinct problem is surfaced once; the per-source
            # verdicts still carry the full report for anyone reading the payload.
            fresh = [
                problem
                for problem in report["problems"]
                if problem not in seen_destination_problems
            ]
            seen_destination_problems.update(report["problems"])
            readbacks.append(
                {
                    "source": number,
                    "destination": destination_number,
                    **report,
                    "unreported_duplicates": len(report["problems"]) - len(fresh),
                    "problems_to_surface": fresh,
                }
            )
    return readbacks
