#!/usr/bin/env python3
"""CLI wrapper around ``classify_push_diff_lib.classify``.

Pre-push hook usage:

```
DIFF=$(python3 scripts/hooks/classify_push_diff.py)
classification=$(printf '%s' "$DIFF" | python3 -c "import sys,yaml; print(yaml.safe_load(sys.stdin)['classification'])")
```

Exit code: 0 in both classifications. A 2 exit signals an error resolving
the diff range (no upstream / git failure); the caller should fall back to
forcing a full gate.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:
    from scripts.yaml_output import emit_yaml


def _load_lib():
    lib_path = Path(__file__).resolve().with_name("classify_push_diff_lib.py")
    spec = importlib.util.spec_from_file_location("classify_push_diff_lib", lib_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load {lib_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LIB = _load_lib()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Classify the pending push as docs-artifact-only vs "
            "full-gate-required. The pre-push hook consults this to decide "
            "whether to skip the broad quality gate (closes #230 Waste 3)."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root used to resolve the diff range",
    )
    parser.add_argument(
        "--remote", default="origin", help="Git remote whose tracking branch defines the diff range"
    )
    parser.add_argument(
        "--diff-range", help="Explicit `<base>..<head>` diff range; overrides upstream resolution"
    )
    parser.add_argument(
        "--paths-stdin",
        action="store_true",
        help="Read newline-separated paths from stdin instead of running git diff",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    if args.paths_stdin:
        import sys

        paths = [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]
        result = LIB.classify(paths)
        emit_yaml(result)
        return 0
    diff_range = args.diff_range
    if diff_range is None:
        diff_range = LIB.resolve_diff_range(repo_root, remote=args.remote)
    if diff_range is None:
        emit_yaml(
            {
                "classification": "full-gate-required",
                "files": [],
                "reason": "no upstream tracking branch found; full gate forced",
            }
        )
        return 0
    try:
        paths = LIB.changed_paths_from_git(repo_root, diff_range)
    except subprocess.CalledProcessError as exc:
        emit_yaml(
            {
                "classification": "full-gate-required",
                "files": [],
                "reason": f"git diff failed; full gate forced: {exc}",
            }
        )
        return 2
    result = LIB.classify(paths)
    result["diff_range"] = diff_range
    emit_yaml(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
