#!/usr/bin/env python3

"""Consumer-side reading of an adapter's version verdict.

`adapter_lib.declared_fields_after_version_check` is the PRODUCER half: a reader that
cannot speak an adapter's `version` honors none of its declared fields, so the resolved
payload is the reader's inferred defaults. That containment is only half a contract. The
other half lives here, because the surfaces that ACT on a resolved payload -- the ones
that scope a gate to an artifact directory, enforce a size ceiling, or write a durable
record -- deliberately do not key on the payload's `valid` flag, for the reason
`validate_debug_artifact._adapter_output_dir` records: a typo'd `repo` must not disarm a
refusal while `output_dir` is perfectly good.

`valid` is the wrong predicate for that job and a REFUSED VERSION is the right one. They
are different questions: `valid: false` can mean one bad field beside fifteen honored
ones, while a refused version means the reader honored NOTHING the repo declared -- a
state this module detects through the ERROR and WARNING channels a resolver reports. Every
public resolver reports both since `#673`; before it, five reported neither. Acting
on the defaults in that state is what turned a legible refusal into a silent one --
measured, not theorised: with `version: 9` and a declared `output_dir`, the retro
validator scoped itself to a directory the repo does not write to and reported
`Validated 0 retro artifact(s).` exit 0 over an explicitly named artifact, and the debug
gate enforced its shipped 180-line ceiling over a repo that had declared 60.

So a consumer that resolves scope, a ceiling, or a write path from an adapter asks this
module first and REFUSES. Falling back to a charness default is not the conservative arm
when the repo declared something else; it is a charness-chosen answer wearing the repo's
name.

TWO error states put a reader in that condition, not one, and keying on only the first
was measured as an escape rather than argued. A version this reader cannot speak is the
first. The second is an adapter the parser REFUSES outright: `simple_skill_adapter_lib`
returns `data=infer_repo_defaults(...)` with `errors=[parse_failure_error(exc)]`, which
is the same "nothing declared is honored" state reached by a different door. A round-1
bounded review found `version: !!int 9` -- one token added to the very input the
version guard refuses -- walking straight past this module, and the pre-repair harm was
reproduced on three release CLIs at exit 0. Round 2 found the first repair applied HERE
and not at the three consumers that ask the predicate directly, where the same input
wrote two durable files to a directory the repo never named; `unhonored_cause` and
`unhonored_remedy` exist so a caller can widen without hand-rolling the branch. So this module's predicate is the CONDITION,
not the wording of one check that detects it.

Blind class: this reads the resolver's ERROR STRINGS. It cannot see a consumer that
never calls it, it says nothing about any other adapter error, and it is coupled to
`validate_adapter_version`'s and `parse_failure_error`'s message wording -- which is why
`tests/quality_gates/test_adapter_version_refusal_is_loud.py` drives the real check
rather than asserting these literals against themselves.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

__all__ = [
    "version_refused",
    "parse_refused",
    "declarations_dropped",
    "declarations_unhonored",
    "unhonored_cause",
    "unhonored_remedy",
    "unspeakable_version_message",
    "refuse_unspeakable_version",
    "UNINTERPRETED_WARNING_MARKER",
]

# The wording `validate_adapter_version` emits. A prefix rather than an equality set
# because the supported version is interpolated into `version must be {supported}`.
#
# BLIND SPOT, stated because an earlier draft of this comment cited it as a REASON for
# the prefix and it is nothing of the kind: a `field=` override defeats prefix matching
# exactly as it defeats equality. `field="schema_version"` emits `schema_version must be
# 1`, which starts with neither entry, and `worktree_doctor_lib`'s `manifest.` prefix has
# the same effect. No call site of the shared check passes `field=` today, and the one
# real renamer is listed as exempt in the reconciliation census -- but a future caller
# that does would turn every consumer guard here into a silent no-op. That limit is
# pinned as an assertion in the driving test rather than left as prose.
#
# Substring matching would cover the rename and was rejected: `tool_version must be a
# string` already exists in this repo's vocabulary, and widening to catch a hypothetical
# renamer at the cost of matching real unrelated errors trades a silent no-op for a
# spurious refusal, which is the worse direction for a guard that stops a run.
_REFUSAL_PREFIXES = ("version must be", "version is required")

# `adapter_lib.parse_failure_error`'s wording. Its own docstring is the argument for
# treating it as this module's second door: "A refusal is not a drop and must not read
# like one." A parser refusal leaves the resolver returning `infer_repo_defaults(...)` --
# the same state a refused version leaves -- so a consumer acting on that payload is
# acting on charness defaults with the repo's name on them.
_PARSE_FAILURE_PREFIX = "adapter could not be parsed:"

# `adapter_lib.UNINTERPRETED_WARNING_MARKER`, duplicated as a literal rather than imported
# because this module is loaded by skill scripts that reach `scripts.` through a runtime
# bootstrap and by repo scripts that import it directly; a hard dependency here would make
# the consumer guard fail to load in the layout where it matters most. The literal is
# pinned against the producer by `test_adapter_version_refusal_is_loud.py`.
#
# THE THIRD DOOR, and the one this module denied having. A round-2 bounded review measured
# it: `adapter_lib._parse_block` silently drops an over-indented line, and the resolvers
# that route through `simple_skill_adapter_lib` record that in WARNINGS, not errors -- so a
# predicate over `errors` alone answers False while `errors: []`, `valid: True`, and the
# repo's declaration is gone. Measured on the real CLI at `9fc1164db`, with the guard
# installed: `survey_verification` printed `adapter_valid: true` beside `tool_checks: []`,
# exit 0. That is WORSE than the pre-guard base, which at least printed `false`.
#
# Only the uninterpreted-line warnings count. Widening to `unreadable_reasons`, which also
# returns every ERROR, would refuse an adapter that is merely invalid in an ordinary way --
# the polarity this module's docstring exists to forbid.
_UNINTERPRETED_WARNING_MARKER = " was not interpreted ("
# PUBLIC, because a consumer that renders its own dropped-line message needs the marker to
# quote the evidence and a round-2 review found `resolve_artifact_path` hardcoding a fifth
# copy. Exported rather than re-duplicated: this module already owns the literal for the
# reason above it, and one more private copy is one more place for the wording to drift.
UNINTERPRETED_WARNING_MARKER = _UNINTERPRETED_WARNING_MARKER


def version_refused(errors: Any) -> bool:
    """True when this reader could not speak the adapter's declared version."""
    return _any_error_starting_with(errors, _REFUSAL_PREFIXES)


