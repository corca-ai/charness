"""Canonicalization of paths cited inside a handoff artifact.

Its own module, not a length-cap spill: "which file does this citation name?" is
a different question from "how does the ``## Next Session`` block split into
entries", and it has its own failure mode. A cited markdown link is relative to
the CITING file, and the parser used to canonicalize by stripping ``./`` and
``../`` prefixes and testing the result against the repo root -- a check run
against the wrong base, reporting its miss as a fact.
"""
from __future__ import annotations

import posixpath
from pathlib import Path


def strip_relative_prefixes(token: str) -> str:
    stripped = token.strip()
    while stripped.startswith(("./", "../")):
        stripped = stripped[2:] if stripped.startswith("./") else stripped[3:]
    return stripped


def resolve_lexically(base_rel: str, token: str) -> str | None:
    """``token`` joined onto ``base_rel`` (a repo-root-relative dir), or None if it escapes.

    LEXICAL, deliberately -- ``Path.resolve()`` follows symlinks, and this repo
    checks in current-pointer symlinks (``charness-artifacts/*/latest.md``,
    ``CLAUDE.md -> AGENTS.md``). Resolving would rewrite a citation of the POINTER
    into its frozen dated target, so a drafted goal's Boundaries would name the
    wrong surface and a pointer+target pair cited together would dedup into one.
    """
    joined = posixpath.normpath(posixpath.join(base_rel, token.strip()))
    if joined == ".." or joined.startswith("../") or joined.startswith("/"):
        return None
    return "" if joined == "." else joined


def with_token_slash(canonical: str, token: str) -> str:
    """Keep a directory token's trailing slash.

    Path joining discards it, and boundary tokens are intersected as EXACT strings
    across sources: handoff entries normalize with an artifact dir while
    issue-derived entries do not, so dropping the slash on one side made
    ``integrations/tools`` and ``integrations/tools/`` stop intersecting and a
    merge that fired before silently stopped firing.
    """
    if token.strip().endswith("/") and canonical and not canonical.endswith("/"):
        return canonical + "/"
    return canonical


def normalize_path(
    token: str, *, artifact_dir: Path | None = None, repo_root: Path | None = None
) -> str:
    """Canonicalize a cited path to repo-root-relative form.

    Handoffs carry TWO citation styles and both are legitimate:

    * genuinely relative links (``./deferred-decisions.md``,
      ``../charness-artifacts/x.md``), which markdown resolves against the CITING
      file's directory, and
    * repo-root-relative bare paths (``charness-artifacts/goals/x.md``), which this
      repo's handoffs write directly.

    Prefix-stripping handles only the second, and made the first right by
    coincidence or wrong by accident: from ``docs/``, ``../charness-artifacts/x.md``
    strips to the right answer because ``docs/..`` IS the root, while
    ``./deferred-decisions.md`` strips to a path that does not exist -- so a live,
    correct link was reported as a stale citation and the drafter stamped MISSING
    on it in a goal's Boundaries.

    Resolving EVERYTHING against the artifact directory is equally wrong, and the
    repo's own tests caught it: a bare ``charness-artifacts/goals/x.md`` became
    ``docs/charness-artifacts/goals/x.md`` and the completed-goal filter stopped
    firing.

    So the base follows the style the token declares. An explicitly relative token
    has unambiguous markdown semantics and gets the artifact directory ONLY --
    falling back to the root base for those would launder a stale citation into a
    different existing file (``./README.md`` in ``docs/`` finding the ROOT README
    after ``docs/README.md`` was deleted, reported live and pointing at the wrong
    surface). A bare token is genuinely ambiguous, so both bases are tried and the
    one that exists wins. When nothing resolves, the stripped form is kept so a
    genuinely stale citation stays reportable instead of being rewritten.
    """
    raw = token.strip()
    if not raw:
        # `[the rule](#skill-routing)` -- `_collect_paths` splits the fragment off
        # and leaves an empty token. Joined onto the artifact base it normalized to
        # the artifact DIRECTORY, and the drafter then rendered `- In scope: docs`:
        # a goal claiming a whole top-level directory, sourced from a link that
        # names no path at all. The wrong-base class, through the new base.
        return ""
    stripped = strip_relative_prefixes(raw)
    if artifact_dir is None or repo_root is None or raw.startswith("/"):
        return stripped
    try:
        base_rel = artifact_dir.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, RuntimeError, ValueError):
        return stripped
    if raw.startswith(("./", "../")):
        # No existence check on this branch. Markdown semantics are unambiguous
        # here, so the resolved form IS the canonical one whether or not the file
        # is on disk -- and returning the stripped form when it is missing is not
        # a neutral fallback: `./README.md` in `docs/` would strip to `README.md`,
        # which the staleness check then finds at the ROOT and reports live. The
        # citation would name the wrong surface with no MISSING marker. Reporting
        # `docs/README.md` as missing is the honest answer.
        candidate = resolve_lexically(base_rel, raw)
        if candidate:
            return with_token_slash(candidate, raw)
        return with_token_slash(stripped, raw)
    # Bare tokens get the ROOT base only. Trying the artifact dir as a fallback
    # re-created round 1's blocker with the BASE diverging instead of the slash:
    # issue-derived entries normalize with no artifact dir, so a bare
    # `conventions/x.md` stayed `conventions/x.md` on that side while the handoff
    # side became `docs/conventions/x.md`, and the merger intersects boundary
    # tokens as exact strings -- the two never meet. Repo convention writes bare
    # tokens root-relative, and matching the issue side is what keeps one string
    # per surface across both sources.
    candidate = resolve_lexically(".", raw)
    if candidate:
        return with_token_slash(candidate, raw)
    return with_token_slash(stripped, raw)
