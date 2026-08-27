"""Release changed-line regression coverage for release and CLI boundaries.

This module is split from the evidence/boundary regression module so each test
file remains below the repository's hard Python length limit.  The literal
source paths are consumed by the focused mutation mapper.
"""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import os
import runpy
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from runtime_bootstrap import import_repo_module

ROOT = Path(__file__).resolve().parents[1]

_MUTATION_SOURCES = (
    "charness",
    "scripts/adversarial_evidence.py",
    "scripts/capability_catalog_resolver.py",
    "scripts/critique_packet_lib.py",
    "scripts/lesson_session_boundary.py",
    "scripts/open_lesson_session.py",
    "scripts/reviewed_input_identity.py",
    "scripts/slice_closeout_telemetry.py",
    "scripts/staged_commit_gate_plan_helpers.py",
    "skills/public/achieve/scripts/scaffold_goal_specs.py",
    "skills/public/critique/scripts/prepare_packet.py",
    "skills/public/debug/scripts/persist_debug_artifact.py",
    "skills/public/quality/scripts/check_dup_ratchet.py",
    "skills/public/quality/scripts/dup_family_lineage.py",
    "skills/public/quality/scripts/dup_ratchet_baseline_lib.py",
    "skills/public/quality/scripts/check_provenance_contract.py",
    "skills/public/setup/scripts/inspect_repo.py",
)


