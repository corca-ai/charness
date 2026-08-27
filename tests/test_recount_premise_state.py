"""The backlog re-verification seam: typed premise state, and the refusals that matter.

The load-bearing case is not "does it detect a refuted premise". It is that a REFUTED
premise with live residue must NOT read as a close candidate -- the instance that motivated
the tool was refuted and still must not close, because its second part was live and a goal
slice log said so. So the suite seeds both directions: an issue whose premise the tree has
refuted AND one whose premise still holds, so a tool that always answers `holds` (or always
answers `refuted-clean`) fails rather than passing on a lucky default.

Round-1 bounded review found the typing sound and residue RECALL defective in four
independent ways, each producing the close-leaning `premise-refuted-clean` on evidence a
human reads as "do not close". It also found three tests here that could not fail on the
defect they claimed to guard. Both sets are covered below and marked, because a suite that
pinned the degenerate behavior as correct is the sharpest version of this repo's own
recurring defect: a record treated as a fact because re-reading it was nobody's step.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "public" / "achieve" / "scripts"


@pytest.fixture(scope="module")
def premise_lib():
    return load_script_module("recount_premise_lib_under_test", SCRIPTS / "recount_premise_lib.py")


@pytest.fixture(scope="module")
def residue_lib():
    return load_script_module("recount_residue_lib_under_test", SCRIPTS / "recount_residue_lib.py")


@pytest.fixture(scope="module")
def premise_cli():
    return load_script_module(
        "recount_premise_state_under_test", SCRIPTS / "recount_premise_state.py"
    )

# Modules this file is the standing coverage for, declared as quoted repo-relative
# paths so `suggest_mutation_coverage_command` can MAP them. The mapper reads
# textual references, and these tests build their paths from a variable
# (`_SCRIPTS / "x.py"`), which matches none of its patterns -- so the changed-line
# coverage gate reported these files unmapped and then blocked on lines this suite
# actually covers. Declaring the mapping is better than making the loader uglier to
# be greppable.
_COVERS = (
    "skills/public/achieve/scripts/recount_premise_lib.py",
    "skills/public/achieve/scripts/recount_residue_lib.py",
    "skills/public/achieve/scripts/recount_premise_state.py",
)



def write_record(repo: Path, name: str, body: str, root: str = "goals") -> Path:
    path = repo / "charness-artifacts" / root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def ran_clean() -> dict:
    """A residue result where both channels RAN and found nothing.

    Every `classify` test that expects `premise-refuted-clean` must go through this, because
    "found nothing" and "never ran" are now different answers and only the first may reach
    the close-leaning state.
    """
    return {
        "declining": [],
        "provenance": {
            "roots_present": ["charness-artifacts"],
            "files_scanned": 4,
            "files_unreadable": [],
            "markers_seen": 0,
            "fenced_markers_skipped": [],
            "listing_mode": "git-tracked",
            "suffixes_scanned": [".md"],
            "records_excluded": 0,
            "excluded": [],
            "prose_matching": "disabled by design",
        },
    }


# --- residue scanning (structural markers only) ------------------------------------------


def marker(number: int, reason: str) -> str:
    return f"Premise-residue: #{number} — {reason}\n"


def test_an_ordinary_mention_is_not_residue(tmp_path, residue_lib):
    """Only an explicit typed marker counts. A record naming an issue says nothing."""
    write_record(tmp_path, "g1.md", "Slice 2 landed the ratchet repair described in #550.\n")
    assert residue_lib.scan_residue(tmp_path, 550)["declining"] == []


def test_prose_that_reads_like_a_decline_is_not_residue(tmp_path, residue_lib):
    """The design's central refusal: no wording is inferred, in any language.

    Each line below WOULD have matched the deleted prose vocabulary. None of them is a
    typed marker, so none of them is residue. This is the test that fails if someone
    reintroduces phrase matching.
    """
    for text in (
        "- `#601` is NOT closed; part 2 is unbuilt.\n",
        "- `#601` remains open by design.\n",
        "- `#601` — carried forward to the successor goal.\n",
        "- `#601` 는 아직 닫지 않는다. 보류.\n",
    ):
        write_record(tmp_path, "g1.md", text)
        assert residue_lib.scan_residue(tmp_path, 601)["declining"] == [], text


def test_a_typed_marker_is_residue(tmp_path, residue_lib):
    write_record(tmp_path, "g1.md", marker(554, "part 2 (the recount helper) is unbuilt"))
    declining = residue_lib.scan_residue(tmp_path, 554)["declining"]
    assert len(declining) == 1
    assert "part 2" in declining[0]["text"]
    assert declining[0]["line"] == 1


@pytest.mark.parametrize(
    "line",
    [
        "Premise-residue: #554 — reason\n",
        "- Premise-residue: #554 — reason\n",
        "- **Premise-residue:** #554 — reason\n",
        "  * `Premise-residue`: #554 — reason\n",
        "premise-residue: #554 — reason\n",
    ],
)
def test_marker_tolerates_the_decoration_artifacts_actually_use(tmp_path, residue_lib, line):
    """Bullet and emphasis decoration is the SAME record, mirroring the other achieve floors."""
    write_record(tmp_path, "g1.md", line)
    assert len(residue_lib.scan_residue(tmp_path, 554)["declining"]) == 1


def test_a_marker_naming_another_issue_is_not_this_issue_s_residue(tmp_path, residue_lib):
    write_record(tmp_path, "g1.md", marker(601, "still unbuilt"))
    assert residue_lib.scan_residue(tmp_path, 602)["declining"] == []


def test_a_marker_with_no_reason_is_not_a_marker(tmp_path, residue_lib):
    """A marker with no reason records a ritual; the point is that a human wrote down WHY."""
    write_record(tmp_path, "g1.md", "Premise-residue:\n")
    scan = residue_lib.scan_residue(tmp_path, 554)
    assert scan["declining"] == []
    assert scan["provenance"]["markers_seen"] == 0


@pytest.mark.parametrize("form", ["#554", "issues/554", "GH-554"])
def test_every_citation_form_is_matched_inside_a_marker(tmp_path, residue_lib, form):
    write_record(tmp_path, "g1.md", f"Premise-residue: {form} — reason\n")
    assert len(residue_lib.scan_residue(tmp_path, 554)["declining"]) == 1


def test_issue_token_does_not_match_a_longer_number(tmp_path, residue_lib):
    """`#55` must not pick up `#554`; a spurious hit looks exactly like the tool working."""
    write_record(tmp_path, "g1.md", marker(554, "reason"))
    assert residue_lib.scan_residue(tmp_path, 55)["declining"] == []
    assert residue_lib.scan_residue(tmp_path, 5)["declining"] == []


def test_excluded_record_cannot_manufacture_its_own_residue(tmp_path, residue_lib):
    """The goal being shaped may carry markers for the very issues it is reasoning about."""
    active = write_record(tmp_path, "active.md", marker(554, "reason"))
    assert residue_lib.scan_residue(tmp_path, 554)["declining"]
    scan = residue_lib.scan_residue(tmp_path, 554, exclude=(active,))
    assert scan["declining"] == []
    assert scan["provenance"]["records_excluded"] == 1


@pytest.mark.parametrize("root", ["goals", "audit", "critique", "retro", "quality", "debug"])
def test_markers_are_read_from_every_artifact_root(tmp_path, residue_lib, root):
    write_record(tmp_path, "note.md", marker(601, "reason"), root=root)
    assert len(residue_lib.scan_residue(tmp_path, 601)["declining"]) == 1


def test_markers_are_read_from_named_durable_docs(tmp_path, residue_lib):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "deferred-decisions.md").write_text(
        marker(601, "deferred until the seam lands"), encoding="utf-8"
    )
    assert len(residue_lib.scan_residue(tmp_path, 601)["declining"]) == 1


def test_fenced_marker_is_skipped_and_reported_with_a_locator(tmp_path, residue_lib):
    """Documentation showing the marker form must not become a live disposition."""
    write_record(tmp_path, "g1.md", "Write it like this:\n\n```\n" + marker(601, "reason") + "```\n")
    scan = residue_lib.scan_residue(tmp_path, 601)
    assert scan["declining"] == []
    assert scan["provenance"]["fenced_markers_skipped"] == ["charness-artifacts/goals/g1.md:4"]


def test_json_and_jsonl_are_not_durable_records(tmp_path, residue_lib):
    """A captured transcript quoting a marker must not become a live disposition."""
    path = tmp_path / "charness-artifacts" / "quality" / "session.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"text": "Premise-residue: #601 — reason"}\n', encoding="utf-8")
    scan = residue_lib.scan_residue(tmp_path, 601)
    assert scan["declining"] == []
    assert scan["provenance"]["suffixes_scanned"] == [".md"]


def test_scan_reports_provenance_so_an_empty_scan_is_distinguishable(tmp_path, residue_lib):
    """"No marker found" and "there were no records" must not be the same output."""
    empty = residue_lib.scan_residue(tmp_path, 601)
    assert empty["provenance"]["roots_present"] == []
    assert empty["provenance"]["files_scanned"] == 0

    write_record(tmp_path, "g1.md", "`#601` shipped.\n")
    populated = residue_lib.scan_residue(tmp_path, 601)
    assert populated["provenance"]["roots_present"] == ["charness-artifacts"]
    assert populated["provenance"]["files_scanned"] == 1


def test_provenance_states_that_prose_matching_is_off(tmp_path, residue_lib):
    """The absence of prose matching is a CLAIM the report makes, not a silent omission."""
    write_record(tmp_path, "g1.md", "x\n")
    assert "disabled by design" in residue_lib.scan_residue(tmp_path, 1)["provenance"]["prose_matching"]


def test_unreadable_record_is_reported_not_silently_dropped(tmp_path, residue_lib):
    path = write_record(tmp_path, "g1.md", "x\n")
    path.write_bytes(b"\xff\xfe\x00 invalid utf-8 \xff")
    scan = residue_lib.scan_residue(tmp_path, 601)
    assert scan["provenance"]["files_unreadable"] == ["charness-artifacts/goals/g1.md"]


def test_scanner_is_gitignore_aware_and_reports_its_listing_mode(tmp_path, residue_lib):
    write_record(tmp_path, "g1.md", marker(601, "reason"))
    scan = residue_lib.scan_residue(tmp_path, 601)
    assert scan["provenance"]["listing_mode"] == "rglob-no-git"
    assert len(scan["declining"]) == 1


def test_gitignored_records_are_not_scanned_in_a_real_checkout(tmp_path, residue_lib):
    import subprocess

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("charness-artifacts/ignored/\n", encoding="utf-8")
    write_record(tmp_path, "kept.md", marker(601, "reason"))
    write_record(tmp_path, "dropped.md", marker(602, "reason"), root="ignored")

    kept = residue_lib.scan_residue(tmp_path, 601)
    assert kept["provenance"]["listing_mode"] == "git-tracked"
    assert len(kept["declining"]) == 1
    assert residue_lib.scan_residue(tmp_path, 602)["declining"] == []


# --- body probes (structural only) --------------------------------------------------------


def test_unchecked_task_items_are_counted(premise_lib):
    """The only surviving body signal, and the only one that is language-independent."""
    body = "## Parts\n\n- [x] ship the floor\n- [ ] resolve the overlap\n- [ ] re-scope\n"
    tasks = premise_lib.body_open_task_items(body)
    assert tasks["open"] == 2
    assert tasks["done"] == 1
    assert tasks["first_open"] == "resolve the overlap"


def test_a_fully_checked_body_has_no_open_task(premise_lib):
    assert premise_lib.body_open_task_items("- [x] done\n- [X] also done\n")["open"] == 0


def test_an_ordinary_bullet_is_not_a_task_item(premise_lib):
    """`- [ ]` is a declared form; a plain bullet is not an ask the issue declares open."""
    assert premise_lib.body_open_task_items("- just a bullet\n- another\n")["open"] == 0


# --- classification ---------------------------------------------------------------------


def test_no_caller_verdict_is_unverifiable_never_holds(premise_lib):
    """A tool that always answers `holds` fails here: absence is a distinct answer."""
    verdict = premise_lib.classify(
        caller_verdict=None, residue=ran_clean()
    )
    assert verdict["state"] == premise_lib.UNVERIFIABLE


def test_caller_cannot_assert_unverifiable(premise_lib):
    """"I looked and could not tell" must not be recordable as "I did not look"."""
    verdict = premise_lib.classify(
        caller_verdict="unverifiable-by-machine",
        residue=ran_clean(),
    )
    assert verdict["state"] == premise_lib.UNVERIFIABLE
    assert "no caller premise judgement" in verdict["reason"]


def test_premise_holds_short_circuits_before_residue(premise_lib):
    """An issue that still describes the tree needs no residue reasoning at all."""
    verdict = premise_lib.classify(
        caller_verdict="holds",
        residue={"declining": [{"path": "g.md", "line": 1, "text": "not closed"}]},
    )
    assert verdict["state"] == premise_lib.PREMISE_HOLDS


def test_refuted_with_declining_record_is_a_refusal_not_a_close_candidate(premise_lib):
    """The motivating instance: refuted, and the correct answer is still DO NOT CLOSE."""
    residue = ran_clean()
    residue["declining"] = [{"path": "goals/g.md", "line": 130, "text": "NOT closed"}]
    verdict = premise_lib.classify(
        caller_verdict="refuted", residue=residue
    )
    assert verdict["state"] == premise_lib.PREMISE_REFUTED_WITH_LIVE_RESIDUE
    assert "goals/g.md:130" in verdict["reason"]
    assert "REFUSAL" in verdict["reason"]


def test_refuted_with_an_open_task_alone_is_still_a_refusal(premise_lib):
    """Body residue is sufficient on its own; a record marker is not required."""
    verdict = premise_lib.classify(
        caller_verdict="refuted",
        residue=ran_clean(),
        open_tasks={"open": 1, "first_open": "resolve the overlap"},
    )
    assert verdict["state"] == premise_lib.PREMISE_REFUTED_WITH_LIVE_RESIDUE
    assert "unchecked task-list item" in verdict["reason"]


def test_refuted_clean_requires_every_channel_to_have_RUN(premise_lib):
    verdict = premise_lib.classify(
        caller_verdict="refuted",
        residue=ran_clean(),
        body_read=True,
    )
    assert verdict["state"] == premise_lib.PREMISE_REFUTED_CLEAN
    assert "every structural channel ran" in verdict["reason"]
    assert "deliberately NOT detected" in verdict["reason"]


def test_unread_body_refuses_rather_than_reading_as_clean(premise_lib):
    """Round-1 F4: an unread body silently meant "no further ask", and the reason said so."""
    verdict = premise_lib.classify(
        caller_verdict="refuted",
        residue=ran_clean(),
        body_read=False,
    )
    assert verdict["state"] == premise_lib.PREMISE_REFUTED_WITH_LIVE_RESIDUE
    assert "did not RUN" in verdict["reason"]
    assert "--with-bodies" in verdict["reason"]


def test_absent_record_roots_refuse_rather_than_reading_as_clean(premise_lib):
    """Round-1 F3: a wrong --repo-root made every refuted issue look closable."""
    residue = ran_clean()
    residue["provenance"]["roots_present"] = []
    verdict = premise_lib.classify(
        caller_verdict="refuted", residue=residue
    )
    assert verdict["state"] == premise_lib.PREMISE_REFUTED_WITH_LIVE_RESIDUE
    assert "--repo-root" in verdict["reason"]


def test_unreadable_record_refuses_rather_than_reading_as_clean(premise_lib):
    residue = ran_clean()
    residue["provenance"]["files_unreadable"] = ["charness-artifacts/goals/g1.md"]
    verdict = premise_lib.classify(
        caller_verdict="refuted", residue=residue
    )
    assert verdict["state"] == premise_lib.PREMISE_REFUTED_WITH_LIVE_RESIDUE
    assert "could not be read" in verdict["reason"]


def test_the_clean_reason_never_claims_a_channel_that_did_not_run(premise_lib):
    """The reason STRING is a verdict surface too: round 1 found it asserting a falsehood."""
    for body_read in (True, False):
        verdict = premise_lib.classify(
            caller_verdict="refuted",
            residue=ran_clean(),
            body_read=body_read,
        )
        if verdict["state"] == premise_lib.PREMISE_REFUTED_CLEAN:
            assert body_read, "clean state reached with an unread body"
        else:
            assert "no further enumerated ask" not in verdict["reason"]


def test_no_suppression_can_upgrade_a_refuted_issue_to_clean(premise_lib):
    """Claim 2, asserted where its risk actually lives, not on the `holds` short-circuit.

    Round 1: the old version of this test fixed `caller_verdict='holds'` for every case, so
    it only re-tested the short-circuit and could not fail on the suppression paths.
    """
    suppressions = [
        ("roots_present", []),
        ("files_unreadable", ["charness-artifacts/goals/g.md"]),
    ]
    for key, value in suppressions:
        residue = ran_clean()
        residue["provenance"][key] = value
        state = premise_lib.classify(
            caller_verdict="refuted", residue=residue
        )["state"]
        assert state == premise_lib.PREMISE_REFUTED_WITH_LIVE_RESIDUE, key
    state = premise_lib.classify(
        caller_verdict="refuted",
        residue=ran_clean(),
        body_read=False,
    )["state"]
    assert state == premise_lib.PREMISE_REFUTED_WITH_LIVE_RESIDUE


# --- report envelope --------------------------------------------------------------------


def fake_runner(issues, bodies=None):
    """Stand in for the backend without asserting a hand-written `gh` output shape.

    Dispatches on the rendered argv the `issue` skill's own `resolve_op` produced, so the
    test still exercises that rendering rather than bypassing it.
    """

    def run(argv):
        if "list" in argv:
            return issues
        number = int(argv[argv.index("view") + 1])
        return {"number": number, "body": (bodies or {}).get(number, "")}

    return run


def seeded_repo(tmp_path: Path) -> Path:
    """A repo with at least one durable record, so the record channel genuinely RAN."""
    write_record(tmp_path, "unrelated.md", "Nothing to see here.\n")
    return tmp_path


def test_report_defaults_every_issue_to_unverifiable(tmp_path, premise_cli):
    report = premise_cli.build_report(
        seeded_repo(tmp_path),
        repo="o/r",
        limit=10,
        premise_file=None,
        exclude=(),
        with_bodies=False,
        runner=fake_runner([{"number": 1, "title": "a"}, {"number": 2, "title": "b"}]),
    )
    assert report["counted"] == 2
    assert report["counts"]["unverifiable-by-machine"] == 2
    assert report["counts"]["premise-refuted-clean"] == 0


def test_report_reproduces_the_motivating_instance(tmp_path, premise_cli):
    """Refuted premise + a goal slice log that declined to close => refusal state."""
    write_record(tmp_path, "prior.md", marker(554, "part 2 (the recount helper) is unbuilt"))
    premise_file = tmp_path / "premise.json"
    premise_file.write_text(
        json.dumps({"554": {"verdict": "refuted", "evidence": "lifecycle-before carries it"}}),
        encoding="utf-8",
    )
    report = premise_cli.build_report(
        tmp_path,
        repo="o/r",
        limit=10,
        premise_file=premise_file,
        exclude=(),
        with_bodies=False,
        runner=fake_runner([{"number": 554, "title": "achieve never reads the tracker"}]),
    )
    entry = report["issues"][0]
    assert entry["state"] == "premise-refuted-with-live-residue"
    assert entry["residue_declining"][0]["path"] == "charness-artifacts/goals/prior.md"
    assert entry["caller_evidence"] == "lifecycle-before carries it"


def test_report_seeds_a_holding_premise_alongside_the_refuted_one(tmp_path, premise_cli):
    """Both directions in one sweep, so a constant-answer tool cannot pass."""
    premise_file = tmp_path / "premise.json"
    premise_file.write_text(
        json.dumps({"554": {"verdict": "refuted"}, "576": {"verdict": "holds"}}), encoding="utf-8"
    )
    report = premise_cli.build_report(
        seeded_repo(tmp_path),
        repo="o/r",
        limit=10,
        premise_file=premise_file,
        exclude=(),
        with_bodies=True,
        runner=fake_runner([{"number": 554, "title": "a"}, {"number": 576, "title": "b"}]),
    )
    states = {item["number"]: item["state"] for item in report["issues"]}
    assert states == {554: "premise-refuted-clean", 576: "premise-holds"}


def test_report_without_bodies_cannot_reach_clean(tmp_path, premise_cli):
    """The end-to-end form of F4: the default mode must not produce close-leaning states."""
    premise_file = tmp_path / "premise.json"
    premise_file.write_text(json.dumps({"554": {"verdict": "refuted"}}), encoding="utf-8")
    report = premise_cli.build_report(
        seeded_repo(tmp_path),
        repo="o/r",
        limit=10,
        premise_file=premise_file,
        exclude=(),
        with_bodies=False,
        runner=fake_runner([{"number": 554, "title": "a"}]),
    )
    assert report["issues"][0]["state"] == "premise-refuted-with-live-residue"


def test_report_never_carries_a_close_recommendation(tmp_path, premise_cli):
    """Checks VALUES, not just key names: round 1 found the old version vacuous."""
    report = premise_cli.build_report(
        seeded_repo(tmp_path),
        repo="o/r",
        limit=10,
        premise_file=None,
        exclude=(),
        with_bodies=False,
        runner=fake_runner([{"number": 1, "title": "a"}]),
    )
    assert "none by design" in report["close_recommendation"]
    entry = report["issues"][0]
    assert not any(key in entry for key in ("disposition", "should_close", "recommendation"))
    blob = json.dumps(entry).lower()
    for phrase in ("safe to close", "can be closed", "ready to close", "recommend closing"):
        assert phrase not in blob


def test_unreadable_body_refuses_rather_than_reading_as_no_further_ask(tmp_path, premise_cli):
    """A fetch failure must never become evidence FOR closing -- asserted on the STATE.

    Round 1: the previous test asserted only `body_read is False`, which is the literal
    definition of the field, and supplied no premise file, so it could not fail on the bug.
    """
    premise_file = tmp_path / "premise.json"
    premise_file.write_text(json.dumps({"7": {"verdict": "refuted"}}), encoding="utf-8")

    def run(argv):
        if "list" in argv:
            return [{"number": 7, "title": "a"}]
        raise RuntimeError("backend exploded")

    report = premise_cli.build_report(
        seeded_repo(tmp_path),
        repo="o/r",
        limit=10,
        premise_file=premise_file,
        exclude=(),
        with_bodies=True,
        runner=run,
    )
    entry = report["issues"][0]
    assert entry["body_read"] is False
    assert entry["state"] == "premise-refuted-with-live-residue"


def test_report_echoes_every_knob_that_can_suppress_residue(tmp_path, premise_cli):
    """Round-1 F7: `--exclude` and `--limit` could silently narrow the answer."""
    excluded = write_record(tmp_path, "active.md", "- Not claimed: `#1` stays open.\n")
    report = premise_cli.build_report(
        tmp_path,
        repo="o/r",
        limit=2,
        premise_file=None,
        exclude=(excluded,),
        with_bodies=False,
        runner=fake_runner([{"number": 1, "title": "a"}, {"number": 2, "title": "b"}]),
    )
    assert report["scan_scope"]["excluded"] == [str(excluded)]
    assert report["scan_scope"]["limit"] == 2
    assert report["scan_scope"]["list_truncated"] is True
    assert report["issues"][0]["residue_provenance"]["excluded"] == [str(excluded)]


def test_untruncated_list_is_reported_as_untruncated(tmp_path, premise_cli):
    report = premise_cli.build_report(
        seeded_repo(tmp_path),
        repo="o/r",
        limit=10,
        premise_file=None,
        exclude=(),
        with_bodies=False,
        runner=fake_runner([{"number": 1, "title": "a"}]),
    )
    assert report["scan_scope"]["list_truncated"] is False


def test_premise_file_accepts_a_bare_verdict_string(tmp_path, premise_cli):
    premise_file = tmp_path / "p.json"
    premise_file.write_text(json.dumps({"#9": "holds"}), encoding="utf-8")
    assert premise_cli.load_premise_verdicts(premise_file)[9]["verdict"] == "holds"


def test_malformed_premise_entry_degrades_instead_of_raising(tmp_path, premise_cli):
    """Round-1 F10: a list value raised TypeError straight past the error envelope."""
    premise_file = tmp_path / "p.json"
    premise_file.write_text(json.dumps({"9": ["refuted"], "10": 3}), encoding="utf-8")
    verdicts = premise_cli.load_premise_verdicts(premise_file)
    assert verdicts[9] == {} and verdicts[10] == {}


def test_unknown_verdict_degrades_to_unverifiable_rather_than_erroring(tmp_path, premise_cli):
    premise_file = tmp_path / "p.json"
    premise_file.write_text(json.dumps({"9": {"verdict": "probably fine"}}), encoding="utf-8")
    report = premise_cli.build_report(
        seeded_repo(tmp_path),
        repo="o/r",
        limit=10,
        premise_file=premise_file,
        exclude=(),
        with_bodies=False,
        runner=fake_runner([{"number": 9, "title": "a"}]),
    )
    assert report["issues"][0]["state"] == "unverifiable-by-machine"


def test_list_op_renders_through_the_issue_skill_resolver(premise_cli):
    """The tracker seam is the `issue` skill's owner, not a third implementation."""
    captured = {}

    def run(argv):
        captured["argv"] = argv
        return []

    premise_cli.list_open_issues(ROOT, repo="o/r", limit=42, runner=run)
    assert captured["argv"][0] == "gh"
    assert "42" in captured["argv"]
