"""WHOSE record a scaffold's write path belongs to.

A cohesive concept, not a spill: `scaffold_artifact_lib` answers WHERE a family writes and
what a write there destroys, and this module answers WHO the thing at that path belongs to.
The two were one file until the length gate refused it, and the split follows the seam the
docstrings already describe -- `write_target_facts` says a write destroys content, and
nothing there could say whether the content is this author's, which is the gap the reported
producer-scaffold defect lived in.

Dependency-free on purpose, like its sibling: skill scaffolds load these modules by file path
with no package context, so nothing here may import repo machinery.
"""

from __future__ import annotations

import re
from pathlib import Path

SUBJECT_MATCH_MATCH = "match"
SUBJECT_MATCH_MISMATCH = "mismatch"
SUBJECT_MATCH_UNKNOWN = "unknown"
#: The invocation named no subject. Distinct from `unknown` (the TARGET is unreadable) because
#: the two have different owners: `undeclared` is answerable by the author with `--subject`.
#: A bounded round found why this state has to exist at all -- with a default-title fallback,
#: `debug`'s undeclared key is `debug-review`, this repo holds twenty `<date>-debug-review.md`
#: records, and a brand-new run therefore MATCHED an unrelated open one. The generic default
#: was not "a key that matches no real investigation"; it was the most common real one.
SUBJECT_MATCH_UNDECLARED = "undeclared"
#: The family DECLINED another path and picked this one. Only ever stamped on a final write
#: path, never on a target being judged: it is the answer to "may I write here", not to "whose
#: record is this", and the record it declined is in the `refused_write_artifact_*` keys.
SUBJECT_MATCH_ROUTED = "routed"
#: The one state that writes in place. Everything else -- mismatch, unreadable target,
#: undeclared invocation -- routes to a path that destroys nothing.
SUBJECT_MATCH_WRITES_IN_PLACE = SUBJECT_MATCH_MATCH
SUBJECT_IDENTITY_KEYS = (
    "invocation_subject_key",
    "write_artifact_subject_key",
    "write_artifact_subject_match",
)
_DATED_RECORD_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.+)\.md$")


def record_subject_channels(write_path: str) -> tuple[str | None, str | None]:
    """The `(slug, date)` a dated record filename carries about WHOSE record it is.

    The filename is the channel, and that is a measurement rather than a preference. Compared
    across this repo's own dated records on 2026-08-15, the H1 title disagrees with the
    filename slug in 1137/1367 critique records, 431/489 retro records, and 114/143 debug
    records -- `debug` writes the generic H1 `# Debug Review` over a specific filename like
    `2026-04-11-plugin-export-drift.md`, so a title-derived key would call every debug record
    the same subject and a title-vs-filename equality rule would refuse most of the tree.
    The filename slug is what actually names the investigation, review, or concept.

    Only `quality` reads the date channel: its recorded instance is a review written over the
    PREVIOUS day's record, where the slug matches and only the date disagrees. The others must
    NOT key on date -- `debug` continues yesterday's open investigation in place by design.

    `(None, None)` for anything that is not a dated record (`latest.md`, a rolling doc, an
    undated file): those have no per-subject filename channel, and the caller's family decides
    what its subject key is instead. `None` means UNKNOWN, never mismatch -- a fact that
    cannot be read must not manufacture a refusal.
    """
    matched = _DATED_RECORD_RE.match(Path(write_path).name)
    return (matched.group("slug"), matched.group("date")) if matched else (None, None)


#: One named accessor over the reader, for the four families that use only the slug and should
#: not have to know a date channel exists. `quality` — the only date reader — takes both
#: channels from `record_subject_channels` instead: a second one-line accessor beside this one
#: was itself a duplicate family, which is a fair verdict on two functions that differ by an
#: index.
def record_subject_slug(write_path: str) -> str | None:
    return record_subject_channels(write_path)[0]


def subject_identity_facts(
    *,
    invocation_subject_key: str | None,
    target_subject_key: str | None,
) -> dict[str, object]:
    """Does the path this invocation would write BELONG to the subject it is for?

    `write_target_facts` says whether a write destroys something; it cannot say whether the
    something is THIS author's. That is the reported gap: `debug`'s scaffold resolved its write
    path onto an unrelated OPEN investigation, and because the artifact it would have written
    carries today's date under today's filename, the date-coherence guard the `quality` family
    earned is inert against it (release scope contract, Fixed Decisions).

    Judged on the PATH's own subject channel, deliberately NOT on whether a file is there. A
    bounded round found the existence short-circuit hiding two live cases: a dangling current
    pointer names `2026-05-06-quality-review.md`, nothing is at it, and writing there files
    TODAY's review under a months-old date -- the very shape the family's validator refuses
    after the fact. Existence is a separate fact with a separate key (`write_artifact_effect`),
    and conflating them made "nothing is there" read as "nothing is at stake".

    Deliberately a FACT, computed from two keys the caller supplies, with the POLICY over it
    owned by each family. The families disagree for recorded reasons -- `debug` continues an
    open investigation in place, `quality` must never overwrite a finished review -- so one
    policy here would false-refuse one of them. What is NOT family-owned is the direction of
    the doubt: only `match` writes in place.
    """
    if invocation_subject_key is None:
        match = SUBJECT_MATCH_UNDECLARED
    elif target_subject_key is None:
        match = SUBJECT_MATCH_UNKNOWN
    elif target_subject_key == invocation_subject_key:
        match = SUBJECT_MATCH_MATCH
    else:
        match = SUBJECT_MATCH_MISMATCH
    return {
        "invocation_subject_key": invocation_subject_key,
        "write_artifact_subject_key": target_subject_key,
        "write_artifact_subject_match": match,
    }


