"""Orchestrator/sub-goal closeout-proof delegation gate for achieve goals.

An *opt-in* orchestrated-closeout mode: a sub-goal can honestly close at
local/proof-carrier complete while a *named orchestrator goal* owns the deferred
external proof (final push/CI, instance apply/restart, provider/live proof,
issue ``CLOSED`` state). A goal with no ``## Closeout Delegation`` section, or an
explicit ``Closeout mode: standalone``, is untouched — the strict standalone
default stays the hard default (the non-weakening constraint).

Two enforced invariants (presence/resolution-based, never a prose classifier —
the same gate-and-intelligence split the disposition/coordination floors use):

- an **orchestrated** sub-goal must name an ``Orchestrator goal:`` AND list at
  least one ``Delegated proof:`` item — it cannot delegate into the void or
  vaguely claim "external proof is elsewhere";
- an **orchestrator** goal must resolve every ``Delegated proof checklist:`` item
  (``verified`` / ``skipped: <reason>`` / ``issue #N``) before it can flip to
  ``complete``, so the orchestrator cannot silently forget a delegated proof.

The closeout-state taxonomy (``impl-local``, ``carrier``, ``pushed-ci``,
``applied-restarted``, ``live``, ``issue-closed``) is the documented vocabulary
in ``references/lifecycle.md`` and ``references/goal-artifact.md``; this gate does
not require those exact tokens, only that each checklist item is resolved.
"""
from __future__ import annotations

import re
from typing import Any

# The six closeout-proof levels — the single source for the taxonomy vocabulary.
# The gate itself is resolution-based and does not require these exact tokens; a
# drift test keeps the canonical lifecycle reference in sync with this tuple so
# the docs and this constant cannot diverge.
CLOSEOUT_STATE_LEVELS = (
    "impl-local",
    "carrier",
    "pushed-ci",
    "applied-restarted",
    "live",
    "issue-closed",
)

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
# Field values are captured SAME-LINE ([ \t] is horizontal whitespace only, never
# a newline) so a blank field cannot borrow the following line as its value.
_MODE = re.compile(r"^[ \t>*-]*Closeout mode[ \t]*:[ \t]*(.*?)[ \t]*$", re.MULTILINE | re.IGNORECASE)
_ORCHESTRATOR = re.compile(
    r"^[ \t>*-]*Orchestrator goal[ \t]*:[ \t]*(.*?)[ \t]*$", re.MULTILINE | re.IGNORECASE
)
_DELEGATED_HDR = re.compile(
    r"^[ \t>*-]*Delegated proof(?: checklist)?[ \t]*:[ \t]*$", re.IGNORECASE
)
_LIST_ITEM = re.compile(r"^\s*[-*]\s+(.+)$")
_PLACEHOLDER = re.compile(r"^(?:(?:TODO|TBD|FIXME)\b|<[^>\n]*>)", re.IGNORECASE)
# Resolution forms (one line per checklist item): an explicit ``skipped: <reason>``,
# a follow-up issue reference, or an *affirmative* ``verified``. ``skipped`` is an
# artifact-visible resolution state declared in attention-state-visibility.json. A
# negation before ``verified`` (``not verified``, ``to be verified``, ``pending …
# verified``) leaves the item unresolved, so a future/negated phrasing cannot pass.
_SKIP_TOKEN = re.compile(r"(?i)\bskipped[ \t]*:[ \t]*\S")
_ISSUE_REF = re.compile(r"(?i)\bissue\s+#?\d+\b|#\d+\b")
_VERIFIED = re.compile(r"(?i)\bverified\b")
_NEG_BEFORE_VERIFIED = re.compile(
    r"(?i)\b(?:not|never|no|to\s+be|will\s+be|yet\s+to|pending|awaiting|unverified)\b.*?\bverified\b"
)
_UNCHECKED_BOX = re.compile(r"\[\s\]")


def _mask_fences(text: str) -> str:
    """Blank out fenced code so a ``## heading`` inside a code block is not read
    as a section. Local copy to avoid a circular import on the parent
    closeout-evidence module (mirrors that module's own local copy).
    """
    masked: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        masked.append("".join("\n" if char == "\n" else " " for char in line) if in_fence else line)
    if in_fence:
        return text
    return "".join(masked)


