"""Referent floor: the destination a disposition NAMES must exist.

The disposition floors already check FORM -- `applied: <what>` / `issue #N` /
`none — <reason>` -- and say out loud that they are "form/enum only (never a
content classifier)", delegating substance to a fresh-eye review. That split
left a decidable middle unowned, and four claims rounds on one release walked
straight through it:

- `Structural follow-up: issue #N (recurs: ...)` passed every gate. `#N` is not
  in the placeholder vocabulary (`TODO|TBD|<...>|FIXME`) and `issue #N` is a
  perfectly well-formed disposition. No issue was ever filed.
- `applied: ... publish_release_execute.py renders it` named a mechanism that
  had been DELETED, in the disposition for the finding about hardcoded claims.
- `applied: recorded in the goal's Coordination Cues` named a section holding
  only unfilled scaffold prose.

None of those needs a content classifier to catch. "Is `#N` an issue number?"
and "does this path exist?" are mechanically decidable, and that is the whole
scope of this module. It does NOT judge whether the destination is the RIGHT
one -- that stays the fresh-eye reviewer's call, exactly as before.

Three rungs, not two:

    form      -- a disposition is present and well-shaped     (existing floors)
    referent  -- the thing it names is real                   (THIS module)
    substance -- the thing it names is the right thing        (fresh-eye review)

Offline and deterministic by design. Issue numbers are checked for SHAPE, not
against the tracker: a network call would make a proof surface non-hermetic and
fail closed on an airgapped run, and the defect that actually shipped was a
literal `#N`, not a plausible-but-wrong number.
"""
from __future__ import annotations

import re
from pathlib import Path

#: `issue #123` / `tracked issue: #123` / `issue 123`.
#:
#: A `#` or a leading digit is REQUIRED. Without that, `issue closeout`,
#: `issue carrier` and `issue anchors` -- ordinary prose about this repo's own
#: issue machinery, which appears in dozens of checked-in goals -- all parse as
#: issue references and the gate cries wolf. A gate with false positives is one
#: authors learn to skip, which would reproduce the very problem it exists to
#: fix, so the narrow form is deliberate: `#N` is still caught, because it has
#: the `#`.
ISSUE_REF_RE = re.compile(
    r"\bissue[:\s]+(?:#([A-Za-z0-9_<>-]+)|(\d+)\b)", re.IGNORECASE
)

#: A disposition VALUE that is still a placeholder belongs to the form floor,
#: which already rejects `TODO`/`TBD`/`<...>`/`FIXME`. This gate stays quiet on
#: them: double-reporting one defect from two gates makes both noisier, and the
#: scaffold seeds `issue #N (recurs:|novel: <reason>)` as literal TEMPLATE text
#: on a `TODO` line, so firing there would flag every freshly scaffolded goal.
PLACEHOLDER_VALUE_RE = re.compile(r":\s*(?:TODO|TBD|FIXME)\b", re.IGNORECASE)

#: A repo-relative path mentioned in a disposition. Requires a directory
#: separator and a file extension so ordinary prose ("the goal's Coordination
#: Cues") is not mistaken for a path; bare filenames are handled below.
PATH_RE = re.compile(r"\b((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]{1,6})\b")

#: Tokens that look like an issue number but name nothing. `n` and `N` are the
#: scaffold's own placeholder; the rest are the shapes seen in practice.
_NON_NUMBERS = {"n", "tbd", "todo", "fixme", "x", "nnn", "<n>", "num"}


def issue_refs(text: str) -> list[str]:
    """Every issue reference in `text`, as written."""
    return [m.group(1) or m.group(2) for m in ISSUE_REF_RE.finditer(text)]


def is_placeholder_line(text: str) -> bool:
    """Whether this line's disposition value is an unfilled placeholder.

    Owned by the form floor, not here. Returning True keeps this gate silent so
    a scaffolded artifact reports one defect from one gate rather than two.
    """
    return PLACEHOLDER_VALUE_RE.search(text) is not None


