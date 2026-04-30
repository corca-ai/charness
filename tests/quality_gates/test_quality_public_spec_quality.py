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
    assert "source_guard_pressure_rollup" in payload["layering"]["heuristics"]
    assert payload["summary"]["source_guard_row_count"] == 1
    assert payload["summary"]["source_guard_pressure_spec_count"] == 1
    assert payload["layering"]["delegated_runner_specs"] == ["docs/specs/current-product.spec.md"]
    recommendations = payload["layering"]["recommendations"]
    assert recommendations[0]["action"] == "move_down"
    assert recommendations[0]["target_items"] == ["docs/specs/current-product.spec.md"]
    source_guard_recommendation = next(
        item for item in recommendations if item["action"] == "classify_source_guards"
    )
    assert source_guard_recommendation["target"] == "top_source_guard_specs"
    assert "replace_with_contract_check" in source_guard_recommendation["guidance"]
    smoke_recommendation = next(
        item for item in recommendations if item["scope"] == "smoke"
    )
    assert smoke_recommendation["action"] == "keep_if_integration_value"
    assert smoke_recommendation["target_items"] == ["tests/cli_smoke_test.py"]


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


def test_inventory_public_spec_quality_rolls_up_top_source_guard_specs(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    (repo / "specs").mkdir(parents=True)
    (repo / "specs" / "alpha.spec.md").write_text(
        "\n".join(
            [
                "# Alpha",
                "",
                "| file | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | source_guard | first |",
                "| docs/a.md | fixed | second |",
                "",
                "source_guard source_guard",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "specs" / "beta.spec.md").write_text(
        "\n".join(
            [
                "# Beta",
                "",
                "| file | matcher | pattern |",
                "| --- | --- | --- |",
                "| README.md | fixed | only |",
                "",
            ]
        ),
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
    assert payload["summary"]["source_guard_row_count"] == 3
    assert payload["summary"]["source_guard_token_count"] == 3
    assert payload["summary"]["source_guard_pressure_spec_count"] == 2
    assert payload["layering"]["top_source_guard_specs"] == [
        {
            "spec_path": "specs/alpha.spec.md",
            "source_guard_row_count": 2,
            "source_guard_token_count": 3,
        },
        {
            "spec_path": "specs/beta.spec.md",
            "source_guard_row_count": 1,
            "source_guard_token_count": 0,
        },
    ]
    recommendation = next(
        item for item in payload["layering"]["recommendations"]
        if item["action"] == "classify_source_guards"
    )
    assert recommendation["target_items"][0]["spec_path"] == "specs/alpha.spec.md"

    text_result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
    )
    assert text_result.returncode == 0, text_result.stderr
    assert "source_guard_rollup: rows=3 tokens=3 affected_specs=2" in text_result.stdout
    assert "top_source_guard_specs:" in text_result.stdout
    assert "recommendation: classify_source_guards top_source_guard_specs" in text_result.stdout


def test_inventory_public_spec_quality_exempts_contract_sections(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "docs" / "specs" / "contract.spec.md").write_text(
        "\n".join(
            [
                "# Contract",
                "",
                "Current reader-facing claim.",
                "",
                "## Fixed Decisions",
                "",
                "The frozen stack names `internal/server/app.py` and `scripts/build.py`.",
                "",
                "## Deferred Decisions",
                "",
                "Deferred scope is intentionally kept here for a later release.",
                "",
                "```bash",
                "demo status --json",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    spec = json.loads(result.stdout)["public_specs"][0]
    assert "implementation_guard_pressure" not in spec["heuristics"]
    assert "future_state_mixed" not in spec["heuristics"]
    assert spec["implementation_path_ref_exempt_count"] == 2
    assert spec["future_state_term_exempt_count"] == 3


def test_inventory_public_spec_quality_still_scans_unexempt_headings(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "docs" / "specs" / "headings.spec.md").write_text(
        "\n".join(
            [
                "# Future roadmap for `internal/app.py` and `scripts/build.py`",
                "",
                "Current reader-facing claim.",
                "",
                "```bash",
                "demo status --json",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    spec = json.loads(result.stdout)["public_specs"][0]
    assert "implementation_guard_pressure" in spec["heuristics"]
    assert "future_state_mixed" in spec["heuristics"]


def test_inventory_public_spec_quality_uses_path_density_floor(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    body = [f"Reader-facing claim {index}." for index in range(200)]
    body.extend(
        [
            "Implementation note points at `internal/app/app.py`.",
            "Another contract reference names `scripts/build.py`.",
            "```bash",
            "demo status --json",
            "```",
        ]
    )
    (repo / "docs" / "specs" / "density.spec.md").write_text(
        "# Density\n\n" + "\n".join(body) + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    spec = json.loads(result.stdout)["public_specs"][0]
    assert spec["implementation_path_ref_count"] == 2
    assert spec["implementation_path_ref_density"] < spec["implementation_path_ref_density_floor"]
    assert "implementation_guard_pressure" not in spec["heuristics"]

    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "public_spec_implementation_ref_density_floor: 0.005",
                "",
            ]
        ),
        encoding="utf-8",
    )
    stricter = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert stricter.returncode == 0, stricter.stderr
    stricter_spec = json.loads(stricter.stdout)["public_specs"][0]
    assert "implementation_guard_pressure" in stricter_spec["heuristics"]


def test_inventory_public_spec_quality_recognizes_pointer_specs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "specs").mkdir(parents=True)
    (repo / "specs" / "pytest-pointer.spec.md").write_text(
        "\n".join(
            [
                "# Pointer",
                "",
                "Behavior is covered by deterministic tests.",
                "Covered by pytest: `tests/test_popup.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "specs" / "frontmatter-pointer.spec.md").write_text(
        "\n".join(
            [
                "---",
                "proof: pointer-spec",
                "---",
                "# Frontmatter Pointer",
                "",
                "Behavior is owned by a lower-level checked proof.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    specs = {item["spec_path"]: item for item in json.loads(result.stdout)["public_specs"]}
    pytest_spec = specs["specs/pytest-pointer.spec.md"]
    frontmatter_spec = specs["specs/frontmatter-pointer.spec.md"]
    assert "no_executable_proof_blocks" not in pytest_spec["heuristics"]
    assert "implementation_guard_pressure" not in pytest_spec["heuristics"]
    assert pytest_spec["pointer_proof_reference_count"] == 1
    assert "no_executable_proof_blocks" not in frontmatter_spec["heuristics"]
    assert frontmatter_spec["pointer_proof_marker_count"] == 1


def test_inventory_public_spec_quality_exempts_wrapped_pytest_pointer_blocks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "specs").mkdir(parents=True)
    (repo / "specs" / "wrapped-pointer.spec.md").write_text(
        "\n".join(
            [
                "# Wrapped Pointer",
                "",
                "Behavior is covered by deterministic tests.",
                "Covered by pytest: `tests/test_runtime_device_detection.py::TestDetectDevice`,",
                "`tests/test_runtime_device_detection.py::TestResolveRequestedDevice`,",
                "`tests/test_runtime_device.py::TestResolveSessionDevice`,",
                "`tests/test_runtime_device_listing.py::TestListAvailableDevices`.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    spec = json.loads(result.stdout)["public_specs"][0]
    assert spec["implementation_path_ref_count"] == 0
    assert spec["implementation_path_ref_total_count"] == 4
    assert spec["implementation_path_ref_exempt_count"] == 4
    assert spec["pointer_proof_reference_count"] == 1
    assert "implementation_guard_pressure" not in spec["heuristics"]
    assert "no_executable_proof_blocks" not in spec["heuristics"]


def test_inventory_public_spec_quality_rejects_invalid_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "specs").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "public_spec_implementation_ref_density_floor: nope",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "specs" / "index.spec.md").write_text("# Index\n", encoding="utf-8")

    result = run_script(
        "skills/public/quality/scripts/inventory_public_spec_quality.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 1
    assert "Invalid quality adapter" in result.stderr
    assert "public_spec_implementation_ref_density_floor must be a number" in result.stderr
