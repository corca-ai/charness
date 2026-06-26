from __future__ import annotations

from pathlib import Path

from scripts.subprocess_guard import TIMEOUT_EXIT_CODE, run_process, run_processes_in_order


def test_run_process_returns_timeout_completed_process(tmp_path: Path) -> None:
    result = run_process(
        ["python3", "-c", "import time; time.sleep(2)"],
        cwd=tmp_path,
        timeout_seconds=0.1,
    )

    assert result.returncode == TIMEOUT_EXIT_CODE
    assert "timed out after 0.1s" in result.stderr


def test_run_processes_in_order_preserves_input_order(tmp_path: Path) -> None:
    results = run_processes_in_order(
        [
            ["python3", "-c", "import time; time.sleep(0.2); print('slow')"],
            ["python3", "-c", "print('fast')"],
        ],
        cwd=tmp_path,
        timeout_seconds=None,
    )

    assert [result.stdout.strip() for result in results] == ["slow", "fast"]
