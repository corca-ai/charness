#!/usr/bin/env python3
"""Verify one critique prepare packet and its reviewed-input binding."""

from __future__ import annotations

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_identity = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.review.reviewed_input_verification"
)
emit_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.yaml_output"
).emit_yaml

EXPECTED_KIND = "charness.critique_prepare_packet"


def _payload(
    *,
    ok: bool,
    reason: str,
    packet_path: str,
    packet_sha256: str,
    identity_sha256: str,
    reason_code: str,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "status": "current" if ok else "refused",
        "reason": reason,
        "reason_code": reason_code,
        "expected_kind": EXPECTED_KIND,
        "packet_path": packet_path,
        "packet_sha256": packet_sha256,
        "identity_sha256": identity_sha256,
    }


def _reason_code(reason: str) -> str:
    if reason == "current":
        return "current"
    rules = (
        (("changed-ref-path-mismatch",), "changed-ref-path-mismatch"),
        (("changed-ref-unavailable",), "changed-ref-unavailable"),
        (("null-content-hash",), "null-or-invalid-hash"),
        (("sha256 is null or invalid",), "null-or-invalid-hash"),
        (("substrate mode",), "substrate-mode-mismatch"),
        (("changed_ref",), "changed-ref-mismatch"),
        (("identity", "stale"), "reviewed-input-stale"),
        (("path", "outside"), "path-outside-repo"),
        (("content hash",), "null-or-invalid-hash"),
        (("packet bytes",), "packet-stale-or-tampered"),
        (("not valid JSON",), "packet-invalid-json"),
        (("wrong kind",), "packet-kind-mismatch"),
        (("artifact identity",), "identity-mismatch"),
        (("zero paths",), "empty-reviewed-paths"),
    )
    for needles, code in rules:
        if all(needle in reason for needle in needles):
            return code
    return "packet-binding-refused"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=Path.cwd(), help="Repo root containing the packet"
    )
    parser.add_argument("--packet-path", required=True, help="Repo-relative packet JSON path")
    parser.add_argument("--packet-sha256", required=True, help="Expected packet byte digest")
    parser.add_argument(
        "--identity-sha256", required=True, help="Expected reviewed-input identity digest"
    )
    args = parser.parse_args(argv)

    try:
        ok, reason = _identity.verify_packet_binding(
            repo_root=args.repo_root.resolve(),
            packet_path=args.packet_path,
            packet_sha256=args.packet_sha256,
            identity_sha256=args.identity_sha256,
            expected_kind=EXPECTED_KIND,
        )
    except Exception as exc:  # malformed packet shapes must remain structured refusals
        ok, reason = False, f"cannot verify packet binding: {exc}"

    emit_yaml(
        _payload(
            ok=ok,
            reason=reason,
            packet_path=args.packet_path,
            packet_sha256=args.packet_sha256,
            identity_sha256=args.identity_sha256,
            reason_code=_reason_code(reason),
        )
    )
    return 0 if ok and reason == "current" else 1


if __name__ == "__main__":
    raise SystemExit(main())
