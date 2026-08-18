#!/usr/bin/env python3
"""Release real-host proof trigger detector, and the state vocabulary it answers in.

``evaluation_scope`` is always emitted and is the key to read FIRST. The VERDICT
key is ``required``, and it exists ONLY when the triggers were actually evaluated
against a non-empty changed scope:

- ``evaluated`` -> exit 0, ``required`` present. Configured triggers were
  compared against N > 0 changed paths. A real answer either way.
- ``not-configured`` -> exit 0, ``required: False``. This repo declares no
  triggers, so there is nothing to evaluate. A genuine opt-out, checked BEFORE
  the empty-scope state so a repo that legitimately declares nothing is answered
  rather than made to refuse forever.
- ``empty`` -> exit 3, and NO ``required`` key. Triggers are configured and the
  changed-path scope handed to this check was EMPTY, so nothing was evaluated
  against them. An empty scope is not evidence of "not required".
- ``not-established`` -> exit 1 on stderr. The trigger configuration itself could
  not be resolved (unknown surface id, unreadable surfaces manifest). A broken
  config is an error to fix, not an undetermined verdict.

The ``empty`` state used to be exit 0 with ``required: False``, printing
"real_host=not-required" -- a release gate reporting SUCCESS while its own reason
string said it evaluated nothing. Exit 3 is ``run-quality.sh``'s
``UNESTABLISHED_EXIT``, which that runner renders UNPROVEN rather than FAIL for
the labels that opted into it.

The absent-``required`` rule is what makes this structural: a caller cannot read a
verdict that was never produced, because there is no key to read.
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







_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)

_scripts_surfaces_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.surfaces_lib")
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces
resolve_trigger_surfaces = _scripts_surfaces_lib_module.resolve_trigger_surfaces
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
_release_delta_module = SKILL_RUNTIME.load_local_skill_module(__file__, "release_delta")
collect_immutable_range = _release_delta_module.collect_immutable_range

#: "Ran, established nothing" -- the same byte `run-quality.sh` reads as
#: UNESTABLISHED and renders UNPROVEN. Deliberately distinct from 1, which this
#: command already spends on a BROKEN trigger configuration: that is a defect to
#: repair, while an empty changed scope is a question this run could not answer.
UNESTABLISHED_EXIT = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root used to resolve the release adapter")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--paths", nargs="*", help="Changed paths to evaluate; defaults to git-derived changed paths")
    scope.add_argument(
        "--changed-range",
        help="Immutable full-object-ID range BASE..HEAD whose changed paths this command resolves",
    )
    parser.add_argument("--detail", action="store_true", help="Emit the full proof-trigger payload as YAML")
    return parser.parse_args()


def collect_range_paths(repo_root: Path, changed_range: str) -> tuple[list[str], dict[str, object]]:
    try:
        delta = collect_immutable_range(repo_root, changed_range)
    except ValueError as exc:
        raise SystemExit(f"real-host proof range resolution failed: {exc}") from exc
    paths = delta.pop("changed_paths")
    return paths, delta


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def broken_trigger_config_payload(
    unresolved: list[str], manifest_path: str
) -> dict[str, object]:
    return {
        "required": False,
        "evaluation_scope": "not-established",
        "configuration_status": "broken",
        "unresolved_trigger_surfaces": unresolved,
        "surfaces_manifest_path": manifest_path,
        "checklist": [],
        "reason": (
            "real_host_required_surfaces references surface ids that are not declared in the surfaces manifest."
        ),
        "remediation": (
            "Fix the typo in real_host_required_surfaces, declare the missing surface id in .agents/surfaces.json, "
            "or remove the unresolved entry. Unresolved trigger ids must not silently fall through to a normal non-match."
        ),
    }


def surface_error_payload(error: str) -> dict[str, object]:
    return {
        "required": False,
        "evaluation_scope": "not-established",
        "error": error,
        "checklist": [],
        "reason": "Release real-host proof configuration is present, but the surfaces manifest could not be loaded.",
        "remediation": (
            "Create a valid repo-local .agents/surfaces.json, or remove real_host_required_surfaces "
            "and real_host_required_path_globs from the release adapter when this repo does not gate on host proof."
        ),
    }


def build_payload(repo_root: Path, changed_paths: list[str]) -> dict[str, object]:
    # GUARDED AT THE READ SITE. Three modules import this `build_payload` directly
    # (`publish_release_cli`, `publish_release_plan`, `plan_release_run`), so a refusal in
    # `main()` would leave all three evaluating triggers this reader invented.
    #
    # WHAT IT COSTS TO BE UNGUARDED, measured on the real CLI: a repo declaring
    # `real_host_required_path_globs: ["src/**"]` and a checklist under a refused version,
    # handed the changed path `src/a.py`, printed `real_host=not-required: This repo
    # declares no release-time real-host proof triggers`, exit 0. The same repo at a
    # speakable version prints `real_host=required`. So the refused version does not
    # degrade the answer -- it INVERTS the verdict, and lands on the permissive side, on
    # the gate whose whole job is to stop a publish that skipped real-host proof.
    #
    # This module's docstring builds a four-state vocabulary specifically so that "not
    # required" can never cover "we never checked". An unspeakable version was the fifth
    # state that vocabulary did not have: `not-configured` is documented as "a genuine
    # opt-out", and it was being printed over a repo that opted IN.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="release-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    trigger_surfaces = adapter["data"].get("real_host_required_surfaces", [])
    trigger_globs = adapter["data"].get("real_host_required_path_globs", [])
    checklist = adapter["data"].get("real_host_checklist", [])

    surface_hits: list[str] = []
    if trigger_surfaces:
        surfaces_manifest = load_surfaces(repo_root)
        assert surfaces_manifest is not None
        resolved_trigger_surfaces = resolve_trigger_surfaces(surfaces_manifest, trigger_surfaces)
        if resolved_trigger_surfaces["unresolved"]:
            return broken_trigger_config_payload(
                resolved_trigger_surfaces["unresolved"], surfaces_manifest["path"]
            )
        declared_trigger_surfaces = set(resolved_trigger_surfaces["declared"])
        matched = match_surfaces(surfaces_manifest, changed_paths)
        surface_hits = [
            surface["surface_id"]
            for surface in matched["matched_surfaces"]
            if surface["surface_id"] in declared_trigger_surfaces
        ]
    path_hits = [path for path in changed_paths if matches_any(path, trigger_globs)]
    required = bool(surface_hits or path_hits)
    # `required: False` was returned identically for four different worlds: a repo
    # that declares no triggers at all, a configured repo handed an EMPTY changed
    # scope, a configured repo whose triggers genuinely did not match, and a
    # trigger config that could not be resolved. Only the last had its own
    # payload. `scope` names which one, so "not required" stops being a single
    # word covering "we checked and it is fine" and "we never checked" (D7).
    configured = bool(trigger_surfaces or trigger_globs)
    if configured and not changed_paths:
        # No `required` key, and exit 3 upstream in `main`. Naming the scope
        # `empty` was already true here, but it travelled with `required: False`
        # at exit 0 -- so every caller that reads the verdict key or the byte was
        # told "not required" by a check that evaluated nothing. The verdict key
        # is absent because a verdict was never produced.
        #
        # Guarded on `configured` so the opt-out above stays FIRST: a repo that
        # declares no triggers reports `not-configured` at exit 0 forever,
        # regardless of how many paths it hands in.
        return {
            "evaluation_scope": "empty",
            "changed_paths": changed_paths,
            "surface_hits": [],
            "path_hits": [],
            "checklist": [],
            "reason": (
                "Release-time real-host proof triggers are configured, but the changed-path scope "
                "handed to this check was EMPTY, so nothing was evaluated against them."
            ),
            "remediation": (
                "Hand this check the release's changed paths (--paths or --changed-range) to get a "
                "verdict. An empty scope is not evidence that real-host proof is not required."
            ),
        }
    if not configured:
        scope, reason = "not-configured", (
            "This repo declares no release-time real-host proof triggers "
            "(`real_host_required_surfaces` / `real_host_required_path_globs`), so no check ran."
        )
    elif required:
        scope, reason = "evaluated", "Changed surfaces hit configured release-time real-host proof seams."
    else:
        scope, reason = "evaluated", (
            "Configured release-time real-host proof triggers were evaluated against "
            f"{len(changed_paths)} changed path(s) and none matched."
        )
    return {
        "required": required,
        "evaluation_scope": scope,
        "changed_paths": changed_paths,
        "surface_hits": surface_hits,
        "path_hits": path_hits,
        "checklist": checklist if required else [],
        "reason": reason,
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    provenance = None
    if args.changed_range:
        changed_paths, provenance = collect_range_paths(repo_root, args.changed_range)
    else:
        changed_paths = args.paths if args.paths is not None else collect_changed_paths(repo_root)
    try:
        payload = build_payload(repo_root, changed_paths)
    except SurfaceError as exc:
        print(yaml_output.render_yaml(surface_error_payload(str(exc))), file=sys.stderr, end="")
        return 1
    if provenance is not None:
        payload.pop("changed_paths", None)
        payload["evidence_provenance"] = provenance
    if payload.get("configuration_status") == "broken":
        rendered = yaml_output.render_yaml(payload)
        print(rendered, file=sys.stderr, end="" if rendered.endswith("\n") else "\n")
        return 1
    if args.detail:
        yaml_output.emit_yaml(payload)
    elif "required" not in payload:
        # No verdict key, so the summary line must not spell a verdict. The word
        # `not-required` here was the whole defect at the one-line surface most
        # callers read.
        print(f"real_host=not-established: {payload['reason']}")
    else:
        print(f"real_host={'required' if payload['required'] else 'not-required'}: {payload['reason']}")
    return UNESTABLISHED_EXIT if "required" not in payload else 0


if __name__ == "__main__":
    raise SystemExit(main())
