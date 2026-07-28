from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import new_proof_surface_advisory as advisory

# The birth trigger for the evidence-surface class. The 2026-07 hunt established
# that these defects are introduced already broken — written once, never revised —
# so the risk sits at a proof surface's BIRTH. Edit-triggering would be useless:
# 60-163 proof-surface files are touched weekly against a population of ~135.
#
# The load-bearing property is RECALL over the population the advisory exists for,
# pinned below against the hunt's own 30 files. A first cut classified files by
# their text and reached 60%, missing nine `scripts/*_lib.py` verdict modules and
# `check_staged_reversion.py`; measured against 20 hand-labelled non-gates it also
# false-fired on scaffolders and adapters. The classification is now the reader's.

GATE_BODY = '''
def main() -> int:
    findings = collect()
    if not findings:
        return 0
    print("violation: " + str(findings))
    return 1
'''

PLAIN_BODY = '''
def render(rows):
    """Format rows for display."""
    return "\\n".join(str(row) for row in rows)
'''

# Every distinct file named in the 30-defect table of
# charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md.
HUNT_SURFACES = (
    "scripts/helper_provenance_lib.py",
    "scripts/staged_commit_gate_plan.py",
    "scripts/staged_commit_gate_plan_helpers.py",
    "scripts/validate_packaging.py",
    "scripts/check_staged_reversion.py",
    "scripts/check_staged_worktree_consistency.py",
    "scripts/check_export_safe_imports.py",
    "scripts/check_bootstrap_shim_consistency.py",
    "scripts/host_hook_install_lib.py",
    "scripts/post_edit_skill_anchor_guard.py",
    "skills/public/issue/scripts/issue_verify_closeout_body.py",
    "skills/public/issue/scripts/issue_resolution_critique.py",
    "scripts/check_issue_closeout_commit_msg.py",
    "scripts/check_prescribed_skill_executed_lib.py",
    "scripts/critique_reviewer_evidence.py",
    "scripts/validate_critique_artifacts.py",
    "scripts/critique_reviewed_input_binding.py",
    "scripts/artifact_validator.py",
    "skills/public/release/scripts/audit_public_release_narrative.py",
    "skills/public/release/scripts/publish_release_post_create.py",
    "scripts/validate_current_pointer_freshness.py",
    "skills/public/release/scripts/release_observer.py",
    "skills/public/release/scripts/check_real_host_proof.py",
    "skills/public/release/scripts/publish_release_artifact_sections.py",
    "scripts/check_current_pointer_writes.py",
    "scripts/check_mutation_score.py",
    "scripts/check_mutation_run_proof.py",
    "scripts/check_changed_line_mutation_coverage.py",
    "scripts/mutation_changed_files_lib.py",
    "scripts/check_coverage.py",
)


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "."], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=repo, check=True)
    subprocess.run(["git", "branch", "-f", "base"], cwd=repo, check=True)
    return repo


def _write(repo: Path, relpath: str, body: str) -> str:
    target = repo / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return relpath


# --- recall over the population this exists for -----------------------------


@pytest.mark.parametrize("surface", HUNT_SURFACES)
def test_every_hunt_surface_would_be_listed_at_birth(surface: str) -> None:
    """100% of the known-defective population, not 60%. Each miss is the advisory
    silently not firing for exactly the files it was built for."""
    assert advisory.is_proof_surface_path(surface), surface


def test_skills_shared_is_covered(tmp_path) -> None:
    """Omitting `skills/shared/` is audit row D9's own defect: an identical
    violation was caught under scripts/ and skills/public/ and invisible there."""
    assert advisory.is_proof_surface_path("skills/shared/scripts/reviewer_boundary_fingerprint.py")


@pytest.mark.parametrize(
    "path",
    ["tests/test_x.py", "docs/a.md", "scripts/sub/check_x.py", "charness-artifacts/x/y.py"],
)
def test_paths_outside_the_families_are_not_listed(path: str) -> None:
    assert not advisory.is_proof_surface_path(path)


# --- the trigger itself ------------------------------------------------------


def test_a_new_surface_without_a_disposition_is_named(tmp_path, capsys) -> None:
    repo = _repo(tmp_path)
    rel = _write(repo, "scripts/check_thing.py", GATE_BODY)

    record = advisory.advise_new_proof_surface(repo, [rel], base="base")

    assert record["new_surface_candidates"] == [rel]
    assert record["undispositioned"] == [rel]
    assert record["scope"] == advisory.SCOPE_EVALUATED
    err = capsys.readouterr().err
    assert "no recorded disposition" in err
    assert rel in err
    assert "empty/degenerate input still returns PASS" in err


