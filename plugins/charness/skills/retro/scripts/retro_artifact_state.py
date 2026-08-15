#!/usr/bin/env python3
"""What TODAY's retro record is, which is not always where the scaffold would write.

The same seam the debug planner carries in `debug_artifact_state`: the plan is assembled FROM
this answer, and the length gate refused one file holding both. The scaffold refuses to write
a fresh template over an existing record and routes to a distinguished sibling, so once
today's retro exists its `write_artifact_path` names a file that does not -- and the
continue-existing arm is about the record that IS there.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _artifact_summary(repo_root: Path, scaffold: dict[str, Any]) -> dict[str, Any]:
    """TODAY's retro record, which is not always the path the scaffold would write.

    The scaffold refuses to write a fresh template over an existing record and routes to a
    distinguished sibling, so once today's retro exists its `write_artifact_path` names a file
    that does not. `refused_write_artifact_path` is the record that IS there, and it is the one
    this summary — and the continue-existing arm that reads it — is about.
    """
    refused = scaffold.get("refused_write_artifact_path")
    write_rel = str(refused if isinstance(refused, str) else scaffold["write_artifact_path"])
    # The refusal names the BASE path, which on a third retro of the day is the first record,
    # not the sibling actually in progress. Walk to the newest record the scaffold skipped so
    # the continue arm names the one an author would still be writing.
    if isinstance(refused, str):
        skipped = sorted(
            (candidate for candidate in (repo_root / Path(refused).parent).glob(f"{Path(refused).stem}*.md") if candidate.is_file()),
            key=lambda candidate: candidate.stat().st_mtime,
        )
        if skipped:
            write_rel = str(skipped[-1].relative_to(repo_root))
    write_path = repo_root / write_rel
    exists = write_path.is_file()
    line_count = len(write_path.read_text(encoding="utf-8").splitlines()) if exists else 0
    return {
        "path": write_rel,
        "exists": exists,
        "line_count": line_count,
        "status": "today_artifact_exists" if exists else "missing",
        "role": scaffold["artifact_role"],
    }
