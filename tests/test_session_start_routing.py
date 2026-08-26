from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest
import session_start_codex_recovery as recovery
import session_start_routing as hook

REPO_ROOT = Path(__file__).resolve().parent.parent

HOOK_SCRIPT = REPO_ROOT / "scripts" / "session_start_routing.py"
LESSON_CONTEXT_SCRIPT = REPO_ROOT / "scripts" / "session_start_lesson_context.py"
PLUGIN_HOOK_SCRIPT = REPO_ROOT / "plugins" / "charness" / "scripts" / "session_start_routing.py"
CODEX_RECOVERY_SCRIPT = REPO_ROOT / "scripts" / "session_start_codex_recovery.py"
PLUGIN_CODEX_RECOVERY_SCRIPT = REPO_ROOT / "plugins" / "charness" / "scripts" / "session_start_codex_recovery.py"

# The session-start routing trigger is installed at USER level
# (~/.claude/settings.json, ~/.codex/config.toml) pointing at the released
# plugin script, not committed into this repo. These tests pin the script's
# behavior (the portable mechanism); the host wiring is per-machine config.
#
# The hook carries ordinary routing context and points at the deterministic
# catalog only for hidden inventory facts. It does not classify tasks or invoke
# a public semantic-routing skill; workflow choice remains owned by installed
# metadata and model judgment.


def _configured_handoff_repo(tmp_path: Path) -> Path:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: fixture\nlanguage: en\noutput_dir: state\n",
        encoding="utf-8",
    )
    return tmp_path


def test_directive_front_loads_inventory_and_ordinary_request_routing() -> None:
    """The hook keeps ordinary routing and inventory without the pickup detour."""
    directive = hook.build_additional_context()
    lowered = directive.lower()
    assert "pickup" not in lowered
    assert "docs/handoff.md" not in directive
    assert "workflow trigger" not in lowered
    assert "charness:handoff" not in directive
    assert "charness catalog list" in directive
    assert "--summary" in directive
    assert "--json" not in directive
    assert "hidden support/integration" in lowered
    assert "treat its facts only as inventory" in lowered
    assert "route ordinary requests directly" in directive
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


def test_codex_compact_recovery_is_appended_to_existing_context() -> None:
    directive = hook.build_additional_context(
        payload={
            "source": "compact",
            "session_id": "current-session",
            "transcript_path": "/tmp/current-rollout.jsonl",
        },
        host="codex",
    )

    assert directive.startswith(hook.DIRECTIVE)
    assert "Codex compact recovery" in directive
    assert "response_item" in directive
    assert "payload.type` is `message" in directive
    assert "user` or `assistant" in directive
    assert (
        "Read only `response_item` records whose `payload.type` is `message` and whose role is "
        "`user` or `assistant`."
    ) in directive
    assert "Do not read reasoning, tool calls or outputs, or file-diff renderings." in directive
    assert (
        "Use the user-text anchor stated by the current recovery request (not by this hook's "
        "SessionStart payload); if that exact anchor is absent or matches zero or multiple "
        "user messages, report compact recovery not established and take no recovery action."
    ) in directive
    assert "when the index and text disagree, trust the text" in directive
    assert "완료 / 진행 중 / 미완료" in directive
    assert "do not rerun completed work; do not terminate or restart active lanes." in directive
    assert 'session_id="current-session"' in directive
    assert 'transcript_path="/tmp/current-rollout.jsonl"' in directive
    assert (
        "continue an active lane, resume uncompleted work only when no live owner exists, "
        "never create a second lane for an existing ID, and treat ambiguous ownership as "
        "no-action recovery."
    ) in directive
    assert "never create a second lane for an existing ID" in directive
    assert "Do not create any recovery receipt or recovery artifact, even for form." in directive
    assert "This hook supplies context only" in directive


def test_codex_resume_does_not_receive_compact_recovery_after_existing_lesson_context(
    tmp_path: Path, monkeypatch
) -> None:
    repo = _configured_handoff_repo(tmp_path)
    (repo / "charness-artifacts" / "retro").mkdir(parents=True)
    (repo / "charness-artifacts" / "retro" / "lesson-ledger.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        hook._lesson_context,
        "build_lesson_context",
        lambda _root, _payload: {"state": "evaluated", "text": "LESSON BLOCK"},
    )

    directive = hook.build_additional_context(
        str(repo),
        {
            "source": "resume",
            "session_id": "host-42",
            "transcript_path": "/tmp/host-42.jsonl",
        },
        host="codex",
    )

    assert "LESSON BLOCK" in directive
    assert "Codex compact recovery" not in directive
    assert "response_item" not in directive
    assert 'session_id="host-42"' not in directive


