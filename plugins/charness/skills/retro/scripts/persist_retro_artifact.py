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






_RETRO_SCRIPT_DIR = REPO_ROOT / "skills" / "public" / "retro" / "scripts"

_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter

_scripts_retro_persistence_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.retro_persistence_lib")
persist_retro_artifact = _scripts_retro_persistence_lib_module.persist_retro_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact-name", required=True)
    parser.add_argument("--markdown-file", type=Path, required=True)
    parser.add_argument("--snapshot-file", type=Path)
    return parser.parse_args()


def _load_json(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    output_dir = repo_root / adapter["data"]["output_dir"]
    summary_rel = adapter["data"].get("summary_path")
    snapshot_rel = adapter["data"].get("snapshot_path")
    markdown_text = args.markdown_file.read_text(encoding="utf-8")
    result = persist_retro_artifact(
        repo_root=repo_root,
        output_dir=output_dir,
        artifact_name=args.artifact_name,
        markdown_text=markdown_text,
        summary_path=(repo_root / summary_rel) if isinstance(summary_rel, str) else None,
        snapshot_path=(repo_root / snapshot_rel) if isinstance(snapshot_rel, str) and args.snapshot_file else None,
        snapshot_data=_load_json(args.snapshot_file),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
