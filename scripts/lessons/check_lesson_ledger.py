#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lessons.lesson_ledger_lib")
validate_lesson_ledger = _ledger.validate_lesson_ledger
lesson_ledger_path = _ledger.lesson_ledger_path
_seeder = import_repo_module(__file__, "scripts.lessons.seed_lesson_transitions")
pending_seed_classes = _seeder.pending_seed_classes
graduated_recurrences = _seeder.graduated_recurrences
_retro_index = import_repo_module(__file__, "scripts.lessons.build_retro_lesson_selection_index")
load_retro_paths = _retro_index._load_retro_paths
_quality_adapter = import_repo_module(__file__, "scripts.adapters.quality_adapter_lib")
load_quality_adapter = _quality_adapter.load_quality_adapter
_quality_universes = import_repo_module(__file__, "scripts.adapters.quality_universes_lib")
DEFAULT_ARTIFACT_ROOTS = _quality_universes.DEFAULT_ARTIFACT_ROOTS
matching_files = _quality_universes.matching_files
refuse_if_declared_and_empty = _quality_universes.refuse_if_declared_and_empty
resolve_universe = _quality_universes.resolve_universe


def _fallback_retro_paths(root: Path) -> tuple[Path, Path | None]:
    universe = resolve_universe(
        load_quality_adapter(root),
        "artifact_roots.retro",
        default=DEFAULT_ARTIFACT_ROOTS["retro"],
    )
    files = matching_files(root, universe)
    refusal = refuse_if_declared_and_empty(universe, files, "validate-lesson-ledger")
    if refusal:
        raise ValueError(refusal)
    if not universe.patterns:
        raise ValueError("validate-lesson-ledger: no retro artifact root was resolved")
    output_dir = root / universe.patterns[0]
    return output_dir, output_dir / "recent-lessons.md"


def _retro_paths(root: Path) -> tuple[Path, Path | None]:
    try:
        return load_retro_paths(root)
    except FileNotFoundError:
        return _fallback_retro_paths(root)


def print_unseeded_advisory(root: Path, output_dir: Path, summary_path: Path | None) -> None:
    """Name every tagged class that is still not in the ledger, without failing.

    ADVISORY, not a gate failure, and the distinction is the point. A tagged class
    goes unseeded for two different reasons: nobody ran the seeder (a defect this
    line fixes by being visible), or seeding it would pass the fixed active-lesson
    budget and the ledger is waiting on a human archive decision (a legitimate
    state that a hard failure would turn into a red lane nobody can clear without
    making that decision under time pressure).

    Silence when the set is empty. A gate line that prints on every clean run is a
    line readers stop reading, and this one has to be noticed on the day it
    appears.
    """
    pending = pending_seed_classes(repo_root=root, output_dir=output_dir, summary_path=summary_path)
    if not pending:
        return
    print(
        f"ADVISORY: {len(pending)} tagged recurrence class(es) not seeded: " + ", ".join(pending)
    )


def print_graduated_recurrence_advisory(
    root: Path, output_dir: Path, summary_path: Path | None
) -> None:
    """Name every graduated lesson a retro tagged again, without failing.

    The sibling of the unseeded advisory and for the same reason: a graduated
    lesson left the selection preview on the promise that its `docs/` page holds
    the rule, and a retro tagging the class again is the only sensor that the
    promise broke. Advisory because the next move (resurrect, strengthen the
    mechanism, or call it a mis-tag) is settled by a person, not a red lane.
    Silent when empty.
    """
    found = graduated_recurrences(repo_root=root, output_dir=output_dir, summary_path=summary_path)
    if not found:
        return
    parts = [
        f"{item['lesson_id']} (owner {item['owner']}; {', '.join(item['retros'])})"
        for item in found
    ]
    print(
        f"ADVISORY: {len(found)} graduated lesson(s) tagged again by a retro the ledger "
        "does not cite: " + "; ".join(parts)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    try:
        output_dir, summary_path = _retro_paths(root)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    ledger_path = lesson_ledger_path(output_dir)
    if not ledger_path.is_file():
        print(
            "Discovered empty lesson ledger universe: "
            f"optional ledger `{ledger_path.relative_to(root)}` is absent."
        )
        return 0
    result = validate_lesson_ledger(
        repo_root=root,
        output_dir=output_dir,
        summary_path=summary_path,
    )
    print(
        "Validated lesson ledger: "
        f"{result['lesson_count']} lessons, "
        f"{result['active_lesson_count']} active, "
        f"{result['transition_count']} seed transitions, "
        f"{result['lifecycle_event_count']} lifecycle events."
    )
    print_unseeded_advisory(root, output_dir, summary_path)
    print_graduated_recurrence_advisory(root, output_dir, summary_path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