def _load_script(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


goal_specs = import_repo_module(
    ROOT / "skills/public/achieve/scripts/scaffold_goal_specs.py",
    "skills.public.achieve.scripts.scaffold_goal_specs",
)
dup_check = _load_script(
    "skills/public/quality/scripts/check_dup_ratchet.py",
    "release_dup_check_split_under_test",
)
dup_lineage = _load_script(
    "skills/public/quality/scripts/dup_family_lineage.py",
    "release_dup_lineage_split_under_test",
)
dup_baseline = _load_script(
    "skills/public/quality/scripts/dup_ratchet_baseline_lib.py",
    "release_dup_baseline_split_under_test",
)
provenance_check = _load_script(
    "skills/public/quality/scripts/check_provenance_contract.py",
    "release_provenance_check_split_under_test",
)
setup_inspect = import_repo_module(
    ROOT / "skills/public/setup/scripts/inspect_repo.py",
    "skills.public.setup.scripts.inspect_repo",
)
debug_persist = import_repo_module(
    ROOT / "skills/public/debug/scripts/persist_debug_artifact.py",
    "skills.public.debug.scripts.persist_debug_artifact",
)


def test_goal_specs_loader_and_missing_goal_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("not-json", encoding="utf-8")
    with pytest.raises(SystemExit, match="unreadable or invalid"):
        goal_specs._load_specs(invalid)
    for payload, message in (([], "non-empty"), ({}, "non-empty"), ({"phases": [1]}, "phase 1")):
        path = tmp_path / f"bad-{len(str(payload))}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(SystemExit, match=message):
            goal_specs._load_specs(path)
    missing = {"slug": "shape", "title": "Shape", "objective": "o", "completion": ["c"], "verification": ["v"], "non_claims": ["n"]}
    missing_path = tmp_path / "missing-field.json"
    missing_path.write_text(json.dumps({"phases": [{**missing, "verification": ""}]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="missing required fields"):
        goal_specs._load_specs(missing_path)
    duplicate_path = tmp_path / "duplicate.json"
    duplicate_path.write_text(json.dumps({"phases": [missing, {**missing, "slug": "goal"}]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="duplicate or unusable"):
        goal_specs._load_specs(duplicate_path)
    string_fields = {**missing, "scope_in": "one"}
    string_path = tmp_path / "strings.json"
    string_path.write_text(json.dumps({"phases": [string_fields]}), encoding="utf-8")
    assert goal_specs._load_specs(string_path)[0]["scope_in"] == ["one"]
    bad_list = tmp_path / "bad-list.json"
    bad_list.write_text(json.dumps({"phases": [{**missing, "scope_in": [""]}]}), encoding="utf-8")
    with pytest.raises(SystemExit, match="list of strings"):
        goal_specs._load_specs(bad_list)
    assert "Phase Specifications" in goal_specs._replace_phase_section("# Goal\n", "## Phase Specifications")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scaffold_goal_specs.py",
            "--repo-root",
            str(tmp_path),
            "--goal-path",
            str(tmp_path / "missing-goal.md"),
            "--specs-file",
            str(string_path),
        ],
    )
    with pytest.raises(SystemExit, match="goal artifact not found"):
        goal_specs.main()
    class MissingBootstrapPath:
        def __init__(self, *_args: object) -> None:
            pass

        def resolve(self) -> "MissingBootstrapPath":
            return self

        @property
        def parents(self) -> list[Path]:
            return []

    monkeypatch.setattr(goal_specs, "Path", MissingBootstrapPath)
    with pytest.raises(ImportError, match="not found"):
        goal_specs._load_skill_runtime_bootstrap()
    monkeypatch.setattr(goal_specs, "Path", Path)
    monkeypatch.setattr(sys, "argv", ["scaffold_goal_specs.py", "--repo-root", str(tmp_path), "--goal-path", str(tmp_path / "missing-goal.md"), "--specs-file", str(string_path)])
    with pytest.raises(SystemExit):
        runpy.run_path(str(ROOT / "skills/public/achieve/scripts/scaffold_goal_specs.py"), run_name="__main__")


def test_dup_baseline_and_lineage_reject_untypeable_rows() -> None:
    assert dup_baseline.load_gate_baseline_families(
        {"code_families": [{"fingerprint": "x", "member_hashes": [], "member_paths": [1]}]}
    ) is None
    assert dup_lineage.readiness(
        ["not-a-row", {"fingerprint": "x", "member_paths": ["x.py"]}], reviewed_ids={"x"}
    )["status"] == "ready"
    assert dup_lineage.family_members({"locations": ["not-a-row", {"file": "src/a.py"}]})[1] == {"src/a.py"}


def test_dup_consumer_renders_lineage_proposal_advisory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    (repo / "q").mkdir()
    (repo / "q/dup-review.json").write_text(
        json.dumps(
            {
                "schemaVersion": "charness.quality.dup_review.v1",
                "fixable_ceiling": 0,
                "entries": [{"id": "OLD", "surface": "code", "class": "fixable", "note": "reviewed", "reviewed_at": "2026-08-25"}],
            }
        ),
        encoding="utf-8",
    )
    baseline = dup_baseline.build_gate_baseline(
        {"OLD": ["old-a", "old-b"]},
        member_paths={"OLD": ["src/a.py", "src/b.py"]},
        tool_version="0.20.0",
        algo_version=dup_check._fingerprint.FINGERPRINT_ALGO_VERSION,
    )
    (repo / "q/dup-ratchet-baseline.json").write_text(json.dumps(baseline), encoding="utf-8")
    (repo / ".agents/quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: consumer",
                "dup_ratchet:",
                "  enabled: true",
                "  floor_F: 0",
                "  escalation_K: 10",
                "  scope_paths:",
                "    - src",
                "  review_artifact_path: q/dup-review.json",
                "  gate_baseline_path: q/dup-ratchet-baseline.json",
                "",
            ]
        ),
        encoding="utf-8",
    )
    code = tmp_path / "code.json"
    code.write_text(
        json.dumps(
            {
                "status": "findings",
                "tool_version": "0.20.0",
                "families": [
                    {
                        "family_fingerprint": "NEW",
                        "family_member_hashes": ["new-a", "new-b"],
                        "locations": [
                            {"file": "src/a.py", "start": 1, "end": 2},
                            {"file": "src/b.py", "start": 3, "end": 4},
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    doc = tmp_path / "doc.json"
    doc.write_text(json.dumps({"status": "ok", "families": []}), encoding="utf-8")
    args = dup_check.parse_args(
        [
            "--repo-root",
            str(repo),
            "--code-inventory",
            str(code),
            "--doc-inventory",
            str(doc),
            "--stagnation",
            "0",
        ]
    )
    monkeypatch.setattr(
        dup_check._lineage,
        "propose",
        lambda **_kwargs: [{"new_fingerprint": "NEW", "old_fingerprints": ["OLD"], "relation": "rotation-proposal"}],
    )
    report = dup_check.run(repo, args)
    assert report["lineage_proposals"]
    assert any("ADVISORY (lineage)" in message for message in report["messages"])


def test_provenance_checker_reads_failure_error_and_anchor_mismatch(tmp_path: Path) -> None:
    failure = tmp_path / "failure.xml"
    failure.write_text("<testsuite><testcase><failure /></testcase></testsuite>", encoding="utf-8")
    error = tmp_path / "error.xml"
    error.write_text("<testsuite><testcase><error /></testcase></testsuite>", encoding="utf-8")
    assert provenance_check._junit_fixture_status(failure, "")[0] == "failed"
    assert provenance_check._junit_fixture_status(error, "")[0] == "errored"
    contract = SimpleNamespace(contract_id="contract-x", consumer_path="skills/shared/scripts/consumer.py")
    consumer = tmp_path / "shared/scripts/consumer.py"
    consumer.parent.mkdir(parents=True)
    consumer.write_text("# no anchor\n", encoding="utf-8")
    errors = provenance_check._validate_plugin_anchors(tmp_path, [contract])
    assert any("not anchored" in item for item in errors)


def test_setup_inspect_refuses_changed_plan_identity(tmp_path: Path) -> None:
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(
            sys,
            "argv",
            ["inspect_repo.py", "--repo-root", str(tmp_path), "--expect-plan-identity", "sha256:" + "0" * 64],
        )
        assert setup_inspect.main() == 2
    finally:
        monkeypatch.undo()


def _persist_args(repo: Path, artifact_path: str, markdown: Path) -> SimpleNamespace:
    return SimpleNamespace(
        repo_root=repo,
        artifact_path=artifact_path,
        title=None,
        subject=None,
        markdown_file=markdown,
    )


def test_debug_persistence_refuses_adapter_and_path_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class MissingBootstrapPath:
        def __init__(self, *_args: object) -> None:
            pass

        def resolve(self) -> "MissingBootstrapPath":
            return self

        @property
        def parents(self) -> list[Path]:
            return []

    monkeypatch.setattr(debug_persist, "Path", MissingBootstrapPath)
    with pytest.raises(ImportError, match="not found"):
        debug_persist._load_skill_runtime_bootstrap()
    monkeypatch.setattr(debug_persist, "Path", Path)
    markdown = tmp_path / "debug.md"
    markdown.write_text("debug", encoding="utf-8")
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "out/good.md", markdown))
    monkeypatch.setattr(debug_persist, "load_adapter", lambda _repo: {"errors": ["unhonored"], "data": {}})
    monkeypatch.setattr(debug_persist._version_verdict, "declarations_unhonored", lambda _errors: True)
    assert debug_persist.main() == 1

    monkeypatch.setattr(debug_persist, "load_adapter", lambda _repo: {"errors": [], "data": {"output_dir": "out"}})
    monkeypatch.setattr(debug_persist._version_verdict, "declarations_unhonored", lambda _errors: False)
    monkeypatch.setattr(
        debug_persist._scaffold,
        "payload_for",
        lambda *_args, **_kwargs: {"write_artifact_path": "out/good.md", "artifact_path": "out/good.md"},
    )
    monkeypatch.setattr(debug_persist._scaffold, "validator_command", lambda *_args: "validate")
    monkeypatch.setattr(debug_persist._persistence, "persist_debug_artifact", lambda **_kwargs: {"validated": True})
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "/absolute.md", markdown))
    assert debug_persist.main() == 1
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "out/other.md", markdown))
    assert debug_persist.main() == 1

    outside = tmp_path.parent / "debug-outside"
    outside.mkdir()
    (tmp_path / "out").mkdir()
    (tmp_path / "out/link.md").symlink_to(outside / "link.md")
    monkeypatch.setattr(debug_persist._scaffold, "payload_for", lambda *_args, **_kwargs: {"write_artifact_path": "out/link.md", "artifact_path": "out/link.md"})
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "out/link.md", markdown))
    assert debug_persist.main() == 1
    monkeypatch.setattr(debug_persist._scaffold, "payload_for", lambda *_args, **_kwargs: {"write_artifact_path": "other/good.md", "artifact_path": "other/good.md"})
    monkeypatch.setattr(debug_persist, "parse_args", lambda: _persist_args(tmp_path, "other/good.md", markdown))
    assert debug_persist.main() == 1


