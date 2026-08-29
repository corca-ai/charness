#!/usr/bin/env python3

"""Inventory what each detector SAYS when it establishes nothing.

`tests/quality_gates/test_empty_scope_refusals.py` owns this repo's rule -- *a gate
that compared nothing must say so, and must not exit 0* -- and it enforces the rule
over a HAND-WRITTEN list of 14 scripts. The list is the problem: a detector nobody
added is not merely unchecked, it is invisible, and the repo has ~130 of them. This
inventory replaces the discovery half of that list with a glob and an observation.

Method: discover detectors by glob, run each one against an EMPTY git repository,
and bucket what comes back.

- `refused`        exit != 0. The rule's strict form.
- `honest-pass`    exit 0 AND the output carries a machine-readable empty-scope
                   marker. A discovered empty set is a real answer and stays a cheap
                   pass -- the asymmetry `test_empty_scope_refusals.py` pins -- but it
                   has to SAY so.
- `positive-verdict-over-zero`
                   exit 0 and the output asserts success (`Validated ...`,
                   `status: clean`) having inspected nothing. This is the defect
                   class. The repo already forbids exactly this shape on ONE gate:
                   `test_code_lengths_named_ungated_paths_pass_without_a_validated_verdict`
                   asserts `check_code_lengths` may not print its validated verdict
                   over an unvalidated scope.
- `silent-pass`    exit 0 and no output at all.
- `prose-only`     exit 0 and the output says something an operator can read but no
                   consumer can (`No presets found.`), so the honesty exists and is
                   not machine-checkable.
- `unprobed`       the probe could not judge: the script rejected `--repo-root`,
                   crashed, or timed out. Reported, never silently dropped.

NOT A GATE. It exits 0 on findings by design. The 2026-08-29 retro asked for an
inventory to READ FOR GAPS and said explicitly that whether a gate follows is a
later question; a gate that audits gates is the treadmill
`charness-artifacts/audit/2026-05-20-quality-treadmill-vs-root-cause.md` names.
`--require-no-positive-verdict-over-zero` exists so a repo that has decided can arm
the one bucket that is unambiguously a defect. This repo does not pass it.

Blind class, stated before the first acceptance test rather than after:

- It probes the DISCOVERED-empty arm only -- an empty repository. The other arm the
  rule cares about, a scope the CALLER NAMED that resolves to nothing, needs
  per-detector arguments this cannot synthesize, so a detector that refuses an empty
  repo may still pass over a named scope that matched nothing.
- It reads exit codes and stdout/stderr text. A detector that writes its verdict to a
  file, or whose honesty lives in a field this marker list does not name, lands in
  `prose-only` or `silent-pass` regardless of how honest it is.
- The glob finds detectors by FILENAME. A detector not named `check_*`/`validate_*`/
  `inventory_*`, or reached only as a library, is not in the population at all.
- It runs each detector once, in this repository's environment. A detector whose
  behaviour depends on installed tooling is judged on whether that tooling is here.
"""
from __future__ import annotations

import argparse
import glob as globlib
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**__import__("runpy").run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from summary_output_lib import add_output_args, emit_selected  # noqa: E402

# discovery-boundary: every family here is Python; the suffix is uniform by construction
DETECTOR_GLOBS = (
    "scripts/check_*.py",
    "scripts/validate_*.py",
    "skills/public/*/scripts/inventory_*.py",
    "skills/public/*/scripts/check_*.py",
    "skills/public/*/scripts/validate_*.py",
)

#: Suffixes that make a discovered file a LIBRARY rather than a detector entrypoint.
#: Kept because the glob is by filename: `check_coverage_lib.py` matches `check_*.py`
#: and has no CLI, so probing it measures "a library printed nothing".
LIBRARY_SUFFIXES = ("_lib.py",)

#: Machine-readable ways this repo already says "I established nothing". A detector
#: whose honesty is only prose lands in `prose-only`, which is the finding.
EMPTY_SCOPE_MARKERS = (
    "empty-scope",
    "empty_scope",
    "measurement_scope",
    "named-scope-empty",
    "unestablished",
    "unscoped",
    "did_not_judge",
    "nothing was compared",
    "nothing was validated",
    "nothing was checked",
    "establishes nothing",
    "resolve to nothing",
)

#: Output shapes that assert success. Matched only when no empty-scope marker is
#: present, so a detector that says BOTH is credited with the marker.
POSITIVE_VERDICT_MARKERS = (
    "validated ",
    "status: clean",
    "state: clean",
    "status: ok",
)

