"""Path-distinctness floor for the goal artifact's closeout evidence lines.

`Retro:` and `Disposition review:` name two different observers' work. When both
resolve to the SAME file, the closeout has one artifact wearing two labels: the
retro's author reviewed their own dispositions, and the record says a second
observer did.

**What this floor is NOT, stated because the obvious stronger rule is
unbuildable.** It does not check that the two files have different AUTHORS. No
signal in a checked-in file determines authorship, and a bounded reviewer never
commits, so any built check would be an authorship PROXY — and a deterministic
false positive on that question trains exactly the token-theater the disposition
module already argues against. Path distinctness is the defect that was actually
observed, and it is decidable from the text alone.

**Why this is ARMED, and why the justification is NOT a corpus count.** The
first version of this docstring rested on "23 in scope, 0 refused". That number
does not support arming: 20 of those 23 artifacts carry no parseable `Created:`
and are in scope only because the grandfather predicate fails closed, 3 are
dated, and only 2 were ever really compared. A pass rate measured over a
population that could not have contained a violation says nothing — which is the
exact defect the sibling figure-form floor was DISARMED for, in the same slice.

The honest justification is enumeration, not statistics. This floor asks one
decidable question — do two paths resolve to the same file — and the failure
modes are countable by hand rather than sampled:

- both bound to different files: pass (the ordinary case);
- one or both recorded as `skipped:`: not compared at all, because a skip has no
  path (see `_satisfied_evidence_paths`);
- both bound to the SAME file: refuse.

There is no fourth case, and **no legitimate reason for one artifact to be both
the record and its own independent review** — which is why a thin corpus is
acceptable HERE and was not acceptable for the figure floor. That floor asks a
fuzzy question (which tokens are figures, which prose is a source) whose answer
can only be learned by running it over real artifacts; this one asks a question
you can settle by reading it. `test_the_refusal_set_is_enumerable` pins that
enumeration so the claim is checked rather than asserted.

Rung-1: presence/identity only. Whether the second file's CONTENT is a real
independent review stays author judgment plus the fresh-eye round.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from goal_artifact_floor_grammar import (  # noqa: E402
    grandfathered_report,
    is_floor_in_scope,
    parse_created_date,
)

# Own rule date, like every other `goal_artifact_*` floor. Without one, a floor
# landing today would be in scope for every undatable prior goal, and the only
# way to green those is to edit frozen artifacts — which is the Goodhart move
# this repo's validators exist to refuse.
EVIDENCE_DISTINCTNESS_RULE_DATE = date(2026, 8, 1)

RETRO_EVIDENCE = "retro_artifact"
REVIEW_EVIDENCE = "disposition_review"


def applies(text: str) -> bool:
    return is_floor_in_scope(parse_created_date(text), EVIDENCE_DISTINCTNESS_RULE_DATE)


def _satisfied_evidence_paths(report: dict[str, Any]) -> dict[str, str]:
    """Map evidence name -> resolved path, for entries bound via a real file.

    A `skip` entry has no path and is deliberately absent: a host-blocked
    subagent recorded as `skipped:` cannot collide with the retro, and refusing
    it would punish the documented degradation instead of the defect.
    """
    paths: dict[str, str] = {}
    for entry in report.get("satisfied") or []:
        if entry.get("via") != "evidence":
            continue
        name = entry.get("name")
        path = entry.get("path")
        if name in (RETRO_EVIDENCE, REVIEW_EVIDENCE) and path:
            paths[name] = path
    return paths


def check(report: dict[str, Any], text: str) -> dict[str, Any]:
    """Return this floor's report fragment without mutating `report`."""
    if not applies(text):
        return grandfathered_report(
            text, EVIDENCE_DISTINCTNESS_RULE_DATE, "evidence-distinctness"
        )
    paths = _satisfied_evidence_paths(report)
    result: dict[str, Any] = {
        "applies": True,
        "rule_date": EVIDENCE_DISTINCTNESS_RULE_DATE.isoformat(),
        "retro_path": paths.get(RETRO_EVIDENCE),
        "disposition_review_path": paths.get(REVIEW_EVIDENCE),
    }
    if len(paths) < 2:
        # Only one of the two is bound as a file. Its own required-evidence floor
        # already owns that case; reporting it here too would double-refuse one
        # defect and obscure which floor to fix.
        result["ok"] = True
        result["reason"] = "not both bound as evidence files; nothing to compare"
        return result
    retro = Path(paths[RETRO_EVIDENCE])
    review = Path(paths[REVIEW_EVIDENCE])
    # Resolve before comparing: the same file reached by `./x.md` and `x.md`, or
    # through a symlink, is still one artifact wearing two labels.
    if _same_file(retro, review):
        result["ok"] = False
        result["reason"] = (
            f"`Retro:` and `Disposition review:` resolve to the same file ({retro.as_posix()}); "
            "the disposition review must be a separate artifact, because one file "
            "cannot be both the record and its own independent review"
        )
        return result
    result["ok"] = True
    result["reason"] = "retro and disposition review resolve to different paths"
    return result


def _same_file(left: Path, right: Path) -> bool:
    try:
        if left.exists() and right.exists():
            return left.resolve().samefile(right.resolve())
    except OSError:
        # Unreadable is not "distinct proven"; fall through to the textual
        # comparison rather than passing on an error we did not interpret.
        pass
    return left.resolve() == right.resolve()


def apply_evidence_distinctness_floor(report: dict[str, Any], text: str) -> None:
    result = check(report, text)
    report["closeout_evidence_distinctness"] = result
    if result["applies"] and not result["ok"]:
        report["ok"] = False
