#!/usr/bin/env python3
"""What a commit message CLAIMS to close, and which artifact carries each claim.

Split from `check_issue_closeout_commit_msg.py` on the seam this file family
already uses: `prepush_close_keyword_scan.py` states it plainly -- everything in
the reading half answers a question with a factual answer, and nothing in it
renders a VERDICT. That is exactly the line here. Every function below can be
checked against git's and GitHub's documented behaviour alone; none of them needs
to know what a closeout ledger is, and none decides whether a floor is satisfied.
The checker next door owns the floors, the refusal, and the remediation.

`partition_closeout_carriers` in particular was already shared with
`prepush_close_keyword_guard.py` rather than reimplemented there, precisely
because two copies would be two answers to "which floor does this close target
get" at an irreversible boundary. Living in a module named for the question makes
that shared ownership explicit instead of incidental.
"""
from __future__ import annotations

import re
from typing import Any

_COMMENT_LINE_RE = re.compile(r"^\s*#")


def _strip_commit_comments(body: str) -> str:
    return "\n".join(line for line in body.splitlines() if not _COMMENT_LINE_RE.match(line)).strip() + "\n"


def _close_keyword_scan_text(raw_body: str, sanitized_body: str) -> str:
    """The text close keywords are DETECTED in: the raw body and the sanitized body
    both, never the sanitized one alone.

    `_strip_commit_comments` models git's editor-mode cleanup, which drops every
    `^\\s*#` line. That model is right for a message typed in an editor and wrong
    for `-m`/`-F`, where git's default cleanup is `whitespace` and comment lines
    are stored verbatim. The gap is not theoretical: a commit body wrapped as

        ... because S7 closes
        #626/#627/#631 on the strength of that gate.

    put its refs on a line beginning with `#`. Stripping made the keyword vanish,
    this carrier reported `not_applicable`, and GitHub read the stored message and
    closed #626 -- an irreversible act with no floor anywhere.

    Scanning both is deliberately asymmetric, and the asymmetry follows the cost.
    Over-detection costs the author one reword or one ledger; under-detection costs
    an issue close that pushing again cannot undo. The added false-positive surface
    is git's own comment block (`# On branch main`, `#\tmodified: <path>`), which
    carries no `close/fix/resolve` verb immediately before a `#N`.

    Only DETECTION reads this text. The carrier body handed to `verify_closeout`
    stays the sanitized one, so a real editor comment can never satisfy a floor --
    it can only trigger one.
    """
    return raw_body + "\n" + sanitized_body


def partition_closeout_carriers(
    artifacts: list[dict[str, Any]], message_refs: set[int], close_numbers: set[int]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[int]]:
    """Split closeout artifacts into live carriers and pause-exempt briefs, and name
    the numbers left with no artifact carrier.

    Shared with the pre-push guard rather than reimplemented there. The pause
    carve-out and the covered-number subtraction decide WHICH floor each close target
    gets, so two copies would be two answers to that question, and the surface that
    drifted would fail open at an irreversible boundary. ``message_refs`` is the
    unfiltered mention set the pause overlap is tested against; ``close_numbers`` is
    the repo-filtered set the bare floor applies to.
    """
    pause_briefs = [
        artifact
        for artifact in artifacts
        if artifact["pause_brief"] and not (set(artifact["numbers"]) & message_refs)
    ]
    live = [artifact for artifact in artifacts if artifact not in pause_briefs]
    covered = {number for artifact in live for number in artifact["numbers"]}
    return live, pause_briefs, sorted(number for number in close_numbers if number not in covered)


def _close_keyword_numbers(scan_text: str, iter_refs: Any, current_repo: str) -> set[int]:
    """Issue numbers in THIS repo that the commit message itself close-keywords.

    GitHub auto-closes on a close keyword landing on the default branch
    regardless of whether any ``charness-artifacts/issue/*.md`` was staged.
    Re-keying the floor to this mechanism (not only the artifact-staging
    convention) closes the escape where a bare ``Fixes #123`` commit message
    auto-closes an issue with no floor anywhere. ``iter_refs`` is the shared
    ``issue_verify_closeout.iter_close_keyword_refs`` scanner (covers the plain,
    colon, and single-keyword comma-list close-keyword forms) so this module
    keeps no second copy of the close-keyword regex.

    Scans ``_close_keyword_scan_text`` -- the raw body AND the comment-stripped one,
    because git's editor-mode comment stripping is a model of the stored message and
    that model was wrong for a ``-m`` commit (see that function; it cost #626). It
    deliberately does NOT strip code
    fences either: GitHub parses the raw commit-message text for close keywords and
    treats backticks as literal characters, so a fenced ``Fixes #123`` still
    auto-closes #123. Stripping fences here reported ``not_applicable`` while
    GitHub closed the issue with no floor anywhere — the exact escape this floor
    exists to close (an agent quoting a log/diff that contains a close keyword,
    or deliberately fencing one to dodge the floor).

    Repository-qualified refs to ANOTHER repo are excluded. GitHub only auto-closes an
    issue in the repo the commit lands in, so ``Fixes acme/other-repo#77`` closes nothing
    here — but folding it in reported ``missing_close_keywords: [77]`` against THIS
    repo's #77, and the remedy that satisfies that report is writing ``Fixes #77``,
    which would auto-close a local issue the author never meant to touch. A floor whose
    remedy causes the harm it guards against is worse than no floor on that path.
    """
    return {
        number
        for repo, number in iter_refs(scan_text)
        if repo is None or repo.lower() == current_repo.lower()
    }
