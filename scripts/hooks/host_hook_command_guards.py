"""Command-time orchestration guards for host Bash hooks.

Three guards that ran for weeks as per-machine host settings now ship as
registry intents, installed for Claude Code PreToolUse(Bash) by the existing
host-hook install path. Each exists because a written rule was read at
session start and violated at the moment of temptation; a gate at the
command fires where the decision is.

Shared shape: match only the executable part (quoted strings and heredoc
bodies are stripped first, since a commit message describing a command is
not the command), fail open on any parse surprise, require a stated reason
for every override, and append each block to the friction log so a repeat
within a day escalates. Genuinely local guards (for example a retired
toolchain) stay in the repository's own tracked host settings, not here.

A repository adapter extends the tables without forking the guard: the hook
payload's working directory resolves the enclosing repository, and that
repository's `.agents/command-guards.local.yaml` may add `extra_patterns`
per guard (id, pattern, reason, overridable) and `extra_verdict_commands`.
Malformed adapter files fail open to the built-in tables.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.hooks.host_hook_command_patterns import (  # noqa: E402
    DISCARD_PATTERNS,
    DISCARD_WORKTREE,
    FIXED_WIDTH_PATTERNS,
    GUARD_KEYS,
    OVERRIDE_MARKERS,
    PARALLEL_WINDOW,
    PARALLEL_WINDOW_PATTERNS,
    VERDICT_CHANNEL,
    VERDICT_COMMANDS,
    GuardPattern,
)
from scripts.runtime_bootstrap import runtime_root  # noqa: E402
from scripts.task_run import task_run_friction as _friction  # noqa: E402

HOOK_REPEAT_WINDOW = timedelta(days=1)
HOOK_REPEAT_ESCALATION = "repair the habit or the tooling, not the command"

ADAPTER_RELATIVE = Path(".agents/command-guards.local.yaml")


_QUOTED_SPAN = re.compile(
    r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|`(?:[^`\\]|\\.)*`",
    re.DOTALL,
)
_HEREDOC_OPEN = re.compile(r"<<-?\s*'?\"?([A-Za-z_][A-Za-z0-9_]*)'?\"?")
_SEPARATOR = re.compile(r";|\|\||&&|\||&|\n")
_TEST_FILE = re.compile(r"^[\w./-]+\.(?:py|js|ts|tsx|jsx|go|rs|rb|java)$")


def _heredoc_split(line: str) -> tuple[str, str | None]:
    """Split an unquoted heredoc opener off; quoted `<<` is not an opener.

    A quoted heredoc delimiter (`<<'EOF'`) is shell syntax, not a quoted
    span — so neither a quote-strip-first nor a heredoc-first pass is
    correct alone; the opener must be found outside quotes.
    """
    index = 0
    end = len(line)
    quote: str | None = None
    while index < end:
        char = line[index]
        if quote is not None:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "'\"`":
            quote = char
            index += 1
            continue
        if line.startswith("<<", index):
            match = _HEREDOC_OPEN.match(line, index)
            if match is not None:
                return line[:index], match.group(1)
            index += 2
            continue
        index += 1
    return line, None


def strip_non_executable(command: str) -> str:
    """Remove heredoc bodies and quoted strings; fail open to the input."""
    try:
        lines = command.splitlines(keepends=True)
        kept: list[str] = []
        skip_delimiter: str | None = None
        for line in lines:
            if skip_delimiter is not None:
                if line.strip() == skip_delimiter:
                    skip_delimiter = None
                continue
            head, delimiter = _heredoc_split(line)
            if delimiter is not None:
                skip_delimiter = delimiter
                kept.append(head)
                continue
            kept.append(line)
        return _QUOTED_SPAN.sub(" ", "".join(kept))
    except Exception:  # noqa: BLE001 - a guard never breaks a command it cannot parse
        return command


def split_segments(executable: str) -> list[str]:
    """Split on shell separators; fail open to one segment."""
    try:
        return [part.strip() for part in _SEPARATOR.split(executable) if part.strip()]
    except Exception:  # noqa: BLE001 - fail open
        return [executable]


def override_reason(command: str, guard: str) -> str | None:
    """The stated `#<marker>: <reason>`, or None when absent or reasonless."""
    marker = OVERRIDE_MARKERS[guard]
    match = re.search(r"#" + re.escape(marker) + r"\s*:\s*(.+)$", command)
    if match is None:
        return None
    reason = match.group(1).strip()
    return reason or None


def is_backgrounded(command: str) -> bool:
    """A trailing `&` (past an optional trailing comment) backgrounds the call."""
    text = re.sub(r"#[^\n]*$", "", command).rstrip()
    return text.endswith("&")


def _pattern_block(
    segments: Sequence[str], patterns: Sequence[GuardPattern], command: str, guard: str
) -> dict[str, Any] | None:
    reason = override_reason(command, guard)
    for entry in patterns:
        try:
            regex = re.compile(entry.pattern)
        except re.error:
            continue
        if not any(regex.search(segment) for segment in segments):
            continue
        if reason is not None and entry.overridable:
            continue
        if reason is None:
            hint = (
                f"reword with #{OVERRIDE_MARKERS[guard]}: <reason>"
                if entry.overridable
                else "run this shape as a host background job instead"
            )
        else:
            hint = f"#{OVERRIDE_MARKERS[guard]} does not apply to this pattern"
        return {
            "guard": guard,
            "pattern_id": entry.id,
            "reason": entry.reason,
            "hint": hint,
        }
    return None


def _sleep_seconds_ok(segment: str) -> bool:
    match = re.search(r"(?<![\w-])sleep\s+(\d+)", segment)
    return match is not None and int(match.group(1)) < 5


def _single_test_file_selected(segment: str) -> bool:
    tokens = segment.split()
    if not tokens:
        return False
    if tokens[0] not in {"pytest", "jest", "vitest", "mocha"} and not (
        len(tokens) > 2 and tokens[0] in {"python", "python3"} and tokens[1] == "-m"
    ):
        return False
    paths = [
        token
        for token in tokens[1:]
        if not token.startswith("-") and token not in {"pytest", "tests"}
    ]
    return len(paths) == 1 and bool(_TEST_FILE.fullmatch(paths[0]))


def _window_hit(entry: GuardPattern, segments: Sequence[str]) -> bool:
    for segment in segments:
        try:
            matched = re.search(entry.pattern, segment) is not None
        except re.error:
            continue
        if not matched:
            continue
        if entry.id == "long-sleep" and _sleep_seconds_ok(segment):
            continue
        if entry.id == "test-bundle" and _single_test_file_selected(segment):
            continue
        return True
    return False


def check_parallel_window(
    command: str, *, extra: Sequence[GuardPattern] = ()
) -> dict[str, Any] | None:
    """Block a long foreground call unless it is backgrounded."""
    executable = strip_non_executable(command)
    if is_backgrounded(executable):
        return None
    # No try here: split_segments fails open internally, so an outer guard
    # would be dead code no test could honestly cover.
    segments = split_segments(executable)
    narrow = [
        entry for entry in (*PARALLEL_WINDOW_PATTERNS, *extra)
        if _window_hit(entry, segments)
    ]
    if not narrow:
        return None
    return _pattern_block(segments, narrow, command, PARALLEL_WINDOW)


def _verdict_bearing(segment: str, commands: Sequence[str]) -> bool:
    lowered = segment.lower()
    return any(
        re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", lowered)
        for name in commands
    )


def _status_reraised(executable: str) -> bool:
    return (
        re.search(r"(?<![\w-])(?:tee\b|>)", executable) is not None
        and re.search(r"=\$\?", executable) is not None
        and re.search(r"(?<![\w-])exit\s+\$", executable) is not None
    )


def _final_test_reraise(segments: Sequence[str]) -> bool:
    if not segments:
        return False
    final = segments[-1]
    return re.match(r"\s*(?:\[|test\b|\[\[)", final) is not None and "$" in final


def check_verdict_channel(
    command: str,
    *,
    extra_commands: Sequence[str] = (),
    extra: Sequence[GuardPattern] = (),
) -> dict[str, Any] | None:
    """Block a verdict-bearing command composed past its own status."""
    executable = strip_non_executable(command)
    # No try here: split_segments fails open internally (see parallel window).
    segments = split_segments(executable)
    if len(segments) < 2:
        masked = False
    else:
        commands = (*VERDICT_COMMANDS, *extra_commands)
        masked = any(
            _verdict_bearing(segment, commands) for segment in segments[:-1]
        )
    width_block = _pattern_block(segments, (*FIXED_WIDTH_PATTERNS, *extra), command, VERDICT_CHANNEL)
    if width_block is not None:
        return width_block
    if not masked:
        return None
    if _status_reraised(executable) or _final_test_reraise(segments):
        return None
    reason = override_reason(command, VERDICT_CHANNEL)
    if reason is not None:
        return None
    verdict = next(
        segment
        for segment in segments[:-1]
        if _verdict_bearing(segment, (*VERDICT_COMMANDS, *extra_commands))
    )
    return {
        "guard": VERDICT_CHANNEL,
        "pattern_id": "verdict-masking-composition",
        "reason": (
            f"a verdict-bearing command ({verdict.strip()[:80]}) composed with a "
            "later command reports the last element's status"
        ),
        "hint": "capture to a minted path and re-raise with exit $rc, "
        "or run the verdict command alone",
    }


def check_discard_worktree(
    command: str, *, extra: Sequence[GuardPattern] = ()
) -> dict[str, Any] | None:
    """Block worktree-destroying commands without a stated reason."""
    executable = strip_non_executable(command)
    # No try here: split_segments fails open internally (see parallel window).
    segments = split_segments(executable)
    return _pattern_block(segments, (*DISCARD_PATTERNS, *extra), command, DISCARD_WORKTREE)


CHECKERS = {
    PARALLEL_WINDOW: check_parallel_window,
    VERDICT_CHANNEL: check_verdict_channel,
    DISCARD_WORKTREE: check_discard_worktree,
}


def _adapter_file(repo_root: Path | None) -> Path | None:
    if repo_root is None:
        return None
    candidate = repo_root / ADAPTER_RELATIVE
    try:
        return candidate if candidate.is_file() else None
    except OSError:
        return None


def repo_root_for(cwd: str | None) -> Path | None:
    """Enclosing repository of the hook's working directory, else None."""
    if not cwd:
        return None
    try:
        here = Path(cwd).expanduser().resolve()
    except (OSError, RuntimeError):
        return None
    for candidate in (here, *here.parents):
        try:
            if (candidate / ".git").exists() or (candidate / ".agents").is_dir():
                return candidate
        except OSError:
            continue
    return None


