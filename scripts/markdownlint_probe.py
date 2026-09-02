#!/usr/bin/env python3
"""The markdownlint-cli2 engine adapter: resolve it, run it, and prove it RAN.

Split out of ``check_doc_authoring_preflight.py`` when that file hit its length cap.
The unit is cohesive rather than a spill: everything here is about ONE external engine
-- which command reaches it (mirroring ``check-markdown.sh``'s tiers), whether that
command actually reached it, and how its output parses. The preflight consumes the
result; it does not need to know how markdownlint is found.

The central distinction this module exists to keep is RESOLUTION vs EXECUTION. A
resolved command is not a run engine, and treating the two as one made a proof surface
report a rule class as forecast-and-clean when it had never been measured.
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Any

try:
    from scripts.subprocess_guard import run_process
except ModuleNotFoundError:  # executed directly from scripts/
    from subprocess_guard import run_process

# markdownlint-cli2's first output line, on every run it makes: ``markdownlint-cli2 v0.21.0
# (markdownlint v0.40.0)``. It is the only evidence available here that the ENGINE ran, as
# opposed to a wrapper that resolved and then refused.
_MARKDOWNLINT_BANNER_RE = re.compile(r"^markdownlint-cli2 v\S+")

# A markdownlint-cli2 per-violation line: ``<file>:<line>[:<col>] error MDxxx/rule desc``.
_MARKDOWNLINT_LINE_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+)(?::(?P<col>\d+))?\s+(?:error\s+)?(?P<rule>MD\d+)/(?P<name>\S+)\s*(?P<desc>.*)$"
)


def resolve_markdownlint_cmd(repo_root: Path | None = None) -> list[str] | None:
    """Mirror ``check-markdown.sh``'s three tiers. Returns None when none resolve.

    The mirror is the point, and it had drifted: this function claimed to mirror the
    shell gate while skipping the ``node_modules/.bin`` tier and spelling the fallback
    ``npm exec --`` with no ``--no``. #630 is filed against exactly that spelling —
    without ``--no``, npm reaches the registry and pays the network round trip on any
    machine where the binary is not on PATH — and this file is emitted as an operator
    command by quality preflight and the Goal Run planner, so the unguarded
    spelling was live, not dead. A docstring
    asserting a mirror is not one; the tiers are duplicated here in the same order the
    shell gate resolves them.
    """
    if shutil.which("markdownlint-cli2"):
        return ["markdownlint-cli2"]
    if repo_root is not None:
        local = repo_root / "node_modules" / ".bin" / "markdownlint-cli2"
        if os.access(local, os.X_OK):
            return [str(local)]
    if shutil.which("npm"):
        return ["npm", "exec", "--no", "--", "markdownlint-cli2"]
    return None


def markdownlint_engine_ran(stdout: str, stderr: str, *, found_violations: bool = False) -> bool:
    """Did markdownlint-cli2 itself run, or only the wrapper that would launch it?

    Blind class, stated before the acceptance. This reads OUTPUT, so:

    * It cannot see an engine that ran and printed NOTHING recognisable. The banner is
      the primary signal and ``found_violations`` the secondary one, so a consumer repo
      setting ``noBanner`` still reports a run whenever violations were parsed — but a
      ``noBanner`` repo on a CLEAN file reads as a non-run. That direction is deliberate:
      unforecast, never falsely clean.
    * It cannot see an engine whose findings were REDIRECTED. ``outputFormatters`` in a
      consumer's ``.markdownlint-cli2.jsonc`` can send violations to a file, leaving the
      banner and no parseable lines — which this reports as ran-and-clean on a file with
      real violations. Not live in this repo (its config sets only ``globs`` and
      ``MD013``), and closing it needs the formatter config read, not another heuristic.
    * It cannot see WHY a non-run happened; the caller gets a boolean, and the operator
      gets the gate's own message.

    Why it exists: ``resolve_markdownlint_cmd``'s npm tier resolves whenever ``npm`` is
    on PATH, which says nothing about whether the package is reachable. ``npm exec --no``
    — the spelling #630 asks for, and the one this mirror already uses — refuses rather
    than installing, so on a machine with no local ``markdownlint-cli2`` it exits 1 having
    linted nothing. Keying availability on resolution reported that as ``available: True``
    with zero findings: a proof surface saying the markdownlint class was forecast and
    clean, when it was never run. That is the shape CI failed on (Quality Core,
    ``1240348b7``); the fixture repos are under ``tmp_path``, so the ``node_modules/.bin``
    tier cannot hit and the npm tier is always the one taken there.
    """
    if found_violations:
        return True
    return any(
        _MARKDOWNLINT_BANNER_RE.match(line.strip())
        for stream in (stdout, stderr)
        for line in stream.splitlines()
    )


def parse_markdownlint_findings(stdout: str, stderr: str, rel: str) -> list[dict[str, Any]]:
    """Violations the engine reported for ``rel``, from either stream.

    Extracted so callers that need the same "did it run" answer -- notably the no-drift
    test helper -- derive ``found_violations`` from the SAME parse production uses. When
    the helper spelled its own weaker check, a banner-suppressed consumer config made
    production report a correct forecast while the helper called it unmeasured.
    """
    findings: list[dict[str, Any]] = []
    for stream in (stderr, stdout):
        for line in stream.splitlines():
            match = _MARKDOWNLINT_LINE_RE.match(line.strip())
            if not match or match.group("file") != rel:
                continue
            findings.append(
                {
                    "line": int(match.group("line")),
                    "col": int(match.group("col")) if match.group("col") else None,
                    "rule": match.group("rule"),
                    "name": match.group("name"),
                    "desc": match.group("desc").strip(),
                }
            )
    return findings


def collect_markdownlint(repo_root: Path, rel: str) -> dict[str, Any]:
    """Run markdownlint-cli2 on the single target file, parsing its findings.

    The same engine + ``.markdownlint-cli2.jsonc`` config the markdown gate uses
    (config is auto-discovered from ``repo_root``). markdownlint-cli2 writes the
    banner to stdout and per-violation lines to stderr; scan both for the target.

    Single-file scope (``--no-globs rel``) is verdict-equivalent to the gate's
    full-list lint because every markdownlint rule in the repo config is
    per-file; a hypothetical cross-file rule (e.g. link-reciprocity) would need
    this to widen to the linked set.
    """
    cmd = resolve_markdownlint_cmd(repo_root)
    if cmd is None:
        return {"available": False, "findings": []}
    proc = run_process(
        [*cmd, "--no-globs", rel],
        cwd=repo_root,
        timeout_seconds=None,
    )
    findings = parse_markdownlint_findings(proc.stdout, proc.stderr, rel)
    # Parse BEFORE deciding whether the engine ran: parsed violations are as strong a
    # proof of a run as the banner, and guarding the parse instead would discard real
    # findings from a banner-suppressed (`noBanner`) consumer repo -- turning a correct
    # block into a clean forecast, which is this guard's own failure class inverted.
    if not markdownlint_engine_ran(proc.stdout, proc.stderr, found_violations=bool(findings)):
        return {"available": False, "findings": [], "resolved_command": cmd}
    return {"available": True, "findings": findings}
