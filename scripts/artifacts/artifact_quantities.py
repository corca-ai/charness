"""Named quantities: state a count ONCE, restate it by reference.

THE FAILURE THIS ANSWERS, measured. Across four claims-review rounds on v6.3.0,
the single most repeated defect was one number written in two places with two
values, inside prose that had been partially updated:

- "the Slice Log totals ten across the slices" / "twelve" -- ten was the count
  from before slice A's findings were added, by the same repair round that then
  "corrected the counts" and did not recount.
- "twenty-one" restated as "the nine" three paragraphs on.
- "the first claims round returned unproven" beside "two claims rounds".
- "four code-reading rounds" beside "seven bounded rounds".

Every one is a restatement drifting from its original. None is catchable by a
reader who does not already know the true value, which is why four rounds of
careful review kept finding a new one.

THE ASYMMETRY THAT PROVES THE MECHANISM. In the same session, by the same
author, the same class of mistake was made in release NOTES -- and caught in
zero seconds, three times, by `lint_release_narrative`, which refuses a bare
quantity in prose and re-derives every number from the tree. Notes have that
machinery. Goals and retros do not, so the identical mistake cost four rounds.
This module extends the cheaper half of that discipline to them.

WHAT IT DOES NOT DO. It does not derive values from the tree -- most of these
counts (blockers found by a reviewer, rounds run) have no tree to derive from.
It enforces the weaker but sufficient property: a quantity written more than
once must agree with itself. That is enough, because every failure above was a
disagreement, not a lone wrong number.

    {{q:total-blockers=27}} blockers, of which {{q:class-carrying=12}} were ...
    ... later ...
    of the {{q:total-blockers=27}} above, ...

A mismatch is reported with every site and value, so the author sees the drift
rather than being told a number is "wrong" with no second reading to compare.

SCOPE LIMIT, stated because the corpus's normal shape crosses it. Consistency is
checked PER FILE. A goal and its retro routinely restate each other's counts, and
this catches none of that -- the v6.3.0 issue count was wrong in both artifacts
simultaneously and agreed with itself inside each. Cross-artifact reconciliation
would need a declared owner per quantity; that is not built, and pretending
otherwise here would be the same defect one layer up.
"""
from __future__ import annotations

import re

#: `{{q:<id>=<value>}}`. The id is kebab-case; the value runs to the closing
#: braces so `1,234` and `~14` are expressible without escaping.
QUANTITY_RE = re.compile(r"\{\{q:([a-z0-9][a-z0-9-]*)=([^}]*)\}\}")


def quantity_sites(text: str) -> list[tuple[int, str, str]]:
    """Every `{{q:...}}` marker as `(line_number, id, value)`, 1-indexed."""
    sites: list[tuple[int, str, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        for match in QUANTITY_RE.finditer(line):
            sites.append((number, match.group(1), match.group(2).strip()))
    return sites


def inconsistent_quantities(text: str) -> list[dict[str, object]]:
    """Quantity ids stated with more than one distinct value.

    A single-site quantity is never a finding: this checks self-consistency, not
    correctness, and one statement cannot disagree with itself. That is a real
    limit and is stated plainly rather than papered over -- a lone wrong number
    still needs a reader.
    """
    by_id: dict[str, list[tuple[int, str]]] = {}
    for number, ident, value in quantity_sites(text):
        by_id.setdefault(ident, []).append((number, value))

    findings: list[dict[str, object]] = []
    for ident, sites in sorted(by_id.items()):
        values = {value for _, value in sites}
        if len(values) <= 1:
            continue
        findings.append({
            "kind": "inconsistent-quantity",
            "id": ident,
            "values": sorted(values),
            "sites": [{"line": number, "value": value} for number, value in sites],
            "detail": (
                f"`{ident}` is stated with {len(values)} different values "
                f"({', '.join(sorted(values))}). A restatement that drifts from its "
                "original is the defect this marker exists to make impossible; fix the "
                "count once and every site follows."
            ),
        })
    return findings


def render(text: str) -> str:
    """Strip markers to their values, for a human-readable rendering.

    Kept beside the checker so a consumer never hand-maintains a second copy of
    the marker syntax to display it.
    """
    return QUANTITY_RE.sub(lambda m: m.group(2).strip(), text)
