#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    repo_root = next(parent for parent in Path(__file__).resolve().parents if (parent / "scripts" / "adapter_init_lib.py").is_file())
    sys.path.insert(0, str(repo_root))
    from scripts.adapter_init_lib import base_adapter_items, run_init_adapter

    def build_items(repo_name: str, _args: argparse.Namespace) -> list[tuple[str, object]]:
        return [*base_adapter_items(repo_name, "charness-artifacts/init-repo")]

    print(run_init_adapter(default_output=Path(".agents/init-repo-adapter.yaml"), build_items=build_items))


if __name__ == "__main__":
    main()
