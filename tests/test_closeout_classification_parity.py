"""The parity gate is a PROOF SURFACE, so these tests prove it can report what it
exists to report -- not that it is green today.

A parity gate that probes nothing is green in exactly the same way a repo in
perfect parity is. So the load-bearing test here is the MEASUREMENT one: under an
assumed seventh disposition every `exact` site must turn red. A gate that cannot
fail has not been shown to check anything, and #586's whole point is that a green
test can exist for code that never runs.

The reachability tests matter for the same reason. This gate was written for the
issue reporting "a check that passes its own direct-call test while never firing
on the wired path"; shipping it unqueued would make it the seventh instance.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
GATE_REL = "scripts/check_closeout_classification_parity.py"
_gate = load_script_module(
    "scripts.check_closeout_classification_parity",
    ROOT / GATE_REL,
)
_RUN_QUALITY = (ROOT / "scripts" / "run-quality.sh").read_text(encoding="utf-8")

# The value the measurement runs assume. It is deliberately NOT a plausible
# disposition name a future author might really add, so a real addition can never
# silently satisfy a test that was meant to prove the gate fires.
ASSUMED = "__assumed-seventh-disposition__"


def _canonical() -> tuple[str, ...]:
    return tuple(
        _gate._attr(_gate._load(ROOT, _gate.CANONICAL_REL), _gate.CANONICAL_ATTR, _gate.CANONICAL_REL)
    )


def _verdict(sites) -> str:
    saved = _gate.SITES
    _gate.SITES = tuple(sites)
    try:
        return _gate.evaluate(ROOT)["status"]
    finally:
        _gate.SITES = saved


def _run(*extra: str) -> tuple[int, dict]:
    result = run_loaded_script_main(
        GATE_REL,
        _gate,
        "--repo-root",
        str(ROOT),
        *extra,
    )
    return result.returncode, yaml.safe_load(result.stdout)


# The roster, pinned by VALUE. Deriving it from _gate.SITES (as an earlier version
# did) makes the coverage test tautological: deleting a site keeps it green.
EXPECTED_SITE_IDS = [
    "audit-brief-known-classifications",
    "commit-msg-hook-regex",
    "release-closeout-message-regex",
    "release-cli-close-issue-choices",
    "issue-plan-classification-actions",
    "closeout-classification-fields",
]


def test_the_gate_is_queued_in_the_quality_run():
    """#586's shape is a check nobody reaches. An unqueued parity gate is instance seven.

    Matches a LIVE `queue_selected` line: an earlier version asserted only that the
    filename appeared somewhere in the script, which a commented-out queue line
    satisfies.
    """
    assert re.search(
        r"^queue_selected \"check-closeout-classification-parity\" .*check_closeout_classification_parity\.py",
        _RUN_QUALITY,
        re.MULTILINE,
    )


def test_the_declared_site_roster_is_the_expected_one():
    """Deleting a site is a coverage loss, and must not be invisible."""
    assert [site["id"] for site in _gate.SITES] == EXPECTED_SITE_IDS


def test_the_tree_is_in_parity_through_the_command_an_operator_runs():
    code, payload = _run()
    assert code == 0, payload
    assert payload["status"] == "pass"
    assert [site["status"] for site in payload["sites"]] == ["pass"] * len(_gate.SITES)


def test_every_declared_site_is_actually_probed():
    """A site that silently vanished from the report is an unmeasured surface."""
    _, payload = _run()
    assert [site["id"] for site in payload["sites"]] == EXPECTED_SITE_IDS


def test_an_assumed_seventh_disposition_turns_every_exact_site_red():
    """THE measurement. This is what the gate catches; a green run does not show it."""
    code, payload = _run("--assume-classification", ASSUMED)
    assert code == 1, payload
    assert payload["status"] == "fail"
    exact = [site for site in payload["sites"] if site["arity"] == "exact"]
    assert exact, "the gate declares no exact site, so it holds nothing"
    for site in exact:
        assert site["status"] == "fail", site
        assert site["missing"] == [ASSUMED], site


def test_a_hypothetical_run_says_it_is_hypothetical():
    """Otherwise a measurement transcript reads as a verdict about the tree."""
    _, payload = _run("--assume-classification", ASSUMED)
    assert payload["hypothetical"]["assumed_classifications"] == [ASSUMED]
    # The subset site cannot be judged for an assumed value; saying so is the point.
    subset = [site for site in payload["sites"] if site["arity"] == "subset"]
    assert subset
    for site in subset:
        assert site["status"] == "pass"
        assert ASSUMED in site["absent_by_design"]


def test_an_unprobeable_site_reports_not_run_and_never_a_pass(monkeypatch):
    """The fail-open this gate could introduce: a broken probe reading as parity."""

    def broken(_repo_root, _canonical):
        raise _gate.ProbeError("probe deliberately broken by the test")

    site = {
        "id": "broken-probe",
        "arity": "exact",
        "surface": "nowhere",
        "why": "test",
        "build": broken,
    }
    monkeypatch.setattr(_gate, "SITES", (site,))
    result = _gate.evaluate(ROOT)
    assert result["status"] == "not-run"
    assert result["sites"][0]["status"] == "not-run"
    payload = _gate.report(result, ROOT)
    assert payload["status"] == "not-run"
    assert "remedy" in payload


def test_a_site_accepting_anything_at_all_fails_rather_than_reading_as_parity():
    """A permissive surface accepts every canonical value, so positives-only reads green."""
    site = {
        "id": "accepts-everything",
        "arity": "exact",
        "surface": "nowhere",
        "why": "test",
        "build": lambda _repo_root, _canonical: (lambda _value: True),
    }
    original = _gate.SITES
    _gate.SITES = (site,)
    try:
        result = _gate.evaluate(ROOT)
    finally:
        _gate.SITES = original
    assert result["status"] == "fail"
    assert result["sites"][0]["accepts_non_classification"] == list(_gate.NON_CLASSIFICATIONS)


def test_the_gate_carries_no_copy_of_the_vocabulary_it_is_judging():
    """A parity gate with its own literal tuple is a seventh copy of the defect.

    Both quoting forms: an earlier version checked only the double-quoted spelling.
    """
    source = (ROOT / GATE_REL).read_text(encoding="utf-8")
    # The `absent_by_design` declarations are policy about ONE site, not a copy of
    # the enumeration, so they are excluded here and held instead by the runtime
    # staleness check below. Everything else must read the vocabulary live.
    declared = {value for site in _gate.SITES for value in site.get("absent_by_design", ())}
    for value in _canonical():
        if value in declared:
            continue
        for literal in (f'"{value}"', f"'{value}'"):
            assert literal not in source, f"the gate hardcodes {literal} instead of reading it live"


def test_a_stale_declared_absence_is_not_run_rather_than_silently_permissive():
    """A declared absence naming a value the vocabulary lost must not keep passing."""
    ledger = _site("closeout-classification-fields")
    assert _verdict([{**ledger, "absent_by_design": ("question", "retired-disposition")}]) == "not-run"


@pytest.mark.parametrize("site", _gate.SITES, ids=lambda site: site["id"])
def test_each_site_probe_discriminates_rather_than_answering_yes_to_everything(site):
    """Per-site version of the permissive check: each real probe must refuse a non-value."""
    canonical = _canonical()
    accepts = site["build"](ROOT, canonical)
    assert accepts(canonical[0]) is True, f"{site['id']} refuses a canonical classification"
    # EVERY sentinel, not just the underscore-wrapped one: a regex loosened to
    # `[a-z][a-z-]*` refuses that shape while enumerating nothing.
    for sentinel in _gate.NON_CLASSIFICATIONS:
        assert accepts(sentinel) is False, f"{site['id']} accepts non-classification {sentinel!r}"


# --- Round-1 reviewer findings, each pinned as the mutation it was reported as ---


def _site(site_id: str) -> dict:
    return next(site for site in _gate.SITES if site["id"] == site_id)


def test_a_subset_site_may_omit_only_the_absences_it_declared():
    """`subset` used to mean ANY subset, so deleting the ledger's `bug` row passed.

    That row carries root-cause/prevention for every bug closeout, and the accessor
    falls through to DEFAULT_FIELDS silently.
    """
    ledger = _site("closeout-classification-fields")
    assert "question" in ledger["absent_by_design"], "the permitted absences must be declared, not implied"
    deleted_bug = {**ledger, "build": lambda _r, _c: (lambda v: v in {"feature", "consolidated"})}
    assert _verdict([deleted_bug]) == "fail"


def test_an_unrecognized_arity_is_not_run_rather_than_permissive():
    """A one-character typo used to demote an exact site to permissive, silently."""
    assert _verdict([{**_site("commit-msg-hook-regex"), "arity": "Exact"}]) == "not-run"


def test_a_site_that_stopped_enumerating_fails_even_if_it_refuses_the_first_sentinel():
    """A regex loosened to `[a-z][a-z-]*` accepts every canonical value and `banana`."""
    permissive = re.compile(r"(?im)^\s*classification\s*:\s*(?P<classification>[a-z][a-z-]*)\s*$")

    def build(_repo_root, _canonical):
        def accepts(value: str) -> bool:
            match = permissive.search(f"Classification: {value}")
            return bool(match) and match.group("classification") == value

        return accepts

    assert accepts_underscore_sentinel_is_refused(build)
    assert _verdict([{**_site("commit-msg-hook-regex"), "build": build}]) == "fail"


def accepts_underscore_sentinel_is_refused(build) -> bool:
    """The permissive pattern must genuinely refuse sentinel[0], or the test is hollow."""
    return build(ROOT, _canonical())(_gate.NON_CLASSIFICATIONS[0]) is False


def test_any_probe_exception_is_one_not_run_site_not_a_lost_report():
    """A non-ProbeError used to escape evaluate() and suppress every other verdict."""

    def boom(_repo_root, _canonical):
        raise IndexError("no such group")

    saved = _gate.SITES
    _gate.SITES = (
        {**_site("commit-msg-hook-regex"), "build": boom},
        _site("audit-brief-known-classifications"),
    )
    try:
        payload = _gate.evaluate(ROOT)
    finally:
        _gate.SITES = saved
    assert payload["status"] == "not-run"
    assert payload["sites"][0]["status"] == "not-run"
    assert "IndexError" in payload["sites"][0]["reason"]
    # The healthy sibling still rendered its own verdict.
    assert payload["sites"][1]["status"] == "pass"


def test_assuming_a_classification_the_tree_already_has_is_refused():
    """Otherwise a re-measurement yields an exit-0 run wearing the hypothetical badge."""
    code, payload = _run("--assume-classification", _canonical()[0])
    assert code == _gate.UNESTABLISHED_EXIT, payload
    assert payload["status"] == "not-run"
    assert "already canonical" in payload["reason"]


def test_the_runner_maps_this_gates_not_run_byte_to_unproven_not_to_a_pass():
    """Repair 7 had no test: reverting the label was invisible to this suite."""
    labels = re.search(r'^UNESTABLISHED_CAPABLE_LABELS="([^"]*)"', _RUN_QUALITY, re.MULTILINE)
    assert labels, "the runner no longer declares an unestablished-capable label list"
    assert "check-closeout-classification-parity" in labels.group(1).split()
    assert re.search(r"^UNESTABLISHED_EXIT=3\b", _RUN_QUALITY, re.MULTILINE) or _gate.UNESTABLISHED_EXIT == 3


def test_a_site_that_dropped_one_classification_FAILS_rather_than_reporting_not_run():
    """The fail-open repair 7 unmasked: a liveness guard keyed on `canonical[0]`.

    A site that had merely dropped `bug` raised ProbeError, resolved to not-run, and
    -- once the label became unestablished-capable -- exited the whole quality run 0
    on a real parity break. Liveness must mean "observes anything", not "accepts bug".
    """
    canonical = _canonical()
    for site_id in ("release-cli-close-issue-choices", "commit-msg-hook-regex"):
        site = _site(site_id)
        real = site["build"]

        def build(repo_root, canon, _real=real):
            accepts_real = _real(repo_root, canon)
            allowed = set(canon) - {canon[0]}
            return lambda value: value in allowed and accepts_real(value)

        assert _verdict([{**site, "build": build}]) == "fail", site_id
    assert canonical[0] == "bug"


def test_a_declared_absence_that_is_no_longer_absent_is_not_a_standing_exemption():
    """Otherwise the declaration silently licenses a later deletion of that row."""
    ledger = _site("closeout-classification-fields")
    everything_present = {**ledger, "build": lambda _r, _c: (lambda v: v not in _gate.NON_CLASSIFICATIONS)}
    assert _verdict([everything_present]) == "not-run"


def test_the_ledger_site_is_probed_by_row_membership_not_by_differing_from_the_default():
    """A row whose value equals DEFAULT_FIELDS has a row, and must not read as missing."""
    rel = _site("closeout-classification-fields")["surface"].split(":")[0]
    module = _gate._load(ROOT, rel)
    assert hasattr(module, "has_classification_row")
    assert module.has_classification_row("bug") is True
    assert module.has_classification_row("question") is False
