from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_inventory_dual_implementation_reports_shared_schema_id(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "internal" / "runtime").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "internal" / "runtime" / "normalize.go").write_text(
        'const Schema = "demo.behavior.packet.v1"\n',
        encoding="utf-8",
    )
    (repo / "scripts" / "normalize.mjs").write_text(
        'export const SCHEMA = "demo.behavior.packet.v1";\n',
        encoding="utf-8",
    )
    (repo / "docs" / "spec.md").write_text(
        "The helper is scripts/normalize.mjs.\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_dual_implementation.py",
        "--repo-root",
        str(repo),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["candidate_count"] == 1
    candidate = payload["candidates"][0]
    assert candidate["schema_id"] == "demo.behavior.packet.v1"
    assert candidate["languages"] == ["go", "javascript"]
    assert "doc_identity_leakage" in candidate["signals"]
    assert candidate["doc_identity_leakage"][0]["path"] == "docs/spec.md"


def test_quality_skill_carries_dual_implementation_lens() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    parity_text = (
        ROOT / "skills" / "public" / "quality" / "references" / "dual-implementation-parity.md"
    ).read_text(encoding="utf-8")

    assert "inventory_dual_implementation.py" in skill_text
    assert "free safety oracle" in skill_text
    assert "free oracle" in parity_text
