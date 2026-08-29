#!/usr/bin/env python3
"""Gate forward-looking prose against transcribed facts a command regenerates.

Ships to consuming repos through the `quality` skill. Surfaces and exemptions come
from the repo's own quality adapter; see `regenerable_facts_lib` for the rule and
the record-versus-forward-looking seam it enforces.
"""
from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_output_lib import emit_yaml  # noqa: E402


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
load_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter").load_adapter
lib = SKILL_RUNTIME.load_local_skill_module(__file__, "regenerable_facts_lib")


def explain(report: dict) -> dict:
    """The verdict classification and its prose, folded into the emitted payload.

    Output is unconditionally YAML, so this can no longer be a second human
    channel. Every branch below carries something the raw counters do not: WHY a
    zero is a refusal rather than a pass, which knob repairs it, and — on the two
    NOT-CONFIGURED branches — that this run rendered no verdict at all. Emitting
    the bare counters would have deleted all of that while leaving `checked: 0`
    looking like a clean sweep, which is the exact claim this gate exists to
    refuse.
    """
    status = _status(report)
    return {"status": status, "diagnostics": _diagnostics(report, status)}


def _status(report: dict) -> str:
    if report.get("adapter_refusal"):
        return "adapter-refusal"
    if report["checked"] == 0 and report["exempted"]:
        return "all-matched-files-exempted"
    if report["checked"] == 0 and not report.get("declared"):
        return "not-configured"
    if report["checked"] == 0:
        return "declared-surfaces-matched-nothing"
    if report["unreasoned_exemptions"]:
        return "unreasoned-exemptions"
    if not report["findings"] and report.get("unclassified_docs"):
        return "not-configured-for-docs"
    if not report["findings"]:
        return "clean"
    return "findings"


def _diagnostics(report: dict, status: str) -> list[str]:
    """Prose FOR a verdict, dispatched on it rather than re-deriving it.

    This ladder used to re-test `_status`'s seven conditions in the same order, so the
    classification was stated twice and could desynchronize -- a `status: clean` beside
    a NOT-CONFIGURED diagnostic, or the reverse. On a gate whose whole purpose is that
    `checked: 0` must never read as a clean sweep, two independently maintained ladders
    is the defect the gate exists to refuse, one level up. Branch ORDER is load-bearing
    (see the exempted-before-undeclared note below) and is now stated once, in `_status`.
    """
    if status == "adapter-refusal":
        return [f"regenerable-facts: {report['adapter_refusal']}"]
    if status == "all-matched-files-exempted":
        # `_status` checks this FIRST, ahead of the undeclared branch. Files that matched and
        # were then exempted are not files that failed to match, and saying "no
        # file matched" over them is a statement about a scope this gate did
        # look at -- the exact class of claim this gate exists to refuse. It
        # reached a real repo: one README at the defaults, exempted with a
        # reason, no `surfaces` declared, and the gate reported that nothing
        # matched.
        return [
            f"regenerable-facts: every matched file is exempted ({len(report['exempted'])} of them), "
            "so nothing was verified. Narrow the exemptions or widen "
            "`regenerable_facts.surfaces`."
        ]
    if status == "not-configured":
        # No adapter config and nothing at the defaults: this repo has no
        # forward-looking prose where the gate looks. Report "no gate", do not
        # claim clean, and do not fail -- failing here would redden every
        # consumer's first quality run before they have configured anything.
        return [
            "regenerable-facts: NOT CONFIGURED — no file matched the default surfaces, "
            "so this repo has no verdict from this gate. Name your forward-looking prose "
            "in `regenerable_facts.surfaces` to arm it."
        ]
    if status == "declared-surfaces-matched-nothing":
        return [
            "regenerable-facts: the declared `regenerable_facts.surfaces` matched 0 files, "
            "so nothing was verified. Fix the globs — a declared scope that matches "
            "nothing is not a clean gate."
        ]
    if status == "unreasoned-exemptions":
        return [
            "regenerable-facts: exemption(s) with no recorded reason: "
            + ", ".join(report["unreasoned_exemptions"])
            + " -- an unexplained exemption is the claim this rule exists to remove"
        ]
    if status == "not-configured-for-docs":
        return [
            f"regenerable-facts: NOT CONFIGURED FOR DOCS — checked {report['checked']} canonical "
            f"forward-looking file(s), but {len(report['unclassified_docs'])} docs file(s) remain "
            "unclassified. Declare `regenerable_facts.surfaces` and reasoned exemptions before "
            "treating the docs tree as clean."
        ]
    if status == "clean":
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
    if report.get("unclassified_docs"):
        lines.append(
            f"NON-CLAIM: {len(report['unclassified_docs'])} docs file(s) were not classified by "
            "the conservative defaults; this failure verdict covers only the named default surfaces."
        )
    return lines


