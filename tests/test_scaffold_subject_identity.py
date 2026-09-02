"""No scaffold family resolves a write path onto another SUBJECT's record.

`write_target_facts` already says whether a write destroys something. It cannot say whether
the something belongs to this author, and that is the gap this suite pins: the debug scaffold
resolved its write path onto an unrelated OPEN investigation, and because the artifact it
would have written carries today's date under today's filename, the date-coherence rule the
quality family earned is inert against it.

The population comes from the TREE, not from a list typed here: `_family_modules()` globs the
scaffold producers, and `test_every_scaffold_family_declares_a_subject_fixture` fails when a
new family appears without one. A hand-written list is what lets a seventh family ship
unguarded while the suite still reports green.

The mismatch itself is constructed per family on purpose. Each family's subject key is its
own, so a single generic fixture would either miss the channel that carries the defect or
manufacture a mismatch the family cannot actually have.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module
from tests.quality_gates.support import ROOT

TODAY = dt.date.today().isoformat()


def _family_modules() -> dict[str, object]:
    modules: dict[str, object] = {}
    for path in sorted(ROOT.glob("skills/public/*/scripts/scaffold_*_artifact.py")):
        family = path.parents[1].name
        modules[family] = import_repo_module(path, f"skills.public.{family}.scripts.{path.stem}")
    return modules


FAMILY_MODULES = _family_modules()


def _seed_adapter(repo: Path, skill_id: str, *, artifact_class: str = "history") -> None:
    """An adapter the skill's own resolver accepts, in the schema it actually reads.

    Copied idiom, not a copied helper: a wrong adapter here does not fail loudly — the
    resolver reports `valid: false`, the producer falls back to inferred defaults, and the
    fixture proves nothing while passing.
    """
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / f"{skill_id}-adapter.yaml").write_text(
        f"version: 1\nrepo: fixture\noutput_dir: charness-artifacts/{skill_id}\nartifact_class: {artifact_class}\n",
        encoding="utf-8",
    )


def _record(repo: Path, relative: str, body: str) -> Path:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _seed_critique(repo: Path) -> tuple[str, dict[str, object]]:
    """The DEFAULT invocation, twice in one day, which is the reachable collision.

    The first version of this fixture passed `--subject "another decision"` so that the
    declared key would disagree with the title-derived path. A bounded round showed that
    certified the wrong thing: the default invocation — the one an author actually runs — had
    `target == invocation` by construction, could never mismatch, and silently overwrote the
    first critique with the second's template.
    """
    _seed_adapter(repo, "critique")
    foreign = f"charness-artifacts/critique/{TODAY}-critique-review.md"
    _record(repo, foreign, "# Critique Review\n\nAn earlier decision under review.\n")
    return foreign, {"title": None, "subject": None}


def _seed_ideation(repo: Path) -> tuple[str, dict[str, object]]:
    foreign = f"charness-artifacts/ideation/{TODAY}-concept-ideation.md"
    _record(repo, foreign, "# Concept Ideation\n\nAn earlier concept.\n")
    return foreign, {"title": None, "subject": None}


def _seed_retro(repo: Path) -> tuple[str, dict[str, object]]:
    """A retro already written today, which the scaffold must not overwrite."""
    _seed_adapter(repo, "retro")
    foreign = f"charness-artifacts/retro/{TODAY}-session-retro.md"
    _record(
        repo,
        foreign,
        "# Session Retro\n\n## Context\n\nAn earlier retro.\n",
    )
    return foreign, {"title": None, "subject": None}


def _seed_quality(repo: Path) -> tuple[str, dict[str, object]]:
    _seed_adapter(repo, "quality")
    foreign = "charness-artifacts/quality/2026-05-06-quality-review.md"
    _record(repo, foreign, "# Quality Review\n")
    (repo / "charness-artifacts/quality/latest.md").symlink_to(Path(foreign).name)
    return foreign, {"title": None, "subject": None}


def _seed_debug(repo: Path) -> tuple[str, dict[str, object]]:
    """The reported instance: the pointer names someone else's OPEN investigation."""
    _seed_adapter(repo, "debug")
    foreign = "charness-artifacts/debug/2026-05-06-someone-elses-investigation.md"
    # A COMPLETE seam-risk declaration, so the planner's risk arms stay out of the way and
    # the branch under test is the ordinary continue-an-open-investigation one. Those arms
    # are deliberately not subject-scoped: an unparseable or open risk interrupt blocks the
    # repo whoever opened it, and repairing that record's own declaration is work in that
    # record rather than this run's investigation written over it.
    _record(
        repo,
        foreign,
        "# Debug Review\n\n## Seam Risk\n\n- Interrupt ID: none\n- Risk Class: none\n- Seam: none\n"
        "- Disproving Observation: none\n- What Local Reasoning Cannot Prove: none\n"
        "- Generalization Pressure: none\n\n## Interrupt Decision\n\n- Resolution: open\n",
    )
    (repo / "charness-artifacts/debug/latest.md").symlink_to(Path(foreign).name)
    return foreign, {"title": None, "subject": None}


