#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

DEFAULT_REVIEW_PROMPTS = [
    "Keep first-touch docs concise; let deeper docs own durable procedure and edge cases.",
    "Check progressive disclosure honesty: entrypoint docs should orient the next move, then link to deeper references instead of becoming a second manual.",
    "Trust a smart agent or operator where inference is safe; do not turn every predictable branch into user-facing flags, modes, or procedural prose.",
    "Check whether nearby entrypoint docs duplicate the same setup/update narrative instead of pointing to one maintained owner.",
]

DEFAULT_DOC_PATHS = (
    "AGENTS.md",
    "README.md",
    "INSTALL.md",
    "UNINSTALL.md",
    "docs/development.md",
    "docs/operator-acceptance.md",
)

INTERNAL_DOC_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+\.md(?:#[^)]+)?)\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--doc-path", action="append", default=[])
    parser.add_argument("--max-core-lines", type=int, default=140)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def iter_doc_paths(repo_root: Path, requested: list[str]) -> Iterable[Path]:
    values = requested or list(DEFAULT_DOC_PATHS)
    seen: set[Path] = set()
    for value in values:
        path = (repo_root / value).resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        yield path


def inventory_doc(repo_root: Path, doc_path: Path, *, max_core_lines: int) -> dict[str, object]:
    text = doc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    nonempty_lines = [line for line in lines if line.strip()]
    lowered = text.lower()
    code_fence_count = sum(1 for line in lines if line.strip().startswith("```"))
    internal_doc_link_count = len(INTERNAL_DOC_LINK_RE.findall(text))
    inline_code_count = len(INLINE_CODE_RE.findall(text))
    heuristics: list[str] = []
    if len(nonempty_lines) > max_core_lines:
        heuristics.append("long_entrypoint")
    if len(nonempty_lines) > max_core_lines and internal_doc_link_count == 0:
        heuristics.append("progressive_disclosure_risk")
    if code_fence_count >= 4 and internal_doc_link_count == 0:
        heuristics.append("code_fence_without_deeper_doc_link")
    if lowered.count(" mode") + lowered.count(" modes") >= 2:
        heuristics.append("mode_pressure_terms_present")
    if lowered.count(" option") + lowered.count(" options") + lowered.count(" flag") + lowered.count(" flags") >= 2:
        heuristics.append("option_pressure_terms_present")
    if inline_code_count >= 16 and internal_doc_link_count == 0:
        heuristics.append("inline_code_density_without_deeper_doc_link")

    return {
        "doc_path": str(doc_path.relative_to(repo_root)),
        "core_nonempty_lines": len(nonempty_lines),
        "internal_doc_link_count": internal_doc_link_count,
        "inline_code_count": inline_code_count,
        "code_fence_count": code_fence_count,
        "heuristics": heuristics,
        "review_prompts": DEFAULT_REVIEW_PROMPTS,
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    docs = [
        inventory_doc(repo_root, doc_path, max_core_lines=args.max_core_lines)
        for doc_path in iter_doc_paths(repo_root, args.doc_path)
    ]
    payload = {
        "repo_root": str(repo_root),
        "max_core_lines": args.max_core_lines,
        "documents": docs,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in docs:
            heuristics = ", ".join(item["heuristics"]) or "none"
            print(
                f"{item['doc_path']}: lines={item['core_nonempty_lines']} "
                f"links={item['internal_doc_link_count']} "
                f"inline_code={item['inline_code_count']} "
                f"heuristics={heuristics}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
