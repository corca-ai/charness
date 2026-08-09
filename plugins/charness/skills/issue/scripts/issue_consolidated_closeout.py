#!/usr/bin/env python3
"""The `consolidated` disposition: a close that claims NOTHING about the defect.

WHY A SIXTH CLASSIFICATION RATHER THAN REUSING ONE. Consolidating a backlog moves
issues; it does not fix them. Neither existing branch fits that, and forcing either
one costs the closeout floor its meaning:

- The RESOLUTION classifications (`bug` / `feature` / `deferred-work`) demand
  `Implementation:`, `Prevention:`, and a per-issue behavioral verdict. A
  consolidation implements nothing, so satisfying them means writing sentences
  that are not true. A floor met by writing false sentences is worse than no
  floor, because the false sentences are now checked-in evidence.
- The EXEMPT classifications (`question` / `decision-needed`) fit no better.
  Using them would misclassify the issue AND open a path where any inconvenient
  bug reaches the light floor by relabelling.

So `consolidated` is NOT floor-exempt. It swaps the resolution floor for its own,
and every check below is machine-verifiable rather than prose a reviewer must
grade. The point is to make the ambiguity unwritable, not to trust the author.

WHAT IT MAY AND MAY NOT SAY. The load-bearing rule is the REFUSAL: a carrier
classified `consolidated` that also claims a repair is rejected. Without it, the
cheap disposition becomes a laundering path — twenty issues closed as "moved"
while the commit message quietly asserts they were fixed, which buys twenty cheap
closes at the price of what a close MEANS in this repo.

WHAT LIVES HERE AND WHAT DOES NOT. This module owns the BODY-side grammar: the
destination field, its arity, and the claim refusal. The checks that need the
tracker — destination exists and is OPEN at close time, destination body contains
this issue's number, destination is not itself a `consolidated` close (no chains),
and the backend close reason is `not planned` rather than `completed` — are
backend readbacks and belong with the verifier that already talks to the backend.
Asserting them in prose here would be the same false-verdict shape this whole
lane exists to remove.
"""
from __future__ import annotations

import re

CLASSIFICATION = "consolidated"

# `Consolidated into: #N`. One destination, named as an anchor. The bullet and
# emphasis tolerance mirrors every other field reader in this package, so
# `- **Consolidated into:** <anchor>` is the same record as the bare form.
_FIELD_RE = re.compile(
    r"^[ \t]*[-*+]?[ \t]*[`*_~]*consolidated\s+into[`*_~]*[ \t]*:[ \t]*(?P<value>.+)$",
    re.IGNORECASE | re.MULTILINE,
)
_ANCHOR_RE = re.compile(r"#(\d+)(?!\d)")

# Fields whose presence means the carrier is claiming a REPAIR. A consolidation
# claims none of them, so their presence is a contradiction rather than a bonus.
# `Prevention:` is deliberately included: a consolidation prevents nothing, and
# the destination issue is where prevention gets decided.
# The claim predicate is "ASSERTS A REPAIR", which is NOT "the resolution floor
# demands it". Two revisions got this wrong in opposite directions. The first
# hand-listed four regexes and forgot several. The second derived the set from the
# whole resolution rows, which over-refused: `Root cause:`, `Siblings:`, `Boundary:`
# and `Debug artifact:` are DIAGNOSTIC or SCOPING -- an unfixed issue can carry all
# four -- and consolidating a cluster IS a sibling-search operation, so
# a `Siblings:` line naming the cluster is the most natural sentence an
# honest consolidation writes and it was being refused.
#
# So the set is named, but named by what it MEANS, and the two line-grammar claims
# (`HOTL #N:` and `Critique:`) are included -- a previous comment asserted they were
# covered by a derivation that could not reach them, since neither is a ledger field.
_REPAIR_ASSERTION_ALIASES = (
    "implementation",
    "prevention",
    "resolution brief",
)

# Claims written as a per-issue LINE rather than a plain field: the name is followed
# by a target segment before the colon (`Behavior <anchors>:`, `HOTL <anchor>:`). A
# plain field pattern cannot see them, which is how a previous comment came to assert
# `hotl`/`critique` coverage that no derivation could actually reach.
_TARGETED_CLAIM_NAMES = ("behaviou?r", "hotl", "critique")


