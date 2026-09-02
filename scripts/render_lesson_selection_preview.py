#!/usr/bin/env python3
"""Render a flat, deterministic projection of the lesson selection index."""

from __future__ import annotations

import argparse
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
from scripts.yaml_output import emit_yaml  # noqa: E402

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
