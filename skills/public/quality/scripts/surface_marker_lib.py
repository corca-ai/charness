from __future__ import annotations

import re
from pathlib import Path

NESTED_CLI_RE = re.compile(
    r"\b(subprocess\.(?:run|check_call|check_output|Popen)|spawnSync|execFileSync|execSync|spawn\(|execa\()"
)
MODULE_RELEASE_ONLY_RE = re.compile(
    r"^pytestmark\s*=\s*(?:pytest\.mark\.release_only|\[[^\n]*pytest\.mark\.release_only[^\n]*\])",
    re.MULTILINE,
)


def nested_cli_files(repo_root: Path, test_files: list[Path]) -> list[str]:
    matches: list[str] = []
    for path in test_files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if NESTED_CLI_RE.search(text):
            matches.append(path.relative_to(repo_root).as_posix())
    return matches


def module_release_only_files(repo_root: Path, rel_paths: list[str]) -> list[str]:
    matches: list[str] = []
    for rel_path in rel_paths:
        try:
            text = (repo_root / rel_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if MODULE_RELEASE_ONLY_RE.search(text):
            matches.append(rel_path)
    return matches
