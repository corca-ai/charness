#!/usr/bin/env python3
"""Claude PreToolUse(Bash) entry for one command-time orchestration guard.

Fired by the adapter-declared hook installed via
`host_hook_command_guards` — one installed command per guard
(`--guard parallel-window|verdict-channel|discard-worktree`); the rule
tables stay repo-owned in that module. Fail-open by design: malformed hook
input exits 0 so the hook never interferes with ordinary commands; a real
finding exits 2 so the host surfaces the verdict at command time.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.hooks import host_hook_command_guards as guards  # noqa: E402
from scripts.runtime_bootstrap import repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)


def _block_message(guard: str, found: dict[str, Any], command: str) -> str:
    event = guards.record_block(REPO_ROOT, found, command)
    facts = event.get("facts", {}) if isinstance(event, dict) else {}
    message = f"command guard [{guard}] blocked: {found['reason']}"
    if facts.get("escalation"):
        message += f" {facts['escalation']}."
    return message + f" ({found.get('hint', '')})"


def decide(payload: Any, guard: str) -> tuple[int, str]:
    """Evaluate guard(s) over hook input; (exit code, stderr message)."""
    if guard == "all":
        try:
            block = guards.evaluate_hook_payload(payload, REPO_ROOT)
        except Exception:  # noqa: BLE001 - malformed hook input exits 0
            return 0, ""
        if block is None or not block.get("blocked"):
            return 0, ""
        return 2, str(block.get("message", ""))
    if guard not in guards.GUARD_KEYS:
        return 0, ""
    try:
        if not isinstance(payload, dict):
            return 0, ""
        tool_input = payload.get("tool_input")
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        if not isinstance(command, str) or not command.strip():
            return 0, ""
        repo_root = guards.repo_root_for(payload.get("cwd"))
        found = guards.check_command(command, guard, repo_root=repo_root)
        if found is None:
            return 0, ""
        return 2, _block_message(guard, found, command)
    except Exception:  # noqa: BLE001 - malformed hook input exits 0
        return 0, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate one command-time guard.")
    parser.add_argument(
        "--guard",
        required=True,
        choices=[*guards.GUARD_KEYS, "all"],
        help="Which guard to evaluate.",
    )
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else None
    except (OSError, ValueError):
        return 0
    code, message = decide(payload, args.guard)
    if message:
        print(message, file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
