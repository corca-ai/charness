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

Blind class: this reads the resolver's ERROR STRINGS. It cannot see a consumer that
never calls it, it says nothing about any other adapter error, and it is coupled to
`validate_adapter_version`'s message wording -- which is why
`tests/quality_gates/test_adapter_version_refusal_is_loud.py` drives the real check
rather than asserting these literals against themselves.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

__all__ = ["version_refused", "unspeakable_version_message", "refuse_unspeakable_version"]

# The wording `validate_adapter_version` emits. A prefix rather than an equality set
# because the supported version is interpolated (`version must be 1`), and a `field=`
# override renames the whole message. Pinned against the real check by the driving test
# named in the module docstring, so a reworded refusal fails there rather than silently
# turning every consumer guard below into a no-op.
_REFUSAL_PREFIXES = ("version must be", "version is required")


def version_refused(errors: Any) -> bool:
    """True when this reader could not speak the adapter's declared version."""
    if not isinstance(errors, list):
        return False
    return any(
        isinstance(error, str) and error.startswith(_REFUSAL_PREFIXES) for error in errors
    )


def unspeakable_version_message(
    load_adapter: Callable[[Path], dict], repo_root: Path, *, adapter_name: str
) -> str | None:
    """The refusal a consumer must render, or None when the version was speakable.

    Returns a message rather than raising so each caller keeps its own error type and
    exit path -- these consumers span `ValidationError`, `WriteError` and bare `exit 1`,
    and routing them through one exception here would put an artifact-rule hint on a
    failure that is not an artifact rule violation.

    An unreadable adapter answers None: whatever is wrong with it is not a version this
    reader refused, and the caller's own discovery already reports it. Swallowing the
    loader failure matches `resolve_adapter_line_budget`, which runs the resolver of the
    repo UNDER validation and must render a verdict rather than a traceback.
    """
    try:
        errors = load_adapter(repo_root).get("errors")
    except Exception:  # noqa: BLE001 - a verdict, never a traceback; see docstring
        return None
    if not version_refused(errors):
        return None
    return (
        f"`.agents/{adapter_name}` declares a `version` this reader does not speak "
        f"({'; '.join(error for error in errors if isinstance(error, str))}). "
        "Nothing the adapter declares is being honored, so this run would fall back to "
        "charness defaults rather than to what the repo declared -- refusing instead. "
        "Set `version: 1`, or upgrade the reader, then re-run."
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
