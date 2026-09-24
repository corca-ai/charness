"""Release-claims evidence: every release claim binds its backing receipt.

A v8.12.0 claims round passed with three advisories that all have the same
shape -- a positive sentence in the prepared record with nothing behind it a
later reader can check:

1. the quality-gate "exited 0" line cited no durable receipt;
2. the `current_release.py` no-drift claim cited no output or receipt, so
   nothing proved the validated tree was the pushed tree;
3. the 8.11.1 -> 8.12.0 bump carried no rationale, and the level itself
   appeared only as two version strings in another section.

These tests pin the three repairs: the record states the receipt or its
absence beside the quality sentence, the no-drift sentence names the validated
commit/tree (and is withheld without that identity), and the bump decision is
a fixed-shape line the next gate can parse.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from types import SimpleNamespace

from .seeding_support import load_module
from .support import ROOT

_RELEASE = ROOT / "skills" / "public" / "release" / "scripts"

ARTIFACT = load_module(
    "publish_release_artifact_claims_evidence",
    _RELEASE / "publish_release_artifact.py",
)
PLAN = load_module(
    "publish_release_plan_claims_evidence",
    _RELEASE / "publish_release_plan.py",
)
CLI = load_module(
    "publish_release_cli_claims_evidence",
    _RELEASE / "publish_release_cli.py",
)

BUMP_LINE_RE = re.compile(
    r"^- Bump: `([^`]+)` -> `([^`]+)`(?: \(`([^`]+)`\))?\.$"
)


def _record(repo: Path, **kwargs) -> str:
    relpath = ARTIFACT.write_release_artifact(
        repo,
        output_dir="charness-artifacts/release",
        package_id="demo",
        previous_version="0.1.0",
        target_version="0.2.0",
        remote="origin",
        branch="main",
        quality_command="./scripts/run-quality.sh",
        release_url=None,
        update_instructions=[],
        **kwargs,
    )
    return (repo / relpath).read_text(encoding="utf-8")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _drift_check(**overrides):
    check = {
        "status": "passed",
        "stage": "post-bump, pre-commit",
        "checked_version": "0.2.0",
        "versioned_surfaces": ["packaging_manifest"],
        "presence_surfaces": [],
        "drift": [],
        "checked_commit": "a" * 40,
        "checked_tree": "b" * 40,
    }
    check.update(overrides)
    return check


def test_quality_sentence_without_receipt_states_the_absence(tmp_path: Path) -> None:
    """An "exited 0" line with no receipt beside it used to read as backed."""
    text = _record(
        tmp_path / "repo", quality_status="exited 0 in 12.0s at `post-bump, pre-commit`"
    )

    assert "exited 0" in text
    assert (
        "- pre-push quality receipt: NOT recorded by this helper invocation, "
        "so the quality sentence above cites no durable receipt." in text
    )


def test_quality_sentence_with_receipt_cites_path_and_sha(tmp_path: Path) -> None:
    text = _record(
        tmp_path / "repo",
        quality_status="exited 0 in 12.0s at `post-claims-review, pre-push`",
        prepush_quality_receipt="charness-artifacts/release/0.2.0-prepush-quality.json",
        prepush_quality_receipt_sha256="c" * 64,
    )

    assert (
        "- pre-push quality receipt: "
        "`charness-artifacts/release/0.2.0-prepush-quality.json` "
        f"(sha256: `{'c' * 64}`)."
    ) in text
    assert "pre-push quality receipt: NOT recorded" not in text


def test_drift_claim_without_validated_identity_is_not_recorded(
    tmp_path: Path,
) -> None:
    """Surfaces without a validated commit are a check report with no subject."""
    text = _record(
        tmp_path / "repo",
        version_drift_check={
            "status": "passed",
            "stage": "post-bump, pre-commit",
            "checked_version": "0.2.0",
            "versioned_surfaces": ["packaging_manifest"],
            "presence_surfaces": [],
            "drift": [],
        },
    )

    assert "Version drift check: NOT recorded by this helper invocation" in text
    assert "reported no version drift" not in text
    assert "Validated tree:" not in text


def test_drift_claim_binds_the_validated_tree(tmp_path: Path) -> None:
    text = _record(tmp_path / "repo", version_drift_check=_drift_check())

    assert "reported no version drift" in text
    assert f"- Validated tree: commit `{'a' * 40}` (tree `{'b' * 40}`)" in text


def test_drift_disposition_records_the_tree_it_validated(
    tmp_path: Path, monkeypatch
) -> None:
    """`ensure_release_surface` stamps WHAT it validated, not just the verdict."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "payload.txt").write_text("seed\n", encoding="utf-8")
    _git(repo, "init", "-b", "main")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    _git(
        repo,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "commit",
        "-m",
        "seed",
    )
    monkeypatch.setattr(
        CLI,
        "build_release_payload",
        lambda root: {
            "versioned_surfaces": ["packaging_manifest"],
            "presence_surfaces": [],
            "drift": [],
        },
    )
    monkeypatch.setattr(CLI, "release_surface_blocker", lambda payload, version: None)

    disposition = CLI.ensure_release_surface(repo, "0.2.0", stage="unit")

    assert disposition["checked_commit"] == _git(repo, "rev-parse", "HEAD")
    assert disposition["checked_tree"] == _git(repo, "rev-parse", "HEAD^{tree}")


