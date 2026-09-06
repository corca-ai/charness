#!/usr/bin/env python3
"""Repository cache command-line interface."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


VERSION = "1.0.0"
CACHE = Path(".state/cache.json")
LEGACY_REFRESH = Path(__file__).resolve().parent / "scripts" / "refresh_cache.py"

TOP_HELP = """Usage: repoctl [--json] COMMAND [OPTIONS]

Commands:
  refresh SOURCE       Parse SOURCE and write .state/cache.json
  doctor               Report cache readiness without changing files
  version              Print the repoctl version

Use `repoctl COMMAND --help` for command-specific help.
"""

COMMAND_HELP = {
    "refresh": """Usage: repoctl refresh [--dry-run] [--json] SOURCE

Parse SOURCE as JSON and write .state/cache.json. With --dry-run, validate
SOURCE and report the planned write without changing any file.
""",
    "doctor": """Usage: repoctl doctor [--json]

Read .state/cache.json and report missing, invalid, or ready status.
""",
    "version": """Usage: repoctl version [--json]

Print the repoctl version.
""",
}


class CliError(ValueError):
    """A command-line grammar error."""


class Parsed:
    def __init__(self, command, source=None, json_mode=False, dry_run=False, help_requested=False):
        self.command = command
        self.source = source
        self.json_mode = json_mode
        self.dry_run = dry_run
        self.help_requested = help_requested


def parse_args(argv):
    command = None
    source = None
    json_mode = False
    dry_run = False
    help_requested = False

    for token in argv:
        if token in ("--help", "-h"):
            help_requested = True
            continue
        if token == "--json":
            if json_mode:
                raise CliError("duplicate option: --json")
            json_mode = True
            continue
        if token == "--dry-run":
            if dry_run:
                raise CliError("duplicate option: --dry-run")
            dry_run = True
            continue
        if token.startswith("-"):
            raise CliError(f"unknown option: {token}")
        if command is None:
            command = token
        elif command == "refresh" and source is None:
            source = token
        else:
            raise CliError(f"unexpected argument: {token}")

    if command is None:
        if help_requested:
            return Parsed(None, json_mode=json_mode, help_requested=True)
        raise CliError("missing command")
    if command not in COMMAND_HELP:
        raise CliError(f"unknown command: {command}")
    if dry_run and command != "refresh":
        raise CliError("--dry-run is only valid with refresh")
    if command == "refresh" and source is None and not help_requested:
        raise CliError("refresh requires SOURCE")
    if command != "refresh" and source is not None:
        raise CliError(f"unexpected argument: {source}")
    return Parsed(
        command,
        source=source,
        json_mode=json_mode,
        dry_run=dry_run,
        help_requested=help_requested,
    )


def emit_json(payload):
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def cache_status():
    if not CACHE.is_file():
        return "missing"
    try:
        json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "invalid"
    return "ready"


def refresh(parsed):
    source = Path(parsed.source)
    if parsed.dry_run:
        try:
            json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return 1, {
                "command": "refresh",
                "dry_run": True,
                "error": str(exc),
                "source": parsed.source,
                "status": "error",
            }
        payload = {
            "cache": CACHE.as_posix(),
            "command": "refresh",
            "dry_run": True,
            "source": parsed.source,
            "status": "would_refresh",
        }
        return 0, payload

    result = subprocess.run(
        [sys.executable, str(LEGACY_REFRESH), parsed.source],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        error = result.stderr.strip() or "refresh failed"
        return 1, {
            "command": "refresh",
            "dry_run": False,
            "error": error,
            "source": parsed.source,
            "status": "error",
        }
    return 0, {
        "cache": CACHE.as_posix(),
        "command": "refresh",
        "dry_run": False,
        "source": parsed.source,
        "status": "refreshed",
    }


def run(parsed):
    if parsed.help_requested:
        print(TOP_HELP if parsed.command is None else COMMAND_HELP[parsed.command], end="")
        return 0
    if parsed.command == "version":
        payload = {"command": "version", "status": "ok", "version": VERSION}
        if parsed.json_mode:
            emit_json(payload)
        else:
            print(f"repoctl {VERSION}")
        return 0
    if parsed.command == "doctor":
        status = cache_status()
        payload = {"cache": CACHE.as_posix(), "command": "doctor", "status": status}
        if parsed.json_mode:
            emit_json(payload)
        else:
            print(status)
        return 0 if status == "ready" else 1

    return_code, payload = refresh(parsed)
    if parsed.json_mode:
        emit_json(payload)
    elif return_code:
        print(f"repoctl refresh: {payload['error']}", file=sys.stderr)
    elif parsed.dry_run:
        print(f"would refresh {payload['cache']} from {parsed.source}")
    else:
        print(f"refreshed {payload['cache']}")
    return return_code


def main(argv=None):
    sys.dont_write_bytecode = True
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        parsed = parse_args(args)
        return run(parsed)
    except CliError as exc:
        print(f"repoctl: {exc}", file=sys.stderr)
        print("Try `repoctl --help` for usage.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
