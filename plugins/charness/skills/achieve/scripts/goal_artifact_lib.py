"""Conservative markdown helpers for achieve goal artifacts.

A goal artifact lives at ``charness-artifacts/goals/<yyyy-mm-dd-slug>.md`` and is
the living scratchpad for one autonomous goal run. These helpers scaffold the
artifact, append slice reports, and check the artifact shape without churning
manual content.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_shared_helper():
    """Load the repo-owned shared closeout-evidence helper.

    Resolution walks parent directories until ``scripts/`` is found, so the
    helper stays portable across the working tree and any installed export.
    """
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "check_prescribed_skill_executed_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "check_prescribed_skill_executed_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/check_prescribed_skill_executed_lib.py not found")

GOAL_DIR = "charness-artifacts/goals"
VALID_STATUSES = ("draft", "active", "blocked", "complete")

# H2 sections every goal artifact must keep so a compacted run can be audited
# from one file.
REQUIRED_SECTIONS = (
    "Goal",
    "Non-Goals",
    "Boundaries",
    "User Acceptance",
    "Agent Verification Plan",
    "Slice Plan",
    "Slice Log",
    "Off-Goal Findings",
    "Final Verification",
    "User Verification Instructions",
    "Auto-Retro",
)

# H2 sections a non-trivial goal must carry so a fresh session can reconstruct
# the originating context (sources, rejected interview alternatives, and
# critique reasoning) without consulting the saving session's working memory.
# A goal is non-trivial when its Slice Plan table has 2+ data rows, or when
# its Slice Log has 2+ ``### Slice`` headings (execution started).
PORTABILITY_SECTIONS = (
    "Context Sources",
    "Interview Decisions",
    "Plan Critique Findings",
)

_TRIVIAL_GOAL_MARKER = re.compile(r"single-slice goal", re.IGNORECASE)

_SLICE_HEADING = re.compile(r"^### Slice (\d+):", re.MULTILINE)
_STATUS_LINE = re.compile(r"^Status:[^\n]*$", re.MULTILINE)
_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _mask_fences(text: str) -> str:
    """Return ``text`` with fenced code-block regions blanked to spaces.

    Length and newline positions are preserved, so a match found on the masked
    copy maps to the same offset in the real text. Heading and slice-number
    detection runs on the masked copy so that ``##``/``### Slice`` lines pasted
    inside ``` fences are ignored instead of corrupting the artifact.
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
        # Unbalanced fences (an unclosed ``` block) would mask every heading to
        # EOF, which is worse than not masking. Fail open: trust the raw text.
        return text
    return "".join(masked)

_TEMPLATE = """# Achieve Goal: {title}

Status: {status}
Created: {date}
Activation: `/goal @{goal_rel}`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

{goal_body}

## Non-Goals

## Boundaries

## User Acceptance

What the user can do to verify completion directly.

## Agent Verification Plan

### Low-Cost Checks

### High-Confidence Checks

### External Or Live Proof

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

## User Verification Instructions

## Auto-Retro
"""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "goal"


def goal_path(repo_root: Path, date: str, slug: str) -> Path:
    if not _DATE.match(date):
        raise ValueError(f"invalid date {date!r}; expected YYYY-MM-DD")
    return repo_root / GOAL_DIR / f"{date}-{slugify(slug)}.md"


def goal_rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def render_template(*, title: str, date: str, status: str, goal_rel_path: str, goal_body: str) -> str:
    return _TEMPLATE.format(
        title=title,
        date=date,
        status=status,
        goal_rel=goal_rel_path,
        goal_body=goal_body.strip() or "_State the desired outcome before activation._",
    )


def set_status(text: str, status: str) -> str:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status {status!r}; expected one of {VALID_STATUSES}")
    match = _STATUS_LINE.search(_mask_fences(text))
    if match is None:
        raise ValueError("artifact has no `Status:` line to update")
    line = text[match.start():match.end()]
    trailing = "\r" if line.endswith("\r") else ""
    return f"{text[:match.start()]}Status: {status}{trailing}{text[match.end():]}"


def read_status(text: str) -> str | None:
    match = _STATUS_LINE.search(_mask_fences(text))
    if match is None:
        return None
    return text[match.start():match.end()].split(":", 1)[1].strip()


