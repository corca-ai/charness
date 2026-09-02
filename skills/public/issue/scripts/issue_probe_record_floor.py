#!/usr/bin/env python3
"""Rung-1 floor: a behavioral close names a probe record, and that record ESTABLISHED
its claim.

The sibling floors in ``issue_closeout_rung1_floors`` refuse silence about behavior --
``Behavior #N:`` must say SOMETHING per closed issue. They cannot refuse a claim that
outran its measurement, because a bare ``Behavior #12: verified via the CLI`` renders
identically whether the probe measured a fix or measured nothing at all.

THE INVARIANT: a close may not assert a verification that no measurement supports. The
failure mode it answers is a stimulus drawn from the author's MODEL of the mechanism
rather than from the source that defines the claim -- an invented shape measures the
unfixed baseline, and the "verified" that results is indistinguishable from a real one.

WHY THIS IS A SEPARATE MODULE. ``issue_closeout_rung1_floors``'s docstring states it
never imports repo-internal ``scripts/``, and that property is worth keeping intact.
This floor MUST read ``scripts.evidence.probe_record_lib`` -- the record's grammar and its typed
outcome live there and must not be respelled. ``issue_resolution_critique`` is the
precedent for a sibling that reaches a repo module; this follows it rather than eroding
the neighbour's stated property.

STILL RUNG-1, AND THE LINE IS NARROWER THAN IT LOOKS. This floor checks that a record is
NAMED and that it resolves ``evaluated``. It does not judge whether the quoted stimulus
is the right one, whether the named observable is the one the claim rests on, or whether
the captured readings were measured rather than transcribed -- ``probe_record_lib``'s
blind class enumerates all of that, and the record carries a ``residual_judgment`` list
so the rung-2 reviewer is handed those questions rather than having to reconstruct them.

THE CONSUMER RULE IS INVERTED FROM ITS SIBLING'S, AND THE SHARED VOCABULARY IS EXACTLY
WHAT WOULD MAKE THAT GO WRONG. ``boundary_probe_lib`` uses the same three words and its
own comment warns callers NOT to key on ``state != PROBE_EVALUATED``, because there
``evaluated``/``hit=False`` is a real answer. A probe record inverts that deliberately:
``evaluated`` is reserved for "the measurement backs the claim", so this floor keys on
``state != evaluated`` and nothing else.
"""
from __future__ import annotations

import re
import runpy
from pathlib import Path
from types import SimpleNamespace

_load_local = runpy.run_path(
    str(Path(__file__).resolve().parent / "issue_local_import.py")
)["sibling_loader"](__file__)
_BODY = _load_local("issue_verify_closeout_body")
_strip_code_fences = _BODY._strip_code_fences
_has_substantive_value = _BODY._has_substantive_value
_FLOORS = _load_local("issue_closeout_rung1_floors")

# The same reason, genuinely: a probe record measures USER-FACING BEHAVIOR, and a
# classification with no behavior to confirm has nothing to probe. Release closeout is
# the remaining consumer of this classification gate.
PROBE_RECORD_CLASSIFICATIONS = _FLOORS.BEHAVIORAL_VERDICT_CLASSIFICATIONS

