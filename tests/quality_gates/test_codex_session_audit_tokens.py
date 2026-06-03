from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from scripts.codex_session_audit_tokens import (
    TOKEN_KEYS,
    aggregate_tokens,
    cost_signal_status,
    token_summary,
)


def line(text: str, ts: str | None = None) -> Any:
    # token_summary only touches `.text` and `.ts`, so a tiny stand-in keeps the
    # unit pinned to this module instead of the full LogLine/audit pipeline.
    return SimpleNamespace(text=text, ts=ts)


COMPLETED = (
    "event.kind=response.completed input_token_count=10 output_token_count=5 "
    "cached_token_count=2 reasoning_token_count=1 tool_token_count=3"
)
SNAPSHOT = (
    "post sampling token usage total_usage_tokens=100 estimated_token_count=80 "
    "auto_compact_scope_tokens=70 auto_compact_scope_limit=200 "
    "full_context_window_limit_reached=false needs_follow_up=false"
)


# --- token_summary: source-kind gate -------------------------------------------------


def test_token_summary_requires_sqlite_source_kind() -> None:
    # source_kind != "sqlite" must short-circuit; this pins the comparison so
    # Eq/ordering/negation mutants of `!= "sqlite"` cannot survive.
    available = token_summary([line(COMPLETED)], "sqlite", "db.sqlite")
    assert available["status"] == "available"

    for non_sqlite in ("tui", "aaa", "zzz", "sqlit", "sqlitee"):
        result = token_summary([line(COMPLETED)], non_sqlite, "src")
        assert result["status"] == "unavailable"
        assert result["signal_class"] == "unavailable"
        assert result["detail"] == "TUI logs do not expose stable token snapshots."


# --- token_summary: empty vs populated branches --------------------------------------


def test_token_summary_unavailable_when_no_token_fields() -> None:
    result = token_summary([line("nothing useful here"), line(COMPLETED.replace("=", " "))], "sqlite", "db")
    assert result["status"] == "unavailable"
    assert result["detail"] == "No stable Codex token snapshot fields found."


def test_token_summary_available_with_only_completed_events() -> None:
    # completed-only: `not completed and not snapshots` is False, so an `and`->`or`
    # or AddNot mutant (which would mark this unavailable) is killed here.
    result = token_summary([line(COMPLETED)], "sqlite", "db")
    assert result["status"] == "available"
    assert result["signal_class"] == "snapshot"
    assert result["source"] == "db"
    assert result["latest_context_snapshots"] == []
    assert result["response_completed_aggregate"]["events"] == 1


def test_token_summary_available_with_only_snapshots() -> None:
    # snapshot-only: the mirror branch that kills the other AddNot/and->or variant.
    result = token_summary([line(SNAPSHOT, ts="t0")], "sqlite", "db")
    assert result["status"] == "available"
    assert result["response_completed_aggregate"]["events"] == 0
    assert len(result["latest_context_snapshots"]) == 1
    assert result["latest_context_snapshots"][0]["total_usage_tokens"] == 100


def test_token_summary_parses_snapshot_bool_fields_by_value() -> None:
    # The bool fields are derived from `match.group("value") == "true"`. Pinning
    # both a true and a false field kills the comparison-operator mutants on that
    # equality (==, !=, <, <=, >, is, is not) for the {true,false} value domain.
    text = (
        "post sampling token usage total_usage_tokens=100 "
        "full_context_window_limit_reached=true needs_follow_up=false"
    )
    snap = token_summary([line(text, ts="t0")], "sqlite", "db")["latest_context_snapshots"][0]
    assert snap["full_context_window_limit_reached"] is True
    assert snap["needs_follow_up"] is False


def test_token_summary_defaults_missing_completed_token_keys_to_zero() -> None:
    # A response.completed line carrying only input_token_count must leave the
    # other token totals at 0 (the `ints.get(key, 0)` default), pinning that
    # default against a NumberReplacer 0->1 mutant.
    text = "event.kind=response.completed input_token_count=7"
    aggregate = token_summary([line(text)], "sqlite", "db")["response_completed_aggregate"]
    assert aggregate["input_token_count"] == 7
    assert aggregate["output_token_count"] == 0
    assert aggregate["cached_token_count"] == 0
    assert aggregate["reasoning_token_count"] == 0
    assert aggregate["tool_token_count"] == 0