def test_helper_provenance_matches_what_scan_residue_actually_emits(tmp_path, residue_lib):
    """Round-2 medium 8: a fixture shape production never produces guards nothing.

    `ran_clean()` feeds every `classify` test. If its keys drift from the real scanner's,
    those tests pass on a dict no run can produce -- which is this goal's own defect class.
    """
    write_record(tmp_path, "g1.md", "`#601` shipped.\n")
    real = residue_lib.scan_residue(tmp_path, 601)["provenance"]
    assert set(real) == set(ran_clean()["provenance"])
def test_zero_files_read_with_a_present_root_is_a_channel_gap(tmp_path, premise_lib):
    """Round-2 blocker 3: a root that EXISTS is not a root that was READ."""
    residue = ran_clean()
    residue["provenance"]["files_scanned"] = 0
    verdict = premise_lib.classify(
        caller_verdict="refuted", residue=residue
    )
    assert verdict["state"] == premise_lib.PREMISE_REFUTED_WITH_LIVE_RESIDUE
    assert "ZERO record files" in verdict["reason"]


def test_excluding_every_record_cannot_produce_a_clean_verdict(tmp_path, premise_cli):
    """The end-to-end form of blocker 3: --exclude must not buy a clean answer."""
    only = write_record(tmp_path, "only.md", "`#601` remains open.\n")
    premise_file = tmp_path / "p.json"
    premise_file.write_text(json.dumps({"601": {"verdict": "refuted"}}), encoding="utf-8")
    report = premise_cli.build_report(
        tmp_path,
        repo="o/r",
        limit=10,
        premise_file=premise_file,
        exclude=(only,),
        with_bodies=True,
        runner=fake_runner([{"number": 601, "title": "a"}]),
    )
    assert report["issues"][0]["state"] == "premise-refuted-with-live-residue"
