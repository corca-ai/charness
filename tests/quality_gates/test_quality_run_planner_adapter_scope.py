from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from .support import ROOT, _load_script_module, run_script

SCRIPT = "skills/public/quality/scripts/plan_quality_run.py"
LIFECYCLE = _load_script_module(
    "quality_declaration_lifecycle_adapter_scope_under_test",
    ROOT / "skills/public/quality/scripts/quality_declaration_lifecycle.py",
)
SCOPE = _load_script_module(
    "quality_skill_scope_under_test",
    ROOT / "skills/public/quality/scripts/quality_skill_scope.py",
)


def _run_plan(repo: Path) -> dict[str, object]:
    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)


def test_quality_run_plan_uses_an_adapter_declared_skill_root(tmp_path: Path) -> None:
    """A consumer-owned skill tree is the planner scope, not an unreachable gap."""
    repo = tmp_path / "consumer"
    skill_dir = repo / "packages" / "official-skills" / "native" / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
    adapter = repo / ".agents" / "quality-adapter.yaml"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        "version: 1\nrepo: consumer\noutput_dir: charness-artifacts/quality\n"
        "product_surfaces:\n- bundled_skill\n"
        "skill_ergonomics_skill_paths:\n- packages/official-skills/native/skills\n",
        encoding="utf-8",
    )

    plan = _run_plan(repo)
    lifecycle = plan["declaration_lifecycle"]

    assert plan["skills_in_scope"] is True
    assert plan["sample_skill_paths"] == [
        "packages/official-skills/native/skills/demo/SKILL.md"
    ]
    assert lifecycle["skill_scope_source"] == "adapter-declared"
    assert lifecycle["skills"][0]["path"] == plan["sample_skill_paths"][0]
    assert lifecycle["declared_skill_paths"][0]["target_state"] == "resolved"
    assert not any(
        gap["kind"] == "declared_surface_unreachable" for gap in lifecycle["gaps"]
    )
    assert plan["structural_review_packet"]["required"] is True


def test_quality_skill_scope_keeps_discovery_without_a_declaration() -> None:
    assert SCOPE.effective_skill_paths(["skills/public/demo/SKILL.md"], [], {}) == (
        ["skills/public/demo/SKILL.md"],
        "discovered",
    )


def test_quality_lifecycle_fails_loudly_when_skill_scope_is_not_loadable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_loader = LIFECYCLE.importlib.util.spec_from_file_location

    def missing_scope(name: str, path: Path):
        if Path(path).name == "quality_skill_scope.py":
            return None
        return real_loader(name, path)

    monkeypatch.setattr(
        LIFECYCLE.importlib.util, "spec_from_file_location", missing_scope
    )
    with pytest.raises(ImportError, match="quality_skill_scope.py not loadable beside"):
        LIFECYCLE._load_skill_scope()
