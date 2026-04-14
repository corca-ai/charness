from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DATE_IN_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})")


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
    return item


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
