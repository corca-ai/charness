#!/usr/bin/env python3
"""Measure the evidence-residual floor against this repo's real evidence corpus.

`check_prescribed_skill_executed_lib.MIN_BOUND_RESIDUAL_CHARS` refuses evidence
that says nothing beyond the identity it was checked against. The number is only
defensible against a measurement, and two prior attempts at this floor were
withdrawn on numbers nobody could re-run -- one of them on a count of TEST
FIXTURES that was standing in for a count of artifacts.

So the measurement is a script, not a comment. It scores every checked-in
artifact of each accepted evidence kind against every word of its own filename
as a token, which is the most aggressive realistic token set (a real caller
supplies one or two), and reports the minimum.

    python3 scripts/gates/measure_evidence_residual.py --repo-root .
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

_lib = import_repo_module(__file__, "scripts.gates.check_prescribed_skill_executed_lib")

KINDS = {
    "markdown_artifacts": "charness-artifacts/**/*.md",
    "json_host_log_probes": "charness-artifacts/probe/*.json",
}


def _tokens_for(path: Path) -> list[str]:
    return [part for part in re.split(r"[^0-9A-Za-z]+", path.stem) if part]


def measure(repo_root: Path, pattern: str) -> dict[str, object]:
    scored: list[tuple[int, str]] = []
    for path in sorted(repo_root.glob(pattern)):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        residual = _lib._bound_residual_chars(text, _tokens_for(path))
        scored.append((residual, str(path.relative_to(repo_root))))
    scored.sort()
    return {
        "files": len(scored),
        "min_residual": scored[0][0] if scored else None,
        "min_residual_path": scored[0][1] if scored else None,
        "smallest_five": [
            {"residual": residual, "path": name} for residual, name in scored[:5]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    payload: dict[str, object] = {
        "floor": _lib.MIN_BOUND_RESIDUAL_CHARS,
        "kinds": {name: measure(repo_root, pattern) for name, pattern in KINDS.items()},
    }
    minimums = [
        kind["min_residual"]
        for kind in payload["kinds"].values()
        if kind["min_residual"] is not None
    ]
    # Reported, never inferred: an empty corpus must not read as "the floor clears
    # every artifact", which is the empty-scope PASS this repo keeps finding.
    payload["floor_below_every_measured_minimum"] = (
        bool(minimums) and _lib.MIN_BOUND_RESIDUAL_CHARS < min(minimums)
    )
    payload["corpus_established"] = bool(minimums)
    emit_yaml(payload)
    return 0 if payload["floor_below_every_measured_minimum"] else 1


if __name__ == "__main__":
    sys.exit(main())
