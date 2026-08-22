"""What a `superseded` goal must carry to be an honest record.

`superseded` is the terminal status for a goal that ENDED WITHOUT COMPLETING --
folded into a successor, overtaken, or abandoned with its remainder handed on.
Its own module because it is one concept with one rule, and because
`goal_artifact_lib` crossed its length cap the moment this was added to it: the
contract here is to separate a concept, never to shave lines.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

#: What `superseded` must carry to be an honest record rather than an escape
#: hatch. A terminal status that skips the closeout floor and asks for
#: nothing in return would be WORSE than the lie it replaces: a goal could be
#: abandoned with no account of where its remainder went, and the next session
#: would find a finished-looking artifact and no successor. So the status costs
#: exactly one line, and that line is the thing a reader actually needs.
SUPERSEDED_RECORD_FIELD = "Superseded by:"

_SUPERSEDED_LINE = re.compile(
    rf"^[ \t>*-]*[`*_~]*{re.escape(SUPERSEDED_RECORD_FIELD)}[`*_~]*[ \t]+(.+)$",
    re.MULTILINE,
)
#: Punctuation-only values do not count. Same class the closeout-plan and backlog
#: floors already learned: `Superseded by: —` is a filled-looking empty field.
_SUPERSEDED_SUBSTANTIVE = re.compile(r"[^\s\-–—:.,;`*_~]")


def check_superseded_record(text: str, *, mask_fences, repo_root: Path | None = None) -> dict[str, Any]:
    """Whether a `superseded` goal says WHERE its remainder went.

    The point of the status is to stop a goal choosing between staying `active`
    forever and claiming a completion it never earned. Both lie; the second loses
    work. But a terminal status that skips the closeout floor and asks for nothing
    in return would lose the same work more quietly -- a finished-looking artifact
    with no successor and no reason. So this is the one thing it must carry.

    `Superseded by: none — <reason>` is accepted and is the point of accepting it:
    a goal genuinely abandoned with nothing downstream should say so out loud
    rather than be unable to close.
    """
    match = _SUPERSEDED_LINE.search(mask_fences(text))
    if match is None:
        return {
            "applies": True,
            "ok": False,
            "reason": (
                f"status is `superseded` but no `{SUPERSEDED_RECORD_FIELD}` line is present; "
                "name the successor goal artifact, or write "
                f"`{SUPERSEDED_RECORD_FIELD} none — <reason>` to say out loud that the "
                "remainder was dropped"
            ),
            "value": None,
        }
    value = match.group(1).strip()
    if not _SUPERSEDED_SUBSTANTIVE.search(value):
        return {
            "applies": True,
            "ok": False,
            "reason": (
                f"`{SUPERSEDED_RECORD_FIELD}` is present but carries no substantive value "
                f"({value!r}); a punctuation placeholder is an empty field that looks filled"
            ),
            "value": value,
        }
    target = _pointer_path(value)
    if repo_root is not None and target is not None and not (repo_root / target).exists():
        # The successor pointer is the ENTIRE cost of this status -- roughly
        # fourteen closeout floors are skipped for it -- and it was the only
        # evidence line in this contract that was never checked for existence.
        # `Superseded by: charness-artifacts/goals/2026-09-01-never-written.md`
        # passed, which is a pointer that loses the work exactly as quietly as
        # having no status at all would have.
        return {
            "applies": True,
            "ok": False,
            "reason": (
                f"`{SUPERSEDED_RECORD_FIELD}` names {target!r}, which does not exist. "
                "Point at the successor that was actually written, or write "
                f"`{SUPERSEDED_RECORD_FIELD} none — <reason>`"
            ),
            "value": value,
        }
    return {"applies": True, "ok": True, "reason": "", "value": value}


#: A value that LOOKS like a repo-relative artifact path, so existence is a fact
#: rather than a guess. Prose (`none — folded into the next unit`) has no `/` and
#: no `.md`, so it is never treated as a pointer.
_POINTER_RE = re.compile(r"(?:^|[\s`(])((?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\.md)\b")


def _pointer_path(value: str) -> str | None:
    match = _POINTER_RE.search(value)
    return match.group(1) if match else None




def refuse_flip_reason(status: str, original: str, *, mask_fences, read_status) -> str | None:
    """Why a flip TO `superseded` must be refused, or None when it may proceed.

    Checked at the WRITE, matching how `complete` is guarded, because a validator
    that only complains afterwards leaves a window in which the artifact already
    reads as terminal to anything that opens it.
    """
    if status != "superseded" or read_status(original) == "superseded":
        return None
    report = check_superseded_record(original, mask_fences=mask_fences)
    if report["ok"]:
        return None
    return "refusing to mark this goal `superseded`: " + report["reason"]
