from __future__ import annotations

import io
import json
import subprocess
from pathlib import Path

import session_start_routing as hook

REPO_ROOT = Path(__file__).resolve().parent.parent

HOOK_SCRIPT = REPO_ROOT / "scripts" / "session_start_routing.py"
PLUGIN_HOOK_SCRIPT = REPO_ROOT / "plugins" / "charness" / "scripts" / "session_start_routing.py"

# The session-start routing trigger is installed at USER level
# (~/.claude/settings.json, ~/.codex/config.toml) pointing at the released
# plugin script, not committed into this repo. These tests pin the script's
# behavior (the portable mechanism); the host wiring is per-machine config.
#
# The hook carries contextual pickup guidance and points at the deterministic
# catalog only for hidden inventory facts. It does not classify tasks or invoke
# a public semantic-routing skill; ordinary workflow choice remains owned by
# installed metadata and model judgment.


def _configured_handoff_repo(tmp_path: Path) -> Path:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: fixture\nlanguage: en\noutput_dir: state\n",
        encoding="utf-8",
    )
    return tmp_path


def test_directive_front_loads_pickup_inventory_and_otherwise_routes() -> None:
    """The directive now states the routing rule directly, not just a pointer.

    Carries over the #240 protections: (1) a pickup deterministically drives
    into the handoff-named workflow and (2) hidden capability inventory stays
    a deterministic catalog lookup rather than semantic routing.
    """
    directive = hook.build_additional_context()
    lowered = directive.lower()
    # (1) Pickup route: names the handoff doc, its Workflow Trigger, and the
    # concrete skill to invoke.
    assert "pickup" in lowered
    assert "docs/handoff.md" in directive
    assert "workflow trigger" in lowered
    assert "charness:handoff" in directive
    # (2) Hidden inventory route: deterministic catalog facts only.
    assert "charness catalog list" in directive
    assert "--summary" in directive
    assert "--json" not in directive
    assert "hidden support/integration" in lowered
    assert "treat its facts only as inventory" in lowered
    assert "start the matching workflow directly" in directive
    assert "if the command returns nonzero" in directive


def test_render_output_claude_emits_session_start_additional_context() -> None:
    payload = json.loads(hook.render_output("claude"))
    inner = payload["hookSpecificOutput"]
    assert inner["hookEventName"] == "SessionStart"
    assert "charness catalog list" in inner["additionalContext"]


def test_render_output_codex_emits_session_start_additional_context() -> None:
    # Codex confirmed 2026-05-29 to support hookSpecificOutput.additionalContext.
    payload = json.loads(hook.render_output("codex"))
    inner = payload["hookSpecificOutput"]
    assert inner["hookEventName"] == "SessionStart"
    assert "charness catalog list" in inner["additionalContext"]


def test_render_output_unknown_emits_plain_directive() -> None:
    out = hook.render_output("unknown")
    # Plain text fallback, not the structured JSON wrapper.
    assert "hookSpecificOutput" not in out
    assert "charness catalog list" in out


