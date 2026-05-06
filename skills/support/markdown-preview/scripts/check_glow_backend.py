#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_render_module():
    module_path = Path(__file__).resolve().with_name("markdown_preview_render.py")
    spec = importlib.util.spec_from_file_location("markdown_preview_render", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    render = _load_render_module()
    payload = render.check_backend("glow")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "healthy" else 1


if __name__ == "__main__":
    raise SystemExit(main())