def test_bump_decision_line_is_machine_checkable(tmp_path: Path) -> None:
    text = _record(tmp_path / "repo", bump_rationale="minor: new operator capability.")

    section = text.split("## Bump Rationale", 1)[1]
    match = next(
        (m for m in (BUMP_LINE_RE.match(line) for line in section.splitlines()) if m),
        None,
    )
    assert match is not None, "no parseable `- Bump: ...` line in the record"
    assert (match.group(1), match.group(2), match.group(3)) == (
        "0.1.0",
        "0.2.0",
        None,
    )
    assert "> minor: new operator capability." in section


def test_bump_decision_line_carries_the_part(tmp_path: Path) -> None:
    text = _record(tmp_path / "repo", bump_rationale="x", bump_part="minor")

    section = text.split("## Bump Rationale", 1)[1]
    match = next(
        (m for m in (BUMP_LINE_RE.match(line) for line in section.splitlines()) if m),
        None,
    )
    assert match is not None
    assert (match.group(1), match.group(2), match.group(3)) == (
        "0.1.0",
        "0.2.0",
        "minor",
    )


def test_bump_absence_still_records_the_decision(tmp_path: Path) -> None:
    """An unexplained level still states what the level was, parseably."""
    text = _record(tmp_path / "repo", bump_part="minor")

    section = text.split("## Bump Rationale", 1)[1]
    assert "- Bump: `0.1.0` -> `0.2.0` (`minor`)." in section
    assert "Bump rationale: NOT recorded by this helper invocation." in section


def _plan_args(**overrides):
    args = {
        "remote": "origin",
        "publish_current": False,
        "part": None,
        "set_version": None,
        "notes_file": None,
        "bump_rationale": None,
        "execute": False,
    }
    args.update(overrides)
    return SimpleNamespace(**args)


def _adapter():
    return {
        "package_id": "demo",
        "quality_command": "./scripts/run-quality.sh",
        "fresh_checkout_probes": [],
    }


def test_plan_records_how_the_target_version_was_chosen() -> None:
    assert (
        PLAN.build_publish_payload(
            _plan_args(part="minor"),
            _adapter(),
            current_version="0.1.0",
            previous_version="0.1.0",
            next_version="0.2.0",
            branch="main",
            tag_name="v0.2.0",
            title="v0.2.0",
            critique_artifact=None,
        )["bump_part"]
        == "minor"
    )
    assert (
        PLAN.build_publish_payload(
            _plan_args(publish_current=True),
            _adapter(),
            current_version="0.2.0",
            previous_version="0.1.0",
            next_version="0.2.0",
            branch="main",
            tag_name="v0.2.0",
            title="v0.2.0",
            critique_artifact=None,
        )["bump_part"]
        == "publish-current"
    )
    assert (
        PLAN.build_publish_payload(
            _plan_args(set_version="0.2.0"),
            _adapter(),
            current_version="0.1.0",
            previous_version="0.1.0",
            next_version="0.2.0",
            branch="main",
            tag_name="v0.2.0",
            title="v0.2.0",
            critique_artifact=None,
        )["bump_part"]
        == "set-version"
    )
