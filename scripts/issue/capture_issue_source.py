#!/usr/bin/env python3
"""Capture GitHub issue source completely, or refuse.

This is the ONLY authority that may write the frozen source snapshot the
acceptance matrix binds to. `gh issue view` remains available as a diagnostic
cross-check and is deliberately not wired in here: it cannot report whether its
comment set is complete, so letting it write the snapshot would put an unprovable
capture underneath every criterion id derived from it.

Usage:
    python3 scripts/issue/capture_issue_source.py --repo corca-ai/charness \\
        --numbers 514 515 518 \\
        --snapshot charness-artifacts/spec/2026-08-07-issue-514-515-518-source.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import (  # noqa: E402
    import_repo_module,
    load_path_module,
    repo_root_from_script,
)

REPO_ROOT = repo_root_from_script(__file__)

_capture_lib = import_repo_module(__file__, "scripts.issue.issue_source_capture_lib")
CaptureRefusal = _capture_lib.CaptureRefusal
build_snapshot_and_receipt = _capture_lib.build_snapshot_and_receipt
capture_issues = _capture_lib.capture_issues
run_gh = _capture_lib.run_gh

_refusal_lib = import_repo_module(__file__, "scripts.review.closeout_refusal_lib")
_normalize_lib = import_repo_module(__file__, "scripts.issue.issue_source_normalize_lib")
canonical_json = _normalize_lib.canonical_json
sha256_text = _normalize_lib.sha256_text

RESOLVER_CANDIDATES = (
    Path("skills") / "public" / "issue" / "scripts" / "resolve_adapter.py",
    Path("skills") / "issue" / "scripts" / "resolve_adapter.py",
)


def resolve_adapter_module(script_root: Path = REPO_ROOT):
    """Load the issue skill's adapter resolver from this copy's OWN tree.

    Two roots are in play and conflating them is the bug this signature prevents.
    The resolver is a sibling of *this script* — root layout puts it under
    `skills/public/issue/`, the installed plugin under `skills/issue/` — while the
    `.agents/issue-adapter.yaml` it reads belongs to the CONSUMER repo passed as
    `--repo-root`. An installed copy must resolve its own sibling implementation
    rather than reaching into whatever `skills/` tree the consumer happens to have.

    The resolver is loaded, never reimplemented: the receipt must record the SAME
    adapter/backend identity the rest of the issue lane resolves, or the identity it
    records proves nothing about the lane that later reads it.
    """
    for candidate in RESOLVER_CANDIDATES:
        path = script_root / candidate
        if path.is_file():
            return load_path_module("issue_resolve_adapter_for_capture", path)
    raise CaptureRefusal(
        "resolver_missing",
        f"no issue resolve_adapter.py under {script_root}; the capture cannot record "
        "which adapter it resolved",
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def run_capture(
    *, repo_root: Path, repo: str, numbers: list[int], snapshot_path: Path, runner=None
) -> dict[str, object]:
    # Resolved at CALL time, not bound as a default at definition time: a default
    # captures the `run_gh` object that existed when this module was imported, so a
    # test patching this module's `run_gh` never reached `main`'s call and the real,
    # locally authenticated `gh` answered instead (#779; green here, exit 4 in CI).
    runner = run_gh if runner is None else runner
    resolver = resolve_adapter_module()
    adapter = resolver.load_adapter(repo_root)
    if not adapter["valid"]:
        raise CaptureRefusal("invalid_adapter", "; ".join(adapter["errors"]))
    capability = adapter["data"].get("issue_source_capture")
    if not capability:
        raise CaptureRefusal(
            "missing_capability", "adapter exposes no issue_source_capture capability"
        )
    if not capability.get("supported", True):
        # The adapter stayed valid so unrelated issue operations keep working; the
        # refusal lands here, on the one operation whose completeness claim the
        # undeclared capability makes unprovable.
        raise CaptureRefusal("unsupported_capability", capability["unsupported_reason"])
    backend = adapter["data"]["issue_backend"]
    captured = capture_issues(
        repo=repo, numbers=numbers, backend=backend, capability=capability, runner=runner
    )

    stem = snapshot_path.name.removesuffix(".json")
    snapshot_rel = snapshot_path.resolve().relative_to(repo_root)
    raw_dir_rel = f"{snapshot_rel.parent.as_posix()}/{stem}-raw"
    receipt_path = snapshot_path.with_name(f"{stem}-capture-receipt.json")
    snapshot, receipt, raw_files = build_snapshot_and_receipt(
        repo=repo,
        numbers=numbers,
        adapter=adapter,
        capability=capability,
        captured=captured,
        raw_dir_rel=raw_dir_rel,
    )
    for rel, body in raw_files.items():
        # Verbatim, with no trailing-newline normalization: the receipt commits to a
        # digest of exactly what the backend returned, and the freeze validator
        # re-derives the snapshot from these bytes. Adding a convenience newline here
        # made every raw page fail its own digest check.
        raw_path = repo_root / rel
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(body, encoding="utf-8")
    snapshot_text = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True)
    _write(snapshot_path, snapshot_text)
    receipt["snapshot_path"] = snapshot_path.relative_to(repo_root).as_posix()
    receipt["snapshot_file_sha256"] = sha256_text(snapshot_text + "\n")
    receipt["raw_response_dir"] = raw_dir_rel
    _write(receipt_path, json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return {
        "ok": True,
        "repository": repo,
        "numbers": sorted(numbers),
        "snapshot_path": receipt["snapshot_path"],
        "receipt_path": receipt_path.relative_to(repo_root).as_posix(),
        "raw_response_dir": raw_dir_rel,
        "source_snapshot_sha256": snapshot["source_snapshot_sha256"],
        "clause_inventory_identity": snapshot["clause_inventory_identity"],
        "pagination_complete": True,
        "per_issue": [
            {
                "number": issue["number"],
                "comment_total_count": issue["comment_total_count"],
                "captured_comment_count": issue["captured_comment_count"],
                "pages": len(issue["pages"]),
            }
            for issue in receipt["issues"]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--repo", required=True, help="owner/name of the issue repository")
    parser.add_argument("--numbers", type=int, nargs="+", required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    snapshot_path = args.snapshot if args.snapshot.is_absolute() else repo_root / args.snapshot
    return _refusal_lib.run_cli(
        "capture_issue_source",
        lambda: run_capture(
            repo_root=repo_root,
            repo=args.repo,
            numbers=list(args.numbers),
            snapshot_path=snapshot_path,
        ),
        refusals=(CaptureRefusal,),
        code_key="refusal",
    )


if __name__ == "__main__":
    raise SystemExit(main())
