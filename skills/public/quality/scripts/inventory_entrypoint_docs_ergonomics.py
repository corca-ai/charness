#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

DEFAULT_REVIEW_PROMPTS = [
    "Keep first-touch docs concise; let deeper docs own durable procedure and edge cases.",
    "Check progressive disclosure honesty: entrypoint docs should orient the next move, then link to deeper references instead of becoming a second manual.",
    "Trust a smart agent or operator where inference is safe; do not turn every predictable branch into user-facing flags, modes, or procedural prose.",
    "Check whether nearby entrypoint docs duplicate the same setup/update narrative instead of pointing to one maintained owner.",
    "Check inbound links and audience-folder placement before treating a quiet outbound-only inventory as healthy.",
]

DEFAULT_DOC_PATHS = (
    "AGENTS.md",
    "README.md",
    "docs/development.md",
    "docs/operator-acceptance.md",
)

INTERNAL_DOC_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+\.md(?:#[^)]+)?)\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
NUMBERED_PROCEDURE_RE = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)
SKIP_MARKDOWN_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "charness-artifacts",
    "node_modules",
}
CORE_DOCS_TOP_LEVEL = {
    "development.md",
    "handoff.md",
    "operator-acceptance.md",
    "roadmap.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--doc-path", action="append", default=[])
    parser.add_argument("--max-core-lines", type=int, default=140)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def default_doc_paths(repo_root: Path) -> list[str]:
    values = list(DEFAULT_DOC_PATHS)
    docs_dir = repo_root / "docs"
    if docs_dir.is_dir():
        values.extend(str(path.relative_to(repo_root)) for path in sorted(docs_dir.glob("*.md")))
    return values


def iter_doc_paths(repo_root: Path, requested: list[str]) -> Iterable[Path]:
    values = requested or default_doc_paths(repo_root)
    seen: set[Path] = set()
    for value in values:
        path = (repo_root / value).resolve()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        yield path


def iter_markdown_files(repo_root: Path) -> Iterable[Path]:
    for path in sorted(repo_root.rglob("*.md")):
        try:
            relative = path.relative_to(repo_root)
        except ValueError:
            continue
        if any(part in SKIP_MARKDOWN_DIRS for part in relative.parts):
            continue
        if path.is_file():
            yield path


def resolve_doc_link(repo_root: Path, source_path: Path, raw_target: str) -> str | None:
    target = unquote(raw_target.split("#", 1)[0]).strip()
    if not target:
        return None
    target_path = Path(target)
    if target_path.is_absolute():
        target_path = repo_root / str(target_path).lstrip("/")
    else:
        target_path = source_path.parent / target_path
    try:
        return str(target_path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return None


def build_inbound_doc_links(repo_root: Path) -> dict[str, list[str]]:
    inbound: dict[str, list[str]] = {}
    for source_path in iter_markdown_files(repo_root):
        source_rel = str(source_path.relative_to(repo_root))
        text = source_path.read_text(encoding="utf-8", errors="replace")
        for raw_target in INTERNAL_DOC_LINK_RE.findall(text):
            target_rel = resolve_doc_link(repo_root, source_path, raw_target)
            if target_rel is None or target_rel == source_rel:
                continue
            inbound.setdefault(target_rel, []).append(source_rel)
    return {path: sorted(set(sources)) for path, sources in inbound.items()}


def is_top_level_docs_file(repo_root: Path, doc_path: Path) -> bool:
    relative = doc_path.relative_to(repo_root)
    return len(relative.parts) == 2 and relative.parts[0] == "docs"


def inventory_doc(
    repo_root: Path,
    doc_path: Path,
    *,
    max_core_lines: int,
    inbound_links: dict[str, list[str]],
) -> dict[str, object]:
    text = doc_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    nonempty_lines = [line for line in lines if line.strip()]
    lowered = text.lower()
    doc_rel = str(doc_path.relative_to(repo_root))
    inbound_sources = inbound_links.get(doc_rel, [])
    code_fence_count = sum(1 for line in lines if line.strip().startswith("```"))
    internal_doc_link_count = len(INTERNAL_DOC_LINK_RE.findall(text))
    inline_code_count = len(INLINE_CODE_RE.findall(text))
    numbered_procedure_count = len(NUMBERED_PROCEDURE_RE.findall(text))
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
    if doc_path.name == "AGENTS.md" and numbered_procedure_count >= 3:
        heuristics.append("host_instruction_runbook_pressure")
    if is_top_level_docs_file(repo_root, doc_path) and doc_path.name not in CORE_DOCS_TOP_LEVEL:
        heuristics.append("top_level_doc_audience_folder_review")
        if not inbound_sources:
            heuristics.append("top_level_doc_without_inbound_link")

    return {
        "doc_path": doc_rel,
        "core_nonempty_lines": len(nonempty_lines),
        "internal_doc_link_count": internal_doc_link_count,
        "inbound_internal_doc_link_count": len(inbound_sources),
        "inbound_internal_doc_links": inbound_sources,
        "inline_code_count": inline_code_count,
        "code_fence_count": code_fence_count,
        "numbered_procedure_count": numbered_procedure_count,
        "heuristics": heuristics,
        "review_prompts": DEFAULT_REVIEW_PROMPTS,
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    inbound_links = build_inbound_doc_links(repo_root)
    docs = [
        inventory_doc(repo_root, doc_path, max_core_lines=args.max_core_lines, inbound_links=inbound_links)
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
                f"inbound={item['inbound_internal_doc_link_count']} "
                f"inline_code={item['inline_code_count']} "
                f"heuristics={heuristics}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
