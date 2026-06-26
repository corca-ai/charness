from __future__ import annotations

import io
import re
import tokenize
from pathlib import Path
from typing import Any

from scripts.repo_file_listing import iter_repo_files
from scripts.vendored_path_lib import is_vendored, vendored_prefixes

IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
TEXT_SUFFIXES = {".cjs", ".js", ".jsx", ".mjs", ".py", ".pyi", ".ts", ".tsx"}
PYTHON_NOQA_RE = re.compile(r"# noqa(?::\s*(?P<codes>[A-Za-z0-9_,\s-]+))?", re.IGNORECASE)
PYTHON_RUFF_FILE_RE = re.compile(r"^\s*#\s*ruff:\s*noqa(?:\s*:\s*(?P<codes>.*))?\s*$", re.IGNORECASE)
PYTHON_PYLINT_RE = re.compile(r"#\s*pylint:\s*disable=(?P<codes>[^#]+)", re.IGNORECASE)
ESLINT_RE = re.compile(
    r"(?:^|\s)(?://|/\*)\s*eslint-disable(?P<scope>-next-line|-line)?(?:\s+(?P<codes>[^*\n]+?))?\s*(?:\*/)?$",
    re.IGNORECASE,
)

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): suppression pressure is an
# inference-layer trend, so the inventory self-declares blind spots and the
# question the `quality` consumer must answer before treating it as debt.
INTERPRETATION = {
    "measures": (
        "lint-suppression sites — `# noqa`, `# ruff: noqa`, `# pylint: disable`, and "
        "`eslint-disable` comments, counted by scope (file/inline), blanket-vs-coded, "
        "and tool"
    ),
    "proxy_for": "normalized lint debt — suppressions that defer a structural fix instead of paying it",
    "blind_spots": (
        "counts suppression comments, not their justification — an intentional, "
        "provenance-bearing file-level ignore (e.g. a launcher's import-order "
        "`# ruff: noqa: E402`) counts the same as undocumented debt; it cannot read "
        "whether a suppression is cheaper than the fix it defers"
    ),
    "interpretation_question": (
        "which of these suppressions are justified, provenance-bearing deferrals "
        "versus normalized debt THIS repo should structurally fix?"
    ),
}


def _iter_candidate_files(repo_root: Path, vendored: list[str]) -> list[Path]:
    paths: list[Path] = []
    for path in iter_repo_files(repo_root):
        if not path.is_file():
            continue
        if any(part in IGNORED_PARTS for part in path.relative_to(repo_root).parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if is_vendored(repo_root, path, vendored):
            continue
        paths.append(path)
    return sorted(paths)


def _parse_codes(raw: str | None) -> list[str]:
    if not raw:
        return []
    cleaned = raw.replace("*/", " ").replace("(", " ").replace(")", " ")
    return [part.strip() for part in re.split(r"[,\s]+", cleaned) if part.strip()]


def _recommendation(*, tool: str, file_level: bool, blanket: bool) -> str:
    if blanket:
        return "Blanket lint suppression is a strong smell; prefer a structural fix or a rule-specific suppression with a clear reason."
    if file_level and tool == "ruff":
        return "File-level Ruff suppression deserves explicit review; prefer packaging or launcher structure that makes the import order legal."
    if file_level:
        return "File-level lint suppression should be localized or justified before it becomes normal maintenance debt."
    return "Inline suppression should stay narrow, rule-specific, and cheaper than the structural fix it is deferring."


def _record_finding(
    findings: list[dict[str, Any]],
    *,
    repo_root: Path,
    path: Path,
    line_no: int,
    tool: str,
    scope: str,
    codes: list[str],
    raw: str,
) -> None:
    findings.append(
        {
            "path": path.relative_to(repo_root).as_posix(),
            "line": line_no,
            "tool": tool,
            "scope": scope,
            "codes": codes,
            "blanket": not codes,
            "recommendation": _recommendation(tool=tool, file_level=scope == "file", blanket=not codes),
            "snippet": raw.strip(),
        }
    )


def _inventory_python_comments(repo_root: Path, path: Path, text: str, findings: list[dict[str, Any]]) -> bool:
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
    except tokenize.TokenError:
        return False

    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        line_no, column = token.start
        comment = token.string
        raw = token.line
        if match := PYTHON_RUFF_FILE_RE.match(comment):
            _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="ruff", scope="file", codes=_parse_codes(match.group("codes")), raw=raw)
        for match in PYTHON_PYLINT_RE.finditer(comment):
            _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="pylint", scope="file" if column == 0 else "inline", codes=_parse_codes(match.group("codes")), raw=raw)
        for match in PYTHON_NOQA_RE.finditer(comment):
            if "ruff:" in comment[: match.start()].lower():
                continue
            scope = "file" if column == 0 and comment.lstrip().lower().startswith("# noqa") else "inline"
            _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="noqa", scope=scope, codes=_parse_codes(match.group("codes")), raw=raw)
    return True


