"""Changed-file classification for mutation scope-gap reporting.

Selection predicates (whole-file coverage floor, whole-file mutation-line) stay
in `mutation_sampling_lib`; this module answers the change-set question only.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path


def changed_line_numbers(repo_root: Path, base_sha: str, head_sha: str, path: str) -> set[int]:
    """New-file line numbers changed for `path` over base..head.

    `--no-renames` makes a renamed-and-modified file read as a full addition so a
    rename never silently empties the set; the blocker then fails closed on it.
    """
    if not base_sha:
        return set()
    head = head_sha or "HEAD"
    command = ["git", "diff", "-U0", "--no-renames", f"{base_sha}..{head}", "--", path]
    result = subprocess.run(command, cwd=repo_root, check=True, text=True, capture_output=True)
    lines: set[int] = set()
    for match in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", result.stdout, re.MULTILINE):
        start = int(match.group(1))
        count = int(match.group(2)) if match.group(2) is not None else 1
        lines.update(range(start, start + count))
    return lines


def classify_changed_line_scope_gap(
    *,
    repo_root: Path,
    base_sha: str | None,
    head_sha: str,
    changed_before_coverage: list[str],
    statement_lines: dict[str, tuple[set[int], set[int]]],
    coverage_enabled: bool,
) -> list[str]:
    """Changed pool files whose changed lines are not test-covered (the blocker).

    Judges the change, not the whole file: a file blocks only if its changed
    lines include uncovered statements, or the suite never tracked the file.
    Pre-existing untested lines elsewhere in a touched file do not block.
    """
    if not coverage_enabled or not base_sha:
        return []
    gaps: list[str] = []
    for path in changed_before_coverage:
        changed = changed_line_numbers(repo_root, base_sha, head_sha, path)
        if not changed:
            continue
        if path not in statement_lines:
            gaps.append(path)
            continue
        _executed, missing = statement_lines[path]
        if changed & missing:
            gaps.append(path)
    return sorted(gaps)


def changed_line_scope_gap_targets(
    *,
    repo_root: Path,
    base_sha: str | None,
    head_sha: str,
    changed_before_coverage: list[str],
    statement_lines: dict[str, tuple[set[int], set[int]]],
    coverage_enabled: bool,
) -> dict[str, list[dict[str, object]]]:
    """Exact changed-line targets that make the scope-gap blocker fire.

    Tracked files report changed lines that are also missing coverage. Untracked
    files report all changed lines because the test suite observed none of the
    file. The source text is included so manual targeted-mutant proof can bind
    to a numbered gate target before editing similar nearby code.
    """
    if not coverage_enabled or not base_sha:
        return {}
    targets: dict[str, list[dict[str, object]]] = {}
    for path in changed_before_coverage:
        changed = changed_line_numbers(repo_root, base_sha, head_sha, path)
        if not changed:
            continue
        if path not in statement_lines:
            target_lines = changed
        else:
            _executed, missing = statement_lines[path]
            target_lines = changed & missing
        if target_lines:
            entries = line_source_targets(repo_root, path, target_lines, ref=head_sha)
            if entries:
                targets[path] = entries
    return dict(sorted(targets.items()))


def classify_changed_sample_scope(
    *,
    repo_root: Path,
    base_sha: str | None,
    head_sha: str,
    changed_before_coverage: list[str],
    eligible: list[str],
    coverage_eligible: list[str],
    statement_lines: dict[str, tuple[set[int], set[int]]],
    coverage_enabled: bool,
) -> tuple[list[str], list[str], list[str], list[str], list[str], dict[str, list[dict[str, object]]]]:
    changed = [path for path in changed_before_coverage if path in set(eligible)]
    (
        changed_files_excluded_by_file_coverage,
        changed_files_excluded_by_mutation_line_coverage,
        uncovered_changed_files,
    ) = classify_changed_file_exclusions(
        changed_before_coverage=changed_before_coverage,
        coverage_eligible=coverage_eligible,
        eligible=eligible,
        coverage_enabled=coverage_enabled,
    )
    changed_line_uncovered_changed_files = classify_changed_line_scope_gap(
        repo_root=repo_root,
        base_sha=base_sha,
        head_sha=head_sha,
        changed_before_coverage=changed_before_coverage,
        statement_lines=statement_lines,
        coverage_enabled=coverage_enabled,
    )
    changed_line_uncovered_changed_line_targets = changed_line_scope_gap_targets(
        repo_root=repo_root,
        base_sha=base_sha,
        head_sha=head_sha,
        changed_before_coverage=changed_before_coverage,
        statement_lines=statement_lines,
        coverage_enabled=coverage_enabled,
    )
    return (
        changed,
        changed_files_excluded_by_file_coverage,
        changed_files_excluded_by_mutation_line_coverage,
        uncovered_changed_files,
        changed_line_uncovered_changed_files,
        changed_line_uncovered_changed_line_targets,
    )


def line_source_targets(
    repo_root: Path,
    path: str,
    line_numbers: set[int],
    ref: str | None = None,
) -> list[dict[str, object]]:
    """Return deterministic ``line`` + ``source`` entries for repo-relative path."""
    source_lines = line_source_text(repo_root, path, ref)
    entries: list[dict[str, object]] = []
    for line_number in sorted(line_numbers):
        source = source_lines[line_number - 1].strip() if 1 <= line_number <= len(source_lines) else ""
        if not source:
            continue
        entries.append({"line": line_number, "source": source})
    return entries


def line_source_text(repo_root: Path, path: str, ref: str | None = None) -> list[str]:
    if ref:
        try:
            result = subprocess.run(
                ["git", "show", f"{ref}:{path}"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError):
            return []
        return result.stdout.splitlines()
    source_path = repo_root / path
    try:
        return source_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


def changed_pool_files_vs_base(repo_root: Path, base_sha: str) -> list[str]:
    """Eligible mutation-pool files that differ from ``base_sha`` in the worktree.

    Diffs ``base_sha`` against the WORKING TREE (no ``..head``) on purpose: the
    closeout producer runs pre-commit (HEAD is still the parent), while the
    pre-push consumer runs post-commit. Comparing base→worktree at both points
    yields the same changed-file set and the same on-disk content across the
    commit boundary, which is what lets the freshness fingerprint match.

    Note: ``git diff`` lists tracked changes only, so a brand-new pool file that
    is still untracked at the producer's pre-commit run is omitted there but
    included once committed — a fingerprint mismatch that makes the consumer skip
    non-blocking (safe). Running the producer on the committed tip (the intended
    pre-push flow) avoids it.
    """
    if not base_sha:
        return []
    from scripts.sample_mutation_files import list_eligible, mutation_pathspecs  # noqa: E402

    command = ["git", "diff", "--name-only", base_sha, "--", *mutation_pathspecs()]
    result = subprocess.run(command, cwd=repo_root, check=True, text=True, capture_output=True)
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    return sorted(changed & set(list_eligible(repo_root)))


def _safe_read_bytes(path: Path) -> bytes:
    """File bytes, or an ``<absent>`` sentinel when the path cannot be read (a
    deleted/replaced pool file or a TOCTOU race between the diff and the read) so
    the fingerprint stays a stable digest instead of crashing the gate."""
    try:
        return path.read_bytes()
    except OSError:
        return b"<absent>"


def changed_pool_fingerprint(repo_root: Path, base_sha: str) -> str:
    """Content fingerprint of the changed eligible pool files over base→worktree.

    Stable across the pre-commit→commit boundary (the producer stamps it, the
    consumer recomputes and compares), and content-based rather than commit-SHA
    based so a no-op recommit/rebase that does not touch the pool does not
    needlessly invalidate fresh coverage. An ``origin/main`` advance changes
    ``base_sha`` and so re-invalidates, which is correct: coverage produced
    against an older base should be re-produced.
    """
    digest = hashlib.sha256()
    digest.update(b"charness-changed-pool-fingerprint-v1\n")
    digest.update((base_sha or "").encode() + b"\n")
    for path in changed_pool_files_vs_base(repo_root, base_sha):
        digest.update(f"{path}:".encode())
        digest.update(hashlib.sha256(_safe_read_bytes(repo_root / path)).hexdigest().encode())
        digest.update(b"\n")
    return digest.hexdigest()


def coverage_fingerprint_marker_path(coverage_json: Path) -> Path:
    """Sibling marker the producer stamps and the consumer trusts for freshness."""
    return coverage_json.with_name(coverage_json.name + ".fingerprint")


def write_coverage_fingerprint_marker(repo_root: Path, coverage_json: Path, base_sha: str) -> str:
    fingerprint = changed_pool_fingerprint(repo_root, base_sha)
    coverage_fingerprint_marker_path(coverage_json).write_text(fingerprint + "\n", encoding="utf-8")
    return fingerprint


def classify_changed_file_exclusions(
    *,
    changed_before_coverage: list[str],
    coverage_eligible: list[str],
    eligible: list[str],
    coverage_enabled: bool,
) -> tuple[list[str], list[str], list[str]]:
    """Advisory whole-file selection exclusions, split by which filter dropped them."""
    if not coverage_enabled:
        return [], [], []
    coverage_eligible_set = set(coverage_eligible)
    eligible_set = set(eligible)
    file_coverage_excluded = [
        path for path in changed_before_coverage if path not in coverage_eligible_set
    ]
    mutation_line_excluded = [
        path
        for path in changed_before_coverage
        if path in coverage_eligible_set and path not in eligible_set
    ]
    return (
        file_coverage_excluded,
        mutation_line_excluded,
        file_coverage_excluded + mutation_line_excluded,
    )
