from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts import lesson_ledger_lib as ledger
from scripts import lesson_score_outcome_lib as outcome_lib
from scripts import seed_lesson_transitions as seeder
from tests.quality_gates.support import run_script
from tests.test_lesson_ledger import ROOT, _ledger, _retro, _validate


def _empty_ledger(repo: Path) -> Path:
    """A ledger with no transitions, the state `init_lesson_ledger.py` leaves."""
    path = repo / "charness-artifacts/retro/lesson-ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "kind": ledger.KIND,
                "schema_version": ledger.SCHEMA_VERSION,
                "transitions": [],
                "active_lesson_budget": ledger.ACTIVE_LESSON_BUDGET,
                "lifecycle_events": [],
                "score_events": [],
                "lessons": {},
            }
        ),
        encoding="utf-8",
    )
    return path


def _seed(repo: Path, **kwargs: object) -> dict:
    return seeder.seed_transitions(
        repo_root=repo,
        output_dir=repo / "charness-artifacts/retro",
        summary_path=repo / "charness-artifacts/retro/recent-lessons.md",
        lesson_ids=kwargs.get("lesson_ids"),  # type: ignore[arg-type]
        dry_run=bool(kwargs.get("dry_run")),
    )


# --------------------------------------------------------------------------
# Ten independent seed/validate scenarios, one node. Each installs its own
# small retro/ledger fixture (plain file writes, no git), so bundling them
# here does not share the product's own `_committed_state` git calls -- it
# only drops ten nodes' fixture/collection overhead to one. A failure names
# the exact `_case_*` function in its traceback, which is where each former
# test's docstring/rationale now lives.
# --------------------------------------------------------------------------


def _case_seeding_an_empty_ledger_makes_a_tagged_class_validate(case_dir: Path) -> None:
    """The whole point of #625: ledger exists -> a lesson is actually in it.

    The pre-fix state was an empty ledger that validated forever while
    `render_lesson_selection_preview` reported `0 eligible`, and no command could
    change that.
    """
    _retro(case_dir, "source.md", "a")
    path = _empty_ledger(case_dir)
    assert _validate(case_dir)["lesson_count"] == 0

    receipt = _seed(case_dir)

    assert receipt["seeded_count"] == 1
    assert receipt["seeded"][0] == {
        "sequence": 1,
        "transition_id": "seed-a",
        "lesson_id": "a",
        "source_retro": "charness-artifacts/retro/source.md",
    }
    assert _validate(case_dir)["lesson_count"] == 1
    lesson = json.loads(path.read_text(encoding="utf-8"))["lessons"]["a"]
    assert lesson == {
        "source_retro": "charness-artifacts/retro/source.md",
        "transition_id": "seed-a",
        "score_total": 0,
        "score_count": 0,
        "outcome_counts": outcome_lib.outcome_counts([]),
        "state": "active",
        "last_lifecycle_event_id": None,
    }


def _case_dry_run_reports_the_plan_and_writes_nothing(case_dir: Path) -> None:
    _retro(case_dir, "source.md", "a")
    path = _empty_ledger(case_dir)
    before = path.read_bytes()

    receipt = _seed(case_dir, dry_run=True)

    assert receipt["dry_run"] is True
    assert [item["lesson_id"] for item in receipt["seeded"]] == ["a"]
    assert path.read_bytes() == before


def _case_empty_plan_is_not_reported_as_a_dry_run(case_dir: Path) -> None:
    """`dry_run` must mean "asked to rehearse", never "happened to write nothing"."""
    _retro(case_dir, "source.md", "a")
    _ledger(case_dir)

    receipt = _seed(case_dir)

    assert receipt["seeded"] == []
    assert receipt["dry_run"] is False


