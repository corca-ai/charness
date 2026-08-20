"""Every state the SessionStart lesson block can reach, over /tmp fixture repos.

The defect this wiring fixes was that the evaluating half of the lesson lifecycle
had zero production callers while the continuity gate reported `violations=0` over
it. The negative cases below are therefore load-bearing, not padding: a repo that
never opted in must pay nothing and hear nothing, and a repo that DID opt in must
hear about every failure rather than silently lose its lesson list.

Never touches the authoring repo's real `charness-artifacts/retro/lesson-ledger.json`:
it is append-only with a committed-prefix check, so a bad write is unrepairable.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import session_start_lesson_context as lesson_context
import yaml

from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import lesson_ledger_lib as ledger_lib
from scripts import lesson_score_outcome_lib as outcome_lib
from scripts import render_lesson_selection_preview as _preview
from tests.script_main import run_loaded_script_main
from tests.test_lesson_ledger import _ledger, _retro

ROOT = Path(__file__).resolve().parents[1]
REFRESH_SCRIPT = ROOT / "skills/public/retro/scripts/refresh_recent_lessons.py"
INIT_LEDGER_SCRIPT = ROOT / "scripts/init_lesson_ledger.py"
OPEN_SESSION_SCRIPT = ROOT / "scripts/open_lesson_session.py"


def _refresh(repo: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(REFRESH_SCRIPT), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def _declare(repo: Path, session_id: str) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(OPEN_SESSION_SCRIPT),
            "--repo-root",
            str(repo),
            "--session-id",
            session_id,
            "--seed",
            session_id,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def _seeded_repo(tmp_path: Path) -> Path:
    """A consuming-repo shape that opted in AND has one seeded lesson."""
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)
    _refresh(tmp_path)
    return tmp_path


def _multi_lesson_repo(tmp_path: Path, slugs: tuple[str, ...]) -> Path:
    """A repo whose preview renders MORE THAN ONE item.

    The single-lesson `_seeded_repo` cannot observe truncation or reordering of
    the injected preview: at one item, `preview == preview[:1]`, so every
    "verbatim bytes" assertion over it is vacuously true. The verbatim contract is
    the load-bearing one — `open_lesson_session.py` digests these exact bytes into
    the emission receipt — so it needs a fixture where breaking it is visible.
    """
    retro = tmp_path / "charness-artifacts/retro/source.md"
    retro.parent.mkdir(parents=True, exist_ok=True)
    retro.write_text(
        "# Session Retro\nDate: 2026-08-12\n\n## Waste\n\n"
        + "".join(f"- lesson about {slug} (recurrence-class: {slug})\n" for slug in slugs),
        encoding="utf-8",
    )
    source = "charness-artifacts/retro/source.md"
    (tmp_path / "charness-artifacts/retro/lesson-ledger.json").write_text(
        json.dumps(
            {
                "kind": ledger_lib.KIND,
                "schema_version": ledger_lib.SCHEMA_VERSION,
                "transitions": [
                    {
                        "sequence": index,
                        "transition_id": f"seed-{slug}",
                        "lesson_id": slug,
                        "source_retro": source,
                    }
                    for index, slug in enumerate(slugs, start=1)
                ],
                "active_lesson_budget": ledger_lib.ACTIVE_LESSON_BUDGET,
                "lifecycle_events": [],
                "session_events": [],
                "score_events": [],
                "lessons": {
                    slug: {
                        "source_retro": source,
                        "transition_id": f"seed-{slug}",
                        "score_total": 0,
                        "score_count": 0,
                        "outcome_counts": outcome_lib.outcome_counts([]),
                        "state": "active",
                        "last_lifecycle_event_id": None,
                    }
                    for slug in slugs
                },
            }
        ),
        encoding="utf-8",
    )
    _refresh(tmp_path)
    return tmp_path


def _opted_in_empty_repo(tmp_path: Path) -> Path:
    """Opted in via the real bootstrap, but no `recurrence-class:` bullet yet."""
    result = subprocess.run(
        [sys.executable, str(INIT_LEDGER_SCRIPT), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    _refresh(tmp_path)
    return tmp_path


def test_no_ledger_is_not_configured_and_runs_no_subprocess(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The opt-out path must cost one `is_file()`, never the ~0.85s preview.

    "Never run the preview to discover that a repo has no ledger" is the whole
    reason the gate exists, so this asserts the absence of the subprocess, not
    just the absence of the text.
    """
    calls: list[object] = []
    monkeypatch.setattr(lesson_context.subprocess, "run", lambda *a, **k: calls.append(a))

    context = lesson_context.build_lesson_context(tmp_path, {"session_id": "s"})

    assert context["state"] == lesson_context.STATE_NOT_CONFIGURED
    assert context["text"] is None
    assert calls == []


