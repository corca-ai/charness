from __future__ import annotations

import shutil
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def make_fake_nose(tmp_path: Path) -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    nose = bin_dir / "nose"
    curl = bin_dir / "curl"
    bin_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIXTURES / "fake_nose.py", nose)
    nose.chmod(0o755)
    curl.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    curl.chmod(0o755)
    return curl, nose
