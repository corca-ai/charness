#!/usr/bin/env python3
"""Validate the deterministic part of retro-to-handoff wiring.

This command checks path/goal identity, the cited retro link, and exact
recurrence-class marker coverage. It deliberately does not judge prose meaning
or whether a human disposition is substantively correct.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from runtime_bootstrap import load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_markdown = load_path_module("retro_handoff_markdown", REPO_ROOT / "scripts/markdown_sections.py")


def _load_handoff_paths():
    script_dir = Path(__file__).resolve().parent
    candidates = (
        script_dir / "../skills/public/handoff/scripts/chunked_routing_paths.py",
        script_dir / "../skills/handoff/scripts/chunked_routing_paths.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return load_path_module("retro_handoff_paths", candidate)
    raise ImportError("handoff path normalizer is not available in this Charness tree")


_paths = _load_handoff_paths()
KIND = "charness.retro-handoff-wiring"
SCHEMA_VERSION = 1
_GOAL_FIELD = re.compile(r"^Goal:[ \t]*(?P<value>\S.*?)[ \t]*$")
_LINK = re.compile(r"\[[^\]]+\]\((?P<target>[^)]+)\)")
_MARKER = re.compile(
    r"(?i)(?<![a-z0-9-])recurrence-class[ \t]*:[ \t]*"
    r"(?P<slug>[a-z0-9][a-z0-9-]*)(?![a-z0-9-])"
)
_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")


def _mask_fences(lines: list[str]) -> list[str]:
    masked: list[str] = []
    active: str | None = None
    for line in lines:
        match = _FENCE.match(line)
        if match is not None:
            marker = match.group(1)[0]
            if active is None:
                active = marker
            elif marker == active:
                active = None
            masked.append("")
        else:
            masked.append("" if active is not None else line)
    return masked


def _authored_lines(lines: list[str]) -> list[str]:
    """Mask fenced and blockquoted content, including lazy quote continuations."""
    masked = _mask_fences(lines)
    authored: list[str] = []
    lazy_quote = False
    list_start = re.compile(r"(?:[-+*][ \t]+|\d+[.)][ \t]+)")
    for line in masked:
        stripped = line.strip()
        if not stripped:
            authored.append("")
            lazy_quote = False
            continue
        if stripped.startswith(">"):
            authored.append("")
            lazy_quote = True
            continue
        if lazy_quote:
            if list_start.match(stripped) or stripped.startswith("#"):
                lazy_quote = False
                authored.append(line)
            else:
                authored.append("")
            continue
        authored.append(line)
    return authored


def _repo_file(repo_root: Path, value: str, label: str) -> tuple[str | None, Path | None, str | None]:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    try:
        resolved = candidate.resolve(strict=True)
        relative = resolved.relative_to(repo_root.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError) as exc:
        return None, None, f"{label} is not a regular file inside the repository: {value} ({exc})"
    if not resolved.is_file():
        return None, None, f"{label} is not a regular file inside the repository: {value}"
    return relative, resolved, None


def _top_level_goal(text: str) -> tuple[str | None, str | None]:
    values: list[str] = []
    seen_title = False
    for line in _authored_lines(text.splitlines()):
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("# ") and not seen_title:
            seen_title = True
            continue
        match = _GOAL_FIELD.fullmatch(line)
        if match is not None:
            values.append(match.group("value").strip().strip("`"))
    if len(values) != 1:
        return None, f"retro must contain exactly one top-level Goal field; found {len(values)}"
    return values[0], None


def _link_paths(text: str, *, handoff_path: Path, repo_root: Path) -> tuple[list[str], list[str]]:
    paths: list[str] = []
    escaped: list[str] = []
    base_rel = handoff_path.parent.resolve().relative_to(repo_root.resolve()).as_posix()
    for match in _LINK.finditer(text):
        target = match.group("target").strip().strip("<>")
        if re.match(r"(?i)^(?:https?:|mailto:)", target):
            continue
        target = target.split("#", 1)[0].split("?", 1)[0]
        if target.startswith(("./", "../")) and _paths.resolve_lexically(base_rel, target) is None:
            escaped.append(target)
            continue
        normalized = _paths.normalize_path(
            target,
            artifact_dir=handoff_path.parent,
            repo_root=repo_root,
        )
        if normalized:
            paths.append(normalized)
    return sorted(set(paths)), sorted(set(escaped))


def _normalize_reference(value: str, *, artifact_path: Path, repo_root: Path) -> tuple[str | None, bool]:
    raw = value.strip().strip("`")
    base_rel = artifact_path.parent.resolve().relative_to(repo_root.resolve()).as_posix()
    if raw.startswith(("./", "../")) and _paths.resolve_lexically(base_rel, raw) is None:
        return None, True
    return _paths.normalize_path(raw, artifact_dir=artifact_path.parent, repo_root=repo_root), False


def _markers(lines: list[str]) -> list[str]:
    found: set[str] = set()
    for line in lines:
        for match in _MARKER.finditer(line):
            found.add(match.group("slug").lower())
    return sorted(found)


def _bullet_items(lines: list[str]) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith(">"):
            continue
        if stripped.startswith("- "):
            if current:
                items.append(" ".join(current))
            current = [stripped[2:]]
        elif current and stripped:
            current.append(stripped)
    if current:
        items.append(" ".join(current))
    return items


def validate_wiring(
    repo_root: Path,
    *,
    goal_path: str,
    retro_path: str,
    handoff_path: str,
) -> dict[str, object]:
    errors: list[dict[str, str]] = []
    goal_rel, goal_file, goal_error = _repo_file(repo_root, goal_path, "goal path")
    retro_rel, retro_file, retro_error = _repo_file(repo_root, retro_path, "retro path")
    handoff_rel, handoff_file, handoff_error = _repo_file(repo_root, handoff_path, "handoff path")
    for code, message in (
        ("goal_path_invalid", goal_error),
        ("retro_path_invalid", retro_error),
        ("handoff_path_invalid", handoff_error),
    ):
        if message:
            errors.append({"code": code, "message": message})
    report: dict[str, object] = {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "status": "failed",
        "goal_path": goal_rel,
        "retro_path": retro_rel,
        "handoff_path": handoff_rel,
        "non_claims": [
            "marker coverage does not judge prose meaning or disposition quality",
            "the handoff citation does not prove a fresh handoff write or any external state",
        ],
    }
    if errors:
        report["errors"] = errors
        return report
    assert goal_file is not None and retro_file is not None and handoff_file is not None
    retro_text = retro_file.read_text(encoding="utf-8")
    handoff_text = handoff_file.read_text(encoding="utf-8")
    declared_goal, goal_error = _top_level_goal(retro_text)
    if goal_error:
        errors.append({"code": "retro_goal_missing", "message": goal_error})
    else:
        normalized_goal, goal_escaped = _normalize_reference(
            declared_goal or "", artifact_path=retro_file, repo_root=repo_root
        )
        if goal_escaped:
            errors.append(
                {
                    "code": "retro_goal_path_escape",
                    "message": "retro Goal field escapes the repository",
                }
            )
        if not goal_escaped and normalized_goal != goal_rel:
            errors.append(
                {
                    "code": "retro_goal_mismatch",
                    "message": f"retro Goal field names {normalized_goal!r}, expected {goal_rel!r}",
                }
            )
    next_session = _markdown.section_lines(handoff_text, "## Next Session")
    if not next_session:
        errors.append({"code": "next_session_missing", "message": "handoff ## Next Session is missing or empty"})
    retro_markers = _markers(
        _bullet_items(_authored_lines(_markdown.section_lines(retro_text, "## Next Improvements")))
    )
    next_session_items = _bullet_items(_authored_lines(next_session))
    citation_paths, escaped_citations = _link_paths(
        "\n".join(next_session_items), handoff_path=handoff_file, repo_root=repo_root
    )
    if escaped_citations:
        errors.append(
            {
                "code": "citation_path_escape",
                "message": "handoff contains relative links that escape the repository: "
                + ", ".join(escaped_citations),
            }
        )
    if retro_rel not in citation_paths:
        errors.append(
            {
                "code": "retro_not_cited",
                "message": f"handoff ## Next Session does not cite {retro_rel}",
            }
        )
    handoff_markers = _markers(next_session_items)
    missing_markers = sorted(set(retro_markers) - set(handoff_markers))
    if missing_markers:
        errors.append(
            {
                "code": "recurrence_markers_missing",
                "message": "handoff ## Next Session is missing exact recurrence markers: "
                + ", ".join(missing_markers),
            }
        )
    report.update(
        {
            "status": "passed" if not errors else "failed",
            "retro_goal": declared_goal,
            "retro_citations": citation_paths,
            "retro_markers": retro_markers,
            "handoff_markers": handoff_markers,
            "missing_markers": missing_markers,
            "marker_obligations": "none declared by retro" if not retro_markers else "exact token coverage only",
        }
    )
    if errors:
        report["errors"] = errors
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--goal-path", required=True)
    parser.add_argument("--retro-path", required=True)
    parser.add_argument("--handoff-path", required=True)
    args = parser.parse_args(argv)
    report = validate_wiring(
        args.repo_root.resolve(),
        goal_path=args.goal_path,
        retro_path=args.retro_path,
        handoff_path=args.handoff_path,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
