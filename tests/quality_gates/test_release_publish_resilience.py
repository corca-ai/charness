from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.yaml_output import render_yaml as _render_yaml

from .release_publish_fixtures import (
    REPO_ROOT,
    _release_env,
    _run_publish,
    _run_publish_patch,
    bug_closeout_body,
)
from .release_resume_fixtures import (
    FailedCloseoutState,
)
from .release_resume_fixtures import (
    seed_failed_closeout as _seed_failed_closeout,
)
from .release_resume_fixtures import (
    seed_partial_publish as _seed_partial_publish,
)
from .release_resume_fixtures import (
    seed_publish_release as _seed_publish_release_repo,
)

PREFLIGHT_PATH = REPO_ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_preflight.py"
PUBLISH_CLI_PATH = REPO_ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_cli.py"
MESSAGE_PATH = REPO_ROOT / "skills" / "public" / "release" / "scripts" / "release_issue_closeout_message.py"
CRITIQUE_BLOCKED = "synthetic-test-harness does not spawn real critique subagents"


def _load_preflight():
    spec = importlib.util.spec_from_file_location("publish_release_preflight_under_test", PREFLIGHT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_POST_CREATE_PATH = REPO_ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_post_create.py"
_RUNTIME_PATH = REPO_ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_runtime.py"
_RESUME_PATH = REPO_ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_resume.py"


def _load_post_create():
    spec = importlib.util.spec_from_file_location("publish_release_post_create_under_test", _POST_CREATE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_runtime():
    spec = importlib.util.spec_from_file_location("publish_release_runtime_under_test", _RUNTIME_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_resume():
    spec = importlib.util.spec_from_file_location("publish_release_resume_under_test", _RESUME_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _failure_payload(stderr: str) -> dict:
    start = "BEGIN publish_release_failure_payload"
    end = "END publish_release_failure_payload"
    assert start in stderr and end in stderr, stderr
    return yaml.safe_load(stderr.split(start, 1)[1].split(end, 1)[0].strip())


def test_failure_payload_preserves_bounded_terminal_detail_when_record_write_fails(
    tmp_path: Path,
) -> None:
    runtime = _load_runtime()
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    stream = io.StringIO()

    def broken_renderer(payload):
        # The injected renderer now serves BOTH the durable record and the
        # terminal print (it used to serve only the record, with the terminal
        # half hardcoded to `json.dumps`). Fail only for the durable payload --
        # identified by the placeholder detail `print_failure_payload` puts
        # there -- so this still tests "the RECORD write failed", which is what
        # the name and the assertions below are about.
        if (payload.get("release_failure") or {}).get("detail") == (
            "raw exception text omitted from durable local state"
        ):
            raise OSError("renderer unavailable")
        return _render_yaml(payload)

    runtime.print_failure_payload(
        {"tag_name": "v1.0.0"},
        RuntimeError("command failed\nactionable stderr detail"),
        repo_root=repo,
        render_yaml=broken_renderer,
        stream=stream,
    )

    payload = _failure_payload(stream.getvalue())
    assert payload["release_failure_record"]["status"] == "failed"
    assert "renderer unavailable" in payload["release_failure_record"]["error"]
    assert "actionable stderr detail" in payload["release_failure"]["error_detail"]


def test_publish_release_cli_direct_loader_context_without_sys_modules() -> None:
    module_name = "publish_release_cli_direct_loader_probe"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, PUBLISH_CLI_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module_name not in sys.modules
    context = module._execution_context()
    assert callable(module.execute_publish_plan)
    assert callable(context.run)
    assert hasattr(context, "_helpers")
    assert context.reconcile_public_release_verification is module.reconcile_public_release_verification


def test_release_closeout_message_direct_loader_context_without_sys_modules() -> None:
    module_name = "release_issue_closeout_message_direct_loader_probe"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, MESSAGE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module_name not in sys.modules
    assert callable(module.release_commit_message)
    assert callable(module.validate_release_closeout_draft)


def test_resume_common_loader_reports_unloadable_helper(monkeypatch) -> None:
    resume = _load_resume()
    monkeypatch.setattr(resume.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None)

    try:
        resume._load_release_common()
    except ImportError as exc:
        assert "Unable to load" in str(exc)
        assert "publish_release_common.py" in str(exc)
    else:
        raise AssertionError("expected unloadable publish_release_common helper to raise")


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


@pytest.mark.release_only
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
    payload = yaml.safe_load(result.stdout)
    assert payload["install_refresh"]["status"] == "refreshed"
    assert payload["install_refresh"]["command"] == "charness update"
    assert refresh_log.exists() and "ran update" in refresh_log.read_text(encoding="utf-8")
    artifact_text = (repo / "charness-artifacts" / "release" / "latest.md").read_text(encoding="utf-8")
    assert "## Install Refresh" in artifact_text
    assert "Post-publish install refresh status: `refreshed`." in artifact_text
    assert "Command: `charness update`" in artifact_text
    assert "## Release Runtime" in artifact_text
    assert "`quality_command`:" in artifact_text


def test_release_runtime_timed_records_success_and_failure_paths() -> None:
    runtime = _load_runtime()
    payload: dict[str, object] = {}

    assert runtime.timed(payload, "success", lambda: "ok") == "ok"

    def fail() -> None:
        raise RuntimeError("boom")

    try:
        runtime.timed(payload, "failure", fail)
    except RuntimeError as exc:
        assert str(exc) == "boom"
    else:
        raise AssertionError("expected RuntimeError")

    entries = payload["release_runtime"]
    assert [entry["label"] for entry in entries] == ["success", "failure"]
    assert all(entry["elapsed_seconds"] >= 0 for entry in entries)


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

    # Stale: describes the previous version instead of an evergreen refresh path.
    assert blocker(["Run update to pull 0.20.0 steps."])
    # Also stale: describes only the target version; release narrative belongs
    # in notes/artifacts, not the adapter refresh path.
    assert blocker(["Run update to pull 0.21.0."])
    # Also stale: an older non-previous release note is still release-pinned
    # adapter narrative.
    assert blocker(["Run update to pull 0.18.0."])
    # Version-agnostic: no release-version pin -> nothing to go stale.
    assert blocker(["Run `demo update`.", "Restart the host."]) is None
    # `v`-prefixed previous is matched by substring; target absent -> stale.
    assert blocker(["Upgrade from v0.20.0."])
    # A dotted date with no previous-version mention must NOT false-positive.
    assert blocker(["Cut on 2026.06.05."]) is None
    # previous == target / no previous version still block version-pinned text.
    assert blocker(["Run update to pull 0.21.0"], previous="0.21.0")
    assert blocker(["mentions 0.20.0"], previous=None)
    # No previous version and no version-pinned text -> no check.
    assert blocker(["Run `demo update`."], previous=None) is None


@pytest.mark.release_only
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
    assert "0.0.0" in result.stderr
    assert "version-agnostic" in result.stderr


# --- #432: lingering `.invalid` git identity guard ----------------------------


def test_invalid_git_identity_blocker_logic(tmp_path: Path, no_ambient_git_identity) -> None:
    preflight = _load_preflight()
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Dev")
    _git(repo, "config", "user.email", "dev@example.com")

    # A normal identity is not blocked.
    assert preflight.invalid_git_identity_blocker(repo) is None

    # A lingering `.invalid` placeholder identity is blocked, and the message
    # names the offending kind and ident.
    _git(repo, "config", "user.email", "hotl-proof@example.invalid")
    blocker = preflight.invalid_git_identity_blocker(repo)
    assert blocker is not None
    assert "hotl-proof@example.invalid" in blocker
    assert "author" in blocker


@pytest.mark.release_only
def test_publish_blocks_when_git_identity_is_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    # Simulate the #432 shape: a proof flow left a synthetic `.invalid` identity
    # in the repo-local config and it was never restored.
    _git(repo, "config", "user.email", "hotl-proof@example.invalid")
    # Drop the session identity only AFTER seeding: git prefers GIT_AUTHOR_* over
    # `user.email`, so leaving it set would mask the `.invalid` config this guard
    # exists to catch -- but clearing it before seeding would break the seed commit.
    for name in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.delenv(name, raising=False)
    env = _release_env(tmp_path, bin_dir)

    result = _run_publish(repo, env, "--part", "patch", "--critique-blocked", CRITIQUE_BLOCKED)

    assert result.returncode != 0
    assert "hotl-proof@example.invalid" in result.stderr
    assert ".invalid" in result.stderr


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
    # The guidance deliberately avoids the target version; per-release narrative
    # belongs in release notes, not adapter update_instructions.
    assert "0.0.1" not in stale["stub_update_instructions_entry"]
    assert stale["suggested_update_instructions"]

    # Fresh / version-agnostic: not stale, guidance still emitted.
    fresh = preflight.build_update_instructions_prep_payload(
        package_id="demo",
        current_version="0.0.0",
        target_version="0.1.0",
        previous_version="0.0.0",
        update_instructions=["Run `demo update`."],
    )
    assert fresh["update_instructions_stale"] is False
    assert fresh["staleness_blocker"] is None
    assert "0.1.0" not in fresh["stub_update_instructions_entry"]

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
    assert "0.1.0" not in as_none["stub_update_instructions_entry"]


@pytest.mark.release_only
def test_prep_update_instructions_emits_stub_without_critique_or_clean_worktree(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    # Dirty the worktree: the prep affordance must NOT require a clean tree, and it
    # passes no critique flag, proving it runs before both gates.
    (repo / "WIP.txt").write_text("mid-prep edit", encoding="utf-8")

    result = _run_publish(repo, env, "--prep-update-instructions", "--part", "minor")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["mode"] == "prep-update-instructions"
    assert payload["target_version"] == "0.1.0"  # current 0.0.0 -> minor
    assert "0.1.0" not in payload["stub_update_instructions_entry"]
    assert payload["suggested_update_instructions"]
    # The seed instructions are version-agnostic -> not stale.
    assert payload["update_instructions_stale"] is False


@pytest.mark.release_only
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
    payload = yaml.safe_load(result.stdout)
    assert payload["update_instructions_stale"] is True
    assert payload["staleness_blocker"]
    assert "0.0.1" not in payload["stub_update_instructions_entry"]


@pytest.mark.release_only
def test_prep_update_instructions_honors_version_selectors(tmp_path: Path) -> None:
    # Lock in the non-`--part` branches of the shared target-version helper:
    # --set-version takes the explicit string; --publish-current targets the
    # current manifest version (no bump), while guidance stays version-agnostic.
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)

    explicit = _run_publish(repo, env, "--prep-update-instructions", "--set-version", "9.9.9")
    assert explicit.returncode == 0, explicit.stderr
    explicit_payload = yaml.safe_load(explicit.stdout)
    assert explicit_payload["target_version"] == "9.9.9"
    assert "9.9.9" not in explicit_payload["stub_update_instructions_entry"]

    current = _run_publish(repo, env, "--prep-update-instructions", "--publish-current")
    assert current.returncode == 0, current.stderr
    current_payload = yaml.safe_load(current.stdout)
    assert current_payload["target_version"] == current_payload["current_version"]


@pytest.mark.release_only
def test_prep_update_instructions_rejects_execute_combo(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    env = _release_env(tmp_path, bin_dir)
    result = _run_publish(repo, env, "--prep-update-instructions", "--part", "patch", "--execute")
    assert result.returncode != 0
    assert "read-only pre-publish affordance" in result.stderr


@pytest.mark.release_only
def test_prep_update_instructions_rejects_invalid_adapter(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    # A non-integer adapter version is a validation error; prep must fail closed.
    (repo / ".agents" / "release-adapter.yaml").write_text("version: not-an-int\nrepo: demo\n", encoding="utf-8")
    env = _release_env(tmp_path, bin_dir)
    result = _run_publish(repo, env, "--prep-update-instructions", "--part", "patch")
    assert result.returncode != 0
    assert "release adapter is invalid" in result.stderr


@pytest.mark.release_only
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


@pytest.mark.release_only
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


@pytest.mark.release_only
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


def _resume_closeout_args(carrier: Path) -> tuple[str, ...]:
    return (
        "--close-issue", "44",
        "--close-issue-classification", "bug",
        "--close-issue-carrier-file", str(carrier),
        "--close-issue-behavior", "Behavior #44: confirmed through the release resume fixture",
        "--close-issue-probe-record", "Probe record #44: local-only-by-contract",
    )


def _resume_closeout_body() -> str:
    return bug_closeout_body(
        close_line="Close #44.",
        behavior_line="Behavior #44: confirmed through the release resume fixture",
    )


def _prepare_closeout_resume(
    tmp_path: Path, *, head_closeout_body: str | None
) -> tuple[Path, dict[str, str], Path]:
    return _seed_partial_publish(tmp_path, head_closeout_body=head_closeout_body)


def _run_closeout_resume(
    repo: Path, env: dict[str, str], carrier: Path
) -> subprocess.CompletedProcess[str]:
    return _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        *_resume_closeout_args(carrier),
        "--critique-blocked",
        CRITIQUE_BLOCKED,
    )


def _resume_patch_closeout(
    repo: Path, env: dict[str, str], carrier: Path
) -> subprocess.CompletedProcess[str]:
    return _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        "--close-issue", "44",
        "--close-issue-classification", "bug",
        "--close-issue-carrier-file", str(carrier),
        "--close-issue-behavior", "Behavior #44: confirmed through recovery fixture",
        "--close-issue-probe-record", "Probe record #44: local-only-by-contract",
        "--critique-blocked", CRITIQUE_BLOCKED,
        "--claims-review-artifact", "charness-artifacts/release-review/fixture-claims.json",
    )


@pytest.mark.release_only
def test_resume_completes_tail_after_carrier_state_readback_failure(tmp_path: Path) -> None:
    repo, env, carrier = _seed_failed_closeout(
        tmp_path, state=FailedCloseoutState.ISSUE_READBACK_FAILED
    )

    resumed = _resume_patch_closeout(repo, env, carrier)
    assert resumed.returncode == 0, resumed.stderr
    payload = yaml.safe_load(resumed.stdout)
    assert payload["issue_closeout"]["status"] == "state-verified"


@pytest.mark.release_only
def test_resume_refuses_exact_message_carrier_without_evidence_tree(tmp_path: Path) -> None:
    repo, env, carrier = _seed_failed_closeout(
        tmp_path, state=FailedCloseoutState.CARRIER_PUSH_FAILED
    )

    artifact = "charness-artifacts/release/latest.md"
    changed = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    observer = next(path for path in changed if path.endswith("-release-observer.json"))
    subprocess.run(["git", "checkout", "HEAD^", "--", artifact], cwd=repo, check=True)
    subprocess.run(["git", "rm", observer], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "--amend", "--no-edit", "--allow-empty"],
        cwd=repo, check=True, capture_output=True, text=True,
    )
    remote_before_resume = subprocess.run(
        ["git", "ls-remote", "origin", "refs/heads/main"],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout.split()[0]

    resumed = _resume_patch_closeout(repo, env, carrier)
    assert resumed.returncode != 0
    # The release-record marker belongs only to its introducing commit.  This
    # amended carrier therefore stays in post-publication recovery and rejects
    # its missing observer tree directly instead of being misclassified as a
    # fresh prepared record.
    assert "carrier evidence tree" in resumed.stderr
    remote_main = subprocess.run(
        ["git", "ls-remote", "origin", "refs/heads/main"],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout.split()[0]
    assert remote_main == remote_before_resume


@pytest.mark.release_only
def test_resume_with_clean_release_content_head_adds_post_observer_carrier(tmp_path: Path) -> None:
    repo, env, carrier = _prepare_closeout_resume(tmp_path, head_closeout_body=None)

    result = _run_closeout_resume(repo, env, carrier)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["resume_head_release_content_close_refs"] == []
    assert payload["issue_closeout_carrier_commit_sha"]


@pytest.mark.release_only
def test_resume_refuses_head_closeout_keywords_before_quality_or_push(tmp_path: Path) -> None:
    repo, env, carrier = _prepare_closeout_resume(
        tmp_path, head_closeout_body=_resume_closeout_body() + "\n\nClose #45."
    )

    result = _run_closeout_resume(repo, env, carrier)

    assert result.returncode != 0
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:1] == ["push"] for entry in git_log)
    payload = _failure_payload(result.stderr)
    assert payload["resume_head_release_content_close_refs"] == [
        {"repo": None, "number": 44},
        {"repo": None, "number": 45},
    ]
    assert payload["issue_closeout_draft_validation"]["ok"] is True
    assert "quality_command" not in {entry["label"] for entry in payload.get("release_runtime", [])}


@pytest.mark.release_only
def test_resume_continues_partial_publish_idempotently(tmp_path: Path) -> None:
    repo, env, _carrier = _seed_partial_publish(tmp_path)

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
    commit_indices = [i for i, entry in enumerate(git_log) if entry[:1] == ["commit"]]
    push_indices = [i for i, entry in enumerate(git_log) if entry[:1] == ["push"]]
    assert commit_indices and push_indices, git_log
    assert min(commit_indices) < min(push_indices), git_log
    # It must NOT have created a second release commit or re-tagged.
    assert ["tag", "v0.0.0"] not in git_log
    assert not any(entry[:1] == ["commit"] and "Release demo 0.0.0" in entry for entry in git_log)

    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8"))
    assert any(entry[:2] == ["release", "create"] for entry in gh_log), gh_log

    payload = yaml.safe_load(result.stdout)
    runtime_labels = {entry["label"] for entry in payload["release_runtime"]}
    assert "quality_command" in runtime_labels
    assert "push_create_verify_release" in runtime_labels
    assert "post_publish_install_refresh" in runtime_labels
    assert "retro_trigger_evaluation" not in payload
    assert payload["distinct_channel_verification"]["status"] == "confirmed"


@pytest.mark.release_only
def test_resume_recreates_missing_local_tag_after_revalidation(tmp_path: Path) -> None:
    repo, env, _carrier = _seed_partial_publish(tmp_path)
    subprocess.run(["git", "tag", "-d", "v0.0.0"], cwd=repo, check=True,
                   capture_output=True, text=True)
    release_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    result = _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        "--critique-blocked",
        CRITIQUE_BLOCKED,
    )

    assert result.returncode == 0, result.stderr
    tag_head = subprocess.run(
        ["git", "rev-list", "-n", "1", "v0.0.0"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert tag_head == release_head
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert ["tag", "v0.0.0", release_head] in git_log


@pytest.mark.release_only
def test_resume_dry_run_describes_revalidation_without_mutating(tmp_path: Path) -> None:
    repo, _env, _carrier = _seed_partial_publish(tmp_path)
    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()

    result = _run_publish(
        repo,
        _release_env(tmp_path, repo.parent / "bin"),
        "--resume",
        "--publish-current",
        "--critique-blocked",
        CRITIQUE_BLOCKED,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["resume"].startswith("dry-run: would re-validate gates")
    assert subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip() == head_before


@pytest.mark.release_only
def test_normal_dry_run_prints_plan_without_mutating(tmp_path: Path) -> None:
    repo, _remote, bin_dir = _seed_publish_release_repo(tmp_path)
    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()

    result = _run_publish(
        repo,
        _release_env(tmp_path, bin_dir),
        "--part",
        "patch",
        "--critique-blocked",
        CRITIQUE_BLOCKED,
    )

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["execute"] is False
    assert subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip() == head_before


def test_resume_preflight_rejects_non_string_manifest_version(tmp_path: Path) -> None:
    resume = _load_resume()
    cli = SimpleNamespace(
        build_release_payload=lambda _repo: {
            "surface_versions": {"packaging_manifest": None}
        }
    )

    try:
        resume.preflight_resume_state(
            tmp_path,
            args=SimpleNamespace(remote="origin"),
            adapter_data={"package_id": "demo", "release_backend": {}, "output_dir": "charness-artifacts/release"},
            cli=cli,
        )
    except SystemExit as exc:
        assert "packaging manifest version" in str(exc)
    else:
        raise AssertionError("non-string manifest version must block resume preflight")


@pytest.mark.release_only
def test_resume_refuses_missing_local_tag_when_remote_tag_exists(tmp_path: Path) -> None:
    repo, env, _carrier = _seed_partial_publish(tmp_path)
    subprocess.run(["git", "tag", "-d", "v0.0.0"], cwd=repo, check=True,
                   capture_output=True, text=True)
    env["FAKE_GIT_TARGET_TAG_EXISTS"] = "1"

    result = _run_publish(
        repo,
        env,
        "--resume",
        "--publish-current",
        "--execute",
        "--critique-blocked",
        CRITIQUE_BLOCKED,
    )

    assert result.returncode != 0
    assert "refusing to reconstruct an ambiguous tag" in result.stderr


@pytest.mark.release_only
def test_resume_aborts_before_push_when_revalidation_fails(tmp_path: Path) -> None:
    # RN2: resume must RE-VALIDATE before continuing — never push a stale local
    # release commit unchecked. Make the re-validated quality gate fail and assert
    # resume aborts before any push or release-create.
    repo, env, _carrier = _seed_partial_publish(tmp_path)
    (repo / "scripts" / "run-quality.sh").write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\necho 'quality gate failed on resume' >&2\nexit 1\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "run-quality.sh").chmod(0o755)
    _git(repo, "add", "scripts/run-quality.sh")
    _git(repo, "commit", "--amend", "--no-edit", "--allow-empty")
    _git(repo, "tag", "-f", "v0.0.0")

    result = _run_publish(
        repo, env, "--resume", "--publish-current", "--execute",
        "--critique-blocked", CRITIQUE_BLOCKED,
    )

    assert result.returncode != 0
    git_log = json.loads((tmp_path / "git-log.json").read_text(encoding="utf-8"))
    assert not any(entry[:1] == ["push"] for entry in git_log), f"resume must not push when re-validation fails: {git_log}"
    gh_log = json.loads((tmp_path / "gh-log.json").read_text(encoding="utf-8")) if (tmp_path / "gh-log.json").exists() else []
    assert not any(entry[:2] == ["release", "create"] for entry in gh_log), gh_log
    payload = _failure_payload(result.stderr)
    assert payload["release_failure"]["status"] == "failed"
    runtime_labels = {entry["label"] for entry in payload["release_runtime"]}
    assert "quality_command" in runtime_labels
    assert "push_create_verify_release" not in runtime_labels


@pytest.mark.release_only
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


@pytest.mark.release_only
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
