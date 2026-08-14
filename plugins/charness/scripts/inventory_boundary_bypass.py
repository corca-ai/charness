#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import render_yaml

REPO_ROOT = repo_root_from_script(__file__)

_lib = import_repo_module(__file__, "scripts.inventory_boundary_bypass_lib")
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