def test_fenced_payload_does_not_lend_its_words_to_surrounding_prose(tmp_path, residue_lib):
    """Round-2 high 5, the other direction: a fenced JSON's `pending` is not a decline."""
    write_record(
        tmp_path,
        "g1.md",
        "The state for `#601` is recorded below.\n```json\n{\"pending_publish\": false}\n```\n",
    )
    assert residue_lib.scan_residue(tmp_path, 601)["declining"] == []


def test_a_real_decline_still_reports_a_dead_channel(premise_lib):
    """Round-2 medium 6: a finding must not conceal the fact that half the evidence is
    missing, or a caller who overrides the finding never learns it."""
    residue = ran_clean()
    residue["declining"] = [{"path": "goals/g.md", "line": 5, "text": "NOT closed"}]
    verdict = premise_lib.classify(
        caller_verdict="refuted",
        residue=residue,
        body_read=False,
    )
    assert "goals/g.md:5" in verdict["reason"]
    assert "Separately, a residue channel did not RUN" in verdict["reason"]
    assert "--with-bodies" in verdict["reason"]


def test_backend_payload_without_a_body_key_counts_as_unread(tmp_path, premise_cli):
    """Round-2 high 4: F4 reopened at the seam via `.get("body") or ""`."""
    premise_file = tmp_path / "p.json"
    premise_file.write_text(json.dumps({"601": {"verdict": "refuted"}}), encoding="utf-8")

    def run(argv):
        if "list" in argv:
            return [{"number": 601, "title": "a"}]
        return {"number": 601}  # adapter-shaped payload with no `body`

    report = premise_cli.build_report(
        seeded_repo(tmp_path),
        repo="o/r",
        limit=10,
        premise_file=premise_file,
        exclude=(),
        with_bodies=True,
        runner=run,
    )
    entry = report["issues"][0]
    assert entry["body_read"] is False
    assert entry["state"] == "premise-refuted-with-live-residue"


