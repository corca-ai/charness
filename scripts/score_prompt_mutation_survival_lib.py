"""Pure scoring logic for `score_prompt_mutation_survival.py`: the S3
deterministic survival scorer for the prompt-mutation-pilot goal
(charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md).

Reads a `run_skill_efficiency_ab.py` output dir (`results.json` + `preserved/
<arm>__<i>/` bundles), a skill's checked-in witness map (`witness_coverage_lib`
schema), and a `generate_prompt_mutants.py generate` manifest (unit_id ->
parentless snapshot SHA), and computes a per-mutant-unit DETECTED / NO-OBSERVED-EFFECT /
INVALID-FOR-VERDICT verdict from three deterministic detection channels ONLY
(never a cautilus judge channel -- no judge-kind grading in this pilot's
survival scoring, per the goal's Boundaries):

  required_command_fragment / required_summary_fragment -- read from the
    preserved `observed.v1.json`'s `evaluation.summary`, which
    build-skill-execution-observation.mjs's `fragmentFindings()` renders as
    `"<label> missing required fragment: <fragment>"` inside a leading
    `"Claim failures: ..."` clause (label is `"command log"` for a
    required_command_fragment witness, `"summary"` for a
    required_summary_fragment witness). A fragment FIRED iff that exact
    "missing required fragment" mention is absent from the summary -- never
    re-derived from a lower-fidelity re-grep of the trace.

  trace_command_marker -- read from the preserved `trace-digest.jsonl`
    (per-tool-call digest; its `args` field truncates at 160 chars,
    ARGS_DIGEST_MAX in build-skill-execution-observation.mjs), with a
    `stream.jsonl` fallback (untruncated tool-call inputs) checked ONLY when
    the marker did not fire via trace-digest, so a marker digestArgs
    truncated away is still recoverable when the fuller source is present in
    the bundle. When a marker did not fire and no stream.jsonl fallback was
    available, callers get a caveat noting the truncation risk: an absence
    there could be a false negative, not proof of removal.

BASELINE VALIDITY is a hard refusal, not a soft caveat: every witness of
every mutant unit under test must have fired in EVERY baseline run, or the
whole experiment is EXPERIMENT-INVALID and NO mutant verdict is emitted --
a baseline whose witness never fires cannot detect anything, so a "survival"
reported against it would be meaningless, not conservative.
"""

from __future__ import annotations

import json
from pathlib import Path

from prompt_mutation_bundle_lib import iter_jsonl_dicts, stream_command_blob
from score_prompt_mutation_sentinel_lib import manifest_sentinels, score_sentinels, sentinel_label
from witness_coverage_lib import WitnessCoverageError, load_witness_map

# Deterministic-only: `judge` is a valid witness-map channel (schema-modeled
# for a future channel) but is never spent on in this pilot's scoring.
DETERMINISTIC_CHANNELS = ("required_command_fragment", "required_summary_fragment", "trace_command_marker")
BASELINE_MARKER = "BASELINE"
VERDICT_DETECTED = "DETECTED"
VERDICT_NO_OBSERVED_EFFECT = "NO-OBSERVED-EFFECT"
VERDICT_INVALID_FOR_VERDICT = "INVALID-FOR-VERDICT"


class SurvivalScorerError(RuntimeError):
    """Structural/authoring errors: bad `--arm` shape, an arm name absent from
    `results.json`, a unit_id absent from the mutant manifest, or a unit with
    no witness-map entry / no deterministic witnesses. Distinct from an
    EXPERIMENT-INVALID verdict, which is a fully-formed report the caller
    still gets to inspect (mirrors witness_coverage_lib's split between hard
    failures and in-band findings)."""


# --- `--arm NAME=VALUE` parsing ---------------------------------------------


