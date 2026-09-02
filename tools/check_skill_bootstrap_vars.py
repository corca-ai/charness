#!/usr/bin/env python3
"""Lint SKILL.md bootstrap blocks for unresolved shell variables.

Every SKILL.md whose `## Bootstrap` section uses `$VAR` references inside
fenced code blocks must either:

- cite `skills/shared/references/bootstrap-resolution.md` for the well-known
  charness vars (`SKILL_DIR`, `CHARNESS_SUPPORT_DIR`, `CHARNESS_REPO_ROOT`)
  that the shared reference is the source of truth for, or
- include an inline assignment (`VAR=...` or `export VAR=...`) within the
  bootstrap section that resolves the variable before it is used.

Skills that have no `## Bootstrap` section, or whose bootstrap section is
prose-only with no shell code blocks referencing `$VAR`, are silently OK.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

_repo_file_listing_module = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _repo_file_listing_module.iter_matching_repo_files

REPO_ROOT = repo_root_from_script(__file__)

CANONICAL_CITE = "shared/references/bootstrap-resolution.md"
KNOWN_RESOLVED_VARS = {"SKILL_DIR", "CHARNESS_SUPPORT_DIR", "CHARNESS_REPO_ROOT"}

BOOTSTRAP_HEADER_RE = re.compile(r"^##\s+Bootstrap\s*$", re.MULTILINE)
NEXT_H2_RE = re.compile(r"^##\s+", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"^```([^\n]*)\n(.*?)^```", re.DOTALL | re.MULTILINE)
SHELL_VAR_RE = re.compile(r"\$\{?([A-Z][A-Z0-9_]+)\}?")
ASSIGN_RE = re.compile(r"^\s*(?:export\s+)?([A-Z][A-Z0-9_]+)=", re.MULTILINE)
NON_EXPORTED_SKILL_DIR_RE = re.compile(r"^\s*SKILL_DIR\s*=", re.MULTILINE)
EXPORTED_SKILL_DIR_RE = re.compile(r"^\s*export\s+SKILL_DIR\s*=", re.MULTILINE)
SHELL_FENCE_RE = re.compile(r"(?:bash|sh|shell|zsh)", re.IGNORECASE)


def _extract_bootstrap_section(text: str) -> str | None:
    header_match = BOOTSTRAP_HEADER_RE.search(text)
    if not header_match:
        return None
    start = header_match.end()
    next_match = NEXT_H2_RE.search(text, start)
    end = next_match.start() if next_match else len(text)
    return text[start:end]


def _shell_vars_in_code_blocks(section: str) -> set[str]:
    found: set[str] = set()
    for fence_match in CODE_FENCE_RE.finditer(section):
        body = fence_match.group(2)
        for var_match in SHELL_VAR_RE.finditer(body):
            found.add(var_match.group(1))
    return found


def _has_canonical_cite(section: str) -> bool:
    return CANONICAL_CITE in section


def _inline_assignments(section: str) -> set[str]:
    return {match.group(1) for match in ASSIGN_RE.finditer(section)}


def _check_non_exported_skill_dir_assignments(text: str, source: Path) -> list[str]:
    """Reject non-exported SKILL_DIR assignments in shell examples."""
    failures: list[str] = []
    for fence_match in CODE_FENCE_RE.finditer(text):
        language = fence_match.group(1).strip()
        if not SHELL_FENCE_RE.search(language):
            continue
        for line_number, line in enumerate(fence_match.group(2).splitlines(), start=1):
            if NON_EXPORTED_SKILL_DIR_RE.match(line) and not EXPORTED_SKILL_DIR_RE.match(line):
                failures.append(
                    f"{source}: shell example line {line_number} assigns SKILL_DIR "
                    "without export; "
                    "export it in a separate command before expanding $SKILL_DIR"
                )
    return failures


def check_canonical_reference(reference: Path) -> list[str]:
    text = reference.read_text(encoding="utf-8")
    return _check_non_exported_skill_dir_assignments(text, reference)


def check_file(skill_md: Path) -> list[str]:
    text = skill_md.read_text(encoding="utf-8")
    section = _extract_bootstrap_section(text)
    if section is None:
        return []
    vars_used = _shell_vars_in_code_blocks(section)
    if not vars_used:
        return []
    cite_present = _has_canonical_cite(section)
    assigned = _inline_assignments(section)
    failures: list[str] = []
    failures.extend(_check_non_exported_skill_dir_assignments(section, skill_md))
    for var in sorted(vars_used):
        if var in KNOWN_RESOLVED_VARS:
            if not cite_present:
                failures.append(
                    f"uses `${var}` in `## Bootstrap` shell block but does not cite "
                    f"`{CANONICAL_CITE}`"
                )
        elif var not in assigned:
            failures.append(
                f"uses `${var}` in `## Bootstrap` shell block without an inline "
                f"assignment (`{var}=...` or `export {var}=...`) and the variable is "
                f"not a canonical charness var; declare its source explicitly"
            )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--require-git-file-listing", action="store_true")
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()

    reference = root / "skills" / CANONICAL_CITE
    reference_failures = check_canonical_reference(reference) if reference.is_file() else []

    patterns = (
        "skills/public/*/SKILL.md",
        "skills/support/*/SKILL.md",
    )
    targets = iter_matching_repo_files(
        root,
        patterns,
        include_untracked=True,
        require_git=args.require_git_file_listing,
    )

    failures: dict[Path, list[str]] = {}
    for path in targets:
        per_file = check_file(path)
        if per_file:
            failures[path] = per_file

    if reference_failures:
        for msg in reference_failures:
            print(msg, file=sys.stderr)
    if failures or reference_failures:
        for path, msgs in sorted(failures.items()):
            for msg in msgs:
                rel = path.relative_to(root) if path.is_relative_to(root) else path
                print(f"{rel}: {msg}", file=sys.stderr)
        return 1

    if not targets:
        # Zero SKILL.md files under a root this gate was pointed at is an
        # unestablished scope, not a clean one: it reads identically to a full
        # pass while proving nothing. Same rule as the packaging and export-safe
        # scans (charness-artifacts/critique/2026-07-27-empty-scope-family.md).
        print(
            f"no public/support SKILL.md files found under {root}; nothing was "
            "validated. Check --repo-root: this gate is scoped to a charness-shaped "
            f"root carrying {' or '.join(patterns)}.",
            file=sys.stderr,
        )
        return 1

    print(f"Validated SKILL.md bootstrap vars for {len(targets)} skill file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
