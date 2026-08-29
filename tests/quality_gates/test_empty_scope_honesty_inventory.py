"""The inventory that reports what a detector says when it establishes nothing.

`test_empty_scope_refusals.py` enforces the rule over a hand-written list of 14
scripts; this inventory discovers ~130 by glob and observes each one. These cases
pin the classification -- the part that decides which bucket a detector lands in --
and the inventory's own empty-scope behaviour, because an inventory that reported a
clean table over a discovery glob that matched nothing would be the very defect it
measures.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from .support import ROOT, run_script

SCRIPT = ROOT / "skills/public/quality/scripts/inventory_empty_scope_honesty.py"


def _load():
    from .seeding_support import load_module

    return load_module("inventory_empty_scope_honesty", SCRIPT)


def test_classification_separates_the_defect_from_the_sanctioned_pass() -> None:
    """The whole point of the inventory is this distinction.

    A discovered empty set is a REAL answer and stays a cheap pass -- but it has to
    say so. Asserting success over it is the defect. Both exit 0, so exit code alone
    cannot separate them and the classifier is what does.
    """

    module = _load()

    assert module.classify(0, "status: empty-scope\nchecked_files: 0\n")[0] == "honest-pass"
    assert module.classify(0, "Validated code length limits for 0 file(s).")[0] == (
        "positive-verdict-over-zero"
    )
    assert module.classify(1, "no packaging manifests found")[0] == "refused"
    assert module.classify(0, "")[0] == "silent-pass"
    assert module.classify(0, "No presets found.")[0] == "prose-only"


def test_a_detector_that_says_both_is_credited_with_the_marker() -> None:
    """Ordering matters and is not incidental: `check-markdown` prints an advisory
    AND a validated line. Matching the positive verdict first would file an honest
    detector as a defect, which would make the defect bucket unreadable."""

    module = _load()

    both = "Validated 0 file(s).\nstatus: empty-scope\n"
    assert module.classify(0, both)[0] == "honest-pass"


def test_unprobed_is_its_own_bucket_and_is_never_a_pass() -> None:
    """The probe's own blind class, kept visible. A detector it could not judge must
    not be counted as honest -- that would be this inventory committing the defect it
    exists to find."""

    module = _load()

    assert module.classify(None, "")[0] == "unprobed"
    assert module.classify(2, "usage: check_x.py [-h]")[0] == "unprobed"
    assert module.classify(0, "Traceback (most recent call last):\n  File ...")[0] == "unprobed"


def test_libraries_are_not_counted_as_detectors(tmp_path: Path) -> None:
    """`check_coverage_lib.py` matches `check_*.py` and has no CLI. Probing it would
    measure "a library printed nothing" and file it as a silent pass."""

    module = _load()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "check_real.py").write_text("", encoding="utf-8")
    (tmp_path / "scripts" / "check_thing_lib.py").write_text("", encoding="utf-8")

    assert module.discover_detectors(tmp_path) == ["scripts/check_real.py"]


def test_an_empty_discovery_glob_reports_its_own_empty_scope(tmp_path: Path) -> None:
    """The inventory applied to itself: no detectors found is not a clean report."""

    module = _load()
    report = module.build_report(tmp_path, empty_repo_parent=tmp_path / "probes")

    assert report["detectors_discovered"] == 0
    assert report["status"] == "empty-scope"
    assert report["counts"] == {}


def test_the_real_repo_run_is_a_reading_surface_not_a_gate(tmp_path: Path) -> None:
    """Exit 0 WITH findings, by design.

    The 2026-08-29 retro asked for an inventory to read for gaps and said whether a
    gate follows is a later question. This repo has detectors in the defect bucket
    today, so a run that exited non-zero here would mean the inventory had been armed
    without that decision being made.
    """

    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    (repo / "scripts" / "check_liar.py").write_text(
        "import argparse\n"
        "p = argparse.ArgumentParser()\n"
        "p.add_argument('--repo-root')\n"
        "p.parse_args()\n"
        "print('Validated everything for 0 file(s).')\n",
        encoding="utf-8",
    )

    result = run_script(str(SCRIPT), "--repo-root", str(repo), "--summary", cwd=ROOT)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["counts"]["positive-verdict-over-zero"] == 1
    assert payload["positive_verdict_over_zero_sample"] == ["scripts/check_liar.py"]

    # ...and the opt-in flag is what turns the same finding into a refusal, so the
    # non-gate posture is a CHOICE this test pins rather than an absence of teeth.
    armed = run_script(
        str(SCRIPT), "--repo-root", str(repo),
        "--require-no-positive-verdict-over-zero", "--summary", cwd=ROOT,
    )
    assert armed.returncode == 1, armed.stdout + armed.stderr
    assert "scripts/check_liar.py" in armed.stderr