def _claim_field_names(ledger) -> tuple[str, ...]:
    owed = list(_REPAIR_ASSERTION_ALIASES)
    consolidated_owes = {
        alias
        for _field_id, aliases in (ledger.CLASSIFICATION_FIELDS.get(CLASSIFICATION, []) if ledger else [])
        for alias in aliases
    }
    # `Behaviou?r` is added by hand because it is not a ledger FIELD -- it is the
    # per-issue behavioral-verdict line, whose grammar allows a target between the
    # name and the colon. The narrower single-anchor form the first version used was
    # evadable by writing two comma-separated anchors.
    return tuple(dict.fromkeys([a for a in owed if a not in consolidated_owes]))


def _field_pattern(alias: str) -> "re.Pattern[str]":
    escaped = re.escape(alias).replace(r"\ ", r"\s+")
    return re.compile(
        rf"^[ \t]*[-*+]?[ \t]*[`*_~]*{escaped}[`*_~]*[ \t]*:[ \t]*\S",
        re.IGNORECASE | re.MULTILINE,
    )


_TARGETED_CLAIM_RES = tuple(
    re.compile(
        rf"^[ \t]*[-*+]?[ \t]*[`*_~]*{name}(?:\s+[^:\n]+?)?[`*_~]*[ \t]*:[ \t]*\S",
        re.IGNORECASE | re.MULTILINE,
    )
    for name in _TARGETED_CLAIM_NAMES
)
# A public repair claim: GitHub renders `Fixes #N` / `Resolves #N` on the issue
# timeline. `Closes` is the neutral keyword a consolidation must use.
_FIX_KEYWORD_RE = re.compile(r"\b(?:fix(?:e[sd])?|resolve[sd]?)\s+#\d+", re.IGNORECASE)
# Every close keyword GitHub honours, including the neutral `Closes`.
_ANY_CLOSE_KEYWORD_RE = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)(?!\d)", re.IGNORECASE
)


def _close_keyword_numbers(text: str) -> list[int]:
    return [int(number) for number in _ANY_CLOSE_KEYWORD_RE.findall(text or "")]

# The backend close reason this disposition requires. `issue_close.py` already
# threads `--reason` through the backend command templates, so the tracker itself
# renders the distinction — which puts the signal on a channel OUTSIDE this repo's
# prose, where a reader who never opens the repo can still see that the close
# claimed nothing.
REQUIRED_CLOSE_REASON = "not planned"


def destinations(text: str) -> list[int]:
    """Every issue number named by EVERY `Consolidated into:` field, in order.

    `finditer`, not `search`. Reading only the first field defeated the arity rule's
    own justification: a body carrying the field twice with different destinations is
    exactly the "went to two places, has no single owner" case the rule refuses, and
    it passed.
    """
    found: list[int] = []
    for match in _FIELD_RE.finditer(text or ""):
        found.extend(int(number) for number in _ANCHOR_RE.findall(match.group("value")))
    return found


def repair_claims(text: str, *, ledger=None, raw_text: str | None = None) -> list[str]:
    """Repair-claiming fields present in a body that says it consolidates.

    `raw_text` is the UNSTRIPPED body, and the split matters. Field reads want fences
    stripped, so a pasted log containing `Implementation:` does not falsely refuse an
    honest consolidation. The close-keyword read must NOT be stripped: GitHub parses
    the raw commit text and treats backticks as literal characters, so a fenced
    `Fixes #N` still auto-closes the issue with a public "fixed" event. Stripping both
    with one call re-opened exactly the evasion the commit-message floor documents.
    """
    found: list[str] = []
    for alias in _claim_field_names(ledger):
        if _field_pattern(alias).search(text or ""):
            found.append(alias)
    for name, pattern in zip(_TARGETED_CLAIM_NAMES, _TARGETED_CLAIM_RES):
        if pattern.search(text or ""):
            found.append(name.replace("ou?", "o"))
    if _FIX_KEYWORD_RE.search(raw_text if raw_text is not None else (text or "")):
        found.append("fix-close-keyword")
    return found


