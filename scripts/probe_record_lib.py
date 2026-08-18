#!/usr/bin/env python3
"""The probe record: a behavioral probe may not claim more than it measured.

On 2026-08-18 three of one session's own measurements were refuted, two of them by
the same generator -- the probe's stimulus came from the agent's MODEL of the
mechanism rather than from the source that defines the claim. `#528` was probed with
a YAML list where the vocabulary is a mapping, so it measured the unfixed baseline.
`#628` was probed under conditions the reported case does not name. "The fix is
absent" and "the fixed branch was never entered" render identically, so a probe that
measured NOTHING reads exactly like a probe that measured a FAILURE.

This module makes that difference sayable. A probe record binds four things that a
prose "verified" leaves implicit:

- the CLAIM, and which KIND of claim it is;
- the OBSERVABLE the claim rests on, named before the measurement;
- the STIMULUS, quoted verbatim, with provenance to the source that defines the
  claim and the CONDITIONS that source names;
- a BASE and a HEAD reading of that one observable.

`resolve_probe_record` then renders the typed outcome.

WHY A SEPARATE ARTIFACT, NOT CARRIER-BODY FIELDS. The issue closeout floors read a
carrier through `_strip_code_fences`, so verbatim stimulus and quoted source text --
which need a fence to survive intact -- are exactly the content those readers throw
away. The record is its own file and the carrier NAMES it; that also gives a debt row
a stable id to cite, which `#N`-per-carrier fields never could.

THE TYPED VOCABULARY IS BORROWED, NOT REINVENTED. `state` is one of
`boundary_probe_lib`'s three words, imported from it rather than respelled, because a
fourth private spelling of "we could not tell" is how the concept drifts back apart
-- that module's own comment says so, and this is the surface it was warning about.

ONE DELIBERATE DIVERGENCE from `boundary_probe_lib`, stated because the shared
vocabulary invites the wrong assumption: there, `evaluated` is orthogonal to the
verdict (`hit` is a separate key, and `evaluated`/`hit=False` is a real answer).
HERE, base==HEAD resolves to `not-established`, not to `evaluated` with a negative
verdict. The reason is what this record is FOR: it exists to support an issue close
or a release publish, and "I ran the probe and the behavior did not change" is not
weak support for such a claim -- it is no support at all, and the honest word for it
is that the claim was not established. Anyone reading `evaluated` here may assume the
measurement backs the claim, so `evaluated` is reserved for exactly that.

BLIND CLASS -- what this mechanism CANNOT see, stated before its first test:

- It never RUNS anything. It reads captured observables. A record whose base and head
  values were transcribed rather than measured is indistinguishable from one that was
  measured, and no field here can close that; the distinct observer reading the record
  against the source is the countermeasure, not this code.
- Verbatim verification proves the quoted text is PRESENT in the cited source, never
  that it is the RIGHT text. A quote lifted from an unrelated part of the same file
  passes. So does a correct quote paired with a stimulus that does not follow from it.
- It cannot judge whether `observable` is the observable the claim actually rests on.
  That is the whole of the `#628` refutation and it stays rung-2 human judgment --
  this module only forces the observable to be NAMED, so a reviewer has something
  specific to disagree with.
- A non-local source (a GitHub issue body, a URL) cannot be read here at all. The
  record can only record that it was unresolvable and carry the degraded reason,
  mirroring `evaluate_source_preservation`'s third form.
- Call-site coverage is SELF-REPORTED. This module refuses silence on the question and
  reports the answer; it does not enumerate call sites itself.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from runtime_bootstrap import import_repo_module

_boundary_probe = import_repo_module(__file__, "scripts.boundary_probe_lib")

# Borrowed, not respelled. See the module docstring's vocabulary note.
PROBE_EVALUATED = _boundary_probe.PROBE_EVALUATED
PROBE_NOT_CONFIGURED = _boundary_probe.PROBE_NOT_CONFIGURED
PROBE_NOT_ESTABLISHED = _boundary_probe.PROBE_NOT_ESTABLISHED

# The base arms. Open Question 1 of the goal that produced this module asked whether a
# base/HEAD rule survives a base that does not build and a fix that is a new file with
# no base at all. It does, but only once the arms are named and dispositioned SEPARATELY
# -- collapsing them is how "base and HEAD differ" gets satisfied by a base that merely
# crashed.
BASE_OBSERVED = "base-observed"
BASE_ABSENT = "base-absent"
BASE_UNRUNNABLE = "base-unrunnable"
BASE_NOT_APPLICABLE = "base-not-applicable"
BASE_ARMS = (BASE_OBSERVED, BASE_ABSENT, BASE_UNRUNNABLE, BASE_NOT_APPLICABLE)

# The claim kinds. The arm alone does not decide the outcome: `base-absent` establishes
# an EXISTENCE claim ("this surface now refuses") and cannot establish a CHANGE claim
# ("this behavior changed"), because there was no prior behavior to change.
CLAIM_CHANGE = "change"
CLAIM_EXISTENCE = "existence"
CLAIM_REFUSAL = "refusal"
CLAIM_KINDS = (CLAIM_CHANGE, CLAIM_EXISTENCE, CLAIM_REFUSAL)

# Field lines every record carries. `Call sites unproven:` is required rather than
# optional ON PURPOSE: the census's stated blind class is that it classifies FILES, not
# call sites, and a row flipped on one guarded site while a second still substitutes a
# default is a refutation this repo has already shipped once. An absent field is the
# silence that hid it, so absence is refused and the literal `none` is the way to say
# there are none.
REQUIRED_FIELDS = (
    "claim",
    "claim_kind",
    "observable",
    "source_ref",
    "source_conditions",
    "base_ref",
    "head_ref",
    "base_arm",
    "call_sites_unproven",
)
# Fenced sections. `stimulus` and `source_text` are verbatim by contract; the two
# observable blocks are the measurement.
REQUIRED_SECTIONS = ("source_text", "stimulus")

_FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?(?P<key>[A-Za-z][A-Za-z0-9 _-]*?)\s*:\s*(?P<value>.*?)\s*$")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<title>.+?)\s*$")
_FENCE_RE = re.compile(r"^\s*(?P<fence>```+|~~~+)\s*\S*\s*$")
_PLACEHOLDER_RE = re.compile(r"^(?:tbd|todo|n/?a|none|-+|\.+|\?+)$", re.IGNORECASE)
# A source ref that names a path this repo can open. `path::node_id` is pytest's form
# and `path:line` the editor form; both keep only the path for reading.
_LOCAL_REF_RE = re.compile(r"^(?P<path>[^\s:]+(?:/[^\s:]+)*\.[A-Za-z0-9_]+)(?:::|:)?")
_NONLOCAL_REF_RE = re.compile(r"^(?:https?://|issue[:# ]|#\d)", re.IGNORECASE)
# "there are no unproven call sites" -- ANCHORED to the leading token and required to be
# followed by a terminator or a separator, mirroring `issue_closeout_rung1_floors`'
# `_HOTL_STATUS_LEAD`. A bare `== "none"` looks equivalent and is worse in both
# directions: it rejects `none - only one call site exists`, which is a BETTER answer
# than the bare word and would train authors to drop the reason; and an unanchored
# search over the same word would accept `none of the call sites were checked`, which
# is the negation. The separator requirement is what splits those two apart -- `none of`
# continues a noun phrase, `none —` introduces a reason.
_NO_UNPROVEN_SITES_RE = re.compile(r"^none\s*(?:[—–:;.,-]|$)", re.IGNORECASE)


def _normalize_key(raw: str) -> str:
    return re.sub(r"[ -]+", "_", raw.strip().strip("`*").lower())


def _substantive(value: object) -> bool:
    """A value that says something. Mirrors the closeout floors' `_has_substantive_value`
    rather than importing it: those live in a public skill that must not depend on
    repo-internal `scripts/`, and the dependency direction here is the reverse one."""
    text = str(value or "").strip().strip("`*").strip()
    return bool(text) and not _PLACEHOLDER_RE.match(text)


def parse_probe_record(text: str) -> dict:
    """Split a probe record into its ``Key: value`` fields and its fenced sections.

    Field lines are read only OUTSIDE fences, so a `Claim:` line quoted inside a
    stimulus block is the stimulus, not the record's claim. Sections are keyed by the
    heading above the fence, normalized the same way field keys are, and a heading with
    no fence under it yields an empty section rather than being dropped -- the
    difference between "the author wrote nothing" and "the author wrote no heading" is
    exactly what the required-section check needs to see.
    """
    fields: dict[str, str] = {}
    sections: dict[str, str] = {}
    # `filled` and not `heading not in sections`: the heading line SEEDS the key with an
    # empty string so a fenceless heading is visibly empty, which means membership can no
    # longer answer "has this section received content" -- and using it for both silently
    # dropped every fence body.
    filled: set[str] = set()
    last_key: str | None = None
    heading: str | None = None
    fence: str | None = None
    buffer: list[str] = []
    for line in text.splitlines():
        if fence is not None:
            if line.strip().startswith(fence):
                if heading is not None and heading not in filled:
                    sections[heading] = "\n".join(buffer)
                    filled.add(heading)
                fence = None
                buffer = []
            else:
                buffer.append(line)
            continue
        if match := _FENCE_RE.match(line):
            fence = match.group("fence")[:3]
            buffer = []
            last_key = None
            continue
        if match := _HEADING_RE.match(line):
            heading = _normalize_key(match.group("title"))
            sections.setdefault(heading, "")
            last_key = None
            continue
        if match := _FIELD_RE.match(line):
            key = _normalize_key(match.group("key"))
            fields.setdefault(key, match.group("value").strip())
            last_key = key
            continue
        # INDENTED CONTINUATION. Field values here are prose that cites paths and node
        # ids, and the markdown gate wraps long lines -- so without this, a value that
        # had to wrap is silently stored as its first line and the record reports a
        # truncated claim under a passing verdict. That exact loss is a lesson this repo
        # already paid for three round-trips on a different line-anchored carrier.
        # Indentation is the signal, so an ordinary following paragraph cannot be
        # swallowed, and a blank line ends the value.
        if not line.strip():
            last_key = None
            continue
        if last_key is not None and line[:1].isspace():
            fields[last_key] = f"{fields[last_key]} {line.strip()}".strip()
    return {"fields": fields, "sections": sections}


def _normalized_lines(text: str) -> list[str]:
    """Non-empty lines, each stripped. Indentation and blank-line differences between a
    record and its source are formatting; the WORDS are what `verbatim` protects."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def _contains_block(haystack: list[str], needle: list[str]) -> bool:
    if not needle:
        return False
    return any(
        haystack[index : index + len(needle)] == needle
        for index in range(len(haystack) - len(needle) + 1)
    )


