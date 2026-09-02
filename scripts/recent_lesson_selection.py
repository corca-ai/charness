"""Own recurrence-aware parsing and ranking for the retro lesson index.

The adjacent ``recent_lessons_lib`` module renders and validates reader-facing
digests. This module owns the distinct selection concept: parse retro evidence,
group lesson identities, apply recency/recurrence weighting, and build the
auditable candidate index.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path
from typing import Any

DATE_IN_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})")
DATE_LINE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
LESSON_INDEX_FILENAME = "lesson-selection-index.json"

# Re-derived 2026-07-27 against the live corpus, from the measured failure that a
# concept holding 7+ rows across 6 dates (2026-05-30 .. 07-26, a 57-day span) never
# won a digest slot. The old pair (alpha 0.35, half-life 14) could not express
# recurrence at all: at 14 days a 50-day-old observation carries weight 0.084, so a
# correctly-counted 5x class scored 0.20 against 1.00 for any same-day one-off --
# recurrence lost 5:1 no matter how many times it bit.
#
# Chosen so a class recurring 5x over 50 days OUTRANKS a 0-day one-off (1.574 vs
# 1.000, a 57% margin rather than the 11% that alpha 0.35 would have left; a thin
# margin silently flips as the corpus moves). The half-life is set to cover the
# observed 57-day recurrence span instead of expiring inside it. Recency still
# decays: the same 5x class falls to 0.21 by 180 days, so a concept that stopped
# recurring drops out rather than holding a slot forever.
#
# The invariant is stated at n=5, which is exactly WARMUP_N -- where alpha saturates,
# so it is the cheapest point at which the invariant can hold. The sub-warmup ladder
# was checked and is deliberately weaker, because twice-seen is not yet evidence of
# a recurring class: at 30 days n=2 scores 0.78 and still loses to a fresh one-off,
# while n=3 reaches 1.08 and just wins. Recurrence earns a slot over roughly three
# independent observations, not two.
# `tests/test_recent_lessons_recurrence.py` pins both ends against these constants.
LESSON_SELECTION_ALPHA_BASE = 0.6
LESSON_SELECTION_WARMUP_N = 5
LESSON_SELECTION_HALF_LIFE_DAYS = 45
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


# Concept identity for a lesson, authored explicitly. `_normalize_lesson_key` keys on
# the first 14 words of the bullet's SURFACE TEXT, so re-wording a lesson resets its
# recurrence count to 1 -- measured, 1594 of 1596 candidates sat at
# `source_count == 1` while one concept held 7+ rows across 6 dates and
# never won a digest slot. A tag is the only identity a re-wording cannot break,
# because a content classifier would rot exactly like the surface text it replaces.
RECURRENCE_CLASS_RE = re.compile(r"(?i)\brecurrence-class[ \t]*:[ \t]*([a-z0-9][a-z0-9-]*)")
_RECURRENCE_CLASS_STRIP_RE = re.compile(
    r"(?i)[\s(\[]*\brecurrence-class[ \t]*:[ \t]*[a-z0-9][a-z0-9-]*[)\]]*"
)


def recurrence_class(text: str) -> str | None:
    """The authored `recurrence-class: <slug>` of a lesson bullet, else None.

    Presence and slug shape only. Whether two bullets REALLY share a concept stays
    the author's and reviewer's judgment, never this function's -- the repo's
    deterministic-floor rule keeps content classification out of gates.
    """
    match = RECURRENCE_CLASS_RE.search(text)
    return match.group(1).lower() if match else None


def strip_recurrence_class(text: str) -> str:
    """The lesson text without its class marker, for display in the digest."""
    return _RECURRENCE_CLASS_STRIP_RE.sub("", text).strip(" \t-–—;,").strip()


def _normalize_lesson_key(text: str) -> str:
    words = re.findall(r"[a-z0-9가-힣]+", text.lower())
    return " ".join(words[:14]) if words else text.strip().lower()


def _candidate_id(kind: str, normalized_key: str) -> str:
    digest = hashlib.sha1(f"{kind}:{normalized_key}".encode("utf-8")).hexdigest()[:12]
    return f"{kind}:{digest}"


def adaptive_lesson_alpha(sample_count: int) -> float:
    warmup_ratio = min(1.0, sample_count / LESSON_SELECTION_WARMUP_N)
    return LESSON_SELECTION_ALPHA_BASE * warmup_ratio


def retro_artifact_paths(output_dir: Path, summary_path: Path | None) -> list[Path]:
    return sorted(
        path
        for path in output_dir.glob("*.md")
        if (summary_path is None or path.resolve() != summary_path.resolve())
        and path.name not in {"recent-lessons.md"}
    )


def _recency_weight(source_date: date | None, as_of: date | None) -> tuple[int | None, float]:
    if source_date is None or as_of is None:
        return None, 0.5
    age_days = max(0, (as_of - source_date).days)
    weight = math.exp(-math.log(2) * age_days / LESSON_SELECTION_HALF_LIFE_DAYS)
    return age_days, weight


def _parse_retro_artifacts(artifacts: list[Path]) -> tuple[list[dict[str, Any]], date | None]:
    parsed_artifacts: list[dict[str, Any]] = []
    dated_values: list[date] = []
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
    return parsed_artifacts, max(dated_values) if dated_values else None


def _collect_lesson_candidates(
    repo_root: Path, parsed_artifacts: list[dict[str, Any]]
) -> dict[tuple[str, str], dict[str, Any]]:
    candidates: dict[tuple[str, str], dict[str, Any]] = {}
    for artifact in parsed_artifacts:
        artifact_path = artifact["path"]
        sections = _extract_sections_loose(artifact["text"])
        source_date_text = artifact["source_date_text"]
        for section_name, kind in LESSON_KINDS.items():
            items = _bullet_items(sections.get(section_name, ""))
            if section_name == "Context" and not items and sections.get(section_name):
                items = [_first_sentence(sections[section_name])]
            for raw_item in items:
                lesson = (
                    _clean_next_improvement(raw_item)
                    if section_name == "Next Improvements"
                    else raw_item
                )
                if not lesson:
                    continue
                lesson_class = recurrence_class(lesson)
                if lesson_class is not None:
                    lesson = strip_recurrence_class(lesson)
                if not lesson:
                    continue
                normalized_key = _normalize_lesson_key(lesson)
                # A tagged lesson groups on its CLASS across every section and date, so
                # the same concept observed in `Waste` here and `Next Improvements`
                # there is one recurring class rather than two one-offs. Untagged
                # lessons keep the historical surface-text key, which is what leaves
                # the 371 already-frozen retros scored exactly as before.
                key = ("class", lesson_class) if lesson_class else (kind, normalized_key)
                entry = candidates.setdefault(
                    key,
                    {
                        "kind": kind,
                        "lesson": lesson,
                        "normalized_key": normalized_key,
                        "recurrence_class": lesson_class,
                        "sources": [],
                    },
                )
                entry["sources"].append(
                    {
                        "artifact_path": str(artifact_path.relative_to(repo_root)),
                        "date": source_date_text,
                        "section": section_name,
                        # Per-source kind and wording, so a class spanning several
                        # sections resolves its display from the NEWEST observation
                        # rather than from whichever filename sorted first.
                        "kind": kind,
                        "lesson": lesson,
                    }
                )
    return candidates


def _candidate_entry(
    kind: str, normalized_key: str, entry: dict[str, Any], as_of: date | None
) -> dict[str, Any]:  # noqa: PLR0914
    source_dates = [_parse_date(source.get("date")) for source in entry["sources"]]
    latest_date = max((value for value in source_dates if value is not None), default=None)
    latest_date_text = latest_date.isoformat() if latest_date else None
    age_days, recency_weight = _recency_weight(latest_date, as_of)
    source_count = len(entry["sources"])
    alpha = adaptive_lesson_alpha(source_count)
    recurrence_multiplier = 1 + alpha * max(0, source_count - 1)
    selection_weight = recency_weight * recurrence_multiplier
    newest_source = max(
        entry["sources"],
        key=lambda source: (source.get("date") or "", source["artifact_path"]),
    )
    latest_source_path = newest_source["artifact_path"]
    lesson_class = entry.get("recurrence_class")
    if lesson_class:
        # Resolve the class's section and wording from its NEWEST observation. Two
        # reasons: artifact order is `sorted(glob(...))`, i.e. lexicographic by
        # filename rather than chronological, so "first seen" was not even the
        # earliest; and the digest cites `latest_source_path`, so showing the oldest
        # wording attributed to the newest retro is a small lie. The section a class
        # renders in follows its latest observation, which is the one the next
        # session is acting on.
        kind = newest_source["kind"]
        lesson_text = newest_source["lesson"]
        # Key the id on the CLASS, not on (kind, first-14-words): a tagged class
        # whose first wording shares its opening words and kind with an untagged
        # bullet elsewhere -- the expected authoring slip of forgetting the tag on
        # one copy -- would otherwise emit two candidates with the same id.
        candidate_id = _candidate_id("class", lesson_class)
    else:
        lesson_text = entry["lesson"]
        candidate_id = _candidate_id(kind, normalized_key)
    return {
        "candidate_id": candidate_id,
        "kind": kind,
        "lesson": lesson_text,
        "normalized_key": normalized_key,
        # None for the untagged historical corpus; a slug once an author declares the
        # concept. Emitted so the index is auditable: a reader can see WHY two rows
        # merged without re-deriving the grouping.
        "recurrence_class": entry.get("recurrence_class"),
        "source_count": source_count,
        "latest_source_path": latest_source_path,
        "latest_source_date": latest_date_text,
        "age_days": age_days,
        "recency_weight": round(recency_weight, 4),
        "alpha": round(alpha, 4),
        "selection_weight": round(selection_weight, 4),
        "sources": sorted(
            entry["sources"], key=lambda source: (source.get("date") or "", source["artifact_path"])
        ),
    }


def _ranked_candidate_entries(
    candidates: dict[tuple[str, str], dict[str, Any]], as_of: date | None
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for (key_head, key_tail), entry in candidates.items():
        # For a class-keyed candidate the tuple head is the literal "class", not a
        # lesson kind; the entry carries the real kind from its first observation.
        kind = entry["kind"] if key_head == "class" else key_head
        normalized_key = entry["normalized_key"] if key_head == "class" else key_tail
        entries.append(_candidate_entry(kind, normalized_key, entry, as_of))
    entries.sort(
        key=lambda entry: (
            -entry["selection_weight"],
            -(entry["source_count"]),
            entry["kind"],
            entry["normalized_key"],
        )
    )
    return entries


def build_lesson_selection_index(
    *,
    repo_root: Path,
    output_dir: Path,
    summary_path: Path | None,
) -> dict[str, Any]:
    artifacts = retro_artifact_paths(output_dir, summary_path)
    parsed_artifacts, as_of = _parse_retro_artifacts(artifacts)
    candidates = _collect_lesson_candidates(repo_root, parsed_artifacts)
    entries = _ranked_candidate_entries(candidates, as_of)
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
