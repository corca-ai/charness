#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from scripts.repo_file_listing import iter_matching_repo_files
except ModuleNotFoundError:
    from repo_file_listing import iter_matching_repo_files

BULLET_RE = re.compile(r"^[-*]\s+")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
BACKTICK_PATH_RE = re.compile(r"`[^`]+\.[A-Za-z0-9]+`")

DEFAULT_TARGET_GLOBS = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "docs/**/*.md",
    "skills/public/**/SKILL.md",
    "skills/shared/**/*.md",
    "skills/support/**/SKILL.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that `## References` sections are link/path inventory only."
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--target-glob",
        action="append",
        default=[],
        help="Override the default markdown file globs to inspect.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-git-file-listing", action="store_true")
    return parser.parse_args()


def find_references_section(lines: list[str]) -> tuple[int, int] | None:
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "## References":
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return (start + 1, end)


def classify_bullet(text: str) -> str:
    inner = text[2:].strip() if text.startswith(("- ", "* ")) else text.strip()
    if MARKDOWN_LINK_RE.search(inner) or BACKTICK_PATH_RE.search(inner):
        return "link_inventory"
    return "workflow_prose"


def scan_file(path: Path, repo_root: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    section = find_references_section(lines)
    rel = str(path.relative_to(repo_root))
    if section is None:
        return {"path": rel, "has_references_section": False, "findings": []}
    start, end = section
    findings: list[dict[str, object]] = []
    in_bullet = False
    for idx in range(start, end):
        raw = lines[idx]
        stripped = raw.strip()
        if not stripped:
            in_bullet = False
            continue
        if BULLET_RE.match(stripped):
            in_bullet = True
            kind = classify_bullet(stripped)
            if kind == "workflow_prose":
                findings.append({
                    "path": rel,
                    "line": idx + 1,
                    "type": "bullet_without_link_or_path",
                    "snippet": stripped[:120],
                })
            continue
        if stripped.startswith("#"):
            in_bullet = False
            continue
        if in_bullet and raw.startswith(("  ", "\t")):
            continue
        findings.append({
            "path": rel,
            "line": idx + 1,
            "type": "non_bullet_prose",
            "snippet": stripped[:120],
        })
    return {"path": rel, "has_references_section": True, "findings": findings}


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    globs = args.target_glob or list(DEFAULT_TARGET_GLOBS)
    inspected: list[dict[str, object]] = []
    seen: set[Path] = set()
    for path in iter_matching_repo_files(
        repo_root,
        tuple(globs),
        require_git=args.require_git_file_listing,
    ):
        if path in seen:
            continue
        seen.add(path)
        inspected.append(scan_file(path, repo_root))
    flagged = [entry for entry in inspected if entry["findings"]]
    payload = {
        "repo_root": str(repo_root),
        "target_globs": globs,
        "files_with_references_section": sum(1 for entry in inspected if entry["has_references_section"]),
        "flagged_file_count": len(flagged),
        "flagged_files": flagged,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1 if flagged else 0
    if not flagged:
        print(
            f"`## References` link inventory clean across "
            f"{payload['files_with_references_section']} file(s)."
        )
        return 0
    print(
        f"`## References` link inventory drift in {len(flagged)} file(s); "
        f"each `## References` bullet must contain a markdown link or backticked path.",
        file=sys.stderr,
    )
    for entry in flagged:
        for finding in entry["findings"]:
            print(
                f"{finding['path']}:{finding['line']}: {finding['type']}: {finding['snippet']}",
                file=sys.stderr,
            )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
