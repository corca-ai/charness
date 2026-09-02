#!/usr/bin/env python3
"""What makes a host settings entry *this* charness hook.

A host settings entry is `{"matcher": <pattern>, "hooks": [{type, command}, ...]}`.
Two independent questions decide what the installer and the status verdict may do
with one:

- **command identity** — is our hook in this entry at all, and does the entry also
  carry someone else's command? The matcher is per-ENTRY, so an entry shared with a
  foreign command is shared state that must not be rewritten.
- **matcher coverage** — will this entry still fire for the events our hook exists
  to catch? Coverage, not string equality: a widened or reordered matcher fires for
  everything we need, so calling it absent is a false refusal and "repairing" it
  silently deletes coverage the operator added.

Split out of `host_hook_install_lib` because both questions are pure predicates over
one settings entry, shared by the installer and the presence detector, and neither
needs the state file, the settings path, or any host I/O.
"""

from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import Any, Iterator

__all__ = [
    "entry_carries_foreign_command",
    "entries_match_command",
    "event_entry",
    "matcher_covers",
    "matcher_events",
]


def script_basename(command: str) -> str | None:
    """Return the `.py` basename used as a logical hook identity."""
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()
    for part in parts:
        if part.endswith(".py"):
            return Path(part).name
    return None


def event_entry(command: str, matcher: str = "") -> dict[str, Any]:
    return {
        "matcher": matcher,
        "hooks": [
            {
                "type": "command",
                "command": command,
            }
        ],
    }


def _entry_commands(entry: Any) -> Iterator[str]:
    """Every `type: command` command string in `entry`, skipping malformed items."""
    if not isinstance(entry, dict):
        return
    inner = entry.get("hooks")
    if not isinstance(inner, list):
        return
    for item in inner:
        if not (isinstance(item, dict) and item.get("type") == "command"):
            continue
        existing = item.get("command")
        if isinstance(existing, str):
            yield existing


def _is_same_hook(existing: str, command: str, target_identity: str | None) -> bool:
    """True when `existing` is our `command`, exactly or by logical identity.

    Logical identity is the `.py` script basename, so the same hook installed from a
    second checkout — different absolute path, same basename — is recognized as
    already present and not double-installed (corca-ai/charness#245). A foreign hook
    (no charness `.py` basename) only ever exact-matches, so it is never touched.
    """
    if existing == command:
        return True
    return target_identity is not None and script_basename(existing) == target_identity


def _entry_holds(entry: Any, command: str, *, ours: bool) -> bool:
    """True when `entry` holds at least one command whose our-hook-ness is `ours`."""
    target_identity = script_basename(command)
    return any(
        _is_same_hook(existing, command, target_identity) is ours
        for existing in _entry_commands(entry)
    )


def entries_match_command(entry: Any, command: str) -> bool:
    """True when `entry` already carries this charness hook."""
    return _entry_holds(entry, command, ours=True)


def entry_carries_foreign_command(entry: Any, command: str) -> bool:
    """True when `entry` groups some OTHER command alongside this charness hook.

    The host's own hooks UI groups several commands under one matcher, so that
    matcher is shared state: rewriting it would change when the foreign command
    fires.
    """
    return _entry_holds(entry, command, ours=False)


_PLAIN_EVENT = re.compile(r"^\w+$")


def matcher_events(matcher: Any) -> set[str] | None:
    """The event names a settings matcher fires for, or `None` when unbounded.

    `None` means "this matcher's coverage is not a set we can bound from below" —
    two different reasons, one answer:

    - an omitted or empty matcher is the host's match-all spelling, so it is not a
      narrower set, it is the absence of a restriction;
    - a matcher is a PATTERN, not a literal list. `*`, `.*`, `Edit.*` and
      `^(Edit|Write)$` all fire for things a literal split cannot enumerate, so
      treating their tokens as an event set would call a live hook inert.

    Only an all-plain-token alternation (`Edit|Write|MultiEdit`) is read as a set.
    """
    if not isinstance(matcher, str) or not matcher.strip():
        return None
    events = {part.strip() for part in matcher.split("|") if part.strip()}
    if not all(_PLAIN_EVENT.match(event) for event in events):
        return None
    return events


def matcher_covers(existing: Any, required: str) -> bool:
    """True when `existing` still fires for every event `required` names.

    Unbounded on either side answers True. That is deliberate: this predicate
    gates a rewrite of the operator's settings file, so the failure it must avoid
    is calling a firing hook absent and narrowing it. An `existing` we cannot
    bound is left exactly as the operator wrote it.
    """
    required_events = matcher_events(required)
    if required_events is None:
        return True
    existing_events = matcher_events(existing)
    if existing_events is None:
        return True
    return required_events <= existing_events