def test_debug_persistence_script_entrypoint_runs_the_main_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    markdown = tmp_path / "debug.md"
    markdown.write_text("debug", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "persist_debug_artifact.py",
            "--repo-root",
            str(tmp_path),
            "--artifact-path",
            "../bad.md",
            "--markdown-file",
            str(markdown),
        ],
    )
    with pytest.raises(SystemExit) as raised:
        runpy.run_path(
            str(ROOT / "skills/public/debug/scripts/persist_debug_artifact.py"),
            run_name="__main__",
        )
    assert raised.value.code == 1


def _load_charness(name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(ROOT / "charness"))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_charness_portable_task_lock_and_recovery_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cli = _load_charness("release_charness_lock_under_test")
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(cli, "fcntl", None)
    with cli.task_lock(repo, "task"):
        assert (repo / ".charness/tasks/.task.lock/owner").is_file()
    assert not (repo / ".charness/tasks/.task.lock").exists()
    timeout = cli.TaskLockTimeout(repo, "task", repo / ".charness/tasks/.task.lock")
    assert "task lock" in str(timeout)

    lock = repo / ".charness/tasks/.stale.lock"
    lock.mkdir(parents=True)
    lock.touch()
    os.utime(lock, (0, 0))
    monkeypatch.setattr(cli, "TASK_LOCK_TIMEOUT_SECONDS", 1.0)
    with cli.task_lock(repo, "stale"):
        assert (lock / "owner").read_text(encoding="ascii")

    disappearing = repo / ".charness/tasks/.disappear.lock"
    disappearing.mkdir(parents=True)
    real_time = cli.time.time
    removed = False

    def remove_before_stat() -> float:
        nonlocal removed
        if not removed:
            shutil.rmtree(disappearing)
            removed = True
        return real_time()

    monkeypatch.setattr(cli.time, "time", remove_before_stat)
    with cli.task_lock(repo, "disappear"):
        assert (repo / ".charness/tasks/.disappear.lock/owner").is_file()

    dead = repo / ".charness/tasks/.dead.lock"
    dead.mkdir(parents=True)
    (dead / "owner").write_text("123", encoding="ascii")
    os.utime(dead, (0, 0))
    monkeypatch.setattr(cli.os, "kill", lambda *_args: (_ for _ in ()).throw(ProcessLookupError()))
    with cli.task_lock(repo, "dead"):
        assert (dead / "owner").read_text(encoding="ascii")

    permission = repo / ".charness/tasks/.permission.lock"
    permission.mkdir(parents=True)
    (permission / "owner").write_text("123", encoding="ascii")
    os.utime(permission, (0, 0))
    monkeypatch.setattr(cli.os, "kill", lambda *_args: (_ for _ in ()).throw(PermissionError()))
    monkeypatch.setattr(cli, "TASK_LOCK_TIMEOUT_SECONDS", 0.0)
    with pytest.raises(cli.TaskLockTimeout):
        with cli.task_lock(repo, "permission"):
            pass

    live = repo / ".charness/tasks/.live.lock"
    live.mkdir(parents=True)
    (live / "owner").write_text("123", encoding="ascii")
    times = iter([0.0, 0.5, 2.0])
    monkeypatch.setattr(cli, "TASK_LOCK_TIMEOUT_SECONDS", 1.0)
    monkeypatch.setattr(cli.time, "monotonic", lambda: next(times))
    monkeypatch.setattr(cli.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(cli.os, "kill", lambda *_args: None)
    with pytest.raises(cli.TaskLockTimeout):
        with cli.task_lock(repo, "live"):
            pass

    for command in ("claim", "submit", "abort", "review"):
        args = argparse.Namespace(
            task_command=command,
            agent="agent-a",
            execution_ref="exec-a",
            summary="summary",
        )
        rendered = cli.task_lock_recovery_command(args, timeout)
        assert "charness task" in rendered and command in rendered


def test_charness_task_cas_identity_and_command_failure_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    cli = _load_charness("release_charness_task_under_test")
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(cli, "fcntl", None)
    task = {"task_id": "task", "status": "claimed", "agent_id": "agent-a", "execution_ref": "exec-a"}
    cli.create_task(repo, dict(task))
    with pytest.raises(FileExistsError):
        cli.create_task(repo, dict(task))
    with pytest.raises(cli.TaskConflict):
        cli.write_task(repo, dict(task), expected_updated_at="wrong")
    assert cli.task_identity_matches(
        argparse.Namespace(agent="other", execution_ref="exec-a"), task
    )
    assert cli.task_identity_matches(
        argparse.Namespace(agent="agent-a", execution_ref="other"), task
    )
    assert cli.task_identity_matches(
        argparse.Namespace(agent="agent-a", execution_ref="exec-a"),
        task,
        require_distinct_reviewer=True,
    )

    mismatch_args = argparse.Namespace(
        repo_root=repo, task_id="task", agent="agent-a", execution_ref="other", summary="retry"
    )
    assert cli.cmd_task_claim(mismatch_args) == 1

    existing = {**task, "status": "claimed"}
    reads = iter([None, existing])
    monkeypatch.setattr(cli, "read_task", lambda *_args: next(reads))
    monkeypatch.setattr(cli, "create_task", lambda *_args, **_kwargs: (_ for _ in ()).throw(FileExistsError("race")))
    race_args = argparse.Namespace(
        repo_root=repo, task_id="race", agent="agent-a", execution_ref="exec-a", summary="race"
    )
    assert cli.cmd_task_claim(race_args) == 1
    monkeypatch.undo()

    cli = _load_charness("release_charness_task_commands_under_test")
    repo = tmp_path / "commands"
    repo.mkdir()
    claimed = {"task_id": "task", "status": "claimed", "agent_id": "agent-a", "execution_ref": "exec-a"}
    cli.write_task(repo, dict(claimed))
    submit_wrong = argparse.Namespace(
        repo_root=repo, task_id="task", agent="other", execution_ref="exec-a", result_carrier="result", summary="summary"
    )
    assert cli.cmd_task_submit(submit_wrong) == 1
    monkeypatch.setattr(cli, "write_task", lambda *_args, **_kwargs: (_ for _ in ()).throw(cli.TaskConflict("submit race")))
    submit_ok = argparse.Namespace(
        repo_root=repo, task_id="task", agent="agent-a", execution_ref="exec-a", result_carrier="result", summary="summary"
    )
    assert cli.cmd_task_submit(submit_ok) == 1
    monkeypatch.undo()
    cli.write_task(repo, dict(claimed))
    abort_wrong = argparse.Namespace(
        repo_root=repo, task_id="task", agent="other", execution_ref="exec-a", reason="reason"
    )
    assert cli.cmd_task_abort(abort_wrong) == 1
    monkeypatch.setattr(cli, "write_task", lambda *_args, **_kwargs: (_ for _ in ()).throw(cli.TaskConflict("abort race")))
    abort_ok = argparse.Namespace(
        repo_root=repo, task_id="task", agent="agent-a", execution_ref="exec-a", reason="reason"
    )
    assert cli.cmd_task_abort(abort_ok) == 1
    monkeypatch.undo()
    missing_review = argparse.Namespace(repo_root=repo, task_id="missing", agent="parent", execution_ref="exec", verdict="approve", summary="summary")
    assert cli.cmd_task_review(missing_review) == 1
    submitted = {**claimed, "status": "submitted"}
    cli.write_task(repo, submitted)
    same_reviewer = argparse.Namespace(repo_root=repo, task_id="task", agent="agent-a", execution_ref="exec-a", verdict="approve", summary="summary")
    assert cli.cmd_task_review(same_reviewer) == 1
    monkeypatch.setattr(cli, "write_task", lambda *_args, **_kwargs: (_ for _ in ()).throw(cli.TaskConflict("review race")))
    distinct_reviewer = argparse.Namespace(repo_root=repo, task_id="task", agent="parent", execution_ref="exec-a", verdict="approve", summary="summary")
    assert cli.cmd_task_review(distinct_reviewer) == 1
    assert "rejected" in capsys.readouterr().out


def test_charness_main_projects_task_lock_timeout_and_reraises_other_commands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cli = _load_charness("release_charness_main_under_test")
    timeout = cli.TaskLockTimeout(tmp_path, "task", tmp_path / ".charness/tasks/.task.lock")

    class Parser:
        def __init__(self, namespace: argparse.Namespace):
            self.namespace = namespace

        def parse_args(self, _argv: list[str]) -> argparse.Namespace:
            return self.namespace

    task_args = argparse.Namespace(
        command="task",
        verbose=False,
        check=False,
        task_command="claim",
        agent="agent",
        execution_ref="exec",
        summary="summary",
        func=lambda _args: (_ for _ in ()).throw(timeout),
    )
    monkeypatch.setattr(cli, "build_parser", lambda: Parser(task_args))
    monkeypatch.setattr(cli, "maybe_record_self_version_state", lambda _args: None)
    assert cli.main(["task"]) == 1

    other_args = argparse.Namespace(
        command="other",
        verbose=False,
        check=False,
        func=lambda _args: (_ for _ in ()).throw(timeout),
    )
    monkeypatch.setattr(cli, "build_parser", lambda: Parser(other_args))
    with pytest.raises(cli.TaskLockTimeout):
        cli.main(["other"])
