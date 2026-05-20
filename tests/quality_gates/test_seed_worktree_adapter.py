"""Regression tests for `skills/public/setup/scripts/seed_worktree_adapter.py`.

Covers:
- #181: documented `--repo-root .` invocation succeeds (does not raise
  `ValueError` from `relative_to` on a relative repo root).
- #182: detection-driven template rendering picks the right package manager
  and hook installer instead of a hardcoded pnpm+lefthook block.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "public" / "setup" / "scripts" / "seed_worktree_adapter.py"
LIB_PATH = ROOT / "skills" / "public" / "setup" / "scripts" / "seed_worktree_adapter_lib.py"

_spec = importlib.util.spec_from_file_location("seed_worktree_adapter_lib", LIB_PATH)
assert _spec is not None and _spec.loader is not None
LIB = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = LIB
_spec.loader.exec_module(LIB)


def _run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def test_repo_root_dot_invocation_writes_file_and_exits_zero(tmp_path: Path) -> None:
    """#181: `--repo-root .` must not raise ValueError after writing."""
    repo = tmp_path / "repo"
    repo.mkdir()
    result = _run(repo, "--repo-root", ".")
    assert result.returncode == 0, result.stderr
    assert "wrote .agents/worktree-adapter.yaml" in result.stdout
    # The printed path must remain relative — a regression to printing the
    # resolved absolute path would still trip operators who eyeball it.
    assert str(repo) not in result.stdout
    assert (repo / ".agents" / "worktree-adapter.yaml").is_file()


def test_existing_file_refuses_without_force(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    target = repo / ".agents" / "worktree-adapter.yaml"
    target.write_text("preserved\n", encoding="utf-8")

    result = _run(repo, "--repo-root", ".")

    assert result.returncode == 1
    assert "already exists" in result.stderr
    assert target.read_text(encoding="utf-8") == "preserved\n"


def test_force_overwrites(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    target = repo / ".agents" / "worktree-adapter.yaml"
    target.write_text("preserved\n", encoding="utf-8")

    result = _run(repo, "--repo-root", ".", "--force")

    assert result.returncode == 0, result.stderr
    assert "preserved" not in target.read_text(encoding="utf-8")


def test_detection_pnpm_lefthook(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pnpm-lock.yaml").touch()
    (repo / "lefthook.yml").write_text("pre-commit:\n  commands: {}\n", encoding="utf-8")

    detection = LIB.detect(repo)
    rendered = LIB.render_template(detection)

    assert detection.package_manager == "pnpm"
    assert detection.hook_system == "lefthook"
    assert detection.hook_install_argv == ("pnpm", "exec", "lefthook", "install")
    assert "- pnpm\n        - install\n        - --frozen-lockfile" in rendered
    assert "- lefthook\n        - install" in rendered


def test_detection_npm_repo_owned_hooks(tmp_path: Path) -> None:
    """Cautilus shape: npm lockfile + repo-owned .githooks + hooks:install script."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package-lock.json").touch()
    (repo / "package.json").write_text(
        json.dumps(
            {"name": "demo", "scripts": {"hooks:install": "./bin/hooks-install"}}
        ),
        encoding="utf-8",
    )
    (repo / ".githooks").mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "core.hooksPath", ".githooks"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    detection = LIB.detect(repo)
    rendered = LIB.render_template(detection)

    assert detection.package_manager == "npm"
    assert detection.hook_system == "repo-owned"
    assert detection.hook_install_argv == ("npm", "run", "hooks:install")
    assert "- npm\n        - ci" in rendered
    assert "- npm\n        - run\n        - hooks:install" in rendered


def test_detection_yarn_classic_husky(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "yarn.lock").touch()
    (repo / ".husky").mkdir()

    detection = LIB.detect(repo)
    rendered = LIB.render_template(detection)

    assert detection.package_manager == "yarn"
    assert detection.package_manager_variant == "classic"
    assert detection.hook_system == "husky"
    assert detection.hook_install_argv == ("yarn", "exec", "husky", "install")
    assert "- yarn\n        - install\n        - --frozen-lockfile" in rendered


def test_detection_yarn_berry_uses_immutable_flag(tmp_path: Path) -> None:
    """Yarn 2+ rejects --frozen-lockfile and expects --immutable."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "yarn.lock").touch()
    (repo / ".yarnrc.yml").write_text("nodeLinker: node-modules\n", encoding="utf-8")

    detection = LIB.detect(repo)
    rendered = LIB.render_template(detection)

    assert detection.package_manager == "yarn"
    assert detection.package_manager_variant == "berry"
    assert "- yarn\n        - install\n        - --immutable" in rendered
    assert "--frozen-lockfile" not in rendered


def test_detection_yarn_berry_via_package_manager_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "yarn.lock").touch()
    (repo / "package.json").write_text(
        json.dumps({"name": "demo", "packageManager": "yarn@4.1.0"}),
        encoding="utf-8",
    )

    detection = LIB.detect(repo)
    rendered = LIB.render_template(detection)

    assert detection.package_manager_variant == "berry"
    assert "--immutable" in rendered


def test_detection_yarn_classic_via_package_manager_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "yarn.lock").touch()
    (repo / "package.json").write_text(
        json.dumps({"name": "demo", "packageManager": "yarn@1.22.19"}),
        encoding="utf-8",
    )

    detection = LIB.detect(repo)
    rendered = LIB.render_template(detection)

    assert detection.package_manager_variant == "classic"
    assert "--frozen-lockfile" in rendered


def test_detection_simple_git_hooks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package-lock.json").touch()
    (repo / "package.json").write_text(
        json.dumps({"name": "demo", "simple-git-hooks": {"pre-commit": "echo demo"}}),
        encoding="utf-8",
    )

    detection = LIB.detect(repo)
    rendered = LIB.render_template(detection)

    assert detection.package_manager == "npm"
    assert detection.hook_system == "simple-git-hooks"
    assert detection.hook_install_argv == ("npx", "simple-git-hooks")
    assert "- npx\n        - simple-git-hooks" in rendered


def test_detection_no_node_tooling(tmp_path: Path) -> None:
    """Python-only repo: neutral commented template."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")

    detection = LIB.detect(repo)
    rendered = LIB.render_template(detection)

    assert detection.package_manager is None
    assert detection.hook_system is None
    assert "No package manager lockfile or package.json detected" in rendered
    assert "No hook system detected" in rendered
    # No active argv blocks should appear.
    assert "    - id: install-deps\n" not in rendered
    assert "    - id: install-hooks\n" not in rendered


def test_rendered_template_is_valid_block_style_yaml(tmp_path: Path) -> None:
    """argv lists must be block-style sequences, not flow-style strings."""
    yaml = pytest.importorskip("yaml")
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pnpm-lock.yaml").touch()
    (repo / "lefthook.yml").write_text("pre-commit:\n  commands: {}\n", encoding="utf-8")

    detection = LIB.detect(repo)
    rendered = LIB.render_template(detection)
    data = yaml.safe_load(rendered)

    assert data["version"] == 1
    commands = data["prepare"]["commands"]
    install_deps = next(c for c in commands if c["id"] == "install-deps")
    assert isinstance(install_deps["argv"], list)
    assert all(isinstance(item, str) for item in install_deps["argv"])
    install_hooks = next(c for c in commands if c["id"] == "install-hooks")
    assert isinstance(install_hooks["argv"], list)
