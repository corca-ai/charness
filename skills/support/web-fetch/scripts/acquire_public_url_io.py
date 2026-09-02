from __future__ import annotations

from pathlib import Path
from typing import Sequence

from url_reader import read_url

try:
    from scripts.core import subprocess_guard as _subprocess_guard
except ModuleNotFoundError:
    _scripts_dir = next(
        (
            ancestor / "scripts"
            for ancestor in (Path(__file__).resolve(), *Path(__file__).resolve().parents)
            if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
        ),
        None,
    )
    if _scripts_dir is None:
        _subprocess_guard = None
    else:
        import sys

        sys.path.insert(0, str(_scripts_dir))
        import scripts.core.subprocess_guard as _subprocess_guard

run_process = _subprocess_guard.run_process if _subprocess_guard is not None else None

# Retain the module-level test seam while the actual spawn remains owned by the
# guard. Both names reference the same standard-library module object.
subprocess = _subprocess_guard.subprocess if _subprocess_guard is not None else None

HTML_ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
MARKDOWN_ACCEPT = "text/markdown"


def read_direct(
    url: str,
    *,
    timeout: int,
    direct_response_file: Path | None,
    accept: str = HTML_ACCEPT,
) -> tuple[str, str | None]:
    if direct_response_file is not None:
        return direct_response_file.read_text(encoding="utf-8"), None
    return read_url(
        url,
        timeout=timeout,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; charness-web-fetch/1.0)",
            "Accept": accept,
        },
    )


def run_command(command: Sequence[str], *, timeout: int) -> tuple[str, str | None]:
    if run_process is None:
        return "", "guard_unavailable:subprocess_guard.py not reachable"
    try:
        completed = run_process(
            list(command),
            cwd=Path.cwd(),
            timeout_seconds=timeout,
        )
    except Exception as exc:
        return "", f"{type(exc).__name__}:{str(exc)[:200]}"
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        return completed.stdout, f"exit={completed.returncode}:{stderr[:200]}"
    return completed.stdout, None
