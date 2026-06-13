"""Floor-addition restraint nudge tests (spec achieve-efficiency,
follow-up:floor-addition-restraint-nudge).

A non-blocking advisory that flags a new blocking floor (a new
`report["ok"] = False` site, or a new REQUIRED_*/_SECTIONS/_EVIDENCE_NAMES
member) added without a recorded Floor-Addition Restraint call. Both polarities
are demonstrable: it fires on a synthetic new-floor diff and stays silent on an
unchanged diff or when the restraint call is recorded.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = ROOT / "scripts/slice_closeout_advisories.py"


def _load():
    spec = importlib.util.spec_from_file_location("slice_closeout_advisories", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    # the module imports `runtime_bootstrap` from scripts/ — put it on the path
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    spec.loader.exec_module(module)
    return module


adv = _load()


# --- pure detectors (no git) --------------------------------------------------


def test_ok_false_site_count_matches_spacing_variants() -> None:
    text = 'report["ok"] = False\nreport[ \'ok\' ]=False\nother = True\n'
    assert adv.ok_false_site_count(text) == 2
    assert adv.ok_false_site_count("no floors here\n") == 0


def test_required_set_members_single_and_multiline() -> None:
    single = 'CLOSEOUT_EVIDENCE_NAMES = ("retro_artifact", "host_log_probe")\n'
    assert adv.required_set_members(single)["CLOSEOUT_EVIDENCE_NAMES"] == {"retro_artifact", "host_log_probe"}
    multi = 'REQUIRED_SECTIONS = (\n    "Goal",\n    "Non-Goals",\n)\n'
    assert adv.required_set_members(multi)["REQUIRED_SECTIONS"] == {"Goal", "Non-Goals"}
    # an unrelated UPPER_SNAKE assignment is ignored
    assert "MAX_RETRIES" not in adv.required_set_members("MAX_RETRIES = (3,)\n")


def test_required_set_members_excludes_non_floor_sets() -> None:
    # REQUIRED/_SECTIONS substrings also name non-floor sets — adding a member to
    # those is not adding a blocking floor, so they must not be tracked.
    for src in (
        'OPTIONAL_SECTIONS = ("Notes",)\n',
        'RECORDED_WORK_SECTIONS = ("Slice Log",)\n',
        'NARRATION_REQUIRED_SECTIONS = ("Waste",)\n',
        'SCOPE_GAP_CAPACITY_ADVISORY_SECTIONS = ("X",)\n',
    ):
        assert adv.required_set_members(src) == {}, src
    # a genuine floor set is still tracked
    assert "REQUIRED_SECTIONS" in adv.required_set_members('REQUIRED_SECTIONS = ("Goal",)\n')


def test_detect_new_floors_ok_false_and_required_member() -> None:
    base = 'X = 1\nREQUIRED_SECTIONS = ("Goal",)\n'
    new = 'X = 1\nREQUIRED_SECTIONS = ("Goal", "Boundaries")\nreport["ok"] = False\n'
    kinds = {f["kind"] for f in adv.detect_new_floors(base, new, "scripts/x.py")}
    assert kinds == {"ok_false_site", "required_set_entry"}


def test_detect_new_floors_silent_when_unchanged() -> None:
    same = 'REQUIRED_SECTIONS = ("Goal",)\nreport["ok"] = False\n'
    assert adv.detect_new_floors(same, same, "scripts/x.py") == []
    # refactoring an existing floor (no NEW site) also stays silent
    moved = 'def g():\n    report["ok"] = False\n'
    orig = 'report["ok"] = False\n'
    assert adv.detect_new_floors(orig, moved, "scripts/x.py") == []


def test_restraint_call_recorded_distinguishes_call_from_mention() -> None:
    assert adv.restraint_call_recorded("Floor-Addition Restraint: chose an advisory over a blocking gate")
    assert adv.restraint_call_recorded("# floor-addition-restraint: advisory is enough here")
    # a bare mention of the rule (heading / follow-up token) is NOT a recorded call
    assert not adv.restraint_call_recorded("## Floor-Addition Restraint\n")
    assert not adv.restraint_call_recorded("tracked as follow-up:floor-addition-restraint-nudge")
    # prose that DESCRIBES the marker form mid-sentence is NOT a recorded call (B2):
    # the marker is anchored to line-start, so a paraphrase cannot wrongly silence.
    assert not adv.restraint_call_recorded("record the call (a `Floor-Addition Restraint:` line in the commit)")


# --- git integration: both polarities -----------------------------------------


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo, check=True, capture_output=True, text=True,
    )


def _seed_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    (repo / "scripts").mkdir()
    (repo / "scripts/floory.py").write_text("def check():\n    report = {}\n    return report\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base: no floors")


def test_advise_fires_on_new_floor_without_recorded_call(tmp_path: Path, capsys) -> None:
    _seed_repo(tmp_path)
    (tmp_path / "scripts/floory.py").write_text(
        'def check():\n    report = {}\n    report["ok"] = False\n    return report\n', encoding="utf-8"
    )
    adv.advise_floor_addition_restraint(tmp_path, ["scripts/floory.py"], base="HEAD")
    err = capsys.readouterr().err
    assert "new blocking floor added without a recorded Floor-Addition Restraint call" in err
    assert "implementation-discipline.md" in err  # the advisory names the checklist


def test_advise_silent_when_restraint_call_recorded(tmp_path: Path, capsys) -> None:
    _seed_repo(tmp_path)
    (tmp_path / "scripts/floory.py").write_text(
        "def check():\n    report = {}\n"
        "    # floor-addition-restraint: prose recurred 3x; an advisory could not gate it\n"
        '    report["ok"] = False\n    return report\n', encoding="utf-8"
    )
    adv.advise_floor_addition_restraint(tmp_path, ["scripts/floory.py"], base="HEAD")
    assert capsys.readouterr().err == ""


def test_advise_silent_when_no_new_floor(tmp_path: Path, capsys) -> None:
    _seed_repo(tmp_path)
    (tmp_path / "scripts/floory.py").write_text(
        'def check():\n    report = {"note": "no floor added"}\n    return report\n', encoding="utf-8"
    )
    adv.advise_floor_addition_restraint(tmp_path, ["scripts/floory.py"], base="HEAD")
    assert capsys.readouterr().err == ""


def test_advise_degrades_silently_off_git(tmp_path: Path, capsys) -> None:
    # no git repo at all -> base ref does not resolve -> no crash, no output
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/floory.py").write_text('report["ok"] = False\n', encoding="utf-8")
    adv.advise_floor_addition_restraint(tmp_path, ["scripts/floory.py"], base="origin/main")
    assert capsys.readouterr().err == ""
