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

BLIND CLASS -- what this mechanism CANNOT see. Two bounded review rounds rewrote this
list after measuring that its first version both over- and under-claimed; each bullet
below is a limit somebody demonstrated, not one that was reasoned about.

- It never RUNS anything. It reads captured observables. A record whose base and head
  values were transcribed rather than measured is indistinguishable from one that was
  measured, and no field here can close that; the distinct observer reading the record
  against the source is the countermeasure, not this code.
- Verbatim verification proves the quoted text is PRESENT in the cited source, never
  that it is the RIGHT text. A quote lifted from an unrelated part of the same file
  passes. So does a correct quote paired with a stimulus that does not follow from it
  -- which means the quote check is NOT `#528`'s countermeasure, however much it looks
  like one. `verify_source_quote` walks that through concretely; the base/HEAD arm rule
  is what catches `#528`.
- Matching preserves each block's RELATIVE indentation but drops blank lines, so a quote
  can still splice two paragraphs its source separates. Keeping blank lines would refuse
  a record that merely reflowed a quote, which is the more common author action.
- `Source conditions:` -- the field the goal's refutation table calls the `#628`
  countermeasure -- is compared to NOTHING. It is required to be present and substantive,
  and then a human reads it or nobody does. `#628` was probed under convenient conditions
  while the reported case stayed broken, and this module cannot tell those apart. It can
  only make the conditions sit beside the stimulus where a reviewer will notice. Nothing
  binds; the table overclaims and this bullet is the correction.
- It cannot judge whether `observable` is the observable the claim actually rests on.
  That is the other half of the `#628` refutation and it stays rung-2 human judgment --
  this module only forces the observable to be NAMED, so a reviewer has something
  specific to disagree with.
- A non-local source (a GitHub issue body, a URL) cannot be read here at all; it resolves
  `unresolvable` and owes a degraded reason, mirroring `evaluate_source_preservation`'s
  third form. `#628`'s own source is exactly this class, so the refutation the quote
  mechanism is named after lives outside that mechanism's reach. A source that merely
  FAILED to read -- a mistyped path, a bad revision pin -- is deliberately NOT covered by
  the degraded form, because gated that way the escape was cheaper than fixing the quote.
- Call-site coverage is SELF-REPORTED. This module does not enumerate call sites. It
  refuses silence on the question, and an unproven site now blocks the claim rather than
  being printed beside a green verdict -- but an author who writes `none` while two call
  sites exist is invisible here.
- It cannot distinguish a source that DEFINES a claim (shipped code, a spec, an issue
  body, a fixture) from one that merely REPORTS it (a handoff bullet, a prior retro).
  Quoting a claim out of the agent's own earlier prose satisfies every check here, which
  is a real hazard for a repo whose handoffs assert checkable facts.
- `evaluated` is not a terminal green. `_result` emits `RESIDUAL_JUDGMENT` alongside it
  precisely so the questions above travel with the pass instead of living only here.
