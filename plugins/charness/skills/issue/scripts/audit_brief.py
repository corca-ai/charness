#!/usr/bin/env python3
"""Audit transcript events to verify the resolution brief precedes mutations.

The audit consumes a transcript JSON that lists ordered events for one or more
issue-resolve fix-units. A fix-unit fails two ways. First, whatever its class,
when a `mutation` event appears before any recognized `classification` event for
that fix-unit — omission used to disarm the check entirely. Second, when its
classification is `feature` or `deferred-work` and a `mutation` event appears
before either a `brief` event or a `trivial_brief` event for that fix-unit.

Transcript schema (single JSON file):

    {
      "events": [
        {"kind": "classification", "issue": 143, "classification": "feature"},
        {"kind": "brief", "issue": 143, "open_decisions": 0},
        {"kind": "mutation", "issue": 143, "tool": "Edit"}
      ]
    }

A `trivial_brief` event replaces a full brief and is acceptable for fix-units
that legitimately use the trivial-feature short-circuit.

Exit codes:
    0 = ok (all feature/deferred-work fix-units satisfy the brief contract)
    1 = audit failed (one or more fix-units violated the contract)
    2 = transcript shape error
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRE_BRIEF_CLASSIFICATIONS = ("feature", "deferred-work")
EVENT_KINDS = ("classification", "brief", "trivial_brief", "mutation", "close")
# The vocabulary `check_issue_closeout_commit_msg.py` accepts on a closeout commit.
# `consolidated` joins this set and NOT `FLOOR_EXEMPT_CLASSIFICATIONS`: a close that
# claims nothing about the defect still owes a floor, just a different one
# (`issue_consolidated_closeout`). Making it exempt would open the relabelling path
# where an inconvenient bug reaches the light floor by changing one word.
KNOWN_CLASSIFICATIONS = (
    "bug", "feature", "deferred-work", "question", "decision-needed", "consolidated",
)


def load_transcript(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "events" not in raw:
        raise ValueError("transcript must be a JSON object with an 'events' list")
    events = raw["events"]
    if not isinstance(events, list):
        raise ValueError("transcript 'events' must be a list")
    if not events:
        # An empty event list is not a clean run: the audit read nothing and used
        # to report `audit ok: 0 fix-unit(s) checked`, exit 0 — the same
        # absent-input-certifies-itself shape this checker exists to catch.
        raise ValueError("transcript records no events; there is nothing to audit")
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError(f"event #{index} is not an object")
        kind = event.get("kind")
        if kind not in EVENT_KINDS:
            raise ValueError(f"event #{index} has unknown kind: {kind!r}")
        if "issue" not in event:
            raise ValueError(f"event #{index} missing 'issue'")
        try:
            int(event["issue"])
        except (TypeError, ValueError) as exc:
            # Without this the crash surfaced from `audit()`, outside main()'s
            # try block: a traceback and exit 1, indistinguishable from a real
            # audit failure.
            raise ValueError(f"event #{index} has a non-numeric 'issue': {event['issue']!r}") from exc
    return events


def audit(events: list[dict[str, Any]]) -> dict[str, Any]:
    state: dict[int, dict[str, Any]] = {}
    violations: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        issue = int(event["issue"])
        unit = state.setdefault(
            issue,
            {
                "classification": None,
                "brief_seen": False,
                "trivial_seen": False,
                "first_mutation_index": None,
            },
        )
        kind = event["kind"]
        if kind == "classification":
            unit["classification"] = event.get("classification")
        elif kind in ("brief", "trivial_brief"):
            unit[("trivial_seen" if kind == "trivial_brief" else "brief_seen")] = True
        elif kind == "mutation":
            if unit["first_mutation_index"] is None:
                unit["first_mutation_index"] = index
            classification = unit["classification"]
            if classification is None or classification not in KNOWN_CLASSIFICATIONS:
                # The contract was armed only by a declared, recognized
                # classification, so omitting the event — or recording it after the
                # mutation, or misspelling its value — disarmed the whole check and
                # still reported `audit ok`. Omission is not evidence of triviality.
                violations.append(
                    {
                        "issue": issue,
                        "classification": classification,
                        "event_index": index,
                        "reason": (
                            "mutation event for issue "
                            f"#{issue} with no recognized classification recorded first "
                            f"(saw {classification!r})"
                        ),
                    }
                )
            elif (
                classification in REQUIRE_BRIEF_CLASSIFICATIONS
                and not unit["brief_seen"]
                and not unit["trivial_seen"]
            ):
                violations.append(
                    {
                        "issue": issue,
                        "classification": classification,
                        "event_index": index,
                        "reason": (
                            "mutation event preceded any brief or trivial_brief event "
                            f"for {classification}-class issue #{issue}"
                        ),
                    }
                )
    summary = {
        "ok": not violations,
        "fix_units": {
            issue: {
                "classification": unit["classification"],
                "brief_seen": unit["brief_seen"],
                "trivial_seen": unit["trivial_seen"],
                "first_mutation_index": unit["first_mutation_index"],
            }
            for issue, unit in state.items()
        },
        "violations": violations,
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", type=Path, required=True, help="Path to the transcript JSON file listing fix-unit events")
    parser.add_argument("--json", action="store_true", help="Emit the full brief-audit payload as JSON")
    args = parser.parse_args()

    try:
        events = load_transcript(args.transcript)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        message = {"ok": False, "error": str(exc), "transcript": str(args.transcript)}
        if args.json:
            print(json.dumps(message, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(f"transcript error: {exc}", file=sys.stderr)
        return 2

    summary = audit(events)
    summary["transcript"] = str(args.transcript)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if summary["ok"]:
            print(f"audit ok: {len(summary['fix_units'])} fix-unit(s) checked")
        else:
            print(f"audit failed: {len(summary['violations'])} violation(s)", file=sys.stderr)
            for violation in summary["violations"]:
                print(f"  - {violation['reason']}", file=sys.stderr)
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
