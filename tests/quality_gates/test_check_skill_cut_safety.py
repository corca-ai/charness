from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import check_skill_cut_safety as csafety

from .git_fixture_support import init_git_repo

SKILL_REL = "skills/public/demo/SKILL.md"
CORE_PIN = "Always prefer the primary source over a cached summary."
SEDIMENT = "This sentence is pure sediment with no behavioral effect at all."
MOVABLE = "Detail that has outgrown the body and belongs in a reference home."


def _run(repo: Path, *args: str) -> None:
    subprocess.run(list(args), cwd=repo, check=True, capture_output=True, text=True)


def _commit(repo: Path, message: str) -> None:
    _run(repo, "git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", message)


def _seed_repo(repo: Path) -> Path:
    repo.mkdir()
    init_git_repo(repo)
    skill_dir = repo / "skills" / "public" / "demo"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n# Demo\n\n"
        f"{CORE_PIN}\n"
        f"{SEDIMENT}\n"
        f"{MOVABLE}\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "detail.md").write_text("# Detail\n\nUnrelated note.\n", encoding="utf-8")
    (repo / "tests").mkdir()
    _run(repo, "git", "add", "-A")
    _commit(repo, "base")
    return skill_dir


def _patch_pins(monkeypatch, core=(), package=()) -> None:
    monkeypatch.setattr(csafety._contracts, "CORE_CONTRACTS", {SKILL_REL: tuple(core)})
    monkeypatch.setattr(csafety._contracts, "PACKAGE_CONTRACTS", {SKILL_REL: tuple(package)})


def test_core_contract_break_blocks(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(CORE_PIN, "Primary source is usually nicer."), encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "blocked"
    [skill] = report["skills"]
    kinds = {b["kind"] for b in skill["blocks"]}
    assert "core-contract" in kinds


def test_reference_home_gap_is_review_not_block(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])  # pin survives; only sediment removed
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(SEDIMENT + "\n", ""), encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "review"  # no contract/test pin broke -> exit 0
    [skill] = report["skills"]
    assert not skill["blocks"]
    assert any(SEDIMENT[:30] in r["phrase"] for r in skill["reviews"])


