from __future__ import annotations

import json
from pathlib import Path

from .test_quality_artifact import run_script


def seed_repo(tmp_path: Path, artifact_body: str | None) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "cautilus-adapters").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "skills" / "public" / "impl").mkdir(parents=True)
    (repo / "charness-artifacts" / "cautilus").mkdir(parents=True)
    (repo / "docs" / "public-skill-validation.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "tiers": {
                    "smoke-only": [],
                    "hitl-recommended": [],
                    "evaluator-required": ["impl"],
                },
                "adapter_requirements": {
                    "required": ["impl"],
                    "adapter-free": [],
                },
                "fallback_policy": {
                    "allow": ["impl"],
                    "visible": [],
                    "block": [],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "skills" / "public" / "impl" / "SKILL.md").write_text("# Impl\n", encoding="utf-8")
    (repo / ".agents" / "cautilus-adapters" / "chatbot-proposals.yaml").write_text("version: 1\n", encoding="utf-8")
    if artifact_body is not None:
        (repo / "charness-artifacts" / "cautilus" / "latest.md").write_text(artifact_body, encoding="utf-8")
    return repo


def write_diagnostic_finding(
    bundle: Path,
    *,
    title: str = "# Demo diagnostic",
    source: str = "## What ran",
    verdict: str = "## Verdict",
    interpretation: str = "## Diagnosis",
    interpretation_item: str = "- follow-up: https://github.com/corca-ai/charness/issues/398",
    extra_lines: list[str] | None = None,
) -> None:
    lines = [
        title,
        "",
        source,
        "",
        "- `/demo`",
        "",
        verdict,
        "",
        "- recommendation: reject",
        "",
        interpretation,
        "",
        interpretation_item,
        "",
    ]
    if extra_lines:
        lines.extend(extra_lines)
    (bundle / "finding.md").write_text("\n".join(lines), encoding="utf-8")


def write_summary_evidence(bundle: Path, payload: object | None = None) -> None:
    if payload is None:
        payload = {
            "schemaVersion": "cautilus.skill_evaluation_summary.v1",
            "recommendation": "reject",
            "evaluations": [{"status": "failed"}],
        }
    (bundle / "summary.v1.json").write_text(json.dumps(payload), encoding="utf-8")


def write_trace_digest(bundle: Path, records: list[dict] | None = None) -> None:
    if records is None:
        records = [
            {"step": 1, "track": "parent", "name": "Read", "args": "doc.md", "out_chars": 12, "wall_ms": None},
            {"step": 2, "track": "parent", "name": "Bash", "args": "ls", "out_chars": 4, "wall_ms": 100},
        ]
    (bundle / "trace-digest.jsonl").write_text(
        "".join(json.dumps(record) + "\n" for record in records), encoding="utf-8"
    )


def run_diagnostic_validator(repo: Path, *paths: str, all_bundles: bool = False):
    args = ["--repo-root", str(repo)]
    if all_bundles:
        args.append("--all")
    else:
        args.append("--paths")
        args.extend(paths)
    return run_script("scripts/validate_cautilus_diagnostics.py", *args)
