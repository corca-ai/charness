#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_recent_lessons_module = import_repo_module(__file__, "scripts.recent_lessons_lib")
build_lesson_selection_index = _recent_lessons_module.build_lesson_selection_index
check_lesson_selection_index = _recent_lessons_module.check_lesson_selection_index
lesson_selection_index_path = _recent_lessons_module.lesson_selection_index_path
lesson_selection_index_text = _recent_lessons_module.lesson_selection_index_text


def _resolver_path(repo_root: Path) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "retro" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "retro" / "scripts" / "resolve_adapter.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("retro resolve_adapter.py not found")


def _load_yamlish_retro_paths(repo_root: Path) -> tuple[Path, Path]:
    adapter_path = repo_root / ".agents" / "retro-adapter.yaml"
    if not adapter_path.is_file():
        raise FileNotFoundError("retro resolve_adapter.py not found")
    data: dict[str, str] = {}
    for raw_line in adapter_path.read_text(encoding="utf-8").splitlines():
        if ":" not in raw_line or raw_line.startswith(" "):
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip()
    output_dir = data.get("output_dir")
    summary_path = data.get("summary_path")
    if not output_dir or not summary_path:
        raise FileNotFoundError("retro adapter must define `output_dir` and `summary_path`")
    return repo_root / output_dir, repo_root / summary_path


def _load_retro_paths(repo_root: Path) -> tuple[Path, Path]:
    try:
        resolver_path = _resolver_path(repo_root)
    except FileNotFoundError:
        return _load_yamlish_retro_paths(repo_root)
    module = load_path_module("retro_lesson_index_resolve_adapter", resolver_path)
    adapter = module.load_adapter(repo_root)
    data = adapter["data"]
    return repo_root / data["output_dir"], repo_root / data["summary_path"]


def _relative(repo_root: Path, path: Path) -> str:
    return str(path.relative_to(repo_root))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_dir, summary_path = _load_retro_paths(repo_root)
    payload = build_lesson_selection_index(repo_root=repo_root, output_dir=output_dir, summary_path=summary_path)
    index_path = lesson_selection_index_path(output_dir)

    if args.write:
        index_path.write_text(lesson_selection_index_text(payload), encoding="utf-8")
        result = {
            "index_path": _relative(repo_root, index_path),
            "source_artifact_count": payload["source_artifact_count"],
            "candidate_count": payload["candidate_count"],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"Wrote {result['index_path']}.")
        return 0
    if args.check:
        check_lesson_selection_index(repo_root, output_dir, summary_path)
        print("Validated retro lesson selection index.")
        return 0

    print(lesson_selection_index_text(payload), end="")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
