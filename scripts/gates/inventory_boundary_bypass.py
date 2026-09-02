#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import render_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.gates.inventory_boundary_bypass_lib")
find_boundary_bypass_candidates = _lib.find_boundary_bypass_candidates
summarize_payload = _lib.summarize_payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Advisory inventory of boundary-bypass tests (subprocess tests of import-safe entrypoints)."
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--summary", action="store_true", help="Emit compact triage output")
    parser.add_argument(
        "--output", type=Path, default=None, help="Write the payload to this path in addition to stdout."
    )
    args = parser.parse_args()

    payload = find_boundary_bypass_candidates(args.repo_root.resolve())
    output_payload = summarize_payload(payload) if args.summary else payload
    # Unconditional YAML, and the SAME document on both channels. The retired
    # one-line advisory was a strict projection of `summary.candidate_count`,
    # `convertible_count`, `internal_boundary_count`, `keep_boundary_count`, and
    # `scanned_test_files`, which the payload carries in full.
    rendered = render_yaml(output_payload)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
