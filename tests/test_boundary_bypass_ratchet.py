from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from tests.dsl import Repo

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INVENTORY = _load("inventory_boundary_bypass_lib", ROOT / "scripts" / "inventory_boundary_bypass_lib.py")
RATCHET = _load("boundary_bypass_ratchet_lib", ROOT / "scripts" / "boundary_bypass_ratchet_lib.py")

IMPORT_SAFE = "\n".join(
    [
        "def main() -> int:",
        "    return 0",
        "",
        "if __name__ == '__main__':",
        "    raise SystemExit(main())",
        "",
    ]
)


def _repo_with_candidate(tmp_path: Path) -> Path:
    return (
        Repo()
        .file("scripts/foo.py", IMPORT_SAFE)
        .file(
            "tests/test_foo.py",
            "\n".join(
                [
                    "from support import run_script",
                    "def test_x():",
                    "    result = run_script('scripts/foo.py')",
                    "    assert result.returncode == 0",
                    "    import json; assert json.loads(result.stdout)",
                    "",
                ]
            ),
        )
        .build(tmp_path)
    )


def test_matching_baseline_passes(tmp_path: Path) -> None:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline(payload)
    report = RATCHET.check_payload(payload, baseline, {})
    assert report["ok"] is True
    assert report["summary"]["candidate_count"] == 1
    assert report["summary"]["candidate_key_count"] == 1


def test_new_unexempt_candidate_fails_no_increase(tmp_path: Path) -> None:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline({"schemaVersion": payload["schemaVersion"], "candidates": []})
    report = RATCHET.check_payload(payload, baseline, {})
    assert report["ok"] is False
    assert report["new_candidate_keys"] == ["tests/test_foo.py::scripts/foo.py"]
    assert report["count_increases"]["candidate_count"] == {"baseline": 0, "current": 1}


def test_inventory_schema_mismatch_fails(tmp_path: Path) -> None:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline(payload)
    payload["schemaVersion"] = "different.schema.v2"
    report = RATCHET.check_payload(payload, baseline, {})
    assert report["ok"] is False
    assert report["schema_mismatch"] == {
        "baseline": "charness.quality.boundary_bypass_inventory.v1",
        "current": "different.schema.v2",
    }


def test_exemption_requires_why_rationale(tmp_path: Path) -> None:
    path = tmp_path / "exemptions.txt"
    path.write_text("tests/test_foo.py::scripts/foo.py\n", encoding="utf-8")
    with pytest.raises(RATCHET.RatchetError, match="# why:"):
        RATCHET.load_exemptions(path)


def test_exemption_allows_new_candidate(tmp_path: Path) -> None:
    payload = INVENTORY.find_boundary_bypass_candidates(_repo_with_candidate(tmp_path))
    baseline = RATCHET.build_baseline({"schemaVersion": payload["schemaVersion"], "candidates": []})
    exemptions = {"tests/test_foo.py::scripts/foo.py": "intentional CLI contract"}
    report = RATCHET.check_payload(payload, baseline, exemptions)
    assert report["ok"] is True
    assert report["summary"]["candidate_count"] == 0
    assert report["exempted_count"] == 1
