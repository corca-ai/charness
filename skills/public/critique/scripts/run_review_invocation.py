#!/usr/bin/env python3
"""Build the portable reviewer-worker invocation from one prepared run."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def runner_command(
    support: Any,
    package: dict[str, Path],
    paths: dict[str, Path],
    *,
    root: Path,
    backend: str,
    scope: str,
    attempt: str,
    packet_sha: str,
    input_sha: str,
    parent_receipt: str,
    boundary_mode: str,
    boundary_sha: str | None,
) -> list[str]:
    """Bind one worker process to the prepared packet and artifact paths."""

    def relative(key: str) -> str:
        return support.relative(root, paths[key])

    command = [
        sys.executable,
        str(package["runner"]),
        "--repo-root", str(root),
        "--backend", backend,
        "--prompt-file", relative("prompt"),
        "--capability-file", relative("capability"),
        "--scope", scope,
        "--packet-identity", packet_sha,
        "--reviewed-input-identity", input_sha,
        "--attempt-id", attempt,
        "--parent-receipt-identity", parent_receipt,
        "--boundary-mode", boundary_mode,
        "--ledger-file", relative("ledger"),
        "--output-file", relative("output"),
        "--receipt-file", relative("receipt"),
        "--report-file", relative("report"),
        "--schema-file", relative("schema"),
        "--stdout-file", relative("backend_stdout"),
        "--stderr-file", relative("backend_stderr"),
        "--run-id", "run-" + attempt,
    ]
    if boundary_sha is not None:
        command.extend(["--boundary-fingerprint", boundary_sha])
    return command
