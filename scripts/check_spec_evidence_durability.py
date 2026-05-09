#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_repo_file_listing = import_repo_module(__file__, "scripts.repo_file_listing")
iter_matching_repo_files = _repo_file_listing.iter_matching_repo_files

DOC_GLOBS = (
    "charness-artifacts/spec/**/*.md",
    "charness-artifacts/quality/**/*.md",
    "charness-artifacts/release/**/*.md",
    "charness-artifacts/dogfood/**/*.md",
    "charness-artifacts/debug/**/*.md",
    "charness-artifacts/premortem/**/*.md",
    "charness-artifacts/design-studies/**/*.md",
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
BACKTICK_CONTENT_RE = re.compile(r"`([^`\n]+)`")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
PATHY_TOKEN_RE = re.compile(r"^(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+$")
REPRODUCTION_MARKER_RE = re.compile(r"<!--\s*reproduction-source\s*-->", re.IGNORECASE)
REPO_REFERENCE_PREFIXES = (
    ".agents/",
    ".charness/",
    ".github/",
    "artifacts/",
    "charness-artifacts/",
    "docs/",
    "evals/",
    "integrations/",
    "packaging/",
    "plugins/",
    "presets/",
    "profiles/",
    "scripts/",
    "skills/",
    "tests/",
)


class ValidationError(Exception):
    pass


def normalize_target(candidate: str) -> str:
    target = candidate.strip().split("#", 1)[0]
    while target.startswith("./"):
        target = target[2:]
    return target.rstrip("/")


def looks_like_repo_path(candidate: str) -> bool:
    target = candidate.lstrip("./").split("#", 1)[0].strip()
    if target.startswith(REPO_REFERENCE_PREFIXES):
        return True
    return bool(PATHY_TOKEN_RE.match(target))


def resolve_relative_to_repo(root: Path, doc: Path, candidate: str) -> Path | None:
    raw = candidate.split("#", 1)[0].strip()
    if not raw or "://" in raw or raw.startswith("mailto:"):
        return None
    if raw.startswith("./") or raw.startswith("../"):
        resolved = (doc.parent / raw).resolve()
    elif raw.startswith("/"):
        return None
    else:
        resolved = (root / raw).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def git_check_ignore(root: Path, paths: list[Path]) -> set[Path] | None:
    """Return the subset of `paths` that match a `.gitignore` rule.

    Returns `None` when the root is not inside a git work tree so the caller
    can skip evidence-durability checks gracefully (e.g., tarball install).
    """
    if not paths:
        return set()
    if not (root / ".git").exists():
        return None
    rel_inputs: list[str] = []
    for path in paths:
        try:
            rel_inputs.append(str(path.relative_to(root)))
        except ValueError:
            continue
    if not rel_inputs:
        return set()
    result = subprocess.run(
        ["git", "check-ignore", "--stdin", "-z"],
        cwd=root,
        input="\0".join(rel_inputs).encode("utf-8") + b"\0",
        capture_output=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        rendered = result.stderr.decode("utf-8", errors="replace").strip()
        if "not a git repository" in rendered.lower():
            return None
        raise ValidationError(f"git check-ignore failed: {rendered or 'unknown error'}")
    ignored: set[Path] = set()
    for raw in result.stdout.split(b"\0"):
        token = raw.decode("utf-8", errors="replace").strip()
        if not token:
            continue
        ignored.add((root / token).resolve())
    return ignored


def iter_citation_lines(doc: Path) -> list[tuple[int, str, list[str]]]:
    """Return (lineno, raw_line, candidate_paths) for each non-fence line."""
    out: list[tuple[int, str, list[str]]] = []
    in_fence = False
    in_html_comment = False
    for lineno, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if in_html_comment:
            if "-->" in stripped:
                in_html_comment = False
            continue
        if stripped.startswith("<!--") and "-->" not in stripped:
            in_html_comment = True
            continue
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        candidates: list[str] = []
        for raw_target in LINK_RE.findall(line):
            target = raw_target.strip()
            if target and looks_like_repo_path(target):
                candidates.append(target)
        for backtick_match in BACKTICK_CONTENT_RE.finditer(line):
            inner = backtick_match.group(1).strip()
            if inner and looks_like_repo_path(inner):
                candidates.append(inner)
        if candidates:
            out.append((lineno, line, candidates))
    return out


def violations_for_doc(root: Path, doc: Path) -> list[str]:
    citation_lines = iter_citation_lines(doc)
    if not citation_lines:
        return []
    candidates_by_path: dict[Path, list[tuple[int, str]]] = {}
    for lineno, line, candidates in citation_lines:
        if REPRODUCTION_MARKER_RE.search(line):
            continue
        for candidate in candidates:
            resolved = resolve_relative_to_repo(root, doc, candidate)
            if resolved is None:
                continue
            candidates_by_path.setdefault(resolved, []).append((lineno, candidate))
    if not candidates_by_path:
        return []
    ignored = git_check_ignore(root, list(candidates_by_path.keys()))
    if ignored is None or not ignored:
        return []
    rel_doc = doc.relative_to(root).as_posix() if doc.is_absolute() else str(doc)
    messages: list[str] = []
    for resolved_path, hits in candidates_by_path.items():
        if resolved_path not in ignored:
            continue
        for lineno, candidate in hits:
            messages.append(
                f"{rel_doc}:{lineno}: cited path `{candidate}` resolves to a gitignored target "
                "(`" + resolved_path.relative_to(root).as_posix() + "`); cite a checked-in proof "
                "artifact or mark the line `<!-- reproduction-source -->`. "
                "See skills/public/spec/references/evidence-durability.md."
            )
    return messages


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    if not (root / ".git").exists():
        print(
            "Skipping evidence-durability check: no git work tree at "
            f"{root}.",
        )
        return 0
    docs = iter_matching_repo_files(root, DOC_GLOBS)
    all_messages: list[str] = []
    for doc in docs:
        all_messages.extend(violations_for_doc(root, doc))
    if all_messages:
        for message in all_messages:
            print(message, file=sys.stderr)
        return 1
    print(f"Validated spec evidence durability across {len(docs)} doc(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
