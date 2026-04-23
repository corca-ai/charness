from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

DATE_IN_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})")
DATE_LINE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
LESSON_INDEX_FILENAME = "lesson-selection-index.json"
LESSON_SELECTION_ALPHA_BASE = 0.35
LESSON_SELECTION_WARMUP_N = 5
LESSON_SELECTION_HALF_LIFE_DAYS = 14
LESSON_DIGEST_SLOTS = {
    "current_focus": 2,
    "repeat_trap": 4,
    "next_improvement": 4,
}
LESSON_KINDS = {
    "Context": "current_focus",
    "Waste": "repeat_trap",
    "Next Improvements": "next_improvement",
}


@dataclass
class RecentLessonsDigest:
    source_path: Path
    summary_text: str
    section_counts: dict[str, int]


def pick_latest_retro_markdown(output_dir: Path, summary_path: Path) -> Path:
    candidates = [
        path
        for path in output_dir.glob("*.md")
        if path.resolve() != summary_path.resolve() and path.name != "recent-lessons.md"
    ]
    if not candidates:
        raise FileNotFoundError(f"No retro markdown artifacts found under {output_dir}")
    return max(candidates, key=lambda path: (path.stat().st_mtime, _date_token(path.name), path.name))


def _date_token(name: str) -> str:
    match = DATE_IN_NAME.search(name)
    return match.group(1) if match else ""


def _extract_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _extract_sections_loose(text: str) -> dict[str, str]:
    sections = _extract_sections(text)
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in {f"{name}:" for name in LESSON_KINDS}:
            current = stripped[:-1]
            sections.setdefault(current, "")
            continue
        if current is not None:
            existing = sections.get(current, "")
            sections[current] = f"{existing}\n{line}".strip()
    return sections