def parse_arm_specs(arm_args: list[str]) -> dict[str, str]:
    """Parse repeated `--arm NAME=VALUE` into `{name: value}`. `VALUE` is
    either the literal `"BASELINE"` (exactly one arm must carry it) or a
    `unit_id` exactly as minted by `generate_prompt_mutants.py generate`'s
    manifest (hash-suffixed, e.g. `.../SKILL.md#a/b@0123456789`)."""
    specs: dict[str, str] = {}
    for raw in arm_args:
        name, sep, value = raw.partition("=")
        name, value = name.strip(), value.strip()
        if not sep or not name or not value:
            raise SurvivalScorerError(f"--arm must be NAME=VALUE (non-empty both sides), got {raw!r}")
        if name in specs:
            raise SurvivalScorerError(f"duplicate --arm name: {name!r}")
        specs[name] = value
    baseline_names = [name for name, value in specs.items() if value == BASELINE_MARKER]
    if len(baseline_names) != 1:
        raise SurvivalScorerError(
            f"--arm must name EXACTLY ONE arm as {BASELINE_MARKER!r}, got {baseline_names or 'none'}"
        )
    if len(specs) < 2:
        raise SurvivalScorerError("--arm must include the baseline arm plus at least one mutant arm")
    return specs


# --- bundle evidence readers (pure over one preserved/<arm>__<i>/ dir) ------


def _observed_summary(bundle_dir: Path) -> str:
    observed_path = bundle_dir / "observed.v1.json"
    if not observed_path.is_file():
        raise SurvivalScorerError(f"bundle missing observed.v1.json: {bundle_dir}")
    packet = json.loads(observed_path.read_text(encoding="utf-8"))
    evaluation = (packet.get("evaluations") or [{}])[0]
    return evaluation.get("summary") or ""


def _label_for_channel(channel: str) -> str:
    # Matches build-skill-execution-observation.mjs's fragmentFindings()
    # labels exactly: "command log missing required fragment: X" /
    # "summary missing required fragment: X".
    return "command log" if channel == "required_command_fragment" else "summary"


def _fragment_fired(summary: str, channel: str, value: str) -> bool:
    return f"{_label_for_channel(channel)} missing required fragment: {value}" not in summary


def _stream_command_blob(stream_path: Path) -> str:
    """Every string tool-call input value across a stream.jsonl (the capture's
    complete parent stdout), UNTRUNCATED -- the recovery source for a
    trace_command_marker the 160-char trace-digest `args` field cut away."""
    return stream_command_blob(stream_path)


def _trace_marker_fired(bundle_dir: Path, value: str) -> tuple[bool, bool]:
    """Returns `(fired, stream_available)`. Checks `trace-digest.jsonl` first;
    `stream.jsonl` (if present in the bundle) is the untruncated fallback,
    consulted only when trace-digest alone did not find the marker.
    `stream_available` records whether that fallback existed, so a caller can
    tell a genuine miss from a "no fallback to double-check" miss."""
    trace_path = bundle_dir / "trace-digest.jsonl"
    stream_path = bundle_dir / "stream.jsonl"
    stream_available = stream_path.is_file()
    if trace_path.is_file():
        for record in iter_jsonl_dicts(trace_path):
            if value in str(record.get("args", "")):
                return True, stream_available
    if stream_available and value in _stream_command_blob(stream_path):
        return True, stream_available
    return False, stream_available


def evaluate_witness(bundle_dir: Path, channel: str, value: str) -> tuple[bool, bool]:
    """`(fired, stream_available)` for one witness over one run bundle.
    `stream_available` is always True for the fragment channels (they never
    depend on stream.jsonl); it only carries real meaning for
    trace_command_marker, where it powers the truncation caveat."""
    if channel in ("required_command_fragment", "required_summary_fragment"):
        return _fragment_fired(_observed_summary(bundle_dir), channel, value), True
    if channel == "trace_command_marker":
        return _trace_marker_fired(bundle_dir, value)
    raise SurvivalScorerError(f"unsupported deterministic witness channel: {channel!r}")


# --- witness-map / manifest resolution --------------------------------------


