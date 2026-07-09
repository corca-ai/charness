"""All-arm sentinel validation and scoring for prompt mutation survival reports."""

from __future__ import annotations

from pathlib import Path
from typing import Callable


def manifest_sentinels(manifest: dict, deterministic_channels: set[str], scorer_error: type[Exception]) -> list[dict]:
    sentinels = manifest.get("sentinels", [])
    if not isinstance(sentinels, list):
        raise scorer_error("mutant manifest `sentinels` must be a list")
    validated: list[dict] = []
    for index, sentinel in enumerate(sentinels):
        if not isinstance(sentinel, dict):
            raise scorer_error(f"mutant manifest sentinel[{index}] must be an object")
        channel = sentinel.get("channel")
        value = sentinel.get("value")
        if channel not in deterministic_channels:
            raise scorer_error(
                f"mutant manifest sentinel[{index}] channel must be one of {deterministic_channels!r}, got {channel!r}"
            )
        if not isinstance(value, str) or not value:
            raise scorer_error(f"mutant manifest sentinel[{index}] must have a non-empty string `value`")
        if sentinel.get("deterministic") is not True:
            raise scorer_error(f"mutant manifest sentinel[{index}] must set deterministic=true")
        name = sentinel.get("name")
        reason = sentinel.get("reason")
        if name is not None and not isinstance(name, str):
            raise scorer_error(f"mutant manifest sentinel[{index}] name must be a string when present")
        if reason is not None and not isinstance(reason, str):
            raise scorer_error(f"mutant manifest sentinel[{index}] reason must be a string when present")
        validated.append({"channel": channel, "value": value, "deterministic": True, "name": name, "reason": reason})
    return validated


def sentinel_label(sentinel: dict) -> str:
    name = sentinel.get("name")
    if isinstance(name, str) and name:
        return name
    return f"[{sentinel['channel']}] {sentinel['value']!r}"


def _sentinel_channel_label(channel: str) -> str:
    if channel == "required_command_fragment":
        return "command log"
    if channel == "required_summary_fragment":
        return "summary"
    return "trace command marker"


def _missed_witness(sentinel: dict) -> dict:
    return {
        "name": sentinel.get("name"),
        "channel": sentinel["channel"],
        "value": sentinel["value"],
        "deterministic": True,
        "fired": False,
    }


def _miss_reason(sentinel: dict) -> str:
    return f"sentinel did not fire: {_sentinel_channel_label(sentinel['channel'])} `{sentinel['value']}`"


def score_sentinels(
    ab_dir: Path,
    arm_specs: dict[str, str],
    runs_by_arm: dict[str, list[int]],
    sentinels: list[dict],
    evaluate_witness: Callable[[Path, str, str], tuple[bool, bool]],
    scorer_error: type[Exception],
) -> dict:
    per_arm = []
    failures: list[dict] = []
    caveats: list[str] = []
    all_fired = True
    for arm_name in arm_specs:
        run_indices = runs_by_arm.get(arm_name, [])
        per_run = []
        arm_all_fired = True
        if sentinels and not run_indices:
            arm_all_fired = False
            for sentinel in sentinels:
                failures.append(
                    {
                        "arm": arm_name,
                        "run": None,
                        "bundle": None,
                        "witness": _missed_witness(sentinel),
                        "reason": f"sentinel had no recorded runs for arm `{arm_name}`",
                    }
                )
        for run_index in run_indices:
            bundle_dir = ab_dir / "preserved" / f"{arm_name}__{run_index}"
            bundle_rel = str(bundle_dir.relative_to(ab_dir))
            run_witnesses = []
            run_all_fired = True
            for sentinel in sentinels:
                eval_error = None
                try:
                    fired, stream_available = evaluate_witness(bundle_dir, sentinel["channel"], sentinel["value"])
                except scorer_error as exc:
                    fired, stream_available = False, True
                    eval_error = str(exc)
                witness_out = {
                    "name": sentinel.get("name"),
                    "channel": sentinel["channel"],
                    "value": sentinel["value"],
                    "deterministic": True,
                    "fired": fired,
                }
                run_witnesses.append(witness_out)
                if not fired:
                    run_all_fired = False
                    failure_reason = f"sentinel could not be evaluated: {eval_error}" if eval_error else _miss_reason(sentinel)
                    if sentinel["channel"] == "trace_command_marker" and not stream_available:
                        caveat = (
                            f"trace_command_marker sentinel {sentinel['value']!r} had no stream.jsonl fallback "
                            f"in arm {arm_name!r} run {run_index} -- trace-digest.jsonl truncates `args` at "
                            "160 chars, so a marker beyond that point there could be a false negative."
                        )
                        caveats.append(caveat)
                        failure_reason += f" ({caveat})"
                    note = sentinel.get("reason")
                    if isinstance(note, str) and note:
                        failure_reason += f" ({note})"
                    failures.append(
                        {
                            "arm": arm_name,
                            "run": run_index,
                            "bundle": bundle_rel,
                            "witness": witness_out,
                            "reason": failure_reason,
                        }
                    )
            per_run.append({"run": run_index, "bundle": bundle_rel, "witnesses": run_witnesses, "all_fired": run_all_fired})
            arm_all_fired = arm_all_fired and run_all_fired
        per_arm.append({"arm": arm_name, "runs": len(run_indices), "per_run": per_run, "all_fired": arm_all_fired})
        all_fired = all_fired and arm_all_fired
    return {"all_fired": all_fired, "definitions": sentinels, "per_arm": per_arm, "failures": failures, "caveats": caveats}
