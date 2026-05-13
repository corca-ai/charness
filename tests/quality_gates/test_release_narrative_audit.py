from __future__ import annotations

import json
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


def test_audit_blocks_notes_file_pointing_at_mutable_tag_record(tmp_path: Path) -> None:
    repo = _seed_fixture(tmp_path)
    (repo / "charness-artifacts" / "release" / "latest.md").write_text(_GOOD_ARTIFACT, encoding="utf-8")
    notes_path = tmp_path / "notes.md"
    notes_path.write_text(
        "See full audit at https://github.com/example/demo/blob/v0.1.0/charness-artifacts/release/latest.md\n",
        encoding="utf-8",
    )

    result = _run_audit(repo, "--notes-file", str(notes_path))

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert any(
        "mutable source-tree record" in blocker for blocker in payload["blockers"]
    )
    assert payload["notes_blockers"], "notes_blockers should surface the offending pointer"


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