SUBJECT_FIXTURES = {
    "critique": _seed_critique,
    "debug": _seed_debug,
    "ideation": _seed_ideation,
    "quality": _seed_quality,
    "retro": _seed_retro,
}


def test_every_scaffold_family_declares_a_subject_fixture() -> None:
    assert set(FAMILY_MODULES) == set(SUBJECT_FIXTURES), (
        "a scaffold family in the tree has no subject-identity fixture; the population is "
        "globbed from skills/public/*/scripts so a new family cannot ship unguarded"
    )
    assert len(FAMILY_MODULES) >= 5, FAMILY_MODULES


@pytest.mark.parametrize("family", sorted(SUBJECT_FIXTURES))
def test_family_refuses_a_write_onto_another_subjects_record(family: str, tmp_path: Path) -> None:
    repo = tmp_path / family
    repo.mkdir()
    foreign, kwargs = SUBJECT_FIXTURES[family](repo)
    payload = FAMILY_MODULES[family].payload_for(repo, **kwargs)

    assert payload["write_artifact_path"] != foreign, payload
    assert payload["write_artifact_effect"] == "create_new_file"
    assert payload["refused_write_artifact_path"] == foreign
    # The refusal names the subject it protected, not just the path: an operator who expected
    # that path has to be able to see WHOSE record it is.
    assert payload["refused_write_artifact_subject_key"]


def test_debug_continuing_its_own_open_investigation_still_writes_in_place(tmp_path: Path) -> None:
    """The negative case, and the reason the mechanism is subject identity rather than dates.

    Continuing an open investigation in place is `debug`'s designed behavior. A rule that
    refuses it would trade one destroyed record for a broken workflow.
    """
    repo = tmp_path / "debug-continue"
    repo.mkdir()
    foreign, _ = _seed_debug(repo)

    payload = FAMILY_MODULES["debug"].payload_for(repo, title=None, subject="someone-elses-investigation")

    assert payload["write_artifact_path"] == foreign
    assert payload["write_artifact_effect"] == "overwrite_existing_content"
    assert payload["write_artifact_subject_match"] == "match"
    assert "refused_write_artifact_path" not in payload


