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
from tests.script_loader import load_script_module
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


def test_north_star_reference_resolves_per_repo_and_never_writes_a_placeholder(
    tmp_path: Path,
) -> None:
    """SUPERSEDES the `<authoring-repo>/` pin, and the reversal is the point.

    The old rule was right that a bare `docs/design-north-star.md` names a file no
    consuming repo has. It was wrong about the remedy: `<authoring-repo>/` is
    charness's INTERNAL vocabulary for "resolves in my tree, not yours", so a consuming
    author reads it as a path and looks for a directory that does not exist. Both
    surfaces now resolve against the repo they are talking about -- the scaffold that
    seeds the section, and the refusal message the author hits when they fail -- and
    neither writes a placeholder in either branch.
    """
    import scripts.validate_retro_artifact as validator

    # The root is derived from the ARTIFACT's location, not from this script's: an
    # exported copy validating a consuming repo's retro would otherwise resolve against
    # the plugin tree and name charness's design doc at a consumer. Both arms, because
    # `None` is what stops an ad-hoc path from being handed an unrelated repo's root.
    canonical = tmp_path / "some-consumer" / "charness-artifacts" / "retro" / "2026-08-16-x.md"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("# x\n", encoding="utf-8")
    assert validator._repo_root_for(canonical) == (tmp_path / "some-consumer").resolve()
    assert validator._repo_root_for(tmp_path / "loose.md") is None
    # A `retro/` parent is not enough: only the full `charness-artifacts/retro/` layout
    # says which tree the artifact belongs to. Asserted separately because the two
    # refusals are separate branches and the first one hides the second.
    assert validator._repo_root_for(tmp_path / "notes" / "retro" / "x.md") is None

    assert "<authoring-repo>" not in validator.north_star_reference(None)
    assert "<authoring-repo>" not in validator.north_star_reference(tmp_path)

    owning = tmp_path / "owning"
    (owning / "docs").mkdir(parents=True)
    (owning / validator.NORTH_STAR_DOC).write_text("# North Star\n", encoding="utf-8")
    assert validator.NORTH_STAR_DOC in validator.north_star_reference(owning)
    assert validator.NORTH_STAR_DOC not in validator.north_star_reference(tmp_path)

    # The two surfaces cannot share code: the scaffold is a PORTABLE skill script and the
    # validator is a repo-root one, so importing across would make an exported module
    # depend on a file the export does not ship. Agreement is pinned as a value instead,
    # which is the honest mechanism at a boundary that cannot be crossed.
    scaffold = load_script_module(
        "scaffold_retro_artifact_for_north_star_agreement",
        ROOT / "skills/public/retro/scripts/scaffold_retro_artifact.py",
    )
    assert scaffold.NORTH_STAR_DOC == validator.NORTH_STAR_DOC

    # The scaffold half is pinned on its RENDERED OUTPUT in tests/test_retro_scaffold.py,
    # not on its source text: the source legitimately names the discarded spelling in a
    # docstring explaining why it was discarded, and a source-substring assertion here
    # would measure the wrong noun and forbid the explanation.


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


_STUB_RESOLVER = '''
def load_adapter(repo_root):
    return {"valid": True, "data": {"output_dir": "artifacts/retros"}}
'''


def _repo_with_retro_output_dir(tmp_path: Path, output_dir: str) -> Path:
    """A repo whose retro adapter declares ``output_dir``, resolved the real way.

    The stub is written at the path `_retro_resolver_path` actually searches, not
    monkeypatched over it: the fact under test is which directory THIS module binds
    from a repo's own declaration, and patching the lookup would prove only that the
    patched value is used.
    """
    repo = tmp_path / "consumer"
    resolver = repo / "skills" / "public" / "retro" / "scripts" / "resolve_adapter.py"
    resolver.parent.mkdir(parents=True)
    resolver.write_text(_STUB_RESOLVER.replace("artifacts/retros", output_dir), encoding="utf-8")
    (repo / output_dir).mkdir(parents=True)
    return repo


def test_retro_prefix_follows_the_repos_declared_output_dir(tmp_path: Path) -> None:
    repo = _repo_with_retro_output_dir(tmp_path, "artifacts/retros")

    assert retro_validator.retro_artifact_prefix(repo) == "artifacts/retros/"


def test_named_retro_paths_are_not_silently_dropped_under_a_custom_output_dir(
    tmp_path: Path,
) -> None:
    """The reported defect: a `--paths`-scoped run over a consumer's own retro
    reported `Validated 0 retro artifact(s).` and exited 0, because the candidate
    filter keyed on this repo's literal prefix rather than that repo's declared one.
    Zero-validated-and-clean over an artifact the caller NAMED is a fail-quiet, not
    an empty scope."""
    repo = _repo_with_retro_output_dir(tmp_path, "artifacts/retros")
    artifact = repo / "artifacts" / "retros" / "2026-08-17-demo.md"
    artifact.write_text(_ACTIVATED_RETRO, encoding="utf-8")

    named = retro_validator.candidate_paths(
        repo, ["artifacts/retros/2026-08-17-demo.md"], all_artifacts=False
    )
    swept = retro_validator.candidate_paths(repo, [], all_artifacts=True)

    assert named == [artifact]
    assert swept == [artifact]