def _unit_deterministic_witnesses(entry: dict) -> list[dict]:
    """Witnesses eligible for THIS scorer: deterministic channels only (never
    `judge` -- no cautilus judge spend in this pilot, goal Boundaries) AND
    `deterministic: true` (a `deterministic: false` row on a deterministic-
    shaped channel would be an authoring contradiction; skip rather than
    trust it silently)."""
    return [
        w
        for w in entry.get("witnesses", [])
        if w.get("channel") in DETERMINISTIC_CHANNELS and w.get("deterministic") is True
    ]


def _load_mutant_units(
    witness_map_path: Path, scenario: str, skill: str, manifest: dict, mutant_specs: dict[str, str]
) -> dict[str, dict]:
    try:
        scenario_obj = load_witness_map(witness_map_path, skill, scenario)
    except WitnessCoverageError as exc:
        raise SurvivalScorerError(str(exc)) from exc
    entries_by_hashless = {entry["unit"]: entry for entry in scenario_obj["entries"]}
    manifest_units_by_id = {u["unit_id"]: u for u in manifest.get("units", [])}

    mutant_units: dict[str, dict] = {}
    for arm_name, unit_id in mutant_specs.items():
        if unit_id not in manifest_units_by_id:
            raise SurvivalScorerError(f"--arm {arm_name}={unit_id!r}: unit_id not present in mutant manifest")
        hashless = unit_id.rsplit("@", 1)[0]
        entry = entries_by_hashless.get(hashless)
        if entry is None:
            raise SurvivalScorerError(
                f"--arm {arm_name}={unit_id!r}: no witness-map entry for unit {hashless!r} (scenario {scenario!r})"
            )
        witnesses = _unit_deterministic_witnesses(entry)
        if not witnesses:
            raise SurvivalScorerError(
                f"--arm {arm_name}={unit_id!r}: unit {hashless!r} has no deterministic witnesses to score"
            )
        mutant_units[arm_name] = {"unit_id": unit_id, "hashless": hashless, "witnesses": witnesses}
    return mutant_units


def _runs_by_arm(results: dict) -> dict[str, list[int]]:
    runs: dict[str, list[int]] = {}
    for record in results.get("runs", []):
        runs.setdefault(record["arm"], []).append(record["run"])
    for arm_name in runs:
        runs[arm_name].sort()
    return runs


# --- scoring -----------------------------------------------------------------


def _witness_triples(mutant_units: dict[str, dict]) -> list[tuple[str, str, str]]:
    """Deduplicated `(unit_id, channel, value)` union across every mutant unit
    under test -- the exact set the baseline-validity check must pass on
    every baseline run before any mutant verdict is trusted."""
    triples: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for info in mutant_units.values():
        for witness in info["witnesses"]:
            key = (info["unit_id"], witness["channel"], witness["value"])
            if key not in seen:
                seen.add(key)
                triples.append(key)
    return triples


def _score_baseline(
    ab_dir: Path, baseline_arm: str, baseline_runs: list[int], triples: list[tuple[str, str, str]]
) -> tuple[dict, list[dict]]:
    per_run = []
    invalid_reasons: list[dict] = []
    if not baseline_runs:
        invalid_reasons.append(
            {
                "unit_id": None, "channel": None, "value": None, "run": None, "bundle": None,
                "reason": f"no runs found for baseline arm {baseline_arm!r}",
            }
        )
    for run_index in baseline_runs:
        bundle_dir = ab_dir / "preserved" / f"{baseline_arm}__{run_index}"
        bundle_rel = str(bundle_dir.relative_to(ab_dir))
        if not (bundle_dir / "observed.v1.json").is_file():
            invalid_reasons.append(
                {
                    "unit_id": None, "channel": None, "value": None, "run": run_index, "bundle": bundle_rel,
                    "reason": "baseline bundle missing observed.v1.json",
                }
            )
            continue
        witnesses_out = []
        for unit_id, channel, value in triples:
            fired, _stream_available = evaluate_witness(bundle_dir, channel, value)
            witnesses_out.append({"unit_id": unit_id, "channel": channel, "value": value, "fired": fired})
            if not fired:
                invalid_reasons.append(
                    {
                        "unit_id": unit_id, "channel": channel, "value": value, "run": run_index, "bundle": bundle_rel,
                        "reason": "witness did not fire in a baseline run",
                    }
                )
        per_run.append({"run": run_index, "bundle": bundle_rel, "witnesses": witnesses_out})
    baseline_block = {
        "arm": baseline_arm,
        "runs": len(baseline_runs),
        "witnesses_all_fired": not invalid_reasons,
        "per_run": per_run,
    }
    return baseline_block, invalid_reasons