# --- the CLI and the backend seam ---------------------------------------------


def test_main_renders_a_report_end_to_end(tmp_path, premise_cli, capsys, monkeypatch) -> None:
    """`main` had only its error envelope covered; the path an operator actually runs
    — list, evaluate, print — had none."""
    write_record(tmp_path, "prior.md", "Premise-residue: #554 — part 2 is unbuilt\n")
    premise_file = tmp_path / "p.json"
    premise_file.write_text(
        json.dumps({"554": {"verdict": "refuted"}, "576": {"verdict": "holds"}}), encoding="utf-8"
    )
    monkeypatch.setattr(
        premise_cli,
        "backend_json",
        lambda _root, argv: (
            [{"number": 554, "title": "a"}, {"number": 576, "title": "b"}]
            if "list" in argv
            else {"number": int(argv[argv.index("view") + 1]), "body": ""}
        ),
    )

    code = premise_cli.main(
        ["--repo-root", str(tmp_path), "--premise-file", str(premise_file), "--with-bodies"]
    )
    payload = yaml.safe_load(capsys.readouterr().out)
    assert code == 0 and payload["ok"] is True
    states = {item["number"]: item["state"] for item in payload["issues"]}
    assert states == {554: "premise-refuted-with-live-residue", 576: "premise-holds"}


