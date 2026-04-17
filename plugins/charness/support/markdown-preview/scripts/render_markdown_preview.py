#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_sibling(module_name: str) -> object:
    module_path = Path(__file__).resolve().with_name(f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(module_name, module)
    spec.loader.exec_module(module)
    return module


_LIB = _load_sibling("markdown_preview_lib")
_RENDER = _load_sibling("markdown_preview_render")
REPO_ROOT = _LIB.REPO_ROOT
load_config = _LIB.load_config
merge_cli = _LIB.merge_cli
select_targets = _LIB.select_targets
render_targets = _RENDER.render_targets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--width", action="append", type=int, default=[])
    parser.add_argument("--artifact-dir")
    parser.add_argument("--backend")
    parser.add_argument("--changed-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    config = merge_cli(
        load_config(repo_root, args.config),
        files=args.file,
        widths=args.width,
        artifact_dir=args.artifact_dir,
        backend=args.backend,
        changed_only=args.changed_only,
    )
    if not config.enabled:
        print(
            json.dumps(
                {
                    "status": "disabled",
                    "repo_root": str(repo_root),
                    "config_path": config.config_path,
                    "warnings": ["Markdown preview is disabled by config."],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    targets, selection_warnings = select_targets(repo_root, config)
    payload = render_targets(repo_root, config, targets)
    payload["warnings"] = selection_warnings + payload["warnings"]
    manifest_path = repo_root / payload["artifact_dir"] / "manifest.json"
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
