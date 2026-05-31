from __future__ import annotations

import re
from pathlib import Path

INLINE_COMMAND_RE = re.compile(r"`([^`\n]+)`")
INLINE_PATH_RE = re.compile(r"`([^`\n]+)`")
BARE_RUNTIME_SCRIPT_INVOCATION_RE = re.compile(
    r"\b(?:python3|python|bash|sh|zsh)\s+scripts/(?P<rel>[A-Za-z0-9._/-]+\.[A-Za-z0-9]+)\b"
)
SOURCE_TREE_SKILL_INVOCATION_RE = re.compile(
    r"\b(?:python3|python|bash|sh|zsh|sed|cat|head|tail|rg|find)\b[^`\n]*"
    r"(?P<rel>skills/(?:public|support)/[A-Za-z0-9._-]+/[^\s`]+)"
)
AUTHORING_MARKER_RE = re.compile(
    r"\b(?:authoring-repo-internal|in the charness source repo|not vendored)\b",
    re.IGNORECASE,
)
OPERATOR_DOCS = {
    "docs/handoff.md",
    "docs/roadmap.md",
    "docs/operator-acceptance.md",
    "docs/release-notes.md",
}


def iter_command_like_snippets(contents: str) -> list[tuple[int, str]]:
    snippets: list[tuple[int, str]] = []
    for line_no, line in enumerate(contents.splitlines(), start=1):
        snippets.append((line_no, line))
        for match in INLINE_COMMAND_RE.finditer(line):
            snippets.append((line_no, match.group(1)))
    return snippets


def find_portability_errors(root: Path, skill_dir: Path, contents: str) -> list[str]:
    errors: list[str] = []
    for line_no, snippet in iter_command_like_snippets(contents):
        bare_script_match = BARE_RUNTIME_SCRIPT_INVOCATION_RE.search(snippet)
        if bare_script_match:
            rel = bare_script_match.group("rel")
            runtime_candidate = root / "scripts" / rel
            skill_candidate = skill_dir / "scripts" / rel
            if runtime_candidate.is_file() or skill_candidate.is_file():
                errors.append(
                    f"line {line_no}: runtime helper invocation `scripts/{rel}` is cwd-relative; "
                    "use `$SKILL_DIR/...` for skill-bundled helpers or a portable sibling-skill path instead"
                )

        source_tree_match = SOURCE_TREE_SKILL_INVOCATION_RE.search(snippet)
        if source_tree_match:
            rel = source_tree_match.group("rel")
            if (root / rel).exists():
                errors.append(
                    f"line {line_no}: source-tree skill path `{rel}` is not portable in execution examples; "
                    "use `$SKILL_DIR/...` or a portable sibling-skill path instead"
                )
    return errors


def _nearby_authoring_marker(lines: list[str], line_no: int) -> bool:
    start = max(1, line_no - 3)
    end = min(len(lines), line_no + 3)
    return any(AUTHORING_MARKER_RE.search(lines[index - 1]) for index in range(start, end + 1))


def _unfenced_line_numbers(lines: list[str]) -> set[int]:
    visible: set[int] = set()
    in_fence = False
    for line_no, line in enumerate(lines, start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            visible.add(line_no)
    return visible if not in_fence else set(range(1, len(lines) + 1))


def _normalize_authoring_path(raw: str) -> str | None:
    value = raw.strip()
    value = value.split("::", 1)[0].split("#", 1)[0].strip()
    repo_root_absolute = value.startswith("<repo-root>/")
    if repo_root_absolute:
        value = value[len("<repo-root>/"):]
    if value.startswith("./"):
        value = value[2:]
    if "<" in value or ">" in value:
        return None
    if value.endswith("/") and not repo_root_absolute:
        return None
    if not value or any(char.isspace() for char in value):
        return None
    if "*" in value:
        return None
    if value.startswith(("http://", "https://", "../", "references/", "scripts/")):
        return None
    if not (
        value.startswith(("docs/", "tests/", "skills/", "charness-artifacts/", ".agents/"))
        or value.endswith((".md", ".py", ".yaml", ".yml"))
    ):
        return None
    return value


def _is_author_only_cite(path: str) -> bool:
    if path.startswith("charness-artifacts/"):
        return False
    if path in OPERATOR_DOCS:
        return False
    if path.startswith("docs/") and path.endswith("-adapter.yaml"):
        return False
    if path.startswith("tests/") and path.endswith(".py"):
        return True
    if path.startswith(("skills/public/", "skills/support/", "skills/shared/")):
        return True
    if path.startswith("docs/conventions/") and path.endswith(".md"):
        return True
    if path.startswith("docs/") and path.endswith(".md"):
        return True
    return False


def find_author_repo_cite_errors(markdown_path: Path, contents: str) -> list[str]:
    if markdown_path.as_posix().endswith("skills/public/create-skill/references/portable-authoring.md"):
        return []
    lines = contents.splitlines()
    visible_lines = _unfenced_line_numbers(lines)
    errors: list[str] = []
    for line_no, line in enumerate(lines, start=1):
        if line_no not in visible_lines:
            continue
        if _nearby_authoring_marker(lines, line_no):
            continue
        for match in INLINE_PATH_RE.finditer(line):
            path = _normalize_authoring_path(match.group(1))
            if path and _is_author_only_cite(path):
                errors.append(
                    f"line {line_no}: author-repo-only cite `{match.group(1)}` is not portable; "
                    "use a skill-relative path when it ships with the vendored skill, or mark it "
                    "authoring-repo-internal"
                )
    return errors
