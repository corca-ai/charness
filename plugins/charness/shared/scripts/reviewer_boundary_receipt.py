#!/usr/bin/env python3
"""Build machine-readable continuation receipts for boundary snapshots."""

from __future__ import annotations


def snapshot_receipt(snapshot: dict, repo_root: str, out_path: str) -> dict:
    """Return the exact verify handoff for one captured review window."""
    window = snapshot["window"]
    return {
        "ok": True,
        "out": out_path,
        "verify_before": out_path,
        "verify_args": [
            "verify",
            "--repo-root",
            repo_root,
            "--before",
            out_path,
            "--window-id",
            window["id"],
        ],
        "head": snapshot["head"],
        "window": window,
    }
