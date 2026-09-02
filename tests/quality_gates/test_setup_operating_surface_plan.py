from __future__ import annotations

from pathlib import Path

from scripts.setup.setup_inspect_quality_lib import quality_setup_snapshot
from scripts.setup.setup_operating_surface_lib import detect_operating_surface_ownership

from .support import inspect_setup_repo


def test_setup_inspect_emits_ownership_plan_for_overloaded_operating_surfaces(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text(
        "# Agents\n\n[Local](./docs/runbook.md) [Parent](../docs/ops.md) [Root](docs/README.md)\n\n"
        + "\n".join(f"Procedure {index}. Move this to its owner." for index in range(150))
        + "\n",
        encoding="utf-8",
    )
    (repo / "docs" / "index.md").write_text(
        "# Docs\n\n" + "\n".join(f"Durable policy paragraph {index}." for index in range(20)) + "\n",
        encoding="utf-8",
    )

    payload = inspect_setup_repo(repo)
    direct = detect_operating_surface_ownership(repo)
    normalization = payload["agent_docs"]["normalization"]
    ownership = normalization["ownership"]
    surfaces = {item["path"]: item for item in ownership["surfaces"]}

    assert ownership["status"] == "plan-only"
    assert ownership["approval_required"] is True
    assert ownership["execution"] == "not-run"
    assert surfaces["AGENTS.md"]["shape"] == "overloaded"
    assert surfaces["docs/index.md"]["shape"] == "substantive-index"
    assert surfaces["AGENTS.md"]["surface"] == "first-touch-contract"
    assert surfaces["AGENTS.md"]["owner"] == "setup"
    assert surfaces["AGENTS.md"]["source"] == "AGENTS.md"
    assert surfaces["AGENTS.md"]["consumer"] == ["quality.quality_setup_snapshot", "setup.inspect_repo"]
    assert surfaces["AGENTS.md"]["confidence"] == "medium"
    assert direct["surfaces"][0]["internal_doc_links"] == ["docs/README.md", "docs/ops.md", "docs/runbook.md"]
    assert ownership["recommended_first_move"]["source"] == "AGENTS.md"
    assert ownership["recommended_first_move"]["approval"] == "required"
    assert quality_setup_snapshot(repo)["operating_surface_ownership"]["moves"]


def test_quality_setup_snapshot_preserves_plan_when_bootstrap_read_fails(monkeypatch, tmp_path: Path) -> None:
    def fail_bootstrap(_repo: Path) -> tuple[dict[str, object], dict[str, object], list[object]]:
        raise RuntimeError("fixture failure")

    monkeypatch.setattr("scripts.adapters.quality_bootstrap_lib.build_bootstrap_state", fail_bootstrap)

    snapshot = quality_setup_snapshot(tmp_path)

    assert snapshot["status"] == "unavailable"
    assert snapshot["operating_surface_ownership"]["status"] == "plan-only"


def test_ownership_plan_refuses_path_only_evidence(tmp_path: Path) -> None:
    plan = detect_operating_surface_ownership(tmp_path)
    surface = plan["surfaces"][0]

    assert surface["source"] == "AGENTS.md"
    assert surface["owner"] is None
    assert surface["confidence"] == "none"
    assert plan["refusal_reason"] == "readable structure is required; path existence alone is insufficient"
    assert plan["moves"][0]["refusal_reason"] == plan["refusal_reason"]
