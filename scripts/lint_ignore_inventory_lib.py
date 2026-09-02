from __future__ import annotations

import io
import re
import tokenize
from pathlib import Path
from typing import Any

from scripts.core.repo_file_listing import iter_repo_files
from scripts.core.vendored_path_lib import is_vendored, vendored_prefixes

IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
# discovery-boundary: adapter-owned default — py/js/ts is the built-in set; consumers add other languages' suffixes+directive syntax via the adapter `lint_ignore_discovery.directives`. Suppression detection is language-syntax-specific, so broadening declares a directive matcher, not just an extension.
TEXT_SUFFIXES = {".cjs", ".js", ".jsx", ".mjs", ".py", ".pyi", ".ts", ".tsx"}
PYTHON_NOQA_RE = re.compile(r"# noqa(?::\s*(?P<codes>[A-Za-z0-9_,\s-]+))?", re.IGNORECASE)
PYTHON_RUFF_FILE_RE = re.compile(r"^\s*#\s*ruff:\s*noqa(?:\s*:\s*(?P<codes>.*))?\s*$", re.IGNORECASE)
PYTHON_PYLINT_RE = re.compile(r"#\s*pylint:\s*disable=(?P<codes>[^#]+)", re.IGNORECASE)
PYTHON_RULE_CODE_RE = re.compile(r"[A-Z]+[0-9]+", re.IGNORECASE)
ESLINT_RE = re.compile(
    r"(?:^|\s)(?://|/\*)\s*eslint-disable(?P<scope>-next-line|-line)?(?:\s+(?P<codes>[^*\n]+?))?\s*(?:\*/)?$",
    re.IGNORECASE,
)
_ADAPTER_DIRECTIVE_SCOPES = {"inline", "file", "leading"}

# Advisory interpretation contract (see skills/shared/references/
# advisory-interpretation-contract.md): suppression pressure is an
# inference-layer trend, so the inventory self-declares blind spots and the
# question the `quality` consumer must answer before treating it as debt.
INTERPRETATION = {
    "measures": (
        "lint-suppression sites — `# noqa`, `# ruff: noqa`, `# pylint: disable`, and "
        "`eslint-disable` comments, plus any adapter-declared language directives, "
        "counted by scope (file/inline), blanket-vs-coded, and tool"
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


def _iter_candidate_files(repo_root: Path, vendored: list[str], suffixes: set[str]) -> list[Path]:
    paths: list[Path] = []
    for path in iter_repo_files(repo_root):
        if not path.is_file():
            continue
        if any(part in IGNORED_PARTS for part in path.relative_to(repo_root).parts):
            continue
        if path.suffix.lower() not in suffixes:
            continue
        if is_vendored(repo_root, path, vendored):
            continue
        paths.append(path)
    return sorted(paths)


def _without_description(raw: str) -> str:
    return re.split(r"\s+--\s+", raw, maxsplit=1)[0]


def _parse_named_codes(raw: str | None) -> list[str]:
    cleaned = _without_description(raw or "").replace("*/", " ").replace("(", " ").replace(")", " ")
    return [part.strip() for part in re.split(r"[,\s]+", cleaned) if part.strip()]


def _parse_python_rule_codes(raw: str | None) -> list[str]:
    """Return the leading Ruff/Flake8 rule list, never its human rationale."""
    codes: list[str] = []
    for part in re.split(r"[,\s]+", (raw or "").strip()):
        if not PYTHON_RULE_CODE_RE.fullmatch(part):
            break
        codes.append(part)
    return codes


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
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except tokenize.TokenError:
        return False

    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        line_no, column = token.start
        comment = token.string
        raw = token.line
        if match := PYTHON_RUFF_FILE_RE.match(comment):
            _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="ruff", scope="file", codes=_parse_python_rule_codes(match.group("codes")), raw=raw)
        for match in PYTHON_PYLINT_RE.finditer(comment):
            _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="pylint", scope="file" if column == 0 else "inline", codes=_parse_named_codes(match.group("codes")), raw=raw)
        for match in PYTHON_NOQA_RE.finditer(comment):
            if "ruff:" in comment[: match.start()].lower():
                continue
            scope = "file" if column == 0 and comment.lstrip().lower().startswith("# noqa") else "inline"
            _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="noqa", scope=scope, codes=_parse_python_rule_codes(match.group("codes")), raw=raw)
    return True


