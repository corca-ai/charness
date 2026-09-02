"""Compatibility surface for retro lesson digest rendering and validation.

Recurrence-aware parsing and candidate indexing live in
``recent_lesson_selection``. This module keeps the original public names while
owning the reader-facing digest, persistence, and stale-index checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.lessons.lesson_command_citation import (  # noqa: E402
    index_build_command,
    refresh_digest_command,
    stale_index_message,
)
from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_selection = import_repo_module(__file__, "scripts.lessons.recent_lesson_selection")
DATE_IN_NAME = _selection.DATE_IN_NAME
DATE_LINE = _selection.DATE_LINE
LESSON_INDEX_FILENAME = _selection.LESSON_INDEX_FILENAME
LESSON_SELECTION_ALPHA_BASE = _selection.LESSON_SELECTION_ALPHA_BASE
LESSON_SELECTION_WARMUP_N = _selection.LESSON_SELECTION_WARMUP_N
LESSON_SELECTION_HALF_LIFE_DAYS = _selection.LESSON_SELECTION_HALF_LIFE_DAYS
LESSON_DIGEST_SLOTS = _selection.LESSON_DIGEST_SLOTS
LESSON_KINDS = _selection.LESSON_KINDS
_date_token = _selection._date_token
_extract_sections = _selection._extract_sections
_extract_sections_loose = _selection._extract_sections_loose
_bullet_items = _selection._bullet_items
_first_sentence = _selection._first_sentence
_clean_next_improvement = _selection._clean_next_improvement
_source_date = _selection._source_date
_parse_date = _selection._parse_date
RECURRENCE_CLASS_RE = _selection.RECURRENCE_CLASS_RE
_RECURRENCE_CLASS_STRIP_RE = _selection._RECURRENCE_CLASS_STRIP_RE
recurrence_class = _selection.recurrence_class
strip_recurrence_class = _selection.strip_recurrence_class
_normalize_lesson_key = _selection._normalize_lesson_key
_candidate_id = _selection._candidate_id
adaptive_lesson_alpha = _selection.adaptive_lesson_alpha
retro_artifact_paths = _selection.retro_artifact_paths
_recency_weight = _selection._recency_weight
_parse_retro_artifacts = _selection._parse_retro_artifacts
_collect_lesson_candidates = _selection._collect_lesson_candidates
_candidate_entry = _selection._candidate_entry
_ranked_candidate_entries = _selection._ranked_candidate_entries
build_lesson_selection_index = _selection.build_lesson_selection_index
lesson_selection_index_path = _selection.lesson_selection_index_path
lesson_selection_index_text = _selection.lesson_selection_index_text


@dataclass
class RecentLessonsDigest:
    source_path: Path
    summary_text: str
    section_counts: dict[str, int]


def pick_latest_retro_markdown(output_dir: Path, summary_path: Path | None) -> Path:
    candidates = [
        path
        for path in output_dir.glob("*.md")
        if (summary_path is None or path.resolve() != summary_path.resolve())
        and path.name != "recent-lessons.md"
    ]
    if not candidates:
        raise FileNotFoundError(f"No retro markdown artifacts found under {output_dir}")
    return max(
        candidates, key=lambda path: (path.stat().st_mtime, _date_token(path.name), path.name)
    )


def write_lesson_selection_index(
    repo_root: Path, output_dir: Path, summary_path: Path | None
) -> Path:
    # The write boundary of the index the four failed publishes corrupted: an
    # An installed-plugin copy of this module once emitted an older schema into a
    # source tree whose own gate then rejected it. Guarding the writer rather than
    # each CLI above it covers every caller.
    # See scripts/core/helper_provenance_lib.py.
    from scripts.core.helper_provenance_lib import require_repo_local_helper

    require_repo_local_helper(__file__, repo_root)
    payload = build_lesson_selection_index(
        repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
    )
    index_path = lesson_selection_index_path(output_dir)
    index_path.write_text(lesson_selection_index_text(payload), encoding="utf-8")
    return index_path


def check_lesson_selection_index(
    repo_root: Path, output_dir: Path, summary_path: Path | None
) -> None:
    payload = build_lesson_selection_index(
        repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
    )
    index_path = lesson_selection_index_path(output_dir)
    expected = lesson_selection_index_text(payload)
    write_command = index_build_command(repo_root, "--write")
    if not index_path.is_file():
        raise FileNotFoundError(
            f"missing retro lesson selection index `{index_path.relative_to(repo_root)}`; "
            f"run `{write_command}`"
        )
    if index_path.read_text(encoding="utf-8") != expected:
        raise ValueError(stale_index_message(str(index_path.relative_to(repo_root)), repo_root))
    if summary_path is None:
        return
    expected_digest = build_indexed_recent_lessons(
        repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
    )
    if not summary_path.is_file():
        raise FileNotFoundError(
            f"missing recent lessons digest `{summary_path.relative_to(repo_root)}`; "
            f"run `{refresh_digest_command(repo_root)}`"
        )
    if summary_path.read_text(encoding="utf-8") != expected_digest.summary_text:
        raise ValueError(
            f"recent lessons digest `{summary_path.relative_to(repo_root)}` is stale relative to the lesson selection index; "
            f"run `{refresh_digest_command(repo_root)}`"
        )


def _fallback_source_path(output_dir: Path, summary_path: Path | None) -> Path:
    try:
        return pick_latest_retro_markdown(output_dir, summary_path)
    except FileNotFoundError:
        if summary_path is None:
            raise
        return summary_path


def _select_digest_candidates(index_payload: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    limit = LESSON_DIGEST_SLOTS[kind]
    return [entry for entry in index_payload["candidates"] if entry.get("kind") == kind][:limit]


def _source_ref(entry: dict[str, Any]) -> str:
    source_path = str(entry.get("latest_source_path") or "")
    source_count = int(entry.get("source_count") or 0)
    if source_count > 1:
        return f"source: `{source_path}`; sources: {source_count}"
    return f"source: `{source_path}`"


def _render_candidate_lines(candidates: list[dict[str, Any]], empty_message: str) -> list[str]:
    if not candidates:
        return [f"- {empty_message}"]
    return [f"- {entry['lesson']} ({_source_ref(entry)})" for entry in candidates]


def build_indexed_recent_lessons(
    *,
    repo_root: Path,
    output_dir: Path,
    summary_path: Path | None,
) -> RecentLessonsDigest:
    if summary_path is None:
        raise ValueError(
            "cannot build recent retro lessons when the retro adapter declares "
            "`summary_path: null`; the lesson projection is disabled"
        )
    index_payload = build_lesson_selection_index(
        repo_root=repo_root, output_dir=output_dir, summary_path=summary_path
    )
    current_focus = _select_digest_candidates(index_payload, "current_focus")
    repeat_traps = _select_digest_candidates(index_payload, "repeat_trap")
    next_checklist = _select_digest_candidates(index_payload, "next_improvement")
    source_paths = sorted(
        {
            source["artifact_path"]
            for entry in current_focus + repeat_traps + next_checklist
            for source in entry["sources"]
        }
    )

    summary_lines = [
        "# Recent Retro Lessons",
        "",
        "## Current Focus",
        "",
        *_render_candidate_lines(
            current_focus, "No current focus bullets found in retro lesson index."
        ),
        "",
        "## Repeat Traps",
        "",
        *_render_candidate_lines(
            repeat_traps, "No repeat traps extracted from retro lesson index."
        ),
        "",
        "## Next-Time Checklist",
        "",
        *_render_candidate_lines(
            next_checklist, "No next improvements extracted from retro lesson index."
        ),
        "",
        "## Selection Policy",
        "",
        "- Source: `charness-artifacts/retro/lesson-selection-index.json`",
        f"- Slots: current_focus={LESSON_DIGEST_SLOTS['current_focus']}, repeat_trap={LESSON_DIGEST_SLOTS['repeat_trap']}, next_improvement={LESSON_DIGEST_SLOTS['next_improvement']}",
        f"- Policy: advisory recency half-life {LESSON_SELECTION_HALF_LIFE_DAYS} days plus recurrence boost with adaptive alpha.",
        "",
        "## Sources",
        "",
    ]
    summary_lines.extend(f"- `{source_path}`" for source_path in source_paths)
    summary_lines.append("")

    return RecentLessonsDigest(
        source_path=_fallback_source_path(output_dir, summary_path),
        summary_text="\n".join(summary_lines),
        section_counts={
            "current_focus": len(current_focus),
            "repeat_traps": len(repeat_traps),
            "next_time_checklist": len(next_checklist),
        },
    )


def build_recent_lessons(source_path: Path, *, repo_root: Path) -> RecentLessonsDigest:
    text = source_path.read_text(encoding="utf-8")
    sections = _extract_sections(text)

    current_focus = _bullet_items(sections.get("Context", ""))[:3]
    if not current_focus and sections.get("Context"):
        current_focus = [_first_sentence(sections["Context"])]
    repeat_traps = _bullet_items(sections.get("Waste", ""))[:4]
    next_checklist = [
        _clean_next_improvement(item)
        for item in _bullet_items(sections.get("Next Improvements", ""))[:5]
    ]

    summary_lines = [
        "# Recent Retro Lessons",
        "",
        "## Current Focus",
        "",
    ]
    summary_lines.extend(
        f"- {item}" for item in current_focus or ["No current focus bullets found in source retro."]
    )
    summary_lines.extend(["", "## Repeat Traps", ""])
    summary_lines.extend(
        f"- {item}" for item in repeat_traps or ["No repeat traps extracted from source retro."]
    )
    summary_lines.extend(["", "## Next-Time Checklist", ""])
    summary_lines.extend(
        f"- {item}"
        for item in next_checklist or ["No next improvements extracted from source retro."]
    )
    summary_lines.extend(
        [
            "",
            "## Sources",
            "",
            f"- `{source_path.relative_to(repo_root)}`",
            "",
        ]
    )
    return RecentLessonsDigest(
        source_path=source_path,
        summary_text="\n".join(summary_lines),
        section_counts={
            "current_focus": len(current_focus),
            "repeat_traps": len(repeat_traps),
            "next_time_checklist": len(next_checklist),
        },
    )
