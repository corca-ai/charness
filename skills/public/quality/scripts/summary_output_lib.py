from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable


def _load_yaml_output() -> SimpleNamespace:
    helper = next(
        (
            ancestor / "scripts" / "yaml_output.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "scripts" / "yaml_output.py").is_file()
        ),
        None,
    )
    if helper is None:
        raise RuntimeError("scripts/yaml_output.py not found")
    return SimpleNamespace(**runpy.run_path(str(helper)))


_YAML_OUTPUT = _load_yaml_output()
dump_yaml = _YAML_OUTPUT.render_yaml


def emit_yaml(payload: dict[str, Any]) -> None:
    print(dump_yaml(payload), end="")


def bounded_list(
    payload: dict[str, Any], key: str, *, sample_limit: int = 10
) -> dict[str, Any]:
    """Return count/sample/truncation fields for one list-valued payload key."""
    value = payload.get(key, [])
    items = value if isinstance(value, list) else []
    return {
        f"{key}_count": len(items),
        f"{key}_sample": items[:sample_limit],
        f"{key}_truncated": len(items) > sample_limit,
    }


def add_output_args(
    parser: argparse.ArgumentParser,
    *,
    summary_help: str,
    detail_help: str,
) -> None:
    output_mode = parser.add_mutually_exclusive_group()
    output_mode.add_argument("--summary", action="store_true", help=summary_help)
    output_mode.add_argument("--detail", action="store_true", help=detail_help)


def emit_selected(
    payload: dict[str, Any],
    args: argparse.Namespace,
    *,
    summarize: Callable[[dict[str, Any]], dict[str, Any]],
) -> bool:
    selected = summarize(payload) if args.summary else payload
    if args.summary or args.detail:
        emit_yaml(selected)
        return True
    return False
