#!/usr/bin/env python3
"""Shared cross-surface probe for the boundary-ownership checkpoint (#408).

Given the repo-owned probe config — surface ids into ``.agents/surfaces.json``
and/or raw path globs — plus a set of changed paths, decide whether a change
touches a cross-surface path. Both consumers share this one core:

- the critique validator's severity upgrade (a hit rejects a bare
  ``single-surface`` verdict), and
- the impl stop-gate escalation hook (a hit forces a standalone critique).

The taxonomy (which paths are cross-surface) stays repo-owned via the adapter;
this portable core never names a surface itself. An empty config never hits, so
the probe is opt-in and a repo that configures nothing keeps the always-brief +
presence-floor without the objective override (spec DBD-4)."""

from __future__ import annotations

from pathlib import Path

from runtime_bootstrap import import_repo_module

_surfaces_lib = import_repo_module(__file__, "scripts.surfaces_lib")
_critique_adapter_lib = import_repo_module(__file__, "scripts.critique_adapter_lib")

BOUNDARY_GLOBS_KEY = "boundary_cross_surface_globs"
BOUNDARY_SURFACES_KEY = "boundary_cross_surface_surfaces"


def probe_config_from_adapter(adapter_data: dict) -> dict[str, list[str]]:
    """Extract the (globs, surfaces) probe config from an adapter's data dict,
    tolerating absent keys and non-list values (treated as empty)."""

    def _as_list(value: object) -> list[str]:
        return [str(item) for item in value] if isinstance(value, list) else []

    return {
        "globs": _as_list(adapter_data.get(BOUNDARY_GLOBS_KEY)),
        "surfaces": _as_list(adapter_data.get(BOUNDARY_SURFACES_KEY)),
    }


def cross_surface_hit(
    repo_root: Path,
    changed_paths: list[str],
    *,
    surfaces: list[str] | None = None,
    globs: list[str] | None = None,
) -> bool:
    """True iff any changed path matches a configured cross-surface glob OR is a
    source/derived path of a configured surface id. Empty config -> always False
    (opt-in). Unknown surface ids are ignored (they resolve to ``unresolved`` and
    simply cannot match); the adapter validator is where a typo surfaces."""
    surfaces = list(surfaces or [])
    globs = list(globs or [])
    if not surfaces and not globs:
        return False
    if globs and any(_surfaces_lib.path_matches_patterns(path, globs) for path in changed_paths):
        return True
    if surfaces:
        manifest = _surfaces_lib.load_surfaces(repo_root, required=False)
        if manifest is not None:
            declared = set(_surfaces_lib.resolve_trigger_surfaces(manifest, surfaces)["declared"])
            matched_ids = {
                surface["surface_id"]
                for surface in _surfaces_lib.match_surfaces(manifest, changed_paths)["matched_surfaces"]
            }
            if matched_ids & declared:
                return True
    return False


def resolve_changed_paths(repo_root: Path, changed_path: list[str] | None, changed_ref: str | None) -> list[str]:
    """The changed paths for the probe: explicit ``changed_path`` wins, else the
    ``changed_ref`` git range, else the working-tree diff."""
    if changed_path is not None:
        return list(changed_path)
    if changed_ref:
        return _surfaces_lib.collect_changed_paths_for_ref(repo_root, changed_ref)
    return _surfaces_lib.collect_changed_paths(repo_root)


def resolve_hit(
    repo_root: Path, *, changed_path: list[str] | None = None, changed_ref: str | None = None
) -> tuple[bool, list[str], dict[str, list[str]]]:
    """Resolve the changed paths, read the critique adapter's probe config, and
    return ``(triggered, changed_paths, probe_config)``. The one home both the
    critique validator's severity upgrade and the impl stop-gate hook call so the
    resolve-and-probe logic lives in a single place."""
    changed = resolve_changed_paths(repo_root, changed_path, changed_ref)
    probe = probe_config_from_adapter(_critique_adapter_lib.load_adapter(repo_root)["data"])
    triggered = cross_surface_hit(repo_root, changed, surfaces=probe["surfaces"], globs=probe["globs"])
    return triggered, changed, probe
