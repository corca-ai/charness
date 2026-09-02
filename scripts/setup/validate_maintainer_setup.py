#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.core.subprocess_guard import run_process
except ModuleNotFoundError:  # executed directly from scripts/
    from scripts.core.subprocess_guard import run_process

CLOSE_KEYWORD_GUARD_BASENAME = "prepush_close_keyword_guard.py"
# The interpreter is required: `scripts/prepush_close_keyword_guard.py` alone would
# also match the string inside an `echo`, which is the mention-counted-as-invocation
# hole this replaced.
CLOSE_KEYWORD_GUARD_RE = re.compile(
    r"""^(?:python3?|/usr/bin/env\s+python3?)\s+
        (?:"?\$\{?REPO_ROOT\}?"?/|\./)?
        scripts/prepush_close_keyword_guard\.py(?=\s|$)""",
    re.VERBOSE,
)
# Shell words that can sit in front of a command without changing which command
# runs. Stripped so `exec`/`if !`/`time cmd` stay recognizable as invocations
# rather than dropping out of the scan entirely.
COMMAND_MODIFIER_RE = re.compile(
    r"^(?:!|if|elif|while|until|then|do|exec|time|command|nohup|nice|builtin)\s+"
)
# One `VAR=value` assignment at the head of a command. Applied repeatedly rather
# than as one greedy prefix so the LAST assignment of a repeated var wins, the
# way the shell resolves it. Same shape as
# `standing_gate_discovery_lib.ENV_PREFIX_RE`; deliberately duplicated rather
# than imported, because this script is copied standalone into consumer repos by
# `install-git-hooks.sh` and must not grow a cross-tree import.
ENV_ASSIGNMENT_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)=("[^"]*"|\'[^\']*\'|\S*)\s+')
# Constructs that mention a command without running it. `[`/`[[` cover defensive
# shell guards, while `echo`/`printf` cover operator-facing advice in the hook.
NOT_A_COMMAND_RE = re.compile(r"^(?:echo|printf|test|\[\[?|:(?:\s|$)|command\s+-v)")
# Separators AFTER an invocation that discard its exit status: `|| fallback`
# swallows the failure, `&` backgrounds it, and `|` makes the pipeline's last
# command own the status. An invocation whose verdict cannot block the push is
# not armed in any sense the operator would recognize.
VERDICT_SWALLOWING_SEPARATORS = ("||", "&", "|")


class ValidationError(Exception):
    pass


def _logical_lines(hook_text: str) -> list[str]:
    """Hook text as logical lines: continuations joined, heredoc bodies dropped.

    A continued command is one logical line, and a heredoc body quoting a command
    is data a maintainer may legitimately write (the hook already prints advice).
    """
    lines: list[str] = []
    pending = ""
    heredoc_terminator: str | None = None
    for raw in hook_text.splitlines():
        if heredoc_terminator is not None:
            if raw.strip() == heredoc_terminator:
                heredoc_terminator = None
            continue
        stripped = raw.strip()
        if pending:
            stripped = pending + " " + stripped
            pending = ""
        # A comment ends at the newline: a trailing `\` inside one does NOT
        # continue it. Joining first can swallow a real command on the next line
        # into a comment, so comments are recognized before continuations.
        if stripped.startswith("#"):
            lines.append(stripped)
            continue
        if stripped.endswith("\\") and not stripped.endswith("\\\\"):
            pending = stripped[:-1].rstrip()
            continue
        heredoc_terminator = _heredoc_terminator(stripped)
        lines.append(stripped)
    if pending:
        lines.append(pending)
    return lines


def _heredoc_terminator(line: str) -> str | None:
    """The heredoc terminator this line opens, or None.

    Both halves matter and each was a defect. The `<<` must be real shell syntax:
    inside a string it is prose (`echo "we use <<MSG"`), and inside `$(( ))` it is
    a left shift (`$(( 1 << bits ))`) — treating either as an opener made every
    following line invisible to the scan, so an invocation after it disappeared
    silently. But the TERMINATOR is commonly quoted (`cat <<'EOF'`), so it has to
    be read from the raw text rather than from a quote-blanked copy; blanking it
    made the real hook's own heredoc unreadable and turned a legitimate advice
    block into a refusal.
    """
    for index in _unquoted_indexes(line, skip_arithmetic=True):
        if line.startswith("<<", index) and not line.startswith("<<<", index):
            match = re.match(r"<<-?\s*[\"']?([A-Za-z_][A-Za-z0-9_]*)", line[index:])
            if match:
                return match.group(1)
    return None


