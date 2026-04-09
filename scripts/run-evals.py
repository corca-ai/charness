#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


class EvalError(Exception):
    pass


@dataclass
class Scenario:
    scenario_id: str
    description: str


def run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def expect_success(result: subprocess.CompletedProcess[str], context: str) -> None:
    if result.returncode != 0:
        raise EvalError(f"{context}: exited with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


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
    with tempfile.TemporaryDirectory(prefix="charness-eval-adapter-") as tmpdir:
        tmp = Path(tmpdir)
        init_script = root / "skills" / "public" / "quality" / "scripts" / "init_adapter.py"
        resolve_script = root / "skills" / "public" / "quality" / "scripts" / "resolve_adapter.py"

        init_result = run_command(
            ["python3", str(init_script), "--repo-root", str(tmp), "--preset-id", "portable-defaults"],
            cwd=root,
        )
        expect_success(init_result, "quality adapter init")

        adapter_path = tmp / ".agents" / "quality-adapter.yaml"
        if not adapter_path.exists():
            raise EvalError("quality adapter init: expected .agents/quality-adapter.yaml to exist")

        resolve_result = run_command(["python3", str(resolve_script), "--repo-root", str(tmp)], cwd=root)
        expect_success(resolve_result, "quality adapter resolve")
        payload = json.loads(resolve_result.stdout)
        if payload.get("found") is not True or payload.get("valid") is not True:
            raise EvalError(f"quality adapter resolve: unexpected payload {payload!r}")
        if payload.get("artifact_path") != "skill-outputs/quality/quality.md":
            raise EvalError(f"quality adapter resolve: unexpected artifact_path {payload.get('artifact_path')!r}")


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


def scenario_handoff_absolute_links(root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="charness-eval-handoff-") as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "docs").mkdir(parents=True)
        (tmp / "README.md").write_text("# Demo\n", encoding="utf-8")
        (tmp / "docs" / "handoff.md").write_text(
            "\n".join(
                [
                    "# Demo Handoff",
                    "",
                    f"[root]({tmp / 'README.md'})",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        result = run_command(["python3", "scripts/check-doc-links.py", "--repo-root", str(tmp)], cwd=root)
        expect_success(result, "handoff absolute-link portability")


def scenario_find_skills_local_first(root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="charness-eval-find-skills-") as tmpdir:
        tmp = Path(tmpdir)
        local_skill_dir = tmp / "skills" / "public" / "local-demo"
        official_skill_dir = tmp / "vendor" / "official-skills" / "official-demo"
        adapter_dir = tmp / ".agents"
        integrations_dir = tmp / "integrations" / "tools"
        local_skill_dir.mkdir(parents=True)
        official_skill_dir.mkdir(parents=True)
        adapter_dir.mkdir(parents=True)
        integrations_dir.mkdir(parents=True)

        (local_skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: local-demo",
                    'description: "Local demo skill."',
                    "---",
                    "",
                    "# Local Demo",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (official_skill_dir / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: official-demo",
                    'description: "Official demo skill."',
                    "---",
                    "",
                    "# Official Demo",
                ]
            )
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
                    "official_skill_roots:",
                    "- vendor/official-skills",
                    "prefer_local_first: true",
                    "allow_external_registry: false",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (integrations_dir / "demo-tool.json").write_text(
            json.dumps({"schema_version": "1", "tool_id": "demo-tool"}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        result = run_command(
            ["python3", "skills/public/find-skills/scripts/list_capabilities.py", "--repo-root", str(tmp)],
            cwd=root,
        )
        expect_success(result, "find-skills local-first discovery")
        payload = json.loads(result.stdout)
        if payload["public_skills"][0]["id"] != "local-demo":
            raise EvalError(f"find-skills local-first discovery: unexpected public skills {payload['public_skills']!r}")
        if payload["official_skills"][0]["id"] != "official-demo":
            raise EvalError(
                f"find-skills local-first discovery: unexpected official skills {payload['official_skills']!r}"
            )
        if payload["integrations"][0]["id"] != "demo-tool":
            raise EvalError(f"find-skills local-first discovery: unexpected integrations {payload['integrations']!r}")


def scenario_representative_skill_contracts(root: Path) -> None:
    result = run_command(["python3", "scripts/check-skill-contracts.py", "--repo-root", str(root)], cwd=root)
    expect_success(result, "representative skill contracts")


SCENARIOS = (
    Scenario("skill-valid", "fixture repo with one valid public skill passes package validation"),
    Scenario("profile-valid", "fixture repo with one valid profile passes artifact validation"),
    Scenario("doc-links-valid", "fixture docs with valid internal links pass markdown link validation"),
    Scenario("quality-adapter-bootstrap", "quality init/resolve scripts bootstrap a clean repo"),
    Scenario("quality-adapter-checked-in", "checked-in quality adapter resolves to the declared repo contract"),
    Scenario("handoff-absolute-links", "repo-local absolute markdown links remain valid in handoff-style docs"),
    Scenario("find-skills-local-first", "find-skills keeps local-first discovery while exposing configured official roots"),
    Scenario("representative-skill-contracts", "representative public skills retain their required contract markers"),
)


def run_scenario(root: Path, scenario: Scenario) -> None:
    handlers = {
        "skill-valid": scenario_skill_package_valid,
        "profile-valid": scenario_profile_valid,
        "doc-links-valid": scenario_doc_links_valid,
        "quality-adapter-bootstrap": scenario_quality_adapter_bootstrap,
        "quality-adapter-checked-in": scenario_quality_adapter_checked_in,
        "handoff-absolute-links": scenario_handoff_absolute_links,
        "find-skills-local-first": scenario_find_skills_local_first,
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
    args = parser.parse_args()

    root = args.repo_root.resolve()
    ensure_fixtures_present(root)

    for scenario in SCENARIOS:
        run_scenario(root, scenario)
        print(f"PASS {scenario.scenario_id}: {scenario.description}")

    print(f"Ran {len(SCENARIOS)} eval scenario(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (EvalError, json.JSONDecodeError, shutil.Error) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
