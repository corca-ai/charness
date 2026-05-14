#!/usr/bin/env python3
"""Detect mutation testing state and propose install actions.

Read-only by default. Pass --execute to apply the install when status is
`missing`: append a fenced `mutation_testing` scaffold to the adapter and copy
the workflow template to the configured `workflow_path`.

Contract: see ../references/mutation-testing.md.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)

_scripts_quality_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.quality_adapter_lib"
)
load_quality_adapter = _scripts_quality_adapter_lib_module.load_quality_adapter

TEMPLATE_RELATIVE_PATH = Path("skills/public/quality/scripts/templates/mutation-tests.yml")
ADAPTER_CANONICAL_PATH = Path(".agents/quality-adapter.yaml")
FENCE_START = "# >>> mutation_testing (charness propose) >>>"
FENCE_END = "# <<< mutation_testing (charness propose) <<<"


def _scaffold_block() -> str:
    return "\n".join(
        [
            FENCE_START,
            "mutation_testing:",
            "  commands:",
            '    dry_run: ""',
            '    full: ""',
            '    sample: ""',
            '    summary: ""',
            "  score_break: 60",
            '  schedule_cron: "17 */3 * * *"',
            "  changed_quota: 5",
            "  max_files: 10",
            "  auto_issue:",
            "    enabled: false",
            "    label: mutation-test",
            "    title: Mutation test regression on main",
            "    marker_token: mutation-test-regression",
            "  workflow_path: .github/workflows/mutation-tests.yml",
            "  report_paths:",
            "    summary_md: reports/mutation/summary.md",
            "    sample_md: reports/mutation/sample.md",
            "    log: reports/mutation/run.log",
            "  declined: false",
            FENCE_END,
            "",
        ]
    )


def classify(adapter_payload: dict) -> str:
    if adapter_payload.get("errors"):
        return "blocked"
    data = adapter_payload.get("data") or {}
    block = data.get("mutation_testing") or {}
    if block.get("declined") is True:
        return "declined"
    commands = block.get("commands") or {}
    full = (commands.get("full") or "").strip()
    if full:
        return "installed"
    return "missing"


def _install_actions(repo_root: Path, adapter_path: str | None, block: dict) -> list[dict]:
    target_adapter = Path(adapter_path) if adapter_path else repo_root / ADAPTER_CANONICAL_PATH
    workflow_path = repo_root / (block.get("workflow_path") or ".github/workflows/mutation-tests.yml")
    return [
        {
            "kind": "append_adapter_block",
            "target": str(target_adapter),
            "fence_start": FENCE_START,
            "fence_end": FENCE_END,
        },
        {
            "kind": "install_workflow_template",
            "source": str(REPO_ROOT / TEMPLATE_RELATIVE_PATH),
            "target": str(workflow_path),
        },
    ]


def _recommendation(status: str, errors: list[str]) -> str:
    if status == "installed":
        return "mutation_testing is configured; no action."
    if status == "missing":
        return (
            "mutation_testing is not configured. Fill commands.* and install the workflow, "
            "or run this script with --execute to scaffold defaults."
        )
    if status == "declined":
        return "mutation_testing.declined is true; remove the flag to reopen the propose loop."
    return f"adapter validation failed with {len(errors)} errors; resolve them before proposing."


SCHEDULE_CRON_PLACEHOLDER = "MUTATION_SCHEDULE_CRON_PLACEHOLDER"


def _execute_install(repo_root: Path, adapter_path: str | None, block: dict) -> list[str]:
    """Append the scaffold block and copy the workflow template.

    Refuses to write when no adapter file exists — running --execute without an
    adapter would produce a YAML file lacking `version:` / `repo:` headers and
    `quality` would later reject it. Operator should run init_adapter first.
    """
    applied: list[str] = []
    if adapter_path is None:
        raise SystemExit(
            "No quality adapter exists. Run skills/public/quality/scripts/init_adapter.py "
            "before --execute so the resulting file passes validation."
        )
    target_adapter = Path(adapter_path)
    if not target_adapter.is_absolute():
        target_adapter = (repo_root / target_adapter).resolve()
    if not target_adapter.is_file():
        raise SystemExit(f"Adapter resolved to {target_adapter} but the file is missing.")
    existing = target_adapter.read_text(encoding="utf-8")
    if FENCE_START in existing:
        applied.append(f"adapter scaffold already present: {target_adapter}")
    else:
        suffix = "" if existing.endswith("\n") else "\n"
        with target_adapter.open("a", encoding="utf-8") as fh:
            fh.write(suffix + "\n" + _scaffold_block())
        applied.append(f"appended mutation_testing scaffold to {target_adapter}")
    workflow_target = repo_root / (block.get("workflow_path") or ".github/workflows/mutation-tests.yml")
    workflow_target.parent.mkdir(parents=True, exist_ok=True)
    template_source = REPO_ROOT / TEMPLATE_RELATIVE_PATH
    if not template_source.is_file():
        raise FileNotFoundError(f"workflow template not found at {template_source}")
    if workflow_target.exists():
        applied.append(f"workflow already present, not overwritten: {workflow_target}")
    else:
        # Substitute the schedule cron at install time. GitHub Actions parses
        # `schedule.cron` before any job step runs, so runtime adapter parsing
        # cannot reach it. Re-run --execute to refresh the cron after changing
        # mutation_testing.schedule_cron.
        schedule_cron = block.get("schedule_cron") or "17 */3 * * *"
        rendered = template_source.read_text(encoding="utf-8").replace(
            SCHEDULE_CRON_PLACEHOLDER, schedule_cron
        )
        workflow_target.write_text(rendered, encoding="utf-8")
        applied.append(f"installed workflow template at {workflow_target} (cron={schedule_cron})")
    return applied


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="Apply install when status is missing.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    payload = load_quality_adapter(repo_root)
    status = classify(payload)
    data = payload.get("data") or {}
    block = data.get("mutation_testing") or {}
    install_actions = _install_actions(repo_root, payload.get("path"), block) if status == "missing" else []
    applied: list[str] = []
    if args.execute and status == "missing":
        applied = _execute_install(repo_root, payload.get("path"), block)
        status = "installed"
    result = {
        "status": status,
        "recommendation": _recommendation(status, payload.get("errors") or []),
        "install_actions": install_actions,
        "applied": applied,
        "adapter_path": payload.get("path"),
        "errors": payload.get("errors") or [],
        "warnings": payload.get("warnings") or [],
    }
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