def _unquoted_indexes(line: str, *, skip_arithmetic: bool = False) -> list[int]:
    """Indexes of `line` that sit outside quotes, with backslash escapes consumed.

    One scanner, two callers. Both the heredoc detector and the command splitter
    need "is this character shell syntax or string content", and hand-rolling the
    quote state twice is how the two would drift into disagreeing about the same
    line — which is the failure shape this whole gate exists to refuse.

    `skip_arithmetic` also drops `$(( ... ))` spans, where `<<` is a left shift
    rather than a heredoc opener. The splitter does not want that: a `;` inside
    an arithmetic expansion still separates nothing it cares about, but dropping
    the span would silently move its chunk boundaries.
    """
    indexes: list[int] = []
    quote: str | None = None
    index = 0
    while index < len(line):
        char = line[index]
        if char == "\\" and quote != "'":
            index += 2
            continue
        if skip_arithmetic and not quote and line.startswith("$((", index):
            close = line.find("))", index)
            index = len(line) if close == -1 else close + 2
            continue
        if quote:
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "\"'":
            quote = char
            index += 1
            continue
        indexes.append(index)
        index += 1
    return indexes


def _split_commands(line: str) -> list[tuple[str, str]]:
    """Split a logical line into (chunk, separator-that-follows) pairs.

    Quote and backslash awareness are both load-bearing. The real hook echoes the
    runner's path inside a double-quoted status string, so a blind split on `;`
    would cut that string open and hand back a fragment that looks like a bare
    invocation; and an escaped `\\"` inside a double-quoted string desynced the
    quote state badly enough to fabricate an ARMED entry out of an `echo`.

    The trailing separator is returned because it decides whether the chunk's
    exit status can still block the push.
    """
    unquoted = set(_unquoted_indexes(line))
    pairs: list[tuple[str, str]] = []
    start = 0
    index = 0
    while index < len(line):
        if index not in unquoted:
            index += 1
            continue
        char = line[index]
        if line.startswith("&&", index) or line.startswith("||", index):
            pairs.append((line[start:index], line[index : index + 2]))
            index += 2
            start = index
            continue
        # `2>&1` and `&>log` are redirections, not backgrounding.
        if char == "&" and (line[index - 1 : index] == ">" or line[index + 1 : index + 2] == ">"):
            index += 1
            continue
        if char in ";|&":
            pairs.append((line[start:index], char))
            index += 1
            start = index
            continue
        index += 1
    pairs.append((line[start:], ""))
    return [(chunk.strip(), separator) for chunk, separator in pairs if chunk.strip()]


def _strip_modifiers_and_env(chunk: str) -> tuple[str, dict[str, str]]:
    """Peel command modifiers and env assignments off a command chunk.

    Returns the remaining command plus the assignments that would be in its
    environment, last-wins. `env VAR=1 cmd` is folded into the same dict so the
    two spellings cannot disagree.
    """
    assignments: dict[str, str] = {}
    command = chunk
    while True:
        modifier = COMMAND_MODIFIER_RE.match(command)
        if modifier:
            command = command[modifier.end() :]
            continue
        if re.match(r"^env\s+(?=[A-Za-z_][A-Za-z0-9_]*=)", command):
            command = re.sub(r"^env\s+", "", command)
            continue
        assignment = ENV_ASSIGNMENT_RE.match(command)
        if assignment:
            name, value = assignment.group(1), assignment.group(2)
            if value[:1] in "\"'" and value[:1] == value[-1:]:
                value = value[1:-1]
            assignments[name] = value
            command = command[assignment.end() :]
            continue
        return command, assignments


def check_close_keyword_guard_arming(hook_path: Path, rel_path: str) -> None:
    """Refuse a pre-push hook that no longer runs the close-keyword guard.

    Deleting the guard's line leaves this gate green and the push console green, and the loss is an
    irreversible GitHub close rather than an unproven line. It is checked HERE
    rather than left to the hook's own tests because those exercise the guard
    through a stub -- they prove the wiring carries stdin, not that the wiring is
    still present in the shipped hook.

    Presence and verdict-reachability only. Whether the guard is CORRECT is
    `tests/quality_gates/test_prepush_close_keyword_guard.py`'s job; what cannot
    be delegated there is that the hook still calls it.

    It runs through the shared `_logical_lines`/`_split_commands`/`NOT_A_COMMAND_RE`
    machinery, and that is the whole content of this
    function's round-2 repair. The first version matched raw physical lines for
    the basename, which passed on `echo "run prepush_close_keyword_guard.py
    yourself"`, on a heredoc advice block naming it, and on a trailing comment --
    and its `|| true` detection tested the suffix of the basename's line, which is
    the FIRST of the invocation's two continued lines, so appending `|| true` to
    the second one disarmed the guard behind a green check. Both are the class the
    the earlier round-2 review already removed one lane over; re-deriving the
    judgment instead of calling it re-created them.
    """
    invocations, unclear, swallowed = close_keyword_guard_invocations(
        hook_path.read_text(encoding="utf-8")
    )
    if unclear:
        raise ValidationError(
            f"`{rel_path}` references `{CLOSE_KEYWORD_GUARD_BASENAME}` in a form this "
            f"gate cannot classify: {', '.join(repr(chunk) for chunk in unclear)}. That "
            "is refused rather than skipped, because a reference the gate cannot read "
            "is a lane it cannot prove is armed."
        )
    if swallowed:
        raise ValidationError(
            f"`{rel_path}` runs the close-keyword guard but discards its verdict: "
            f"{', '.join(repr(chunk) for chunk in swallowed)}. A refusal that cannot "
            "stop the push is not a floor."
        )
    if not invocations:
        raise ValidationError(
            f"`{rel_path}` no longer runs `scripts/{CLOSE_KEYWORD_GUARD_BASENAME}`, so a "
            "commit whose message close-keywords a GitHub issue can land unfloored and "
            "close it. That act is not undoable by pushing again. If the guard moved, "
            "update this gate with it rather than leaving the boundary unguarded."
        )