def test_a_named_missing_retro_is_refused_under_a_custom_output_dir(tmp_path: Path) -> None:
    """`unresolvable_named_paths` refuses a named path the validator OWNS but cannot
    resolve. Bound to a constant, `owned_prefix` owned a directory the consumer never
    writes to, so a caller naming a nonexistent retro there got a clean exit.

    End-to-end through the script rather than an assertion about its source: the fact
    under test is that the runner receives a repo-resolved prefix, and reading the
    argument back out of the file would prove only that the line is written.
    """
    repo = _repo_with_retro_output_dir(tmp_path, "artifacts/retros")

    result = run_script(
        str(ROOT / "scripts" / "validate_retro_artifact.py"),
        "--repo-root",
        str(repo),
        "--paths",
        "artifacts/retros/2026-08-17-never-written.md",
    )

    assert result.returncode != 0, result.stdout
    assert "2026-08-17-never-written.md" in (result.stdout + result.stderr)


def test_verdict_and_announcement_agree_under_a_custom_output_dir(tmp_path: Path) -> None:
    """One run must not refuse an artifact and report no duty in the same breath.

    The half-done migration shipped exactly that: `report_enforcement_scope` moved to
    the adapter while `lesson_evaluator_declared` kept the literal
    `charness-artifacts/retro`, so a consumer declaring `artifacts/retros` got
    "Lesson evaluation floor: inert -- no retro owes a disposition" on stdout and a
    refusal for a missing disposition in the exit code. Running the opt-in command the
    message printed could never fix it, because `init_lesson_ledger.py` writes to the
    directory the verdict half never looked at.
    """
    repo = _repo_with_retro_output_dir(tmp_path, "artifacts/retros")
    (repo / "artifacts" / "retros" / "2026-08-17-demo.md").write_text(
        _ACTIVATED_RETRO, encoding="utf-8"
    )

    result = run_script(
        str(ROOT / "scripts" / "validate_retro_artifact.py"), "--repo-root", str(repo), "--all"
    )

    combined = result.stdout + result.stderr
    announced_no_duty = "floor: inert" in combined or "out of scope" in combined
    refused_for_disposition = result.returncode != 0 and "Lesson evaluation" in combined
    assert not (announced_no_duty and refused_for_disposition), combined
    # The lifecycle cannot address this repo's retros, so the honest pair is:
    # announce the boundary, do not refuse.
    assert announced_no_duty, combined
    assert result.returncode == 0, combined


def test_a_custom_output_dir_repo_is_told_the_floor_cannot_reach_it(tmp_path: Path) -> None:
    """A scoped floor announces the boundary it does not cross.

    This is not fail-open: fail-open is a probe that cannot see the state and guesses
    "no duty". Here the state is established positively -- the repo declares a
    directory and the lifecycle provably cannot address it -- and the run says so,
    including that the opt-in would not change it.
    """
    repo = _repo_with_retro_output_dir(tmp_path, "artifacts/retros")
    (repo / "artifacts" / "retros" / "2026-08-17-demo.md").write_text(
        _ACTIVATED_RETRO, encoding="utf-8"
    )
    ledger_dir = repo / "charness-artifacts" / "retro"
    init_lesson_ledger.init_lesson_ledger(
        repo_root=repo,
        output_dir=ledger_dir,
        summary_path=ledger_dir / "recent-lessons.md",
    )

    result = run_script(
        str(ROOT / "scripts" / "validate_retro_artifact.py"), "--repo-root", str(repo), "--all"
    )

    # NOT refused, and the run says why. Enforcing here was tried and is the defect this
    # scoping replaced: `canonical_retro_citation` refuses any --source-retro outside
    # `charness-artifacts/retro`, and `collect_retro_candidates` globs the same literal,
    # so no score event could ever cite this retro. The only satisfying disposition would
    # be `not-evaluated / missing-start`, forever -- a duty whose sole legal answer is
    # "not evaluated" is the dishonesty the floor's own docstring names.
    assert result.returncode == 0, result.stdout + result.stderr
    assert "out of scope" in (result.stdout + result.stderr)
    assert "would not change that" in (result.stdout + result.stderr)