def test_the_debug_planner_does_not_route_a_run_into_the_record_the_scaffold_refused(tmp_path: Path) -> None:
    """The consumer half: a producer's refusal is undone if the plan still names that path.

    `plan_debug_run` is the surface the skill routes to FIRST, and its
    `continue-existing-artifact` mode instructs the author to continue the pointer's record.
    """
    planner = import_repo_module(
        ROOT / "skills/public/debug/scripts/plan_debug_run.py", "skills.public.debug.scripts.plan_debug_run"
    )
    repo = tmp_path / "planner"
    repo.mkdir()
    foreign, _ = _seed_debug(repo)

    # A DECLARED subject that disagrees. An undeclared run is ambiguity, not disagreement, and
    # this planner's fail-safe for ambiguity is deliberate and separately tested: it continues
    # an open investigation rather than abandoning one. What the scaffold refuses either way is
    # handing that record back as a template's write target.
    plan = planner.build_plan(repo, subject="a-different-investigation")

    assert plan["mode"] != "continue-existing-artifact"
    assert plan["next_action"]["write_artifact_path"] != foreign
    assert plan["next_action"]["refused_write_artifact_path"] == foreign
    assert "--subject someone-elses-investigation" in plan["next_action"]["continue_refused_subject_command"]
    # The emitted command reproduces THIS plan's write path, `--subject` included.
    assert "--subject a-different-investigation" in plan["next_action"]["command"]
    # The refused record stays visible as prior memory rather than being excluded as the
    # record this run is continuing — it is not continuing it.
    assert any(incident["path"] == foreign for incident in plan["prior_incidents"]), plan["prior_incidents"]
    # It may be READ as prior memory; what it must not be is framed as the state this run is
    # continuing, which is the reason string the un-updated third copy of the decision emitted.
    assert all("current debugging state" not in read["why"] for read in plan["required_reads"])

    resumed = planner.build_plan(repo, subject="someone-elses-investigation")
    assert resumed["mode"] == "continue-existing-artifact"
    assert resumed["next_action"]["write_artifact_path"] == foreign


def test_only_a_confirmed_match_writes_in_place(tmp_path: Path) -> None:
    """The direction of the doubt, pinned at the owner.

    Three states are not a match, and the first version of this rule wrote in place for two of
    them: it compared against `mismatch`, so an unreadable target subject (`latest.md` as a
    regular file, a legacy undated record name) and an undeclared invocation both continued
    silently. Each of those is a live layout, not a hypothetical.
    """
    lib = import_repo_module(ROOT / "scripts/core/scaffold_artifact_lib.py", "scripts.core.scaffold_artifact_lib")

    unknown = lib.subject_identity_facts(invocation_subject_key="quality-review@2026-08-15", target_subject_key=None)
    undeclared = lib.subject_identity_facts(invocation_subject_key=None, target_subject_key="an-open-investigation")
    mismatch = lib.subject_identity_facts(invocation_subject_key="mine", target_subject_key="theirs")
    match = lib.subject_identity_facts(invocation_subject_key="mine", target_subject_key="mine")

    assert [facts["write_artifact_subject_match"] for facts in (unknown, undeclared, mismatch, match)] == [
        "unknown",
        "undeclared",
        "mismatch",
        "match",
    ]
    assert [lib.writes_in_place(facts) for facts in (unknown, undeclared, mismatch)] == [False, False, False]
    assert lib.writes_in_place(match) is True


def test_two_unreadable_channels_do_not_compose_into_a_match(tmp_path: Path) -> None:
    """Two unavailable subject channels must not compare as a match.

    A multi-channel key whose unavailable channels both compare equal must still
    refuse an in-place write, so two same-day records cannot silently collide.
    """
    lib = import_repo_module(ROOT / "scripts/core/scaffold_artifact_lib.py", "scripts.core.scaffold_artifact_lib")

    assert lib.compose_subject_key("session-retro", None) is None
    assert lib.compose_subject_key(None, "2026-08-15") is None
    assert lib.compose_subject_key("quality-review", "2026-08-15") == "quality-review@2026-08-15"
    unreadable_both = lib.subject_identity_facts(
        invocation_subject_key=lib.compose_subject_key("session-retro", None),
        target_subject_key=lib.compose_subject_key("session-retro", None),
    )
    assert not lib.writes_in_place(unreadable_both)


