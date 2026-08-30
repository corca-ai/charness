from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml

from scripts import worktree_create_lib as lib
from tests.charness_cli.worktree_fixtures import copy_worktree_seed

ROOT = Path(__file__).resolve().parents[2]


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _git_commit_no_hooks(message: str, *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "commit", "-m", message],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _make_primary(tmp_path: Path) -> Path:
    return copy_worktree_seed(tmp_path, "primary")


def _install_lefthook_shim(repo: Path) -> None:
    hooks_dir = repo / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    shim = hooks_dir / "pre-commit"
    shim.write_text("#!/bin/sh\nexec lefthook run pre-commit\n", encoding="utf-8")
    shim.chmod(0o755)


def test_create_dry_run_plans_git_worktree_add(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    target = tmp_path / "feature"

    payload = lib.run_create(repo, target_path=target, branch="feature", base="main", dry_run=True)

    assert payload["status"] == lib.PASS
    assert payload["dry_run"] is True
    assert payload["created"] is False
    assert payload["actions"] == [
        {
            "id": "create-worktree",
            "command": ["git", "worktree", "add", "-b", "feature", str(target.resolve()), "main"],
            "status": "planned",
        }
    ]
    assert not target.exists()


def test_create_runs_doctor_and_warns_for_unprepared_worktree(tmp_path: Path, monkeypatch) -> None:
    repo = _make_primary(tmp_path)
    _install_lefthook_shim(repo)
    target = tmp_path / "feature"
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).resolve().parent) + os.pathsep + "/usr/bin" + os.pathsep + "/bin",
    )

    payload = lib.run_create(repo, target_path=target, branch="feature", base="main")

    assert payload["status"] == lib.WARN
    assert payload["created"] is True
    assert target.exists()
    assert payload["doctor"]["status"] == "fail"
    assert payload["_checkout"] == payload["doctor"]["_checkout"]
    assert Path(payload["_checkout"]["own_dir"]).is_dir()
    assert "charness worktree prepare" in payload["next_step"]


def test_create_prepare_runs_adapter_and_returns_pass(tmp_path: Path, monkeypatch) -> None:
    repo = _make_primary(tmp_path)
    _install_lefthook_shim(repo)
    (repo / ".agents").mkdir()
    (repo / ".agents" / "worktree-adapter.yaml").write_text(
        (
            "version: 1\n"
            "prepare:\n"
            "  commands:\n"
            "    - id: install-lefthook\n"
            "      argv:\n"
            "        - sh\n"
            "        - -c\n"
            "        - 'mkdir -p node_modules/lefthook-linux-x64/bin && printf \"#!/bin/sh\\nexit 0\\n\" > node_modules/lefthook-linux-x64/bin/lefthook && chmod +x node_modules/lefthook-linux-x64/bin/lefthook'\n"
        ),
        encoding="utf-8",
    )
    _git("add", ".agents/worktree-adapter.yaml", cwd=repo)
    _git_commit_no_hooks("add worktree adapter", cwd=repo)
    target = tmp_path / "feature"
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).resolve().parent) + os.pathsep + "/usr/bin" + os.pathsep + "/bin",
    )

    payload = lib.run_create(repo, target_path=target, branch="feature", base="main", prepare=True)

    assert payload["status"] == lib.PASS, payload
    assert payload["created"] is True
    assert payload["prepare"]["status"] == "pass"
    assert payload["doctor"]["status"] == "pass"


def test_create_with_failing_prepare_carries_recovering_next_step(tmp_path: Path, monkeypatch) -> None:
    repo = _make_primary(tmp_path)
    target = tmp_path / "prep-fail"
    monkeypatch.setattr(
        lib._doctor_lib,
        "run_prepare",
        lambda path, **_kwargs: {"status": "fail", "next_step": None, "doctor": {"status": "fail"}},
    )

    payload = lib.run_create(repo, target_path=target, branch="prep-fail", base="main", prepare=True)

    assert payload["status"] == lib.FAIL
    assert payload["next_step"] == "Fix prepare failures, then re-run `charness worktree prepare`."