def load_adapter_extras(repo_root: Path | None) -> dict[str, Any]:
    """Adapter pattern extensions for one repository; fail open to empty."""
    path = _adapter_file(repo_root)
    if path is None:
        return {"extra_verdict_commands": [], "extra_patterns": {}}
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - malformed adapters fail open
            return {"extra_verdict_commands": [], "extra_patterns": {}}
    else:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - malformed adapters fail open
            return {"extra_verdict_commands": [], "extra_patterns": {}}
    if not isinstance(data, Mapping):
        return {"extra_verdict_commands": [], "extra_patterns": {}}
    commands = data.get("extra_verdict_commands", [])
    commands = [item for item in commands if isinstance(item, str) and item.strip()]
    patterns: dict[str, list[GuardPattern]] = {}
    raw_patterns = data.get("extra_patterns", {})
    if isinstance(raw_patterns, Mapping):
        for guard, entries in raw_patterns.items():
            if guard not in GUARD_KEYS or not isinstance(entries, list):
                continue
            rows = []
            for row in entries:
                if not isinstance(row, Mapping):
                    continue
                pid = row.get("id")
                pattern = row.get("pattern")
                reason = row.get("reason")
                if not all(isinstance(value, str) for value in (pid, pattern, reason)):
                    continue
                try:
                    re.compile(pattern)
                except re.error:
                    continue
                rows.append(
                    GuardPattern(
                        id=pid,
                        pattern=pattern,
                        reason=reason,
                        overridable=row.get("overridable", True) is True,
                    )
                )
            patterns[guard] = rows
    return {"extra_verdict_commands": commands, "extra_patterns": patterns}


