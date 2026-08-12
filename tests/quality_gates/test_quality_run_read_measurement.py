from __future__ import annotations

import importlib.util
from pathlib import Path

from .support import ROOT


def _load_plan(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