def test_token_summary_matches_source_kind_by_value_not_identity() -> None:
    # A dynamically built "sqlite" is value-equal but not the interned literal, so
    # an `!=` -> `is not` mutant would wrongly treat it as non-sqlite. Asserting it
    # still produces an available summary pins value comparison on the source gate.
    dynamic_sqlite = "".join(["sq", "lite"])  # value-equal to "sqlite" but a fresh, non-interned object
    result = token_summary([line(COMPLETED)], dynamic_sqlite, "db")
    assert result["status"] == "available"


def test_token_summary_completed_marker_needs_token_field() -> None:
    # response.completed text without input_token_count must NOT count as completed;
    # this pins the `and "input_token_count" in ints` guard (and->or / AddNot).
    bare = "event.kind=response.completed output_token_count=5"
    result = token_summary([line(bare)], "sqlite", "db")
    assert result["status"] == "unavailable"


def test_token_summary_snapshot_marker_needs_total_usage_tokens() -> None:
    bare = "post sampling token usage estimated_token_count=80"
    result = token_summary([line(bare)], "sqlite", "db")
    assert result["status"] == "unavailable"


# --- token_summary: snapshot tail window (kills NumberReplacer on -10) ----------------


def test_token_summary_keeps_only_last_ten_snapshots_in_order() -> None:
    lines = [
        line(f"post sampling token usage total_usage_tokens={n} estimated_token_count={n}", ts=f"t{n}")
        for n in range(1, 13)
    ]
    result = token_summary(lines, "sqlite", "db")
    tail = result["latest_context_snapshots"]
    assert len(tail) == 10
    # Of 12 snapshots, the last 10 are totals 3..12 in original order.
    assert [snap["total_usage_tokens"] for snap in tail] == list(range(3, 13))


# --- aggregate_tokens ----------------------------------------------------------------


def test_aggregate_tokens_empty_is_all_zero() -> None:
    result = aggregate_tokens([])
    assert result == {key: 0 for key in TOKEN_KEYS} | {"events": 0}


def test_aggregate_tokens_sums_and_defaults_missing_keys_to_zero() -> None:
    # The missing keys must default to 0 (not 1), which pins the `.get(key, 0)`
    # default against a NumberReplacer mutant.
    items = [
        {"input_token_count": 10, "output_token_count": 5},
        {"input_token_count": 2, "tool_token_count": 4},
    ]
    result = aggregate_tokens(items)
    assert result["input_token_count"] == 12
    assert result["output_token_count"] == 5
    assert result["tool_token_count"] == 4
    assert result["cached_token_count"] == 0
    assert result["reasoning_token_count"] == 0
    assert result["events"] == 2


# --- cost_signal_status --------------------------------------------------------------


def test_cost_signal_status_snapshot_branch() -> None:
    available_snapshot = cost_signal_status({"signal_class": "snapshot", "status": "available"})
    assert available_snapshot["snapshot"] == ["sqlite_runtime_token_snapshots"]
    assert "codex_token_snapshots" not in available_snapshot["unavailable"]
    assert available_snapshot["measured"] == ["tool_calls", "turns_with_ids"]
    assert available_snapshot["proxy"] == [
        "command_chars",
        "line_chars",
        "requested_max_output_tokens",
        "repeated_command_families",
    ]


def test_cost_signal_status_non_snapshot_signal_class_clears_snapshot_list() -> None:
    for signal_class in ("unavailable", "aaa", "zzz", "snapshots"):
        result = cost_signal_status({"signal_class": signal_class, "status": "available"})
        assert result["snapshot"] == []


def test_cost_signal_status_marks_codex_snapshots_unavailable_when_not_available() -> None:
    for status in ("unavailable", "aaa", "zzz", "availabl"):
        result = cost_signal_status({"signal_class": "snapshot", "status": status})
        assert "codex_token_snapshots" in result["unavailable"]
    # The available baseline always carries the two fixed unavailable signals.
    baseline = cost_signal_status({"signal_class": "snapshot", "status": "available"})
    assert baseline["unavailable"] == ["full_tool_output_bytes", "session_token_total"]


def test_cost_signal_status_compares_signal_class_and_status_by_value() -> None:
    # Dynamically built strings are value-equal but not the interned literals, so
    # `==`/`!=` -> identity (`is`/`is not`) mutants on the signal_class and status
    # guards would flip these branches. Pinning value comparison kills them.
    dynamic_snapshot = "".join(["snap", "shot"])  # value-equal but non-interned
    dynamic_available = "".join(["avail", "able"])  # value-equal but non-interned
    result = cost_signal_status({"signal_class": dynamic_snapshot, "status": dynamic_available})
    assert result["snapshot"] == ["sqlite_runtime_token_snapshots"]
    assert "codex_token_snapshots" not in result["unavailable"]
