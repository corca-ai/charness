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
    _run_publish_patch,
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


_POST_CREATE_PATH = REPO_ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_post_create.py"


def _load_post_create():
    spec = importlib.util.spec_from_file_location("publish_release_post_create_under_test", _POST_CREATE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FakeShellResult:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def test_post_publish_install_refresh_auto_runs_declared_command() -> None:
    post_create = _load_post_create()
    calls: list[tuple[str, bool]] = []

    def fake_run_shell(command: str, *, cwd, check: bool):
        calls.append((command, check))
        return _FakeShellResult(0, "updated to 0.30.0")

    out = post_create.run_post_publish_install_refresh(
        Path("."), command="charness update", run_shell=fake_run_shell
    )
    assert out["status"] == "refreshed"
    assert out["command"] == "charness update"
    # Must run check=False — a failed refresh cannot abort the already-published release.
    assert calls == [("charness update", False)]


def test_post_publish_install_refresh_skips_when_not_declared() -> None:
    post_create = _load_post_create()

    def boom(*_a, **_k):  # must never be called when no command is declared
        raise AssertionError("run_shell should not run when no command is declared")

    out = post_create.run_post_publish_install_refresh(Path("."), command="", run_shell=boom)
    assert out["status"] == "not_configured"
    assert out["command"] is None


def test_publish_auto_runs_declared_install_refresh_end_to_end(tmp_path: Path) -> None:
    # Integration: a full --execute publish auto-runs the adapter-declared
    # post_publish_install_refresh after the verified release and records it in
    # the payload (locks the CLI wiring; the helper unit tests cover branches).
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter = repo / ".agents" / "release-adapter.yaml"
    adapter.write_text(
        adapter.read_text(encoding="utf-8").replace(
            "quality_command: ./scripts/run-quality.sh",
            "quality_command: ./scripts/run-quality.sh\npost_publish_install_refresh: charness update",
        ),
        encoding="utf-8",
    )
    refresh_log = tmp_path / "charness-refresh.log"
    fake_charness = bin_dir / "charness"
    fake_charness.write_text(
        f'#!/usr/bin/env bash\necho "ran $*" >> {refresh_log}\nexit 0\n', encoding="utf-8"
    )
    fake_charness.chmod(0o755)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "declare post_publish_install_refresh")

    env = _release_env(tmp_path, bin_dir)
    result = _run_publish_patch(repo, env)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["install_refresh"]["status"] == "refreshed"
    assert payload["install_refresh"]["command"] == "charness update"
    assert refresh_log.exists() and "ran update" in refresh_log.read_text(encoding="utf-8")


def test_post_publish_install_refresh_records_failure_without_raising() -> None:
    post_create = _load_post_create()
    out = post_create.run_post_publish_install_refresh(
        Path("."),
        command="charness update",
        run_shell=lambda *_a, **_k: _FakeShellResult(1, "", "boom"),
    )
    # Recorded as a closeout risk, never raised — the release is already published.
    assert out["status"] == "failed"
    assert out["returncode"] == 1
    assert "boom" in out["stderr_tail"]


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


# --- update_instructions pre-publish stub (prep affordance) -------------------


def test_build_update_instructions_prep_payload_surfaces_stub_and_staleness() -> None:
    preflight = _load_preflight()

    # Stale: previous version is described, target is not -> reported as data.
    stale = preflight.build_update_instructions_prep_payload(
        package_id="demo",
        current_version="0.0.0",
        target_version="0.0.1",
        previous_version="0.0.0",
        update_instructions=["Run update to pull 0.0.0."],
    )
    assert stale["mode"] == "prep-update-instructions"
    assert stale["update_instructions_stale"] is True
    assert stale["staleness_blocker"]
    # The stub embeds the target version verbatim, so pasting it satisfies the guard.
    assert "0.0.1" in stale["stub_update_instructions_entry"]

    # Fresh / version-agnostic: not stale, stub still emitted.
    fresh = preflight.build_update_instructions_prep_payload(
        package_id="demo",
        current_version="0.0.0",
        target_version="0.1.0",
        previous_version="0.0.0",
        update_instructions=["Run `demo update`."],
    )
    assert fresh["update_instructions_stale"] is False
    assert fresh["staleness_blocker"] is None
    assert "0.1.0" in fresh["stub_update_instructions_entry"]

    # A bare string is normalized to a single-element list (not split per char).
    as_string = preflight.build_update_instructions_prep_payload(
        package_id="demo",
        current_version="0.0.0",
        target_version="0.1.0",
        previous_version=None,
        update_instructions="Run `demo update` for the refresh.",
    )
    assert as_string["current_update_instructions"] == ["Run `demo update` for the refresh."]

    # None / empty normalizes to an empty list; the stub is still emitted.
    as_none = preflight.build_update_instructions_prep_payload(
        package_id="demo",
        current_version="0.0.0",
        target_version="0.1.0",
        previous_version=None,
        update_instructions=None,
    )
    assert as_none["current_update_instructions"] == []
    assert "0.1.0" in as_none["stub_update_instructions_entry"]


