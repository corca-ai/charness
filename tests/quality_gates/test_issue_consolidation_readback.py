"""The four consolidation facts that must come from the TRACKER, not from prose.

A consolidated close asserts exactly one thing — the content moved to a destination —
and every way that assertion can be false is a way the work silently evaporates. These
checks were listed as `not_checked_here` for one round and implemented nowhere, which
to a downstream reader looks like handled work; this suite exists so the list stops
being a promise.

The most important test here is the LAST one: a readback that could not run must never
read as a readback that passed.
"""
from __future__ import annotations

import runpy
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills/public/issue/scripts"
_MOD = runpy.run_path(str(_SCRIPTS / "issue_consolidation_readback.py"))
evaluate_destination = _MOD["evaluate_destination"]
verify_consolidation = _MOD["verify_consolidation"]

# Modules this file is the standing coverage for, declared as quoted repo-relative
# paths so `suggest_mutation_coverage_command` can MAP them. The mapper reads
# textual references, and these tests build their paths from a variable
# (`_SCRIPTS / "x.py"`), which matches none of its patterns -- so the changed-line
# coverage gate reported these files unmapped and then blocked on lines this suite
# actually covers. Declaring the mapping is better than making the loader uglier to
# be greppable.
_COVERS = (
    "skills/public/issue/scripts/issue_consolidation_readback.py",
    "skills/public/issue/scripts/issue_state_readback.py",
    "skills/public/issue/scripts/issue_close_comment_floor.py",
    "skills/public/issue/scripts/issue_verify_closeout.py",
    "skills/public/issue/scripts/issue_close.py",
)



def destination(**overrides) -> dict:
    payload = {
        "number": 600,
        "state": "OPEN",
        "body": "Umbrella for the prompt-surface cluster: #555, #556, #557.",
    }
    payload.update(overrides)
    return payload


def check(payload, source=555, dest=600) -> dict:
    return evaluate_destination(payload, source_number=source, destination_number=dest)


def test_a_well_formed_destination_passes() -> None:
    report = check(destination())
    assert report["ok"] is True
    assert report["state"] == "OPEN"
    assert report["names_source"] is True
    assert report["is_chain"] is False


def test_a_missing_destination_is_refused() -> None:
    """Consolidating into a number nobody created loses the issue outright, and a
    typo in an anchor is one keystroke."""
    report = check({})
    assert report["ok"] is False
    assert report["state"] == "missing"
    assert "does not exist" in report["problems"][0]


def test_a_closed_destination_is_refused() -> None:
    """The same evaporation, with a plausible-looking trail: both issues then read
    closed and nothing says one absorbed the other."""
    report = check(destination(state="CLOSED"))
    assert report["ok"] is False
    assert any("not OPEN" in problem for problem in report["problems"])


def test_a_destination_of_unknown_state_is_refused() -> None:
    report = check(destination(state=""))
    assert report["ok"] is False
    assert any("unknown state" in problem for problem in report["problems"])


def test_a_destination_that_does_not_name_the_source_is_refused() -> None:
    """The load-bearing check: it forces "does the content actually live somewhere?"
    without answering "therefore this is resolved", and only an edit to the
    DESTINATION can satisfy it."""
    report = check(destination(body="Umbrella for the cluster."))
    assert report["ok"] is False
    assert report["names_source"] is False
    assert any("does not name" in problem for problem in report["problems"])


def test_prose_in_the_closing_issue_cannot_satisfy_the_naming_check() -> None:
    """Restated as a property: the check reads the DESTINATION's body only, so
    nothing the closing side writes about itself can make it pass."""
    report = check(destination(body="This umbrella absorbed everything relevant."))
    assert report["ok"] is False


def test_the_destination_may_name_the_source_by_url() -> None:
    report = check(destination(body="Absorbs https://github.com/o/r/issues/555 and more."))
    assert report["names_source"] is True


def test_an_anchor_is_not_matched_inside_a_longer_number() -> None:
    """A destination naming #5551 has not named #555."""
    report = check(destination(body="Absorbs #5551."))
    assert report["names_source"] is False


def test_a_chained_destination_is_refused() -> None:
    """A into B into C leaves a reader following pointers; a cycle leaves them
    looping."""
    report = check(destination(body="Absorbs #555.\n\nConsolidated into: #700\n"))
    assert report["ok"] is False
    assert report["is_chain"] is True
    assert any("itself consolidated" in problem for problem in report["problems"])


