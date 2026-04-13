from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_validate_surfaces_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-surfaces.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert "Validated surfaces manifest" in result.stdout


def test_check_changed_surfaces_reports_expected_obligations_for_readme() -> None:
    result = run_script(
        "scripts/check-changed-surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "checked-in-plugin-export" in surface_ids
    assert "repo-markdown" in surface_ids
    assert "python3 scripts/sync_root_plugin_manifests.py --repo-root ." in payload["sync_commands"]
    assert "python3 scripts/validate-packaging.py --repo-root ." in payload["verify_commands"]
    assert "python3 scripts/check-doc-links.py --repo-root ." in payload["verify_commands"]
    assert "./scripts/check-markdown.sh" in payload["verify_commands"]


def test_check_changed_surfaces_reports_unmatched_paths() -> None:
    result = run_script(
        "scripts/check-changed-surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "notes/private-plan.txt",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["matched_surfaces"] == []
    assert payload["unmatched_paths"] == ["notes/private-plan.txt"]


def test_validate_surfaces_rejects_duplicate_ids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "dup",
                        "description": "first",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    },
                    {
                        "surface_id": "dup",
                        "description": "second",
                        "source_paths": ["docs/**"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("scripts/validate-surfaces.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "duplicate surface id `dup`" in result.stderr