def _case_appending_a_later_class_is_the_same_operation_as_seeding(case_dir: Path) -> None:
    """A lesson authored after the ledger existed must have a path in.

    A bootstrap-only seeder would close the cold start and leave this open, which
    is the state the authoring repo was actually in: 16 seeded classes, 15 tagged
    classes with no command that could add them.
    """
    _retro(case_dir, "source.md", "a")
    _ledger(case_dir)
    _retro(case_dir, "later.md", "b")

    receipt = _seed(case_dir)

    assert [item["lesson_id"] for item in receipt["seeded"]] == ["b"]
    assert receipt["seeded"][0]["sequence"] == 2
    assert set(json.loads((case_dir / "charness-artifacts/retro/lesson-ledger.json").read_text()) ["lessons"]) == {"a", "b"}


def _case_multi_source_class_cites_its_latest_source(case_dir: Path) -> None:
    """The digest renders a class from its newest observation, so the ledger cites
    the same artifact; citing an older member would attribute the shown wording to
    a retro that does not contain it."""
    _retro(case_dir, "2026-08-01-old.md", "a")
    _retro(case_dir, "2026-08-30-new.md", "a")
    _empty_ledger(case_dir)

    receipt = _seed(case_dir)

    assert receipt["seeded"][0]["source_retro"] == "charness-artifacts/retro/2026-08-30-new.md"
    assert _validate(case_dir)["lesson_count"] == 1


def _case_untagged_lesson_is_never_invented_as_a_class(case_dir: Path) -> None:
    path = case_dir / "charness-artifacts/retro/untagged.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Session Retro\nDate: 2026-08-12\n\n## Waste\n\n- a lesson with no class tag\n",
        encoding="utf-8",
    )
    ledger_path = _empty_ledger(case_dir)
    before = ledger_path.read_bytes()

    assert _seed(case_dir)["seeded"] == []
    assert ledger_path.read_bytes() == before
    with pytest.raises(ValueError, match="not a tagged retro class"):
        _seed(case_dir, lesson_ids=["invented"])
    assert ledger_path.read_bytes() == before


def _case_reseeding_a_seeded_lesson_is_refused_without_rewriting(case_dir: Path) -> None:
    _retro(case_dir, "source.md", "a")
    path = _ledger(case_dir)
    before = path.read_bytes()

    with pytest.raises(ValueError, match="already seeded"):
        _seed(case_dir, lesson_ids=["a"])

    assert path.read_bytes() == before


def _case_a_transition_id_burned_by_another_lesson_is_refused_by_name(case_dir: Path) -> None:
    """The collision the `already seeded` check cannot see.

    `seeded` is keyed by lesson_id and `existing_ids` by transition_id, and the two
    disagree exactly when a transition_id was spent on a DIFFERENT lesson -- the
    hand-edited rows this command replaces are how that happens, and archiving does
    not release the id afterwards. Left to the validator it surfaces as a generic
    duplicate after a partial plan was already built, which names neither the id nor
    the lesson that holds it.

    Driven through `plan_seeds` with an explicit payload because the state is
    unreachable from a ledger this command itself wrote: nothing here mints
    `seed-a` for anything but `a`.
    """
    _retro(case_dir, "source.md", "a")
    _retro(case_dir, "other.md", "b")
    payload = {
    # `b` holds `seed-a`, and `a` is tagged, unseeded, and therefore a target.
        "transitions": [
            {
                "sequence": 1,
                "transition_id": "seed-a",
                "lesson_id": "b",
                "source_retro": "charness-artifacts/retro/other.md",
            }
        ],
        "lessons": {"b": {"transition_id": "seed-a"}},
    }

    with pytest.raises(ValueError) as raised:
        seeder.plan_seeds(
            repo_root=case_dir,
            output_dir=case_dir / "charness-artifacts/retro",
            summary_path=case_dir / "charness-artifacts/retro/recent-lessons.md",
            payload=payload,
            lesson_ids=None,
        )

    message = str(raised.value)
    # The id itself, not "a duplicate exists": the operator's only move is to look
    # up who holds `seed-a`, and the permanence is what rules out renaming it back.
    assert "`seed-a`" in message
    assert "already used by a different lesson" in message
    assert "archiving does not release one" in message
    # And `b` alone -- the only lesson whose id is spent -- still plans cleanly, so
    # the refusal is about the collision rather than about the fixture.
    assert seeder.plan_seeds(
        repo_root=case_dir,
        output_dir=case_dir / "charness-artifacts/retro",
        summary_path=case_dir / "charness-artifacts/retro/recent-lessons.md",
        payload={"transitions": [], "lessons": {}},
        lesson_ids=["b"],
    ) == [
        {
            "sequence": 1,
            "transition_id": "seed-b",
            "lesson_id": "b",
            "source_retro": "charness-artifacts/retro/other.md",
        }
    ]


