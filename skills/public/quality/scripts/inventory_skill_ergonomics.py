#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Iterable


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_scripts_skill_markdown_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.skill_markdown_lib")
count_fence_blocks = _scripts_skill_markdown_lib_module.count_fence_blocks
extract_h2_section_lines = _scripts_skill_markdown_lib_module.extract_h2_section_lines
strip_fenced_lines = _scripts_skill_markdown_lib_module.strip_fenced_lines
strip_frontmatter = _scripts_skill_markdown_lib_module.strip_frontmatter

DEFAULT_REVIEW_PROMPTS = [
    "Keep `SKILL.md` core concise; push nuance and payload into references or scripts.",
    "Check progressive disclosure honesty: core owns selection and sequencing, references deepen rather than fork the workflow.",
    "Treat unnecessary user-facing modes or options as pressure to simplify with stronger defaults and inference.",
    "Check trigger overlap or undertrigger risk against nearby public skills; a smart model still needs an honest invocation boundary.",
    "When the skill repeats prose ritual, prefer a repo-owned helper script over another paragraph.",
    "Check installed-bundle portability: prose helper paths should not read like cwd-relative runtime commands when `$SKILL_DIR` is required.",
]

MODE_TERMS_RE = re.compile(r"\bmode(?:s)?\b", re.IGNORECASE)
OPTION_TERMS_RE = re.compile(r"\boption(?:s)?\b", re.IGNORECASE)
BARE_HELPER_PATH_RE = re.compile(r"`scripts/[A-Za-z0-9._/-]+\.(?:py|sh|bash|zsh|js|ts|rb|pl|lua)`")
SOURCE_TREE_FILE_PATH_RE = re.compile(
    r"`skills/(?:public|support)/[A-Za-z0-9._-]+/[A-Za-z0-9._/-]+\.(?:md|py|sh|bash|zsh|js|ts|rb|pl|lua|yaml|yml|json)`"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--skill-path", action="append", default=[])
    parser.add_argument("--max-core-lines", type=int, default=160)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def iter_skill_paths(repo_root: Path, requested: list[str]) -> Iterable[Path]:
    seen: set[Path] = set()
    if requested:
        for value in requested:
            path = (repo_root / value).resolve()
            skill_path = path if path.name == "SKILL.md" else path / "SKILL.md"
            if skill_path not in seen:
                seen.add(skill_path)
                yield skill_path
        return

    for parent in (repo_root / "skills", repo_root / "skills" / "public", repo_root / "skills" / "support"):
        if not parent.is_dir():
            continue
        for skill_path in sorted(parent.glob("*/SKILL.md")):
            if "generated" in skill_path.parts:
                continue
            if skill_path in seen:
                continue
            seen.add(skill_path)
            yield skill_path


def count_files(directory: Path) -> int:
    if not directory.is_dir():
        return 0
    return sum(1 for path in directory.rglob("*") if path.is_file())


def has_portable_path_ambiguity(lines: list[str]) -> bool:
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- `scripts/"):
            continue
        if "$SKILL_DIR/scripts/" in line or "$SKILL_DIR/../" in line:
            continue
        if BARE_HELPER_PATH_RE.search(line) or SOURCE_TREE_FILE_PATH_RE.search(line):
            return True
    return False


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
    prose_lines = strip_fenced_lines(body_lines)
    prose = "\n".join(prose_lines)
    bootstrap_lines = extract_h2_section_lines(body, "Bootstrap")
    code_fence_count = sum(1 for line in body_lines if line.strip().startswith("```"))
    bootstrap_fence_count = count_fence_blocks(bootstrap_lines)
    reference_count = count_files(skill_dir / "references")
    script_count = count_files(skill_dir / "scripts")
    heuristics: list[str] = []
    if len(nonempty_lines) > max_core_lines:
        heuristics.append("long_core")
    if reference_count == 0 and script_count == 0 and len(nonempty_lines) > 80:
        heuristics.append("progressive_disclosure_risk")
    if len(MODE_TERMS_RE.findall(prose)) >= 2:
        heuristics.append("mode_pressure_terms_present")
    if len(OPTION_TERMS_RE.findall(prose)) >= 2:
        heuristics.append("option_pressure_terms_present")
    if bootstrap_fence_count >= 3 and script_count == 0:
        heuristics.append("code_fence_without_helper_script")
    if has_portable_path_ambiguity(prose_lines):
        heuristics.append("portable_helper_path_ambiguity")

    skill_type = "support" if "support" in relative_skill.parts else "public"
    return {
        "skill_id": skill_dir.name,
        "skill_type": skill_type,
        "skill_path": str(skill_path.relative_to(repo_root)),
        "core_nonempty_lines": len(nonempty_lines),
        "reference_file_count": reference_count,
        "script_file_count": script_count,
        "code_fence_count": code_fence_count,
        "bootstrap_fence_count": bootstrap_fence_count,
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
