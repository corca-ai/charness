from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Callable

ISSUE_ANCHOR_RE = re.compile(
    r"(?:"
    r"\b[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#\d+\b|"
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/\d+\b|"
    r"\bissues/\d+\b|"
    r"\bissue-\d+\b|"
    r"\b(?:issue|bug|pr|pull request)s?\s+#\d+\b|"
    r"(?<![A-Za-z0-9_])#\d{3,}\b"
    r")",
    re.IGNORECASE,
)
DATED_INCIDENT_RE = re.compile(
    r"(?:20\d{2}-\d{2}-\d{2}.{0,80}\b(?:incident|miss|regression|trap|failure|bug|closeout|lesson)s?\b|"
    r"\b(?:incident|miss|regression|trap|failure|bug|closeout|lesson)s?\b.{0,80}20\d{2}-\d{2}-\d{2})",
    re.IGNORECASE,
)
HOST_SURFACE_REFERENCE_RE = re.compile(
    r"\b(?:Claude Code|Codex|settings\.json|host system prompt|host-managed checkout)\b|"
    r"(?:^|[^\w.])\.(?:claude|codex)(?:/|$)",
    re.IGNORECASE,
)
PACKAGE_TEXT_SUFFIXES = {
    ".bash",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}
PACKAGE_TEXT_FILENAMES = {"SKILL.md"}
ISSUE_VERSION_FIELD_RE = re.compile(r"defaults_version\b.*\bissue-\d+\b", re.IGNORECASE)
PLACEHOLDER_ISSUE_URL_RE = re.compile(r"\.\.\./issues/\d+\b")
REFERENCE_LIST_ITEM_RE = re.compile(r"^\s*-\s+`(references/[A-Za-z0-9._/-]+)`(?:\s|$)")


def _is_package_text_file(path: Path) -> bool:
    return path.name in PACKAGE_TEXT_FILENAMES or path.suffix in PACKAGE_TEXT_SUFFIXES


def _iter_package_text_files(skill_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in skill_dir.rglob("*")
        if path.is_file()
        and _is_package_text_file(path)
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
    )


def _excerpt(line: str) -> str:
    return line.strip()[:160]


def _line_findings_for_pattern(
    repo_root: Path,
    skill_dir: Path,
    *,
    heuristic: str,
    pattern: re.Pattern[str],
    skip: Callable[[str], bool] | None = None,
    review_context: Callable[[Path, str], str] | None = None,
) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in _iter_package_text_files(skill_dir):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for index, line in enumerate(lines, start=1):
            if not pattern.search(line):
                continue
            if skip is not None and skip(line):
                continue
            relative_path = path.relative_to(repo_root)
            finding: dict[str, object] = {
                "heuristic": heuristic,
                "path": str(relative_path),
                "line": index,
                "excerpt": _excerpt(line),
            }
            if review_context is not None:
                finding["review_context"] = review_context(relative_path, line)
            findings.append(finding)
    return findings


def is_allowed_issue_anchor_context(line: str) -> bool:
    return bool(ISSUE_VERSION_FIELD_RE.search(line) or PLACEHOLDER_ISSUE_URL_RE.search(line))


def issue_anchor_package_findings(repo_root: Path, skill_dir: Path) -> list[dict[str, object]]:
    return _line_findings_for_pattern(
        repo_root,
        skill_dir,
        heuristic="portable_package_issue_anchor",
        pattern=ISSUE_ANCHOR_RE,
        skip=is_allowed_issue_anchor_context,
    )


def issue_anchor_findings_for_file(repo_root: Path, path: Path) -> list[dict[str, object]]:
    """Disallowed issue-anchor findings for ONE already-resolved package file.

    Same per-line verdict as ``issue_anchor_package_findings`` — the canonical
    ``ISSUE_ANCHOR_RE`` match with the ``is_allowed_issue_anchor_context`` skip —
    but scoped to a single file so an author/preflight surface can flag the file
    just edited before the package-wide commit sweep pays for it. A non-package
    or unreadable file yields no findings (the package sweep ignores it too)."""
    if not _is_package_text_file(path):
        return []
    if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
        return []  # exact parity with `_iter_package_text_files`
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    findings: list[dict[str, object]] = []
    for index, line in enumerate(lines, start=1):
        if not ISSUE_ANCHOR_RE.search(line):
            continue
        if is_allowed_issue_anchor_context(line):
            continue
        findings.append(
            {
                "heuristic": "portable_package_issue_anchor",
                "path": str(path.relative_to(repo_root)),
                "line": index,
                "excerpt": _excerpt(line),
            }
        )
    return findings


def dated_incident_package_findings(repo_root: Path, skill_dir: Path) -> list[dict[str, object]]:
    return _line_findings_for_pattern(
        repo_root,
        skill_dir,
        heuristic="portable_package_dated_incident",
        pattern=DATED_INCIDENT_RE,
    )


