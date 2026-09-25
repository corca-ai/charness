"""Command-time orchestration guards: parallel window, verdict channel, discard (#868)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.hooks import host_hook_command_guards as guards
from scripts.hooks import host_hook_command_guard_install as install
from scripts.hooks import host_hook_registry

pytestmark = pytest.mark.boundary_contract(
    reason="hook entry scripts and fresh-import probes cross real process and import boundaries"
)

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_SCRIPTS = {
    "parallel-window": REPO_ROOT / "scripts" / "host_parallel_window_hook.py",
    "verdict-channel": REPO_ROOT / "scripts" / "host_verdict_channel_hook.py",
    "discard-worktree": REPO_ROOT / "scripts" / "host_discard_worktree_hook.py",
}


def blocked(command: str, guard: str, **kwargs) -> dict | None:
    return guards.check_command(command, guard, **kwargs)


def _isolate_runtime_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Point the runtime at a tmp sibling and drop the ambient auto markers.

    Importing anything downstream of `scripts.task_run.task_run_git` runs
    `configure_runtime_environment` for the real repo, leaving
    CHARNESS_RUNTIME_ROOT_AUTO=1 with the real repo's key behind. While those
    linger, `runtime_root` silently ignores a pointed CHARNESS_RUNTIME_ROOT
    for any other repo and routes records into the shared auto tree, so
    repeat/escalation assertions observe other tests' history. Deleting both
    markers (the `test_bootstrap_runtime` pattern) takes the configured
    branch, where the sibling layout below is honored deterministically.
    """
    runtime = tmp_path / "runtime"
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(runtime))
    monkeypatch.delenv("CHARNESS_RUNTIME_ROOT_AUTO", raising=False)
    monkeypatch.delenv("CHARNESS_RUNTIME_REPO_KEY", raising=False)
    return runtime


def test_parallel_window_blocks_long_foreground_sleep() -> None:
    found = blocked("sleep 20", guards.PARALLEL_WINDOW)
    assert found is not None
    assert found["pattern_id"] == "long-sleep"


def test_parallel_window_passes_backgrounded_and_short_sleep() -> None:
    assert blocked("sleep 20 &", guards.PARALLEL_WINDOW) is None
    assert blocked("sleep 2", guards.PARALLEL_WINDOW) is None


def test_parallel_window_override_needs_a_stated_reason() -> None:
    assert (
        blocked("sleep 20 #window-ok: waiting for the lane verdict", guards.PARALLEL_WINDOW)
        is None
    )
    assert blocked("sleep 20 #window-ok:", guards.PARALLEL_WINDOW) is not None


def test_parallel_window_blocks_bundles_not_single_files() -> None:
    assert blocked("python3 -m pytest tests/ -x -q", guards.PARALLEL_WINDOW) is not None
    assert blocked("pytest", guards.PARALLEL_WINDOW) is not None
    assert (
        blocked(
            "python3 -m pytest tests/charness_cli/test_task_run_scope.py -q",
            guards.PARALLEL_WINDOW,
        )
        is None
    )


def test_parallel_window_blocks_foreground_lane_launch_and_wait() -> None:
    assert (
        blocked("charness task run --lane x --scope pkg --prompt p --effort xhigh", guards.PARALLEL_WINDOW)
        is not None
    )
    assert (
        blocked(
            "charness task run --lane x --scope pkg --prompt p --effort xhigh --detach",
            guards.PARALLEL_WINDOW,
        )
        is None
    )
    waited = blocked("charness task wait lane-a", guards.PARALLEL_WINDOW)
    assert waited is not None
    assert (
        blocked("charness task wait lane-a #window-ok: quick check", guards.PARALLEL_WINDOW)
        is not None
    )


def test_verdict_channel_blocks_masked_composition() -> None:
    assert blocked("pytest tests/ -q; echo done", guards.VERDICT_CHANNEL) is not None
    assert blocked("git push origin main | tail -5", guards.VERDICT_CHANNEL) is not None
    assert (
        blocked("charness task run --lane x || echo failed", guards.VERDICT_CHANNEL)
        is not None
    )


def test_verdict_channel_passes_captured_and_reraised_status() -> None:
    assert (
        blocked(
            "pytest tests/ -q > /tmp/lane.log; rc=$?; tail -3 /tmp/lane.log; exit $rc",
            guards.VERDICT_CHANNEL,
        )
        is None
    )


