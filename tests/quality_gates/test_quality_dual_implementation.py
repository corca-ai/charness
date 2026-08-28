from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

from .support import ROOT
from .seeding_support import load_module

SCRIPT = ROOT / "skills/public/quality/scripts/inventory_dual_implementation.py"
inventory_dual = load_module("inventory_dual_implementation", SCRIPT)


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

    payload = inventory_dual.build_payload(repo)
    assert payload["candidate_count"] == 1
    candidate = payload["candidates"][0]
    assert candidate["schema_id"] == "demo.behavior.packet.v1"
    assert candidate["languages"] == ["go", "javascript"]
    assert "doc_identity_leakage" in candidate["signals"]
    assert candidate["doc_identity_leakage"][0]["path"] == "docs/spec.md"


def test_inventory_dual_implementation_defaults_to_yaml_with_json_compatibility(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    command = [sys.executable, str(SCRIPT), "--repo-root", str(repo)]

    default = subprocess.run(command, check=False, capture_output=True, text=True)
    detail_json = subprocess.run(
        [*command, "--detail"], check=False, capture_output=True, text=True
    )
    summary = subprocess.run(
        [*command, "--summary"], check=False, capture_output=True, text=True
    )
    summary_json = subprocess.run(
        [*command, "--summary"], check=False, capture_output=True, text=True
    )

    assert default.returncode == detail_json.returncode == summary.returncode == summary_json.returncode == 0
    assert yaml.safe_load(default.stdout) == yaml.safe_load(detail_json.stdout)
    assert yaml.safe_load(summary.stdout) == yaml.safe_load(summary_json.stdout)


def test_quality_skill_carries_dual_implementation_lens() -> None:
    dispatch = (
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-dispatch.md"
    ).read_text(encoding="utf-8")
    parity_text = (
        ROOT / "skills" / "public" / "quality" / "references" / "dual-implementation-parity.md"
    ).read_text(encoding="utf-8")

    assert "inventory_dual_implementation.py" in dispatch
    assert "free safety oracle" in dispatch
    assert "free oracle" in parity_text
