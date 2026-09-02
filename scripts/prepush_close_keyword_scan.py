#!/usr/bin/env python3
"""What a push RANGE contains, and what GitHub would CLOSE in it.

The reading half of the pre-push close-keyword floor, split from
``prepush_close_keyword_guard.py`` when that file passed its length cap. The seam is
not mechanical: everything here answers a question with a factual answer -- which
commits does this ref update land, what does this commit's stored message say, which
issues would GitHub close on it -- and nothing here renders a VERDICT about any of
them. The guard next door owns the verdict, the refusal, and the remediation.

That boundary is worth keeping. Every function here can be checked against git's and
GitHub's documented behavior alone; nothing here needs to know what a closeout ledger
is. A future widening of the close-keyword grammar belongs in this file and can be
reviewed without re-reading the floor.

Not claimed by this reader:
  - STALE CLONE. ``range_commits`` bounds a ref CREATION with the local
    remote-tracking refs, which an unfetched or unpruned clone can overstate: commits
    the target remote has never seen are then excluded and never judged. That
    direction is a MISS, not a false refusal, and it is the same staleness every
    other consumer of ``origin/main`` in this repo already carries. Restated here
    because the release record sends readers to this module docstring for it, and a
    caveat reachable only from one function's docstring is a caveat most readers
    never reach.
  - The unbounded-creation scan is CAPPED at ``MAX_UNBOUNDED_CREATION_SCAN``; commits
    past it are not read. The cap is reported through ``notes`` ONLY when the caller
    supplies a list -- ``range_commits``'s ``notes`` parameter defaults to ``None``,
    and a caller who leaves it there gets a silent truncation. ``evaluate`` always
    passes one; a direct library caller must.
  - ``parse_push_stdin`` DROPS a line that is not four whitespace-separated fields
    and only COUNTS it. It cannot say what ref that line named, so the count is a
    coverage hole, not a diagnosis; the guard next door turns a nonzero count into a
    no-verdict exit rather than judging the remainder as if it were the push.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ZERO_SHA = "0" * 40
GIT_TIMEOUT_SECONDS = 30
NO_VERDICT_EXIT = 2

try:
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:  # executed directly from scripts/
    try:
        from scripts.core.subprocess_guard import run_process
    except ModuleNotFoundError:

        def run_process(*_args: Any, **_kwargs: Any):
            raise ModuleNotFoundError("subprocess_guard")


# The close verbs and the three ref forms GitHub closes on, spelled exactly as the
# canonical scanner now spells them. `GH-123` and the full issue URL were once visible
# ONLY here, so a body using either closed an issue that `iter_close_keyword_refs`
# reported nothing about; that gap is closed at the source and this copy is now a
# REDUNDANT second reader, not the only one that can see them.
_VERB = r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)(?:\s*:\s*|\s+)"
_SLUG = r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"
_REF = rf"(?:(?:{_SLUG})?\#\d+|GH-\d+|https?://(?:www\.)?github\.com/{_SLUG}/issues/\d+)"
# The comma-list form applies to every spelling, not only to `#N`. Keeping `GH-`/URL
# out of the list grammar left `Closes GH-10, GH-11` reporting only 10 -- under-fire
# on the one surface whose job is to be at least as wide as GitHub.
_LAUNCH_RE = re.compile(_VERB + rf"(?P<refs>{_REF}(?:\s*,\s*{_REF})*)")
# IGNORECASE, matching `_LAUNCH_RE`'s leading `(?i)`. A launch that classifies a span as
# a close and then extracts nothing from it is the one shape a two-regex scanner can
# reach and a one-regex one cannot; `closes gh-700` was exactly that.
_REF_RE = re.compile(
    rf"(?:https?://(?:www\.)?github\.com/(?P<url_repo>{_SLUG})/issues/(?P<url_number>\d+)"
    rf"|GH-(?P<gh_number>\d+)"
    rf"|(?P<repo>{_SLUG})?\#(?P<number>\d+))",
    re.IGNORECASE,
)
# A ref-creation push with no remote-tracking refs to bound it (a URL push, or a
# remote never fetched) has no honest upper bound, and an unbounded scan of a long
# history is how a push-time gate gets uninstalled. It is capped and the cap is
# REPORTED -- a silent truncation would read as "the whole range came back clean".
MAX_UNBOUNDED_CREATION_SCAN = 2000


class RangeUnreadable(RuntimeError):
    """The push range could not be resolved. Distinct from a refusal: the guard
    judged nothing, so its exit code must not be confused with a pass."""


def _git(repo_root: Path, *args: str) -> str:
    result = run_process(["git", *args], cwd=repo_root, timeout_seconds=GIT_TIMEOUT_SECONDS)
    if result.returncode == 124:
        raise RangeUnreadable(f"git {' '.join(args)} timed out after {GIT_TIMEOUT_SECONDS}s")
    if result.returncode != 0:
        raise RangeUnreadable(f"git {' '.join(args)} failed: {result.stderr.strip()!r}")
    return result.stdout


def parse_push_stdin(text: str) -> list[dict[str, str]]:
    """The ``<local-ref> <local-sha> <remote-ref> <remote-sha>`` lines git feeds a
    pre-push hook (``git help githooks``).

    Lines that are not four whitespace-separated fields are dropped and COUNTED, and
    the count is reported. git itself always emits four fields and ref names cannot
    contain spaces, so a dropped line means some wrapper fed this something else.
    This reader renders no verdict about that: it reports the count, and the guard
    treats any nonzero count as a NO-VERDICT rather than judging the lines it could
    read as if they were the whole push. A dropped line names a ref nothing here can
    recover, so the commits it would have landed are unjudged -- and an unjudged
    commit reported through a zero exit is the false green this floor exists to stop.
    """
    refs: list[dict[str, str]] = []
    dropped = 0
    for line in text.splitlines():
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 4:
            dropped += 1
            continue
        local_ref, local_sha, remote_ref, remote_sha = fields
        refs.append(
            {
                "local_ref": local_ref,
                "local_sha": local_sha,
                "remote_ref": remote_ref,
                "remote_sha": remote_sha,
                "dropped_lines": dropped,
            }
        )
    if not refs and dropped:
        return [
            {
                "local_ref": "",
                "local_sha": "",
                "remote_ref": "",
                "remote_sha": "",
                "dropped_lines": dropped,
            }
        ]
    for ref in refs:
        ref["dropped_lines"] = dropped
    return refs


def _published_exclusions(repo_root: Path, remote: str) -> list[str]:
    """``rev-list`` exclusions that bound a ref CREATION to the unpublished set.

    Prefers the remote actually being pushed to, because git passes its name as the
    hook's first argument and ``origin`` is not always it: pushing a fork layout's
    ``upstream`` while excluding ``origin`` would exclude commits the TARGET remote
    has never seen, and the guard would skip exactly the commits it is meant to read.
    When that remote has no tracking refs at all -- a URL push, or a remote never
    fetched -- the fallback is NO exclusion, not "every remote-tracking ref". Falling
    back to all remotes is the false green itself: it would exclude commits some OTHER
    remote carries and the target has never seen, which is exactly the set under
    review. Scanning the whole branch is the honest cost of not being able to ask the
    target anything.
    """
    prefix = f"refs/remotes/{remote}/"
    # `for-each-ref`, not `rev-list --count`: an exclusion pattern matching NO refs
    # makes `rev-list --count` print `0` and exit 0, so a count-based probe reports
    # "this pattern works" for every remote name including one that does not exist,
    # and the fallback would be unreachable. Asking the ref store directly is the only
    # form of this that can answer no.
    if _git(repo_root, "for-each-ref", "--count=1", "--format=%(refname)", prefix).strip():
        return ["--not", f"--remotes={remote}"]
    return []


def range_commits(
    repo_root: Path,
    local_sha: str,
    remote_sha: str,
    remote: str = "origin",
    notes: list[str] | None = None,
) -> list[str]:
    """Commits this ref update would land on the remote.

    A ref DELETION (``local_sha`` all zeros) lands no commits and is skipped. A ref
    CREATION (``remote_sha`` all zeros) has no remote tip to diff against, so the
    range is bounded by ``_published_exclusions`` above.

    The exclusion is only as accurate as the local remote-tracking refs, which a
    stale (unfetched, unpruned) clone can overstate. That direction is a miss, not a
    false refusal, and it is the same staleness every other consumer of
    ``origin/main`` in this repo already carries.
    """
    if local_sha == ZERO_SHA:
        return []
    if remote_sha == ZERO_SHA:
        exclusions = _published_exclusions(repo_root, remote)
        # Unbounded only in the no-exclusion case, and then capped. Without the cap a
        # URL push walks the whole history: minutes of subprocesses on the hook's
        # first phase, and -- worse -- today's floor applied to every historical
        # close-keyword commit, several of which cite evidence paths that have since
        # moved. Those refusals have no author-side fix short of rewriting main, so
        # the guard would be uninstalled rather than satisfied.
        cap = [] if exclusions else [f"--max-count={MAX_UNBOUNDED_CREATION_SCAN}"]
        out = _git(repo_root, "rev-list", local_sha, *exclusions, *cap)
        commits = out.split()
        if cap and len(commits) == MAX_UNBOUNDED_CREATION_SCAN and notes is not None:
            # Named, because a silent truncation reads as "the whole range came back
            # clean" -- and the repo rule is that a bounded lane says what it dropped.
            notes.append(
                f"{local_sha}: remote {remote!r} has no local tracking refs, so the "
                f"creation range could not be bounded and was capped at "
                f"{MAX_UNBOUNDED_CREATION_SCAN} commits; older commits were NOT judged"
            )
        return commits
    out = _git(repo_root, "rev-list", f"{remote_sha}..{local_sha}")
    return out.split()


def commit_body(repo_root: Path, sha: str) -> str:
    """The STORED commit message, byte for byte as GitHub's parser will read it.

    No comment stripping and no fence stripping, deliberately. Both are models of
    what some other tool did or will do to the text, and the whole point of this
    surface is that it reads the text itself.
    """
    return _git(repo_root, "show", "-s", "--format=%B", sha)


def commit_paths(repo_root: Path, sha: str) -> list[str]:
    """Paths this commit added, copied, or modified.

    A merge commit lists nothing here, so a merge whose message close-keywords an
    issue falls through to the bare-keyword path and gets the STRICTER floor. That is
    the safe direction and is why the empty result is not special-cased.
    """
    # `core.quotePath=false` because the default renders a non-ASCII path as
    # `"charness-artifacts/issue/\303\251.md"` -- quotes and all -- which fails the
    # `charness-artifacts/issue/` prefix test downstream. The artifact is then skipped
    # and its declared classification lost, which is the defect this reader exists to
    # fix, arriving through the filename instead of through the parse.
    out = _git(
        repo_root,
        "-c",
        "core.quotePath=false",
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "--diff-filter=ACM",
        "-r",
        sha,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def commit_file(repo_root: Path, sha: str, path: str) -> str:
    return _git(repo_root, "show", f"{sha}:{path}")


def close_targets(body: str, iter_refs: Any) -> list[tuple[str | None, int]]:
    """Every ``(repo_or_None, number)`` a GitHub close keyword in ``body`` would fire.

    UNFILTERED by repository, deliberately. The bare-ledger floor applies only to this
    repo's issues, but the protected-target authorization must see a foreign ref to
    refuse it: filtering here dropped ``Fixes owner/fork#626`` before authorization
    ran, so a crosswalk-protected target escaped through the near-miss lane the
    authorization exists to catch. Callers filter for the floor; nobody filters for
    authorization.

    Two grammars unioned, and they are currently IDENTICAL: the canonical scanner has
    been widened to the ``GH-N`` and issue-URL spellings this file's launch regex was
    written for, so the union is a no-op for every input today. Kept anyway, and the
    reason is the direction of failure -- a future NARROWING of the shared scanner
    would silently narrow the one surface whose job is to model GitHub rather than
    this repo's convention, and a redundant reader costs a set union.
    """
    found: set[tuple[str | None, int]] = set(iter_refs(body))
    for launch in _LAUNCH_RE.finditer(body):
        for ref in _REF_RE.finditer(launch.group("refs")):
            if ref.group("url_number"):
                found.add((ref.group("url_repo"), int(ref.group("url_number"))))
            elif ref.group("gh_number"):
                found.add((None, int(ref.group("gh_number"))))
            else:
                found.add((ref.group("repo"), int(ref.group("number"))))
    return sorted(found, key=lambda ref: (ref[0] or "", ref[1]))


def local_numbers(qualified: list[tuple[str | None, int]], repo: str) -> set[int]:
    """The subset of ``qualified`` GitHub could actually close from this repo.

    GitHub only auto-closes in the repo the commit lands in, so applying the ledger
    floor to a foreign ref would refuse over a close that cannot happen and push the
    author toward writing the unqualified form that can.
    """
    return {
        number
        for ref_repo, number in qualified
        if ref_repo is None or ref_repo.lower() == repo.lower()
    }
