#!/usr/bin/env python3
"""Render a flat, deterministic projection of the lesson selection index."""

from __future__ import annotations

import argparse
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

ROOT = repo_root_from_script(__file__)
_preview = import_repo_module(__file__, "scripts.lessons.lesson_selection_preview_lib")
build_lesson_selection_preview = _preview.build_lesson_selection_preview
_retro = import_repo_module(__file__, "scripts.retro_debug.retro_output_dir_lib")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--seed", required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    preview = build_lesson_selection_preview(
        repo_root=root,
        output_dir=_retro.retro_output_dir(root),
        summary_path=_retro.retro_summary_path(root),
        seed=args.seed,
    )
    # The payload is deliberately just the projection. It is useful for an agent
    # choosing context, but it is not a presentation, session, or evaluation
    # receipt and must not acquire one of those contracts by accident.
    emit_yaml(preview)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
