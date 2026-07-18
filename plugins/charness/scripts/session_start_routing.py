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

Failure modes are intentionally silent: hook script errors must never break a
host session. Set `CHARNESS_SESSION_START_DEBUG=1` for stderr diagnostics.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

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


def _debug(message: str) -> None:
    if os.environ.get("CHARNESS_SESSION_START_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}:
        print(f"session_start_routing: {message}", file=sys.stderr)


def build_additional_context() -> str:
    """Return the front-loaded session-start routing directive."""
    return DIRECTIVE


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
        sys.stdout.write(render_output(args.host) + "\n")
    except Exception as exc:  # pragma: no cover - never propagate hook errors
        _debug(f"unhandled error: {exc!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
