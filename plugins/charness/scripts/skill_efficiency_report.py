#!/usr/bin/env python3

"""Pure aggregation, comparison, and report rendering for the skill-efficiency A/B
harness. No subprocess or filesystem access; unit-tested via
tests/test_skill_efficiency_ab.py. Split from run_skill_efficiency_ab.py at the
marked pure-section seam (length cap, D33).
"""

from __future__ import annotations

import statistics

import skill_outcome_wiring as outcome

# Metrics aggregated and compared across runs. "lower is leaner" for every key
# here — the comparison reads a positive delta as the arm spending more.
METRIC_KEYS = (
    "total_tokens",
    "output_tokens",
    "duration_ms",
    "tool_count",
    "waste_smell_count",
    "output_lines",
)
COMPARISON_IDENTITY_KEYS = (
    "source_class",
    "command_id",
    "corpus_id",
    "signal_class",
    "reconstruction_status",
    "model_id",
    "parser_id",
)


def aggregate_metrics(runs: list[dict]) -> dict:
    """Per-metric mean/median/min/max + pass_rate across one arm's runs."""
    agg: dict = {"n": len(runs)}
    if runs:
        passed = sum(1 for r in runs if r.get("outcome") == "passed")
        agg["pass_rate"] = round(passed / len(runs), 3)
    else:
        agg["pass_rate"] = None
    for key in METRIC_KEYS:
        vals = [r[key] for r in runs if isinstance(r.get(key), (int, float)) and not isinstance(r.get(key), bool)]
        if not vals:
            agg[key] = None
            continue
        agg[key] = {
            "mean": round(statistics.mean(vals), 1),
            "median": statistics.median(vals),
            "min": min(vals),
            "max": max(vals),
            "n": len(vals),
        }
    return agg


def relative_deltas(baseline_agg: dict, arm_agg: dict) -> dict:
    """Percent change of each metric's mean vs the baseline arm (None when either
    side is missing or the baseline mean is zero)."""
    out: dict = {}
    for key in METRIC_KEYS:
        base = baseline_agg.get(key)
        arm = arm_agg.get(key)
        if not isinstance(base, dict) or not isinstance(arm, dict) or not base.get("mean"):
            out[key] = None
            continue
        out[key] = round((arm["mean"] - base["mean"]) / base["mean"] * 100.0, 1)
    return out


def _arm_identity(config: dict, arm_name: str) -> dict:
    shared = config.get("comparison_identity")
    identity = dict(shared) if isinstance(shared, dict) else {}
    arm = next(
        (item for item in config.get("arms", []) if isinstance(item, dict) and item.get("name") == arm_name),
        {},
    )
    override = arm.get("comparison_identity")
    if isinstance(override, dict):
        identity.update(override)
    return {key: identity.get(key) for key in COMPARISON_IDENTITY_KEYS}


def _ordered_arms(config: dict, agg_by_arm: dict) -> list[str]:
    declared: list[str] = []
    for arm in config.get("arms", []):
        name = arm.get("name") if isinstance(arm, dict) else None
        if name in agg_by_arm and name not in declared:
            declared.append(name)
    return [*declared, *(name for name in agg_by_arm if name not in declared)]


def build_comparison_summary(config: dict, agg_by_arm: dict, outcome_by_arm: dict | None = None) -> dict:
    """Classify each delta against the baseline and keep outcome evidence adjacent."""

    arms = _ordered_arms(config, agg_by_arm)
    if not arms:
        return {"baseline": None, "arms": {}}
    baseline = arms[0]
    baseline_identity = _arm_identity(config, baseline)
    comparisons: dict[str, dict] = {}
    for arm in arms[1:]:
        identity = _arm_identity(config, arm)
        missing = [key for key in COMPARISON_IDENTITY_KEYS if not baseline_identity.get(key) or not identity.get(key)]
        mismatched = [
            key
            for key in COMPARISON_IDENTITY_KEYS
            if baseline_identity.get(key)
            and identity.get(key)
            and baseline_identity.get(key) != identity.get(key)
        ]
        reasons = [*(f"missing:{key}" for key in missing), *(f"mismatch:{key}" for key in mismatched)]
        comparable = not reasons
        grade = (outcome_by_arm or {}).get(arm, {}).get("pass_rate")
        comparisons[arm] = {
            "status": "comparable" if comparable else "incomparable",
            "reasons": reasons,
            "identity": identity,
            "cost_deltas": relative_deltas(agg_by_arm[baseline], agg_by_arm[arm]) if comparable else None,
            "outcome": {
                "capture_pass_rate": agg_by_arm[arm].get("pass_rate"),
                "grade_pass_rate": grade.get("mean") if isinstance(grade, dict) else None,
            },
        }
    return {"baseline": baseline, "baseline_identity": baseline_identity, "arms": comparisons}