def _inventory_text_lines(repo_root: Path, path: Path, text: str, findings: list[dict[str, Any]]) -> None:
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in ESLINT_RE.finditer(line):
            _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="eslint", scope="file" if match.group("scope") is None else "inline", codes=_parse_named_codes(match.group("codes")), raw=line)


def _compile_directives(config: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Compile adapter-declared language directive matchers.

    Suppression detection is language-syntax-specific, so a consuming repo whose
    linters live outside py/js/ts (Go `//nolint`, Ruby `# rubocop:disable`, …)
    declares each directive's suffixes + regex here rather than the portable body
    guessing them. Malformed entries are dropped defensively here; the adapter
    validator is the authoritative shape gate that surfaces them as errors, so a
    bad directive is never a silent no-op.
    """
    compiled: list[dict[str, Any]] = []
    for directive in (config or {}).get("directives") or []:
        if not isinstance(directive, dict):
            continue
        tool = directive.get("tool")
        pattern = directive.get("pattern")
        suffixes = directive.get("suffixes")
        if not (isinstance(tool, str) and tool and isinstance(pattern, str) and pattern):
            continue
        if not (isinstance(suffixes, list) and suffixes and all(isinstance(item, str) and item for item in suffixes)):
            continue
        try:
            regex = re.compile(pattern)
        except re.error:
            continue
        scope = directive.get("scope", "leading")
        compiled.append(
            {
                "tool": tool,
                "suffixes": {item.lower() for item in suffixes},
                "regex": regex,
                "scope": scope if scope in _ADAPTER_DIRECTIVE_SCOPES else "leading",
            }
        )
    return compiled


def _effective_suffixes(directives: list[dict[str, Any]]) -> set[str]:
    suffixes = set(TEXT_SUFFIXES)
    for directive in directives:
        suffixes |= directive["suffixes"]
    return suffixes


def _directive_scope(line: str, match: re.Match[str], scope: str) -> str:
    if scope in {"file", "inline"}:
        return scope
    return "file" if not line[: match.start()].strip() else "inline"


def _inventory_adapter_directives(
    repo_root: Path, path: Path, text: str, findings: list[dict[str, Any]], directives: list[dict[str, Any]]
) -> None:
    applicable = [directive for directive in directives if path.suffix.lower() in directive["suffixes"]]
    if not applicable:
        return
    for line_no, line in enumerate(text.splitlines(), start=1):
        for directive in applicable:
            for match in directive["regex"].finditer(line):
                codes = _parse_named_codes(match.groupdict().get("codes")) if "codes" in match.groupdict() else []
                _record_finding(
                    findings,
                    repo_root=repo_root,
                    path=path,
                    line_no=line_no,
                    tool=directive["tool"],
                    scope=_directive_scope(line, match, directive["scope"]),
                    codes=codes,
                    raw=line,
                )


def inventory_lint_ignores(
    repo_root: Path,
    vendored_paths: list[str] | None = None,
    lint_ignore_discovery: dict[str, Any] | None = None,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    vendored = vendored_prefixes(vendored_paths)
    directives = _compile_directives(lint_ignore_discovery)
    for path in _iter_candidate_files(repo_root, vendored, _effective_suffixes(directives)):
        text = path.read_text(encoding="utf-8", errors="replace")
        _inventory_adapter_directives(repo_root, path, text, findings, directives)
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
                _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="ruff", scope="file", codes=_parse_python_rule_codes(match.group("codes")), raw=line)
            for match in PYTHON_PYLINT_RE.finditer(line):
                _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="pylint", scope="file" if line.lstrip().startswith("#") else "inline", codes=_parse_named_codes(match.group("codes")), raw=line)
            for match in PYTHON_NOQA_RE.finditer(line):
                if "ruff:" in line[: match.start()].lower():
                    continue
                stripped = line.lstrip()
                scope = "file" if stripped.startswith("#") and stripped.lower().startswith("# noqa") else "inline"
                _record_finding(findings, repo_root=repo_root, path=path, line_no=line_no, tool="noqa", scope=scope, codes=_parse_python_rule_codes(match.group("codes")), raw=line)

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
