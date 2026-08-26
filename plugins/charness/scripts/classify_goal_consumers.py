#!/usr/bin/env python3
"""Census old goal-identity consumers and route each row to its owner.

This is an inventory gate, not a semantic proof.  It records every matching
line, including historical fixtures and generated mirrors, so removal work can
be scoped without guessing from a count.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

SCAN_ROOTS = ("README.md", ".agents", "docs", "scripts", "skills", "plugins", "tests")
TOKEN_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("goal-directory", re.compile(r"charness-artifacts/goals")),
    ("goal-path", re.compile(r"\bgoal_path\b")),
    ("local-active-status", re.compile(r"Status:\s+(?:active|blocked|complete)\b")),
    ("slice-log-writer", re.compile(r"\bappend_slice_log\b")),
    ("at-file-activation", re.compile(r"/goal\s+@")),
    ("running-memory", re.compile(r"running[- ]memory|single durable|living scratchpad")),
    ("goal-template", re.compile(r"\bgoal_artifact_template\b")),
    ("auto-draft-goal", re.compile(r"\bauto_draft_goal\b")),
    ("draft-goal-from-chunk", re.compile(r"\bdraft_goal_from_chunk\b")),
    ("chunked-routing-auto-draft", re.compile(r"\bchunked_routing_auto_draft\b")),
)
_HISTORICAL_MARKERS = (
    "test_goal_artifact",
    "test_handoff_chunker",
    "test_goal_coordination_floors",
    "coverage_debt/",
    "goal-artifact.md",
    "handoff-chunked-routing.md",
    "docs/deferred-decisions.md",
    "docs/prompt-mutation-policy.md",
    "docs/public-skill-dogfood.json",
)
_HISTORICAL_PATH_PREFIXES = (
    "tests/fixtures/",
    "tests/quality_gates/fixtures/",
)
_HISTORICAL_PATHS = frozenset(
    {
        "docs/deferred-decisions.md",
        "docs/handoff-chunked-routing.md",
        "docs/prompt-mutation-policy.md",
        "docs/public-skill-dogfood.json",
        "scripts/generate_prompt_mutants.py",
        "scripts/prompt_mutant_lib.py",
        "scripts/score_prompt_mutation_survival.py",
        "scripts/score_prompt_mutation_survival_lib.py",
        "scripts/witness_coverage.py",
        "scripts/witness_coverage_lib.py",
        "skills/public/achieve/scripts/audit_disposition_corpus.py",
    }
)
_DRAFT_PROVENANCE_PATHS = frozenset(
    {
        "scripts/check_artifact_referents.py",
        "scripts/check_artifact_surface_preflight.py",
        "scripts/check_docs_graph.py",
        "scripts/check_spec_evidence_durability.py",
        "scripts/closeout_bundle.py",
        "scripts/final_bundle_preflight_evidence.py",
        "scripts/host_log_probe_lib.py",
        "scripts/premise_preflight_lib.py",
        "scripts/retro_persistence_lib.py",
        "scripts/setup_commit_discipline_lib.py",
        "scripts/slice_manifest_lib.py",
        "scripts/validate_retro_handoff_wiring.py",
        "scripts/validate_slice_manifest.py",
        "skills/public/achieve/adapter.example.yaml",
        "skills/public/achieve/scripts/achieve_adapter_policy.py",
        "skills/public/achieve/scripts/goal_artifact_backlog.py",
        "skills/public/achieve/scripts/goal_artifact_floor_grammar.py",
        "skills/public/achieve/scripts/goal_artifact_lib.py",
        "skills/public/achieve/scripts/goal_artifact_naming.py",
        "skills/public/achieve/scripts/goal_artifact_superseded.py",
        "skills/public/achieve/scripts/init_adapter.py",
        "skills/public/achieve/scripts/record_metric_window.py",
        "skills/public/achieve/scripts/scaffold_goal_specs.py",
        "skills/public/release/scripts/claims_review_scope.py",
        "skills/public/release/scripts/release_closeout_floors.py",
        "skills/public/retro/scripts/persist_retro_artifact.py",
        "skills/public/retro/scripts/probe_host_logs.py",
    }
)
_DRAFT_PROVENANCE_TOKENS = frozenset({"goal-directory", "goal-path", "goal-template"})
_TARGET_TESTS = (
    "test_achieve_goal_run_pickup.py",
    "test_goal_binding_v1.py",
    "test_goal_evidence_lineage.py",
    "test_issue_goal_run.py",
)
_EXCLUDED = {"scripts/classify_goal_consumers.py"}


def _emit_yaml(payload: dict[str, Any]) -> None:
    """Render command output through the repository's portable YAML helper."""
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        helper = ancestor / "scripts" / "yaml_output.py"
        if not helper.is_file():
            continue
        spec = importlib.util.spec_from_file_location("charness_census_yaml_output", helper)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.emit_yaml(payload)
        return
    raise RuntimeError("scripts/yaml_output.py not found above classify_goal_consumers.py")


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _pair_path(repo_root: Path, relative: str) -> str | None:
    if relative.startswith("plugins/charness/skills/"):
        return "skills/public/" + relative.removeprefix("plugins/charness/skills/")
    if relative.startswith("plugins/charness/shared/"):
        return "skills/shared/" + relative.removeprefix("plugins/charness/shared/")
    if relative.startswith("plugins/charness/scripts/"):
        return "scripts/" + relative.removeprefix("plugins/charness/scripts/")
    return None


