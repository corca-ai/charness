from __future__ import annotations

from pathlib import Path

from tests.script_loader import load_script_module

_SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "public" / "release" / "scripts"


def load_release_script(name: str, *, suffix: str = "test"):
    return load_script_module(f"{name}_{suffix}", _SCRIPTS / f"{name}.py")