def test_verdict_channel_passes_combined_test_reraise() -> None:
    assert (
        blocked(
            "pytest tests/ -q > /tmp/lane.log; a=$?; b=1; [ $a = 0 ] && [ $b = 1 ]",
            guards.VERDICT_CHANNEL,
        )
        is None
    )


def test_verdict_channel_blocks_truncated_record() -> None:
    assert (
        blocked("cat /tmp/lane-result.json | cut -c1-200", guards.VERDICT_CHANNEL)
        is not None
    )
    assert (
        blocked(
            "cat /tmp/lane-result.json | cut -c1-200 #verdict-ok: previewing shape",
            guards.VERDICT_CHANNEL,
        )
        is None
    )


def test_verdict_channel_quoted_description_is_not_the_command() -> None:
    assert (
        blocked(
            "git commit -m 'run pytest; echo done' -- tests/test_x.py",
            guards.VERDICT_CHANNEL,
        )
        is None
    )


def test_verdict_channel_heredoc_body_is_not_the_command() -> None:
    command = "cat > /tmp/notes.md <<'EOF'\npytest tests/ -q; echo done\ngit push | tail\nEOF\n"
    assert blocked(command, guards.VERDICT_CHANNEL) is None


def test_discard_blocks_destructive_shapes() -> None:
    for command in (
        "git checkout -- pkg/module.py",
        "git checkout .",
        "git restore pkg/module.py",
        "git reset --hard HEAD",
        "git clean -fd",
        "git clean -d -f",
        "git stash drop",
        "git worktree remove --force /tmp/lane",
    ):
        assert blocked(command, guards.DISCARD_WORKTREE) is not None, command


def test_discard_passes_staged_only_and_overrides() -> None:
    assert blocked("git restore --staged", guards.DISCARD_WORKTREE) is None
    assert blocked("git checkout main", guards.DISCARD_WORKTREE) is None
    assert (
        blocked(
            "git checkout -- pkg/module.py #discard-ok: dropping my own stray hunk",
            guards.DISCARD_WORKTREE,
        )
        is None
    )
    assert (
        blocked("git checkout -- pkg/module.py #discard-ok:", guards.DISCARD_WORKTREE)
        is not None
    )


def test_discard_quoted_description_is_not_the_command() -> None:
    assert (
        blocked(
            'git commit -m "never git checkout -- paths" -- pkg/module.py',
            guards.DISCARD_WORKTREE,
        )
        is None
    )


def test_hook_script_exit_codes(tmp_path: Path, monkeypatch) -> None:
    runtime = tmp_path / "runtime"
    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(runtime))

    def run(command: str, guard: str, raw: str | None = None) -> subprocess.CompletedProcess[str]:
        payload = (
            raw
            if raw is not None
            else json.dumps(
                {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(tmp_path)}
            )
        )
        env = dict(os.environ, CHARNESS_RUNTIME_ROOT=str(runtime))
        # Drop the ambient auto markers (see _isolate_runtime_root) so the
        # child honors the pointed root instead of the shared auto tree.
        env.pop("CHARNESS_RUNTIME_ROOT_AUTO", None)
        env.pop("CHARNESS_RUNTIME_REPO_KEY", None)
        return subprocess.run(
            [sys.executable, str(HOOK_SCRIPTS[guard])],
            input=payload,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

    blocked_call = run("sleep 30", "parallel-window")
    assert blocked_call.returncode == 2
    assert "parallel-window" in blocked_call.stderr
    assert run("sleep 30 &", "parallel-window").returncode == 0
    assert run("sleep 30", "discard-worktree").returncode == 0
    assert run("sleep 30", "parallel-window", raw="{not json").returncode == 0
    assert run("sleep 30", "parallel-window", raw="").returncode == 0
    assert run("git checkout -- x.py", "discard-worktree").returncode == 2


def test_malformed_payload_decide_is_fail_open() -> None:
    from scripts import host_command_guard_hook as hook

    assert hook.decide(None, "parallel-window") == (0, "")
    assert hook.decide({"tool_input": {}}, "parallel-window") == (0, "")
    assert hook.decide({"tool_input": {"command": 42}}, "parallel-window") == (0, "")


def test_adapter_pattern_blocks_only_in_its_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "command-guards.local.yaml").write_text(
        "extra_verdict_commands:\n"
        "  - task-verify\n"
        "extra_patterns:\n"
        "  parallel-window:\n"
        "    - id: repo-slow-publish\n"
        "      pattern: 'publish\\s+preview'\n"
        "      reason: the preview publish idles the turn here\n"
        "      overridable: true\n",
        encoding="utf-8",
    )
    other = tmp_path / "other"
    other.mkdir()

    assert (
        blocked("task-verify --lane x | tail -3", guards.VERDICT_CHANNEL, repo_root=repo)
        is not None
    )
    assert (
        blocked("task-verify --lane x | tail -3", guards.VERDICT_CHANNEL, repo_root=other)
        is None
    )
    assert blocked("publish preview", guards.PARALLEL_WINDOW, repo_root=repo) is not None
    assert blocked("publish preview", guards.PARALLEL_WINDOW, repo_root=other) is None