def test_undiscoverable_repo_root_is_not_configured_and_silent() -> None:
    context = lesson_context.build_lesson_context(None, {})
    assert context["state"] == lesson_context.STATE_NOT_CONFIGURED
    assert context["text"] is None


def test_opted_in_repo_injects_verbatim_preview_bytes_and_the_declare_command(
    tmp_path: Path,
) -> None:
    """The injected bytes must be exactly what a declared session would freeze.

    `render_preview_bytes` output is the `charness.lesson-session-preview.text.v1`
    payload `open_lesson_session.py` writes into the bundle and digests into the
    receipt, so a truncated or reformatted injection would make a later receipt
    attest bytes nobody saw.
    """
    repo = _seeded_repo(tmp_path)
    # In-process rather than a spawned interpreter: the boundary-bypass ratchet counts
    # this file as convertible because the target imports cleanly, and the migration is
    # what pushed it to a subprocess (the renderer's bytes moved into a payload key, so
    # the test started running the CLI to read stdout). Same main(), same stdout.
    rendered = run_loaded_script_main(
        "render_lesson_selection_preview.py",
        _preview,
        "--repo-root",
        str(repo),
        "--seed",
        "2026-01-01-host-1",
    )
    assert rendered.returncode == 0, rendered.stderr
    # The renderer's bytes now travel INSIDE its payload as `preview_text`; that is
    # the `charness.lesson-session-preview.text.v1` string, not the YAML wrapper.
    preview_text = yaml.safe_load(rendered.stdout)["preview_text"]

    context = lesson_context.build_lesson_context(repo, {"session_id": "host-1"})

    assert context["state"] == lesson_context.STATE_EVALUATED
    assert context["eligible_lessons_present"] is True
    assert preview_text.rstrip() in context["text"]
    assert context["declare_command"] in context["text"]
    assert "open_lesson_session.py" in context["declare_command"]
    assert f"--session-id {context['session_id']} --seed {context['session_id']}" in (
        context["declare_command"]
    )
    # The honest ceiling has to travel WITH the payload, not live only in a docstring.
    assert "EMITTED" in context["text"]
    assert "presentation-unproven" in context["text"]
    assert context["unclaimed_sessions"] == []


def test_session_start_surfaces_unclaimed_session_without_claiming_or_writing_it(
    tmp_path: Path,
) -> None:
    repo = _seeded_repo(tmp_path)
    _declare(repo, "2026-08-14-host-1")
    ledger = repo / "charness-artifacts/retro/lesson-ledger.json"
    before = ledger.read_bytes()

    context = lesson_context.build_lesson_context(repo, {"session_id": "host-2"})

    assert context["unclaimed_sessions"] == [
        {
            "session_id": "2026-08-14-host-1",
            "bundle_path": (
                "charness-artifacts/retro/lesson-session-receipts/2026-08-14-host-1.md"
            ),
        }
    ]
    assert "Outstanding declared lesson session" in context["text"]
    assert "2026-08-14-host-1" in context["text"]
    assert "does not claim, score, or disposition it" in context["text"]
    assert ledger.read_bytes() == before


def test_session_start_keeps_routing_failure_loud_instead_of_calling_it_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _seeded_repo(tmp_path)

    def fail_router(_repo: Path) -> dict[str, object]:
        raise OSError("router unavailable")

    monkeypatch.setattr(lesson_context, "_run_unclaimed_sessions", fail_router)

    context = lesson_context.build_lesson_context(repo, {"session_id": "host-1"})

    assert context["state"] == lesson_context.STATE_EVALUATED
    assert context["unclaimed_sessions"] is None
    assert "router unavailable" in context["unclaimed_sessions_cause"]
    assert "could not establish" in context["text"]
    assert "no outstanding work" in context["text"]


