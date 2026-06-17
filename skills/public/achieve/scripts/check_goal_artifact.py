#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from datetime import date as date_cls
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
goal_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_lib")
head_freshness = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_head_freshness")
# The proof-mismatch floor is a portable top-level module (reused by issue
# closeout); loaded via the repo-module path so its `from scripts.` imports resolve.
proof_mismatch = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.proof_mismatch")


def _resolve_goal_path(args) -> Path:
    repo_root = args.repo_root.expanduser().resolve()
    if args.goal_path is not None:
        return args.goal_path.expanduser().resolve()
    if not (args.slug and args.date):
        raise SystemExit("provide --goal-path, or both --slug and --date")
    try:
        return goal_lib.goal_path(repo_root, args.date, args.slug)
    except ValueError as exc:
        raise SystemExit(str(exc))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check that a goal artifact keeps the required sections, status, and activation line.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root that owns charness-artifacts/goals/")
    parser.add_argument("--goal-path", type=Path, help="Explicit path to the goal artifact (overrides --slug/--date)")
    parser.add_argument("--slug", help="Goal slug, used with --date to locate the artifact")
    parser.add_argument("--date", default=date_cls.today().isoformat(), help="Goal date prefix YYYY-MM-DD used with --slug")
    parser.add_argument(
        "--pursue-ready",
        action="store_true",
        help="Instead of the full section/status check, report whether the goal is shaped "
        "enough to pursue via `/goal`. Exit 1 when unshaped.",
    )
    return parser.parse_args()


def _evidence_missing_bits(evidence_report: dict) -> list[str]:
    """Human-facing reasons the After-phase evidence gate refused the flip.

    Surfaces each rung's own reason (including the disposition-form rung 1c and the
    recurrence-lineage rung 1d) so the CLI message is actionable, not just the JSON
    report. Extracted from ``main`` to keep its cyclomatic complexity in budget.
    """
    bits: list[str] = []
    if evidence_report["missing"]:
        bits.append("missing: " + ", ".join(evidence_report["missing"]))
    if evidence_report["missing_evidence_files"]:
        bits.append(
            "missing files: "
            + ", ".join(entry["name"] for entry in evidence_report["missing_evidence_files"])
        )
    if evidence_report["invalid_skips"]:
        bits.append(
            "invalid skips: " + ", ".join(entry["name"] for entry in evidence_report["invalid_skips"])
        )
    if evidence_report.get("binding_failures"):
        bits.append(
            "evidence not bound to this goal: "
            + ", ".join(entry["name"] for entry in evidence_report["binding_failures"])
        )
    if evidence_report.get("disposition_blank"):
        bits.append(
            "improvement-disposition gate: cited retro lists improvements but "
            "## Auto-Retro is blank and no opt-out is recorded"
        )
    if evidence_report.get("disposition_form"):
        bits.append("disposition form: " + evidence_report["disposition_form"]["reason"])
    if evidence_report.get("recurrence_lineage"):
        bits.append("recurrence-lineage floor: " + evidence_report["recurrence_lineage"]["reason"])
    if evidence_report.get("residual_ledger", {}).get("reason"):
        bits.append("residual-ledger floor: " + evidence_report["residual_ledger"]["reason"])
    if evidence_report.get("proof_mismatch", {}).get("reason"):
        bits.append("proof-mismatch floor: " + evidence_report["proof_mismatch"]["reason"])
    if evidence_report.get("coordination_missing"):
        bits.append(
            "coordination floors: "
            + "; ".join(f"{entry['floor']} step missing" for entry in evidence_report["coordination_missing"])
        )
    if evidence_report.get("closeout_delegation", {}).get("failures"):
        bits.append("closeout delegation: " + "; ".join(evidence_report["closeout_delegation"]["failures"]))
    if evidence_report.get("section_placeholders"):
        bits.append(
            "section placeholders: "
            + ", ".join(
                f"{entry['section']} line {entry['line']} starts with {entry['marker']!r}"
                for entry in evidence_report["section_placeholders"]
            )
        )
    if evidence_report.get("operator_decision_queue", {}).get("reason"):
        bits.append(
            "operator-decision-queue floor: "
            + evidence_report["operator_decision_queue"]["reason"]
        )
    return bits


def main() -> int:
    args = parse_args()
    path = _resolve_goal_path(args)
    if not path.exists():
        print(json.dumps({"ok": False, "issues": [f"goal artifact not found: {path}"]}, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    text = path.read_text(encoding="utf-8")
    if args.pursue_ready:
        report = goal_lib.pursue_readiness(text)
        report["path"] = str(path)
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if report["pursue_ready"] else 1
    result = goal_lib.check_goal(text)
    result["path"] = str(path)
    freshness_report = head_freshness.check_head_freshness(
        text,
        head_sha=head_freshness.current_head(args.repo_root.expanduser().resolve()),
    )
    result["head_freshness"] = freshness_report
    if not freshness_report["ok"]:
        result["ok"] = False
        lines = ", ".join(str(entry["line"]) for entry in freshness_report["findings"])
        result["issues"].append(
            "mutable HEAD freshness: current-HEAD wording names stale SHA(s) on line(s) "
            + lines
            + "; use `HEAD` in the live command or mark the SHA as historical/proof-targeted"
        )
    if result.get("status") == "blocked":
        matrix_report = goal_lib.check_blocked_matrix(text)
        result["blocked_matrix"] = matrix_report
        if matrix_report.get("applies") and not matrix_report["ok"]:
            result["ok"] = False
            result["issues"].append("remaining-boundary-matrix floor — " + matrix_report["reason"])
    if result.get("status") == "complete":
        repo_root = args.repo_root.expanduser().resolve()
        evidence_report = goal_lib.check_complete_evidence(repo_root, text)
        proof_mismatch.apply_proof_mismatch_floor(evidence_report, repo_root, text)
        timebox_report = goal_lib.check_timebox_closeout(text)
        result["closeout_evidence"] = evidence_report
        result["timebox_closeout"] = timebox_report
        if not timebox_report["ok"]:
            result["ok"] = False
            result["issues"].append(
                "timebox closeout not satisfied — "
                + "; ".join(timebox_report["issues"])
            )
        if not evidence_report["ok"]:
            result["ok"] = False
            result["issues"].append(
                "After-phase prescribed-skill evidence not satisfied — "
                + "; ".join(_evidence_missing_bits(evidence_report))
            )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
