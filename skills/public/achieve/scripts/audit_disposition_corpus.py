#!/usr/bin/env python3
"""Corpus-discovery runner for the improvement-disposition gate (rung 1).

Calibration is **discovery, not "assert 0"**: run the real deterministic floor
(``check_complete_evidence``) over every completed goal artifact and report what
it would do, so a human can confirm:

- pre-rule goals (Created < the rule date) are grandfathered — 0 deterministic
  refusals (the gate does not retroactively punish goals shaped before it);
- the floor is **not inert** — in-scope goals that lack a bound
  ``Disposition review:`` line or carry a blank ``## Auto-Retro`` are surfaced
  (these are the cases a post-rule closeout must now satisfy).

Exit code is always 0 unless ``--fail-on-pre-rule-refusal`` is passed and a
*pre-rule* goal is refused (which would mean the grandfather leaked). The runner
never gates a closeout itself; it is a read-only audit/observation surface.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path

GOAL_DIR = "charness-artifacts/goals"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ce = _load("goal_artifact_closeout_evidence", "goal_artifact_closeout_evidence.py")
_disp = _load("goal_artifact_disposition", "goal_artifact_disposition.py")

_STATUS = re.compile(r"^Status:\s*(\S+)", re.MULTILINE)
_REVIEW_LINE = re.compile(
    r"^[\s>*-]*Disposition[- ]review\s*:", re.MULTILINE | re.IGNORECASE
)


def audit_goal(repo_root: Path, path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    status_match = _STATUS.search(text)
    status = status_match.group(1) if status_match else None
    report = _ce.check_complete_evidence(repo_root, text)
    scope = report.get("disposition_scope", {})
    return {
        "goal": path.name,
        "status": status,
        "created": scope.get("created"),
        "in_scope": scope.get("in_scope"),
        "auto_retro_blank": report.get("auto_retro_blank"),
        "retro_improvements_present": report.get("retro_improvements_present"),
        "has_disposition_review_line": bool(_REVIEW_LINE.search(_disp._mask_fences(text))),
        "rung1a_block_the_blank": "disposition_blank" in report,
        "disposition_optout": report.get("disposition_optout", {}).get("reason"),
        "evidence_ok": report["ok"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the goal corpus against the disposition floor.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--completed-only", action="store_true", help="Only audit goals with Status: complete")
    parser.add_argument("--fail-on-pre-rule-refusal", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    goals_dir = repo_root / GOAL_DIR
    rows = []
    for path in sorted(goals_dir.glob("*.md")):
        row = audit_goal(repo_root, path)
        if args.completed_only and row["status"] != "complete":
            continue
        rows.append(row)
    completed = [r for r in rows if r["status"] == "complete"]
    pre_rule = [r for r in completed if r["in_scope"] is False]
    in_scope = [r for r in completed if r["in_scope"] is True]
    pre_rule_refused = [r for r in pre_rule if r["rung1a_block_the_blank"]]
    in_scope_missing_review = [r for r in in_scope if not r["has_disposition_review_line"]]
    in_scope_blank = [r for r in in_scope if r["rung1a_block_the_blank"]]
    summary = {
        "completed_goals": len(completed),
        "pre_rule_grandfathered": len(pre_rule),
        "in_scope": len(in_scope),
        "pre_rule_rung1a_refusals": len(pre_rule_refused),
        "in_scope_blank_refusals": len(in_scope_blank),
        "in_scope_missing_disposition_review_line": [r["goal"] for r in in_scope_missing_review],
    }
    print(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2, sort_keys=True))
    if args.fail_on_pre_rule_refusal and pre_rule_refused:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
