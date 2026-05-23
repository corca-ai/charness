#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

SCHEMA_VERSION = "charness.quality.behavior_test_recommendation.v1"
CAUTILUS_REQUEST_SCHEMA = "cautilus.robustness_request.v1"
CAUTILUS_PLAN_SCHEMA = "cautilus.robustness_plan.v1"
CAUTILUS_REPORT_SCHEMA = "cautilus.robustness_report.v1"
EXPECTED_RELATIONS = ("preserve_behavior", "surface_failure", "recover", "clarify", "refuse")
RELATION_STATUSES = ("satisfied", "violated", "blocked", "invalid", "inconclusive")
MUTATION_KINDS = ("stimulus", "implementation")
STATES = ("recommend_only", "executed", "blocked", "unavailable")


def _split_values(values: list[str]) -> list[str]:
    parsed: list[str] = []
    for value in values:
        parsed.extend(part.strip() for part in value.split(",") if part.strip())
    return parsed


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    mutation_kinds = _split_values(args.mutation_kind) or ["stimulus"]
    source_refs = _split_values(args.source_evidence_ref)
    limitations = _split_values(args.limitation)
    if not limitations and args.state == "recommend_only":
        limitations = ["recommend-only: no live Cautilus run was requested or executed"]
    payload: dict[str, object] = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "state": args.state,
        "behaviorSeam": args.behavior_seam,
        "deterministicProofGap": args.deterministic_gap,
        "cautilusContract": {
            "requestSchema": CAUTILUS_REQUEST_SCHEMA,
            "planSchema": CAUTILUS_PLAN_SCHEMA,
            "reportSchema": CAUTILUS_REPORT_SCHEMA,
            "expectedRelations": list(EXPECTED_RELATIONS),
            "relationStatuses": list(RELATION_STATUSES),
        },
        "suggestedRequest": {
            "schemaVersion": CAUTILUS_REQUEST_SCHEMA,
            "subjectRef": args.subject_ref,
            "intent": args.intent,
            "riskFocus": args.risk_focus,
            "sourceEvidenceRefs": source_refs,
            "requestedMutationKinds": mutation_kinds,
            "limitations": limitations,
        },
        "expectedResultFields": [
            "planRef",
            "subjectRef",
            "intentProfile",
            "summary.countsByRelationStatus",
            "caseResults.caseId",
            "caseResults.expectedRelation",
            "caseResults.observedRelation",
            "caseResults.relationStatus",
            "caseResults.reasonCodes",
            "caseResults.limitations",
            "recommendation",
            "nextActions",
        ],
    }
    if args.report_ref:
        payload["executedReportRef"] = args.report_ref
    return payload


def render_markdown(payload: dict[str, object]) -> str:
    request = payload["suggestedRequest"]
    assert isinstance(request, dict)
    contract = payload["cautilusContract"]
    assert isinstance(contract, dict)
    source_refs = request.get("sourceEvidenceRefs") or []
    mutation_kinds = request.get("requestedMutationKinds") or []
    return "\n".join(
        [
            f"- active NON_AUTOMATABLE: recommend Cautilus robustness proof for `{payload['behaviorSeam']}`.",
            f"  - state: `{payload['state']}`",
            f"  - deterministic gap: {payload['deterministicProofGap']}",
            f"  - Cautilus request: `{contract['requestSchema']}`",
            f"  - Cautilus report: `{contract['reportSchema']}`",
            f"  - subject: `{request['subjectRef']}`",
            f"  - risk focus: {request['riskFocus']}",
            f"  - mutation kinds: {', '.join(mutation_kinds) if mutation_kinds else 'none'}",
            f"  - source evidence: {', '.join(source_refs) if source_refs else 'missing'}",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit a Charness quality behavior-test recommendation using the Cautilus robustness contract."
    )
    parser.add_argument("--behavior-seam", required=True, help="Behavior seam under test (free-form identifier for the operator-visible contract)")
    parser.add_argument("--subject-ref", required=True, help="Cautilus subjectRef value pointing at the artifact being probed")
    parser.add_argument("--intent", default="operator_behavior", help="Intent profile passed to Cautilus (e.g. operator_behavior)")
    parser.add_argument("--risk-focus", required=True, help="Short label describing the risk this robustness probe should stress")
    parser.add_argument("--deterministic-gap", required=True, help="Reason the deterministic gate alone cannot prove this seam")
    parser.add_argument("--source-evidence-ref", action="append", default=[], help="Evidence reference supporting the recommendation (repeatable; commas accepted)")
    parser.add_argument("--mutation-kind", action="append", choices=MUTATION_KINDS, default=[], help="Mutation kinds requested from Cautilus (repeatable; defaults to stimulus)")
    parser.add_argument("--limitation", action="append", default=[], help="Known limitation to record on the recommendation (repeatable)")
    parser.add_argument("--state", choices=STATES, default="recommend_only", help="Lifecycle state of the recommendation (recommend_only, executed, blocked, unavailable)")
    parser.add_argument("--report-ref", help="Required when --state executed; points to the Cautilus report.")
    parser.add_argument("--markdown", action="store_true", help="Render the recommendation as a markdown bullet instead of JSON")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.state == "executed" and not args.report_ref:
        parser.error("--state executed requires --report-ref")
    payload = build_payload(args)
    if args.markdown:
        print(render_markdown(payload))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
