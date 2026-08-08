from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_markdown import section_bounds as _section_bounds  # noqa: E402

_DRAFT_DISPOSITION = re.compile(
    r"\b(real draft/backlog|stale draft|reshape[- ]before[- ]activat(?:e|ing)|current disposition:)",
    re.IGNORECASE,
)


def _section_body(text: str, masked: str, section: str) -> str:
    """Body read from RAW text, located by a scan over the fence-masked copy."""
    bounds = _section_bounds(masked, section)
    return "" if bounds is None else text[bounds[0]:bounds[1]]


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
