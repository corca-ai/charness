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
and queued only under `CHARNESS_QUALITY_DEAD_CODE=1`. `runtime_budget_intent`
now records the adapter's declared trigger for that class and exposes it as an
execution non-claim, but it cannot prove that the trigger is satisfiable or that
the label ran. The consumer-installed skill can reconcile membership when its
adapter supplies the runner-owned `runtime_budget_universe` command; this
source gate remains the Charness-specific static reader.

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
Makefile -- and teaching the installed skill one runner's syntax would either
refuse every other consumer budget or no-op silently. The installed skill instead
consumes the adapter's runner-neutral one-label-per-line command when a consumer
opts in; an absent command remains an explicit non-claim, not a claim of coverage.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import adapter_lib
import quality_label_universe

from runtime_bootstrap import (
    import_repo_module,
    load_path_module,
    repo_root_from_script,
    skill_script,
)
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

ADAPTER_PATH = Path(".agents/quality-adapter.yaml")

_PROFILE_LIB_CACHE = {}
_ADAPTER_VALIDATORS_CACHE = {}


def _runtime_profile_lib():
    """Cached: `load_path_module` execs a fresh module per call."""
    if "lib" not in _PROFILE_LIB_CACHE:
        _PROFILE_LIB_CACHE["lib"] = load_path_module(
            "runtime_profile_lib_for_universe",
            skill_script(REPO_ROOT, "quality", "runtime_profile_lib.py"),
        )
    return _PROFILE_LIB_CACHE["lib"]


def _adapter_validators():
    """Load the quality adapter field owner once for intent validation."""
    if "module" not in _ADAPTER_VALIDATORS_CACHE:
        # Reuse the quality resolver's loaded validator so its sibling schema
        # modules stay on the same import path in source and exported layouts.
        _ADAPTER_VALIDATORS_CACHE["module"] = import_repo_module(
            __file__, "scripts.quality_adapter_lib"
        ).adapter_validators
    return _ADAPTER_VALIDATORS_CACHE["module"]


def _labels_outside(budgeted: dict[str, list[str]], reference: set[str]) -> list[dict[str, object]]:
    """Every budgeted label absent from `reference`, paired with the block(s) that
    budget it. One shared shape for two different reference sets this gate asks
    the same question against: the runner's known labels (`unknown_labels`) and
    the selected profile's reachable labels (`unreachable_by_selected_profile`)."""
    return [
        {"label": label, "blocks": blocks}
        for label, blocks in sorted(budgeted.items())
        if label not in reference
    ]


def budgeted_labels(adapter: dict) -> dict[str, list[str]]:
    """Every budgeted label, mapped to the blocks that budget it.

    Delegates to the EXPORTED owner. The union loop used to live here as a second
    copy of logic the consumer inventory also needed; consolidating it is the same
    one-owner move SC18 made for the coverage builders, and for the same reason --
    two readers of one adapter shape drift, and the drift is invisible until they
    disagree about a bar.
    """
    return _runtime_profile_lib().budgeted_label_union(adapter)


def _runtime_budget_intent(adapter: dict, budgeted: dict[str, list[str]]) -> dict[str, object]:
    """Reconcile explicit scheduling intent with every declared budget.

    Missing intent stays a migration warning for older consumer adapters. Once an
    adapter declares the field, an omitted or extra label is a configuration error;
    otherwise a budget can be added or removed without its scheduling meaning
    changing with it. The conditional list is deliberately a non-claim: a trigger
    string names intent, not evidence that the trigger fired.
    """
    labels = set(budgeted)
    empty = {
        "status": "not-applicable" if not labels else "not-declared",
        "always": [],
        "conditional": {},
        "external": {},
        "missing_labels": sorted(labels),
        "extra_labels": [],
        "errors": [],
        "conditional_non_claims": [],
    }
    if (
        not labels
        or "runtime_budget_intent" not in adapter
        or adapter.get("runtime_budget_intent") is None
    ):
        return empty

    errors: list[str] = []
    normalized = _adapter_validators().runtime_budget_intent(
        adapter.get("runtime_budget_intent"), errors
    )
    if normalized is None:
        normalized = {"always": [], "conditional": {}, "external": {}}
    declared = (
        set(normalized["always"]) | set(normalized["conditional"]) | set(normalized["external"])
    )
    missing = sorted(labels - declared)
    extra = sorted(declared - labels)
    if missing:
        errors.append(
            "runtime_budget_intent does not classify budgeted label(s): " + ", ".join(missing)
        )
    if extra:
        errors.append(
            "runtime_budget_intent classifies label(s) with no budget: " + ", ".join(extra)
        )
    conditional = dict(normalized["conditional"])
    return {
        "status": "configured" if not errors else "invalid",
        "always": list(normalized["always"]),
        "conditional": conditional,
        "external": dict(normalized["external"]),
        "missing_labels": missing,
        "extra_labels": extra,
        "errors": errors,
        "conditional_non_claims": [
            {"label": label, "trigger": trigger, "execution_proven": False}
            for label, trigger in sorted(conditional.items())
        ],
    }


