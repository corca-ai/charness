from __future__ import annotations

import re
from pathlib import Path

INLINE_COMMAND_RE = re.compile(r"`([^`\n]+)`")
BARE_RUNTIME_SCRIPT_INVOCATION_RE = re.compile(
    r"\b(?:python3|python|bash|sh|zsh)\s+scripts/(?P<rel>[A-Za-z0-9._/-]+\.[A-Za-z0-9]+)\b"
)
SOURCE_TREE_SKILL_INVOCATION_RE = re.compile(
    r"\b(?:python3|python|bash|sh|zsh|sed|cat|head|tail|rg|find)\b[^`\n]*"
    r"(?P<rel>skills/(?:public|support)/[A-Za-z0-9._-]+/[^\s`]+)"
)


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
