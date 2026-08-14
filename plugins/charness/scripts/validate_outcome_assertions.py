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
from pathlib import Path

import grade_skill_outcome

from runtime_bootstrap import repo_root_from_script
from yaml_output import emit_yaml

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
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    results = validate_all(repo_root)
    problems = {rel: errs for rel, errs in results.items() if errs}

    # Unconditional YAML. The retired human rendering carried three things the bare
    # `{checked, problems}` payload did not state: the per-file OK/FAIL verdict, the
    # checked count, and the "none ship yet" reading of an EMPTY glob -- which is a
    # pass over nothing, not a validated corpus. All three are folded in below so a
    # zero-set run cannot be misread as a clean verdict over real sets.
    payload = {
        "status": "invalid" if problems else "valid",
        "checked": list(results),
        "checked_count": len(results),
        "verdicts": {rel: ("fail" if errs else "ok") for rel, errs in results.items()},
        "problems": problems,
    }
    if not results:
        payload["note"] = (
            f"No outcome-assertions.json sets found under `{GLOB}` (none ship yet). "
            "Nothing was validated; this is not a verdict over any assertion set."
        )
    emit_yaml(payload)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