def test_every_selected_lesson_is_injected_verbatim_and_in_order(tmp_path: Path) -> None:
    """Truncation, reordering, or a top-N slice must fail a test, not ship.

    `open_lesson_session.py` digests `render_preview_bytes` output into the
    emission receipt, so injecting a SUBSET of it would make a later receipt
    attest bytes nobody was shown while the single-item fixture stayed green. Four
    seeded lessons make the whole rendered block observable.
    """
    slugs = ("alpha-lesson", "beta-lesson", "gamma-lesson", "delta-lesson")
    repo = _multi_lesson_repo(tmp_path, slugs)
    # The seed the module itself would derive. A hardcoded seed would silently
    # compare two DIFFERENT shuffles and only pass while the fixture holds one item.
    seed = lesson_context.derive_session_id({"session_id": "host-1"}, repo_root=repo)
    # In-process, same reason as the sibling call above: the target imports cleanly, so
    # spawning an interpreter to read its stdout is the boundary bypass the ratchet
    # flags. Same main(), same stdout.
    rendered = run_loaded_script_main(
        "render_lesson_selection_preview.py",
        _preview,
        "--repo-root",
        str(repo),
        "--seed",
        seed,
    )
    assert rendered.returncode == 0, rendered.stderr
    preview_text = yaml.safe_load(rendered.stdout)["preview_text"]
    item_lines = [line for line in preview_text.splitlines() if line.startswith("- ")]
    assert len(item_lines) == len(slugs), rendered.stdout

    context = lesson_context.build_lesson_context(repo, {"session_id": "host-1"})

    # Contiguous and in the renderer's own order, not merely "each id appears".
    assert preview_text.rstrip() in context["text"]
    assert context["preview_byte_count"] == len(preview_text.encode("utf-8"))
    injected = [line for line in context["text"].splitlines() if line.startswith("- ")]
    assert injected == item_lines


