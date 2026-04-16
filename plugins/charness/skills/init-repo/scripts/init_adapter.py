#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    repo_root = next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "adapter_init_lib.py").is_file())
    sys.path.insert(0, str(repo_root))
    from scripts.adapter_init_lib import base_adapter_items, run_init_adapter

    print(run_init_adapter(default_output=Path(".agents/init-repo-adapter.yaml"), build_items=lambda repo_name, _args: base_adapter_items(repo_name, "charness-artifacts/init-repo")))


if __name__ == "__main__":
    main()
