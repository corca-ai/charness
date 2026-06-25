from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from typing import NamedTuple

from .support import ROOT

_SPEC = importlib.util.spec_from_file_location(
    "inventory_skill_ergonomics",
    ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_skill_ergonomics.py",
)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


class Result(NamedTuple):
    returncode: int
    stdout: str
    stderr: str


def run_inventory_skill_ergonomics(*args: str) -> Result:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    sys.argv = ["inventory_skill_ergonomics.py", *args]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = _MODULE.main()
    finally:
        sys.argv = saved_argv
    return Result(returncode=code, stdout=out.getvalue(), stderr=err.getvalue())