_DOMINANCE_GATE_CACHE = {}


def _dominance_gate():
    """Cached: `load_path_module` execs a fresh module per call."""
    if "gate" not in _DOMINANCE_GATE_CACHE:
        _DOMINANCE_GATE_CACHE["gate"] = load_path_module(
            "check_command_dominance_for_universe",
            REPO_ROOT / "scripts" / "check_command_dominance.py",
        )
    return _DOMINANCE_GATE_CACHE["gate"]


def _dominance_arm(repo_root: Path) -> tuple[dict[str, object] | None, dict[str, object]]:
    """Load the dominance gate's own verdict once, and name whether the SECOND
    direction (universe -> prescription) actually ran.

    `unbudgeted_expensive_commands` used to render `[]` on a `RegistryError` and
    on an unarmed registry alike -- correctly, because a malformed registry is
    genuinely the dominance gate's verdict to render, not this gate's. But the
    summary line then reads that `[]` as "ran, found zero", and the deferral was
    not anywhere in the payload for a reader to find. This names the difference:
    `ran` is false and `reason` is set on exactly the two deferred cases;
    `examined` is the count of findings THIS direction actually classified, which
    reads 0-because-none only when `ran` is also true.

    Called at most once per `evaluate()`, so the dominance scan does not run
    twice in one pass; a caller after `unbudgeted_expensive_commands` directly
    (the tests do) still gets its own single scan.
    """
    # No `registry_path.is_file()` pre-check here, deliberately. The dominance
    # gate already decides "is there a registry" and reports it as `armed`, and
    # asking the same question in two places made whichever answer came second
    # unreachable -- the changed-line proof reported exactly that line as never
    # executed. One owner for the question, and this reads its answer.
    gate = _dominance_gate()
    dominance = gate._load_dominance_lib()
    try:
        report = gate.evaluate(repo_root)
    except dominance.RegistryError as exc:
        # A malformed registry is genuinely the dominance gate's verdict to
        # render, so that one case stays deferred; everything else now
        # propagates (narrowed from a bare `except Exception`, which also
        # swallowed a missing library, an ImportError, and any AttributeError
        # from a future refactor -- and in every one of those cases this gate
        # returned `armed: True` with an empty list and a summary claiming the
        # direction had run).
        return None, {"ran": False, "examined": 0, "reason": f"registry error: {exc}"}
    if not report.get("armed"):
        return None, {
            "ran": False,
            "examined": 0,
            "reason": str(report.get("reason") or "command dominance registry not armed"),
        }
    return report, {"ran": True, "examined": len(report.get("findings", [])), "reason": None}


def _findings_to_unbudgeted(
    report: dict[str, object] | None, budgeted_label_set: set[str]
) -> list[dict[str, object]]:
    """The dominance findings that name no budgeted label, given an already-fetched report.

    Split out of `unbudgeted_expensive_commands` so `evaluate()` can read
    `_dominance_arm`'s single scan once and hand the same report to both the
    status and the finding list, instead of scanning twice.
    """
    if report is None:
        return []
    dominance = _dominance_gate()._load_dominance_lib()
    reported: list[dict[str, object]] = []
    for finding in report.get("findings", []):
        label = (finding.get("context") or {}).get("queue_label")
        if label and label in budgeted_label_set:
            continue
        reported.append(
            {
                "site": str(finding.get("site", "")),
                "command": finding.get("command"),
                "rule_id": finding.get("rule_id"),
                "exempt": finding.get("exempt", False),
                "queue_label": label,
                # One owner for the sentence; see `unbudgeted_basis`.
                "basis": dominance.unbudgeted_basis(label),
            }
        )
    return reported


