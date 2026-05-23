#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules.setdefault(spec.name, module)
            spec.loader.exec_module(module)
            return module
    raise ImportError("runtime_bootstrap.py not found")


arm_cli_timeout = _load_runtime_bootstrap().arm_cli_timeout


def _repo_root() -> Path:
    return next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "announcement_preflight_lib.py").is_file())


def main() -> None:
    cancel_timeout = arm_cli_timeout(label="announcement preflight_sources")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root that owns the announcement adapter and draft artifact")
    parser.add_argument("--draft-path", type=Path, default=None, help="Override path to the announcement draft to preflight (defaults to the adapter artifact path)")
    try:
        args = parser.parse_args()
        repo_root = args.repo_root.resolve()
        sys.path.insert(0, str(_repo_root()))
        from scripts.announcement_adapter_lib import load_announcement_adapter
        from scripts.announcement_preflight_lib import preflight_sources

        adapter = load_announcement_adapter(repo_root)
        adapter_data = adapter["data"]
        if args.draft_path is not None:
            draft_path = args.draft_path.resolve()
        else:
            artifact_path = Path(adapter["artifact_path"])
            draft_path = artifact_path if artifact_path.is_absolute() else (repo_root / artifact_path)
        payload = preflight_sources(adapter_data, draft_path)
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        sys.exit(0 if payload["ok"] else 2)
    finally:
        cancel_timeout()


if __name__ == "__main__":
    main()
