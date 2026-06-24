from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_plan_module() -> ModuleType:
    script = ROOT / "skills" / "public" / "debug" / "scripts" / "plan_debug_run.py"
    spec = importlib.util.spec_from_file_location("debug_plan_run_under_test", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_plan(repo: Path) -> dict[str, object]:
    return json.loads(json.dumps(load_plan_module().build_plan(repo.resolve())))


def write_adapter(repo: Path) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/debug",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_debug_plan_scaffolds_when_current_artifact_is_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)

    payload = run_plan(repo)

    assert payload["schema_version"] == "debug.run_plan.v1"
    assert payload["mode"] == "fresh-investigation"
    assert payload["artifact"]["status"] == "missing"
    assert payload["next_action"]["kind"] == "scaffold-debug-artifact"
    assert payload["artifact"]["write_path"] == "charness-artifacts/debug/latest.md"
    assert "template" not in payload["scaffold"]

    required_paths = {read["path"] for read in payload["required_reads"]}
    assert "scripts/scaffold_debug_artifact.py" in required_paths
    assert "references/five-steps.md" in required_paths
    assert "references/debug-memory.md" in required_paths
    packet_ids = {packet["id"] for packet in payload["gate_packets"]}
    assert "debug-artifact-scaffold" in packet_ids
    assert "debug-artifact-shape" in packet_ids


def test_debug_plan_missing_adapter_adds_adapter_contract_read(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    payload = run_plan(repo)

    assert payload["ok"] is True
    assert payload["adapter"]["found"] is False
    required_paths = {read["path"] for read in payload["required_reads"]}
    assert "references/adapter-contract.md" in required_paths


def test_debug_plan_reports_missing_skill_runtime_bootstrap(monkeypatch) -> None:
    module = load_plan_module()

    class MissingBootstrapPath:
        def __init__(self, _path: object) -> None:
            pass

        def resolve(self) -> object:
            return type("ResolvedPath", (), {"parents": []})()

    monkeypatch.setattr(module, "Path", MissingBootstrapPath)

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        module._load_skill_runtime_bootstrap()


def test_debug_plan_continues_existing_current_artifact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text("# Current Debug\n\n## Problem\n\nTODO\n", encoding="utf-8")

    payload = run_plan(repo)

    assert payload["mode"] == "continue-existing-artifact"
    assert payload["artifact"]["status"] == "current_pointer_exists"
    assert payload["artifact"]["line_count"] == 5
    assert payload["next_action"]["kind"] == "continue-existing-artifact"
    required_paths = [read["path"] for read in payload["required_reads"]]
    assert required_paths[0] == "charness-artifacts/debug/latest.md"


def test_debug_plan_preserves_symlinked_current_pointer_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    target = debug_dir / "debug-2026-05-06-demo.md"
    target.write_text("# Demo Debug\n", encoding="utf-8")
    (debug_dir / "latest.md").symlink_to(target.name)

    payload = run_plan(repo)

    assert payload["artifact"]["status"] == "current_pointer_target_exists"
    assert payload["artifact"]["write_path"] == "charness-artifacts/debug/debug-2026-05-06-demo.md"
    assert payload["artifact"]["current_pointer_symlink_target"] == "debug-2026-05-06-demo.md"
    assert payload["next_action"]["write_artifact_path"] == "charness-artifacts/debug/debug-2026-05-06-demo.md"


def test_debug_plan_surfaces_prior_incidents_as_conditional_reads(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    old_prior = debug_dir / "debug-2026-04-01-provider-timeout.md"
    old_prior.write_text("# Old Provider Timeout Debug\n", encoding="utf-8")
    new_prior = debug_dir / "2026-06-01-provider-timeout.md"
    new_prior.write_text("# New Provider Timeout Debug\n", encoding="utf-8")
    os.utime(old_prior, (100, 100))
    os.utime(new_prior, (200, 200))

    payload = run_plan(repo)

    assert payload["mode"] == "fresh-investigation-with-prior-memory"
    assert payload["prior_incidents"][0]["path"] == "charness-artifacts/debug/2026-06-01-provider-timeout.md"
    assert payload["prior_incidents"][0]["title"] == "New Provider Timeout Debug"
    required_paths = {read["path"] for read in payload["required_reads"]}
    assert "charness-artifacts/debug/2026-06-01-provider-timeout.md" in required_paths
    assert "charness-artifacts/debug/debug-2026-04-01-provider-timeout.md" in required_paths


def test_debug_plan_caps_prior_incidents_and_allows_missing_titles(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    for index in range(7):
        path = debug_dir / f"debug-2026-06-0{index}-case.md"
        path.write_text("No markdown title here\n", encoding="utf-8")
        os.utime(path, (100 + index, 100 + index))

    payload = run_plan(repo)

    assert len(payload["prior_incidents"]) == 5
    assert payload["prior_incidents"][0]["path"] == "charness-artifacts/debug/debug-2026-06-06-case.md"
    assert payload["prior_incidents"][0]["title"] is None


def test_debug_plan_missing_prior_title_file_returns_none(tmp_path: Path) -> None:
    module = load_plan_module()

    assert module._title_for(tmp_path / "missing.md") is None


def test_debug_plan_interrupts_external_seam_risk_before_impl(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text(
        "\n".join(
            [
                "# Current Debug",
                "",
                "## Seam Risk",
                "",
                "- Risk Class: external-seam",
                "",
                "## Interrupt Decision",
                "",
                "- Next Step: spec",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = run_plan(repo)

    assert payload["mode"] == "risk-interrupt"
    assert payload["artifact"]["requires_interrupt"] is True
    assert payload["next_action"]["kind"] == "interrupt-to-spec"
    required_paths = {read["path"] for read in payload["required_reads"]}
    assert "references/document-seams.md" in required_paths
    assert "references/invariant-first-review.md" in required_paths


def test_debug_plan_main_emits_json(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    module = load_plan_module()
    monkeypatch.setattr(
        "sys.argv",
        [
            "plan_debug_run.py",
            "--repo-root",
            str(repo),
            "--json",
        ],
    )

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "debug.run_plan.v1"


def test_debug_plan_uses_canonical_forced_risk_taxonomy(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (debug_dir / "latest.md").write_text(
        "\n".join(
            [
                "# Current Debug",
                "",
                "## Seam Risk",
                "",
                "- Risk Class: repeated-symptom",
                "- Generalization Pressure: none",
                "",
                "## Interrupt Decision",
                "",
                "- Next Step: impl",
                "",
            ]
        ),
        encoding="utf-8",
    )

    payload = run_plan(repo)

    assert payload["mode"] == "risk-interrupt"
    assert payload["artifact"]["risk_classes"] == ["repeated-symptom"]
    assert payload["artifact"]["requires_interrupt"] is True
    assert payload["next_action"]["kind"] == "interrupt-to-spec"