def unbudgeted_expensive_commands(
    repo_root: Path, budgeted_label_set: set[str]
) -> list[dict[str, object]]:
    """The direction this gate did not have: universe -> prescription (SC15).

    The recorded defect was one-directional. This gate asked "does every budgeted
    label still exist", and never "is the expensive thing we tell sessions to run
    budgeted at all". The second question is what let a 25-minute serial pytest
    run live in `cosmic-ray.toml`, spawned by a gate, measured by nothing: it is
    not a `run-quality.sh` queue call site, so it has no label, so no bar could
    ever fail on it.

    REPAIRED after two independent bounded reviewers found that the first version
    computed a different predicate than the sentence it printed. It derived a
    "label" from the TAIL OF THE SITE STRING -- a config key like `test-command`,
    or a file path like `scripts/run-quality.sh` -- and compared it against the
    RUNNER UNIVERSE rather than the budgeted set, while the advisory it emitted
    said "outside every budgeted label, so no bar can ever fail on them". Neither
    half was true. It was structurally always-report for the standing-gate seam,
    and silently drop-on-collision for the config seam: a `Makefile` line spelled
    `pytest = "python3 -m pytest tests"` produced site `Makefile:pytest`, matched
    the runner's `pytest` label, and vanished from the report. Its two tests
    pinned that behaviour as intended by feeding a fabricated label set.

    Now: the label comes from the queue wrapper that actually carries it
    (`command_dominance_lib.wrapper_label`, threaded through the finding's
    `context.queue_label`), and it is compared against the BUDGETED labels. A
    finding with no queue label carries no budget by construction -- that is a
    different fact from "its label is not budgeted", and both are reported with
    `basis` naming which one applies.

    The command inventory is the dominance registry's, not a new scanner. That
    bounds this arm exactly as tightly as the registry: a command nobody
    registered as dominated is not asked about here either. Stated because
    "every expensive command is budgeted" is precisely the over-read a green
    result invites, and it is not what this measures.

    ADVISORY, not blocking. Every entry here is a site the repo has already
    recorded a judgement about; turning an authored inventory into a red lane
    would make deleting the registry entry the cheapest response.

    REPO_ROOT, not `repo_root`, for loading the gate module below (see
    `_dominance_gate`). Third instance of the same mistake in this slice, and
    the acceptance test found all three: the GATE ships beside this one, while
    only the registry and the scanned sites belong to the analysed tree.
    Resolving the tool from `--repo-root` crashes on every tree that is not a
    charness checkout.
    """
    report, _status = _dominance_arm(repo_root)
    return _findings_to_unbudgeted(report, budgeted_label_set)


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
    # A shell reader with no literal call sites cannot reconcile budgets. A
    # declarative reader is different: its non-empty declaration has already been
    # validated by `quality_label_universe`, and its rows are the authority even
    # though the shell is still carrying the old queue during this migration.
    if universe.get("source") != "data" and not universe["sources"]["queue_call_sites"]:
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
    adapter_dict = adapter if isinstance(adapter, dict) else {}
    budgeted = budgeted_labels(adapter_dict)
    intent = _runtime_budget_intent(adapter_dict, budgeted)
    known = set(universe["labels"])
    unknown = _labels_outside(budgeted, known)
    dominance_report, second_direction_status = _dominance_arm(repo_root)
    lib = _runtime_profile_lib()
    # The selected-profile reachability check, computed with the SAME resolver
    # `check_runtime_budget.py` uses on this machine, absent any `--runtime-profile`
    # override this gate does not take. It answers a narrower, honestly computable
    # neighbor of "does this label ever run": is it in the block THIS run's own
    # selection would read at all. A different machine or an explicit override may
    # still select the block this run does not; that is why this is scoped to
    # "by the selected profile", never claimed as "ever".
    selected_profile = lib.selected_runtime_profile(adapter_dict, None)
    reachable, profile_errors = lib.profile_budgets(adapter_dict, selected_profile)
    if profile_errors:
        unreachable_by_selected_profile = None
        unreachable_by_selected_profile_reason = profile_errors[0]
    else:
        unreachable_by_selected_profile = _labels_outside(budgeted, set(reachable))
        unreachable_by_selected_profile_reason = None
    return {
        "armed": True,
        "reason": None,
        "unknown_labels": unknown,
        "runtime_budget_intent": intent,
        "conditional_non_claims": intent["conditional_non_claims"],
        "unbudgeted_expensive_commands": _findings_to_unbudgeted(dominance_report, set(budgeted)),
        "second_direction_status": second_direction_status,
        "malformed_budget_profile_blocks": lib.malformed_budget_profile_blocks(adapter_dict),
        "selected_runtime_profile": selected_profile,
        "unreachable_by_selected_profile": unreachable_by_selected_profile,
        "unreachable_by_selected_profile_reason": unreachable_by_selected_profile_reason,
        "checked": len(budgeted),
        "universe_size": len(known),
        "source": universe.get("source", "shell"),
        "universe_sources": {name: len(labels) for name, labels in universe["sources"].items()},
    }


