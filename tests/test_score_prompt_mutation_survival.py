from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
# Both modules do bare sibling imports (`from witness_coverage_lib import ...` /
# `from score_prompt_mutation_survival_lib import ...`), so scripts/ must be on
# sys.path when they are exec'd standalone here (mirrors
# test_generate_prompt_mutants.py / test_witness_coverage.py).
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

lib = load_script_module(
    "score_prompt_mutation_survival_lib_under_test", ROOT / "scripts" / "score_prompt_mutation_survival_lib.py"
)
cli = load_script_module(
    "score_prompt_mutation_survival_under_test", ROOT / "scripts" / "score_prompt_mutation_survival.py"
)

UNIT_HASHLESS = "plugins/charness/skills/x/SKILL.md#section-a"
UNIT_ID = f"{UNIT_HASHLESS}@abc1234567"
FRAGMENT_VALUE = "foo.md"
MARKER_VALUE = "plan_x.py"
SENTINEL_SUMMARY_VALUE = "slim-pointer.md"


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _witness_map(tmp_path: Path) -> Path:
    # Shape mirrors evals/cautilus/handoff-claim-fidelity/witness-map.json:
    # schema_version/skill/scenarios.<name>.{spec,entries}, one unit with a
    # required_command_fragment witness + a trace_command_marker witness.
    path = tmp_path / "witness-map.json"
    _write_json(
        path,
        {
            "schema_version": 1,
            "skill": "x",
            "scenarios": {
                "refresh": {
                    "spec": "refresh.spec.json",
                    "entries": [
                        {
                            "unit": UNIT_HASHLESS,
                            "status": "witnessed",
                            "witnesses": [
                                {
                                    "channel": "required_command_fragment",
                                    "value": FRAGMENT_VALUE,
                                    "causal_path": "test causal path",
                                    "deterministic": True,
                                },
                                {
                                    "channel": "trace_command_marker",
                                    "value": MARKER_VALUE,
                                    "causal_path": "test causal path",
                                    "deterministic": True,
                                },
                            ],
                        },
                    ],
                },
            },
        },
    )
    return path


def _mutant_manifest(tmp_path: Path, *, sentinels: list[dict] | None = None) -> Path:
    # Shape mirrors generate_prompt_mutants.py generate's manifest output.
    path = tmp_path / "mutants.json"
    _write_json(
        path,
        {
            "skill": "x",
            "baseline_sha": "deadbeef",
            "baseline_snapshot_sha": "feedface",
            "sentinels": sentinels or [],
            "units": [
                {
                    "unit_id": UNIT_ID,
                    "mutant_sha": "cafebabe",
                    "files_mutated": ["plugins/charness/skills/x/SKILL.md"],
                    "public_mutated": False,
                },
            ],
        },
    )
    return path


def _observed_packet(
    *, missing_fragment: bool, label: str = "command log", missing_sentinel_summary: bool = False
) -> dict:
    # Real shape (verified against a checked-in bundle:
    # charness-artifacts/efficiency/hitl-baseline-vs-skill/preserved/baseline__0/
    # observed.v1.json): evaluations[0].summary carries a
    # "Claim failures: <label> missing required fragment: <fragment>." clause
    # when a required fragment is absent; otherwise "All declared claims met."
    failures = []
    if missing_fragment:
        failures.append(f"{label} missing required fragment: {FRAGMENT_VALUE}")
    if missing_sentinel_summary:
        failures.append(f"summary missing required fragment: {SENTINEL_SUMMARY_VALUE}")
    if failures:
        summary = "Execution of /x: 100 total tokens. Claim failures: " + "; ".join(failures) + "."
        outcome = "failed"
    else:
        summary = "Execution of /x: 100 total tokens. All declared claims met."
        outcome = "passed"
    return {
        "schemaVersion": "cautilus.skill_evaluation_inputs.v1",
        "skillId": "x",
        "evaluations": [{"evaluationId": "e", "summary": summary, "outcome": outcome, "metrics": {}}],
    }


