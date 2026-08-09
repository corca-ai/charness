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
    if report.get("adapter_refusal"):
        return [f"regenerable-facts: {report['adapter_refusal']}"]
    if report["checked"] == 0:
        # Distinguish the two causes: an unconfigured scope and a scope whose every
        # file is exempted need different remedies, and one message for both points
        # half the readers at the wrong knob.
        if report["exempted"]:
            return [
                f"regenerable-facts: every matched file is exempted ({len(report['exempted'])} of them), "
                "so nothing was verified. Narrow the exemptions or widen "
                "`regenerable_facts.surfaces`."
            ]
        return [
            "regenerable-facts: scanned 0 files, so nothing was verified. Configure "
            "`regenerable_facts.surfaces` in the quality adapter to name this repo's "
            "forward-looking prose. A gate that matched no file is not a clean gate."
        ]
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
    refusal = None
    try:
        adapter = load_adapter(repo_root)
    except Exception as exc:  # noqa: BLE001 - report it; do NOT quietly fall back to defaults
        # `str(StopIteration())` is empty, and the portable adapter shim raises
        # exactly that when the package is installed without its scripts sibling.
        # A blank reason is a permanently red gate nobody can diagnose.
        detail = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
        adapter, refusal = None, f"quality adapter could not be loaded ({detail}); declared surfaces are unknown"
    if isinstance(adapter, dict) and adapter.get("found") and not adapter.get("valid", True):
        # Falling back to defaults here would silently DISCARD the surfaces and
        # exemptions the repo declared, and report clean over a scope nobody chose.
        refusal = "quality adapter is invalid (" + "; ".join(adapter.get("errors") or []) + ")"
        adapter = None
    if refusal:
        # Do NOT scan on a refusal: findings from the default scope, emitted beside
        # "declared surfaces are unknown", invite a machine consumer to act on a
        # scope the same payload just said nobody chose.
        report = {"checked": 0, "surfaces": [], "exempted": [], "findings": [], "unreasoned_exemptions": []}
    else:
        report = lib.scan_repo(repo_root, adapter if isinstance(adapter, dict) else None)
    report["adapter_refusal"] = refusal
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for line in render(report):
            print(line)
    # `checked == 0` is a REFUSAL, not a pass: a gate that matched no file has
    # verified nothing, and reporting that as clean is the defect this rule is
    # about. It is the shipped guard, not a test-only assertion.
    failed = (
        report["findings"]
        or report["unreasoned_exemptions"]
        or report["checked"] == 0
        or report.get("adapter_refusal")
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
