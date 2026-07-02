from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import check_skill_surface_preflight as preflight


def _write_skill(repo: Path, *, skill_lines: list[str]) -> Path:
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text("\n".join(skill_lines) + "\n", encoding="utf-8")
    return skill_path


def _skill_at_ceiling() -> list[str]:
    lines = [
        "---",
        "name: demo",
        'description: "Demo skill."',
        "---",
        "",
        "# Demo",
    ]
    lines.extend(f"Core line {index}" for index in range(159))
    lines.extend(["", "## References", "", "- `references/note.md`"])
    lines.extend("" for _ in range(31))
    assert len(lines) == 200
    return lines


def test_skill_surface_preflight_blocks_skill_md_preview_past_known_ceilings(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=_skill_at_ceiling())

    payload = preflight.build_report(repo.resolve(), str(skill_path), 1, False)
    assert json.loads(json.dumps(payload))["status"] == "blocked"
    assert payload["status"] == "blocked"
    assert set(payload["blockers"]) == {"skill_md_total", "core_nonempty"}
    assert payload["headroom"]["skill_md_total"]["remaining_after_preview"] == -1
    assert payload["headroom"]["core_nonempty"]["remaining_after_preview"] == -1


def _skill_near_cap(total_lines: int) -> list[str]:
    lines = [
        "---",
        "name: demo",
        'description: "Demo skill."',
        "---",
        "",
        "# Demo",
        "",
        "Use this when the repo needs a demo skill.",
        "",
        "## References",
        "",
        "- `references/note.md`",
    ]
    lines.extend("" for _ in range(total_lines - len(lines)))
    assert len(lines) == total_lines
    return lines


def test_skill_surface_preflight_warns_near_cap_without_blocking(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=_skill_near_cap(195))

    payload = preflight.build_report(repo.resolve(), str(skill_path), 0, False)
    assert payload["status"] == "ok"
    assert payload["blockers"] == []
    assert [row["id"] for row in payload["warnings"]] == ["near_cap"]
    assert "195/200" in payload["warnings"][0]["message"]
    assert "never silently drop" in payload["warnings"][0]["message"]
    human = preflight.format_human(payload)
    assert "WARN near_cap:" in human


def test_skill_surface_preflight_no_near_cap_warning_below_floor(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=_skill_near_cap(194))

    payload = preflight.build_report(repo.resolve(), str(skill_path), 0, False)
    assert payload["status"] == "ok"
    assert payload["warnings"] == []
    assert "WARN near_cap:" not in preflight.format_human(payload)


def test_skill_surface_preflight_at_ceiling_warns_and_blocks_independently(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=_skill_at_ceiling())

    payload = preflight.build_report(repo.resolve(), str(skill_path), 1, False)
    assert payload["status"] == "blocked"
    assert [row["id"] for row in payload["warnings"]] == ["near_cap"]