def _write_bundle(
    ab_dir: Path,
    arm: str,
    index: int,
    *,
    missing_fragment: bool = False,
    missing_sentinel_summary: bool = False,
    marker_in_trace: bool = True,
    marker_in_stream: bool | None = None,
    include_trace: bool = True,
) -> None:
    bundle = ab_dir / "preserved" / f"{arm}__{index}"
    bundle.mkdir(parents=True, exist_ok=True)
    _write_json(
        bundle / "observed.v1.json",
        _observed_packet(missing_fragment=missing_fragment, missing_sentinel_summary=missing_sentinel_summary),
    )
    if include_trace:
        # Shape mirrors trace-digest.jsonl records emitted by
        # collectToolTrace() in build-skill-execution-observation.mjs.
        args_value = MARKER_VALUE if marker_in_trace else "something-else"
        record = {
            "step": 1, "track": "parent", "name": "Bash", "args": args_value, "out_chars": 5,
            "msg_out_tokens": 1, "msg_cache_read": 0, "msg_tool_count": 1, "wall_ms": None,
        }
        (bundle / "trace-digest.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    if marker_in_stream is not None:
        command = MARKER_VALUE if marker_in_stream else "something-else"
        event = {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": command}}],
            },
        }
        (bundle / "stream.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")


def _write_results(ab_dir: Path, arm_runs: dict[str, int]) -> None:
    # Shape mirrors run_skill_efficiency_ab.py's results.json: config.arms
    # names every configured arm; runs lists one {"arm","run"} record per
    # SUCCESSFUL capture (a failed capture is dropped, never recorded).
    arms = [{"name": name} for name in arm_runs]
    runs = [{"arm": name, "run": i} for name, count in arm_runs.items() for i in range(count)]
    _write_json(ab_dir / "results.json", {"config": {"name": "t", "arms": arms}, "runs": runs})


ARM_SPECS = {"baseline": "BASELINE", "m1": UNIT_ID}
SENTINELS = [
    {
        "name": "summary canary",
        "channel": "required_summary_fragment",
        "value": SENTINEL_SUMMARY_VALUE,
        "reason": "baseline summary must still show the canary fragment",
        "deterministic": True,
    },
    {
        "name": "planner marker",
        "channel": "trace_command_marker",
        "value": MARKER_VALUE,
        "deterministic": True,
    },
]


# --- parse_arm_specs ---------------------------------------------------------


def test_parse_arm_specs_happy_path() -> None:
    specs = lib.parse_arm_specs(["baseline=BASELINE", "m1=unit-1"])
    assert specs == {"baseline": "BASELINE", "m1": "unit-1"}


def test_parse_arm_specs_requires_exactly_one_baseline() -> None:
    with pytest.raises(lib.SurvivalScorerError):
        lib.parse_arm_specs(["a=BASELINE", "b=BASELINE", "c=unit-1"])
    with pytest.raises(lib.SurvivalScorerError):
        lib.parse_arm_specs(["a=unit-1"])


def test_parse_arm_specs_rejects_malformed_entry() -> None:
    with pytest.raises(lib.SurvivalScorerError):
        lib.parse_arm_specs(["not-a-kv-pair"])


# --- baseline-validity refusal -----------------------------------------------


def test_baseline_validity_refusal_when_witness_silent_in_one_baseline_run(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    _write_bundle(ab_dir, "baseline", 0, missing_fragment=False, marker_in_trace=True)
    _write_bundle(ab_dir, "baseline", 1, missing_fragment=True, marker_in_trace=True)  # witness silent here
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 1, missing_fragment=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    assert report["experiment_valid"] is False
    assert report["units"] == []
    reasons = report["experiment_invalid_reasons"]
    assert any(r["run"] == 1 and r["channel"] == "required_command_fragment" for r in reasons)
    assert report["baseline"]["witnesses_all_fired"] is False

    argv = [
        "--ab-dir", str(ab_dir), "--witness-map", str(witness_map), "--scenario", "refresh",
        "--mutant-manifest", str(manifest), "--arm", "baseline=BASELINE", "--arm", f"m1={UNIT_ID}",
    ]
    rc = cli.main(argv)
    assert rc != 0


def test_baseline_validity_refusal_when_no_baseline_runs(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 0, "m1": 2})
    _write_bundle(ab_dir, "m1", 0)
    _write_bundle(ab_dir, "m1", 1)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    assert report["experiment_valid"] is False
    assert report["baseline"]["runs"] == 0