def _score_mutant_unit(ab_dir: Path, arm_name: str, info: dict, run_indices: list[int]) -> dict:
    n = len(run_indices)
    per_witness = []
    truncation_runs_by_witness: dict[tuple[str, str], list[int]] = {}
    for witness in info["witnesses"]:
        channel, value = witness["channel"], witness["value"]
        fired_per_run = []
        for run_index in run_indices:
            bundle_dir = ab_dir / "preserved" / f"{arm_name}__{run_index}"
            fired, stream_available = evaluate_witness(bundle_dir, channel, value)
            fired_per_run.append(fired)
            # Only a MISS is at truncation risk (a hit is trustworthy either
            # way); only flag it when there was no untruncated fallback to
            # double-check against.
            if channel == "trace_command_marker" and not fired and not stream_available:
                truncation_runs_by_witness.setdefault((channel, value), []).append(run_index)
        per_witness.append({"channel": channel, "value": value, "fired_per_run": fired_per_run})

    caveats = [
        f"trace_command_marker witness {value!r} had no stream.jsonl fallback in run(s) {runs} -- "
        "trace-digest.jsonl truncates `args` at 160 chars (ARGS_DIGEST_MAX in "
        "build-skill-execution-observation.mjs), so a marker beyond that point there could be a false negative."
        for (_channel, value), runs in truncation_runs_by_witness.items()
    ]

    if n < 2:
        verdict = VERDICT_INVALID_FOR_VERDICT
        survival_rate = None
    else:
        all_fired_per_run = [all(pw["fired_per_run"][i] for pw in per_witness) for i in range(n)]
        survival_rate = round(sum(all_fired_per_run) / n, 3)
        any_witness_failed = any(not fired for pw in per_witness for fired in pw["fired_per_run"])
        verdict = VERDICT_DETECTED if any_witness_failed else VERDICT_NO_OBSERVED_EFFECT

    return {
        "unit_id": info["unit_id"],
        "arm": arm_name,
        "verdict": verdict,
        "survival_rate": survival_rate,
        "n": n,
        "per_witness": per_witness,
        "caveats": caveats,
    }


def score_survival(
    ab_dir: Path, witness_map_path: Path, scenario: str, mutant_manifest_path: Path, arm_specs: dict[str, str]
) -> dict:
    """The full S3 survival report. Raises `SurvivalScorerError` only for
    structural/config problems (bad CLI shape, missing files, an arm/unit_id
    that does not exist); an invalid EXPERIMENT is still a normal return
    (`experiment_valid: False`) so the caller gets a full, inspectable report
    -- mirrors witness_coverage_lib.compute_coverage's split between hard
    failures and in-band findings."""
    results_path = ab_dir / "results.json"
    if not results_path.is_file():
        raise SurvivalScorerError(f"results.json not found under --ab-dir: {results_path}")
    results = json.loads(results_path.read_text(encoding="utf-8"))
    runs_by_arm = _runs_by_arm(results)
    config_arm_names = {arm["name"] for arm in results.get("config", {}).get("arms", [])}
    for arm_name in arm_specs:
        if arm_name not in config_arm_names:
            raise SurvivalScorerError(
                f"--arm names {arm_name!r}, not present in {results_path} config.arms ({sorted(config_arm_names)})"
            )

    manifest = json.loads(mutant_manifest_path.read_text(encoding="utf-8"))
    skill = manifest.get("skill")
    if not isinstance(skill, str) or not skill:
        raise SurvivalScorerError(f"mutant manifest missing 'skill': {mutant_manifest_path}")
    sentinels = manifest_sentinels(manifest, DETERMINISTIC_CHANNELS, SurvivalScorerError)

    baseline_arm = next(name for name, value in arm_specs.items() if value == BASELINE_MARKER)
    mutant_specs = {name: value for name, value in arm_specs.items() if name != baseline_arm}
    mutant_units = _load_mutant_units(witness_map_path, scenario, skill, manifest, mutant_specs)

    triples = _witness_triples(mutant_units)
    baseline_block, invalid_reasons = _score_baseline(ab_dir, baseline_arm, runs_by_arm.get(baseline_arm, []), triples)
    sentinel_report = score_sentinels(ab_dir, arm_specs, runs_by_arm, sentinels, evaluate_witness, SurvivalScorerError)

    if invalid_reasons:
        return {
            "scenario": scenario,
            "baseline": baseline_block,
            "sentinels": sentinel_report,
            "units": [],
            "experiment_valid": False,
            "experiment_invalid_reasons": invalid_reasons,
        }

    units_out = [
        _score_mutant_unit(ab_dir, arm_name, info, runs_by_arm.get(arm_name, []))
        for arm_name, info in mutant_units.items()
    ]
    return {
        "scenario": scenario,
        "baseline": baseline_block,
        "sentinels": sentinel_report,
        "units": units_out,
        "experiment_valid": True,
    }


