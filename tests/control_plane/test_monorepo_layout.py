from __future__ import annotations

from pathlib import Path

from scripts import repo_layout
from scripts.repo_file_listing import iter_matching_repo_files

REPO_ROOT = Path(__file__).resolve().parents[2]


def _seed_split_layout(public_root: Path, support_root: Path) -> None:
    public_skills = public_root / "skills" / "public"
    public_skills.mkdir(parents=True)
    (public_skills / "demo").mkdir()
    (public_skills / "demo" / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    scripts_dir = public_skills / "demo" / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "helper.py").write_text("print('hi')\n", encoding="utf-8")

    support_root.mkdir(parents=True)
    schema_src = REPO_ROOT / "skills" / "support" / "capability.schema.json"
    (support_root / "capability.schema.json").write_text(schema_src.read_text(encoding="utf-8"), encoding="utf-8")
    demo_support = support_root / "demo-support"
    demo_support.mkdir()
    (demo_support / "SKILL.md").write_text("# support demo\n", encoding="utf-8")
    support_scripts = demo_support / "scripts"
    support_scripts.mkdir()
    (support_scripts / "support_helper.py").write_text("print('support')\n", encoding="utf-8")


def test_support_dir_honors_env_override(tmp_path, monkeypatch):
    public_root = tmp_path / "public-pkg"
    support_root = tmp_path / "support-pkg"
    _seed_split_layout(public_root, support_root)

    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(support_root))

    resolved = repo_layout.support_dir(public_root)
    assert resolved == support_root.resolve()
    schema_path = repo_layout.support_capability_schema_path(public_root)
    assert schema_path == support_root.resolve() / "capability.schema.json"
    assert schema_path.is_file()


def test_iter_matching_repo_files_picks_up_support_in_split_layout(tmp_path, monkeypatch):
    public_root = tmp_path / "public-pkg"
    support_root = tmp_path / "support-pkg"
    _seed_split_layout(public_root, support_root)

    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(support_root))

    paths = iter_matching_repo_files(
        public_root,
        ("skills/public/*/scripts/*.py", "skills/support/*/scripts/*.py"),
        include_untracked=True,
    )
    relative_names = sorted(p.name for p in paths)
    assert "helper.py" in relative_names
    assert "support_helper.py" in relative_names


def test_iter_matching_repo_files_default_layout_unchanged(tmp_path):
    repo = tmp_path / "single-pkg"
    public_skills = repo / "skills" / "public"
    public_skills.mkdir(parents=True)
    (public_skills / "demo").mkdir()
    scripts_dir = public_skills / "demo" / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "helper.py").write_text("print('hi')\n", encoding="utf-8")
    support_skills = repo / "skills" / "support" / "demo-support" / "scripts"
    support_skills.mkdir(parents=True)
    (support_skills / "support_helper.py").write_text("print('support')\n", encoding="utf-8")

    paths = iter_matching_repo_files(
        repo,
        ("skills/public/*/scripts/*.py", "skills/support/*/scripts/*.py"),
        include_untracked=True,
    )
    names = sorted(p.name for p in paths)
    assert names == ["helper.py", "support_helper.py"]


def test_load_support_capability_schema_uses_override(tmp_path, monkeypatch):
    public_root = tmp_path / "public-pkg"
    support_root = tmp_path / "support-pkg"
    _seed_split_layout(public_root, support_root)

    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(support_root))

    from scripts import control_plane_lib

    schema = control_plane_lib.load_support_capability_schema(public_root)
    assert isinstance(schema, dict)
    assert schema.get("$schema") or "type" in schema


def test_repo_root_from_script_honors_charness_repo_root(tmp_path, monkeypatch):
    custom_root = tmp_path / "elsewhere"
    custom_root.mkdir()
    monkeypatch.setenv("CHARNESS_REPO_ROOT", str(custom_root))

    from scripts.runtime_bootstrap import repo_root_from_script

    resolved = repo_root_from_script("/anywhere/scripts/foo.py")
    assert resolved == custom_root.resolve()