# The did-NOT-judge line the module docstring's second paragraph insists on. It
# used to be printed only on the passing human line; with output unconditionally
# YAML it has to ride on every verdict, or a green here reads as "every budgeted
# bar is live" -- the exact misreading this gate was built to prevent.
NOT_JUDGED = (
    "whether a named label ever RUNS -- a label queued only under a condition that "
    "never holds is in the universe and passes here (see #546)",
    "whether a declared conditional trigger occurred -- runtime_budget_intent records "
    "operator intent, not execution evidence",
    "whether an expensive command NOBODY REGISTERED is budgeted -- the second "
    "direction reads the dominance registry, which is a denylist, so its silence "
    "is not coverage",
    "whether anything BOUNDS a reported command's runtime -- the second direction "
    "asks only whether a budgeted LABEL names it, and a config literal can carry "
    "no label at all, so that seam is structurally always-report",
)


def _append_advisory(payload: dict[str, object], message: str) -> None:
    """Keep independent attention findings visible in one report."""

    previous = payload.get("advisory")
    payload["advisory"] = f"{previous}\n{message}" if previous else message


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
    intent = report.get("runtime_budget_intent") or {}
    if intent.get("status") == "not-declared":
        _append_advisory(
            payload,
            (
                "WARN: runtime budget intent is not declared for the budgeted labels; "
                "conditional execution remains unproven. Add `runtime_budget_intent` "
                "to the adapter when migrating it."
            ),
        )
    elif intent.get("status") == "invalid":
        errors = "; ".join(str(error) for error in intent.get("errors", []))
        _append_advisory(payload, f"WARN: runtime budget intent is invalid: {errors}")
    unreachable = report.get("unreachable_by_selected_profile") or []
    if unreachable:
        labels = ", ".join(str(entry.get("label")) for entry in unreachable)
        _append_advisory(
            payload,
            (
                f"WARN: runtime budget universe: {len(unreachable)} budgeted label(s) "
                f"are unreachable by selected profile {report.get('selected_runtime_profile')!r} "
                f"in this run ({labels}); this is profile-scoped, not a claim that they "
                "never run under another profile."
            ),
        )
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
    malformed_blocks = report.get("malformed_budget_profile_blocks") or []
    if malformed_blocks:
        # WARN-marked like the advisory below: a block this reader silently
        # dropped is a defect nobody would otherwise see, not routine scope.
        payload["malformed_budget_profile_blocks_summary"] = (
            f"WARN: {len(malformed_blocks)} runtime_budget_profiles block(s) carry a "
            "`budgets` entry this reader cannot use (present but not a mapping), so "
            "every label they would have budgeted is silently absent from the "
            "universe check above. See `malformed_budget_profile_blocks` for which."
        )
    unbudgeted = report.get("unbudgeted_expensive_commands") or []
    if unbudgeted:
        # Rides the WARN marker for the same reason the dominance gate does: a
        # passing phase log is surfaced only when it carries an attention marker,
        # so an unmarked advisory is written to a file nobody opens.
        # Wording tracks what the code computes, after a reviewer measured that
        # the first version's sentence described a predicate the code did not
        # implement. Each entry carries its own `basis`; the summary must not
        # collapse the two into one claim.
        no_label = sum(1 for entry in unbudgeted if not entry.get("queue_label"))
        _append_advisory(
            payload,
            (
                f"WARN: {len(unbudgeted)} registered expensive command(s) are named by no "
                f"budgeted LABEL ({no_label} carry no queue label at all, "
                f"{len(unbudgeted) - no_label} carry a label with no budget entry). This is "
                "not a claim that nothing bounds their runtime; see "
                "`unbudgeted_expensive_commands`, where each entry states its own basis."
            ),
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
    intent = report.get("runtime_budget_intent") or {}
    return 1 if report["unknown_labels"] or intent.get("status") == "invalid" else 0


if __name__ == "__main__":
    raise SystemExit(main())
