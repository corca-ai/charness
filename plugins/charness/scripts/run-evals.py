#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.eval_init_repo import run_init_repo_inspect_states
from scripts.eval_registry import SCENARIOS, Scenario


class EvalError(Exception):
    pass


def run_command(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
def expect_success(result: subprocess.CompletedProcess[str], context: str) -> None:
    if result.returncode != 0:
        raise EvalError(f"{context}: exited with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
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

        init_result = run_command(["python3", str(init_script), "--repo-root", str(tmp)], cwd=root)
        expect_success(init_result, f"{skill_id} adapter init")

        adapter_path = tmp / ".agents" / adapter_name
        if not adapter_path.exists():
            raise EvalError(f"{skill_id} adapter init: expected {adapter_path.relative_to(tmp)} to exist")

        resolve_result = run_command(["python3", str(resolve_script), "--repo-root", str(tmp)], cwd=root)
        expect_success(resolve_result, f"{skill_id} adapter resolve")
        payload = json.loads(resolve_result.stdout)
        if payload.get("found") is not True or payload.get("valid") is not True:
            raise EvalError(f"{skill_id} adapter resolve: unexpected payload {payload!r}")
        if expected_artifact_path is not None and payload.get("artifact_path") != expected_artifact_path:
            raise EvalError(f"{skill_id} adapter resolve: unexpected artifact_path {payload.get('artifact_path')!r}")
        if expected_data is not None:
            data = payload.get("data", {})
            for key, expected in expected_data.items():
                if data.get(key) != expected:
                    raise EvalError(f"{skill_id} adapter resolve: unexpected {key} {data.get(key)!r}")
def scenario_skill_package_valid(root: Path) -> None:
    fixture = root / "evals" / "fixtures" / "skill-valid"
    result = run_command(["python3", "scripts/validate-skills.py", "--repo-root", str(fixture)], cwd=root)
    expect_success(result, "skill-valid fixture")
def scenario_profile_valid(root: Path) -> None:
    fixture = root / "evals" / "fixtures" / "profile-valid"
    result = run_command(["python3", "scripts/validate-profiles.py", "--repo-root", str(fixture)], cwd=root)
    expect_success(result, "profile-valid fixture")
def scenario_doc_links_valid(root: Path) -> None:
    fixture = root / "evals" / "fixtures" / "doc-links-valid"
    result = run_command(["python3", "scripts/check-doc-links.py", "--repo-root", str(fixture)], cwd=root)
    expect_success(result, "doc-links-valid fixture")
def scenario_quality_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(root, skill_id="quality", adapter_name="quality-adapter.yaml", expected_artifact_path="skill-outputs/quality/quality.md")
def scenario_impl_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(root, skill_id="impl", adapter_name="impl-adapter.yaml", expected_data={"output_dir": "skill-outputs/impl", "verification_tools": [], "ui_verification_tools": []})
def scenario_debug_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(root, skill_id="debug", adapter_name="debug-adapter.yaml", expected_artifact_path="skill-outputs/debug/debug.md")
def scenario_quality_adapter_checked_in(root: Path) -> None:
    resolve_script = root / "skills" / "public" / "quality" / "scripts" / "resolve_adapter.py"
    resolve_result = run_command(["python3", str(resolve_script), "--repo-root", str(root)], cwd=root)
    expect_success(resolve_result, "checked-in quality adapter resolve")
    payload = json.loads(resolve_result.stdout)
    if payload.get("found") is not True or payload.get("valid") is not True:
        raise EvalError(f"checked-in quality adapter resolve: unexpected payload {payload!r}")
    if payload.get("artifact_path") != "skill-outputs/quality/quality.md":
        raise EvalError(
            f"checked-in quality adapter resolve: unexpected artifact_path {payload.get('artifact_path')!r}"
        )
    gate_commands = payload.get("data", {}).get("gate_commands", [])
    if "./scripts/run-quality.sh" not in gate_commands:
        raise EvalError(f"checked-in quality adapter resolve: missing canonical gate command in {gate_commands!r}")

def scenario_narrative_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(root, skill_id="narrative", adapter_name="narrative-adapter.yaml", expected_artifact_path="skill-outputs/narrative/narrative.md")

def scenario_release_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(root, skill_id="release", adapter_name="release-adapter.yaml", expected_artifact_path="skill-outputs/release/release.md")

def scenario_handoff_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(root, skill_id="handoff", adapter_name="handoff-adapter.yaml", expected_artifact_path="skill-outputs/handoff/handoff.md")
def scenario_gather_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(root, skill_id="gather", adapter_name="gather-adapter.yaml", expected_artifact_path="skill-outputs/gather/gather.md")
def scenario_init_repo_adapter_bootstrap(root: Path) -> None:
    expect_adapter_bootstrap(root, skill_id="init-repo", adapter_name="init-repo-adapter.yaml", expected_artifact_path="skill-outputs/init-repo/init-repo.md")
def scenario_init_repo_inspect_states(root: Path) -> None:
    run_init_repo_inspect_states(root, run_command=run_command, expect_success=expect_success, error_type=EvalError)
def scenario_handoff_relative_links(root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="charness-eval-handoff-") as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "docs").mkdir(parents=True)
        (tmp / "README.md").write_text("# Demo\n", encoding="utf-8")
        (tmp / "docs" / "handoff.md").write_text(
            "\n".join(
                [
                    "# Demo Handoff",
                    "",
                    "[root](../README.md)",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        result = run_command(["python3", "scripts/check-doc-links.py", "--repo-root", str(tmp)], cwd=root)
        expect_success(result, "handoff relative-link portability")
def seed_find_skills_fixture(tmp: Path) -> None:
    local_skill_dir = tmp / "skills" / "public" / "local-demo"
    trusted_skill_dir = tmp / "vendor" / "trusted-skills" / "trusted-demo"
    adapter_dir = tmp / ".agents"
    integrations_dir = tmp / "integrations" / "tools"
    local_skill_dir.mkdir(parents=True)
    trusted_skill_dir.mkdir(parents=True)
    adapter_dir.mkdir(parents=True)
    integrations_dir.mkdir(parents=True)

    (local_skill_dir / "SKILL.md").write_text(
        "\n".join(["---", "name: local-demo", 'description: "Local demo skill."', "---", "", "# Local Demo"]) + "\n",
        encoding="utf-8",
    )
    (trusted_skill_dir / "SKILL.md").write_text(
        "\n".join(["---", "name: trusted-demo", 'description: "Trusted demo skill."', "---", "", "# Trusted Demo"])
        + "\n",
        encoding="utf-8",
    )
    (adapter_dir / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                f"repo: {tmp.name}",
                "language: en",
                "output_dir: skill-outputs/find-skills",
                "preset_id: portable-defaults",
                "customized_from: portable-defaults",
                "trusted_skill_roots:",
                "- vendor/trusted-skills",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (integrations_dir / "demo-tool.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "demo-tool",
                "kind": "external_binary",
                "upstream_repo": "https://example.com/demo-tool",
                "homepage": "https://example.com/demo-tool",
                "lifecycle": {
                    "install": {"commands": ["demo-tool install"], "notes": "Install demo-tool."},
                    "update": {"commands": ["demo-tool update"], "notes": "Update demo-tool."},
                },
                "checks": {
                    "detect": {"commands": ["demo-tool --version"], "success_criteria": ["exit_code:0"]},
                    "healthcheck": {"commands": ["demo-tool health"], "success_criteria": ["exit_code:0"]},
                },
                "access_modes": ["binary", "degraded"],
                "capability_requirements": {
                    "permission_scopes": ["browser.session"],
                },
                "readiness_checks": [
                    {
                        "check_id": "browser-setup",
                        "summary": "Browser setup is complete.",
                        "commands": ["test -f .browser-ready"],
                        "success_criteria": ["exit_code:0"],
                    }
                ],
                "version_expectation": {"policy": "advisory", "constraint": "latest"},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp / ".browser-ready").write_text("ready\n", encoding="utf-8")


def assert_find_skills_payload(payload: dict[str, object]) -> None:
    if payload["public_skills"][0]["id"] != "local-demo":
        raise EvalError(f"find-skills local-first discovery: unexpected public skills {payload['public_skills']!r}")
    if payload["trusted_skills"][0]["id"] != "trusted-demo":
        raise EvalError(f"find-skills local-first discovery: unexpected trusted skills {payload['trusted_skills']!r}")
    integration = payload["integrations"][0]
    if integration["id"] != "demo-tool":
        raise EvalError(f"find-skills local-first discovery: unexpected integrations {payload['integrations']!r}")
    if integration["kind"] != "external_binary":
        raise EvalError(f"find-skills local-first discovery: unexpected integrations {payload['integrations']!r}")
    if integration["access_modes"] != ["binary", "degraded"]:
        raise EvalError(f"find-skills local-first discovery: unexpected integrations {payload['integrations']!r}")
    if integration["capability_requirements"] != {"permission_scopes": ["browser.session"]}:
        raise EvalError(f"find-skills local-first discovery: unexpected integrations {payload['integrations']!r}")
    if integration["readiness_checks"] != [{"check_id": "browser-setup", "summary": "Browser setup is complete."}]:
        raise EvalError(f"find-skills local-first discovery: unexpected integrations {payload['integrations']!r}")

def scenario_find_skills_local_first(root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="charness-eval-find-skills-") as tmpdir:
        tmp = Path(tmpdir)
        seed_find_skills_fixture(tmp)

        result = run_command(
            ["python3", "skills/public/find-skills/scripts/list_capabilities.py", "--repo-root", str(tmp)],
            cwd=root,
        )
        expect_success(result, "find-skills local-first discovery")
        assert_find_skills_payload(json.loads(result.stdout))

def scenario_representative_skill_contracts(root: Path) -> None:
    result = run_command(["python3", "scripts/check-skill-contracts.py", "--repo-root", str(root)], cwd=root)
    expect_success(result, "representative skill contracts")

def scenario_support_sync_contracts(root: Path) -> None:
    result = run_command(["python3", "scripts/eval_support_sync_contracts.py", "--repo-root", str(root)], cwd=root)
    expect_success(result, "support-sync dry-run contracts")

def run_scenario(root: Path, scenario: Scenario) -> None:
    handlers = {
        "skill-valid": scenario_skill_package_valid,
        "profile-valid": scenario_profile_valid,
        "doc-links-valid": scenario_doc_links_valid,
        "impl-adapter-bootstrap": scenario_impl_adapter_bootstrap,
        "debug-adapter-bootstrap": scenario_debug_adapter_bootstrap,
        "quality-adapter-bootstrap": scenario_quality_adapter_bootstrap,
        "quality-adapter-checked-in": scenario_quality_adapter_checked_in,
        "narrative-adapter-bootstrap": scenario_narrative_adapter_bootstrap,
        "release-adapter-bootstrap": scenario_release_adapter_bootstrap,
        "handoff-adapter-bootstrap": scenario_handoff_adapter_bootstrap,
        "gather-adapter-bootstrap": scenario_gather_adapter_bootstrap,
        "init-repo-adapter-bootstrap": scenario_init_repo_adapter_bootstrap,
        "init-repo-inspect-states": scenario_init_repo_inspect_states,
        "handoff-relative-links": scenario_handoff_relative_links,
        "find-skills-local-first": scenario_find_skills_local_first,
        "support-sync-contracts": scenario_support_sync_contracts,
        "representative-skill-contracts": scenario_representative_skill_contracts,
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repo-owned smoke scenarios under evals/.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--scenario-id", action="append", default=[])
    args = parser.parse_args()

    root = args.repo_root.resolve()
    ensure_fixtures_present(root)
    selected = [scenario for scenario in SCENARIOS if not args.scenario_id or scenario.scenario_id in args.scenario_id]
    if args.scenario_id:
        known = {scenario.scenario_id for scenario in SCENARIOS}
        unknown = sorted(set(args.scenario_id) - known)
        if unknown:
            raise EvalError(f"unknown scenario id(s): {', '.join(unknown)}")

    for scenario in selected:
        run_scenario(root, scenario)
        print(f"PASS {scenario.scenario_id}: {scenario.description}")

    print(f"Ran {len(selected)} eval scenario(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (EvalError, json.JSONDecodeError, shutil.Error) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