def test_main_state_filter_narrows_issues_but_not_counts(tmp_path, premise_cli, capsys, monkeypatch) -> None:
    """`counts` stays a whole-backlog denominator, and the filter is recorded so the
    disagreement with `counted` is visible rather than confusing."""
    write_record(tmp_path, "g.md", "nothing\n")
    monkeypatch.setattr(
        premise_cli,
        "backend_json",
        lambda _root, argv: [{"number": 1, "title": "a"}, {"number": 2, "title": "b"}],
    )
    code = premise_cli.main(
        ["--repo-root", str(tmp_path), "--state", "premise-holds"]
    )
    payload = yaml.safe_load(capsys.readouterr().out)
    assert code == 0
    assert payload["counted"] == 2 and payload["issues"] == []
    assert payload["scan_scope"]["state_filter"] == "premise-holds"


def test_backend_json_refuses_a_nonzero_backend(tmp_path, premise_cli, monkeypatch) -> None:
    import subprocess

    import pytest

    owner = premise_cli.load_issue_module(ROOT, "issue_backend")
    monkeypatch.setattr(
        owner, "run_backend", lambda argv: subprocess.CompletedProcess(argv, 1, "", "boom")
    )
    with pytest.raises(RuntimeError, match="boom"):
        premise_cli.backend_json(ROOT, ["gh", "issue", "list"])