def bad_issue_refs(text: str) -> list[str]:
    """Issue references that cannot name a real issue.

    A reference is bad when it is not a positive integer. `#N` is the case this
    exists for: it is the scaffold's placeholder, it is well-formed as a
    disposition, and it shipped inside a release bundle pointing at nothing.
    """
    bad = []
    for ref in issue_refs(text):
        raw = ref.strip()
        # `<n>` / `<N>` is this repo's documented placeholder syntax, and the form
        # floor's own vocabulary already contains `<[^>]*>`. An author writing
        # `tracked issue: #<n>` is QUOTING THE FORM, not dispositioning anything --
        # which is exactly how the reference guidance and this gate's own rationale
        # are written. Bare `#N` carries no such marking: it reads as a filled-in
        # disposition and was the shape that shipped pointing at nothing.
        if raw.startswith("<") and raw.endswith(">"):
            continue
        if raw.isdigit() and int(raw) > 0:
            continue
        bad.append(ref)
    return bad


def missing_paths(text: str, repo_root: Path) -> list[str]:
    """Repo-relative paths named in `text` that do not exist on disk.

    Only paths with a separator AND an extension are considered, so this cannot
    fire on prose. A path inside a code span is still checked -- backticks are
    how this repo writes real paths, so exempting them would exempt the cases
    that matter.
    """
    missing = []
    for match in PATH_RE.finditer(text):
        candidate = match.group(1)
        # A bare `x.y` version-ish token or a sentence-final abbreviation cannot
        # reach here (no separator), but a URL can -- skip anything schemed.
        if "://" in candidate:
            continue
        if not (repo_root / candidate).exists():
            missing.append(candidate)
    return missing


#: A git SHA as this repo writes them in artifacts: 7-40 hex chars, usually in a
#: code span. Bounded below at 7 so ordinary hex-ish words ("added", "faced",
#: "decade") cannot reach the resolver -- those are <7 or contain non-hex.
SHA_RE = re.compile(r"\b([0-9a-f]{7,40})\b")

#: Words that are pure hex and >= 7 chars. English has a few; without this they
#: reach `git cat-file` and are reported as unresolvable SHAs, which is a false
#: positive on ordinary prose.
_HEX_WORDS = {"accede", "acceded", "deface", "defaced", "effaced", "facade", "decade", "decaf"}


def unresolvable_shas(text: str, repo_root: Path, *, run) -> list[str]:
    """SHA-shaped tokens in `text` that git cannot resolve to a commit.

    Catches the class where a commit is cited that does not exist, or a SHA is
    mistyped -- a claims round found a goal attributing one commit to two
    different review rounds two lines apart, and the real commit for one of them
    appeared nowhere in the tree.

    `run` is injected so this stays testable without a git fixture, and so a
    caller in a non-git context can pass a stub rather than have the gate crash.
    """
    bad = []
    for match in SHA_RE.finditer(text):
        token = match.group(1)
        if token.lower() in _HEX_WORDS:
            continue
        if token.isdigit():
            # A run of 7+ digits is a number in prose, not a SHA.
            continue
        if not run(token, repo_root):
            bad.append(token)
    return bad


def git_commit_exists(sha: str, repo_root: Path) -> bool:
    """Whether `sha` resolves to a commit object in `repo_root`."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "cat-file", "-t", sha],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        # Git unavailable: do NOT invent a defect. Absence of a resolver is not
        # evidence the referent is bad.
        return True
    return result.returncode == 0 and result.stdout.strip() == "commit"


def check_disposition_referents(text: str, repo_root: Path) -> list[dict[str, str]]:
    """Every referent defect in one disposition line or block.

    Returns a list of findings rather than raising, so a caller can attach them
    to its own report shape. An empty list means every destination this text
    names is real -- NOT that the destinations are correct.
    """
    findings: list[dict[str, str]] = []
    if is_placeholder_line(text):
        return findings
    for ref in bad_issue_refs(text):
        findings.append({
            "kind": "unresolvable-issue-ref",
            "token": ref,
            "detail": (
                f"`issue #{ref}` does not name an issue. A disposition's whole job is to "
                "point somewhere; a placeholder is a disposition that resolves to nothing "
                "while passing every form check."
            ),
        })
    for path in missing_paths(text, repo_root):
        findings.append({
            "kind": "missing-path-referent",
            "token": path,
            "detail": (
                f"`{path}` does not exist. A disposition naming a file that is not there "
                "reads as applied and is not."
            ),
        })
    return findings
