#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.cautilus_scenarios_lib import REGISTRY_PATH, validate_registry


class EvalError(Exception):
    pass


def load_profile_skills(repo_root: Path, profile: str) -> list[dict[str, object]]:
    registry = validate_registry(repo_root)["registry"]
    profiles = registry["profiles"]
    profile_payload = profiles.get(profile)
    if not isinstance(profile_payload, dict):
        raise EvalError(f"{REGISTRY_PATH}: unknown profile `{profile}`")
    skills = profile_payload.get("skills")
    if not isinstance(skills, list):
        raise EvalError(f"{REGISTRY_PATH}: `{profile}` profile is missing `skills`")
    return skills


def run_selected_evals(repo_root: Path, scenario_names: list[str]) -> subprocess.CompletedProcess[str]:
    command = ["python3", "scripts/run-evals.py", "--repo-root", str(repo_root)]
    for scenario_name in scenario_names:
        command.extend(["--scenario-id", scenario_name])
    return subprocess.run(command, cwd=repo_root, check=False, capture_output=True, text=True)


def build_summary(
    *,
    repo_root: Path,
    mode: str,
    profile: str,
    baseline_ref: str,
    samples: int,
    command: subprocess.CompletedProcess[str],
    skills: list[dict[str, object]],
) -> dict[str, object]:
    selected_ids = sorted({scenario_id for item in skills for scenario_id in item["scenario_ids"]})
    return {
        "schema_version": 1,
        "repo": repo_root.name,
        "mode": mode,
        "profile": profile,
        "baseline_ref": baseline_ref,
        "samples": samples,
        "scenario_count": len(selected_ids),
        "skills": skills,
        "run_evals": {
            "command": "python3 scripts/run-evals.py --repo-root . "
            + " ".join(f"--scenario-id {scenario_id}" for scenario_id in selected_ids),
            "exit_code": command.returncode,
            "stdout": command.stdout.strip(),
            "stderr": command.stderr.strip(),
        },
    }


def write_summary(output_dir: Path, summary: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Cautilus Scenario Summary",
        "",
        f"- mode: `{summary['mode']}`",
        f"- profile: `{summary['profile']}`",
        f"- baseline_ref: `{summary['baseline_ref']}`",
        f"- scenarios: `{summary['scenario_count']}`",
        f"- run-evals exit: `{summary['run_evals']['exit_code']}`",
        "",
        "## Skills",
        "",
    ]
    for item in summary["skills"]:
        scenario_ids = ", ".join(f"`{scenario_id}`" for scenario_id in item["scenario_ids"])
        lines.append(f"- `{item['skill_id']}`: {scenario_ids}")
    lines.extend(
        [
            "",
            "## Run Evals Output",
            "",
            "```text",
            summary["run_evals"]["stdout"] or summary["run_evals"]["stderr"] or "(no output)",
            "```",
            "",
        ]
    )
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--profile", default="evaluator-required")
    parser.add_argument("--baseline-ref", default="origin/main")
    parser.add_argument("--samples", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    skills = load_profile_skills(repo_root, args.profile)
    selected_ids = sorted({scenario_id for item in skills for scenario_id in item["scenario_ids"]})
    result = run_selected_evals(repo_root, selected_ids)
    summary = build_summary(
        repo_root=repo_root,
        mode=args.mode,
        profile=args.profile,
        baseline_ref=args.baseline_ref,
        samples=args.samples,
        command=result,
        skills=skills,
    )
    write_summary(args.output_dir.resolve(), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if result.returncode != 0:
        raise EvalError("selected cautilus-backed eval scenarios failed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (EvalError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