def test_every_problem_is_reported_not_only_the_first() -> None:
    """A destination can be wrong in several ways at once, and an author fixing them
    one round-trip at a time is an author who stops reading the output."""
    report = check(destination(state="CLOSED", body="Consolidated into: #700\n"))
    assert len(report["problems"]) == 3


# --- the distinction this whole lane exists to hold ---------------------------


def test_an_unreadable_destination_is_UNKNOWN_not_satisfied() -> None:
    """A readback that did not RUN is not a readback that passed.

    This is the same rule the sibling premise-state seam had to learn twice: an
    absent channel is missing evidence, never evidence of absence.
    """
    report = check(None)
    assert report["ok"] is False
    assert report["state"] == "unknown"
    assert "did not RUN" in report["problems"][0]


def test_a_backend_failure_is_reported_rather_than_raised() -> None:
    """A backend exception must not escape as a traceback, and must not be caught
    into silence either — the caller needs a typed refusal."""

    def explode(_number):
        raise RuntimeError("gh: API rate limit exceeded")

    report = verify_consolidation(source_number=555, destination_number=600, fetch=explode)
    assert report["ok"] is False
    assert report["state"] == "unknown"
    assert "rate limit" in report["problems"][0]
    assert "did not RUN" in report["problems"][0]


def test_the_happy_path_threads_the_fetch() -> None:
    seen: list[int] = []

    def fetch(number):
        seen.append(number)
        return destination()

    report = verify_consolidation(source_number=555, destination_number=600, fetch=fetch)
    assert report["ok"] is True
    assert seen == [600]


def test_nothing_here_closes_or_recommends_closing_anything() -> None:
    """It renders findings and stops, like the premise-state seam beside it."""
    report = check(destination())
    assert set(report) == {"ok", "state", "names_source", "is_chain", "problems"}
    blob = " ".join(str(value) for value in report.values()).lower()
    for phrase in ("safe to close", "ready to close", "recommend closing"):
        assert phrase not in blob


# --- reachability: the defect a previous round caught on the sibling surface ---


def test_the_readback_actually_FIRES_through_verify_closeout(tmp_path, monkeypatch) -> None:
    """A check that exists and is never called is the defect this lane keeps finding.

    The `consolidated` classification itself shipped once as unreachable — present in
    two data structures and in no execution path — so this asserts the readback runs
    from the surface an operator actually invokes, not from a direct call.
    """
    verify = runpy.run_path(str(_SCRIPTS / "issue_verify_closeout.py"))

    seen: list[int] = []

    def fake_view(repo_root, *, repo, number, backend, json_fields="number,state,url"):
        seen.append(number)
        # The destination is CLOSED and does not name the source: two of the four facts
        # are false, and the close must be refused on both.
        return {"number": number, "state": "CLOSED", "url": "u", "body": "unrelated"}

    # `runpy.run_path` hands back a COPY of the module globals, so patching that dict
    # does not reach the function -- it resolves the name in its own `__globals__`.
    monkeypatch.setitem(verify["verify_closeout"].__globals__, "_view_issue_state", fake_view)
    body_file = tmp_path / "body.md"
    body_file.write_text(
        "Closes #555\n\nClassification: consolidated\nJtbd: fold it\n"
        "Consolidated into: #600\n",
        encoding="utf-8",
    )

    result = verify["verify_closeout"](
        repo_root=tmp_path,
        repo="o/r",
        numbers=[555],
        classification="consolidated",
        carrier="manual-fallback",
        backend={"id": "gh", "binary": "gh", "commands": None},
        body_file=body_file,
        manual_fallback_reason="operator-directed-manual-close",
    )

    assert seen == [600], "the readback never reached the backend for the destination"
    assert result["ok"] is False
    problems = " ".join(result["missing_fields"])
    assert "not OPEN" in problems
    assert "does not name" in problems
    assert result["consolidation_readback"][0]["destination"] == 600


