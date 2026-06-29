#!/usr/bin/env python3

"""Durable validator for the per-eval OUTCOME assertion sets
(`evals/cautilus/*-claim-fidelity/outcome-assertions.json`) — the data the A/B harness
auto-grades through grade_skill_outcome.py.

Today only hitl ships a set; this gates every set that exists (and any future one)
against the grader's OWN schema, so a malformed assertion set is caught at the authoring
boundary instead of crashing a live grade mid-run. It shares the schema with the grader
(`grade_skill_outcome.validate_assertion_set`) so there is one definition of a
well-formed set. Wired into the `claim-fidelity-specs` surface verify_commands, the
sibling of validate_claim_fidelity_specs.py (which only indexes the *.spec.json).
floor-addition-restraint: closes a known coverage gap (outcome-assertions.json was
unvalidated by any surface gate), not a speculative new floor.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import grade_skill_outcome

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
GLOB = "evals/cautilus/*-claim-fidelity/outcome-assertions.json"


def find_assertion_sets(repo_root: Path) -> list[Path]:
    return sorted(repo_root.glob(GLOB))


def validate_file(path: Path) -> list[str]:
    """Problems for one assertion set file (empty = valid): JSON parse then schema."""
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"not valid JSON: {exc}"]
    return grade_skill_outcome.validate_assertion_set(obj)


def validate_all(repo_root: Path) -> dict[str, list[str]]:
    """Map of repo-relative path -> problems list for every set under the glob."""
    return {
        str(path.relative_to(repo_root)): validate_file(path)
        for path in find_assertion_sets(repo_root)
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate per-eval outcome-assertions.json sets against the grader schema.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable report.")
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    results = validate_all(repo_root)
    problems = {rel: errs for rel, errs in results.items() if errs}

    if args.json:
        print(json.dumps({"checked": list(results), "problems": problems}, indent=2))
        return 1 if problems else 0

    if not results:
        print("No outcome-assertions.json sets found (none ship yet).")
        return 0
    for rel, errs in results.items():
        if errs:
            print(f"FAIL {rel}:", file=sys.stderr)
            for err in errs:
                print(f"  - {err}", file=sys.stderr)
        else:
            print(f"OK   {rel}")
    if problems:
        return 1
    print(f"Validated {len(results)} outcome assertion set(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
