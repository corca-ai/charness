#!/usr/bin/env python3
"""Typed premise state for one open issue: is the record still true of the tree?

WHY THIS EXISTS, AND WHY IT IS NOT A SECOND BACKLOG READER. The backlog-recount floor is
presence-only: a goal must record what it claims and what it does not. That floor makes the
reasoning visible; it never asks whether the issues themselves are still true. This module
is the re-check, and the originating issue's own text names the constraint it must obey --
building a second backlog reader inside `achieve` would be the wrong repair. So the tracker
is read through the `issue` skill's backend, the contractual owner and now the only
implementation, and this file holds nothing but verdict logic. Residue DETECTION lives in
`recount_residue_lib`.

THE INSTANCE THIS IS BUILT FROM, AND WHY THE OBVIOUS TYPING IS WRONG. The originating issue
was FIXED before it was last read, and nobody re-read it after shipping its fix. But a
two-state `premise-holds` / `premise-refuted` typing would have pushed the WRONG WAY on
exactly that instance: its premise WAS refuted and the correct answer was still DO NOT
CLOSE, because its second part was live and the goal that shipped the first part said so.
A refuted premise is not a close signal. Hence four states, and hence
`premise-refuted-with-live-residue` being a REFUSAL to recommend rather than a candidate.

WHAT THIS MODULE MAY AND MAY NOT DECIDE (north star P5). It renders a premise state and
STOPS. Nothing here closes an issue, recommends closing one, or emits a disposition a
caller could thread into `issue_close`. The PREMISE judgement -- "does this issue still
describe the tree" -- is CALLER-SUPPLIED and defaults to `unverifiable-by-machine`. A
caller that supplies nothing gets `unverifiable-by-machine` for every issue, never `holds`.

EVERY SIGNAL IS STRUCTURAL. Nothing here reads human wording. Earlier versions matched
hand-written English and Korean phrase lists and a hand-written list of "suggested
direction" heading words; all of it was repo-specific hardcoding inside a portable skill,
and its thresholds had been fitted to this repo's own backlog until the output looked
right. What survives is what a machine can actually read: a typed `Premise-residue:` marker
in a durable record, and unchecked `- [ ]` task items in the issue body. Both mean exactly
one thing, in every repo and every language.

THE ASYMMETRY. Machine facts may only DOWNGRADE a caller's `refuted` toward refusal; none
may upgrade anything toward `premise-refuted-clean`. Bounded review found that held inside
`classify` and failed at the TOOL level: an unread body, an absent record root, an
unreadable file, and a root that existed but was never read each silently removed residue,
which is an upgrade by subtraction. So `classify` reads the scan's provenance and refuses
when a channel did not RUN. A channel that did not run is not a channel that came back clean.
"""
from __future__ import annotations

import re

# The four states. `premise-refuted-with-live-residue` is not a severity between the other
# two -- it is a different KIND of answer, a refusal to recommend, and callers must not
# collapse it into `premise-refuted-clean` by treating residue as advisory.
PREMISE_HOLDS = "premise-holds"
PREMISE_REFUTED_CLEAN = "premise-refuted-clean"
PREMISE_REFUTED_WITH_LIVE_RESIDUE = "premise-refuted-with-live-residue"
UNVERIFIABLE = "unverifiable-by-machine"

STATES = (PREMISE_HOLDS, PREMISE_REFUTED_CLEAN, PREMISE_REFUTED_WITH_LIVE_RESIDUE, UNVERIFIABLE)

# Only these two are accepted from a caller. `unverifiable-by-machine` is what the ABSENCE
# of a judgement produces; a caller cannot assert it, because "I looked and could not tell"
# and "I did not look" must not be the same record.
CALLER_VERDICTS = ("holds", "refuted")

_OPEN_TASK_RE = re.compile(r"^\s*[-*+]\s+\[ \]\s+(\S.*)$", re.MULTILINE)
_DONE_TASK_RE = re.compile(r"^\s*[-*+]\s+\[[xX]\]\s+\S", re.MULTILINE)


def body_open_task_items(body: str) -> dict:
    """Unchecked task-list items in the body, which are live asks by construction.

    The only body-side signal, and the only one that deserved to survive: `- [ ]` is a
    declared markdown/GitHub form with exactly one meaning, identical in every repo and
    every language. An unchecked box is an ask the issue itself declares outstanding.
    """
    open_items = _OPEN_TASK_RE.findall(body or "")
    return {
        "open": len(open_items),
        "done": len(_DONE_TASK_RE.findall(body or "")),
        "first_open": open_items[0][:200] if open_items else None,
    }


