from __future__ import annotations

import json
from typing import Any


def dump_yaml(payload: dict[str, Any]) -> str:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise SystemExit("PyYAML is required for --summary-yaml") from exc
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)


def emit_summary(payload: dict[str, Any], *, as_yaml: bool) -> None:
    if as_yaml:
        print(dump_yaml(payload), end="")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