# ``Probe record #N: <path-or-disposition>``, single-issue shorthand ``Probe record:``.
# Mirrors the ``Behavior #N:`` / ``HOTL #N:`` grammar so a carrier author writes one shape.
_PROBE_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?Probe record(?:\s+(?P<target>[^:]+?))?\s*:\s*(?P<value>.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
_ISSUE_REF_RE = re.compile(r"#(\d+)\b")
# A close that CANNOT carry a probe says so in a typed word instead of naming a record.
# Mirrors the sibling HOTL vocabulary rather than inventing a second one, anchored to the
# leading token for the reason that module already records: an unanchored search over the
# same words accepts a status's own negation.
_DISPOSITION_LEAD = re.compile(
    r"(?i)^(?:blocked-needs-(?:operator|capability)|deferred-by-operator|accepted-risk"
    r"|out-of-scope|local-only-by-contract|no-behavior-change)\b"
)
_VALUE_LEAD = re.compile(r"^[ \t\-\*>`]+")
# The subset of `_DISPOSITION_LEAD` that asserts a probe was IMPOSSIBLE, as opposed to
# unnecessary. Only these contradict a verification claim.
_IMPOSSIBILITY_LEAD = re.compile(
    r"(?i)^(?:blocked-needs-(?:operator|capability)|no-behavior-change)\b"
)


def _load_probe_record_lib() -> SimpleNamespace | None:
    """``scripts.evidence.probe_record_lib``, or ``None`` when this tree does not ship it.

    Resolved through the skill runtime bootstrap, which returns the repo root in an
    authoring tree and ``plugins/<package>`` in an installed one, so the same call finds
    the mirrored copy either side. ``None`` rather than a raise: the caller turns an
    unresolvable library into a legible REFUSAL, which is the honest outcome, where a
    traceback at a closeout boundary reads as a broken tool.
    """
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:  # pragma: no cover - defensive broken-install layout
        return None
    try:
        runtime = SimpleNamespace(**runpy.run_path(str(bootstrap)))
        return runtime.load_repo_module_from_skill_script(__file__, "scripts.evidence.probe_record_lib")
    except Exception:  # pragma: no cover - a tree without the repo module
        return None



# The HOTL vocabulary MINUS `verified`, plus the shapes that defer rather than confirm.
# A `Behavior #N:` value leading with one of these CLAIMS NOTHING about a measurement, so
# it owes no record; anything else -- `verified via ...`, or a bare channel name -- is a
# verification claim and owes one.
# The typed non-verifying statuses. Each must be followed by a terminator or a separator,
# NOT by more sentence: without that, `out-of-scope drift aside, verified via CLI` leads
# with a typed token and reads as a non-claim.
_NON_VERIFYING_LEAD = re.compile(
    r"(?i)^(?:blocked-needs-(?:operator|capability)|deferred-by-operator|accepted-risk"
    r"|out-of-scope|local-only-by-contract|no-behavior-change|not-verified)\b\s*(?:[-—–:;.,]|$)"
)
# `issue`/`issues` is the one status whose bare token is also an ordinary English word, so
# it must carry the tracker ref its own contract requires -- the sibling
# `issue_closeout_rung1_floors` splits it into its own regex plus a `_ISSUE_REF` conjunct
# and SAYS SO, and mirroring it as a flat alternant silently dropped the conjunct. Measured:
# `Behavior #42: issues with the stale cache are gone; confirmed via a fresh checkout`
# led with `issues`, owed nothing, and closed with an unbacked verification claim.
_DEFER_TO_ISSUE_LEAD = re.compile(r"(?i)^(?:issues?\b|#\d)")


def _numbers_claiming_verification(text: str, numbers: list[int]) -> list[int]:
    """The closed issues whose `Behavior #N:` line CLAIMS a verification.

    THE OBLIGATION ATTACHES TO THE CLAIM, NOT TO THE CLASSIFICATION, which is the whole
    thesis: a verdict may not claim more than its probe measured. A close that honestly
    records `blocked-needs-operator` or `local-only-by-contract` asserts no measurement and
    is owed nothing; a close that says `verified via the CLI` asserts one and owes the
    record that shows what was measured.

    Gating on classification instead would tax every honest non-verifying close for a
    claim it never made, and would leave the mechanism looking like a tollbooth rather
    than a consequence of what the carrier said.

    An issue with NO behavior line at all is owed nothing HERE -- the sibling
    behavioral-verdict floor already refuses that silence, and two floors reporting the
    same missing line is how a failure report starts double-counting.
    """
    claiming: list[int] = []
    for line in _FLOORS._behavior_lines(text):
        if not _has_substantive_value(line["value"]):
            continue
        if not _claims_verification(line["value"]):
            continue
        claiming.extend(n for n in _bound_targets(line, numbers) if n not in claiming)
    return claiming



def _claims_verification(value: str) -> bool:
    """Does this `Behavior #N:` value ASSERT a measurement?

    False for a typed non-verifying status, and for a defer that carries its tracker ref.
    True for everything else -- including a bare channel name, which is what most carriers
    write. Defaulting to True is the safe direction: an unrecognised value is a claim until
    it says otherwise.
    """
    cleaned = _VALUE_LEAD.sub("", value.strip()).strip().strip("*`").strip()
    if _NON_VERIFYING_LEAD.match(cleaned):
        return False
    return not (_DEFER_TO_ISSUE_LEAD.match(cleaned) and _ISSUE_REF_RE.search(cleaned))


def _bound_targets(line: dict, numbers: list[int]) -> list[int]:
    """Which closed issues this line speaks for.

    ONE rule, called by both readers. Written out twice first, and the duplicate ratchet
    flagged the two copies inside this one file -- rightly, because the single-issue
    shorthand fallback is exactly the kind of rule that gets fixed in one copy.
    A line targeting no closed issue speaks for none: a quoted or copied entry for another
    issue is not this carrier's disposition.
    """
    targets = [number for number in line["target_numbers"] if number in numbers]
    if not targets and line["target"] is None and len(numbers) == 1:
        targets = [numbers[0]]
    return targets

def _probe_lines(text: str) -> list[dict]:
    plain = "\n".join(_strip_code_fences(text))
    lines: list[dict] = []
    for match in _PROBE_LINE_RE.finditer(plain):
        target = (match.group("target") or "").strip()
        lines.append(
            {
                "target": target or None,
                "value": match.group("value").strip(),
                "target_numbers": [int(raw) for raw in _ISSUE_REF_RE.findall(target)],
            }
        )
    return lines


def _dispositioned(value: str) -> bool:
    cleaned = _VALUE_LEAD.sub("", value.strip()).strip().strip("*`").strip()
    return bool(_DISPOSITION_LEAD.match(cleaned))


def _resolve_named_record(repo_root: Path, value: str, library) -> dict:
    """Read the record this line names and report whether it establishes its claim."""
    rel = value.strip().strip("`").strip()
    record_path = (repo_root / rel) if not Path(rel).is_absolute() else Path(rel)
    try:
        text = record_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "ok": False,
            "state": library.PROBE_NOT_ESTABLISHED,
            "path": rel,
            "reasons": [f"the named probe record could not be read: {exc}"],
            "residual_judgment": [],
        }
    result = library.resolve_probe_record_text(text, repo_root=repo_root)
    return {
        # KEYED ON THE STATE, never on `supports_claim` alone, and never on the sibling
        # `boundary_probe_lib`'s `hit`. See the module docstring's inverted-rule note.
        "ok": result["state"] == library.PROBE_EVALUATED,
        "state": result["state"],
        "path": rel,
        "reasons": list(result["undetermined_reasons"]),
        "residual_judgment": list(result["residual_judgment"]),
    }