def test_a_non_consolidated_close_makes_no_destination_readback(tmp_path, monkeypatch) -> None:
    """The readback must not add backend calls to every other classification."""
    verify = runpy.run_path(str(_SCRIPTS / "issue_verify_closeout.py"))
    seen: list[int] = []

    def fake_view(repo_root, *, repo, number, backend, json_fields="number,state,url"):
        seen.append(number)
        return {"number": number, "state": "OPEN", "url": "u", "body": ""}

    monkeypatch.setitem(verify["verify_closeout"].__globals__, "_view_issue_state", fake_view)
    body_file = tmp_path / "body.md"
    body_file.write_text("Closes #555\n\nJtbd: x\n", encoding="utf-8")

    result = verify["verify_closeout"](
        repo_root=tmp_path,
        repo="o/r",
        numbers=[555],
        classification="question",
        carrier="manual-fallback",
        backend={"id": "gh", "binary": "gh", "commands": None},
        body_file=body_file,
        manual_fallback_reason="operator-directed-manual-close",
    )
    assert seen == []
    assert result["consolidation_readback"] == []


# --- round-2 repairs ----------------------------------------------------------


def test_an_answer_about_a_different_issue_is_not_evidence_about_this_one() -> None:
    """Being told is not obeying. A cross-repo anchor (`owner/other#12`) is fetched
    against the SOURCE repo, so an unrelated local #12 that happens to mention the
    source would otherwise pass all four checks."""
    report = check(destination(number=601), dest=600)
    assert report["ok"] is False
    assert any("answered about #601" in problem for problem in report["problems"])


def test_a_wrong_repo_answer_carrying_the_right_number_is_refused() -> None:
    report = evaluate_destination(
        {"number": 600, "state": "OPEN", "body": "#555", "repository": {"nameWithOwner": "o/other"}},
        source_number=555,
        destination_number=600,
        expected_repo="o/r",
        answer_repo=lambda payload: (payload.get("repository") or {}).get("nameWithOwner"),
    )
    assert report["ok"] is False
    assert any("wrong-repo answer" in problem for problem in report["problems"])


def test_a_non_dict_payload_is_a_backend_problem_not_a_crash() -> None:
    """It previously reached `.get` and escaped as an AttributeError traceback, which
    contradicts this module's own rule that any backend failure is "did not run"."""
    for payload in ([{"number": 600}], "not json", 7):
        report = check(payload)
        assert report["ok"] is False
        assert report["state"] == "unknown"
        assert "did not RUN" in report["problems"][0]


def test_destination_scoped_problems_are_surfaced_once_across_many_sources() -> None:
    """Twenty closes into one bad umbrella produced ~40 byte-identical lines and buried
    every other finding."""
    readbacks = _MOD["readbacks_for_closeout"](
        numbers=list(range(100, 120)),
        destinations=[600],
        fetch=lambda _dest: destination(state="CLOSED", body="names nobody"),
    )
    assert len(readbacks) == 20
    surfaced = [problem for entry in readbacks for problem in entry["problems_to_surface"]]
    closed_lines = [problem for problem in surfaced if "not OPEN" in problem]
    assert len(closed_lines) == 1, "a destination-scoped fact must be surfaced once"
    # ...while the per-source naming problem is still reported for each source.
    naming = [problem for problem in surfaced if "does not name" in problem]
    assert len(naming) == 20


def test_the_readback_runs_on_the_carrier_a_consolidated_close_MUST_use(tmp_path, monkeypatch) -> None:
    """A consolidated close is forced through `close-with-comment`, and that carrier
    checked neither the destination grammar nor whether the destination exists.

    This is the third instance of an asymmetry the close floor's own comments already
    name twice: a check lands on `verify-closeout` and the carrier that mutates GitHub
    directly never gets it.
    """
    import pytest

    close_mod = runpy.run_path(str(_SCRIPTS / "issue_close.py"))
    readback_mod = close_mod["_state_readback"]
    monkeypatch.setattr(
        readback_mod,
        "view_issue_state",
        lambda *a, **k: {"number": 600, "state": "CLOSED", "body": "names nobody"},
    )
    body = tmp_path / "body.md"
    body.write_text("Closes #555\n\nJtbd: fold it\nConsolidated into: #600\n", encoding="utf-8")

    with pytest.raises(RuntimeError) as excinfo:
        close_mod["close_with_comment"](
            repo="o/r",
            number=555,
            body_file=body,
            repo_root=tmp_path,
            classification="consolidated",
            reason="not planned",
        )
    assert "presence floor" in str(excinfo.value)


