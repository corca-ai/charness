#!/usr/bin/env python3
"""The backlog-recount floor: a goal must say what it CLAIMS and what it does not.

`achieve`'s Before phase shapes outcome, non-goals, boundaries, acceptance and a slice
sequence, and never had a reason to open the issue tracker. `--pursue-ready` -- the thing
that decides a goal may activate -- validated headings, placeholders and closeout-plan
fields, so a goal whose scope contradicted the tracker passed it cleanly. That is this
repo's own recurring shape: a declaration (the goal's scope) that no executable reader
ever reconciles against the source of truth (the tracker). The measured cost, in the run
that prompted this, was a duplicate issue filed, the issue the whole run was fixing left
open and unreferenced, and a known issue re-discovered and worked around instead of
linked.

PRESENCE-ONLY, AND THAT IS THE DESIGN, NOT A SHORTCUT. This floor checks that the goal
RECORDED a recount and a claim split. It does not check that the split is correct, that
every open issue was considered, or that the claimed issues are the right ones. Which
issues a goal takes is the operator's judgement, and a floor that graded that judgement
would be a new false-verdict surface inside the tool built to stop them -- it would have
to answer "should this goal have claimed that one", which nothing can decide from the
artifact. The floor makes the reasoning VISIBLE and auditable; a human or a reviewer
grades it. Every other conditional floor in this module's siblings is presence-shaped for
the same reason.

WHY A DATE GRANDFATHER. Nineteen goal artifacts predate this rule and none carries the
section. Making it unconditional would redden every historical artifact and the broad
gate with them, which is how a floor gets disarmed rather than obeyed. `RULE_DATE` gates
on the goal's own `Created:` line and fails CLOSED on a missing or malformed one, so a
dateless artifact is covered rather than exempted.
"""
from __future__ import annotations

import importlib.util
import re
from datetime import date
from pathlib import Path


def _load_floor_grammar():
    """Load the sibling grammar by path, the way every other floor in this package does.

    Not a package-relative import: these modules are executed directly as often as they
    are imported, and the export flattens the layout, so a dotted import works in one
    tree and not the other.
    """
    spec = importlib.util.spec_from_file_location(
        "goal_artifact_floor_grammar",
        Path(__file__).resolve().parent / "goal_artifact_floor_grammar.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("goal_artifact_floor_grammar.py not found beside goal_artifact_backlog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_GRAMMAR = _load_floor_grammar()
parse_created_date = _GRAMMAR.parse_created_date
is_floor_in_scope = _GRAMMAR.is_floor_in_scope
grandfathered_report = _GRAMMAR.grandfathered_report
joined_section_body = _GRAMMAR.joined_section_body

SECTION = "Backlog Recount"

# The rule lands with the goal that repairs the defect. That goal's own artifact is in
# scope on purpose -- it is the first test of the floor it ships, and a rule its author's
# own artifact escapes is a rule nobody has run.
RULE_DATE = date(2026, 8, 8)

# `Counted:` is the evidence the recount HAPPENED; the two claim lines are the reasoning
# it produced. All three are required because any one alone is defeatable: a count with no
# split records a ritual, and a split with no count records an assertion.
REQUIRED_FIELDS = ("Counted", "Claims", "Not claimed")

# An empty value is not a record. `Claims: none` and `Not claimed: none` are legal --
# a goal may genuinely claim nothing tracked -- but the operator has to write the word,
# which is the difference between a decision and an omission.
#
# `[^\S\n]*` after the colon, NOT `\s*`. `\s` matches a newline, so `\s*` on an EMPTY
# `Claims:` line consumed the line break and captured the NEXT field's text as this
# field's value -- an empty field reporting itself satisfied, which is precisely the
# defect this floor exists to catch, inside the floor that catches it. Caught by the
# test written for the empty-value case, not by review.
_FIELD_RE = r"^[^\S\n]*[-*]?[^\S\n]*{field}[^\S\n]*:[^\S\n]*(?P<value>.*)$"


def applies(text: str) -> bool:
    """Gate on the goal's ``Created:`` date; fail closed on a missing or malformed one."""
    return is_floor_in_scope(parse_created_date(text), RULE_DATE)


def _field_value(body: str, field: str) -> str | None:
    pattern = re.compile(_FIELD_RE.format(field=re.escape(field)), re.MULTILINE)
    match = pattern.search(body)
    if match is None:
        return None
    return match.group("value").strip()


def missing_fields(body: str) -> list[str]:
    """Fields absent entirely, or present with an empty value.

    Both are the same defect from a reader's point of view: `Claims:` with nothing after
    it tells the next session exactly as much as no line at all, while LOOKING like the
    floor was satisfied. That look-alike is the whole class this goal family exists to
    remove, so the two cases are collapsed into one verdict rather than distinguished.
    """
    return [field for field in REQUIRED_FIELDS if not (_field_value(body, field) or "")]


def check(text: str) -> dict:
    """Presence verdict for one goal artifact's backlog recount."""
    if not applies(text):
        return grandfathered_report(text, RULE_DATE, "backlog-recount")
    body = joined_section_body(text, SECTION)
    if body is None:
        return {
            "applies": True,
            "ok": False,
            "missing_fields": list(REQUIRED_FIELDS),
            "reason": (
                f"missing `## {SECTION}` section -- recount the tracker and record what this "
                "goal claims and does not before `/goal`"
            ),
        }
    missing = missing_fields(body)
    if missing:
        return {
            "applies": True,
            "ok": False,
            "missing_fields": missing,
            "reason": (
                "incomplete backlog recount: field(s) absent or empty ("
                + ", ".join(missing)
                + ") -- `Claims:`/`Not claimed:` may say `none`, but the word has to be written"
            ),
        }
    return {"applies": True, "ok": True, "missing_fields": [], "reason": "backlog recount recorded"}
