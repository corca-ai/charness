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
