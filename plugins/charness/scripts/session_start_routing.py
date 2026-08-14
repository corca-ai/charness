#!/usr/bin/env python3
"""SessionStart hook payload script for contextual session routing hints.

The hook carries context only: pickup follows the handoff, ordinary requests
start their matching workflow from installed skill metadata and model judgment,
and hidden support or integration availability uses the exact read-only
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
import subprocess
import sys
from pathlib import Path

HANDOFF_ADAPTER_RELATIVE = Path(".agents/handoff-adapter.yaml")
RESOLVER_TIMEOUT_SECONDS = 3

# Fallback-only copy of `session_start_lesson_context.LEDGER_RELATIVE`, pinned
# equal to it by `tests/test_session_start_routing.py`. It exists for exactly one
# window: a packaging failure in which this hook shipped without its sibling
# module. In that window a repo that never opted in must still pay nothing and
# hear nothing (so we need the gate), while a repo that DID opt in must hear that
# its lesson loop is broken rather than silently lose it. A hard import would
# instead crash the hook in every session on the machine, opted in or not.
LESSON_LEDGER_RELATIVE = Path("charness-artifacts/retro/lesson-ledger.json")

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

DIRECTIVE = (
    "charness session-start routing: route the opening message directly. (1) "
    "Pickup — a bare handoff mention or no explicit task (if the message also "
    "names a concrete task, the task governs): follow the repo handoff's "
    "`## Workflow Trigger` (docs/handoff.md; skip this branch if the file "
    "doesn't exist) and invoke the workflow it names; for the default charness "
    "handoff that is `charness:handoff`. "
    "(2) Ordinary requests — use installed skill metadata and your own judgment "
    "to start the matching workflow directly. (3) Hidden support/integration inventory "
    "or an unclear availability question — run the read-only `charness catalog "
    "list --repo-root <repo> --summary` command. Treat its facts only as inventory; "
    "if the command returns nonzero, report the command failure."
)


def _handoff_resolver() -> Path | None:
    """Find the handoff resolver in either authoring or shipped-plugin layout."""
    plugin_root = Path(__file__).resolve().parent.parent
    return next(
        (
            candidate
            for candidate in (
                plugin_root / "skills" / "public" / "handoff" / "scripts" / "resolve_adapter.py",
                plugin_root / "skills" / "handoff" / "scripts" / "resolve_adapter.py",
            )
            if candidate.is_file()
        ),
        None,
    )


def _discover_repo_root(cwd: str) -> Path | None:
    """Find the nearest handoff adapter, otherwise the enclosing Git root."""
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


def _configured_handoff_state(cwd: object) -> tuple[str, bool] | None:
    """Return the adapter-owned handoff path and whether it is present.

    SessionStart receives a cwd from both supported hosts.  Resolve the same
    handoff adapter the workflow uses instead of deciding presence from the
    author's default path.  This stays deliberately fail-closed: a malformed
    payload, resolver, or path produces no pickup route rather than a route to
    an unrelated artifact.
    """
    if not isinstance(cwd, str) or not cwd.strip():
        return None
    repo_root = _discover_repo_root(cwd)
    if repo_root is None:
        return None
    resolver = _handoff_resolver()
    if resolver is None:
        return None
    try:
        completed = subprocess.run(
            [sys.executable, str(resolver), "--repo-root", str(repo_root)],
            capture_output=True,
            text=True,
            timeout=RESOLVER_TIMEOUT_SECONDS,
            check=False,
        )
        if completed.returncode != 0:
            return None
        payload = json.loads(completed.stdout)
        artifact_path = payload.get("artifact_path") if isinstance(payload, dict) else None
        if not isinstance(artifact_path, str) or not artifact_path.strip():
            return None
        relative = Path(artifact_path)
        if relative.is_absolute():
            return None
        resolved = (repo_root / relative).resolve()
        try:
            resolved.relative_to(repo_root)
        except ValueError:
            return None
        return (relative.as_posix(), resolved.is_file())
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
        return None


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


def build_additional_context(
    cwd: object | None = None, payload: dict[str, object] | None = None
) -> str:
    """Return the front-loaded session-start routing directive, plus any lesson block.

    With a host-provided cwd, the pickup branch reflects the configured handoff
    artifact's actual presence.  The no-argument default preserves the portable
    context used by direct callers that have no repository state to inspect --
    including the lesson block, which needs a repo to have an opt-in state at all.
    """
    if not isinstance(cwd, str) or not cwd.strip():
        return DIRECTIVE
    state = _configured_handoff_state(cwd)
    if state is None:
        pickup = (
            "Pickup — the hook could not resolve the configured handoff artifact; "
            "report that routing boundary instead of inventing a handoff path. "
        )
    else:
        artifact_path, exists = state
        if exists:
            pickup = (
                "Pickup — a bare handoff mention or no explicit task (if the message also "
                "names a concrete task, the task governs): follow the repo handoff's "
                f"`## Workflow Trigger` ({artifact_path}) and invoke the workflow it names; "
                "for the default charness handoff that is `charness:handoff`. "
            )
        else:
            pickup = (
                f"Pickup — the configured handoff artifact `{artifact_path}` is absent, "
                "so skip the handoff branch. "
            )
    ordinary = (
        "(2) Ordinary requests — use installed skill metadata and your own judgment "
        "to start the matching workflow directly. (3) Hidden support/integration inventory "
        "or an unclear availability question — run the read-only `charness catalog "
        "list --repo-root <repo> --summary` command. Treat its facts only as inventory; "
        "if the command returns nonzero, report the command failure."
    )
    return (
        "charness session-start routing: route the opening message directly. (1) "
        + pickup
        + ordinary
        + _lesson_block(cwd, payload)
    )


def render_output(host: str, *, directive: str | None = None) -> str:
    """Render the host-appropriate stdout payload that injects the directive.

    Claude Code and Codex both read `hookSpecificOutput.additionalContext` and
    add it to session context. `unknown` falls back to plain stdout, which both
    hosts also add to context.
    """
    text = directive if directive is not None else build_additional_context()
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
    return text


def _read_payload(stream) -> dict[str, object]:
    try:
        raw = (stream.read() or "").strip()
    except OSError as exc:
        _debug(f"stdin read failed: {exc}")
        return {}
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        _debug(f"stdin JSON decode failed: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        choices=["claude", "codex", "unknown"],
        default="unknown",
        help="Host that fired the hook; selects the stdout injection format.",
    )
    args = parser.parse_args(argv)
    try:
        payload = _read_payload(sys.stdin)
        _debug(f"source={payload.get('source')!r} cwd={payload.get('cwd')!r}")
        directive = build_additional_context(payload.get("cwd"), payload)
        sys.stdout.write(render_output(args.host, directive=directive) + "\n")
    except Exception as exc:  # pragma: no cover - never propagate hook errors
        _debug(f"unhandled error: {exc!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