def test_a_new_non_gate_file_is_still_listed_for_the_reader_to_decide(tmp_path, capsys) -> None:
    """The advisory deliberately does not classify. A measured 73%-recall text
    classifier that also false-fires 55% of the time is worse than asking."""
    repo = _repo(tmp_path)
    rel = _write(repo, "skills/public/quality/scripts/render_rows.py", PLAIN_BODY)

    record = advisory.advise_new_proof_surface(repo, [rel], base="base")

    assert record["new_surface_candidates"] == [rel]
    assert "no recorded disposition" in capsys.readouterr().err


def test_editing_an_existing_surface_does_not_fire(tmp_path, capsys) -> None:
    """Firing on edits would make this a permanent nag, i.e. not a trigger."""
    repo = _repo(tmp_path)
    rel = _write(repo, "scripts/check_thing.py", GATE_BODY)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "add gate"], cwd=repo, check=True)
    subprocess.run(["git", "branch", "-f", "base"], cwd=repo, check=True)
    (repo / rel).write_text(GATE_BODY + "\n# later edit\n", encoding="utf-8")

    record = advisory.advise_new_proof_surface(repo, [rel], base="base")

    assert record["new_surface_candidates"] == []
    assert capsys.readouterr().err == ""


# --- dispositions ------------------------------------------------------------


def test_a_disposition_naming_the_path_silences_that_path(tmp_path, capsys) -> None:
    repo = _repo(tmp_path)
    rel = _write(
        repo,
        "scripts/check_thing.py",
        GATE_BODY + "\n# Fresh-eye pass: scripts/check_thing.py — bounded reviewer found none\n",
    )

    record = advisory.advise_new_proof_surface(repo, [rel], base="base")

    assert record["dispositioned"] == [rel]
    assert record["undispositioned"] == []
    assert capsys.readouterr().err == ""


def test_a_recorded_skip_counts_and_stays_in_the_payload(tmp_path, capsys) -> None:
    """Skipping is an accepted answer; skipping SILENTLY is not."""
    repo = _repo(tmp_path)
    rel = _write(
        repo,
        "scripts/check_thing.py",
        GATE_BODY + "\n# Fresh-eye pass: scripts/check_thing.py — skipped, host blocked spawning\n",
    )

    record = advisory.advise_new_proof_surface(repo, [rel], base="base")

    assert record["dispositioned"] == [rel]
    assert record["new_surface_candidates"] == [rel]
    assert capsys.readouterr().err == ""


def test_one_marker_does_not_cover_the_other_surfaces(tmp_path, capsys) -> None:
    """The first cut applied a single slice-wide boolean to every new surface, so
    one line silenced N of them and the record read as if all N were reviewed —
    N-1 quiet skips, the one thing this advisory exists to prevent."""
    repo = _repo(tmp_path)
    covered = _write(
        repo,
        "scripts/check_a.py",
        GATE_BODY + "\n# Fresh-eye pass: scripts/check_a.py — none found\n",
    )
    uncovered = _write(repo, "scripts/validate_b.py", GATE_BODY)
    third = _write(repo, "skills/public/x/scripts/check_c.py", GATE_BODY)

    record = advisory.advise_new_proof_surface(repo, [covered, uncovered, third], base="base")

    assert record["dispositioned"] == [covered]
    assert sorted(record["undispositioned"]) == sorted([uncovered, third])
    err = capsys.readouterr().err
    assert uncovered in err and third in err
    assert "does not cover the others" in err


def test_a_fenced_marker_does_not_count_as_a_disposition(tmp_path, capsys) -> None:
    """Fenced text is shown, not asserted. A critique artifact ABOUT this advisory
    is exactly the document that quotes the marker form; this repo has shipped
    that defect four times."""
    repo = _repo(tmp_path)
    rel = _write(repo, "scripts/check_thing.py", GATE_BODY)
    _write(
        repo,
        "notes.md",
        "Record it like this:\n\n```\nFresh-eye pass: scripts/check_thing.py — none\n```\n",
    )

    record = advisory.advise_new_proof_surface(repo, [rel, "notes.md"], base="base")

    assert record["undispositioned"] == [rel]
    assert "no recorded disposition" in capsys.readouterr().err