def check_command(
    command: str, guard: str, *, repo_root: Path | None = None
) -> dict[str, Any] | None:
    """Run one guard with its repository adapter extensions; fail open."""
    if guard not in CHECKERS:
        return None
    try:
        extras = load_adapter_extras(repo_root)
        if guard == VERDICT_CHANNEL:
            return check_verdict_channel(
                command,
                extra_commands=extras["extra_verdict_commands"],
                extra=list(extras["extra_patterns"].get(guard, ())),
            )
        if guard == PARALLEL_WINDOW:
            return check_parallel_window(
                command, extra=list(extras["extra_patterns"].get(guard, ()))
            )
        return check_discard_worktree(
            command, extra=list(extras["extra_patterns"].get(guard, ()))
        )
    except Exception:  # noqa: BLE001 - a guard never breaks a command it cannot judge
        return None


def record_block(
    installing_repo: Path, block: Mapping[str, Any], command: str
) -> dict[str, Any] | None:
    """Append the block to the friction log; the repeat carries escalation."""
    try:
        runtime_path = runtime_root(installing_repo, dict(os.environ))
    except Exception:  # noqa: BLE001 - logging must not break the verdict
        return None
    try:
        return _friction.append_friction_event(
            runtime_path,
            "block",
            task_id=f"command-guard:{block['guard']}:{uuid.uuid4().hex[:8]}",
            facts={
                "guard": block["guard"],
                "pattern_id": block.get("pattern_id", ""),
                "reason": str(block.get("reason", ""))[:500],
                "command": command[:500],
                "producer": "command-guard",
            },
            repeat_window=HOOK_REPEAT_WINDOW,
            escalation=HOOK_REPEAT_ESCALATION,
        )
    except (OSError, ValueError):
        return None