def test_codex_recovery_requires_a_host_selected_rollout_identity() -> None:
    directive = hook.build_additional_context(
        payload={"source": "compact", "session_id": "current-session"}, host="codex"
    )

    assert "state: not-established" in directive
    assert "unambiguous session_id and transcript_path" in directive
    assert "Report only that compact recovery could not be established" in directive
    assert "never create a second lane" not in directive


def test_missing_codex_recovery_helper_is_visible_and_fail_closed(monkeypatch) -> None:
    monkeypatch.setattr(hook, "_codex_recovery", None)

    directive = hook.build_additional_context(
        payload={
            "source": "compact",
            "session_id": "current-session",
            "transcript_path": "/tmp/current-rollout.jsonl",
        },
        host="codex",
    )

    assert "charness session-start routing" in directive
    assert "state: not-established" in directive
    assert "recovery helper is missing" in directive
    assert "Report only that compact recovery could not be established" in directive


def test_failing_codex_recovery_helper_is_visible_and_fail_closed(monkeypatch) -> None:
    class BrokenRecovery:
        @staticmethod
        def build_recovery_context(_payload):
            raise RuntimeError("broken sibling")

    monkeypatch.setattr(hook, "_codex_recovery", BrokenRecovery)

    directive = hook.build_additional_context(
        payload={
            "source": "compact",
            "session_id": "current-session",
            "transcript_path": "/tmp/current-rollout.jsonl",
        },
        host="codex",
    )

    assert "state: not-established" in directive
    assert "helper raised RuntimeError" in directive
    assert (
        "Do not inspect a different rollout, reconcile state, launch, resume, or replay any lane."
        not in directive
    )
    assert (
        "Do not inspect a different rollout, reconcile state, launch, resume, or replay any lane"
        in directive
    )


def test_claude_does_not_receive_codex_compact_recovery() -> None:
    directive = hook.build_additional_context(
        payload={"source": "compact", "session_id": "current-session"}, host="claude"
    )

    assert "charness session-start routing" in directive
    assert "Codex compact recovery" not in directive


def test_codex_startup_does_not_pay_for_compact_recovery() -> None:
    directive = hook.build_additional_context(
        payload={"source": "startup", "session_id": "current-session"}, host="codex"
    )

    assert "charness catalog list" in directive
    assert "Codex compact recovery" not in directive
    assert "response_item" not in directive
    assert "state: " not in directive


@pytest.mark.parametrize("bad_source", [None, ["compact"], "future-source"])
def test_codex_unknown_source_is_visible_and_does_not_claim_recovery(bad_source) -> None:
    payload = {
        "session_id": "current-session",
        "transcript_path": "/tmp/current-rollout.jsonl",
    }
    if bad_source is not None:
        payload["source"] = bad_source
    directive = hook.build_additional_context(
        payload=payload,
        host="codex",
    )

    assert "charness session-start routing" in directive
    assert "state: not-established" in directive
    assert "source was missing, non-string, or unknown" in directive
    assert "No compact recovery context was added" in directive
    assert "Codex compact recovery" not in directive


@pytest.mark.parametrize("bad_value", [None, "", 42])
def test_codex_empty_or_non_string_helper_output_is_visible_and_fail_closed(
    monkeypatch, bad_value
) -> None:
    class BrokenRecovery:
        @staticmethod
        def build_recovery_context(_payload):
            return bad_value

    monkeypatch.setattr(hook, "_codex_recovery", BrokenRecovery)
    directive = hook.build_additional_context(
        payload={
            "source": "compact",
            "session_id": "current-session",
            "transcript_path": "/tmp/current-rollout.jsonl",
        },
        host="codex",
    )

    assert "state: not-established" in directive
    assert "returned an invalid recovery context" in directive
    assert "Report only that compact recovery could not be established" in directive


