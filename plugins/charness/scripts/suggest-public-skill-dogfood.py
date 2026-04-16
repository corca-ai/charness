#!/usr/bin/env python3
# ruff: noqa: E402, I001

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.public_skill_validation_lib import (
    load_policy,
    public_skill_ids,
    validate_policy,
)


REPO_SHAPE_HINTS = {
    "announcement": "repo with recent checked-in changes and one clear delivery context such as release notes or a team update",
    "create-cli": "tooling repo where ad hoc shell or Python entrypoints already exist and the command surface needs to be normalized",
    "create-skill": "skills repo with adjacent public/support surfaces, references, and packaging constraints already present",
    "debug": "active repo slice with a reproducible failure, existing logs or tests, and enough local state to preserve a durable debug artifact",
    "find-skills": "repo with multiple public and support skills where the user names a capability instead of a file path",
    "gather": "repo that already keeps gathered artifacts and a source identity that may need refresh-in-place behavior",
    "handoff": "mature repo with an existing handoff artifact and enough adjacent state that the next pickup path can be ambiguous",
    "hitl": "repo with a bounded review target and a decision that must stay explicitly human-owned",
    "ideation": "minimal or loosely defined repo context where the request is still concept-shaping rather than implementation-ready",
    "impl": "repo with an active build slice, existing code or config surfaces, and at least one verification path",
    "init-repo": "partially initialized mature repo with divergent but valid naming and intentionally missing optional surfaces",
    "narrative": "repo with existing source-of-truth docs that drift from the current product or project story",
    "premortem": "repo with a non-trivial pending decision whose main risk is choosing the wrong plan too early",
    "quality": "mature repo with standing local gates, some drift or fragility, and at least one final stop-before-finish command",
    "release": "repo with checked-in version or packaging surfaces and a maintainer-facing release workflow",
    "retro": "repo that just completed a meaningful slice or exposed a missed issue that should feed repeat-trap memory",
    "spec": "repo with an under-specified change request and enough current docs or code to refine a build contract",
}

PROMPT_HINTS = {
    "announcement": "Summarize the latest repo changes into a chat-ready update and keep the draft scoped to what changed.",
    "create-cli": "We keep adding ad hoc scripts here; normalize this into one repo-owned CLI before the command surface sprawls further.",
    "create-skill": "Improve this skill package first so the trigger, references, and helper surface stay portable.",
    "debug": "Investigate this regression and leave a durable record of what actually failed before changing code.",
    "find-skills": "Which skill should handle this named capability, and what existing support surface already covers it?",
    "gather": "Fetch this external source into a durable local artifact instead of giving me a one-turn summary.",
    "handoff": "Use docs/handoff.md as the pickup surface and continue the next highest-leverage workflow from there.",
    "hitl": "Set up a bounded human review loop for this target so the agent does not auto-decide the final judgment.",
    "ideation": "The concept is still fuzzy; help shape the workflow before we commit to a spec or implementation.",
    "impl": "Implement the smallest meaningful slice now and verify it against the current repo contract.",
    "init-repo": "Normalize this partially initialized repo without pretending it needs a greenfield rewrite.",
    "narrative": "Tighten the repo's durable story first, then derive one concise brief from that source of truth.",
    "premortem": "Stress this pending decision before we lock it in and separate real blockers from over-worry.",
    "quality": "Review the current quality posture and install the next deterministic gate if the move is obvious.",
    "release": "Verify and advance the checked-in release surface without hand-editing generated packaging artifacts.",
    "retro": "Run a short retro on this slice and persist the repeat trap if the workflow should have caught it.",
    "spec": "Turn this vague request into a living implementation contract before code changes spread.",
}

