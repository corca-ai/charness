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


#: A repo-relative path mentioned in a disposition. Requires a directory
#: separator and a file extension so ordinary prose is not mistaken for a path;
#: bare filenames are handled below.
PATH_RE = re.compile(r"\b((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]{1,6})\b")



def issue_refs(text: str) -> list[str]:
    """Every issue reference in `text`, as written."""
    return [m.group(1) or m.group(2) for m in ISSUE_REF_RE.finditer(text)]


#: The disposition keyword whose VALUE the placeholder test applies to. Anchored
#: at the start so a trailing `Owner: TODO` on the same line cannot reach it.
#: THE disposition vocabulary, owned here and imported by the gate. Two
#: near-identical copies existed; the failure mode was not "they drift" but
#: "one grows and the other silently degrades" -- adding a keyword to the gate's
#: copy would have quietly reverted this module's value-scoping to whole-line
#: behaviour, reintroducing the M2 and M3 evasions at once.
DISPOSITION_KEYWORDS = (
    r"Retro dispositions|Structural follow-up|Disposition|Decision|applied|tracked issue"
)

#: `applied:` / `tracked issue:` mid-line, tolerating bold markers.
#: `Disposition: **applied** — ...` is this repo's second-most-common spelling
#: (75 occurrences across 28 goals) and the bold markers sit between the word
#: and the colon, so a plain `\bapplied\s*:` cannot see it.
INLINE_DISPOSITION_RE = re.compile(r"\b\**(?:applied|tracked issue)\**\s*:", re.IGNORECASE)

#: Anchored at line start: matches the keyword that OPENS a disposition.
DISPOSITION_LINE_RE = re.compile(
    rf"^[\s>*+-]*\**(?:{DISPOSITION_KEYWORDS})\**\s*:",
    re.IGNORECASE,
)

#: Same, but consuming trailing space so the caller gets the VALUE.
_LEADING_DISPOSITION_RE = re.compile(
    r"^[\s>*+-]*\**(?:Retro dispositions|Structural follow-up|Disposition|Decision|applied"
    r"|tracked issue)\**\s*:\s*",
    re.IGNORECASE,
)


def is_placeholder_line(text: str) -> bool:
    """Whether this line's DISPOSITION VALUE is an unfilled placeholder.

    Owned by the form floor, not here: returning True keeps this gate silent so a
    scaffolded artifact reports one defect from one gate rather than two.

    Scoped to the value, NOT the line. An earlier version searched the whole line,
    which made the rung trivially evadable --

        Structural follow-up: issue #N (recurs: x). Owner: TODO

    -- where an unrelated unfilled field suppressed the `#N` this module was
    written about. Any author leaving one scaffold field blank disarmed the rung
    for that entire line.
    """
    match = _LEADING_DISPOSITION_RE.match(text)
    if match is None:
        # No leading keyword. Take the tail after the LAST inline disposition
        # colon, so `- The retro entry is applied: TODO` still defers. An earlier
        # version set `head = text` and then clipped the first clause of the
        # LINE, which never began with the placeholder -- a comment describing
        # behaviour the code did not have, on a proof surface.
        inline = list(INLINE_DISPOSITION_RE.finditer(text))
        head = text[inline[-1].end():] if inline else text
    else:
        head = text[match.end():]
    # Only the FIRST clause of the value can be a placeholder; a later sentence
    # is separate prose.
    first_clause = re.split(r"[.;]", head, maxsplit=1)[0]
    return re.match(r"^\s*(?:TODO|TBD|FIXME)\b", first_clause, re.IGNORECASE) is not None


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
        # A URL's tail looks exactly like a repo path (`example.com/docs/x.md`),
        # and the scheme is OUTSIDE the match -- so testing `candidate` for
        # `://` never fired. Look at what PRECEDES the match instead. Without
        # this, every external link in a disposition is reported as a missing
        # file, which is the false-positive class that makes a gate ignorable.
        if "://" in text[max(0, match.start() - 8):match.start()]:
            continue
        if not (repo_root / candidate).exists():
            missing.append(candidate)
    return missing


#: A git SHA as this repo writes them in artifacts: 7-40 hex chars, usually in a
#: code span. Bounded below at 7 so ordinary hex-ish words ("added", "faced",
#: "decade") cannot reach the resolver -- those are <7 or contain non-hex.
SHA_RE = re.compile(r"\b([0-9a-f]{7,40})\b")

