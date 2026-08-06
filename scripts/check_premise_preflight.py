#!/usr/bin/env python3
"""Run the offline implementation-premise preflight and persist its decision."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
_preflight = import_repo_module(__file__, "scripts.premise_preflight_lib")
PremiseError = _preflight.PremiseError
run_preflight = _preflight.run_preflight


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare a captured issue-tool readback and declared git tree identity "
            "before implementation. Offline only; provider freshness and runtime behavior "
            "are not claimed."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--premise", type=Path, required=True, help="Candidate premise JSON inside the repository.")
    parser.add_argument("--issue-readback", type=Path, required=True, help="Captured issue_tool.py read JSON inside the repository.")
    parser.add_argument("--decision-log", help="Optional repo-relative JSONL path overriding premise.decision_log.")
    parser.add_argument("--json", action="store_true", help="Emit stable machine-readable JSON.")
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    try:
        result = run_preflight(
            repo_root,
            args.premise.resolve(),
            args.issue_readback.resolve(),
            decision_log=args.decision_log,
        )
    except PremiseError as exc:
        result = {
            "status": "refused",
            "exit_code": 2,
            "persisted": False,
            "non_claim": _preflight.NON_CLAIM,
            "error": exc.as_dict(),
        }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif result["status"] == "accepted":
        print(f"premise-preflight: ACCEPTED decision_log={result['decision_log']}")
    else:
        detail = result.get("error") or {"reason_codes": result["decision"]["reason_codes"]}
        print(f"premise-preflight: REFUSED {json.dumps(detail, ensure_ascii=False, sort_keys=True)}", file=sys.stderr)
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
