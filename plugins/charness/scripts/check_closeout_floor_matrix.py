#!/usr/bin/env python3
"""Refuse when the declared closeout floor matrix disagrees with observed behavior.

The declaration (`.agents/closeout-floor-matrix.json`) states,
for every `(carrier, classification, floor)`, whether that floor reaches the close
verdict. This gate re-derives the same grid by RUNNING each real closeout ingress
against a passing body and a one-floor-broken body (`closeout_floor_matrix_lib`) and
refuses on any disagreement, in either direction.

Totality is the point as much as agreement: a pair with no declaration, or a declared
pair the carriers no longer accept, refuses. Classifications are read live from
`issue_verify_closeout.CLASSIFICATIONS`, so adding a seventh disposition without
declaring its cells fails here rather than shipping unmeasured.

What this gate does NOT check: the prose in `reason`. The observation is binary
(fires / inert / input-refused); whether an inert floor is skipped-by-design or
not-applicable is declared judgment, and a wrong reason beside a right state passes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module

_LIB = import_repo_module(__file__, "scripts.closeout_floor_matrix_lib")
CARRIERS = _LIB.CARRIERS
FLOORS = _LIB.FLOORS
observe_matrix = _LIB.observe_matrix

MATRIX_REL = ".agents/closeout-floor-matrix.json"

# What each declared state commits to, in OBSERVED vocabulary. EVERY state pins
# exactly ONE observation. Round-1 review found the earlier `not-applicable` admitting
# both `inert` and `input-refused`, which made the six cells carrying this slice's
# central finding self-confirming: drop `hotl` from the consolidated disposition's
# repair-claim vocabulary and those cells slide `input-refused -> inert` -- a brand-new
# silent skip on the carrier that writes to GitHub -- with the gate still green and the
# cell's own "measured, not assumed" reason now false.
STATE_ALLOWS = {
    "fires": ("fires",),
    "skipped-by-design": ("inert",),
    "not-applicable": ("inert",),
    "input-refused": ("input-refused",),
    "undispositioned": ("inert",),
}
# `undispositioned` is the honest state for an inert floor nobody has justified. It
# must carry a `finding` -- a filed issue -- so the gap is tracked instead of resting
# in an advisory nobody reads, which is the shape `#586` was filed about. A cell that
# is inert with neither a reason nor a finding is a REFUSAL, not a default.
STATE_REQUIRES = {
    "skipped-by-design": "reason",
    "not-applicable": "reason",
    "input-refused": "reason",
    "undispositioned": "finding",
}
# A `finding` must be a filed issue, not a promise. `"finding": "later"` passed the
# non-empty test and tracked nothing.
FINDING_RE = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/issues/\d+")


def _problems(declared: dict, observed: dict) -> list[str]:
    problems: list[str] = []
    classifications = observed["classifications"]
    for key, missing in (
        ("classifications", set(classifications) ^ set(declared.get("classifications", []))),
        ("carriers", set(CARRIERS) ^ set(declared.get("carriers", []))),
        ("floors", set(FLOORS) ^ set(declared.get("floors", []))),
    ):
        if missing:
            problems.append(f"declared {key} disagree with the live axis: {sorted(missing)}")
    if problems:
        # Every pair key is built from these axes, so a mismatched axis would report
        # itself again once per pair. Stop at the axis.
        return problems

    declared_pairs = declared.get("pairs", {})
    expected = {f"{carrier}|{c}" for carrier in CARRIERS for c in classifications}
    for key in sorted(expected - set(declared_pairs)):
        problems.append(f"{key}: no declaration; an absent cell is a refusal, not a default")
    for key in sorted(set(declared_pairs) - expected):
        problems.append(f"{key}: declared but no such (carrier, classification) pair exists")
    for key in sorted(expected & set(declared_pairs)):
        problems.extend(_pair_problems(key, declared_pairs[key], observed["pairs"][key]))
    return problems


def _refused_pair_problems(key: str, declared: dict, observed: dict) -> list[str]:
    """A pair the carrier does not accept at all: no floor there is observable, so the
    only things to verify are that the declaration says WHY and names WHICH refusal."""
    problems: list[str] = []
    if not str(declared.get("reason", "")).strip():
        problems.append(f"{key}: a refused pair must declare why the carrier refuses it")
    if declared.get("floors"):
        problems.append(f"{key}: a refused pair has no observable floors; drop its cells")
    # Without this, a refused pair is verified only by the word "refused" -- and since
    # `run_ingress` renders any raise as a refusal, a pair-specific engine breakage
    # would read green. The signature pins WHICH refusal was seen.
    signature = str(declared.get("refusal_signature", "")).strip()
    if not signature:
        problems.append(
            f"{key}: a refused pair must declare a `refusal_signature` the observed "
            "refusal contains, or 'refused' is the only thing verified"
        )
    elif signature not in observed.get("refusal_detail", ""):
        problems.append(
            f"{key}: declared refusal_signature {signature!r} is absent from the "
            f"refusal the carrier actually produced: {observed.get('refusal_detail', '')[:200]!r}"
        )
    return problems


def _cell_problems(key: str, floor: str, cell: object, observation: str) -> list[str]:
    """One cell against one observation."""
    if not isinstance(cell, dict):
        # `"ai_provenance": null` used to pass every check below by being present and
        # then skipped over -- four characters to turn the doctrine off.
        return [f"{key}/{floor}: cell must be an object, got {type(cell).__name__}"]
    state = cell.get("state")
    allowed = STATE_ALLOWS.get(state)
    if allowed is None:
        return [f"{key}/{floor}: unknown state {state!r}"]
    problems: list[str] = []
    if observation not in allowed:
        problems.append(
            f"{key}/{floor}: declared {state!r} but the carrier observably "
            f"{observation!r} this floor"
        )
    required = STATE_REQUIRES.get(state)
    raw = cell.get(required) if required else None
    # `isinstance`, not `str(...)`: `str(None)` is `"None"`, so `"reason": null` passed
    # the emptiness test -- the same four characters the cell guard above closes,
    # still working one level down on the justification the state exists to demand.
    value = raw.strip() if isinstance(raw, str) else ""
    if required and not value:
        problems.append(f"{key}/{floor}: state {state!r} requires a non-empty `{required}` string")
    elif required == "finding" and not FINDING_RE.search(value):
        problems.append(f"{key}/{floor}: `finding` must name a filed issue URL, got {value!r}")
    return problems


def _pair_problems(key: str, declared: dict, observed: dict) -> list[str]:
    if declared.get("baseline") != observed["baseline"]:
        return [
            f"{key}: declared baseline {declared.get('baseline')!r} but the carrier "
            f"{observed['baseline']!r} a body built to pass every floor"
        ]
    if observed["baseline"] == "refused":
        return _refused_pair_problems(key, declared, observed)
    cells = declared.get("floors")
    if not isinstance(cells, dict):
        return [f"{key}: `floors` must be an object of floor cells"]
    problems: list[str] = []
    for floor in sorted(set(FLOORS) - set(cells)):
        problems.append(f"{key}/{floor}: no cell; an absent cell is a refusal, not a default")
    for floor in sorted(set(cells) - set(FLOORS)):
        problems.append(f"{key}/{floor}: declared but no such floor")
    for floor in FLOORS:
        if floor in cells:
            problems.extend(_cell_problems(key, floor, cells[floor], observed["floors"][floor]))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--emit-observed", type=Path, default=None,
        help="write the observed grid here (for authoring the declaration; never a substitute for it)",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    matrix_path = repo_root / MATRIX_REL
    if not matrix_path.is_file():
        print(f"closeout floor matrix: declaration not found at {MATRIX_REL}", file=sys.stderr)
        return 1
    declared = json.loads(matrix_path.read_text(encoding="utf-8"))
    observed = observe_matrix(repo_root)
    if args.emit_observed is not None:
        args.emit_observed.write_text(json.dumps(observed, indent=2) + "\n", encoding="utf-8")
    problems = _problems(declared, observed)

    if args.json:
        print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    elif problems:
        print(
            "closeout floor matrix: the declaration disagrees with what the carriers "
            f"actually do ({len(problems)} finding(s)).",
            file=sys.stderr,
        )
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "  Re-measure with: python3 scripts/check_closeout_floor_matrix.py "
            "--repo-root . --emit-observed /tmp/observed.json",
            file=sys.stderr,
        )
    else:
        pairs = len(observed["pairs"])
        print(f"closeout floor matrix: {pairs} pairs declared and observed in agreement.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