def evaluate_probe_record(
    text: str,
    classification: str,
    numbers: list[int],
    *,
    repo_root: Path,
) -> dict:
    """Rung-1 floor: every behaviorally-closed issue names a probe record that ESTABLISHED
    its claim, or carries a typed disposition saying why no probe applies.

    Refuses three things, and nothing else:

    - SILENCE. A ``bug``/``feature``/``deferred-work`` close with no ``Probe record #N:``
      line for an issue fails. This is the half the goal's acceptance names: a carrier
      missing the field must refuse, not merely be encouraged.
    - A record that did NOT establish its claim. ``not-established`` and
      ``not-configured`` both fail, carrying the record's own reasons so the author is
      told which question went unanswered rather than that "the floor failed".
    - An UNTYPED escape. A value that is neither a readable record nor a typed
      disposition is undispositioned and fails closed.

    A typed disposition satisfies this floor exactly as a record does, because a close
    that genuinely cannot be probed must remain closeable -- the sibling behavioral-verdict
    floor takes the same position for the same reason. Whether the disposition is HONEST is
    the rung-2 resolution critique's judgment, never this floor's.
    """
    if classification not in PROBE_RECORD_CLASSIFICATIONS:
        return {
            "applies": False,
            "ok": True,
            "missing": [],
            "failed": [],
            "records": [],
            "skipped_classification": classification,
        }
    library = _load_probe_record_lib()
    if library is None:
        return {
            "applies": True,
            "ok": False,
            "missing": list(numbers),
            "failed": [],
            "records": [],
            "library_unavailable": (
                "`scripts/evidence/probe_record_lib.py` could not be resolved from this tree, so no "
                "named probe record can be read. This floor refuses rather than passing: a "
                "check that cannot run has not run, and reporting it as satisfied is the "
                "class of silence this floor exists to close."
            ),
        }
    owing = _numbers_claiming_verification(text, numbers)
    bound: set[int] = set()
    failed: list[dict] = []
    records: list[dict] = []
    for line in _probe_lines(text):
        if not _has_substantive_value(line["value"]):
            continue
        targets = _bound_targets(line, numbers)
        if not targets:
            continue
        if _dispositioned(line["value"]):
            # A DISPOSITION THAT ASSERTS IMPOSSIBILITY CANNOT SIT BESIDE A CLAIM.
            # `Behavior #42: confirmed via the CLI` with `Probe record #42:
            # blocked-needs-operator` says "I measured this" and "measuring was impossible"
            # at once; one of the two is false and the floor refuses rather than picking.
            #
            # `local-only-by-contract` is deliberately NOT in that set: it says the
            # verification happened locally and the contract accepts local, which is
            # coherent with a claim rather than a contradiction of it. That leaves it as a
            # one-line escape from producing a record, which is REAL and is reported --
            # `claim_rests_on: disposition` travels with the result so the rung-2 reviewer
            # is handed the closes whose claim rests on a word rather than a measurement,
            # instead of having to find them. Whether such a disposition is honest is that
            # reviewer's judgment; it was never this floor's.
            contradicts = (
                [number for number in targets if number in owing]
                if _IMPOSSIBILITY_LEAD.match(
                    _VALUE_LEAD.sub("", line["value"].strip()).strip().strip("*`").strip()
                )
                else []
            )
            entry = {
                "targets": targets,
                "value": line["value"],
                "disposition": True,
                "ok": not contradicts,
                "reasons": [] if not contradicts else [
                    "the behavioral verdict for "
                    + ", ".join(f"#{number}" for number in contradicts)
                    + " CLAIMS a verification while this line says no probe applies. Put the "
                    "disposition on the `Behavior #N:` line instead, or name a record that "
                    "establishes the claim"
                ],
                "state": "contradicted",
            }
        else:
            resolved = _resolve_named_record(repo_root, line["value"], library)
            entry = {"targets": targets, "value": line["value"], "disposition": False, **resolved}
        records.append(entry)
        if entry["ok"]:
            bound.update(targets)
        else:
            failed.append(entry)
    # An issue whose line was PRESENT but did not satisfy the floor is `failed`, never
    # `missing`. Counting it as both made the report say "has no `Probe record #N:` line"
    # about a line the author can see in the carrier -- a false statement in a refusal, and
    # the fastest way to teach a reader that the floor's messages cannot be trusted.
    attempted = {number for entry in failed for number in entry["targets"]}
    missing = [number for number in owing if number not in bound and number not in attempted]
    return {
        "applies": True,
        "ok": not missing and not failed,
        "missing": missing,
        "failed": failed,
        "records": records,
        "classification": classification,
        "owing": owing,
        "not_owing": [number for number in numbers if number not in owing],
        # The closes whose verification claim is backed by a WORD, not a record. Reported
        # because the escape is real and cheap: without this the rung-2 reviewer would have
        # to find them, and a reviewer who has to go looking is a reviewer who will not.
        "claim_rests_on_disposition": sorted(
            {
                number
                for entry in records
                if entry.get("disposition")
                for number in entry["targets"]
                if number in owing
            }
        ),
    }


