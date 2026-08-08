#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
goal_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_lib")
goal_cli = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_cli_args")
head_freshness = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_head_freshness")
adapter_policy = SKILL_RUNTIME.load_local_skill_module(__file__, "achieve_adapter_policy")
# The proof-mismatch floor is a portable top-level module (reused by issue
# closeout); loaded via the repo-module path so its `from scripts.` imports resolve.
proof_mismatch = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.proof_mismatch")
phase_brief_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_phase_brief")


def _attach_phase_brief(payload: dict, status: str | None) -> None:
    """Advisory routing only: names which reference section covers this phase."""
    brief = phase_brief_lib.phase_brief(status)
    if brief is not None:
        payload["phase_brief"] = brief


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check that a goal artifact keeps the required sections, status, and activation line.")
    goal_cli.add_goal_target_args(parser)
    parser.add_argument(
        "--pursue-ready",
        action="store_true",
        help="Instead of the full section/status check, report whether the goal is shaped "
        "enough to pursue via `/goal`. Exit 1 when unshaped.",
    )
    return parser.parse_args()


def _refusal_bits(entries, label: str, render, *, joiner: str = ", ") -> list[str]:
    """``["<label>: a, b"]`` for a non-empty refusal set, else ``[]``.

    Every refusal category in this renderer is the same shape -- name the set, join
    its entries -- and writing that shape out per category is what let a NEW
    category (`stub_evidence`) ship with no branch at all, refusing the flip with
    an empty tail. One home makes adding a category one line.
    """
    entries = entries or []
    if not entries:
        return []
    return [label + ": " + joiner.join(render(entry) for entry in entries)]


def _stub_evidence_bits(evidence_report: dict) -> list[str]:
    """The stub-evidence refusal: present and non-empty, so no other set names it."""
    return _refusal_bits(
        evidence_report.get("stub_evidence"),
        "stub evidence",
        lambda entry: f"{entry['name']} ({entry['detail']})",
    )


def _evidence_missing_bits(evidence_report: dict) -> list[str]:
    """Human-facing reasons the After-phase evidence gate refused the flip.

    Surfaces each rung's own reason (including the disposition-form rung 1c and the
    recurrence-lineage rung 1d) so the CLI message is actionable, not just the JSON
    report. Extracted from ``main`` to keep its cyclomatic complexity in budget.
    """
    bits: list[str] = []
    bits += _refusal_bits(evidence_report["missing"], "missing", str)
    bits += _refusal_bits(
        evidence_report["missing_evidence_files"], "missing files", lambda e: e["name"]
    )
    bits += _stub_evidence_bits(evidence_report)
    bits += _refusal_bits(
        evidence_report["invalid_skips"],
        "invalid skips",
        lambda e: f"{e['name']} ({e['detail']})" if e.get("detail") else e["name"],
    )
    bits += _refusal_bits(
        evidence_report.get("binding_failures"),
        "evidence not bound to this goal",
        lambda e: e["name"],
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
    # Guarded on `applies and not ok`, not on `reason` truthiness: this floor
    # carries a reason when it PASSES too (`queue disposition recorded`) and when
    # it is grandfathered off, so the old truthiness guard put a passing floor's
    # text into the refusal message for every in-scope goal — noise that reads as
    # the cause of a refusal it had nothing to do with.
    _queue = evidence_report.get("operator_decision_queue", {})
    if _queue.get("applies") and not _queue.get("ok", True):
        bits.append("operator-decision-queue floor: " + _queue.get("reason", ""))
    # Guarded on `applies and not ok`, NOT on `reason` truthiness: the
    # grandfathered payload always carries a reason, so a truthiness guard would
    # append a PASSING floor's text. That is the shape round 1 caught one line
    # down — an in-scope distinctness refusal emitted only the operator-queue
    # floor's `queue disposition recorded`, naming a floor that passed as the
    # reason for a refusal.
    for _floor_key, _floor_label in (
        ("closeout_evidence_distinctness", "closeout-evidence distinctness"),
        ("final_verification_figure_form", "final-verification figure form"),
    ):
        _floor = evidence_report.get(_floor_key, {})
        if _floor.get("applies") and not _floor.get("ok", True):
            bits.append(f"{_floor_label}: {_floor.get('reason', 'refused with no reason recorded')}")
    if evidence_report.get("invalid_early_close_reports"):
        bits.append(
            "early-close report shape: "
            + "; ".join(
                f"{failure['section']} ({failure['reason']})"
                for entry in evidence_report["invalid_early_close_reports"]
                for failure in entry.get("failures", [])
            )
        )
    return bits


def main() -> int:
    args = parse_args()
    path = goal_cli.resolve_goal_path(args, goal_lib)
    if not path.exists():
        print(json.dumps({"ok": False, "issues": [f"goal artifact not found: {path}"]}, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    text = path.read_text(encoding="utf-8")
    if args.pursue_ready:
        # The pre-activation discussion gate's deploy vocabulary is adapter-provided
        # (consumer-axis), not a charness hardcode; absent adapter -> English default.
        deploy_vocab = adapter_policy.resolve_discussion_deploy_vocab(args.repo_root.expanduser().resolve()) or None
        report = goal_lib.pursue_readiness(text, deploy_vocab=deploy_vocab)
        report["path"] = str(path)
        _attach_phase_brief(report, goal_lib.read_status(text))
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if report["pursue_ready"] else 1
    result = goal_lib.check_goal(text)
    result["path"] = str(path)
    _attach_phase_brief(result, result.get("status"))
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
        # Non-blocking, and deliberately hoisted OUT of the refusal renderer. The
        # opt-out census matters most on goals that PASS — every floor satisfied,
        # each by an opt-out — and `_evidence_missing_bits` only runs when the
        # evidence gate REFUSES. Left there it would have been invisible on exactly
        # the runs it was built for.
        aggregate = evidence_report.get("coordination_optout_aggregate")
        if isinstance(aggregate, dict) and aggregate.get("reason"):
            result.setdefault("advisories", []).append(
                "coordination opt-out census — " + aggregate["reason"]
            )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
