from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


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

    result = run_script(
        "scripts/check_skill_surface_preflight.py",
        "--repo-root",
        str(repo),
        "--path",
        str(skill_path),
        "--preview-delta",
        "1",
        "--json",
    )

    assert result.returncode == 1, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert set(payload["blockers"]) == {"skill_md_total", "core_nonempty"}
    assert payload["headroom"]["skill_md_total"]["remaining_after_preview"] == -1
    assert payload["headroom"]["core_nonempty"]["remaining_after_preview"] == -1


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

    result = run_script(
        "scripts/check_skill_surface_preflight.py",
        "--repo-root",
        str(repo),
        "--path",
        str(reference_path),
        "--preview-delta",
        "200",
        "--json",
    )

    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["target"]["kind"] == "reference"
    assert payload["headroom"]["skill_md_total"]["preview_delta"] == 0
    assert payload["headroom"]["core_nonempty"]["preview_delta"] == 0
    assert "reference_link_depth" in {row["id"] for row in payload["couplings"]}
    assert "plugin_mirror_sync" in {row["id"] for row in payload["couplings"]}


def test_skill_surface_preflight_rejects_non_skill_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    outside = repo / "docs" / "note.md"
    outside.parent.mkdir(parents=True)
    outside.write_text("# Note\n", encoding="utf-8")

    result = run_script(
        "scripts/check_skill_surface_preflight.py",
        "--repo-root",
        str(repo),
        "--path",
        str(outside),
    )

    assert result.returncode == 2
    assert "target must live under skills/public" in result.stderr
