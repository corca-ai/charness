#!/usr/bin/env python3
"""Shared cross-surface probe for the boundary-ownership checkpoint (#408).

Given the repo-owned probe config — surface ids into ``.agents/surfaces.json``
and/or raw path globs — plus a set of changed paths, decide whether a change
touches a cross-surface path. The critique validator uses this shared core:

- the critique validator's severity upgrade (a hit rejects a bare
  ``single-surface`` verdict).

The taxonomy (which paths are cross-surface) stays repo-owned via the adapter;
this portable core never names a surface itself. An empty config never hits, so
the probe is opt-in and a repo that configures nothing keeps the always-brief +
presence-floor without the objective override (spec DBD-4) -- provided its
adapter READ. A repo whose adapter the loader refused gets ``not-established``
rather than that opt-in silence, because an unread adapter cannot declare an
opt-out any more than it can declare a probe.

Scoped claim, because a round-3 review found the unscoped one false: that refusal
holds for ``resolve_probe_state`` and for the critique validator's entry branch.
It does NOT hold for a partially-valid adapter reaching
``critique_enforcement_scope.resolve_cross_surface_scope``'s post-hit path, which
consumes ``resolve_hit`` and flattens the typed state to a bare bool, so a
downgraded state still renders as ``evaluated ... (no match)`` there. Closing that
means giving the second consumer the typed state instead of the flattened one."""

from __future__ import annotations

from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_surfaces_lib = import_repo_module(__file__, "scripts.adapters.surfaces_lib")
_critique_adapter_lib = import_repo_module(__file__, "scripts.review.critique_adapter_lib")
_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")

BOUNDARY_GLOBS_KEY = "boundary_cross_surface_globs"
BOUNDARY_SURFACES_KEY = "boundary_cross_surface_surfaces"

# The probe's typed outcome vocabulary (#622). Deliberately the SAME three words
# `scripts/review/critique_enforcement_scope.py` already uses for `CrossSurfaceScope` and the
# boundary probes use for typed evaluation scope -- a fourth private spelling
# of "we could not tell" is how the concept drifts back apart.
#
# It lives HERE as the shared implementation for the critique validator because
# the validator alone could not close the hole:
# `resolve_cross_surface_scope` typed the states it could see from OUTSIDE the probe (no
# config, no changed scope) and then delegated the rest to `cross_surface_hit`, which
# returned a bare `False` when `.agents/surfaces.json` was absent. A repo that configured
# `boundary_cross_surface_surfaces` and had no manifest therefore resolved to
# `evaluated (no match)` -- a positive claim that the probe ran -- and silently disarmed
# the #408 5b tooth in `validate-critique-artifacts`.
PROBE_EVALUATED = "evaluated"
PROBE_NOT_CONFIGURED = "not-configured"
PROBE_NOT_ESTABLISHED = "not-established"


def probe_config_from_adapter(adapter_data: dict) -> dict[str, list[str]]:
    """Extract the (globs, surfaces) probe config from an adapter's data dict,
    tolerating absent keys and non-list values (treated as empty)."""

    def _as_list(value: object) -> list[str]:
        return [str(item) for item in value] if isinstance(value, list) else []

    return {
        "globs": _as_list(adapter_data.get(BOUNDARY_GLOBS_KEY)),
        "surfaces": _as_list(adapter_data.get(BOUNDARY_SURFACES_KEY)),
    }


