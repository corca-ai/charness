"""Scan portable skill/script bodies for polyglot code/test-surface discovery lists.

The failure class: a portable body hardcodes a *multi-language* test/source-file
discovery list (an extension/glob/suffix constant spanning two or more code
language families). Such a list silently undercounts any language the repo
actually uses but the list does not cover, so the measurement diverges from the
repo's real surface — for example a Node ESM `.mjs` test suite invisible to a
JS/TS-only pattern list. Discovery of a polyglot surface is the consuming repo's
contract, so each such list should be either adapter-owned or an explicitly
marked intentional boundary.

Scope is deliberately narrow: single-purpose globs (`*.md` docs, `*.json`
config, a Python-only `*.py` tool scan) are NOT this class and are not flagged —
they are correctly-typed selectors, not polyglot-surface enumerations that can
omit a language. A site is silenced by an inline ``# discovery-boundary:
<reason>`` marker on the same line or the line directly above (a blank line in
between does not silence). This is a lexical advisory: it forces the
adapter-vs-boundary question to be answered in code; a marked boundary is
trusted here, never verified.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Iterator

DEFAULT_SCAN_ROOTS = ("skills/public", "scripts", "tools")
# The scanner itself is excluded so its own family map does not self-flag.
SELF_EXCLUDED_NAMES = {"discovery_filter_scan_lib.py", "inventory_hardcoded_discovery.py"}
IGNORED_PARTS = {".git", "__pycache__", "mutants", "node_modules", ".venv", "plugins"}

# Core CODE language families only. Docs/config/shell (`.md`, `.json`, `.yaml`,
# `.txt`, `.sh`, `.bash`) are intentionally absent: a list mixing them is not a
# polyglot-code surface enumeration, so it stays out of scope.
CODE_LANGUAGE_FAMILIES: dict[str, frozenset[str]] = {
    "python": frozenset({".py", ".pyi"}),
    "javascript": frozenset({".js", ".jsx", ".mjs", ".cjs"}),
    "typescript": frozenset({".ts", ".tsx", ".mts", ".cts"}),
    "go": frozenset({".go"}),
    "rust": frozenset({".rs"}),
    "ruby": frozenset({".rb"}),
    "java": frozenset({".java", ".kt"}),
    "c-family": frozenset({".c", ".cc", ".cpp", ".h", ".hpp"}),
}
MARKER_RE = re.compile(r"#\s*discovery-boundary:\s*(?P<reason>\S.*)")
# A constant whose NAME advertises discovery patterns (…EXTENSIONS/SUFFIXES/PATTERNS/GLOBS).
DISCOVERY_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*(EXTENSIONS?|SUFFIXES?|PATTERNS?|GLOBS?)$")
_EXT_TOKEN_RE = re.compile(r"\.[A-Za-z0-9]+")


def _string_members(node: ast.AST) -> list[str]:
    if not isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return []
    return [
        element.value
        for element in node.elts
        if isinstance(element, ast.Constant) and isinstance(element.value, str)
    ]


def _code_families(members: list[str]) -> list[str]:
    extensions: set[str] = set()
    for member in members:
        extensions.update(_EXT_TOKEN_RE.findall(member))
    return sorted(
        family for family, family_exts in CODE_LANGUAGE_FAMILIES.items() if extensions & family_exts
    )


def _marker_reason(lines: list[str], lineno: int) -> str | None:
    for candidate in (
        lines[lineno - 1] if lineno - 1 < len(lines) else "",
        lines[lineno - 2] if lineno >= 2 else "",
    ):
        match = MARKER_RE.search(candidate)
        if match:
            return match.group("reason").strip()
    return None


def _scan_text(rel_path: str, text: str, lines: list[str]) -> Iterator[dict[str, Any]]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):  # ValueError = source with null bytes
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        names = [
            target.id
            for target in node.targets
            if isinstance(target, ast.Name) and DISCOVERY_NAME_RE.match(target.id)
        ]
        if not names:
            continue
        members = _string_members(node.value)
        families = _code_families(members)
        if len(families) < 2:
            continue
        reason = _marker_reason(lines, node.lineno)
        yield {
            "path": rel_path,
            "line": node.lineno,
            "constant": names[0],
            "code_families": families,
            "marked_boundary": reason is not None,
            "boundary_reason": reason,
        }


def _iter_python_files(repo_root: Path, scan_roots: list[str]) -> Iterator[Path]:
    for root in scan_roots:
        base = repo_root / root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            if path.name in SELF_EXCLUDED_NAMES:
                continue
            if any(part in IGNORED_PARTS for part in path.relative_to(repo_root).parts):
                continue
            yield path


def scan(repo_root: Path, scan_roots: list[str] | None = None) -> list[dict[str, Any]]:
    roots = list(scan_roots) if scan_roots is not None else list(DEFAULT_SCAN_ROOTS)
    findings: list[dict[str, Any]] = []
    for path in _iter_python_files(repo_root, roots):
        rel_path = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        findings.extend(_scan_text(rel_path, text, text.splitlines()))
    findings.sort(key=lambda hit: (hit["path"], hit["line"]))
    return findings