# SEVERITY, in ONE place so the flip is one edit rather than a hunt.
#
# `review` by operator ruling (2026-08-18): the floor was built blocking, as the goal's
# acceptance specifies, and migrating the existing suite to it measured the cost at 67
# tests across 15 files plus a standing obligation on every verification-claiming close.
# The operator chose to hold it at REVIEW severity until slice 5 reports what a probe
# record actually costs across 45 real rows -- a mechanism with one worked example is how
# this repo has repeatedly shipped rules that did not survive their second case.
#
# What REVIEW means here, precisely: the floor still EVALUATES, still resolves the named
# record, and still reports everything it found. It does not veto the close. Flipping this
# to `block` is the whole change; every carrier reads it rather than deciding for itself,
# so they cannot disagree about severity the way three earlier floors disagreed about
# which carriers they reached.
PROBE_RECORD_SEVERITY = "review"


def probe_record_blocks() -> bool:
    """True when a failing probe-record floor should veto the close."""
    return PROBE_RECORD_SEVERITY == "block"


def probe_record_problem_fields(result: dict) -> list[str]:
    """The floor's findings as carrier problems -- EMPTY while it is advisory.

    The severity branch lives here rather than in each carrier. Written the other way
    first, and two things went wrong at once: every carrier grew an `if
    probe_record_blocks()` of its own (three copies of one decision, which is how three
    earlier floors came to disagree about which carriers they reached), and the guarded
    line was unreachable at REVIEW severity so the changed-line gate reported it uncovered
    -- correctly, since the flip after slice 5 would otherwise be the first time it ran.
    """
    return probe_record_problems(result) if probe_record_blocks() else []


