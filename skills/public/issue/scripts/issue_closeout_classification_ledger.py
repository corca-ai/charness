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

import re
from typing import Any, Callable

KNOWN_CLASSIFICATIONS = (
    "bug",
    "feature",
    "deferred-work",
    "question",
    "decision-needed",
    "consolidated",
)
_TARGETED_CLASSIFICATION_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?Classification(?:\*\*)?\s+(?P<target>[^:]+?)(?:\*\*)?\s*:\s*(?P<value>.*?)\s*$",
    re.IGNORECASE,
)
_GLOBAL_CLASSIFICATION_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?Classification(?:\*\*)?\s*:\s*(?P<value>.*?)\s*$",
    re.IGNORECASE,
)
_TARGET_RE = re.compile(r"^#(?P<number>[0-9]+)$")


class ClassificationResolutionError(RuntimeError, ValueError):
    """The carrier does not declare one unambiguous classification authority."""


def _classification_declarations(lines: list[str]) -> tuple[dict[int, str], list[str]]:
    """Read declarations without erasing duplicate or malformed authority."""
    targeted: dict[int, str] = {}
    global_values: list[str] = []
    for line in lines:
        match = _TARGETED_CLASSIFICATION_RE.match(line)
        if match is not None:
            target = _TARGET_RE.fullmatch(match.group("target").strip())
            if target is None:
                raise ClassificationResolutionError(
                    "targeted classification declarations must use `Classification #N: <value>`"
                )
            number = int(target.group("number"))
            if number in targeted:
                raise ClassificationResolutionError(
                    f"duplicate targeted classification declaration for #{number}"
                )
            targeted[number] = match.group("value").strip().lower()
            continue
        match = _GLOBAL_CLASSIFICATION_RE.match(line)
        if match is not None:
            global_values.append(match.group("value").strip().lower())
    return targeted, global_values


def resolve_classifications(
    text: str,
    numbers: list[int],
    *,
    scalar_classification: str | None,
    fallback_classification: str | None,
    strip_fences: Callable[[str], list[str]],
) -> dict[int, str]:
    """Resolve a total issue-owned classification map before any provider read.

    A targeted declaration is a one-number ``Classification #N: value`` line.
    Once one exists, only a complete exact map is authoritative; a caller's
    scalar classification is also rejected because it would create mixed
    authority.  With no targeted declaration, the historical scalar/global /
    inferred fallback remains in force.
    """
    return _resolve_declarations(
        _classification_declarations(strip_fences(text)), numbers,
        scalar_classification, fallback_classification,
    )


def _resolve_declarations(
    declarations: tuple[dict[int, str], list[str]],
    numbers: list[int],
    scalar_classification: str | None,
    fallback_classification: str | None,
) -> dict[int, str]:
    """Resolve already-parsed declarations without losing duplicate validation."""
    expected = list(numbers)
    if len(set(expected)) != len(expected):
        raise ClassificationResolutionError("closeout invocation contains duplicate issue numbers")
    targeted, global_values = declarations
    if targeted:
        if global_values:
            raise ClassificationResolutionError(
                "targeted classifications cannot be mixed with global Classification authority"
            )
        if scalar_classification is not None:
            raise ClassificationResolutionError(
                "targeted classifications cannot be mixed with scalar classification authority"
            )
        unknown = sorted({value for value in targeted.values() if value not in KNOWN_CLASSIFICATIONS})
        if unknown:
            raise ClassificationResolutionError(f"unknown targeted classification(s): {unknown}")
        expected_set = set(expected)
        declared_set = set(targeted)
        extra = sorted(declared_set - expected_set)
        missing = sorted(expected_set - declared_set)
        if extra:
            raise ClassificationResolutionError(
                f"targeted classifications contain extra/foreign issue numbers: {extra}"
            )
        if missing:
            raise ClassificationResolutionError(
                f"targeted classifications are missing issue numbers: {missing}"
            )
        return {number: targeted[number] for number in expected}

    value = scalar_classification
    if value is None:
        if len(set(global_values)) > 1:
            raise ClassificationResolutionError(
                "multiple conflicting global Classification declarations"
            )
        value = global_values[0] if global_values else fallback_classification
    if value not in KNOWN_CLASSIFICATIONS:
        raise ClassificationResolutionError(f"unknown classification: {value}")
    return {number: value for number in expected}