# UUID components can be SHA-shaped in durable typed identities such as lesson
# `session_id` values. Treat the canonical UUID as one non-commit token rather than
# sending its 8- and 12-hex components to Git independently. This is deliberately
# shape-bound: malformed UUID-like text and a real SHA elsewhere on the same line
# remain candidates.
UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)

# Content-addressed review packets type their SHA-256 values as identities. Their
# abbreviated display values are SHA-shaped, but they are not Git commit
# citations. Preserve the producer's explicit type while leaving any actual
# commit candidate elsewhere on the same line visible to the resolver.
TYPED_CONTENT_DIGEST_RE = re.compile(
    r"\b(?:"
    r"packet(?:[\s_-]+identity)?|"
    r"(?:reviewed[\s_-]+)?input[\s_-]+identity|"
    r"findings[\s_-]+identity|"
    r"identity_sha256"
    r")(?:\s*:\s*|\s+)`?([0-9a-f]{7,64})(?:\.\.\.)?`?",
    re.IGNORECASE,
)

#: Words that are pure hex and >= 7 chars. English has a few; without this they
#: reach `git cat-file` and are reported as unresolvable SHAs, which is a false
#: positive on ordinary prose.
#: Only >= 7 chars can reach here at all -- `SHA_RE` is `{7,40}` -- so shorter
#: hex words (`facade`, `decade`, `decaf`) are excluded by the length bound and
#: listing them here was dead weight that made the filter look broader than it is.
_HEX_WORDS = {"acceded", "defaced", "effaced"}


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
    for token in sha_candidates(text):
        if not run(token, repo_root):
            bad.append(token)
    return bad


def sha_candidates(text: str) -> list[str]:
    """SHA-shaped tokens in `text` that are worth asking git about.

    Split out so a caller can COUNT what the rung actually examined. The gate
    previously incremented its `shas_resolved` counter once per LINE, which made
    it a line counter wearing a SHA counter's name -- it stayed at the corpus
    line count whether or not a single token was ever resolved, and so was
    structurally incapable of showing the collapse it was added to detect.
    """
    out = []
    uuid_spans = [match.span() for match in UUID_RE.finditer(text)]
    content_digest_spans = [
        match.span(1) for match in TYPED_CONTENT_DIGEST_RE.finditer(text)
    ]
    for match in SHA_RE.finditer(text):
        if any(start <= match.start() and match.end() <= end for start, end in uuid_spans):
            continue
        if any(
            start <= match.start() and match.end() <= end
            for start, end in content_digest_spans
        ):
            continue
        token = match.group(1)
        if token.lower() in _HEX_WORDS:
            continue
        if token.isdigit():
            # A run of 7+ digits is a number in prose, not a SHA.
            continue
        out.append(token)
    return out


class ResolverUnavailable(Exception):
    """Git cannot answer, as opposed to answering "no".

    The distinction is the whole point. A missing binary raises; so does `exit
    128`, which is what git returns for "not a git work tree" (a source tarball,
    a vendored copy, a pip-installed tree) and for "detected dubious ownership"
    (`safe.directory`, routine in containers and under a different uid). An
    earlier version caught only OSError and treated exit 128 as "this SHA does
    not exist" -- which would have reported EVERY sha in EVERY dated artifact as
    unresolvable the moment the gate ran in a container. A docstring promising
    "absence of a resolver is not evidence the referent is bad" while a
    present-but-refusing resolver produced a corpus-wide false-positive storm is
    the exact class this gate exists to catch, so it is raised, not swallowed.
    """


def reachable_head_commits(repo_root: Path) -> set[str]:
    """Full commit identities reachable from ``HEAD`` in a complete repository.

    The corpus gate asks about thousands of tokens. Reading the ancestry once
    avoids turning a structural durability check into one Git process per token.
    A shallow repository cannot disprove older reachability, so it is reported
    as unestablished instead of producing false missing-history findings.
    """
    import subprocess

    try:
        shallow = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--is-shallow-repository"],
            capture_output=True, text=True, timeout=10,
        )
        if shallow.returncode != 0:
            raise ResolverUnavailable(
                (shallow.stderr or "").strip() or f"git exited {shallow.returncode}"
            )
        if shallow.stdout.strip() == "true":
            raise ResolverUnavailable(
                "repository history is shallow; missing ancestry cannot be disproved"
            )
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-list", "HEAD"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ResolverUnavailable(f"git could not be run: {exc}") from exc
    if result.returncode != 0:
        raise ResolverUnavailable(
            (result.stderr or "").strip() or f"git exited {result.returncode}"
        )
    return set(result.stdout.splitlines())


