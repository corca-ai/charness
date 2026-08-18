#!/usr/bin/env python3

"""Consumer-side reading of an adapter's version verdict.

`adapter_lib.declared_fields_after_version_check` is the PRODUCER half: a reader that
cannot speak an adapter's `version` honors none of its declared fields, so the resolved
payload is the reader's inferred defaults. That containment is only half a contract. The
other half lives here, because the surfaces that ACT on a resolved payload -- the ones
that scope a gate to an artifact directory, enforce a line ceiling, or write a durable
record -- deliberately do not key on the payload's `valid` flag, for the reason
`validate_debug_artifact._adapter_output_dir` records: a typo'd `repo` must not disarm a
refusal while `output_dir` is perfectly good.

`valid` is the wrong predicate for that job and a REFUSED VERSION is the right one. They
are different questions: `valid: false` can mean one bad field beside fifteen honored
ones, while a refused version means the reader honored NOTHING the repo declared. Acting
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
reproduced on three release CLIs at exit 0. So this module's predicate is the CONDITION,
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
    "declarations_unhonored",
    "unspeakable_version_message",
    "refuse_unspeakable_version",
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


def version_refused(errors: Any) -> bool:
    """True when this reader could not speak the adapter's declared version."""
    return _any_error_starting_with(errors, _REFUSAL_PREFIXES)


def parse_refused(errors: Any) -> bool:
    """True when the parser refused the adapter document outright."""
    return _any_error_starting_with(errors, (_PARSE_FAILURE_PREFIX,))


def declarations_unhonored(errors: Any) -> bool:
    """True when the reader honored NOTHING the repo declared.

    The predicate this module is actually about. `version_refused` and `parse_refused`
    are the two doors into that state; a caller wanting the state should ask this rather
    than either door, so a third door added later does not silently bypass every guard.
    """
    return version_refused(errors) or parse_refused(errors)


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

    Named for the first of the two doors and kept that way because fifteen consumers call
    it under this name; it answers `declarations_unhonored`, which is the condition. The
    message BRANCHES, because the remediation differs: one is an adapter line, the other
    is a YAML document the parser would not read at all.

    A loader that RAISES still answers None. That is a different thing from a parse
    failure recorded in `errors`: the resolver caught the latter and handed back defaults,
    which is the state this module refuses, while the former produced no payload for
    anyone to act on. Swallowing the raise matches `resolve_adapter_line_budget`, which
    runs the resolver of the repo UNDER validation and must render a verdict rather than
    a traceback.

    An earlier draft of this docstring justified answering None on a recorded parse
    failure with "the caller's own discovery already reports it". A bounded review
    measured that clause false: of the five release/hitl consumers guarded here, only
    `current_release` echoes `adapter["errors"]` at all, and echoing while acting on the
    defaults is the "a read is not a check" shape those consumers exist to stop.
    """
    try:
        errors = load_adapter(repo_root).get("errors")
    except Exception:  # noqa: BLE001 - a verdict, never a traceback; see docstring
        return None
    if not declarations_unhonored(errors):
        return None
    detail = "; ".join(error for error in errors if isinstance(error, str))
    lead = (
        f"`.agents/{adapter_name}` could not be parsed ({detail})."
        if parse_refused(errors)
        else (
            f"`.agents/{adapter_name}` declares a `version` this reader does not speak "
            f"({detail})."
        )
    )
    fix = (
        "Fix the YAML so the document parses, then re-run."
        if parse_refused(errors)
        else "Set `version: 1`, or upgrade the reader, then re-run."
    )
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