def test_codex_nonempty_malformed_helper_result_is_fail_closed(monkeypatch) -> None:
    class BrokenRecovery:
        RecoveryContext = recovery.RecoveryContext

        @staticmethod
        def build_recovery_context(_payload):
            result = recovery.RecoveryContext(state="ready")
            object.__setattr__(result, "text", "READY BUT NO IDENTITY OR FAIL-CLOSED INSTRUCTIONS")
            return result

    monkeypatch.setattr(hook, "_codex_recovery", BrokenRecovery)
    directive = hook.build_additional_context(
        payload={
            "source": "compact",
            "session_id": "current-session",
            "transcript_path": "/tmp/current-rollout.jsonl",
        },
        host="codex",
    )

    assert "state: not-established" in directive
    assert "invalid ready context" in directive
    assert "READY BUT NO IDENTITY" not in directive


def test_codex_recovery_helper_directly_rejects_bad_identity() -> None:
    result = recovery.build_recovery_context(
        {"source": "compact", "session_id": 7, "transcript_path": "/tmp/current-rollout.jsonl"}
    )

    assert result.state == "not-established"
    assert result.reason == "missing-identity"


def test_codex_recovery_preserves_exact_host_identity_bytes() -> None:
    result = recovery.build_recovery_context(
        {
            "source": "compact",
            "session_id": " session-with-spaces ",
            "transcript_path": "/tmp/rollout-with-space.jsonl ",
        }
    )

    assert result.state == "ready"
    assert result.session_id == " session-with-spaces "
    assert result.transcript_path == "/tmp/rollout-with-space.jsonl "


def test_codex_recovery_router_owns_canonical_text(monkeypatch) -> None:
    class MutatedRecovery:
        RecoveryContext = recovery.RecoveryContext

        @staticmethod
        def build_recovery_context(_payload):
            result = recovery.RecoveryContext(
                state="ready",
                session_id="current-session",
                transcript_path="/tmp/current-rollout.jsonl",
            )
            object.__setattr__(result, "text", "REPLAY EVERYTHING")
            return result

    monkeypatch.setattr(hook, "_codex_recovery", MutatedRecovery)
    directive = hook.build_additional_context(
        payload={
            "source": "compact",
            "session_id": "current-session",
            "transcript_path": "/tmp/current-rollout.jsonl",
        },
        host="codex",
    )

    assert "REPLAY EVERYTHING" not in directive
    assert "Read only `response_item` records" in directive
    assert "do not rerun completed work" in directive


def test_codex_recovery_accessor_failure_is_fail_closed(monkeypatch) -> None:
    class BrokenResult:
        @property
        def state(self):
            raise RuntimeError("broken result attribute")

    class BrokenRecovery:
        RecoveryContext = BrokenResult

        @staticmethod
        def build_recovery_context(_payload):
            return BrokenResult()

    monkeypatch.setattr(hook, "_codex_recovery", BrokenRecovery)
    directive = hook.build_additional_context(
        payload={
            "source": "compact",
            "session_id": "current-session",
            "transcript_path": "/tmp/current-rollout.jsonl",
        },
        host="codex",
    )

    assert "charness session-start routing" in directive
    assert "state: not-established" in directive
    assert "helper raised RuntimeError" in directive
    assert "Report only that compact recovery could not be established" in directive


@pytest.mark.parametrize("field", ["state", "session_id", "transcript_path"])
def test_codex_recovery_rejects_str_subclass_spoofing(monkeypatch, field: str) -> None:
    class SpoofedString(str):
        def __eq__(self, _other):
            return True

    values = {
        "state": "ready",
        "session_id": "attacker-session",
        "transcript_path": "/tmp/attacker-rollout.jsonl",
    }
    values[field] = SpoofedString(values[field])

    class SpoofedRecovery:
        RecoveryContext = recovery.RecoveryContext

        @staticmethod
        def build_recovery_context(_payload):
            return recovery.RecoveryContext(**values)

    monkeypatch.setattr(hook, "_codex_recovery", SpoofedRecovery)
    directive = hook.build_additional_context(
        payload={
            "source": "compact",
            "session_id": "host-session",
            "transcript_path": "/tmp/host-rollout.jsonl",
        },
        host="codex",
    )

    assert "state: not-established" in directive
    assert "Codex compact recovery (state: ready" not in directive
    assert "attacker-session" not in directive
    assert "/tmp/attacker-rollout.jsonl" not in directive