def test_prep_update_instructions_emits_stub_without_critique_or_clean_worktree(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    # Dirty the worktree: the prep affordance must NOT require a clean tree, and it
    # passes no critique flag, proving it runs before both gates.
    (repo / "WIP.txt").write_text("mid-prep edit", encoding="utf-8")

    result = _run_publish(repo, env, "--prep-update-instructions", "--part", "minor")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["mode"] == "prep-update-instructions"
    assert payload["target_version"] == "0.1.0"  # current 0.0.0 -> minor
    assert "0.1.0" in payload["stub_update_instructions_entry"]
    # The seed instructions are version-agnostic -> not stale.
    assert payload["update_instructions_stale"] is False


def test_prep_reports_staleness_as_data_where_dry_run_would_hold(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    adapter = repo / ".agents" / "release-adapter.yaml"
    text = adapter.read_text(encoding="utf-8")
    text = text.replace(
        "update_instructions:\n- Run `demo update`.\n- Restart the host if the previous version is still visible.",
        "update_instructions:\n- Run `demo update` to pull 0.0.0.\n- Restart the host if the previous version is still visible.",
    )
    adapter.write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "seed stale update_instructions")

    env = _release_env(tmp_path, bin_dir)
    # The regular dry-run SystemExits on this stale state (see
    # test_publish_blocks_when_update_instructions_are_stale). The prep affordance
    # instead reports it as data and exits 0, so the maintainer can fix it first.
    result = _run_publish(repo, env, "--prep-update-instructions", "--part", "patch")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["update_instructions_stale"] is True
    assert payload["staleness_blocker"]
    assert "0.0.1" in payload["stub_update_instructions_entry"]


def test_prep_update_instructions_honors_version_selectors(tmp_path: Path) -> None:
    # Lock in the non-`--part` branches of the shared target-version helper:
    # --set-version takes the explicit string; --publish-current targets the
    # current manifest version (no bump), so the stub still embeds it.
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)

    explicit = _run_publish(repo, env, "--prep-update-instructions", "--set-version", "9.9.9")
    assert explicit.returncode == 0, explicit.stderr
    explicit_payload = json.loads(explicit.stdout)
    assert explicit_payload["target_version"] == "9.9.9"
    assert "9.9.9" in explicit_payload["stub_update_instructions_entry"]

    current = _run_publish(repo, env, "--prep-update-instructions", "--publish-current")
    assert current.returncode == 0, current.stderr
    current_payload = json.loads(current.stdout)
    assert current_payload["target_version"] == current_payload["current_version"]


def test_prep_update_instructions_rejects_execute_combo(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    result = _run_publish(repo, env, "--prep-update-instructions", "--part", "patch", "--execute")
    assert result.returncode != 0
    assert "read-only pre-publish affordance" in result.stderr


def test_prep_update_instructions_rejects_invalid_adapter(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    # A non-integer adapter version is a validation error; prep must fail closed.
    (repo / ".agents" / "release-adapter.yaml").write_text("version: not-an-int\nrepo: demo\n", encoding="utf-8")
    env = _release_env(tmp_path, bin_dir)
    result = _run_publish(repo, env, "--prep-update-instructions", "--part", "patch")
    assert result.returncode != 0
    assert "release adapter is invalid" in result.stderr


def test_prep_update_instructions_guards_non_string_manifest_version(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    manifest = repo / "packaging" / "demo.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["version"] = 123  # non-string -> current_release reports no manifest version
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    env = _release_env(tmp_path, bin_dir)
    result = _run_publish(repo, env, "--prep-update-instructions", "--part", "patch")
    assert result.returncode != 0
    assert "did not report a packaging manifest version" in result.stderr


def test_publish_dry_run_requires_clean_worktree(tmp_path: Path) -> None:
    # The non-prep path enforces a clean worktree before building the plan; prep
    # (above) deliberately does not. A dirty tree on the dry-run path is refused.
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    (repo / "DIRTY.txt").write_text("uncommitted", encoding="utf-8")
    env = _release_env(tmp_path, bin_dir)
    result = _run_publish(repo, env, "--part", "patch", "--critique-blocked", CRITIQUE_BLOCKED)
    assert result.returncode != 0
    assert "requires a clean worktree" in result.stderr


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


def test_resume_commits_artifact_before_push_with_executed_retro_payload(tmp_path: Path) -> None:
    # #312-B1: resume must commit the refreshed charness-artifacts/release/latest.md
    # BEFORE the push (so .githooks/pre-push's `git diff --quiet -- charness-artifacts`
    # does not falsely block), and must not regress the retro-trigger payload to the
    # plan's dry-run (would_write / release_content_paths) version on the resumed
    # artifact — it must carry the executed (written / final_release_paths) shape.
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    _simulate_partial_publish(repo)
    env = _release_env(tmp_path, bin_dir)

    result = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute",
        "--critique-blocked", CRITIQUE_BLOCKED,
    )
    assert result.returncode == 0, result.stderr

    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    commit_indices = [i for i, entry in enumerate(git_log) if entry[:1] == ["commit"]]
    push_indices = [i for i, entry in enumerate(git_log) if entry[:1] == ["push"]]
    assert commit_indices and push_indices, git_log
    # The refreshed release artifact is committed before the first push: a clean
    # charness-artifacts/ tree at push time.
    assert min(commit_indices) < min(push_indices), git_log

    payload = json.loads(result.stdout)
    retro = payload["retro_trigger_evaluation"]
    assert retro["evaluated_at"] == "final_release_paths", retro
    # No dry-run regression: would_write is the dry-run-only closeout status.
    assert retro["closeout"]["status"] != "would_write", retro


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
