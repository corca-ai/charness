from __future__ import annotations

import sqlite3
from collections import deque
from pathlib import Path


def choose_source(home: Path, requested: str) -> tuple[str, Path]:
    sqlite_path = home / ".codex" / "logs_2.sqlite"
    tui_path = home / ".codex" / "log" / "codex-tui.log"
    if requested == "sqlite":
        return "sqlite", sqlite_path
    if requested == "tui":
        return "tui", tui_path
    if sqlite_path.exists() and sqlite_status(sqlite_path) == "used":
        return "sqlite", sqlite_path
    return ("tui", tui_path) if tui_path.exists() else ("sqlite", sqlite_path)


def source_status(source_kind: str, source_path: Path) -> str:
    if not source_path.exists():
        return "missing"
    return sqlite_status(source_path) if source_kind == "sqlite" else "used"


def sqlite_status(path: Path) -> str:
    try:
        connection = sqlite3.connect(path)
        try:
            table_rows = connection.execute(
                "select name from sqlite_master where type='table' and name='logs'"
            ).fetchall()
            column_rows = connection.execute("pragma table_info(logs)").fetchall()
        finally:
            connection.close()
    except sqlite3.Error:
        return "unreadable"
    columns = {str(row[1]) for row in column_rows}
    required = {"id", "ts", "ts_nanos", "feedback_log_body", "estimated_bytes", "thread_id"}
    return "used" if table_rows and required <= columns else "unreadable"


def tail_text_lines(path: Path, max_lines: int) -> list[tuple[int, str]]:
    if max_lines <= 0:
        with path.open(encoding="utf-8", errors="replace") as handle:
            return [(index, line.rstrip("\n")) for index, line in enumerate(handle, start=1)]
    buffer: deque[tuple[int, str]] = deque(maxlen=max_lines)
    with path.open(encoding="utf-8", errors="replace") as handle:
        for index, line in enumerate(handle, start=1):
            buffer.append((index, line.rstrip("\n")))
    return list(buffer)
