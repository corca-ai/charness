"""#546: a budgeted runtime label the runner cannot name is an unenforceable bar.

The gate under test answers membership, not history. These tests pin both what it
refuses and -- more importantly for this issue -- what it deliberately does NOT
refuse, because the previous repair on this surface was reverted for refusing too
much and a test suite that only pins the teeth would let that recur.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.support import run_script

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from runtime_bootstrap import import_repo_module  # noqa: E402

_ADAPTER_LIB = import_repo_module(REPO_ROOT / "scripts/adapter_lib.py", "scripts.adapter_lib")
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


def _run(script: Path, *args: str, real_process: bool = False):
    return run_script(str(script), *args, cwd=REPO_ROOT, real_process=real_process)


def _payload(result) -> dict:
    return yaml.safe_load(result.stdout)


def test_universe_reads_every_queue_wrapper_not_only_queue_selected(tmp_path: Path) -> None:
    repo = _write_repo(tmp_path)
    result = _run(UNIVERSE, "--repo-root", str(repo))
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
    exclusion makes the reader RAISE, so the run would die in `yaml.safe_load` rather
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
    result = _run(UNIVERSE, "--repo-root", str(repo))
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
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "wrapped-gate" in _payload(result)["labels"]


@pytest.mark.parametrize("flags", [(), ("--labels-only",)])
def test_universe_refuses_a_label_outside_the_runtime_label_shape(
    tmp_path: Path, flags: tuple[str, ...]
) -> None:
    """A hard-red path on a pre-push gate, so it owes a pin.

    The label is single-token on purpose: a spaced one never reaches the shape
    check, because `\\S+` captures only `"Not` and the literal rule refuses it
    first. Writing this test with spaces would have exercised the neighbouring
    branch while claiming to cover this one.
    """
    runner = RUNNER_STUB + '\nqueue_selected "Check-Foo" python3 x.py\n'
    repo = _write_repo(tmp_path, runner=runner)
    result = _run(UNIVERSE, "--repo-root", str(repo), *flags)
    assert result.returncode == 1
    assert "not a runtime" in result.stderr


@pytest.mark.parametrize("flags", [(), ("--labels-only",)])
def test_universe_refuses_a_non_literal_label_at_a_call_site(
    tmp_path: Path, flags: tuple[str, ...]
) -> None:
    """A shrunk universe turns a correct budget into a blocking false red whose
    only escape is `--no-verify`, so an unresolvable call site fails loudly."""
    runner = RUNNER_STUB + '\nqueue_selected "$computed" python3 x.py\n'
    repo = _write_repo(tmp_path, runner=runner)
    result = _run(UNIVERSE, "--repo-root", str(repo), *flags)
    assert result.returncode == 1
    assert "non-literal label" in result.stderr
    assert "run-quality.sh:" in result.stderr


def test_universe_enumerates_all_four_aggregate_labels(tmp_path: Path) -> None:
    """The aggregate label is computed from the run's own mode, so no single run
    can observe more than one. Enumerating the cross-product is what stops the
    other three from reading as renamed."""
    repo = _write_repo(tmp_path)
    aggregate = _payload(_run(UNIVERSE, "--repo-root", str(repo)))["sources"][
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
    payload = _payload(_run(UNIVERSE, "--repo-root", str(repo)))
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
    payload = _payload(_run(UNIVERSE, "--repo-root", str(repo)))
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
    payload = _payload(_run(UNIVERSE, "--repo-root", str(repo)))
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
    result = _run(GATE, "--repo-root", str(repo))
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
    payload = _payload(result)
    # The typo alone. `alpha-gate` IS a name the runner queues, and listing it here
    # would send the operator to delete a correct bar -- the exact remedy that got
    # the previous repair on this surface reverted.
    assert [entry["label"] for entry in payload["unknown_labels"]] == ["alpha-gatte"]
    assert "can never be exercised" in payload["summary"]
    assert "delete it" in payload["remedy"]


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
    unknown = {entry["label"]: entry["blocks"] for entry in _payload(result)["unknown_labels"]}
    assert "ghost-gate" in unknown
    # The block is what makes the finding actionable: the operator has to know WHICH
    # of the four budget blocks holds the orphan before they can repair it.
    assert unknown["ghost-gate"] == ["runtime_budget_profiles.never-selected-here"]


def test_gate_does_not_refuse_a_conditional_label_that_never_runs(tmp_path: Path) -> None:
    """THE non-claim, pinned. `opt-in-gate` is queued only under an env opt-in, so
    its bar can never fire on an ordinary run -- a real instance of #546 that this
    gate deliberately passes. Membership is what is decidable without operator
    intent; whether a named condition is still satisfiable is not, and refusing it
    here is exactly what got the previous repair reverted."""
    adapter = (
        "runtime_budgets:\n"
        "  opt-in-gate: 1000\n"
        "runtime_budget_intent:\n"
        "  conditional:\n"
        "    opt-in-gate: \"OPT_IN=1\"\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = _payload(result)
    assert payload["runtime_budget_intent"]["status"] == "configured"
    assert payload["conditional_non_claims"] == [
        {"label": "opt-in-gate", "trigger": "OPT_IN=1", "execution_proven": False}
    ]


def test_gate_refuses_intent_that_does_not_cover_every_budget(tmp_path: Path) -> None:
    adapter = (
        "runtime_budgets:\n"
        "  alpha-gate: 1000\n"
        "  beta-gate: 1000\n"
        "runtime_budget_intent:\n"
        "  always:\n"
        "    - alpha-gate\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 1
    payload = _payload(result)
    assert payload["runtime_budget_intent"]["status"] == "invalid"
    assert payload["runtime_budget_intent"]["missing_labels"] == ["beta-gate"]
    assert any(
        "does not classify budgeted label(s): beta-gate" in error
        for error in payload["runtime_budget_intent"]["errors"]
    )


def test_gate_rejects_a_non_mapping_runtime_budget_intent(tmp_path: Path) -> None:
    adapter = "runtime_budgets:\n  alpha-gate: 1000\nruntime_budget_intent: broken\n"
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 1
    payload = _payload(result)
    assert payload["runtime_budget_intent"]["status"] == "invalid"
    assert any(
        "runtime_budget_intent must be a mapping" in error
        for error in payload["runtime_budget_intent"]["errors"]
    )


def test_gate_rejects_an_intent_label_without_a_budget(tmp_path: Path) -> None:
    adapter = (
        "runtime_budgets:\n"
        "  alpha-gate: 1000\n"
        "runtime_budget_intent:\n"
        "  always:\n"
        "    - alpha-gate\n"
        "  external:\n"
        "    ghost-gate: \"consumer-owned\"\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 1
    payload = _payload(result)
    assert payload["runtime_budget_intent"]["status"] == "invalid"
    assert payload["runtime_budget_intent"]["extra_labels"] == ["ghost-gate"]
    assert any(
        "classifies label(s) with no budget: ghost-gate" in error
        for error in payload["runtime_budget_intent"]["errors"]
    )


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
    delete correct bars; passing SILENTLY would re-create #546 there. The payload's
    `advisory` line is WARN-prefixed because `print_phase_output` surfaces a phase
    log only on a WARN/ADVISORY marker -- an unprefixed degrade renders as a bare
    green PASS."""
    adapter = "runtime_budgets:\n  anything-at-all: 1000\n"
    repo = _write_repo(tmp_path, runner=None, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = _payload(result)
    assert payload["armed"] is False
    assert payload["advisory"].startswith("WARN ")
    assert "not armed" in payload["advisory"]


def test_gate_is_inert_without_an_adapter(tmp_path: Path) -> None:
    repo = _write_repo(tmp_path, adapter=None)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert _payload(result)["armed"] is False


def _declared_budget_labels() -> set[str]:
    """Every budgeted label the adapter declares, across all four blocks.

    Derived from the adapter rather than pinned, because the number moves for
    honest reasons -- deleting a capability deletes its budgets -- and a
    hand-bumped floor answers "still enough" to whatever it was last set to.
    This repo has recorded that exact form as its worst available ratchet shape;
    the union is the thing the assertion actually means.
    """
    adapter = _ADAPTER_LIB.load_yaml_file(REPO_ROOT / ".agents" / "quality-adapter.yaml")
    labels = set(adapter.get("runtime_budgets") or {})
    for profile in (adapter.get("runtime_budget_profiles") or {}).values():
        labels.update((profile or {}).get("budgets") or {})
    return labels


def test_this_repo_has_no_orphaned_budget(tmp_path: Path) -> None:
    """The live blast-radius measurement, kept as a test rather than a claim:
    every budgeted label across all four blocks is a name the runner still knows,
    so arming this gate refused nothing that previously passed."""
    result = _run(GATE, "--repo-root", str(REPO_ROOT))
    assert result.returncode == 0, result.stderr
    payload = _payload(result)
    assert payload["armed"] is True
    assert payload["unknown_labels"] == []
    assert payload["runtime_budget_intent"]["status"] == "configured"
    assert payload["runtime_budget_intent"]["missing_labels"] == []
    assert payload["runtime_budget_intent"]["extra_labels"] == []
    assert {
        "label": "validate-packaging-committed",
        "trigger": "--release or CHARNESS_QUALITY_LABELS includes validate-packaging-committed",
        "execution_proven": False,
    } in payload["conditional_non_claims"]
    # `> 0` would have stayed green through the regression that matters most here:
    # dropping `runtime_budget_profiles` from `budgeted_labels` leaves the ten
    # top-level budgets and hides every profile block, which is the exact
    # single-profile blindness this gate reads the union to fix. Comparing
    # against the DECLARED union catches that without a number to bump.
    declared = _declared_budget_labels()
    # `==`, not `>=`. Both sides derive the same union, so they are equal by
    # construction and `>=` only tolerated the GATE over-counting -- admitting a
    # non-`budgets` profile key as a label would have stayed green.
    assert payload["checked"] == len(declared), (payload["checked"], sorted(declared))
    # The independent-derivation guard above cannot see a regression in the shared
    # YAML reader: a parser that dropped SOME profile budgets moves both sides down
    # together and stays green. This repo has already shipped that exact class --
    # `test_probe_reader_handles_several_probes_and_a_flush_free_list_style` pins
    # the parser that "decided the block had ENDED on that style and dropped every
    # probe". So assert per-BLOCK, which a partial loss cannot satisfy: every
    # declared block still contributes budgets, and the union still exceeds any
    # single block.
    adapter = _ADAPTER_LIB.load_yaml_file(REPO_ROOT / ".agents" / "quality-adapter.yaml")
    blocks = {"runtime_budgets": set(adapter.get("runtime_budgets") or {})}
    for name, profile in (adapter.get("runtime_budget_profiles") or {}).items():
        blocks[f"runtime_budget_profiles.{name}"] = set((profile or {}).get("budgets") or {})
    assert len(blocks) >= 4, sorted(blocks)
    for name, labels in blocks.items():
        assert labels, f"{name} contributed no budgeted label"
        assert len(declared) > len(labels) or labels == declared, (name, len(labels))
    # `charness-version` is budgeted in all four blocks and reachable ONLY through
    # the standing-probe source; if that source empties, it orphans and the gate
    # turns red for a correct adapter.
    assert payload["universe_sources"]["standing_startup_probes"] == 1


@pytest.mark.parametrize("flags", [(), ("--labels-only",)])
def test_an_unparseable_adapter_is_a_named_refusal_not_a_traceback(
    tmp_path: Path, flags: tuple[str, ...]
) -> None:
    """The reader is consumed by `run-quality.sh` at STARTUP, so an unnamed
    exception here aborts the entire run with a traceback blaming the queue lines --
    for an edit to a block scalar elsewhere in the adapter. Before this reader
    existed, the same adapter defect surfaced as one red gate with an accurate
    message; a repair must not make the diagnostic worse than what it replaced."""
    repo = _write_repo(tmp_path, adapter="startup_probes:\n  - label: x\n    note: >+\n      bad header\n")
    result = _run(UNIVERSE, "--repo-root", str(repo), *flags)
    assert result.returncode == 1
    assert "could not be parsed" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("flags", [(), ("--labels-only",)])
def test_a_producer_error_stays_nonzero_in_labels_only_mode(
    tmp_path: Path, flags: tuple[str, ...]
) -> None:
    repo = _write_repo(tmp_path)
    (repo / "scripts" / "run-quality.sh").write_bytes(b"\xff\n")
    result = _run(UNIVERSE, "--repo-root", str(repo), *flags, real_process=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "UnicodeDecodeError" in result.stderr


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
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert _payload(result)["sources"]["standing_startup_probes"] == []


def test_an_underivable_universe_answers_in_the_payload_never_in_prose(tmp_path: Path) -> None:
    """The not-derivable case, which used to answer on stderr with an EMPTY stdout.

    A prose sentence on stdout once became a one-element universe, which defeated
    the runner's own "empty means do not assert" degrade and refused the first gate
    with a remedy about queue-line quoting. stdout is still the machine surface;
    what changed is that it now carries a document on every path, so "no universe"
    has to be readable as `resolved: false` plus a reason rather than as an absence
    a consumer would have to infer from zero lines. An empty `labels` list with
    `resolved` missing or true is the regression this pins.
    """
    repo = _write_repo(tmp_path, runner=None)
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = _payload(result)
    assert payload["resolved"] is False
    assert payload["labels"] == []
    assert "does not vendor the run-quality surface" in payload["reason"]


def test_labels_only_keeps_an_unresolved_universe_out_of_stdout(tmp_path: Path) -> None:
    """The line transport must not silently turn unresolved into a valid empty set.

    The runner still degrades non-fatally for a consumer that does not vendor its
    own run-quality script, but the diagnostic remains visible on stderr.
    """
    repo = _write_repo(tmp_path, runner=None)
    result = _run(UNIVERSE, "--repo-root", str(repo), "--labels-only")
    assert result.returncode == 0
    assert result.stdout == ""
    assert "quality label universe: not derivable" in result.stderr


def test_the_gate_surfaces_a_reader_refusal_instead_of_a_verdict(tmp_path: Path) -> None:
    """The gate's own `read_or_refuse` path. A reader refusal is not a budget
    verdict, and reporting it as one would be a verdict rendered over an input the
    reader said it could not read."""
    runner = RUNNER_STUB + '\nqueue_selected "$computed" python3 x.py\n'
    repo = _write_repo(tmp_path, runner=runner, adapter="runtime_budgets:\n  alpha-gate: 1000\n")
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "runtime budget universe:" in result.stderr
    assert "non-literal label" in result.stderr
    # The "instead of" half, which only became assertable once every verdict emits a
    # document: a refusal emits none, so there is nothing downstream can read as one.
    assert result.stdout == ""


def test_a_derived_universe_carries_every_label_in_one_document(tmp_path: Path) -> None:
    """The resolved half of the pair above. There is one output shape now -- a single
    YAML document -- so `labels` is the list a consumer reads instead of counting
    bare stdout lines, and it must still carry a queued label and an aggregate one.
    """
    repo = _write_repo(tmp_path)
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = _payload(result)
    assert payload["resolved"] is True
    labels = payload["labels"]
    assert "alpha-gate" in labels
    assert "run-quality-full" in labels
    # Labels are keys downstream: a stray surrounding space or an empty entry makes
    # a universe member nothing can ever match.
    assert all(isinstance(label, str) and label.strip() == label and label for label in labels)


def test_labels_only_matches_the_default_document_label_order(tmp_path: Path) -> None:
    repo = _write_repo(tmp_path)
    default = _run(UNIVERSE, "--repo-root", str(repo))
    labels_only = _run(UNIVERSE, "--repo-root", str(repo), "--labels-only")
    assert default.returncode == 0, default.stderr
    assert labels_only.returncode == 0, labels_only.stderr

    documents = list(yaml.safe_load_all(default.stdout))
    assert len(documents) == 1
    payload = documents[0]
    assert payload["resolved"] is True
    expected = "".join(f"{label}\n" for label in payload["labels"])
    assert labels_only.stdout == expected
    assert labels_only.stderr == ""


def test_a_file_ending_mid_continuation_still_yields_its_last_line(
    tmp_path: Path,
) -> None:
    """A runner whose final line ends in a backslash is malformed bash, but the
    reader must not silently drop the statement it was accumulating -- a dropped
    queue line is a label that leaves the universe without anyone saying so."""
    runner = 'queue_selected "tail-gate" python3 x.py\nqueue_selected \\\\\n'
    repo = _write_repo(tmp_path, runner=runner)
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "non-literal label" in result.stderr


def test_startup_probes_declared_as_a_mapping_is_refused(tmp_path: Path) -> None:
    """`startup_probes:` written as a mapping instead of a list. Returning `[]`
    would orphan `charness-version`; the refusal names the shape instead."""
    repo = _write_repo(tmp_path, adapter="startup_probes:\n  label: charness-version\n")
    result = _run(UNIVERSE, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "is not a list" in result.stderr


# --------------------------------------------------------------------------- #
# Slice 4 ("gate by property, not by enumeration"): this gate now names three
# genuinely computable counts in its own output -- a malformed profile block
# `budgeted_label_union` used to silently drop, whether the universe -> prescription
# direction actually ran this pass, and which budgeted labels the SELECTED profile
# (this run's own reachability, not a claim about any other machine) never reaches.
# --------------------------------------------------------------------------- #
def test_malformed_budgets_block_is_named_not_silently_dropped(tmp_path: Path) -> None:
    """A `budgets:` key that is present but not a mapping used to vanish from the
    union with no signal at all -- the reader only `continue`d past it. This pins
    that the gate now NAMES the block it dropped, as a list a caller can count,
    while still not treating the block as a fatal error (the selected-profile
    reader is `check_runtime_budget.py`'s job, not this gate's)."""
    adapter = (
        "runtime_budgets:\n"
        "  alpha-gate: 1000\n"
        "runtime_budget_profiles:\n"
        "  typo-block:\n"
        "    budgets:\n"
        "      - not-a-mapping\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = _payload(result)
    assert payload["malformed_budget_profile_blocks"] == ["typo-block"]
    assert "1 runtime_budget_profiles block" in payload["malformed_budget_profile_blocks_summary"]


def test_tolerated_profile_stub_is_not_reported_malformed(tmp_path: Path) -> None:
    """The shape `test_gate_tolerates_a_profile_without_a_budgets_mapping` already
    pins as legitimate (no `budgets` key at all) must NOT show up in the new
    malformed list -- the two shapes look similar but only one is a typo."""
    adapter = (
        "runtime_budgets:\n"
        "  alpha-gate: 1000\n"
        "runtime_budget_profiles:\n"
        "  stub-profile:\n"
        "    note: no budgets key here\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert _payload(result)["malformed_budget_profile_blocks"] == []


def test_second_direction_status_names_why_it_did_not_run(tmp_path: Path) -> None:
    """`unbudgeted_expensive_commands` reads `[]` identically whether the second
    direction ran and found nothing, or never ran because the dominance registry
    is absent. This pins that the payload now says WHICH happened, without
    changing the pinned `== []` behavior itself."""
    adapter = "runtime_budgets:\n  alpha-gate: 1000\n"
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = _payload(result)
    assert payload["unbudgeted_expensive_commands"] == []
    status = payload["second_direction_status"]
    assert status["ran"] is False
    assert status["examined"] == 0
    assert "absent" in status["reason"]


def test_unreachable_by_selected_profile_names_a_block_this_run_cannot_select(tmp_path: Path) -> None:
    """The module docstring's own example: a profile block nobody on THIS machine
    selects reaches no sample from THIS run. `feasible=false` covers 'never runs
    under any condition'; this is the narrower, honestly computable neighbor --
    reachable from THIS run's own profile selection, or not."""
    adapter = (
        "runtime_profile_default: ci-profile\n"
        "runtime_budget_profiles:\n"
        "  ci-profile:\n"
        "    budgets:\n"
        "      alpha-gate: 1000\n"
        "  aarch64-profile:\n"
        "    budgets:\n"
        "      beta-gate: 1000\n"
    )
    repo = _write_repo(tmp_path, adapter=adapter)
    result = _run(GATE, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = _payload(result)
    assert payload["selected_runtime_profile"] == "ci-profile"
    labels = {entry["label"] for entry in payload["unreachable_by_selected_profile"]}
    assert labels == {"beta-gate"}
    assert payload["unreachable_by_selected_profile_reason"] is None
    assert payload["advisory"].startswith("WARN:")
    assert "beta-gate" in payload["advisory"]


def test_malformed_block_classifier_covers_every_shape_it_discriminates() -> None:
    """The three branches the changed-line gate named as uncovered.

    `malformed_budget_profile_blocks` exists to discriminate shapes that one silent
    `continue` used to collapse. Two of its arms -- a `None` stub and a block that is
    not a mapping at all -- had no test, so the discrimination the field was added for
    was itself unproven on those inputs.
    """
    lib = import_repo_module(
        REPO_ROOT / "skills/public/quality/scripts/runtime_profile_lib.py",
        "skills.public.quality.scripts.runtime_profile_lib",
    )
    adapter = {
        "runtime_budget_profiles": {
            "empty-stub": None,                      # tolerated: an empty block
            "not-a-mapping": ["budgets"],            # malformed: block is not a dict
            "no-budgets-key": {"note": "docs only"},  # tolerated: no budgets key
            "budgets-not-a-mapping": {"budgets": ["x"]},  # malformed: budgets not a dict
            "healthy": {"budgets": {"label": 1.0}},  # fine
        }
    }

    assert lib.malformed_budget_profile_blocks(adapter) == [
        "not-a-mapping",
        "budgets-not-a-mapping",
    ]
    # A non-dict `runtime_budget_profiles` is not a malformed BLOCK; it is no blocks.
    assert lib.malformed_budget_profile_blocks({"runtime_budget_profiles": []}) == []
    assert lib.malformed_budget_profile_blocks({}) == []
