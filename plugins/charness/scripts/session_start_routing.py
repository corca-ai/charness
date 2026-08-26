#!/usr/bin/env python3
"""SessionStart hook payload script for contextual session routing hints.

The hook carries context only: ordinary requests start their matching workflow
from installed skill metadata and model judgment, and hidden support or integration
availability uses the exact read-only
`charness catalog list --repo-root <repo> --summary` inventory. A nonzero result
is reported as a command failure. The hook supplies context for the session.

Wiring (installed at USER level so it fires in every session, pointing at the
released plugin copy of this script — not committed into any one repo):

- Claude Code: a `SessionStart` entry in `~/.claude/settings.json` runs
  `python3 <plugin-source>/scripts/session_start_routing.py --host claude`.
- Codex: a `[[hooks.SessionStart]]` entry in `~/.codex/config.toml` runs the
  same script with `--host codex`.

Both hosts add the emitted `hookSpecificOutput.additionalContext` string to the
session context (Codex confirmed 2026-05-29; see
charness-artifacts/gather/2026-05-22-codex-hooks-surface.md). `--host unknown`
falls back to plain stdout, which both hosts also add to context.

Honest ceiling: a hook injects context the model must still honor; it cannot
invoke a Skill tool directly. This strengthens routing via context-recency but
is not hard execution-forcing; the front-loaded rule text remains contextual.

The same ceiling applies, harder, to the lesson block appended below: injecting
the lesson preview bytes proves EMISSION, never PRESENTATION. Nothing here may be
reported as "the agent read this" -- that is why the disposition grammar carries
`not-evaluated / presentation-unproven` as a state distinct from
`emission-unproven`. Measured cost of the lesson block in the authoring repo (566
retro artifacts): ~0.85 s of bounded subprocess and 2396 bytes of injected text
when a ledger exists, and one `is_file()` with zero injected bytes when it does
not. See `scripts/session_start_lesson_context.py`.

Failure modes are intentionally silent for the ROUTING directive: hook script
errors must never break a host session. That blanket deliberately does NOT extend
to the lesson block, which carries its own three-state text -- a repo that opted
in and then could not produce a lesson list must be told so, because silence
there is the "green over a capability that was never installed" defect this hook
was extended to fix. Set `CHARNESS_SESSION_START_DEBUG=1` for stderr diagnostics.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HANDOFF_ADAPTER_RELATIVE = Path(".agents/handoff-adapter.yaml")

# Fallback-only copy of `session_start_lesson_context.LEDGER_RELATIVE`, pinned
# equal to it by `tests/test_session_start_routing.py`. It exists for exactly one
# window: a packaging failure in which this hook shipped without its sibling
# module. In that window a repo that never opted in must still pay nothing and
# hear nothing (so we need the gate), while a repo that DID opt in must hear that
# its lesson loop is broken rather than silently lose it. A hard import would
# instead crash the hook in every session on the machine, opted in or not.
LESSON_LEDGER_RELATIVE = Path("charness-artifacts/retro/lesson-ledger.json")
# Codex source code gives compaction a distinct SessionStart source. A normal
# `resume` is not enough evidence that the session just compacted.
CODEX_RECOVERY_SOURCES = frozenset({"compact"})
CODEX_SESSION_START_SOURCES = frozenset({"startup", "resume", "clear", "compact"})
INVALID_PAYLOAD_KEY = "_charness_session_start_payload"

# `except Exception`, not `except ImportError`: the realistic packaging failure is
# a TRUNCATED or half-written sibling file, which raises `SyntaxError` -- and a
# `SyntaxError` here propagates out of module import, BEFORE `main()`'s own
# `except Exception`, so the hook exits nonzero with empty stdout and loses the
# ROUTING directive too, in every session on the machine, opted in or not. That is
# the exact "a missing optional host hook must not block session startup" line this
# module is not allowed to cross, so every import-time failure degrades to the
# `_lesson_context is None` branch below.
# `tests/test_session_start_routing.py::test_a_corrupt_sibling_module_never_costs_the_routing_directive`
# runs this as a real subprocess against a broken sibling file.
try:  # sibling module; ships in the same directory in both the authoring and plugin trees
    import session_start_lesson_context as _lesson_context
except Exception:  # noqa: BLE001 - see above; narrowing this re-breaks every session
    _lesson_context = None

# The Codex recovery fragment is optional at import time for the same reason as
# the lesson sibling: a half-written plugin copy must not take down the common
# routing directive on Claude or Codex. The fragment itself is host- and
# source-gated, so an ordinary startup pays no extra text.
try:
    import session_start_codex_recovery as _codex_recovery
except Exception:  # noqa: BLE001 - a hook must survive an incomplete sibling copy
    _codex_recovery = None

DIRECTIVE = (
    "charness session-start routing: route ordinary requests directly using "
    "installed skill metadata and your own judgment. Hidden support/integration inventory "
    "or an unclear availability question — run the read-only `charness catalog "
    "list --repo-root <repo> --summary` command. Treat its facts only as inventory; "
    "if the command returns nonzero, report the command failure."
)

# These are deliberately prebuilt from constants. The outer hook boundary must
# still emit usable host context if payload handling, repository discovery, or
# the normal renderer itself raises; calling that same path again in `except`
# would recreate the silent-success failure this fallback prevents.
SAFE_SESSION_START_FALLBACK_CONTEXT = (
    DIRECTIVE
    + "\n\ncharness session-start hook (state: not-established, context-only): optional "
    "session-start context could not be established; use ordinary session-start routing only."
)
SAFE_CODEX_SESSION_START_FALLBACK_CONTEXT = (
    DIRECTIVE
    + "\n\ncharness Codex SessionStart payload (state: not-established, context-only): "
    "the session-start hook could not establish optional context. No compact recovery "
    "context was added; use ordinary session-start routing only."
)
SAFE_CLAUDE_SESSION_START_FALLBACK_OUTPUT = json.dumps(
    {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": SAFE_SESSION_START_FALLBACK_CONTEXT,
        }
    },
    ensure_ascii=False,
)
SAFE_CODEX_SESSION_START_FALLBACK_OUTPUT = json.dumps(
    {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": SAFE_CODEX_SESSION_START_FALLBACK_CONTEXT,
        }
    },
    ensure_ascii=False,
)


def _discover_repo_root(cwd: str) -> Path | None:
    """Find the nearest Charness adapter, otherwise the enclosing Git root."""
    candidate = Path(cwd).expanduser().resolve()
    if not candidate.is_dir():
        return None
    git_root: Path | None = None
    while True:
        if (candidate / HANDOFF_ADAPTER_RELATIVE).is_file():
            return candidate
        if git_root is None and (candidate / ".git").exists():
            git_root = candidate
        if candidate.parent == candidate:
            return git_root
        candidate = candidate.parent


def _lesson_block(cwd: str, payload: dict[str, object] | None) -> str:
    """Return the lesson block to append, or `""` when there is nothing to say.

    Three outcomes, in the vocabulary `check_auto_trigger.py` already speaks:

    - `not-configured` -> `""`. A repo with no `lesson-ledger.json` never opted in;
      that silence is a real recorded answer and costs one `is_file()`.
    - `evaluated` -> the preview bytes (or the zero-lessons line) plus the declare
      command.
    - `not-established` -> a visible line naming the state, the cause, and the
      remediation. This is the branch that must never be swallowed.

    The bare `except Exception` covers only a CRASH of the context builder itself
    -- not a preview failure, which the builder already turns into
    `not-established` text. Even then the gate is re-applied first, so a hook that
    somehow cannot classify a repo stays silent in every repo that never opted in.
    """
    repo_root = _discover_repo_root(cwd)
    if repo_root is None or not (repo_root / LESSON_LEDGER_RELATIVE).is_file():
        return ""
    if _lesson_context is None:
        return (
            "\n\ncharness lesson loop (state: not-established): this repo declares a lesson "
            f"evaluator (`{LESSON_LEDGER_RELATIVE.as_posix()}`) but this charness install shipped "
            "no `session_start_lesson_context.py` beside the session-start hook, so no lesson list "
            "can be produced. Do not read that absence as `no lessons owed`; reinstall or update "
            "charness."
        )
    try:
        context = _lesson_context.build_lesson_context(repo_root, payload or {})
        text = context.get("text")
    except Exception as exc:  # never take a host session down over a lesson block
        _debug(f"lesson context failed: {exc!r}")
        return (
            "\n\ncharness lesson loop (state: not-established): this repo declares a lesson "
            f"evaluator but the session-start lesson context raised {type(exc).__name__}. Do not "
            "read that absence as `no lessons owed`."
        )
    return f"\n\n{text}" if isinstance(text, str) and text.strip() else ""


def _debug(message: str) -> None:
    if os.environ.get("CHARNESS_SESSION_START_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}:
        print(f"session_start_routing: {message}", file=sys.stderr)


def _codex_recovery_not_established(reason: str) -> str:
    return (
        "\n\ncharness Codex compact recovery (state: not-established, context-only): "
        f"{reason} Do not inspect a different rollout, reconcile state, launch, resume, "
        "or replay any lane, and do not create a recovery receipt or recovery artifact. "
        "Report only that compact recovery could not be established."
    )


def _codex_payload_not_established(reason: str) -> str:
    return (
        "\n\ncharness Codex SessionStart payload (state: not-established, context-only): "
        f"{reason} No compact recovery context was added; use ordinary session-start "
        "routing only."
    )


def _codex_recovery_ready_context(session_id: str, transcript_path: str) -> str:
    """Render canonical recovery prose from validated structured fields only."""
    identity_text = (
        f"session_id={json.dumps(session_id, ensure_ascii=False)}, "
        f"transcript_path={json.dumps(transcript_path, ensure_ascii=False)}"
    )
    return (
        "\n\ncharness Codex compact recovery (state: ready, context-only): after compact, "
        "use this host-selected rollout identity — "
        f"`{identity_text}` — and inspect its local Codex session JSONL. "
        "Identify the current rollout from that path rather than guessing from another "
        "session. Read only `response_item` records whose `payload.type` is `message` "
        "and whose role is `user` or `assistant`. Do not read reasoning, tool calls or "
        "outputs, or file-diff renderings. Use the user-text anchor stated by the current "
        "recovery request (not by this hook's SessionStart payload); if that exact anchor "
        "is absent or matches zero or multiple user messages, report compact recovery not "
        "established and take no recovery action. Do not trust a stale numeric message "
        "index; when the index and text disagree, trust the text, and read through the "
        "compaction boundary. Reconcile only the delta against (1) user-confirmed "
        "principles and still-live promises, (2) the current compact summary's "
        "completed/in-progress state and active lane/session IDs, and (3) the actual "
        "worktree. Classify items as `완료 / 진행 중 / 미완료`; do not rerun completed "
        "work; do not terminate or restart active lanes. Each existing lane/session ID "
        "has one owner: continue an active lane, resume uncompleted work only when no "
        "live owner exists, never create a second lane for an existing ID, and treat "
        "ambiguous ownership as no-action recovery. Do not create any recovery receipt "
        "or recovery artifact, even for form. Briefly report the recovered incomplete "
        "delta and lanes to continue, then resume; parallelize independent work and "
        "keep complex design, verification, and synthesis direct. This hook supplies "
        "context only; it does not prove that the recovery was read or performed."
    )


def _codex_recovery_block(host: str, payload: dict[str, object] | None) -> str:
    """Append only the Codex compact context, never for Claude or known ordinary sources."""
    if host != "codex":
        return ""
    if type(payload) is not dict:
        return _codex_payload_not_established(
            "The Codex SessionStart payload was missing or malformed."
        )
    if payload.get(INVALID_PAYLOAD_KEY):
        return _codex_payload_not_established(
            "The Codex SessionStart payload was missing or malformed."
        )
    source = payload.get("source")
    if type(source) is not str or source not in CODEX_SESSION_START_SOURCES:
        return _codex_payload_not_established(
            "The Codex SessionStart source was missing, non-string, or unknown."
        )
    if source not in CODEX_RECOVERY_SOURCES:
        return ""
    if _codex_recovery is None:
        return _codex_recovery_not_established(
            "The installed Codex recovery helper is missing or could not be imported."
        )
    try:
        host_session_id = payload.get("session_id")
        host_transcript_path = payload.get("transcript_path")
        if (
            type(host_session_id) is not str
            or not host_session_id.strip()
            or type(host_transcript_path) is not str
            or not host_transcript_path.strip()
        ):
            return _codex_recovery_not_established(
                "The host did not provide one unambiguous session_id and transcript_path."
            )
        result = _codex_recovery.build_recovery_context(payload)
        result_type = getattr(_codex_recovery, "RecoveryContext", None)
        if type(result_type) is not type or type(result) is not result_type:
            return _codex_recovery_not_established(
                "The installed Codex recovery helper returned an invalid recovery context."
            )
        state = getattr(result, "state", None)
        if type(state) is str and state == "not-established":
            reason = getattr(result, "reason", None)
            if type(reason) is str and reason == "missing-identity":
                return _codex_recovery_not_established(
                    "The host did not provide one unambiguous session_id and transcript_path."
                )
            return _codex_recovery_not_established(
                "The installed Codex recovery helper reported that recovery was not established."
            )
        session_id = getattr(result, "session_id", None)
        transcript_path = getattr(result, "transcript_path", None)
        if (
            type(state) is str
            and state == "ready"
            and type(session_id) is str
            and session_id.strip()
            and type(transcript_path) is str
            and transcript_path.strip()
            and type(host_session_id) is str
            and type(host_transcript_path) is str
            and session_id == host_session_id
            and transcript_path == host_transcript_path
        ):
            return _codex_recovery_ready_context(host_session_id, host_transcript_path)
        return _codex_recovery_not_established(
            "The installed Codex recovery helper returned an invalid ready context."
        )
    except Exception as exc:  # pragma: no cover - defensive hook boundary
        _debug(f"codex recovery validation failed: {exc!r}")
        return _codex_recovery_not_established(
            f"The installed Codex recovery helper raised {type(exc).__name__}."
        )


def build_additional_context(
    cwd: object | None = None,
    payload: dict[str, object] | None = None,
    *,
    host: str = "unknown",
) -> str:
    """Return the session-start routing directive, plus lesson and compact context."""
    lesson = _lesson_block(cwd, payload) if isinstance(cwd, str) and cwd.strip() else ""
    return DIRECTIVE + lesson + _codex_recovery_block(host, payload)


def render_output(host: str, *, directive: str | None = None) -> str:
    """Render the host-appropriate stdout payload that injects the directive.

    Claude Code and Codex both read `hookSpecificOutput.additionalContext` and
    add it to session context. `unknown` falls back to plain stdout, which both
    hosts also add to context.
    """
    text = directive if directive is not None else build_additional_context(host=host)
    if host in ("claude", "codex"):
        return json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": text,
                }
            },
            ensure_ascii=False,
        )
    # Grok Build ignores SessionStart stdout today, so keep the plain-text
    # fallback. The host flag is still recorded so installers can pass `--host grok`.
    return text


def _safe_fallback_output(host: str) -> str:
    """Return a prebuilt output without entering any normal hook code path."""
    if host == "claude":
        return SAFE_CLAUDE_SESSION_START_FALLBACK_OUTPUT
    if host == "codex":
        return SAFE_CODEX_SESSION_START_FALLBACK_OUTPUT
    return SAFE_SESSION_START_FALLBACK_CONTEXT


def _read_payload(stream) -> dict[str, object]:
    try:
        raw = (stream.read() or "").strip()
    except OSError as exc:
        _debug(f"stdin read failed: {exc}")
        return {INVALID_PAYLOAD_KEY: "not-established"}
    if not raw:
        return {INVALID_PAYLOAD_KEY: "not-established"}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        _debug(f"stdin JSON decode failed: {exc}")
        return {INVALID_PAYLOAD_KEY: "not-established"}
    return payload if isinstance(payload, dict) else {INVALID_PAYLOAD_KEY: "not-established"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        choices=["claude", "codex", "grok", "unknown"],
        default="unknown",
        help="Host that fired the hook; selects the stdout injection format.",
    )
    args = parser.parse_args(argv)
    fallback = _safe_fallback_output(args.host)
    try:
        payload = _read_payload(sys.stdin)
        _debug(f"source={payload.get('source')!r} cwd={payload.get('cwd')!r}")
        directive = build_additional_context(payload.get("cwd"), payload, host=args.host)
        sys.stdout.write(render_output(args.host, directive=directive) + "\n")
    except Exception as exc:  # pragma: no cover - never propagate hook errors
        _debug(f"unhandled error: {exc!r}")
        sys.stdout.write(fallback + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
