#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parents[4]


REPO_ROOT = _runtime_root()
_RETRO_SCRIPT_DIR = REPO_ROOT / "skills" / "public" / "retro" / "scripts"
sys.path[:0] = [str(REPO_ROOT), str(_RETRO_SCRIPT_DIR)]

from resolve_adapter import load_adapter

from scripts.retro_persistence_lib import persist_retro_artifact


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