def _channel_gaps(residue: dict, body_read: bool) -> list[str]:
    """Residue channels that did not RUN, as distinct from channels that came back clean.

    Each of these once silently produced `premise-refuted-clean`: an unread body meant "no
    open task", an absent artifact root meant "no record declined", an unreadable file meant
    its markers never existed, and a root that existed but was gitignored or fully excluded
    meant a verdict backed by zero files. None is evidence; all are MISSING evidence, and
    the stated asymmetry says missing evidence resolves toward refusal.
    """
    provenance = residue.get("provenance") or {}
    gaps: list[str] = []
    if not provenance.get("roots_present"):
        gaps.append(
            "no durable-record root was found under this repo root, so the record channel "
            "never ran -- check --repo-root"
        )
    elif not provenance.get("files_scanned"):
        gaps.append(
            "a durable-record root exists but ZERO record files were read (gitignored, "
            "excluded, or empty), so the record channel never ran"
        )
    unreadable = provenance.get("files_unreadable") or []
    if unreadable:
        gaps.append(
            f"{len(unreadable)} durable record file(s) could not be read, so any markers in "
            f"them were never read (first: {unreadable[0]})"
        )
    fenced = provenance.get("fenced_markers_skipped") or []
    if fenced:
        gaps.append(
            f"{len(fenced)} typed residue marker(s) sat inside fenced blocks and were not "
            f"read (first: {fenced[0]})"
        )
    if not body_read:
        gaps.append(
            "the issue body was not read, so the open-task channel never ran -- rerun with "
            "--with-bodies"
        )
    return gaps


def classify(
    *,
    caller_verdict: str | None,
    residue: dict,
    open_tasks: dict | None = None,
    body_read: bool = True,
) -> dict:
    """Combine the caller's premise judgement with structural facts into one typed state.

    Order encodes the design. An absent or unrecognised caller verdict is
    `unverifiable-by-machine` FIRST, before any machine fact is consulted, so residue can
    never manufacture a judgement the caller did not make. Then `holds` short-circuits. Only
    `refuted` reaches the residue branch -- and gaps are computed UNCONDITIONALLY, so a run
    that finds one marker and also failed to read the body reports both. The terminal state
    is the same either way; the reason is not, and a caller who overrides the finding needs
    to know half the evidence was missing.
    """
    if caller_verdict not in CALLER_VERDICTS:
        return {
            "state": UNVERIFIABLE,
            "reason": (
                "no caller premise judgement supplied -- this tool does not decide whether an "
                "issue still describes the tree; it renders what it can check around that "
                "judgement"
            ),
        }
    if caller_verdict == "holds":
        return {
            "state": PREMISE_HOLDS,
            "reason": "caller judged the issue still describes the tree",
        }

    causes: list[str] = []
    declining = residue.get("declining") or []
    if declining:
        first = declining[0]
        causes.append(
            f"{len(declining)} durable record(s) carry an explicit `Premise-residue:` marker "
            f"naming it, first at {first['path']}:{first['line']}"
        )
    open_count = (open_tasks or {}).get("open") or 0
    if open_count:
        causes.append(
            f"the body carries {open_count} unchecked task-list item(s), which the issue "
            f"itself declares outstanding (first: {(open_tasks or {}).get('first_open')})"
        )

    gaps = _channel_gaps(residue, body_read)
    if causes:
        reason = (
            "premise refuted, but " + "; and ".join(causes) + " -- this is a REFUSAL to "
            "recommend, not a close candidate; read the cited lines before deciding"
        )
        if gaps:
            reason += ". Separately, a residue channel did not RUN: " + "; and ".join(gaps)
        return {"state": PREMISE_REFUTED_WITH_LIVE_RESIDUE, "reason": reason}
    if gaps:
        return {
            "state": PREMISE_REFUTED_WITH_LIVE_RESIDUE,
            "reason": (
                "premise refuted and no residue was FOUND, but a residue channel did not RUN: "
                + "; and ".join(gaps)
                + " -- a channel that did not run is not a channel that came back clean, so "
                "this is a REFUSAL to recommend rather than a clean result"
            ),
        }
    return {
        "state": PREMISE_REFUTED_CLEAN,
        "reason": (
            "premise refuted; every structural channel ran and none fired -- no durable "
            "record carries a typed `Premise-residue:` marker naming it, and the body has no "
            "unchecked task item. The channels are STRUCTURAL by design: a decline written "
            "only as ordinary prose is deliberately NOT detected, so this is not a claim "
            "that nobody ever declined. Still a human's decision, not this tool's"
        ),
    }