def _bullet_items(section_text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for raw_line in section_text.splitlines():
        if raw_line.startswith("- "):
            if current:
                items.append(" ".join(part.strip() for part in current if part.strip()))
            current = [raw_line[2:].strip()]
            continue
        if current and raw_line.strip():
            current.append(raw_line.strip())
    if current:
        items.append(" ".join(part.strip() for part in current if part.strip()))
    return [item for item in items if item]


def _first_sentence(text: str) -> str:
    stripped = " ".join(text.split())
    if not stripped:
        return stripped
    for marker in (". ", "? ", "! "):
        if marker in stripped:
            return stripped.split(marker, 1)[0].strip() + marker.strip()
    return stripped


def _clean_next_improvement(item: str) -> str:
    if item.startswith("`") and "`:" in item:
        return item.split("`:", 1)[1].strip()
    if ":" in item:
        prefix, rest = item.split(":", 1)
        if prefix in {"workflow", "capability", "memory", "validation", "tooling"}:
            return rest.strip()
    return item


def _source_date(path: Path, text: str) -> str | None:
    match = DATE_LINE.search(text)
    if match:
        return match.group(1)
    token = _date_token(path.name)
    return token or None


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _normalize_lesson_key(text: str) -> str:
    words = re.findall(r"[a-z0-9가-힣]+", text.lower())
    return " ".join(words[:14]) if words else text.strip().lower()


def _candidate_id(kind: str, normalized_key: str) -> str:
    digest = hashlib.sha1(f"{kind}:{normalized_key}".encode("utf-8")).hexdigest()[:12]
    return f"{kind}:{digest}"


def adaptive_lesson_alpha(sample_count: int) -> float:
    warmup_ratio = min(1.0, sample_count / LESSON_SELECTION_WARMUP_N)
    return LESSON_SELECTION_ALPHA_BASE * warmup_ratio


def retro_artifact_paths(output_dir: Path, summary_path: Path) -> list[Path]:
    return sorted(
        path
        for path in output_dir.glob("*.md")
        if path.resolve() != summary_path.resolve()
        and path.name not in {"recent-lessons.md"}
    )


def _recency_weight(source_date: date | None, as_of: date | None) -> tuple[int | None, float]:
    if source_date is None or as_of is None:
        return None, 0.5
    age_days = max(0, (as_of - source_date).days)
    weight = math.exp(-math.log(2) * age_days / LESSON_SELECTION_HALF_LIFE_DAYS)
    return age_days, weight


def build_lesson_selection_index(
    *,
    repo_root: Path,
    output_dir: Path,
    summary_path: Path,
) -> dict[str, Any]:
    artifacts = retro_artifact_paths(output_dir, summary_path)
    parsed_artifacts: list[dict[str, Any]] = []
    dated_values: list[date] = []
    candidates: dict[tuple[str, str], dict[str, Any]] = {}

    for artifact_path in artifacts:
        text = artifact_path.read_text(encoding="utf-8")
        source_date_text = _source_date(artifact_path, text)
        source_date = _parse_date(source_date_text)
        if source_date is not None:
            dated_values.append(source_date)
        parsed_artifacts.append(
            {
                "path": artifact_path,
                "text": text,
                "source_date_text": source_date_text,
                "source_date": source_date,
            }
        )

    as_of = max(dated_values) if dated_values else None
    for artifact in parsed_artifacts:
        artifact_path = artifact["path"]
        sections = _extract_sections_loose(artifact["text"])
        source_date = artifact["source_date"]
        source_date_text = artifact["source_date_text"]
        for section_name, kind in LESSON_KINDS.items():
            items = _bullet_items(sections.get(section_name, ""))
            if section_name == "Context" and not items and sections.get(section_name):
                items = [_first_sentence(sections[section_name])]
            for raw_item in items:
                lesson = _clean_next_improvement(raw_item) if section_name == "Next Improvements" else raw_item
                if not lesson:
                    continue
                normalized_key = _normalize_lesson_key(lesson)
                key = (kind, normalized_key)
                entry = candidates.setdefault(
                    key,
                    {
                        "kind": kind,
                        "lesson": lesson,
                        "normalized_key": normalized_key,
                        "sources": [],
                    },
                )
                entry["sources"].append(
                    {
                        "artifact_path": str(artifact_path.relative_to(repo_root)),
                        "date": source_date_text,
                        "section": section_name,
                    }
                )

    entries: list[dict[str, Any]] = []
    for (kind, normalized_key), entry in candidates.items():
        source_dates = [_parse_date(source.get("date")) for source in entry["sources"]]
        latest_date = max((value for value in source_dates if value is not None), default=None)
        latest_date_text = latest_date.isoformat() if latest_date else None
        age_days, recency_weight = _recency_weight(latest_date, as_of)
        source_count = len(entry["sources"])
        alpha = adaptive_lesson_alpha(source_count)
        recurrence_multiplier = 1 + alpha * max(0, source_count - 1)
        selection_weight = recency_weight * recurrence_multiplier
        latest_source_path = max(
            entry["sources"],
            key=lambda source: (source.get("date") or "", source["artifact_path"]),
        )["artifact_path"]
        entries.append(
            {
                "candidate_id": _candidate_id(kind, normalized_key),
                "kind": kind,
                "lesson": entry["lesson"],
                "normalized_key": normalized_key,
                "source_count": source_count,
                "latest_source_path": latest_source_path,
                "latest_source_date": latest_date_text,
                "age_days": age_days,
                "recency_weight": round(recency_weight, 4),
                "alpha": round(alpha, 4),
                "selection_weight": round(selection_weight, 4),
                "sources": sorted(entry["sources"], key=lambda source: (source.get("date") or "", source["artifact_path"])),
            }
        )

    entries.sort(
        key=lambda entry: (
            -entry["selection_weight"],
            -(entry["source_count"]),
            entry["kind"],
            entry["normalized_key"],
        )
    )
    return {
        "schema_version": 1,
        "kind": "retro-lesson-selection-index",
        "source": "charness-artifacts/retro/*.md Context/Waste/Next Improvements",
        "selection_policy": {
            "advisory": True,
            "recency_half_life_days": LESSON_SELECTION_HALF_LIFE_DAYS,
            "alpha_base": LESSON_SELECTION_ALPHA_BASE,
            "warmup_n": LESSON_SELECTION_WARMUP_N,
            "recurrence_multiplier": "1 + alpha_t * max(0, source_count - 1)",
            "alpha_t": "alpha_base * min(1, source_count / warmup_n)",
        },
        "as_of_source_date": as_of.isoformat() if as_of else None,
        "source_artifact_count": len(artifacts),
        "candidate_count": len(entries),
        "top_candidates": entries[:12],
        "candidates": entries,
    }


def lesson_selection_index_path(output_dir: Path) -> Path:
    return output_dir / LESSON_INDEX_FILENAME


def lesson_selection_index_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def write_lesson_selection_index(repo_root: Path, output_dir: Path, summary_path: Path) -> Path:
    payload = build_lesson_selection_index(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
    index_path = lesson_selection_index_path(output_dir)
    index_path.write_text(lesson_selection_index_text(payload), encoding="utf-8")
    return index_path


def check_lesson_selection_index(repo_root: Path, output_dir: Path, summary_path: Path) -> None:
    payload = build_lesson_selection_index(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
    index_path = lesson_selection_index_path(output_dir)
    expected = lesson_selection_index_text(payload)
    if not index_path.is_file():
        raise FileNotFoundError(
            f"missing retro lesson selection index `{index_path.relative_to(repo_root)}`; "
            "run `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write`"
        )
    if index_path.read_text(encoding="utf-8") != expected:
        raise ValueError(
            f"retro lesson selection index `{index_path.relative_to(repo_root)}` is stale; "
            "run `python3 scripts/build_retro_lesson_selection_index.py --repo-root . --write`"
        )


def _fallback_source_path(output_dir: Path, summary_path: Path) -> Path:
    try:
        return pick_latest_retro_markdown(output_dir, summary_path)
    except FileNotFoundError:
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
    summary_path: Path,
) -> RecentLessonsDigest:
    index_payload = build_lesson_selection_index(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
    current_focus = _select_digest_candidates(index_payload, "current_focus")
    repeat_traps = _select_digest_candidates(index_payload, "repeat_trap")
    next_checklist = _select_digest_candidates(index_payload, "next_improvement")
    source_paths = sorted({source["artifact_path"] for entry in current_focus + repeat_traps + next_checklist for source in entry["sources"]})

    summary_lines = [
        "# Recent Retro Lessons",
        "",
        "## Current Focus",
        "",
        *_render_candidate_lines(current_focus, "No current focus bullets found in retro lesson index."),
        "",
        "## Repeat Traps",
        "",
        *_render_candidate_lines(repeat_traps, "No repeat traps extracted from retro lesson index."),
        "",
        "## Next-Time Checklist",
        "",
        *_render_candidate_lines(next_checklist, "No next improvements extracted from retro lesson index."),
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
    next_checklist = [_clean_next_improvement(item) for item in _bullet_items(sections.get("Next Improvements", ""))[:5]]

    summary_lines = [
        "# Recent Retro Lessons",
        "",
        "## Current Focus",
        "",
    ]
    summary_lines.extend(f"- {item}" for item in current_focus or ["No current focus bullets found in source retro."])
    summary_lines.extend(["", "## Repeat Traps", ""])
    summary_lines.extend(f"- {item}" for item in repeat_traps or ["No repeat traps extracted from source retro."])
    summary_lines.extend(["", "## Next-Time Checklist", ""])
    summary_lines.extend(f"- {item}" for item in next_checklist or ["No next improvements extracted from source retro."])
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