EVIDENCE_OVERRIDES = {
    "create-skill": [
        "treats the public skill frontmatter and core trigger as classifier input, not only documentation",
        "keeps `SKILL.md` as selection/sequence core and pushes bulky nuance into references or scripts",
    ],
    "find-skills": [
        "uses the named skill or capability lookup path before falling back to broad filesystem search",
    ],
    "handoff": [
        "reads the current workflow trigger before broad repo exploration and keeps the baton pass continuation-first",
    ],
    "quality": [
        "runs or names the existing repo-owned quality gates before proposing new ones",
        "uses one realistic consumer prompt when the risk is public-skill routing or artifact behavior",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--skill-id", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _load_frontmatter(skill_path: Path) -> dict[str, str]:
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def _resolve_artifact(repo_root: Path, skill_id: str) -> str | None:
    resolve_script = repo_root / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py"
    if not resolve_script.is_file():
        return None
    result = subprocess.run(
        ["python3", str(resolve_script), "--repo-root", str(repo_root)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    payload = json.loads(result.stdout)
    artifact_path = payload.get("artifact_path")
    if isinstance(artifact_path, str) and artifact_path:
        return artifact_path
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    for key in ("summary_path", "output_dir", "state_dir"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _index_partition(partition: dict[str, list[str]]) -> dict[str, str]:
    indexed: dict[str, str] = {}
    for label, skill_ids in partition.items():
        for skill_id in skill_ids:
            indexed[skill_id] = label
    return indexed


def _acceptance_evidence(
    skill_id: str,
    *,
    expected_artifact: str | None,
    tier: str,
    adapter_requirement: str,
) -> list[str]:
    evidence = [
        f"routes the prompt to `{skill_id}` instead of an adjacent public skill",
    ]
    if expected_artifact is not None:
        evidence.append(
            f"names or refreshes `{expected_artifact}` when the skill persists durable state"
        )
    elif adapter_requirement == "adapter-free":
        evidence.append(
            "does not invent host-specific adapter state when repo inspection alone should be enough"
        )
    if tier == "evaluator-required":
        evidence.append(
            "handles the skill's load-bearing contract without needing the user to restate obvious repo context"
        )
    else:
        evidence.append(
            "produces an output that a maintainer could review directly without re-deriving the whole request"
        )
    evidence.extend(EVIDENCE_OVERRIDES.get(skill_id, []))
    return evidence


def build_matrix(repo_root: Path, skill_ids: list[str]) -> dict[str, object]:
    policy = validate_policy(load_policy(repo_root), repo_root)
    tier_by_skill = _index_partition(policy["tiers"])
    adapter_by_skill = _index_partition(policy["adapter_requirements"])

    matrix: list[dict[str, object]] = []
    for skill_id in skill_ids:
        skill_path = repo_root / "skills" / "public" / skill_id / "SKILL.md"
        frontmatter = _load_frontmatter(skill_path)
        expected_artifact = _resolve_artifact(repo_root, skill_id)
        tier = tier_by_skill[skill_id]
        adapter_requirement = adapter_by_skill[skill_id]
        matrix.append(
            {
                "skill_id": skill_id,
                "description": frontmatter.get("description", ""),
                "prompt": PROMPT_HINTS.get(skill_id, frontmatter.get("description", "")),
                "repo_shape": REPO_SHAPE_HINTS.get(
                    skill_id,
                    "repo shape not yet classified; add a concrete mature or cold-start fixture before relying on this row",
                ),
                "expected_skill": skill_id,
                "expected_artifact": expected_artifact,
                "validation_tier": tier,
                "adapter_requirement": adapter_requirement,
                "acceptance_evidence": _acceptance_evidence(
                    skill_id,
                    expected_artifact=expected_artifact,
                    tier=tier,
                    adapter_requirement=adapter_requirement,
                ),
            }
        )
    return {
        "schema_version": 1,
        "repo_root": str(repo_root),
        "matrix": matrix,
    }


def format_human(report: dict[str, object]) -> str:
    lines = ["Public skill consumer dogfood matrix:"]
    for row in report["matrix"]:
        assert isinstance(row, dict)
        lines.append(
            f"- `{row['skill_id']}`: prompt={row['prompt']} repo_shape={row['repo_shape']}"
        )
        artifact = row["expected_artifact"] or "none"
        lines.append(
            f"  expected_skill=`{row['expected_skill']}` artifact=`{artifact}` "
            f"tier=`{row['validation_tier']}` adapter=`{row['adapter_requirement']}`"
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    all_skill_ids = public_skill_ids(repo_root)
    requested = args.skill_id or all_skill_ids
    unknown = sorted(set(requested) - set(all_skill_ids))
    if unknown:
        rendered = ", ".join(f"`{skill_id}`" for skill_id in unknown)
        print(f"Unknown public skill id(s): {rendered}", file=sys.stderr)
        return 1

    report = build_matrix(repo_root, requested)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_human(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
