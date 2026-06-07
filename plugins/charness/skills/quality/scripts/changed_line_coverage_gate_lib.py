"""Portable changed-line coverage gate (handoff-3).

Promotes the charness changed-line mutation pre-merge gate to a stack-neutral
`quality` capability. The blocking signal is the same as the scheduled mutation
gate's: a changed pool file whose changed lines over `base..head` lack test
coverage. This portable version sources the eligible-file set from adapter globs
(not a tool-specific config like `cosmic-ray.toml`), reuses a coverage report a
full / scheduled run already produced (coverage.py JSON), and gates trust on a
content-fingerprint freshness marker so a stale report cannot raise false
positives.

It reuses the tool-neutral classifier (`mutation_changed_files_lib`) and the
coverage.py statement reader (`mutation_sampling_lib`); only the eligible-file
source and the fingerprint pool become glob-driven so consuming repos inherit
the gate without the charness mutation-runner wiring.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Callable


def _git_lines(repo_root: Path, args: list[str]) -> list[str]:
    try:
        result = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True)
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


@lru_cache(maxsize=512)
def _glob_regex(pattern: str) -> re.Pattern[str]:
    """Translate a `**`-aware glob to a regex (`fnmatch` treats `**` as plain `*`).

    `**/` matches zero or more directory segments, `**` matches anything, `*`
    matches within a segment, `?` matches one non-separator char.
    """
    out: list[str] = []
    i, n = 0, len(pattern)
    while i < n:
        char = pattern[i]
        if char == "*":
            if pattern[i : i + 2] == "**":
                i += 2
                if pattern[i : i + 1] == "/":
                    out.append("(?:.*/)?")
                    i += 1
                else:
                    out.append(".*")
                continue
            out.append("[^/]*")
        elif char == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(char))
        i += 1
    return re.compile("(?s:" + "".join(out) + r")\Z")


def _matches(rel: str, globs: list[str]) -> bool:
    return any(_glob_regex(pattern).match(rel) for pattern in globs)


def eligible(rel_paths: list[str], eligible_globs: list[str], exclude_globs: list[str]) -> list[str]:
    """Filter repo-relative paths to the configured eligible set minus excludes."""
    return sorted(
        rel
        for rel in rel_paths
        if _matches(rel, eligible_globs) and not _matches(rel, exclude_globs)
    )


def changed_eligible(
    repo_root: Path, base_sha: str, head_sha: str, eligible_globs: list[str], exclude_globs: list[str]
) -> list[str]:
    # Two-dot base..head for the change-set (what to judge); the fingerprint pool
    # below uses base->worktree on purpose. The split mirrors the active gate.
    head = head_sha or "HEAD"
    changed = _git_lines(repo_root, ["diff", "--name-only", f"{base_sha}..{head}"])
    return eligible(changed, eligible_globs, exclude_globs)


def changed_pool_vs_base(
    repo_root: Path, base_sha: str, eligible_globs: list[str], exclude_globs: list[str]
) -> list[str]:
    """Eligible files differing from base in the WORKING TREE (for the fingerprint).

    Mirrors the charness gate's base→worktree comparison so the fingerprint the
    producer stamps pre-commit matches what the consumer recomputes post-commit.
    """
    changed = _git_lines(repo_root, ["diff", "--name-only", base_sha])
    return eligible(changed, eligible_globs, exclude_globs)


def fingerprint(repo_root: Path, base_sha: str, files: list[str]) -> str:
    digest = hashlib.sha256()
    digest.update(b"changed-line-coverage-gate-fingerprint-v1\n")
    digest.update((base_sha or "").encode() + b"\n")
    for rel in sorted(files):
        path = repo_root / rel
        try:
            content = path.read_bytes()
        except OSError:
            content = b"<absent>"
        digest.update(f"{rel}:".encode())
        digest.update(hashlib.sha256(content).hexdigest().encode())
        digest.update(b"\n")
    return digest.hexdigest()


def run_gate(
    repo_root: Path,
    config: dict[str, object],
    *,
    base_sha: str | None,
    head_sha: str,
    classify: Callable[..., list[str]],
    load_statement_lines: Callable[[Path, Path], dict[str, tuple[set[int], set[int]]]],
    marker_path: Callable[[Path], Path],
) -> dict[str, object]:
    """Run the changed-line coverage gate from the adapter config.

    Returns `{ok, inert, blocking, ...}`. Inert (exit 0) when `eligible_globs` is
    empty (opt-out). Non-blocking skip when there is no base SHA, no eligible
    changed file, no coverage report, or a stale freshness marker — matching the
    charness gate so a missing/old coverage source never false-fails.
    """
    eligible_globs = list(config.get("eligible_globs") or [])
    exclude_globs = list(config.get("exclude_globs") or [])
    coverage_rel = str(config.get("coverage_json") or "")
    base = {"inert": False, "blocking": [], "base_sha": base_sha, "head_sha": head_sha}
    if not eligible_globs:
        return {"ok": True, **base, "inert": True, "reason": "eligible_globs empty: gate inert (opted out)"}
    if not base_sha:
        return {"ok": True, **base, "reason": "no base_sha: changed-line classifier is non-blocking (matches workflow_dispatch)"}
    if not coverage_rel:
        return {"ok": True, **base, "reason": "no coverage_json configured: gate skipped (non-blocking)"}
    changed = changed_eligible(repo_root, base_sha, head_sha, eligible_globs, exclude_globs)
    if not changed:
        return {"ok": True, **base, "reason": "no eligible changed files in this range"}
    coverage_json = repo_root / coverage_rel
    if not coverage_json.is_file():
        return {"ok": True, **base, "changed_pool_files": changed,
                "reason": f"no coverage source at {coverage_rel}: gate skipped (non-blocking). Produce it in the full/scheduled run and reuse it here."}
    marker = marker_path(coverage_json)
    recorded = marker.read_text(encoding="utf-8").strip() if marker.is_file() else None
    current = fingerprint(repo_root, base_sha, changed_pool_vs_base(repo_root, base_sha, eligible_globs, exclude_globs))
    if recorded is None or recorded != current:
        return {"ok": True, **base, "changed_pool_files": changed,
                "reason": f"coverage source is stale (marker {recorded or 'absent'} != current {current}): gate skipped (non-blocking). Re-produce coverage for this range."}
    statement_lines = load_statement_lines(repo_root, coverage_json)
    blocking = classify(
        repo_root=repo_root, base_sha=base_sha, head_sha=head_sha,
        changed_before_coverage=changed, statement_lines=statement_lines, coverage_enabled=True,
    )
    return {"ok": not blocking, **base, "blocking": blocking, "changed_pool_files": changed,
            "coverage_json": coverage_rel}


def stamp_marker(
    repo_root: Path,
    config: dict[str, object],
    base_sha: str,
    *,
    marker_path: Callable[[Path], Path],
) -> str | None:
    """Producer side: stamp the freshness marker after coverage exists for this
    range, so the consumer's freshness check can trust the reused report. Returns
    the fingerprint, or None when inert/unconfigured."""
    eligible_globs = list(config.get("eligible_globs") or [])
    coverage_rel = str(config.get("coverage_json") or "")
    if not eligible_globs or not coverage_rel or not base_sha:
        return None
    exclude_globs = list(config.get("exclude_globs") or [])
    files = changed_pool_vs_base(repo_root, base_sha, eligible_globs, exclude_globs)
    fp = fingerprint(repo_root, base_sha, files)
    marker_path(repo_root / coverage_rel).write_text(fp + "\n", encoding="utf-8")
    return fp