def resolve_closeout_classifications(
    body: str,
    numbers: list[int],
    classification: str | None,
    supplied: dict[int, str] | None = None,
    *,
    strip_fences: Callable[[str], list[str]],
) -> dict[int, str]:
    """Reconcile supplied artifact authority with declarations in the carrier.

    A supplied map replaces inference, never parsing: malformed, duplicate, or
    conflicting carrier declarations remain refusals even when artifacts exist.
    """
    declarations = _classification_declarations(strip_fences(body))
    if supplied is None:
        return _resolve_declarations(declarations, numbers, classification, classification or "bug")
    declared = _resolve_declarations(declarations, numbers, None, "bug") if any(declarations) else None
    return _reconcile_supplied(numbers, classification, supplied, declared)


def _reconcile_supplied(
    numbers: list[int],
    classification: str | None,
    supplied: dict[int, str],
    declared: dict[int, str] | None = None,
) -> dict[int, str]:
    """Validate complete artifact authority, then reject carrier disagreement."""
    if (
        len(set(numbers)) != len(numbers)
        or set(supplied) != set(numbers)
        or any(value not in KNOWN_CLASSIFICATIONS for value in supplied.values())
    ):
        raise ClassificationResolutionError(
            "supplied classifications must be a complete issue->classification map"
        )
    if classification is not None:
        raise ClassificationResolutionError(
            "supplied classifications cannot be mixed with scalar classification authority"
        )
    if declared is not None:
        conflicts = sorted(number for number in numbers if declared[number] != supplied[number])
        if conflicts:
            raise ClassificationResolutionError(
                f"carrier classifications conflict with supplied artifact classifications: {conflicts}"
            )
    return {number: supplied[number] for number in numbers}


def resolve_closeout_invocation(
    body: str,
    artifacts: list[dict[str, Any]],
    bare_numbers: list[int],
    *,
    strip_fences: Callable[[str], list[str]],
) -> dict[str, Any]:
    """Join active artifact scopes into one carrier invocation, retaining sources.

    Artifact maps are already parsed against their own targets. Their union is
    the citation scope, including artifact-only targets whose missing message
    close keywords must still be refused. Paused briefs never enter this join.
    """
    supplied: dict[int, str] = {}
    sources: dict[int, list[str]] = {}
    for artifact in artifacts:
        artifact_values = artifact.get("classifications")
        values = _reconcile_supplied(
            artifact["numbers"], None,
            artifact_values if artifact_values is not None else {
                number: artifact["classification"] for number in artifact["numbers"]
            },
        )
        for number, value in values.items():
            if number in supplied and supplied[number] != value:
                raise ClassificationResolutionError(
                    f"conflicting artifact classifications for #{number}: "
                    f"{sources[number]} and {artifact['path']}"
                )
            supplied[number] = value
            sources.setdefault(number, []).append(artifact["path"])
    numbers = sorted(set(supplied) | set(bare_numbers))
    declarations = _classification_declarations(strip_fences(body))
    if any(declarations):
        declared = _resolve_declarations(declarations, numbers, None, "bug")
    else:
        declared = {number: supplied.get(number, "bug") for number in numbers}
    classifications = _reconcile_supplied(
        numbers, None,
        {number: supplied.get(number, declared[number]) for number in numbers},
        declared,
    )
    return {
        "numbers": numbers,
        "classifications": classifications,
        "source_artifact": artifacts[0]["path"] if len(artifacts) == 1 else None,
        "source_artifacts": {number: sources.get(number, []) for number in numbers},
        "bare_close_numbers": bare_numbers,
    }


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