def test_sentinels_fire_across_baseline_and_mutant(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
        _write_bundle(ab_dir, "m1", i, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path, sentinels=SENTINELS)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    assert report["experiment_valid"] is True
    assert report["sentinels"]["all_fired"] is True
    assert [arm["all_fired"] for arm in report["sentinels"]["per_arm"]] == [True, True]
    assert report["sentinels"]["failures"] == []


def test_sentinel_missing_in_one_mutant_run_reports_failure(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 1, missing_fragment=False, missing_sentinel_summary=True, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path, sentinels=SENTINELS)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    assert report["experiment_valid"] is True
    assert report["sentinels"]["all_fired"] is False
    failures = report["sentinels"]["failures"]
    assert len(failures) == 1
    failure = failures[0]
    assert failure["arm"] == "m1"
    assert failure["run"] == 1
    assert failure["witness"]["name"] == "summary canary"
    assert "sentinel did not fire: summary `slim-pointer.md`" in failure["reason"]
    markdown = lib.render_markdown(report)
    assert "SENTINEL-FAILURE" in markdown
    assert "summary canary" in markdown


def test_baseline_validity_refusal_still_holds_with_sentinels(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    _write_bundle(ab_dir, "baseline", 0, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "baseline", 1, missing_fragment=True, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 1, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path, sentinels=SENTINELS)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    assert report["experiment_valid"] is False
    assert report["units"] == []
    assert report["sentinels"]["all_fired"] is True
    assert report["baseline"]["witnesses_all_fired"] is False


def test_missing_baseline_bundle_with_sentinels_returns_invalid_report(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    _write_bundle(ab_dir, "baseline", 0, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    (ab_dir / "preserved" / "baseline__1").mkdir(parents=True)
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 1, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path, sentinels=SENTINELS)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    assert report["experiment_valid"] is False
    assert report["units"] == []
    assert report["sentinels"]["all_fired"] is False
    assert any("missing observed.v1.json" in failure["reason"] for failure in report["sentinels"]["failures"])


def test_configured_sentinel_zero_run_arm_is_not_green(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 0})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path, sentinels=SENTINELS)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    assert report["experiment_valid"] is True
    assert report["units"][0]["verdict"] == "INVALID-FOR-VERDICT"
    assert report["sentinels"]["all_fired"] is False
    assert any(failure["arm"] == "m1" and failure["run"] is None for failure in report["sentinels"]["failures"])


def test_trace_marker_sentinel_miss_without_stream_records_caveat(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 1, missing_fragment=False, marker_in_trace=False)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(
        tmp_path,
        sentinels=[{"channel": "trace_command_marker", "value": MARKER_VALUE, "deterministic": True}],
    )

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    assert report["sentinels"]["all_fired"] is False
    assert report["sentinels"]["caveats"]
    assert "no stream.jsonl fallback" in report["sentinels"]["caveats"][0]


def test_sentinel_failure_does_not_erase_causal_unit_verdict(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 1, missing_fragment=False, missing_sentinel_summary=True, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path, sentinels=SENTINELS)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    unit = report["units"][0]
    assert unit["verdict"] == "NO-OBSERVED-EFFECT"
    assert unit["survival_rate"] == 1.0
    assert report["sentinels"]["all_fired"] is False


def test_cli_returns_nonzero_when_sentinels_fail(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, missing_sentinel_summary=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 1, missing_fragment=False, missing_sentinel_summary=True, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path, sentinels=SENTINELS)

    rc = cli.main(
        [
            "--ab-dir", str(ab_dir), "--witness-map", str(witness_map), "--scenario", "refresh",
            "--mutant-manifest", str(manifest), "--arm", "baseline=BASELINE", "--arm", f"m1={UNIT_ID}",
        ]
    )
    assert rc == 1
    err = capsys.readouterr().err
    assert "SENTINEL-FAILURE" in err


# --- verdicts -----------------------------------------------------------------


def test_detected_on_missing_fragment_in_mutant_run(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 1, missing_fragment=True, marker_in_trace=True)  # fragment fails to fire
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)
    manifest_json = json.loads(manifest.read_text(encoding="utf-8"))
    assert "mutant_ref" not in manifest_json["units"][0]

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    assert report["experiment_valid"] is True
    unit = report["units"][0]
    assert unit["verdict"] == "DETECTED"
    assert unit["n"] == 2
    assert unit["survival_rate"] == 0.5


