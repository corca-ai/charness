#!/usr/bin/env python3
"""Gate forward-looking prose against transcribed facts a command regenerates.

Ships to consuming repos through the `quality` skill. Surfaces and exemptions come
from the repo's own quality adapter; see `regenerable_facts_lib` for the rule and
the record-versus-forward-looking seam it enforces.
"""
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
load_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter").load_adapter
lib = SKILL_RUNTIME.load_local_skill_module(__file__, "regenerable_facts_lib")


def render(report: dict) -> list[str]:
    if report["unreasoned_exemptions"]:
        return [
            "regenerable-facts: exemption(s) with no recorded reason: "
            + ", ".join(report["unreasoned_exemptions"])
            + " -- an unexplained exemption is the claim this rule exists to remove"
        ]
    if not report["findings"]:
        return [
            f"no regenerable facts in {report['checked']} forward-looking file(s) "
            f"({len(report['exempted'])} exempted with a recorded reason)"
        ]
    lines = [f"regenerable facts on {len(report['findings'])} line(s):"]
    for finding in report["findings"]:
        lines.append(
            f"  - {finding['path']}:{finding['line']}: {finding['label']} "
            f"(`{finding['literal']}`); {finding['remedy']}"
        )
    lines.append(
        "A cheap command goes in the prose alone. An EXPENSIVE one carries the command "
        "AND a link to the checked-in artifact holding its output -- do not make every "
        "future reader re-run it."
    )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refuse transcribed versions, shas, and as-of counts on forward-looking prose surfaces."
    )
    parser.add_argument(
        "--repo-root", type=Path, default=None, help="Repository root to scan (default: the repo owning this script)."
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit the findings, exemptions, and scanned surfaces as JSON."
    )
    args = parser.parse_args()
    repo_root = (args.repo_root or REPO_ROOT).resolve()
    try:
        adapter = load_adapter(repo_root)
    except Exception:  # noqa: BLE001 - a repo without a quality adapter still gets the defaults
        adapter = None
    report = lib.scan_repo(repo_root, adapter if isinstance(adapter, dict) else None)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for line in render(report):
            print(line)
    return 1 if report["findings"] or report["unreasoned_exemptions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