def diverts_from_target(repo_root: Path, *, write_path: str, facts: dict[str, object]) -> bool:
    """Should a continue-in-place family route AWAY from the target it resolved?

    Two conditions, and both are needed. Unconfirmed identity is the first: mismatch, an
    unreadable target subject, and an undeclared invocation all mean nobody established the
    record is this author's. Something at stake is the second: with no current pointer at all
    the target is an empty `latest.md`, and diverting there would change the no-pointer
    bootstrap for no safety gain.

    "At stake" is: something is THERE, or the path NAMES a subject. The second half is the
    dangling-pointer case -- the record was moved or archived, and writing to the name it left
    behind files today's work under another record's date and slug, which is the shape the
    quality validator refuses after the fact.

    Not `== SUBJECT_MATCH_MISMATCH`. Two round-2 reviewers independently found that spelling
    here re-opening the hole this function was written to close: an UNDECLARED run against a
    dangling pointer is `undeclared`, not `mismatch`, so the comparison let it write in place
    under the other investigation's name while the same payload stamped `undeclared`. The
    stated rule is "only a confirmed match writes in place", and a second private spelling of
    the match test is exactly how the first version of this slice broke it in three families.
    """
    if writes_in_place(facts):
        return False
    return (repo_root / write_path).exists() or facts["write_artifact_subject_key"] is not None


def final_subject_facts(*, invocation_subject_key: str | None, target_subject_key: str | None, chosen: bool) -> dict[str, object]:
    """The identity facts for the path a payload FINALLY names.

    `routed` exists because the alternative was a payload that told its reader to distrust the
    path the scaffold had just picked for it: a debug run resuming subject `x` off a finished
    record lands on `x-followup`, whose slug never equals `x`, and the naive comparison stamped
    `mismatch` on a fresh file chosen deliberately and holding nothing.

    So: `match` when the record at the path is this invocation's own, `routed` when the family
    picked the path after declining another, and the unconfirmed values only when neither is
    true. The invocation half stays what the INVOCATION declared, because a consumer rebuilds
    `--subject` from it -- an earlier fix that overwrote it with the resolved slug would have
    had the debug planner emit a flag naming a redirect artifact the author never asked for.
    """
    facts = subject_identity_facts(
        invocation_subject_key=invocation_subject_key,
        # The FAMILY's reader, not the slug channel: `quality` keys on `slug@date`, and
        # comparing its two-channel invocation key against a bare slug never matches.
        target_subject_key=target_subject_key,
    )
    if chosen and not writes_in_place(facts):
        facts["write_artifact_subject_match"] = SUBJECT_MATCH_ROUTED
    return facts


def writes_in_place(facts: dict[str, object]) -> bool:
    """ONE reading of the facts, so no family invents its own polarity.

    Three families consumed the match value independently and two of them compared against
    `mismatch`, which quietly made `unknown` and `undeclared` write in place -- the same
    two-derivations-of-one-decision shape a bounded round found in the debug planner.
    """
    return facts["write_artifact_subject_match"] == SUBJECT_MATCH_WRITES_IN_PLACE


SUBJECT_KEY_CHANNEL_SEPARATOR = "@"


def compose_subject_key(*channels: str | None) -> str | None:
    """One spelling for a multi-channel subject key, so the families cannot drift apart.

    A family whose identity needs more than the record slug adds a channel: `quality` adds the
    record date, because its recorded instance is a review written over the PREVIOUS day's
    record, where the slug matches and only the date disagrees.

    An unreadable channel makes the WHOLE key `None`, which is unknown rather than a value.
    The first version spelled it `none` and reasoned that it "compares unequal to a real one".
    That was true and beside the point: a bounded round showed two unreadable channels compose
    to `none@none` on BOTH sides and compare EQUAL, so a repo with no lesson evaluator -- and
    every retro carrying the scaffold's own seeded `"session_id":"none"` -- silently matched.
    `None` cannot collide that way, and it also removes the sentinel's other bug: a subject
    literally named `none`.
    """
    return None if any(channel is None for channel in channels) else SUBJECT_KEY_CHANNEL_SEPARATOR.join(channels)


SUBJECT_REFUSAL_KEYS = (
    "refused_write_artifact_path",
    "refused_write_artifact_subject_key",
    "refused_write_artifact_reason",
)


def subject_refusal_facts(
    *, refused_path: str, refused_subject_key: str | None, reason: str
) -> dict[str, object]:
    """WHICH record a family declined to write over, and WHY, kept on the payload after it routes.

    Without these keys the refusal is invisible: the identity facts are recomputed from the
    FINAL write path, so a routed payload reads as if nothing was ever at risk. A run that
    cannot see it was routed cannot tell an operator why the path it expected is not the path
    it got.

    `reason` is the match value that caused it, and consumers need it because the three are not
    interchangeable. `mismatch` means the author named a DIFFERENT subject than the record's --
    a positive disagreement. `undeclared` means they named none, which is ambiguity, not
    disagreement: the scaffold must still refuse to hand back a template's write path, but a
    planner that treats it as disagreement would drop this repo's deliberate
    fail-safe-to-continue behavior for an open investigation.
    """
    return {
        "refused_write_artifact_path": refused_path,
        "refused_write_artifact_subject_key": refused_subject_key,
        "refused_write_artifact_reason": reason,
    }