def test_a_sweep_over_a_missing_output_directory_is_refused_not_reported_clean(
    tmp_path: Path,
) -> None:
    """`--all` IS the corpus audit, so it must not be satisfiable by looking nowhere.

    The permissive adapter read was copied from the debug sibling without the
    directory-existence refusal that made it safe there: `output_dir: [unclosed`
    parses to a plain string with `valid: True`, globs nothing, and printed green
    over the entire corpus.
    """
    repo = _repo_with_retro_output_dir(tmp_path, "artifacts/retros")
    (repo / "artifacts" / "retros").rmdir()

    result = run_script(
        str(ROOT / "scripts" / "validate_retro_artifact.py"), "--repo-root", str(repo), "--all"
    )

    assert result.returncode != 0, result.stdout
    assert "not a clean corpus" in result.stderr
    assert "Validated 0" not in result.stdout


def test_an_untidy_output_dir_does_not_split_the_scaffold_from_the_validator(
    tmp_path: Path,
) -> None:
    """One trailing slash reopened the whole fail-quiet: the scaffold built its write
    path with a raw f-string while the validator normalised, so `retro/` produced
    `retro//x.md`, whose tail then held a `/` and was dropped as a nested archive.
    Canonicalising in the adapter is what makes the two halves agree by construction."""
    resolve_adapter = load_script_module(
        "retro_resolve_adapter_untidy", ROOT / "skills/public/retro/scripts/resolve_adapter.py"
    )
    for untidy in ("charness-artifacts/retro/", "./charness-artifacts/retro", "charness-artifacts//retro"):
        data, errors, _warnings = resolve_adapter.validate_adapter_data(
            {"version": 1, "output_dir": untidy}, tmp_path
        )
        assert errors == [], (untidy, errors)
        assert data["output_dir"] == "charness-artifacts/retro", untidy


def test_an_output_dir_outside_the_repo_is_refused_by_the_adapter(tmp_path: Path) -> None:
    """Every consumer joins this value to the repo root, so a value that resolves
    outside cannot be made to mean anything; owning nothing is the fail-quiet."""
    resolve_adapter = load_script_module(
        "retro_resolve_adapter_escape", ROOT / "skills/public/retro/scripts/resolve_adapter.py"
    )
    for escaping in ("/tmp/retros", "../outside"):
        _data, errors, _warnings = resolve_adapter.validate_adapter_data(
            {"version": 1, "output_dir": escaping}, tmp_path
        )
        assert any("repo-relative" in error for error in errors), (escaping, errors)


def test_prefix_resolution_returns_a_verdict_when_the_consumer_resolver_raises(
    tmp_path: Path,
) -> None:
    """A verdict surface must not traceback. The docstring claimed an unreadable
    adapter kept today's behaviour while only a MISSING one did."""
    output_dir_lib = load_script_module(
        "retro_output_dir_lib_raising", ROOT / "scripts" / "retro_output_dir_lib.py"
    )
    repo = tmp_path / "broken"
    resolver = repo / "skills" / "public" / "retro" / "scripts" / "resolve_adapter.py"
    resolver.parent.mkdir(parents=True)
    resolver.write_text("raise ImportError('skill_runtime_bootstrap.py not found')\n", encoding="utf-8")

    assert (
        output_dir_lib.retro_artifact_prefix(repo)
        == output_dir_lib.DEFAULT_RETRO_ARTIFACT_PREFIX
    )


def test_the_adapter_loader_raises_when_no_resolver_is_reachable(tmp_path: Path, monkeypatch) -> None:
    """`load_retro_adapter` is the version preflight's loader, and its no-resolver arm is
    a RAISE where `retro_artifact_prefix` falls back.

    The two answers are deliberately different. A missing resolver means this validator
    cannot say anything about that repo's adapter, and `unspeakable_version_message`
    reads that raise as "not a version refusal" -- the arm asserted below. Falling back
    to a message here instead would refuse every run in a repo with no retro skill
    installed, which is a legitimate no-op, not an error.

    `_retro_resolver_path` is patched rather than fixtured because it searches THIS
    repo's tree as its second root, which always has a resolver: no temp-directory layout
    can make it return None.
    """
    output_dir_lib = load_script_module(
        "retro_output_dir_lib_no_resolver", ROOT / "scripts" / "retro_output_dir_lib.py"
    )
    verdict = load_script_module(
        "adapter_version_verdict_no_resolver", ROOT / "scripts" / "adapter_version_verdict.py"
    )
    monkeypatch.setattr(output_dir_lib, "_retro_resolver_path", lambda _repo_root: None)

    with pytest.raises(FileNotFoundError, match="no retro resolve_adapter.py reachable"):
        output_dir_lib.load_retro_adapter(tmp_path)

    assert (
        verdict.unspeakable_version_message(
            output_dir_lib.load_retro_adapter, tmp_path, adapter_name="retro-adapter.yaml"
        )
        is None
    )


