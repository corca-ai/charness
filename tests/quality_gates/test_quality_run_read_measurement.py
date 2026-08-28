from __future__ import annotations

from pathlib import Path

from .seeding_support import load_module
from .support import ROOT


def _load_plan(path: Path, name: str):
    return load_module(name, path)


def test_quality_required_read_measurement_is_source_plugin_parity_and_never_zero_for_missing(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    source = _load_plan(ROOT / "skills/public/quality/scripts/plan_quality_run.py", "quality_plan_source")
    plugin = _load_plan(ROOT / "plugins/charness/skills/quality/scripts/plan_quality_run.py", "quality_plan_plugin")

    for plan, skill_root in (
        (source.build_plan(repo), ROOT / "skills/public/quality"),
        (plugin.build_plan(repo), ROOT / "plugins/charness/skills/quality"),
    ):
        quality_lenses = next(read for read in plan["required_reads"] if read["path"] == "references/quality-lenses.md")
        assert quality_lenses["size_bytes"] == (skill_root / "references/quality-lenses.md").stat().st_size

    missing = source._measure_required_read({"path": "references/absent.md", "why": "test", "role": "required-primer"})
    assert missing["measurement_state"] == "unavailable"
    assert missing["unavailable_reason"] == "missing"
    assert "size_bytes" not in missing

    isolated_skill_root = tmp_path / "isolated-quality-skill"
    isolated_skill_root.mkdir()
    loop = isolated_skill_root / "loop"
    loop.symlink_to("loop")
    monkeypatch.setattr(source, "SKILL_ROOT", isolated_skill_root)
    failed = source._measure_required_read({"path": "loop", "why": "test", "role": "required-primer"})
    assert failed["unavailable_reason"] == "stat-failed"

    directory = isolated_skill_root / "directory"
    directory.mkdir()
    assert source._measure_required_read({"path": "directory", "why": "test"})["unavailable_reason"] == "not-a-file"
    assert source._measure_required_read({"path": "../outside.md", "why": "test"})["unavailable_reason"] == "outside-declared-base"
    assert source._measure_required_read({"path": None, "why": "test"})["unavailable_reason"] == "unknown-base"


def test_a_ref_declaring_a_base_the_quality_planner_has_no_anchor_for_is_unknown_base():
    """Pins the LITERAL base map. The sibling assertion above reaches `unknown-base`
    through the PATH guard, so it stayed green under the defect this pins: a map
    built as `{ref.get("base"): SKILL_ROOT}` derives its key from the value being
    looked up, always hits, and prices a `base: repo` ref against the SKILL root --
    reporting `missing`, or a confident size for the wrong file. Found by round 2.
    """
    source = _load_plan(ROOT / "skills/public/quality/scripts/plan_quality_run.py", "quality_plan_base_probe")
    measured = source._measure_required_read(
        {"path": "references/quality-lenses.md", "why": "t", "base": "repo"}
    )
    assert measured["measurement_state"] == "unavailable"
    assert measured["unavailable_reason"] == "unknown-base"
