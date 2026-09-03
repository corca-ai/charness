#!/usr/bin/env python3
"""Whether the generated plugin mirror is fresh, before a gate run reads it.

The materialized ``plugins/<pkg>`` tree is a DERIVED surface: it is regenerated
from ``skills/`` and ``scripts/`` by the exporter and is gitignored here, so any
source edit makes it stale until the exporter runs again. Around thirty standing
tests read that on-disk tree -- byte-comparing a mirrored script against its
source, executing the mirrored copy, scanning the whole export -- so a stale
mirror does not read as "regenerate me". It reads as a scattering of unrelated
failures in tests that name neither the exporter nor the edit, and four sessions
were lost chasing exactly that.

This module is the one place that decides what to do about it. A writing run
regenerates; a read-only run validates and REFUSES while naming the exact
regenerate command, which is a refusal an operator can act on rather than a red
test they must first diagnose. Both the quality engine's preamble and the
standing pytest runner call it, so the two entry points into the suite cannot
disagree about mirror freshness.

Two guards keep this inert for a consuming repo, and both must hold: a declared
packaging manifest whose resolved plugin root is inside this repo, and a plugin
root that git actually ignores. A consumer's unrelated ``plugins/`` directory is
never a reason to delete or regenerate anything.

Deliberately stdlib-only and I/O-injected: the caller supplies ``probe`` (the
repo's ONE child-process owner, ``scripts.core.subprocess_guard.run_process``,
bound to that caller's cwd and environment) and ``log``. Neither caller's
process model is assumed here, and the tests drive the decision without spawning
anything.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

SYNC_SCRIPT = "scripts/plugin_export/sync_root_plugin_manifests.py"
VALIDATE_SCRIPT = "scripts/plugin_export/validate_packaging.py"

Probe = Callable[[list[str]], subprocess.CompletedProcess[str]]
Log = Callable[[str], None]


def regenerate_command(repo_root: Path) -> str:
    """The exact command an operator can paste to refresh the mirror."""
    return f"python3 {SYNC_SCRIPT} --repo-root {repo_root}"


def ensure_plugin_mirror(
    repo_root: Path,
    *,
    read_only: bool,
    probe: Probe,
    log: Log,
) -> int:
    """Refresh (writing run) or verify (read-only run) the generated plugin mirror.

    Returns a process-style code: ``0`` to proceed, non-zero to stop. In
    read-only mode validation generates into a temporary directory internally and
    compares bytes without mutating the checkout, so a read-only lane stays
    read-only; the caller's job on a non-zero return is to stop before the work
    that would have observed the stale mirror.
    """
    manifest_path = repo_root / "packaging" / "charness.json"
    if not manifest_path.is_file():
        return 0
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        relative_root = manifest["codex"]["repo_marketplace"]["materialized_source_path"]
        plugin_root = (repo_root / str(relative_root).removeprefix("./")).resolve()
        plugin_root.relative_to(repo_root.resolve())
    except (OSError, KeyError, TypeError, ValueError) as exc:
        log(f"could not resolve packaged plugin root: {exc}")
        return 1
    relative_plugin_root = plugin_root.relative_to(repo_root.resolve()).as_posix()
    ignored = probe(
        [
            "git",
            "check-ignore",
            "--no-index",
            "-q",
            "--",
            relative_plugin_root,
        ]
    )
    if ignored.returncode != 0:
        return 0
    command = [
        "python3",
        VALIDATE_SCRIPT if read_only else SYNC_SCRIPT,
        "--repo-root",
        str(repo_root),
    ]
    if read_only:
        command.append("--validate-export")
    result = probe(command)
    if result.returncode != 0:
        log("plugin manifest preamble failed")
        _replay(result.stdout, log)
        _replay(result.stderr, log)
        if read_only:
            log(f"regenerate with `{regenerate_command(repo_root)}`")
    return result.returncode


def _replay(stream: str, log: Log) -> None:
    """Forward a failed child's output line by line so the caller's prefix holds."""
    for line in stream.splitlines():
        log(line)
