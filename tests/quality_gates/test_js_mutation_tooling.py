from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from scripts.mutation.run_js_mutation import (
    JS_MUTATION_MUTANT_WEIGHTS,
    list_js_targets,
    remove_stale_report,
    select_js_targets,
)
from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT

RUN_JS_MUTATION = load_script_module(
    "run_js_mutation_cli_boundary", ROOT / "scripts" / "mutation" / "run_js_mutation.py"
)
CHECK_JS_MUTATION_SCORE = load_script_module(
    "check_js_mutation_score_cli", ROOT / "scripts" / "mutation" / "check_js_mutation_score.py"
)


@pytest.mark.boundary_contract(
    reason="exact process exit-code contract: Node must load the repository's ESM Stryker configuration"
)
def test_stryker_config_mutates_only_agent_runtime_sources() -> None:
    env = os.environ.copy()
    env.pop("MUTATION_JS_TARGETS", None)
    result = subprocess.run(
        [
            "node",
            "-e",
            "import('./stryker.config.mjs').then(m => console.log(JSON.stringify(m.default)))",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    config = json.loads(result.stdout)
    assert config["mutate"] == ["scripts/agent-runtime/**/*.mjs"]
    assert "plugins/**" in config["ignorePatterns"]
    assert "node_modules/**" in config["ignorePatterns"]
    assert config["testRunner"] == "command"
    assert config["commandRunner"]["command"] == "npm run test:agent-runtime"
    assert "pytest" not in config["commandRunner"]["command"]
    assert config["concurrency"] == 2
    assert config["thresholds"]["break"] == 80


def test_js_mutation_pool_is_agent_runtime_only() -> None:
    targets = list_js_targets(ROOT)

    assert targets == [
        "scripts/agent-runtime/codex-eval-runtime.mjs",
        "scripts/agent-runtime/contract-versions.mjs",
        "scripts/agent-runtime/instruction-surface-case-suite.mjs",
        "scripts/agent-runtime/instruction-surface-support.mjs",
        "scripts/agent-runtime/run-local-eval-test.mjs",
        "scripts/agent-runtime/skill-test-telemetry.mjs",
    ]
    assert "skills/support/gather-slack/vendor/slack-api.mjs" not in targets
    assert "plugins/charness/scripts/agent-runtime/run-local-eval-test.mjs" not in targets


def test_js_mutation_weight_table_covers_every_pool_target() -> None:
    assert set(JS_MUTATION_MUTANT_WEIGHTS) == set(list_js_targets(ROOT))
    assert all(weight > 0 for weight in JS_MUTATION_MUTANT_WEIGHTS.values())


def test_js_mutation_full_mode_rejects_unweighted_pool_target(tmp_path, monkeypatch) -> None:
    target = tmp_path / "scripts" / "agent-runtime" / "nested" / "new-runtime.mjs"
    target.parent.mkdir(parents=True)
    target.write_text("export const value = 1;\n", encoding="utf-8")
    monkeypatch.delenv("MUTATION_JS_TARGETS", raising=False)

    with pytest.raises(SystemExit, match="missing JS mutation mutant weights"):
        select_js_targets(tmp_path, mode="full")


def test_js_mutation_full_mode_rejects_non_positive_weight(monkeypatch) -> None:
    monkeypatch.delenv("MUTATION_JS_TARGETS", raising=False)
    monkeypatch.setitem(
        JS_MUTATION_MUTANT_WEIGHTS, "scripts/agent-runtime/contract-versions.mjs", 0
    )

    with pytest.raises(SystemExit, match="non-positive JS mutation mutant weights"):
        select_js_targets(ROOT, mode="full")


def test_js_native_tests_import_every_mutated_agent_runtime_module() -> None:
    # The invariant is coverage: every mutated module must be imported by *some*
    # native test. Scan all tests/agent-runtime/*.test.mjs so the gate stays
    # correct as the suite grows beyond a single native.test.mjs file.
    test_dir = ROOT / "tests" / "agent-runtime"
    imported_runtime_modules: set[str] = set()
    for test_file in test_dir.glob("*.test.mjs"):
        test_source = test_file.read_text(encoding="utf-8")
        for match in re.findall(
            r'from "(\.\./\.\./scripts/agent-runtime/[^"]+\.mjs)"', test_source
        ):
            imported_runtime_modules.add(
                str((test_dir / match).resolve().relative_to(ROOT).as_posix())
            )

    assert sorted(imported_runtime_modules) == list_js_targets(ROOT)


def test_js_mutation_full_mode_samples_targets(monkeypatch) -> None:
    monkeypatch.delenv("MUTATION_JS_TARGETS", raising=False)
    monkeypatch.setenv("MUTATION_SAMPLE_SEED", "fixed-seed")
    monkeypatch.setenv("MUTATION_JS_MAX_FILES", "2")

    targets = select_js_targets(ROOT, mode="full")

    assert targets == [
        "scripts/agent-runtime/contract-versions.mjs",
        "scripts/agent-runtime/skill-test-telemetry.mjs",
    ]
    assert set(targets) <= set(list_js_targets(ROOT))


def test_js_mutation_explicit_targets_override_budget(monkeypatch) -> None:
    monkeypatch.setenv("MUTATION_JS_TARGETS", "scripts/agent-runtime/run-local-eval-test.mjs")
    monkeypatch.setenv("MUTATION_JS_MAX_MUTANTS", "1")

    assert select_js_targets(ROOT, mode="full") == ["scripts/agent-runtime/run-local-eval-test.mjs"]


def test_js_mutation_runner_requires_local_stryker_install(tmp_path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "stryker.config.mjs").write_text("export default {};\n", encoding="utf-8")
    runner = ROOT / "scripts" / "mutation" / "run_js_mutation.py"

    result = run_loaded_script_main(
        str(runner), RUN_JS_MUTATION, "--repo-root", str(repo), "--mode", "dry-run"
    )

    assert result.returncode != 0
    assert "StrykerJS is not installed" in result.stderr


def test_js_mutation_runner_removes_stale_report_before_execution(tmp_path) -> None:
    repo = tmp_path / "repo"
    report = repo / "reports" / "mutation" / "stryker-js.json"
    report.parent.mkdir(parents=True)
    report.write_text('{"stale": true}\n', encoding="utf-8")

    removed = remove_stale_report(repo, Path("reports/mutation/stryker-js.json"))

    assert removed == report
    assert not report.exists()


def test_js_mutation_summary_fails_when_report_missing(tmp_path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "output_dir: reports/quality",
                "mutation_testing:",
                "  score_break: 80",
                "  report_paths:",
                "    summary_md: reports/mutation/summary.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "scripts/mutation/check_js_mutation_score.py",
        CHECK_JS_MUTATION_SCORE,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 1
    assert "StrykerJS report not found" in result.stderr
    summary = (repo / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "- Status: **UNMEASURED** (StrykerJS JSON report missing)" in summary
    assert "did not produce a fresh JSON report" in summary


def test_js_all_ignored_report_is_unmeasured_through_the_cli(tmp_path) -> None:
    """A Stryker report that scored nothing, driven through the real CLI.

    The zero-denominator property's other tests call `append_summary` directly. This
    one goes through `check_js_mutation_score.py` as an operator would, because the
    goal that introduced the property names #586 -- a check that passes its own
    direct-call test while never firing on the wired path -- as a constraint on its
    own repairs, and a round-2 review found the property had only direct-call cover.

    All mutants `Ignored` is the realistic route: a `Stryker disable all` in the
    mutated files, or an `excludedMutations` config covering the operator set.
    """
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "output_dir: reports/quality",
                "mutation_testing:",
                "  score_break: 80",
                "  report_paths:",
                "    summary_md: reports/mutation/summary.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    report = repo / "reports" / "mutation" / "stryker-js.json"
    report.parent.mkdir(parents=True)
    report.write_text(
        json.dumps(
            {
                "files": {
                    "src/a.js": {
                        "mutants": [
                            {"status": "Ignored", "mutatorName": "BooleanLiteral"},
                            {"status": "Ignored", "mutatorName": "ArithmeticOperator"},
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "scripts/mutation/check_js_mutation_score.py",
        CHECK_JS_MUTATION_SCORE,
        "--repo-root",
        str(repo),
    )

    summary = (repo / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "- Status: **UNMEASURED**" in summary
    assert "**FAIL**" not in summary
    assert "no score was computed" in summary
    assert "- Reachable mutants: 0" in summary
    # Unmeasured is still red on the wired path, not only in the renderer.
    assert result.returncode == 1


def test_js_mutation_summary_appends_stryker_results(tmp_path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "reports" / "mutation").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "output_dir: reports/quality",
                "mutation_testing:",
                "  score_break: 60",
                "  report_paths:",
                "    summary_md: reports/mutation/summary.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "reports" / "mutation" / "summary.md").write_text(
        "# Mutation Testing Summary\n", encoding="utf-8"
    )
    (repo / "reports" / "mutation" / "stryker-js.json").write_text(
        json.dumps(
            {
                "files": {
                    "scripts/agent-runtime/demo.mjs": {
                        "mutants": [
                            {"status": "Killed", "mutatorName": "StringLiteral"},
                            {
                                "status": "Survived",
                                "mutatorName": "BooleanLiteral",
                                "location": {"start": {"line": 3}},
                            },
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "scripts/mutation/check_js_mutation_score.py",
        CHECK_JS_MUTATION_SCORE,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 1
    summary = (repo / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "## StrykerJS Mutation Slice" in summary
    assert "- Killed: 1" in summary
    assert "- Survived: 1" in summary
    assert "`scripts/agent-runtime/demo.mjs:3 `BooleanLiteral``" in summary


def test_js_mutation_summary_blocks_no_coverage_mutants(tmp_path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "reports" / "mutation").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "output_dir: reports/quality",
                "mutation_testing:",
                "  score_break: 80",
                "  report_paths:",
                "    summary_md: reports/mutation/summary.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "reports" / "mutation" / "stryker-js.json").write_text(
        json.dumps(
            {
                "files": {
                    "scripts/agent-runtime/demo.mjs": {
                        "mutants": [
                            {"status": "Killed", "mutatorName": "StringLiteral"},
                            {"status": "NoCoverage", "mutatorName": "StringLiteral"},
                            {"status": "NoCoverage", "mutatorName": "BooleanLiteral"},
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = run_loaded_script_main(
        "scripts/mutation/check_js_mutation_score.py",
        CHECK_JS_MUTATION_SCORE,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 1
    summary = (repo / "reports" / "mutation" / "summary.md").read_text(encoding="utf-8")
    assert "- Status: **FAIL**" in summary
    assert "- No coverage: 2" in summary
    assert "Blocking signal: JS mutants had no coverage" in summary