def test_no_observed_effect_when_all_witnesses_fire(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, marker_in_trace=True)
        _write_bundle(ab_dir, "m1", i, missing_fragment=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    unit = report["units"][0]
    assert unit["verdict"] == "NO-OBSERVED-EFFECT"
    assert unit["survival_rate"] == 1.0
    assert unit["caveats"] == []

    markdown = lib.render_markdown(report)
    assert "NO-OBSERVED-EFFECT" in markdown
    assert "m1" in markdown


def test_invalid_for_verdict_when_n_is_one(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 1})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    unit = report["units"][0]
    assert unit["verdict"] == "INVALID-FOR-VERDICT"
    assert unit["survival_rate"] is None
    assert unit["n"] == 1


def test_invalid_for_verdict_when_n_is_zero(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 0})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    unit = report["units"][0]
    assert unit["verdict"] == "INVALID-FOR-VERDICT"
    assert unit["n"] == 0


# --- trace_command_marker: trace-digest + stream fallback + truncation caveat -


def test_trace_marker_fires_via_trace_digest_alone(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, marker_in_trace=True)
        _write_bundle(ab_dir, "m1", i, missing_fragment=False, marker_in_trace=True)  # no stream.jsonl
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    unit = report["units"][0]
    marker_witness = next(w for w in unit["per_witness"] if w["channel"] == "trace_command_marker")
    assert marker_witness["fired_per_run"] == [True, True]
    assert unit["caveats"] == []  # fired via trace-digest -- no truncation risk to flag


