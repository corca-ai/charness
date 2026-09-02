#!/usr/bin/env python3
"""Delivery verification for the announcement skill's external-write boundary.

`delivery_kind: human-backend` is the only announcement delivery kind that
writes to a system this repo does not control (Slack, a chat backend, etc.).
`none` (draft-only) and `release-notes` (a checked-in, git-reversible file)
stay outside this floor. This mirrors the release skill's rung-1 presence
floor / rung-2 distinct-channel observer split
(`skills/public/release/scripts/publish_release_post_create.py`), reusing its
verdict vocabulary so the same status means the same thing everywhere.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

# Reuses the release skill's rung-2 verdict vocabulary verbatim: a
# `confirmed`, or a typed non-`verified` disposition -- never absent.
DELIVERY_VERIFICATION_STATUSES = (
    "confirmed",
    "not-confirmed",
    "blocked-needs-capability",
    "skipped",
)

EXTERNAL_WRITE_DELIVERY_KIND = "human-backend"
PROBE_TIMEOUT_SECONDS = 120


def requires_delivery_verification(delivery_kind: str) -> bool:
    """Only the external-write delivery kind is gated; draft-only and the
    git-reversible release-notes file update are not."""
    return delivery_kind == EXTERNAL_WRITE_DELIVERY_KIND


def evaluate_delivery_verification(verification: dict[str, Any] | None) -> dict[str, Any]:
    """Rung-1 presence floor (P5): a `confirmed` or a typed non-`verified`
    disposition passes EQUALLY; only a missing/empty/untyped record fails."""
    ok = (
        isinstance(verification, dict)
        and str(verification.get("status", "")).strip() in DELIVERY_VERIFICATION_STATUSES
    )
    return {"ok": ok, "record": verification if ok else None}


def fail_missing_delivery_verification(delivery_kind: str) -> None:
    # floor-addition-restraint: irreversible-boundary (external write) P4 floor, typed-disposition-only.
    raise SystemExit(
        "announcement delivery floor refused: delivery_kind is "
        f"`{delivery_kind}` (an external write) but no verification was "
        "recorded before appending the delivered record.\n"
        "Record a confirmation or a typed non-`verified` disposition: pass "
        f"--verification-status with one of {DELIVERY_VERIFICATION_STATUSES}, "
        "or have the adapter declare `post_delivery_readback_probe` so the "
        "rung-2 observer can record one automatically."
    )


def evaluate_delivery_kind_agreement(
    *, recorded_kind: str, adapter_delivery_kind: str | None, adapter_resolved: bool
) -> dict[str, Any]:
    """Cross-check the self-attested `--delivery-kind` against the adapter's
    resolved `delivery_kind`, closing the self-attestation bypass where a
    record claims a lower-risk kind than the adapter's declared backend.
    Scoped narrowly: only refuses when the adapter declares the external-write
    kind and the record disagrees. When the adapter cannot be resolved, falls
    back to CLI `choices=`-validated trust and says so in the returned record
    (never a silent, un-cross-checked pass)."""
    if not adapter_resolved:
        return {"adapter_resolved": False, "trust": "cli-choices-validated"}
    return {
        "adapter_resolved": True,
        "adapter_delivery_kind": adapter_delivery_kind,
        "agrees_with_recorded_kind": recorded_kind == adapter_delivery_kind,
    }


def requires_delivery_kind_agreement(adapter_delivery_kind: str | None) -> bool:
    return adapter_delivery_kind == EXTERNAL_WRITE_DELIVERY_KIND


def fail_delivery_kind_mismatch(*, recorded_kind: str, adapter_delivery_kind: str | None) -> None:
    # floor-addition-restraint: irreversible-boundary (external write) P4 floor, typed-disposition-only.
    raise SystemExit(
        "announcement delivery floor refused: the adapter resolves "
        f"delivery_kind=`{adapter_delivery_kind}` but this record self-attests "
        f"--delivery-kind=`{recorded_kind}`.\n"
        "The adapter declares the external-write backend, so a record cannot "
        "disagree with it. Pass --delivery-kind human-backend (with its typed "
        "verification), or correct the adapter's delivery_kind."
    )


def render_readback_probe_command(
    template: str, *, delivery_target: str, delivery_handle: str
) -> str:
    return template.replace("{delivery_target}", delivery_target).replace(
        "{delivery_handle}", delivery_handle
    )


def _default_run_shell(
    command: str, *, cwd: Path, check: bool = False
) -> subprocess.CompletedProcess[str]:
    del check  # signature parity with the release skill's run_shell; probes never abort the record
    return run_process(
        command,
        cwd=cwd,
        shell=True,
        executable="/bin/bash",
        timeout_seconds=PROBE_TIMEOUT_SECONDS,
    )


def run_readback_probe(
    *,
    probe_template: str,
    delivery_target: str,
    delivery_handle: str,
    repo_root: Path,
    run_shell=_default_run_shell,
) -> dict[str, Any]:
    """Rung-2 observer: an adapter-declared `post_delivery_readback_probe`
    command, run AFTER delivery, distinct from the delivery post itself. Never
    raises: the delivery already happened, so a failed probe is a recorded
    typed disposition, not a fatal error."""
    rendered = render_readback_probe_command(
        probe_template, delivery_target=delivery_target, delivery_handle=delivery_handle
    )
    result = run_shell(rendered, cwd=repo_root, check=False)
    record: dict[str, Any] = {
        "channel": "adapter-probe",
        "command": rendered,
        "status": "confirmed" if result.returncode == 0 else "not-confirmed",
        "returncode": result.returncode,
    }
    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "").strip()[-1500:]
        record["reason"] = tail or "readback probe returned a nonzero exit"
    return record


# `confirmed` is the only status that needs no justification; mirrors the
# release skill's treatment of `skipped` as reserved for an objectively absent
# probe (never a shrug), and requires a reason for `blocked-needs-capability`
# too, for symmetry.
STATUSES_REQUIRING_REASON = ("not-confirmed", "blocked-needs-capability", "skipped")


def resolve_manual_disposition(*, status: str, channel: str, reason: str) -> dict[str, Any] | None:
    """Fallback path (finding c): when no adapter probe is declared,
    verification is a typed disposition the agent records by hand."""
    if not status:
        return None
    if status in STATUSES_REQUIRING_REASON and not reason:
        raise SystemExit(
            f"--verification-status={status} requires a non-empty "
            "--verification-reason; `confirmed` is the only status that does not."
        )
    record: dict[str, Any] = {"channel": channel or "human-observation", "status": status}
    if reason:
        record["reason"] = reason
    return record
