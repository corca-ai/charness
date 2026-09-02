"""Changed-file classification for mutation scope-gap reporting.

Selection predicates (whole-file coverage floor, whole-file mutation-line) stay
in `mutation_sampling_lib`; this module answers the change-set question only.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path

from scripts.worktree.checkout_view import CheckoutView, GitCheckout  # noqa: E402
from scripts.core.git_status_snapshot import GitStatusError  # noqa: E402
from scripts.mutation.mutation_changed_line_diff import (  # noqa: E402
    changed_line_numbers_for_paths as _batch_changed_line_numbers_for_paths,
)
from scripts.core.subprocess_guard import run_process

_IMMUTABLE_REF = re.compile(r"[0-9a-f]{40}")
_CHANGED_LINE_CACHE: dict[tuple[str, str, str, str], frozenset[int]] = {}


def resolved_mutation_pool(repo_root: Path, *, gate_label: str = "mutation-sampling"):
    from scripts.quality_adapter_lib import load_quality_adapter
    from scripts.quality_universes_lib import (
        DEFAULT_UNIVERSES,
        matching_files,
        refuse_if_declared_and_empty,
        resolve_universe,
    )

    adapter = load_quality_adapter(repo_root)
    if adapter.get("valid") is False:
        errors = "; ".join(str(error) for error in adapter.get("errors", []))
        raise SystemExit(
            f"{gate_label}: quality adapter is invalid{f': {errors}' if errors else '.'}"
        )
    universe = resolve_universe(
        adapter, "mutation_pool", default=DEFAULT_UNIVERSES["mutation_pool"]
    )
    files = [path for path in matching_files(repo_root, universe) if path.name != "__init__.py"]
    refusal = refuse_if_declared_and_empty(universe, files, gate_label)
    if refusal is not None:
        raise SystemExit(refusal)
    return universe, files


def _is_immutable_ref(value: str) -> bool:
    """Whether a ref names an immutable Git object rather than a moving ref."""
    return bool(_IMMUTABLE_REF.fullmatch(value))


def changed_line_numbers_for_paths(
    repo_root: Path,
    base_sha: str,
    head_sha: str,
    paths: list[str],
) -> dict[str, set[int]]:
    """Return changed new-file lines for several paths in one Git invocation."""
    return _batch_changed_line_numbers_for_paths(
        repo_root, base_sha, head_sha, paths, changed_line_numbers
    )


def changed_line_numbers(repo_root: Path, base_sha: str, head_sha: str, path: str) -> set[int]:
    """New-file line numbers changed for `path` over base..head.

    `--no-renames` makes a renamed-and-modified file read as a full addition so a
    rename never silently empties the set; the blocker then fails closed on it.
    """
    if not base_sha:
        return set()
    head = head_sha or "HEAD"
    cache_key = (str(repo_root.resolve()), base_sha, head, path)
    if _is_immutable_ref(base_sha) and _is_immutable_ref(head):
        cached = _CHANGED_LINE_CACHE.get(cache_key)
        if cached is not None:
            return set(cached)
    command = ["git", "diff", "-U0", "--no-renames", f"{base_sha}..{head}", "--", path]
    result = run_process(command, cwd=repo_root, timeout_seconds=None)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f"git diff failed with exit {result.returncode}"
        )
    lines: set[int] = set()
    for match in re.finditer(
        r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", result.stdout, re.MULTILINE
    ):
        start = int(match.group(1))
        count = int(match.group(2)) if match.group(2) is not None else 1
        lines.update(range(start, start + count))
    if _is_immutable_ref(base_sha) and _is_immutable_ref(head):
        _CHANGED_LINE_CACHE[cache_key] = frozenset(lines)
    return lines


def _classify_changed_line_scope_gap_from_map(
    *,
    changed_before_coverage: list[str],
    statement_lines: dict[str, tuple[set[int], set[int]]],
    coverage_enabled: bool,
    changed_lines: Mapping[str, set[int]],
) -> list[str]:
    if not coverage_enabled:
        return []
    gaps: list[str] = []
    for path in changed_before_coverage:
        changed = changed_lines.get(path, set())
        if not changed:
            continue
        if path not in statement_lines:
            gaps.append(path)
            continue
        _executed, missing = statement_lines[path]
        if changed & missing:
            gaps.append(path)
    return sorted(gaps)


def _changed_line_scope_gap_targets_from_map(
    *,
    repo_root: Path,
    head_sha: str,
    changed_before_coverage: list[str],
    statement_lines: dict[str, tuple[set[int], set[int]]],
    coverage_enabled: bool,
    changed_lines: Mapping[str, set[int]],
) -> dict[str, list[dict[str, object]]]:
    if not coverage_enabled:
        return {}
    targets: dict[str, list[dict[str, object]]] = {}
    for path in changed_before_coverage:
        changed = changed_lines.get(path, set())
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


def classify_changed_line_scope_gap(
    *,
    repo_root: Path,
    base_sha: str | None,
    head_sha: str,
    changed_before_coverage: list[str],
    statement_lines: dict[str, tuple[set[int], set[int]]],
    coverage_enabled: bool,
    _changed_lines: Mapping[str, set[int]] | None = None,
) -> list[str]:
    """Changed pool files whose changed lines are not test-covered (the blocker).

    Judges the change, not the whole file: a file blocks only if its changed
    lines include uncovered statements, or the suite never tracked the file.
    Pre-existing untested lines elsewhere in a touched file do not block.
    """
    if not coverage_enabled or not base_sha:
        return []
    if _changed_lines is not None:
        return _classify_changed_line_scope_gap_from_map(
            changed_before_coverage=changed_before_coverage,
            statement_lines=statement_lines,
            coverage_enabled=coverage_enabled,
            changed_lines=_changed_lines,
        )
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
    _changed_lines: Mapping[str, set[int]] | None = None,
) -> dict[str, list[dict[str, object]]]:
    """Exact changed-line targets that make the scope-gap blocker fire.

    Tracked files report changed lines that are also missing coverage. Untracked
    files report all changed lines because the test suite observed none of the
    file. The source text is included so manual targeted-mutant proof can bind
    to a numbered gate target before editing similar nearby code.
    """
    if not coverage_enabled or not base_sha:
        return {}
    if _changed_lines is not None:
        return _changed_line_scope_gap_targets_from_map(
            repo_root=repo_root,
            head_sha=head_sha,
            changed_before_coverage=changed_before_coverage,
            statement_lines=statement_lines,
            coverage_enabled=coverage_enabled,
            changed_lines=_changed_lines,
        )
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
) -> tuple[
    list[str], list[str], list[str], list[str], list[str], dict[str, list[dict[str, object]]]
]:
    changed_lines = (
        changed_line_numbers_for_paths(repo_root, base_sha or "", head_sha, changed_before_coverage)
        if coverage_enabled and base_sha
        else {}
    )
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
        _changed_lines=changed_lines,
    )
    changed_line_uncovered_changed_line_targets = changed_line_scope_gap_targets(
        repo_root=repo_root,
        base_sha=base_sha,
        head_sha=head_sha,
        changed_before_coverage=changed_before_coverage,
        statement_lines=statement_lines,
        coverage_enabled=coverage_enabled,
        _changed_lines=changed_lines,
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
        source = (
            source_lines[line_number - 1].strip() if 1 <= line_number <= len(source_lines) else ""
        )
        if not source:
            continue
        entries.append({"line": line_number, "source": source})
    return entries


def line_source_text(repo_root: Path, path: str, ref: str | None = None) -> list[str]:
    if ref:
        try:
            result = run_process(
                ["git", "show", f"{ref}:{path}"], cwd=repo_root, timeout_seconds=None
            )
        except OSError:
            return []
        if result.returncode != 0:
            return []
        return result.stdout.splitlines()
    source_path = repo_root / path
    try:
        return source_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


def changed_pool_files_vs_base(
    repo_root: Path,
    base_sha: str,
    *,
    checkout: CheckoutView | None = None,
    untracked: frozenset[str] | None = None,
) -> list[str]:
    """Eligible mutation-pool files that differ from ``base_sha`` in the worktree.

    Diffs ``base_sha`` against the WORKING TREE (no ``..head``) on purpose: the
    closeout producer runs pre-commit (HEAD is still the parent), while the
    pre-push consumer runs post-commit. Comparing base→worktree at both points
    yields the same changed-file set and the same on-disk content across the
    commit boundary, which is what lets the freshness fingerprint match.

    ``git diff`` lists tracked changes only. Untracked membership is a checkout
    view (status), not a second listing command: untracked is not in any commit,
    so vs-base and vs-HEAD are the same population.
    """
    if not base_sha:
        return []
    from scripts.mutation.sample_mutation_files import mutation_pathspecs  # noqa: E402

    universe, pool_files = resolved_mutation_pool(
        repo_root,
        gate_label="release-changed-line-coverage",
    )
    eligible = [path.relative_to(repo_root).as_posix() for path in pool_files]
    if not pool_files and not universe.declared:
        patterns = ", ".join(universe.patterns) or "<empty>"
        print(
            "release-changed-line-coverage: discovered empty mutation_pool universe "
            f"(patterns: {patterns}); no mutation-pool files can be analyzed.",
            file=sys.stderr,
        )
    command = ["git", "diff", "--name-only", base_sha, "--", *mutation_pathspecs(repo_root)]
    result = run_process(command, cwd=repo_root, timeout_seconds=None)
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f"git diff failed with exit {result.returncode}"
        )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    if untracked is None:
        try:
            untracked = (checkout or GitCheckout(repo_root)).status().untracked_paths()
        except (GitStatusError, OSError):
            untracked = frozenset()
    changed.update(path for path in untracked if path in eligible)
    return sorted(changed & set(eligible))


def _safe_read_bytes(path: Path) -> bytes:
    """File bytes, or an ``<absent>`` sentinel when the path cannot be read (a
    deleted/replaced pool file or a TOCTOU race between the diff and the read) so
    the fingerprint stays a stable digest instead of crashing the gate."""
    try:
        return path.read_bytes()
    except OSError:
        return b"<absent>"


def changed_pool_fingerprint(
    repo_root: Path,
    base_sha: str,
    *,
    checkout: CheckoutView | None = None,
) -> str:
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
    for path in changed_pool_files_vs_base(repo_root, base_sha, checkout=checkout):
        digest.update(f"{path}:".encode())
        digest.update(hashlib.sha256(_safe_read_bytes(repo_root / path)).hexdigest().encode())
        digest.update(b"\n")
    return digest.hexdigest()


def coverage_fingerprint_marker_path(coverage_json: Path) -> Path:
    """Generic portable-gate marker path.

    Charness's changed-line producer uses the namespaced path below so a
    sampler or another producer cannot silently reuse this gate's marker.
    """
    return coverage_json.with_name(coverage_json.name + ".fingerprint")


CHANGED_LINE_COVERAGE_PRODUCER = "changed-line-coverage"
CHANGED_LINE_COVERAGE_MARKER_SCHEMA = "charness.changed-line-coverage-fingerprint.v1"


def changed_line_coverage_marker_path(coverage_json: Path) -> Path:
    """Marker path owned only by the Charness changed-line producer."""
    return coverage_json.with_name(coverage_json.name + ".changed-line.fingerprint")


def read_changed_line_coverage_marker(marker_path: Path) -> str | None:
    """Read a producer-qualified changed-line marker, or ``None`` if unusable."""
    try:
        payload = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("schema") != CHANGED_LINE_COVERAGE_MARKER_SCHEMA:
        return None
    if payload.get("producer") != CHANGED_LINE_COVERAGE_PRODUCER:
        return None
    fingerprint = payload.get("fingerprint")
    if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        return None
    return fingerprint


def write_coverage_fingerprint_marker(repo_root: Path, coverage_json: Path, base_sha: str) -> str:
    """Stamp the changed-line producer's content marker.

    The historical function name is retained for callers and test seams. The
    output is now a namespaced, producer-qualified record rather than a bare
    hash, so a sampler report cannot satisfy this gate by inheriting a marker.
    """
    fingerprint = changed_pool_fingerprint(repo_root, base_sha)
    marker = changed_line_coverage_marker_path(coverage_json)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "producer": CHANGED_LINE_COVERAGE_PRODUCER,
                "schema": CHANGED_LINE_COVERAGE_MARKER_SCHEMA,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return fingerprint


def invalidate_changed_line_coverage_marker(coverage_json: Path) -> None:
    """Remove a changed-line marker before another producer rewrites the report."""
    marker = changed_line_coverage_marker_path(coverage_json)
    try:
        marker.unlink()
    except FileNotFoundError:
        pass


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
