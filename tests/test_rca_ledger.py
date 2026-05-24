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


# AC4 -------------------------------------------------------------------------
def test_ac4_committed_ledger_both_outcomes_and_empty_baseline() -> None:
    events = lib.read_events(COMMITTED_LEDGER)
    assert all(e.get("seed") is True for e in events)
    converted = [e for e in events if e.get("converted") is True]
    unconverted = [e for e in events if e.get("converted") is False]
    assert converted and unconverted

    payload = lib.aggregate(events)
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
def test_ac7_off_state_banner_na_and_no_baseline_number() -> None:
    payload = json.loads(
        run_script("aggregate_rca_ledger.py", "--repo-root", str(ROOT), "--json").stdout
    )
    assert payload["auto_append"] == "auto_append: OFF (slice 2 not wired)"
    assert payload["auto_append_wired"] is False
    assert payload["seed_excluded"]["rate"] == lib.NA
    assert payload["baseline_rate_available"] is False

    text = run_script("aggregate_rca_ledger.py", "--repo-root", str(ROOT)).stdout
    assert "auto_append: OFF (slice 2 not wired)" in text
    baseline_line = next(line for line in text.splitlines() if "overall: n/a" in line)
    assert "%" not in baseline_line  # no numeric baseline rate printed


# AC8 -------------------------------------------------------------------------
def test_ac8_caught_by_enum_enforced_and_optional(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    write_raw(bad, [json.dumps(event(caught_by="robot"))])
    assert run_script("validate_rca_ledger.py", "--ledger", str(bad)).returncode == 1

    omitted = tmp_path / "ok.jsonl"
    write_ledger(omitted, [event()])  # no caught_by key
    assert "caught_by" not in event()
    assert run_script("validate_rca_ledger.py", "--ledger", str(omitted)).returncode == 0