def test_failed_create_carries_the_next_step_affordance_to_stdout(tmp_path: Path) -> None:
    """A failing create still hands the operator its recovery step.

    Restated premise: this used to assert `render_create_text` printed the step as
    `NEXT: ...`. That renderer was deleted, so the presentation contract it pinned
    (uppercase prefix, no lowercase `next: `) no longer exists to assert. The
    information it carried is now a `next_step` key in the payload the command
    emits, so that is what this pins -- reachable by the operator, verbatim, and
    on a run that FAILED, which is the case the affordance exists for.
    """
    repo = _make_primary(tmp_path)
    target = tmp_path / "conflicting"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "charness"),
            "worktree",
            "create",
            "--repo-root",
            str(repo),
            "--path",
            str(target),
            "--branch",
            "conflicting",
            "--detach",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == lib.FAIL
    assert payload["next_step"] == "`--branch` and `--detach` cannot be used together."
    assert not target.exists()


def test_cli_worktree_create_and_add_are_discoverable(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "charness"), "worktree", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "create" in result.stdout
    assert "add" in result.stdout

    create_help = subprocess.run(
        [sys.executable, str(ROOT / "charness"), "worktree", "create", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert create_help.returncode == 0, create_help.stderr
    assert "--prepare" in create_help.stdout
    assert "--path" in create_help.stdout

    add_help = subprocess.run(
        [sys.executable, str(ROOT / "charness"), "worktree", "add", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert add_help.returncode == 0, add_help.stderr
    assert "--prepare" in add_help.stdout
    assert "--path" in add_help.stdout


def test_cli_worktree_create_json_executes_and_reports_doctor(tmp_path: Path) -> None:
    repo = _make_primary(tmp_path)
    target = tmp_path / "cli-feature"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "charness"),
            "worktree",
            "create",
            "--repo-root",
            str(repo),
            "--path",
            str(target),
            "--branch",
            "cli-feature",
            "--base",
            "main",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == lib.PASS
    assert payload["created"] is True
    assert payload["doctor"]["status"] == "pass"
    assert target.exists()


def test_create_requires_isolation_of_the_worktree_it_just_made(
    tmp_path: Path, monkeypatch
) -> None:
    """SC10's flag has to be part of the mechanism, not a command to remember.

    Round 1 found `--require-isolation` had no production caller at all;
    `worktree create` became that caller. Round 2 then found the `--prepare`
    path -- the one the operating contract prescribes -- discarded the verdict,
    because `run_prepare` re-ran the doctor WITHOUT the requirement and
    overwrote both the payload and the status with the result.

    So this pins the requirement on BOTH paths by recording what each doctor
    call was actually asked.
    """
    repo = _make_primary(tmp_path)
    asked: list[bool] = []
    real_doctor = lib._doctor_lib.run_doctor

    def recording_doctor(repo_root, *, require_isolation=False):
        asked.append(require_isolation)
        return real_doctor(repo_root, require_isolation=require_isolation)

    monkeypatch.setattr(lib._doctor_lib, "run_doctor", recording_doctor)

    payload = lib.run_create(
        repo_root=repo, target_path=tmp_path / "wt", branch="slice", base=None,
        detach=False, prepare=False, dry_run=False, force=False,
    )

    assert payload["created"] is True
    assert asked == [True], "creation must assert isolation of the worktree it just made"
    check = next(
        item for item in payload["doctor"]["checks"] if item["id"] == "worktree_isolation"
    )
    assert check["status"] == "pass"


def test_the_prepare_path_does_not_discard_the_isolation_requirement(
    tmp_path: Path, monkeypatch
) -> None:
    # The round-2 blocker directly: every doctor run reached through
    # `--prepare` must carry the requirement, or the verdict that replaces the
    # payload was computed without it.
    repo = _make_primary(tmp_path)
    asked: list[bool] = []
    real_doctor = lib._doctor_lib.run_doctor

    def recording_doctor(repo_root, *, require_isolation=False):
        asked.append(require_isolation)
        return real_doctor(repo_root, require_isolation=require_isolation)

    monkeypatch.setattr(lib._doctor_lib, "run_doctor", recording_doctor)

    lib.run_create(
        repo_root=repo, target_path=tmp_path / "wt", branch="slice", base=None,
        detach=False, prepare=True, dry_run=False, force=False,
    )

    assert asked, "no doctor run was observed"
    assert all(asked), f"a doctor run on the --prepare path dropped the requirement: {asked}"
