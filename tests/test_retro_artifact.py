from __future__ import annotations

from pathlib import Path

from tests.quality_gates.support import run_script

_PRELUDE = "# Session Retro: Demo\nDate: 2026-05-23\nMode: session\n\n## Waste\n\n- something\n\n"


def _seed(repo: Path, body: str, name: str = "2026-05-23-demo.md") -> Path:
    artifact = repo / "charness-artifacts" / "retro" / name
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(body, encoding="utf-8")
    return artifact


def test_retro_sibling_search_accepts_followup(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Sibling Search\n\n"
        + "- same layer: skills/public/x/SKILL.md:10 | decision: valid follow-up outside the slice | proof: static scan | follow-up: https://github.com/x/y/issues/9\n\n"
        + "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_sibling_search_accepts_trivial_short_circuit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Sibling Search\n\n"
        + "- n/a — trivial fix; no plausible siblings\n\n"
        + "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_sibling_search_rejects_followup_without_identifier(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Sibling Search\n\n"
        + "- abstraction up: scripts/foo.py:1 | decision: valid follow-up outside the slice | proof: static scan\n\n"
        + "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "follow-up:" in result.stderr
    assert "abstraction up: scripts/foo.py:1" in result.stderr


def test_retro_sibling_search_rejects_bare_deferred(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        _PRELUDE
        + "## Sibling Search\n\n"
        + "- same layer: scripts/foo.py:1 | decision: valid follow-up outside the slice | proof: static | follow-up: deferred\n\n"
        + "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "follow-up:" in result.stderr


def test_retro_sibling_search_is_opt_in(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = _PRELUDE + "## Next Improvements\n\n- workflow: do better\n\n## Persisted\n\nPersisted: yes path\n"
    _seed(repo, body)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_validator_skips_generated_digest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    # recent-lessons.md is generated; a stray bad sibling block in it must not gate.
    body = (
        "# Recent Lessons\n\n## Sibling Search\n\n"
        + "- same layer: a:1 | decision: valid follow-up outside the slice | proof: x\n"
    )
    _seed(repo, body, name="recent-lessons.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr
    assert "Validated 0 retro artifact(s)." in result.stdout


def test_retro_validator_no_artifacts_passes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_persisted_form_rejects_future_legacy_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n"
        "## Persisted\n\nPersisted: yes path\n"
    )
    _seed(repo, body, name="2026-06-25-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "`## Persisted` has invalid persisted status" in result.stderr


def test_retro_persisted_form_rejects_future_missing_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n"
    )
    _seed(repo, body, name="2026-06-25-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "`## Persisted` must state" in result.stderr


def test_retro_persisted_form_accepts_future_canonical_shape(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-06-25-demo.md\n"
    )
    _seed(repo, body, name="2026-06-25-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


_NORTH_STAR_TAIL = (
    "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-08-05-demo.md\n"
)


def test_retro_north_star_section_is_required_after_the_rule_date(tmp_path: Path) -> None:
    """Every retro consults the design standard and records what it found.

    Prose asking for it was not enough: two consecutive retros shipped without a
    facet mapping and the operator asked twice, which is the recurrence that
    earned a floor.
    """
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-08-05\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n" + _NORTH_STAR_TAIL
    )
    _seed(repo, body, name="2026-08-05-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "`## North Star Alignment`" in result.stderr


def test_retro_north_star_section_rejects_an_untouched_placeholder(tmp_path: Path) -> None:
    """The scaffold seeds a TODO; leaving it is the same as omitting the section."""
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-08-05\nMode: session\n\n"
        "## North Star Alignment\n\nTODO read the standard and record what it says.\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n" + _NORTH_STAR_TAIL
    )
    _seed(repo, body, name="2026-08-05-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "`## North Star Alignment`" in result.stderr


def test_retro_north_star_section_accepts_real_content(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-08-05\nMode: session\n\n"
        "## North Star Alignment\n\n- P1 held: the slice was reversible throughout.\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n" + _NORTH_STAR_TAIL
    )
    _seed(repo, body, name="2026-08-05-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_north_star_section_grandfathers_earlier_retros(tmp_path: Path) -> None:
    """Landing day plus one, so artifacts frozen before the decision are not refused.

    Three same-day retros predate this rule; refusing them retroactively would
    punish authors for a decision taken after they wrote.
    """
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-08-02\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-08-02-demo.md\n"
    )
    _seed(repo, body, name="2026-08-02-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_validator_uses_changed_path_discovery(tmp_path: Path) -> None:
    from tests.quality_gates.repo_shapes import install_committed_repo

    repo = install_committed_repo(tmp_path / "repo", {"README.md": "seed\n"})
    _seed(
        repo,
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Next Improvements\n\n- workflow: do better\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-06-25-demo.md\n",
        name="2026-06-25-demo.md",
    )

    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "Validated 1 retro artifact(s)." in result.stdout


def test_retro_reports_every_rule_violation_in_one_pass(tmp_path: Path) -> None:
    """A retro breaking two DISTINCT rules names both, not just the first.

    validate_retro_artifact chains four independent checks; before the one-pass
    wiring, a two-rule draft cost two gate runs to discover.
    """
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Waste\n\n- something\n\n"
        # invalid disposition form (prose, not one of the accepted forms) AND a
        # malformed Persisted line -- two DISTINCT rules, so the count is 2.
        "## Next Improvements\n\n- workflow: do better\n  - Disposition: prose only\n\n"
        "## Persisted\n\nPersisted: yes\n"
    )
    _seed(repo, body, name="2026-06-25-demo.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    # Pin the COUNT, not just the phrase: "rule violation(s):" is emitted for a
    # count of 1 too, so a bare substring assert passes vacuously the moment one
    # of the two rules stops firing.
    assert "2 retro artifact rule violation(s):" in result.stderr
    assert "disposition line(s) in an invalid form" in result.stderr
    assert "Persisted:" in result.stderr


def test_retro_reports_every_failing_artifact_in_one_pass(tmp_path: Path) -> None:
    """Two bad artifacts in one batch both get named, not just the first.

    Aborting on the first bad artifact hid the rest of a multi-artifact batch
    behind one edit -- the same one-per-run tax at the batch level.
    """
    repo = tmp_path / "repo"
    bad = (
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Waste\n\n- something\n\n"
        "## Persisted\n\nPersisted: yes\n"
    )
    _seed(repo, bad, name="2026-06-25-first.md")
    _seed(repo, bad.replace("2026-06-25", "2026-06-26"), name="2026-06-26-second.md")
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "2026-06-25-first.md" in result.stderr
    assert "2026-06-26-second.md" in result.stderr
    assert "scaffold_retro_artifact.py" in result.stderr


def test_retro_fail_fast_stops_at_the_first_failing_artifact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    bad = (
        "# Session Retro: Demo\nDate: 2026-06-25\nMode: session\n\n"
        "## Waste\n\n- something\n\n"
        "## Persisted\n\nPersisted: yes\n"
    )
    _seed(repo, bad, name="2026-06-25-first.md")
    _seed(repo, bad.replace("2026-06-25", "2026-06-26"), name="2026-06-26-second.md")
    result = run_script(
        "scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all", "--fail-fast"
    )
    assert result.returncode == 1
    assert "2026-06-26-second.md" not in result.stderr
    # Absence alone is not enough: fail-fast must still say WHICH retro failed.
    # Retro rule messages never embed the path, so an unlabeled re-raise would
    # report a violation with no file to open.
    assert "2026-06-25-first.md" in result.stderr


def test_retro_rejects_a_malformed_recurrence_class_slug(tmp_path: Path) -> None:
    """A typo'd tag must be loud, not silently truncated to a different class.

    `recurrence-class: Bad_Slug!` parses to the class `bad` under a prefix match,
    so an unvalidated typo would create a WRONG concept identity -- worse than an
    untagged lesson, because the author believes the grouping is working.
    """
    repo = tmp_path / "repo"
    _seed(
        repo,
        "# Session Retro: Demo\nDate: 2026-07-27\nMode: session\n\n"
        "## Waste\n\n- something (recurrence-class: Bad_Slug!)\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-07-27-demo.md\n",
        name="2026-07-27-demo.md",
    )
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 1
    assert "malformed `recurrence-class:` tag(s)" in result.stderr
    assert "Bad_Slug!" in result.stderr


def test_retro_accepts_a_well_formed_recurrence_class_and_ignores_prose(tmp_path: Path) -> None:
    """Prose ABOUT recurrence classes is not a tag; only `token:` is scanned."""
    repo = tmp_path / "repo"
    _seed(
        repo,
        "# Session Retro: Demo\nDate: 2026-07-27\nMode: session\n\n"
        "## Waste\n\n"
        "- a recurrence-class that has bitten K times must carry a mechanism\n"
        "- batch the edits (recurrence-class: derived-surface-batching)\n\n"
        "## Persisted\n\nPersisted: yes: charness-artifacts/retro/2026-07-27-demo.md\n",
        name="2026-07-27-demo.md",
    )
    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")
    assert result.returncode == 0, result.stderr


def test_retro_body_date_cannot_backdate_a_currently_dated_file(tmp_path: Path) -> None:
    """The sibling C2 left behind: the retro floors read the body `Date:` FIRST and
    fell back to the filename only when it was absent.

    Every floor here grandfathers on `date < RULE_DATE`, so whichever channel reads
    EARLIER buys the exemption — and the body line is author-written while the
    filename is what the scaffold and the directory listing show. One `Date:` line
    took a retro out of the disposition-form, recurrence-lineage and persisted-form
    floors at once. The rule is now the LATER of the two channels, so an artifact is
    exempt only when both agree it is old.
    """
    repo = tmp_path / "repo"
    body = (
        "# Session Retro: Demo\nDate: 2026-01-01\nMode: session\n\n"
        "## Waste\n\n- something\n\n"
        "## Next Improvements\n\n- memory: remember this\n\n"
        "## Persisted\n\nPersisted: sure\n"
    )
    _seed(repo, body, name="2026-07-27-backdated.md")

    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")

    # Under the old body-first `or`, the 2026-01-01 line put this file before every
    # RULE_DATE and the run exited 0 over a malformed `Persisted:` line.
    assert result.returncode == 1, result.stdout + result.stderr
    assert "invalid persisted status" in result.stderr


def test_retro_genuinely_old_on_both_channels_stays_grandfathered(tmp_path: Path) -> None:
    """Falsifiable counterpart. Taking the LATER date must not un-grandfather the
    frozen historical corpus: when body and filename agree the retro is old, the
    date-gated floors stay off. A filename-only date must keep working too, because
    retros predating the `Date:` header convention carry no body line at all."""
    repo = tmp_path / "repo"
    loose = (
        "## Waste\n\n- something\n\n"
        "## Next Improvements\n\n- memory: remember this\n\n"
        "## Persisted\n\nPersisted: sure\n"
    )
    _seed(repo, "# Session Retro: Demo\nDate: 2026-01-01\nMode: session\n\n" + loose,
          name="2026-01-01-both-old.md")
    _seed(repo, "# Session Retro: Demo\nMode: session\n\n" + loose, name="2026-01-02-filename-only.md")

    result = run_script("scripts/validate_retro_artifact.py", "--repo-root", str(repo), "--all")

    assert result.returncode == 0, result.stdout + result.stderr
