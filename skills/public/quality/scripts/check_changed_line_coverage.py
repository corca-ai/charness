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
gap, an invalid adapter, or a run that could not establish its own scope because
git would not answer (all fail closed). The last case prints `UNESTABLISHED:`
rather than `FAIL:`, because "could not look" is not "looked and found a gap" —
it used to return an empty changed set and pass as `ok`. Base/head come from `--base-sha` /
`--head-sha` or `MUTATION_BASE_SHA` / `MUTATION_HEAD_SHA` (head defaults to HEAD).

Exit **3** is a third code, not a variant of 1: the analyzed head is not the
checked-out `HEAD` and the range touched eligible files, so the run could not
judge. It carries `ok: true` and is not a coverage failure — but it IS nonzero,
and a caller that treats every nonzero as red will read it as one. This case
exited 0 before the code existed, which is the silent false green it replaces.
Pinning `--head-sha` to a PR head sha on a `pull_request` event produces it on
every run; pass only `--base-sha`. Full table: the `changed_line_mutation_gate`
section of the quality `references/adapter-contract.md`.
"""
from __future__ import annotations

import argparse
import os
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
_gate_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "changed_line_coverage_gate_lib")
_quality_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_adapter_lib")
_changed_files_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.mutation_changed_files_lib")
_sampling_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.mutation_sampling_lib")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portable changed-line coverage gate.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root containing the quality adapter and changed files",
    )
    parser.add_argument("--base-sha", default=None, help="Base SHA; defaults to $MUTATION_BASE_SHA.")
    parser.add_argument("--head-sha", default=None, help="Head SHA; defaults to $MUTATION_HEAD_SHA, else HEAD.")
    parser.add_argument("--stamp-marker", action="store_true", help="Producer mode: stamp the freshness marker, then exit 0.")
    return parser.parse_args(argv)


def _resolve_shas(args) -> tuple[str | None, str]:
    base = (args.base_sha if args.base_sha is not None else os.environ.get("MUTATION_BASE_SHA") or "").strip() or None
    head = (args.head_sha if args.head_sha is not None else os.environ.get("MUTATION_HEAD_SHA") or "").strip() or "HEAD"
    return base, head


def _false_green_warning(
    repo_root: Path,
    head_sha: str,
    eligible_globs: list[str],
    exclude_globs: list[str],
    *,
    scope: "_gate_lib.HeadScope | None" = None,
) -> str | None:
    """Warn when analyzing HEAD while eligible pool files have uncommitted changes
    excluded from base..HEAD — a clean verdict would be a false green for them.

    Resolves through `resolve_head_scope` rather than its own `rev-parse`. It used
    a BARE `rev-parse <head>` while the scope check peeled with `^{commit}`, so an
    annotated tag on the checked-out commit read as "same head" there and
    "different head" here — and this guard, whose whole job is the false green,
    turned itself off on a run that had just been cleared to render a verdict.

    `scope`, when given, is the `HeadScope` `run_gate` already resolved for this
    SAME `head_sha` -- threaded through so this does not re-ask git the identical
    question. `run_gate` only resolves a scope once it is past its own
    base-sha/coverage-config skip checks, so a caller reached before either exists
    (`scope=None`) still resolves it here itself.

    Nothing raises out of here any more either. `_git_lines` raises on a nonzero
    git exit, so an unresolvable `--head-sha` used to kill the process with a
    traceback AFTER `run_gate` had already produced the unestablished report —
    the operator got no parseable payload at all.
    """
    if scope is None:
        scope = _gate_lib.resolve_head_scope(repo_root, head_sha)
    if scope.error or scope.mismatch:
        return None
    try:
        dirty = _gate_lib.eligible(
            _gate_lib._git_lines(repo_root, ["diff", "--name-only", "HEAD"]), eligible_globs, exclude_globs
        )
    except _gate_lib.GitUnavailable:
        return None
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
    # Pop, don't leave: `run_gate` rides its already-resolved `HeadScope` through
    # the report only so this function can thread it into `_false_green_warning`
    # below without a second `resolve_head_scope` over the same `head_sha`. It is
    # not YAML-safe and not part of the gate's contract, so it must never reach
    # the payload `main()` emits.
    resolved_scope = report.pop("_head_scope", None)
    disclosure = report.get("analyzed_head_not_checked_out_head")
    if disclosure:
        # Exit stays 0 (the analyzed range really did change no eligible file), so
        # this stderr warning is the loud channel that says the empty scope belongs
        # to the analyzed head and not to this tree; the payload carries the same
        # fact under `analyzed_head_not_checked_out_head` and `analyzed_head`.
        sys.stderr.write(
            f"WARNING (changed-line coverage gate): {disclosure}. This range changed no "
            "eligible file, so there was nothing to prove -- but the empty scope is the "
            "ANALYZED head's, not this tree's.\n"
        )
    if not report.get("inert") and not report.get("unestablished"):
        warning = _false_green_warning(
            repo_root, head_sha, list(config.get("eligible_globs") or []), list(config.get("exclude_globs") or []),
            scope=resolved_scope,
        )
        if warning:
            report["warning"] = warning
            sys.stderr.write(f"WARNING (changed-line coverage gate): {warning}\n")
    return report


def verdict(report: dict) -> dict[str, object]:
    """The verdict WORD and its explanation, folded into the emitted payload.

    Output is unconditionally YAML, so anything a reader needs has to live in the
    payload. Two things did not, and both are load-bearing:

    - The verdict word itself. `unestablished` reports carry an EMPTY `blocking`
      list, so a reader who derives the verdict from `blocking` alone reads a
      could-not-judge run as a pass while the process exits nonzero — the same
      conflation the unestablished state was introduced to end.
    - Whether the judged head is this worktree's. A non-default head can arrive
      from `$MUTATION_HEAD_SHA` rather than from anything the operator typed, so
      a verdict over a range nobody asked for would otherwise read as an
      unqualified one.
    """
    if report.get("adapter_errors"):
        return {
            "verdict": "adapter-invalid",
            "verdict_detail": "quality adapter invalid: "
            + "; ".join(str(e) for e in report["adapter_errors"]),
        }
    if report.get("inert"):
        return {
            "verdict": "inert",
            "verdict_detail": "changed_line_mutation_gate.eligible_globs is empty; gate inert (opted out).",
        }
    requested = str(report.get("head_sha") or "HEAD")
    resolved = report.get("resolved_head_sha")
    scope: dict[str, object] = (
        {} if requested == "HEAD" or not resolved else {"analyzed_head": str(resolved)}
    )
    if report.get("unestablished"):
        return {
            "verdict": "unestablished",
            "verdict_detail": str(report.get("reason", "this run established nothing")),
            **scope,
        }
    if report["blocking"]:
        return {
            "verdict": "fail",
            "verdict_detail": (
                f"{len(report['blocking'])} changed file(s) have uncovered changed lines: "
                f"{', '.join(report['blocking'])}"
            ),
            **scope,
        }
    return {
        "verdict": "ok",
        "verdict_detail": str(report.get("reason", "no uncovered changed lines")),
        **scope,
    }


UNESTABLISHED_EXIT = 3


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    report = run(repo_root, args)
    emit_yaml({**report, **verdict(report)})
    if report.get("adapter_errors"):
        return 1
    # Exit 3 for "this run could not judge the range", separately from exit 1 for
    # "it judged and the changed lines are uncovered". A consumer's CI reads the
    # exit code, not stdout, so collapsing them made a could-not-judge arrive as a
    # coverage failure. `ok: True` marks the causes that are lenient by a NAMED
    # reason (the analyzed head is not this worktree); a cause the gate could not
    # even look into keeps `ok: False` and exit 1, because leniency granted for one
    # reason must not be inherited by another.
    if report.get("unestablished") and report.get("ok"):
        return UNESTABLISHED_EXIT
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
