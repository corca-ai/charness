"""Optional lesson-ledger lifecycle helpers, wired over /tmp fixture repos.

The default setup, retro planner, and quality/release paths do not emit session
receipts or require retro disposition continuity. The tests that remain here
cover the separately callable ledger/session helpers and their append-only
honesty checks; they are not default or release closeout requirements.

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
from tests.test_retro_plan import write_adapter

ROOT = Path(__file__).resolve().parents[1]
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


# --- solicitation: the questions the routing asks (#627) -------------------


def test_routing_asks_the_harmful_question_and_carries_the_emitted_wording(
    tmp_path: Path,
) -> None:
    """Routing told an author WHERE to score and never WHAT to judge.

    A lesson presented, read, and not acted on produced no signal, so its wording
    was never revised and it returned at the same weight in the same words. These
    are the questions the ledger contract fixed and nothing asked.
    """
    _seeded_repo(tmp_path)
    _declare(tmp_path, "2026-08-14-host-1")

    session = records.lesson_session_routing(tmp_path)["sessions"][0]

    solicitation = session["solicitation"]
    # The harmful arm by name: the contract asks for it explicitly because it is
    # the least volunteered signal, and it is asked FIRST.
    assert "WRONG action" in solicitation["pushed_a_wrong_action"]
    assert "pushed-a-wrong-action" in solicitation["pushed_a_wrong_action"]
    # The two arms a single number used to collapse. `read-but-not-applied` says
    # the lesson may be perfect and never landed; `not-consulted` says it never
    # reached the decision. Different repairs, so they must be asked separately.
    assert "IN VIEW at the decision" in solicitation["read_but_not_applied"]
    assert "never revisit" in solicitation["not_consulted"]
    assert "EVERY outcome requires an anchor" in solicitation["anchor_rule"]
    # And the citation rule the whole #631 repair rests on.
    assert "not the lesson's origin retro" in solicitation["cite_this_retro"]
    # And the counterweight, so the ask cannot be read as "score everything".
    assert "not a health measure" in solicitation["no_score_is_valid"]

    lesson = session["lessons"][0]
    assert lesson["lesson_id"] == "a"
    # The emitted wording, so the judgment is made on the lesson rather than on its
    # slug. `_seeded_repo` writes `useful lesson (recurrence-class: a)`.
    assert lesson["lesson_text"] == "useful lesson"
    assert lesson["already_scored"] is False
    assert session["unscored_lesson_ids"] == ["a"]


def test_scored_lessons_are_marked_so_the_open_question_stays_visible(
    tmp_path: Path,
) -> None:
    _seeded_repo(tmp_path)
    _declare(tmp_path, "2026-08-14-host-1")
    scorer.append_score(
        repo_root=tmp_path,
        output_dir=tmp_path / "charness-artifacts/retro",
        summary_path=tmp_path / "charness-artifacts/retro/recent-lessons.md",
        event_id="score-1",
        session_id="2026-08-14-host-1",
        lesson_id="a",
        source_retro="charness-artifacts/retro/source.md",
        outcome="changed-an-action",
        anchor=(
            "took the measured path here rather than the assumed one, which would have "
            "shipped a false count"
        ),
    )

    session = records.lesson_session_routing(tmp_path)["sessions"][0]

    assert session["lessons"][0]["already_scored"] is True
    assert session["unscored_lesson_ids"] == []
    assert session["existing_score_event_count"] == 1


def test_a_digest_mismatched_bundle_demotes_the_whole_session(tmp_path: Path) -> None:
    """Named for what it PROVES, after a review caught the earlier name claiming
    the opposite ("keeps the routing" while asserting the routing is dropped).

    A bundle whose digest no longer matches invalidates its receipt, so the
    session stops being RECEIPTED and drops out of `sessions` entirely. That is
    the correct answer -- honest routing must not invent a scoreable list from a
    file it just failed to verify -- but it is a DEMOTION, not a degradation that
    preserves routing.
    """
    _seeded_repo(tmp_path)
    _declare(tmp_path, "2026-08-14-host-1")
    bundle = tmp_path / "charness-artifacts/retro/lesson-session-receipts/2026-08-14-host-1.md"
    bundle.write_text("corrupted, no longer digest-matching\n", encoding="utf-8")

    payload = records.lesson_session_routing(tmp_path)

    assert payload["state"] == "not-established"
    assert payload["sessions"] == []
    assert payload["undetermined"]


def test_lesson_wording_containing_the_separator_round_trips_intact(
    tmp_path: Path,
) -> None:
    """Through the real render -> receipt -> parse path, not a reimplementation.

    Real lessons contain ` — ` (the digest uses it constantly), and the parser
    splits on the FIRST occurrence, so the remainder must survive unsplit. The
    other fixture in this file uses a separator-free lesson, which cannot tell a
    correct parse from one that truncates at the first dash.
    """
    path = tmp_path / "charness-artifacts/retro/source.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Session Retro\nDate: 2026-08-12\n\n## Waste\n\n"
        "- **the headline** — the body, which itself contains — a second separator "
        "(recurrence-class: a)\n",
        encoding="utf-8",
    )
    _ledger(tmp_path)
    result = _run(str(REFRESH_SCRIPT), "--repo-root", str(tmp_path))
    assert result.returncode == 0, result.stderr
    _declare(tmp_path, "2026-08-14-host-1")

    session = records.lesson_session_routing(tmp_path)["sessions"][0]

    # Split on the first separator after the ID only: the whole lesson, including
    # both of its own ` — ` separators, survives as the text.
    assert session["lessons"][0]["lesson_text"] == (
        "**the headline** — the body, which itself contains — a second separator"
    )


def test_router_and_gate_agree_about_the_same_declared_session(tmp_path: Path) -> None:
    """The router's `work to do` and the gate's `unclaimed-emission` must name the
    identical session. They share `unclaimed_receipted_sessions`; this pins that
    the two entry points really do reach the same answer over one repo."""
    _seeded_repo(tmp_path)
    _declare(tmp_path, "2026-08-14-host-1")
    checker = load_script_module(
        "check_lesson_continuity_for_wiring", ROOT / "scripts/check_lesson_evaluation_continuity.py"
    )
    from datetime import date, timedelta

    routed = [item["session_id"] for item in records.lesson_session_routing(tmp_path)["sessions"]]
    # `as_of` is DERIVED from today, not pinned to a literal date. The session id
    # says 2026-08-14, but the receipt `_declare` writes is emitted at real now,
    # and `unclaimed_receipted_sessions` compares `emitted < as_of` exclusively.
    # A hardcoded `date(2026, 8, 15)` therefore held only while the real UTC date
    # was still 2026-08-14: at UTC midnight the receipt's emitted date became
    # equal to `as_of`, the gate stopped flagging it, and this test began failing
    # on a clean checkout with nothing changed. Measured on a HEAD worktree at
    # 2026-08-15T00:23Z. Tomorrow is always strictly after any receipt this
    # fixture can emit, so the comparison the test exists to pin is preserved
    # without coupling it to a calendar day.
    report = checker.build_report(tmp_path, as_of=date.today() + timedelta(days=1))
    flagged = sorted(
        item["session_id"] for item in report["violations"] if item["id"] == "unclaimed-emission"
    )

    assert routed == flagged == ["2026-08-14-host-1"]


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
        "outcome": "changed-an-action",
        "anchor": (
            "recorded the encounter against this session's own retro rather than the origin "
            "retro, which would have declared a recurrence that did not happen"
        ),
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