def test_a_dangling_pointer_does_not_file_todays_work_under_another_records_name(tmp_path: Path) -> None:
    """Judged on the PATH, not on whether a file is there.

    The pointer names an archived review that has been moved away. Nothing is at the path, so
    an existence-first rule reported `no_target` and wrote there — filing today's review under
    a months-old date, the shape the family's own validator refuses after the fact.
    """
    repo = tmp_path / "dangling"
    repo.mkdir()
    _seed_adapter(repo, "quality")
    (repo / "charness-artifacts/quality").mkdir(parents=True)
    (repo / "charness-artifacts/quality/latest.md").symlink_to("2026-05-06-quality-review.md")

    payload = FAMILY_MODULES["quality"].payload_for(repo, title=None)

    assert payload["write_artifact_path"] == f"charness-artifacts/quality/{TODAY}-quality-review.md"
    assert payload["refused_write_artifact_path"] == "charness-artifacts/quality/2026-05-06-quality-review.md"


def test_divert_is_decided_by_the_path_naming_a_subject_not_by_a_mismatch_comparison(tmp_path: Path) -> None:
    """The carve-out that let the hole back in.

    "Something at stake" was spelled `match == mismatch`, which is a second private copy of the
    match test — and `undeclared` is not `mismatch`, so an undeclared run against a dangling
    pointer wrote in place under another investigation's name while the same payload stamped
    `undeclared`. At stake means: something is there, OR the path names a subject.
    """
    lib = import_repo_module(ROOT / "scripts/core/scaffold_artifact_lib.py", "scripts.core.scaffold_artifact_lib")
    repo = tmp_path / "divert"
    (repo / "charness-artifacts/debug").mkdir(parents=True)
    (repo / "charness-artifacts/debug/2026-05-06-theirs.md").write_text("# Theirs\n", encoding="utf-8")

    def divert(write_path: str, invocation: str | None) -> bool:
        return lib.diverts_from_target(
            repo,
            write_path=write_path,
            facts=lib.subject_identity_facts(
                invocation_subject_key=invocation,
                target_subject_key=lib.record_subject_slug(write_path),
            ),
        )

    dangling = "charness-artifacts/debug/2026-05-06-moved-away.md"
    existing = "charness-artifacts/debug/2026-05-06-theirs.md"
    bootstrap = "charness-artifacts/debug/latest.md"

    # Named path, nothing there: still diverts, for every unconfirmed invocation.
    assert divert(dangling, None) and divert(dangling, "mine")
    # Named path holding a record: diverts unless it is confirmed mine.
    assert divert(existing, None) and divert(existing, "mine")
    assert not divert(existing, "theirs")
    # No subject channel and nothing there: nothing at stake, so the bootstrap still writes.
    assert not divert(bootstrap, None) and not divert(bootstrap, "mine")


def test_an_undeclared_run_is_routed_off_a_dangling_pointer(tmp_path: Path) -> None:
    """The concrete failing state two round-2 reviewers derived independently."""
    repo = tmp_path / "dangling-debug"
    repo.mkdir()
    _seed_adapter(repo, "debug")
    (repo / "charness-artifacts/debug").mkdir(parents=True)
    (repo / "charness-artifacts/debug/latest.md").symlink_to("2026-05-06-archived-elsewhere.md")

    payload = FAMILY_MODULES["debug"].payload_for(repo, title=None)

    assert payload["write_artifact_path"] != "charness-artifacts/debug/2026-05-06-archived-elsewhere.md"
    assert payload["refused_write_artifact_path"] == "charness-artifacts/debug/2026-05-06-archived-elsewhere.md"
    assert payload["refused_write_artifact_reason"] == "undeclared"


