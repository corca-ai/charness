"""Small checks for the maintainer hook install and irreversible hook floor."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from runtime_bootstrap import import_repo_module

from .support import ROOT

PRE_PUSH_HOOK_TEXT = (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")
PRE_COMMIT_HOOK_TEXT = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
CLOSE_GUARD_INVOCATION = (
    'printf \'%s\\n\' "$push_stdin" | python3 scripts/prepush_close_keyword_guard.py \\\n'
    '  --repo-root "$REPO_ROOT" --remote "${1:-origin}"'
)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, check=False, capture_output=True, text=True)


def _seed_source_repo(tmp_path: Path, pre_push_text: str = PRE_PUSH_HOOK_TEXT) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    (repo / "packaging").mkdir(parents=True)
    (repo / "plugins" / "charness").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text("{}\n", encoding="utf-8")
    shutil.copy2(ROOT / "scripts" / "validate_maintainer_setup.py", repo / "scripts" / "validate_maintainer_setup.py")
    for name in ("pre-commit", "commit-msg"):
        shutil.copy2(ROOT / ".githooks" / name, repo / ".githooks" / name)
    (repo / ".githooks" / "pre-push").write_text(pre_push_text, encoding="utf-8")
    _git(repo, "init")
    _git(repo, "config", "core.hooksPath", str(repo / ".githooks"))
    return repo


def _run_setup(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "scripts/validate_maintainer_setup.py", "--repo-root", str(repo)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def test_install_git_hooks_sets_core_hookspath(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", repo / "scripts" / "install-git-hooks.sh")
    for name in ("pre-commit", "commit-msg", "pre-push"):
        shutil.copy2(ROOT / ".githooks" / name, repo / ".githooks" / name)
    _git(repo, "init")

    result = subprocess.run(
        ["bash", "scripts/install-git-hooks.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    configured = _git(repo, "config", "--get", "core.hooksPath")
    assert configured.stdout.strip() == str((repo / ".githooks").resolve())


def test_install_git_hooks_does_not_make_sourced_helpers_executable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", repo / "scripts/install-git-hooks.sh")
    for name in ("pre-commit", "commit-msg", "pre-push", "runtime-env.sh"):
        shutil.copy2(ROOT / ".githooks" / name, repo / ".githooks" / name)
    (repo / ".githooks/runtime-env.sh").chmod(0o644)
    _git(repo, "init")

    result = subprocess.run(
        ["bash", "scripts/install-git-hooks.sh"], cwd=repo,
        check=False, capture_output=True, text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (repo / ".githooks/runtime-env.sh").stat().st_mode & 0o111 == 0
    for name in ("pre-commit", "commit-msg", "pre-push"):
        assert (repo / ".githooks" / name).stat().st_mode & 0o111


def test_install_git_hooks_materializes_consumer_commit_msg_hook(tmp_path: Path) -> None:
    source = tmp_path / "source"
    consumer = tmp_path / "consumer"
    (source / "scripts").mkdir(parents=True)
    (consumer / ".git").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", source / "scripts" / "install-git-hooks.sh")
    checker = source / "scripts" / "check_issue_closeout_commit_msg.py"
    checker.write_text("#!/usr/bin/env python3\nprint('checker')\n", encoding="utf-8")
    checker.chmod(0o755)
    _git(consumer, "init")

    result = subprocess.run(
        ["bash", str(source / "scripts" / "install-git-hooks.sh"), "--repo-root", str(consumer)],
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    hook = consumer / ".githooks" / "commit-msg"
    assert str(checker) in hook.read_text(encoding="utf-8")
    assert ".githooks/runtime-env.sh" in hook.read_text(encoding="utf-8")


def test_hook_runtime_bootstrap_confines_initial_python_cache(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".githooks").mkdir(parents=True)
    (repo / "scripts").mkdir()
    shutil.copy2(ROOT / ".githooks" / "runtime-env.sh", repo / ".githooks" / "runtime-env.sh")
    (repo / "scripts" / "subject.py").write_text("value = 1\n", encoding="utf-8")

    result = subprocess.run(
        [
            "bash",
            "-c",
            "REPO_ROOT=\"$1\"; source \"$REPO_ROOT/.githooks/runtime-env.sh\"; "
            "printf '%s\\n' \"$PYTHONPYCACHEPREFIX\"; python3 -m py_compile scripts/subject.py",
            "runtime-env-test",
            str(repo),
        ],
        cwd=repo,
        env={
            **os.environ,
            "TMPDIR": str(repo / "tmp"),
            "PYTHONPYCACHEPREFIX": str(repo / "pycache"),
            "PYTEST_DEBUG_TEMPROOT": str(repo / "pytest-tmp"),
            "CHARNESS_PYTEST_CACHE_DIR": str(repo / "pytest-cache"),
            "RUFF_CACHE_DIR": str(repo / ".ruff_cache"),
            "COVERAGE_FILE": str(repo / ".coverage"),
        },
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    prefix = Path(result.stdout.splitlines()[0]).resolve()
    assert repo.resolve() not in prefix.parents
    assert not list(repo.rglob("__pycache__"))


def test_hook_runtime_clears_git_discovery_for_child_repositories(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / ".githooks" / "runtime-env.sh", repo / ".githooks" / "runtime-env.sh")
    _git(repo, "init", "-q")
    child = repo / "child"
    child.mkdir()

    result = subprocess.run(
        [
            "bash",
            "-c",
            "set -euo pipefail; "
            "REPO_ROOT=\"$1\"; source \"$REPO_ROOT/.githooks/runtime-env.sh\"; "
            "test -z \"${GIT_DIR:-}\"; test -z \"${GIT_WORK_TREE:-}\"; "
            "cd \"$2\"; git init -q; git config user.name Child; git config user.email child@example.com",
            "runtime-env-git-test",
            str(repo),
            str(child),
        ],
        cwd=repo,
        env={**os.environ, "GIT_DIR": str(repo / ".git"), "GIT_WORK_TREE": str(repo)},
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Child" in (child / ".git" / "config").read_text(encoding="utf-8")
    assert "Child" not in (repo / ".git" / "config").read_text(encoding="utf-8")


def test_validate_maintainer_setup_requires_installed_hookspath(tmp_path: Path) -> None:
    repo = _seed_source_repo(tmp_path)
    (repo / ".git" / "config").unlink()
    missing = _run_setup(repo)
    assert missing.returncode == 1
    assert "install-git-hooks.sh" in missing.stderr

    _git(repo, "config", "core.hooksPath", str(repo / ".githooks"))
    ready = _run_setup(repo)
    assert ready.returncode == 0, ready.stderr


def test_pre_push_keeps_release_boundary_and_drops_mutation_arm(tmp_path: Path) -> None:
    assert "CHARNESS_PRE_PUSH" not in PRE_PUSH_HOOK_TEXT
    module = import_repo_module(__file__, "scripts.validate_maintainer_setup")
    hook = tmp_path / "pre-push"
    hook.write_text(PRE_PUSH_HOOK_TEXT, encoding="utf-8")
    module.check_close_keyword_guard_arming(hook, ".githooks/pre-push")


def test_pre_commit_keeps_the_irreversible_identity_guard() -> None:
    assert 'python3 -B scripts/check_git_identity.py --repo-root "$REPO_ROOT"' in PRE_COMMIT_HOOK_TEXT
    assert 'check_git_identity.py --repo-root "$REPO_ROOT" || true' not in PRE_COMMIT_HOOK_TEXT
    assert "runtime-env.sh" not in PRE_COMMIT_HOOK_TEXT


def _guard_hook(tmp_path: Path, invocation: str) -> Path:
    hook = tmp_path / "pre-push"
    hook.write_text(PRE_PUSH_HOOK_TEXT.replace(CLOSE_GUARD_INVOCATION, invocation), encoding="utf-8")
    return hook


@pytest.mark.parametrize(
    ("invocation", "expected"),
    [
        ('echo "run python3 scripts/prepush_close_keyword_guard.py yourself"', "no longer runs"),
        (
            'printf \'%s\\n\' "$push_stdin" | python3 scripts/prepush_close_keyword_guard.py \\\n'
            '  --repo-root "$REPO_ROOT" || true',
            "discards its verdict",
        ),
        (
            'printf \'%s\\n\' "$push_stdin" | python3 scripts/prepush_close_keyword_guard.py '
            '--repo-root "$REPO_ROOT" &',
            "discards its verdict",
        ),
        ('# python3 scripts/prepush_close_keyword_guard.py --repo-root "$REPO_ROOT"', "no longer runs"),
        ('$GUARD --repo-root "$REPO_ROOT" # prepush_close_keyword_guard.py', "cannot classify"),
    ],
)
def test_close_keyword_guard_arming_refuses_each_disarm(
    tmp_path: Path, invocation: str, expected: str
) -> None:
    module = import_repo_module(__file__, "scripts.validate_maintainer_setup")
    with pytest.raises(module.ValidationError) as excinfo:
        module.check_close_keyword_guard_arming(_guard_hook(tmp_path, invocation), ".githooks/pre-push")
    assert expected in str(excinfo.value)


def test_validate_maintainer_setup_accepts_source_hook_without_mutation_arm(tmp_path: Path) -> None:
    result = _run_setup(_seed_source_repo(tmp_path))
    assert result.returncode == 0, result.stderr
