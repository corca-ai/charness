#!/usr/bin/env python3
"""Run nose and parse/summarize its versioned JSON report.

Split out of `inventory_nose_clones.py` (cohesion + length cap): turning a nose
invocation into a normalized `{status, families, scope, ranking, ...}` payload is
its own concern, separate from command building, the advisory-interpretation
contract, and rendering. The nose command + JSON shape are pinned here — the one
resolver shared by the clone advisory and the dup-ratchet gate.

nose 0.13.3 removed the deprecated `nose scan` subcommand, so the code path runs
`nose query` instead. The migration is isolated to this resolver:

- `nose query --root P1 --root P2 ... all top=N sort=K --mode M --min-size S
  --format json`. `all`, `top=`, and `sort=` are query TERMS (bare args, which
  `--root` mode treats as terms), NOT flags — passing `--top`/`--sort` to `query`
  errors and yields zero families.
- nose 0.14.0 `--root/-r` takes EVERY scope root in one invocation, so the whole
  scope is analyzed as a single corpus in one `collect_families` call (no per-root
  loop). A cross-root clone family is therefore GROUPED, not split per path —
  unlike the pre-0.14.0 per-root-loop-and-merge, which missed cross-root clones.
  This is a deliberate semantic choice (global clustering); identities are
  scanner-version- AND scope-model-scoped, so re-baseline when switching it.
- The report SHAPES (which key holds the families, and when a report establishes no
  family set at all) live in `nose_report_shape_lib`; `extract_report` /
  `report_shape_error` are re-exported here so consumers keep one import site.
- Family identity is `id` in query output (a stable 16-hex content hash), named
  `family_id` in the removed `scan` output; `family_summary` normalizes to
  `family_id`. Locations use `start`/`end` (query) vs `start_line`/`end_line`
  (scan). `query` carries no top-level `tool_version`, so it is stamped from
  `nose --version` (`resolve_tool_version`) when the report omits it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _load_sibling(module_name: str) -> Any:
    """Load a sibling without coupling this standalone library to skill bootstrap."""
    import importlib.util

    path = Path(__file__).resolve().with_name(f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_fingerprint = _load_sibling("nose_fingerprint_lib")
_tool = _load_sibling("nose_tool_lib")
_shape = _load_sibling("nose_report_shape_lib")
NOSE_TIMEOUT_SECONDS = _tool.NOSE_TIMEOUT_SECONDS
# Re-exported so existing consumers (and the report-shape tests) keep one import site for
# "turn nose's stdout into a family set"; the shapes themselves live in one module now.
extract_report = _shape.extract_report
raw_family_entries = _shape.raw_family_entries
report_shape_error = _shape.report_shape_error


def tool_version_skew(baseline_version: str | None, live_version: str | None) -> str | None:
    """Operator warning when a stored baseline was minted under a different nose
    version than the one now scanning, else ``None``.

    Since Slice 4 the gate/advisory identity is a gate-computed content fingerprint, not
    nose's id — but the clone family SET (which spans nose groups at a given mode/min-size)
    is still nose-version-scoped, so a nose bump can regroup families and drift the stored
    fingerprint set even though each family's identity is offset/path-stable. An unrecorded
    skew therefore still makes the stored set stale. A MISSING stamp on either side returns
    ``None`` (it is "unknown", NOT a mismatch): legacy unstamped baselines do not warn until
    a deliberate re-baseline stamps the version, after which a future bump surfaces here. The
    warning never degrades a gate — it explains a block rather than suppressing one
    (suppressing would hide real new duplication)."""
    base = str(baseline_version or "").strip()
    live = str(live_version or "").strip()
    if base and live and base != live:
        return (
            f"nose version skew: baseline written under nose {base}, now scanning with "
            f"nose {live}. The clone family SET is nose-version-scoped (a bump can regroup "
            "families), so a re-baseline (--write-baseline) is the honest fix — do NOT treat "
            "the drifted fingerprints as new duplication."
        )
    return None


def resolve_tool_version(nose_bin: str) -> str:
    """Best-effort `nose --version` string ("" on failure). The `query` JSON omits
    the version that the removed `scan` report carried, so the advisory stamps it
    from here when a report does not supply one."""
    return _tool.version_text(_tool.probe_nose_version(nose_bin).get("version"))


def build_query_command(
    nose_bin: str,
    paths: list[str],
    *,
    mode: str,
    min_size: int,
    top: int,
    sort: str,
    exclude: list[str] | None = None,
    ignore_file: str | None = None,
) -> list[str]:
    """One `nose query` command over the FULL scope via nose 0.14.0 `--root/-r`
    (every root in a single invocation). `all`/`top=`/`sort=` are query TERMS
    (bare args, which `--root` mode treats as terms); `--mode`/`--min-size`/
    `--exclude`/`--ignore-file`/`--format` are flags. A single root via `--root` is
    identical to the legacy positional form, so this one builder serves both."""
    if not paths:
        # Fail loud: a `nose query` with no `--root` would scan the default tree
        # (the WRONG scope), silently. Callers guard with `or DEFAULT_PATHS`; this
        # backstops a future caller that forgets, instead of a wrong-scope scan.
        raise ValueError("build_query_command requires at least one scope root")
    command = [nose_bin, "query"]
    for root in paths:
        command.extend(["--root", root])
    command.extend([
        "all",
        f"top={top}",
        f"sort={sort}",
        "--mode",
        mode,
        "--min-size",
        str(min_size),
    ])
    for pattern in exclude or []:
        command.extend(["--exclude", pattern])
    if ignore_file:
        command.extend(["--ignore-file", ignore_file])
    command.extend(["--format", "json"])
    return command


def family_identity(family: dict[str, Any]) -> str | None:
    """Normalized clone-family identity: query's `id` or scan's `family_id`."""
    identity = family.get("family_id") or family.get("id")
    return str(identity) if identity else None


def collect_families(
    repo_root: Path,
    nose_bin: str,
    paths: list[str],
    *,
    mode: str,
    min_size: int,
    top: int,
    sort: str,
    exclude: list[str] | None = None,
    ignore_file: str | None = None,
) -> dict[str, Any]:
    """Run ONE `nose query` over the full multi-root scope (nose 0.14.0 `--root`)
    and return the family set. The scope is analyzed as a single corpus, so a
    cross-root clone family is GROUPED rather than split per path. A nose error
    makes the WHOLE result `error` so a consumer degrades to advisory rather than
    under-reporting a broken scan as a clean pass. Each family carries a normalized
    `family_id`."""
    command = build_query_command(
        nose_bin, paths, mode=mode, min_size=min_size, top=top, sort=sort,
        exclude=exclude, ignore_file=ignore_file,
    )
    result = run_nose(repo_root, command)
    if result["status"] == "error":
        return {
            "status": "error",
            "exit_code": result.get("exit_code") or 1,
            "stdout": "",
            "stderr": result.get("stderr", ""),
            "families": [],
            "tool_version": result.get("tool_version") or resolve_tool_version(nose_bin),
            "scope": {"paths": list(paths)},
            "ranking": {"total_families": 0, "shown_families": 0},
        }
    keyed: dict[str, dict[str, Any]] = {}
    unkeyed: list[dict[str, Any]] = []
    for family in result["families"]:
        # Stamp the offset/path-independent content fingerprint once here (Slice 4),
        # from the RAW full `locations`, the same way family_id is stamped. Every
        # consumer (gate, advisory, overlay seed via family_summary) reads this one
        # field instead of recomputing it, so there is no per-consumer truncation
        # (family_summary's sample_locations caps at 6) and no three-way divergence.
        # Absent (None) when a member span is unreadable -> the gate degrades whole.
        # The per-member hash list is stamped alongside it (schema v3, item 5 slice
        # D): the gate baseline stores it per family, and the reduction pre-pass
        # diffs it as a multiset — computed here, once, from the same locations, so
        # it can never disagree with the fingerprint that hashes it.
        member_hashes = _fingerprint.family_member_hashes(family, repo_root)
        if member_hashes:
            family.setdefault("family_member_hashes", member_hashes)
            family.setdefault("family_fingerprint", _fingerprint.fingerprint_from_member_hashes(member_hashes))
        identity = family_identity(family)
        if identity:
            family.setdefault("family_id", identity)
            keyed.setdefault(identity, family)
        else:
            unkeyed.append(family)
    families = list(keyed.values()) + unkeyed
    tool_version = result.get("tool_version") or resolve_tool_version(nose_bin)
    ranked = (result.get("ranking") or {}).get("total_families")
    return {
        "status": "findings" if families else "clean",
        "exit_code": result.get("exit_code", 0),
        "stdout": "",
        "stderr": "",
        "families": families,
        "tool_version": tool_version,
        "scope": {"paths": list(paths)},
        "ranking": {
            "total_families": ranked if isinstance(ranked, int) else len(families),
            "shown_families": len(families),
        },
    }


def family_summary(family: dict[str, Any]) -> dict[str, Any]:
    """Normalize one clone family across scan (`family_id`/`start_line`/`dup_lines`)
    and query (`id`/`start`/derived) shapes. `dup_lines` is derived from the member
    location spans when the report omits it (query carries no `dup_lines`); it stays
    a display proxy, never a reduction target."""
    locations = family.get("locations", [])
    files = []
    derived_dup_lines = 0
    have_span = False
    if isinstance(locations, list):
        for location in locations:
            if not isinstance(location, dict):
                continue
            file = location.get("file")
            if not isinstance(file, str):
                continue
            start = location.get("start_line", location.get("start"))
            end = location.get("end_line", location.get("end"))
            if isinstance(start, int) and isinstance(end, int):
                derived_dup_lines += max(0, end - start + 1)
                have_span = True
            if len(files) < 6:
                files.append(
                    {
                        "file": file,
                        "start_line": start,
                        "end_line": end,
                        "name": location.get("name"),
                        "kind": location.get("kind"),
                    }
                )
    dup_lines = family.get("dup_lines")
    if not isinstance(dup_lines, int):
        dup_lines = derived_dup_lines if have_span else None
    shared_lines = family.get("shared_lines")
    if not isinstance(shared_lines, int):
        shared_lines = family.get("shared")
    return {
        "family_id": family.get("family_id") or family.get("id"),
        "family_fingerprint": family.get("family_fingerprint"),
        "value": family.get("value"),
        "members": family.get("members"),
        "files": family.get("files"),
        "modules": family.get("modules"),
        "languages": family.get("languages"),
        "mean_score": family.get("mean_score"),
        "dup_lines": dup_lines,
        "shared_lines": shared_lines,
        "params": family.get("params"),
        "sample_locations": files,
    }


def run_nose(repo_root: Path, command: list[str]) -> dict[str, Any]:
    result = _tool.run_json_query(repo_root, command)
    error_kind = result.get("error_kind")
    if error_kind == "timeout":
        return {
            "status": "error",
            "exit_code": 124,
            "stdout": result["stdout"],
            "stderr": f"nose timed out after {NOSE_TIMEOUT_SECONDS}s",
            "families": [],
            "tool_version": "",
        }
    if error_kind == "oserror":
        # An explicitly-set-but-invalid NOSE_BIN (resolve_nose_bin returns the
        # override unchecked) must degrade to advisory, not crash — FD8: a broken
        # tool never false-blocks. Symmetric with resolve_tool_version's guard.
        return {
            "status": "error",
            "exit_code": 1,
            "stdout": "",
            "stderr": f"nose could not be executed: {result.get('error', '')}",
            "families": [],
            "tool_version": "",
        }
    if error_kind == "empty-output":
        return {
            "status": "error",
            "exit_code": result["exit_code"] or 1,
            "stdout": "",
            "stderr": "nose emitted no output; the scan produced nothing to read",
            "families": [],
            "tool_version": "",
        }
    if error_kind == "invalid-json":
        return {
            "status": "error",
            "exit_code": result["exit_code"],
            "stdout": result["stdout"],
            "stderr": f"nose emitted invalid JSON: {result.get('error', '')}; stderr: {result['stderr']}",
            "families": [],
            "tool_version": "",
        }
    families, tool_version, scope, ranking = extract_report(result["payload"])
    status = "findings" if families else "clean"
    stderr = result["stderr"]
    shape_error = report_shape_error(result["payload"], families, ranking)
    if shape_error:
        status = "error"
        stderr = f"{shape_error}; nose stderr: {stderr}" if stderr else shape_error
    if result["status"] == "error":
        status = "error"
    return {
        "status": status,
        "exit_code": result["exit_code"],
        "stdout": "",
        "stderr": stderr,
        "families": families,
        "tool_version": tool_version,
        "scope": scope,
        "ranking": ranking,
    }