def test_skill_surface_preflight_reference_preview_preserves_core_headroom(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    _write_skill(
        repo,
        skill_lines=[
            "---",
            "name: demo",
            'description: "Demo skill."',
            "---",
            "",
            "# Demo",
            "",
            "Use this when the repo needs a demo skill.",
            "",
            "## References",
            "",
            "- `references/note.md`",
        ],
    )
    reference_path = repo / "skills" / "public" / "demo" / "references" / "note.md"

    payload = preflight.build_report(repo.resolve(), str(reference_path), 200, False)
    assert payload["target"]["kind"] == "reference"
    assert payload["headroom"]["skill_md_total"]["preview_delta"] == 0
    assert payload["headroom"]["core_nonempty"]["preview_delta"] == 0
    assert "reference_link_depth" in {row["id"] for row in payload["couplings"]}
    assert "plugin_mirror_sync" in {row["id"] for row in payload["couplings"]}


def test_check_commands_cover_full_portable_package_gate_set() -> None:
    # #328: the one-shot --run-checks preflight must report ALL the portable-package
    # gates at once (a narrower set leaves ~4 commit-boundary round-trips uncaught).
    ids = {check_id for check_id, _command in preflight._check_commands(Path("."))}
    assert {
        "validate_skills",
        "validate_skill_ergonomics",
        "check_skill_ownership_overlap",
        "validate_attention_state_visibility",
        "check_doc_links",
        "check_markdown",
    } <= ids


def test_run_checks_reports_all_portable_package_gates_on_real_repo() -> None:
    # Integration: the extended gate set runs clean against the committed repo, so
    # --run-checks is a true one-shot preflight rather than a partial subset.
    from .support import ROOT

    report = preflight.build_report(ROOT, "skills/public/quality/SKILL.md", 0, True)
    seen = {row["id"] for row in report["checks"]}
    assert "validate_skill_ergonomics" in seen
    assert "check_skill_ownership_overlap" in seen
    assert "validate_attention_state_visibility" in seen
    assert report["check_failures"] == []


def test_skill_surface_preflight_rejects_non_skill_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    outside = repo / "docs" / "note.md"
    outside.parent.mkdir(parents=True)
    outside.write_text("# Note\n", encoding="utf-8")

    with pytest.raises(preflight.PreflightError, match="target must live under skills/public"):
        preflight.build_report(repo.resolve(), str(outside), 0, False)


# --- #319: commit-boundary core_nonempty headroom-buffer ratchet ---


_LIMIT = preflight.MAX_CORE_NONEMPTY_LINES
_BUFFER = preflight.CORE_NONEMPTY_HEADROOM_BUFFER


def _skill_with_core(core: int) -> str:
    lines = ["---", "name: demo", 'description: "Demo skill."', "---", "", "# Demo"]
    lines.extend(f"Core line {index}" for index in range(core - 1))
    lines.extend(["", "## References", "", "- `references/note.md`"])
    return "\n".join(lines) + "\n"


def test_skill_with_core_helper_counts_match_core_nonempty() -> None:
    # Guards the test fixture itself: the broad-gate computation must agree with
    # what _skill_with_core claims, or the ratchet cases below would be vacuous.
    assert preflight._core_nonempty_lines(_skill_with_core(_LIMIT)) == _LIMIT
    assert preflight._core_nonempty_lines(_skill_with_core(_LIMIT - 10)) == _LIMIT - 10


def test_evaluate_core_headroom_blocks_healthy_skill_dropped_below_buffer() -> None:
    # The #316 triggering instance generalized: a skill with headroom edited down
    # to the hard limit (0 remaining) is blocked at the commit boundary.
    verdict = preflight.evaluate_core_headroom(_LIMIT, _LIMIT - (_BUFFER + 4))
    assert verdict["new_remaining"] == 0
    assert verdict["blocked"] is True


def test_evaluate_core_headroom_grandfathers_existing_under_buffer_flat_edit() -> None:
    # A skill already at the limit (0 remaining) may take a flat edit without being
    # retroactively blocked -- the ratchet only blocks fresh erosion.
    verdict = preflight.evaluate_core_headroom(_LIMIT, _LIMIT)
    assert verdict["under_buffer"] is True
    assert verdict["regressed"] is False
    assert verdict["blocked"] is False


def test_evaluate_core_headroom_allows_under_buffer_improvement() -> None:
    verdict = preflight.evaluate_core_headroom(_LIMIT - 1, _LIMIT)
    assert verdict["under_buffer"] is True
    assert verdict["blocked"] is False


def test_evaluate_core_headroom_blocks_brand_new_surface_without_buffer() -> None:
    verdict = preflight.evaluate_core_headroom(_LIMIT - (_BUFFER - 2), None)
    assert verdict["base_remaining"] is None
    assert verdict["blocked"] is True


def test_evaluate_core_headroom_allows_healthy_change() -> None:
    verdict = preflight.evaluate_core_headroom(_LIMIT - (_BUFFER + 2), _LIMIT - (_BUFFER + 6))
    assert verdict["under_buffer"] is False
    assert verdict["blocked"] is False


def _git_stage(repo: Path, rel: str, content: str) -> None:
    (repo / rel).write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", rel], cwd=repo, check=True, capture_output=True, text=True)


def _git_commit_skill(repo: Path, rel: str, content: str) -> None:
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    _git_stage(repo, rel, content)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "base"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def test_scan_changed_skill_md_blocks_new_drop_below_buffer(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/public/demo/SKILL.md"
    _git_commit_skill(repo, rel, _skill_with_core(_LIMIT - (_BUFFER + 4)))
    _git_stage(repo, rel, _skill_with_core(_LIMIT))

    report = preflight.scan_changed_skill_md(repo.resolve(), [rel])
    assert report["status"] == "blocked"
    assert report["blocked"] == [rel]


def test_scan_changed_skill_md_judges_staged_not_worktree(tmp_path: Path) -> None:
    # #319 honesty: the gate must judge what is being committed (the index), not a
    # working tree that was repaired after a bad version was staged.
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/public/demo/SKILL.md"
    healthy = _skill_with_core(_LIMIT - (_BUFFER + 4))
    _git_commit_skill(repo, rel, healthy)
    _git_stage(repo, rel, _skill_with_core(_LIMIT))  # stage the 0-headroom version
    (repo / rel).write_text(healthy, encoding="utf-8")  # repair only the working tree

    report = preflight.scan_changed_skill_md(repo.resolve(), [rel])
    assert report["status"] == "blocked"
    assert report["blocked"] == [rel]


def test_scan_changed_skill_md_grandfathers_existing_under_buffer(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/support/demo/SKILL.md"
    _git_commit_skill(repo, rel, _skill_with_core(_LIMIT))
    # Reword a core line in place: still 0 remaining, not made worse.
    _git_stage(
        repo,
        rel,
        _skill_with_core(_LIMIT).replace("Core line 0", "Reworded core line"),
    )

    report = preflight.scan_changed_skill_md(repo.resolve(), [rel])
    assert report["status"] == "ok"
    assert report["checked"][0]["base_remaining"] == 0


def test_scan_changed_skill_md_blocks_brand_new_skill_without_buffer(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/public/fresh/SKILL.md"
    target = repo / rel
    target.parent.mkdir(parents=True)
    target.write_text(_skill_with_core(_LIMIT - (_BUFFER - 1)), encoding="utf-8")

    report = preflight.scan_changed_skill_md(repo.resolve(), [rel])
    assert report["status"] == "blocked"
    assert report["checked"][0]["base_remaining"] is None


def test_scan_changed_skill_md_ignores_non_skill_core_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "note.md").write_text("# Note\n", encoding="utf-8")
    report = preflight.scan_changed_skill_md(repo.resolve(), ["docs/note.md"])
    assert report == {"status": "ok", "blocked": [], "checked": []}


def test_changed_skill_md_cli_blocks_with_exit_one(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    rel = "skills/public/demo/SKILL.md"
    _git_commit_skill(repo, rel, _skill_with_core(_LIMIT - (_BUFFER + 4)))
    _git_stage(repo, rel, _skill_with_core(_LIMIT))

    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_surface_preflight.py", "--repo-root", str(repo), "--changed-skill-md", rel],
    )
    assert preflight.main() == 1
    assert "BLOCK" in capsys.readouterr().out


def test_changed_skill_md_cli_empty_list_is_ok(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(
        "sys.argv",
        ["check_skill_surface_preflight.py", "--repo-root", str(repo), "--changed-skill-md", "--json"],
    )
    assert preflight.main() == 0


# --- closeout-vocabulary anti-abuse preflight ---


def test_closeout_vocabulary_findings_flags_overlong_and_prose() -> None:
    tokens = [f"- token-{index} <command>" for index in range(12)]
    text = "\n".join(
        [
            "# Demo",
            "",
            f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
            "",
            *tokens,
            "This is prose. It clearly runs two sentences.",
            "",
            "## Next",
            "",
            "- after",
        ]
    )
    findings = preflight.closeout_vocabulary_findings(text)
    # 13 non-empty lines (> the 12 cap) => an over-length finding, plus the
    # multi-sentence line => a prose finding. The trailing `## Next` bounds the block.
    assert any("non-empty lines" in finding for finding in findings)
    assert any("multi-sentence prose" in finding for finding in findings)


def test_closeout_vocabulary_findings_empty_when_token_shaped() -> None:
    text = "\n".join(
        [
            "# Demo",
            "",
            f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
            "",
            "- ran-fail-deferred <command> <issue|anchor>",
            "",
            "## Next",
            "",
            "- after",
        ]
    )
    assert preflight.closeout_vocabulary_findings(text) == []


def test_format_human_surfaces_closeout_vocab_block(tmp_path: Path) -> None:
    tokens = [f"- token-{index} <command>" for index in range(13)]
    skill_lines = [
        "---",
        "name: demo",
        'description: "Demo skill."',
        "---",
        "",
        "# Demo",
        "",
        "Use this when the repo needs a demo skill.",
        "",
        f"## {preflight.CLOSEOUT_VOCAB_SECTION}",
        "",
        *tokens,
        "",
        "## References",
        "",
        "- `references/note.md`",
    ]
    repo = tmp_path / "repo"
    skill_path = _write_skill(repo, skill_lines=skill_lines)
    payload = preflight.build_report(repo.resolve(), str(skill_path), 0, False)
    assert payload["closeout_vocab"]
    human = preflight.format_human(payload)
    assert "BLOCK closeout-vocab:" in human


def test_format_changed_human_surfaces_vocab_findings() -> None:
    report = {
        "status": "blocked",
        "checked": [
            {
                "path": "skills/public/demo/SKILL.md",
                "blocked": True,
                "base_remaining": None,
                "new_remaining": 3,
                "buffer": 5,
                "vocab_findings": ["`## Closeout Vocabulary` line is multi-sentence prose"],
            }
        ],
    }
    human = preflight.format_changed_human(report)
    assert "closeout-vocab:" in human
    assert "[BLOCK]" in human
