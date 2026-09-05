"""Regression tests for the inventory-consumption validators.

Covers the consumer-side of issue #145: a quality artifact that cites an
inventory in `## Commands Run` must engage with declared non-headline fields,
not just the headline status. When the declaration lists ≥2 fields, the body
must engage with at least two distinct ones (gameability tighten).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.quality_gates.support import run_script
from tools import validate_inventory_consumption_declaration as declaration

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "gates" / "validate_inventory_consumption.py"


def _run(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return run_script(str(SCRIPT), "--repo-root", str(repo_root))


def test_declaration_runner_rejects_non_yaml_inventory_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def main():
        print("items: [unterminated")
        return 0

    monkeypatch.setattr(
        declaration,
        "load_path_module",
        lambda *_args: SimpleNamespace(main=main),
    )

    payload, error = declaration._run_inventory(tmp_path / "inventory_example.py", tmp_path)

    assert payload is None
    assert error is not None and error.startswith("non-YAML stdout:")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_repo(
    tmp_path: Path,
    *,
    artifact_body: str,
    consumer_fields: dict,
) -> Path:
    repo = tmp_path / "repo"
    _write(repo / "charness-artifacts" / "quality" / "latest.md", artifact_body)
    _write(
        repo / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json",
        json.dumps(consumer_fields),
    )
    return repo


_DEFAULT_DECLARATION = {
    "inventories": {
        "inventory_skill_ergonomics.py": {
            "non_headline_fields": ["script_file_count", "reference_file_count"]
        }
    }
}


_TARGET_SCOPE_LINES = (
    "Target boundary: retro skill quality review.\n"
    "Ambient repo findings: none found by this focused fixture.\n"
)


def test_passes_when_two_declared_fields_are_cited(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Scope\n"
        f"{_TARGET_SCOPE_LINES}"
        "## Healthy\n"
        "- skill ergonomics clean; script_file_count 0 and reference_file_count 3; "
        "prose_review_status=still_required.\n"
        "- prose review result: trigger boundaries and progressive disclosure were reviewed; no blockers found.\n"
        "- structural review result: no helper-owned packet gap; no structural move now.\n"
        "## Commands Run\n- `python3 inventory_skill_ergonomics.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 0, result.stderr
    assert "Validated inventory consumption for 1" in result.stdout


def test_fails_when_only_one_of_two_declared_fields_is_cited(tmp_path: Path) -> None:
    # Declaration lists two fields; engaging with only one is gameable.
    artifact = (
        "# Quality Review\n"
        "## Scope\n"
        f"{_TARGET_SCOPE_LINES}"
        "## Healthy\n"
        "- skill ergonomics clean; script_file_count is 0; prose_review_status=still_required.\n"
        "- prose review result: trigger boundaries were reviewed; no blockers found.\n"
        "- structural review result: no helper-owned packet gap; no structural move now.\n"
        "## Commands Run\n- `python3 inventory_skill_ergonomics.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1, result.stdout
    assert "engages with 1 of its declared non-headline fields" in result.stderr
    assert "≥2 distinct field(s)" in result.stderr


def test_fails_when_inventory_cited_without_any_declared_field(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Scope\n"
        f"{_TARGET_SCOPE_LINES}"
        "## Healthy\n"
        "- skill ergonomics overall clean; prose_review_status=still_required.\n"
        "- prose review result: trigger boundaries were reviewed; no blockers found.\n"
        "- structural review result: no helper-owned packet gap; no structural move now.\n"
        "## Commands Run\n- `python3 inventory_skill_ergonomics.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1
    assert "inventory_skill_ergonomics.py" in result.stderr
    assert "non-headline fields" in result.stderr


def test_single_field_declaration_still_requires_only_one(tmp_path: Path) -> None:
    declaration = {
        "inventories": {
            "inventory_skill_ergonomics.py": {"non_headline_fields": ["script_file_count"]}
        }
    }
    artifact = (
        "# Quality Review\n"
        "## Scope\n"
        f"{_TARGET_SCOPE_LINES}"
        "## Healthy\n"
        "- skill ergonomics clean; script_file_count is 0; prose_review_status=still_required.\n"
        "- prose review result: trigger boundaries were reviewed; no blockers found.\n"
        "- structural review result: no helper-owned packet gap; no structural move now.\n"
        "## Commands Run\n- `python3 inventory_skill_ergonomics.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=declaration)

    result = _run(repo)

    assert result.returncode == 0, result.stderr


def test_non_quality_inventory_path_is_out_of_scope(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n- adapter gate design clean (no findings reported).\n"
        "## Commands Run\n- `python3 scripts/gates/inventory_boundary_bypass.py --repo-root .`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 0, result.stderr


def test_noncanonical_quality_scripts_path_is_out_of_scope(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n- adapter gate design clean (no findings reported).\n"
        "## Commands Run\n- `python3 tools/quality/scripts/inventory_example.py --repo-root .`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 0, result.stderr


def test_skill_dir_parent_escape_is_out_of_scope(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n- adapter gate design clean (no findings reported).\n"
        "## Commands Run\n- `python3 $SKILL_DIR/scripts/../gates/inventory_boundary_bypass.py`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 0, result.stderr


def test_exported_plugin_quality_scripts_path_is_out_of_scope(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n- adapter gate design clean (no findings reported).\n"
        "## Commands Run\n- `python3 skills/quality/scripts/inventory_example.py --repo-root .`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 0, result.stderr


def test_prefixed_lookalike_quality_scripts_path_is_out_of_scope(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n- adapter gate design clean (no findings reported).\n"
        "## Commands Run\n"
        "- `python3 vendor/skills/public/quality/scripts/inventory_example.py --repo-root .`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 0, result.stderr


def test_skill_dir_scripts_undeclared_inventory_is_still_refused(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n- adapter gate design clean (no findings reported).\n"
        "## Commands Run\n- `python3 $SKILL_DIR/scripts/inventory_adapter_gate_design.py --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1, result.stdout
    assert "inventory_adapter_gate_design.py" in result.stderr
    assert "is not declared" in result.stderr


def test_quality_path_undeclared_inventory_is_still_refused(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n- adapter gate design clean (no findings reported).\n"
        "## Commands Run\n"
        "- `python3 skills/public/quality/scripts/inventory_adapter_gate_design.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1, result.stdout
    assert "inventory_adapter_gate_design.py" in result.stderr
    assert "is not declared" in result.stderr


def test_inventory_outside_declaration_is_refused(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n- adapter gate design clean (no findings reported).\n"
        "## Commands Run\n- `python3 inventory_adapter_gate_design.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1, result.stdout
    assert "inventory_adapter_gate_design.py" in result.stderr
    assert "is not declared" in result.stderr


def test_opted_out_inventory_citation_does_not_require_body_fields(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n- gitignore scan hygiene ran as a gate.\n"
        "## Commands Run\n- `python3 inventory_gitignore_scan_hygiene.py --repo-root .`\n"
        "## History\n"
    )
    declaration = {
        "inventories": {
            "inventory_gitignore_scan_hygiene.py": {
                "non_headline_fields": [],
                "opt_out_reason": "consumed by a gate, not this artifact body",
            }
        }
    }
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=declaration)

    result = _run(repo)

    assert result.returncode == 0, result.stderr


def test_field_citation_inside_commands_run_does_not_count(tmp_path: Path) -> None:
    # Citing the field name in the same `## Commands Run` line where the script is
    # mentioned should not satisfy the contract; engagement must happen elsewhere
    # in the artifact body.
    artifact = (
        "# Quality Review\n"
        "## Scope\n"
        f"{_TARGET_SCOPE_LINES}"
        "## Healthy\n- nothing to report.\n"
        "## Weak\n- prose_review_status=still_required.\n"
        "## Advisory\n- prose review result: trigger boundaries were reviewed; no blockers found.\n"
        "## Commands Run\n"
        "- `python3 inventory_skill_ergonomics.py --repo-root . --detail` (script_file_count visible)\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1, result.stdout
    assert "script_file_count" in result.stderr


def test_skill_ergonomics_inventory_requires_prose_review_status(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Scope\n"
        f"{_TARGET_SCOPE_LINES}"
        "## Healthy\n- skill ergonomics clean; script_file_count 0 and reference_file_count 3.\n"
        "## Advisory\n- prose review result: trigger boundaries were reviewed; no blockers found.\n"
        "## Commands Run\n- `python3 inventory_skill_ergonomics.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1
    assert "prose_review_status" in result.stderr


def test_skill_ergonomics_inventory_requires_prose_review_result(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Scope\n"
        f"{_TARGET_SCOPE_LINES}"
        "## Healthy\n"
        "- skill ergonomics clean; script_file_count 0 and reference_file_count 3; "
        "prose_review_status=still_required.\n"
        "## Commands Run\n- `python3 inventory_skill_ergonomics.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1
    assert "prose review result" in result.stderr


def test_skill_ergonomics_inventory_requires_structural_review_result(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Scope\n"
        f"{_TARGET_SCOPE_LINES}"
        "## Healthy\n"
        "- skill ergonomics clean; script_file_count 0 and reference_file_count 3; "
        "prose_review_status=still_required.\n"
        "## Advisory\n- prose review result: trigger boundaries were reviewed; no blockers found.\n"
        "## Commands Run\n- `python3 inventory_skill_ergonomics.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1
    assert "structural review result" in result.stderr


def test_skill_ergonomics_inventory_requires_target_and_ambient_split(tmp_path: Path) -> None:
    artifact = (
        "# Quality Review\n"
        "## Healthy\n"
        "- skill ergonomics clean; script_file_count 0 and reference_file_count 3; "
        "prose_review_status=still_required.\n"
        "## Advisory\n"
        "- prose review result: trigger boundaries were reviewed; no blockers found.\n"
        "- structural review result: no helper-owned packet gap; no structural move now.\n"
        "## Commands Run\n- `python3 inventory_skill_ergonomics.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 1
    assert "Target boundary" in result.stderr
    assert "Ambient repo findings" in result.stderr


def test_artifact_predating_contract_start_is_skipped(tmp_path: Path) -> None:
    # Artifacts dated before 2026-05-13 are frozen retros — rewriting them to fit
    # this later gate would be Goodhart. The validator must skip them entirely.
    artifact = (
        "# Quality Review\n"
        "Date: 2026-05-12\n"
        "\n"
        "## Healthy\n- skill ergonomics overall clean.\n"
        "## Commands Run\n- `python3 inventory_skill_ergonomics.py --repo-root . --detail`\n"
        "## History\n"
    )
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 0, result.stderr
    assert "predates contract start" in result.stdout
    # This fixture is a NON-git tmp_path, so the arm it actually exercises is the
    # uncorroborated one. Asserting that keeps the test from reading as coverage of the
    # corroborated exemption, which `test_a_declaration_is_not_its_own_corroboration.py`
    # owns.
    assert "NOT CORROBORATED" in result.stdout


def test_no_commands_run_section_means_nothing_to_enforce(tmp_path: Path) -> None:
    artifact = "# Quality Review\n## Healthy\n- everything fine.\n## History\n"
    repo = _seed_repo(tmp_path, artifact_body=artifact, consumer_fields=_DEFAULT_DECLARATION)

    result = _run(repo)

    assert result.returncode == 0, result.stderr


def test_real_repo_artifact_passes() -> None:
    """The committed charness-artifacts/quality/latest.md must satisfy the contract."""
    result = _run(ROOT)

    assert result.returncode == 0, result.stderr


COVERAGE_SCRIPT = ROOT / "tools" / "check_inventory_declaration_coverage.py"


def _run_coverage(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return run_script(str(COVERAGE_SCRIPT), "--repo-root", str(repo_root))


@pytest.mark.boundary_contract(reason="prove the coverage checker exit code on a seeded inventory tree")
def test_declaration_coverage_allows_undeclared_inventory_scripts(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts = repo / "skills" / "public" / "quality" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "inventory_used.py").write_text("# used\n", encoding="utf-8")
    (scripts / "inventory_unused.py").write_text("# unused\n", encoding="utf-8")
    refs = repo / "skills" / "public" / "quality" / "references"
    refs.mkdir(parents=True)
    (refs / "inventory-consumer-fields.json").write_text(
        json.dumps(
            {
                "inventories": {
                    "inventory_used.py": {"non_headline_fields": ["alpha", "beta"]}
                }
            }
        ),
        encoding="utf-8",
    )

    result = _run_coverage(repo)

    assert result.returncode == 0, result.stderr
    assert "1 undeclared inventory script(s) are not in the consumption contract" in result.stdout


@pytest.mark.boundary_contract(reason="prove the coverage checker exit code when a declared script is missing")
def test_declaration_coverage_still_refuses_declared_missing_script(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts = repo / "skills" / "public" / "quality" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "inventory_used.py").write_text("# used\n", encoding="utf-8")
    refs = repo / "skills" / "public" / "quality" / "references"
    refs.mkdir(parents=True)
    (refs / "inventory-consumer-fields.json").write_text(
        json.dumps(
            {
                "inventories": {
                    "inventory_ghost.py": {"non_headline_fields": ["alpha", "beta"]}
                }
            }
        ),
        encoding="utf-8",
    )

    result = _run_coverage(repo)

    assert result.returncode == 1
    assert "inventory_ghost.py" in result.stderr


@pytest.mark.boundary_contract(reason="prove the live consumption declaration coverage exit code")
def test_real_repo_declaration_coverage_passes() -> None:
    result = _run_coverage(ROOT)

    assert result.returncode == 0, result.stderr
    assert "undeclared inventory script(s) are not in the consumption contract" in result.stdout
