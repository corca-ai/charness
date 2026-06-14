#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

# Default scan surface: the canonical repo-owned TS/JS source. The plugin mirror
# under plugins/charness/ is a generated copy (would double-count) and vendored
# third-party code is out of scope, so neither is a default path.
DEFAULT_PATHS = ("scripts/agent-runtime",)
PRY_VERSION_TIMEOUT_SECONDS = 10
PRY_MAP_TIMEOUT_SECONDS = 120


def _pry_binary() -> str | None:
    """Resolve the pry binary, honoring the PRY_BIN maintainer-local override."""
    override = os.environ.get("PRY_BIN")
    if override:
        return override if Path(override).exists() else None
    return shutil.which("pry")


def _pry_version(binary: str) -> str | None:
    try:
        completed = subprocess.run(
            [binary, "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=PRY_VERSION_TIMEOUT_SECONDS,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _run_pry_map(binary: str, repo_root: Path, path: str) -> dict:
    target = repo_root / path
    try:
        completed = subprocess.run(
            [binary, "map", str(target)],
            capture_output=True,
            text=True,
            check=False,
            timeout=PRY_MAP_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"pry map {path} timed out after {PRY_MAP_TIMEOUT_SECONDS}s") from exc
    if completed.returncode != 0:
        raise RuntimeError(
            f"pry map {path} exited with status {completed.returncode}: {completed.stderr.strip()}"
        )
    return json.loads(completed.stdout)


def _backlog_entry(path: str, finding: dict) -> dict:
    return {
        "path": path,
        "file": finding.get("file"),
        "line": finding.get("line"),
        "col": finding.get("col"),
        "kind": finding.get("kind"),
        "reason": finding.get("reason"),
        "class": finding.get("class"),
    }


def inventory_testability_surface(repo_root: Path, *, paths: list[str]) -> dict:
    """Run pry over the repo's TS/JS surface and return its welded-at-demand backlog.

    pry surfaces *welded boundary calls with no injection seam* (a testability
    backlog, NOT a bug list). The `demand=true` substitution-demand subset is the
    ranked backlog. This inventory is advisory and must never fail standing
    quality: a missing or erroring `pry` degrades to a reported state.
    """
    payload: dict = {
        "schema_version": 1,
        "scope": "pry-testability-surface",
        "engine": "pry",
        "repo_root": str(repo_root),
        "paths": list(paths),
        "advisory_notes": [
            "pry surfaces welded boundary calls with no injection seam; this is a "
            "testability backlog, not a bug list, and must never fail standing quality.",
            "The demand=true substitution-demand subset is the ranked backlog; "
            "welded calls outside it are lower-priority context.",
        ],
    }
    binary = _pry_binary()
    if binary is None:
        payload.update(
            status="degraded",
            reason="pry binary not on PATH (and PRY_BIN unset or missing)",
            install_hint=(
                "See integrations/tools/pry.json or "
                "https://github.com/corca-ai/pry — advisory input to quality; "
                "absence omits the welded-at-demand testability backlog."
            ),
            pry_version=None,
            scanned={},
            demand_backlog=[],
            totals={"files_scanned": 0, "welded": 0, "seamed": 0, "demand_total": 0, "welded_at_demand": 0},
        )
        return payload

    version = _pry_version(binary)
    scanned: dict[str, dict] = {}
    demand_backlog: list[dict] = []
    totals = {"files_scanned": 0, "welded": 0, "seamed": 0, "demand_total": 0, "welded_at_demand": 0}
    errors: list[str] = []
    for path in paths:
        try:
            report = _run_pry_map(binary, repo_root, path)
        except RuntimeError as exc:
            errors.append(str(exc))
            continue
        summary = report.get("summary", {})
        demand = summary.get("substitution_demand_subset", {})
        scanned[path] = {
            "files_scanned": summary.get("files_scanned", 0),
            "welded": summary.get("welded", 0),
            "seamed": summary.get("seamed", 0),
            "demand_total": demand.get("total", 0),
            "demand_welded": demand.get("welded", 0),
            "demand_seamed": demand.get("seamed", 0),
        }
        totals["files_scanned"] += summary.get("files_scanned", 0)
        totals["welded"] += summary.get("welded", 0)
        totals["seamed"] += summary.get("seamed", 0)
        totals["demand_total"] += demand.get("total", 0)
        for finding in report.get("findings", []):
            # The actionable backlog is welded-AT-demand: a high-demand boundary
            # with no injection seam. A demand finding already classed `seamed`
            # is testable, so it is not backlog.
            if finding.get("demand") and finding.get("class") == "welded":
                demand_backlog.append(_backlog_entry(path, finding))
    totals["welded_at_demand"] = len(demand_backlog)

    if errors and not scanned:
        payload.update(
            status="degraded",
            reason="; ".join(errors),
            pry_version=version,
            scanned={},
            demand_backlog=[],
            totals=totals,
        )
        return payload

    payload.update(
        status="ok",
        pry_version=version,
        scanned=scanned,
        demand_backlog=sorted(
            demand_backlog,
            key=lambda e: (e["path"], e.get("file") or "", e.get("line") or 0),
        ),
        totals=totals,
    )
    if errors:
        payload["partial_errors"] = errors
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="pry-backed testability-surface inventory for quality (advisory).",
    )
    parser.add_argument(
        "--repo-root", type=Path, required=True, help="Repo root for the pry testability inventory"
    )
    parser.add_argument(
        "--path",
        action="append",
        default=None,
        help="TS/JS file or directory to analyze (repeatable). "
        "Defaults to the canonical agent-runtime source.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the full inventory payload as JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the JSON payload to this path in addition to stdout.",
    )
    args = parser.parse_args()

    paths = list(args.path) if args.path else list(DEFAULT_PATHS)
    payload = inventory_testability_surface(args.repo_root.resolve(), paths=paths)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.json:
        print(rendered)
    else:
        if payload["status"] == "degraded":
            print(f"Testability surface: degraded ({payload['reason']})")
        else:
            totals = payload["totals"]
            prefix = "ADVISORY: " if totals["welded_at_demand"] else ""
            print(
                f"{prefix}Testability surface: {totals['welded_at_demand']} welded-at-demand "
                f"backlog item(s) of {totals['welded']} welded boundary call(s) across "
                f"{totals['files_scanned']} file(s) ({payload['pry_version']})"
            )
            for entry in payload["demand_backlog"]:
                print(
                    f"  - {entry['path']}/{entry['file']}:{entry['line']} "
                    f"{entry['kind']} ({entry['reason']})"
                )
    return 0


if __name__ == "__main__":  # pragma: no cover - thin CLI dispatch; main() is unit-tested
    raise SystemExit(main())