def _case_selected_subset_leaves_other_classes_unseeded(case_dir: Path) -> None:
    _retro(case_dir, "a.md", "a")
    _retro(case_dir, "b.md", "b")
    _empty_ledger(case_dir)

    receipt = _seed(case_dir, lesson_ids=["b"])

    assert [item["lesson_id"] for item in receipt["seeded"]] == ["b"]
    assert set(_validate(case_dir) and json.loads(
        (case_dir / "charness-artifacts/retro/lesson-ledger.json").read_text()
    )["lessons"]) == {"b"}


def _case_over_budget_seeding_is_refused_with_its_arithmetic(case_dir: Path, monkeypatch) -> None:
    _retro(case_dir, "a.md", "a")
    _retro(case_dir, "b.md", "b")
    # Both module objects: the seeder imports the library through
    # `import_repo_module`, which can hand back a distinct instance, and the ledger
    # file itself must carry the same budget or its own fixed-budget check fires
    # first and the seeder's arithmetic is never reached.
    for module in {id(ledger): ledger, id(seeder._ledger): seeder._ledger}.values():
        monkeypatch.setattr(module, "ACTIVE_LESSON_BUDGET", 1)
    path = _empty_ledger(case_dir)
    before = path.read_bytes()

    with pytest.raises(ValueError, match="past the fixed budget of 1"):
        _seed(case_dir)

    assert path.read_bytes() == before
    # And the one-lesson subset still fits, so the refusal is about the arithmetic
    # rather than the command being broken at a small budget.
    assert _seed(case_dir, lesson_ids=["a"])["seeded_count"] == 1


_SEED_TRANSITION_CASES = {
    "seeding-an-empty-ledger-makes-a-tagged-class-validate": (
        _case_seeding_an_empty_ledger_makes_a_tagged_class_validate, False
    ),
    "dry-run-reports-the-plan-and-writes-nothing": (
        _case_dry_run_reports_the_plan_and_writes_nothing, False
    ),
    "empty-plan-is-not-reported-as-a-dry-run": (
        _case_empty_plan_is_not_reported_as_a_dry_run, False
    ),
    "appending-a-later-class-is-the-same-operation-as-seeding": (
        _case_appending_a_later_class_is_the_same_operation_as_seeding, False
    ),
    "multi-source-class-cites-its-latest-source": (
        _case_multi_source_class_cites_its_latest_source, False
    ),
    "untagged-lesson-is-never-invented-as-a-class": (
        _case_untagged_lesson_is_never_invented_as_a_class, False
    ),
    "reseeding-a-seeded-lesson-is-refused-without-rewriting": (
        _case_reseeding_a_seeded_lesson_is_refused_without_rewriting, False
    ),
    "a-transition-id-burned-by-another-lesson-is-refused-by-name": (
        _case_a_transition_id_burned_by_another_lesson_is_refused_by_name, False
    ),
    "selected-subset-leaves-other-classes-unseeded": (
        _case_selected_subset_leaves_other_classes_unseeded, False
    ),
    "over-budget-seeding-is-refused-with-its-arithmetic": (
        _case_over_budget_seeding_is_refused_with_its_arithmetic, True
    ),
}


