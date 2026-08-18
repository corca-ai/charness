#!/usr/bin/env python3
"""The rung-1 floors a release close-issue boundary must clear.

Split from ``release_issue_closeout`` on the same concept boundary the issue skill
already drew between ``issue_verify_closeout_body`` and ``issue_closeout_rung1_floors``:
that module answers "how does a release close a linked issue" -- authorization, carrier
draft, state readback, the irreversible call -- and this one answers "what must the close
CARRY, and which floor refuses when it does not".

Two floors live here, one rung apart. ``evaluate_release_behavioral_verdict`` refuses
SILENCE about behavior. ``evaluate_release_probe_record`` refuses a claim that outran its
measurement: a publish is where such a claim escapes to users, and ``Behavior #N:
confirmed via X`` reads identically whether the probe measured a fix or measured nothing.
The second is triggered BY THE FIRST's content -- an issue whose behavior line records a
typed non-verified disposition asserts no measurement and owes no record.

Both release entrypoints call it. That is not redundancy: ``release_issue_closeout``'s
own comment records that ``ensure_release_issues_closed`` reaches ``gh issue close``
directly and that resume/recovery can invoke it with no preflight in the process.
Guarding only the preflight would leave one of two entrypoints to an irreversible
boundary unguarded -- the third of the three 2026-08-18 refutations, reproduced in the
wiring of its own countermeasure.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

# Every release-linked issue close is by definition a user-facing behavior claim, so the
# classification gate is force-applied rather than read from an issue type -- mirroring
# `release_issue_closeout._RELEASE_BEHAVIORAL_CLASSIFICATION`, whose reasoning this
# inherits verbatim.
_RELEASE_BEHAVIORAL_CLASSIFICATION = "feature"


def _package_root(script_path: Path) -> tuple[Path, bool]:
    parts = script_path.parts
    for index in range(len(parts) - 3):
        if parts[index : index + 4] == ("skills", "public", "release", "scripts"):
            return Path(*parts[:index]), False
    for index in range(len(parts) - 2):
        if parts[index : index + 3] == ("skills", "release", "scripts"):
            return Path(*parts[:index]), True
    raise ImportError(f"cannot resolve release package root for {script_path}")


def _load_issue_skill_module(filename: str, alias: str):
    """Load one module from the ISSUE skill, from either layout, without modifying it.

    One parameterized loader rather than one per target: the first cut wrote
    `_load_issue_closeout_body_lib` and `_load_probe_floor` out longhand and the duplicate
    ratchet flagged them immediately -- correctly, because two copies of the
    source-tree/installed candidate ORDER are two answers to "where is the issue skill"
    that can drift apart, which is precisely what having a single owner was for.

    Mirrors `handoff/scripts/draft_goal_from_chunk._load_goal_artifact_lib`, this repo's
    established cross-skill import pattern. Returns ``None`` when the module is absent;
    the two callers differ in what they do about that, and that difference is theirs.
    """
    here = Path(__file__).resolve()
    package_root, installed_first = _package_root(here)
    rels = (
        Path(f"skills/issue/scripts/{filename}"),
        Path(f"skills/public/issue/scripts/{filename}"),
    )
    if not installed_first:
        rels = tuple(reversed(rels))
    for rel in rels:
        candidate = package_root / rel
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location(alias, candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None


def _load_issue_closeout_body_lib():
    """The issue skill's rung-1 floor helper. RAISES on absence, because a release close
    cannot proceed without the floor it mirrors, and the module-level binding below turns
    that raise into a recorded error rather than an import crash."""
    module = _load_issue_skill_module(
        "issue_closeout_rung1_floors.py", "release_issue_closeout_rung1_floors"
    )
    if module is None:
        raise ImportError(
            "issue skill issue_closeout_rung1_floors.py not found in source-tree "
            "skills/public/issue/scripts or installed skills/issue/scripts layout"
        )
    return module


try:
    _ISSUE_CLOSEOUT_BODY = _load_issue_closeout_body_lib()
    _ISSUE_CLOSEOUT_BODY_ERROR: str | None = None
except Exception as exc:  # pragma: no cover - defensive: a partial install
    _ISSUE_CLOSEOUT_BODY = None
    _ISSUE_CLOSEOUT_BODY_ERROR = str(exc)


def _issue_closeout_body():
    """The issue skill's rung-1 floor helper, or ``None`` on an install without it.

    ONE owner for cross-skill resolution. This module and `release_issue_closeout` briefly
    had a copy each -- the split's first shape -- which is two answers to "where is the
    issue skill" that can disagree on exactly the install where it matters.
    """
    return _ISSUE_CLOSEOUT_BODY


_PROBE_FLOOR_UNLOADED = object()
_PROBE_FLOOR_CACHE: object = _PROBE_FLOOR_UNLOADED


def _load_probe_floor():
    """The issue skill's PROBE-RECORD floor, or ``None``. Absence becomes a REFUSAL naming
    what to install, never a pass: a publish is an irreversible boundary where a traceback
    reads as a broken tool rather than as a check that did not run.

    CACHED, for the second time in this slice and for the same two reasons: re-executing
    the module per call is wasteful, and it makes the floor UNPATCHABLE -- every caller got
    a fresh copy, so the severity read by `release_probe_record_blocks` and the severity
    read a line later by the floor itself came from different module objects. A test that
    armed one of them was silently testing nothing, which is how this was found.
    """
    global _PROBE_FLOOR_CACHE
    if _PROBE_FLOOR_CACHE is _PROBE_FLOOR_UNLOADED:
        _PROBE_FLOOR_CACHE = _load_issue_skill_module(
            "issue_probe_record_floor.py", "release_issue_probe_record_floor"
        )
    return _PROBE_FLOOR_CACHE


def evaluate_release_probe_record(
    behavior_lines: list[str],
    probe_lines: list[str],
    issue_numbers: list[int],
    repo_root: Path,
) -> dict[str, Any]:
    """Rung-1 floor: a release-linked issue close whose behavioral verdict CLAIMS a
    verification names a probe record that established it.

    Mirrors `evaluate_release_behavioral_verdict` onto the same boundary, one rung deeper.
    That floor refuses SILENCE about behavior; this one refuses a claim that outran its
    measurement -- a publish is where such a claim escapes to users, and `Behavior #N:
    confirmed via X` reads identically whether the probe measured a fix or measured
    nothing.

    Both line sets are passed because the OBLIGATION IS TRIGGERED BY THE CLAIM: an issue
    whose behavior line records a typed non-verified disposition asserts no measurement and
    owes no record.
    """
    if not issue_numbers:
        return {"applies": False, "ok": True, "missing": []}
    floor = _load_probe_floor()
    if floor is None:
        return {
            "applies": True,
            "ok": False,
            "missing": list(issue_numbers),
            "failed": [],
            "records": [],
            "library_unavailable": (
                "the issue skill's issue_probe_record_floor.py was not found on this install, so "
                "no probe record can be read. Vendor/install the `issue` skill alongside `release`, "
                "or drop --close-issue from this publish."
            ),
        }
    return floor.evaluate_probe_record(
        "\n".join(list(behavior_lines) + list(probe_lines)),
        _RELEASE_BEHAVIORAL_CLASSIFICATION,
        issue_numbers,
        repo_root=repo_root,
    )


def release_probe_record_blocks() -> bool:
    """Whether a failing probe-record floor vetoes a publish.

    Read from the ISSUE skill's floor rather than restated, so the two boundaries cannot
    drift apart on severity. When the issue floor is absent the answer is False -- absence
    already produces a refusal payload with `library_unavailable`, and a second refusal
    keyed on a severity nobody could read would be a guess.
    """
    floor = _load_probe_floor()
    return bool(floor is not None and floor.probe_record_blocks())


def fail_release_probe_record_floor(verdict: dict[str, Any]) -> None:
    floor = _load_probe_floor()
    detail = "\n".join(floor.probe_record_problems(verdict)) if floor is not None else str(verdict)
    raise SystemExit(
        "release issue closeout refused: a behavioral verdict claims a verification that no "
        "probe record establishes.\n"
        f"{detail}\n"
        'pass `--close-issue-probe-record "Probe record #<N>: <path-to-record>"` naming a record '
        "that resolves `evaluated`, or a typed disposition saying why no probe applies "
        "(repeat per issue). A publish is an irreversible boundary: this floor refuses rather "
        "than letting a claim reach users on a measurement nobody can read."
    )


def evaluate_release_behavioral_verdict(behavior_lines: list[str], issue_numbers: list[int]) -> dict[str, Any]:
    """Rung-1 presence floor (P5): mirrors the issue skill's own
    ``evaluate_behavioral_verdict`` onto the release close-issue boundary. A
    `Behavior #N: <...>` line (or the single-issue `Behavior: <...>` shorthand)
    naming a distinct evidence channel, or a typed non-`verified` disposition,
    satisfies it EQUALLY (F2a) -- it refuses *silence* only. Whether the named
    channel is genuinely distinct is the fresh-eye release closeout reviewer's
    judgment (rung-2), never this floor's.
    """
    if not issue_numbers:
        return {"applies": False, "ok": True, "missing": []}
    body_floors = _issue_closeout_body()
    if body_floors is None:
        raise SystemExit(
            "release --close-issue requires the issue skill's "
            "issue_closeout_rung1_floors.py (the behavioral-verdict floor helper), but it was "
            "not found on this install.\n"
            "vendor/install the `issue` skill alongside `release` on this host, or drop "
            "--close-issue from this publish."
        )
    return body_floors.evaluate_behavioral_verdict(
        "\n".join(behavior_lines), _RELEASE_BEHAVIORAL_CLASSIFICATION, issue_numbers
    )



def fail_release_behavioral_verdict_floor(verdict: dict[str, Any]) -> None:
    # floor-addition-restraint: mirrors the issue skill's existing rung-1
    # behavioral-verdict presence floor onto the release close-issue boundary
    # (counterweight-verified north-star finding: release closeout bypassed it
    # entirely). Presence-only -- no new authored surface beyond the
    # `--close-issue-behavior` CLI flag this floor reads.
    raise SystemExit(
        "release issue closeout refused: missing per-issue behavioral-verdict line.\n"
        f"issues without a `Behavior #N:` line (or typed non-verified disposition): {verdict.get('missing')}\n"
        'pass `--close-issue-behavior "Behavior #<N>: <distinct-channel or disposition>"` '
        "(repeat per issue; the single-issue shorthand `Behavior: <...>` also matches) "
        "before release closes a linked issue."
    )
