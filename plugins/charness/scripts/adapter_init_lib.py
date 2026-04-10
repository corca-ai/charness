#!/usr/bin/env python3

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

from scripts.adapter_lib import render_yaml_mapping, write_adapter_scaffold


def base_adapter_items(
    repo_name: str,
    output_dir: str,
    *,
    preset_id: str = "portable-defaults",
) -> list[tuple[str, object]]:
    return [
        ("version", 1),
        ("repo", repo_name),
        ("language", "en"),
        ("output_dir", output_dir),
        ("preset_id", preset_id),
        ("customized_from", preset_id),
    ]


def run_init_adapter(
    *,
    default_output: Path,
    build_items: Callable[[str, argparse.Namespace], list[tuple[str, object]]],
    add_arguments: Callable[[argparse.ArgumentParser], None] | None = None,
) -> Path:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--force", action="store_true")
    if add_arguments is not None:
        add_arguments(parser)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    contents = render_yaml_mapping(build_items(repo_root.name, args))
    return write_adapter_scaffold(repo_root, args.output, contents, args.force)
