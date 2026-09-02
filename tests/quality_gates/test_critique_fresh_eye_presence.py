from __future__ import annotations

from pathlib import Path

from .support import ROOT, run_script

# The fresh-eye typed-presence floor (counterweight-verified: an omitted
# `Fresh-eye satisfaction:` line skipped every distinct-observer check below it
# — the #386 same-observer rubber stamp in file form, reproduced in file
# validator terms). Enforced for artifacts dated on/after
# `FRESH_EYE_PRESENCE_RULE_DATE` (2026-07-05); a dated artifact before that is
# grandfathered — see `scripts/review/validate_critique_artifacts.py`'s module comment
# for the established `RULE_DATE = landing_day + 1` precedent this mirrors. An
# UNDATABLE artifact is NOT fail-open by default (a second adversarial pass
# found the first cut's fail-open-on-`None` treated "no date" as a permanent
# dodge): it is enforced exactly like post-cutoff, with no exception at all. This
# floor carried an undatable allowlist naming two artifacts until 2026-07-28, when
# both were shown to be prepare packets `candidate_paths` excludes by content kind
# — an exemption list that excused nothing while reading as though it did.


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
        "scripts/review/validate_critique_artifacts.py",
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
        "scripts/review/validate_critique_artifacts.py",
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
        "scripts/review/validate_critique_artifacts.py",
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
                "- **Requested spawn fields**: `model=gpt-5.6-terra`",
                "- **Host exposure state**: `requested_fields_sent`",
                "- **Application state**: `fields accepted by spawn call; provider application not independently confirmed`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/review/validate_critique_artifacts.py",
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
        "scripts/review/validate_critique_artifacts.py",
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
        "scripts/review/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/2026-07-05-demo.md",
    )

    assert result.returncode == 0, result.stderr


def test_critique_artifact_validator_accepts_round_cap_as_explicit_non_approval(
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
                "Fresh-Eye Satisfaction: accepted-unreviewed-under-round-cap round-2 repair cap; no third review run.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "scripts/review/validate_critique_artifacts.py",
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
        "scripts/review/validate_critique_artifacts.py",
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
        "scripts/review/validate_critique_artifacts.py",
        "--repo-root",
        str(repo),
        "--paths",
        "charness-artifacts/critique/demo.md",
    )

    assert result.returncode == 1
    assert "has no `Fresh-eye satisfaction:` line" in result.stderr


def test_this_floor_has_no_undatable_exemption_and_needs_none(tmp_path: Path) -> None:
    """This floor carried an undatable allowlist naming two filenames, and the test
    that proved the allowlist worked is the reason the dead rows survived a month.

    The fixture it used carried the filename but NOT the
    `charness.critique_prepare_packet` Kind marker, so `candidate_paths` selected
    it — while the real artifacts of those names are prepare packets that
    `candidate_paths` excludes by content kind in every selection mode. The
    exemption branch could not fire for either real file, so the allowlist read as
    two live grandfather decisions while excusing nothing, and its test agreed
    because the test had reconstructed a file the corpus does not contain.

    What is pinned now is the pair of facts that made the rows dead: the real shape
    is excluded before any floor runs, and an undatable artifact that DOES reach the
    floor is enforced with no exception at all.
    """
    repo = tmp_path / "repo"
    critiques = repo / "charness-artifacts" / "critique"
    critiques.mkdir(parents=True)
    no_fresh_eye = ["# Demo Critique", "", "## Decision Under Review", "", "no fresh-eye line at all", ""]

    # The real corpus shape: a prepare packet, undatable, no fresh-eye line. Excluded
    # by content kind, so the run validates nothing and passes on an empty selection.
    (critiques / "release-0-55-1-packet.md").write_text(
        "\n".join(
            ["# Critique Prepare Packet — demo", "", "- **Kind**: `charness.critique_prepare_packet` (v1)", ""]
        ),
        encoding="utf-8",
    )
    packet_result = run_script(
        "scripts/review/validate_critique_artifacts.py", "--repo-root", str(repo),
        "--paths", "charness-artifacts/critique/release-0-55-1-packet.md",
    )
    assert packet_result.returncode == 0, packet_result.stderr

    # A real critique carrying that same allowlisted filename is now enforced: being
    # undatable buys nothing, which is what the allowlist appeared to be about.
    (critiques / "release-0-55-1-packet.md").write_text("\n".join(no_fresh_eye), encoding="utf-8")
    enforced = run_script(
        "scripts/review/validate_critique_artifacts.py", "--repo-root", str(repo),
        "--paths", "charness-artifacts/critique/release-0-55-1-packet.md",
    )
    assert enforced.returncode == 1
    assert "has no `Fresh-eye satisfaction:` line" in enforced.stderr


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
        "scripts/review/validate_critique_artifacts.py",
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
        "scripts/review/validate_critique_artifacts.py",
        "--repo-root",
        str(repo_root),
        "--all",
    )
    assert result.returncode == 0, result.stderr