def cross_surface_probe_state(
    repo_root: Path,
    changed_paths: list[str],
    *,
    surfaces: list[str] | None = None,
    globs: list[str] | None = None,
) -> dict[str, object]:
    """Run the probe and report WHICH QUESTION it managed to answer, not just the answer.

    Returns ``{"state", "hit", "scanned_paths", "undetermined_reasons",
    "unresolved_surfaces"}`` where ``state`` is one of ``evaluated`` /
    ``not-configured`` / ``not-established``, and ``hit`` is a verdict ONLY under
    ``evaluated``.

    Three conditions used to collapse into the same bare ``False`` this function
    replaces (#622):

    - no config at all -- the opt-in design (spec DBD-4); genuinely "no override",
      not "could not tell", so it stays exit-0 for callers and keeps ``hit: False``;
    - a configured surface id with NO ``.agents/surfaces.json`` on disk -- the probe
      could not resolve a single id, so it compared nothing;
    - a configured surface id that is not declared in the manifest (a typo) -- the
      old docstring said unknown ids "simply cannot match" and deferred to the adapter
      validator, which means a typo and a genuine miss printed the same word.

    A HIT SHORT-CIRCUITS TO ``evaluated`` even when another part of the config is
    unresolvable, and that asymmetry is deliberate: the positive is established by the
    path that matched, and downgrading it would DISARM the #408 override (a glob hit
    beside a typo'd surface id used to reject a bare ``single-surface`` verdict, and
    must keep doing so). Only the negative can be undetermined.

    A malformed manifest still raises ``SurfaceError`` out of ``load_surfaces`` rather
    than becoming ``not-established``: that path is already loud, and softening it to a
    typed state would turn a hard failure of `validate-critique-artifacts` into an
    ``overrides: False`` that quietly stops gating.
    """
    surfaces = list(surfaces or [])
    globs = list(globs or [])
    scanned = len(changed_paths)
    if not surfaces and not globs:
        return _probe_state(PROBE_NOT_CONFIGURED, False, scanned)
    if globs and any(_surfaces_lib.path_matches_patterns(path, globs) for path in changed_paths):
        return _probe_state(PROBE_EVALUATED, True, scanned)
    undetermined: list[str] = []
    unresolved: list[str] = []
    if not changed_paths:
        undetermined.append(
            "the probe is configured but was handed zero changed paths, so nothing was compared against it"
        )
    if surfaces:
        manifest = _surfaces_lib.load_surfaces(repo_root, required=False)
        if manifest is None:
            undetermined.append(
                "`boundary_cross_surface_surfaces` is configured but `.agents/surfaces.json` is absent, "
                "so no configured surface id could be resolved"
            )
        else:
            resolved = _surfaces_lib.resolve_trigger_surfaces(manifest, surfaces)
            declared = set(resolved["declared"])
            matched_ids = {
                surface["surface_id"]
                for surface in _surfaces_lib.match_surfaces(manifest, changed_paths)["matched_surfaces"]
            }
            if matched_ids & declared:
                return _probe_state(PROBE_EVALUATED, True, scanned)
            unresolved = list(resolved["unresolved"])
            if unresolved:
                undetermined.append(
                    "`boundary_cross_surface_surfaces` references surface ids that are not declared in "
                    f"{manifest['path']}: {', '.join(unresolved)}"
                )
    if undetermined:
        return _probe_state(PROBE_NOT_ESTABLISHED, False, scanned, undetermined, unresolved)
    return _probe_state(PROBE_EVALUATED, False, scanned)


def _probe_state(
    state: str,
    hit: bool,
    scanned_paths: int,
    undetermined_reasons: list[str] | None = None,
    unresolved_surfaces: list[str] | None = None,
) -> dict[str, object]:
    """Every return of `cross_surface_probe_state`, built once, so no branch can omit a
    key a consumer branches on."""
    return {
        "state": state,
        "hit": hit,
        "scanned_paths": scanned_paths,
        "undetermined_reasons": list(undetermined_reasons or []),
        "unresolved_surfaces": list(unresolved_surfaces or []),
    }


def cross_surface_hit(
    repo_root: Path,
    changed_paths: list[str],
    *,
    surfaces: list[str] | None = None,
    globs: list[str] | None = None,
) -> bool:
    """True iff the probe EVALUATED and matched. Kept as the positive-only shorthand for
    callers that only act on a hit (the #408 severity upgrade, and the per-path witness
    search that explains one). Anything that renders or exits on the NEGATIVE must call
    `cross_surface_probe_state` instead: `False` here still cannot distinguish "no match"
    from "could not tell" -- it just no longer has to, because the typed answer exists."""
    return bool(
        cross_surface_probe_state(repo_root, changed_paths, surfaces=surfaces, globs=globs)["hit"]
    )


def resolve_changed_paths(
    repo_root: Path,
    changed_path: list[str] | None,
    changed_ref: str | None,
    *,
    include_worktree: bool = False,
) -> list[str]:
    """The changed paths for the probe: explicit ``changed_path`` wins, else the
    ``changed_ref`` git range, else the working-tree diff.

    ``include_worktree`` UNIONS the working tree into whichever of those was
    chosen, instead of replacing it. It exists because verify precedes commit: a
    caller that hands this a committed range is asking about work that already
    landed, while the slice actually under review is still on disk. With the
    committed range alone the probe is structurally blind to the change it is
    meant to judge -- measured, the same working tree produced `hit=False` from
    `HEAD..HEAD` and `hit=True` from its own worktree paths, so the cross-surface
    tooth was armed or disarmed by which question was asked, not by the code.

    Off by default: the existing callers' semantics do not change, and a caller
    that genuinely means "the committed range" (a post-hoc audit) must not have
    an unrelated dirty file quietly widen its scope.
    """
    if changed_path is not None:
        resolved = list(changed_path)
    elif changed_ref:
        resolved = _surfaces_lib.collect_changed_paths_for_ref(repo_root, changed_ref)
    else:
        return _surfaces_lib.collect_changed_paths(repo_root)
    if not include_worktree:
        return resolved
    return _surfaces_lib.dedupe_preserve_order(
        resolved + _surfaces_lib.collect_changed_paths(repo_root)
    )


