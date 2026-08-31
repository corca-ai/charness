from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from .support import run_script

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = "skills/public/release/scripts/audit_public_release_narrative.py"


def _seed_fixture(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "charness-artifacts" / "release").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "output_dir: charness-artifacts/release",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return repo


_GOOD_ARTIFACT = """# Release Surface Check
Date: 2026-05-13

## Scope

Advanced `demo` toward release `0.1.0` (tag `v0.1.0`) through the repo-owned release helper.

## Current Version

- previous version: `0.0.9`
- target version: `0.1.0`

## Verification

- quality gate passed before publish.

## Release State

- local release mutation: complete
- branch/tag push: complete
- GitHub release record: created
- public release surface verification: not checked by this helper
- audit narrative: durable record written to `charness-artifacts/release/latest.md`

## Public Release Verification

- pending
"""


def _run_audit(repo: Path, *extra: str):
    return run_script(
        AUDIT_SCRIPT,
        "--repo-root",
        str(repo),
        "--target-tag",
        "v0.1.0",
        *extra,
        cwd=REPO_ROOT,
    )


def test_audit_passes_for_well_formed_artifact(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "passed"
    assert payload["blockers"] == []


def test_audit_blocks_when_tag_is_missing(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    stale = _GOOD_ARTIFACT.replace("(tag `v0.1.0`)", "(tag `v0.0.9`)").replace("v0.1.0", "v0.0.9")
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(stale, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    assert any("target tag `v0.1.0`" in blocker for blocker in payload["blockers"])


def test_audit_blocks_when_required_heading_missing(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    truncated = _GOOD_ARTIFACT.replace("## Public Release Verification\n\n- pending\n", "")
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(truncated, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert any("`## Public Release Verification`" in blocker for blocker in payload["blockers"])


def test_audit_blocks_when_state_ledger_entry_missing(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    without_audit_entry = _GOOD_ARTIFACT.replace(
        "- audit narrative: durable record written to `charness-artifacts/release/latest.md`\n",
        "",
    )
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(without_audit_entry, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert any("audit narrative" in blocker for blocker in payload["blockers"])


def test_audit_blocks_when_artifact_missing(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert any("durable release artifact missing" in blocker for blocker in payload["blockers"])


def test_audit_blocks_notes_file_pointing_at_mutable_ref(tmp_path: Path) -> None:
    """D2 regression: the discriminator was exactly inverted.

    A published note must not point at content that can change after
    publication. The blocker fired only when the ref EQUALED the release tag, so
    the one pointer that could never rot was refused while `main`, a branch, and
    a `raw.githubusercontent.com` link — all of which move under the reader —
    were passed. Ref immutability is the test now, not equality with the tag."""
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")
    for label, link in (
        ("branch main", "https://github.com/example/demo/blob/main/charness-artifacts/release/latest.md"),
        ("raw host", "https://raw.githubusercontent.com/example/demo/main/docs/x.md"),
        ("feature branch", "https://github.com/example/demo/tree/feature-x/docs/"),
    ):
        notes_path = tmp_path / "notes.md"
        notes_path.write_text(f"See {link}\n", encoding="utf-8")

        result = _run_audit(repo, "--notes-file", str(notes_path))

        assert result.returncode == 1, label
        payload = yaml.safe_load(result.stdout)
        assert payload["notes_blockers"], label
        assert any("MUTABLE ref" in blocker for blocker in payload["blockers"]), label


def test_audit_passes_notes_file_pinned_to_an_immutable_ref(tmp_path: Path) -> None:
    """Falsifiable counterpart: a pointer that cannot rot — the release tag or a
    commit sha — is exactly what the notes SHOULD carry, and used to be the only
    thing this audit refused."""
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")
    for label, link in (
        ("release tag", "https://github.com/example/demo/blob/v0.1.0/charness-artifacts/release/latest.md"),
        ("bare version tag", "https://github.com/example/demo/blob/0.1.0/docs/x.md"),
        ("commit sha", f"https://github.com/example/demo/blob/{'a' * 40}/docs/x.md"),
    ):
        notes_path = tmp_path / "notes.md"
        notes_path.write_text(f"See {link}\n", encoding="utf-8")

        result = _run_audit(repo, "--notes-file", str(notes_path))

        assert result.returncode == 0, (label, result.stdout)
        assert yaml.safe_load(result.stdout)["notes_blockers"] == [], label


def test_audit_passes_for_self_contained_notes_file(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")
    notes_path = tmp_path / "notes.md"
    notes_path.write_text(
        "## v0.1.0\n\n- One self-contained bullet describing the change.\n",
        encoding="utf-8",
    )

    result = _run_audit(repo, "--notes-file", str(notes_path))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "passed"
    assert payload["notes_blockers"] == []


def test_audit_blocks_suffixed_release_state_heading_with_empty_ledger(tmp_path: Path) -> None:
    """D1 regression: heading presence and block location disagreed, and the
    disagreement failed open.

    `REQUIRED_HEADINGS` tests `## Release State` as a SUBSTRING, while the block
    reader matched the heading line EXACTLY. So `## Release State (ledger)`
    satisfied the substring test, produced no block, and the early return skipped
    all five ledger entry checks while the audit still reported `passed` — an
    empty ledger publishing green. This gates publish through
    `publish_release_cli.run_narrative_audit`."""
    repo = _seed_fixture(tmp_path)
    artifact = _GOOD_ARTIFACT.replace("## Release State", "## Release State (ledger)")
    # Strip the five ledger entries, keeping the suffixed heading.
    artifact = re.sub(r"(?m)^- (local release mutation|branch/tag push|GitHub release record|"
                      r"public release surface verification|audit narrative):.*\n", "", artifact)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(artifact, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    # All five entries must be reported, not silently skipped.
    assert len([b for b in payload["blockers"] if "missing required entry" in b]) == 5


def test_audit_accepts_a_suffixed_release_state_heading_with_a_full_ledger(tmp_path: Path) -> None:
    """Falsifiable counterpart: a suffixed heading is legitimate authoring, so
    the fix locates it rather than refusing it. The ledger under it is checked."""
    repo = _seed_fixture(tmp_path)
    artifact = _GOOD_ARTIFACT.replace("## Release State", "## Release State (ledger)")
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(artifact, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 0, result.stdout
    assert yaml.safe_load(result.stdout)["status"] == "passed"


def test_audit_does_not_accept_a_fenced_example_ledger_as_the_real_one(tmp_path: Path) -> None:
    """D1's own escape class, one indirection over — and a FALSE PASS at the
    publish boundary.

    `_release_state_block` takes the FIRST matching heading and was fence-blind,
    so an artifact that documents the ledger format in a code fence satisfied all
    five entry checks while its real `## Release State` section below was empty.
    Content rendered as code is shown to the reader, not asserted."""
    repo = _seed_fixture(tmp_path)
    ledger = "\n".join(
        f"- {label}: complete"
        for label in (
            "local release mutation", "branch/tag push", "GitHub release record",
            "public release surface verification", "audit narrative",
        )
    )
    artifact = (
        "# Release Surface Check\n\n## Scope\n\nRelease `0.1.0` (tag `v0.1.0`). The ledger form is:\n\n"
        f"```markdown\n## Release State\n\n{ledger}\n```\n\n"
        "## Verification\n\n- ok\n\n## Release State\n\n(nothing recorded)\n\n"
        "## Public Release Verification\n\n- pending\n"
    )
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(artifact, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert len([b for b in payload["blockers"] if "missing required entry" in b]) == 5


def test_audit_reports_one_coherent_blocker_when_the_state_section_is_absent(tmp_path: Path) -> None:
    """An artifact with no `## Release State` at all must not draw two blockers
    that contradict each other about whether a heading exists."""
    repo = _seed_fixture(tmp_path)
    artifact = re.sub(r"(?ms)^## Release State\n.*?(?=^## Public Release Verification)", "", _GOOD_ARTIFACT)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(artifact, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    state_blockers = [b for b in yaml.safe_load(result.stdout)["blockers"] if "Release State" in b]
    assert len(state_blockers) == 1
    assert "missing section" in state_blockers[0]


def test_audit_notes_ref_classification_matrix(tmp_path: Path) -> None:
    """Both directions of the mutable-ref rule, including the cases the first D2
    fix got wrong: short shas and two-component tags were over-blocked, the
    `refs/tags/` raw form was over-blocked, a `tree/main` link with no path
    escaped entirely, and a fenced install one-liner was refused with advice
    ("pin to the release tag") that is impossible for a third-party repo."""
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")
    notes_path = tmp_path / "notes.md"
    for label, body, should_block in (
        ("short sha", "See https://github.com/o/r/blob/a1b2c3d/docs/x.md", False),
        ("two-part tag", "See https://github.com/o/r/blob/v1.0/docs/x.md", False),
        ("refs/tags raw form", "See https://raw.githubusercontent.com/o/r/refs/tags/v0.1.0/x.md", False),
        ("prerelease tag", "See https://github.com/o/r/blob/v0.1.0-rc1/docs/x.md", False),
        ("fenced install one-liner",
         "```\ncurl https://raw.githubusercontent.com/other/repo/main/install.sh\n```\n", False),
        ("inline-code url", "Run `https://github.com/o/r/blob/main/x.md`\n", False),
        ("releases/tag link", "See https://github.com/o/r/releases/tag/v0.1.0", False),
        ("branch main", "See https://github.com/o/r/blob/main/docs/x.md", True),
        ("tree ref with no path", "See https://github.com/o/r/tree/main", True),
        ("refs/heads raw form", "See https://raw.githubusercontent.com/o/r/refs/heads/main/x.md", True),
        ("markdown link", "See [audit](https://github.com/o/r/blob/main/docs/x.md).", True),
    ):
        notes_path.write_text(body, encoding="utf-8")
        result = _run_audit(repo, "--notes-file", str(notes_path))
        blocked = yaml.safe_load(result.stdout)["notes_blockers"] != []
        assert blocked is should_block, (label, result.stdout)


def test_audit_refuses_a_release_state_mentioned_only_in_prose(tmp_path: Path) -> None:
    """The third ledger world: the phrase is present but never as a heading line.

    `_release_state_block` returns None, so the five entry checks cannot run — and
    returning quietly there is what let an artifact report `passed` over a ledger
    that was never located (D1). It must not draw the plain "missing section"
    blocker either, because the phrase IS there; the blocker has to name why the
    section could not be located and what to do about it."""
    repo = _seed_fixture(tmp_path)
    artifact = (
        "# Release Surface Check\n\n## Scope\n\nRelease `0.1.0` (tag `v0.1.0`).\n\n"
        "## Verification\n\n"
        "- the ## Release State ledger for this publish is recorded in the previous artifact\n\n"
        "## Public Release Verification\n\n- pending\n"
    )
    artifact_path = repo / "charness-artifacts" / "release" / "latest.md"
    artifact_path.write_text(artifact, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    state_blockers = [b for b in yaml.safe_load(result.stdout)["blockers"] if "Release State" in b]
    assert len(state_blockers) == 1
    assert "never checked" in state_blockers[0]
    assert "on its own heading line" in state_blockers[0]

    # Also in-process, so the branch is attributable to this test rather than only
    # to the CLI child process.
    from tests.script_loader import load_script_module

    audit = load_script_module(
        "audit_public_release_narrative_prose",
        REPO_ROOT / "skills" / "public" / "release" / "scripts" / "audit_public_release_narrative.py",
    )
    inprocess = [b for b in audit._audit_artifact(artifact_path, target_tag="v0.1.0") if "Release State" in b]
    assert len(inprocess) == 1
    assert "never checked" in inprocess[0]


# --- Drafted notes that publish never handed over -------------------------------
#
# Reproduced against this repo's own history, not inferred: v2.11.0's notes were
# authored, committed to `charness-artifacts/release/`, and left there while
# publish took the `--generate-notes` default. The published body was one
# `**Full Changelog**` link, so the section amending 2.10.0's now-wrong migration
# instruction reached no operator. Every audit before this one read notes the
# publisher CHOSE to hand over, so none of them could see this.


def _seed_drafted(repo: Path, name: str) -> Path:
    path = repo / "charness-artifacts" / "release" / name
    path.write_text("# demo 0.1.0\n\nSelf-contained notes.\n", encoding="utf-8")
    return path


def test_audit_blocks_when_drafted_notes_exist_but_publish_supplied_none(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")
    _seed_drafted(repo, "2026-05-13-v0.1.0-notes.md")

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    blocker = next(b for b in payload["blockers"] if "drafted notes files match" in b)
    # The refusal names the file AND the flag that resolves it: a blocker that
    # only says "notes exist" sends the publisher back to guess the path.
    assert "2026-05-13-v0.1.0-notes.md" in blocker
    assert "--notes-file" in blocker
    assert payload["drafted_notes"] and "2026-05-13-v0.1.0-notes.md" in payload["drafted_notes"][0]


def test_audit_does_not_block_when_the_drafted_notes_were_supplied(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")
    drafted = _seed_drafted(repo, "2026-05-13-v0.1.0-notes.md")

    result = _run_audit(repo, "--notes-file", str(drafted))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "passed"
    assert payload["blockers"] == []
    # `drafted_notes` reports what discovery FOUND, not what was wrong with it —
    # the draft is still there, and the blocker is what says whether that matters.
    # Emptying it here would make the payload unable to distinguish "no drafts" from
    # "drafts, correctly shipped", and discovery now runs on both branches so that
    # supplying the WRONG file is caught too.
    assert [Path(p).name for p in payload["drafted_notes"]] == ["2026-05-13-v0.1.0-notes.md"]


def test_audit_stays_silent_for_a_repo_that_drafts_no_notes(tmp_path: Path) -> None:
    # `--generate-notes` is a legitimate publish shape. The refusal fires on the
    # observed defect — notes written and then not passed — never on the flag.
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 0, result.stdout + result.stderr
    assert yaml.safe_load(result.stdout)["drafted_notes"] == []


def test_drafted_notes_discovery_matches_the_naming_shapes_in_this_repos_release_dir(tmp_path: Path) -> None:
    """The shapes are READ OFF `charness-artifacts/release/`, not sampled by hand.

    The first version of this test enumerated four shapes and asserted it had
    them all. The directory held a fifth — `2026-07-14-v1-0-7-public-notes.md`,
    dash-separated, used three times — which the dotted-only token missed. A test
    claiming exhaustiveness over a directory it never read is why that shipped,
    so the real directory is the fixture now.
    """
    from tests.script_loader import load_script_module

    audit = load_script_module(
        "audit_public_release_narrative_drafted",
        REPO_ROOT / "skills" / "public" / "release" / "scripts" / "audit_public_release_narrative.py",
    )
    live = sorted(p.name for p in (REPO_ROOT / "charness-artifacts" / "release").glob("*.md"))
    assert live, "the release output_dir is the fixture; an empty one makes this test vacuous"

    repo = _seed_fixture(tmp_path)
    for name in live:
        _seed_drafted(repo, name)
    # Two shapes the live directory does not currently hold, pinned so the
    # bounding rules stay covered if those files are ever pruned.
    # A dash-separated fixture is pinned explicitly: the live archive is the only
    # thing currently covering that shape, and it is exactly the shape the first
    # implementation missed. Pruning the archive must not silently retire it.
    for name in ("2026-07-26-v2.1-notes.md", "2026-07-27-v2.11.3-critique.md", "v3-2-1-notes.md"):
        _seed_drafted(repo, name)

    def found(tag: str) -> list[str]:
        return [p.name for p in audit.find_drafted_notes(repo, "charness-artifacts/release", target_tag=tag)]

    # Dotted, `v`-prefixed, dated -- and the dash-separated shape that was missed.
    assert found("v2.11.0") == ["2026-07-26-v2.11.0-notes.md"]
    assert found("v1.0.7") == ["2026-07-14-v1-0-7-public-notes.md"]
    assert found("v0.63.1") == ["2026-07-09-v0-63-1-notes.md"]
    # Bare `v`-prefixed, and the two prefix forms with no `v` at all.
    assert found("v2.11.2") == ["v2.11.2-notes.md"]
    assert found("v0.56.6") == ["notes-0.56.6.md"]
    # `v2.11.3` must not pick up the critique artifact carrying the same version:
    # the rule is "a notes file for this tag", not "any artifact mentioning it".
    assert found("v2.11.3") == ["notes-2.11.3.md"]
    # The collision an unbounded substring test gets wrong: `2.1` is a prefix of
    # `2.11.0`/`2.11.2`/`2.11.3`, so it would refuse a v2.1 publish over three
    # notes files belonging to other releases.
    assert found("v2.1") == ["2026-07-26-v2.1-notes.md"]
    # A dash-separated release-check artifact carries the version but not the
    # `notes` role word, so the role filter -- not the version token -- excludes it.
    assert "2026-07-22-v2-4-2-release-check.md" not in found("v2.4.2")
    assert found("v3.2.1") == ["v3-2-1-notes.md"]
    # ...and it must not answer for a version it merely CONTAINS. The
    # bounded-substring search that first fixed the dash shape matched
    # `v3-2-1-notes.md` here, because `-2-1-` has a separator on both sides.
    assert "v3-2-1-notes.md" not in found("v2.1")
    # Same class, single-component tag: `14` is a substring of every date-prefixed
    # name in the archive, and a token comparison never sees it as a version.
    assert found("v14") == []
    assert found("v9.9.9") == []


def test_drafted_notes_discovery_refuses_an_empty_version_over_a_real_directory(tmp_path: Path) -> None:
    """The `not version` guard, exercised where it can actually fail.

    Pinned against a POPULATED directory: with an empty output_dir both the
    guarded and unguarded paths return `[]`, so the guard had no coverage. An
    empty version compiles a token that matches nearly any stem, which would turn
    every notes file in the directory into a publish blocker.
    """
    from tests.script_loader import load_script_module

    audit = load_script_module(
        "audit_public_release_narrative_empty_version",
        REPO_ROOT / "skills" / "public" / "release" / "scripts" / "audit_public_release_narrative.py",
    )
    repo = _seed_fixture(tmp_path)
    _seed_drafted(repo, "2026-05-13-v0.1.0-notes.md")
    assert audit.find_drafted_notes(repo, "charness-artifacts/release", target_tag="v0.1.0")

    assert audit.find_drafted_notes(repo, "charness-artifacts/release", target_tag="v") == []
    assert audit.find_drafted_notes(repo, "charness-artifacts/release", target_tag="") == []


def test_drafted_notes_discovery_survives_an_absent_or_unreadable_output_dir(tmp_path: Path) -> None:
    from tests.script_loader import load_script_module

    audit = load_script_module(
        "audit_public_release_narrative_no_dir",
        REPO_ROOT / "skills" / "public" / "release" / "scripts" / "audit_public_release_narrative.py",
    )
    # A repo whose adapter names an output_dir that does not exist yet must not
    # crash the publish preflight on a directory listing.
    assert audit.find_drafted_notes(tmp_path, "charness-artifacts/release", target_tag="v0.1.0") == []

    # An UNREADABLE directory is a DIFFERENT answer and used to be the same one.
    # This assertion previously read `== []` and called the fail-open a pinned
    # platform behavior: `Path.glob` swallows the scandir error, so an
    # `except OSError` arm written here was dead and the old assertion held for
    # the wrong reason. `iterdir` raises, so the guard is reachable and the two
    # states are now distinguishable -- absent stays publishable, unreadable does
    # not, because "no drafted notes" is a claim about contents nobody read.
    blocked = tmp_path / "locked"
    blocked.mkdir()
    (blocked / "v0.1.0-notes.md").write_text("x", encoding="utf-8")
    blocked.chmod(0o000)
    try:
        if _permissions_are_enforced(blocked) is False:
            pytest.skip("filesystem/user does not enforce directory permissions here")
        with pytest.raises(audit.NotesDirectoryUnreadable) as excinfo:
            audit.find_drafted_notes(tmp_path, "locked", target_tag="v0.1.0")
        assert "could not read the drafted-notes directory" in str(excinfo.value)
    finally:
        # Restore in `finally`, including on the skip path: a `Skipped` exception
        # raised inside the old `try` left the directory at 0o000 under tmp_path,
        # which breaks pytest's tmp-dir retention cleanup on later runs.
        blocked.chmod(0o755)


def test_drafted_notes_blocker_names_every_candidate_without_picking_one(tmp_path: Path) -> None:
    """A pre-release draft and a role-suffixed draft are the same shape after the
    version, so the filename cannot settle which belongs to this release.

    The first version emitted one blocker per file, each saying `Pass
    --notes-file <it>`. For tag `v1.2.3` with `v1.2.3-rc1-notes.md` drafted, that
    instructed the operator to publish RELEASE-CANDIDATE notes as the GA body --
    a verdict surface handing out an instruction it cannot support.
    """
    from tests.script_loader import load_script_module

    audit = load_script_module(
        "audit_public_release_narrative_candidates",
        REPO_ROOT / "skills" / "public" / "release" / "scripts" / "audit_public_release_narrative.py",
    )
    repo = _seed_fixture(tmp_path)
    final = _seed_drafted(repo, "v1.2.3-notes.md")
    rc = _seed_drafted(repo, "v1.2.3-rc1-notes.md")

    drafted = audit.find_drafted_notes(repo, "charness-artifacts/release", target_tag="v1.2.3")
    assert [p.name for p in drafted] == ["v1.2.3-notes.md", "v1.2.3-rc1-notes.md"]

    blockers = audit.drafted_notes_blockers(repo, drafted, target_tag="v1.2.3", notes_file=None)

    assert len(blockers) == 1, "one question, not one imperative per candidate"
    assert "v1.2.3-notes.md" in blockers[0] and "v1.2.3-rc1-notes.md" in blockers[0]
    # The remedy must not assert which file is right...
    assert "belongs to this release" in blockers[0]
    # ...and must say the deletion needs committing: publish refuses a dirty
    # worktree, so `rm` alone trades this refusal for a different one.
    assert "COMMIT" in blockers[0]

    # Supplying either candidate discharges it; supplying neither does not.
    assert audit.drafted_notes_blockers(repo, drafted, target_tag="v1.2.3", notes_file=final) == []
    assert audit.drafted_notes_blockers(repo, drafted, target_tag="v1.2.3", notes_file=rc) == []


def test_audit_blocks_when_a_notes_file_other_than_the_draft_is_supplied(tmp_path: Path) -> None:
    """The premise is "the publisher wrote notes and published something else",
    and handing over `latest.md` satisfies it exactly as `--generate-notes` did.

    The first version made the whole arm the `else` of `notes_file is not None`,
    so passing ANY file discharged it."""
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")
    _seed_drafted(repo, "2026-05-13-v0.1.0-notes.md")
    decoy = repo / "charness-artifacts" / "release" / "some-other.md"
    decoy.write_text("Unrelated.\n", encoding="utf-8")

    result = _run_audit(repo, "--notes-file", str(decoy))

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    blocker = next(b for b in payload["blockers"] if "drafted notes files match" in b)
    assert "which is none of them" in blocker
    assert "2026-05-13-v0.1.0-notes.md" in blocker


def test_drafted_notes_blocker_survives_an_absolute_output_dir(tmp_path: Path) -> None:
    """`output_dir` is an unvalidated free string in the release adapter, so an
    absolute one made `relative_to` raise -- after the bump and the pre-push
    gates, stranding a publish over a display string."""
    from tests.script_loader import load_script_module

    audit = load_script_module(
        "audit_public_release_narrative_abs",
        REPO_ROOT / "skills" / "public" / "release" / "scripts" / "audit_public_release_narrative.py",
    )
    outside = tmp_path / "outside"
    outside.mkdir()
    drafted = outside / "v0.1.0-notes.md"
    drafted.write_text("notes", encoding="utf-8")

    blockers = audit.drafted_notes_blockers(
        tmp_path / "repo", [drafted], target_tag="v0.1.0", notes_file=None
    )

    assert len(blockers) == 1
    assert str(drafted) in blockers[0]


def _permissions_are_enforced(path: Path) -> bool:
    """Whether this filesystem/user actually honours a 0o000 directory.

    Root and some filesystems do not, and both new permission tests self-skip
    there -- so in a root CI container neither the fix nor a regression of it is
    observed at all. Recorded rather than left as a silent "tested".
    """
    try:
        list(path.iterdir())
    except OSError:
        return True
    return False


def _load_release_module(name: str, script: str):
    from tests.script_loader import load_script_module

    return load_script_module(name, REPO_ROOT / "skills" / "public" / "release" / "scripts" / script)


def _seed_publishable_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "schema_version: 1\nrepo: t\noutput_dir: rel\ncurrent_pointer: latest.md\n", encoding="utf-8"
    )
    rel = repo / "rel"
    rel.mkdir()
    (rel / "latest.md").write_text("# Release\n\nVersion: v0.1.0\n", encoding="utf-8")
    (rel / "v0.1.0-notes.md").write_text("real notes\n", encoding="utf-8")
    return repo, rel


def test_an_unreadable_output_dir_blocks_publish_at_both_call_sites(tmp_path: Path) -> None:
    """Unreadable is not absent, and both arms have to say so.

    Absent stays publishable -- it is the normal state for a repo that drafts no
    notes. Unreadable is a directory the arm could not look inside, and reporting
    "no drafted notes" for it is a claim about contents nobody read. The audit
    arm also runs AFTER the artifact audit, whose uncaught PermissionError used
    to fire first and hide it in the default layout where `latest.md` lives
    inside `output_dir`.
    """
    audit = _load_release_module("audit_unreadable", "audit_public_release_narrative.py")
    gate = _load_release_module("gate_unreadable", "publish_release_narrative_gate.py")
    repo, rel = _seed_publishable_repo(tmp_path)

    readable = audit.build_payload(repo, target_tag="v0.1.0", notes_file=None)
    assert readable["drafted_notes_established"] is True
    assert readable["drafted_notes"], "the control needs a real drafted note to be meaningful"

    rel.chmod(0o000)
    try:
        if _permissions_are_enforced(rel) is False:
            pytest.skip("filesystem/user does not enforce directory permissions here")

        payload = audit.build_payload(repo, target_tag="v0.1.0", notes_file=None)
        assert payload["status"] == "blocked"
        assert payload["drafted_notes_established"] is False
        blockers = payload["blockers"]
        # A traceback where a verdict belongs, and a wrong word: the artifact may
        # be right there, so "missing" would be false about it.
        assert any("could not stat the durable release artifact" in b for b in blockers), blockers
        assert not any("durable release artifact missing" in b for b in blockers), blockers
        assert any("could not read the drafted-notes directory" in b for b in blockers), blockers

        with pytest.raises(SystemExit) as excinfo:
            gate.run_notes_file_preflight(repo, target_tag="v0.1.0", notes_file=None)
        assert "could not read the drafted-notes directory" in str(excinfo.value)
    finally:
        rel.chmod(0o755)


def test_an_absent_output_dir_stays_publishable(tmp_path: Path) -> None:
    """The half that must NOT change: refusing here would break every repo that
    drafts no notes, and the fastest route around a blocking gate is deleting
    it."""
    audit = _load_release_module("audit_absent", "audit_public_release_narrative.py")
    assert audit.find_drafted_notes(tmp_path, "no-such-dir", target_tag="v0.1.0") == []


def test_the_role_word_stays_narrow_and_says_what_it_still_misses(tmp_path: Path) -> None:
    """The widening that was written here and reverted, pinned as a decision.

    Adding `release` to the recognised role words made a dated
    `<date>-<version>-release-record.md` match inside a directory literally named
    `release` -- and the refusal's remedy tells the operator to "rename or delete
    it and commit that". A verdict surface at an irreversible boundary
    instructing an operator to delete durable evidence is worse than the miss it
    guarded, and the miss was never observed: no draft in this repo's 51-file
    release directory was missed by requiring `notes`.

    The residual is asserted, not implied: a draft with no role word at all is
    still invisible. An allowlist relocates that miss rather than closing it.
    """
    audit = _load_release_module("audit_roles", "audit_public_release_narrative.py")
    notes_dir = tmp_path / "rel"
    notes_dir.mkdir()
    for name in (
        "2026-07-30-v2.13.0-notes.md",
        "2026-07-30-v2.13.0-public-notes.md",
        "2026-07-30-v2.13.0-release-record.md",
        "2026-07-30-v2.13.0-release-check.md",
        "v2.13.0-blockers.md",
        "2026-07-30-v2.13.0.md",
        "2026-07-30-v2.12.0-notes.md",
    ):
        (notes_dir / name).write_text("x", encoding="utf-8")

    found = [path.name for path in audit.find_drafted_notes(tmp_path, "rel", target_tag="v2.13.0")]
    assert found == [
        "2026-07-30-v2.13.0-notes.md",
        "2026-07-30-v2.13.0-public-notes.md",
    ], found
    # Named residual: a role-word-less draft for the target tag is NOT found.
    assert "2026-07-30-v2.13.0.md" not in found

    # The role word is a whole TOKEN, not a substring -- the substring form is
    # what let the reverted `release` widening match a dated release RECORD, and
    # it matches `footnotes`/`denotes` here for the same reason. Position is free
    # on purpose: this repo ships both `v0.55.0-notes.md` and `notes-v0.56.7.md`,
    # so a last-token rule would drop five real drafts.
    for name in ("footnotes-v2.13.0.md", "denotes-v2.13.0.md"):
        (notes_dir / name).write_text("x", encoding="utf-8")
    (notes_dir / "notes-v2.13.0.md").write_text("x", encoding="utf-8")
    widened = [path.name for path in audit.find_drafted_notes(tmp_path, "rel", target_tag="v2.13.0")]
    assert "notes-v2.13.0.md" in widened
    assert "footnotes-v2.13.0.md" not in widened
    assert "denotes-v2.13.0.md" not in widened


def test_an_unreadable_notes_file_is_not_reported_as_missing(tmp_path: Path) -> None:
    """`audit_notes_file` carried the identical unguarded stat/read pair.

    It runs FIRST in the publish preflight, so in the very state the unreadable-
    directory blocker was written for, adding `--notes-file` (the ordinary
    publish shape) turned that new verdict back into a traceback. Reproduced.
    """
    audit = _load_release_module("audit_notes_file_guard", "audit_public_release_narrative.py")
    holder = tmp_path / "held"
    holder.mkdir()
    notes = holder / "v0.1.0-notes.md"
    notes.write_text("# v0.1.0\n\nreal notes\n", encoding="utf-8")
    holder.chmod(0o000)
    try:
        if _permissions_are_enforced(holder) is False:
            pytest.skip("filesystem/user does not enforce directory permissions here")
        blockers = audit.audit_notes_file(notes, target_tag="v0.1.0")
        assert blockers, "an unreadable notes file must produce a blocker, not a traceback"
        assert "could not stat the public release notes file" in blockers[0]
        # The absent-file wording would be false here: the file is right there.
        assert "public release notes file missing" not in blockers[0]
    finally:
        holder.chmod(0o755)


def test_an_undecodable_release_artifact_blocks_instead_of_raising(tmp_path: Path) -> None:
    """`UnicodeDecodeError` subclasses `ValueError`, not `OSError`.

    So the first version of the read guard caught the permission case and let a
    UTF-16 or single-stray-byte artifact traceback out of the publish boundary --
    the same traceback-where-a-verdict-belongs shape, in the function being
    hardened.
    """
    audit = _load_release_module("audit_decode", "audit_public_release_narrative.py")
    repo, rel = _seed_publishable_repo(tmp_path)
    (rel / "latest.md").write_bytes(b"\xff\xfe# Release State\n")

    payload = audit.build_payload(repo, target_tag="v0.1.0", notes_file=None)

    assert any("could not read the durable release artifact" in b for b in payload["blockers"]), payload["blockers"]
    # `status == "blocked"` alone would be VACUOUS here: the seed artifact is
    # missing required sections, so it blocks for unrelated reasons even when the
    # bytes decode. The control below shows the decode failure is what added the
    # blocker above, not the fixture.
    (rel / "latest.md").write_text("# Release\n\nVersion: v0.1.0\n", encoding="utf-8")
    decodable = audit.build_payload(repo, target_tag="v0.1.0", notes_file=None)
    assert not any("could not read the durable release artifact" in b for b in decodable["blockers"]), (
        decodable["blockers"]
    )


def test_an_undecodable_notes_file_blocks_instead_of_raising(tmp_path: Path) -> None:
    """`audit_notes_file`'s read arm, separate from its stat arm.

    The stat guard is exercised by the permission test, which self-skips as
    root; this one needs no permissions, so the read arm stays measured
    everywhere. `UnicodeDecodeError` is a `ValueError`, so an `except OSError`
    here would still traceback out of the publish preflight.
    """
    audit = _load_release_module("audit_notes_decode", "audit_public_release_narrative.py")
    notes = tmp_path / "v0.1.0-notes.md"
    notes.write_bytes(b"\xff\xfe# v0.1.0\n")

    blockers = audit.audit_notes_file(notes, target_tag="v0.1.0")

    assert blockers, "an undecodable notes file must produce a blocker, not a traceback"
    assert "could not read the public release notes file" in blockers[0]
    assert "public release notes file missing" not in blockers[0]

    # Control: a decodable file for the same tag produces no read blocker.
    notes.write_text("# v0.1.0\n\nreal notes\n", encoding="utf-8")
    assert not any(
        "could not read the public release notes file" in b
        for b in audit.audit_notes_file(notes, target_tag="v0.1.0")
    )