def test_backend_json_parses_a_successful_answer(tmp_path, premise_cli, monkeypatch) -> None:
    import subprocess

    owner = premise_cli.load_issue_module(ROOT, "issue_backend")
    monkeypatch.setattr(
        owner, "run_backend", lambda argv: subprocess.CompletedProcess(argv, 0, '[{"number": 1}]', "")
    )
    assert premise_cli.backend_json(ROOT, ["gh", "issue", "list"]) == [{"number": 1}]


def test_a_list_that_is_not_a_list_is_refused(premise_cli) -> None:
    import pytest

    with pytest.raises(RuntimeError, match="did not return a list"):
        premise_cli.list_open_issues(ROOT, repo="o/r", limit=5, runner=lambda _argv: {"n": 1})


def test_view_issue_degrades_a_non_dict_payload(premise_cli) -> None:
    assert premise_cli.view_issue(ROOT, 1, repo="o/r", runner=lambda _argv: ["nope"]) == {}


def test_the_sibling_loader_memoizes_and_refuses_a_missing_module(premise_cli) -> None:
    import pytest

    assert premise_cli.sibling("recount_premise_lib") is premise_cli.sibling("recount_premise_lib")
    with pytest.raises(ImportError, match="not found beside"):
        premise_cli.sibling("recount_no_such_module")


