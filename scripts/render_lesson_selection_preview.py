#!/usr/bin/env python3
"""Render a flat, deterministic preview of scored lesson candidates."""

from __future__ import annotations

import argparse
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

ROOT = repo_root_from_script(__file__)
_preview = import_repo_module(__file__, "scripts.lesson_selection_preview_lib")
_continuity = import_repo_module(__file__, "scripts.lesson_evaluation_continuity_lib")
build_lesson_selection_preview = _preview.build_lesson_selection_preview


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--seed", required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    preview = build_lesson_selection_preview(
        repo_root=root,
        output_dir=root / "charness-artifacts/retro",
        summary_path=root / "charness-artifacts/retro/recent-lessons.md",
        seed=args.seed,
    )
    # `preview_text` carries the rendered bytes INSIDE the payload rather than as a
    # second output mode. Those bytes are `charness.lesson-session-preview.text.v1`
    # -- the exact string `open_lesson_session.py` freezes into a session bundle and
    # digests into the emission receipt -- so they are data this command owes its
    # callers, not a display convenience that could be deleted with the human mode.
    # Rendering them here, from the one renderer, also keeps every consumer off a
    # second hand-written copy of the item format.
    emit_yaml({**preview, "preview_text": _continuity.render_preview_bytes(preview).decode("utf-8")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
