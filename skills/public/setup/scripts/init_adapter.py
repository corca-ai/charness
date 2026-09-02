#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    repo_root = next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "scripts" / "adapters" / "adapter_init_lib.py").is_file()
    )
    sys.path.insert(0, str(repo_root))
    from scripts.adapters.adapter_init_lib import base_adapter_items, run_init_adapter

    def build_items(repo_name: str, _args: argparse.Namespace) -> list[tuple[str, object]]:
        return [
            *base_adapter_items(repo_name, "charness-artifacts/setup"),
            ("operating_surface_profile", "flat-wiki"),
            ("approval_required", True),
            ("prose_wrap_policy", "semantic"),
        ]

    run_init_adapter(default_output=Path(".agents/setup-adapter.yaml"), build_items=build_items)


if __name__ == "__main__":
    main()
