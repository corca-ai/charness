#!/usr/bin/env python3
"""SessionStart hook payload script for the charness find-skills routing trigger.

This is the **dumb** half of the #240 session-start-routing fix: it only injects
a directive to invoke `charness:find-skills` at session open. It carries no
routing intelligence — the "drive the routed workflow from the result" contract
(a pickup continues with `charness:handoff`) lives in the find-skills skill, not
in this hook text. See `skills/public/find-skills/references/session-start-routing.md`.

Wiring (installed at USER level so it fires in every session, pointing at the
released plugin copy of this script — not committed into any one repo):

- Claude Code: a `SessionStart` entry in `~/.claude/settings.json` runs
  `python3 <plugin-source>/scripts/session_start_find_skills.py --host claude`.
- Codex: a `[[hooks.SessionStart]]` entry in `~/.codex/config.toml` runs the
  same script with `--host codex`.

Both hosts add the emitted `hookSpecificOutput.additionalContext` string to the
session context (Codex confirmed 2026-05-29; see
charness-artifacts/gather/2026-05-22-codex-hooks-surface.md). `--host unknown`
falls back to plain stdout, which both hosts also add to context.

Honest ceiling: a hook injects context the model must still honor; it cannot
invoke a Skill tool directly. This strengthens routing via context-recency but
is not hard execution-forcing.

Failure modes are intentionally silent: hook script errors must never break a
host session. Set `CHARNESS_SESSION_START_DEBUG=1` for stderr diagnostics.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

DIRECTIVE = (
    "charness session-start routing: before acting on the opening message, "
    "invoke the `charness:find-skills` skill once. It maps installed "
    "capabilities and, per its own contract, owns the routing decision and "
    "drives the next step from its result. This trigger only points you at "
    "find-skills; the routing decision lives in that skill."
)


def _debug(message: str) -> None:
    if os.environ.get("CHARNESS_SESSION_START_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}:
        print(f"session_start_find_skills: {message}", file=sys.stderr)


def build_additional_context() -> str:
    """Return the dumb find-skills routing directive injected at session start."""
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