def _load_adapter_for_scan(repo_root: Path) -> tuple[dict | None, str | None]:
    try:
        adapter = load_adapter(repo_root)
    except Exception as exc:  # noqa: BLE001 - report it; do NOT quietly fall back to defaults
        detail = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
        return None, f"quality adapter could not be loaded ({detail}); declared surfaces are unknown"
    if isinstance(adapter, dict) and adapter.get("found") and not adapter.get("valid", True):
        return None, "quality adapter is invalid (" + "; ".join(adapter.get("errors") or []) + ")"
    return (adapter if isinstance(adapter, dict) else None), None


def _staged_advisory(repo_root: Path) -> int:
    try:
        paths = lib.staged_surface_paths(lib.staged_paths(repo_root))
    except Exception as exc:  # noqa: BLE001 - an advisory must name unavailable tooling
        print(f"ADVISORY: regenerable-facts unavailable: {type(exc).__name__}: {exc}")
        return 0
    if not paths:
        return 0

    adapter, refusal = _load_adapter_for_scan(repo_root)
    if refusal:
        print(f"ADVISORY: regenerable-facts unavailable: {refusal}")
        return 0
    try:
        report = lib.scan_paths(repo_root, paths, adapter, from_index=True)
    except Exception as exc:  # noqa: BLE001 - keep the commit boundary advisory
        print(f"ADVISORY: regenerable-facts unavailable: {type(exc).__name__}: {exc}")
        return 0

    for unavailable in report["unavailable"]:
        print(
            f"ADVISORY: regenerable-facts unavailable for {unavailable['path']}: "
            f"{unavailable['reason']}"
        )
    for finding in report["findings"]:
        print(
            f"ADVISORY: regenerable-facts {finding['path']}:{finding['line']}: "
            f"flagged `{finding['literal']}` ({finding['label']}); rule: {lib.RULE_TEXT} "
            f"Remedy: {finding['remedy']}."
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refuse transcribed versions, shas, and as-of counts on forward-looking prose surfaces."
    )
    parser.add_argument(
        "--repo-root", type=Path, default=None, help="Repository root to scan (default: the repo owning this script)."
    )
    parser.add_argument(
        "--staged-paths",
        action="store_true",
        help="Emit non-blocking advisories for staged AGENTS.md, README.md, and docs/**/*.md files.",
    )
    args = parser.parse_args()
    repo_root = (args.repo_root or REPO_ROOT).resolve()
    if args.staged_paths:
        return _staged_advisory(repo_root)

    adapter, refusal = _load_adapter_for_scan(repo_root)
    if refusal:
        # Do NOT scan on a refusal: findings from the default scope, emitted beside
        # "declared surfaces are unknown", invite a machine consumer to act on a
        # scope the same payload just said nobody chose.
        report = {
            "checked": 0,
            "surfaces": [],
            "exempted": [],
            "findings": [],
            "unreasoned_exemptions": [],
            "unclassified_docs": [],
        }
    else:
        report = lib.scan_repo(repo_root, adapter if isinstance(adapter, dict) else None)
    report["adapter_refusal"] = refusal
    emit_yaml({**report, **explain(report)})
    # `checked == 0` is a REFUSAL, not a pass: a gate that matched no file has
    # verified nothing, and reporting that as clean is the defect this rule is
    # about. It is the shipped guard, not a test-only assertion.
    failed = (
        report["findings"]
        or report["unreasoned_exemptions"]
        # A DECLARED scope matching nothing is a broken config and fails. An
        # unconfigured repo matching nothing is "no gate", reported and not failed.
        or (report["checked"] == 0 and report.get("declared"))
        or report.get("adapter_refusal")
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
