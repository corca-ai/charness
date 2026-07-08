#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_claim_fidelity_lib_module = import_repo_module(__file__, "scripts.claim_fidelity_lib")
ALLOWLIST_PATH = _scripts_claim_fidelity_lib_module.ALLOWLIST_PATH
cross_check_conditional_reads = _scripts_claim_fidelity_lib_module.cross_check_conditional_reads
_scripts_public_skill_validation_lib_module = import_repo_module(__file__, "scripts.public_skill_validation_lib")
ValidationError = _scripts_public_skill_validation_lib_module.ValidationError


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = cross_check_conditional_reads(repo_root)
    covered = sorted(report["skills"])
    print(f"Validated conditional-reads cross-check for {len(covered)} planner-covered skill(s): {covered}.")
    for skill_id in report["not_yet_covered"]:
        print(f"  advisory: `{skill_id}` has no forced-read extractor yet (PLANNER_FORCED_READ_EXTRACTORS); not cross-checked")
    for entry in report["stale_allowlist"]:
        print(f"  advisory: {ALLOWLIST_PATH} entry `{entry['skill_id']}:{entry['ref']}` looks stale (already covered without the waiver)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
