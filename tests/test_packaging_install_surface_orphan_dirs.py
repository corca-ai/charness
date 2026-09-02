from __future__ import annotations

from pathlib import Path

from runtime_bootstrap import import_repo_module

_module = import_repo_module(__file__, "scripts.validate_packaging_install_surface")
validate_exported_public_skills = _module.validate_exported_public_skills
validate_exported_support_assets = _module.validate_exported_support_assets


def _noop_require_dir(path: Path, field: str) -> None:
    if not path.is_dir():
        raise AssertionError(f"missing dir for {field}: {path}")


def _noop_require_file(path: Path, field: str) -> None:
    if not path.is_file():
        raise AssertionError(f"missing file for {field}: {path}")


def _validate_relative_path(value: object, field: str) -> str:
    assert isinstance(value, str)
    return value


def _seed_skill(parent: Path, skill_id: str) -> None:
    skill_dir = parent / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(f"# {skill_id}\n", encoding="utf-8")


def _seed_orphan(parent: Path, skill_id: str) -> None:
    orphan = parent / skill_id / "scripts" / "__pycache__"
    orphan.mkdir(parents=True, exist_ok=True)
    (orphan / "stale.cpython-310.pyc").write_bytes(b"\x00")


def test_validate_exported_public_skills_ignores_orphan_dir(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    source_public = root / "skills" / "public"
    source_public.mkdir(parents=True)
    plugin_root = root / "plugins" / "demo"
    exported_skills = plugin_root / "skills"
    exported_skills.mkdir(parents=True)

    _seed_skill(source_public, "demo-a")
    _seed_skill(exported_skills, "demo-a")
    _seed_orphan(source_public, "demo-removed")

    validate_exported_public_skills(
        root,
        plugin_root,
        {"public_skills_dir": "skills/public"},
        require_dir=_noop_require_dir,
        require_file=_noop_require_file,
        validate_relative_path=_validate_relative_path,
    )


def test_validate_exported_support_assets_ignores_orphan_dir(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    source_support = root / "skills" / "support"
    source_support.mkdir(parents=True)
    plugin_root = root / "plugins" / "demo"
    exported_support = plugin_root / "support"
    exported_support.mkdir(parents=True)

    _seed_skill(source_support, "agent-foo")
    _seed_skill(exported_support, "agent-foo")
    _seed_orphan(source_support, "support-removed")

    validate_exported_support_assets(
        root,
        plugin_root,
        {"support_skills_dir": "skills/support"},
        require_dir=_noop_require_dir,
        validate_relative_path=_validate_relative_path,
    )
