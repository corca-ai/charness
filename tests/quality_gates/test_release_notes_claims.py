"""Pins for the derived claim surfaces and the notes-versus-tree gate.

The failure under test is recorded, not hypothetical. The prepared `6.0.0` notes
asserted *"twelve public skill scripts still declare one"* over a tree where
the measured answer was zero, one day after the same file had been hand-repaired
for four other false claims. So the OVER-CLAIM direction — notes asserting more
than the tree has — is the direction these tests exist for, and it is asserted
separately from the omission direction rather than folded into "mismatch".

`_fixture_repo` builds a miniature repo rather than measuring this one on
purpose: a pin whose expected value is this tree's current count would go red on
every unrelated commit that adds a skill or a gate, and the first remedy anyone
reaches for is to re-record the number — which is the class under test.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.quality_gates.repo_shapes import replace_with_committed_repo
from tests.script_loader import load_script_module

from .support import ROOT

_RELEASE_SCRIPTS = ROOT / "skills" / "public" / "release" / "scripts"

SURFACES = load_script_module("release_claim_surfaces_under_test", _RELEASE_SCRIPTS / "release_claim_surfaces.py")
CLAIMS = load_script_module("release_notes_claims_under_test", _RELEASE_SCRIPTS / "release_notes_claims.py")
GENERATE = load_script_module("generate_release_notes_under_test", _RELEASE_SCRIPTS / "generate_release_notes.py")
GATE = load_script_module("narrative_gate_claims_under_test", _RELEASE_SCRIPTS / "publish_release_narrative_gate.py")

_ENTRYPOINT = """#!/usr/bin/env python3
import argparse


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("demo", help="a demo subcommand")
    nested = subparsers.add_parser("group").add_subparsers(dest="sub")
    nested.add_parser("inner", help="not a top-level subcommand")
