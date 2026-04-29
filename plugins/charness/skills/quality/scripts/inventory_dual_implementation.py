#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

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


def _git_visible_repo_files(repo_root: Path) -> set[Path] | None:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return {repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    return parser.parse_args()


def _iter_code_files(repo_root: Path) -> list[Path]:
    visible_files = _git_visible_repo_files(repo_root)
    paths: list[Path] = []
    for path in visible_files if visible_files is not None else repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", "__pycache__", "plugins"} for part in path.parts):
            continue
        if path.suffix in CODE_EXTENSIONS:
            paths.append(path)
    return paths


def _schema_hits(repo_root: Path) -> dict[str, list[dict[str, str]]]:
    hits: dict[str, list[dict[str, str]]] = {}
    for path in _iter_code_files(repo_root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        matches = sorted(set(SCHEMA_ID_RE.findall(text)))
        if not matches:
            continue
        rel_path = path.relative_to(repo_root).as_posix()
        language = CODE_EXTENSIONS[path.suffix]
        for schema_id in matches:
            hits.setdefault(schema_id, []).append({"path": rel_path, "language": language})
    return hits


def _doc_identity_leakage(repo_root: Path, candidate_paths: list[str]) -> list[dict[str, object]]:
    basenames = {Path(path).name for path in candidate_paths}
    findings: list[dict[str, object]] = []
    visible_files = _git_visible_repo_files(repo_root)
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


def build_payload(repo_root: Path) -> dict[str, object]:
    schema_hits = _schema_hits(repo_root)
    candidates: list[dict[str, object]] = []
    for schema_id, hits in sorted(schema_hits.items()):
        languages = sorted({entry["language"] for entry in hits})
        if len(languages) < 2:
            continue
        paths = sorted(entry["path"] for entry in hits)
        doc_leakage = _doc_identity_leakage(repo_root, paths)
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


def main() -> int:
    args = parse_args()
    payload = build_payload(args.repo_root.resolve())
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
