#!/usr/bin/env python3
"""Deprecated compatibility checker; no Charness gate invokes this module."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "being",
        "but",
        "by",
        "do",
        "does",
        "else",
        "for",
        "from",
        "how",
        "if",
        "in",
        "is",
        "it",
        "its",
        "not",
        "of",
        "on",
        "or",
        "so",
        "than",
        "that",
        "the",
        "then",
        "these",
        "this",
        "those",
        "to",
        "was",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "whom",
        "why",
        "with",
        "you",
        "your",
        "into",
        "out",
        "over",
        "under",
        "up",
        "down",
        "via",
        "vs",
        "about",
        "after",
        "before",
        "between",
    }
)
STRUCTURAL_H1 = frozenset(
    {"problem", "decision", "context", "summary", "issue", "draft", "design", "overview", "spec"}
)
STRUCTURAL_SLUGS = frozenset({"skill", "readme", "config", "agents", "claude", "index", "main"})
DEFAULT_ROOTS = (
    Path("docs/specs"),
    Path("charness-artifacts/spec"),
    Path("charness-artifacts/goals"),
)
DEPRECATION_NOTICE = (
    "DEPRECATED: check_title_slug_drift.py is not run by Charness gates; "
    "use bounded rename/title coherence review."
)


def _content_words(text: str) -> set[str]:
    cleaned = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return {token for token in cleaned.split() if len(token) >= 3 and token not in STOPWORDS}


def _h1(path: Path) -> str | None:
    in_fence = False
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and (match := re.match(r"#\s+(.+)$", stripped)):
            return match.group(1).strip()
    return None


def _slug_words(path: Path) -> set[str]:
    name = path.name
    for suffix in (".spec.md", ".md"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return _content_words(name.replace("_", "-").replace(".", "-"))


def find_drift(paths: list[Path]) -> list[dict[str, str | list[str]]]:
    drift: list[dict[str, str | list[str]]] = []
    for path in paths:
        title = _h1(path)
        if not title:
            continue
        title_words = _content_words(title)
        slug_words = _slug_words(path)
        if len(title_words) == 1 and next(iter(title_words)) in STRUCTURAL_H1:
            continue
        if len(slug_words) == 1 and next(iter(slug_words)) in STRUCTURAL_SLUGS:
            continue
        if not title_words or not slug_words or title_words & slug_words:
            continue
        drift.append(
            {
                "path": str(path),
                "title": title,
                "title_words": sorted(title_words),
                "slug_words": sorted(slug_words),
            }
        )
    return drift


def collect_paths(roots: list[Path], include_skill_prose: bool) -> list[Path]:
    paths: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix == ".md":
            paths.append(root)
        elif root.is_dir():
            paths.extend(
                path
                for path in sorted(root.rglob("*.md"))
                if include_skill_prose or "/skills/" not in path.as_posix()
            )
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Deprecated title/slug overlap checker retained for v4 compatibility; "
            "Charness gates no longer invoke it."
        )
    )
    parser.add_argument("roots", nargs="*", type=Path, default=list(DEFAULT_ROOTS))
    parser.add_argument("--include-skill-prose", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when drift is detected.")
    args = parser.parse_args()
    paths = collect_paths(args.roots, args.include_skill_prose)
    drift = find_drift(paths)
    payload = {
        "status": "deprecated",
        "verdict": "finding" if drift else "no-finding-observed",
        "checked": len(paths),
        "drift": drift,
        "roots": [str(root) for root in args.roots],
        "replacement": "bounded rename/title coherence review",
    }
    print(DEPRECATION_NOTICE, file=sys.stderr)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif drift:
        prefix = "" if args.strict else "WARN: "
        print(f"{prefix}title-slug drift in {len(drift)} of {len(paths)} files:")
        for entry in drift:
            print(f"  - {entry['path']}: title={entry['title']!r} slug_words={entry['slug_words']}")
    else:
        print(f"no title-slug drift observed in {len(paths)} files (deprecated advisory scope)")
    return 1 if drift and args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
