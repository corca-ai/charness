from __future__ import annotations

import json

from .support import ROOT, run_script


def test_retro_auto_trigger_hits_configured_install_surface() -> None:
    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["triggered"] is True
    assert "checked-in-plugin-export" in payload["surface_hits"]


def test_retro_auto_trigger_skips_non_matching_slice() -> None:
    result = run_script(
        "skills/public/retro/scripts/check_auto_trigger.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/retro-self-improvement-spec.md",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["triggered"] is False
    assert payload["surface_hits"] == []
    assert payload["path_hits"] == []
