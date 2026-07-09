"""Pure logic for `witness_coverage.py`: static witness-coverage verdicts over
a skill's prompt-mutation units (S2 of the prompt-mutation-pilot goal,
charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md).

Resolves a checked-in witness map's HASH-LESS unit prefixes
(`file#heading-path`, no `@hash` -- so the map survives content edits) against
the LIVE unit manifest (worktree file discovery via `prompt_mutant_files_lib`
and unit splitting via `prompt_mutant_lib`, never a capture), applies the
verdict rules from the goal's Low-Cost Checks /
plan-critique F2 (judge-only witnesses never promote a unit to WITNESSED), and
cross-checks deterministic witness values against the scenario's spec file's
`requiredCommandFragments`/`requiredSummaryFragments` floors. No network, no
git mutation -- read-only over the checked-out worktree.
"""

from __future__ import annotations

import json
from pathlib import Path

from prompt_mutant_files_lib import list_skill_files_worktree, read_worktree_file
from prompt_mutant_lib import units_for_file

SCHEMA_VERSION = 1
STATUS_VALUES = ("witnessed", "untested", "excluded")
CHANNEL_VALUES = ("required_command_fragment", "required_summary_fragment", "trace_command_marker", "judge")
# Only these two channels have a spec-file floor to cross-check against;
# trace_command_marker is free-form (matched later against captured
# transcripts by S3) and judge is not a deterministic assertion at all.
SPEC_FLOOR_FIELD_BY_CHANNEL = {
    "required_command_fragment": "requiredCommandFragments",
    "required_summary_fragment": "requiredSummaryFragments",
}
UNMAPPED_REASON = "unmapped"


class WitnessCoverageError(RuntimeError):
    """Structural/authoring errors in the witness map or its scenario -- a
    hard failure distinct from the stale/ambiguous/spec-floor findings that
    `compute_coverage` reports (and still returns a full report for)."""


def default_witness_map_path(skill: str) -> Path:
    return Path(f"evals/cautilus/{skill}-claim-fidelity/witness-map.json")


