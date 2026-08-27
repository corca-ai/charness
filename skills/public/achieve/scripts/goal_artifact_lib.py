"""Planning-only Goal Draft helpers.

The Goal Draft records intent until the operator approves it. After approval
the exact bytes are frozen by Goal Binding; execution state belongs to the
provider-backed Goal Run. This module deliberately has no local status,
progress, closeout, evidence, or metric writer.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_sibling(module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).resolve().parent / f"{module_name}.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside goal_artifact_lib.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_markdown = _load_sibling("goal_artifact_markdown")
_naming = _load_sibling("goal_artifact_naming")
_discussion = _load_sibling("goal_artifact_discussion")
_portability = _load_sibling("goal_path_portability")
_scaffold = _load_sibling("goal_artifact_scaffold")

_mask_fences = _markdown.mask_fences
_fences_balanced = _markdown.fences_balanced

GOAL_DIR = _naming.GOAL_DIR
SLUG_FALLBACK = _naming.SLUG_FALLBACK
slugify = _naming.slugify
normalize_goal_text = _naming.normalize_goal_text
resolve_supplied_slug = _naming.resolve_supplied_slug
goal_path = _naming.goal_path
goal_rel = _naming.goal_rel


def validate_goal_values(title: str, goal_body: str) -> tuple[str, str]:
    return _naming.validate_goal_values(
        title,
        goal_body,
        fences_balanced=_fences_balanced,
        mask_fences=_mask_fences,
    )

REQUIRED_SECTIONS = (
    "Goal",
    "Non-Goals",
    "Boundaries",
    "User Acceptance",
    "Agent Verification Plan",
    "Slice Plan",
    "Discuss Before Activation",
    "Context Sources",
    "Interview Decisions",
    "Plan Critique Findings",
)

_TITLE = re.compile(r"^# Achieve Goal:.*$", re.MULTILINE)
_GOAL_HEADING = re.compile(r"^## Goal[ \t]*\r?$", re.MULTILINE)
_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)


def _replace_goal_heading(text: str, title: str) -> str:
    match = _TITLE.search(_mask_fences(text))
    if match is None:
        raise ValueError("existing Goal Draft has no `# Achieve Goal:` heading")
    line_end = "\r" if text[match.start():match.end()].endswith("\r") else ""
    return f"{text[:match.start()]}# Achieve Goal: {title}{line_end}{text[match.end():]}"


def _replace_goal_body(text: str, goal_body: str) -> str:
    masked = _mask_fences(text)
    heading = _GOAL_HEADING.search(masked)
    if heading is None:
        raise ValueError("existing Goal Draft has no `## Goal` section")
    headings = list(_H2.finditer(masked))
    next_heading = next(
        (candidate for candidate in headings if candidate.start() > heading.start()),
        None,
    )
    body_start = masked.find("\n", heading.start())
    body_start = heading.end() if body_start == -1 else body_start + 1
    body_end = next_heading.start() if next_heading is not None else len(text)
    replacement = goal_body.strip()
    if replacement:
        replacement += "\n\n"
    return text[:body_start] + replacement + text[body_end:]


def _binding_path(path: Path) -> Path:
    return path.with_suffix(".binding.json")


def upsert_goal(
    repo_root: Path,
    *,
    date: str,
    slug: str,
    title: str,
    goal_body: str = "",
) -> dict[str, Any]:
    """Create or update one planning record, refusing a bound draft.

    Existing records are updated only in their title and ``## Goal`` body;
    authored planning sections remain byte-for-byte intact. A sibling binding
    is the freeze boundary and makes the record immutable.
    """
    path = goal_path(repo_root, date, slug)
    rel = goal_rel(repo_root, path)
    title, goal_body = validate_goal_values(title, goal_body)
    if _binding_path(path).exists():
        return {
            "action": "refused",
            "path": rel,
            "reason": "frozen-binding",
            "note": "Goal Binding exists; the frozen Goal Draft cannot be rewritten",
        }

    if not path.exists():
        if not title.strip():
            raise ValueError("goal title is empty; a new planning record needs a title")
        path.parent.mkdir(parents=True, exist_ok=True)
        rendered = _scaffold.render_goal_template(
            _scaffold.TEMPLATE,
            title=title,
            date=date,
            goal_rel_path=rel,
            goal_body=goal_body,
        )
        shape = check_planning_shape(rendered)
        if not shape["ok"]:
            raise ValueError("invalid Goal Draft planning shape: " + "; ".join(shape["issues"]))
        path.write_text(rendered, encoding="utf-8")
        return {"action": "created", "path": rel}

    original = path.read_text(encoding="utf-8")
    updated = original
    if title.strip():
        updated = _replace_goal_heading(updated, title)
    if goal_body.strip():
        updated = _replace_goal_body(updated, goal_body)
    if updated == original:
        return {
            "action": "unchanged",
            "path": rel,
            "note": "planning record already matches supplied fields",
        }
    shape = check_planning_shape(updated)
    if not shape["ok"]:
        raise ValueError("invalid Goal Draft planning shape: " + "; ".join(shape["issues"]))
    path.write_text(updated, encoding="utf-8")
    return {"action": "updated", "path": rel, "note": "updated planning fields only"}


def check_planning_shape(text: str) -> dict[str, Any]:
    """Validate record shape without judging execution or completion."""
    masked = _mask_fences(text)
    missing, _unused, duplicates = _markdown.required_heading_report(
        masked, REQUIRED_SECTIONS, ()
    )
    issues: list[str] = []
    if not _fences_balanced(text):
        issues.append("unbalanced code fence")
    if not _TITLE.search(masked):
        issues.append("missing `# Achieve Goal:` heading")
    if missing:
        issues.append("missing sections: " + ", ".join(missing))
    if duplicates:
        issues.append("duplicate sections: " + ", ".join(duplicates))
    path_portability = _portability.check_goal_path_portability(masked)
    if not path_portability["ok"]:
        issues.extend("path portability: " + issue for issue in path_portability["issues"])
    discussion = _discussion.discussion_readiness(text)
    return {
        "ok": not issues,
        "missing_sections": missing,
        "duplicate_sections": duplicates,
        "path_portability": path_portability,
        "discussion": discussion,
        "issues": issues,
    }


__all__ = [
    "GOAL_DIR",
    "REQUIRED_SECTIONS",
    "check_planning_shape",
    "goal_path",
    "goal_rel",
    "normalize_goal_text",
    "resolve_supplied_slug",
    "slugify",
    "upsert_goal",
    "validate_goal_values",
]