# --- markdown rendering ------------------------------------------------------


def render_markdown(report: dict) -> str:
    lines = [f"# Prompt-mutation survival: scenario {report['scenario']}", ""]
    baseline = report["baseline"]
    lines.append(
        f"Baseline arm `{baseline['arm']}`: {baseline['runs']} run(s), "
        f"witnesses_all_fired={baseline['witnesses_all_fired']}"
    )
    lines.append("")
    sentinels = report.get("sentinels") or {
        "all_fired": True,
        "definitions": [],
        "per_arm": [],
        "failures": [],
        "caveats": [],
    }
    lines.append(
        f"Sentinels: {len(sentinels['definitions'])} configured, all_fired={sentinels['all_fired']}"
    )
    for arm in sentinels["per_arm"]:
        lines.append(f"- arm `{arm['arm']}`: {arm['runs']} run(s), all_fired={arm['all_fired']}")
        for run in arm["per_run"]:
            details = ", ".join(
                f"{sentinel_label(w)}={'yes' if w['fired'] else 'no'}" for w in run["witnesses"]
            ) or "no sentinels configured"
            lines.append(f"  - run {run['run']} ({run['bundle']}): {details}")
    for failure in sentinels["failures"]:
        witness = failure["witness"]
        lines.append(
            f"- SENTINEL-FAILURE arm `{failure['arm']}` run {failure['run']} ({failure['bundle']}): "
            f"{sentinel_label(witness)} -- {failure['reason']}"
        )
    for caveat in sentinels.get("caveats", []):
        lines.append(f"- SENTINEL-CAVEAT: {caveat}")
    lines.append("")
    if not report["experiment_valid"]:
        lines.append("## EXPERIMENT-INVALID -- no mutant verdicts emitted")
        lines.append("")
        for reason in report.get("experiment_invalid_reasons", []):
            if reason["channel"]:
                witness = f"[{reason['channel']}] {reason['value']!r} (unit {reason['unit_id']})"
            else:
                witness = "n/a"
            lines.append(f"- run {reason['run']} ({reason['bundle']}): {witness} -- {reason['reason']}")
        return "\n".join(lines).rstrip() + "\n"

    lines.append("## Units")
    lines.append("")
    for unit in report["units"]:
        rate = unit["survival_rate"]
        rate_str = "n/a" if rate is None else f"{rate:.3f}"
        lines.append(
            f"- `{unit['unit_id']}` (arm `{unit['arm']}`): **{unit['verdict']}** "
            f"survival_rate={rate_str} n={unit['n']}"
        )
        for witness in unit["per_witness"]:
            lines.append(f"  - [{witness['channel']}] {witness['value']!r}: fired_per_run={witness['fired_per_run']}")
        for caveat in unit["caveats"]:
            lines.append(f"  - CAVEAT: {caveat}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"