def test_malformed_adapter_fails_open(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "command-guards.local.yaml").write_text(
        "extra_patterns: [unclosed\n", encoding="utf-8"
    )

    assert blocked("publish preview", guards.PARALLEL_WINDOW, repo_root=repo) is None
    assert blocked("sleep 30", guards.PARALLEL_WINDOW, repo_root=repo) is not None
    assert blocked("echo hello", guards.PARALLEL_WINDOW, repo_root=repo) is None


def test_registry_carries_four_intents() -> None:
    keys = [intent.key for intent in host_hook_registry.SIBLING_HOOK_INTENTS]
    assert keys == [
        "skill_anchor_edit_guard",
        "command_guard_parallel_window",
        "command_guard_verdict_channel",
        "command_guard_discard_worktree",
    ]


def _adapter(*sections: str) -> dict:
    return {section: {"claude": "enabled"} for section in sections}


def test_reconcile_installs_and_status_reports_per_host(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    adapter = _adapter("command_guard_parallel_window")

    actions = host_hook_registry.reconcile_sibling_hooks(
        repo, adapter=adapter, home=home
    )

    assert actions["command_guard_parallel_window"]["claude"]["result"]["action"] in {
        "installed",
        "noop",
    }
    assert (
        "codex"
        in actions["command_guard_parallel_window"]["codex"].get("error", "")
        or "codex" in actions["command_guard_parallel_window"]["codex"].get("result", {}).get("reason", "")
    )
    statuses = host_hook_registry.sibling_hook_statuses(
        repo, adapter=adapter, home=home
    )
    window = statuses["command_guard_parallel_window"]
    assert window["hosts"]["claude"]["intent"] == "enabled"
    assert window["hosts"]["claude"]["actual"]["present"] is True
    assert window["in_sync"] is True

    removed = host_hook_registry.reconcile_sibling_hooks(repo, adapter={}, home=home)
    assert removed["command_guard_parallel_window"]["claude"]["result"]["action"] in {
        "removed",
        "absent",
        "not_installed",
    }
    assert (
        host_hook_registry.sibling_hook_statuses(repo, adapter={}, home=home)[
            "command_guard_parallel_window"
        ]["in_sync"]
        is True
    )


def test_repeat_block_within_a_day_escalates(tmp_path: Path, monkeypatch) -> None:
    # The runtime root must sit OUTSIDE the installing repo
    # (scripts.runtime_bootstrap refuses a repo-local runtime), so the repo
    # under test and the runtime are siblings, not parent and child.
    repo = tmp_path / "repo"
    repo.mkdir()
    _isolate_runtime_root(monkeypatch, tmp_path)
    first = guards.record_block(
        repo,
        {"guard": guards.PARALLEL_WINDOW, "pattern_id": "long-sleep", "reason": "idle"},
        "sleep 30",
    )
    second = guards.record_block(
        repo,
        {"guard": guards.PARALLEL_WINDOW, "pattern_id": "long-sleep", "reason": "idle"},
        "sleep 40",
    )

    assert first is not None and "escalation" not in first["facts"]
    assert second is not None
    assert guards.HOOK_REPEAT_ESCALATION in second["facts"]["escalation"]

    other = guards.record_block(
        repo,
        {"guard": guards.DISCARD_WORKTREE, "pattern_id": "reset-hard", "reason": "x"},
        "git reset --hard",
    )
    assert other is not None and "escalation" not in other["facts"]


def _exec_module_fresh(path: Path, name: str):
    """Execute a module body with the repo root absent from sys.path.

    Covers the bootstrap `sys.path.insert` line every scripts module owns:
    the loader finds the file by path, so the body's own bootstrap is what
    makes the absolute `scripts.*` imports that follow resolve.
    """
    import importlib.util

    from tests.module_eviction import evict_new_modules

    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    saved = sys.path[:]
    root = str(REPO_ROOT)
    sys.path[:] = [
        entry
        for entry in sys.path
        if entry not in ("", root) and os.path.abspath(entry) != root
    ]
    before = set(sys.modules)
    try:
        # Register before exec: dataclass processing resolves the defining
        # class via sys.modules[cls.__module__] during module execution.
        sys.modules[name] = module
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved
        # Owner-side eviction (#781): drops the fresh entry and anything the
        # exec pulled in, without stranding rebound parent attributes.
        evict_new_modules(before)
    return module


def test_fresh_import_executes_bootstrap_inserts() -> None:
    for relative, name in (
        ("scripts/hooks/host_hook_command_guards.py", "fresh_guards"),
        ("scripts/hooks/host_hook_command_patterns.py", "fresh_patterns"),
        ("scripts/hooks/host_hook_command_guard_install.py", "fresh_install"),
        ("scripts/host_command_guard_hook.py", "fresh_hook"),
        ("scripts/host_parallel_window_hook.py", "fresh_window"),
        ("scripts/host_verdict_channel_hook.py", "fresh_verdict"),
        ("scripts/host_discard_worktree_hook.py", "fresh_discard"),
    ):
        _exec_module_fresh(REPO_ROOT / relative, name)


def test_strip_and_split_fail_open_on_hostile_input() -> None:
    assert guards.strip_non_executable(None) is None  # type: ignore[arg-type]
    assert guards.split_segments(None) == [None]  # type: ignore[arg-type]
    assert guards.strip_non_executable('echo "a\\\\b" && sleep 30') is not None
    assert guards.strip_non_executable("echo a <<123") is not None


def test_window_hit_skips_invalid_extra_pattern() -> None:
    bad = guards.GuardPattern(id="bad", pattern="([", reason="never compiles")
    assert (
        guards.check_parallel_window("sleep 30", extra=[bad]) is not None
    )
    assert guards._window_hit(bad, ["sleep 30"]) is False
    assert guards._single_test_file_selected("") is False
    assert guards._single_test_file_selected("echo hi") is False
    assert guards._final_test_reraise([]) is False


def test_verdict_override_excuses_a_masked_command() -> None:
    assert (
        guards.check_verdict_channel(
            "pytest tests/ -q; echo done #verdict-ok: log already shipped",
        )
        is None
    )
    assert guards.check_command("echo hi", "no-such-guard") is None


def test_evaluate_reports_blocks_and_escalation(tmp_path: Path, monkeypatch) -> None:
    # Sibling layout: the runtime root must sit outside the installing repo
    # (scripts.runtime_bootstrap refuses a repo-local runtime).
    repo = tmp_path / "repo"
    repo.mkdir()
    _isolate_runtime_root(monkeypatch, tmp_path)
    first = guards.evaluate_hook_payload(
        {"tool_input": {"command": "sleep 30"}, "cwd": str(repo)},
        repo,
    )
    assert first is not None and first["blocked"] is True
    assert "parallel-window" in first["message"]
    second = guards.evaluate_hook_payload(
        {"tool_input": {"command": "sleep 40"}, "cwd": str(repo)},
        repo,
    )
    assert second is not None and guards.HOOK_REPEAT_ESCALATION in second["message"]
    assert (
        guards.evaluate_hook_payload(
            {"tool_input": {"command": "echo hi"}, "cwd": str(repo)}, repo
        )
        == {"blocked": False}
    )
    assert guards.evaluate_hook_payload(None, repo) is None


def test_evaluate_fails_open_when_a_guard_raises(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        guards, "check_command", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    assert (
        guards.evaluate_hook_payload(
            {"tool_input": {"command": "sleep 30"}}, tmp_path
        )
        is None
    )
    assert guards.run_guards("sleep 30") == []


def test_repo_root_for_edge_shapes(tmp_path: Path, monkeypatch) -> None:
    assert guards.repo_root_for("") is None
    assert guards.repo_root_for(None) is None
    assert guards.repo_root_for("/") is None
    monkeypatch.setattr(Path, "resolve", lambda self: (_ for _ in ()).throw(OSError("gone")))
    try:
        assert guards.repo_root_for(str(tmp_path)) is None
    finally:
        monkeypatch.undo()
    monkeypatch.setattr(
        Path, "is_file", lambda self: (_ for _ in ()).throw(OSError("gone"))
    )
    try:
        assert guards.load_adapter_extras(tmp_path) == {
            "extra_verdict_commands": [],
            "extra_patterns": {},
        }
    finally:
        monkeypatch.undo()


def test_adapter_extras_without_yaml_and_with_bad_rows(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "command-guards.local.yaml").write_text(
        '{"extra_verdict_commands": ["task-verify"]}', encoding="utf-8"
    )
    monkeypatch.setitem(sys.modules, "yaml", None)
    try:
        extras = guards.load_adapter_extras(repo)
    finally:
        monkeypatch.undo()
    assert extras["extra_verdict_commands"] == ["task-verify"]
    (repo / ".agents" / "command-guards.local.yaml").write_text("[1, 2]", encoding="utf-8")
    assert guards.load_adapter_extras(repo) == {
        "extra_verdict_commands": [],
        "extra_patterns": {},
    }
    (repo / ".agents" / "command-guards.local.yaml").write_text(
        "extra_verdict_commands: [ok, 42]\n"
        "extra_patterns:\n"
        "  parallel-window: not-a-list\n"
        "  verdict-channel:\n"
        "    - not-a-mapping\n"
        "    - {id: only-id}\n"
        "    - {id: bad-regex, pattern: '([', reason: 'x'}\n"
        "    - {id: good, pattern: 'zzz-no-match', reason: 'y', overridable: false}\n"
        "  no-such-guard:\n"
        "    - {id: x, pattern: 'y', reason: 'z'}\n",
        encoding="utf-8",
    )
    extras = guards.load_adapter_extras(repo)
    assert extras["extra_verdict_commands"] == ["ok"]
    assert [row.id for row in extras["extra_patterns"]["verdict-channel"]] == ["good"]


def test_adapter_from_file_branches(tmp_path: Path) -> None:
    assert install.adapter_from_file(None) == {}
    missing = tmp_path / "absent.yaml"
    try:
        install.adapter_from_file(missing)
    except ValueError as exc:
        assert "could not read" in str(exc)
    else:
        raise AssertionError("missing adapter file must fail")
    empty = tmp_path / "empty.yaml"
    empty.write_text("", encoding="utf-8")
    assert install.adapter_from_file(empty) == {}
    listed = tmp_path / "list.yaml"
    listed.write_text("- a\n", encoding="utf-8")
    try:
        install.adapter_from_file(listed)
    except ValueError as exc:
        assert "must contain a mapping" in str(exc)
    else:
        raise AssertionError("non-mapping adapter must fail")
    valid = tmp_path / "adapter.yaml"
    valid.write_text("command_guard_parallel_window:\n  claude: enabled\n", encoding="utf-8")
    assert install.adapter_from_file(valid) == {
        "command_guard_parallel_window": {"claude": "enabled"}
    }


def test_status_payload_reports_sync(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    payload, code = install.status_payload(repo, home, {})
    assert code == 0
    assert set(payload["intents"]) == {
        "skill_anchor_edit_guard",
        "command_guard_parallel_window",
        "command_guard_verdict_channel",
        "command_guard_discard_worktree",
    }


def test_reconcile_records_install_errors(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    (home / ".claude" / "settings.json").write_text("{broken", encoding="utf-8")
    actions = host_hook_registry.reconcile_sibling_hooks(
        repo,
        adapter={"command_guard_parallel_window": {"claude": "enabled"}},
        home=home,
    )
    assert "error" in actions["command_guard_parallel_window"]["claude"]
    actions = host_hook_registry.reconcile_sibling_hooks(
        repo,
        adapter={"command_guard_parallel_window": {"codex": "enabled"}},
        home=home,
    )
    assert "codex" in actions["command_guard_parallel_window"]["codex"]["error"]


def test_record_block_fails_open(tmp_path: Path, monkeypatch) -> None:
    import scripts.task_run.task_run_friction as friction

    monkeypatch.setattr(
        guards, "runtime_root", lambda *a, **k: (_ for _ in ()).throw(OSError("gone"))
    )
    assert (
        guards.record_block(tmp_path, {"guard": "parallel-window"}, "sleep 30") is None
    )
    monkeypatch.setattr(
        friction,
        "append_friction_event",
        lambda *a, **k: (_ for _ in ()).throw(OSError("gone")),
    )
    assert (
        guards.record_block(tmp_path, {"guard": "parallel-window"}, "sleep 30") is None
    )


def test_hook_decide_all_branch_and_unknown_guard(tmp_path: Path, monkeypatch) -> None:
    from scripts import host_command_guard_hook as hook

    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(tmp_path / "runtime"))
    code, message = hook.decide(
        {"tool_input": {"command": "sleep 30"}, "cwd": str(tmp_path)}, "all"
    )
    assert code == 2 and "parallel-window" in message
    assert hook.decide({"tool_input": {"command": "echo hi"}}, "all") == (0, "")
    assert hook.decide({"tool_input": {"command": "sleep 30"}}, "nope") == (0, "")
    monkeypatch.setattr(
        guards,
        "evaluate_hook_payload",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    assert hook.decide({"tool_input": {"command": "sleep 30"}}, "all") == (0, "")
    monkeypatch.setattr(
        guards, "check_command", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    assert hook.decide({"tool_input": {"command": "sleep 30"}}, "parallel-window") == (0, "")


def test_hook_main_entry_points(tmp_path: Path, monkeypatch) -> None:
    import runpy

    from scripts import host_command_guard_hook as hook

    monkeypatch.setenv("CHARNESS_RUNTIME_ROOT", str(tmp_path / "runtime"))
    monkeypatch.setattr(sys, "stdin", __import__("io").StringIO(""))
    with pytest.raises(SystemExit) as clean:
        runpy.run_path(str(REPO_ROOT / "scripts" / "host_command_guard_hook.py"), run_name="__main__")
    assert clean.value.code == 2 or clean.value.code == 0
    assert hook.main(["--guard", "parallel-window"]) == 0
    for script in (
        "host_parallel_window_hook.py",
        "host_verdict_channel_hook.py",
        "host_discard_worktree_hook.py",
    ):
        with pytest.raises(SystemExit) as exited:
            runpy.run_path(str(REPO_ROOT / "scripts" / script), run_name="__main__")
        assert exited.value.code == 0
    with pytest.raises(SystemExit) as blocked_exit:
        monkeypatch.setattr(
            sys, "stdin", __import__("io").StringIO('{"tool_input": {"command": "sleep 30"}}')
        )
        runpy.run_path(str(REPO_ROOT / "scripts" / "host_parallel_window_hook.py"), run_name="__main__")
    assert blocked_exit.value.code == 2


def test_hooks_status_command_reports_intents(tmp_path: Path, monkeypatch) -> None:
    from tests.charness_cli.support import CLI, load_cli_module

    cli = load_cli_module("charness_hooks_status_cli", CLI)
    monkeypatch.setattr(cli, "_load_task_run_lib", lambda _args: object())
    emitted: list[dict] = []
    monkeypatch.setattr(cli, "emit_yaml", emitted.append)

    code = cli.cmd_hooks_status(
        __import__("argparse").Namespace(
            repo_root=tmp_path, home_root=tmp_path, adapter_file=None
        )
    )

    assert code == 0
    assert set(emitted[-1]["intents"]) >= {"command_guard_parallel_window"}

    code = cli.cmd_task_run_detached(
        __import__("argparse").Namespace(dry_run=True)
    ) if False else code
    with pytest.raises(cli.CharnessError, match="--detach cannot be combined"):
        cli.cmd_task_run_detached(__import__("argparse").Namespace(dry_run=True))


def test_invalid_extra_pattern_compiles_to_skip_without_match() -> None:
    # The parallel-window checker narrows through `_window_hit` first, so an
    # invalid extra never reaches `_pattern_block` there; the verdict checker
    # calls `_pattern_block` directly, forcing `re.compile` through the bad
    # entry and covering the `except re.error` skip.
    bad = guards.GuardPattern(id="bad", pattern="([", reason="never compiles")
    assert guards.check_parallel_window("echo hello", extra=[bad]) is None
    found = guards.check_verdict_channel(
        "task-verify --lane x | tail -3",
        extra_commands=["task-verify"],
        extra=[bad],
    )
    assert found is not None and found["pattern_id"] != "bad"


def test_check_command_fails_open_when_checker_raises(monkeypatch) -> None:
    # The dispatch tail (`except Exception: return None`) only runs when a
    # checker itself blows up; force it so a guard never breaks the command.
    monkeypatch.setattr(
        guards,
        "check_parallel_window",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    assert guards.check_command("sleep 30", guards.PARALLEL_WINDOW) is None


def test_repo_root_for_survives_unreadable_markers(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        Path, "exists", lambda self: (_ for _ in ()).throw(OSError("gone"))
    )
    assert guards.repo_root_for(str(tmp_path)) is None


def test_adapter_extras_without_yaml_and_malformed_json(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "command-guards.local.yaml").write_text(
        "extra_patterns: [unclosed\n", encoding="utf-8"
    )
    monkeypatch.setitem(sys.modules, "yaml", None)
    try:
        assert guards.load_adapter_extras(repo) == {
            "extra_verdict_commands": [],
            "extra_patterns": {},
        }
    finally:
        monkeypatch.undo()


def test_check_command_routes_parallel_window_extras(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "command-guards.local.yaml").write_text(
        "extra_patterns:\n"
        "  parallel-window:\n"
        "    - id: repo-slow-publish\n"
        "      pattern: 'publish\\s+preview'\n"
        "      reason: the preview publish idles the turn here\n"
        "      overridable: true\n",
        encoding="utf-8",
    )
    found = guards.check_command(
        "publish preview", guards.PARALLEL_WINDOW, repo_root=repo
    )
    assert found is not None and found["pattern_id"] == "repo-slow-publish"


def test_record_block_fails_open_when_append_raises(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _isolate_runtime_root(monkeypatch, tmp_path)
    monkeypatch.setattr(
        guards._friction,
        "append_friction_event",
        lambda *a, **k: (_ for _ in ()).throw(OSError("gone")),
    )
    assert (
        guards.record_block(
            repo,
            {"guard": guards.PARALLEL_WINDOW, "pattern_id": "x", "reason": "y"},
            "sleep 30",
        )
        is None
    )


def test_evaluate_rejects_malformed_tool_input(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    assert guards.evaluate_hook_payload({"tool_input": ["sleep 30"]}, repo) is None
    assert guards.evaluate_hook_payload({"tool_input": {"command": 42}}, repo) is None


def test_run_guards_returns_blocks() -> None:
    found = guards.run_guards("sleep 30")
    assert len(found) == 1 and found[0]["pattern_id"] == "long-sleep"
    assert guards.run_guards("echo hi") == []


def test_hook_decide_second_block_carries_escalation(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import host_command_guard_hook as hook

    repo = tmp_path / "repo"
    repo.mkdir()
    _isolate_runtime_root(monkeypatch, tmp_path)
    payload = {"tool_input": {"command": "sleep 30"}, "cwd": str(repo)}
    first_code, first_message = hook.decide(payload, "parallel-window")
    second_code, second_message = hook.decide(payload, "parallel-window")
    assert (first_code, second_code) == (2, 2)
    assert guards.HOOK_REPEAT_ESCALATION not in first_message
    assert guards.HOOK_REPEAT_ESCALATION in second_message


def test_adapter_from_file_without_yaml(tmp_path: Path, monkeypatch) -> None:
    adapter = tmp_path / "adapter.yaml"
    adapter.write_text("intents: {}\n", encoding="utf-8")
    monkeypatch.setitem(sys.modules, "yaml", None)
    try:
        with pytest.raises(ValueError, match="needs PyYAML"):
            install.adapter_from_file(adapter)
    finally:
        monkeypatch.undo()


def test_hooks_status_command_wraps_adapter_errors(
    tmp_path: Path, monkeypatch
) -> None:
    from tests.charness_cli.support import CLI, load_cli_module

    cli = load_cli_module("charness_hooks_status_errors_cli", CLI)
    monkeypatch.setattr(cli, "_load_task_run_lib", lambda _args: object())
    with pytest.raises(cli.CharnessError, match="could not read"):
        cli.cmd_hooks_status(
            __import__("argparse").Namespace(
                repo_root=tmp_path,
                home_root=tmp_path,
                adapter_file=tmp_path / "absent.yaml",
            )
        )