def parse_refused(errors: Any) -> bool:
    """True when the parser refused the adapter document outright."""
    return _any_error_starting_with(errors, (_PARSE_FAILURE_PREFIX,))


def declarations_dropped(adapter: Any) -> bool:
    """True when the loader silently DISCARDED a line the repo wrote.

    Takes the whole payload, not `errors`, because the evidence lives in `warnings`.

    CLOSED. Five resolvers used to call `adapter_lib.load_yaml_file` bare and discard that
    sink, so this answered False for them and their consumers kept a blind arm. `#673`
    routed all five through `adapter_lib.read_declared_adapter`; the door is reachable for
    all sixteen and `tests/quality_gates/test_every_resolver_answers_a_refused_document.py`
    asserts it per resolver rather than in prose.
    """
    if not isinstance(adapter, dict):
        return False
    warnings = adapter.get("warnings")
    if not isinstance(warnings, list):
        return False
    return any(
        isinstance(warning, str) and _UNINTERPRETED_WARNING_MARKER in warning
        for warning in warnings
    )


def declarations_unhonored(errors: Any) -> bool:
    """True when the reader honored NOTHING the repo declared.

    `version_refused` and `parse_refused` are two doors into that state; a caller wanting
    the state should ask this rather than either door, so a door added later does not
    silently bypass every guard.

    NOT A BICONDITIONAL, and an earlier draft of this docstring read like one. This is a
    predicate over `errors` ONLY. A declaration the parser silently DROPPED leaves
    `errors: []` and is invisible here -- that is `declarations_dropped`, which reads
    `warnings`, and the two are deliberately separate because only the caller with the
    whole payload can ask the second. Both are reachable for all sixteen resolvers since
    `#673`; before it, five discarded the warning sink and neither predicate could see a
    dropped line there at all.
    """
    return version_refused(errors) or parse_refused(errors)


def unhonored_cause(errors: Any) -> str:
    """The clause naming WHICH door, for a caller that writes its own sentence.

    Round 2 of the slice-5 review found the round-1 repair applied to this module and not
    to the three consumers that ask the predicate directly and phrase their own refusal.
    Those refusals all said "declares a `version` this reader does not speak", which is
    the wrong instruction for a document the parser never read. This exists so a caller
    can widen its predicate without hand-rolling that branch -- and so the two wordings
    have one owner rather than four.
    """
    return "could not be parsed" if parse_refused(errors) else (
        "declares a `version` this reader does not speak"
    )


def unhonored_remedy(errors: Any, adapter_name: str) -> str:
    """The matching fix instruction for `unhonored_cause`."""
    return (
        f"Fix the YAML in `.agents/{adapter_name}` so the document parses, then re-run."
        if parse_refused(errors)
        else f"Set `version: 1` in `.agents/{adapter_name}` and re-run."
    )


def _any_error_starting_with(errors: Any, prefixes: tuple[str, ...]) -> bool:
    if not isinstance(errors, list):
        return False
    return any(isinstance(error, str) and error.startswith(prefixes) for error in errors)


