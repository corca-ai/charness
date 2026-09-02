from __future__ import annotations

from pathlib import Path

from scripts import check_skill_surface_preflight as preflight
from skills.public.quality.scripts import inventory_skill_ergonomics
from tools import validate_skills

from .support import ROOT


def _write_indexed_skill(
    repo: Path,
    *,
    skill_extra_lines: list[str] | None = None,
    index_text: str = "# Reference Index\n\n- `references/note.md`\n",
) -> Path:
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (references_dir / "index.md").write_text(index_text, encoding="utf-8")
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    lines = [
        "---",
        "name: demo",
        'description: "Demo skill."',
        "---",
        "",
        "# Demo",
        "",
        *(skill_extra_lines or []),
        "## References",
        "",
        "- `references/index.md`",
    ]
    (skill_dir / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return skill_dir


def _run_validate_skills_in_process(repo: Path) -> tuple[int, str]:
    try:
        for kind, skill_dir in validate_skills.iter_skill_dirs(repo.resolve()):
            skill_md = skill_dir / "SKILL.md"
            validate_skills.validate_frontmatter(skill_md)
            validate_skills.validate_support_files(repo.resolve(), skill_dir, kind)
    except validate_skills.ValidationError as exc:
        return 1, str(exc)
    return 0, ""


def _first_skill_from_inventory(repo: Path) -> dict[str, object]:
    adapter = inventory_skill_ergonomics._adapter_payload(repo.resolve())
    data = inventory_skill_ergonomics._adapter_data(adapter)
    skill_paths = [
        path
        for path in inventory_skill_ergonomics.iter_skill_paths(
            repo.resolve(),
            [],
            adapter_skill_paths=inventory_skill_ergonomics._adapter_skill_paths(data),
        )
        if path.is_file()
    ]
    return inventory_skill_ergonomics.inventory_skill(
        repo.resolve(),
        skill_paths[0],
        max_core_lines=160,
    )


def test_validate_skills_rejects_reference_mentioned_only_in_skill_prose(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    _write_indexed_skill(
        repo,
        skill_extra_lines=[
            "## Notes",
            "",
            "This prose mentions `references/note.md` without listing it.",
            "",
        ],
        index_text="# Reference Index\n",
    )

    returncode, stderr = _run_validate_skills_in_process(repo)

    assert returncode != 0
    assert "unlisted reference file(s): `references/note.md`" in stderr


def test_inventory_reports_reference_mentioned_only_in_index_prose(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    _write_indexed_skill(
        repo,
        index_text=(
            "# Reference Index\n\nThis prose mentions `references/note.md` without listing it.\n"
        ),
    )

    skill = _first_skill_from_inventory(repo)

    assert "reference_discoverability_gap" in skill["heuristics"]
    assert skill["unlisted_reference_count"] == 1


def test_validate_skills_accepts_reference_index_listing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_indexed_skill(repo)

    returncode, stderr = _run_validate_skills_in_process(repo)

    assert returncode == 0, stderr


def test_removed_skill_bytecode_residue_is_not_a_skill_package(tmp_path: Path) -> None:
    cache = tmp_path / "skills/public/retired/scripts/__pycache__"
    cache.mkdir(parents=True)
    (cache / "helper.cpython-310.pyc").write_bytes(b"residue")

    assert validate_skills.iter_skill_dirs(tmp_path) == []


def test_manifestless_skill_source_still_reports_as_a_broken_package(tmp_path: Path) -> None:
    script = tmp_path / "skills/public/broken/scripts/helper.py"
    script.parent.mkdir(parents=True)
    script.write_text("VALUE = 1\n", encoding="utf-8")

    assert validate_skills.iter_skill_dirs(tmp_path) == [
        ("public", tmp_path / "skills/public/broken")
    ]


def test_inventory_skill_ergonomics_accepts_reference_index_for_discoverability(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    _write_indexed_skill(repo)

    skill = _first_skill_from_inventory(repo)
    assert "reference_discoverability_gap" not in skill["heuristics"]
    assert skill["unlisted_reference_count"] == 0


def test_achieve_root_uses_reference_index_with_core_headroom() -> None:
    skill_path = ROOT / "skills" / "public" / "achieve" / "SKILL.md"
    index_path = ROOT / "skills" / "public" / "achieve" / "references" / "index.md"
    skill_text = skill_path.read_text(encoding="utf-8")
    index_text = index_path.read_text(encoding="utf-8")
    report = preflight.build_report(ROOT, str(skill_path), 0, False)

    assert "- `references/index.md`" in skill_text
    assert (
        report["headroom"]["core_nonempty"]["remaining"] >= preflight.CORE_NONEMPTY_HEADROOM_BUFFER
    )
    for reference in (
        "references/lifecycle.md",
        "references/goal-artifact.md",
        "references/coordination.md",
        "references/adapter-contract.md",
    ):
        assert reference in index_text


def test_over_cap_skill_body_error_states_the_split_or_delete_rule(tmp_path: Path) -> None:
    """North-star P2: the gate message at the moment of cap pressure must brief
    the split-or-delete rule, never instruct displacing overflow into
    references/ (displaced overflow goes unread)."""
    repo = tmp_path / "repo"
    skill_dir = _write_indexed_skill(repo, skill_extra_lines=["filler"] * 250)

    try:
        validate_skills.validate_support_files(repo.resolve(), skill_dir, "public")
    except validate_skills.ValidationError as exc:
        message = str(exc)
    else:
        raise AssertionError("over-cap SKILL.md passed the length gate")

    assert "separate a concept" in message
    assert "delete" in message
    assert "P2" in message
    assert "move detail into references" not in message
