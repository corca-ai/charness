from __future__ import annotations

import argparse
import io
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.cli.cmd_goal as cmd_goal
import scripts.hooks.host_hook_goal_reinject_install as reinject_install
import scripts.host_goal_reinject_hook as reinject_hook


def _checkout_with_helper(base: Path) -> Path:
    root = base / "checkout"
    helper_dir = root / "skills" / "public" / "achieve" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "goal_run_pickup.py").write_text("# pickup helper\n", encoding="utf-8")
    return root


def test_resolve_helper_embedded_repo_root(tmp_path: Path, monkeypatch) -> None:
    checkout = _checkout_with_helper(tmp_path)
    monkeypatch.setattr(cmd_goal._bootstrap, "EMBEDDED_REPO_ROOT", checkout)
    monkeypatch.setattr(cmd_goal, "ensure_checkout", lambda *args, **kwargs: None)
    args = argparse.Namespace(charness_checkout=None, home_root=tmp_path)
    assert cmd_goal._resolve_goal_run_helper_repo_root(args) == checkout


def test_resolve_helper_repo_root_fallback(tmp_path: Path, monkeypatch) -> None:
    checkout = _checkout_with_helper(tmp_path)
    seen: dict[str, object] = {}

    def _fake_ensure(repo_root: Path, **kwargs: object) -> None:
        seen["repo_root"] = repo_root
        seen.update(kwargs)

    monkeypatch.setattr(cmd_goal._bootstrap, "EMBEDDED_REPO_ROOT", None)
    monkeypatch.setattr(cmd_goal, "resolve_repo_root", lambda *args: (checkout, True))
    monkeypatch.setattr(cmd_goal, "ensure_checkout", _fake_ensure)
    args = argparse.Namespace(charness_checkout=None, home_root=tmp_path)
    assert cmd_goal._resolve_goal_run_helper_repo_root(args) == checkout
    assert seen.get("managed") is True


def test_cmd_goal_run_malformed_payload(tmp_path: Path, monkeypatch, capsys) -> None:
    checkout = _checkout_with_helper(tmp_path)
    target = tmp_path / "target"
    target.mkdir()
    monkeypatch.setattr(cmd_goal, "ensure_checkout", lambda *args, **kwargs: None)
    monkeypatch.setattr(cmd_goal, "resolve_repo_python", lambda _root: "python3")
    monkeypatch.setattr(
        cmd_goal,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout='{"not": "an envelope"}', stderr="helper warn\n", returncode=0
        ),
    )

    def _bad_payload(_stdout: str, _helper: str) -> object:
        raise cmd_goal.CharnessError("unparseable helper output")

    emitted: list[object] = []
    monkeypatch.setattr(cmd_goal, "parse_repo_script_payload", _bad_payload)
    monkeypatch.setattr(cmd_goal, "emit_yaml", emitted.append)
    args = argparse.Namespace(
        charness_checkout=checkout, home_root=tmp_path, repo_root=target, objective="ship it"
    )
    assert cmd_goal.cmd_goal_run(args) == 0
    assert emitted == [{"helper_stdout": '{"not": "an envelope"}'}]
    assert capsys.readouterr().err == "helper warn\n"


def test_reconcile_codex_enabled_is_unsupported(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    actions = reinject_install.reconcile_goal_reinject_hooks(
        repo_root,
        adapter={"goal_reinject": {"claude": "disabled", "codex": "enabled"}},
        home=home,
    )
    assert actions["codex"]["intent"] == "enabled"
    assert actions["codex"]["error"] == reinject_install.CODEX_UNSUPPORTED_REASON


def test_repo_root_for_branches(tmp_path: Path, monkeypatch) -> None:
    assert reinject_hook.repo_root_for(None) is None
    assert reinject_hook.repo_root_for("") is None

    repo = tmp_path / "repo"
    repo.mkdir()
    # tmp ancestors may carry hook markers; isolate the negative case.
    monkeypatch.setattr(Path, "exists", lambda self: False)
    monkeypatch.setattr(Path, "is_dir", lambda self: False)
    assert reinject_hook.repo_root_for(str(repo)) is None
    monkeypatch.undo()
    (repo / ".git").mkdir()
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    assert reinject_hook.repo_root_for(str(nested)) == repo


def test_repo_root_for_oserror_branches(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    def _boom(self: Path) -> bool:
        raise OSError("stat unavailable")

    monkeypatch.setattr(Path, "exists", _boom)
    monkeypatch.setattr(Path, "is_dir", lambda self: False)
    assert reinject_hook.repo_root_for(str(repo)) is None


def test_repo_root_for_resolve_failure(monkeypatch) -> None:
    def _boom(self: Path, *args: object, **kwargs: object) -> Path:
        raise OSError("resolve unavailable")

    monkeypatch.setattr(Path, "resolve", _boom)
    assert reinject_hook.repo_root_for("/somewhere") is None


def _write_state(repo: Path, payload: object) -> None:
    state_path = repo / reinject_hook.STATE_RELATIVE
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload), encoding="utf-8")


def test_pointer_for_branches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    assert reinject_hook.pointer_for(repo) is None

    (repo / reinject_hook.STATE_RELATIVE).parent.mkdir(parents=True, exist_ok=True)
    (repo / reinject_hook.STATE_RELATIVE).write_text("{oops", encoding="utf-8")
    assert reinject_hook.pointer_for(repo) is None

    _write_state(repo, ["not", "a", "mapping"])
    assert reinject_hook.pointer_for(repo) is None

    _write_state(repo, {reinject_hook.ACTIVE_KEY: {"number": -1, "ledger_path": "x"}})
    assert reinject_hook.pointer_for(repo) is None

    _write_state(
        repo,
        {reinject_hook.ACTIVE_KEY: {"number": 7, "ledger_path": "docs/ledger.md"}},
    )
    pointer = reinject_hook.pointer_for(repo)
    assert pointer == "/goal #7\nledger: docs/ledger.md\nstatus: charness task status"


def _repo_with_active_pointer(base: Path) -> Path:
    repo = base / "repo"
    (repo / ".git").mkdir(parents=True)
    _write_state(
        repo,
        {reinject_hook.ACTIVE_KEY: {"number": 3, "ledger_path": "ledger.md"}},
    )
    return repo


def test_main_prints_pointer_for_compact(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = _repo_with_active_pointer(tmp_path)
    payload = json.dumps({"source": "compact", "cwd": str(repo)})
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    assert reinject_hook.main([]) == 0
    assert "/goal #3" in capsys.readouterr().out


def test_main_invalid_stdin_and_empty_stdin(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("{not json"))
    assert reinject_hook.main([]) == 0
    assert capsys.readouterr().out == ""

    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert reinject_hook.main([]) == 0
    assert capsys.readouterr().out == ""


def test_module_main_entrypoint(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(Path(reinject_hook.__file__)), run_name="__main__")
    assert excinfo.value.code == 0
    assert capsys.readouterr().out == ""
