#!/usr/bin/env python3
"""Run the offline implementation-premise preflight and persist its decision."""

from __future__ import annotations

import argparse
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)
_preflight = import_repo_module(__file__, "scripts.premise.premise_preflight_lib")
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
    # The deleted human renderer surfaced the refusal REASON CODES even when the
    # refusal came from the decision (not from a PremiseError). Output is
    # unconditionally YAML now, so that detail is lifted onto the payload rather
    # than left buried one level down in a branch nobody prints.
    if result["status"] != "accepted" and "error" not in result:
        result = {**result, "refusal_detail": {"reason_codes": result["decision"]["reason_codes"]}}
    emit_yaml(result)
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
