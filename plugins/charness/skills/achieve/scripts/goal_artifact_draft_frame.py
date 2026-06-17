from __future__ import annotations

import re
from typing import Any

_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_DRAFT_DISPOSITION = re.compile(
    r"\b(real draft/backlog|stale draft|reshape[- ]before[- ]activat(?:e|ing)|current disposition:)",
    re.IGNORECASE,
)


def _section_body(text: str, masked: str, section: str) -> str:
    headings = list(_H2.finditer(masked))
    for index, match in enumerate(headings):
        if match.group(1).strip() != section:
            continue
        body_start = masked.find("\n", match.start())
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        return text[body_start + 1 if body_start != -1 else match.end():body_end]
    return ""


def draft_frame_disposition(text: str, *, status: str | None, masked: str) -> dict[str, Any]:
    if status != "draft":
        return {"required": False, "present": True, "warning": ""}
    active_frame = _section_body(text, masked, "Active Operating Frame")
    present = bool(_DRAFT_DISPOSITION.search(active_frame))
    warning = (
        ""
        if present
        else (
            "draft Active Operating Frame lacks lifecycle disposition; newly scaffolded "
            "drafts should name real draft/backlog awaiting activation, stale draft, "
            "reshape-before-activation, or an equivalent `Current disposition:` before `/goal`"
        )
    )
    return {"required": True, "present": present, "warning": warning}