def resolve_probe_state(
    repo_root: Path,
    *,
    changed_path: list[str] | None = None,
    changed_ref: str | None = None,
    include_worktree: bool = False,
) -> tuple[dict[str, object], list[str], dict[str, list[str]]]:
    """Resolve the changed paths, read the critique adapter's probe config, and return
    ``(probe_state, changed_paths, probe_config)``. The critique validator's
    severity upgrade calls this shared resolver, so the resolve-and-probe logic
    lives in a single place."""
    changed = resolve_changed_paths(
        repo_root, changed_path, changed_ref, include_worktree=include_worktree
    )
    adapter = _critique_adapter_lib.load_adapter(repo_root)
    probe = probe_config_from_adapter(adapter["data"])
    state = cross_surface_probe_state(
        repo_root, changed, surfaces=probe["surfaces"], globs=probe["globs"]
    )
    # The loader's `errors`/`warnings` used to be dropped on the floor here, so a
    # critique adapter that FAILED TO PARSE -- or whose `boundary_cross_surface_globs`
    # was a string instead of a list, which `validate_adapter_data` records as an error
    # -- produced empty probe config, then `not-configured`, then exit 0 with
    # `triggered: false`. That is the #622 defect ("errored probes fail toward silence")
    # in the probe #622 also named: a verdict-shaped "do nothing" over a broken config.
    #
    # A HIT still wins, preserving this module's documented asymmetry: the positive is
    # established by the path that matched, and downgrading it would disarm the #408
    # override. Only a negative or an opt-out can be undetermined.
    #
    # Keyed on `hit`, NOT on `state != PROBE_EVALUATED`. The state spelling looks
    # equivalent and is not: the two probe keys validate INDEPENDENTLY, so an adapter
    # the loader refused can still yield usable globs, and a change that simply does
    # not match them lands on `evaluated`/`hit=False`. A state-keyed guard exempts that
    # negative and re-ships the very defect this block exists to remove, narrowed from
    # "no config" to "partially-valid config". A round-2 bounded review caught it here
    # after round 1 caught the original; only a hit is a positive boundary claim.
    #
    # Measured 2026-08-14 and CORRECTED after `#673`, because four of the five sentences
    # the first version carried are now false and a stale comment on a proof surface tells
    # the next reader the guard is blind where it is live.
    #
    # WAS: only ERRORS could fire here; `load_adapter` read through `load_yaml_file`, not
    # the report variant, so it never produced an uninterpreted-line warning, and the two
    # callers were not equally armed. An unsupported scalar RAISED out of `load_adapter`
    # instead of becoming a typed state, and a silently DROPPED key was invisible entirely.
    #
    # IS: `critique_adapter_lib` routes through `adapter_lib.resolve_adapter_payload`, so
    # BOTH sources of `unreadable_reasons` fire at this call site, both callers are armed
    # the same way, and a refused scalar or a dropped key becomes a typed `not-established`
    # rather than a traceback out of the critique validator's severity upgrade.
    #
    # ONE gap remains, pre-existing and still not closed: a MISSPELLED key name
    # (`boundary_cross_surface_glob:`) is neither an error nor a drop, because the validator
    # has no unknown-key detection -- it passes through to empty config and
    # `not-configured`. That is the most likely operator typo and the least covered.
    unreadable = _adapter_lib.unreadable_reasons(adapter)
    if unreadable and not state["hit"]:
        state = _probe_state(
            PROBE_NOT_ESTABLISHED,
            False,
            len(changed),
            # EXTENDED, not replaced. A rebuilt state drops the reasons the probe had
            # already established -- an unresolved surface id is the actionable half of
            # a repo that also has an adapter error, and rebuilding threw it away.
            undetermined_reasons=[
                *state["undetermined_reasons"],
                *(
                    "critique adapter could not be read whole, so its probe config is "
                    f"not the repo's answer: {reason}"
                    for reason in unreadable
                ),
            ],
            unresolved_surfaces=state["unresolved_surfaces"],
        )
    return state, changed, probe


def resolve_hit(
    repo_root: Path,
    *,
    changed_path: list[str] | None = None,
    changed_ref: str | None = None,
    include_worktree: bool = False,
) -> tuple[bool, list[str], dict[str, list[str]]]:
    """`resolve_probe_state` with the state flattened back to ``(triggered, ...)``.

    Kept for callers that already type the surrounding states themselves. Same warning as
    `cross_surface_hit`: the `False` this returns is not a verdict on its own."""
    state, changed, probe = resolve_probe_state(
        repo_root,
        changed_path=changed_path,
        changed_ref=changed_ref,
        include_worktree=include_worktree,
    )
    return bool(state["hit"]), changed, probe
