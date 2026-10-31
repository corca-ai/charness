"""The backend shell line is quoted for the platform shell that will read it."""

from __future__ import annotations

import shlex
from pathlib import Path

from skills.shared.scripts.reviewer_process import shell_command_line


def test_posix_line_uses_exec_and_shlex_words() -> None:
    prompt = Path("p q") / "prompt.md"

    line = shell_command_line(["codex", "exec", "-C", "/a b"], prompt, windows=False)

    assert line == f"exec codex exec -C '/a b' < {shlex.quote(str(prompt))}"


def test_windows_line_uses_cmd_double_quotes_and_no_exec() -> None:
    line = shell_command_line(
        ["codex", "exec", "-C", "C:\\Users\\a b\\repo"], Path("C:\\run dir\\prompt.md"), windows=True
    )

    assert line == 'codex exec -C "C:\\Users\\a b\\repo" < "C:\\run dir\\prompt.md"'