def close_keyword_guard_invocations(hook_text: str) -> tuple[list[str], list[str], list[str]]:
    """Classify close-keyword-guard references into (invoked, unclear, swallowed).

    The guard is the last command of a pipeline in the shipped hook
    (``printf ... | python3 scripts/prepush_close_keyword_guard.py ...``), so the
    separator that FOLLOWS its chunk is empty and its exit status is the
    pipeline's. A `|` after it would not be.
    """
    invoked: list[str] = []
    unclear: list[str] = []
    swallowed: list[str] = []
    for line in _logical_lines(hook_text):
        if not line or line.startswith("#") or CLOSE_KEYWORD_GUARD_BASENAME not in line:
            continue
        for chunk, separator in _split_commands(line):
            if CLOSE_KEYWORD_GUARD_BASENAME not in chunk:
                continue
            command, _assignments = _strip_modifiers_and_env(chunk)
            if NOT_A_COMMAND_RE.match(command):
                continue
            if not CLOSE_KEYWORD_GUARD_RE.match(command):
                unclear.append(chunk)
            elif separator in VERDICT_SWALLOWING_SEPARATORS:
                swallowed.append(f"{chunk} {separator}".strip())
            else:
                invoked.append(chunk)
    return invoked, unclear, swallowed


def run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_process(["git", *args], cwd=repo_root, timeout_seconds=None)


def resolve_hookspath(repo_root: Path, configured: str) -> Path:
    path = Path(configured)
    if path.is_absolute():
        return path.resolve()
    return (repo_root / path).resolve()


def is_charness_source_repo(repo_root: Path) -> bool:
    return (repo_root / "packaging" / "charness.json").is_file() and (
        repo_root / "plugins" / "charness"
    ).is_dir()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    hook_names = ["commit-msg"]
    if is_charness_source_repo(repo_root):
        hook_names = ["pre-commit", "commit-msg", "pre-push"]
    expected_hooks = [repo_root / ".githooks" / name for name in hook_names]
    present_hooks = [path for path in expected_hooks if path.exists()]
    if not present_hooks:
        print("No checked-in maintainer hooks to validate.")
        return 0
    missing_hooks = [
        str(path.relative_to(repo_root)) for path in expected_hooks if not path.exists()
    ]
    if missing_hooks:
        raise ValidationError(
            "checked-in maintainer hook set is incomplete: " + ", ".join(missing_hooks)
        )

    worktree = run_git(repo_root, "rev-parse", "--is-inside-work-tree")
    if worktree.returncode != 0 or worktree.stdout.strip() != "true":
        print("Repo is not a git worktree; maintainer hook validation skipped.")
        return 0

    configured = run_git(repo_root, "config", "--get", "core.hooksPath")
    if configured.returncode != 0 or not configured.stdout.strip():
        raise ValidationError(
            "checked-in `.githooks` maintainer hooks are not active in this clone; run `./scripts/install-git-hooks.sh`"
        )

    configured_path = resolve_hookspath(repo_root, configured.stdout.strip())
    expected_dir = (repo_root / ".githooks").resolve()
    if configured_path != expected_dir:
        raise ValidationError(
            f"core.hooksPath points to `{configured.stdout.strip()}` instead of repo-owned `.githooks`; "
            "run `./scripts/install-git-hooks.sh`"
        )

    # Content, not just existence. Scoped to the source repo because
    # `install-git-hooks.sh` writes only a `commit-msg` wrapper downstream.
    if "pre-push" in hook_names:
        check_close_keyword_guard_arming(repo_root / ".githooks" / "pre-push", ".githooks/pre-push")

    print(f"Validated maintainer hook setup via {expected_dir}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