def commit_identity_in_ancestry(sha: str, commits: set[str]) -> bool:
    """Whether a full or abbreviated identity names exactly one ancestry commit."""
    return sum(commit.startswith(sha) for commit in commits) == 1


def git_commit_reachable_from_head(sha: str, repo_root: Path) -> bool:
    """Whether `sha` is durable history reachable from `repo_root`'s ``HEAD``.

    Raises `ResolverUnavailable` when git cannot answer at all.

    Object presence is deliberately insufficient. A long-lived authoring clone
    can retain commits from deleted branches or sibling worktrees that a clean
    clone of the same reviewed ``HEAD`` cannot fetch. The full ancestry reader
    above makes the verdict a property of the published tree instead of the
    local object database and is the single semantic owner. Exact and
    unambiguous abbreviated identities are accepted; missing, non-commit, side
    branch, and ambiguous prefixes are all non-durable.
    """
    return commit_identity_in_ancestry(sha, reachable_head_commits(repo_root))


#: The disposition vocabulary, for detecting a line that ENUMERATES forms rather
#: than using one.
_VOCAB_RE = re.compile(
    r"`?(?:applied|tracked issue|issue|none|accepted-risk|out-of-scope|repo-local guard"
    r"|Structural follow-up|Retro dispositions)\s*[:#]",
    re.IGNORECASE,
)

#: An angle-bracket slot (`<what>`, `<reason>`, `<path>`) is unambiguous evidence
#: that a line is showing the FORM.
_SLOT_RE = re.compile(r"<[a-z][a-z /|-]*>", re.IGNORECASE)


def documents_the_vocabulary(text: str) -> bool:
    """Whether this line is SHOWING disposition forms rather than using one.

    Without this the gate cannot be documented inside its own enforced corpus:
    every reference page, and the next retro explaining this gate, contains a
    sentence like "the floor accepts `applied: <what>` / `issue #N` / `none`",
    and `issue #N` there is an example, not a dangling pointer.

    A backtick test would be WRONG and was rejected: the real v6.3.0 defect --
    ``Decision: `issue #N (recurs: ...)` `` -- was itself inside a code span, so
    exempting code spans would exempt the exact case this module exists for.

    The discriminator is ENUMERATION. Documentation lists the alternatives (two
    or more distinct forms, or an explicit `<slot>`); a real disposition commits
    to one.
    """
    # Everything is measured on the VALUE, never the line. Round 1 scoped the
    # form count and left `_SLOT_RE` searching the whole line, which reproduced
    # the very evasion (M2) that scoping was meant to close: any lowercase
    # angle-bracket token anywhere -- `<ref>`, `<repo-root>`, `<path>`, all
    # ordinary repo idiom -- exempted the line.
    match = _LEADING_DISPOSITION_RE.match(text)
    value = text[match.end():] if match else text
    forms = len({m.group(0).strip("`").lower() for m in _VOCAB_RE.finditer(value)})
    has_slot = _SLOT_RE.search(value) is not None

    # THREE or more forms is documentation on its own: nobody commits a single
    # improvement to three destinations at once.
    if forms >= 3:
        return True
    # Two forms is ambiguous, and getting it wrong in the permissive direction is
    # how round 1 shipped an evasion. `Retro dispositions: applied: filed as
    # issue #N` is the corpus's DOMINANT spelling and names two forms while
    # committing to one -- a bare count exempted it. A slot is what separates
    # showing from doing, so two forms only count as documentation alongside one.
    return forms >= 2 and has_slot


def check_disposition_referents(text: str, repo_root: Path) -> list[dict[str, str]]:
    """Every referent defect in one disposition line or block.

    Returns a list of findings rather than raising, so a caller can attach them
    to its own report shape. An empty list means every destination this text
    names is real -- NOT that the destinations are correct.
    """
    findings: list[dict[str, str]] = []
    if is_placeholder_line(text):
        return findings
    # Scoped to the ISSUE rung. The self-documentation problem is specific to
    # `issue #N` appearing as an example; a path has no such problem, and round
    # 1's blanket early-return also exempted a documentation line naming a
    # DELETED file -- a wider exemption than its own justification.
    documenting = documents_the_vocabulary(text)
    for ref in ([] if documenting else bad_issue_refs(text)):
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