@pytest.mark.parametrize("hook_script", [HOOK_SCRIPT, PLUGIN_HOOK_SCRIPT])
def test_hook_entrypoints_use_a_valid_codex_fallback_for_unusable_cwd(hook_script: Path) -> None:
    result = subprocess.run(
        ["python3", str(hook_script), "--host", "codex"],
        input=json.dumps(
            {
                "source": "compact",
                "cwd": "\x00",
                "session_id": "host-session",
                "transcript_path": "/tmp/host-rollout.jsonl",
            }
        ),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    emitted = json.loads(result.stdout)
    context = emitted["hookSpecificOutput"]["additionalContext"]
    assert "charness session-start routing" in context
    assert "state: not-established" in context
    assert "No compact recovery context was added" in context
    assert "Codex compact recovery (state: ready" not in context


def test_main_uses_prebuilt_fallback_when_output_renderer_raises(monkeypatch, capsys) -> None:
    def explode(*_args, **_kwargs):
        raise RuntimeError("renderer unavailable")

    monkeypatch.setattr(hook, "render_output", explode)
    monkeypatch.setattr(
        sys,
        "stdin",
        io.StringIO(json.dumps({"source": "compact", "session_id": "host-session"})),
    )

    assert hook.main(["--host", "codex"]) == 0
    emitted = json.loads(capsys.readouterr().out)
    context = emitted["hookSpecificOutput"]["additionalContext"]
    assert "charness session-start routing" in context
    assert "state: not-established" in context
    assert "No compact recovery context was added" in context


def test_shipped_codex_recovery_fragment_is_present_and_matches_source() -> None:
    assert PLUGIN_CODEX_RECOVERY_SCRIPT.is_file()
    assert PLUGIN_CODEX_RECOVERY_SCRIPT.read_bytes() == CODEX_RECOVERY_SCRIPT.read_bytes()


def test_shipped_session_start_router_is_present_and_matches_source() -> None:
    assert PLUGIN_HOOK_SCRIPT.is_file()
    assert PLUGIN_HOOK_SCRIPT.read_bytes() == HOOK_SCRIPT.read_bytes()


@pytest.mark.parametrize("source", ["compact", "startup", "resume", "clear"])
def test_shipped_plugin_codex_entrypoint_honors_compact_source_only(
    source: str, tmp_path: Path
) -> None:
    result = subprocess.run(
        ["python3", str(PLUGIN_HOOK_SCRIPT), "--host", "codex"],
        input=json.dumps(
            {
                "hook_event_name": "SessionStart",
                "source": source,
                "cwd": str(tmp_path),
                "session_id": "plugin-session",
                "transcript_path": "/tmp/plugin-rollout.jsonl",
            }
        ),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    if source == "compact":
        assert "Codex compact recovery" in context
        assert 'session_id="plugin-session"' in context
    else:
        assert "Codex compact recovery" not in context
        assert "response_item" not in context


@pytest.mark.parametrize("bad_source", [None, ["compact"], "future-source"])
def test_shipped_plugin_codex_entrypoint_rejects_unknown_source(
    bad_source, tmp_path: Path
) -> None:
    payload = {
        "hook_event_name": "SessionStart",
        "cwd": str(tmp_path),
        "session_id": "plugin-session",
        "transcript_path": "/tmp/plugin-rollout.jsonl",
    }
    if bad_source is not None:
        payload["source"] = bad_source
    result = subprocess.run(
        ["python3", str(PLUGIN_HOOK_SCRIPT), "--host", "codex"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "state: not-established" in context
    assert "No compact recovery context was added" in context
    assert "Codex compact recovery" not in context


def test_codex_compact_recovery_survives_the_hook_entrypoint() -> None:
    payload = json.dumps(
        {
            "hook_event_name": "SessionStart",
            "source": "compact",
            "cwd": str(REPO_ROOT),
            "session_id": "test",
            "transcript_path": "/tmp/current-rollout.jsonl",
        }
    )
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "codex"],
        input=payload,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    emitted = json.loads(result.stdout)
    context = emitted["hookSpecificOutput"]["additionalContext"]
    assert "charness catalog list" in context
    assert "Codex compact recovery" in context


def test_codex_malformed_entrypoint_payload_is_visible_and_fail_closed() -> None:
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "codex"],
        input="not json at all {{{",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "charness session-start routing" in context
    assert "state: not-established" in context
    assert "SessionStart payload was missing or malformed" in context
    assert "No compact recovery context was added" in context
    assert "Codex compact recovery" not in context


@pytest.mark.parametrize("source", ["startup", "resume"])
def test_codex_entrypoint_does_not_emit_compact_recovery_for_ordinary_sources(
    source: str, tmp_path: Path
) -> None:
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "codex"],
        input=json.dumps(
            {
                "hook_event_name": "SessionStart",
                "source": source,
                "cwd": str(tmp_path),
                "session_id": "ordinary-session",
                "transcript_path": "/tmp/ordinary-rollout.jsonl",
            }
        ),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "charness catalog list" in context
    assert "Codex compact recovery" not in context
    assert "response_item" not in context
    assert 'session_id="ordinary-session"' not in context


def test_codex_entrypoint_empty_payload_does_not_claim_compact_recovery() -> None:
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "codex"],
        input="",
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "state: not-established" in context
    assert "No compact recovery context was added" in context
    assert "Codex compact recovery" not in context


