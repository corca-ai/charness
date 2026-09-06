#!/usr/bin/env python3
"""Small command-line interface for the cache fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path


VERSION = "1.0.0"
CACHE = Path(".state/cache.json")

TOP_HELP = """usage: repoctl [--json] COMMAND [OPTIONS]

Commands:
  refresh SOURCE  validate SOURCE and refresh .state/cache.json
  doctor          report cache readiness without changing files
  version         print the repoctl version

Options:
  --json          emit one JSON object on stdout
  -h, --help      show help
"""

REFRESH_HELP = """usage: repoctl [--json] refresh [--dry-run] SOURCE [--json]

Validate SOURCE and write .state/cache.json. Use --dry-run to validate and
report the planned refresh without changing any file.
"""

DOCTOR_HELP = """usage: repoctl [--json] doctor [--json]

Report whether .state/cache.json is missing, invalid, or ready.
"""

VERSION_HELP = """usage: repoctl [--json] version [--json]

Print the repoctl version without reading or writing repository state.
"""


class UsageError(ValueError):
    """An invalid command-line shape."""


def _parse(argv):
    command = None
    command_index = None
    source = None
    json_count = 0
    dry_run_count = 0
    dry_run_index = None
    help_count = 0

    for index, token in enumerate(argv):
        if token == "--json":
            json_count += 1
            if json_count > 1:
                raise UsageError("duplicate option: --json")
        elif token == "--dry-run":
            dry_run_count += 1
            if dry_run_count > 1:
                raise UsageError("duplicate option: --dry-run")
            dry_run_index = index
        elif token in ("-h", "--help"):
            help_count += 1
            if help_count > 1:
                raise UsageError("duplicate option: --help")
        elif token.startswith("-"):
            raise UsageError(f"unknown option: {token}")
        elif command is None:
            command = token
            command_index = index
        elif source is None:
            source = token
        else:
            raise UsageError(f"unexpected argument: {token}")

    help_requested = help_count == 1
    if command is None:
        if dry_run_count:
            raise UsageError("--dry-run is only valid after refresh")
        if not help_requested:
            raise UsageError("missing command")
        return {
            "command": None,
            "dry_run": bool(dry_run_count),
            "help": True,
            "json": bool(json_count),
            "source": source,
        }
    if command not in {"refresh", "doctor", "version"}:
        raise UsageError(f"unknown command: {command}")
    if dry_run_index is not None and dry_run_index < command_index:
        raise UsageError("--dry-run is only valid after refresh")
    if dry_run_count and command != "refresh":
        raise UsageError("--dry-run is only valid with refresh")

    if command == "refresh":
        if source is None and not help_requested:
            raise UsageError("refresh requires SOURCE")
    elif source is not None:
        raise UsageError(f"{command} does not accept SOURCE")

    return {
        "command": command,
        "dry_run": bool(dry_run_count),
        "help": help_requested,
        "json": bool(json_count),
        "source": source,
    }


def _help_for(command):
    if command == "refresh":
        return REFRESH_HELP
    if command == "doctor":
        return DOCTOR_HELP
    if command == "version":
        return VERSION_HELP
    return TOP_HELP


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_cache(payload):
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _cache_status():
    if not CACHE.is_file():
        return "missing"
    try:
        _read_json(CACHE)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "invalid"
    return "ready"


def _emit(result, human, json_mode):
    if json_mode:
        print(json.dumps(result, sort_keys=True))
    else:
        print(human)


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        parsed = _parse(args)
    except UsageError as exc:
        print(f"repoctl: error: {exc}", file=sys.stderr)
        print("Try 'repoctl --help' for usage.", file=sys.stderr)
        return 2

    command = parsed["command"]
    if parsed["help"]:
        print(_help_for(command), end="")
        return 0

    if command == "refresh":
        source = parsed["source"]
        try:
            payload = _read_json(source)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            print(f"repoctl: {exc}", file=sys.stderr)
            return 1

        result = {
            "cache": CACHE.as_posix(),
            "command": "refresh",
            "dry_run": parsed["dry_run"],
            "source": source,
            "status": "would_refresh" if parsed["dry_run"] else "refreshed",
        }
        if not parsed["dry_run"]:
            try:
                _write_cache(payload)
            except OSError as exc:
                print(f"repoctl: {exc}", file=sys.stderr)
                return 1
        _emit(
            result,
            (
                f"would refresh {CACHE.as_posix()} (dry-run)"
                if parsed["dry_run"]
                else f"refreshed {CACHE.as_posix()}"
            ),
            parsed["json"],
        )
        return 0

    if command == "doctor":
        status = _cache_status()
        _emit(
            {"cache": CACHE.as_posix(), "command": "doctor", "status": status},
            f"cache: {status}",
            parsed["json"],
        )
        return 0 if status == "ready" else 1

    _emit(
        {"command": "version", "status": "ok", "version": VERSION},
        f"repoctl {VERSION}",
        parsed["json"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
