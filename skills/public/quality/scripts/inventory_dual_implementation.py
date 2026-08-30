#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from git_inventory_lib import (  # noqa: E402
    VisibleRepoFilesSnapshot,
    visible_repo_files,
)
from summary_output_lib import add_output_args, emit_selected, emit_yaml  # noqa: E402

SCHEMA_ID_RE = re.compile(r"\b[a-z0-9_]+(?:\.[a-z0-9_]+){2,}\.v\d+\b")
CODE_EXTENSIONS = {
    ".go": "go",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".py": "python",
    ".rb": "ruby",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".sh": "shell",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root for the duplicate-implementation scan")
    add_output_args(
        parser,
        summary_help="Emit compact YAML candidate counts and samples for triage",
        detail_help="Emit the full duplicate-implementation inventory as YAML",
    )
    return parser.parse_args()


def _iter_code_files(
    repo_root: Path, *, snapshot: VisibleRepoFilesSnapshot | None = None
) -> list[Path]:
    visible_files = visible_repo_files(repo_root, snapshot=snapshot)
    paths: list[Path] = []
    for path in visible_files if visible_files is not None else repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", "__pycache__", "plugins"} for part in path.parts):
            continue
        if path.suffix in CODE_EXTENSIONS:
            paths.append(path)
    return paths


def _schema_hits(
    repo_root: Path, *, snapshot: VisibleRepoFilesSnapshot | None = None
) -> dict[str, list[dict[str, str]]]:
    hits: dict[str, list[dict[str, str]]] = {}
    for path in _iter_code_files(repo_root, snapshot=snapshot):
        text = path.read_text(encoding="utf-8", errors="ignore")
        matches = sorted(set(SCHEMA_ID_RE.findall(text)))
        if not matches:
            continue
        rel_path = path.relative_to(repo_root).as_posix()
        language = CODE_EXTENSIONS[path.suffix]
        for schema_id in matches:
            hits.setdefault(schema_id, []).append({"path": rel_path, "language": language})
    return hits


def _doc_identity_leakage(
    repo_root: Path,
    candidate_paths: list[str],
    *,
    snapshot: VisibleRepoFilesSnapshot | None = None,
) -> list[dict[str, object]]:
    basenames = {Path(path).name for path in candidate_paths}
    findings: list[dict[str, object]] = []
    visible_files = visible_repo_files(repo_root, snapshot=snapshot)
    candidate_docs = visible_files if visible_files is not None else repo_root.rglob("*.md")
    for doc_path in candidate_docs:
        if doc_path.suffix != ".md":
            continue
        if any(part in {".git", ".venv", "node_modules", "__pycache__", "plugins"} for part in doc_path.parts):
            continue
        text = doc_path.read_text(encoding="utf-8", errors="ignore")
        mentioned = sorted(name for name in basenames if name in text)
        if mentioned and len(mentioned) < len(basenames):
            findings.append(
                {
                    "path": doc_path.relative_to(repo_root).as_posix(),
                    "mentioned_paths": mentioned,
                    "missing_paths": sorted(basenames.difference(mentioned)),
                }
            )
    return findings


def build_payload(
    repo_root: Path, *, snapshot: VisibleRepoFilesSnapshot | None = None
) -> dict[str, object]:
    snapshot = snapshot or VisibleRepoFilesSnapshot(visible_repo_files(repo_root))
    schema_hits = _schema_hits(repo_root, snapshot=snapshot)
    candidates: list[dict[str, object]] = []
    for schema_id, hits in sorted(schema_hits.items()):
        languages = sorted({entry["language"] for entry in hits})
        if len(languages) < 2:
            continue
        paths = sorted(entry["path"] for entry in hits)
        doc_leakage = _doc_identity_leakage(repo_root, paths, snapshot=snapshot)
        candidates.append(
            {
                "schema_id": schema_id,
                "languages": languages,
                "paths": paths,
                "doc_identity_leakage": doc_leakage,
                "signals": [
                    "shared_schema_id_across_languages",
                    *(
                        ["doc_identity_leakage"]
                        if doc_leakage
                        else []
                    ),
                ],
                "suggested_actions": [
                    "add a parity harness that feeds identical input through both paths",
                    "pick one path as canonical and delete or wrap the other",
                    "if the divergence is intentional, document it and add a test that asserts the difference",
                ],
            }
        )
    return {
        "candidate_count": len(candidates),
        "candidates": candidates,
        "notes": [
            "This inventory is advisory and intentionally weak-heuristic.",
            "It only proves a likely duplicate when the same schema id appears in code across multiple language groups.",
        ],
    }


def summarize(payload: dict[str, object], *, sample_limit: int = 10) -> dict[str, object]:
    candidates = payload.get("candidates", [])
    return {
        "summary_note": "summary is triage output; use --detail for full candidate evidence",
        "candidate_count": payload["candidate_count"],
        "candidates_sample": candidates[:sample_limit] if isinstance(candidates, list) else [],
        "notes": payload["notes"],
    }


def main() -> int:
    args = parse_args()
    payload = build_payload(args.repo_root.resolve())
    if not emit_selected(payload, args, summarize=summarize):
        emit_yaml(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
