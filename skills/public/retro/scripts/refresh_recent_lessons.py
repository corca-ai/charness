#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)







_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)

_scripts_recent_lessons_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.recent_lessons_lib")
build_recent_lessons = _scripts_recent_lessons_lib_module.build_recent_lessons
build_indexed_recent_lessons = _scripts_recent_lessons_lib_module.build_indexed_recent_lessons
write_lesson_selection_index = _scripts_recent_lessons_lib_module.write_lesson_selection_index

emit_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output").emit_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root that owns the retro adapter and recent-lessons summary")
    parser.add_argument("--source", type=Path, help="Optional repo-relative retro source artifact to require during digest rebuild")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    SKILL_RUNTIME.require_repo_local_helper(__file__, repo_root)
    adapter = load_adapter(repo_root)
    # The same guard `persist_retro_artifact` carries, and the same harm: measured, a
    # `version: 9` adapter declaring `output_dir: docs/retros` +
    # `summary_path: docs/retros/lessons.md` wrote a SHADOW digest and selection index
    # into `charness-artifacts/retro/`, left the repo's declared digest untouched, and
    # reported the shadow path as a success payload at exit 0. This command is the
    # explicit repair path, so the operator is sent here precisely when the adapter is
    # the thing that is wrong.
    refused = _version_verdict.refuse_unspeakable_version(
        load_adapter, repo_root, adapter_name="retro-adapter.yaml"
    )
    if refused is not None:
        return refused
    summary_rel = adapter["data"]["summary_path"]
    if summary_rel is None:
        # The adapter declared `summary_path: null` -- this repo's lesson owner is not
        # a Markdown projection. Refusing beats writing: this command exists to
        # WRITE the digest, so a no-op success would report a path the repo asked not
        # to have. `repo_root / None` is a TypeError, which is what this replaces.
        print(
            "retro adapter declares `summary_path: null`; the recent-lessons projection "
            "is disabled for this repository and there is nothing to refresh. Remove the "
            "declaration to re-enable it.",
            file=sys.stderr,
        )
        return 2
    output_dir = repo_root / adapter["data"]["output_dir"]
    summary_path = repo_root / summary_rel
    source_path = (repo_root / args.source).resolve() if args.source else None
    if source_path is not None and not source_path.is_file():
        raise FileNotFoundError(f"retro source not found: {source_path}")
    digest = build_indexed_recent_lessons(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(digest.summary_text, encoding="utf-8")
    index_path = write_lesson_selection_index(repo_root, output_dir, summary_path)
    emit_yaml(
        {
            "summary_path": str(summary_path.relative_to(repo_root)),
            "source_path": str(digest.source_path.relative_to(repo_root)),
            "lesson_selection_index_path": str(index_path.relative_to(repo_root)),
            "section_counts": digest.section_counts,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
