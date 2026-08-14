"""The lesson loop's READ/EVALUATE half, wired end to end over /tmp fixture repos.

Before this slice the write half was fully automated and the read half had zero
production callers, so `check_lesson_evaluation_continuity.py` reported
`not-evaluated/missing-start=3; violations=0` — a green verdict over a capability
that was never installed. These tests pin the three seams that close it: setup
REPORTS the opt-in state without creating it, the retro planner ROUTES to the
session that owes a score, and the ledger still REFUSES a score for a lesson that
was never presented.

Never touches the authoring repo's real ledger: it is append-only with a
committed-prefix check against `git show HEAD:<path>`, so a bad append is
unrepairable. Every write here lands in a pytest tmp_path.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import lesson_evaluation_records_lib as records
from scripts import record_lesson_score as scorer
from tests.script_loader import load_script_module
from tests.test_lesson_ledger import _ledger, _materialize, _payload, _retro, _session_event
from tests.test_retro_plan import run_plan, write_adapter

ROOT = Path(__file__).resolve().parents[1]
SEED_RETRO_MEMORY = ROOT / "skills/public/setup/scripts/seed_retro_memory.py"
REFRESH_SCRIPT = ROOT / "skills/public/retro/scripts/refresh_recent_lessons.py"
OPEN_SESSION_SCRIPT = ROOT / "scripts/open_lesson_session.py"
LEDGER_RELATIVE = "charness-artifacts/retro/lesson-ledger.json"


def _run(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *argv], capture_output=True, text=True, check=False)


def _seeded_repo(repo: Path) -> Path:
    _retro(repo, "source.md", "a")
    _ledger(repo)
    result = _run(str(REFRESH_SCRIPT), "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    return repo


def _declare(repo: Path, session_id: str) -> None:
    result = _run(
        str(OPEN_SESSION_SCRIPT),
        "--repo-root",
        str(repo),
        "--session-id",
        session_id,
        "--seed",
        session_id,
    )
    assert result.returncode == 0, result.stderr


# --- setup: report the opt-in, create nothing -----------------------------


def _seed_retro_memory(repo: Path) -> dict[str, object]:
    result = _run(str(SEED_RETRO_MEMORY), "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_setup_reports_the_lesson_loop_state_and_creates_no_ledger(tmp_path: Path) -> None:
    """`init_lesson_ledger.py` states the opt-in must be an operator command, never
    a side effect of a seam bootstrap, because declaring an evaluator turns on a
    per-retro disposition duty. Setup therefore reports and stops."""
    report = _seed_retro_memory(tmp_path)["lesson_loop"]

    assert report["state"] == "not-configured"
    assert report["created"] is False
    assert not (tmp_path / LEDGER_RELATIVE).exists()
    assert "init_lesson_ledger.py" in report["opt_in_command"]


def test_setup_reports_evaluated_once_the_repo_opted_in(tmp_path: Path) -> None:
    _seeded_repo(tmp_path)

    report = _seed_retro_memory(tmp_path)["lesson_loop"]

    assert report["state"] == "evaluated"
    assert report["created"] is False


def test_setup_reports_not_established_for_an_unreadable_ledger(tmp_path: Path) -> None:
    """An unreadable ledger is not an opt-out. Reporting `not-configured` here
    would be a `triggered: false` from a probe that never ran (#622)."""
    (tmp_path / "charness-artifacts/retro").mkdir(parents=True)
    (tmp_path / LEDGER_RELATIVE).write_text("{ not json", encoding="utf-8")

    report = _seed_retro_memory(tmp_path)["lesson_loop"]

    assert report["state"] == "not-established"
    assert report["undetermined"]


# --- routing: which session THIS retro owes a score for -------------------


def test_routing_is_not_configured_without_a_ledger(tmp_path: Path) -> None:
    payload = records.lesson_session_routing(tmp_path)

    assert payload["state"] == "not-configured"
    assert payload["sessions"] == []
    assert "init_lesson_ledger.py" in payload["opt_in_command"]


def test_routing_is_not_established_when_no_session_was_declared(tmp_path: Path) -> None:
    """A declared evaluator with no presented list has exactly one honest answer,
    and the router emits it from the library constant rather than retyping it."""
    _seeded_repo(tmp_path)

    payload = records.lesson_session_routing(tmp_path)

    assert payload["state"] == "not-established"
    assert payload["configuration_status"] == "no-unclaimed-session"
    assert '"reason":"missing-start"' in payload["honest_disposition"]
    assert payload["sessions"] == []


def test_routing_is_not_established_when_the_ledger_will_not_validate(tmp_path: Path) -> None:
    _seeded_repo(tmp_path)
    (tmp_path / LEDGER_RELATIVE).write_text('{"kind": "wrong"}', encoding="utf-8")

    payload = records.lesson_session_routing(tmp_path)

    assert payload["state"] == "not-established"
    assert payload["configuration_status"] == "ledger-unreadable"
    assert payload["undetermined"]


def test_routing_names_the_declared_session_its_bundle_and_a_runnable_score_command(
    tmp_path: Path,
) -> None:
    _seeded_repo(tmp_path)
    _declare(tmp_path, "2026-08-14-host-1")

    payload = records.lesson_session_routing(
        tmp_path, source_retro="charness-artifacts/retro/2026-08-14-session-retro.md"
    )

    assert payload["state"] == "evaluated"
    session = payload["sessions"][0]
    assert session["session_id"] == "2026-08-14-host-1"
    # The FROZEN bundle, not a newest-file guess: `references/lesson-evaluation.md`
    # requires recovering the explicit bundle before judging effects.
    assert (tmp_path / session["bundle_path"]).is_file()
    assert session["lesson_ids"] == ["a"]
    assert session["existing_score_event_count"] == 0
    command = session["score_command_templates"][0]
    assert "record_lesson_score.py" in command
    assert "--session-id 2026-08-14-host-1" in command
    assert "--lesson-id a" in command
    assert "--source-retro charness-artifacts/retro/2026-08-14-session-retro.md" in command


def test_router_and_gate_agree_about_the_same_declared_session(tmp_path: Path) -> None:
    """The router's `work to do` and the gate's `unclaimed-emission` must name the
    identical session. They share `unclaimed_receipted_sessions`; this pins that
    the two entry points really do reach the same answer over one repo."""
    _seeded_repo(tmp_path)
    _declare(tmp_path, "2026-08-14-host-1")
    checker = load_script_module(
        "check_lesson_continuity_for_wiring", ROOT / "scripts/check_lesson_evaluation_continuity.py"
    )
    from datetime import date

    routed = [item["session_id"] for item in records.lesson_session_routing(tmp_path)["sessions"]]
    report = checker.build_report(tmp_path, as_of=date(2026, 8, 15))
    flagged = sorted(
        item["session_id"] for item in report["violations"] if item["id"] == "unclaimed-emission"
    )

    assert routed == flagged == ["2026-08-14-host-1"]


# --- the retro planner carries the routing ---------------------------------


def test_retro_planner_reports_not_configured_for_a_repo_that_never_opted_in(
    tmp_path: Path,
) -> None:
    write_adapter(tmp_path)

    payload = run_plan(tmp_path)

    assert payload["lesson_session"]["state"] == "not-configured"
    assert payload["lesson_session"]["available"] is True


def test_retro_planner_routes_to_the_declared_session_and_names_the_ordering(
    tmp_path: Path,
) -> None:
    write_adapter(tmp_path)
    _seeded_repo(tmp_path)
    _declare(tmp_path, "2026-08-14-host-1")

    payload = run_plan(tmp_path)

    assert payload["lesson_session"]["state"] == "evaluated"
    assert payload["lesson_session"]["sessions"][0]["session_id"] == "2026-08-14-host-1"
    ordering = [line for line in payload["phase_barriers"] if "lesson_session" in line]
    assert ordering, payload["phase_barriers"]
    assert "append every score FIRST" in ordering[0]


def test_retro_planner_degrades_to_not_established_when_it_cannot_read_the_module(
    tmp_path: Path,
) -> None:
    """An unreadable probe has not established that the repo opted out."""
    write_adapter(tmp_path)
    module = load_script_module(
        "plan_retro_run_for_lesson_wiring", ROOT / "skills/public/retro/scripts/plan_retro_run.py"
    )
    payload = module._repo_module_payload(
        "scripts.no_such_lesson_module",
        lambda _module: {"state": "evaluated"},
        fallback={"state": "not-established", "sessions": []},
    )

    assert payload["state"] == "not-established"
    assert payload["available"] is False
    assert "ModuleNotFoundError" in payload["unavailable_reason"]


# --- the refusal that keeps the loop honest --------------------------------


def _two_lesson_repo(repo: Path) -> Path:
    """Two seeded lessons, one declared session that froze only lesson `a`."""
    _retro(repo, "source.md", "a")
    _retro(repo, "source-b.md", "b")
    payload = _payload()
    payload["transitions"].append(
        {
            "sequence": 2,
            "transition_id": "seed-b",
            "lesson_id": "b",
            "source_retro": "charness-artifacts/retro/source-b.md",
        }
    )
    payload["lessons"]["b"] = copy.deepcopy(payload["lessons"]["a"])
    payload["lessons"]["b"]["source_retro"] = "charness-artifacts/retro/source-b.md"
    payload["lessons"]["b"]["transition_id"] = "seed-b"
    payload["session_events"] = [_session_event(lesson_ids=["a"])]
    path = repo / LEDGER_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_materialize(payload)), encoding="utf-8")
    return repo


