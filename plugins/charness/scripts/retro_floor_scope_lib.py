#!/usr/bin/env python3
"""The dated retro floors: when each activates, whether it applies to THIS repo, and
how a run announces that.

Split from `validate_retro_artifact` at its length cap, and the split line is the one
a review found the module had drawn WRONG. Enforcement asked "does this repo declare
an evaluator" from a hardcoded `charness-artifacts/retro`, while the announcement
asked the adapter -- so one run refused an artifact for a missing disposition and
printed "no retro owes a disposition" in the same breath, with an opt-in command that
wrote to the directory the enforcement half never read. The two probes now live
together and resolve the directory the same way; keeping them apart is what let them
disagree.

Nothing here renders a verdict on an artifact's CONTENT: this answers which floors are
switched on, and `validate_retro_artifact` enforces them. It re-exports every public
name, so `plan_retro_run` and `seed_retro_memory` keep one import site.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from runtime_bootstrap import import_repo_module

_lesson_evaluation = import_repo_module(__file__, "scripts.lesson_evaluation_continuity_lib")
_lesson_records = import_repo_module(__file__, "scripts.lesson_evaluation_records_lib")
#: The lesson-ledger subsystem is keyed on ONE literal, repo-wide, deliberately.
#: Making these probes adapter-derived was tried and reverted twice. The first attempt
#: moved the announcement only, and the run then refused an artifact for a missing
#: disposition while printing "no retro owes a disposition". The second moved the
#: writer too, and that was worse: 29 other lifecycle entry points -- `open_lesson_session`,
#: `record_lesson_score`, `check_lesson_ledger`, the contract register -- still read the
#: literal, so a consumer who opted in got the floor switched ON and every one of those
#: raising `FileNotFoundError`. Inert-and-stuck beats on-and-unsatisfiable.
#:
#: A consistent literal is a known, greppable state; a half-migrated one disagrees with
#: itself for exactly the consumers the migration was for. Migrating it is one slice over
#: all 30 sites with its own proof, not a rider on a validator repair. What IS
#: adapter-derived is `validate_retro_artifact`'s candidate filter and owned prefix --
#: the reported defect, and a different question from where the ledger lives.
LESSON_LEDGER_PREFIX = "charness-artifacts/retro/"


# Every retro must consult the north star and say what it found (user standing
# request, 2026-08-02). Recorded as a floor rather than prose because prose is what it
# already was: `SKILL.md` has always pointed at the design standard, two consecutive
# retros still shipped without a facet mapping, and the operator had to ask twice.
#
# Presence-only, never a content classifier: the floor proves the question was ASKED,
# and the answer's quality is the fresh-eye reviewer's call.
#
# Lands 2026-08-02; enforcement begins the NEXT day so every retro frozen on or before
# the landing day is grandfathered -- the established RESIDUAL_LEDGER_RULE_DATE /
# STRUCTURAL_FOLLOWUP_RULE_DATE precedent.
NEXT_IMPROVEMENTS_HEADING = "## Next Improvements"
# Recurrence-lineage floor for standalone retros: the symmetric extension of the
# achieve rung 1d to a session retro's `## Next Improvements`. Its own enforce-from
# date lands the day after this floor so every existing retro is grandfathered; only
# retros dated on/after it must carry a lineage marker on issue-form dispositions.
RECURRENCE_LINEAGE_RULE_DATE = date(2026, 6, 9)
PERSISTED_FORM_RULE_DATE = date(2026, 6, 25)
NORTH_STAR_RULE_DATE = date(2026, 8, 3)
NORTH_STAR_HEADING = "North Star Alignment"
LESSON_LEDGER_FILENAME = "lesson-ledger.json"
LESSON_LEDGER_BOOTSTRAP_SCRIPT = "init_lesson_ledger.py"


def lesson_evaluator_declared(
    path: Path, *, output_dir: Path | None = None, repo_root: Path | None = None
) -> bool:
    """Whether this repo declares the lesson evaluator the disposition floor scores.

    Both `skills/public/retro/references/lesson-evaluation.md` ("repos whose
    evidence declares no evaluator have no lesson-scoring duty") and the retro
    `SKILL.md` ("otherwise there is no scoring duty") say the duty is
    conditional. The code said the opposite: EVERY retro dated on/after the
    activation date owed a disposition in ANY repo. A consuming repo that had
    never opted in could therefore satisfy the gate only with `not-evaluated /
    missing-start` — permanently, because no other value is reachable without a
    ledger — while the prose told it there was no duty at all. Prose and code
    disagreeing about a duty is the dishonesty here, not the strictness; the code
    now matches the prose.

    The declaration is the ledger itself: it is the declared-session evaluator's
    only state, and `scripts/init_lesson_ledger.py` is the explicit opt-in that
    creates it. Probed beside the artifact because that directory IS the retro
    output dir.

    Fail-CLOSED when the artifact does not sit in the repo's retro output dir.
    There the probe cannot see the repo's evaluator state at all, and a floor
    that switches ITSELF off on an unrecognized layout is a floor that silently
    never fires — the exact escape shape the sibling floors' fail-closed
    grandfathering guards.

    TWO questions, and they take different answers because they are different
    questions. "Is this artifact one of this repo's retros" is adapter-shaped -- the
    validator's candidate filter now yields artifacts from a declared `output_dir`, so a
    membership test keyed on the literal would call every one of them foreign and
    fail-closed onto a floor the repo never opted into. "Where is the ledger" is the
    LITERAL, because 30 scripts read it there and moving one moves nothing (see
    `LESSON_LEDGER_PREFIX`).

    Reading the ledger beside the ARTIFACT was the shape that made the two halves of one
    run disagree: for a declared `artifacts/retros` it probed a directory the
    announcement never looked at, and no opt-in could reconcile them. Both halves now
    read one path.

    Fail-CLOSED when the artifact is outside the repo's retro directory: there the probe
    cannot see the repo's evaluator state, and a floor that switches ITSELF off on an
    unrecognized layout is a floor that silently never fires.
    """
    directory = path.parent
    if output_dir is None:
        if directory.name != "retro" or directory.parent.name != "charness-artifacts":
            return True
    elif directory.resolve() != output_dir.resolve():
        return True
    # `repo_root` is PASSED, never re-derived by walking up from `output_dir`: that walk
    # has to guess how many segments the declared directory has, and it is only right for
    # a two-segment one. A caller with no run context falls back to the artifact's own
    # directory, which is the literal layout by construction.
    ledger_root = repo_root / LESSON_LEDGER_PREFIX if repo_root is not None else path.parent
    return (ledger_root / LESSON_LEDGER_FILENAME).is_file()


def lesson_ledger_bootstrap_command(repo_root: Path) -> str:
    """The runnable opt-in command for THIS layout, not one repo's spelling.

    A consuming repo has no `scripts/` of its own — it gets one beside this
    validator inside the installed plugin. Emitting a bare
    `scripts/init_lesson_ledger.py` would tell a consuming author to run a file
    they do not have, which is the same "names a path nothing creates" defect
    that put the retro scaffold's north star line and this repo's own adapter
    anchor on the reported list. Repo-local wins when present, mirroring
    `scaffold_artifact_lib.validator_command`'s resolution order so a consumer
    cites the same script its broad gate would.

    Delegated to `lesson_evaluation_records_lib` since the retro run planner had to
    resolve `record_lesson_score.py` the identical way: a second copy of this
    resolution is how one surface starts naming `scripts/...` in a repo that has no
    `scripts/` while its sibling names the installed path.
    """
    return _lesson_records.repo_or_installed_command(
        repo_root, LESSON_LEDGER_BOOTSTRAP_SCRIPT, "--repo-root", "."
    )


def date_activated_rules(repo_root: Path) -> list[dict[str, object]]:
    """Every retro floor that switches on by artifact date, as announceable data.

    These dates were reachable only by TRIPPING them: a consuming author whose
    previous retro needed no `## Lesson Evaluation` section read the new refusal
    as breakage rather than as a dated floor that had just activated. The achieve
    family already emits `rule_date` in every report payload; the retro planner
    now announces the same thing from these constants, so the announcement cannot
    drift from the rule it announces.
    """
    prefix = LESSON_LEDGER_PREFIX
    ledger = repo_root / prefix / LESSON_LEDGER_FILENAME
    declared = ledger.is_file()
    return [
        {
            "id": "lesson-evaluation-disposition",
            "rule_date": _lesson_evaluation.ACTIVATION_DATE.isoformat(),
            "what": (
                "a retro dated on/after this owes exactly one `Lesson evaluation: <JSON>` line "
                f"inside `{_lesson_evaluation.SECTION_HEADING}`"
            ),
            "conditional_on": (
                f"this repo declaring a lesson evaluator ({prefix}{LESSON_LEDGER_FILENAME})"
            ),
            "evaluator_declared": declared,
            "enforced_here": declared,
            "opt_in_command": None if declared else lesson_ledger_bootstrap_command(repo_root),
        },
        {
            "id": "north-star-alignment",
            "rule_date": NORTH_STAR_RULE_DATE.isoformat(),
            "what": f"a retro dated on/after this needs a `## {NORTH_STAR_HEADING}` section with content",
            "enforced_here": True,
        },
        {
            "id": "recurrence-lineage",
            "rule_date": RECURRENCE_LINEAGE_RULE_DATE.isoformat(),
            "what": (
                f"`{NEXT_IMPROVEMENTS_HEADING}` issue-routed dispositions need a recurrence-lineage "
                "marker (`novel:` / `recurs:`)"
            ),
            "enforced_here": True,
        },
        {
            "id": "persisted-form",
            "rule_date": PERSISTED_FORM_RULE_DATE.isoformat(),
            "what": "`## Persisted` must read `Persisted: yes: <path>` or `Persisted: no: <reason>`",
            "enforced_here": True,
        },
    ]


def report_enforcement_scope(run, artifacts) -> None:
    """Name whether the conditional lesson-evaluation floor actually ran.

    `run_changed_artifact_validator` documents `on_complete` for exactly this
    case: a floor that is off emits nothing by construction, so a run reporting
    only "Validated N retro artifacts" reads as coverage it does not have. Both
    silences this closes were reported together — an activation date invisible
    until tripped, and a disposition duty a repo could not tell it had opted out
    of. Reporting only; it changes no verdict and no exit code.
    """
    prefix = LESSON_LEDGER_PREFIX
    ledger = run.repo_root / prefix / LESSON_LEDGER_FILENAME
    declared = ledger.is_file()
    activation = _lesson_evaluation.ACTIVATION_DATE.isoformat()
    if declared:
        print(
            f"Lesson evaluation floor: enforced for retros dated >= {activation} "
            f"(evaluator declared at {prefix}{LESSON_LEDGER_FILENAME})."
        )
        return
    print(
        f"Lesson evaluation floor: inert — this repo declares no lesson evaluator "
        f"({prefix}{LESSON_LEDGER_FILENAME} absent), so no retro owes a disposition. "
        f"Opt in with `{lesson_ledger_bootstrap_command(run.repo_root)}`; the floor then applies "
        f"from {activation}."
    )