def test_the_preview_runs_against_its_own_tree_despite_a_hostile_repo_root_export(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A stale `CHARNESS_REPO_ROOT` in the host env must not break the loop.

    `runtime_bootstrap` honors that variable when locating the `scripts.` package,
    so a session that exported it for an unrelated repo would make the preview
    child die with `ModuleNotFoundError: No module named 'scripts'` and report
    `not-established` — a failure caused by the CALLER's environment, not by the
    repo's state. `_run_preview` pins it to the tree this script lives in.
    """
    repo = _seeded_repo(tmp_path / "repo")
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    monkeypatch.setenv("CHARNESS_REPO_ROOT", str(unrelated))

    context = lesson_context.build_lesson_context(repo, {"session_id": "host-1"})

    assert context["state"] == lesson_context.STATE_EVALUATED, context.get("cause")
    assert context["eligible_lessons_present"] is True


def test_a_raising_preview_reports_its_cause_not_the_traceback_banner() -> None:
    """`not-established` has to name something an operator can act on.

    The preview child fails by raising, and a Python traceback's FIRST line is the
    constant `Traceback (most recent call last):`. Publishing that as the cause
    gives every distinct failure — invalid ledger, stale index, unreadable JSON —
    the same eight uninformative words.
    """
    traceback_text = (
        "Traceback (most recent call last):\n"
        '  File "render_lesson_selection_preview.py", line 30, in main\n'
        "    build_lesson_selection_preview(...)\n"
        "ValueError: lesson ledger invalid: invalid JSON: Expecting value\n"
    )
    assert lesson_context._first_line(traceback_text) == (
        "ValueError: lesson ledger invalid: invalid JSON: Expecting value"
    )
    # A plain one-line diagnostic is still reported as itself.
    assert lesson_context._first_line("\n  usage: bad flag\n") == "usage: bad flag"
    assert lesson_context._first_line("  \n") == "(no diagnostic output)"


def test_opted_in_repo_with_no_seeded_lesson_says_so_and_names_the_next_step(
    tmp_path: Path,
) -> None:
    repo = _opted_in_empty_repo(tmp_path)

    context = lesson_context.build_lesson_context(repo, {"session_id": "host-1"})

    assert context["state"] == lesson_context.STATE_EVALUATED
    assert context["eligible_lessons_present"] is False
    assert "0 eligible lessons" in context["text"]
    assert lesson_context.seed_lesson_next_step(repo) in context["text"]
    assert "recurrence-class:" in context["text"]


def test_the_seed_next_step_names_a_command_the_reading_repo_actually_has(
    tmp_path: Path,
) -> None:
    """A consuming repo has no `scripts/`, so a bare `scripts/...` is unrunnable there.

    This is the #624 class ("instructs an action the reader cannot perform") as it
    reappeared inside the #625 fix: the sentence shipped as a constant naming one
    spelling, and its whole audience is a repo that just opted in -- which, for a
    consumer, is a repo with no `scripts/` at all.
    """
    consumer = _opted_in_empty_repo(tmp_path)

    step = lesson_context.seed_lesson_next_step(consumer)

    commands = [part for part in step.split("`") if part.startswith("python3 ")]
    assert commands, f"next step names no runnable command: {step}"
    for command in commands:
        named = Path(command.split()[1])
        # Resolved against the READING repo, which is what the sentence addresses.
        # `Path(named).is_file()` alone would not do it: a bare
        # `scripts/seed_lesson_transitions.py` is cwd-relative, so it is TRUE whenever
        # the suite runs from the authoring repo root -- meaning that assertion would
        # have PASSED on the exact defect this test is named after. A round-2 review
        # caught that; the assertion now demands a path the consumer can actually reach.
        assert named.is_absolute(), f"next step names {named}, relative to the reader's cwd"
        assert named.is_file(), f"next step names {named}, which does not exist"


def test_stale_or_missing_selection_index_is_not_established_and_still_speaks(
    tmp_path: Path,
) -> None:
    """The likeliest real consumer failure, and the one silence would hide.

    `check_lesson_selection_index` byte-compares the persisted index against what
    the RUNNING copy rebuilds, so a consumer whose index was written by an older
    plugin version fails here. Reporting nothing would recreate exactly the "green
    over a capability that was never installed" defect this slice exists to fix.
    """
    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)  # opted in, but no lesson-selection-index.json written

    context = lesson_context.build_lesson_context(tmp_path, {"session_id": "host-1"})

    assert context["state"] == lesson_context.STATE_NOT_ESTABLISHED
    assert context["text"] is not None
    assert "not-established" in context["text"]
    assert "no lessons owed" in context["text"]
    assert "refresh_recent_lessons.py" in context["remediation"]
    assert context["remediation"] in context["text"]


def test_preview_timeout_is_not_established_and_names_the_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seeded_repo(tmp_path)

    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == lesson_context.LESSON_PREVIEW_TIMEOUT_SECONDS
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(lesson_context.subprocess, "run", timeout)

    context = lesson_context.build_lesson_context(tmp_path, {"session_id": "host-1"})

    assert context["state"] == lesson_context.STATE_NOT_ESTABLISHED
    assert str(lesson_context.LESSON_PREVIEW_TIMEOUT_SECONDS) in context["cause"]


def test_missing_preview_script_is_not_established_not_silent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A charness install shipped without the renderer is a broken loop, not an opt-out."""
    _seeded_repo(tmp_path)
    monkeypatch.setattr(lesson_context, "_sibling_script", lambda name: tmp_path / "absent" / name)

    context = lesson_context.build_lesson_context(tmp_path, {"session_id": "host-1"})

    assert context["state"] == lesson_context.STATE_NOT_ESTABLISHED
    assert lesson_context.PREVIEW_SCRIPT_NAME in context["cause"]


def test_suggested_session_id_grammar_matches_the_ledger_validator() -> None:
    """The stdlib-only copy keeps the lexical grammar and owns the sentinel exclusion.

    `session_start_lesson_context` cannot import the continuity library (it runs
    inside a host SessionStart path and must not be able to fail on a repo import),
    so the regex is copied. The ledger's regex accepts the `none` sentinel because
    the validator excludes it at the semantic boundary; the hook excludes it before
    producing an operator command, so it cannot suggest a known refusal.
    """
    for value in ("host-1", "2026-08-14-host-1", "a.b_c-2"):
        assert lesson_context._SESSION_ID.fullmatch(value)
        assert continuity._SESSION_ID.fullmatch(value)
    assert lesson_context._SESSION_ID.fullmatch("none") is None
    assert continuity._SESSION_ID.fullmatch("none")


def test_session_id_is_the_seed_and_falls_back_when_the_host_id_is_unusable(
    tmp_path: Path,
) -> None:
    usable = lesson_context.derive_session_id(
        {"session_id": "0f2e-4a", "source": "startup"}, repo_root=tmp_path, today="2026-08-14"
    )
    assert usable == "2026-08-14-0f2e-4a"
    continuity.validate_session_id(usable)

    hostile = lesson_context.derive_session_id(
        {"session_id": "a/b c", "source": "startup"}, repo_root=tmp_path, today="2026-08-14"
    )
    assert hostile != "2026-08-14-a/b c"
    continuity.validate_session_id(hostile)

    absent = lesson_context.derive_session_id(
        {"source": "startup"}, repo_root=tmp_path, today="2026-08-14"
    )
    continuity.validate_session_id(absent)
    assert absent.startswith("2026-08-14-")
    # Deterministic for one repo+source pair, so the id the hook prints is the id
    # the operator can retype after scrollback is gone.
    assert absent == lesson_context.derive_session_id(
        {"source": "startup"}, repo_root=tmp_path, today="2026-08-14"
    )
    reserved = lesson_context.derive_session_id(
        {"session_id": lesson_context.RESERVED_SESSION_ID, "source": "startup"},
        repo_root=tmp_path,
        today="2026-08-14",
    )
    assert reserved == absent


def test_building_the_context_never_writes_to_the_ledger(tmp_path: Path) -> None:
    """The hook path must be read-only. A ledger write here would emit one
    `unclaimed-emission` violation per non-retro session, forever."""
    repo = _seeded_repo(tmp_path)
    ledger_path = repo / "charness-artifacts/retro/lesson-ledger.json"
    before = ledger_path.read_bytes()
    receipts = repo / "charness-artifacts/retro/lesson-session-receipts"

    lesson_context.build_lesson_context(repo, {"session_id": "host-1"})

    assert ledger_path.read_bytes() == before
    assert not receipts.exists()


@pytest.mark.parametrize(
    ("factory", "expected_state", "expected_exit"),
    [
        (lambda path: path, lesson_context.STATE_NOT_CONFIGURED, 0),
        (_seeded_repo, lesson_context.STATE_EVALUATED, 0),
        (lambda path: (_retro(path, "source.md", "a"), _ledger(path), path)[-1],
         lesson_context.STATE_NOT_ESTABLISHED, lesson_context.UNDETERMINED_EXIT),
    ],
)
def test_cli_exits_three_only_when_undetermined(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    factory,
    expected_state: str,
    expected_exit: int,
) -> None:
    """Same byte contract as `check_auto_trigger.py`: ANY nonzero means "not a no".

    `not-configured` exits 0 because it is a real recorded answer (this repo opted
    out); `not-established` exits 3 because the probe could not tell.
    """
    repo = factory(tmp_path)

    code = lesson_context.main(["--repo-root", str(repo), "--session-id", "host-1"])

    assert code == expected_exit
    assert yaml.safe_load(capsys.readouterr().out)["state"] == expected_state


def test_the_seed_command_targets_the_repo_it_was_given_not_the_readers_cwd(
    tmp_path: Path,
) -> None:
    """The repo-local branch, which round 3 found untested and mis-targeting.

    `_seed_command` used the root to CHOOSE the branch and then emitted `--repo-root .`,
    so `init_lesson_ledger.py --repo-root <other checkout>` printed a next step whose `.`
    resolves to the operator's cwd -- a different repo than the one just initialized.
    """
    repo_local = tmp_path / "authoring"
    (repo_local / "scripts").mkdir(parents=True)
    (repo_local / "scripts" / lesson_context.SEED_SCRIPT_NAME).write_text("", encoding="utf-8")

    step = lesson_context.seed_lesson_next_step(repo_local)

    assert f"--repo-root {repo_local}" in step
    assert "--repo-root ." not in step


def test_the_refresh_command_resolves_against_the_tree_it_runs_from(tmp_path: Path) -> None:
    """`_refresh_command` names a path that exists in THIS layout.

    Same class as the seed command: a consuming repo has no `skills/public/...`, so a
    hardcoded spelling would name a file the reader does not have.
    """
    text = lesson_context._refresh_command(tmp_path)

    named = Path(text.split()[1])
    assert named.is_absolute() and named.is_file(), text
    assert f"--repo-root {tmp_path}" in text


def test_the_refresh_command_falls_back_to_a_placeholder_rather_than_a_wrong_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Neither layout resolved: emit a bare-token placeholder, not a wrong path.

    This is the branch for a tree shaped like neither the authoring repo nor the
    installed plugin. A reader can substitute a placeholder; a reader cannot debug a
    confidently-printed path that is simply absent. The token is BARE on purpose:
    a `<...>` placeholder pasted into a shell becomes a redirection error, and
    `skills/public/` is a spelling no consuming tree has (#632). Driven by pointing
    the module at a tree that has no refresh script, because both real layouts DO
    resolve here.
    """
    monkeypatch.setattr(lesson_context, "_script_tree_root", lambda: tmp_path)

    text = lesson_context._refresh_command(tmp_path)

    assert text.startswith("python3 CHARNESS_PLUGIN_DIR/skills/retro/scripts/")
    assert "<" not in text
    assert f"--repo-root {tmp_path}" in text


def _stub_router_process(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *, returncode: int = 0, stderr: bytes = b"") -> None:
    router = tmp_path / "plan_retro_run.py"
    router.write_text("# fixture router\n", encoding="utf-8")
    monkeypatch.setattr(lesson_context, "_retro_plan_script", lambda: router)
    monkeypatch.setattr(
        lesson_context.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], returncode, stdout=b"ignored", stderr=stderr
        ),
    )


def test_unclaimed_router_reports_missing_router_script(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lesson_context, "_retro_plan_script", lambda: None)

    with pytest.raises(OSError, match="no `plan_retro_run.py`"):
        lesson_context._run_unclaimed_sessions(tmp_path)


def test_unclaimed_router_reports_child_exit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_router_process(monkeypatch, tmp_path, returncode=7, stderr=b"router failed\n")

    with pytest.raises(OSError, match="exited 7: router failed"):
        lesson_context._run_unclaimed_sessions(tmp_path)


def test_unclaimed_router_reports_unreadable_payload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_router_process(monkeypatch, tmp_path)
    monkeypatch.setattr(lesson_context, "_parse_preview", lambda _output: (_ for _ in ()).throw(ValueError("bad payload")))

    with pytest.raises(ValueError, match="emitted unreadable output.*bad payload"):
        lesson_context._run_unclaimed_sessions(tmp_path)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "no `lesson_session` routing payload"),
        (
            {"lesson_session": {"state": "not-established", "sessions": []}},
            "retro routing is not established",
        ),
        (
            {
                "lesson_session": {
                    "state": lesson_context.STATE_EVALUATED,
                    "sessions": [{"session_id": "only-id"}],
                }
            },
            "without id or frozen bundle path",
        ),
        (
            {"lesson_session": {"state": lesson_context.STATE_EVALUATED, "sessions": []}},
            "claimed evaluated state but emitted no sessions",
        ),
    ],
)
def test_unclaimed_router_rejects_unestablished_shapes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, payload: dict[str, object], message: str
) -> None:
    _stub_router_process(monkeypatch, tmp_path)
    monkeypatch.setattr(lesson_context, "_parse_preview", lambda _output: payload)

    with pytest.raises(ValueError, match=message):
        lesson_context._run_unclaimed_sessions(tmp_path)


def test_unclaimed_router_preserves_the_explicit_no_session_answer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_router_process(monkeypatch, tmp_path)
    monkeypatch.setattr(
        lesson_context,
        "_parse_preview",
        lambda _output: {"lesson_session": {"configuration_status": "no-unclaimed-session"}},
    )

    assert lesson_context._run_unclaimed_sessions(tmp_path) == {
        "state": "no-unclaimed-session",
        "sessions": [],
    }


def test_routing_details_keeps_not_established_distinct_from_empty() -> None:
    text, sessions = lesson_context._routing_details(
        Path("/repo"), {"state": "not-established", "cause": "router unavailable"}
    )

    assert sessions is None
    assert "could not establish" in text
    assert "router unavailable" in text


def test_evaluated_context_records_routing_cause_when_no_lessons_are_selected(tmp_path: Path) -> None:
    result = lesson_context._evaluated(
        tmp_path,
        tmp_path / "lesson-ledger.json",
        "session-1",
        {"preview_text": "", "items": []},
        {"state": "not-established", "cause": "router unavailable"},
    )

    assert result["eligible_lessons_present"] is False
    assert result["unclaimed_sessions"] is None
    assert result["unclaimed_sessions_cause"] == "router unavailable"


def test_build_context_carries_routing_failure_into_evaluated_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _seeded_repo(tmp_path)
    monkeypatch.setattr(
        lesson_context,
        "_run_preview",
        lambda _repo, _seed: (0, "ignored", ""),
    )
    monkeypatch.setattr(
        lesson_context,
        "_parse_preview",
        lambda _output: {"preview_text": "- lesson", "items": [{}]},
    )
    monkeypatch.setattr(
        lesson_context,
        "_run_unclaimed_sessions",
        lambda _repo: (_ for _ in ()).throw(OSError("router unavailable")),
    )

    result = lesson_context.build_lesson_context(repo, {"session_id": "host-1"})

    assert result["unclaimed_sessions"] is None
    assert result["unclaimed_sessions_cause"].startswith("OSError: router unavailable")
