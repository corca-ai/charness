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


_blocked_matrix = _load_sibling("goal_artifact_blocked_matrix")
_closeout = _load_sibling("goal_artifact_closeout_evidence")
_discussion = _load_sibling("goal_artifact_discussion")
_draft_frame = _load_sibling("goal_artifact_draft_frame")
_markdown = _load_sibling("goal_artifact_markdown")
_metric_window = _load_sibling("goal_metric_window_lib")
_policy = _load_sibling("achieve_adapter_policy")
_pursue = _load_sibling("goal_artifact_pursue")
_scaffold = _load_sibling("goal_artifact_scaffold")
_timebox = _load_sibling("goal_artifact_timebox")
CLOSEOUT_EVIDENCE_NAMES = _closeout.CLOSEOUT_EVIDENCE_NAMES
NARRATION_REQUIRED_SECTIONS = _closeout.NARRATION_REQUIRED_SECTIONS
parse_closeout_evidence = _closeout.parse_closeout_evidence
check_complete_evidence = _closeout.check_complete_evidence
derive_goal_tokens = _closeout.derive_goal_tokens
narration_sections_present = _closeout.narration_sections_present
discussion_readiness = _discussion.discussion_readiness
# Goal-window evidence recording lives in its own module so this file stays under
# its code-line limit; re-export so callers keep using `goal_artifact_lib`.
render_metric_window_line = _metric_window.render_metric_window_line
record_metric_window = _metric_window.record_metric_window
metric_window_attention = _metric_window.metric_window_attention
check_timebox_closeout = _timebox.check_timebox_closeout
check_blocked_matrix = _blocked_matrix.check
_mask_fences = _markdown.mask_fences
_fences_balanced = _markdown.fences_balanced
slice_plan_data_row_count = _markdown.slice_plan_data_row_count

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

# H2 sections every goal must carry so a fresh session can reconstruct the
# originating context (sources, rejected interview alternatives, and critique
# reasoning) without consulting the saving session's working memory. Required
# on every goal regardless of size: a goal that genuinely has nothing for a
# section keeps the heading and states ``N/A — <reason>``. The retired
# size/marker exemption (a ``Single-slice goal:`` opt-out scanned over the full
# body) because the full-text scan was poisoned by prose merely describing it.
PORTABILITY_SECTIONS = (
    "Context Sources",
    "Interview Decisions",
    "Plan Critique Findings",
)

# The Before-phase placeholder marker moved with the readiness concept to
# `goal_artifact_pursue.UNSHAPED_MARKER` — its only reader. Left as ONE
# definition rather than a second copy here: a repair that duplicates a rule
# instead of moving it is the shape that has come back repeatedly.

_SLICE_HEADING = re.compile(r"^### Slice (\d+):", re.MULTILINE)
_STATUS_LINE = re.compile(r"^Status:[^\n]*$", re.MULTILINE)
_H2 = re.compile(r"^## (.+?)[ \t]*\r?$", re.MULTILINE)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}\Z")  # \Z, not $: `$` also matches before a trailing newline, so a
# date carrying one passed validation and built a filename with an embedded line break.
# A real activation line: its own line (optionally a list item) with a non-empty
# value. The old substring test (`"Activation:" not in text`) passed a goal whose
# only occurrence was a fenced template excerpt or a bare valueless label.
# Prefix class matches the sibling `_CREATED_LINE` in goal_artifact_floor_grammar:
# a bold, bullet or blockquoted `Activation:` line is present, only decorated, and
# refusing it with "missing `Activation:` line" asserts something the code did not
# establish. The shape check is that the line stands on its own and carries a
# non-empty value -- what the old bare `"Activation:" in text` substring never did.
_ACTIVATION_LINE = re.compile(r"^[ \t>*\-]*\**[ \t]*Activation[ \t]*:[ \t]*\**[ \t]*\S", re.MULTILINE)


_TEMPLATE = (Path(__file__).resolve().parent / "goal_artifact_template.md").read_text(encoding="utf-8")


#: What `slugify` returns when the input contained nothing usable. Named because it is
#: the TOTAL-LOSS signature callers refuse on -- not merely "was coerced", which is
#: normal and global.
SLUG_FALLBACK = "goal"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or SLUG_FALLBACK


def goal_path(repo_root: Path, date: str, slug: str) -> Path:
    if not _DATE.match(date):
        raise ValueError(f"invalid date {date!r}; expected YYYY-MM-DD")
    return repo_root / GOAL_DIR / f"{date}-{slugify(slug)}.md"