"""

from __future__ import annotations

import re
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

_parse = import_repo_module(__file__, "scripts.probe_record_parse")

# Re-exported so the split stays an implementation detail: `probe_record_lib` remains the
# one import site for anything that reads or judges a record.
parse_probe_record = _parse.parse_probe_record
verify_source_quote = _parse.verify_source_quote
_normalized_lines = _parse._normalized_lines
_substantive = _parse._substantive
_contains_block = _parse._contains_block
_dedent = _parse._dedent
_NO_UNPROVEN_SITES_RE = _parse._NO_UNPROVEN_SITES_RE

# A capture that differs from the other arm ONLY by naming which arm it is. The repo's
# first worked example wrote `base  waited 10.0s -> ...` / `head  waited 12.1s -> ...`,
# which is a natural thing to paste and which makes the base==head rule unfalsifiable for
# every record that copies it. Stripped before comparing, so the label cannot manufacture
# a disagreement.
_ARM_LABEL_RE = re.compile(r"^(?:base|head)\b[\s:]*", re.IGNORECASE)

# What an `evaluated` record still has NOT settled. See `_result` for why these ride
# along with the pass rather than living only in this module's docstring.
RESIDUAL_JUDGMENT = (
    "the quoted source text is PRESENT in the cited source; whether it is the RIGHT text, "
    "and whether the stimulus follows from it, was not checked here",
    "`Source conditions:` is recorded for a reader to compare against the stimulus; nothing "
    "in this module compares them",
    "whether the named observable is the one the claim actually rests on is not decidable here",
    "the base and head readings are captured values; that they were measured rather than "
    "transcribed is not observable from the record",
)

def _missing_fields(fields: dict[str, str], sections: dict[str, str]) -> list[str]:
    missing = [name for name in REQUIRED_FIELDS if not _substantive(fields.get(name))]
    # `Call sites unproven: none` is a real answer, so the placeholder filter above --
    # which treats a bare `none` as silence everywhere else -- must not fire on it.
    #
    # The rescue is gated on the `none` grammar and NOT on mere non-emptiness. Written
    # the loose way it re-admitted the ENTIRE placeholder vocabulary through the one
    # field whose whole purpose is refusing silence: `Call sites unproven: TBD` was
    # measured resolving `evaluated`. A real list of sites is already substantive and
    # never reaches this branch, so the grammar is the only thing the rescue owes.
    if "call_sites_unproven" in missing and _NO_UNPROVEN_SITES_RE.match(
        (fields.get("call_sites_unproven") or "").strip("`*").strip()
    ):
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
    if arm not in (BASE_ABSENT, BASE_OBSERVED):
        # Fall through to the arm-identity refusals below. The captured-reading check
        # must NOT run first for these: `base-not-applicable` and a typo'd arm owe an
        # answer about the ARM, and reporting "your Head observable is empty" instead
        # would send the author to fix the wrong thing.
        if arm == BASE_NOT_APPLICABLE:
            # Reached only on a record that claims BEHAVIOR while declaring no base
            # applies. `resolve_probe_record` routes a `refusal` claim away before it
            # gets here, so this arm on any other claim kind is the escape hatch it
            # looks like.
            return False, (
                f"base arm `{BASE_NOT_APPLICABLE}` is reserved for a `{CLAIM_REFUSAL}` claim; a claim "
                f"kind of `{claim_kind or '(unset)'}` asserts behavior and owes a base reading"
            )
        return False, f"unknown base arm `{arm}`; expected one of {', '.join(BASE_ARMS)}"
    # BOTH remaining arms owe BOTH readings. This check used to live inside the
    # `base-observed` branch alone, and a bounded review measured the consequence: a
    # record declaring `base-absent` + `existence` with NO observable sections at all
    # resolved `evaluated` and exited 0 under `--require-evaluated`. Both fields are
    # author-chosen, so relabelling a change claim as an existence claim on an absent
    # base was a two-word bypass of the entire base/HEAD bar -- which is, per the goal's
    # own table, the actual `#528` countermeasure. An existence claim still owes a HEAD
    # reading: that reading IS the claim. An absent base still owes a base statement --
    # the evidence that the surface really is absent, not merely a declaration that it is.
    if not _substantive(head):
        return False, (
            f"base arm `{arm}` claims a HEAD reading was taken, but the `Head observable` section "
            "is empty; an evidence record with no captured observable is not populated"
        )
    if not _substantive(base):
        return False, (
            f"base arm `{arm}` owes a `Base observable` section stating what was read at base "
            f"(for `{BASE_ABSENT}`, the evidence that the surface is absent there)"
        )
    if arm == BASE_ABSENT:
        if claim_kind == CLAIM_EXISTENCE:
            return True, None
        return False, (
            f"claim kind `{claim_kind}` asserts a behavior CHANGED, but the surface does not exist "
            "at base, so there is no prior behavior for the change to be measured against; only an "
            f"`{CLAIM_EXISTENCE}` claim is established by an absent base"
        )
    # `base-observed` is what remains after the membership guard and the `base-absent`
    # branch, so it is the fall-through rather than a third `if` with an unreachable tail.
    if _observable_lines(base) == _observable_lines(head):
        return False, (
            "base and HEAD agree on the bound observable, so the probe measured nothing "
            "about this claim (compared with any leading `base`/`head` arm label removed, "
            "because a label is not a measurement)"
        )
    return True, None


def _observable_lines(text: str) -> list[str]:
    """A capture's lines with any leading `base`/`head` arm label removed.

    Without this the base==head rule is defeated by the most natural way to paste two
    captures -- prefixing each with which arm it came from. The repo's first worked
    example did exactly that, so the one exemplar every later record copies would have
    made the module's central rule unfalsifiable.
    """
    # EMPTIED LINES ARE DROPPED, not kept as `""`. `re.sub` replaces a whole-line label
    # with the empty string rather than removing the line, so a capture pasted WITH its
    # arm banner and the other retyped without one compared as `["", "exit 1"]` versus
    # `["exit 1"]` -- unequal, `evaluated`, on two readings that are identical once the
    # label is gone. The symmetric case the strip was written for worked; the asymmetric
    # paste, which is the likelier one, manufactured exactly the disagreement the strip
    # exists to prevent.
    return [stripped for line in _normalized_lines(text) if (stripped := _ARM_LABEL_RE.sub("", line))]


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
    if duplicated := record.get("duplicated_fields") or []:
        reasons.append(
            "the record states these fields more than once, so which value the verdict rests on is "
            "ambiguous: " + ", ".join(f"`{name}`" for name in duplicated)
        )
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
    elif quote["status"] == "unresolvable":
        # THE DEGRADED-REASON ESCAPE IS FOR A SOURCE THAT IS INHERENTLY UNREADABLE HERE
        # (a GitHub issue body, a URL) -- NOT for one this repo simply failed to open.
        # Gated on `unresolvable` alone it was an opt-out from the verbatim check, and a
        # strictly cheaper one than fixing the quote: a fabricated quote is refused, but
        # a fabricated quote plus a one-letter typo in the path was accepted, measured
        # resolving `evaluated`. A bad `Source revision:` pin bought the same exemption.
        # That is the relabel-instead-of-repair shape this goal exists to make visible,
        # reproduced inside the mechanism meant to prevent it.
        if not quote["local"]:
            if not _substantive(fields.get("source_degraded_reason")):
                reasons.append(
                    f"the cited source cannot be read from this repo ({quote['reason']}) and the record "
                    "carries no `Source degraded reason:`, so nothing states why the quote is unverifiable"
                )
        else:
            reasons.append(
                f"the cited source names a repo path that could not be read ({quote['reason']}). A "
                "`Source degraded reason:` does not cover this: the degraded form is for a source that "
                "is inherently unreadable here, not for one whose path or pin is wrong. Fix the ref"
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
        if arm != BASE_NOT_APPLICABLE:
            # The reservation runs both ways. `base-not-applicable` was already refused for
            # a behavioral claim; without this, a refusal could name any arm at all --
            # including a typo -- and the record would still resolve, reporting an arm
            # nothing had checked.
            reasons.append(
                f"claim kind `{CLAIM_REFUSAL}` owes base arm `{BASE_NOT_APPLICABLE}`, not "
                f"`{arm or '(unset)'}`: a refusal is precisely the case where no base reading applies"
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
    # AN UNPROVEN CALL SITE STOPS THE RECORD FROM SUPPORTING ITS CLAIM. It used to be
    # reported and ignored -- `covers_all_call_sites: false` sat in the output while the
    # state read `evaluated`, so a record HONESTLY naming a second, unprobed entrypoint
    # still exited 0 under `--require-evaluated`. That is the third 2026-08-18 refutation
    # replayed exactly: a close landing while one of two entrypoints is still broken.
    # Naming the site keeps the record COMPLETE, which is what Fixed Decision 5 asks for;
    # it does not make the claim ESTABLISHED, which is what the Behavioral Proof line
    # ("a row does not improve while an enumerated site is unproven") requires. Both
    # readings are satisfied by refusing here rather than at authoring time.
    if not covers_all_call_sites:
        reasons.append(
            f"call sites remain unproven ({unproven}), so this record does not establish the claim "
            "for the whole file; it is complete and honest about what it did not reach"
        )
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
        # EMITTED ON THE PASSING PATH, on purpose. The north star says there is no
        # terminal green, and this module mints a new one (`evaluated`) at exactly the
        # boundary where a wrong claim escapes. Every refusal here explains itself while
        # the pass returned nothing but the word, which is how `evaluated` would come to
        # mean "reviewed" instead of "measured". These are the questions the mechanism
        # structurally cannot answer, carried WITH the green so the distinct observer
        # reading the record is handed their agenda rather than having to reconstruct it.
        "residual_judgment": list(RESIDUAL_JUDGMENT) if state == PROBE_EVALUATED else [],
        "source_quote": quote,
        "base_arm": arm,
        "claim_kind": claim_kind,
        "covers_all_call_sites": covers_all_call_sites,
        "call_sites_unproven": call_sites_unproven,
    }


def demoted_result(result: dict, reasons: list[str]) -> dict:
    """``result`` demoted to `not-established`, with ``reasons`` appended -- built by `_result`.

    The third construction site this module's single-owner rule forbids was already being
    written when a round-2 bounded review caught it: `check_probe_record._merge_stimulus_replay`
    hand-set `state`, `supports_claim`, `undetermined_reasons` and `residual_judgment` in
    place, forty lines below the comment recording that a previous hand-rolled copy had
    drifted past `residual_judgment` and the `local` flag. The four values coincided with
    `_result`'s today, so nothing was wrong yet -- and that is exactly the state the earlier
    copy was in before it drifted. `_result` derives `supports_claim` and `residual_judgment`
    FROM `state`, so any fifth state-dependent key it grows would be stale on this path only.
    """
    return _result(
        PROBE_NOT_ESTABLISHED,
        list(result.get("undetermined_reasons") or []) + list(reasons),
        result.get("source_quote") or {},
        result.get("base_arm") or "",
        result.get("claim_kind") or "",
        bool(result.get("covers_all_call_sites")),
        result.get("call_sites_unproven") or "",
    )


def unreadable_record_result(reason: str) -> dict:
    """The result for a record that could not be read at all, built through `_result`.

    It lives here rather than at the CLI because `_result` exists so no branch can omit a
    key a consumer branches on -- and a SECOND, hand-rolled construction of the same shape
    defeats that exactly. The CLI's copy was written before `residual_judgment` and
    `source_quote["local"]` existed and silently never gained either, so a consumer written
    against the documented contract would raise `KeyError` on precisely the could-not-read
    path. One construction site is the only version of this guarantee that holds.
    """
    return _result(
        PROBE_NOT_ESTABLISHED,
        [reason],
        {"status": "unresolvable", "reason": reason, "path": None, "local": False},
        "",
        "",
        False,
        "",
    )


def resolve_probe_record_text(text: str, *, repo_root: Path) -> dict:
    """`parse_probe_record` then `resolve_probe_record`, for the common one-file case."""
    return resolve_probe_record(parse_probe_record(text), repo_root=repo_root)
