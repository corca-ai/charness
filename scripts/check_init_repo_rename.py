#!/usr/bin/env python3
"""Fail-closed validator for the Leg 6 `init-repo` -> `setup` rename.

Scans every tracked file in the repo for the words `init-repo` and `init_repo`
(case-insensitive) and fails when a cite lands outside the contracted
allowlist at `scripts/check_init_repo_rename.allowlist.txt`.

Allowlist format: one entry per line, `<path>\\t<reason>`. Lines with a
trailing `/` are treated as directory prefixes. Lines that start with `#`
or are blank are ignored.

Exit status:
  0 — every cite is allowlisted
  1 — at least one cite is outside the allowlist (fail-closed)
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Iterable


def _load_scan_lib():
    spec = importlib.util.spec_from_file_location(
        "rename_allowlist_scan_lib",
        Path(__file__).resolve().parent / "rename_allowlist_scan_lib.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError("rename_allowlist_scan_lib.py not found")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_scan_lib = _load_scan_lib()

# Match `init-repo` and `init_repo` with alpha-only boundaries so identifiers
# like `setup_init_repo_adapter` and Korean-adjacent prose do not silently
# slip past.
INIT_REPO_RE = re.compile(r"(?<![A-Za-z])init[-_]repo(?![A-Za-z])", re.IGNORECASE)

ALLOWLIST_PATH = "scripts/check_init_repo_rename.allowlist.txt"


def main(argv: Iterable[str] | None = None) -> int:
    return _scan_lib.run_validator(
        description=__doc__ or "",
        argv=argv,
        pattern=INIT_REPO_RE,
        allowlist_default=ALLOWLIST_PATH,
        validator_name="init-repo-rename",
    )


if __name__ == "__main__":
    sys.exit(main())