def test_the_issue_module_loader_refuses_a_missing_script(premise_cli, tmp_path) -> None:
    import pytest

    with pytest.raises(ImportError, match="issue skill script"):
        premise_cli.load_issue_module(tmp_path, "no_such_issue_script")


def test_a_git_listing_that_cannot_start_falls_back_and_says_so(tmp_path, residue_lib, monkeypatch) -> None:
    """The git probe has two failure shapes — a nonzero exit and a binary that cannot
    start — and only the first was exercised."""
    monkeypatch.setattr(
        residue_lib.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(OSError("no git"))
    )
    write_record(tmp_path, "g.md", "Premise-residue: #601 — reason\n")
    scan = residue_lib.scan_residue(tmp_path, 601)
    assert scan["provenance"]["listing_mode"] == "rglob-no-git"
    assert len(scan["declining"]) == 1


def test_a_fenced_marker_is_a_channel_gap_in_classify(premise_lib) -> None:
    """The fenced-marker gap branch had no test: an unbalanced fence can hide every
    marker below it, so the suppression must refuse rather than footnote."""
    residue = ran_clean()
    residue["provenance"]["fenced_markers_skipped"] = ["charness-artifacts/goals/g.md:4"]
    verdict = premise_lib.classify(caller_verdict="refuted", residue=residue)
    assert verdict["state"] == premise_lib.PREMISE_REFUTED_WITH_LIVE_RESIDUE
    assert "fenced blocks" in verdict["reason"]


