#!/usr/bin/env python3
"""Render a flat, deterministic preview of scored lesson candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

ROOT = repo_root_from_script(__file__)
_preview = import_repo_module(__file__, "scripts.lesson_selection_preview_lib")
_continuity = import_repo_module(__file__, "scripts.lesson_evaluation_continuity_lib")
build_lesson_selection_preview = _preview.build_lesson_selection_preview


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    preview = build_lesson_selection_preview(
        repo_root=root,
        output_dir=root / "charness-artifacts/retro",
        summary_path=root / "charness-artifacts/retro/recent-lessons.md",
        seed=args.seed,
    )
    if args.json:
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return 0
    print(_continuity.render_preview_bytes(preview).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