def test_a_corrupt_codex_recovery_sibling_keeps_routing_and_reports_failure(tmp_path: Path) -> None:
    install = tmp_path / "install" / "scripts"
    install.mkdir(parents=True)
    (install / "session_start_routing.py").write_text(
        HOOK_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (install / "session_start_codex_recovery.py").write_text(")", encoding="utf-8")

    completed = subprocess.run(
        ["python3", str(install / "session_start_routing.py"), "--host", "codex"],
        input=json.dumps(
            {
                "source": "compact",
                "session_id": "current-session",
                "transcript_path": "/tmp/current-rollout.jsonl",
            }
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    context = json.loads(completed.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "charness session-start routing" in context
    assert "state: not-established" in context
    assert "recovery helper is missing" in context


def test_render_output_unknown_emits_plain_directive() -> None:
    out = hook.render_output("unknown")
    # Plain text fallback, not the structured JSON wrapper.
    assert "hookSpecificOutput" not in out
    assert "charness catalog list" in out


def test_render_output_grok_emits_plain_directive() -> None:
    # Grok Build ignores SessionStart stdout; do not pretend the Claude JSON wrapper injects.
    out = hook.render_output("grok")
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


def test_hook_does_not_inspect_configured_handoff_path_when_present(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: fixture\nlanguage: en\noutput_dir: state\n",
        encoding="utf-8",
    )
    (tmp_path / "state").mkdir()
    (tmp_path / "state" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")

    directive = hook.build_additional_context(str(tmp_path))

    assert "Pickup" not in directive
    assert "charness catalog list" in directive


def test_shipped_plugin_hook_does_not_resolve_handoff_path(tmp_path: Path) -> None:
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
    context = emitted["hookSpecificOutput"]["additionalContext"]
    assert "Pickup" not in context
    assert "charness catalog list" in context


def test_source_hook_keeps_context_lean_for_nested_cwd(tmp_path: Path) -> None:
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

    assert "Pickup" not in directive


def test_hook_omits_handoff_pickup_when_configured_artifact_is_missing(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: fixture\nlanguage: en\noutput_dir: state\n",
        encoding="utf-8",
    )

    directive = hook.build_additional_context(str(tmp_path))

    assert "Pickup" not in directive
    assert "charness catalog list" in directive


def test_hook_preserves_default_directive_without_a_host_cwd() -> None:
    result = subprocess.run(
        ["python3", str(HOOK_SCRIPT), "--host", "claude"],
        input=json.dumps({"source": "startup"}),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    emitted = json.loads(result.stdout)
    context = emitted["hookSpecificOutput"]["additionalContext"]
    assert "docs/handoff.md" not in context
    assert "Pickup" not in context


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

    assert hook._read_payload(BrokenStream()) == {hook.INVALID_PAYLOAD_KEY: "not-established"}
    assert "session_start_routing: stdin read failed: stdin unavailable" in capsys.readouterr().err


def test_read_payload_empty_input_marks_context_not_established() -> None:
    assert hook._read_payload(io.StringIO("  \n")) == {hook.INVALID_PAYLOAD_KEY: "not-established"}