def probe_record_advisory(result: dict) -> list[str]:
    """REVIEW-severity lines for a floor that found something and is not vetoing.

    Forces a question for whoever reads the close output, never fails the command --
    mirroring `review_advisory_for_classification`. Two distinct things get surfaced, and
    conflating them would hide the second: an unmet obligation, and a claim that IS met but
    rests on a typed disposition rather than on a measurement.
    """
    lines = [f"REVIEW: {problem}" for problem in probe_record_problems(result)]
    if resting := result.get("claim_rests_on_disposition"):
        refs = ", ".join(f"#{number}" for number in resting)
        lines.append(
            f"REVIEW: the behavioral verdict for {refs} claims a verification whose probe record "
            "is a typed disposition, not a measurement. That is permitted and is the cheap "
            "escape from producing a record; whether it is honest is this close's rung-2 "
            "judgment (advisory only, never blocks)."
        )
    return lines


def probe_record_problems(result: dict) -> list[str]:
    """The floor's findings as carrier-problem strings, one per unmet obligation.

    Rendered here rather than at each call site so the two carriers that run this floor
    cannot describe the same failure differently -- the drift the sibling module's own
    D36 note records paying for.
    """
    if result.get("ok", True) or not result.get("applies"):
        return []
    if unavailable := result.get("library_unavailable"):
        return [f"probe_record:{unavailable}"]
    problems = [
        f"probe_record:#{number} has no `Probe record #{number}:` line naming a record that "
        "established its claim, and no typed disposition saying why no probe applies"
        for number in result.get("missing", [])
    ]
    for entry in result.get("failed", []):
        targets = ", ".join(f"#{number}" for number in entry["targets"])
        detail = "; ".join(entry.get("reasons") or []) or "the value is neither a readable probe record nor a typed disposition"
        problems.append(
            f"probe_record:{targets} names `{entry['value']}`, which resolves "
            f"`{entry.get('state', 'undispositioned')}` rather than `evaluated`: {detail}"
        )
    return problems
