#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import date as date_cls
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
goal_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_lib")
head_freshness = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_head_freshness")


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
        "enough to pursue via `/goal` (#247). Exit 1 when unshaped.",
    )
    return parser.parse_args()


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
    if result.get("status") == "complete":
        evidence_report = goal_lib.check_complete_evidence(args.repo_root.expanduser().resolve(), text)
        result["closeout_evidence"] = evidence_report
        if not evidence_report["ok"]:
            result["ok"] = False
            missing_bits: list[str] = []
            if evidence_report["missing"]:
                missing_bits.append("missing: " + ", ".join(evidence_report["missing"]))
            if evidence_report["missing_evidence_files"]:
                missing_bits.append(
                    "missing files: "
                    + ", ".join(entry["name"] for entry in evidence_report["missing_evidence_files"])
                )
            if evidence_report["invalid_skips"]:
                missing_bits.append(
                    "invalid skips: "
                    + ", ".join(entry["name"] for entry in evidence_report["invalid_skips"])
                )
            if evidence_report.get("binding_failures"):
                missing_bits.append(
                    "evidence not bound to this goal: "
                    + ", ".join(
                        entry["name"] for entry in evidence_report["binding_failures"]
                    )
                )
            if evidence_report.get("disposition_blank"):
                missing_bits.append(
                    "improvement-disposition gate (#253): cited retro lists "
                    "improvements but ## Auto-Retro is blank and no opt-out is recorded"
                )
            if evidence_report.get("coordination_missing"):
                missing_bits.append(
                    "coordination floors: "
                    + "; ".join(
                        f"{entry['floor']} step missing"
                        for entry in evidence_report["coordination_missing"]
                    )
                )
            result["issues"].append(
                "After-phase prescribed-skill evidence not satisfied — "
                + "; ".join(missing_bits)
            )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
