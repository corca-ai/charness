from __future__ import annotations

from pathlib import Path

from scripts.subprocess_guard import TIMEOUT_EXIT_CODE, run_process


def test_run_process_returns_timeout_completed_process(tmp_path: Path) -> None:
    result = run_process(
        ["python3", "-c", "import time; time.sleep(2)"],
        cwd=tmp_path,
        timeout_seconds=0.1,
    )

    assert result.returncode == TIMEOUT_EXIT_CODE
    assert "timed out after 0.1s" in result.stderr
