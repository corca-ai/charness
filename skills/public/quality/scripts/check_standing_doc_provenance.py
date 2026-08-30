#!/usr/bin/env python3
"""Portable check for the provenance-placement policy.

Flags standing/contract-doc rule prose that carries ISO dates or multiple issue
refs, with an explicit standing-vs-tracking allowlist, so charness-consuming
repos inherit the hygiene through the public `quality` skill instead of
re-deriving it. Config lives in the quality adapter
(`standing_doc_provenance` block); the policy is documented in the
`standing-doc-provenance.md` quality reference.

Opt-in: empty `standing_doc_provenance.standing_docs` makes this a no-op
(stack-neutral default). A consuming repo opts in by listing its rule docs.

Exit 0 when clean or inert (opted out); exit 1 on a flagged line or an invalid
adapter (it fails closed — errors surface in the YAML payload and on stderr).
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
_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "standing_doc_provenance_lib")
scan_standing_docs = _lib.scan_standing_docs
_quality_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_adapter_lib")
load_quality_adapter_strict = _quality_adapter_lib.load_quality_adapter_strict


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check standing-doc provenance placement.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root containing the quality adapter and standing docs",
    )
    return parser.parse_args(argv)


def run(repo_root: Path, *, snapshot=None) -> dict[str, object]:
    adapter = load_quality_adapter_strict(repo_root)
    adapter_errors = list(adapter.get("errors") or [])
    if adapter_errors:
        return {
            "ok": False,
            "adapter_errors": adapter_errors,
            "adapter_path": adapter.get("path"),
            "scanned": [],
            "findings": [],
            "inert": False,
        }
    config = adapter["data"].get("standing_doc_provenance") or {}
    result = scan_standing_docs(repo_root, config, snapshot=snapshot)
    return {
        "ok": not result["findings"],
        "adapter_errors": [],
        "adapter_path": adapter.get("path"),
        "scanned": result["scanned"],
        "findings": result["findings"],
        "inert": result["inert"],
    }


def _verdict(report: dict[str, object]) -> dict[str, object]:
    """The verdict word and the remedy, folded into the emitted payload.

    Output is unconditionally YAML. `ok: true` on an INERT run and `ok: true` on a
    scanned-and-clean run are the same byte with different meanings, and the
    remedy sentence — which names where provenance belongs and what the one
    allowed trailing ref is — existed nowhere else. Emitting the bare result would
    have dropped both.
    """
    if report["adapter_errors"]:
        joined = "; ".join(str(e) for e in report["adapter_errors"])
        return {"verdict": "adapter-invalid", "verdict_detail": f"quality adapter invalid: {joined}"}
    if report["inert"]:
        return {
            "verdict": "inert",
            "verdict_detail": "standing_doc_provenance.standing_docs is empty; check is inert (opted out).",
        }
    if report["ok"]:
        return {
            "verdict": "ok",
            "verdict_detail": f"{len(report['scanned'])} standing doc(s) scanned; no drifted provenance.",
        }
    return {
        "verdict": "fail",
        "verdict_detail": f"{len(report['findings'])} flagged line(s) in standing docs.",
        "remedy": (
            "Move stacked dates/incident-names to the record layer (retro/*, RCA, debug/*) + one "
            "link; keep at most one load-bearing trailing (#NNN). See the standing-doc-provenance "
            "quality reference."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    report = run(repo_root)
    emit_yaml({**report, **_verdict(report)})
    if report["adapter_errors"]:
        sys.stderr.write("standing-doc provenance check skipped: repair the quality adapter.\n")
        return 1
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