def test_hook_runs_end_to_end_and_injects_directive() -> None:
    """Simulate the host firing the hook: SessionStart payload on stdin."""
    payload = json.dumps(
        {
            "hook_event_name": "SessionStart",
            "source": "startup",
            "cwd": str(REPO_ROOT),
            "session_id": "test",
        }
    )
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "claude"],
        input=payload,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    emitted = json.loads(result.stdout)
    assert emitted["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "charness catalog list" in emitted["hookSpecificOutput"]["additionalContext"]


def test_hook_uses_configured_handoff_path_when_present(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: fixture\nlanguage: en\noutput_dir: state\n",
        encoding="utf-8",
    )
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")

    directive = hook.build_additional_context(str(tmp_path))

    assert "`## Workflow Trigger` (state/handoff.md)" in directive
    assert "skip the handoff branch" not in directive


def test_shipped_plugin_hook_resolves_the_same_configured_handoff_path(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: fixture\nlanguage: en\noutput_dir: state\n",
        encoding="utf-8",
    )
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")

    nested_cwd = tmp_path / "nested" / "work"
    nested_cwd.mkdir(parents=True)
    result = subprocess.run(
        ["python3", str(PLUGIN_HOOK_SCRIPT), "--host", "codex"],
        input=json.dumps({"cwd": str(nested_cwd)}),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    emitted = json.loads(result.stdout)
    assert "`## Workflow Trigger` (state/handoff.md)" in emitted["hookSpecificOutput"]["additionalContext"]


def test_source_hook_discovers_configured_handoff_from_nested_cwd(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: fixture\nlanguage: en\noutput_dir: state\n",
        encoding="utf-8",
    )
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")
    nested_cwd = tmp_path / "nested" / "work"
    nested_cwd.mkdir(parents=True)

    directive = hook.build_additional_context(str(nested_cwd))

    assert "`## Workflow Trigger` (state/handoff.md)" in directive


def test_hook_skips_pickup_when_configured_handoff_is_missing(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: fixture\nlanguage: en\noutput_dir: state\n",
        encoding="utf-8",
    )

    directive = hook.build_additional_context(str(tmp_path))

    assert "configured handoff artifact `state/handoff.md` is absent" in directive
    assert "skip the handoff branch" in directive


def test_hook_reports_resolver_boundary_instead_of_defaulting_to_docs(monkeypatch, tmp_path: Path) -> None:
    _configured_handoff_repo(tmp_path)
    monkeypatch.setattr(hook, "_handoff_resolver", lambda: None)

    directive = hook.build_additional_context(str(tmp_path))

    assert "could not resolve the configured handoff artifact" in directive
    assert "docs/handoff.md" not in directive


def test_hook_preserves_default_directive_without_a_host_cwd() -> None:
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "claude"],
        input=json.dumps({"source": "startup"}),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    emitted = json.loads(result.stdout)
    assert "docs/handoff.md" in emitted["hookSpecificOutput"]["additionalContext"]


def test_hook_resolver_timeout_returns_the_explicit_boundary(monkeypatch, tmp_path: Path) -> None:
    _configured_handoff_repo(tmp_path)
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def timeout(*args, **kwargs):
        calls.append((args, kwargs))
        assert kwargs["timeout"] == hook.RESOLVER_TIMEOUT_SECONDS
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(hook.subprocess, "run", timeout)

    directive = hook.build_additional_context(str(tmp_path))

    assert len(calls) == 1
    assert "could not resolve the configured handoff artifact" in directive


def test_hook_nonzero_resolver_returns_the_explicit_boundary(monkeypatch, tmp_path: Path) -> None:
    _configured_handoff_repo(tmp_path)
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def nonzero(*args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args[0], 1, stdout="", stderr="resolver failed")

    monkeypatch.setattr(hook.subprocess, "run", nonzero)

    directive = hook.build_additional_context(str(tmp_path))

    assert len(calls) == 1
    assert "could not resolve the configured handoff artifact" in directive


def test_hook_entrypoint_emits_skip_context_for_missing_configured_handoff(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    _configured_handoff_repo(tmp_path)
    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(json.dumps({"cwd": str(tmp_path)})))

    assert hook.main(["--host", "codex"]) == 0

    emitted = json.loads(capsys.readouterr().out)
    assert "configured handoff artifact `state/handoff.md` is absent" in emitted["hookSpecificOutput"]["additionalContext"]


def test_hook_entrypoint_emits_boundary_context_on_timeout(monkeypatch, capsys, tmp_path: Path) -> None:
    _configured_handoff_repo(tmp_path)

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(hook.subprocess, "run", timeout)
    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(json.dumps({"cwd": str(tmp_path)})))

    assert hook.main(["--host", "codex"]) == 0

    emitted = json.loads(capsys.readouterr().out)
    assert "could not resolve the configured handoff artifact" in emitted["hookSpecificOutput"]["additionalContext"]


def test_hook_entrypoint_emits_boundary_context_on_nonzero_resolver(monkeypatch, capsys, tmp_path: Path) -> None:
    _configured_handoff_repo(tmp_path)
    monkeypatch.setattr(
        hook.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 1, stdout="", stderr="resolver failed"),
    )
    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(json.dumps({"cwd": str(tmp_path)})))

    assert hook.main(["--host", "codex"]) == 0

    emitted = json.loads(capsys.readouterr().out)
    assert "could not resolve the configured handoff artifact" in emitted["hookSpecificOutput"]["additionalContext"]


def test_hook_is_silent_failing_on_garbage_stdin() -> None:
    """A hook script error must never break the host session (exit 0)."""
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "claude"],
        input="not json at all {{{",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    # Still emits the directive even when the stdin payload is unparseable.
    assert "charness catalog list" in result.stdout


def test_read_payload_reports_oserror_in_debug_mode(monkeypatch, capsys) -> None:
    class BrokenStream:
        def read(self) -> str:
            raise OSError("stdin unavailable")

    monkeypatch.setenv("CHARNESS_SESSION_START_DEBUG", "1")

    assert hook._read_payload(BrokenStream()) == {}
    assert "session_start_routing: stdin read failed: stdin unavailable" in capsys.readouterr().err


def test_read_payload_empty_input_returns_empty_mapping() -> None:
    assert hook._read_payload(io.StringIO("  \n")) == {}


def test_repo_root_discovery_and_configured_state_fail_closed_at_each_boundary(
    monkeypatch, tmp_path: Path
) -> None:
    missing = tmp_path / "missing"
    assert hook._discover_repo_root(str(missing)) is None

    git_only = tmp_path / "git-only"
    (git_only / ".git").mkdir(parents=True)
    nested = git_only / "nested"
    nested.mkdir()
    assert hook._discover_repo_root(str(nested)) == git_only

    configured = tmp_path / "configured"
    configured.mkdir()
    repo = _configured_handoff_repo(configured)
    monkeypatch.setattr(hook, "_handoff_resolver", lambda: Path("resolver.py"))
    assert hook._configured_handoff_state("") is None
    assert hook._configured_handoff_state(str(missing)) is None

    def resolved_payload(*_args, **_kwargs):
        return subprocess.CompletedProcess([], 0, stdout=json.dumps({"artifact_path": "/tmp/absolute"}))

    monkeypatch.setattr(hook.subprocess, "run", resolved_payload)
    assert hook._configured_handoff_state(str(repo)) is None

    def escaped_payload(*_args, **_kwargs):
        return subprocess.CompletedProcess([], 0, stdout=json.dumps({"artifact_path": "../outside.md"}))

    monkeypatch.setattr(hook.subprocess, "run", escaped_payload)
    assert hook._configured_handoff_state(str(repo)) is None
