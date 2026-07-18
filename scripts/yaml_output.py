from __future__ import annotations

import json
from typing import Any


def render_yaml(payload: Any) -> str:
    """Render one portable YAML document, with JSON syntax as a valid fallback."""

    normalized = json.loads(json.dumps(payload, ensure_ascii=False, allow_nan=False))
    try:
        import yaml
    except ImportError:
        return json.dumps(normalized, ensure_ascii=False, separators=(",", ":")) + "\n"
    return yaml.safe_dump(normalized, allow_unicode=True, sort_keys=False)


def emit_yaml(payload: Any) -> None:
    print(render_yaml(payload), end="")
