from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts import rca_ledger_lib as lib

ROOT = Path(__file__).resolve().parents[1]
COMMITTED_LEDGER = ROOT / "charness-artifacts" / "metrics" / "rca-ledger.jsonl"


def run_script(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", f"scripts/{script}", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def event(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": 1,
        "ts": "2026-05-24T00:00:00Z",
        "source": "debug",
        "event_kind": "bug",
        "converted": True,
        "durable_kind": "gate",
        "class_key": "k",
    }
    record.update(overrides)
    return record


def write_ledger(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in records),
        encoding="utf-8",
    )


def write_raw(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# AC1 -------------------------------------------------------------------------
def test_ac1_validate_rejects_each_malformed_case(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    write_raw(
        ledger,
        [
            json.dumps(event(converted=False, durable_kind="gate")),  # invariant dir A
            json.dumps(event(converted=True, durable_kind="none")),  # invariant dir B
            json.dumps(event(source="slack")),  # bad enum
            json.dumps({"schema_version": 1, "ts": "2026-05-24T00:00:00Z", "source": "debug"}),  # missing
            json.dumps(event(ts="not-a-dateZ")),  # bad timestamp (ends in Z but not RFC3339)
        ],
    )
    result = run_script("validate_rca_ledger.py", "--ledger", str(ledger), "--json")
    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    assert payload["error_count"] == 5
    assert {entry["line"] for entry in payload["errors"]} == {1, 2, 3, 4, 5}


def test_ac1_validate_rejects_impossible_calendar_timestamp(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    write_ledger(ledger, [event(ts="2026-99-99T99:99:99Z")])

    result = run_script("validate_rca_ledger.py", "--ledger", str(ledger), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["errors"][0]["line"] == 1
    assert "date-time" in payload["errors"][0]["error"]


def test_ac1_timestamp_calendar_check_ignores_non_string_values() -> None:
    lib._validate_timestamp_calendar(None)


def test_ac1_validate_covers_missing_blank_and_invalid_json_paths(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    assert lib.validate_ledger(missing, lib.load_schema()) == [
        {"line": 0, "error": "ledger file not found"}
    ]
    assert lib.read_events(missing) == []

    ledger = tmp_path / "ledger.jsonl"
    write_raw(ledger, ["", "{not-json}", json.dumps(event())])

    errors = lib.validate_ledger(ledger, lib.load_schema())

    assert errors == [{"line": 2, "error": "invalid JSON: Expecting property name enclosed in double quotes"}]


def test_ac1_validate_accepts_committed_ledger() -> None:
    result = run_script("validate_rca_ledger.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


# #219 Slice 2: kill the validate_rca_ledger main() survivors -----------------
# The #219 regression (commit 59841e0, source unchanged since) left three live
# survivors in main(); existing tests asserted returncode/error_count but never
# the status string, the exact JSON indent, or the text-mode error loop.
def test_ac1_validate_json_status_field_reflects_validity(tmp_path: Path) -> None:
    """`"status": "valid" if not errors else "invalid"` survived because no test
    asserted the status string, so the `not errors` flip (Delete_Not / AddNot)
    went unnoticed. Pin both polarities."""
    clean = tmp_path / "clean.jsonl"
    write_ledger(clean, [event()])
    ok = run_script("validate_rca_ledger.py", "--ledger", str(clean), "--json")
    assert ok.returncode == 0, ok.stderr
    assert json.loads(ok.stdout)["status"] == "valid"

    bad = tmp_path / "bad.jsonl"
    write_raw(bad, [json.dumps(event(source="slack"))])  # bad enum
    invalid = run_script("validate_rca_ledger.py", "--ledger", str(bad), "--json")
    assert invalid.returncode == 1
    assert json.loads(invalid.stdout)["status"] == "invalid"


def test_ac1_validate_json_uses_two_space_indent(tmp_path: Path) -> None:
    """`print(json.dumps(result, indent=2))` survived because every assertion
    does `json.loads` (indent-agnostic). Pin the RAW 2-space formatting, the
    same kill #251 applied to the aggregate output."""
    bad = tmp_path / "bad.jsonl"
    write_raw(bad, [json.dumps(event(source="slack"))])
    result = run_script("validate_rca_ledger.py", "--ledger", str(bad), "--json")
    raw = result.stdout
    payload = json.loads(raw)
    assert raw.rstrip("\n") == json.dumps(payload, indent=2)
    assert '\n  "' in raw  # a top-level key indented by exactly two spaces


def test_ac1_validate_text_mode_prints_each_malformed_line(tmp_path: Path) -> None:
    """The non-`--json` error branch (`for entry in errors: print(... stderr)`)
    was never exercised, so the ZeroIterationForLoop mutant survived. Run text
    mode on a malformed ledger and assert each line's error is printed."""
    bad = tmp_path / "bad.jsonl"
    write_raw(
        bad,
        [
            json.dumps(event(source="slack")),  # bad enum
            json.dumps(event(converted=False, durable_kind="gate")),  # invariant break
        ],
    )
    result = run_script("validate_rca_ledger.py", "--ledger", str(bad))  # no --json
    assert result.returncode == 1
    assert "invalid: 2 malformed line(s)" in result.stderr
    # Each malformed line is reported individually; ZeroIterationForLoop drops these.
    assert "line 1:" in result.stderr
    assert "line 2:" in result.stderr


# AC2 -------------------------------------------------------------------------
def test_ac2_aggregate_rate_and_breakdown(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    write_ledger(
        ledger,
        [
            event(source="debug", event_kind="bug", converted=True, durable_kind="gate"),
            event(source="debug", event_kind="bug", converted=False, durable_kind="none"),
            event(source="issue", event_kind="repeated_correction", converted=True, durable_kind="issue"),
            event(source="issue", event_kind="weak_proof", converted=False, durable_kind="none"),
            event(source="retro", event_kind="bug", converted=True, durable_kind="test", seed=True),
            event(source="retro", event_kind="bug", converted=False, durable_kind="none", seed=True),
        ],
    )
    result = run_script("aggregate_rca_ledger.py", "--ledger", str(ledger), "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    included = payload["seed_included"]
    assert included["total"] == 6 and included["converted"] == 3
    assert included["rate"] == 0.5
    assert included["by_source"]["debug"]["rate"] == 0.5
    assert included["by_event_kind"]["repeated_correction"]["rate"] == 1.0
    assert included["by_event_kind"]["weak_proof"]["rate"] == 0.0

    excluded = payload["seed_excluded"]
    assert excluded["total"] == 4 and excluded["converted"] == 2
    assert excluded["rate"] == 0.5
    assert "retro" not in excluded["by_source"]


# #251 Slice 3: kill the survived `indent=2` mutant -------------------------
def test_aggregate_json_uses_two_space_indent(tmp_path: Path) -> None:
    """``print(json.dumps(payload, indent=2))`` survived mutation because the
    AC2 assertion does ``json.loads`` (indent-agnostic). The NumberReplacer
    mutant on ``indent=2`` still emits parseable JSON, so pin the RAW 2-space
    formatting instead (critique B3)."""
    ledger = tmp_path / "ledger.jsonl"
    write_ledger(
        ledger,
        [event(source="debug", event_kind="bug", converted=True, durable_kind="gate")],
    )
    result = run_script("aggregate_rca_ledger.py", "--ledger", str(ledger), "--json")
    assert result.returncode == 0, result.stderr
    raw = result.stdout
    payload = json.loads(raw)
    # Exact 2-space indentation: any other indent value diverges here.
    assert raw.rstrip("\n") == json.dumps(payload, indent=2)
    assert '\n  "' in raw  # a top-level key indented by exactly two spaces


# AC3 -------------------------------------------------------------------------
def test_ac3_record_round_trip_and_refuse_before_append(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    ok = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "retro", "--event-kind", "weak_proof", "--class-key", "rt",
    )
    assert ok.returncode == 0, ok.stderr
    assert run_script("validate_rca_ledger.py", "--ledger", str(ledger)).returncode == 0
    size_before = ledger.stat().st_size

    bad = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "debug", "--event-kind", "bug",
        "--durable-kind", "gate", "--class-key", "bad",  # converted defaults false -> invariant break
    )
    assert bad.returncode == 1
    assert ledger.stat().st_size == size_before  # ledger unchanged


def test_ac3_record_optional_fields_round_trip(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"

    ok = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue",
        "--event-kind", "bug",
        "--converted",
        "--durable-kind", "issue",
        "--class-key", "optional-fields",
        "--caught-by", "human",
        "--seed",
        "--ref", "#211",
        "--note", "covers optional field branches",
        "--json",
    )

    assert ok.returncode == 0, ok.stderr
    payload = json.loads(ok.stdout)
    assert payload["appended"] is True
    [record] = lib.read_events(ledger)
    assert record["caught_by"] == "human"
    assert record["seed"] is True
    assert record["ref"] == "#211"
    assert record["note"] == "covers optional field branches"


def test_ac3_record_duplicate_identity_is_success_noop(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    first = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue",
        "--event-kind", "bug",
        "--converted",
        "--durable-kind", "issue",
        "--class-key", "duplicate-class",
        "--ref", "#212",
    )
    assert first.returncode == 0, first.stderr

    duplicate = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue",
        "--event-kind", "bug",
        "--converted",
        "--durable-kind", "issue",
        "--class-key", "duplicate-class",
        "--ref", "different-ref-does-not-change-identity",
        "--json",
    )

    assert duplicate.returncode == 0, duplicate.stderr
    payload = json.loads(duplicate.stdout)
    assert payload["status"] == "duplicate"
    assert payload["appended"] is False
    records = lib.read_events(ledger)
    assert len(records) == 1
    assert records[0]["ref"] == "#212"


def test_ac3_record_duplicate_identity_does_not_rewrite_existing_duplicates(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    first = event(
        source="issue",
        event_kind="bug",
        converted=True,
        durable_kind="issue",
        class_key="preexisting-duplicate-class",
        ref="first-existing",
    )
    second = event(
        source="issue",
        event_kind="bug",
        converted=True,
        durable_kind="issue",
        class_key="preexisting-duplicate-class",
        ref="second-existing",
    )
    write_raw(ledger, [json.dumps(first), json.dumps(second)])
    before = ledger.read_text(encoding="utf-8")

    duplicate = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue",
        "--event-kind", "bug",
        "--converted",
        "--durable-kind", "issue",
        "--class-key", "preexisting-duplicate-class",
        "--ref", "third-should-not-append",
        "--json",
    )

    assert duplicate.returncode == 0, duplicate.stderr
    assert json.loads(duplicate.stdout)["status"] == "duplicate"
    assert ledger.read_text(encoding="utf-8") == before


def test_ac3_record_distinct_identity_appends(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    for class_key in ("first-class", "second-class"):
        result = run_script(
            "record_rca_event.py",
            "--ledger", str(ledger),
            "--source", "issue",
            "--event-kind", "bug",
            "--converted",
            "--durable-kind", "issue",
            "--class-key", class_key,
        )
        assert result.returncode == 0, result.stderr

    assert [record["class_key"] for record in lib.read_events(ledger)] == [
        "first-class",
        "second-class",
    ]


def test_ac3_record_duplicate_scan_ignores_malformed_existing_lines(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    write_raw(
        ledger,
        [
            "{not-json}",
            json.dumps(
                event(
                    source="issue",
                    event_kind="bug",
                    converted=True,
                    durable_kind="issue",
                    class_key="blocked-by-invalid-ledger",
                    ref="#212",
                )
            ),
        ],
    )

    duplicate = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue",
        "--event-kind", "bug",
        "--converted",
        "--durable-kind", "issue",
        "--class-key", "blocked-by-invalid-ledger",
        "--json",
    )

    assert duplicate.returncode == 0, duplicate.stderr
    assert json.loads(duplicate.stdout)["status"] == "duplicate"
    assert ledger.read_text(encoding="utf-8").count("\n") == 2

    new_key = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue",
        "--event-kind", "bug",
        "--converted",
        "--durable-kind", "issue",
        "--class-key", "new-key-despite-invalid-existing-line",
    )
    assert new_key.returncode == 0, new_key.stderr
    assert ledger.read_text(encoding="utf-8").count("\n") == 3


# AC4 -------------------------------------------------------------------------
def seed_only_both_outcomes() -> list[dict[str, object]]:
    return [
        event(converted=True, durable_kind="gate", seed=True),
        event(converted=False, durable_kind="none", seed=True),
    ]


def test_ac4_committed_ledger_retains_both_seed_outcomes() -> None:
    # The committed ledger keeps its seeded both-outcome set even as live
    # (non-seed) events accrue, so this asserts about the seed subset only —
    # it must not regress the moment auto-append (slice 2) fires.
    seed_events = [e for e in lib.read_events(COMMITTED_LEDGER) if e.get("seed") is True]
    assert [e for e in seed_events if e.get("converted") is True]
    assert [e for e in seed_events if e.get("converted") is False]


def test_ac4_seed_only_window_baseline_is_empty(tmp_path: Path) -> None:
    # Empty-baseline honesty is a property of a seed-only window, proven on a
    # synthetic fixture decoupled from the live committed ledger.
    ledger = tmp_path / "seed_only.jsonl"
    write_ledger(ledger, seed_only_both_outcomes())
    payload = lib.aggregate(lib.read_events(ledger))
    assert payload["baseline_rate_available"] is False
    assert payload["seed_excluded"]["rate"] == lib.NA
    assert 0.0 < payload["seed_included"]["rate"] < 1.0


# AC5 -------------------------------------------------------------------------
def test_ac5_round_trip_independent_of_usage_episodes_adapter(tmp_path: Path) -> None:
    # Independence is structural: the RCA ledger never touches the
    # usage-episodes adapter or its state/session machinery, so it works under
    # any adapter state (the adapter is currently enabled in this repo, which is
    # a stronger independence proof than the spec's assumed disabled state).
    # Reusing the pure portable-path helper is the spec-blessed reuse, not coupling.
    forbidden = ("usage-episodes-adapter", "emit_usage_episode", ".charness/usage-episodes", "usage_episode.jsonl")
    for name in ("record_rca_event.py", "validate_rca_ledger.py", "aggregate_rca_ledger.py", "rca_ledger_lib.py"):
        source = (ROOT / "scripts" / name).read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in source, f"{name} references adapter machinery: {token}"
    assert callable(lib.portable_path)  # the spec-blessed helper reuse resolves at runtime

    ledger = tmp_path / "ledger.jsonl"
    ok = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "debug", "--event-kind", "bug",
        "--converted", "--durable-kind", "gate", "--class-key", "indep",
    )
    assert ok.returncode == 0, ok.stderr
    assert run_script("validate_rca_ledger.py", "--ledger", str(ledger)).returncode == 0


# AC6 -------------------------------------------------------------------------
def test_ac6_doc_contains_rubric() -> None:
    doc = (ROOT / "docs" / "product-success-metrics.md").read_text(encoding="utf-8")
    assert "Classification Rubric" in doc
    assert "applies to **every** `durable_kind`" in doc
    assert "Tie-break default" in doc
    assert "converted=false" in doc


# AC7 -------------------------------------------------------------------------
def test_ac7_on_state_keeps_na_and_no_baseline_number(tmp_path: Path) -> None:
    # Slice 2 wired auto-append, so the banner reads ON. The substantive guard
    # AC7 protects (no numeric baseline while the seed-excluded window is empty)
    # is proven on a synthetic seed-only fixture, decoupled from the live
    # committed ledger so accruing real events cannot mask the guard.
    ledger = tmp_path / "seed_only.jsonl"
    write_ledger(ledger, seed_only_both_outcomes())
    payload = json.loads(
        run_script("aggregate_rca_ledger.py", "--ledger", str(ledger), "--json").stdout
    )
    assert payload["auto_append"] == lib.AUTO_APPEND_ON_BANNER
    assert payload["auto_append"].startswith("auto_append: ON")
    assert payload["auto_append_wired"] is True
    assert payload["seed_excluded"]["rate"] == lib.NA
    assert payload["baseline_rate_available"] is False

    text = run_script("aggregate_rca_ledger.py", "--ledger", str(ledger)).stdout
    assert "auto_append: ON" in text
    # flipping OFF->ON must not strip the "do not quote" guard from the seed-only number
    assert "do not quote" in text
    baseline_line = next(line for line in text.splitlines() if "overall: n/a" in line)
    assert "%" not in baseline_line  # no numeric baseline rate printed


def test_ac7_render_text_covers_empty_and_live_baseline_branches() -> None:
    empty_text = lib.render_text(lib.aggregate([]))
    assert "by source:\n      (none)" in empty_text
    assert "overall: n/a" in empty_text

    live_text = lib.render_text(
        lib.aggregate([event(source="retro", event_kind="weak_proof", converted=False, durable_kind="none")])
    )
    assert "seed-excluded (baseline figure):" in live_text
    assert "overall: 0/1 (0.0%)" in live_text
    assert "retro: 0/1 (0.0%)" in live_text


# AC8 -------------------------------------------------------------------------
def test_ac8_caught_by_enum_enforced_and_optional(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    write_raw(bad, [json.dumps(event(caught_by="robot"))])
    assert run_script("validate_rca_ledger.py", "--ledger", str(bad)).returncode == 1

    omitted = tmp_path / "ok.jsonl"
    write_ledger(omitted, [event()])  # no caught_by key
    assert "caught_by" not in event()
    assert run_script("validate_rca_ledger.py", "--ledger", str(omitted)).returncode == 0


# Slice 2: auto-append wiring -------------------------------------------------
APPEND_REFERENCE = ROOT / "skills" / "shared" / "references" / "rca-ledger-append.md"
SKILL_SOURCE_FLAGS = {
    "debug": "--source debug",
    "issue": "--source issue",
    "retro": "--source retro",
}


def test_slice2_append_reference_is_presence_gated_and_rubric_anchored() -> None:
    text = APPEND_REFERENCE.read_text(encoding="utf-8")
    # presence gate keeps the public-skill change a no-op for consumer repos
    assert "scripts/record_rca_event.py" in text
    assert "silent no-op" in text
    # judgment calls defer to the rubric instead of being restated/extended here
    assert "product-success-metrics.md" in text
    # the seed flag must stay reserved for hand-entered history
    assert "Never pass `--seed`" in text
    # tie-break default to converted=false on ambiguity
    assert "inflate the denominator" in text


def test_slice2_three_skills_cite_append_reference_with_correct_source() -> None:
    for skill, source_flag in SKILL_SOURCE_FLAGS.items():
        text = (ROOT / "skills" / "public" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert "rca-ledger-append.md" in text, f"{skill}/SKILL.md must cite the append reference"
        assert source_flag in text, f"{skill}/SKILL.md must wire {source_flag}"


# Slice 3: #184 numeric target (floor + zero-falsified-conversion tripwire) ----
def ts_event(day: int, **overrides: object) -> dict[str, object]:
    return event(ts=f"2026-06-{day:02d}T00:00:00Z", **overrides)


def test_target_falsified_detects_recurrence_after_conversion_only() -> None:
    # converted then recurred -> falsified; never-converted recurrence -> not listed;
    # recurrence BEFORE the conversion -> not listed (the artifact postdates it);
    # a recurrence that is itself converted=true still counts (the class recurred).
    events = [
        ts_event(1, class_key="converted-then-recurred", converted=True, durable_kind="gate"),
        ts_event(5, class_key="converted-then-recurred", converted=False, durable_kind="none"),
        ts_event(1, class_key="never-converted", converted=False, durable_kind="none"),
        ts_event(5, class_key="never-converted", converted=False, durable_kind="none"),
        ts_event(1, class_key="recurred-before-conversion", converted=False, durable_kind="none"),
        ts_event(5, class_key="recurred-before-conversion", converted=True, durable_kind="test"),
        ts_event(2, class_key="reconverted-recurrence", converted=True, durable_kind="gate"),
        ts_event(6, class_key="reconverted-recurrence", converted=True, durable_kind="test"),
    ]
    falsified = lib.falsified_conversions(events)
    assert [entry["class_key"] for entry in falsified] == [
        "converted-then-recurred",
        "reconverted-recurrence",
    ]
    assert falsified[0]["converted_ts"] == "2026-06-01T00:00:00Z"
    assert falsified[0]["recurrence_ts"] == "2026-06-05T00:00:00Z"


def test_target_falsified_includes_converted_seed_recurring_live() -> None:
    events = [
        ts_event(1, class_key="seeded-conversion", converted=True, durable_kind="gate", seed=True),
        ts_event(9, class_key="seeded-conversion", converted=False, durable_kind="none"),
    ]
    assert [entry["class_key"] for entry in lib.falsified_conversions(events)] == ["seeded-conversion"]


def test_target_no_live_events_and_insufficient_n() -> None:
    seed_only = [ts_event(1, class_key="s", seed=True)]
    target = lib.evaluate_target(seed_only)
    assert target["status"] == "no-live-events"
    assert target["window"] is None

    few = [ts_event(day, class_key=f"k{day}") for day in range(1, lib.TARGET_MIN_EVENTS)]
    target = lib.evaluate_target(few)
    assert target["status"] == "insufficient-n"
    assert target["window"]["total"] == lib.TARGET_MIN_EVENTS - 1


def test_target_met_not_met_and_tripwire() -> None:
    converted = [
        ts_event(day, class_key=f"ok{day}", converted=True, durable_kind="gate")
        for day in range(1, 11)
    ]
    assert lib.evaluate_target(converted)["status"] == "met"

    # 5/10 converted -> below the 70% floor.
    half = converted[:5] + [
        ts_event(day, class_key=f"miss{day}", converted=False, durable_kind="none")
        for day in range(11, 16)
    ]
    below = lib.evaluate_target(half)
    assert below["status"] == "not-met"
    assert below["reasons"] == ["rate below floor"]

    # Rate above floor but one converted class recurs inside the window -> tripwire.
    tripped = lib.evaluate_target(
        converted + [ts_event(12, class_key="ok1", converted=False, durable_kind="none")]
    )
    assert tripped["status"] == "not-met"
    assert tripped["reasons"] == ["falsified conversion in window (tripwire)"]
    assert tripped["window"]["falsified_in_window"] == 1


def test_target_falsified_recurrence_outside_window_does_not_trip() -> None:
    # The tripwire judges recurrences whose ts falls in the rolling window; an
    # aged-out falsified conversion stays in the all-time list (and keeps its
    # per-instance response contract) but no longer blocks the verdict.
    stale_falsified = [
        event(ts="2026-01-01T00:00:00Z", class_key="aged", converted=True, durable_kind="gate"),
        event(ts="2026-01-05T00:00:00Z", class_key="aged", converted=False, durable_kind="none"),
    ]
    fresh = [
        ts_event(day, class_key=f"new{day}", converted=True, durable_kind="gate")
        for day in range(1, 11)
    ]
    target = lib.evaluate_target(stale_falsified + fresh)
    assert [entry["class_key"] for entry in target["falsified_conversions"]] == ["aged"]
    assert target["window"]["falsified_in_window"] == 0
    assert target["status"] == "met"


def test_event_identity_non_string_fields_and_upgrade_ref() -> None:
    # The early return for a record missing/typed-wrong identity fields, and
    # the upgrade identity extension (marker + redesign ref) that lets an
    # upgrade append alongside the original triple.
    assert lib.event_identity({"source": "issue", "event_kind": "bug"}) is None
    assert lib.event_identity({"source": "issue", "event_kind": "bug", "class_key": 7}) is None
    base = {"source": "issue", "event_kind": "bug", "class_key": "k"}
    assert lib.event_identity(base) == ("issue", "bug", "k")
    upgrade = dict(base, conversion_upgrade=True, ref="#358")
    assert lib.event_identity(upgrade) == ("issue", "bug", "k", "conversion_upgrade", "#358")
    assert lib.event_identity(dict(base, conversion_upgrade=True)) == (
        "issue", "bug", "k", "conversion_upgrade", "",
    )


def test_conversion_upgrade_is_not_a_recurrence_but_refreshes_the_stamp() -> None:
    # #358 tripwire response: an explicit conversion_upgrade=true re-record is
    # artifact work, not a new occurrence — it must not be listed as a
    # falsified conversion. It refreshes the conversion stamp, so a LATER
    # recurrence still falsifies the upgraded artifact.
    upgraded_only = [
        ts_event(1, class_key="upgraded", converted=True, durable_kind="retro_lesson"),
        ts_event(7, class_key="upgraded", converted=True, durable_kind="gate", conversion_upgrade=True),
    ]
    assert lib.falsified_conversions(upgraded_only) == []

    recurred_after_upgrade = upgraded_only + [
        ts_event(9, class_key="upgraded", converted=False, durable_kind="none"),
    ]
    [entry] = lib.falsified_conversions(recurred_after_upgrade)
    assert entry["converted_ts"] == "2026-06-07T00:00:00Z"  # the upgrade is what got falsified
    assert entry["recurrence_ts"] == "2026-06-09T00:00:00Z"


def test_conversion_upgrade_annotates_but_does_not_clear_falsified_entry() -> None:
    # The #358 shape itself: converted -> recurred -> artifact upgraded. The
    # falsified entry stays (the tripwire response contract clears nothing) but
    # carries the upgrade annotation so the response is visible in the report.
    events = [
        ts_event(1, class_key="c", converted=True, durable_kind="retro_lesson"),
        ts_event(5, class_key="c", converted=False, durable_kind="none", ref="#301"),
        ts_event(9, class_key="c", converted=True, durable_kind="gate", conversion_upgrade=True, ref="#358"),
    ]
    [entry] = lib.falsified_conversions(events)
    assert entry["recurrence_ts"] == "2026-06-05T00:00:00Z"
    assert entry["upgraded_ts"] == "2026-06-09T00:00:00Z"
    assert entry["upgraded_ref"] == "#358"

    # The in-window tripwire still trips on the recurrence ts: the upgrade
    # annotates, it does not clear.
    padding = [
        ts_event(day, class_key=f"ok{day}", converted=True, durable_kind="gate")
        for day in range(10, 20)
    ]
    target = lib.evaluate_target(events + padding)
    assert target["status"] == "not-met"
    assert target["reasons"] == ["falsified conversion in window (tripwire)"]


def test_conversion_upgrade_excluded_from_rates_and_window_denominator() -> None:
    # Upgrade events are always converted=true artifact-work records; counting
    # them would let tripwire responses inflate the conversion rate.
    events = [
        ts_event(1, class_key="a", converted=True, durable_kind="gate"),
        ts_event(2, class_key="b", converted=False, durable_kind="none"),
        ts_event(3, class_key="a", converted=True, durable_kind="gate", conversion_upgrade=True, ref="#358"),
    ]
    payload = lib.aggregate(events)
    assert payload["total_events"] == 3
    assert payload["seed_excluded"]["total"] == 2
    assert payload["seed_excluded"]["converted"] == 1
    assert payload["seed_excluded"]["rate"] == 0.5
    target = lib.evaluate_target(events)
    assert target["window"]["total"] == 2


def test_conversion_upgrade_render_text_shows_upgrade_annotation(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    write_ledger(
        ledger,
        [
            ts_event(1, class_key="c", converted=True, durable_kind="retro_lesson"),
            ts_event(5, class_key="c", converted=False, durable_kind="none"),
            ts_event(9, class_key="c", converted=True, durable_kind="gate", conversion_upgrade=True, ref="#358"),
        ],
    )
    result = run_script("aggregate_rca_ledger.py", "--ledger", str(ledger))
    assert result.returncode == 0, result.stderr
    assert "c: converted 2026-06-01, recurred 2026-06-05 (artifact upgraded 2026-06-09, #358)" in result.stdout


def test_conversion_upgrade_schema_requires_converted(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    write_raw(
        bad,
        [json.dumps(event(converted=False, durable_kind="none", conversion_upgrade=True))],
    )
    assert run_script("validate_rca_ledger.py", "--ledger", str(bad)).returncode == 1

    ok = tmp_path / "ok.jsonl"
    write_ledger(ok, [event(conversion_upgrade=True)])  # converted=True in the base event
    assert run_script("validate_rca_ledger.py", "--ledger", str(ok)).returncode == 0


def test_conversion_upgrade_recorder_flag_round_trip_and_distinct_identity(tmp_path: Path) -> None:
    # The upgrade re-records an existing (source, event_kind, class_key)
    # identity triple, so the recorder must append it rather than refuse it as
    # a duplicate; its identity carries the redesign ref.
    ledger = tmp_path / "ledger.jsonl"
    original = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue", "--event-kind", "weak_proof",
        "--converted", "--durable-kind", "retro_lesson",
        "--class-key", "upgrade-class", "--ref", "#251",
    )
    assert original.returncode == 0, original.stderr

    upgrade = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue", "--event-kind", "weak_proof",
        "--converted", "--durable-kind", "gate", "--conversion-upgrade",
        "--class-key", "upgrade-class", "--ref", "#358", "--json",
    )
    assert upgrade.returncode == 0, upgrade.stderr
    assert json.loads(upgrade.stdout)["appended"] is True
    records = lib.read_events(ledger)
    assert len(records) == 2
    assert records[1]["conversion_upgrade"] is True

    # Re-running the same upgrade is the idempotent duplicate no-op.
    duplicate = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue", "--event-kind", "weak_proof",
        "--converted", "--durable-kind", "gate", "--conversion-upgrade",
        "--class-key", "upgrade-class", "--ref", "#358", "--json",
    )
    assert duplicate.returncode == 0, duplicate.stderr
    assert json.loads(duplicate.stdout)["status"] == "duplicate"
    assert len(lib.read_events(ledger)) == 2

    # An upgrade without --converted is refused before any write.
    invalid = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue", "--event-kind", "weak_proof",
        "--conversion-upgrade", "--class-key", "upgrade-class", "--ref", "#359",
    )
    assert invalid.returncode == 1
    assert len(lib.read_events(ledger)) == 2

    # An upgrade without --ref is refused: the redesign ref is the upgrade's
    # idempotency identity; without it a second ref-less upgrade would be
    # silently dropped as a duplicate.
    refless = run_script(
        "record_rca_event.py",
        "--ledger", str(ledger),
        "--source", "issue", "--event-kind", "weak_proof",
        "--converted", "--durable-kind", "gate", "--conversion-upgrade",
        "--class-key", "upgrade-class",
    )
    assert refless.returncode == 1
    assert "--conversion-upgrade requires --ref" in refless.stderr
    assert len(lib.read_events(ledger)) == 2


def test_target_parse_ts_defensive_branches_skip_bad_timestamps() -> None:
    # Schema-valid ledgers always carry RFC3339 ts; the evaluator still
    # tolerates raw events with a missing or malformed ts by skipping them
    # instead of crashing or letting them anchor the window.
    assert lib._parse_ts(None) is None
    assert lib._parse_ts("not-a-dateZ") is None
    bad_ts: list[dict[str, object]] = [
        {"class_key": "no-ts", "converted": False},
        event(ts="not-a-dateZ", class_key="bad-ts", converted=False, durable_kind="none"),
    ]
    fresh = [
        ts_event(day, class_key=f"new{day}", converted=True, durable_kind="gate")
        for day in range(1, 11)
    ]
    target = lib.evaluate_target(bad_ts + fresh)
    assert target["window"]["total"] == 10
    assert target["status"] == "met"


def test_target_window_excludes_events_older_than_28_days() -> None:
    stale = [
        event(ts="2026-01-01T00:00:00Z", class_key=f"old{i}", converted=False, durable_kind="none")
        for i in range(5)
    ]
    fresh = [
        ts_event(day, class_key=f"new{day}", converted=True, durable_kind="gate")
        for day in range(1, 11)
    ]
    target = lib.evaluate_target(stale + fresh)
    # The stale unconverted events (and any stale recurrence) fall outside the
    # rolling window anchored on the latest live event, so the verdict is met.
    assert target["window"]["total"] == 10
    assert target["status"] == "met"


def test_target_render_text_reports_floor_falsified_and_status(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    write_ledger(
        ledger,
        [ts_event(1, class_key="c", converted=True, durable_kind="gate"),
         ts_event(5, class_key="c", converted=False, durable_kind="none")],
    )
    result = run_script("aggregate_rca_ledger.py", "--ledger", str(ledger))
    assert result.returncode == 0, result.stderr
    text = result.stdout
    assert "target (#184, set 2026-06-13): >=70% rolling 28d" in text
    assert "falsified conversions (all-time, tripwire input): 1" in text
    assert "c: converted 2026-06-01, recurred 2026-06-05" in text
    assert "status: insufficient-n" in text


def test_target_committed_ledger_payload_is_structurally_judged() -> None:
    # Structural assertions only: the committed ledger keeps accruing, so the
    # live status/rate must not be pinned here (slice-2 retro lesson: never
    # reuse the committed ledger as a value fixture).
    payload = lib.aggregate(lib.read_events(COMMITTED_LEDGER))
    target = payload["target"]
    assert target["floor"] == 0.7
    assert target["status"] in {"no-live-events", "insufficient-n", "met", "not-met"}
    for entry in target["falsified_conversions"]:
        assert entry["converted_ts"] < entry["recurrence_ts"]
