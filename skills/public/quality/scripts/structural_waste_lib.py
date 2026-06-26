from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path
from typing import Any

PYTEST_COLLECT_RE = re.compile(r"\bpytest\b[^\n]*(?:--collect-only|--collectonly|--co)(?:\s|$)")
BROAD_SCAN_RE = re.compile(r"(?:rglob\(|glob\(|git[^\\n]{0,40}ls-files|Path\.walk|os\.walk)")
PARSER_RE = re.compile(r"\bast\.parse\b")
PREFILTER_RE = re.compile(
    r"(?:\b|_)(?:candidate|prefilter|needle|token|substring|grep|ripgrep|rg|contains)(?:\b|_)",
    re.IGNORECASE,
)
PYTHON_SOURCE_DIRS = ("scripts", "skills/public", "skills/support")
IGNORED_PARTS = {"__pycache__", ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "mutants"}

INTERPRETATION = {
    "measures": "command snippets that repeat broad test discovery and Python helper code that combines broad file discovery with parser work",
    "proxy_for": "quality-gate runtime waste from duplicated discovery/collection or parsing files before a cheap candidate prefilter",
    "blind_spots": "token evidence is conservative and advisory: a broad parser can be justified by correctness, a prefilter can be hidden in a helper, and the inventory does not measure wall-clock by itself",
    "interpretation_question": "is this candidate doing broad discovery or parser work that duplicates an already-owned runner/target list, or should it stay broad for correctness?",
}


def _load_discovery_lib() -> Any:
    module_path = Path(__file__).resolve().with_name("standing_gate_discovery_lib.py")

    spec = importlib.util.spec_from_file_location("standing_gate_discovery_lib", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_DISCOVERY = _load_discovery_lib()
discover_surfaces = _DISCOVERY.discover_surfaces
iter_snippets = _DISCOVERY.iter_snippets


def _tracked_files(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode == 0:
        return sorted(repo_root / rel.decode("utf-8") for rel in result.stdout.split(b"\0") if rel)
    return sorted(path for path in repo_root.rglob("*") if path.is_file())


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def _python_sources(repo_root: Path) -> list[Path]:
    sources = []
    for path in _tracked_files(repo_root):
        try:
            rel = path.relative_to(repo_root)
        except ValueError:
            continue
        if path.suffix == ".py" and rel.parts and rel.parts[0] in PYTHON_SOURCE_DIRS and not _is_ignored(rel):
            sources.append(path)
    return sorted(sources)


def _canonical_runner_candidates(snippets: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        item
        for item in snippets
        if any(token in item["snippet"] for token in ("run_standing_pytest.py", "pytest_targets", "pytest target"))
    ]


def _repo_runner_candidates(repo_root: Path) -> list[dict[str, str]]:
    candidates = []
    for rel_path in ("scripts/run_standing_pytest.py", "scripts/run-quality.sh"):
        if (repo_root / rel_path).is_file():
            candidates.append({"path": rel_path, "origin": "repo-file", "snippet": rel_path})
    return candidates


def _duplicate_discovery_candidates(snippets: list[dict[str, str]], canonical: list[dict[str, str]]) -> list[dict[str, Any]]:
    candidates = []
    for item in snippets:
        snippet = item["snippet"]
        if not PYTEST_COLLECT_RE.search(snippet):
            continue
        duplicate = bool(canonical)
        candidates.append(
            {
                "type": "pytest_collect_only_duplicate" if duplicate else "pytest_collect_only_broad_collection",
                "path": item["path"],
                "origin": item["origin"],
                "snippet": snippet,
                "canonical_runner_count": len(canonical),
                "recommended_action": (
                    "Replace duplicate pytest collection with a canonical runner target list or file-level target coverage when that proves the same contract."
                    if duplicate
                    else "Name the canonical runner or target-list owner before treating this broad collection as duplicated proof."
                ),
            }
        )
    return candidates


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _broad_scanner_candidates(repo_root: Path) -> list[dict[str, Any]]:
    candidates = []
    for path in _python_sources(repo_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not BROAD_SCAN_RE.search(text):
            continue
        parser_matches = list(PARSER_RE.finditer(text))
        if not parser_matches:
            continue
        if PREFILTER_RE.search(text):
            continue
        first_parser = parser_matches[0]
        rel_path = path.relative_to(repo_root).as_posix()
        candidates.append(
            {
                "type": "broad_parser_without_visible_prefilter",
                "path": rel_path,
                "line": _line_number(text, first_parser.start()),
                "parser_token": first_parser.group(0),
                "recommended_action": "Add a cheap path/text candidate prefilter before parser work, or record why full parsing is the correctness boundary.",
            }
        )
    return candidates


def inventory(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    snippets = iter_snippets(discover_surfaces(repo_root))
    canonical = [*_canonical_runner_candidates(snippets), *_repo_runner_candidates(repo_root)]
    duplicate_candidates = _duplicate_discovery_candidates(snippets, canonical)
    scanner_candidates = _broad_scanner_candidates(repo_root)
    findings: list[dict[str, Any]] = []
    if duplicate_candidates:
        has_canonical_duplicate = any(candidate["canonical_runner_count"] for candidate in duplicate_candidates)
        findings.append(
            {
                "type": "duplicate_discovery" if has_canonical_duplicate else "broad_collection_review",
                "severity": "advisory",
                "message": (
                    "One or more gate snippets run broad collection that may duplicate a canonical runner or target list."
                    if has_canonical_duplicate
                    else "One or more gate snippets run broad collection, but no canonical runner or target list was visible."
                ),
                "candidate_count": len(duplicate_candidates),
                "recommended_action": (
                    "Centralize runner target expansion or replace the second collection with file-level target coverage."
                    if has_canonical_duplicate
                    else "Identify the runner/target-list owner first; do not call this duplicate proof until that owner is visible."
                ),
            }
        )
    if scanner_candidates:
        findings.append(
            {
                "type": "broad_scanner_prefilter",
                "severity": "advisory",
                "message": "One or more helper scripts parse broadly discovered files without a visible cheap prefilter.",
                "candidate_count": len(scanner_candidates),
                "recommended_action": "Filter candidate paths or source text before AST/parser work when that preserves correctness.",
            }
        )
    return {
        "repo_root": str(repo_root),
        "command_snippet_count": len(snippets),
        "python_source_count": len(_python_sources(repo_root)),
        "canonical_runner_candidates": canonical,
        "duplicate_discovery_candidates": duplicate_candidates,
        "broad_scanner_candidates": scanner_candidates,
        "findings": findings,
        "interpretation": dict(INTERPRETATION),
    }
