"""Regression coverage for the #697 mutation-producer ownership boundary."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

import scripts.mutation.sample_mutation_files as sample_mutation_files
from scripts.mutation.mutation_changed_files_lib import (
    CHANGED_LINE_COVERAGE_MARKER_SCHEMA,
    CHANGED_LINE_COVERAGE_PRODUCER,
    changed_line_coverage_marker_path,
    read_changed_line_coverage_marker,
)

from .support import run_script
from .test_changed_line_mutation_coverage import (
    _fingerprint,
    _seed_repo_with_changed_pool_file,
)

_TEETH = "scripts/mutation/check_changed_line_mutation_coverage.py"


def test_sampler_shaped_report_with_matching_legacy_marker_is_rejected(tmp_path: Path) -> None:
    """A content-only legacy marker cannot identify the writer.

    The sampler and changed-line producer shared a report path. If the sampler
    replaced the JSON while an older changed-line marker still matched the
    changed-pool content, the consumer accepted the sampler-shaped report as
    authoritative. The report deliberately has no readable context header:
    that is the unknown-header arm the heuristic cannot safely attribute.
    """
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    coverage = repo / "reports" / "mutation" / "test-coverage.json"
    coverage.parent.mkdir(parents=True)
    coverage.write_text(
        json.dumps(
            {
                "files": {
                    "scripts/foo.py": {
                        "executed_lines": [1, 2, 5, 6],
                        "missing_lines": [],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    coverage.with_name(f"{coverage.name}.fingerprint").write_text(
        _fingerprint(repo, base), encoding="utf-8"
    )

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--require-fresh-coverage",
        "--coverage-json",
        str(coverage),
    )

    assert result.returncode == 3, result.stdout + result.stderr
    assert "stale" in yaml.safe_load(result.stdout)["reason"]
    payload = yaml.safe_load(result.stdout)
    assert payload["blocking"] == []
    assert payload["changed_eligible_files"] == ["scripts/foo.py"]
    assert payload["coverage_not_verified"] is True
    assert "stale" in payload["reason"]


def test_foreign_producer_marker_is_not_fresh_for_changed_line_consumer(tmp_path: Path) -> None:
    repo, base, head = _seed_repo_with_changed_pool_file(tmp_path)
    coverage = repo / "reports" / "mutation" / "test-coverage.json"
    coverage.parent.mkdir(parents=True)
    coverage.write_text('{"files": {}}', encoding="utf-8")
    changed_line_coverage_marker_path(coverage).write_text(
        json.dumps(
            {
                "fingerprint": _fingerprint(repo, base),
                "producer": "mutation-sampler",
                "schema": CHANGED_LINE_COVERAGE_MARKER_SCHEMA,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--require-fresh-coverage",
        "--coverage-json",
        str(coverage),
    )

    assert result.returncode == 3, result.stdout + result.stderr


def test_changed_line_marker_reader_rejects_malformed_payloads(tmp_path: Path) -> None:
    non_mapping = tmp_path / "non-mapping.json"
    non_mapping.write_text("[]", encoding="utf-8")
    assert read_changed_line_coverage_marker(non_mapping) is None

    wrong_schema = tmp_path / "wrong-schema.json"
    wrong_schema.write_text(
        json.dumps(
            {
                "schema": "other.schema.v1",
                "producer": CHANGED_LINE_COVERAGE_PRODUCER,
                "fingerprint": "0" * 64,
            }
        ),
        encoding="utf-8",
    )
    assert read_changed_line_coverage_marker(wrong_schema) is None

    malformed_fingerprint = tmp_path / "malformed-fingerprint.json"
    malformed_fingerprint.write_text(
        json.dumps(
            {
                "schema": CHANGED_LINE_COVERAGE_MARKER_SCHEMA,
                "producer": CHANGED_LINE_COVERAGE_PRODUCER,
                "fingerprint": "not-a-sha256-fingerprint",
            }
        ),
        encoding="utf-8",
    )
    assert read_changed_line_coverage_marker(malformed_fingerprint) is None


def test_changed_line_marker_identifies_its_producer(tmp_path: Path) -> None:
    from scripts.mutation import filter_cosmic_ray_mutants, run_cosmic_ray_mutation

    coverage = tmp_path / "reports" / "mutation" / "test-coverage.json"
    marker = changed_line_coverage_marker_path(coverage)
    marker.parent.mkdir(parents=True)
    marker.write_text(
        json.dumps(
            {
                "fingerprint": "0" * 64,
                "producer": CHANGED_LINE_COVERAGE_PRODUCER,
                "schema": CHANGED_LINE_COVERAGE_MARKER_SCHEMA,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    assert marker.name == "test-coverage.json.changed-line.fingerprint"
    assert marker.is_file()
    assert sample_mutation_files.DEFAULT_COVERAGE_JSON.as_posix() == (
        "reports/mutation/sample-coverage.json"
    )
    assert sample_mutation_files.DEFAULT_COVERAGE_JSON != Path(
        "reports/mutation/test-coverage.json"
    )
    assert run_cosmic_ray_mutation.DEFAULT_COVERAGE_JSON == sample_mutation_files.DEFAULT_COVERAGE_JSON
    assert filter_cosmic_ray_mutants.DEFAULT_MUTATION_SAMPLE_COVERAGE_JSON == (
        sample_mutation_files.DEFAULT_COVERAGE_JSON
    )


def test_sampler_invalidates_changed_line_marker_before_shared_override(
    tmp_path: Path, monkeypatch
) -> None:
    coverage = tmp_path / "reports" / "mutation" / "test-coverage.json"
    marker = changed_line_coverage_marker_path(coverage)
    marker.parent.mkdir(parents=True)
    marker.write_text("old changed-line marker", encoding="utf-8")

    def fake_probe(_repo_root, _command, coverage_json, **_kwargs) -> None:
        Path(coverage_json).write_text('{"files": {}}', encoding="utf-8")

    monkeypatch.setattr(sample_mutation_files, "run_test_coverage", fake_probe)
    monkeypatch.setattr(sample_mutation_files, "load_covered_lines", lambda *_args: {})
    monkeypatch.setattr(sample_mutation_files, "load_file_statement_lines", lambda *_args: {})
    monkeypatch.setattr(sample_mutation_files, "load_line_contexts", lambda *_args: {})
    monkeypatch.setattr(
        sample_mutation_files,
        "filter_eligible_by_coverage",
        lambda candidates, *_args, **_kwargs: candidates,
    )
    monkeypatch.setattr(
        sample_mutation_files,
        "build_mutation_line_coverage",
        lambda *_args: {},
    )
    monkeypatch.setattr(
        sample_mutation_files,
        "filter_eligible_by_mutation_line_coverage",
        lambda candidates, *_args: candidates,
    )

    result = sample_mutation_files.select_eligible_for_mutation(
        repo_root=tmp_path,
        config_path=tmp_path / "cosmic-ray.toml",
        all_eligible=["scripts/foo.py"],
        coverage_enabled=True,
        coverage_json=coverage,
        test_command="pytest -q",
        min_file_coverage=0.85,
        baseline_abort_marker_path=tmp_path / "baseline-abort.json",
    )

    assert result[0] == ["scripts/foo.py"]
    assert not marker.exists()
