from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from .release_publish_fixtures import (
    REPO_ROOT,
    _release_env,
    _run_publish,
    _seed_publish_release_repo,
)

PREFLIGHT_PATH = REPO_ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_preflight.py"
CRITIQUE_BLOCKED = "synthetic-test-harness does not spawn real critique subagents"


def _load_preflight():
    spec = importlib.util.spec_from_file_location("publish_release_preflight_under_test", PREFLIGHT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


# --- Gap 3: update_instructions version-staleness check -----------------------


def test_update_instructions_version_blocker_logic() -> None:
    preflight = _load_preflight()

    def blocker(instructions, target="0.21.0", previous="0.20.0"):
        return preflight.update_instructions_version_blocker(
            instructions, target_version=target, previous_version=previous
        )

    # Stale: describes the previous version but not the target.
    assert blocker(["Run update to pull 0.20.0 steps."])
    # Fresh: mentions the target version.
    assert blocker(["Run update to pull 0.21.0."]) is None
    # Version-agnostic: previous version not present -> nothing to go stale.
    assert blocker(["Run `demo update`.", "Restart the host."]) is None
    # `v`-prefixed previous is matched by substring; target absent -> stale.
    assert blocker(["Upgrade from v0.20.0."])
    # A dotted date with no previous-version mention must NOT false-positive.
    assert blocker(["Cut on 2026.06.05."]) is None
    # previous == target (no version change) -> no check.
    assert blocker(["anything 0.21.0"], previous="0.21.0") is None
    # No previous version available -> no check.
    assert blocker(["mentions 0.20.0"], previous=None) is None


def test_publish_blocks_when_update_instructions_are_stale(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter = repo / ".agents" / "release-adapter.yaml"
    text = adapter.read_text(encoding="utf-8")
    # Replace the version-agnostic instructions with a stale, version-pinned line.
    text = text.replace(
        "update_instructions:\n- Run `demo update`.\n- Restart the host if the previous version is still visible.",
        "update_instructions:\n- Run `demo update` to pull 0.0.0.\n- Restart the host if the previous version is still visible.",
    )
    adapter.write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "seed stale update_instructions")

    env = _release_env(tmp_path, bin_dir)
    # --part patch targets 0.0.1; the stale instructions name 0.0.0 -> blocked (dry-run).
    result = _run_publish(repo, env, "--part", "patch", "--critique-blocked", CRITIQUE_BLOCKED)

    assert result.returncode != 0
    assert "update_instructions" in result.stderr
    assert "0.0.1" in result.stderr


# --- Gap 2: installed/exported plugin-cache bootstrap -------------------------


def test_publish_release_imports_from_exported_plugin_layout() -> None:
    # The exported plugin layout drops the `public` path segment, so a hardcoded
    # `skills.public.retro...` import raised ModuleNotFoundError from the cache.
    exported = REPO_ROOT / "plugins" / "charness" / "skills" / "release" / "scripts" / "publish_release.py"
    assert exported.is_file(), "exported plugin mirror must exist"
    result = subprocess.run(
        [sys.executable, str(exported), "--help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert "ModuleNotFoundError" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert "--resume" in result.stdout


# --- Gap 1: resumable / idempotent publish ------------------------------------


def _simulate_partial_publish(repo: Path) -> None:
    # Reproduce the post-commit, pre-push partial state: a local `Release demo
    # 0.0.0` commit + tag v0.0.0 that never reached the remote and has no release.
    output_dir = repo / "charness-artifacts" / "release"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "latest.md").write_text("# Release demo 0.0.0 (partial)\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "Release demo 0.0.0")
    _git(repo, "tag", "v0.0.0")


def test_resume_continues_partial_publish_idempotently(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _simulate_partial_publish(repo)
    env = _release_env(tmp_path, bin_dir)

    result = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute",
        "--critique-blocked", CRITIQUE_BLOCKED,
    )

    assert result.returncode == 0, result.stderr
    # Idempotent: it did not try to recreate the commit or tag.
    assert "nothing to commit" not in result.stderr
    assert "already exists" not in result.stderr

    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    pushes = [entry for entry in git_log if entry[:1] == ["push"]]
    # The resume pushed the branch + tag (and the verification record commit).
    assert any("v0.0.0" in entry for entry in pushes), pushes
    # It must NOT have created a second release commit or re-tagged.
    assert ["tag", "v0.0.0"] not in git_log
    assert not any(entry[:1] == ["commit"] and "Release demo 0.0.0" in entry for entry in git_log)

    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert any(entry[:2] == ["release", "create"] for entry in gh_log), gh_log


def test_resume_aborts_before_push_when_revalidation_fails(tmp_path: Path) -> None:
    # RN2: resume must RE-VALIDATE before continuing — never push a stale local
    # release commit unchecked. Make the re-validated quality gate fail and assert
    # resume aborts before any push or release-create.
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    (repo / "scripts" / "run-quality.sh").write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\necho 'quality gate failed on resume' >&2\nexit 1\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "run-quality.sh").chmod(0o755)
    _simulate_partial_publish(repo)  # the failing quality script is part of the release commit
    env = _release_env(tmp_path, bin_dir)

    result = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute",
        "--critique-blocked", CRITIQUE_BLOCKED,
    )

    assert result.returncode != 0
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:1] == ["push"] for entry in git_log), f"resume must not push when re-validation fails: {git_log}"
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8")) if (tmp_path / "gh-log.json").exists() else []
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log), gh_log


def test_resume_refuses_when_no_partial_state(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    # HEAD is the seed commit, not a release commit -> nothing to resume.
    result = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute",
        "--critique-blocked", CRITIQUE_BLOCKED,
    )
    assert result.returncode != 0
    assert "resume" in result.stderr.lower()


def test_resume_requires_publish_current(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    result = _run_publish(
        repo, env, "--resume", "--part", "patch", "--execute",
        "--critique-blocked", CRITIQUE_BLOCKED,
    )
    assert result.returncode != 0
    # Assert the specific guard message (not just any usage line that happens to
    # contain the flag name) so this stays a discriminating regression guard.
    assert "--resume requires --publish-current" in result.stderr