def goal_rel(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


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


def _section_placeholder_summary(report: dict[str, Any]) -> str:
    entries = report.get("section_placeholders") or []
    return ", ".join(
        f"{entry['section']} line {entry['line']} starts with {entry['marker']!r}"
        for entry in entries
    )


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
            timebox_report = check_timebox_closeout(original)
            if not evidence_report["ok"] or not timebox_report["ok"]:
                placeholder_summary = _section_placeholder_summary(evidence_report)
                placeholder_note = (
                    f" Section placeholders: {placeholder_summary}."
                    if placeholder_summary
                    else ""
                )
                return {
                    "action": "refused",
                    "path": rel,
                    "status": read_status(original) or "unknown",
                    "requested_status": status,
                    "note": (
                        "refused to flip to complete: After-phase evidence missing, "
                        "invalid, unbound, the disposition gate, or a coordination floor "
                        "is unmet, or a timeboxed goal is closing before its closeout window. "
                        "Add bound `Retro:`/`Host log probe:` "
                        "lines (path or `skipped: <enum>: <detail>`); in-scope goals also need "
                        "a bound `Disposition review:` line, a non-blank `## Auto-Retro` (or a "
                        "`Retro dispositions: none — <reason>` opt-out), and any triggered "
                        "`Routing:`/`Gather:`/`Release:`/`Issue closeout:` step in "
                        "`## Coordination Cues`. Each section's first body line must be real "
                        "content, not a pending/TODO/TBD placeholder. For early timebox "
                        "closeout, record why no safe next slice remains. "
                        "See the closeout contract."
                        + placeholder_note
                    ),
                    "evidence_report": evidence_report,
                    "section_placeholder_summary": placeholder_summary,
                    "timebox_report": timebox_report,
                }
        if status == "blocked":
            blocked_refusal = _blocked_matrix.flip_refusal(original, rel, read_status(original))
            if blocked_refusal is not None:
                return blocked_refusal
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
    adapter = _policy.load_adapter(repo_root)
    if adapter["found"] and not adapter["valid"]:
        return {"action": "refused", "path": rel, "status": "missing", "requested_status": status,
                "note": "refused to create goal artifact: achieve adapter is invalid", "adapter_errors": adapter["errors"]}
    path.parent.mkdir(parents=True, exist_ok=True)
    body = _scaffold.render_goal_template(
        _TEMPLATE,
        title=title,
        date=date,
        status=status,
        goal_rel_path=rel,
        frame_lines=adapter["data"]["scaffold"]["draft_active_frame_lines"],
        execution_efficiency_context_path=adapter["data"]["scaffold"]["execution_efficiency_context_path"],
        goal_body=goal_body,
    )
    if status == "blocked":
        # Creating straight to `blocked` would bypass the flip gate, so a fresh
        # goal could reach blocked-on-disk with no boundary matrix. Re-run the
        # floor on the rendered body (no prior status) and refuse if unclean.
        create_refusal = _blocked_matrix.flip_refusal(body, rel, None)
        if create_refusal is not None:
            create_refusal["status"] = "missing"
            return create_refusal
    path.write_text(body, encoding="utf-8")
    return {"action": "created", "path": rel, "status": status}


def next_slice_number(text: str) -> int:
    numbers = [int(match.group(1)) for match in _SLICE_HEADING.finditer(_mask_fences(text))]
    return (max(numbers) + 1) if numbers else 1


PURSUE_SCOPE_NOT_CHECKED = _pursue.SCOPE_NOT_CHECKED


def pursue_readiness(text: str, *, deploy_vocab: tuple[str, ...] | list[str] | None = None) -> dict[str, Any]:
    """Whether a goal is shaped enough to *pursue* via ``/goal``.

    The concept lives in ``goal_artifact_pursue``; this wrapper supplies the two
    facts this module owns -- the artifact's status and the required-heading set
    ``check_goal`` enforces -- so the readiness module never reaches back here.
    """
    return _pursue.pursue_readiness(
        text,
        required_sections=REQUIRED_SECTIONS + PORTABILITY_SECTIONS,
        status=read_status(text),
        deploy_vocab=deploy_vocab,
        mask_fences=_mask_fences,
        fences_balanced=_fences_balanced,
        discussion_readiness=discussion_readiness,
        draft_frame_disposition=_draft_frame.draft_frame_disposition,
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
    if not _fences_balanced(text):
        # `mask_fences` fails open on odd parity, so every check below just read the
        # RAW body, fenced template examples included. Say that, rather than render
        # a verdict over a reading nobody established -- and name the one-character
        # fix, because the alternative repair (pair fences left-to-right and mask
        # everything but the tail) was measured to hide real sections behind a
        # single stray marker.
        issues.append(
            "unbalanced code fence: an unclosed ``` leaves fenced examples readable "
            "as real fields, so fence-masked checks below are unestablished; close it"
        )
    if _ACTIVATION_LINE.search(_mask_fences(text)) is None:
        issues.append("missing `Activation:` line")
    if missing:
        issues.append("missing sections: " + ", ".join(missing))
    portability_missing = [section for section in PORTABILITY_SECTIONS if section not in present]
    if portability_missing:
        issues.append(
            "missing portability sections: "
            + ", ".join(portability_missing)
            + " — every goal keeps these headings (use `N/A — <reason>` if a section is empty)"
        )
    return {
        "ok": not issues,
        "status": status,
        "missing_sections": missing,
        "portability_missing_sections": portability_missing,
        "issues": issues,
    }