def test_a_premise_file_key_that_is_not_an_issue_number_is_skipped(tmp_path, premise_cli) -> None:
    """A stray key is not a judgement about anything, so it is dropped rather than
    raising — the file is a human's notes and one bad line must not lose the rest."""
    premise_file = tmp_path / "p.json"
    premise_file.write_text(
        json.dumps({"not-a-number": "holds", "#9": "refuted"}), encoding="utf-8"
    )
    verdicts = premise_cli.load_premise_verdicts(premise_file)
    assert set(verdicts) == {9}


def test_the_script_runs_as_a_command_and_exits_nonzero_on_a_bad_premise_file(tmp_path) -> None:
    """Covers the `__main__` entry an operator actually invokes, not just `main()`.

    A module whose CLI entry is only ever called in-process can ship an import-time
    or argv-shape break that every in-process test misses.
    """
    import subprocess
    import sys

    premise_file = tmp_path / "p.json"
    premise_file.write_text("[]", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "recount_premise_state.py"),
            "--repo-root", str(tmp_path),
            "--premise-file", str(premise_file),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["ok"] is False
    assert "JSON object" in payload["error"]


def test_a_candidate_that_yields_no_loader_is_skipped_not_crashed(tmp_path, premise_cli, monkeypatch) -> None:
    """A defensive branch, and this test says plainly what it proves and what it does not.

    `spec_from_file_location` returns a loaderless spec only for a path Python cannot
    recognise as a module, which the `is_file()` guard above makes unreachable for the
    `.py` candidates this loader is given. So this proves the guard SKIPS rather than
    raises — it does not prove the guard is reachable in production. Every sibling
    loader in this repo carries the same guard; deleting it here would be the odd one
    out, and a loader that crashed on an unloadable candidate would fail a whole run
    for a file it was only ever going to skip.
    """
    import pytest

    monkeypatch.setattr(premise_cli.importlib.util, "spec_from_file_location", lambda *a, **k: None)
    premise_cli._MODULES.pop("recount_premise_lib", None)
    with pytest.raises(ImportError, match="not found beside"):
        premise_cli.sibling("recount_premise_lib")
    premise_cli._MODULES.pop("recount_premise_lib", None)
