"""How a runtime bar is SIZED, separate from whether a run exceeds one.

`runtime_budget_lib` answers "did this run break its budget"; this module answers
"what should the budget have been". They were one file until the 360-line cap fired,
and the cap named a real seam rather than an arbitrary place to cut: sizing reads
recorded samples and proposes numbers a human commits, enforcement reads committed
numbers and decides an exit code. Enforcement depends on sizing (its slack advisory
proposes a retune), never the reverse.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from runtime_profile_lib import profile_commands, selected_runtime_profile
from runtime_timing_log_lib import evaluate_timing_log

# Headroom retained when proposing a bar: 1.4x the worst observed run still absorbs
# normal variance while letting a genuine 2x regression trip.
SLACK_SUGGESTION_HEADROOM = 1.4
# Proposed bars round up to this step so a checked-in budgets block reads as a
# decision rather than as a transcribed measurement.
SUGGESTION_ROUNDING_MS = 500
# Machine token -> operator-facing label. Tokens match `runtime_budget_lib.evaluate`'s
# `commands_source`, so a caller compares tokens and only the render differs.
COMMANDS_SOURCE_LABELS = {
    "runtime_signals": "runtime-signals.json",
    "command_timing_log": "the repo-declared command_timing_log",
    "none": "no sample source",
}


def suggested_bar_ms(entry: dict[str, Any]) -> int | None:
    """A bar for one label, or None when no sample can justify one.

    The worst recent run is the basis, not the median: a bar drawn at the median is
    red half the time by construction. `max_recent_elapsed_ms` is absent for a label
    recorded exactly once, so the single `latest` sample stands in.
    """
    worst = _worst_observed_ms(entry)
    if worst is None:
        return None
    scaled = worst * SLACK_SUGGESTION_HEADROOM
    steps = -(-int(scaled) // SUGGESTION_ROUNDING_MS)  # ceil
    return steps * SUGGESTION_ROUNDING_MS


def _worst_observed_ms(entry: dict[str, Any]) -> int | None:
    worst = entry.get("max_recent_elapsed_ms")
    if not isinstance(worst, int):
        latest = entry.get("latest")
        worst = latest.get("elapsed_ms") if isinstance(latest, dict) else None
    if not isinstance(worst, int) or worst <= 0:
        return None
    return worst


def _sample_count(entry: dict[str, Any]) -> int:
    samples = entry.get("samples")
    if isinstance(samples, int) and samples > 0:
        return samples
    recent = entry.get("recent")
    return len(recent) if isinstance(recent, list) and recent else 1


def suggest_profile_budgets(commands: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Derive a budgets block for a profile from the samples it already recorded.

    The samples that block an unconfigured profile are the same samples a bar should
    be drawn from, so the gate derives the block rather than describing it. Every
    value is a starting point an operator is expected to edit; what it removes is the
    hand-transcription step that shipped eight bars BELOW already-observed runs on
    this repo's own aarch64 profile.

    Each entry carries the evidence DEPTH alongside the number, because a bar sized
    from one sample and a bar sized from twenty read identically once committed, and
    nothing downstream can tell them apart: the slack advisory only fires at 3x, so a
    1.4x-of-one-sample bar is invisible to it forever.
    """
    suggestions: dict[str, dict[str, int]] = {}
    for label, entry in sorted(commands.items()):
        if not isinstance(label, str) or not isinstance(entry, dict):
            continue
        bar = suggested_bar_ms(entry)
        if bar is None:
            continue
        suggestions[label] = {
            "budget_ms": bar,
            "worst_observed_ms": _worst_observed_ms(entry) or 0,
            "samples": _sample_count(entry),
        }
    return suggestions


def format_budget_suggestion(
    runtime_profile: str,
    suggestions: dict[str, dict[str, int]],
    *,
    commands_source: str,
) -> str:
    """Render a paste-ready `runtime_budget_profiles` fragment for the adapter.

    `commands_source` is a machine token from `COMMANDS_SOURCE_LABELS` and is stated
    because the header otherwise reads as if the profile id were the measurement's
    provenance. It is not: a repo-declared `command_timing_log` with no `profile`
    field matches every profile, so bars labelled for one machine can be measured on
    another.
    """
    thin = sorted(label for label, item in suggestions.items() if item["samples"] < 3)
    source_label = COMMANDS_SOURCE_LABELS.get(commands_source, commands_source)
    lines = [
        f"# Derived for `{runtime_profile}` from {len(suggestions)} label(s) in {source_label} at",
        f"# {SLACK_SUGGESTION_HEADROOM}x each label's worst observed run, rounded up to {SUGGESTION_ROUNDING_MS}ms.",
        "# Review every value before committing: this is a starting point, not a verdict.",
        "# `n=` is the evidence depth behind each bar. A bar drawn from one or two samples",
        "# is sized from noise, and no later advisory will ever say so.",
    ]
    if thin:
        lines.append(f"# THIN EVIDENCE (n<3), size these by judgment: {', '.join(thin)}")
    lines.extend(
        [
            "runtime_budget_profiles:",
            f"  {runtime_profile}:",
            "    budgets:",
        ]
    )
    lines.extend(
        f"      {label}: {item['budget_ms']}  # n={item['samples']}, worst {item['worst_observed_ms']}ms"
        for label, item in suggestions.items()
    )
    return "\n".join(lines)


def suggest_budgets(
    repo_root: Path,
    load_adapter: Callable[[Path], dict[str, Any]],
    load_signals: Callable[[Path], dict[str, Any]],
    *,
    runtime_profile: str | None = None,
    state_root: Path | None = None,
) -> tuple[str, dict[str, dict[str, int]], str]:
    """Resolve the profile the gate would enforce, derive a block, and name the source.

    The signals loader is injected rather than imported so this module stays the
    sizing half of the seam: enforcement owns where samples live. The source is
    returned, not just used, because a derived bar is only as trustworthy as the log
    it came from.

    The source is one of `COMMANDS_SOURCE_LABELS`' machine tokens, matching the
    `commands_source` token `runtime_budget_lib.evaluate` already reports. A caller
    that wants to refuse a timing-log-derived block compares a token; the prose is a
    render concern, so the two halves of this seam do not name the same fact twice.
    """
    adapter_data = load_adapter(repo_root)["data"]
    selected_profile = selected_runtime_profile(adapter_data, runtime_profile)
    if state_root is None:
        signals = load_signals(repo_root)
    else:
        signals = load_signals(repo_root, state_root=state_root)
    commands = profile_commands(signals, selected_profile) if isinstance(signals, dict) else {}
    commands_source = "runtime_signals" if commands else "none"
    if not commands:
        commands = evaluate_timing_log(repo_root, adapter_data, selected_profile)["commands"]
        if commands:
            commands_source = "command_timing_log"
    return selected_profile, suggest_profile_budgets(commands), commands_source
