"""`scripts.quality_policy_merge` must import on its own, in a fresh process.

It and `quality_policy_defaults` reference each other — the merge functions need the
DEFAULT_* dicts, and `defaults` re-exports the merge names so every existing importer
keeps working. A module-level import in both directions is a cycle that resolves in
exactly ONE order, and the whole test suite masks it: every current importer reaches
`defaults` first, so `merge` is always fully built by the time anything asks for it.

The first person to write a unit test starting `from scripts.quality_policy_merge
import ...` would have hit `ImportError: ... partially initialized module` in a
single-file pytest run nobody else could reproduce. This is that test, run in a
SUBPROCESS on purpose: in-process it would be satisfied by whatever a conftest or an
earlier test file already imported, which is precisely the masking being guarded
against.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.boundary_contract(
    reason="prove each quality-policy module imports first in a fresh interpreter without prior pytest module state"
)


@pytest.mark.parametrize(
    "first",
    ["scripts.quality_policy_merge", "scripts.quality_policy_defaults"],
)
def test_either_module_can_be_imported_first(first: str) -> None:
    result = subprocess.run(
        [sys.executable, "-c", f"import {first}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "partially initialized" not in result.stderr


def test_the_reexport_still_resolves_from_either_entry_point() -> None:
    """The cycle break must not cost the re-export: `quality_bootstrap_lib` imports all
    three merge names FROM `quality_policy_defaults`, so removing them from there to
    dodge the cycle would trade an import error for a different import error."""
    probe = (
        "from scripts.quality_policy_defaults import "
        "merge_coverage_floor_policy, merge_prompt_asset_policy, refilled_policy_subkeys; "
        "from scripts.quality_policy_merge import merge_coverage_floor_policy as m; "
        "assert m is merge_coverage_floor_policy"
    )
    result = subprocess.run([sys.executable, "-c", probe], cwd=ROOT, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