def unspeakable_version_message(
    load_adapter: Callable[[Path], dict], repo_root: Path, *, adapter_name: str
) -> str | None:
    """The refusal a consumer must render, or None when the version was speakable.

    Returns a message rather than raising so each caller keeps its own error type and
    exit path -- these consumers span `ValidationError`, `WriteError` and bare `exit 1`,
    and routing them through one exception here would put an artifact-rule hint on a
    failure that is not an artifact rule violation.

    Named for the first of the two doors and kept that way because seven consumers call
    it under this name and four more call `refuse_unspeakable_version`; it answers `declarations_unhonored`, which is the condition. The
    message BRANCHES, because the remediation differs: one is an adapter line, the other
    is a YAML document the parser would not read at all.

    A loader that RAISES still answers None, and the justification an earlier draft gave
    for that -- "the former produced no payload for anyone to act on" -- was FALSE and is
    corrected here rather than deleted. The raise stopped the GUARD, not the CALLER:
    `validate_quality_artifact` called `refuse_unspeakable_version`, got None because the
    quality resolver raised, and then CONTINUED to resolve its own `output_dir` from
    charness defaults. That was a live exit-0 bypass, and `#673` closed it by making the
    resolver return instead of raise.

    The swallow arm stays, matching `resolve_adapter_line_budget`, which runs the resolver
    of the repo UNDER validation and must render a verdict rather than a traceback. Its
    remaining reach is UNMEASURED, and the scope of that statement matters: no
    `skills/public/*/scripts/resolve_adapter.py` raises on a refused parse now, but the
    loaders actually HANDED to this function are repo scripts and skill-local callables, and
    `#673` made one of those (`resolve_artifact_path.load_adapter`) raise. It does not reach
    this arm only because it raises `SystemExit`, a `BaseException`. A future change making
    that guard raise an ordinary exception would silently activate the swallow arm at a
    write surface.

    An earlier draft of this docstring justified answering None on a recorded parse
    failure with "the caller's own discovery already reports it". A bounded review
    measured that clause false: of the five release/hitl consumers guarded here, only
    `current_release` echoes `adapter["errors"]` at all, and echoing while acting on the
    defaults is the "a read is not a check" shape those consumers exist to stop.
    """
    try:
        adapter = load_adapter(repo_root)
    except Exception:  # noqa: BLE001 - a verdict, never a traceback; see docstring
        return None
    errors = adapter.get("errors") if isinstance(adapter, dict) else None
    if declarations_dropped(adapter) and not declarations_unhonored(errors):
        dropped = "; ".join(
            warning
            for warning in adapter.get("warnings", [])
            if isinstance(warning, str) and _UNINTERPRETED_WARNING_MARKER in warning
        )
        return (
            f"`.agents/{adapter_name}` has lines this reader could not interpret, so what "
            f"they declared is serving an inferred default instead ({dropped}). Refusing "
            "rather than acting on a charness default wearing this repo's name. Fix the "
            "indentation or the syntax on those lines, then re-run."
        )
    if not declarations_unhonored(errors):
        return None
    detail = "; ".join(error for error in errors if isinstance(error, str))
    # THROUGH THE HELPERS, so "one owner rather than four" is true rather than aspirational.
    # A round-2 review measured that it was not: this function inlined its own copies and
    # they DIFFERED from `unhonored_remedy` -- the parse door omitted the adapter path, the
    # version door added "or upgrade the reader" -- so the same input got a different
    # instruction depending on which entrypoint a consumer used. Two owners in one module.
    lead = f"`.agents/{adapter_name}` {unhonored_cause(errors)} ({detail})."
    fix = unhonored_remedy(errors, adapter_name)
    return (
        f"{lead} Nothing the adapter declares is being honored, so this run would fall "
        f"back to charness defaults rather than to what the repo declared -- refusing "
        f"instead. {fix}"
    )


def refuse_unspeakable_version(
    load_adapter: Callable[[Path], dict], repo_root: Path, *, adapter_name: str
) -> int | None:
    """Print the refusal and return an exit code, or None when the version is speakable.

    The `main()`-shaped half of `unspeakable_version_message`, for the validators that
    own their own entrypoint rather than going through
    `run_changed_artifact_validator`'s `preflight` hook. Extracted because two of them
    wrote the identical five-line block and a duplication gate caught it -- which is the
    right outcome: this is one decision (refuse, say why, exit non-zero), and two copies
    of it are two places for the wording and the exit code to drift apart.

    Returns `1` rather than raising, because a version refusal is not an artifact rule
    violation: routing it through a `ValidationError` handler would append the "start
    from the owning scaffold" hint, advising a stub rewrite when the fix is one adapter
    line.
    """
    message = unspeakable_version_message(load_adapter, repo_root, adapter_name=adapter_name)
    if message is None:
        return None
    print(message, file=sys.stderr)
    return 1
