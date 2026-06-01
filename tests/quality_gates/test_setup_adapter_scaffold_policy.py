from __future__ import annotations

from scripts.adapter_lib import load_yaml_file

from .support import run_script


def test_setup_init_adapter_scaffolds_review_policy_surface(tmp_path) -> None:
    result = run_script("skills/public/setup/scripts/init_adapter.py", "--repo-root", str(tmp_path))
    assert result.returncode == 0, result.stderr

    raw = load_yaml_file(tmp_path / ".agents" / "setup-adapter.yaml")
    assert isinstance(raw, dict)
    assert raw["prose_wrap_policy"] == "semantic"
    assert raw["surfaces"]["roadmap"] == "docs/roadmap.md"
    assert raw["defaults_version"] == "issue-64"
    policy = raw["policy_sources"][0]
    assert policy["path"] == "AGENTS.md"
    assert "bounded fresh-eye review" in policy["evidence_terms"]
    assert "recommendations" not in policy
    assert raw["recommendation_sets"]["enabled"] == []


def test_scaffolded_setup_adapter_does_not_force_review_policy(tmp_path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# Agents\n\nExisting operating policy.\n", encoding="utf-8")
    (tmp_path / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (tmp_path / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")

    init = run_script("skills/public/setup/scripts/init_adapter.py", "--repo-root", str(tmp_path))
    assert init.returncode == 0, init.stderr
    inspect = run_script("skills/public/setup/scripts/inspect_repo.py", "--repo-root", str(tmp_path))
    assert inspect.returncode == 0, inspect.stderr

    assert "agents.delegated_review_policy" not in inspect.stdout
