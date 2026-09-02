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
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402

ROOT = repo_root_from_script(__file__)
_ledger = import_repo_module(__file__, "scripts.lessons.lesson_ledger_lib")
validate_lesson_ledger = _ledger.validate_lesson_ledger
lesson_ledger_path = _ledger.lesson_ledger_path
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
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
