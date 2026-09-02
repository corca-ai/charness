#!/usr/bin/env python3

from __future__ import annotations

import argparse
import concurrent.futures
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
# Process width has one owner in this repo: the standing pytest runner, which decides
# xdist worker count from affinity. Consumed here rather than re-derived so a third
# copy of the affinity question cannot drift from the other two.
usable_cpu_count = import_repo_module(__file__, "scripts.run_standing_pytest").usable_cpu_count
_scripts_subprocess_guard_module = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _scripts_subprocess_guard_module.run_process
_tools_eval_setup_module = import_repo_module(__file__, "tools.eval_setup")
run_setup_inspect_states = _tools_eval_setup_module.run_setup_inspect_states
run_setup_operator_acceptance_synthesis = (
    _tools_eval_setup_module.run_setup_operator_acceptance_synthesis
)
_tools_eval_issue_scenarios_module = import_repo_module(__file__, "tools.eval_issue_scenarios")
run_issue_sibling_search_concept_fixtures = (
    _tools_eval_issue_scenarios_module.run_issue_sibling_search_concept_fixtures
)
_tools_eval_registry_module = import_repo_module(__file__, "tools.eval_registry")
SCENARIOS = _tools_eval_registry_module.SCENARIOS
Scenario = _tools_eval_registry_module.Scenario


class EvalError(Exception):
    pass


COMMAND_TIMEOUT_SECONDS = 60


