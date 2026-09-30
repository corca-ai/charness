"""In-process proof for the references link-inventory gate.

The gate previously drove only through the quality engine subprocess, so its
import binding had no in-process proof; the historical try/except fallback is
removed and the repo bootstrap is the single owner of repo-root insertion.
`find_references_section`/`scan_file` are pure over their inputs, so the unit
pins below double as the gate's first behavioral tests.
"""

from __future__ import annotations

from pathlib import Path

import tools.check_references_link_inventory as link_inventory


def test_check_references_link_inventory_binds_packaged_helpers() -> None:
    assert (
        link_inventory.iter_matching_repo_files.__module__ == "scripts.core.repo_file_listing"
    )
    assert link_inventory.emit_yaml.__module__ == "scripts.yaml_output"


def test_find_references_section_bounds() -> None:
    assert link_inventory.find_references_section(["# t", "", "body"]) is None
    assert link_inventory.find_references_section(
        ["# t", "", "## References", "", "- [a](./b.md)", "", "## Next", "x"]
    ) == (3, 6)


def test_scan_file_flags_prose_bullet_and_passes_link_bullets(tmp_path: Path) -> None:
    clean = tmp_path / "clean.md"
    clean.write_text("# t\n\n## References\n\n- [a](./b.md)\n- `scripts/x.py`\n", encoding="utf-8")
    assert link_inventory.scan_file(clean, tmp_path)["findings"] == []
    dirty = tmp_path / "dirty.md"
    dirty.write_text("# t\n\n## References\n\n- run the thing daily\n", encoding="utf-8")
    findings = link_inventory.scan_file(dirty, tmp_path)["findings"]
    assert [entry["type"] for entry in findings] == ["bullet_without_link_or_path"]
