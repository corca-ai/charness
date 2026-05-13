#!/usr/bin/env python3
"""Shared helper for SKILL.md-gated public/support skill directory walks.

Several validators need the same shape: list directory names under a given
base (typically `<repo>/skills/public` or `<repo>/skills/support`) that are
real skills, where "real skill" means the directory contains a `SKILL.md`.
Some callers also need to exclude machine-managed sibling directories such
as `generated`.

Centralizing the walk keeps the SKILL.md-gating contract consistent across
`public_skill_validation_lib`, `skill_t_inventory_lib`,
`validate_skill_t_inventory`, and `validate_packaging_install_surface`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def iter_skill_ids(base_dir: Path, *, exclude: Iterable[str] = ()) -> list[str]:
    """Return sorted directory names under `base_dir` that contain a SKILL.md.

    Returns an empty list when `base_dir` does not exist. Names in `exclude`
    are filtered out before the SKILL.md gate runs.
    """
    if not base_dir.is_dir():
        return []
    excluded = set(exclude)
    return sorted(
        path.name
        for path in base_dir.iterdir()
        if path.is_dir()
        and path.name not in excluded
        and (path / "SKILL.md").is_file()
    )
