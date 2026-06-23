#!/usr/bin/env python3
"""Plan the first phase of a quality run before broad gates or fixes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

BASE_PRIMER_REFS = [
    "references/quality-lenses.md",
    "references/inventory-dispatch.md",
    "references/automation-promotion.md",
    "references/gate-classification.md",
    "references/proposal-flow.md",
    "references/maintainer-local-enforcement.md",
    "references/operability-signals.md",
]

SKILL_PRIMER_REFS = [
    "references/skill-quality.md",
    "references/skill-ergonomics.md",
]

ON_DEMAND_TRIGGERS = {
    "references/adapter-contract.md": "adapter missing, invalid, stale, or under-specified",
    "references/adapter-gate-review.md": "adapter or gate recommendation needs enforcement-tier review",
    "references/agent-production-runtime.md": "production agent runtime, provider policy, fallback, telemetry, or serving-path risk",
    "references/dup-ratchet.md": "dup-ratchet failure, scanner skew, baseline update, or clone-family interpretation",
    "references/bootstrap-escalations.md": "bootstrap path needs non-default escalation",
    "references/bootstrap-posture.md": "quality adapter bootstrap or setup-state repair",
    "references/boundary-bypass-ratchet.md": "boundary-bypass inventory, ratchet, or exemption review",
    "references/brittle-source-guards.md": "brittle source guard finding or matcher migration",
    "references/standing-gate-verbosity.md": "standing gate output, runtime, progress signal, or failure detail review",
    "references/testability-and-selection.md": "slow tests, affected-test selection, mutation workload, or broad test economics",
    "references/cautilus-on-demand.md": "cautilus evaluate fixture, observation, or skill-experiment is being considered",
    "references/behavior-testing.md": "deterministic gates cannot honestly prove an agent/user behavior seam",
    "references/ci-recoverable-gate-triage.md": "slow local gate pressure raises CI recoverability as an option",
    "references/cli-ergonomics-smells.md": "CLI ergonomics, command archetype, or mutating-probe review",
    "references/coverage-floor-policy.md": "coverage-floor inventory or policy finding",
    "references/dual-implementation-parity.md": "dual implementation smell or parity-harness question",
    "references/entrypoint-docs-ergonomics.md": "entrypoint documentation ergonomics review",
    "references/executable-spec-economics.md": "executable-spec runtime, duplication, or layering review",
    "references/installable-cli-probes.md": "installable CLI probe, doctor, help, or lifecycle ownership review",
    "references/lint-ignore-discipline.md": "lint-ignore inventory or retained-suppression decision",
    "references/mutation-testing.md": "mutation-testing adapter, workflow, summary, or sampling review",
    "references/prompt-asset-policy.md": "prompt asset inventory or prompt-regression proof",
    "references/public-spec-layering.md": "public spec layering, smoke duplication, or source-guard pressure review",
    "references/quality-signal-scorecard.md": "structural quality cleanup candidate scoring",
    "references/security-overview.md": "security posture or supply-chain proof separation is in scope",
    "references/standing-doc-provenance.md": "standing-doc provenance finding or policy review",
    "references/unit-test-quality.md": "unit test body quality or fixture/assertion review",
}


def _skill_paths_under(repo_root: Path, parents: list[Path]) -> list[str]:
    found: set[str] = set()
    for parent in parents:
        if not parent.is_dir():
            continue
        found.update(
            str(path.relative_to(repo_root))
            for path in sorted(parent.glob("*/SKILL.md"))
            if "generated" not in path.parts
        )
    return sorted(found)


def _skill_paths(repo_root: Path) -> list[str]:
    root_skills = _skill_paths_under(
        repo_root,
        [repo_root / "skills" / "public", repo_root / "skills" / "support"],
    )
    if root_skills:
        return root_skills
    plugin_skill_parents = []
    plugins_root = repo_root / "plugins"
    if plugins_root.is_dir():
        plugin_skill_parents = sorted(path / "skills" for path in plugins_root.iterdir() if (path / "skills").is_dir())
    return _skill_paths_under(repo_root, plugin_skill_parents)


def build_plan(repo_root: Path) -> dict[str, Any]:
    skills = _skill_paths(repo_root)
    skills_in_scope = bool(skills)
    required_refs = [*BASE_PRIMER_REFS, *(SKILL_PRIMER_REFS if skills_in_scope else [])]
    return {
        "schema_version": "quality.run_plan.v1",
        "repo_root": str(repo_root),
        "skills_in_scope": skills_in_scope,
        "skill_scope_reason": (
            f"found {len(skills)} checked-in skill package(s)" if skills else "no skills/public or skills/support SKILL.md files found"
        ),
        "sample_skill_paths": skills[:8],
        "required_primer_refs": required_refs,
        "gate_plan": "report_first",
        "next_action": "read_primer_refs",
        "phase_barriers": [
            "Read required_primer_refs before broad gates.",
            "Run deterministic gates as a report, then analyze the report against the primer refs before fixing.",
            "Open on-demand refs only when a concrete gate, inventory, source, or operator finding matches their trigger.",
        ],
        "on_demand_trigger_map": ON_DEMAND_TRIGGERS,
    }


def format_human(plan: dict[str, Any]) -> str:
    lines = [
        "Quality run plan:",
        f"- next_action: {plan['next_action']}",
        f"- skills_in_scope: {str(plan['skills_in_scope']).lower()} ({plan['skill_scope_reason']})",
        f"- gate_plan: {plan['gate_plan']}",
        "- required_primer_refs:",
    ]
    lines.extend(f"  - {ref}" for ref in plan["required_primer_refs"])
    lines.append("- phase_barriers:")
    lines.extend(f"  - {barrier}" for barrier in plan["phase_barriers"])
    lines.append("- on_demand_triggers: open only from concrete findings")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    plan = build_plan(args.repo_root.resolve())
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_human(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
