from __future__ import annotations

from pathlib import Path

import pytest

from scripts import repo_file_listing, repo_layout
from scripts.repo_file_listing import (
    RepoFileListingError,
    RepoFileSnapshot,
    bind_subject_listing,
    iter_matching_repo_files,
    iter_repo_files,
    unbind_subject_listing,
)

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


def test_iter_matching_repo_files_can_require_git_listing(tmp_path):
    repo = tmp_path / "not-a-git-repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")

    with pytest.raises(RepoFileListingError) as exc_info:
        iter_matching_repo_files(repo, ("README.md",), require_git=True)

    message = str(exc_info.value)
    assert "repo file listing failed" in message
    assert "command: git ls-files -z --cached --others --exclude-standard" in message


def test_plain_fixture_fallback_does_not_spawn_a_predictable_git_refusal(
    tmp_path, monkeypatch
):
    repo = tmp_path / "plain-fixture"
    repo.mkdir()
    readme = repo / "README.md"
    readme.write_text("# Demo\n", encoding="utf-8")

    def unexpected_git(*_args, **_kwargs):
        raise AssertionError("plain fixture must not probe Git before its fallback")

    monkeypatch.setattr(repo_file_listing.subprocess, "run", unexpected_git)

    assert iter_matching_repo_files(repo, ("README.md",)) == [readme]


def test_bare_repository_signature_still_reaches_the_real_git_boundary(tmp_path) -> None:
    repo = tmp_path / "bare.git"
    (repo / "objects").mkdir(parents=True)
    (repo / "refs").mkdir()
    (repo / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    assert repo_file_listing._git_metadata_is_discoverable(repo) is True


def test_repo_file_snapshot_reuses_one_listing_across_derived_views(
    tmp_path, monkeypatch
):
    repo = tmp_path / "repo"
    repo.mkdir()
    readme = repo / "README.md"
    readme.write_text("# Demo\n", encoding="utf-8")
    calls = 0

    def listed(*args, **kwargs):
        nonlocal calls
        calls += 1
        return [readme]

    monkeypatch.setattr(repo_file_listing, "git_list_repo_files", listed)
    snapshot = RepoFileSnapshot(repo)

    assert iter_repo_files(repo, snapshot=snapshot) == [readme]
    assert iter_matching_repo_files(
        repo, ("*.md",), snapshot=snapshot
    ) == [readme]
    assert calls == 1


def test_bound_subject_listing_is_shared_until_unbound(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    readme = repo / "README.md"
    readme.write_text("# Demo\n", encoding="utf-8")
    calls = 0

    def listed(*args, **kwargs):
        nonlocal calls
        calls += 1
        return [readme]

    monkeypatch.setattr(repo_file_listing, "git_list_repo_files", listed)
    bind_subject_listing(RepoFileSnapshot(repo, require_git=True))
    try:
        assert iter_repo_files(repo, require_git=True) == [readme]
        assert iter_matching_repo_files(repo, ("*.md",), require_git=True) == [readme]
        assert RepoFileSnapshot(repo, require_git=True).list_files() == [readme]
        assert calls == 1
    finally:
        unbind_subject_listing(repo, require_git=True)
    assert RepoFileSnapshot(repo, require_git=True).list_files() == [readme]
    assert calls == 2


def test_this_repo_listing_is_bound_for_the_session() -> None:
    assert repo_file_listing._subject_listing(REPO_ROOT, require_git=True) is not None


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