def evaluate(
    text: str,
    *,
    self_number: int | None = None,
    self_numbers: tuple[int, ...] = (),
    ledger=None,
    report_missing: bool = True,
    raw_text: str | None = None,
    carrier_auto_closes: bool = False,
) -> dict:
    """Body-side verdict for a `consolidated` close.

    Presence and ARITY, plus the claim refusal. Everything requiring the tracker
    is deliberately absent — see the module docstring.
    """
    found = destinations(text)
    claims = repair_claims(text, ledger=ledger, raw_text=raw_text)
    problems: list[str] = []

    field_present = _FIELD_RE.search(text or "") is not None
    if not found and (report_missing or field_present):
        # `report_missing=False` says the caller already reports an ABSENT field. It
        # does not say a PRESENT field with no anchor is fine -- and that seam is
        # where `Consolidated into: the umbrella issue` slipped through both owners,
        # leaving the one thing this disposition exists to require unrequired.
        problems.append(
            "`Consolidated into:` names no issue anchor -- a consolidated close must name "
            "WHERE the content went as `#N`, or it is a close that says nothing at all"
            if field_present
            else "missing `Consolidated into: #N` -- a consolidated close must name where "
            "the content went, or it is a close that says nothing at all"
        )
    if len(found) > 1:
        problems.append(
            "`Consolidated into:` names "
            + ", ".join(f"#{number}" for number in found)
            + " -- exactly one destination is required, because an issue that went to two "
            "places has no single owner and neither destination can be checked for it"
        )
    else:
        # ALL the numbers this carrier closes, not just the first. A single carrier
        # closing twenty issues into an umbrella is the intended shape, and comparing
        # only `numbers[0]` let the destination be one of the other nineteen -- the
        # same "evaporates the work" failure, one index over.
        closing = set(self_numbers) | ({self_number} if self_number is not None else set())
        if found and found[0] in closing:
            problems.append(
                f"`Consolidated into: #{found[0]}` names an issue this same carrier is "
                "closing -- consolidating into something that is being closed evaporates "
                "the work rather than moving it"
            )

    # THE CARRIER RESTRICTION, and it is the whole of what makes the close reason
    # real. GitHub auto-closes a keyword-referenced issue as COMPLETED, and there is
    # no `--reason` argv on that path to intercept -- so a consolidated close carried
    # by a commit or PR keyword lands publicly as "completed", asserting exactly the
    # repair this disposition refuses in prose, on the one channel outside this repo.
    # Refusing `Fixes`/`Resolves` was not enough, because the neutral `Closes` the
    # module recommended produces the same public event. A consolidated close must
    # therefore go through `close-with-comment`, where `--reason "not planned"` is
    # passed and `issue_close` enforces it.
    if carrier_auto_closes and self_numbers:
        auto = [number for number in self_numbers if number in set(_close_keyword_numbers(raw_text or text))]
        if auto:
            problems.append(
                "this carrier auto-closes "
                + ", ".join(f"#{number}" for number in auto)
                + " via a close keyword, and GitHub renders a keyword close as COMPLETED "
                "with no reason argv to intercept -- which asserts the repair a "
                "consolidated close refuses. Close it with `issue_tool.py "
                f"close-with-comment --reason {REQUIRED_CLOSE_REASON!r}` instead"
            )

    if claims:
        problems.append(
            "classification `consolidated` claims nothing about the defect, but the carrier "
            "asserts a repair via " + ", ".join(f"`{name}`" for name in claims)
            + " -- either the close is a resolution (use its real classification and meet the "
            "resolution floor) or it is a move (drop the repair claim). Allowing both is how "
            "cheap closes get bought at the price of what a close means"
        )

    return {
        "classification": CLASSIFICATION,
        "ok": not problems,
        "destinations": found,
        "repair_claims": claims,
        "required_close_reason": REQUIRED_CLOSE_REASON,
        "problems": problems,
        "not_checked_here": [
            "destination exists and is OPEN at close time (backend readback)",
            "destination body contains this issue's number (backend readback)",
            "destination is not itself closed as consolidated -- no chains (backend readback)",
            f"backend close reason is `{REQUIRED_CLOSE_REASON}` (backend argv)",
        ],
    }
