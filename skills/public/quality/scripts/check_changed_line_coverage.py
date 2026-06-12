#!/usr/bin/env python3
"""Portable changed-line coverage gate as a `quality` capability (handoff-3).

Reproduces the blocking signal of a scheduled mutation gate locally: a changed
pool file whose changed lines over `base..head` lack test coverage. Driven by
the quality adapter's `changed_line_mutation_gate` block so a consuming repo
inherits the gate without the charness mutation-runner wiring; reuses a
coverage.py JSON a full / scheduled run produced, gated by a content-fingerprint
freshness marker. See the `mutation-testing.md` quality reference.

Opt-in: empty `changed_line_mutation_gate.eligible_globs` makes this inert.

Exit 0 when clean, inert, or skipped (no base / no eligible change / no fresh
coverage — all non-blocking by construction); exit 1 on a blocking changed-line
gap or an invalid adapter (fails closed). Base/head come from `--base-sha` /
`--head-sha` or `MUTATION_BASE_SHA` / `MUTATION_HEAD_SHA` (head defaults to HEAD).
"""
from __future__ import annotations

import argparse
import json
import os
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_gate_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "changed_line_coverage_gate_lib")
_quality_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_adapter_lib")
_changed_files_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.mutation_changed_files_lib")
_sampling_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.mutation_sampling_lib")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portable changed-line coverage gate.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--base-sha", default=None, help="Base SHA; defaults to $MUTATION_BASE_SHA.")
    parser.add_argument("--head-sha", default=None, help="Head SHA; defaults to $MUTATION_HEAD_SHA, else HEAD.")
    parser.add_argument("--stamp-marker", action="store_true", help="Producer mode: stamp the freshness marker, then exit 0.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def _resolve_shas(args) -> tuple[str | None, str]:
    base = (args.base_sha if args.base_sha is not None else os.environ.get("MUTATION_BASE_SHA") or "").strip() or None
    head = (args.head_sha if args.head_sha is not None else os.environ.get("MUTATION_HEAD_SHA") or "").strip() or "HEAD"
    return base, head


def _false_green_warning(repo_root: Path, head_sha: str, eligible_globs: list[str], exclude_globs: list[str]) -> str | None:
    """Warn when analyzing HEAD while eligible pool files have uncommitted changes
    excluded from base..HEAD — a clean verdict would be a false green for them."""
    resolved = _gate_lib._git_lines(repo_root, ["rev-parse", head_sha])
    head = _gate_lib._git_lines(repo_root, ["rev-parse", "HEAD"])
    if not (head_sha == "HEAD" or (resolved and head and resolved[0] == head[0])):
        return None
    dirty = _gate_lib.eligible(
        _gate_lib._git_lines(repo_root, ["diff", "--name-only", "HEAD"]), eligible_globs, exclude_globs
    )
    if not dirty:
        return None
    return (
        f"analyzed head resolves to HEAD but {len(dirty)} eligible file(s) have uncommitted changes "
        f"excluded from base..HEAD ({', '.join(dirty)}); a clean verdict is a FALSE GREEN for them. "
        "Commit them, then re-run."
    )


def run(repo_root: Path, args) -> dict[str, object]:
    adapter = _quality_adapter_lib.load_quality_adapter_strict(repo_root)
    adapter_errors = list(adapter.get("errors") or [])
    if adapter_errors:
        return {"ok": False, "adapter_errors": adapter_errors, "inert": False, "blocking": []}
    config = adapter["data"].get("changed_line_mutation_gate") or {}
    base_sha, head_sha = _resolve_shas(args)
    if args.stamp_marker:
        fp = _gate_lib.stamp_marker(repo_root, config, base_sha or "", marker_path=_changed_files_lib.coverage_fingerprint_marker_path)
        return {"ok": True, "adapter_errors": [], "inert": fp is None, "blocking": [],
                "reason": "marker stamped" if fp else "inert/unconfigured: nothing to stamp", "fingerprint": fp}
    report = _gate_lib.run_gate(
        repo_root, config, base_sha=base_sha, head_sha=head_sha,
        classify=_changed_files_lib.classify_changed_line_scope_gap,
        load_statement_lines=_sampling_lib.load_file_statement_lines,
        marker_path=_changed_files_lib.coverage_fingerprint_marker_path,
    )
    report["adapter_errors"] = []
    if not report.get("inert"):
        warning = _false_green_warning(
            repo_root, head_sha, list(config.get("eligible_globs") or []), list(config.get("exclude_globs") or [])
        )
        if warning:
            report["warning"] = warning
            sys.stderr.write(f"WARNING (changed-line coverage gate): {warning}\n")
    return report


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    report = run(repo_root, args)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        if report.get("adapter_errors"):
            print(f"quality adapter invalid: {'; '.join(str(e) for e in report['adapter_errors'])}")
        elif report.get("inert"):
            print("changed_line_mutation_gate.eligible_globs is empty; gate inert (opted out).")
        elif report["blocking"]:
            print(f"FAIL: {len(report['blocking'])} changed file(s) have uncovered changed lines: {', '.join(report['blocking'])}")
        else:
            print(f"OK: {report.get('reason', 'no uncovered changed lines')}")
    if report.get("adapter_errors"):
        return 1
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
