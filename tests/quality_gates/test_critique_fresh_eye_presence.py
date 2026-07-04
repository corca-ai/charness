from __future__ import annotations

from pathlib import Path

from .support import ROOT, run_script

# The fresh-eye typed-presence floor (counterweight-verified: an omitted
# `Fresh-eye satisfaction:` line skipped every distinct-observer check below it
# — the #386 same-observer rubber stamp in file form, reproduced in file
# validator terms). Enforced for artifacts dated on/after
# `FRESH_EYE_PRESENCE_RULE_DATE` (2026-07-05); a dated artifact before that is
# grandfathered — see `scripts/validate_critique_artifacts.py`'s module comment
# for the established `RULE_DATE = landing_day + 1` precedent this mirrors. An
# UNDATABLE artifact is NOT fail-open by default (a second adversarial pass
# found the first cut's fail-open-on-`None` treated "no date" as a permanent
# dodge): it is enforced exactly like post-cutoff unless its filename is one of
# the two named legacy exceptions in `LEGACY_UNDATABLE_CRITIQUE_ARTIFACTS`.


def test_critique_artifact_validator_rejects_missing_fresh_eye_line_post_cutoff(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-05-demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(["# Demo Critique", "", "## Decision Under Review", "", "no fresh-eye line at all", ""]),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/2026-07-05-demo.md",
    )

    assert result.returncode == 1
    assert "has no `Fresh-eye satisfaction:` line" in result.stderr
    assert "parent-delegated" in result.stderr
    assert "nested-delegated" in result.stderr
    assert "blocked <host-signal>" in result.stderr


def test_critique_artifact_validator_rejects_untyped_fresh_eye_value_post_cutoff(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-05-demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(["# Demo Critique", "", "Fresh-Eye Satisfaction: reviewed carefully by me.", ""]),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/2026-07-05-demo.md",
    )

    assert result.returncode == 1
    assert "does not open with one of the typed values" in result.stderr


def test_critique_artifact_validator_rejects_typed_value_with_unedited_todo_remainder(
    tmp_path: Path,
) -> None:
    """Adversarial-review finding: a typed prefix is not enough if the text
    after it is still an unedited `TODO` — that is a stub silently claiming
    delegation, not a real record (the exact loophole the default scaffold
    text used to leave open before this fix)."""
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-05-demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "Fresh-Eye Satisfaction: parent-delegated (TODO confirm the reviewer actually ran before relying on this).",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/2026-07-05-demo.md",
    )

    assert result.returncode == 1
    assert "does not open with one of the typed values" in result.stderr
    assert "unedited `todo`" in result.stderr


def test_critique_artifact_validator_accepts_parent_delegated_post_cutoff(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-05-demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "Fresh-Eye Satisfaction: parent-delegated.",
                "",
                "## Reviewer Tier Evidence",
                "",
                "- **Requested tier**: `high-leverage`",
                "- **Requested spawn fields**: `model=gpt-5.5`",
                "- **Host exposure state**: `requested_fields_sent`",
                "- **Application state**: `fields accepted by spawn call; provider application not independently confirmed`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/2026-07-05-demo.md",
    )

    assert result.returncode == 0, result.stderr


def test_critique_artifact_validator_accepts_nested_delegated_post_cutoff(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-05-demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            ["# Demo Critique", "", "Fresh-Eye Satisfaction: nested-delegated; recursive delegation actually ran.", ""]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/2026-07-05-demo.md",
    )

    assert result.returncode == 0, result.stderr


def test_critique_artifact_validator_accepts_blocked_with_signal_post_cutoff(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-05-demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(
            [
                "# Demo Critique",
                "",
                "Fresh-Eye Satisfaction: blocked.",
                "",
                "host signal: agent-count budget exhausted before the bounded reviewer could be spawned.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/2026-07-05-demo.md",
    )

    assert result.returncode == 0, result.stderr


def test_critique_artifact_validator_grandfathers_missing_line_on_landing_day(
    tmp_path: Path,
) -> None:
    """Dated exactly on the floor's landing day (2026-07-04): grandfathered, not
    enforced — mirrors the established `RULE_DATE = landing_day + 1` shape."""
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-04-demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(["# Demo Critique", "", "## Decision Under Review", "", "no fresh-eye line at all", ""]),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/2026-07-04-demo.md",
    )

    assert result.returncode == 0, result.stderr


def test_critique_artifact_validator_fails_closed_for_new_undatable_artifact(
    tmp_path: Path,
) -> None:
    """No date in the filename or body, and not on the legacy allowlist: this
    is now enforced exactly like post-cutoff, not grandfathered. A NEW artifact
    with no parseable date is itself the anomaly (an author omitting the date
    line/filename convention is not a safe default to trust) — the adversarial
    review's should-fix, replacing the first cut's fail-open-on-`None`."""
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "demo.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(["# Demo Critique", "", "## Decision Under Review", "", "no fresh-eye line at all", ""]),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 1
    assert "has no `Fresh-eye satisfaction:` line" in result.stderr


def test_critique_artifact_validator_grandfathers_legacy_undatable_allowlist_entry(
    tmp_path: Path,
) -> None:
    """The two named legacy filenames stay grandfathered even though undatable
    — a closed, explicit exception, not a fail-open default. Uses the real
    corpus filename so a rename off the allowlist is caught here too."""
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "release-0-55-1-packet.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(
        "\n".join(["# Demo Critique", "", "## Decision Under Review", "", "no fresh-eye line at all", ""]),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/release-0-55-1-packet.md",
    )

    assert result.returncode == 0, result.stderr


def test_critique_scaffold_default_stub_fails_validation_post_cutoff(
    tmp_path: Path,
) -> None:
    """The KEY regression test for the adversarial finding: the scaffold's own
    unedited output — exactly what `skills/public/critique/scripts/
    scaffold_critique_artifact.py` renders, untouched by any author — must NOT
    satisfy the fresh-eye floor once dated post-cutoff. Before the fix, the
    scaffold pre-filled a real typed token (`parent-delegated (TODO ...)`),
    which a same-agent artifact could ship completely unedited and still pass
    — the exact #386 same-observer rubber stamp this floor exists to stop."""
    import sys

    sys.path.insert(0, str(ROOT / "skills" / "public" / "critique" / "scripts"))
    import scaffold_critique_artifact as scaffold

    template = scaffold.render_template(title="Critique Review", date_text="2026-07-05")
    repo = tmp_path / "repo"
    artifact = repo / "charness-artifacts" / "critique" / "2026-07-05-critique-review.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(template, encoding="utf-8")

    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/2026-07-05-critique-review.md",
    )

    assert result.returncode == 1
    assert "does not open with one of the typed values" in result.stderr


def test_live_corpus_critique_artifacts_pass_whole_tree_validation() -> None:
    """Durable regression proof: the fresh-eye typed-presence floor must never
    retroactively refuse the existing corpus (603 artifacts at floor-landing
    time). Runs the validator exactly as the pre-push hook's
    `validate-critique-artifacts` step does, over every checked artifact."""
    repo_root = Path(__file__).resolve().parents[2]
    result = run_script(
        "scripts/validate_critique_artifacts.py",
        "--repo-root",
        str(repo_root),
        "--all",
        "--report-all",
    )
    assert result.returncode == 0, result.stderr
