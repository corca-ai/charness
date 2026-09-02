#!/usr/bin/env python3
"""Auto-retro trigger probe.

Exit contract. `triggered` is a VERDICT KEY and is emitted only when the probe reached a
real answer; ``state`` is the first key of every payload and the one to read first:

- ``0`` + ``state: evaluated``       -> ``triggered: true|false`` is a real answer;
- ``0`` + ``state: not-configured``  -> ``triggered: false``, an opt-out this repo
  explicitly recorded by setting BOTH trigger fields to ``[]``;
- ``3`` + ``state: not-established`` -> NO ``triggered`` key; the probe could not tell
  (no adapter, unset keys, an adapter the loader could not fully interpret, or a
  configured probe handed an empty changed set);
- ``1`` + ``state: not-established`` -> the probe REFUSED: a typo'd trigger surface id,
  an unloadable surfaces manifest, or a failed `git diff`. Already loud today; kept a
  distinct byte because a broken config needs an edit, not a re-run.

ANY nonzero exit means "not a no". The four undetermined worlds above all used to print
``triggered: false`` as key #1 -- the value that means "do nothing" -- so every failure
mode of this probe failed toward silence and a skipped retro looked identical to a
correctly skipped one. `state` / `evaluated` / `not-configured` / `not-established` is
the same vocabulary as the critique cross-surface scope
already speak; 3 matches `scripts/run-quality.sh`'s ``UNESTABLISHED_EXIT``.

Undetermined is deliberately NOT reported as ``triggered: true``: this repo cannot know a
consumer's trigger surfaces, and firing on absence would make the probe cry wolf on every
unconfigured repo instead of asking it to decide once.
"""

from __future__ import annotations

import argparse
import fnmatch
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
run_process = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.subprocess_guard"
).run_process


_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter

_scripts_surfaces_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.surfaces_lib"
)
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces
resolve_trigger_surfaces = _scripts_surfaces_lib_module.resolve_trigger_surfaces
SurfaceError = _scripts_surfaces_lib_module.SurfaceError

_yaml_output_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.yaml_output"
)
render_yaml = _yaml_output_module.render_yaml
emit_yaml = _yaml_output_module.emit_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root to scan for auto-retro trigger surfaces and path globs",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Changed paths to evaluate against trigger surfaces (defaults to git diff)",
    )
    parser.add_argument("--base-ref", help="Base git ref for explicit commit-range path discovery")
    parser.add_argument(
        "--head-ref",
        default="HEAD",
        help="Head git ref for --base-ref path discovery (default: HEAD)",
    )
    return parser.parse_args()


# The typed-state vocabulary used by the cross-surface probes is deliberately consistent:
# `evaluation_scope` and the critique cross-surface scope spells its `state`. Literal
# strings rather than a shared constant module, matching that precedent: three words are
# not worth a dependency, and the critique/release ADAPTER stack in particular stays
# unimported here. That rule is about adapter stacks, not about every repo module -- this
# script already imports `scripts.surfaces_lib` below, and now `scripts.adapter_lib`,
# which is the loader whose own output these states describe.
STATE_EVALUATED = "evaluated"
STATE_NOT_CONFIGURED = "not-configured"
STATE_NOT_ESTABLISHED = "not-established"

UNDETERMINED_EXIT = 3

# `adapter_lib` owns both the marker and the rule that reads it, because it is the ONE
# producer of the sentence. This script kept its own copy until the cross-surface boundary
# probe needed the identical judgment and the duplicate-ratchet gate named the pair -- two
# consumers re-deriving a loader's verdict is exactly the drift the old comment here
# warned about, arrived at from the other direction. Re-exported under this module's
# original name, which its own call sites below still use. The marker constant is NOT
# re-exported: nothing referenced it outside the deleted function body, and a name kept
# "for callers" that has no caller is the shape this repo keeps filing.
_scripts_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_lib"
)
adapter_unreadable_reasons = _scripts_adapter_lib_module.unreadable_reasons


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def no_config_payload(paths: list[str], adapter: dict[str, object]) -> dict[str, object]:
    field_state = adapter.get("field_state") or {}
    surface_state = field_state.get("auto_session_trigger_surfaces")
    glob_state = field_state.get("auto_session_trigger_path_globs")
    unreadable = adapter_unreadable_reasons(adapter)
    # An opt-out is only real when the repo WROTE one: both fields present and empty, in
    # an adapter the loader read whole. Everything else -- no adapter, unset keys, a
    # misspelled key that passes through ignored, a dropped or refused line -- is a repo
    # that never answered the question, and used to be reported with the same
    # `triggered: false` as the answer.
    intentional_empty = (
        surface_state == "explicit-empty" and glob_state == "explicit-empty" and not unreadable
    )
    payload: dict[str, object] = {
        "state": STATE_NOT_CONFIGURED if intentional_empty else STATE_NOT_ESTABLISHED
    }
    if intentional_empty:
        payload["triggered"] = False
    payload.update(
        {
            "changed_paths": paths,
            "surface_hits": [],
            "path_hits": [],
            "suggested_mode": None,
            "configuration_status": (
                "intentional-empty"
                if intentional_empty
                else unconfigured_status(adapter, unreadable)
            ),
            "field_state": {
                "auto_session_trigger_surfaces": surface_state,
                "auto_session_trigger_path_globs": glob_state,
            },
        }
    )
    if intentional_empty:
        payload["reason"] = "Auto-retro trigger surfaces and path globs are explicitly empty."
    else:
        payload["reason"] = (
            "Auto-retro trigger configuration could not be established, so this run has no "
            "answer either way — do not read it as `no retro owed`."
        )
        payload["remediation"] = (
            "Add auto_session_trigger_surfaces or auto_session_trigger_path_globs, "
            "or set both fields to [] to record an intentional opt-out."
        )
    # Same key as the configured path uses, so a caller learns ONE place to read the
    # machine-checkable causes behind `state: not-established`, not one per branch.
    if unreadable:
        payload["undetermined"] = unreadable
    return payload


