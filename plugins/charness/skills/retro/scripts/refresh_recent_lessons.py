#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)






_RESOLVER_DIR = REPO_ROOT / "skills" / "public" / "retro" / "scripts"

_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter

_scripts_recent_lessons_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.recent_lessons_lib")
build_recent_lessons = _scripts_recent_lessons_lib_module.build_recent_lessons
pick_latest_retro_markdown = _scripts_recent_lessons_lib_module.pick_latest_retro_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    summary_rel = adapter["data"]["summary_path"]
    output_dir = repo_root / adapter["data"]["output_dir"]
    summary_path = repo_root / summary_rel
    source_path = (repo_root / args.source).resolve() if args.source else pick_latest_retro_markdown(output_dir, summary_path)
    digest = build_recent_lessons(source_path, repo_root=repo_root)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(digest.summary_text + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_path": str(summary_path.relative_to(repo_root)),
                "source_path": str(digest.source_path.relative_to(repo_root)),
                "section_counts": digest.section_counts,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
