#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)






_RETRO_SCRIPT_DIR = REPO_ROOT / "skills" / "public" / "retro" / "scripts"

_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter

_scripts_retro_persistence_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.retro_persistence_lib")
persist_retro_artifact = _scripts_retro_persistence_lib_module.persist_retro_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root that owns the retro adapter and output directory")
    parser.add_argument("--artifact-name", required=True, help="Filename stem (without extension) for the persisted retro artifact")
    parser.add_argument("--markdown-file", type=Path, required=True, help="Path to the rendered retro markdown body to persist")
    parser.add_argument("--snapshot-file", type=Path, help="Optional path to a JSON snapshot payload to persist alongside the artifact")
    parser.add_argument(
        "--force-empty-summary",
        action="store_true",
        help=(
            "Allow the summary refresh to write an empty-stub digest even when "
            "lesson extraction returns 0 candidates and a non-stub summary "
            "already exists. Default behavior preserves the existing summary."
        ),
    )
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
        force_empty_summary=args.force_empty_summary,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
