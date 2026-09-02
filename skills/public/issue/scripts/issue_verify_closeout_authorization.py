"""Build the authorization report attached to a closeout readback.

This module owns the post-publication authorization projection: it records the
targets and carrier used by verification without gating on authorization after
the close has already happened. That reporting seam is distinct from the
verifier's carrier and floor orchestration.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def authorization_record(
    repo_root: Path,
    repo: str,
    numbers: list[int],
    carrier: str,
    *,
    bootstrap: Path | None,
    caller_file: str,
) -> dict[str, Any]:
    """Return the reported authorization record for a completed closeout."""
    if bootstrap is None:
        return {
            "applies": False,
            "authorized": True,
            "crosswalk_status": "authorization_module_unavailable",
        }
    runtime = SimpleNamespace(**runpy.run_path(str(bootstrap)))
    module = runtime.load_local_skill_module(caller_file, "issue_closeout_authorization")
    record = module.authorize(
        invoked_targets=[
            {"repository": repo, "issue_number": number, "source": f"verify:{carrier}"}
            for number in numbers
        ],
        carrier_targets=[],
        carrier_source=f"verify-readback:{carrier}",
        repo_root=repo_root,
    )
    record["gating"] = (
        "reported-only: a post-publication readback cannot prevent a close that already happened"
    )
    return record