def test_seed_and_validate_decision_cases(tmp_path: Path, monkeypatch) -> None:
    for label, (case, needs_monkeypatch) in _SEED_TRANSITION_CASES.items():
        case_dir = tmp_path / label
        case_dir.mkdir()
        if needs_monkeypatch:
            case(case_dir, monkeypatch)
        else:
            case(case_dir)


def test_committed_transition_prefix_is_preserved_across_a_seed(tmp_path: Path) -> None:
    """The append-only gate compares against `git show HEAD:<path>`, which is exactly
    what the hand-edit this command replaces could not satisfy."""
    from tests.quality_gates.repo_shapes import replace_with_committed_repo

    _retro(tmp_path, "source.md", "a")
    _ledger(tmp_path)
    replace_with_committed_repo(tmp_path)
    _retro(tmp_path, "later.md", "b")

    _seed(tmp_path)

    payload = json.loads((tmp_path / "charness-artifacts/retro/lesson-ledger.json").read_text())
    assert [item["lesson_id"] for item in payload["transitions"]] == ["a", "b"]
    assert _validate(tmp_path)["transition_count"] == 2




def test_cli_dry_run_and_write_roundtrip(tmp_path: Path) -> None:
    """The rehearsal must plan exactly what the write then performs, and must leave
    the ledger byte-identical while it does."""
    _retro(tmp_path, "source.md", "a")
    path = _empty_ledger(tmp_path)
    rehearsal = run_script(
        str(ROOT / "scripts/seed_lesson_transitions.py"),
        "--repo-root",
        str(tmp_path),
        "--dry-run",
    )
    assert rehearsal.returncode == 0, rehearsal.stderr
    planned = yaml.safe_load(rehearsal.stdout)
    assert planned["dry_run"] is True and planned["seeded_count"] == 1
    # The ledger on disk stays JSON; only the command's own receipt moved to YAML.
    assert json.loads(path.read_text(encoding="utf-8"))["transitions"] == []

    applied = run_script(
        str(ROOT / "scripts/seed_lesson_transitions.py"),
        "--repo-root",
        str(tmp_path),
    )
    assert applied.returncode == 0, applied.stderr
    applied_receipt = yaml.safe_load(applied.stdout)
    assert applied_receipt["seeded"] == planned["seeded"]
    assert applied_receipt["dry_run"] is False
    assert _validate(tmp_path)["lesson_count"] == 1


def test_receipt_carries_the_freeze_warning_and_its_context_on_every_path(tmp_path: Path) -> None:
    """The risk statement and the next step, on all three receipt shapes.

    The freeze warning was gated on the WRITE, so it arrived only after the bytes
    it warned about had landed -- while the dry run, the inspection moment the
    whole mitigation rests on, stayed silent. Untested wording on a surface whose
    own job is stating a risk is the `proof-surface-message-drift` class this
    slice seeded as a lesson, and it does not stop being untested because the
    wording now travels as a payload field instead of a printed line.

    The receipt remains intentionally small: it reports the plan and the
    append-only citation warning, without carrying a second lifecycle state.
    """
    _retro(tmp_path, "source.md", "a")
    _empty_ledger(tmp_path)
    rehearsal = run_script(
        str(ROOT / "scripts/seed_lesson_transitions.py"),
        "--repo-root",
        str(tmp_path),
        "--dry-run",
    )
    assert rehearsal.returncode == 0, rehearsal.stderr
    planned = yaml.safe_load(rehearsal.stdout)
    assert planned["dry_run"] is True and planned["seeded_count"] == 1
    assert "unrepairably" in planned["freeze_note"]
    assert planned["seeded"][0]["lesson_id"] == "a"
    assert planned["seeded"][0]["source_retro"] == "charness-artifacts/retro/source.md"
    assert planned["active_lesson_count"] == 1
    assert planned["active_lesson_budget"] == ledger.ACTIVE_LESSON_BUDGET

    applied = run_script(
        str(ROOT / "scripts/seed_lesson_transitions.py"),
        "--repo-root",
        str(tmp_path),
    )
    assert applied.returncode == 0, applied.stderr
    written = yaml.safe_load(applied.stdout)
    assert written["dry_run"] is False and written["seeded_count"] == 1
    assert "unrepairably" in written["freeze_note"]

    # And the nothing-to-do receipt names why, rather than reporting an empty list.
    idle = run_script(
        str(ROOT / "scripts/seed_lesson_transitions.py"),
        "--repo-root",
        str(tmp_path),
    )
    assert idle.returncode == 0, idle.stderr
    nothing = yaml.safe_load(idle.stdout)
    assert nothing["seeded"] == [] and nothing["already_seeded_count"] == 1
    assert "recurrence-class" in nothing["recurrence_tag_instruction"]
    assert "unrepairably" in nothing["freeze_note"]