def upsert_goal(
    repo_root: Path,
    *,
    date: str,
    slug: str,
    title: str,
    status: str = "draft",
    goal_body: str = "",
) -> dict[str, Any]:
    """Create the goal artifact when missing, else update only its status.

    Returns a structured result. An existing artifact is never overwritten; only
    the ``Status:`` line is touched, and only when the value actually changes.
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status {status!r}; expected one of {VALID_STATUSES}")
    path = goal_path(repo_root, date, slug)
    rel = goal_rel(repo_root, path)
    if path.exists():
        original = path.read_text(encoding="utf-8")
        if status == "complete" and read_status(original) != "complete":
            evidence_report = check_complete_evidence(repo_root, original)
            if not evidence_report["ok"]:
                return {
                    "action": "refused",
                    "path": rel,
                    "status": read_status(original) or "unknown",
                    "requested_status": status,
                    "note": (
                        "refused to flip to complete: After-phase prescribed sub-skill "
                        "evidence missing or invalid. Add `Retro:` and `Host log probe:` "
                        "lines (path or `skipped: <enum>: <detail>`) to the goal artifact, "
                        "then re-run. See docs/prescribed-skill-closeout-contract.md."
                    ),
                    "evidence_report": evidence_report,
                }
        updated = set_status(original, status)
        changed = updated != original
        if changed:
            path.write_text(updated, encoding="utf-8")
        return {
            "action": "updated" if changed else "unchanged",
            "path": rel,
            "status": status,
            "note": "existing artifact: only Status was changed; title and goal body were left as-is",
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    body = render_template(
        title=title,
        date=date,
        status=status,
        goal_rel_path=rel,
        goal_body=goal_body,
    )
    path.write_text(body, encoding="utf-8")
    return {"action": "created", "path": rel, "status": status}


def next_slice_number(text: str) -> int:
    numbers = [int(match.group(1)) for match in _SLICE_HEADING.finditer(_mask_fences(text))]
    return (max(numbers) + 1) if numbers else 1


def slice_plan_data_row_count(text: str) -> int:
    """Count data rows in the first markdown table inside ``## Slice Plan``.

    Data rows start with ``|`` and are neither the header row nor the table
    separator row (the ``| --- |`` line). Counting against the dominant
    representation (a markdown table) keeps the portability discriminator
    honest; the ``### Slice N:`` heading form is execution intent in
    ``## Slice Log``, not planning intent in ``## Slice Plan``.
    """
    masked = _mask_fences(text)
    headings = list(_H2.finditer(masked))
    section_text: str | None = None
    for index, match in enumerate(headings):
        if match.group(1).strip() != "Slice Plan":
            continue
        body_start = masked.find("\n", match.start())
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(masked)
        section_text = masked[body_start + 1 if body_start != -1 else match.start():body_end]
        break
    if section_text is None:
        return 0
    seen_header = False
    seen_separator = False
    data_rows = 0
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if seen_header:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        is_separator = bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)
        if not seen_header:
            seen_header = True
            continue
        if not seen_separator and is_separator:
            seen_separator = True
            continue
        if is_separator:
            continue
        data_rows += 1
    return data_rows


def is_non_trivial_goal(text: str) -> bool:
    """A goal is non-trivial when planning intent shows ≥2 slices, when
    execution started (≥2 ``### Slice`` headings in the Slice Log), or when
    no explicit ``Single-slice goal:`` exemption marker is present *and* any
    activity exists. A scaffolded empty goal stays trivial."""
    if _TRIVIAL_GOAL_MARKER.search(text):
        return False
    if slice_plan_data_row_count(text) >= 2:
        return True
    masked = _mask_fences(text)
    return sum(1 for _ in _SLICE_HEADING.finditer(masked)) >= 2


def missing_portability_sections(text: str) -> list[str]:
    present = {match.group(1).strip() for match in _H2.finditer(_mask_fences(text))}
    return [section for section in PORTABILITY_SECTIONS if section not in present]


# Closeout-evidence parsing -------------------------------------------------

# After-phase evidence names. The achieve closeout requires a checked-in retro
# artifact plus a host-log probe output; either may be skipped with an
# enum-valid reason (see ``check_prescribed_skill_executed_lib.ALLOWED_SKIP_REASONS``).
CLOSEOUT_EVIDENCE_NAMES = ("retro_artifact", "host_log_probe")

_EVIDENCE_LINE = re.compile(
    r"^[\s>*-]*(Retro|Host[- ]log[- ]probe)\s*:\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def _normalize_evidence_name(label: str) -> str:
    label = label.strip().lower()
    if label == "retro":
        return "retro_artifact"
    if re.fullmatch(r"host[- ]log[- ]probe", label):
        return "host_log_probe"
    return label.replace(" ", "_").replace("-", "_")


def parse_closeout_evidence(text: str) -> dict[str, dict[str, str]]:
    """Extract ``Retro:`` and ``Host log probe:`` lines from the goal body.

    Returns ``{name: {"kind": "evidence"|"skip", "value": <path-or-reason>}}``.
    A value that starts with ``skipped:`` (case-insensitive) is treated as a
    skip and the remaining text is the reason; otherwise the value is a
    repo-relative or absolute path to the evidence file.
    """
    masked = _mask_fences(text)
    parsed: dict[str, dict[str, str]] = {}
    for match in _EVIDENCE_LINE.finditer(masked):
        name = _normalize_evidence_name(match.group(1))
        raw_value = match.group(2).strip()
        if not raw_value:
            continue
        skip_match = re.match(r"^skipped\s*:\s*(.+)$", raw_value, re.IGNORECASE)
        if skip_match:
            parsed[name] = {"kind": "skip", "value": skip_match.group(1).strip()}
        else:
            parsed[name] = {"kind": "evidence", "value": raw_value}
    return parsed


def check_complete_evidence(repo_root: Path, text: str) -> dict[str, Any]:
    """Run the shared closeout-evidence helper for an ``achieve`` After-phase.

    The wrapper extracts ``Retro:`` and ``Host log probe:`` lines from the
    goal artifact body and feeds them as evidence/skip arguments to the
    portable ``check`` function. The wrapper supplies the contract
    (CLOSEOUT_EVIDENCE_NAMES); the helper is the gate.
    """
    helper = _load_shared_helper()
    parsed = parse_closeout_evidence(text)
    evidence: dict[str, str] = {}
    skips: dict[str, str] = {}
    for name, payload in parsed.items():
        if payload["kind"] == "evidence":
            evidence[name] = payload["value"]
        else:
            skips[name] = payload["value"]
    return helper.check(
        repo_root=repo_root,
        required=list(CLOSEOUT_EVIDENCE_NAMES),
        evidence=evidence,
        skips=skips,
        kind="achieve-after",
    )


def render_slice_block(number: int, name: str, fields: dict[str, str]) -> str:
    lines = [f"### Slice {number}: {name}", ""]
    for label in (
        "Objective",
        "Why this approach",
        "Commits",
        "What changed",
        "Alternatives rejected",
        "Targeted verification",
        "Test duplication pressure",
        "Critique",
        "Off-goal findings",
        "Lessons carried forward",
        "Metrics",
    ):
        value = fields.get(label, "").strip()
        lines.append(f"- {label}: {value}" if value else f"- {label}:")
    return "\n".join(lines) + "\n"


def append_slice(text: str, slice_block: str) -> str:
    """Insert a slice block at the end of the ``## Slice Log`` section."""
    headings = list(_H2.finditer(_mask_fences(text)))
    for index, match in enumerate(headings):
        if match.group(1).strip() != "Slice Log":
            continue
        newline = text.find("\n", match.start())
        heading_line_end = len(text) if newline == -1 else newline + 1
        section_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        existing = text[heading_line_end:section_end].strip("\n")
        block = slice_block.strip("\n")
        body = f"{existing}\n\n{block}" if existing else block
        suffix = "\n" if section_end == len(text) else f"\n\n{text[section_end:]}"
        return f"{text[:heading_line_end]}\n{body}{suffix}"
    raise ValueError("artifact has no `## Slice Log` section")


def check_goal(text: str) -> dict[str, Any]:
    present = {match.group(1).strip() for match in _H2.finditer(_mask_fences(text))}
    missing = [section for section in REQUIRED_SECTIONS if section not in present]
    status = read_status(text)
    issues: list[str] = []
    if status is None:
        issues.append("missing `Status:` line")
    elif status not in VALID_STATUSES:
        issues.append(f"status {status!r} is not one of {VALID_STATUSES}")
    if "Activation:" not in text:
        issues.append("missing `Activation:` line")
    if missing:
        issues.append("missing sections: " + ", ".join(missing))
    portability_missing: list[str] = []
    if is_non_trivial_goal(text):
        portability_missing = [section for section in PORTABILITY_SECTIONS if section not in present]
        if portability_missing:
            issues.append(
                "missing portability sections (non-trivial goal): "
                + ", ".join(portability_missing)
                + " — add the sections or mark with `Single-slice goal:` to exempt"
            )
    return {
        "ok": not issues,
        "status": status,
        "missing_sections": missing,
        "portability_missing_sections": portability_missing,
        "issues": issues,
    }