def _read_source(repo_root: Path, rel: str, revision: str | None) -> tuple[str | None, str | None]:
    """``(body, error)`` for one source, from the worktree or from a pinned revision.

    Pinning exists because the most quotable sources here are LIVING documents. A record
    that quotes `docs/handoff.md` verifies today and reads `absent` the next time anyone
    edits that file -- and the record would then be reporting a provenance failure for a
    repair that was fine, which trains readers to ignore the signal. `Source revision:`
    makes the frozen target explicit and visible in the record instead of implicit in
    whenever the check happened to run.
    """
    if revision:
        try:
            done = subprocess.run(
                ["git", "show", f"{revision}:{rel}"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:  # pragma: no cover - git absent from PATH
            return None, f"could not run git to read `{rel}` at `{revision}`: {exc}"
        if done.returncode != 0:
            return None, f"could not read `{rel}` at revision `{revision}`: {done.stderr.strip()}"
        return done.stdout, None
    try:
        return (repo_root / rel).read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"could not read `{rel}`: {exc}"


def verify_source_quote(
    repo_root: Path, source_ref: str, source_text: str, *, revision: str | None = None
) -> dict:
    """Is the quoted source text actually present in the cited source?

    This is the `#528` countermeasure at its own level. A stimulus invented from the
    agent's model of a mechanism cannot be quoted from the source that defines it: a
    vocabulary that is a mapping does not yield a list to copy. Checking the QUOTE
    rather than the stimulus is deliberate -- the stimulus is derived and the derivation
    is judgment, but the quote is either in the file or it is not.

    Returns ``status`` of ``verified`` / ``absent`` / ``unresolvable``, never a bare
    bool: `unresolvable` (a GitHub issue body, a URL) is not a failure and must not
    render as one, but it is not a verification either, and the record owes a degraded
    reason for it exactly as `evaluate_source_preservation` requires.
    """
    ref = (source_ref or "").strip().strip("`")
    if not ref or not _substantive(source_text):
        return {"status": "unresolvable", "reason": "no source ref or no quoted source text", "path": None}
    if _NONLOCAL_REF_RE.match(ref):
        return {"status": "unresolvable", "reason": f"`{ref}` is not a path this repo can open", "path": None}
    match = _LOCAL_REF_RE.match(ref)
    if match is None:
        return {"status": "unresolvable", "reason": f"`{ref}` does not name a readable path", "path": None}
    rel = match.group("path")
    body, error = _read_source(repo_root, rel, revision)
    if error is not None:
        return {"status": "unresolvable", "reason": error, "path": rel}
    if _contains_block(_normalized_lines(body), _normalized_lines(source_text)):
        return {"status": "verified", "reason": None, "path": rel}
    return {
        "status": "absent",
        "reason": f"the quoted source text does not appear in `{rel}`",
        "path": rel,
    }


def _missing_fields(fields: dict[str, str], sections: dict[str, str]) -> list[str]:
    missing = [name for name in REQUIRED_FIELDS if not _substantive(fields.get(name))]
    # `Call sites unproven: none` is a real answer, so the placeholder filter above --
    # which treats a bare `none` as silence everywhere else -- must not fire on it.
    if "call_sites_unproven" in missing and (fields.get("call_sites_unproven") or "").strip():
        missing.remove("call_sites_unproven")
    missing += [f"{name} (section)" for name in REQUIRED_SECTIONS if not _substantive(sections.get(name))]
    return missing


def _base_arm_outcome(arm: str, claim_kind: str, base: str, head: str) -> tuple[bool, str | None]:
    """``(established, reason_when_not)`` for one base arm and claim kind.

    Every arm's disposition is written here rather than inferred, because the failure
    this module exists to prevent is precisely an arm silently borrowing another arm's
    verdict.
    """
    if arm == BASE_UNRUNNABLE:
        # The sharpest rule in the module. A base that CRASHED also "differs from HEAD",
        # and accepting that difference is how `#528` measured an unfixed baseline and
        # called it a fix. A base that could not run is not a base that disagreed.
        return False, (
            "the probe could not run at base, so the pre-change behavior was never observed; "
            "a base that could not run is not a base that disagreed"
        )
    if arm == BASE_ABSENT:
        if claim_kind == CLAIM_EXISTENCE:
            return True, None
        return False, (
            f"claim kind `{claim_kind}` asserts a behavior CHANGED, but the surface does not exist "
            "at base, so there is no prior behavior for the change to be measured against; only an "
            f"`{CLAIM_EXISTENCE}` claim is established by an absent base"
        )
    if arm == BASE_OBSERVED:
        if not _substantive(base) or not _substantive(head):
            return False, (
                "base arm `base-observed` claims both readings were taken, but the "
                "`Base observable` / `Head observable` section is empty"
            )
        if _normalized_lines(base) == _normalized_lines(head):
            return False, (
                "base and HEAD agree on the bound observable, so the probe measured nothing "
                "about this claim"
            )
        return True, None
    if arm == BASE_NOT_APPLICABLE:
        # Reached only on a record that claims BEHAVIOR while declaring no base applies.
        # `resolve_probe_record` routes a `refusal` claim away before it gets here, so
        # this arm on any other claim kind is the escape hatch it looks like.
        return False, (
            f"base arm `{BASE_NOT_APPLICABLE}` is reserved for a `{CLAIM_REFUSAL}` claim; a claim "
            f"kind of `{claim_kind or '(unset)'}` asserts behavior and owes a base reading"
        )
    return False, f"unknown base arm `{arm}`; expected one of {', '.join(BASE_ARMS)}"


def resolve_probe_record(record: dict, *, repo_root: Path) -> dict:
    """Render a parsed probe record's typed outcome.

    Order matters and is not cosmetic: a record missing required fields is refused
    BEFORE its base arm is read, so an incomplete record can never reach `evaluated` by
    having a lucky arm. Every reason the record failed is collected rather than
    short-circuited, because an author fixing one at a time is the round-trip cost this
    whole mechanism is supposed to remove.
    """
    fields = record.get("fields", {})
    sections = record.get("sections", {})
    reasons: list[str] = []
    claim_kind = (fields.get("claim_kind") or "").strip().strip("`").lower()
    arm = (fields.get("base_arm") or "").strip().strip("`").lower()
    unproven = (fields.get("call_sites_unproven") or "").strip()
    covers_all_call_sites = bool(_NO_UNPROVEN_SITES_RE.match(unproven.strip("`*").strip()))

    if missing := _missing_fields(fields, sections):
        reasons.append("the record is incomplete; missing: " + ", ".join(f"`{name}`" for name in missing))
    if claim_kind and claim_kind not in CLAIM_KINDS:
        reasons.append(f"unknown claim kind `{claim_kind}`; expected one of {', '.join(CLAIM_KINDS)}")

    quote = verify_source_quote(
        repo_root,
        fields.get("source_ref", ""),
        sections.get("source_text", ""),
        revision=(fields.get("source_revision") or "").strip().strip("`") or None,
    )
    if quote["status"] == "absent":
        reasons.append(f"stimulus provenance is unverified: {quote['reason']}")
    elif quote["status"] == "unresolvable" and not _substantive(fields.get("source_degraded_reason")):
        reasons.append(
            f"the cited source could not be read here ({quote['reason']}) and the record carries no "
            "`Source degraded reason:`, so nothing states why the quote is unverifiable"
        )

    # A recorded refusal makes NO behavioral claim, so no probe applies to it. It resolves
    # `not-configured` -- the vocabulary's word for "there is genuinely no question here" --
    # and never `evaluated`, so it cannot be read as support for a flip it never claimed.
    if claim_kind == CLAIM_REFUSAL:
        if not _substantive(fields.get("refusal_reason")):
            reasons.append(
                "claim kind `refusal` records that the row cannot be wired, and owes a "
                "`Refusal reason:` saying why; without it the refusal is undocumented"
            )
        state = PROBE_NOT_CONFIGURED if not reasons else PROBE_NOT_ESTABLISHED
        if state == PROBE_NOT_CONFIGURED:
            reasons.append(
                "this record makes no behavioral claim, so no base/HEAD measurement applies; "
                "it is a recorded refusal and is NOT evidence of a repair"
            )
        return _result(state, reasons, quote, arm, claim_kind, covers_all_call_sites, unproven)

    established, arm_reason = _base_arm_outcome(
        arm, claim_kind, sections.get("base_observable", ""), sections.get("head_observable", "")
    )
    if arm_reason:
        reasons.append(arm_reason)
    state = PROBE_EVALUATED if (established and not reasons) else PROBE_NOT_ESTABLISHED
    return _result(state, reasons, quote, arm, claim_kind, covers_all_call_sites, unproven)


def _result(
    state: str,
    reasons: list[str],
    quote: dict,
    arm: str,
    claim_kind: str,
    covers_all_call_sites: bool,
    call_sites_unproven: str,
) -> dict:
    """Every return built once, so no branch can omit a key a consumer branches on --
    the same reason `boundary_probe_lib._probe_state` exists."""
    return {
        "state": state,
        "supports_claim": state == PROBE_EVALUATED,
        "undetermined_reasons": list(reasons),
        "source_quote": quote,
        "base_arm": arm,
        "claim_kind": claim_kind,
        "covers_all_call_sites": covers_all_call_sites,
        "call_sites_unproven": call_sites_unproven,
    }


def resolve_probe_record_text(text: str, *, repo_root: Path) -> dict:
    """`parse_probe_record` then `resolve_probe_record`, for the common one-file case."""
    return resolve_probe_record(parse_probe_record(text), repo_root=repo_root)