@pytest.mark.boundary_contract(
    reason="the ledger lock smoke requires two real writer processes"
)
def test_two_concurrent_seeders_smoke_check_the_shared_lock(tmp_path: Path) -> None:
    """A SMOKE CHECK, deliberately weaker than it first claimed to be.

    Two unsynchronized `Popen` processes cannot force the interleaving: with two
    interpreter cold starts dominating a sub-millisecond critical section, this
    would usually pass even with the lock removed. The real mutual-exclusion proof
    for this lock is `tests/test_lesson_ledger.py`'s fork-plus-`Barrier` pair,
    which rendezvouses both writers inside the window and skips where `fcntl` is
    unavailable.

    Kept because it cannot produce a false FAILURE -- with the lock held the loser
    always re-reads inside it and plans zero -- so it catches a gross regression
    (a double-seed or a lost append) at near-zero cost. It does not establish
    mutual exclusion, and an earlier docstring claiming parity with that fork-based
    proof was corrected by a review round.
    """
    _retro(tmp_path, "a.md", "a")
    _retro(tmp_path, "b.md", "b")
    _empty_ledger(tmp_path)

    command = [
        sys.executable,
        str(ROOT / "scripts/seed_lesson_transitions.py"),
        "--repo-root",
        str(tmp_path),
    ]
    first, second = (
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for _ in range(2)
    )
    outputs = [process.communicate() for process in (first, second)]
    codes = [process.returncode for process in (first, second)]

    assert codes == [0, 0], outputs
    # Whoever wins seeds both; the loser re-reads inside the lock and plans nothing.
    seeded = sorted(yaml.safe_load(out)["seeded_count"] for out, _err in outputs)
    assert seeded == [0, 2], outputs
    payload = json.loads(
        (tmp_path / "charness-artifacts/retro/lesson-ledger.json").read_text(encoding="utf-8")
    )
    assert [item["lesson_id"] for item in payload["transitions"]] == ["a", "b"]
    assert _validate(tmp_path)["lesson_count"] == 2


def test_cli_refuses_a_missing_ledger_and_names_the_bootstrap(tmp_path: Path) -> None:
    _retro(tmp_path, "source.md", "a")
    command = run_script(
        str(ROOT / "scripts/seed_lesson_transitions.py"),
        "--repo-root",
        str(tmp_path),
        real_process=True,
    )
    assert command.returncode == 1
    assert not (tmp_path / "charness-artifacts/retro/lesson-ledger.json").exists()
    # Not just the bare filename: that assertion held both before and after the message
    # was repaired, so it could not fail on a revert. `tmp_path` has no `scripts/` of its
    # own -- the shape of a consuming repo -- and the bootstrap command must therefore
    # resolve to a path that reader can actually run, not to `scripts/...`.
    assert "python3 scripts/init_lesson_ledger.py" not in command.stderr
    commands = [part for part in command.stderr.split("`") if part.startswith("python3 ")]
    assert commands, command.stderr
    named = Path(commands[0].split()[1])
    assert named.is_absolute() and named.is_file(), command.stderr
