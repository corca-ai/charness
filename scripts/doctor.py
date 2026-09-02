#!/usr/bin/env python3
"""Compatibility entrypoint for the setup package's consumer doctor."""

from __future__ import annotations

import sys

from runtime_bootstrap import import_repo_module

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
