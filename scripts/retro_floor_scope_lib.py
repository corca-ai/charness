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
_output_dir_lib = import_repo_module(__file__, "scripts.retro_output_dir_lib")


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


def lesson_evaluator_declared(path: Path, *, output_dir: Path | None = None) -> bool:
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

    The lesson-evaluation lifecycle is keyed on the LITERAL layout end to end, and this
    floor is scoped to what that lifecycle can actually serve.

    That scope is not a guess. `lesson_score_outcome_lib.canonical_retro_citation`
    refuses any `--source-retro` whose parts are not exactly
    `("charness-artifacts", "retro", "<name>.md")`, and
    `lesson_evaluation_records_lib.collect_retro_candidates` globs the same literal. So
    for a repo declaring another `output_dir`, no score event can cite its retros and no
    candidate enumeration can see them: the only disposition value reachable is
    `not-evaluated / missing-start`, forever. Enforcing a duty whose sole satisfying
    answer is "not evaluated" is the dishonesty this floor's own history names, and it is
    what an earlier version of this function shipped -- with a test pinning it as correct.

    So an artifact outside the literal layout owes NOTHING, and `report_enforcement_scope`
    says why rather than staying quiet. That is the difference from fail-open: fail-open
    is a probe that cannot see the repo's state and guesses "no duty". Here the state is
    established positively -- the repo declares a directory, and the lifecycle provably
    cannot address it. A floor that silently never fires is the escape shape; a floor that
    announces the boundary it does not cross is a scoped floor.

    THREE cases, and collapsing the last two was a defect in both directions:

    * inside the literal layout -- the ledger beside the artifact is the declaration,
      probed at the one path all ~30 lifecycle scripts read.
    * inside a directory the repo POSITIVELY DECLARED as its `output_dir` -- scoped out
      per the paragraph above, and `report_enforcement_scope` prints why.
    * anywhere else -- fail-CLOSED. Here the probe genuinely cannot see the repo's
      evaluator state, and a floor that switches ITSELF off on an unrecognized layout is
      a floor that silently never fires. This is the case the scoped-out arm must not
      swallow: "the lifecycle cannot address a declared directory" is an established
      fact, while "I do not know where this file is" is not.
    """
    directory = path.parent
    if directory.name == "retro" and directory.parent.name == "charness-artifacts":
        return (directory / LESSON_LEDGER_FILENAME).is_file()
    if output_dir is not None and directory.resolve() == output_dir.resolve():
        return False
    return True


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
    # The boundary is ANNOUNCED, not left to be inferred from a floor that quietly
    # never fires. A repo whose retros live outside the literal layout cannot reach
    # the lifecycle at all -- scores cannot cite those paths and candidate
    # enumeration cannot see them -- so it owes no disposition and deserves to be
    # told that, including that the opt-in below would not change it.
    declared_dir = _output_dir_lib.retro_artifact_prefix(run.repo_root)
    if declared_dir != prefix:
        print(
            f"Lesson evaluation floor: out of scope -- this repo declares "
            f"`output_dir: {declared_dir.rstrip('/')}`, and the lesson lifecycle is keyed on "
            f"`{prefix.rstrip('/')}` end to end (score citations and candidate enumeration "
            "both refuse other paths). Its retros owe no disposition, and creating a "
            "ledger would not change that."
        )
        return
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
