#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

DEFAULT_REVIEW_PROMPTS = [
    "Keep `SKILL.md` core concise; push nuance and payload into references or scripts.",
    "Check progressive disclosure honesty: core owns selection and sequencing, references deepen rather than fork the workflow.",
    "Treat unnecessary user-facing modes or options as pressure to simplify with stronger defaults and inference.",
    "Check trigger overlap or undertrigger risk against nearby public skills; a smart model still needs an honest invocation boundary.",
    "When the skill repeats prose ritual, prefer a repo-owned helper script over another paragraph.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--skill-path", action="append", default=[])
    parser.add_argument("--max-core-lines", type=int, default=160)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def iter_skill_paths(repo_root: Path, requested: list[str]) -> Iterable[Path]:
    if requested:
        for value in requested:
            path = (repo_root / value).resolve()
            if path.name == "SKILL.md":
                yield path
            else:
                yield path / "SKILL.md"
        return

    for parent in (repo_root / "skills" / "public", repo_root / "skills" / "support"):
        if not parent.is_dir():
            continue
        for skill_path in sorted(parent.glob("*/SKILL.md")):
            if "generated" in skill_path.parts:
                continue
            yield skill_path


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if len(lines) >= 3 and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :])
    return text


def count_files(directory: Path) -> int:
    if not directory.is_dir():
        return 0
    return sum(1 for path in directory.rglob("*") if path.is_file())


def inventory_skill(
    repo_root: Path,
    skill_path: Path,
    *,
    max_core_lines: int,
) -> dict[str, object]:
    skill_dir = skill_path.parent
    relative_skill = skill_dir.relative_to(repo_root)
    body = strip_frontmatter(skill_path.read_text(encoding="utf-8"))
    body_lines = body.splitlines()
    nonempty_lines = [line for line in body_lines if line.strip()]
    lowered = body.lower()
    code_fence_count = sum(1 for line in body_lines if line.strip().startswith("```"))
    reference_count = count_files(skill_dir / "references")
    script_count = count_files(skill_dir / "scripts")
    heuristics: list[str] = []
    if len(nonempty_lines) > max_core_lines:
        heuristics.append("long_core")
    if reference_count == 0 and script_count == 0 and len(nonempty_lines) > 80:
        heuristics.append("progressive_disclosure_risk")
    if lowered.count(" mode") + lowered.count(" modes") >= 2:
        heuristics.append("mode_pressure_terms_present")
    if lowered.count(" option") + lowered.count(" options") >= 2:
        heuristics.append("option_pressure_terms_present")
    if code_fence_count >= 4 and script_count == 0:
        heuristics.append("code_fence_without_helper_script")

    skill_type = "support" if "support" in relative_skill.parts else "public"
    return {
        "skill_id": skill_dir.name,
        "skill_type": skill_type,
        "skill_path": str(skill_path.relative_to(repo_root)),
        "core_nonempty_lines": len(nonempty_lines),
        "reference_file_count": reference_count,
        "script_file_count": script_count,
        "code_fence_count": code_fence_count,
        "heuristics": heuristics,
        "review_prompts": DEFAULT_REVIEW_PROMPTS,
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    skills = [
        inventory_skill(repo_root, skill_path, max_core_lines=args.max_core_lines)
        for skill_path in iter_skill_paths(repo_root, args.skill_path)
        if skill_path.is_file()
    ]
    payload = {
        "repo_root": str(repo_root),
        "max_core_lines": args.max_core_lines,
        "skills": skills,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in skills:
            heuristics = ", ".join(item["heuristics"]) or "none"
            print(
                f"{item['skill_path']}: lines={item['core_nonempty_lines']} "
                f"refs={item['reference_file_count']} scripts={item['script_file_count']} "
                f"heuristics={heuristics}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
