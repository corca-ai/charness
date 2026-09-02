#!/usr/bin/env python3
"""What each closeout classification OWES: its required fields, and its own extra rule.

Split from `issue_verify_closeout_body` on a concept boundary, not to dodge a line
cap: this file answers one question — given a classification, what must the carrier
carry — while the body reader answers a different one, which is how to read a field
out of markdown at all.

ONE DISPATCH ON CLASSIFICATION, NOT TWO. Adding the `consolidated` branch first
produced a second `if classification == ...` chain beside the existing one, and the
duplicate ratchet named the pair immediately -- correctly, because two dispatches on
the same key are two places to forget a classification. The table below holds both
halves of what a classification owes: the fields it must carry, and the extra checker
(when the rule is too rich to express as a field name).

`deferred-work` shares `feature`'s row: both close by DELIVERING something, so both
owe the implementation ledger. `question`/`decision-needed` fall through to the
default, which is the light branch they are exempt into.
"""
from __future__ import annotations

from typing import Callable

_JTBD = ("jtbd", ("jtbd",))

CLASSIFICATION_FIELDS: dict[str, list[tuple[str, tuple[str, ...]]]] = {
    "bug": [
        _JTBD,
        ("root_cause", ("root cause",)),
        ("debug_artifact", ("debug artifact",)),
        ("siblings", ("siblings", "sibling search")),
        ("prevention", ("prevention",)),
    ],
    "feature": [
        _JTBD,
        ("boundary", ("boundary",)),
        ("resolution_brief", ("resolution brief",)),
        ("implementation", ("implementation",)),
        ("prevention", ("prevention",)),
    ],
    # A consolidation implements nothing, so it owes no `Implementation:` and no
    # `Prevention:` -- demanding them would mean writing sentences that are not true.
    # `Consolidated into:` IS listed here, and the split with the extra check below is
    # deliberate: this row owns PRESENCE (so the surfaced draft shape and the enforced
    # fields round-trip, which a drift guard checks), while the extra check owns arity,
    # self-reference and the repair-claim contradiction. The extra check suppresses its
    # own missing-field message so one absence is still reported once.
    "consolidated": [_JTBD, ("consolidated_into", ("consolidated into",))],
}
# The SAME list object, deliberately -- but the rows are tuples and the accessor
# copies, so an editor cannot reshape `feature` by mutating `deferred-work`, and a
# caller cannot reshape the floor for four classifications at once by appending to
# what `classification_requirements` handed them.
CLASSIFICATION_FIELDS["deferred-work"] = CLASSIFICATION_FIELDS["feature"]

DEFAULT_FIELDS: list[tuple[str, tuple[str, ...]]] = [
    _JTBD,
    ("answer_or_decision", ("answer", "decision", "recorded decision")),
]


def has_classification_row(classification: str) -> bool:
    """Whether this classification has its OWN row, rather than falling through.

    The fallthrough at `classification_requirements` is silent by design, so a
    caller asking "does this classification have a row" cannot answer it by
    comparing the returned list to DEFAULT_FIELDS: a row whose value happened to
    equal the default would read as absent. Exposed for
    the authoring repository's closeout-parity gate, which must distinguish the
    two without reading the table as an attribute.
    """
    return classification in CLASSIFICATION_FIELDS


def classification_requirements(classification: str) -> list[tuple[str, tuple[str, ...]]]:
    """A COPY of the row, so a caller cannot reshape a proof surface's floor."""
    return list(CLASSIFICATION_FIELDS.get(classification, DEFAULT_FIELDS))


def build_extra_checks(
    *,
    ledger_counts,
    consolidated,
    first_field: Callable,
    substantive: Callable,
    self_numbers: Callable[[str], list[int]] | None = None,
    strip_fences: Callable[[str], str] | None = None,
    ledger=None,
    auto_closing_carriers: tuple[str, ...] = (),
) -> dict:
    """Per-classification rules that are richer than a field name.

    The collaborators are injected rather than imported so this module stays a
    plain table with no sibling-loader wiring, and so a caller can test either rule
    without standing up the other.
    """

    def bug_sibling_problems(text: str, fields: dict, carrier=None) -> list[str]:
        """What the sibling-search field must STATE, owned by the ledger-counts module:
        the decision/proof pair, and -- when it makes a counting claim -- population and
        removals as separate numbers."""
        return list(
            ledger_counts.missing_sibling_ledger_fields(
                first_field(fields, ("siblings", "sibling search")),
                substantive=substantive,
            )
        )

    def consolidated_problems(
        text: str, fields: dict, carrier=None, invoked_numbers: tuple[int, ...] = ()
    ) -> list[str]:
        """Destination arity, self-reference, and the repair-claim contradiction.

        `self_numbers` is threaded because without it the self-reference check
        silently never ran: `evaluate` defaults `self_number` to None and its guard
        is `is not None`, so `Consolidated into: <the issue being closed>` passed the
        wired path while passing only in the module's own direct-call test.
        """
        # Fences stripped first, as every other body reader in this package does.
        # Without it a fenced authoring template satisfied the destination field,
        # and a pasted log containing `Implementation:` triggered a FALSE refusal.
        body = strip_fences(text) if strip_fences is not None else text
        # A direct API close has an invoked number even when its body deliberately
        # contains no GitHub close keyword. Prefer that caller-owned identity; the
        # body scan remains the source for commit/PR carriers and direct helper use.
        numbers = list(invoked_numbers) or (self_numbers(body) if self_numbers is not None else [])
        return [
            f"consolidated:{problem}"
            for problem in consolidated.evaluate(
                body,
                self_number=numbers[0] if numbers else None,
                ledger=ledger,
                # The row above already reports an absent field; repeating it here made
                # one missing destination report twice, and two owners of one rule is
                # how they drift.
                report_missing=False,
                self_numbers=tuple(numbers),
                # The UNSTRIPPED body, for the close-keyword read only.
                raw_text=text,
                carrier_auto_closes=carrier in auto_closing_carriers,
            )["problems"]
        ]

    return {"bug": bug_sibling_problems, "consolidated": consolidated_problems}
