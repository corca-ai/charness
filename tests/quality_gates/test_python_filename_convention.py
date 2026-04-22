from __future__ import annotations

from .support import ROOT, run_script


def test_python_filenames_use_snake_case() -> None:
    result = run_script("scripts/check_python_filenames.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
