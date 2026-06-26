from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence

from url_reader import read_url


def read_direct(url: str, *, timeout: int, direct_response_file: Path | None) -> tuple[str, str | None]:
    if direct_response_file is not None:
        return direct_response_file.read_text(encoding="utf-8"), None
    return read_url(
        url,
        timeout=timeout,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; charness-web-fetch/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )


def run_command(command: Sequence[str], *, timeout: int) -> tuple[str, str | None]:
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:
        return "", f"{type(exc).__name__}:{str(exc)[:200]}"
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        return completed.stdout, f"exit={completed.returncode}:{stderr[:200]}"
    return completed.stdout, None