def _append(repo: Path, **overrides: object) -> dict[str, object]:
    arguments: dict[str, object] = {
        "repo_root": repo,
        "output_dir": repo / "charness-artifacts/retro",
        "summary_path": repo / "charness-artifacts/retro/recent-lessons.md",
        "event_id": "score-1",
        "session_id": "session-a",
        "lesson_id": "a",
        "source_retro": "charness-artifacts/retro/source.md",
        "score": 1,
        "anchor": None,
    }
    arguments.update(overrides)
    return scorer.append_score(**arguments)


def test_a_lesson_that_was_never_presented_cannot_be_scored(tmp_path: Path) -> None:
    """The residual honesty guarantee of the whole loop.

    Lesson `b` is seeded, active, and cited by a real retro — everything except
    PRESENT in the session's frozen snapshot. `_replay_scores` refuses it, and the
    ledger must be byte-identical afterwards: a rejected score that still mutated
    the file would be worse than no check at all.
    """
    repo = _two_lesson_repo(tmp_path)
    before = (repo / LEDGER_RELATIVE).read_bytes()

    with pytest.raises(ValueError, match="lesson is absent from session"):
        _append(repo, lesson_id="b", source_retro="charness-artifacts/retro/source-b.md")

    assert (repo / LEDGER_RELATIVE).read_bytes() == before

    # And the presented lesson from the same session still scores, so the refusal
    # above is about presentation, not about the fixture being unscoreable.
    assert _append(repo)["lesson_id"] == "a"
    assert (repo / LEDGER_RELATIVE).read_bytes() != before


def test_a_score_naming_an_undeclared_session_is_refused(tmp_path: Path) -> None:
    repo = _two_lesson_repo(tmp_path)
    before = (repo / LEDGER_RELATIVE).read_bytes()

    with pytest.raises(ValueError, match="names unknown session"):
        _append(repo, session_id="never-declared")

    assert (repo / LEDGER_RELATIVE).read_bytes() == before
