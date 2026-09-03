"""The two mechanisms that stop a tagged recurrence class from stranding.

Tagging a retro bullet `(recurrence-class: <id>)` makes a lesson SEEDABLE. The
seed transition that makes it SELECTABLE was a second command, and nobody ran it:
twelve tagged classes sat outside the ledger with no surface saying so. Persisting
the retro now runs the seeder, and the standing lane names whatever is still
pending. Both halves are exercised here rather than in
`test_retro_persistence.py`, which owns the persistence contract itself and is
already inside its length warn band.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module
from scripts.lessons import lesson_ledger_lib as ledger
from scripts.lessons import seed_lesson_transitions as seeder
from tests.quality_gates.seeding_support import write_retro_adapter
from tests.quality_gates.test_retro_persistence import run_persist
from tests.script_loader import load_script_module
from tests.test_lesson_ledger import ROOT, _ledger, _retro
from tests.test_seed_lesson_transitions import _empty_ledger

# The SAME module object `run_persist` drives, so a direct call and an end-to-end
# persist exercise one implementation rather than two loads of one file.
_persist = import_repo_module(
    ROOT / "skills/public/retro/scripts/persist_retro_artifact.py",
    "skills.public.retro.scripts.persist_retro_artifact",
)


def _tagged_retro_body(lesson_class: str) -> str:
    """A retro whose Waste bullet tags a class, carrying the `## Persisted` line.

    The `Persisted:` placeholder is what persistence stamps, and the `Seeding:`
    note is defined to sit directly under it, so a body without one cannot show
    where the note lands.
    """
    return "\n".join(
        [
            "# Session Retro",
            "",
            "## Context",
            "",
            "- The seed transition was a separate command nobody ran.",
            "",
            "## Waste",
            "",
            f"- a lesson nothing could select (recurrence-class: {lesson_class})",
            "",
            "## Next Improvements",
            "",
            "- `capability`: seed at the moment the tag becomes durable.",
            "",
            "## Persisted",
            "",
            "Persisted: yes: TODO path",
            "",
        ]
    )


def _persist_tagged_retro(repo: Path, monkeypatch, capsys, lesson_class: str, name: str):
    markdown_file = repo / f"{lesson_class}-session.md"
    markdown_file.write_text(_tagged_retro_body(lesson_class), encoding="utf-8")
    return run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        name,
        "--markdown-file",
        str(markdown_file),
    )


def _patch_budget(monkeypatch, value: int) -> None:
    """Both module objects, for the reason `test_seed_lesson_transitions` records.

    The seeder reaches the ledger library through `import_repo_module`, which can
    hand back an instance distinct from the one imported here, and the ledger file
    itself must carry the same budget or its own fixed-budget check fires before
    the seeder's arithmetic is ever reached.
    """
    for module in {id(ledger): ledger, id(seeder._ledger): seeder._ledger}.values():
        monkeypatch.setattr(module, "ACTIVE_LESSON_BUDGET", value)


def test_persist_seeds_the_class_the_retro_just_tagged(tmp_path, monkeypatch, capsys) -> None:
    """The whole point: tagging and seeding stop being two separate acts.

    The retro under persist is the one that introduces the class, so this also
    pins the ORDER -- the seeder derives candidates from `output_dir/*.md` and can
    only see the tag once the artifact is durable.
    """
    repo = tmp_path / "repo"
    write_retro_adapter(repo)
    _empty_ledger(repo)
    ledger_path = repo / "charness-artifacts/retro/lesson-ledger.json"

    result = _persist_tagged_retro(
        repo, monkeypatch, capsys, "stranded-class", "2026-09-03-seeding.md"
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert [item["lesson_id"] for item in payload["transitions"]] == ["stranded-class"]
    assert payload["lessons"]["stranded-class"]["state"] == "active"
    written = (repo / "charness-artifacts/retro/2026-09-03-seeding.md").read_text(encoding="utf-8")
    assert "Persisted: yes: charness-artifacts/retro/2026-09-03-seeding.md\n" in written
    assert "Seeding: 1 class(es) seeded" in written
    # Directly UNDER the persisted line, which is the only place a reader of that
    # block looks for it.
    lines = written.splitlines()
    assert lines[lines.index("Seeding: 1 class(es) seeded") - 1].startswith("Persisted: yes:")
    # And the ledger validates afterwards, so persistence cannot leave behind a
    # transition the standing lane then rejects.
    assert ledger.validate_lesson_ledger(
        repo_root=repo,
        output_dir=repo / "charness-artifacts/retro",
        summary_path=repo / "charness-artifacts/retro/recent-lessons.md",
    )["lesson_count"] == 1


def test_a_budget_refusal_is_carried_by_the_retro_and_leaves_the_ledger_alone(
    tmp_path, monkeypatch, capsys
) -> None:
    """An over-budget ledger is a legitimate state awaiting a human archive call.

    Failing the persist would throw away a retro that is already written for a
    condition its author cannot fix in that moment, so the refusal travels as text
    instead. This is the state the real repo is in: 49 active lessons and twelve
    tagged classes that will not fit under the fixed budget.
    """
    repo = tmp_path / "repo"
    write_retro_adapter(repo)
    _patch_budget(monkeypatch, 1)
    _retro(repo, "source.md", "a")
    ledger_path = _ledger(repo)
    before = ledger_path.read_bytes()

    result = _persist_tagged_retro(repo, monkeypatch, capsys, "over-budget", "2026-09-03-full.md")

    assert result.returncode == 0, result.stderr
    assert ledger_path.read_bytes() == before
    written = (repo / "charness-artifacts/retro/2026-09-03-full.md").read_text(encoding="utf-8")
    assert "Seeding: refused: " in written
    assert "past the fixed budget of 1" in written
    # One line, because the block it lands in is read line-per-fact.
    note = next(line for line in written.splitlines() if line.startswith("Seeding: "))
    assert "record_lesson_lifecycle.py" in note


def test_a_repo_with_no_lesson_ledger_is_untouched_and_carries_no_note(
    tmp_path, monkeypatch, capsys
) -> None:
    """The portability contract: the ledger is optional and most repos keep none.

    No ledger means no seeder run, no created ledger, and no `Seeding:` line --
    the same silent no-op the digest refresh uses when no `summary_path` is
    declared.
    """
    repo = tmp_path / "repo"
    write_retro_adapter(repo)

    result = _persist_tagged_retro(repo, monkeypatch, capsys, "no-ledger", "2026-09-03-plain.md")

    assert result.returncode == 0, result.stderr
    assert not (repo / "charness-artifacts/retro/lesson-ledger.json").exists()
    written = (repo / "charness-artifacts/retro/2026-09-03-plain.md").read_text(encoding="utf-8")
    assert "Seeding:" not in written
    assert "seeding" not in result.stdout


def test_a_body_that_claims_no_durable_home_carries_no_seeding_note() -> None:
    """No `Persisted:` line means no line for this note to qualify.

    A hand-authored body that never claimed a durable home would otherwise grow a
    `Seeding:` line anchored to nothing, in a block whose reader takes every line
    as a fact about the artifact on disk. The receipt still reports the seeding,
    so the outcome is not lost -- only the in-artifact copy is skipped.
    """
    body = "\n".join(["# Session Retro", "", "## Waste", "", "- nothing durable was claimed", ""])

    assert _persist.stamp_seeding_note(body, "1 class(es) seeded") == body


def test_re_persisting_replaces_the_previous_seeding_note_instead_of_stacking() -> None:
    """Re-persisting an explicitly named artifact runs the seeder again.

    The second run's answer is the true one -- the first run already seeded what
    it found -- so appending would leave the reader two `Seeding:` lines with no
    way to tell which run produced which.
    """
    first = _persist.stamp_seeding_note(_tagged_retro_body("restamped"), "none pending")

    second = _persist.stamp_seeding_note(first, "1 class(es) seeded")

    notes = [line for line in second.splitlines() if line.startswith("Seeding: ")]
    assert notes == ["Seeding: 1 class(es) seeded"]
    lines = second.splitlines()
    assert lines[lines.index(notes[0]) - 1].startswith("Persisted: ")


def _run_check(repo: Path, monkeypatch, capsys):
    checker = load_script_module(
        "check_lesson_ledger_for_seeding_test", ROOT / "scripts/lessons/check_lesson_ledger.py"
    )
    monkeypatch.setattr(sys, "argv", ["check_lesson_ledger.py", "--repo-root", str(repo)])
    returncode = checker.main()
    return returncode, capsys.readouterr().out


def test_the_standing_lane_names_unseeded_classes_without_failing(
    tmp_path, monkeypatch, capsys
) -> None:
    """ADVISORY, and exit 0, on purpose.

    A tagged class goes unseeded either because nobody ran the seeder or because
    the ledger is over budget and waiting on an archive decision. The second is
    legitimate, so a hard failure would hold the lane red on a state no one can
    clear without making that decision under time pressure. Silence is the wrong
    answer too -- that is what let twelve classes strand.
    """
    repo = tmp_path / "repo"
    _retro(repo, "source.md", "a")
    _ledger(repo)
    _retro(repo, "later.md", "b")

    returncode, out = _run_check(repo, monkeypatch, capsys)

    assert returncode == 0
    assert "ADVISORY: 1 tagged recurrence class(es) not seeded: b" in out
    # The validation verdict still leads; the advisory qualifies it rather than
    # replacing it.
    assert out.splitlines()[0].startswith("Validated lesson ledger: 1 lessons")


def test_a_fully_seeded_ledger_prints_no_advisory(tmp_path, monkeypatch, capsys) -> None:
    """A line that prints on every clean run is a line readers stop reading."""
    repo = tmp_path / "repo"
    _retro(repo, "source.md", "a")
    _ledger(repo)

    returncode, out = _run_check(repo, monkeypatch, capsys)

    assert returncode == 0
    assert "ADVISORY" not in out


def test_the_advisory_and_the_seeder_answer_from_one_derivation(tmp_path) -> None:
    """The gate must never name a class the seeder would not plan, or miss one.

    Two independent derivations of "what is pending" is exactly how a gate ends up
    reassuring a reader about a class the command still refuses to touch.
    """
    repo = tmp_path / "repo"
    _retro(repo, "source.md", "a")
    _ledger(repo)
    _retro(repo, "later.md", "b")
    output_dir = repo / "charness-artifacts/retro"
    summary_path = output_dir / "recent-lessons.md"

    pending = seeder.pending_seed_classes(
        repo_root=repo, output_dir=output_dir, summary_path=summary_path
    )
    planned = seeder.seed_transitions(
        repo_root=repo,
        output_dir=output_dir,
        summary_path=summary_path,
        lesson_ids=None,
        dry_run=True,
    )

    assert pending == ["b"]
    assert [item["lesson_id"] for item in planned["seeded"]] == pending


def test_a_repo_with_no_ledger_has_nothing_pending(tmp_path) -> None:
    """The read-only surface is portable too: an absent ledger is not an error.

    `check_lesson_ledger.py` asks what is pending on repos that keep tagged retros
    and no ledger at all, which is the ordinary consuming-repo shape. An absent
    optional ledger has nothing pending, so the answer is empty rather than a
    crash or a phantom list of classes no ledger could hold.
    """
    repo = tmp_path / "repo"
    _retro(repo, "source.md", "a")
    output_dir = repo / "charness-artifacts/retro"
    assert not (output_dir / "lesson-ledger.json").exists()

    pending = seeder.pending_seed_classes(
        repo_root=repo, output_dir=output_dir, summary_path=output_dir / "recent-lessons.md"
    )

    assert pending == []
    # And nothing was created by asking, so the read-only claim holds.
    assert not (output_dir / "lesson-ledger.json").exists()
