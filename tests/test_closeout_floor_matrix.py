"""Pins for the closeout floor x classification x carrier matrix (`#586`).

Two halves, and the second is the load-bearing one. The declaration was GENERATED
from the first measurement, so it agreed with observation on day one by construction
-- its teeth are entirely on the next change. These tests pin that the probe reads
live behavior rather than a table: patch a floor's classification gate, and the
observed cell must move.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import scripts.closeout_floor_matrix_lib as lib
from scripts.check_closeout_floor_matrix import MATRIX_REL, _problems
from scripts.check_closeout_floor_matrix import main as gate_main
from scripts.closeout_floor_matrix_lib import (
    CARRIERS,
    FLOORS,
    ProbeWorld,
    _commit_msg,
    observe,
    probe_body,
    run_ingress,
)
from tests.repo_copy import clone_seeded_charness_repo, seeded_charness_repo  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATIONS = ("bug", "feature", "deferred-work", "question", "decision-needed", "consolidated")
GATE = "scripts/check_closeout_floor_matrix.py"


def _observed(overrides: dict[str, dict] | None = None) -> dict:
    pairs = {
        f"{carrier}|{classification}": {
            "baseline": "passes",
            "floors": {floor: "fires" for floor in FLOORS},
        }
        for carrier in CARRIERS
        for classification in CLASSIFICATIONS
    }
    pairs.update(overrides or {})
    return {
        "classifications": list(CLASSIFICATIONS),
        "carriers": list(CARRIERS),
        "floors": list(FLOORS),
        "pairs": pairs,
    }


def _declared(observed: dict) -> dict:
    """The declaration that agrees with `observed` on every cell."""
    pairs = {}
    for key, pair in observed["pairs"].items():
        if pair["baseline"] == "refused":
            pairs[key] = {
                "baseline": "refused",
                "reason": "the carrier refuses this disposition",
                "refusal_signature": "auto-closes",
            }
            continue
        pairs[key] = {
            "baseline": "passes",
            "floors": {
                floor: {"state": "fires"} if state == "fires"
                else {"state": "not-applicable", "reason": "no input on this pair"}
                for floor, state in pair["floors"].items()
            },
        }
    return {
        "classifications": list(observed["classifications"]),
        "carriers": list(observed["carriers"]),
        "floors": list(observed["floors"]),
        "pairs": pairs,
    }


def test_a_matching_declaration_reports_no_problems() -> None:
    observed = _observed()
    assert _problems(_declared(observed), observed) == []


def test_an_undeclared_pair_refuses() -> None:
    observed = _observed()
    declared = _declared(observed)
    declared["pairs"].pop("pr-body|question")
    problems = _problems(declared, observed)
    assert any("pr-body|question" in problem and "refusal, not a default" in problem for problem in problems)


def test_a_declared_pair_that_does_not_exist_refuses() -> None:
    observed = _observed()
    declared = _declared(observed)
    declared["pairs"]["pr-body|retired-disposition"] = {"baseline": "passes", "floors": {}}
    assert any("no such (carrier, classification) pair" in p for p in _problems(declared, observed))


def test_an_undeclared_floor_cell_refuses() -> None:
    observed = _observed()
    declared = _declared(observed)
    declared["pairs"]["pr-body|bug"]["floors"].pop("ai_provenance")
    assert any(
        "pr-body|bug/ai_provenance" in p and "refusal, not a default" in p
        for p in _problems(declared, observed)
    )


def test_declaring_fires_where_the_carrier_is_inert_refuses() -> None:
    observed = _observed({"pr-body|question": {"baseline": "passes", "floors": {
        **{floor: "fires" for floor in FLOORS}, "behavioral_verdict": "inert"}}})
    declared = _declared(_observed())
    problems = _problems(declared, observed)
    assert any(
        "pr-body|question/behavioral_verdict" in p and "observably 'inert'" in p for p in problems
    )


def test_declaring_inert_where_the_carrier_fires_refuses() -> None:
    observed = _observed()
    declared = _declared(observed)
    declared["pairs"]["pr-body|bug"]["floors"]["hotl_dispositions"] = {
        "state": "skipped-by-design", "reason": "claimed deliberate"
    }
    assert any("observably 'fires'" in p for p in _problems(declared, observed))


@pytest.mark.parametrize("state", ["not-applicable", "skipped-by-design", "undispositioned"])
def test_no_state_but_input_refused_accepts_an_input_refused_observation(state: str) -> None:
    """The anti-self-confirmation pin.

    Round 1 found `not-applicable` admitting BOTH `inert` and `input-refused`, which
    let the six cells carrying this slice's central finding slide from one to the
    other with the gate still green -- turning a brand-new silent skip on the
    direct-write carrier into a pass. Every state now pins exactly one observation.
    """
    observed = _observed({"manual-fallback|consolidated": {"baseline": "passes", "floors": {
        **{floor: "fires" for floor in FLOORS}, "behavioral_verdict": "input-refused"}}})
    declared = _declared(_observed())
    cell = {"state": state, "reason": "the disposition refuses this line"}
    if state == "undispositioned":
        cell = {"state": state, "finding": "https://github.com/corca-ai/charness/issues/591"}
    declared["pairs"]["manual-fallback|consolidated"]["floors"]["behavioral_verdict"] = cell
    assert any("observably 'input-refused'" in p for p in _problems(declared, observed))


def test_input_refused_declared_as_such_is_accepted() -> None:
    observed = _observed({"manual-fallback|consolidated": {"baseline": "passes", "floors": {
        **{floor: "fires" for floor in FLOORS}, "behavioral_verdict": "input-refused"}}})
    declared = _declared(_observed())
    declared["pairs"]["manual-fallback|consolidated"]["floors"]["behavioral_verdict"] = {
        "state": "input-refused", "reason": "the disposition refuses this line"
    }
    assert _problems(declared, observed) == []


def test_a_null_cell_is_a_refusal_and_not_a_pass() -> None:
    """`"ai_provenance": null` was four characters that turned the doctrine off: the
    key is PRESENT, so the absence check passes, and the old code then skipped every
    state and observation check for it."""
    observed = _observed({"pr-body|question": {"baseline": "passes", "floors": {
        **{floor: "fires" for floor in FLOORS}, "ai_provenance": "inert"}}})
    declared = _declared(_observed())
    declared["pairs"]["pr-body|question"]["floors"]["ai_provenance"] = None
    assert any("must be an object" in p for p in _problems(declared, observed))


def test_a_null_justification_is_a_refusal_and_not_a_pass() -> None:
    """`str(None)` is `"None"`, so `"reason": null` used to clear the emptiness test --
    the same four characters the cell-level guard closes, one level down on the
    justification the state exists to demand."""
    observed = _observed({"pr-body|question": {"baseline": "passes", "floors": {
        **{floor: "fires" for floor in FLOORS}, "behavioral_verdict": "inert"}}})
    declared = _declared(_observed())
    declared["pairs"]["pr-body|question"]["floors"]["behavioral_verdict"] = {
        "state": "skipped-by-design", "reason": None
    }
    assert any("requires a non-empty `reason` string" in p for p in _problems(declared, observed))


def test_a_finding_must_name_a_filed_issue_not_a_promise() -> None:
    observed = _observed({"pr-body|question": {"baseline": "passes", "floors": {
        **{floor: "fires" for floor in FLOORS}, "ai_provenance": "inert"}}})
    declared = _declared(_observed())
    declared["pairs"]["pr-body|question"]["floors"]["ai_provenance"] = {
        "state": "undispositioned", "finding": "later"
    }
    assert any("must name a filed issue URL" in p for p in _problems(declared, observed))


def test_an_unattributed_refusal_is_no_state_at_all() -> None:
    """`refused-elsewhere` is what the probe records when a carrier refused but did
    not attribute the refusal to the broken floor -- a probe breakage, or a verdict
    flipped by some other check. No declared state accepts it, so it cannot pass."""
    observed = _observed({"pr-body|bug": {"baseline": "passes", "floors": {
        **{floor: "fires" for floor in FLOORS}, "ai_provenance": "refused-elsewhere"}}})
    assert any(
        "observably 'refused-elsewhere'" in p for p in _problems(_declared(_observed()), observed)
    )


@pytest.mark.parametrize(
    "state,field", [("skipped-by-design", "reason"), ("not-applicable", "reason"), ("undispositioned", "finding")]
)
def test_a_non_firing_cell_without_its_required_justification_refuses(state: str, field: str) -> None:
    observed = _observed({"pr-body|question": {"baseline": "passes", "floors": {
        **{floor: "fires" for floor in FLOORS}, "ai_provenance": "inert"}}})
    declared = _declared(_observed())
    declared["pairs"]["pr-body|question"]["floors"]["ai_provenance"] = {"state": state, field: "   "}
    assert any(f"requires a non-empty `{field}`" in p for p in _problems(declared, observed))


def test_an_undispositioned_cell_with_a_finding_is_accepted() -> None:
    observed = _observed({"pr-body|question": {"baseline": "passes", "floors": {
        **{floor: "fires" for floor in FLOORS}, "ai_provenance": "inert"}}})
    declared = _declared(_observed())
    declared["pairs"]["pr-body|question"]["floors"]["ai_provenance"] = {
        "state": "undispositioned", "finding": "https://github.com/corca-ai/charness/issues/591"
    }
    assert _problems(declared, observed) == []


def test_an_unknown_state_refuses() -> None:
    observed = _observed()
    declared = _declared(observed)
    declared["pairs"]["pr-body|bug"]["floors"]["ai_provenance"] = {"state": "probably-fine"}
    assert any("unknown state" in p for p in _problems(declared, observed))


def test_a_refused_pair_must_say_why_and_must_carry_no_cells() -> None:
    observed = _observed({"pr-body|consolidated": {"baseline": "refused", "refusal_detail": "x", "floors": {}}})
    declared = _declared(_observed())
    declared["pairs"]["pr-body|consolidated"] = {
        "baseline": "refused", "reason": "", "floors": {"ai_provenance": {"state": "fires"}}
    }
    problems = _problems(declared, observed)
    assert any("must declare why the carrier refuses it" in p for p in problems)
    assert any("no observable floors" in p for p in problems)
    assert any("must declare a `refusal_signature`" in p for p in problems)


def test_a_refused_pair_whose_signature_is_absent_from_the_real_refusal_refuses() -> None:
    """Without this, a refused pair is verified only by the word "refused" -- and any
    engine breakage on that pair renders as a refusal, so it would read green."""
    observed = _observed({"pr-body|consolidated": {
        "baseline": "refused",
        "refusal_detail": '{"refusing_floors": ["behavioral_verdict"]}',
        "floors": {},
    }})
    declared = _declared(_observed())
    declared["pairs"]["pr-body|consolidated"] = {
        "baseline": "refused", "reason": "the carrier auto-closes", "refusal_signature": "auto-closes"
    }
    assert any("is absent from the refusal the carrier actually produced" in p
               for p in _problems(declared, observed))


def test_a_pair_the_carrier_refuses_cannot_be_declared_as_passing() -> None:
    observed = _observed({"pr-body|consolidated": {"baseline": "refused", "refusal_detail": "x", "floors": {}}})
    assert any(
        "declared baseline 'passes' but the carrier 'refused'" in p
        for p in _problems(_declared(_observed()), observed)
    )


def test_an_axis_mismatch_stops_before_reporting_every_pair() -> None:
    observed = _observed()
    declared = _declared(observed)
    declared["classifications"] = [c for c in CLASSIFICATIONS if c != "consolidated"]
    problems = _problems(declared, observed)
    assert problems == ["declared classifications disagree with the live axis: ['consolidated']"]


def test_the_checked_in_declaration_covers_every_live_pair() -> None:
    declared = json.loads((ROOT / MATRIX_REL).read_text(encoding="utf-8"))
    assert set(declared["pairs"]) == {
        f"{carrier}|{classification}"
        for carrier in declared["carriers"]
        for classification in declared["classifications"]
    }


# --- behavioral half: the probe must read the code, not a table ----------------


@pytest.fixture()
def world(tmp_path: Path) -> ProbeWorld:
    return ProbeWorld(ROOT, tmp_path / "world")


def test_a_bug_close_is_refused_by_every_body_floor(world: ProbeWorld) -> None:
    result = observe(world, "pr-body", "bug")
    assert result["baseline"] == "passes"
    assert result["floors"] == {
        "source_preservation": "fires",
        "behavioral_verdict": "fires",
        "hotl_dispositions": "fires",
        "ai_provenance": "fires",
        "resolution_critique": "fires",
        "consolidation_readback": "inert",
    }


def test_a_consolidated_close_is_refused_outright_by_an_auto_closing_carrier(world: ProbeWorld) -> None:
    result = observe(world, "pr-body", "consolidated")
    assert result["baseline"] == "refused"
    assert "auto-closes" in result["refusal_detail"]


def test_a_consolidated_close_reaches_its_destination_readback_on_the_carrier_it_must_use(
    world: ProbeWorld,
) -> None:
    result = observe(world, "close-with-comment", "consolidated")
    assert result["baseline"] == "passes"
    assert result["floors"]["consolidation_readback"] == "fires"
    # The repair-claiming lines cannot exist on this body at all -- observed by adding
    # them back, not by reading the disposition's source.
    assert result["floors"]["behavioral_verdict"] == "input-refused"
    assert result["floors"]["resolution_critique"] == "input-refused"


def test_the_release_lane_does_not_exempt_a_light_close_from_the_behavioral_verdict(
    world: ProbeWorld,
) -> None:
    """The finding round 1 caught, pinned.

    Every other carrier exempts `question` from the behavioral-verdict floor. The
    release lane runs its own floor first, with a FIXED `feature` classification over
    a separate input channel, so it refuses. Probing one layer lower -- at the release
    message helper rather than at `preflight_release_issues` -- measured the opposite
    and declared `skipped-by-design` where a real release close is refused.
    """
    assert observe(world, "pr-body", "question")["floors"]["behavioral_verdict"] == "inert"
    assert observe(world, "release-draft", "question")["floors"]["behavioral_verdict"] == "fires"


def test_a_consolidated_close_is_refused_by_the_auto_close_rule_on_the_release_lane(
    world: ProbeWorld,
) -> None:
    """Round 2 caught this reading `behavioral_verdict`, which was a probe artifact:
    the probe derived `--close-issue-behavior` from the carrier body, and a
    consolidated body cannot carry a `Behavior:` line. A real operator passes the flag
    regardless, so the refusal that actually fires is the auto-close rule -- the same
    one the other three refused pairs hit."""
    result = observe(world, "release-draft", "consolidated")
    assert result["baseline"] == "refused"
    assert "auto-closes" in result["refusal_detail"]


def test_the_consolidation_readback_cells_can_actually_move(world: ProbeWorld) -> None:
    """The 30 non-consolidated readback cells must be measurements, not decoration.

    Round 2 found them unmovable: the probe broke only the destination's tracker state
    on bodies that carried no `Consolidated into:` anchor, so `destinations()` was
    empty and the readback returned early whatever its applicability gate said. A row
    that can never fire is the shape this artifact excludes `closeout_authorization`
    for. With the anchor present, widening the gate must move the cell.
    """
    before = observe(world, "pr-body", "bug")
    assert before["floors"]["consolidation_readback"] == "inert"

    world.verifier._consolidated.CLASSIFICATION = "bug"
    after = observe(world, "pr-body", "bug")
    assert after["floors"]["consolidation_readback"] == "fires"


def test_the_probe_reads_the_live_floor_and_not_a_declared_table(world: ProbeWorld) -> None:
    """The anti-circularity pin.

    A matrix generated from observation agrees with observation trivially. What must
    be true is that the observation MOVES when the code does: widen the
    behavioral-verdict floor to cover `question`, and that cell must stop being inert.
    """
    before = observe(world, "pr-body", "question")
    assert before["floors"]["behavioral_verdict"] == "inert"

    floors = world.verifier._FLOORS
    floors.BEHAVIORAL_VERDICT_CLASSIFICATIONS = floors.BEHAVIORAL_VERDICT_CLASSIFICATIONS + ("question",)
    after = observe(world, "pr-body", "question")
    assert after["floors"]["behavioral_verdict"] == "fires"


def test_a_probe_body_is_broken_in_exactly_one_place() -> None:
    baseline = probe_body("bug", "pr-body", None)
    for floor in ("behavioral_verdict", "ai_provenance", "resolution_critique"):
        assert probe_body("bug", "pr-body", floor) != baseline
    # Source preservation is presence-gated the other way: the baseline is inert
    # because it declares no external origin, so breaking it ADDS a line.
    assert len(probe_body("bug", "pr-body", "source_preservation")) > len(baseline)


def test_every_carrier_accepts_the_baseline_and_refuses_a_broken_behavioral_verdict(
    world: ProbeWorld,
) -> None:
    """The carriers the pair-level tests above do not enter.

    `direct-commit` reads a real commit, `manual-fallback` needs its typed reason, and
    `commit-msg` runs the hook as the subprocess a git hook runs -- three distinct
    ingress mechanics, none exercised by the `pr-body` probes.
    """
    for carrier in ("direct-commit", "manual-fallback", "commit-msg"):
        result = observe(world, carrier, "bug")
        assert result["baseline"] == "passes", (carrier, result)
        assert result["floors"]["behavioral_verdict"] == "fires", carrier


def test_a_carrier_that_raises_is_recorded_as_a_refusal_without_attribution(
    world: ProbeWorld,
) -> None:
    """A raise carries no per-floor record, so the probe must not credit the broken
    floor with it -- that is what `refused-elsewhere` is for."""
    ok, detail, refusing = run_ingress(
        world, "close-with-comment", "consolidated",
        probe_body("consolidated", "close-with-comment", None) + "\nBehavior: a repair claim\n",
    )
    assert ok is False
    assert refusing == set()
    assert detail


def test_the_commit_msg_carrier_reports_a_non_json_verdict_as_an_engine_failure(
    world: ProbeWorld,
) -> None:
    """The hook exits 1 with empty stdout on any internal exception. That must surface
    as a RuntimeError naming the exit code, not as a silent refusal."""
    world.source_root = world.root / "no-such-tree"
    with pytest.raises(RuntimeError, match="no readable verdict"):
        _commit_msg(world, "bug", "Closes #77\n", None)


@pytest.mark.slow_corpus
def test_the_cli_reports_agreement_and_can_emit_the_observed_grid(tmp_path: Path, capsys) -> None:
    """The `main()` path: exit 0, the operator summary, and `--emit-observed`."""
    out = tmp_path / "observed.json"
    exit_code = gate_main(["--repo-root", str(ROOT), "--emit-observed", str(out)])
    assert exit_code == 0
    grid = json.loads(out.read_text(encoding="utf-8"))
    assert len(grid["pairs"]) == len(grid["carriers"]) * len(grid["classifications"])
    # The agreement line said how many pairs it covered; `observed_pairs` is what
    # keeps that population visible, because an agreement over zero pairs is not the
    # same verdict as one over all of them.
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["observed_pairs"] == len(grid["pairs"])


def test_the_cli_refuses_when_the_declaration_is_missing(tmp_path: Path, capsys) -> None:
    (tmp_path / ".agents").mkdir()
    assert gate_main(["--repo-root", str(tmp_path)]) == 1
    assert "declaration not found" in capsys.readouterr().err


@pytest.mark.release_only
def test_the_gate_refuses_when_a_floor_changes_under_an_unchanged_declaration(
    tmp_path: Path, seeded_charness_repo: Path  # noqa: F811
) -> None:
    """End to end, through the CLI, including the commit-msg subprocess carrier.

    Green first, so a red result cannot be an artifact of the copy; then one edit to
    a floor's classification gate, and the same unchanged declaration must refuse.
    """
    repo = clone_seeded_charness_repo(tmp_path, seeded_charness_repo)
    green = subprocess.run(
        [sys.executable, GATE, "--repo-root", str(repo)],
        cwd=repo, capture_output=True, text=True,
    )
    assert yaml.safe_load(green.stdout)["ok"], green.stdout

    floor_source = repo / "skills/public/issue/scripts/issue_closeout_rung1_floors.py"
    floor_source.write_text(
        floor_source.read_text(encoding="utf-8").replace(
            'BEHAVIORAL_VERDICT_CLASSIFICATIONS = ("bug", "feature", "deferred-work")',
            'BEHAVIORAL_VERDICT_CLASSIFICATIONS = ("bug", "feature", "deferred-work", "question")',
        ),
        encoding="utf-8",
    )
    red = subprocess.run(
        [sys.executable, GATE, "--repo-root", str(repo)],
        cwd=repo, capture_output=True, text=True,
    )
    payload = yaml.safe_load(red.stdout)
    assert payload["ok"] is False
    assert any(
        "|question/behavioral_verdict" in problem and "observably 'fires'" in problem
        for problem in payload["problems"]
    ), payload["problems"]


def test_a_floors_value_that_is_not_an_object_refuses() -> None:
    observed = _observed()
    declared = _declared(observed)
    declared["pairs"]["pr-body|bug"]["floors"] = ["ai_provenance"]
    assert any("`floors` must be an object" in p for p in _problems(declared, observed))


def test_a_cell_for_a_floor_that_does_not_exist_refuses() -> None:
    observed = _observed()
    declared = _declared(observed)
    declared["pairs"]["pr-body|bug"]["floors"]["retired_floor"] = {"state": "fires"}
    assert any("retired_floor: declared but no such floor" in p for p in _problems(declared, observed))


def _repo_with_declaration(tmp_path: Path, mutate) -> Path:
    """A repo root carrying a declaration derived from the real one, then mutated."""
    declared = json.loads((ROOT / MATRIX_REL).read_text(encoding="utf-8"))
    mutate(declared)
    target = tmp_path / MATRIX_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(declared), encoding="utf-8")
    for rel in ("scripts", "skills", "AGENTS.md", "runtime_bootstrap.py", "skill_runtime_bootstrap.py"):
        source = ROOT / rel
        if source.exists():
            (tmp_path / rel).symlink_to(source)
    return tmp_path


@pytest.mark.slow_corpus
def test_the_cli_reports_disagreements_with_their_finding_summary_and_remedy(
    tmp_path: Path, capsys
) -> None:
    """One reporting path, on a declaration that disagrees with the real carriers.

    The human branch carried three things the bare problem list does not: that the
    declaration disagrees with the carriers, how many findings there are, and how to
    re-measure the grid. They are payload fields now, so a reader who only parses
    still gets them.
    """
    def break_a_cell(declared: dict) -> None:
        declared["pairs"]["pr-body|question"]["floors"]["behavioral_verdict"] = {"state": "fires"}

    repo = _repo_with_declaration(tmp_path, break_a_cell)
    assert gate_main(["--repo-root", str(repo)]) == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["ok"] is False
    assert any("pr-body|question/behavioral_verdict" in p for p in payload["problems"])
    assert "the declaration disagrees with what the carriers actually do" in payload["finding_summary"]
    assert f"{len(payload['problems'])} finding(s)" in payload["finding_summary"]
    assert "Re-measure with:" in payload["remedy"]


def test_the_script_entrypoint_exits_nonzero_without_a_declaration(tmp_path: Path) -> None:
    """Through `python3 scripts/...`, so the module's own `SystemExit(main())` runs."""
    result = subprocess.run(
        [sys.executable, GATE, "--repo-root", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "declaration not found" in result.stderr


def test_an_ingress_that_raises_is_a_refusal_the_probe_cannot_attribute(
    world: ProbeWorld,
) -> None:
    """`verify_closeout` raises on an unknown classification. A raise carries no
    per-floor record, so the probe must report it as an unattributed refusal rather
    than crediting whichever floor happened to be broken."""
    ok, detail, refusing = run_ingress(world, "pr-body", "not-a-classification", "Closes #77\n")
    assert ok is False
    assert refusing == set()
    assert "unknown classification" in detail


def test_a_readback_control_run_that_is_refused_never_claims_the_floor_fired(
    world: ProbeWorld, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the `Consolidated into:` anchor itself is refused, the CLOSED run would prove
    nothing -- the cell must not read `fires` off a refusal the anchor caused."""
    monkeypatch.setattr(
        lib, "run_ingress", lambda *a, **k: (False, "the anchor was refused", set())
    )
    assert lib._readback_outcome(world, "pr-body", "bug") == "input-refused"