def test_trace_marker_fires_via_stream_fallback_when_trace_digest_lacks_it(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, marker_in_trace=True)
    # trace-digest.jsonl's `args` was truncated away; stream.jsonl (untruncated)
    # still carries the marker.
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, marker_in_trace=False, marker_in_stream=True)
    _write_bundle(ab_dir, "m1", 1, missing_fragment=False, marker_in_trace=False, marker_in_stream=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    unit = report["units"][0]
    marker_witness = next(w for w in unit["per_witness"] if w["channel"] == "trace_command_marker")
    assert marker_witness["fired_per_run"] == [True, True]
    assert unit["verdict"] == "NO-OBSERVED-EFFECT"
    assert unit["caveats"] == []


def test_trace_marker_truncation_caveat_when_absent_and_no_stream_fallback(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, marker_in_trace=True)
    _write_bundle(ab_dir, "m1", 0, missing_fragment=False, marker_in_trace=False)  # no stream.jsonl either
    _write_bundle(ab_dir, "m1", 1, missing_fragment=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)

    report = lib.score_survival(ab_dir, witness_map, "refresh", manifest, ARM_SPECS)
    unit = report["units"][0]
    assert unit["verdict"] == "DETECTED"  # run 0's marker witness did not fire
    assert any("truncates" in c and "160 chars" in c for c in unit["caveats"])
    markdown = lib.render_markdown(report)
    assert "160 chars" in markdown


# --- required_summary_fragment label ------------------------------------------


def test_summary_fragment_channel_uses_summary_label(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    summary_witness_map = tmp_path / "witness-map-summary.json"
    _write_json(
        summary_witness_map,
        {
            "schema_version": 1,
            "skill": "x",
            "scenarios": {
                "refresh": {
                    "spec": "refresh.spec.json",
                    "entries": [
                        {
                            "unit": UNIT_HASHLESS,
                            "status": "witnessed",
                            "witnesses": [
                                {
                                    "channel": "required_summary_fragment",
                                    "value": "Refresh kept:",
                                    "causal_path": "test",
                                    "deterministic": True,
                                },
                            ],
                        },
                    ],
                },
            },
        },
    )
    manifest = _mutant_manifest(tmp_path)

    def _write(arm: str, index: int, missing: bool) -> None:
        bundle = ab_dir / "preserved" / f"{arm}__{index}"
        bundle.mkdir(parents=True, exist_ok=True)
        if missing:
            summary = "Execution of /x: Claim failures: summary missing required fragment: Refresh kept:."
            outcome = "failed"
        else:
            summary = "Execution of /x: All declared claims met."
            outcome = "passed"
        _write_json(
            bundle / "observed.v1.json", {"evaluations": [{"summary": summary, "outcome": outcome, "metrics": {}}]}
        )

    _write("baseline", 0, missing=False)
    _write("baseline", 1, missing=False)
    _write("m1", 0, missing=False)
    _write("m1", 1, missing=True)

    report = lib.score_survival(ab_dir, summary_witness_map, "refresh", manifest, ARM_SPECS)
    assert report["experiment_valid"] is True
    unit = report["units"][0]
    assert unit["verdict"] == "DETECTED"


# --- structural CLI-shape errors -----------------------------------------------


def test_score_survival_rejects_unknown_arm_name(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i)
        _write_bundle(ab_dir, "m1", i)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)
    with pytest.raises(lib.SurvivalScorerError):
        lib.score_survival(ab_dir, witness_map, "refresh", manifest, {"baseline": "BASELINE", "nope": UNIT_ID})


def test_score_survival_rejects_unknown_unit_id(tmp_path: Path) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i)
        _write_bundle(ab_dir, "m1", i)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)
    with pytest.raises(lib.SurvivalScorerError):
        lib.score_survival(
            ab_dir, witness_map, "refresh", manifest, {"baseline": "BASELINE", "m1": "not-a-real-unit-id"}
        )


# --- CLI end-to-end + --help --------------------------------------------------


def test_cli_json_and_markdown_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    ab_dir = tmp_path / "ab"
    _write_results(ab_dir, {"baseline": 2, "m1": 2})
    for i in range(2):
        _write_bundle(ab_dir, "baseline", i, missing_fragment=False, marker_in_trace=True)
        _write_bundle(ab_dir, "m1", i, missing_fragment=False, marker_in_trace=True)
    witness_map = _witness_map(tmp_path)
    manifest = _mutant_manifest(tmp_path)
    manifest_json = json.loads(manifest.read_text(encoding="utf-8"))
    assert manifest_json["baseline_snapshot_sha"] == "feedface"
    assert "mutant_ref" not in manifest_json["units"][0]
    argv = [
        "--ab-dir", str(ab_dir), "--witness-map", str(witness_map), "--scenario", "refresh",
        "--mutant-manifest", str(manifest), "--arm", "baseline=BASELINE", "--arm", f"m1={UNIT_ID}",
    ]
    rc = cli.main(argv)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["experiment_valid"] is True

    rc = cli.main([*argv, "--markdown"])
    assert rc == 0
    text = capsys.readouterr().out
    assert "NO-OBSERVED-EFFECT" in text


def test_cli_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--help"])
    assert excinfo.value.code == 0
