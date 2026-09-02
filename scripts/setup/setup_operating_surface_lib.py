from __future__ import annotations

import re
from pathlib import Path

OPERATING_SURFACE_LINE_BUDGET = 48
_MARKDOWN_LINK = re.compile(r"\]\(([^)#\s]+)")
_CONSUMERS = ["quality.quality_setup_snapshot", "setup.inspect_repo"]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _linked_doc_targets(text: str) -> list[str]:
    """Return documentation targets in source order."""

    found: list[str] = []
    for raw in _MARKDOWN_LINK.findall(text):
        candidate = raw.split("#", 1)[0]
        if candidate.startswith("./docs/"):
            found.append(candidate.removeprefix("./"))
        elif candidate.startswith("../docs/"):
            found.append(candidate.removeprefix("../"))
        elif candidate.startswith("docs/"):
            found.append(candidate)
    return found


def _linked_docs(text: str) -> list[str]:
    """Return unique documentation targets named by an operating surface."""

    return sorted(set(_linked_doc_targets(text)))


def _duplicate_doc_links(text: str) -> list[str]:
    targets = _linked_doc_targets(text)
    return sorted({target for target in targets if targets.count(target) > 1})


def _surface_shape(path: Path, text: str, *, role: str) -> dict[str, object]:
    lines = [line for line in text.splitlines() if line.strip()]
    links = _linked_docs(text)
    duplicate_links = _duplicate_doc_links(text) if role == "documentation-index" else []
    headings = sum(1 for line in lines if line.lstrip().startswith("#"))
    index_entries = sum(1 for line in lines if re.match(r"^\s*[-*+]\s+\[", line))
    substantive = sum(
        1
        for line in lines
        if not line.lstrip().startswith(("#", "- [", "* [", "+ [", ">"))
    )
    if not lines:
        shape, action = "missing-or-empty", "refuse ownership assignment until readable structure exists"
        owner, confidence = None, "none"
        refusal_reason = "readable structure is required; path existence alone is insufficient"
    elif duplicate_links:
        shape, action = "duplicate-index-entry", "list each current documentation page once"
        owner, confidence, refusal_reason = "documentation", "high", None
    elif role == "first-touch-contract" and len(lines) > OPERATING_SURFACE_LINE_BUDGET:
        shape, action = "overloaded", "thin the entrypoint after assigning procedures to deeper owners"
        owner, confidence, refusal_reason = "setup", "medium", None
    elif role == "documentation-index" and substantive > 12:
        shape, action = "substantive-index", "keep the index link-oriented and move durable prose to owning docs"
        owner, confidence, refusal_reason = "documentation", "medium", None
    elif role == "documentation-index" and index_entries >= max(3, len(lines) // 3):
        shape, action = "index-oriented", "leave the index shape; change only with explicit ownership approval"
        owner, confidence, refusal_reason = "documentation", "medium", None
    else:
        shape, action = "within-observed-shape", "no semantic move proposed from this read"
        owner = "setup" if role == "first-touch-contract" else "documentation"
        confidence, refusal_reason = "medium", None
    return {
        "path": path.as_posix(),
        "role": role,
        "surface": role,
        "owner": owner,
        "source": path.as_posix(),
        "consumer": _CONSUMERS,
        "confidence": confidence,
        "refusal_reason": refusal_reason,
        "nonempty_lines": len(lines),
        "line_budget": OPERATING_SURFACE_LINE_BUDGET,
        "heading_count": headings,
        "internal_doc_links": links,
        "duplicate_doc_links": duplicate_links,
        "shape": shape,
        "action": action,
    }


def detect_operating_surface_ownership(
    repo_root: Path, *, agents_text: str | None = None
) -> dict[str, object]:
    """Describe first-touch/deeper-doc ownership without rewriting either file."""

    agent_value = agents_text if agents_text is not None else _read_text(repo_root / "AGENTS.md")
    surfaces = [
        _surface_shape(Path("AGENTS.md"), agent_value, role="first-touch-contract"),
        _surface_shape(Path("docs/index.md"), _read_text(repo_root / "docs/index.md"), role="documentation-index"),
    ]
    flagged = [
        surface
        for surface in surfaces
        if surface["shape"] in {
            "overloaded",
            "substantive-index",
            "duplicate-index-entry",
            "missing-or-empty",
        }
    ]
    moves = [
        {
            "surface": surface["surface"],
            "owner": surface["owner"],
            "source": surface["source"],
            "consumer": surface["consumer"],
            "deeper_owner_candidates": surface["internal_doc_links"],
            "action": surface["action"],
            "confidence": surface["confidence"],
            "refusal_reason": surface["refusal_reason"],
            "approval": "required",
            "execution": "not-run",
        }
        for surface in flagged
    ]
    return {
        "status": "plan-only",
        "approval_required": True,
        "execution": "not-run",
        "contract": {
            "first_touch": "AGENTS.md owns routing and small operating constraints",
            "deeper_docs": "linked owner pages carry durable procedures and rationale",
            "index": "docs/index.md owns reachability, not a second copy of every procedure",
        },
        "surfaces": surfaces,
        "moves": moves,
        "recommended_first_move": moves[0] if moves else None,
        "refusal_reason": next(
            (surface["refusal_reason"] for surface in surfaces if surface["refusal_reason"]),
            None,
        ),
        "non_claims": [
            "line counts and lexical shape are signals, not permission for a bulk rewrite",
            "no content was moved, deleted, or rewritten by this inspection",
        ],
    }
