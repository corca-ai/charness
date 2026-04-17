from __future__ import annotations

import json
from pathlib import Path

from .support import run_script


def test_inventory_public_spec_quality_flags_reader_facing_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "tests" / "cli_smoke_test.py").write_text("def test_smoke():\n    pass\n", encoding="utf-8")
    (repo / "docs" / "specs" / "current-product.spec.md").write_text(
        "\n".join(
            [
                "# Current Product",
                "",
                "Current reader-facing claim.",
                "Future roadmap note stays here for later.",
                "Implementation note points at `internal/app/app_test.go` and `scripts/build_contract.py`.",
                "",
                "| file | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | current shipped phrase |",
                "",
                "```bash",
                "pytest -k cli_smoke",
                "```",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    spec = payload["public_specs"][0]
    assert spec["spec_path"] == "docs/specs/current-product.spec.md"
    assert set(spec["heuristics"]) == {
        "source_inventory_pressure",
        "implementation_guard_pressure",
        "future_state_mixed",
        "delegated_test_runner_proof",
    }
    assert "proof_layering_review_needed" in payload["layering"]["heuristics"]
    assert payload["layering"]["delegated_runner_specs"] == ["docs/specs/current-product.spec.md"]
    recommendations = payload["layering"]["recommendations"]
    assert recommendations[0]["action"] == "move_down"
    assert recommendations[0]["target_items"] == ["docs/specs/current-product.spec.md"]
    assert recommendations[1]["action"] == "keep_if_integration_value"
    assert recommendations[1]["scope"] == "smoke"
    assert recommendations[1]["target_items"] == ["tests/cli_smoke_test.py"]


def test_inventory_public_spec_quality_detects_duplicate_public_examples(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "tests" / "end_to_end_flow.py").write_text("def test_e2e():\n    pass\n", encoding="utf-8")
    first = "\n".join(["# First", "", "```bash", "demo status --json", "```", ""]) + "\n"
    second = "\n".join(["# Second", "", "```bash", "$ demo status --json", "```", ""]) + "\n"
    (repo / "docs" / "specs" / "alpha.spec.md").write_text(first, encoding="utf-8")
    (repo / "docs" / "specs" / "beta.spec.md").write_text(second, encoding="utf-8")

    result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["summary"]["duplicate_command_count"] == 1
    duplicate = payload["layering"]["duplicate_command_examples"][0]
    assert duplicate["command"] == "demo status --json"
    assert duplicate["spec_paths"] == [
        "docs/specs/alpha.spec.md",
        "docs/specs/beta.spec.md",
    ]
    assert "duplicate_public_spec_examples" in payload["layering"]["heuristics"]
    assert "proof_layering_review_needed" in payload["layering"]["heuristics"]
    recommendations = payload["layering"]["recommendations"]
    assert recommendations[0]["action"] == "delete_or_merge"
    assert recommendations[0]["target"] == "duplicate_command_examples"
    assert recommendations[1]["action"] == "keep_if_integration_value"
    assert recommendations[1]["scope"] == "on-demand-e2e"
    assert recommendations[1]["target_items"] == ["tests/end_to_end_flow.py"]


def test_inventory_public_spec_quality_recognizes_specdown_run_shell_blocks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "specs").mkdir(parents=True)
    (repo / "specs" / "index.spec.md").write_text(
        "\n".join(
            [
                "# CLI Contract",
                "",
                "Reader-facing current claim.",
                "",
                "```run:shell",
                "demo doctor --json",
                "```",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    spec = payload["public_specs"][0]
    assert spec["spec_path"] == "specs/index.spec.md"
    assert spec["command_examples"] == ["demo doctor --json"]
    assert "no_executable_proof_blocks" not in spec["heuristics"]
    assert "delegated_test_runner_proof" not in spec["heuristics"]
