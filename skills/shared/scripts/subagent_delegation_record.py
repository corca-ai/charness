#!/usr/bin/env python3
"""Rung 2 of the bounded-review authorization ladder: the structured record.

The ladder itself lives in the sibling ``resolve_subagent_delegation.py``; this
module owns only the storage half — reading and writing
``<repo-root>/.agents/subagent-delegation.json``. The split is the concept
boundary: "where the grant is kept" is separable from "which rung answers".

The record is STRUCTURED rather than prose because the sibling defect this
ladder was built alongside was a literal compared against a bolded sentence: a
wording, an emphasis, or a line wrap must never decide whether a rule fires.

Everything here fails toward ``None`` (no decision), never toward a grant. A
caller that cannot read a decision must ask; a caller that reads a grant out of
a malformed file would let the plugin authorize its own spawns.
"""

from __future__ import annotations

import json
from pathlib import Path

RECORD_RELPATH = ".agents/subagent-delegation.json"
RECORD_VERSION = 1
DECISION_FIELD = "bounded_review_delegation"
GRANTED = "granted"
DECLINED = "declined"
RECORDABLE_DECISIONS = (GRANTED, DECLINED)

# The bounded reviewer scopes a rung-3 question must name, so the user is
# answering about concrete runs rather than an open-ended spawn licence.
CANONICAL_SCOPES = ("setup", "quality", "critique", "release", "issue")

_MAX_RECORD_BYTES = 64_000


class DelegationError(Exception):
    """A usage-level failure: bad arguments or a repo root that is not one."""


class RecordWriteError(Exception):
    """The answer could not be persisted. Distinct from a usage error on purpose.

    A caller that cannot tell these apart re-asks on the next slice believing it
    hit a typo, quietly breaking "asked at most once per repo".
    """


def read_text(path: Path) -> str | None:
    """Return file text, or None when absent or unreadable.

    Unreadable is NOT adopted. `is_file()` can pass on a file this process
    cannot read, and letting the OSError escape would surface as a traceback
    rather than as a resolved rung.
    """

    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def read_delegation_record(repo_root: Path) -> dict[str, object]:
    """Read the structured record in ONE parse.

    Returns `{"decision", "scopes", "provenance", "reason"}` with `decision` None
    whenever the file does not yield a recognized decision; `reason` always names
    why. Single-parse on purpose: an earlier version re-read and re-parsed the
    file for its scopes, so a concurrent write could pair the old decision with
    the new scope list.
    """

    def unreadable(reason: str) -> dict[str, object]:
        return {"decision": None, "scopes": None, "provenance": {}, "reason": reason}

    text = read_text(Path(repo_root) / RECORD_RELPATH)
    if text is None:
        return unreadable(f"no record at {RECORD_RELPATH}")
    if len(text.encode("utf-8")) > _MAX_RECORD_BYTES:
        return unreadable(f"{RECORD_RELPATH} exceeds {_MAX_RECORD_BYTES} bytes; not read as a decision")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return unreadable(f"{RECORD_RELPATH} is not valid JSON ({exc.msg}); resolving to ask")
    if not isinstance(data, dict):
        return unreadable(f"{RECORD_RELPATH} is not a JSON object; resolving to ask")
    raw = data.get(DECISION_FIELD)
    if not isinstance(raw, str):
        return unreadable(f"{RECORD_RELPATH} has no string `{DECISION_FIELD}` field; resolving to ask")
    decision = raw.strip().lower()
    if decision not in RECORDABLE_DECISIONS:
        return unreadable(
            f"{RECORD_RELPATH} `{DECISION_FIELD}` value `{raw[:40]}` is not one of "
            f"{RECORDABLE_DECISIONS}; resolving to ask"
        )
    # A `scopes` key that is present but not a non-empty list of strings makes the
    # record unreadable rather than defaulting to every canonical scope. Defaulting
    # widened the grant exactly when the author had tried to narrow it: an empty
    # list, a bare string, or a list of objects all collapsed to "all five".
    scopes: list[str] | None = None
    if "scopes" in data:
        raw_scopes = data.get("scopes")
        if not isinstance(raw_scopes, list) or not raw_scopes or not all(isinstance(s, str) for s in raw_scopes):
            return unreadable(
                f"{RECORD_RELPATH} has a `scopes` key that is not a non-empty list of strings; "
                "resolving to ask rather than widening the grant to every scope"
            )
        # Lowercased: `--scope` comparison is exact, so a record written
        # `["Critique"]` would silently downgrade a real grant to `ask` --
        # a capitalization deciding whether a rule fires, which is the exact
        # thing structured storage exists to prevent.
        scopes = [s.strip().lower() for s in raw_scopes]
    provenance = {
        key: data.get(key)
        for key in ("recorded_by", "recorded_on", "note", "version")
        if isinstance(data.get(key), (str, int))
    }
    return {
        "decision": decision,
        "scopes": scopes,
        "provenance": provenance,
        "reason": f"recorded in {RECORD_RELPATH}",
    }


def write_delegation_record(
    repo_root: Path,
    *,
    decision: str,
    scopes: list[str],
    recorded_on: str | None,
    note: str | None,
) -> dict[str, object]:
    """Persist a rung-3 answer into rung 2 so it is asked at most once per repo."""

    repo_root = Path(repo_root)
    if decision not in RECORDABLE_DECISIONS:
        raise DelegationError(f"--decision must be one of {RECORDABLE_DECISIONS}, got `{decision}`")
    if not repo_root.is_dir():
        # Without this, a typo'd or cwd-relative repo root silently CREATES the
        # whole path, reports success, and the answer lands where no later
        # resolve will look -- so the user is asked again and a stray dot
        # directory shows up as untracked drift.
        raise DelegationError(f"--repo-root `{repo_root}` is not an existing directory")
    if decision == GRANTED and not (note and note.strip()):
        raise DelegationError(
            "--note is required for `granted`: record the question the user actually answered, "
            "so a grant with no provenance is not indistinguishable from a self-grant"
        )
    path = repo_root / RECORD_RELPATH
    previous = read_delegation_record(repo_root)["decision"]
    payload: dict[str, object] = {
        "version": RECORD_VERSION,
        DECISION_FIELD: decision,
        "scopes": scopes or list(CANONICAL_SCOPES),
        "recorded_by": "user",
    }
    if recorded_on:
        payload["recorded_on"] = recorded_on
    if note:
        payload["note"] = note
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        tmp.replace(path)
    except OSError as exc:
        raise RecordWriteError(f"cannot write {path}: {exc}") from exc
    result: dict[str, object] = {"recorded": True, "path": str(path.resolve()), **payload}
    if previous is not None and previous != decision:
        # Silent clobber of the opposite answer is exactly the class this ladder
        # exists to stop; say what was replaced.
        result["replaced_decision"] = previous
    return result