def _section(text: str, name: str) -> str | None:
    masked = _mask_fences(text)
    headings = list(_H2.finditer(masked))
    for index, heading in enumerate(headings):
        if heading.group(1).strip() != name:
            continue
        body_start = masked.find("\n", heading.start())
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        start = body_start + 1 if body_start != -1 else heading.end()
        return masked[start:body_end]
    return None


def _delegated_items(section: str) -> list[str]:
    """List items directly under the ``Delegated proof[ checklist]:`` header.

    Items are the indented ``- ``/``* `` lines following the header, up to the
    first blank or non-list line, excluding the mode/orchestrator field lines.
    """
    items: list[str] = []
    capturing = False
    for line in section.splitlines():
        if _DELEGATED_HDR.match(line):
            capturing = True
            continue
        if not capturing:
            continue
        if not line.strip():
            continue  # blank lines inside the list do not end it (a blank between
            # items must not hide later unresolved items from the gate)
        match = _LIST_ITEM.match(line)
        if not match:
            break  # the first non-blank, non-list line ends the checklist
        if _MODE.match(line) or _ORCHESTRATOR.match(line):
            continue
        items.append(match.group(1).strip())
    return items


def _item_resolved(item: str) -> bool:
    if _UNCHECKED_BOX.search(item):
        return False
    if _SKIP_TOKEN.search(item) or _ISSUE_REF.search(item):
        return True
    return bool(_VERIFIED.search(item) and not _NEG_BEFORE_VERIFIED.search(item))


def parse_closeout_delegation(text: str) -> dict[str, Any]:
    """Parse the optional ``## Closeout Delegation`` section.

    Returns ``mode`` (standalone | orchestrated | orchestrator), whether the
    section was ``declared``, the named ``orchestrator``, and the
    ``delegated_items``. Absent section -> implicit standalone.
    """
    section = _section(text, "Closeout Delegation")
    if section is None:
        return {"mode": "standalone", "declared": False, "orchestrator": "", "delegated_items": []}
    mode_match = _MODE.search(section)
    # Take the first bareword of the mode value so a trailing comment/clause
    # (`standalone (owns all proof)`) cannot reclassify the mode and block a goal.
    mode_tokens = mode_match.group(1).strip().split() if mode_match else []
    mode = mode_tokens[0].lower() if mode_tokens else "standalone"
    orchestrator_match = _ORCHESTRATOR.search(section)
    orchestrator = orchestrator_match.group(1).strip() if orchestrator_match else ""
    return {
        "mode": mode,
        "declared": True,
        "orchestrator": orchestrator,
        "delegated_items": _delegated_items(section),
    }


def apply_closeout_delegation(report: dict[str, Any], text: str) -> None:
    """Gate orchestrator/sub-goal closeout delegation; no-op for standalone.

    Mutates ``report`` in place: records the parsed delegation under
    ``closeout_delegation`` and sets ``report["ok"] = False`` with a ``failures``
    list when an orchestrated/orchestrator goal violates its invariant.
    """
    parsed = parse_closeout_delegation(text)
    report["closeout_delegation"] = parsed
    mode = parsed["mode"]
    if not parsed["declared"] or mode in {"", "standalone"}:
        return

    failures: list[str] = []
    if mode == "orchestrated":
        orchestrator = parsed["orchestrator"]
        if not orchestrator or _PLACEHOLDER.match(orchestrator):
            failures.append(
                "orchestrated sub-goal must name an `Orchestrator goal:` that owns the "
                "delegated external proof"
            )
        if not parsed["delegated_items"]:
            failures.append(
                "orchestrated sub-goal must list at least one `Delegated proof:` item "
                "naming the deferred external proof level(s)"
            )
    elif mode == "orchestrator":
        items = parsed["delegated_items"]
        if not items:
            failures.append(
                "orchestrator goal must carry a `Delegated proof checklist:` with at least "
                "one delegated item it owns"
            )
        unresolved = [item for item in items if not _item_resolved(item)]
        parsed["unresolved_items"] = unresolved
        for item in unresolved:
            failures.append(
                "delegated-proof checklist item is not resolved (needs `verified`, "
                f"`skipped: <reason>`, or `issue #N`): {item}"
            )
    else:
        failures.append(
            f"unknown `Closeout mode: {mode}` — use standalone, orchestrated, or orchestrator"
        )

    parsed["failures"] = failures
    if failures:
        report["ok"] = False
