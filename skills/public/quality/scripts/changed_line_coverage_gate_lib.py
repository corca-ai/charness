"""Portable changed-line coverage gate (handoff-3).

Promotes the charness changed-line mutation release-boundary gate to a stack-neutral
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
import sys
from functools import lru_cache
from pathlib import Path
from typing import Callable, NamedTuple

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the script dir is on sys.path, the repo root is not
    _scripts = (p / "scripts" for p in Path(__file__).resolve().parents)
    sys.path.insert(0, str(next(d for d in _scripts if (d / "subprocess_guard.py").is_file())))
    from scripts.core.subprocess_guard import run_process


class GitUnavailable(RuntimeError):
    """A git command this gate needs could not be run, or failed.

    Raised rather than collapsed. Returning ``[]`` here made "git said nothing
    changed" and "git would not answer" the same value, so an unresolvable
    ``base_sha`` produced ``ok: True, "no eligible changed files in this range"``
    and the blocking classifier was never invoked at all. Parent-reproduced.
    """


def _git_lines(repo_root: Path, args: list[str]) -> list[str]:
    # `-c core.quotePath=false` because git otherwise C-quotes non-ASCII paths
    # (`"src/f\303\266.py"`), which never match the glob-derived eligible set.
    try:
        result = run_process(
            ["git", "-c", "core.quotePath=false", *args],
            cwd=repo_root,
            timeout_seconds=None,
        )
    except OSError as exc:  # pragma: no cover - exercised via GitUnavailable below
        raise GitUnavailable(f"could not run `git {' '.join(args)}`: {exc}") from exc
    if result.returncode != 0:
        raise GitUnavailable(
            f"`git {' '.join(args)}` exited {result.returncode}: "
            f"{(result.stderr or '').strip() or 'no stderr'}"
        )
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


def eligible(
    rel_paths: list[str], eligible_globs: list[str], exclude_globs: list[str]
) -> list[str]:
    """Filter repo-relative paths to the configured eligible set minus excludes."""
    return sorted(
        rel
        for rel in rel_paths
        if _matches(rel, eligible_globs) and not _matches(rel, exclude_globs)
    )


def changed_eligible(
    repo_root: Path,
    base_sha: str,
    head_sha: str,
    eligible_globs: list[str],
    exclude_globs: list[str],
) -> list[str]:
    # Two-dot base..head for the change-set (what to judge); the fingerprint pool
    # below uses base->worktree on purpose. The split mirrors the active gate.
    head = head_sha or "HEAD"
    changed = _git_lines(repo_root, ["diff", "--name-only", f"{base_sha}..{head}"])
    return eligible(changed, eligible_globs, exclude_globs)


class HeadScope(NamedTuple):
    """What the analyzed head resolves to, and whether it can support a verdict.

    Three fields, three distinct states, because collapsing them is how this gate
    got into trouble in the first place:

    * `resolved` -- the analyzed head as a COMMIT sha, for anything that renders
      or records which head was judged. Never the raw input: `--head-sha main`
      and `--head-sha refs/heads/main` name a commit but are not one, and a
      verdict line that echoes the raw string names no commit at all.
    * `error` -- the head (or `HEAD`) could not be resolved. Could-not-look, not
      nothing-found.
    * `mismatch` -- the head resolved fine but is not the checked-out `HEAD`.
      Coverage is collected from the LIVE worktree while the change set is diffed
      against the analyzed head, so the mapping and the measurement describe
      different trees.
    """

    resolved: str | None
    error: str | None
    mismatch: str | None


def resolve_head_scope(repo_root: Path, head_sha: str) -> HeadScope:
    """Resolve the analyzed head ONCE, for every consumer that needs it.

    Single-sourced deliberately. Two resolvers of the same input disagreed here:
    this check peeled with `rev-parse --verify <head>^{commit}` while
    `_false_green_warning` used a bare `rev-parse <head>`, so an ANNOTATED TAG on
    the checked-out commit resolved equal here (peeled to the commit) and unequal
    there (the tag object's own sha). The run was cleared to a verdict while the
    one guard against an uncommitted-changes false green silently switched itself
    off -- the same "render a verdict over inputs that cannot support one" class
    this function exists to refuse.

    Parent-reproduced, the case that started it: with `MUTATION_HEAD_SHA` exported
    to the base commit, the same `--base-sha B` run over the same tree went from
    `FAIL: 1 changed file(s) have uncovered changed lines` to `OK: no eligible
    changed files in this range`, exit 0 -- `B..B` is empty, and the human line
    never named the head it had actually analyzed.
    """
    try:
        head = _git_lines(repo_root, ["rev-parse", "--verify", "HEAD^{commit}"])
    except GitUnavailable as exc:
        return HeadScope(None, f"could not resolve `HEAD`: {exc}", None)
    if not head:
        return HeadScope(None, "could not resolve `HEAD`", None)
    if head_sha == "HEAD":
        return HeadScope(head[0], None, None)
    try:
        resolved = _git_lines(repo_root, ["rev-parse", "--verify", f"{head_sha}^{{commit}}"])
    except GitUnavailable as exc:
        return HeadScope(None, f"could not resolve `{head_sha}` to a commit: {exc}", None)
    if not resolved:
        return HeadScope(None, f"could not resolve `{head_sha}` to a commit", None)
    if resolved[0] == head[0]:
        return HeadScope(resolved[0], None, None)
    return HeadScope(
        resolved[0],
        None,
        f"the analyzed head `{resolved[0][:12]}` is not the checked-out HEAD `{head[0][:12]}`, "
        "but coverage is collected from the HEAD worktree, so the mapping and the "
        "measurement describe different trees",
    )


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


def gate_config(config: dict[str, object]) -> tuple[list[str], str, list[str]]:
    """`(eligible_globs, coverage_json, exclude_globs)` from the adapter block.

    Both entry points unpacked these three the same way; keeping one reader means
    the producer that stamps the freshness marker and the consumer that checks it
    cannot end up scoped to different file sets.
    """
    return (
        list(config.get("eligible_globs") or []),
        str(config.get("coverage_json") or ""),
        list(config.get("exclude_globs") or []),
    )


def _scope_mismatch_report(base: dict, changed: list[str], mismatch: str) -> dict[str, object]:
    """The analyzed head is not `HEAD` and the range DID touch eligible files.

    `ok: True`, not `ok: False`, and reported only once the changed set is known.
    Both choices copy `scripts/mutation/check_changed_line_mutation_coverage.py`, which
    reached them the hard way and wrote down why:

    * Placed AFTER the changed set, because refusing before it made an EMPTY scope
      refusable -- a push stoppable with the reason "no eligible files changed",
      which the release-owned producer names as an incoherent blocker
      on the gate whose credibility is the point.
    * `ok: True` with its own exit code, because a could-not-judge is not a
      coverage failure. Collapsing them onto the failing exit puts "I could not
      look" in the bucket reserved for "I looked and it is uncovered" -- the exact
      conflation the unestablished state was introduced to end.

    Callers read `unestablished` to pick the exit code; `ok` stays out of it.
    """
    return {
        **base,
        "ok": True,
        "unestablished": True,
        "changed_pool_files": changed,
        "reason": f"cannot judge this range: {mismatch}",
    }


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

    An analyzed head that is not the checked-out `HEAD` establishes nothing, but
    it is reported the way the repo-local sibling reports it, which is NOT the
    obvious way. See `_scope_mismatch_report`.
    """
    eligible_globs = list(config.get("eligible_globs") or [])
    exclude_globs = list(config.get("exclude_globs") or [])
    coverage_rel = str(config.get("coverage_json") or "")
    base = {"inert": False, "blocking": [], "base_sha": base_sha, "head_sha": head_sha}
    if not eligible_globs:
        return {
            "ok": True,
            **base,
            "inert": True,
            "reason": "eligible_globs empty: gate inert (opted out)",
        }
    if not base_sha:
        return {
            "ok": True,
            **base,
            "reason": "no base_sha: changed-line classifier is non-blocking (matches workflow_dispatch)",
        }
    if not coverage_rel:
        return {
            "ok": True,
            **base,
            "reason": "no coverage_json configured: gate skipped (non-blocking)",
        }
    scope = resolve_head_scope(repo_root, head_sha)
    # `_head_scope` is a private, non-YAML-safe passenger: `run()` pops it back off
    # before the report is ever emitted. It exists so a caller that also needs
    # this SAME scope (the false-green warning) can thread it through instead of
    # calling `resolve_head_scope` a second time over the identical `head_sha`.
    base = {**base, "resolved_head_sha": scope.resolved, "_head_scope": scope}
    if scope.error:
        # Could-not-look, not nothing-found — the same distinction the changed-set
        # arm below draws. `ok: False`, because a head this gate cannot resolve is
        # not a range it may quietly decline to judge.
        return {
            "ok": False,
            **base,
            "unestablished": True,
            "reason": f"could not establish the analyzed head: {scope.error}",
        }
    try:
        changed = changed_eligible(repo_root, base_sha, head_sha, eligible_globs, exclude_globs)
    except GitUnavailable as exc:
        # NOT `ok: True`. The gate could not read the range, so it has no standing
        # to report an empty one -- the shape that let an unresolvable base_sha
        # pass as "nothing changed" while the classifier never ran.
        return {
            "ok": False,
            **base,
            "unestablished": True,
            "reason": f"could not establish the changed set: {exc}",
        }
    if scope.mismatch and changed:
        return _scope_mismatch_report(base, changed, scope.mismatch)
    if not changed:
        empty: dict[str, object] = {
            "ok": True,
            **base,
            "reason": "no eligible changed files in this range",
        }
        if scope.mismatch:
            # Exit stays 0 -- the range honestly changed no eligible file, and
            # refusing an empty scope is the incoherent blocker the sibling names
            # by name. But the DISCLOSURE must not vanish with the refusal: the
            # empty scope is the ANALYZED head's, not this tree's. `reason` is
            # deliberately untouched so consumers can still prefix-match it.
            empty["analyzed_head_not_checked_out_head"] = scope.mismatch
        return empty
    coverage_json = repo_root / coverage_rel
    if not coverage_json.is_file():
        return {
            "ok": True,
            **base,
            "changed_pool_files": changed,
            "reason": f"no coverage source at {coverage_rel}: gate skipped (non-blocking). Produce it in the full/scheduled run and reuse it here.",
        }
    marker = marker_path(coverage_json)
    recorded = marker.read_text(encoding="utf-8").strip() if marker.is_file() else None
    try:
        current = fingerprint(
            repo_root,
            base_sha,
            changed_pool_vs_base(repo_root, base_sha, eligible_globs, exclude_globs),
        )
    except GitUnavailable as exc:
        return {
            "ok": False,
            **base,
            "changed_pool_files": changed,
            "unestablished": True,
            "reason": f"could not establish the coverage-freshness fingerprint: {exc}",
        }
    if recorded is None or recorded != current:
        return {
            "ok": True,
            **base,
            "changed_pool_files": changed,
            "reason": f"coverage source is stale (marker {recorded or 'absent'} != current {current}): gate skipped (non-blocking). Re-produce coverage for this range.",
        }
    statement_lines = load_statement_lines(repo_root, coverage_json)
    blocking = classify(
        repo_root=repo_root,
        base_sha=base_sha,
        head_sha=head_sha,
        changed_before_coverage=changed,
        statement_lines=statement_lines,
        coverage_enabled=True,
    )
    return {
        "ok": not blocking,
        **base,
        "blocking": blocking,
        "changed_pool_files": changed,
        "coverage_json": coverage_rel,
    }


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
    eligible_globs, coverage_rel, exclude_globs = gate_config(config)
    if not eligible_globs or not coverage_rel or not base_sha:
        return None
    # Deliberately NOT caught: `changed_pool_vs_base` can now raise when git will
    # not answer, and a marker stamped from a file set the producer could not read
    # would certify freshness it never established. Failing loudly here is the
    # point -- the consumer trusts this marker.
    files = changed_pool_vs_base(repo_root, base_sha, eligible_globs, exclude_globs)
    fp = fingerprint(repo_root, base_sha, files)
    marker_path(repo_root / coverage_rel).write_text(fp + "\n", encoding="utf-8")
    return fp