def _inventory_text_lines(repo_root: Path, path: Path, text: str, findings: list[dict[str, Any]]) -> None:
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in ESLINT_RE.finditer(line):
            _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="eslint", scope="file" if match.group("scope") is None else "inline", codes=_parse_codes(match.group("codes")), raw=line)


def inventory_lint_ignores(repo_root: Path, vendored_paths: list[str] | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    vendored = vendored_prefixes(vendored_paths)
    for path in _iter_candidate_files(repo_root, vendored):
        text = path.read_text(encoding="utf-8", errors="replace")
        lower_text = text.lower()
        has_eslint_marker = "eslint-disable" in lower_text
        has_python_marker = "noqa" in lower_text or "pylint:" in lower_text or "ruff:" in lower_text
        if not has_eslint_marker and not has_python_marker:
            continue

        is_python = path.suffix.lower() in {".py", ".pyi"}
        handled_python = is_python and has_python_marker and _inventory_python_comments(repo_root, path, text, findings)
        if handled_python:
            if has_eslint_marker:
                _inventory_text_lines(repo_root, path, text, findings)
            continue

        if has_eslint_marker:
            _inventory_text_lines(repo_root, path, text, findings)
        if not is_python or not has_python_marker:
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            if match := PYTHON_RUFF_FILE_RE.match(line):
                _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="ruff", scope="file", codes=_parse_codes(match.group("codes")), raw=line)
            for match in PYTHON_PYLINT_RE.finditer(line):
                _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="pylint", scope="file" if line.lstrip().startswith("#") else "inline", codes=_parse_codes(match.group("codes")), raw=line)
            for match in PYTHON_NOQA_RE.finditer(line):
                if "ruff:" in line[: match.start()].lower():
                    continue
                stripped = line.lstrip()
                scope = "file" if stripped.startswith("#") and stripped.lower().startswith("# noqa") else "inline"
                _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="noqa", scope=scope, codes=_parse_codes(match.group("codes")), raw=line)

    return {
        "repo_root": str(repo_root),
        "summary": {
            "ignore_count": len(findings),
            "files_with_ignores": len({finding["path"] for finding in findings}),
            "blanket_count": sum(1 for finding in findings if finding["blanket"]),
            "file_level_count": sum(1 for finding in findings if finding["scope"] == "file"),
            "inline_count": sum(1 for finding in findings if finding["scope"] == "inline"),
            "by_tool": {
                tool: sum(1 for finding in findings if finding["tool"] == tool)
                for tool in sorted({finding["tool"] for finding in findings})
            },
        },
        "review_prompts": [
            "Treat lint suppressions as advisory debt inventory, not invisible background noise.",
            "Blanket or file-level ignores are stronger review targets than narrow rule-specific inline suppressions.",
            "When the same ignore shape repeats, prefer a structural seam over proliferating more comments.",
        ],
        "interpretation": dict(INTERPRETATION),
        "findings": findings,
    }