def test_the_emitted_opt_in_writes_where_the_floor_probe_reads(tmp_path: Path) -> None:
    """The announcement's remedy must be able to close what the announcement describes.

    The verdict and announcement halves were joined, and the opt-in they BOTH name was
    left writing to a literal. For a custom `output_dir` repo that traded a loud false
    refusal for a quiet permanent one: the floor reported inert, the operator ran the
    command it printed, a ledger appeared somewhere the probe never looks, and the
    report said inert again -- forever. No test compared the command's write target
    with the probed directory, which is the same join that caught the sibling defect.
    """
    repo = _repo_with_retro_output_dir(tmp_path, "artifacts/retros")

    result = run_script(
        str(ROOT / "scripts" / "init_lesson_ledger.py"), "--repo-root", str(repo)
    )

    assert result.returncode == 0, result.stderr
    # The LITERAL, matching all 30 readers of this ledger. Writing it to the declared
    # `output_dir` was tried and reverted: the probe then saw it and switched the floor
    # ON while every other lifecycle entry point still opened the literal and raised.
    written = repo / "charness-artifacts" / "retro" / retro_validator.LESSON_LEDGER_FILENAME
    assert written.is_file(), result.stdout

    # ...and the floor still does not reach this repo's retros, because the lifecycle
    # cannot cite or enumerate them. The opt-in is honest about its own limit.
    assert not retro_validator.lesson_evaluator_declared(
        repo / "artifacts" / "retros" / "2026-08-17-demo.md",
        output_dir=repo / "artifacts" / "retros",
    )


def test_a_stray_artifact_still_fails_closed(tmp_path: Path) -> None:
    """Scoping the floor to declared directories must not swallow the blind case."""
    repo = _repo_with_retro_output_dir(tmp_path, "artifacts/retros")
    stray = repo / "somewhere-else" / "2026-08-17-demo.md"
    stray.parent.mkdir(parents=True)
    stray.write_text(_ACTIVATED_RETRO, encoding="utf-8")

    # A stray file is the fail-CLOSED case, not the scoped-out one: the probe cannot
    # see where it is, which is a different answer from a declared directory the
    # lifecycle provably cannot address.
    assert retro_validator.lesson_evaluator_declared(
        stray, output_dir=repo / "artifacts" / "retros"
    )


def test_prefix_falls_back_when_a_resolver_hands_back_a_path_outside_the_repo(
    tmp_path: Path,
) -> None:
    """Every consumer joins this value to the repo root. The adapter refuses an absolute
    or escaping value; if one arrives from an older adapter or a resolver that skips
    validation, owning NOTHING is the fail-quiet this module exists to close."""
    output_dir_lib = load_script_module(
        "retro_output_dir_lib_escaping", ROOT / "scripts" / "retro_output_dir_lib.py"
    )
    repo = tmp_path / "escaping"
    resolver = repo / "skills" / "public" / "retro" / "scripts" / "resolve_adapter.py"
    resolver.parent.mkdir(parents=True)
    resolver.write_text(
        'def load_adapter(repo_root):\n    return {"data": {"output_dir": "/tmp/retros"}}\n',
        encoding="utf-8",
    )

    assert (
        output_dir_lib.retro_artifact_prefix(repo)
        == output_dir_lib.DEFAULT_RETRO_ARTIFACT_PREFIX
    )


def test_no_resolver_in_either_root_yields_no_resolver_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The second root is the installed plugin, so in THIS repo it always resolves.
    Forcing both to miss is the only way to reach the arm, and the arm matters: a repo
    with no retro skill reachable is a no-op, not an error."""
    output_dir_lib = load_script_module(
        "retro_output_dir_lib_norsolver", ROOT / "scripts" / "retro_output_dir_lib.py"
    )
    monkeypatch.setattr(output_dir_lib, "_SCRIPT_REPO_ROOT", tmp_path / "nowhere")

    assert output_dir_lib._retro_resolver_path(tmp_path / "also-nowhere") is None
    assert (
        output_dir_lib.retro_artifact_prefix(tmp_path / "also-nowhere")
        == output_dir_lib.DEFAULT_RETRO_ARTIFACT_PREFIX
    )


def test_a_blank_output_dir_is_left_alone_rather_than_canonicalised(tmp_path: Path) -> None:
    """Nothing to canonicalise and nothing to refuse: a blank value is already handled
    by the callers' own emptiness guards, and rewriting it here would invent a
    directory the repo never declared."""
    resolve_adapter = load_script_module(
        "retro_resolve_adapter_blank", ROOT / "skills/public/retro/scripts/resolve_adapter.py"
    )
    validated = {"output_dir": "   "}
    errors: list[str] = []

    resolve_adapter.canonicalize_output_dir(validated, errors)

    assert validated["output_dir"] == "   "
    assert errors == []
