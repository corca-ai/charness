from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

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


def _run_audit(repo: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "python3",
            AUDIT_SCRIPT,
            "--repo-root",
            str(repo),
            "--target-tag",
            "v0.1.0",
            "--json",
            *extra,
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_audit_passes_for_well_formed_artifact(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    assert payload["blockers"] == []


def test_audit_blocks_when_tag_is_missing(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    stale = _GOOD_ARTIFACT.replace("(tag `v0.1.0`)", "(tag `v0.0.9`)").replace("v0.1.0", "v0.0.9")
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(stale, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert any("target tag `v0.1.0`" in blocker for blocker in payload["blockers"])


def test_audit_blocks_when_required_heading_missing(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    truncated = _GOOD_ARTIFACT.replace("## Public Release Verification\n\n- pending\n", "")
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(truncated, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
    assert any("audit narrative" in blocker for blocker in payload["blockers"])


def test_audit_blocks_when_artifact_missing(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)

    result = _run_audit(repo)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
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
        payload = json.loads(result.stdout)
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
        assert json.loads(result.stdout)["notes_blockers"] == [], label


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
    payload = json.loads(result.stdout)
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
    payload = json.loads(result.stdout)
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
    assert json.loads(result.stdout)["status"] == "passed"


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
    payload = json.loads(result.stdout)
    assert len([b for b in payload["blockers"] if "missing required entry" in b]) == 5


def test_audit_reports_one_coherent_blocker_when_the_state_section_is_absent(tmp_path: Path) -> None:
    """An artifact with no `## Release State` at all must not draw two blockers
    that contradict each other about whether a heading exists."""
    repo = _seed_fixture(tmp_path)
    artifact = re.sub(r"(?ms)^## Release State\n.*?(?=^## Public Release Verification)", "", _GOOD_ARTIFACT)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(artifact, encoding="utf-8")

    result = _run_audit(repo)

    assert result.returncode == 1
    state_blockers = [b for b in json.loads(result.stdout)["blockers"] if "Release State" in b]
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
        blocked = json.loads(result.stdout)["notes_blockers"] != []
        assert blocked is should_block, (label, result.stdout)