def evaluate_hook_payload(
    payload: Mapping[str, Any], installing_repo: Path
) -> dict[str, Any] | None:
    """Evaluate every guard over a PreToolUse payload; first block wins."""
    try:
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, Mapping):
            return None
        command = tool_input.get("command")
        if not isinstance(command, str) or not command.strip():
            return None
        repo_root = repo_root_for(payload.get("cwd"))
        for guard in GUARD_KEYS:
            block = check_command(command, guard, repo_root=repo_root)
            if block is not None:
                event = record_block(installing_repo, block, command)
                facts = event.get("facts", {}) if isinstance(event, Mapping) else {}
                message = f"command guard [{guard}] blocked: {block['reason']}"
                if facts.get("escalation"):
                    message += f" {facts['escalation']}."
                message += f" ({block.get('hint', '')})"
                return {"blocked": True, "guard": guard, "message": message}
        return {"blocked": False}
    except Exception:  # noqa: BLE001 - malformed hook input exits 0 (fail open)
        return None


def run_guards(command: str, *, repo_root: Path | None = None) -> list[dict[str, Any]]:
    """Evaluate every guard over a raw command (fixture/testing surface)."""
    found: list[dict[str, Any]] = []
    for guard in GUARD_KEYS:
        try:
            block = check_command(command, guard, repo_root=repo_root)
        except Exception:  # noqa: BLE001 - fail open per guard
            continue
        if block is not None:
            found.append(block)
    return found