def run_command(
    command: list[str], *, cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return run_process(
        command,
        cwd=cwd,
        env=env,
        timeout_seconds=COMMAND_TIMEOUT_SECONDS,
    )


def expect_success(result: subprocess.CompletedProcess[str], context: str) -> None:
    if result.returncode != 0:
        raise EvalError(
            f"{context}: exited with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def expect_adapter_bootstrap(
    root: Path,
    *,
    skill_id: str,
    adapter_name: str,
    expected_artifact_path: str | None = None,
    expected_data: dict[str, object] | None = None,
) -> None:
    with tempfile.TemporaryDirectory(prefix=f"charness-eval-{skill_id}-adapter-") as tmpdir:
        tmp = Path(tmpdir)
        skill_dir = root / "skills" / "public" / skill_id / "scripts"
        init_script = skill_dir / "init_adapter.py"
        resolve_script = skill_dir / "resolve_adapter.py"

        init_result = run_command(
            [sys.executable, str(init_script), "--repo-root", str(tmp)], cwd=root
        )
        expect_success(init_result, f"{skill_id} adapter init")

        adapter_path = tmp / ".agents" / adapter_name
        if not adapter_path.exists():
            raise EvalError(
                f"{skill_id} adapter init: expected {adapter_path.relative_to(tmp)} to exist"
            )

        resolve_result = run_command(
            [sys.executable, str(resolve_script), "--repo-root", str(tmp)], cwd=root
        )
        expect_success(resolve_result, f"{skill_id} adapter resolve")
        payload = yaml.safe_load(resolve_result.stdout)
        if payload.get("found") is not True or payload.get("valid") is not True:
            raise EvalError(f"{skill_id} adapter resolve: unexpected payload {payload!r}")
        if (
            expected_artifact_path is not None
            and payload.get("artifact_path") != expected_artifact_path
        ):
            raise EvalError(
                f"{skill_id} adapter resolve: unexpected artifact_path {payload.get('artifact_path')!r}"
            )
        if expected_data is not None:
            data = payload.get("data", {})
            for key, expected in expected_data.items():
                if data.get(key) != expected:
                    raise EvalError(
                        f"{skill_id} adapter resolve: unexpected {key} {data.get(key)!r}"
                    )


def scenario_skill_package_valid(root: Path) -> None:
    fixture = root / "evals" / "fixtures" / "skill-valid"
    result = run_command(
        [sys.executable, "-m", "tools.validate_skills", "--repo-root", str(fixture)], cwd=root
    )
    expect_success(result, "skill-valid fixture")


def scenario_profile_valid(root: Path) -> None:
    fixture = root / "evals" / "fixtures" / "profile-valid"
    result = run_command(
        [sys.executable, "-m", "tools.validate_profiles", "--repo-root", str(fixture)], cwd=root
    )
    expect_success(result, "profile-valid fixture")


def scenario_doc_links_valid(root: Path) -> None:
    fixture = root / "evals" / "fixtures" / "doc-links-valid"
    result = run_command(
        [sys.executable, "scripts/check_doc_links.py", "--repo-root", str(fixture)], cwd=root
    )
    expect_success(result, "doc-links-valid fixture")


def scenario_quality_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(
        root,
        skill_id="quality",
        adapter_name="quality-adapter.yaml",
        expected_artifact_path="charness-artifacts/quality/latest.md",
    )


def scenario_impl_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(
        root,
        skill_id="impl",
        adapter_name="impl-adapter.yaml",
        expected_data={
            "output_dir": "charness-artifacts/impl",
            "verification_tools": [],
            "ui_verification_tools": [],
            "truth_surfaces": [],
        },
    )


def scenario_debug_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(
        root,
        skill_id="debug",
        adapter_name="debug-adapter.yaml",
        expected_artifact_path="charness-artifacts/debug/latest.md",
    )


def scenario_quality_adapter_checked_in(root: Path) -> None:
    resolve_script = root / "skills" / "public" / "quality" / "scripts" / "resolve_adapter.py"
    resolve_result = run_command(
        [sys.executable, str(resolve_script), "--repo-root", str(root)], cwd=root
    )
    expect_success(resolve_result, "checked-in quality adapter resolve")
    payload = yaml.safe_load(resolve_result.stdout)
    if payload.get("found") is not True or payload.get("valid") is not True:
        raise EvalError(f"checked-in quality adapter resolve: unexpected payload {payload!r}")
    if payload.get("artifact_path") != "charness-artifacts/quality/latest.md":
        raise EvalError(
            f"checked-in quality adapter resolve: unexpected artifact_path {payload.get('artifact_path')!r}"
        )
    data = payload.get("data", {})
    gate_commands = data.get("gate_commands", [])
    if "./scripts/run-quality.sh" not in gate_commands:
        raise EvalError(
            f"checked-in quality adapter resolve: missing canonical gate command in {gate_commands!r}"
        )
    if data.get("coverage_fragile_margin_pp") != 1.0:
        raise EvalError(
            f"checked-in quality adapter resolve: unexpected coverage fragile margin {data!r}"
        )
    floor_policy = data.get("coverage_floor_policy", {})
    if floor_policy.get("min_statements_threshold") != 30:
        raise EvalError(
            f"checked-in quality adapter resolve: unexpected coverage floor policy {data!r}"
        )
    if (
        data.get("spec_pytest_reference_format")
        != r"Covered by pytest:\s+`tests/[^`]+`(?:,\s*`tests/[^`]+`)*"
    ):
        raise EvalError(
            f"checked-in quality adapter resolve: unexpected pytest reference format {data!r}"
        )


def scenario_quality_bootstrap_posture(root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="charness-eval-quality-bootstrap-") as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "docs").mkdir(parents=True)
        (tmp / "scripts").mkdir(parents=True)
        (tmp / "README.md").write_text("# Demo\n", encoding="utf-8")
        (tmp / "docs" / "index.md").write_text("# Documentation index\n", encoding="utf-8")
        (tmp / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
        (tmp / "scripts" / "run-quality.sh").write_text(
            "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
        )
        (tmp / "scripts" / "check-secrets.sh").write_text(
            "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
        )

        bootstrap_result = run_command(
            [
                sys.executable,
                "skills/public/quality/scripts/bootstrap_adapter.py",
                "--repo-root",
                str(tmp),
            ],
            cwd=root,
        )
        expect_success(bootstrap_result, "quality bootstrap posture")
        payload = yaml.safe_load(bootstrap_result.stdout)
        if payload["field_statuses"]["gate_commands"] != "installed":
            raise EvalError(f"quality bootstrap posture: unexpected gate status {payload!r}")
        if payload["field_statuses"]["preflight_commands"] != "deferred":
            raise EvalError(f"quality bootstrap posture: unexpected preflight status {payload!r}")
        if payload["preset_lineage"] != ["python-quality"]:
            raise EvalError(f"quality bootstrap posture: unexpected preset lineage {payload!r}")
        if not payload["deferred_setup"]:
            raise EvalError(
                f"quality bootstrap posture: expected deferred setup report {payload!r}"
            )

        resolve_result = run_command(
            [
                sys.executable,
                "skills/public/quality/scripts/resolve_adapter.py",
                "--repo-root",
                str(tmp),
            ],
            cwd=root,
        )
        expect_success(resolve_result, "quality bootstrap posture resolve")
        resolved = yaml.safe_load(resolve_result.stdout)
        if resolved["data"]["gate_commands"] != ["./scripts/run-quality.sh"]:
            raise EvalError(
                f"quality bootstrap posture resolve: unexpected adapter payload {resolved!r}"
            )
        if resolved["data"]["coverage_fragile_margin_pp"] != 1.0:
            raise EvalError(
                f"quality bootstrap posture resolve: unexpected fragile margin {resolved!r}"
            )
        if resolved["data"]["coverage_floor_policy"]["gate_script_pattern"] != "*-quality-gate.sh":
            raise EvalError(
                f"quality bootstrap posture resolve: unexpected floor policy {resolved!r}"
            )


def scenario_narrative_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(
        root,
        skill_id="narrative",
        adapter_name="narrative-adapter.yaml",
        expected_artifact_path="charness-artifacts/narrative/latest.md",
    )


def scenario_release_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(
        root,
        skill_id="release",
        adapter_name="release-adapter.yaml",
        expected_artifact_path="charness-artifacts/release/latest.md",
    )


def scenario_gather_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(
        root,
        skill_id="gather",
        adapter_name="gather-adapter.yaml",
        expected_artifact_path="charness-artifacts/gather/latest.md",
    )


def scenario_setup_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(
        root,
        skill_id="setup",
        adapter_name="setup-adapter.yaml",
        expected_artifact_path="charness-artifacts/setup/latest.md",
    )


def scenario_setup_inspect_states(root: Path) -> None:
    run_setup_inspect_states(
        root, run_command=run_command, expect_success=expect_success, error_type=EvalError
    )


def scenario_setup_operator_acceptance_synthesis(root: Path) -> None:
    run_setup_operator_acceptance_synthesis(
        root,
        run_command=run_command,
        expect_success=expect_success,
        error_type=EvalError,
    )


def scenario_representative_skill_contracts(root: Path) -> None:
    result = run_command(
        [sys.executable, "-m", "tools.check_skill_contracts", "--repo-root", str(root)], cwd=root
    )
    expect_success(result, "representative skill contracts")


def scenario_support_sync_contracts(root: Path) -> None:
    result = run_command(
        [sys.executable, "scripts/eval_support_sync_contracts.py", "--repo-root", str(root)],
        cwd=root,
    )
    expect_success(result, "support-sync dry-run contracts")


def scenario_issue_sibling_search_concept_fixtures(root: Path) -> None:
    run_issue_sibling_search_concept_fixtures(
        root, run_command=run_command, expect_success=expect_success
    )


def run_scenario(root: Path, scenario: Scenario) -> None:
    handlers = {
        "skill-valid": scenario_skill_package_valid,
        "profile-valid": scenario_profile_valid,
        "doc-links-valid": scenario_doc_links_valid,
        "impl-adapter-bootstrap": scenario_impl_adapter_bootstrap,
        "debug-adapter-bootstrap": scenario_debug_adapter_bootstrap,
        "quality-adapter-bootstrap": scenario_quality_adapter_bootstrap,
        "quality-adapter-checked-in": scenario_quality_adapter_checked_in,
        "quality-bootstrap-posture": scenario_quality_bootstrap_posture,
        "narrative-adapter-bootstrap": scenario_narrative_adapter_bootstrap,
        "release-adapter-bootstrap": scenario_release_adapter_bootstrap,
        "gather-adapter-bootstrap": scenario_gather_adapter_bootstrap,
        "setup-adapter-bootstrap": scenario_setup_adapter_bootstrap,
        "setup-inspect-states": scenario_setup_inspect_states,
        "setup-operator-acceptance-synthesis": scenario_setup_operator_acceptance_synthesis,
        "support-sync-contracts": scenario_support_sync_contracts,
        "representative-skill-contracts": scenario_representative_skill_contracts,
        "issue-sibling-search-concept-fixtures": scenario_issue_sibling_search_concept_fixtures,
    }
    handlers[scenario.scenario_id](root)


def ensure_fixtures_present(root: Path) -> None:
    required = (
        root / "evals" / "fixtures" / "skill-valid" / "skills" / "public" / "demo" / "SKILL.md",
        root / "evals" / "fixtures" / "profile-valid" / "profiles" / "minimal.json",
        root / "evals" / "fixtures" / "doc-links-valid" / "README.md",
    )
    for path in required:
        if not path.exists():
            raise EvalError(f"missing required eval fixture `{path.relative_to(root)}`")


NO_FIXTURE_SCENARIOS: set[str] = set()


def run_selected_scenarios(root: Path, selected: list[Scenario], jobs: int) -> None:
    if jobs <= 1 or len(selected) <= 1:
        for scenario in selected:
            run_scenario(root, scenario)
            print(f"PASS {scenario.scenario_id}: {scenario.description}")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {scenario: executor.submit(run_scenario, root, scenario) for scenario in selected}
        for scenario in selected:
            futures[scenario].result()
            print(f"PASS {scenario.scenario_id}: {scenario.description}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repo-owned smoke scenarios under evals/.")
    parser.add_argument("--repo-root", type=Path, default=repo_root_from_script(__file__))
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument(
        "--jobs",
        type=int,
        default=0,
        help="Concurrent scenario jobs; default: min(4, selected scenarios).",
    )
    args = parser.parse_args()

    root = args.repo_root.resolve()
    selected = [
        scenario
        for scenario in SCENARIOS
        if not args.scenario_id or scenario.scenario_id in args.scenario_id
    ]
    if args.jobs < 0:
        raise EvalError("--jobs must be zero or a positive integer")
    if args.scenario_id:
        known = {scenario.scenario_id for scenario in SCENARIOS}
        unknown = sorted(set(args.scenario_id) - known)
        if unknown:
            raise EvalError(f"unknown scenario id(s): {', '.join(unknown)}")
    if not selected or any(
        scenario.scenario_id not in NO_FIXTURE_SCENARIOS for scenario in selected
    ):
        ensure_fixtures_present(root)

    # Affinity, not the box's total: under `taskset`/a cpuset this otherwise picks 4
    # jobs for 1 usable CPU. Capped at 4 either way, so the blast radius is far
    # smaller than the pytest runner's 16 -- but it is the same wrong question.
    run_selected_scenarios(root, selected, args.jobs or min(4, len(selected), usable_cpu_count()))
    print(f"Ran {len(selected)} eval scenario(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (EvalError, yaml.YAMLError, shutil.Error) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