def _load_json(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise WitnessCoverageError(f"cannot read {path}: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise WitnessCoverageError(f"{path}: invalid JSON: {exc}") from exc


def live_units(repo_root: Path, skill: str) -> list[dict]:
    """Every live mutation unit for `skill` from the checked-out worktree
    (same discovery `generate_prompt_mutants.py split` uses), each decorated
    with `hashless_id` (`file#heading-path`, no `@hash` -- what witness-map
    entries key on)."""
    file_pairs = list_skill_files_worktree(repo_root, skill)
    if not file_pairs:
        raise WitnessCoverageError(f"no SKILL.md found for skill {skill!r}")
    units: list[dict] = []
    for plugin_relpath, _public_relpath in file_pairs:
        text = read_worktree_file(repo_root, plugin_relpath)
        if text is None:
            continue
        for entry in units_for_file(plugin_relpath, text):
            entry["hashless_id"] = entry["unit_id"].rsplit("@", 1)[0]
            units.append(entry)
    return units


def _validate_witness(scenario_key: str, unit_prefix: str, index: int, witness: object) -> dict:
    if not isinstance(witness, dict):
        raise WitnessCoverageError(
            f"scenario {scenario_key!r} unit {unit_prefix!r}: witness[{index}] must be an object"
        )
    channel = witness.get("channel")
    if channel not in CHANNEL_VALUES:
        raise WitnessCoverageError(
            f"scenario {scenario_key!r} unit {unit_prefix!r}: witness[{index}] channel must be one of "
            f"{CHANNEL_VALUES}, got {channel!r}"
        )
    if not isinstance(witness.get("value"), str) or not witness["value"]:
        raise WitnessCoverageError(
            f"scenario {scenario_key!r} unit {unit_prefix!r}: witness[{index}] must have a non-empty string `value`"
        )
    if not isinstance(witness.get("deterministic"), bool):
        raise WitnessCoverageError(
            f"scenario {scenario_key!r} unit {unit_prefix!r}: witness[{index}] must have a boolean `deterministic`"
        )
    if not isinstance(witness.get("causal_path"), str):
        raise WitnessCoverageError(
            f"scenario {scenario_key!r} unit {unit_prefix!r}: witness[{index}] must have a string `causal_path`"
        )
    return witness


def _validate_entry(scenario_key: str, index: int, entry: object) -> dict:
    if not isinstance(entry, dict):
        raise WitnessCoverageError(f"scenario {scenario_key!r}: entries[{index}] must be an object")
    unit_prefix = entry.get("unit")
    if not isinstance(unit_prefix, str) or not unit_prefix:
        raise WitnessCoverageError(f"scenario {scenario_key!r}: entries[{index}] must have a non-empty string `unit`")
    status = entry.get("status")
    if status not in STATUS_VALUES:
        raise WitnessCoverageError(
            f"scenario {scenario_key!r} unit {unit_prefix!r}: status must be one of {STATUS_VALUES}, got {status!r}"
        )
    witnesses = entry.get("witnesses", [])
    if not isinstance(witnesses, list):
        raise WitnessCoverageError(f"scenario {scenario_key!r} unit {unit_prefix!r}: `witnesses` must be a list")
    for witness_index, witness in enumerate(witnesses):
        _validate_witness(scenario_key, unit_prefix, witness_index, witness)
    if status in ("untested", "excluded"):
        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise WitnessCoverageError(
                f"scenario {scenario_key!r} unit {unit_prefix!r}: status {status!r} requires a non-empty `reason`"
            )
    return entry


def load_witness_map(witness_map_path: Path, skill: str, scenario: str) -> dict:
    """Load and structurally validate `witness_map_path`, returning the
    resolved scenario dict (`{"spec": ..., "entries": [...]}`). Raises
    `WitnessCoverageError` for authoring-contract violations (missing keys,
    bad enum values, wrong types) -- these are hard failures, distinct from
    the stale/ambiguous/spec-floor findings `compute_coverage` reports on."""
    if not witness_map_path.is_file():
        raise WitnessCoverageError(f"witness map not found: {witness_map_path}")
    data = _load_json(witness_map_path)
    if data.get("schema_version") != SCHEMA_VERSION:
        raise WitnessCoverageError(
            f"{witness_map_path}: schema_version must be {SCHEMA_VERSION}, got {data.get('schema_version')!r}"
        )
    map_skill = data.get("skill")
    if map_skill != skill:
        raise WitnessCoverageError(f"{witness_map_path}: map skill {map_skill!r} does not match --skill {skill!r}")
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, dict):
        raise WitnessCoverageError(f"{witness_map_path}: missing/invalid `scenarios` object")
    if scenario not in scenarios:
        raise WitnessCoverageError(
            f"{witness_map_path}: unknown scenario {scenario!r}; known scenarios: {sorted(scenarios)}"
        )
    scenario_obj = scenarios[scenario]
    if not isinstance(scenario_obj, dict) or not isinstance(scenario_obj.get("spec"), str):
        raise WitnessCoverageError(f"{witness_map_path}: scenario {scenario!r} must have a string `spec`")
    entries = scenario_obj.get("entries")
    if not isinstance(entries, list):
        raise WitnessCoverageError(f"{witness_map_path}: scenario {scenario!r} must have an `entries` list")
    for index, entry in enumerate(entries):
        _validate_entry(scenario, index, entry)
    return scenario_obj


def load_spec_floors(witness_map_path: Path, spec_filename: str) -> dict:
    spec_path = witness_map_path.parent / spec_filename
    spec = _load_json(spec_path)
    return {
        "required_command_fragments": list(spec.get("requiredCommandFragments", []) or []),
        "required_summary_fragments": list(spec.get("requiredSummaryFragments", []) or []),
    }


def _witness_promotes_to_witnessed(witness: dict) -> bool:
    return bool(witness.get("deterministic") is True and str(witness.get("causal_path") or "").strip())


def _entry_is_witnessed(entry: dict) -> bool:
    return any(_witness_promotes_to_witnessed(w) for w in entry.get("witnesses", []))


def _spec_floor_violations(unit_prefix: str, entry: dict, scenario_floors: dict) -> list[dict]:
    field_by_channel = {
        "required_command_fragment": scenario_floors["required_command_fragments"],
        "required_summary_fragment": scenario_floors["required_summary_fragments"],
    }
    violations = []
    for witness in entry.get("witnesses", []):
        channel = witness.get("channel")
        floor_field = SPEC_FLOOR_FIELD_BY_CHANNEL.get(channel)
        if floor_field is None:
            continue  # trace_command_marker / judge: no spec-file floor to cross-check
        if witness.get("value") not in field_by_channel[channel]:
            violations.append(
                {
                    "unit": unit_prefix,
                    "channel": channel,
                    "value": witness.get("value"),
                    "reason": f"value not present in spec's {SPEC_FLOOR_FIELD_BY_CHANNEL[channel]!r}",
                }
            )
    return violations


def compute_coverage(repo_root: Path, skill: str, scenario: str, witness_map_path: Path | None = None) -> dict:
    """The full static coverage report for `skill`/`scenario`. Raises
    `WitnessCoverageError` only for structural/missing-input problems (bad
    schema, missing spec/map file, unknown scenario); stale unit prefixes,
    ambiguous unit prefixes, and spec-floor violations are all reported
    in-band (`report["ok"] is False`, with a listing under the matching key)
    rather than raised, so the caller always gets a full, inspectable report."""
    candidate_map_path = witness_map_path or default_witness_map_path(skill)
    resolved_map_path = candidate_map_path if candidate_map_path.is_absolute() else repo_root / candidate_map_path
    scenario_obj = load_witness_map(resolved_map_path, skill, scenario)
    scenario_floors = load_spec_floors(resolved_map_path, scenario_obj["spec"])

    units = live_units(repo_root, skill)
    units_by_hashless: dict[str, list[dict]] = {}
    for unit in units:
        units_by_hashless.setdefault(unit["hashless_id"], []).append(unit)

    stale_entries: list[str] = []
    ambiguous_entries: list[dict] = []
    spec_floor_errors: list[dict] = []
    downgraded_entries: list[dict] = []
    witnessed: list[dict] = []
    untested_debt: list[dict] = []
    excluded: list[dict] = []
    resolved_hashless_ids: set[str] = set()

    for entry in scenario_obj["entries"]:
        unit_prefix = entry["unit"]
        spec_floor_errors.extend(_spec_floor_violations(unit_prefix, entry, scenario_floors))
        matches = units_by_hashless.get(unit_prefix, [])
        if not matches:
            stale_entries.append(unit_prefix)
            continue
        if len(matches) > 1:
            ambiguous_entries.append(
                {"unit": unit_prefix, "matches": sorted(m["unit_id"] for m in matches)}
            )
            continue
        live_unit = matches[0]
        resolved_hashless_ids.add(unit_prefix)
        unit_id = live_unit["unit_id"]
        status = entry["status"]
        if status == "witnessed":
            if _entry_is_witnessed(entry):
                witnessed.append({"unit_id": unit_id, "witnesses": entry.get("witnesses", [])})
            else:
                reason = (
                    "downgraded from witnessed: no witness has both deterministic=true and a non-empty "
                    "causal_path (judge-only witnesses never promote a unit to WITNESSED)"
                )
                downgraded_entries.append({"unit_id": unit_id, "reason": reason})
                untested_debt.append({"unit_id": unit_id, "reason": reason})
        elif status == "untested":
            untested_debt.append({"unit_id": unit_id, "reason": entry["reason"]})
        else:  # "excluded"
            excluded.append({"unit_id": unit_id, "reason": entry["reason"]})

    for unit in units:
        if unit["hashless_id"] not in resolved_hashless_ids:
            untested_debt.append({"unit_id": unit["unit_id"], "reason": UNMAPPED_REASON})

    ok = not stale_entries and not ambiguous_entries and not spec_floor_errors
    return {
        "skill": skill,
        "scenario": scenario,
        "spec": scenario_obj["spec"],
        "generated_from_baseline": "worktree",
        "counts": {"witnessed": len(witnessed), "untested": len(untested_debt), "excluded": len(excluded)},
        "witnessed": witnessed,
        "untested_debt": untested_debt,
        "excluded": excluded,
        "downgraded_entries": downgraded_entries,
        "scenario_floors": scenario_floors,
        "stale_entries": stale_entries,
        "ambiguous_entries": ambiguous_entries,
        "spec_floor_errors": spec_floor_errors,
        "ok": ok,
    }


def render_markdown(report: dict) -> str:
    lines = [
        f"# Witness coverage: {report['skill']} / {report['scenario']} (spec: {report['spec']})",
        "",
        f"Counts: witnessed={report['counts']['witnessed']} "
        f"untested={report['counts']['untested']} excluded={report['counts']['excluded']}"
        f" -- ok={report['ok']}",
        "",
    ]

    def _section(title: str, rows: list[str]) -> None:
        lines.append(f"## {title} ({len(rows)})")
        if rows:
            lines.extend(f"- {row}" for row in rows)
        else:
            lines.append("(none)")
        lines.append("")

    _section("Witnessed", [f"{w['unit_id']} ({len(w['witnesses'])} witnesses)" for w in report["witnessed"]])
    _section("Untested debt", [f"{u['unit_id']} -- {u['reason']}" for u in report["untested_debt"]])
    _section("Excluded", [f"{e['unit_id']} -- {e['reason']}" for e in report["excluded"]])
    _section("Downgraded (witnessed -> untested)", [f"{d['unit_id']} -- {d['reason']}" for d in report["downgraded_entries"]])
    _section("Stale entries (no live match)", report["stale_entries"])
    _section(
        "Ambiguous entries (multiple live matches)",
        [f"{a['unit']} -> {', '.join(a['matches'])}" for a in report["ambiguous_entries"]],
    )
    _section(
        "Spec-floor errors",
        [f"{e['unit']} [{e['channel']}] {e['value']!r} -- {e['reason']}" for e in report["spec_floor_errors"]],
    )
    return "\n".join(lines).rstrip() + "\n"
