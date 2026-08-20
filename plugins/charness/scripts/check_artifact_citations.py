#!/usr/bin/env python3
"""Syntactically verify ``path:line`` claims in selected durable Markdown.

This is deliberately a citation checker, not a semantic fact checker.  It verifies
that a cited repository path exists, the cited line or range exists, and an inline
identifier named close to the citation is present in that range.  It cannot decide
whether a count, call-graph claim, or prose conclusion is true; the report says so
explicitly instead of turning a syntactic pass into a semantic verdict.

Only caller-selected Markdown below declared artifact roots is scanned.  That path
scope is the historical-corpus grandfather: an old artifact is not re-litigated
merely because a closeout checks a different changed path.  Fenced examples,
ordinary prose numbers, and URLs are not citations.  A non-code, external, or
historical citation must carry ``Citation disposition: <kind>`` in the same or
immediately preceding line so intentional exceptions remain visible and auditable.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

DEFAULT_ARTIFACT_ROOTS = ("charness-artifacts",)
DISPOSITION_VALUES = frozenset(
    {"non-code", "external", "historical", "evidence-only", "semantic-only"}
)
CODE_SUFFIXES = frozenset(
    {
        ".awk",
        ".bash",
        ".c",
        ".cc",
        ".cpp",
        ".css",
        ".go",
        ".h",
        ".hpp",
        ".java",
        ".js",
        ".jsx",
        ".mjs",
        ".php",
        ".pl",
        ".py",
        ".rb",
        ".rs",
        ".sh",
        ".sql",
        ".swift",
        ".ts",
        ".tsx",
        ".zsh",
    }
)

# A slash or a known source suffix keeps dates, ratios, and prose ``5:30`` out.
_PATH_LINE_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"(?P<path>(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+)"
    r":(?P<start>\d+)"
    r"(?:-(?P<end>\d+))?"
    r"(?!\d)"
)
_FENCE_RE = re.compile(r"^[ \t]*(?P<mark>`{3,}|~{3,})")
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_DISPOSITION_RE = re.compile(
    r"\bCitation[ _-]+disposition\s*:\s*(?P<value>[^\n]+)", re.IGNORECASE
)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass(frozen=True)
class Citation:
    artifact: str
    artifact_line: int
    target: str
    start: int
    end: int
    identifier: str | None
    disposition: str | None


@dataclass(frozen=True)
class CitationIssue:
    artifact: str
    artifact_line: int
    citation: str
    reason: str


def _relative_path(repo_root: Path, value: str | Path) -> str | None:
    candidate = Path(value)
    if candidate.is_absolute():
        return None
    try:
        relative = (repo_root / candidate).resolve().relative_to(repo_root.resolve())
    except ValueError:
        return None
    return relative.as_posix()


def _declared_roots(repo_root: Path, roots: Iterable[str | Path]) -> tuple[Path, ...]:
    resolved: list[Path] = []
    for raw in roots:
        relative = _relative_path(repo_root, raw)
        if not relative or relative == ".":
            raise ValueError(f"artifact root must be a non-empty repo-relative path: {raw!r}")
        root = (repo_root / relative).resolve()
        if root not in resolved:
            resolved.append(root)
    if not resolved:
        raise ValueError("at least one declared artifact root is required")
    return tuple(resolved)


def _under_root(path: Path, roots: Sequence[Path]) -> bool:
    resolved = path.resolve()
    return any(resolved == root or root in resolved.parents for root in roots)


def _selected_artifacts(
    repo_root: Path, paths: Iterable[str | Path], roots: Sequence[Path]
) -> list[tuple[str, Path]]:
    selected: dict[str, Path] = {}
    for raw in paths:
        relative = _relative_path(repo_root, raw)
        if relative is None or not relative.lower().endswith(".md"):
            continue
        candidate = (repo_root / relative).resolve()
        if _under_root(candidate, roots) and candidate.is_file():
            selected[relative] = candidate
    return sorted(selected.items())


def _mask_non_assertions(text: str) -> list[str]:
    """Blank fenced blocks and HTML comments while preserving line positions."""
    without_comments = _HTML_COMMENT_RE.sub(
        lambda match: "\n" * match.group(0).count("\n"), text
    )
    masked: list[str] = []
    fence_character: str | None = None
    for line in without_comments.splitlines():
        match = _FENCE_RE.match(line)
        if match:
            character = match.group("mark")[0]
            if fence_character is None:
                fence_character = character
            elif character == fence_character:
                fence_character = None
            masked.append("")
        else:
            masked.append("" if fence_character is not None else line)
    return masked


def _is_candidate_path(path: str) -> bool:
    return "/" in path or Path(path).suffix.lower() in CODE_SUFFIXES or Path(path).suffix


def _disposition(lines: Sequence[str], index: int) -> str | None:
    candidates = [lines[index]]
    if index:
        candidates.append(lines[index - 1])
    for line in candidates:
        match = _DISPOSITION_RE.search(line)
        if not match:
            continue
        value = match.group("value").strip().strip("`*_ ")
        kind = value.split(None, 1)[0].lower()
        if kind not in DISPOSITION_VALUES:
            kind = value.split("—", 1)[0].split(":", 1)[0].strip().lower()
        return kind or ""
    return None


def _nearby_identifier(lines: Sequence[str], index: int, citation: str) -> str | None:
    start = max(0, index - 1)
    stop = min(len(lines), index + 2)
    candidates: list[tuple[int, str]] = []
    for line_index in range(start, stop):
        for match in _INLINE_CODE_RE.finditer(lines[line_index]):
            value = match.group(1).strip()
            if value == citation or _PATH_LINE_RE.fullmatch(value):
                continue
            if _IDENTIFIER_RE.fullmatch(value):
                candidates.append((abs(line_index - index), value))
    return min(candidates, key=lambda item: item[0])[1] if candidates else None


def _parse_line(line: str, *, artifact: str, artifact_line: int, lines: Sequence[str], index: int) -> list[Citation]:
    parsed: list[Citation] = []
    for match in _PATH_LINE_RE.finditer(line):
        target = match.group("path")
        if not _is_candidate_path(target):
            continue
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        citation = match.group(0)
        parsed.append(
            Citation(
                artifact=artifact,
                artifact_line=artifact_line,
                target=target,
                start=start,
                end=end,
                identifier=_nearby_identifier(lines, index, citation),
                disposition=_disposition(lines, index),
            )
        )
    return parsed


def find_citations(artifact: Path, *, repo_root: Path, relative_name: str | None = None) -> list[Citation]:
    text = artifact.read_text(encoding="utf-8")
    lines = _mask_non_assertions(text)
    name = relative_name or artifact.resolve().relative_to(repo_root.resolve()).as_posix()
    citations: list[Citation] = []
    for index, line in enumerate(lines):
        citations.extend(
            _parse_line(line, artifact=name, artifact_line=index + 1, lines=lines, index=index)
        )
    return citations


def _range_lines(target: Path, start: int, end: int) -> tuple[list[str] | None, str | None]:
    if start < 1 or end < start:
        return None, "line range must be one-based with start <= end"
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return None, f"target cannot be read: {exc}"
    if end > len(lines):
        return lines, f"line range {start}-{end} exceeds target length {len(lines)}"
    return lines, None


def _check_one(repo_root: Path, citation: Citation) -> CitationIssue | None:
    if citation.disposition is not None:
        if citation.disposition not in DISPOSITION_VALUES:
            return CitationIssue(
                citation.artifact,
                citation.artifact_line,
                f"{citation.target}:{citation.start}",
                f"unknown Citation disposition {citation.disposition!r}; choose one of {sorted(DISPOSITION_VALUES)}",
            )
        if citation.disposition == "external":
            return None
        if citation.disposition == "non-code" and Path(citation.target).suffix.lower() in CODE_SUFFIXES:
            return CitationIssue(
                citation.artifact,
                citation.artifact_line,
                f"{citation.target}:{citation.start}",
                "non-code disposition contradicts a code target",
            )
    elif Path(citation.target).suffix.lower() not in CODE_SUFFIXES:
        return CitationIssue(
            citation.artifact,
            citation.artifact_line,
            f"{citation.target}:{citation.start}",
            "non-code citation requires explicit `Citation disposition: non-code` (or another intentional disposition)",
        )

    relative = _relative_path(repo_root, citation.target)
    if relative is None:
        return CitationIssue(
            citation.artifact,
            citation.artifact_line,
            f"{citation.target}:{citation.start}",
            "target must be a repository-relative path",
        )
    target = (repo_root / relative).resolve()
    if not target.is_file():
        if citation.disposition in {"historical", "evidence-only", "semantic-only"}:
            return None
        return CitationIssue(
            citation.artifact,
            citation.artifact_line,
            f"{citation.target}:{citation.start}",
            "target path does not exist in the current tree",
        )
    lines, range_error = _range_lines(target, citation.start, citation.end)
    if range_error:
        if citation.disposition in {"historical", "evidence-only", "semantic-only"} and lines is None:
            return None
        return CitationIssue(
            citation.artifact,
            citation.artifact_line,
            f"{citation.target}:{citation.start}-{citation.end}",
            range_error,
        )
    if citation.identifier and not any(
        re.search(rf"(?<![A-Za-z0-9_]){re.escape(citation.identifier)}(?![A-Za-z0-9_])", line)
        for line in lines[citation.start - 1 : citation.end]
    ):
        return CitationIssue(
            citation.artifact,
            citation.artifact_line,
            f"{citation.target}:{citation.start}-{citation.end}",
            f"nearby identifier `{citation.identifier}` is absent from the cited line range",
        )
    return None


def check_artifact_citations(
    repo_root: Path, paths: Iterable[str | Path], *, artifact_roots: Iterable[str | Path] = DEFAULT_ARTIFACT_ROOTS
) -> dict[str, object]:
    """Check selected Markdown and return a structured, non-semantic report."""
    root = repo_root.resolve()
    roots = _declared_roots(root, artifact_roots)
    selected = _selected_artifacts(root, paths, roots)
    citations: list[Citation] = []
    issues: list[CitationIssue] = []
    read_failures: list[CitationIssue] = []
    for relative, artifact in selected:
        try:
            citations.extend(find_citations(artifact, repo_root=root, relative_name=relative))
        except (OSError, UnicodeError) as exc:
            read_failures.append(CitationIssue(relative, 0, relative, f"artifact cannot be read: {exc}"))
    for citation in citations:
        issue = _check_one(root, citation)
        if issue:
            issues.append(issue)
    issues.extend(read_failures)
    return {
        "ok": not issues,
        "status": "findings" if issues else ("checked" if selected else "no-scope"),
        "artifact_roots": [root_path.relative_to(root).as_posix() for root_path in roots],
        "artifacts_checked": [relative for relative, _ in selected],
        "citations_checked": [asdict(citation) for citation in citations],
        "issues": [asdict(issue) for issue in issues],
        "semantic_scope": "syntactic-only",
        "semantic_blind_spots": [
            "truth of the cited claim",
            "counts and quantities in prose",
            "call-graph or runtime reachability",
        ],
    }


def advise_artifact_citations(repo_root: Path, paths: Iterable[str | Path]) -> dict[str, object]:
    """Report changed durable-artifact citations without blocking closeout.

    The closeout consumer owns the path scope; this function owns one structured
    report and the explicit syntactic-only non-claim. A no-scope slice stays quiet,
    while selected artifacts always produce a visible advisory, including findings.
    """
    report = check_artifact_citations(repo_root, paths)
    if report["status"] == "no-scope":
        return report
    print(
        "ADVISORY: durable artifact citation report (syntactic-only; semantic truth "
        "and counts remain unverified):",
        file=sys.stderr,
    )
    print(yaml.safe_dump(report, sort_keys=False), file=sys.stderr, end="")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--paths", nargs="+", required=True, help="changed paths to inspect")
    parser.add_argument("--artifact-root", action="append", dest="artifact_roots")
    args = parser.parse_args(argv)
    try:
        report = check_artifact_citations(
            args.repo_root,
            args.paths,
            artifact_roots=args.artifact_roots or DEFAULT_ARTIFACT_ROOTS,
        )
    except ValueError as exc:
        print(f"artifact citation checker configuration error: {exc}", file=sys.stderr)
        return 2
    print(yaml.safe_dump(report, sort_keys=False), end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