def test_sprawl_split_to_reference_is_lossless_clean(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    # Move the movable line OUT of the body and INTO a reference home (the sprawl cure).
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(MOVABLE + "\n", ""), encoding="utf-8")
    detail = skill_dir / "references" / "detail.md"
    detail.write_text(detail.read_text() + f"\n{MOVABLE}\n", encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    [skill] = report["skills"]
    assert not skill["blocks"]
    # The moved line survives in the reference, so it is NOT a reference-home gap.
    assert not any(MOVABLE[:30] in r["phrase"] for r in skill["reviews"])


def test_package_pin_may_move_to_reference(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN], package=[MOVABLE])
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(MOVABLE + "\n", ""), encoding="utf-8")
    detail = skill_dir / "references" / "detail.md"
    detail.write_text(detail.read_text() + f"\n{MOVABLE}\n", encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    [skill] = report["skills"]
    # A package pin that moved to a reference still survives the package -> no break.
    assert not any(b["kind"] == "package-contract" for b in skill["blocks"])


def test_test_literal_pin_blocks(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch)  # no contract pins; isolate the test-literal signal
    (repo / "tests" / "test_demo.py").write_text(
        f'def test_demo_pins(text):\n    assert "{SEDIMENT}" in text\n', encoding="utf-8"
    )
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(SEDIMENT + "\n", ""), encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "blocked"
    [skill] = report["skills"]
    assert any(b["kind"] == "test-pin" for b in skill["blocks"])


def test_test_pin_surviving_elsewhere_not_blocked(tmp_path: Path, monkeypatch) -> None:
    # A test literal that lands on a removed line but still survives elsewhere in the
    # body is NOT a real break (`assert X in skill_text` still passes) -> not a BLOCK.
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text() + f"\n{SEDIMENT}\n", encoding="utf-8")  # 2nd copy
    _run(repo, "git", "add", "-A")
    _commit(repo, "two-copy")
    (repo / "tests" / "test_demo.py").write_text(
        f'def test_demo_pins(text):\n    assert "{SEDIMENT}" in text\n', encoding="utf-8"
    )
    # Remove only the first copy; the literal survives at the appended copy.
    skill_md.write_text(skill_md.read_text().replace(SEDIMENT + "\n", "", 1), encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    [skill] = report["skills"]
    assert not any(b["kind"] == "test-pin" for b in skill["blocks"])


def test_clean_when_nothing_removed(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text() + "\nA purely additive trailing line of guidance.\n", encoding="utf-8")

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "clean"


def test_deleted_skill_md_forces_review_not_silent_clean(tmp_path: Path, monkeypatch) -> None:
    # North-star P5 (finding 3): a maximal cut (deleting the whole SKILL.md) must
    # not structurally escape this checker -- `changed_skill_md` filters
    # `code != "D"`, so without the deletion pass this previously reported "clean".
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    (skill_dir / "SKILL.md").unlink()

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "review"
    [skill] = report["skills"]
    assert skill["path"] == SKILL_REL
    assert any(r["kind"] == "deleted-surface" for r in skill["reviews"])
    assert not skill["blocks"]


def test_deleted_reference_home_forces_review(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    (skill_dir / "references" / "detail.md").unlink()

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "review"
    paths = {s["path"] for s in report["skills"]}
    assert "skills/public/demo/references/detail.md" in paths


def test_deleted_shared_reference_forces_review(tmp_path: Path, monkeypatch) -> None:
    # Fresh-eye finding: skills/shared/references/*.md is a cross-skill contract
    # home (e.g. fresh-eye-subagent-review.md) cited by MANY skills, just as
    # irreversible to delete as a public/support one -- but skills/shared has no
    # per-skill SKILL.md layer, so it must be caught by the deletion pass even
    # though it never appears in `changed_skill_md`'s public/support-only scan.
    repo = tmp_path / "repo"
    _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    shared_ref = repo / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
    shared_ref.parent.mkdir(parents=True)
    shared_ref.write_text("# Fresh Eye\n\nCross-skill contract text.\n", encoding="utf-8")
    _run(repo, "git", "add", "-A")
    _commit(repo, "add shared reference")
    shared_ref.unlink()

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "review"
    paths = {s["path"] for s in report["skills"]}
    assert "skills/shared/references/fresh-eye-subagent-review.md" in paths
    [shared_skill] = [s for s in report["skills"] if s["path"].startswith("skills/shared/")]
    assert any(r["kind"] == "deleted-surface" for r in shared_skill["reviews"])


def test_modified_shared_reference_is_not_scanned_as_skill_md(tmp_path: Path, monkeypatch) -> None:
    # The public/support-only scoping for the NON-deletion checks (changed_skill_md,
    # CORE/PACKAGE contracts) is unaffected by widening the deletion pass: a plain
    # edit (not a deletion) to a skills/shared/references/*.md must not be treated
    # as a changed SKILL.md surface.
    repo = tmp_path / "repo"
    _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    shared_ref = repo / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
    shared_ref.parent.mkdir(parents=True)
    shared_ref.write_text("# Fresh Eye\n\nOriginal text.\n", encoding="utf-8")
    _run(repo, "git", "add", "-A")
    _commit(repo, "add shared reference")
    shared_ref.write_text("# Fresh Eye\n\nEdited text.\n", encoding="utf-8")

    assert csafety.changed_skill_md(repo.resolve()) == []
    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "clean"


def test_deleted_skill_md_with_surviving_test_pin_still_blocks(tmp_path: Path, monkeypatch) -> None:
    # A deletion that ALSO breaks a test-pinned literal is a real deterministic
    # break -- it should still BLOCK, alongside the forced deletion REVIEW.
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch)  # isolate the test-literal signal
    (repo / "tests" / "test_demo.py").write_text(
        f'def test_demo_pins(text):\n    assert "{SEDIMENT}" in text\n', encoding="utf-8"
    )
    (skill_dir / "SKILL.md").unlink()

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "blocked"
    [skill] = report["skills"]
    assert any(b["kind"] == "test-pin" for b in skill["blocks"])
    assert any(r["kind"] == "deleted-surface" for r in skill["reviews"])


def test_staged_flag_scopes_deletion_detection_to_the_index(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    skill_md = skill_dir / "SKILL.md"
    _run(repo, "git", "rm", "-q", str(skill_md.relative_to(repo)))

    staged_report = csafety.build_report(repo.resolve(), None, [repo / "tests"], staged=True)
    assert staged_report["status"] == "review"
    default_report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert default_report["status"] == "review"  # git rm touches both index and worktree


def test_unrelated_deletion_is_not_flagged(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    unrelated = repo / "notes.md"
    unrelated.write_text("hello\n", encoding="utf-8")
    _run(repo, "git", "add", "-A")
    _commit(repo, "add notes")
    unrelated.unlink()

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "clean"


def test_explicit_path_mode_does_not_scan_for_deletions(tmp_path: Path, monkeypatch) -> None:
    # When the caller passes an explicit `--path` list, the deletion pass is
    # skipped: the caller owns the target set, mirroring the non-deleted branch.
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    (skill_dir / "SKILL.md").unlink()

    report = csafety.build_report(repo.resolve(), [SKILL_REL], [repo / "tests"])
    assert report["status"] == "clean"


def test_is_skill_surface_path_rejects_non_public_support_shared_root(tmp_path: Path) -> None:
    # A deleted path under "skills/<other>/..." (not "shared", "public", or
    # "support") is not a tracked skill surface -- the `parts[1] not in
    # {"public", "support"}` guard must return False rather than fall through
    # to the public/support-only SKILL.md / references checks below it.
    assert csafety._is_skill_surface_path("skills/vendor/detail.md") is False
    assert csafety._is_skill_surface_path("skills/vendor/references/detail.md") is False


def test_report_payload_reports_deleted_surface_reviews(tmp_path: Path, monkeypatch) -> None:
    # A whole-SKILL.md deletion produces a "review" status with a deleted-surface
    # finding. `format_human` was deleted with `--json` on 2026-08-14, so both
    # things it rendered have to reach the emitted payload: the per-skill review
    # row naming the surface, and the explanation of what a deleted-surface REVIEW
    # OBLIGES (which the raw finding row never carried).
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    (skill_dir / "SKILL.md").unlink()

    report = csafety.build_report(repo.resolve(), None, [repo / "tests"])
    assert report["status"] == "review"
    payload = csafety.report_payload(report)
    reviews = [review for skill in payload["skills"] for review in skill["reviews"]]
    assert any(
        review["kind"] == "deleted-surface" and review["phrase"] == SKILL_REL for review in reviews
    )
    assert "a whole SKILL.md" in payload["kind_meaning"]["deleted-surface"]
    assert "not reversible" in payload["kind_meaning"]["deleted-surface"]


def test_cli_strict_fails_on_review(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    skill_dir = _seed_repo(repo)
    _patch_pins(monkeypatch, core=[CORE_PIN])
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace(SEDIMENT + "\n", ""), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_cut_safety.py", "--repo-root", str(repo), "--tests-root", "tests", "--strict"],
    )
    assert csafety.main() == 1
    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_cut_safety.py", "--repo-root", str(repo), "--tests-root", "tests"],
    )
    assert csafety.main() == 0  # review-only is exit 0 without --strict