def unconfigured_status(adapter: dict[str, object], unreadable: list[str]) -> str:
    """Which of the four undetermined worlds this is. They share one `state` because they
    share one consequence; the label is what tells the operator which edit to make. Read
    in precedence order: a refused parse outranks a dropped line, which outranks an
    absent file, because each earlier cause can produce the later one's symptom."""
    if adapter.get("errors"):
        status = "adapter-unreadable"
    elif unreadable:
        status = "adapter-partially-uninterpreted"
    elif not adapter.get("found"):
        status = "adapter-missing"
    else:
        status = "unset"
    return status


def surface_error_payload(error: str) -> dict[str, object]:
    return {
        "state": STATE_NOT_ESTABLISHED,
        "error": error,
        "reason": "Auto-retro trigger configuration is present, but the surfaces manifest could not be loaded.",
        "remediation": (
            "Create a valid repo-local .agents/surfaces.json, or remove "
            "auto_session_trigger_surfaces and auto_session_trigger_path_globs "
            "from the retro adapter when this repo does not use auto-retro triggers."
        ),
    }


def collect_range_paths(repo_root: Path, *, base_ref: str, head_ref: str) -> list[str]:
    result = run_process(
        ["git", "diff", "--name-only", f"{base_ref}..{head_ref}"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if result.returncode != 0:
        raise SurfaceError(
            "git diff failed while collecting auto-retro trigger paths\n"
            f"base_ref: {base_ref}\n"
            f"head_ref: {head_ref}\n"
            f"exit_code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
    return [line for line in result.stdout.splitlines() if line.strip()]


def broken_trigger_config_payload(unresolved: list[str], manifest_path: str) -> dict[str, object]:
    return {
        "state": STATE_NOT_ESTABLISHED,
        "configuration_status": "broken",
        "unresolved_trigger_surfaces": unresolved,
        "surfaces_manifest_path": manifest_path,
        "reason": (
            "auto_session_trigger_surfaces references surface ids that are not declared in the surfaces manifest."
        ),
        "remediation": (
            "Fix the typo in auto_session_trigger_surfaces, declare the missing surface id in .agents/surfaces.json, "
            "or remove the unresolved entry. Unresolved trigger ids must not silently fall through to a normal non-match."
        ),
    }


def resolve_surface_hits(
    repo_root: Path, trigger_surfaces: list[str], changed_paths: list[str]
) -> tuple[list[str], dict[str, object] | None]:
    """``(surface_hits, broken_config_payload)``; the payload is None unless a configured
    trigger id is undeclared.

    The manifest is loaded only when SURFACE ids are configured. A repo that took the
    remediation's other branch — `auto_session_trigger_path_globs` alone — needs no
    surfaces manifest to answer, and requiring one refused the exact configuration this
    script had just told the operator to write."""
    if not trigger_surfaces:
        return [], None
    manifest = load_surfaces(repo_root)
    assert manifest is not None
    resolved = resolve_trigger_surfaces(manifest, trigger_surfaces)
    if resolved["unresolved"]:
        return [], broken_trigger_config_payload(resolved["unresolved"], manifest["path"])
    declared = set(resolved["declared"])
    matched = match_surfaces(manifest, changed_paths)
    return [
        surface["surface_id"]
        for surface in matched["matched_surfaces"]
        if surface["surface_id"] in declared
    ], None


def _input_paths(
    repo_root: Path,
    *,
    paths: list[str] | None = None,
    base_ref: str | None = None,
    head_ref: str = "HEAD",
) -> tuple[list[str], dict[str, object]]:
    if paths is not None and base_ref:
        raise SurfaceError("--paths and --base-ref are mutually exclusive")
    if base_ref:
        return collect_range_paths(repo_root, base_ref=base_ref, head_ref=head_ref), {
            "mode": "commit_range",
            "base_ref": base_ref,
            "head_ref": head_ref,
        }
    if paths is not None:
        return paths, {"mode": "explicit_paths"}
    return collect_changed_paths(repo_root), {"mode": "working_tree_diff"}


def build_payload(
    repo_root: Path,
    *,
    paths: list[str] | None = None,
    base_ref: str | None = None,
    head_ref: str = "HEAD",
) -> dict[str, object]:
    adapter = load_adapter(repo_root)
    trigger_surfaces = adapter["data"].get("auto_session_trigger_surfaces", [])
    trigger_globs = adapter["data"].get("auto_session_trigger_path_globs", [])
    if not trigger_surfaces and not trigger_globs and paths is None and not base_ref:
        payload = no_config_payload([], adapter)
        payload["input"] = {"mode": "working_tree_diff"}
        return payload
    changed_paths, input_payload = _input_paths(
        repo_root, paths=paths, base_ref=base_ref, head_ref=head_ref
    )
    if not trigger_surfaces and not trigger_globs:
        payload = no_config_payload(changed_paths, adapter)
        payload["input"] = input_payload
        return payload

    surface_hits, broken = resolve_surface_hits(repo_root, trigger_surfaces, changed_paths)
    if broken is not None:
        broken["input"] = input_payload
        broken["changed_paths"] = changed_paths
        return broken
    path_hits = [path for path in changed_paths if matches_any(path, trigger_globs)]
    triggered = bool(surface_hits or path_hits)

    # A HIT is established by the paths that matched, so it short-circuits every doubt
    # below. Only the NEGATIVE can be undetermined — and downgrading a hit would disarm
    # the trigger, which is the opposite of the defect being fixed.
    #
    # Two things make a negative unestablished here. An EMPTY changed set is the one this
    # repo already walked into: a release helper committed and pushed, the working-tree
    # diff went empty, and the probe answered `triggered: false` about a slice it could no
    # longer see. And an adapter the loader could not fully interpret may have dropped the
    # very trigger line that would have matched.
    undetermined: list[str] = []
    if not changed_paths:
        undetermined.append(
            "Auto-retro triggers are configured, but the changed-path set handed to this run was "
            "EMPTY, so nothing was compared against them. Re-run with --paths or --base-ref naming "
            "the slice; a clean tree after a commit cannot reconstruct it."
        )
    undetermined.extend(adapter_unreadable_reasons(adapter))
    established = triggered or not undetermined

    payload: dict[str, object] = {
        "state": STATE_EVALUATED if established else STATE_NOT_ESTABLISHED
    }
    if established:
        payload["triggered"] = triggered
    payload.update(
        {
            "changed_paths": changed_paths,
            "surface_hits": surface_hits,
            "path_hits": path_hits,
            "suggested_mode": "session" if triggered else None,
            "input": input_payload,
            "reason": (
                "Changed surfaces hit configured install/update/support/export/discovery retro triggers."
                if triggered
                else "No configured auto-retro trigger matched the current slice."
                if established
                else "Auto-retro triggers are configured but could not be evaluated, so this run has "
                "no answer either way — do not read it as `no retro owed`."
            ),
        }
    )
    # Named for what they ARE under each state. Under `not-established` these are the
    # causes; under a hit they are still true but no longer block a verdict, and calling
    # them `undetermined` beside `triggered: true` would be a contradiction on the wire.
    if undetermined:
        payload["advisories" if established else "undetermined"] = undetermined
    return payload


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    payload = build_payload(
        repo_root,
        paths=args.paths,
        base_ref=args.base_ref,
        head_ref=args.head_ref,
    )
    if payload.get("configuration_status") == "broken":
        print(render_yaml(payload), end="", file=sys.stderr)
        return 1
    emit_yaml(payload)
    # The payload goes to STDOUT in every non-refusing state so one parse works
    # everywhere; the BYTE is what stops a shell caller from reading an undetermined run
    # as a no. Without it `check_auto_trigger.py ... && skip_retro` was correct-looking
    # shell that skipped on four failure modes.
    return UNDETERMINED_EXIT if payload["state"] == STATE_NOT_ESTABLISHED else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(render_yaml(surface_error_payload(str(exc))), end="", file=sys.stderr)
        raise SystemExit(1)