def host_surface_review_context(path: Path, line: str) -> str:
    """Route a host-surface hit to its most useful review context.

    This is annotation only: every regex hit remains a finding regardless of
    category, and the portable-prose fallback deliberately asks for the most
    reviewer judgment.
    """
    normalized = f"/{path.as_posix().lower()}"
    name = path.name.lower()
    stem = path.stem.lower()
    line_lower = line.lower()
    # These two high-signal host-policy shapes have dedicated review owners.
    # Check them before broader path/line heuristics so a policy reference is
    # not mislabeled as generic portable prose.
    policy_path = "skills/public/setup/references/agent-docs-policy.md"
    path_text = path.as_posix().lower()
    if path_text == policy_path or path_text.endswith(f"/{policy_path}"):
        return "named-host-integration"
    if (
        ".codex/" in line_lower
        and ".claude/" in line_lower
        and re.search(r"\.(?:ya?ml|json|toml)\b", line_lower)
    ):
        return "adapter-compatibility"
    in_quality_scripts = "/quality/scripts/" in normalized
    if in_quality_scripts and (
        name.startswith(("inventory_", "validate_", "check_"))
        or "skill_text_quality" in name
        or "skill_ergonomics" in name
    ):
        return "detector-definition"
    if name.startswith("adapter.example.") or "/templates/" in normalized:
        return "adapter-mapping"
    if name in {"adapter-contract.md", "adapter-pattern.md"} or stem == "resolve_adapter" or stem.endswith("_adapter_policy"):
        return "adapter-compatibility"
    if path.suffix.lower() == ".json":
        return "policy-fixture"
    integration_path_markers = (
        "goal-artifact",
        "lifecycle",
        "packag",
        "phase-aware",
        "routing",
        "session",
    )
    integration_line_markers = (
        "audit_codex_session",
        "config.toml",
        "host primitive",
        "marketplace",
        "plugin",
        "resolve_skill_path",
        "resolver",
        "rollout jsonl",
        "stop-hook",
        "thread-goal",
    )
    if (
        "/scripts/" in normalized
        or any(marker in normalized for marker in integration_path_markers)
        or any(marker in line_lower for marker in integration_line_markers)
    ):
        return "named-host-integration"
    return "portable-prose"


def host_surface_reference_findings(repo_root: Path, skill_dir: Path) -> list[dict[str, object]]:
    return _line_findings_for_pattern(
        repo_root,
        skill_dir,
        heuristic="portable_package_host_surface_reference",
        pattern=HOST_SURFACE_REFERENCE_RE,
        review_context=host_surface_review_context,
    )


def _add_argument_calls_missing_help(path: Path) -> list[int]:
    """`argparse.add_argument(...)` call sites in one script with no `help=`
    keyword. AST-based (not line-regex) because a real call site routinely
    spans multiple lines; a per-line pattern would miss most of them."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return []
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_argument"
        and not any(keyword.arg == "help" for keyword in node.keywords)
    ]


def argparse_missing_help_findings(repo_root: Path, skill_dir: Path) -> list[dict[str, object]]:
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return []
    findings: list[dict[str, object]] = []
    for path in sorted(scripts_dir.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for lineno in _add_argument_calls_missing_help(path):
            findings.append(
                {
                    "heuristic": "argparse_missing_help",
                    "path": str(path.relative_to(repo_root)),
                    "line": lineno,
                    "excerpt": "add_argument(...) call has no help= string",
                }
            )
    return findings


def _h2_section_lines(contents: str, heading: str) -> list[str]:
    lines = contents.splitlines()
    start: int | None = None
    marker = f"## {heading}"
    for index, line in enumerate(lines):
        if line.strip() == marker:
            start = index + 1
            break
    if start is None:
        return []
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return lines[start:end]


def listed_reference_paths_from_lines(lines: list[str]) -> set[str]:
    return {
        match.group(1)
        for line in lines
        if (match := REFERENCE_LIST_ITEM_RE.match(line))
    }


def reference_discoverability_findings(repo_root: Path, skill_path: Path, body: str) -> list[dict[str, object]]:
    references_dir = skill_path.parent / "references"
    if not references_dir.is_dir():
        return []
    listed_references = listed_reference_paths_from_lines(_h2_section_lines(body, "References"))
    if "references/index.md" in listed_references:
        index_path = skill_path.parent / "references" / "index.md"
        if index_path.is_file():
            listed_references.update(
                listed_reference_paths_from_lines(index_path.read_text(encoding="utf-8").splitlines())
            )
    findings: list[dict[str, object]] = []
    for path in sorted(references_dir.rglob("*")):
        if not path.is_file() or not _is_package_text_file(path):
            continue
        if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
            continue
        relative_to_skill = path.relative_to(skill_path.parent).as_posix()
        if relative_to_skill in listed_references:
            continue
        findings.append(
            {
                "heuristic": "reference_discoverability_gap",
                "path": str(path.relative_to(repo_root)),
                "line": 0,
                "excerpt": f"{relative_to_skill} is not listed in SKILL.md",
            }
        )
    return findings