def test_debug_never_reuses_a_finished_record_by_name(tmp_path: Path) -> None:
    """The reuse repair, carrying the class it repaired.

    Reusing an alternative whose slug matches the declared subject is right for an OPEN record
    and destructive for a finished one — and the helper it was added to is the
    finished-investigation arm.
    """
    repo = tmp_path / "resolved-reuse"
    repo.mkdir()
    _seed_adapter(repo, "debug")
    (repo / "charness-artifacts/debug").mkdir(parents=True)
    _record(repo, "charness-artifacts/debug/latest.md", "# Current\n")
    finished = _record(
        repo,
        f"charness-artifacts/debug/{TODAY}-cache-bug.md",
        "# Debug Review\n\n## Interrupt Decision\n\n- Resolution: resolved\n",
    )

    payload = FAMILY_MODULES["debug"].payload_for(repo, title=None, subject="cache bug")

    assert payload["write_artifact_path"] != str(finished.relative_to(repo))
    assert payload["write_artifact_effect"] == "create_new_file"


def test_quality_refuses_rather_than_routing_onto_an_existing_record(tmp_path: Path) -> None:
    """The family whose contract is "never overwrite a finished review" had no destination check.

    The redirect target is a dated path computed without asking whether anything is at it, so a
    stale pointer plus today's finished review routed straight onto that review while the
    refusal keys named the stale pointer as the thing it had protected.
    """
    repo = tmp_path / "quality-occupied"
    repo.mkdir()
    _seed_adapter(repo, "quality")
    _record(repo, f"charness-artifacts/quality/{TODAY}-quality-review.md", "# Quality Review\n")
    (repo / "charness-artifacts/quality/latest.md").symlink_to("2026-05-06-quality-review.md")
    _record(repo, "charness-artifacts/quality/2026-05-06-quality-review.md", "# Quality Review\n")

    with pytest.raises(SystemExit) as refusal:
        FAMILY_MODULES["quality"].payload_for(repo, title=None)

    assert f"{TODAY}-quality-review.md" in str(refusal.value)


def test_a_declared_subject_against_an_unreadable_target_stops_the_continue_arm(tmp_path: Path) -> None:
    """Ambiguity is the author's to resolve; an unreadable target is not ambiguity on their side.

    The fail-safe that keeps an undeclared run continuing an open investigation must not also
    swallow `unknown`: the author DID say which investigation this is, and the record cannot
    confirm it is that one.
    """
    planner = import_repo_module(
        ROOT / "skills/public/debug/scripts/plan_debug_run.py", "skills.public.debug.scripts.plan_debug_run"
    )
    repo = tmp_path / "legacy-declared"
    repo.mkdir()
    _seed_adapter(repo, "debug")
    (repo / "charness-artifacts/debug").mkdir(parents=True)
    _record(repo, "charness-artifacts/debug/debug-2026-05-06-legacy.md", "# Debug Review\n\n- Resolution: open\n")
    (repo / "charness-artifacts/debug/latest.md").symlink_to("debug-2026-05-06-legacy.md")

    assert planner.build_plan(repo)["mode"] == "continue-existing-artifact"
    declared = planner.build_plan(repo, subject="something-else")
    assert declared["mode"] != "continue-existing-artifact"
    # Every arm that names an existing record carries what the producer declined.
    assert declared["next_action"]["refused_write_artifact_path"]


def test_debug_resumes_its_own_record_even_when_the_pointer_moved(tmp_path: Path) -> None:
    """The SC5 negative case in the arm the first tests missed.

    Alternatives were chosen by existence alone, so an author resuming investigation `x` while
    the pointer sat on `y` was routed PAST their own open `x` record to `x-followup`.
    """
    repo = tmp_path / "resume"
    repo.mkdir()
    _seed_debug(repo)
    mine = _record(
        repo,
        f"charness-artifacts/debug/{TODAY}-my-own-investigation.md",
        "# Debug Review\n\n## Interrupt Decision\n\n- Resolution: open\n",
    )

    payload = FAMILY_MODULES["debug"].payload_for(repo, title=None, subject="my own investigation")

    assert payload["write_artifact_path"] == str(mine.relative_to(repo))
    assert payload["write_artifact_subject_match"] == "match"
