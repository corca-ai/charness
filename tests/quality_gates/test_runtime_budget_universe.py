"""#546: a budgeted runtime label the runner cannot name is an unenforceable bar.

The gate under test answers membership, not history. These tests pin both what it
refuses and -- more importantly for this issue -- what it deliberately does NOT
refuse, because the previous repair on this surface was reverted for refusing too
much and a test suite that only pins the teeth would let that recur.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE = REPO_ROOT / "scripts" / "check_runtime_budget_universe.py"
UNIVERSE = REPO_ROOT / "scripts" / "quality_label_universe.py"

RUNNER_STUB = """#!/usr/bin/env bash
queue_timed() {
  local label="$1"
  shift
  run_it "$label" "$@"
}
queue_selected() {
  local label="$1"
  shift
  queue_timed "$label" "$@"
}
queue_selected "alpha-gate" python3 alpha.py
queue_timed "beta-gate" python3 beta.py
if [[ "${OPT_IN:-0}" == "1" ]]; then
  queue_timed "opt-in-gate" python3 opt.py
fi
"""


def _write_repo(
    tmp_path: Path,
    *,
    runner: str | None = RUNNER_STUB,
    adapter: str | None = None,
) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".agents").mkdir(parents=True)
    if runner is not None:
        (repo / "scripts" / "run-quality.sh").write_text(runner, encoding="utf-8")
    if adapter is not None:
        (repo / ".agents" / "quality-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def _payload(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


def test_universe_reads_every_queue_wrapper_not_only_queue_selected(tmp_path: Path) -> None:
    repo = _write_repo(tmp_path)
    result = _run(UNIVERSE, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    sources = _payload(result)["sources"]
    # `beta-gate` reaches the queue through `queue_timed`, which the pre-2026-08-10
    # reader could not see. That blindness is the defect this source list closes.
    assert "beta-gate" in sources["queue_call_sites"]
    assert "alpha-gate" in sources["queue_call_sites"]


def test_universe_excludes_dispatcher_bodies_but_not_other_functions(
    tmp_path: Path,
) -> None:
    """`queue_timed "$label"` inside a wrapper is plumbing, not a gate name -- but a
    LITERAL call inside an ordinary function is a real gate and must survive.

    The negative half alone was near-unfalsifiable: deleting the dispatcher
    exclusion makes the reader RAISE, so the run would die in `json.loads` rather
    than on the assertion it is named for. The positive half is the discriminating
    case for the function tracker, and it is what fails if the exclusion is widened
    from "dispatchers" to "any function".
    """
    runner = RUNNER_STUB + """