def ranks_worse(lean_metrics: dict, wasteful_metrics: dict, keys: tuple[str, ...]) -> list[str]:
    """Keys on which `wasteful` is NOT strictly greater than `lean`. Empty list
    means the instruments correctly ranked the wasteful run worse on every key —
    the self-test gate."""
    failed = []
    for key in keys:
        lean = lean_metrics.get(key)
        waste = wasteful_metrics.get(key)
        if not isinstance(lean, (int, float)) or not isinstance(waste, (int, float)) or not waste > lean:
            failed.append(key)
    return failed


def _fmt_metric(stat: dict | None) -> str:
    if not isinstance(stat, dict):
        return "n/a"
    return f"{stat['mean']:g} [{stat['min']:g}–{stat['max']:g}]"


def _fmt_scalar(value: object) -> str:
    return "n/a" if value is None else str(value)


def build_report(config: dict, agg_by_arm: dict, outcome_by_arm: dict | None = None) -> str:
    """Markdown comparison: per-arm mean [min–max] table + deltas vs the first arm,
    plus the advisory outcome-grade section when an eval has an assertion set."""
    arms = _ordered_arms(config, agg_by_arm)
    lines = [
        f"# Efficiency A/B — {config.get('name', 'unnamed')}",
        "",
        "Advisory efficiency comparison (NOT a pass/fail verdict). Lower is leaner.",
        "",
        "## Per-arm (mean [min–max])",
        "",
        "| metric | " + " | ".join(arms) + " |",
        "| --- | " + " | ".join(["---"] * len(arms)) + " |",
        "| n | " + " | ".join(str(agg_by_arm[a]["n"]) for a in arms) + " |",
        "| pass_rate | " + " | ".join(_fmt_scalar(agg_by_arm[a]["pass_rate"]) for a in arms) + " |",
    ]
    for key in METRIC_KEYS:
        row = f"| {key} | " + " | ".join(_fmt_metric(agg_by_arm[a].get(key)) for a in arms) + " |"
        lines.append(row)
    if len(arms) >= 2:
        baseline = arms[0]
        comparison = build_comparison_summary(config, agg_by_arm, outcome_by_arm)
        lines += ["", f"## Deltas vs `{baseline}` (mean %, + = spends more)", ""]
        others = arms[1:]
        lines.append("| arm | comparability | capture pass_rate | outcome grade pass_rate | cost deltas |")
        lines.append("| --- | --- | --- | --- | --- |")
        for arm in others:
            entry = comparison["arms"][arm]
            if entry["status"] == "comparable":
                deltas = entry["cost_deltas"] or {}
                costs = ", ".join(
                    f"{key}={value:+g}%" for key, value in deltas.items() if value is not None
                ) or "n/a"
            else:
                costs = "not reported (" + ", ".join(entry["reasons"]) + ")"
            evidence = entry["outcome"]
            lines.append(
                f"| {arm} | {entry['status']} | {_fmt_scalar(evidence['capture_pass_rate'])} | "
                f"{_fmt_scalar(evidence['grade_pass_rate'])} | {costs} |"
            )
    section = outcome.render_outcome_section(outcome_by_arm) if outcome_by_arm else ""
    if section:
        lines.append(section)
    lines += [
        "",
        "## Honest caveats",
        "",
        f"- n={config.get('runs')} per arm — read the [min–max] range, not just the mean; small-n means overlap is common.",
        "- output_lines is best-effort (added lines in the worktree vs the capture base ref, including any in-run commit's slice).",
        "- No LLM judge yet (over-build / completeness deferred) — these are process + size metrics only.",
        "- Cross-ref arms hold project instruction routing constant, so a delta is the ref difference. A same-ref 'baseline' plain prompt still runs in the charness worktree and can auto-route to the skill (CONTAMINATION) — verify via each arm's Skill/tool trace before trusting a baseline-vs-skill delta.",
        "",
    ]
    return "\n".join(lines)
