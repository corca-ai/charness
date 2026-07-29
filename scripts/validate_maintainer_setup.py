#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# The env var `scripts/run-quality.sh` reads to arm the push-time changed-line
# refusal (`--refuse-unestablished`). The hook is its only setter, so the hook
# and the runner are two surfaces that must not disagree; the pin below is what
# stops them drifting apart silently.
PRE_PUSH_ARMING_VAR = "CHARNESS_PRE_PUSH"
QUALITY_RUNNER_BASENAME = "run-quality.sh"
# The runner as a command word. `$REPO_ROOT/` shapes are accepted because the
# hook already computes and `cd`s to `REPO_ROOT`, so writing the invocation that
# way is a refactor a maintainer would plausibly make.
QUALITY_RUNNER_RE = re.compile(
    r"""^(?:(?:bash|sh)\s+)?                       # an explicit interpreter
        (?:"?\$\{?REPO_ROOT\}?"?/|\./)?            # "$REPO_ROOT"/ or ./
        scripts/run-quality\.sh(?=\s|$)""",        # the runner itself, not .sh.bak
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
ENV_ASSIGNMENT_RE = re.compile(
    r'^([A-Za-z_][A-Za-z0-9_]*)=("[^"]*"|\'[^\']*\'|\S*)\s+'
)
# Constructs that MENTION the runner without running it. `[`/`[[` cover the
# defensive `if [[ ! -x ./scripts/run-quality.sh ]]` guard a maintainer would
# plausibly add; refusing that was a false stop, and this repo's own runner
# comment records that a false stop is how a lane stops being enforced.
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

    A `CHARNESS_PRE_PUSH=1 \\` + newline + runner invocation is one command that
    naive per-physical-line scanning reads as an unarmed one, and a heredoc body
    quoting the runner is data a maintainer may legitimately write (the hook
    already prints multi-line advice).
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
        # continue it. Joining first let `# CHARNESS_PRE_PUSH=1 \` swallow the
        # real invocation on the next line into a comment the scan then skipped,
        # which is a lane disarmed behind a PASS — round 2 found it, and it is
        # exactly what commenting out the first half of a continued command does.
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
            pairs.append((line[start:index], line[index:index + 2]))
            index += 2
            start = index
            continue
        # `2>&1` and `&>log` are redirections, not backgrounding.
        if char == "&" and (line[index - 1:index] == ">" or line[index + 1:index + 2] == ">"):
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
            command = command[modifier.end():]
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
            command = command[assignment.end():]
            continue
        return command, assignments


def quality_runner_invocations(
    hook_text: str,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Classify runner references into (armed, unarmed, unclear, swallowed).

    Buckets three and four are corrections, each found by a bounded review round
    reading the previous version and each reproduced by execution before being
    accepted.

    Round 1: the first version recognized ONE invocation spelling and silently
    skipped everything else. The hook has TWO invocations, so rewriting either as
    `exec ...`, `"$REPO_ROOT"/scripts/...`, `if ! ...`, `true | ...`, or via a
    variable left the other armed and the gate green — a lane disarmed behind a
    PASS, the exact class this gate exists to refuse, one level up. Hence
    `unclear`: a reference the parser cannot classify is reported, not dropped.

    Round 2, reading that repair, found it carrying the class again in four more
    places: a comment ending in `\\` swallowed the next line's real invocation, a
    `<<MSG` inside a comment or string made every following line invisible, an
    escaped `\\"` desynced the quote state enough to fabricate an ARMED entry out
    of an `echo`, and a `.sh`-suffixed stub path satisfied a `\\b` boundary. It also found
    that `... || true` and `... &` keep the var and discard the verdict, which
    disarms the lane more completely than dropping the prefix does — hence
    `swallowed`.

    Comments, heredoc bodies, and the known non-commands (`echo`, `printf`,
    `test`/`[`/`[[`, `:`, `command -v`) are the only ways a mention stays silent.
    """
    armed: list[str] = []
    unarmed: list[str] = []
    unclear: list[str] = []
    swallowed: list[str] = []
    exported: dict[str, str] = {}
    for line in _logical_lines(hook_text):
        if not line or line.startswith("#"):
            continue
        # `export VAR=1` on an earlier line arms every later invocation for real,
        # so reading only command-prefix assignments called a working hook broken.
        for name, value in re.findall(
            r"\bexport\s+([A-Za-z_][A-Za-z0-9_]*)=(\"[^\"]*\"|'[^']*'|\S*)", line
        ):
            exported[name] = value.strip("\"'")
        if QUALITY_RUNNER_BASENAME not in line:
            continue
        for chunk, separator in _split_commands(line):
            if QUALITY_RUNNER_BASENAME not in chunk:
                continue
            command, assignments = _strip_modifiers_and_env(chunk)
            if NOT_A_COMMAND_RE.match(command):
                continue
            if not QUALITY_RUNNER_RE.match(command):
                unclear.append(chunk)
                continue
            if separator in VERDICT_SWALLOWING_SEPARATORS:
                swallowed.append(f"{chunk} {separator}".strip())
                continue
            if {**exported, **assignments}.get(PRE_PUSH_ARMING_VAR) == "1":
                armed.append(chunk)
            else:
                unarmed.append(chunk)
    return armed, unarmed, unclear, swallowed


def check_pre_push_arming(hook_path: Path, rel_path: str) -> None:
    """Refuse a pre-push hook that no longer arms the changed-line lane.

    Existence was the only thing checked before, so deleting the
    `CHARNESS_PRE_PUSH=1` prefix left the lane disarmed with this gate green and
    a green push console — the exact silent-disarm the D40 lane was built to
    prevent. Reproduced against a copy of this repo's own hook before the fix.

    An invocation count of ZERO is an error, not a vacuous pass: "every
    invocation is armed" is trivially true for a hook that stopped invoking the
    runner at all, and that state is a bigger loss than an unarmed one.
    """
    armed, unarmed, unclear, swallowed = quality_runner_invocations(
        hook_path.read_text(encoding="utf-8")
    )
    if swallowed:
        raise ValidationError(
            f"`{rel_path}` runs the quality runner but discards its verdict: "
            f"{', '.join(repr(line) for line in swallowed)}. A trailing `|| ...`, "
            "`&`, or `|` means the push proceeds whatever the gate decided, which "
            "disarms the lane more completely than dropping the arming variable. "
            "Let the invocation's exit status reach the hook's exit status."
        )
    if unarmed:
        raise ValidationError(
            f"`{rel_path}` invokes the quality runner without arming the push-time "
            f"changed-line refusal: {', '.join(repr(line) for line in unarmed)}. "
            f"Prefix each invocation with `{PRE_PUSH_ARMING_VAR}=1` — "
            "`scripts/run-quality.sh` reads it to add `--refuse-unestablished`, and "
            "without it a push whose changed lines were never proven exits green."
        )
    if unclear:
        raise ValidationError(
            f"`{rel_path}` references `{QUALITY_RUNNER_BASENAME}` in a form this gate "
            f"cannot classify: {', '.join(repr(line) for line in unclear)}. That is "
            "refused rather than skipped, because a reference the gate cannot read is "
            "a lane it cannot prove is armed. If it is an invocation, write it as "
            f"`{PRE_PUSH_ARMING_VAR}=1 ./scripts/run-quality.sh ...`; if it is a guard "
            "or a message that only names the runner, teach this gate that shape in "
            "the same commit rather than working around it."
        )
    if not armed:
        raise ValidationError(
            f"`{rel_path}` no longer invokes `scripts/run-quality.sh` at all, so the "
            "push-time changed-line refusal cannot run. If the runner moved, update "
            "this gate with it rather than leaving the lane unenforced."
        )


def run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def resolve_hookspath(repo_root: Path, configured: str) -> Path:
    path = Path(configured)
    if path.is_absolute():
        return path.resolve()
    return (repo_root / path).resolve()


def is_charness_source_repo(repo_root: Path) -> bool:
    return (repo_root / "packaging" / "charness.json").is_file() and (repo_root / "plugins" / "charness").is_dir()


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
    missing_hooks = [str(path.relative_to(repo_root)) for path in expected_hooks if not path.exists()]
    if missing_hooks:
        raise ValidationError(
            "checked-in maintainer hook set is incomplete: "
            + ", ".join(missing_hooks)
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

    # Content, not just existence. Scoped to the source repo for the same reason
    # `pre-push` itself is: `install-git-hooks.sh` writes only a `commit-msg`
    # wrapper downstream, and no consumer repo runs this repo's quality runner.
    if "pre-push" in hook_names:
        check_pre_push_arming(repo_root / ".githooks" / "pre-push", ".githooks/pre-push")

    print(f"Validated maintainer hook setup via {expected_dir}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