phase_two() {
  queue_selected "inside-a-plain-function" python3 c.py
}
phase_two
"""
    repo = _write_repo(tmp_path, runner=runner)
    result = _run(UNIVERSE, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    labels = _payload(result)["labels"]
    assert not any("$" in label for label in labels)
    assert "inside-a-plain-function" in labels


def test_universe_reads_a_label_across_a_line_continuation(tmp_path: Path) -> None:
    """An ordinary long-line wrap is not a defect. Before continuations were
    joined, the label landed on a line whose head was the previous one, so the
    reader either dropped the gate silently or refused a correct file with a
    remedy ("spell the label literally") that did not apply."""
    runner = RUNNER_STUB + '''
queue_selected \\
  "wrapped-gate" python3 wrapped.py
'''
    repo = _write_repo(tmp_path, runner=runner)
    result = _run(UNIVERSE, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    assert "wrapped-gate" in _payload(result)["labels"]


def test_universe_refuses_a_label_outside_the_runtime_label_shape(
    tmp_path: Path,
) -> None:
    """A hard-red path on a pre-push gate, so it owes a pin.

    The label is single-token on purpose: a spaced one never reaches the shape
    check, because `\\S+` captures only `"Not` and the literal rule refuses it
    first. Writing this test with spaces would have exercised the neighbouring
    branch while claiming to cover this one.
    """
    runner = RUNNER_STUB + '\nqueue_selected "Check-Foo" python3 x.py\n'
    repo = _write_repo(tmp_path, runner=runner)
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "not a runtime" in result.stderr


def test_universe_refuses_a_non_literal_label_at_a_call_site(tmp_path: Path) -> None:
    """A shrunk universe turns a correct budget into a blocking false red whose
    only escape is `--no-verify`, so an unresolvable call site fails loudly."""
    runner = RUNNER_STUB + '\nqueue_selected "$computed" python3 x.py\n'
    repo = _write_repo(tmp_path, runner=runner)
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "non-literal label" in result.stderr
    assert "run-quality.sh:" in result.stderr


def test_universe_enumerates_all_four_aggregate_labels(tmp_path: Path) -> None:
    """The aggregate label is computed from the run's own mode, so no single run
    can observe more than one. Enumerating the cross-product is what stops the
    other three from reading as renamed."""
    repo = _write_repo(tmp_path)
    aggregate = _payload(_run(UNIVERSE, "--repo-root", str(repo), "--json"))["sources"][
        "aggregate"
    ]
    assert sorted(aggregate) == [
        "run-quality-full",
        "run-quality-full-release",
        "run-quality-read-only",
        "run-quality-read-only-release",
    ]


@pytest.mark.parametrize(
    ("probe_class", "expected"),
    [("standing", ["charness-version"]), ("release", [])],
)
def test_startup_probes_are_admitted_only_when_standing(
    tmp_path: Path, probe_class: str, expected: list[str]
) -> None:
    """`measure_startup_probes.py` is invoked `--class standing` and filters on the
    field, so a probe of any other class is named in the adapter and never
    measured -- admitting it would pass a bar that can never be exercised."""
    adapter = (
        "startup_probes:\n"
        "  - label: charness-version\n"
        "    command:\n"
        "      - python3\n"
        "      - charness\n"
        '      - "--version"\n'
        f"    class: {probe_class}\n"
        "    samples: 3\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    payload = _payload(_run(UNIVERSE, "--repo-root", str(repo), "--json"))
    assert payload["sources"]["standing_startup_probes"] == expected


def test_probe_reader_stops_at_the_next_top_level_key(tmp_path: Path) -> None:
    """The real adapter has `quality_phases:` after `startup_probes:`, and it has
    its OWN `- label:` entries. A reader that ran past the block boundary would
    admit `inventory-sloc` as a startup probe -- and it is a queued gate, so the
    leak would be invisible in the merged universe and visible only here."""
    adapter = (
        "startup_probes:\n"
        "  - label: charness-version\n"
        "    class: standing\n"
        "quality_phases:\n"
        "  - label: inventory-sloc\n"
        "    class: standing\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    payload = _payload(_run(UNIVERSE, "--repo-root", str(repo), "--json"))
    assert payload["sources"]["standing_startup_probes"] == ["charness-version"]


def test_probe_reader_handles_several_probes_and_a_flush_free_list_style(
    tmp_path: Path,
) -> None:
    """Two probes, only one standing, written with the list flush against its key.
    The first hand-rolled parser decided the block had ENDED on that style and
    dropped every probe, orphaning a label budgeted in all four blocks."""
    adapter = (
        "startup_probes:\n"
        "- label: first-probe\n"
        "  class: release\n"
        "- label: second-probe\n"
        "  class: standing\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    payload = _payload(_run(UNIVERSE, "--repo-root", str(repo), "--json"))
    assert payload["sources"]["standing_startup_probes"] == ["second-probe"]


def test_gate_is_not_armed_when_the_runner_names_no_gate_labels(
    tmp_path: Path,
) -> None:
    """Presence of a runner is not a derivable universe. A runner driving its gates
    from a list file has zero literal call sites; arming on the four aggregate
    labels alone would refuse EVERY other budget, with a remedy telling the
    operator to delete correct bars."""
    adapter = "runtime_budgets:\n  some-gate: 1000\n"
    repo = _write_repo(tmp_path, runner="#!/usr/bin/env bash\necho hi\n", adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    assert _payload(result)["armed"] is False


def test_gate_tolerates_a_profile_without_a_budgets_mapping(tmp_path: Path) -> None:
    adapter = (
        "runtime_budgets:\n"
        "  alpha-gate: 1000\n"
        "runtime_budget_profiles:\n"
        "  malformed:\n"
        "    note: no budgets key here\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_gate_refuses_a_budget_whose_label_the_runner_cannot_name(tmp_path: Path) -> None:
    adapter = "runtime_budgets:\n  alpha-gate: 1000\n  alpha-gatte: 1000\n"
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "alpha-gatte" in result.stderr
    assert "alpha-gate " not in result.stderr.replace("alpha-gatte", "")


def test_gate_checks_every_budget_block_not_only_the_selected_profile(
    tmp_path: Path,
) -> None:
    """`profile_budgets` returns exactly one block per run, so a single-profile
    reader never reaches the blocks nobody on this machine runs -- which is
    precisely where a typo outlives the repo."""
    adapter = (
        "runtime_budgets:\n"
        "  alpha-gate: 1000\n"
        "runtime_budget_profiles:\n"
        "  never-selected-here:\n"
        "    budgets:\n"
        "      beta-gate: 1000\n"
        "      ghost-gate: 1000\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "ghost-gate" in result.stderr
    assert "runtime_budget_profiles.never-selected-here" in result.stderr


def test_gate_does_not_refuse_a_conditional_label_that_never_runs(tmp_path: Path) -> None:
    """THE non-claim, pinned. `opt-in-gate` is queued only under an env opt-in, so
    its bar can never fire on an ordinary run -- a real instance of #546 that this
    gate deliberately passes. Membership is what is decidable without operator
    intent; whether a named condition is still satisfiable is not, and refusing it
    here is exactly what got the previous repair reverted."""
    adapter = "runtime_budgets:\n  opt-in-gate: 1000\n"
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_gate_reads_no_sample_history(tmp_path: Path) -> None:
    """A fresh machine with no signals file answers identically to one with a year
    of samples. The reverted repair hard-failed a first run; this cannot."""
    adapter = "runtime_budgets:\n  alpha-gate: 1000\n"
    repo = _write_repo(tmp_path, adapter=adapter)
    assert not (repo / ".charness").exists()
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_gate_degrades_loudly_when_the_runner_is_absent(tmp_path: Path) -> None:
    """A consumer repo installs the quality skill without vendoring the runner.
    Refusing its budgets would be a blocking false red telling the operator to
    delete correct bars; passing SILENTLY would re-create #546 there. The line is
    WARN-prefixed because `print_phase_output` surfaces a phase log only on a
    WARN/ADVISORY marker -- an unprefixed degrade renders as a bare green PASS."""
    adapter = "runtime_budgets:\n  anything-at-all: 1000\n"
    repo = _write_repo(tmp_path, runner=None, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("WARN ")
    assert "not armed" in result.stdout


def test_gate_is_inert_without_an_adapter(tmp_path: Path) -> None:
    repo = _write_repo(tmp_path, adapter=None)
    result = _run(GATE, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    assert _payload(result)["armed"] is False


def test_this_repo_has_no_orphaned_budget(tmp_path: Path) -> None:
    """The live blast-radius measurement, kept as a test rather than a claim: all
    38 budgeted labels across all four blocks are names the runner still knows, so
    arming this gate refused nothing that previously passed."""
    result = _run(GATE, "--repo-root", str(REPO_ROOT), "--json")
    assert result.returncode == 0, result.stderr
    payload = _payload(result)
    assert payload["armed"] is True
    assert payload["unknown_labels"] == []
    # `> 0` would have stayed green through the regression that matters most here:
    # dropping `runtime_budget_profiles` from `budgeted_labels` leaves the ten
    # top-level budgets and hides every profile block, which is the exact
    # single-profile blindness this gate reads the union to fix.
    assert payload["checked"] >= 38, payload["checked"]
    # `charness-version` is budgeted in all four blocks and reachable ONLY through
    # the standing-probe source; if that source empties, it orphans and the gate
    # turns red for a correct adapter.
    assert payload["universe_sources"]["standing_startup_probes"] == 1


def test_an_unparseable_adapter_is_a_named_refusal_not_a_traceback(
    tmp_path: Path,
) -> None:
    """The reader is consumed by `run-quality.sh` at STARTUP, so an unnamed
    exception here aborts the entire run with a traceback blaming the queue lines --
    for an edit to a block scalar elsewhere in the adapter. Before this reader
    existed, the same adapter defect surfaced as one red gate with an accurate
    message; a repair must not make the diagnostic worse than what it replaced."""
    repo = _write_repo(tmp_path, adapter="startup_probes:\n  - label: x\n    note: >+\n      bad header\n")
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "could not be parsed" in result.stderr
    assert "Traceback" not in result.stderr


def test_a_declared_probe_with_no_readable_label_is_refused(tmp_path: Path) -> None:
    """Declared-but-unreadable RAISES rather than shrugging. Returning `[]` would
    drop `charness-version` -- budgeted in every block -- and turn the budget gate
    red for a correct adapter, with a remedy naming the wrong repair."""
    repo = _write_repo(tmp_path, adapter="startup_probes:\n  - class: standing\n")
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "no readable" in result.stderr


def test_a_probe_that_is_simply_not_standing_is_not_a_refusal(tmp_path: Path) -> None:
    """The discriminating case for the rule above: unreadable is a refusal, but a
    readable probe of another class is just not measured, and answering that is the
    source's job."""
    repo = _write_repo(
        tmp_path, adapter="startup_probes:\n  - label: release-probe\n    class: release\n"
    )
    result = _run(UNIVERSE, "--repo-root", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    assert _payload(result)["sources"]["standing_startup_probes"] == []


def test_stdout_carries_labels_or_nothing_never_prose(tmp_path: Path) -> None:
    """`run-quality.sh` inserts each stdout line into the universe as a key. A prose
    sentence on stdout became a one-element universe, which defeated the runner's
    own "empty means do not assert" degrade and refused the first gate with a remedy
    about queue-line quoting. stdout is the machine surface."""
    repo = _write_repo(tmp_path, runner=None)
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert "not derivable" in result.stderr