"""

_JSON_DECLARING = """import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--json", action="store_true")
"""

_JSON_ADJACENT = """import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--json-path")
parser.add_argument("--json-out")
"""


def _fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "skills" / "public" / "demo").mkdir(parents=True)
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    (repo / "skills" / "public" / "demo" / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    (repo / "scripts" / "check-demo.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    (repo / "charness").write_text(_ENTRYPOINT, encoding="utf-8")
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/release\n", encoding="utf-8"
    )
    return repo


def _tree(repo: Path) -> object:
    root = repo.resolve()
    allowed = frozenset(
        path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts
    )
    return SURFACES.TrackedReleaseTree(root, allowed)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _write_tracked(repo: Path, rel: str, text: str) -> Path:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _remove_tracked(repo: Path, rel: str) -> None:
    (repo / rel).unlink()


def _derived(repo: Path) -> dict[str, dict[str, object]]:
    return {
        str(entry["id"]): entry
        for entry in SURFACES.derive_surfaces(repo, tracked_tree=_tree(repo))
    }


def _render(repo: Path) -> str:
    return GENERATE.render_block(repo, tracked_tree=_tree(repo))


def _audit(notes: Path, repo: Path) -> list:
    return CLAIMS.audit_notes_file(notes, repo, tracked_tree=_tree(repo))


def _preflight(repo: Path, notes: Path, *, target_tag: str = "v0.1.0", **kwargs) -> None:
    GATE.run_notes_file_preflight(
        repo,
        target_tag=target_tag,
        notes_file=notes,
        tracked_tree=_tree(repo),
        **kwargs,
    )


def test_the_surfaces_measure_the_fixture_tree(tmp_path: Path) -> None:
    derived = _derived(_fixture_repo(tmp_path))

    assert derived["json-declaring-scripts"]["count"] == 0
    assert derived["public-skills"]["items"] == ["demo"]
    assert derived["repo-shell-gates"]["items"] == ["check-demo.sh"]
    # Top-level only. `inner` is declared on a nested subparser, and a flat list
    # that included it would name `charness inner`, which is not an invocation.
    assert derived["charness-subcommands"]["items"] == ["demo", "group"]


def test_all_claim_surfaces_share_one_tracked_tree_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _fixture_repo(tmp_path)
    replace_with_committed_repo(repo)
    calls = 0
    original = SURFACES._repo_file_listing.git_list_repo_files

    def observed(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(SURFACES._repo_file_listing, "git_list_repo_files", observed)

    assert len(SURFACES.derive_surfaces(repo)) == len(SURFACES.SURFACES)
    assert calls == 1


def test_a_json_adjacent_flag_is_not_a_json_declaration(tmp_path: Path) -> None:
    """`--json-path` and `--json-out` are what this tree actually still carries.

    A prefix or substring test counts them as `--json` declarations and produces
    a derivation that AGREES with the false prepared claim. Equality is what made
    the measured answer zero."""
    repo = _fixture_repo(tmp_path)
    _write_tracked(repo, "scripts/adjacent.py", _JSON_ADJACENT)

    assert _derived(repo)["json-declaring-scripts"]["count"] == 0

    _write_tracked(repo, "scripts/real.py", _JSON_DECLARING)
    surface = _derived(repo)["json-declaring-scripts"]
    assert surface["count"] == 1
    assert surface["items"] == ["scripts/real.py"]


def test_a_source_that_does_not_parse_is_declared_unscanned_not_counted_as_zero(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    _write_tracked(repo, "scripts/broken.py", "def (\n")

    surface = _derived(repo)["json-declaring-scripts"]
    assert surface["count"] == 0
    assert any("could not parse" in str(entry) for entry in surface["unscanned"])


def test_generated_notes_over_the_same_tree_produce_no_finding(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "v0.1.0-notes.md"

    GENERATE._do_sync(notes, _render(repo))

    assert _audit(notes, repo) == []


def test_notes_asserting_a_surface_the_tree_does_not_have_are_an_over_claim(tmp_path: Path) -> None:
    """The recorded sentence, in miniature: a digit in prose over a measured zero."""
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "v0.1.0-notes.md"
    GENERATE._do_sync(notes, _render(repo))
    notes.write_text(
        notes.read_text(encoding="utf-8")
        + "\nTwelve scripts still declare it: {{claim:json-declaring-scripts.count=12}}.\n",
        encoding="utf-8",
    )

    findings = _audit(notes, repo)

    assert [finding["kind"] for finding in findings] == ["marker-disagrees"]
    assert findings[0]["direction"] == "over-claim"
    assert findings[0]["surface"] == "json-declaring-scripts"
    assert "the tree says `0`" in str(findings[0]["detail"])


def test_notes_omitting_a_surface_the_tree_has_are_an_under_claim(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "v0.1.0-notes.md"
    GENERATE._do_sync(notes, _render(repo))
    text = notes.read_text(encoding="utf-8")
    start = text.index("<!-- claim-surface: repo-shell-gates -->")
    notes.write_text(text[:start] + text[text.index(CLAIMS.BLOCK_END):], encoding="utf-8")

    findings = _audit(notes, repo)

    assert [finding["kind"] for finding in findings] == ["surface-omitted"]
    assert findings[0]["direction"] == "under-claim"
    assert findings[0]["surface"] == "repo-shell-gates"


def test_a_hand_edited_derived_block_is_caught_with_its_direction(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    _write_tracked(repo, "scripts/real.py", _JSON_DECLARING)
    notes = repo / "charness-artifacts" / "release" / "v0.1.0-notes.md"
    GENERATE._do_sync(notes, _render(repo))

    # The hand-repair that failed twice: edit the block instead of regenerating.
    # Scoped to one chunk — the fixture's other surfaces also measure 1, and a
    # whole-file replace would edit three blocks while claiming to test one.
    text = notes.read_text(encoding="utf-8")
    start = text.index("<!-- claim-surface: json-declaring-scripts -->")
    end = text.index("<!-- claim-surface: charness-subcommands -->")
    notes.write_text(text[:start] + text[start:end].replace("count: 1", "count: 9") + text[end:], encoding="utf-8")

    findings = _audit(notes, repo)

    assert [finding["kind"] for finding in findings] == ["surface-disagrees"]
    assert findings[0]["direction"] == "over-claim"


def test_an_unknown_surface_or_field_is_unresolvable_rather_than_a_mismatch(tmp_path: Path) -> None:
    """A typo'd claim and a contradicted claim are different operator problems.

    Reporting a typo as a mismatch sends the author to re-measure a surface that
    does not exist."""
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "v0.1.0-notes.md"
    GENERATE._do_sync(notes, _render(repo))
    notes.write_text(
        notes.read_text(encoding="utf-8")
        + "\n{{claim:no-such-surface.count=1}} and {{claim:public-skills.median=1}}\n",
        encoding="utf-8",
    )

    findings = _audit(notes, repo)

    assert [finding["kind"] for finding in findings] == ["marker-unknown-surface", "marker-unknown-field"]
    assert {finding["direction"] for finding in findings} == {"unresolvable"}


def test_notes_with_no_derived_block_at_all_are_named_as_such(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "v0.1.0-notes.md"
    notes.write_text("# 0.1.0\n\nEverything is fine.\n", encoding="utf-8")

    findings = _audit(notes, repo)

    assert [finding["kind"] for finding in findings] == ["missing-derived-block"]


def test_an_unterminated_block_is_malformed_rather_than_read_to_end_of_file(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "v0.1.0-notes.md"
    notes.write_text(f"# 0.1.0\n\n{CLAIMS.BLOCK_BEGIN}\n\nstill going\n", encoding="utf-8")

    findings = _audit(notes, repo)

    assert [finding["kind"] for finding in findings] == ["malformed-derived-block"]


def test_a_surface_described_twice_is_refused_rather_than_last_wins(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "v0.1.0-notes.md"
    GENERATE._do_sync(notes, _render(repo))
    text = notes.read_text(encoding="utf-8")
    chunk_start = text.index("<!-- claim-surface: public-skills -->")
    chunk_end = text.index("<!-- claim-surface: repo-shell-gates -->")
    chunk = text[chunk_start:chunk_end]
    notes.write_text(text[:chunk_start] + chunk + chunk + text[chunk_start:][len(chunk):], encoding="utf-8")

    kinds = [finding["kind"] for finding in _audit(notes, repo)]

    assert "duplicate-surface-block" in kinds


def test_sync_appends_a_block_without_destroying_authored_prose(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "v0.1.0-notes.md"
    notes.write_text("# 0.1.0\n\nThe authored part.\n", encoding="utf-8")

    GENERATE._do_sync(notes, _render(repo))

    text = notes.read_text(encoding="utf-8")
    assert "The authored part." in text
    assert _audit(notes, repo) == []


# --- the publish boundary -------------------------------------------------


def test_publish_preflight_refuses_notes_the_tree_contradicts(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "2026-05-13-v0.1.0-notes.md"
    GENERATE._do_sync(notes, _render(repo))
    notes.write_text(
        notes.read_text(encoding="utf-8") + "\n{{claim:public-skills.count=99}}\n", encoding="utf-8"
    )

    with pytest.raises(SystemExit) as excinfo:
        _preflight(repo, notes)

    message = str(excinfo.value)
    assert "over-claim" in message
    assert "public-skills" in message


def test_publish_preflight_refuses_notes_that_were_correct_when_generated(tmp_path: Path) -> None:
    """The recorded failure mode exactly: correct at authoring, stale at publish.

    Notes are generated over a tree that HAS a `--json` declaration, then the
    declaration is removed — the 2026-08-15 migration in miniature. Nothing about
    the notes changed; the tree moved underneath them, and the committed note now
    claims a surface that is gone."""
    repo = _fixture_repo(tmp_path)
    _write_tracked(repo, "scripts/real.py", _JSON_DECLARING)
    notes = repo / "charness-artifacts" / "release" / "2026-05-13-v0.1.0-notes.md"
    GENERATE._do_sync(notes, _render(repo))
    _preflight(repo, notes)

    _remove_tracked(repo, "scripts/real.py")

    with pytest.raises(SystemExit) as excinfo:
        _preflight(repo, notes)

    message = str(excinfo.value)
    assert "over-claim" in message
    assert "json-declaring-scripts" in message


def test_the_opt_out_covers_an_absent_block_and_not_a_contradicted_claim(tmp_path: Path) -> None:
    """Opting out of the requirement is not a licence to publish a false claim."""
    repo = _fixture_repo(tmp_path)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/release\n"
        "require_derived_release_claims: false\n",
        encoding="utf-8",
    )
    notes = repo / "charness-artifacts" / "release" / "2026-05-13-v0.1.0-notes.md"
    notes.write_text("# 0.1.0\n\nNo derived block here.\n", encoding="utf-8")

    _preflight(repo, notes)

    notes.write_text(
        "# 0.1.0\n\nStill {{claim:public-skills.count=99}} skills.\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit):
        _preflight(repo, notes)


def test_the_requirement_is_armed_by_default_so_deleting_the_line_re_arms_it(tmp_path: Path) -> None:
    """Disarm-by-deletion, refused by direction.

    An opt-IN flag is disarmed by deleting one adapter line with nothing red.
    Here the same deletion restores the default and ARMS the gate, so the only
    way to publish unguarded notes is to write the opt-out down."""
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "2026-05-13-v0.1.0-notes.md"
    notes.write_text("# 0.1.0\n\nNo derived block here.\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        _preflight(repo, notes)

    assert "missing-derived-block" in str(excinfo.value)


def _synced_notes(repo: Path, name: str = "2026-05-13-v0.1.0-notes.md") -> Path:
    notes = repo / "charness-artifacts" / "release" / name
    GENERATE._do_sync(notes, _render(repo))
    return notes


def test_publish_preflight_refuses_an_ungrounded_quantity_in_prose(tmp_path: Path) -> None:
    """The containment arm, exercised THROUGH the production caller.

    Its own unit tests call the lint directly, so deleting the one line that
    wires it into the preflight left every test green while a publish accepted
    the recorded sentence. That is the slot-never-reached-from-its-caller shape,
    and this is the test that fails when the wiring goes."""
    repo = _fixture_repo(tmp_path)
    notes = _synced_notes(repo)
    notes.write_text(
        notes.read_text(encoding="utf-8")
        + "\nTwelve public skill scripts still declare one.\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as excinfo:
        _preflight(repo, notes)

    message = str(excinfo.value)
    assert "bare-quantity" in message
    assert "twelve" in message.lower()


def test_publish_preflight_does_not_refuse_on_an_advisory_word_alone(tmp_path: Path) -> None:
    """Honest-limits language must reach publish.

    `only` is real signal and it is reported by the lint, but blocking on it
    refuses the sentence that makes a note honest — and the operator's cheapest
    response is the adapter opt-out, which takes the arm that works with it."""
    repo = _fixture_repo(tmp_path)
    notes = _synced_notes(repo)
    notes.write_text(
        notes.read_text(encoding="utf-8")
        + "\nVisibility is verified only after the release has been published.\n",
        encoding="utf-8",
    )

    _preflight(repo, notes)


def test_the_refusal_names_the_adapter_key_and_the_remedy(tmp_path: Path) -> None:
    """A refusal an operator can only resolve by reading source is a trap.

    The first version printed N blocker lines and never said the generator
    command existed, nor that the requirement is adapter-controlled at all."""
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "2026-05-13-v0.1.0-notes.md"
    notes.write_text("# 0.1.0\n\nNo derived block here.\n", encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        _preflight(repo, notes)

    message = str(excinfo.value)
    assert "generate_release_notes.py" in message
    assert "require_derived_release_claims" in message


def test_the_opt_out_disarms_prose_containment_as_well_as_the_block(tmp_path: Path) -> None:
    """One key, both arms — asserted in BOTH directions so the scope is pinned.

    Neither direction was tested before, so making the opt-out unconditional or
    deleting it changed no assertion."""
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "2026-05-13-v0.1.0-notes.md"
    notes.write_text("# 0.1.0\n\nTwelve scripts still declare one.\n", encoding="utf-8")

    with pytest.raises(SystemExit):
        _preflight(repo, notes)

    (repo / ".agents" / "release-adapter.yaml").write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/release\n"
        "require_derived_release_claims: false\n",
        encoding="utf-8",
    )
    _preflight(repo, notes)


def test_the_claim_arms_run_on_the_resume_lane_too(tmp_path: Path) -> None:
    """The resume lane is the ONLY path that reaches `create_release`.

    A previous revision skipped both arms there, reasoning that the prepared-stop
    window is closed to worktree changes. That reasoning is about the TREE and
    does not transfer to the NOTES: `--notes-file` is a free argument on resume,
    nothing binds it to the file the prepare validated, so a second drafted note
    for the same tag could be handed over and published with nothing reading its
    claims. This is the test that fails if the lane check comes back."""
    repo = _fixture_repo(tmp_path)
    validated = _synced_notes(repo, "2026-05-14-v0.1.0-notes.md")
    _preflight(repo, validated, on_resume=True)

    # A second, stale draft for the same tag: a real candidate as far as the
    # drafted-notes arm is concerned, and never validated by the prepare.
    stale = repo / "charness-artifacts" / "release" / "2026-05-13-v0.1.0-notes.md"
    stale.write_text("# 0.1.0\n\nTwelve scripts still declare one.\n", encoding="utf-8")

    with pytest.raises(SystemExit):
        _preflight(repo, stale, on_resume=True)


def test_the_remedy_is_not_attached_to_an_unrelated_blocker(tmp_path: Path) -> None:
    """The remedy used to be decided by substring-matching rendered blocker text.

    This repo has an audit artifact whose path contains `surface-`, so a note
    linking to it at a mutable ref drew a claims remedy telling the operator to
    re-run the notes generator and offering an opt-out that disarms two arms
    having nothing to do with a stale link."""
    repo = _fixture_repo(tmp_path)
    notes = repo / "charness-artifacts" / "release" / "2026-05-13-v0.1.0-notes.md"
    notes.write_text(
        "# 0.1.0\n\nSee https://github.com/o/r/blob/main/charness-artifacts/audit/"
        "2026-07-28-evidence-surface-triage-sweep.md\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as excinfo:
        _preflight(repo, notes)

    message = str(excinfo.value)
    assert "surface-triage-sweep" in message
    assert GATE.CLAIMS_REMEDY not in message


def test_check_refuses_an_ungrounded_quantity_and_is_not_stricter_than_the_gate(tmp_path: Path) -> None:
    """`--check` is the command the skill's workflow tells an author to run.

    Two regressions it has already had: printing `clean` while running only the
    claim arm, and — once the prose arm was added — refusing every correct note
    for naming its own version in its title, which the publish gate accepts."""
    repo = _fixture_repo(tmp_path)
    notes = _synced_notes(repo)

    clean = GENERATE._do_check(notes, repo, require_git=False, versions=("v0.1.0",))
    assert clean["status"] == "clean"
    assert clean["finding_count"] == 0

    notes.write_text(
        notes.read_text(encoding="utf-8") + "\nTwelve scripts still declare one.\n",
        encoding="utf-8",
    )
    dirty = GENERATE._do_check(notes, repo, require_git=False, versions=("v0.1.0",))
    assert dirty["status"] == "disagrees"
    assert [f["kind"] for f in dirty["narrative_blocking"]] == ["bare-quantity"]


def test_check_reports_an_advisory_without_failing_on_it(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    notes = _synced_notes(repo)
    notes.write_text(
        notes.read_text(encoding="utf-8") + "\nVerified only after publication.\n",
        encoding="utf-8",
    )

    payload = GENERATE._do_check(notes, repo, require_git=False, versions=("v0.1.0",))

    assert payload["status"] == "clean"
    assert [f["kind"] for f in payload["narrative_advisory"]] == ["bare-completeness-word"]


def test_an_items_level_over_claim_is_named_over_claim(tmp_path: Path) -> None:
    """Same count, fabricated member.

    A count-only comparison called this a `contradiction`, so `over_claim_count`
    read 0 over a note naming a surface the tree does not have — the direction
    the release contract singles out."""
    repo = _fixture_repo(tmp_path)
    notes = _synced_notes(repo)
    text = notes.read_text(encoding="utf-8")
    notes.write_text(text.replace("- check-demo.sh", "- check-invented.sh"), encoding="utf-8")

    findings = _audit(notes, repo)

    assert [f["kind"] for f in findings] == ["surface-disagrees"]
    assert findings[0]["direction"] == "over-claim"


def test_an_untracked_file_is_not_counted_into_the_shipped_tree(tmp_path: Path) -> None:
    """A release ships committed content.

    Counting an untracked scratch skill made the mechanism produce the fault it
    exists to refuse: notes synced in that worktree assert a skill the release
    does not contain."""
    repo = _fixture_repo(tmp_path)
    replace_with_committed_repo(repo)
    before = [
        entry["items"]
        for entry in SURFACES.derive_surfaces(repo, require_git=True)
        if entry["id"] == "public-skills"
    ][0]

    scratch = repo / "skills" / "public" / "scratch"
    scratch.mkdir(parents=True)
    (scratch / "SKILL.md").write_text("# scratch\n", encoding="utf-8")

    after = [
        entry["items"]
        for entry in SURFACES.derive_surfaces(repo, require_git=True)
        if entry["id"] == "public-skills"
    ][0]
    assert after == before

    _git(repo, "add", "-A")
    shipped = [
        entry["items"]
        for entry in SURFACES.derive_surfaces(repo, require_git=True)
        if entry["id"] == "public-skills"
    ][0]
    assert "scratch" in shipped