def _owner(relative: str) -> str:
    if relative.startswith("plugins/"):
        return "generated-mirror"
    if relative.startswith(("skills/public/achieve/", "skills/public/achieve")):
        return "achieve-orchestration"
    if relative.startswith("skills/public/issue/"):
        return "goal-run-provider"
    if relative.startswith(("scripts/", "skills/public/retro/", "skills/public/critique/", "skills/public/prove/", "skills/public/release/", "skills/public/quality/", "skills/shared/")):
        return "goal-evidence-lineage"
    if relative.startswith("skills/public/handoff/"):
        return "goal-binding-v1"
    if relative.startswith(("docs/", ".agents/", "README.md")):
        return "achieve-orchestration"
    if relative.startswith("tests/"):
        return "historical-fixture"
    return "unassigned"


def _classification(relative: str, token: str) -> tuple[str, str]:
    if relative.startswith("plugins/"):
        return "generated-mirror", "generated placement is classified through its canonical source owner"
    if relative.startswith("tests/") and any(relative.endswith(name) for name in _TARGET_TESTS):
        return "goal-run-identity", "focused fixture exercises the current draft, binding, or Goal Run identity contract"
    if relative.startswith(_HISTORICAL_PATH_PREFIXES) or relative in _HISTORICAL_PATHS:
        return "historical-fixture", "retained corpus or historical surface preserves the retired path without execution authority"
    if any(marker in relative for marker in _HISTORICAL_MARKERS):
        return "historical-fixture", "fixture or historical documentation preserves the retired path for regression context"
    if relative.startswith("tests/") and relative.endswith(".py"):
        return "historical-fixture", "test fixture preserves a legacy artifact or activation shape while the runtime cutover removes its authority"
    if relative.startswith(".agents/") and token == "goal-directory":
        return "draft-provenance", "adapter or surface configuration names the repository artifact directory, not an execution state"
    if relative in _DRAFT_PROVENANCE_PATHS and token in _DRAFT_PROVENANCE_TOKENS:
        return "draft-provenance", "the path names immutable Goal Draft provenance or its planning-only evidence input, not execution state"
    if token in {"goal-directory", "goal-path"} and relative in {
        ".agents/achieve-adapter.yaml",
        "scripts/goal_lineage.py",
        "skills/public/achieve/scripts/goal_run_pickup.py",
        "skills/public/achieve/scripts/goal_run_pickup_contract.py",
    }:
        return "goal-run-identity", "the path is planning provenance or an issue-native identity input, not execution state"
    if relative.startswith("skills/public/issue/"):
        return "provider-truth", "the issue provider owns current parent, child, and relationship state"
    return "defect", "active consumer still relies on a retired local-status, receipt, or @file execution path"


def _iter_files(repo_root: Path):
    for raw in SCAN_ROOTS:
        root = repo_root / raw
        if root.is_file():
            yield root
        elif root.is_dir():
            yield from (
                path
                for path in sorted(root.rglob("*"))
                if path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix.lower() not in {".pyc", ".pyo"}
            )


def classify(repo_root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in _iter_files(repo_root):
        relative = path.relative_to(repo_root).as_posix()
        if relative in _EXCLUDED:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            rows.append({"path": relative, "line": 0, "matched_token": "unreadable", "owning_child": "unassigned", "classification": "defect", "rationale": f"file could not be read: {exc}"})
            continue
        pair = _pair_path(repo_root, relative)
        for line_number, line in enumerate(text.splitlines(), 1):
            for token, pattern in TOKEN_RULES:
                if pattern.search(line) is None:
                    continue
                classification, rationale = _classification(relative, token)
                row = {
                    "path": relative,
                    "line": line_number,
                    "matched_token": token,
                    "owning_child": _owner(relative),
                    "classification": classification,
                    "rationale": rationale,
                }
                if pair is not None:
                    pair_path = repo_root / pair
                    row["source_generated_pair"] = {
                        "paired_path": pair,
                        "paired_exists": pair_path.is_file(),
                        "paired_sha256": _sha256(pair_path),
                        "observed_sha256": _sha256(path),
                    }
                rows.append(row)
    defects = [row for row in rows if row["classification"] == "defect" or row["owning_child"] == "unassigned"]
    return {
        "kind": "charness.goal-consumer-census/v1",
        "repo_root": str(repo_root),
        "scan_roots": list(SCAN_ROOTS),
        "rows": rows,
        "summary": {
            "matched_rows": len(rows),
            "defect_rows": len(defects),
            "unassigned_rows": sum(row["owning_child"] == "unassigned" for row in rows),
        },
        "ok": not defects,
        "non_claims": [
            "token census is not semantic proof that a remaining path is safe or unsafe",
            "historical-fixture classification preserves old behavior but does not make it a supported runtime path",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify Goal Draft and Goal Run consumers")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("json",), default="json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = classify(args.repo_root.resolve())
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        output = args.output if args.output.is_absolute() else args.repo_root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        _emit_yaml(payload)
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
