"""The retro floors whose SCOPE is conditional, and the refusals that teach it.

Sibling of `tests/test_retro_artifact.py`, which covers the floors' verdicts.
This file covers the two things a consuming repo actually reported: which floors
apply to it at all, and whether a refusal tells an author what to write.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

from scripts import init_lesson_ledger
from scripts import lesson_evaluation_continuity_lib as continuity
from scripts import validate_retro_artifact as retro_validator
from tests.quality_gates.support import ROOT, run_script
from tests.script_main import run_loaded_script_main

_SCAFFOLD_REL = "skills/public/retro/scripts/scaffold_retro_artifact.py"


def _scaffold_module():
    spec = importlib.util.spec_from_file_location(
        "scaffold_retro_artifact_floors", ROOT / _SCAFFOLD_REL
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

_ACTIVATED_RETRO = (
    "# Session Retro: Demo\nDate: 2026-08-14\nMode: session\n\n"
    "## North Star Alignment\n\n- P1 held: the slice stayed reversible.\n\n"
    "## Next Improvements\n\n- workflow: do better\n\n"
    "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-08-14-demo.md\n"
)


def _seed_retro(repo: Path, body: str = _ACTIVATED_RETRO) -> Path:
    artifact = repo / "charness-artifacts" / "retro" / "2026-08-14-demo.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(body, encoding="utf-8")
    return artifact


# In-process, not subprocess: both entrypoints are import-safe, and this repo
# ratchets the test-suite process boundary down (`scripts/check_boundary_bypass_
# ratchet.py`). What these tests assert is the validator's own stdout/stderr and
# exit code, which `run_loaded_script_main` reproduces from `main()` — none of it
# needs a second interpreter. The scaffold below stays a subprocess: it is the
# operator-facing emitter whose payload contract this test consumes end-to-end.
# Repo-owned commands emit YAML unconditionally since the `--json` removal, so
# every payload here is read with `yaml.safe_load` (a JSON superset).
def _validate(repo: Path):
    return run_loaded_script_main(
        "validate_retro_artifact.py", retro_validator, "--repo-root", str(repo), "--all"
    )


def _init_ledger(repo: Path, *args: str):
    """Run the ledger bootstrap the way its `__main__` guard does.

    `cli_error_types` mirrors that guard's own `except (FileExistsError,
    FileNotFoundError, OSError, ValueError)` arm, so the append-only refusal below
    still lands on stderr with exit 1 instead of escaping as a raw traceback.
    """
    return run_loaded_script_main(
        "init_lesson_ledger.py",
        init_lesson_ledger,
        "--repo-root",
        str(repo),
        *args,
        cli_error_types=(OSError, ValueError),
    )


def test_disposition_floor_is_inert_in_a_repo_that_declares_no_evaluator(tmp_path: Path) -> None:
    """The prose says an undeclared repo has no scoring duty; the code now agrees.

    Before this, every retro dated on/after the activation date owed a
    disposition in ANY repo — while the only reachable value without a ledger was
    `not-evaluated / missing-start`, forever. The floor demanded paperwork the
    repo could never make mean anything.
    """
    repo = tmp_path / "repo"
    _seed_retro(repo)

    result = _validate(repo)

    assert result.returncode == 0, result.stderr
    assert "Lesson evaluation floor: inert" in result.stdout
    assert "init_lesson_ledger.py" in result.stdout


def test_disposition_floor_applies_once_the_repo_opts_in(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_retro(repo)
    init = _init_ledger(repo)
    assert init.returncode == 0, init.stderr
    receipt = yaml.safe_load(init.stdout)
    assert receipt["lesson_count"] == 0
    assert "recurrence-class:" in receipt["next_step"]

    result = _validate(repo)

    assert result.returncode == 1
    assert "Lesson Evaluation" in result.stderr
    assert "Lesson evaluation floor: enforced" in result.stdout


def test_disposition_floor_fails_closed_outside_a_canonical_retro_directory(tmp_path: Path) -> None:
    """A floor that switches ITSELF off on an unrecognized layout never fires.

    The evaluator probe can only speak about an artifact sitting in the repo's
    retro output dir. Anywhere else it cannot see the repo's evaluator state, so
    the floor stays on rather than silently exempting the artifact.
    """
    import scripts.validate_retro_artifact as validator

    loose = tmp_path / "2026-08-14-demo.md"
    loose.write_text(_ACTIVATED_RETRO, encoding="utf-8")

    assert validator.lesson_evaluator_declared(loose) is True
    with pytest.raises(validator.ValidationError, match="Lesson Evaluation"):
        validator.validate_retro_artifact(loose)


def test_init_lesson_ledger_refuses_to_overwrite_an_existing_ledger(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    assert _init_ledger(repo).returncode == 0

    second = _init_ledger(repo)

    assert second.returncode == 1
    assert "append-only" in second.stderr


def test_disposition_refusals_name_the_grammar_they_demand(tmp_path: Path) -> None:
    """Both refusals an author hits FIRST used to name zero keys.

    The reference they pointed at deliberately keeps the grammar repo-owned, and
    the only prose home was an authoring-repo doc the plugin does not ship — two
    validator round-trips and a source dive to write one line.
    """
    for text in (
        "## Context\n\nno section at all\n",
        f"{continuity.SECTION_HEADING}\n\nno typed line here\n",
    ):
        with pytest.raises(continuity.LessonEvaluationError) as excinfo:
            continuity.parse_disposition(text)
        message = str(excinfo.value)
        for token in sorted(continuity.BASE_DISPOSITION_KEYS):
            assert token in message
        for token in sorted(continuity.STATUSES) + sorted(continuity.REASONS):
            assert token in message
        assert continuity.canonical_json(continuity.MISSING_START_DISPOSITION) in message


def test_north_star_reference_uses_the_portable_authoring_repo_spelling() -> None:
    """A bare `docs/design-north-star.md` names a file no consuming repo has."""
    import scripts.validate_retro_artifact as validator

    assert validator.NORTH_STAR_REFERENCE == "<authoring-repo>/docs/design-north-star.md"
    assert (
        "<authoring-repo>/docs/design-north-star.md"
        in (ROOT / "skills/public/retro/scripts/scaffold_retro_artifact.py").read_text(
            encoding="utf-8"
        )
    )


def test_scaffold_drops_adapter_sections_that_collide_with_a_heading_it_owns() -> None:
    """The reported defect: an adapter re-declaring a scaffold-owned heading.

    This repo's own `.agents/retro-adapter.yaml` declared `## Lesson Evaluation`,
    the exact heading the disposition floor requires to appear EXACTLY once, so
    the scaffold emitted an artifact its own validator refused twice over. The
    adapter is now empty, which means only THIS test holds the code fix in place:
    without it, deleting `_sections_without_owned_headings` leaves every suite
    green and the defect returns the moment any consuming adapter declares the
    heading.

    Dropping is per BLOCK, so the colliding section's body goes with its heading
    rather than stranding orphan prose under the scaffold's own heading.
    """
    scaffold = _scaffold_module()

    template = scaffold.render_template(
        title="Session Retro",
        date_text="2026-08-14",
        artifact_sections=[
            "## Lesson Evaluation",
            "",
            "Lesson evaluation: TODO replace with the repo-owned form",
            "## Repo Evaluator",
            "",
            "Repo evaluation: TODO exact repo-owned form",
        ],
    )
    lines = template.splitlines()

    assert [line.strip() for line in lines].count(continuity.SECTION_HEADING) == 1
    assert sum(1 for line in lines if line.startswith(continuity.LINE_PREFIX)) == 1
    # The colliding block's BODY left with its heading...
    assert "TODO replace with the repo-owned form" not in template
    # ...while the scaffold's own validating disposition survived...
    assert continuity.canonical_json(continuity.MISSING_START_DISPOSITION) in template
    # ...and a non-colliding adapter section is still appended untouched.
    assert "## Repo Evaluator" in template
    assert "Repo evaluation: TODO exact repo-owned form" in template


def test_scaffolded_retro_validates_unchanged_in_a_repo_that_opted_in(tmp_path: Path) -> None:
    """The #623 headline: the prescribed path must produce a VALID artifact.

    End-to-end through the real scripts — scaffold, opt in, write the template
    byte-for-byte, validate — with the disposition floor ENFORCED, because an
    inert floor would prove nothing about the seeded disposition. The adapter
    deliberately re-declares the colliding heading so this also covers the
    scaffold path, not just `render_template` in isolation.
    """
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "version: 1\n"
        "repo: consumer\n"
        "language: en\n"
        "output_dir: charness-artifacts/retro\n"
        "artifact_sections:\n"
        '  - "## Lesson Evaluation"\n'
        '  - ""\n'
        '  - "Lesson evaluation: TODO replace with the repo-owned form"\n',
        encoding="utf-8",
    )
    assert _init_ledger(repo).returncode == 0

    scaffolded = run_script(_SCAFFOLD_REL, "--repo-root", str(repo), "--title", "Demo")
    assert scaffolded.returncode == 0, scaffolded.stderr
    payload = yaml.safe_load(scaffolded.stdout)
    written = repo / payload["write_artifact_path"]
    written.write_text(payload["template"], encoding="utf-8")

    result = _validate(repo)

    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert "Lesson evaluation floor: enforced" in result.stdout


def test_date_activated_rules_announce_every_dated_retro_floor(tmp_path: Path) -> None:
    """Four rule dates were reachable only by tripping them."""
    import scripts.validate_retro_artifact as validator

    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    rules = {rule["id"]: rule for rule in validator.date_activated_rules(repo)}

    assert set(rules) == {
        "lesson-evaluation-disposition",
        "north-star-alignment",
        "recurrence-lineage",
        "persisted-form",
    }
    assert rules["lesson-evaluation-disposition"]["rule_date"] == (
        continuity.ACTIVATION_DATE.isoformat()
    )
    assert rules["lesson-evaluation-disposition"]["evaluator_declared"] is False
    assert rules["lesson-evaluation-disposition"]["enforced_here"] is False
    assert "init_lesson_ledger.py" in rules["lesson-evaluation-disposition"]["opt_in_command"]
    assert rules["north-star-alignment"]["rule_date"] == validator.NORTH_STAR_RULE_DATE.isoformat()
    assert rules["recurrence-lineage"]["rule_date"] == (
        validator.RECURRENCE_LINEAGE_RULE_DATE.isoformat()
    )
    assert rules["persisted-form"]["rule_date"] == validator.PERSISTED_FORM_RULE_DATE.isoformat()