def test_a_fetch_failure_in_the_WIRED_loop_is_reported_on_the_verdict() -> None:
    """`readbacks_for_closeout` has its own error branch, distinct from
    `verify_consolidation`'s, and it was the one with no test — the wired path sets
    `payload = None` and appends the backend's message to the refusal."""

    def explode(_number):
        raise RuntimeError("gh: could not resolve host")

    readbacks = _MOD["readbacks_for_closeout"](
        numbers=[555, 556], destinations=[600], fetch=explode
    )
    assert len(readbacks) == 2
    assert all(entry["state"] == "unknown" for entry in readbacks)
    assert "could not resolve host" in readbacks[0]["problems"][0]
    # The dedupe still applies: one destination-scoped failure, surfaced once.
    surfaced = [p for entry in readbacks for p in entry["problems_to_surface"]]
    assert len(surfaced) == 1
    assert readbacks[1]["unreported_duplicates"] == 1


# --- the extracted backend state read -----------------------------------------

_STATE = runpy.run_path(str(_SCRIPTS / "issue_state_readback.py"))
view_issue_state = _STATE["view_issue_state"]
GH_BACKEND = {"id": "gh", "binary": "gh", "commands": None}


def test_a_non_gh_backend_without_a_view_command_is_refused(tmp_path) -> None:
    """Carrier text alone is not issue closeout: a backend that cannot read state
    must say so rather than let the caller proceed on prose."""
    import pytest

    with pytest.raises(RuntimeError, match="requires backend commands.view"):
        view_issue_state(
            tmp_path, repo="o/r", number=1, backend={"id": "acme", "binary": "acme"}
        )


def test_a_command_that_cannot_start_is_a_typed_refusal(tmp_path, monkeypatch) -> None:
    import subprocess as sp

    import pytest

    monkeypatch.setattr(_STATE["subprocess"], "run", lambda *a, **k: (_ for _ in ()).throw(OSError("no such binary")))
    with pytest.raises(RuntimeError, match="failed to start"):
        view_issue_state(tmp_path, repo="o/r", number=1, backend=GH_BACKEND)
    assert sp is not None


def test_a_timeout_becomes_a_nonzero_result_rather_than_an_escape(tmp_path, monkeypatch) -> None:
    """A timeout must land in the same refusal channel as any other failure, not
    escape as a different exception type the caller does not handle."""
    import subprocess

    import pytest

    def timeout(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd="gh", timeout=1)

    monkeypatch.setattr(_STATE["subprocess"], "run", timeout)
    with pytest.raises(RuntimeError, match="timed out"):
        view_issue_state(tmp_path, repo="o/r", number=1, backend=GH_BACKEND)


def test_a_nonzero_exit_names_the_issue_and_the_stderr(tmp_path, monkeypatch) -> None:
    import subprocess

    import pytest

    monkeypatch.setattr(
        _STATE["subprocess"],
        "run",
        lambda *a, **k: subprocess.CompletedProcess("gh", 1, "", "not found"),
    )
    with pytest.raises(RuntimeError, match=r"o/r#42.*not found"):
        view_issue_state(tmp_path, repo="o/r", number=42, backend=GH_BACKEND)


def test_unparseable_output_is_refused_rather_than_returned(tmp_path, monkeypatch) -> None:
    """Invalid JSON must not reach `evaluate_destination` as a string — that is the
    non-dict payload path, and refusing here is the earlier, clearer place."""
    import subprocess

    import pytest

    monkeypatch.setattr(
        _STATE["subprocess"],
        "run",
        lambda *a, **k: subprocess.CompletedProcess("gh", 0, "not json", ""),
    )
    with pytest.raises(RuntimeError, match="invalid JSON"):
        view_issue_state(tmp_path, repo="o/r", number=1, backend=GH_BACKEND)


def test_a_well_formed_read_returns_the_payload(tmp_path, monkeypatch) -> None:
    import json as _json
    import subprocess

    monkeypatch.setattr(
        _STATE["subprocess"],
        "run",
        lambda *a, **k: subprocess.CompletedProcess(
            "gh", 0, _json.dumps({"number": 600, "state": "OPEN"}), ""
        ),
    )
    assert view_issue_state(tmp_path, repo="o/r", number=600, backend=GH_BACKEND)["number"] == 600
