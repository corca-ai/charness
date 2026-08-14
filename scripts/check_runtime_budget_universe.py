#!/usr/bin/env python3

"""A budgeted runtime label the runner cannot name is a bar nothing can enforce (#546).

`check_runtime_budget` fails on `violations` and `profile_config_errors`. A budget
whose label has NO sample renders `WARN ... no sample yet` and exits 0, so a bar
that nothing exercises reads as protection forever -- someone deliberately sized
it, and the gate has no way to fail on it.

This gate closes the one cause of that state which is decidable without operator
intent: the label was RENAMED, retired, or typo'd, so `run-quality.sh` no longer
names it and nothing will ever record it again. It asks membership, not history:
is this budgeted label still a name the runner knows?

WHAT THIS GATE DOES NOT DECIDE, and must not be read as deciding. A label the
runner still names but does not RUN -- queued only under a condition that never
holds, or moved behind an opt-in nobody sets -- is in the universe and passes
here. `dead-code-advisory` is the live example: budgeted, spelled in the runner,
and queued only under `CHARNESS_QUALITY_DEAD_CODE=1`, so its bar can never fail
and this gate reports it clean. Separating "legitimately conditional" from
"abandoned behind an opt-in" needs an adapter-declared expectation, because the
runner does not have that information either; it lives in operator intent. #546
stays open for that half.

Why membership rather than the recorded sample window: a previous repair keyed on
sample history was built, measured defective and REVERTED. It hard-failed a fresh
machine's first run (the budget gate is queued second-to-last, so by the time it
runs the profile has ~80 samples and any "has this machine run" guard reads true
while the history is still partial), and it permanently failed six legitimately
conditional labels on a box that runs only the read-only lane, with `--no-verify`
as the operator's sole escape. Membership has neither exposure: it reads no
history, and a conditional label is in the runner's text whether or not it ran.

The union, not the selected profile. `profile_budgets` returns exactly ONE block
per run, so a gate checking only the selected profile never reaches the blocks
nobody on this machine runs -- and the adapter itself records that the aarch64
block has zero recorded samples, which is precisely where a typo would outlive the
repo. Membership is machine-independent, so checking every block costs nothing in
false reds and is the only version that reaches those blocks.

Absent from the consumer-installed quality skill by decision, NOT by oversight.
`check_runtime_budget.py` lives in `skills/public/quality/scripts/` and is installed
into consumer repos; this gate lives in `scripts/`, so it reaches plugin hosts
through the `plugins/charness/` mirror but is never installed as part of the
quality skill a consumer runs. The distinction matters because a consumer's label universe is
whatever ITS runner declares -- an adapter `command_timing_log`, npm scripts, a
Makefile -- and shipping a universe reader that only understands `run-quality.sh`
would either refuse every consumer budget or no-op silently. Consumers therefore
still carry #546's defect. That is a stated gap, not a claim of coverage.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import adapter_lib
import quality_label_universe

from runtime_bootstrap import repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

ADAPTER_PATH = Path(".agents/quality-adapter.yaml")


def budgeted_labels(adapter: dict) -> dict[str, list[str]]:
    """Every budgeted label, mapped to the blocks that budget it.

    Both shapes are read: the top-level `runtime_budgets` map (used when the
    selected profile is `default`) and every `runtime_budget_profiles.<name>.budgets`
    block. A label budgeted in a profile this machine never selects is exactly the
    case a single-profile reader cannot see.
    """
    found: dict[str, list[str]] = {}
    top = adapter.get("runtime_budgets")
    if isinstance(top, dict):
        for label in top:
            found.setdefault(str(label), []).append("runtime_budgets")
    profiles = adapter.get("runtime_budget_profiles")
    if isinstance(profiles, dict):
        for name, config in profiles.items():
            budgets = (config or {}).get("budgets") if isinstance(config, dict) else None
            if not isinstance(budgets, dict):
                continue
            for label in budgets:
                found.setdefault(str(label), []).append(f"runtime_budget_profiles.{name}")
    return found


def evaluate(repo_root: Path) -> dict[str, object]:
    adapter_path = repo_root / ADAPTER_PATH
    if not adapter_path.is_file():
        return {
            "armed": False,
            "reason": f"{ADAPTER_PATH} is absent; no budgets to check",
            "unknown_labels": [],
            "checked": 0,
        }
    universe = quality_label_universe.label_universe(repo_root)
    if not universe["resolved"]:
        return {
            "armed": False,
            "reason": str(universe["reason"]),
            "unknown_labels": [],
            "checked": 0,
        }
    # Presence of the runner is not the same as a derivable universe. A repo whose
    # `run-quality.sh` drives its gates from a list file has zero literal call
    # sites, so the universe would be the four aggregate labels alone and EVERY
    # other budget would read as orphaned -- a blocking red whose remedy tells the
    # operator to delete correct bars. That is the reverted repair's defect one
    # layer out, so an empty call-site set is "no universe", never "an empty one".
    if not universe["sources"]["queue_call_sites"]:
        return {
            "armed": False,
            "reason": (
                f"{quality_label_universe.RUN_QUALITY_PATH} names no gate labels this "
                "reader can resolve, so there is no universe to reconcile budgets against"
            ),
            "unknown_labels": [],
            "checked": 0,
        }
    adapter = adapter_lib.load_yaml_file(adapter_path)
    budgeted = budgeted_labels(adapter if isinstance(adapter, dict) else {})
    known = set(universe["labels"])
    unknown = [
        {"label": label, "blocks": blocks}
        for label, blocks in sorted(budgeted.items())
        if label not in known
    ]
    return {
        "armed": True,
        "reason": None,
        "unknown_labels": unknown,
        "checked": len(budgeted),
        "universe_size": len(known),
        "universe_sources": {
            name: len(labels) for name, labels in universe["sources"].items()
        },
    }


# The did-NOT-judge line the module docstring's second paragraph insists on. It
# used to be printed only on the passing human line; with output unconditionally
# YAML it has to ride on every verdict, or a green here reads as "every budgeted
# bar is live" -- the exact misreading this gate was built to prevent.
NOT_JUDGED = (
    "whether a named label ever RUNS -- a label queued only under a condition that "
    "never holds is in the universe and passes here (see #546)",
)


def report_payload(report: dict[str, object]) -> dict[str, object]:
    """Fold the verdict-explaining text into the payload the gate emits."""
    payload = dict(report)
    if not report["armed"]:
        # NOT-ARMED carries no `did_not_judge`, for the same reason `check_docs_graph`
        # withholds it on NOT-RUN: this run judged nothing, so listing exclusions
        # dresses an unobserved run up as a scoped verdict. The excluded claim here is
        # "a label in the universe PASSES here" -- false on a run where no universe was
        # built and nothing passed, and a machine reader keying on `did_not_judge`
        # would read that scope off an unarmed run.
        #
        # The WARN marker is load-bearing for `print_phase_output`, which surfaces a
        # passing phase log only when it carries a WARN/ADVISORY marker; an unmarked
        # degrade renders as a bare green PASS over an unchecked bar.
        payload["advisory"] = f"WARN  runtime budget universe: not armed -- {report['reason']}"
        return payload
    payload["did_not_judge"] = list(NOT_JUDGED)
    unknown = report["unknown_labels"]
    if unknown:
        payload["summary"] = (
            f"{len(unknown)} budgeted runtime label(s) are not names "
            f"`{quality_label_universe.RUN_QUALITY_PATH}` can queue, so their bars "
            "can never be exercised and can never fail."
        )
        payload["remedy"] = (
            "Rename the budget to the label the runner now uses, or delete it. "
            "Inspect the universe with "
            "`python3 scripts/quality_label_universe.py --repo-root .`."
        )
        return payload
    payload["summary"] = (
        f"runtime budget universe: {report['checked']} budgeted label(s) all named "
        f"by the runner ({report['universe_size']} in the universe)."
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    code, report = quality_label_universe.read_or_refuse(
        "runtime budget universe", lambda: evaluate(args.repo_root.resolve())
    )
    if report is None:
        return code
    emit_yaml(report_payload(report))
    if not report["armed"]:
        return 0
    return 1 if report["unknown_labels"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
