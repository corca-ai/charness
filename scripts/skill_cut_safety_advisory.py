#!/usr/bin/env python3
"""Predict-commit advisory: force a REVIEW question when a staged commit deletes a
public/support skill's SKILL.md or a references/*.md contract home.

`check_skill_cut_safety` previously filtered deletions out of its default target
list (`changed_skill_md` drops `code == "D"` rows), so a maximal cut -- deleting
the whole skill -- produced zero findings; a merged deletion is not reversible
once pushed. This surfaces that gap as an advisory line (exit 0,
`run_slice_closeout.py --predict-commit` aggregate), NOT a blocking GateCommand:
an intentional, justified cut must never hard-fail the commit, only force the
reviewer to look at it.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from runtime_bootstrap import import_repo_module

_cut_safety = import_repo_module(__file__, "scripts.check_skill_cut_safety")


# floor-addition-restraint: irreversible-boundary P5, forces-question-only --
# this is the one new REVIEW-severity wiring for the deletion boundary; it must
# stay an advisory_provider line (never a blocking GateCommand exit) so an
# intentional, justified skill-surface deletion is never hard-blocked.
def provider(repo_root: Path, _selected_paths: Sequence[str]) -> list[str]:
    """Advisory provider for `run_slice_closeout.py --predict-commit`.

    Re-derives staged deletions directly from git, independent of the gate plan's
    own path sets. The plan's SCHEDULING set does carry deletions now (A3), but this
    advisory asks a different question — is this specific cut safe — and keeps its
    own source so it cannot be disarmed by a change to that set. Exit-0 informational
    lines only; never blocks.
    """
    deleted = _cut_safety.deleted_skill_surfaces(repo_root, staged=True)
    if not deleted:
        return []
    lines = [
        "REVIEW: staged deletion of a skill contract surface -- confirm the "
        "deletion is justified or re-home the contract before this commit lands "
        "(check_skill_cut_safety; advisory only, never blocks):",
    ]
    lines.extend(f"- {path}" for path in deleted)
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Skill-deletion REVIEW advisory nudge (exit 0 always).")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    for line in provider(repo_root, []):
        print(line)
    return 0


if __name__ == "__main__":  # pragma: no cover - thin CLI dispatch; main() is unit-tested
    sys.exit(main())