def test_a_marker_in_a_modified_tracked_file_counts(tmp_path, capsys) -> None:
    """The channel the advisory actually instructs authors to use — a critique
    artifact — is a MODIFIED tracked file, which exercises the `git diff` branch
    rather than the new-file raw-text branch. The first suite tested only the
    latter."""
    repo = _repo(tmp_path)
    _write(repo, "critique.md", "initial\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "add critique"], cwd=repo, check=True)
    subprocess.run(["git", "branch", "-f", "base"], cwd=repo, check=True)
    rel = _write(repo, "scripts/check_thing.py", GATE_BODY)
    (repo / "critique.md").write_text(
        "initial\n\n- Fresh-eye pass: scripts/check_thing.py — reviewer found none\n", encoding="utf-8"
    )

    record = advisory.advise_new_proof_surface(repo, [rel, "critique.md"], base="base")

    assert record["dispositioned"] == [rel]
    assert capsys.readouterr().err == ""


def test_this_modules_own_documentation_is_not_a_disposition(tmp_path, capsys) -> None:
    """A file that documents the marker form must not count as a use of it."""
    repo = _repo(tmp_path)
    rel = _write(repo, "scripts/check_thing.py", GATE_BODY)
    _write(
        repo,
        "scripts/new_proof_surface_advisory.py",
        "# form: Fresh-eye pass: scripts/check_thing.py — example\n",
    )

    record = advisory.advise_new_proof_surface(
        repo, [rel, "scripts/new_proof_surface_advisory.py"], base="base"
    )

    # The marker inside the self-documenting file does not disposition anything —
    # including itself, which is correctly listed as a candidate in its own right.
    assert record["dispositioned"] == []
    assert rel in record["undispositioned"]
    assert "no recorded disposition" in capsys.readouterr().err


# --- scope: the class this advisory itself triggers on -----------------------


def test_unresolvable_base_reports_not_established_not_an_empty_pass(tmp_path, capsys) -> None:
    """`[]` alone cannot distinguish "added nothing here" from "could not look".
    That ambiguity is class (a)/(d) — the family this advisory exists to trigger
    on — and the first cut shipped it, with a test pinning it as intended."""
    repo = _repo(tmp_path)
    rel = _write(repo, "scripts/check_thing.py", GATE_BODY)

    record = advisory.advise_new_proof_surface(repo, [rel], base="no-such-ref")

    assert record["scope"] == advisory.SCOPE_NOT_ESTABLISHED
    assert record["new_surface_candidates"] == []
    assert capsys.readouterr().err == ""


def test_no_candidate_paths_reports_evaluated(tmp_path, capsys) -> None:
    repo = _repo(tmp_path)

    record = advisory.advise_new_proof_surface(repo, ["docs/x.md"], base="base")

    assert record["scope"] == advisory.SCOPE_EVALUATED
    assert record["new_surface_candidates"] == []
    assert capsys.readouterr().err == ""


def test_an_undecodable_new_file_is_listed_rather_than_dropped(tmp_path, capsys) -> None:
    """UnicodeDecodeError is a ValueError, not an OSError. Uncaught it aborts a
    closeout that would otherwise pass; swallowed it drops the file silently."""
    repo = _repo(tmp_path)
    target = repo / "scripts" / "check_binary.py"
    target.write_bytes(b"# \xff\xfe not utf-8\nreturn 1\n")

    record = advisory.advise_new_proof_surface(repo, ["scripts/check_binary.py"], base="base")

    assert record["new_surface_candidates"] == ["scripts/check_binary.py"]
    assert record["undispositioned"] == ["scripts/check_binary.py"]
    assert "no recorded disposition" in capsys.readouterr().err


def test_attach_puts_the_whole_record_on_the_durable_payload(tmp_path) -> None:
    """stderr scrolls past; a skip that only ever existed on stderr is the silence
    this advisory exists to break."""
    repo = _repo(tmp_path)
    rel = _write(repo, "scripts/check_thing.py", GATE_BODY)
    payload = {"changed_paths": [rel]}

    advisory.attach_new_proof_surface_advisory(payload, repo, base="base")

    record = payload["new_proof_surface_advisory"]
    assert record["new_surface_candidates"] == [rel]
    assert record["undispositioned"] == [rel]
    assert record["scope"] == advisory.SCOPE_EVALUATED
