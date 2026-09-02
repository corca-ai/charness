#!/usr/bin/env python3
"""Compatibility entrypoint for the setup package's consumer doctor."""

from __future__ import annotations

import sys


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_doctor = import_repo_module(__file__, "scripts.setup.doctor")


def __getattr__(name: str):
    return getattr(_doctor, name)


def __dir__():
    return sorted(set(globals()) | set(dir(_doctor)))


main = _doctor.main


if __name__ != "__main__":
    # Keep imports and monkeypatching aimed at `scripts.doctor` attached to the
    # delegated consumer module, while direct execution still enters below.
    sys.modules[__name__] = _doctor


if __name__ == "__main__":
    raise SystemExit(main())