PROBE_TIMEOUT_SECONDS = 60


def discover_detectors(repo_root: Path) -> list[str]:
    found = {
        path
        for pattern in DETECTOR_GLOBS
        for path in globlib.glob(pattern, root_dir=str(repo_root))
        if not path.endswith(LIBRARY_SUFFIXES)
    }
    return sorted(found)


def classify(returncode: int | None, output: str) -> tuple[str, str | None]:
    low = output.lower()
    if returncode is None:
        return "unprobed", "timed out"
    if "traceback (most recent call last)" in low:
        return "unprobed", "crashed"
    if returncode == 2 and "usage:" in low:
        return "unprobed", "does not accept --repo-root"
    if returncode != 0:
        return "refused", None
    marker = next((m for m in EMPTY_SCOPE_MARKERS if m in low), None)
    if marker is not None:
        return "honest-pass", marker
    positive = next((m for m in POSITIVE_VERDICT_MARKERS if m in low), None)
    if positive is not None:
        return "positive-verdict-over-zero", positive
    if not output.strip():
        return "silent-pass", None
    return "prose-only", None


def probe_detector(repo_root: Path, script: str, empty_repo: Path) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [sys.executable, script, "--repo-root", str(empty_repo)],
            cwd=repo_root,
            capture_output=True,
            timeout=PROBE_TIMEOUT_SECONDS,
            text=True,
            errors="replace",
        )
        returncode: int | None = completed.returncode
        output = completed.stdout + completed.stderr
    except subprocess.TimeoutExpired:
        returncode, output = None, ""
    bucket, evidence = classify(returncode, output)
    return {
        "detector": script,
        "bucket": bucket,
        "exit_code": returncode,
        "evidence": evidence,
        "first_line": output.strip().splitlines()[0][:200] if output.strip() else "",
    }


def build_report(repo_root: Path, *, empty_repo_parent: Path) -> dict[str, Any]:
    detectors = discover_detectors(repo_root)
    findings: list[dict[str, Any]] = []
    for index, script in enumerate(detectors):
        empty_repo = empty_repo_parent / f"r{index}"
        empty_repo.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=empty_repo, check=True, capture_output=True)
        findings.append(probe_detector(repo_root, script, empty_repo))
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding["bucket"]] = counts.get(finding["bucket"], 0) + 1
    return {
        "schema": "charness.empty_scope_honesty_inventory.v1",
        "repo_root": str(repo_root),
        "detectors_discovered": len(detectors),
        # A discovery glob that matched nothing is this inventory's OWN empty scope.
        # It reports the state rather than an empty clean table, because that is the
        # rule the inventory exists to measure.
        "status": "established" if detectors else "empty-scope",
        "counts": counts,
        "findings": findings,
    }


def summarize(report: dict[str, Any], *, sample_limit: int = 10) -> dict[str, Any]:
    ranked = sorted(
        (f for f in report["findings"] if f["bucket"] == "positive-verdict-over-zero"),
        key=lambda f: f["detector"],
    )
    return {
        "schema": report["schema"],
        "status": report["status"],
        "detectors_discovered": report["detectors_discovered"],
        "counts": report["counts"],
        "positive_verdict_over_zero_sample": [f["detector"] for f in ranked[:sample_limit]],
        "positive_verdict_over_zero_truncated": len(ranked) > sample_limit,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--require-no-positive-verdict-over-zero",
        action="store_true",
        help=(
            "Exit non-zero when any detector asserts success over a scope it never "
            "established. OPT-IN: this inventory is a reading surface, not a gate."
        ),
    )
    add_output_args(
        parser,
        summary_help="Emit bucket counts and a bounded sample of the defect bucket",
        detail_help="Emit the full per-detector inventory as YAML",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    root = args.repo_root.resolve()
    with tempfile.TemporaryDirectory() as tmpdir:
        report = build_report(root, empty_repo_parent=Path(tmpdir))
    if not emit_selected(report, args, summarize=summarize):
        counts = report["counts"]
        print(f"empty-scope honesty: {report['detectors_discovered']} detector(s) probed over an empty repo.")
        for bucket in sorted(counts):
            print(f"  {bucket}: {counts[bucket]}")
    offenders = [f for f in report["findings"] if f["bucket"] == "positive-verdict-over-zero"]
    if args.require_no_positive_verdict_over_zero and offenders:
        print(
            "REFUSED: detector(s) asserted success over a scope they never established: "
            + ", ".join(f["detector"] for f in offenders),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
