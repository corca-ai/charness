#!/usr/bin/env python3
"""Author-time shape preflight for the hand-authored artifact family.

Generalizes ``check_skill_surface_preflight.py`` from skill surfaces to the
``charness-artifacts/**`` artifact-shape validator family. Given an artifact
path or type it surfaces the owning validator's required shape — delegating to
the owning scaffold or the validator's declared shape source, never
re-declaring it — and at the commit boundary it relocates the owning validator's
verdict earlier (a blocking structural-sweep member), so an author learns the
required shape before the broad gate rather than by failing it
(the #284 -> #308 -> #325 -> #329 -> #332 -> #334 recurrence class).

The registry below is the generalization: one place that knows the artifact-
authoring family. Each surface declares a *shape source* — a ``scaffold`` script
(stub-by-construction) or a ``template`` section — plus its owning validator. The
dispatcher reads shape from that source; it adds no new shape requirement and
changes no validator verdict.
"""

from __future__ import annotations

import argparse
import contextlib
import inspect
import io
import json
import os
import subprocess
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script
from skill_runtime_bootstrap import load_repo_module_from_skill_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)
_path_portability = import_repo_module(__file__, "scripts.path_portability_lib")
_artifact_run_scope = import_repo_module(__file__, "scripts.artifact_run_scope")
_critique_paths = import_repo_module(__file__, "scripts.critique_artifact_paths")
safe_repo_relative_path = _artifact_run_scope.safe_repo_relative_path
is_critique_round_record = _critique_paths.is_critique_round_record


@dataclass(frozen=True)
class Surface:
    artifact_type: str
    prefix: str | None  # repo-relative path prefix (or exact file); None for non-path
    validator: str | None  # repo-relative owning validator
    scaffold: str | None  # repo-relative scaffold script (shape source)
    template_section: str | None  # (template_path, "## Heading") shape source
    commit_boundary: bool  # relocate the validator's verdict to the commit gate
    note: str
    paths_arg: bool = True  # validator accepts --paths; False => validate-all default
    artifact_path_arg: bool = (
        False  # validator accepts --artifact-path: judge THIS draft, not the adapter default
    )
    owner: str | None = None  # override for the validator=None owner line
    shape_command: tuple[str, ...] | None = (
        None  # skill-script argv that prints the enforced shape (run with --stub for a starter); rendered from the owning validator's live constants
    )

    def excludes(self, rel: str) -> bool:
        tail = rel[len(self.prefix or "") :]
        # Critique round records are append-only evidence consumed by the next
        # review round, not hand-authored critique decisions. Their writer owns
        # a different shape and the critique validator must not reinterpret them
        # as completed artifacts at the commit boundary.
        if self.artifact_type == "critique":
            return is_critique_round_record(rel)
        # retro validator skips its rolled-up memory + archived history.
        if self.artifact_type == "retro":
            return tail == "recent-lessons.md" or tail.startswith("history/")
        return False


# The artifact-authoring shape family. Two coverage tiers, by validator shape:
#  - Prefix-mapped surfaces (critique, ideation, retro, debug) accept `--paths` and
#    run CHANGED-SCOPED, so they are wired into the blocking fail-fast structural
#    sweep (`commit_boundary=True`): cheap, changed-scoped, no reordering of the
#    deeper quality-run stages.
#  - Adapter-scoped quality siblings validate-ALL (no --paths), so they
#    are NOT in the fail-fast sweep (`commit_boundary=False`); they get author-time
#    shape help via `--type`/`--emit-stub`/`--path` and the broad gate remains their
#    enforcement. (Putting a validate-all gate in the fail-fast sweep would block a
#    commit on pre-existing siblings the author never touched.) Giving one of these
#    `--paths` is what moves it into the tier above — that is how debug moved.
# See charness-artifacts/spec/authoring-preflight-generalization-and-disposition-delaunder.md
# and charness-artifacts/spec/artifact-shape-preflight-coverage.md.
REGISTRY: tuple[Surface, ...] = (
    Surface(
        "critique",
        "charness-artifacts/critique/",
        "scripts/validate_critique_artifacts.py",
        "skills/public/critique/scripts/scaffold_critique_artifact.py",
        None,
        True,
        "Hand-authored critique record; `## Reviewer Tier Evidence` + `## Structured Findings` enforced when present.",
    ),
    Surface(
        "ideation",
        "charness-artifacts/ideation/",
        "scripts/validate_ideation_artifact.py",
        "skills/public/ideation/scripts/scaffold_ideation_artifact.py",
        None,
        True,
        "Hand-authored ideation record; `## Structured Questions` enforced when present.",
    ),
    Surface(
        "retro",
        "charness-artifacts/retro/",
        "scripts/validate_retro_artifact.py",
        "skills/public/retro/scripts/scaffold_retro_artifact.py",
        None,
        True,
        "Hand-authored session retro; `## Next Improvements` disposition form enforced.",
    ),
    # closeout-draft: the GitHub-issue closeout surface the authoring-preflight class
    # (#284 -> #334) did not cover — discovered by failing `validate-closeout-draft`
    # ~4x this cycle. Author-time-only (validator=None: a verdict needs the full
    # `--repo/--number/--classification/--carrier` command, not just a path); the
    # shape is rendered live from the verifier's constants, never re-declared.
    Surface(
        "closeout-draft",
        None,
        None,
        None,
        None,
        False,
        "GitHub-issue closeout-draft body shape (bug-only resolution_critique + `tool signal:`, "
        "carrier-body source = commit message for direct-commit, per-classification "
        "ledger fields, close keyword); rendered live from `validate-closeout-draft`'s "
        "verifier constants.",
        shape_command=("skills/public/issue/scripts/describe_closeout_draft_shape.py",),
        owner=(
            "issue closeout-draft validation — `python3 skills/public/issue/scripts/issue_tool.py "
            "validate-closeout-draft --repo <owner/repo> --number <N> --classification <c> "
            "--carrier <c> ...` (the verdict needs the full command, not just a path; this "
            "surface is author-time shape only)."
        ),
    ),
    # debug moved into the fail-fast sweep (#454 follow-up): the validator gained
    # `--paths`, so the documented objection — a validate-ALL gate blocking a commit
    # on pre-existing siblings — no longer applies. Scoped to the artifacts actually
    # being committed it is cheap and changed-scoped like its critique/retro/ideation
    # peers. This is the surface whose shape was previously discoverable only at the
    # RELEASE gate, which is where the #454 session spent ~10 round trips learning it.
    Surface(
        "debug",
        "charness-artifacts/debug/",
        "scripts/validate_debug_artifact.py",
        "skills/public/debug/scripts/scaffold_debug_artifact.py",
        None,
        True,
        "Hand-authored debug artifact; required sections + seam-risk/interrupt prefixed values + cross-file sibling marker.",
    ),
    Surface(
        "quality",
        "charness-artifacts/quality/",
        "scripts/validate_quality_artifact.py",
        "skills/public/quality/scripts/scaffold_quality_artifact.py",
        None,
        False,
        "Hand-authored quality artifact; required sections + runtime-signal/delegated-review shape.",
        artifact_path_arg=True,
        paths_arg=False,
    ),
)


def _resolve(repo_root: Path, raw: str) -> str:
    # Disposition: echo the raw path. A target outside the repo is still worth naming
    # in the shape output, so this surface never refuses on resolution alone.
    rel = _path_portability.resolve_within_repo(repo_root, raw)
    return rel if rel is not None else Path(raw).as_posix()


def surface_for_path(rel: str) -> Surface | None:
    rel = safe_repo_relative_path(rel)
    if rel is None:
        return None
    for surface in REGISTRY:
        if surface.prefix and rel.startswith(surface.prefix) and rel.endswith(".md"):
            if not surface.excludes(rel):
                return surface
    return None


def surface_for_type(artifact_type: str) -> Surface | None:
    return next((s for s in REGISTRY if s.artifact_type == artifact_type), None)


def _load_repo_script(script: Path):
    relative = script.resolve().relative_to(REPO_ROOT.resolve())
    module_name = ".".join(relative.with_suffix("").parts)
    if relative.parts[0] == "scripts":
        return import_repo_module(script, module_name)
    return load_repo_module_from_skill_script(script, module_name)


def _run_repo_script(
    repo_root: Path, script: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    """Run a repo-owned script's main in-process while retaining its CLI result shape."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    previous_argv = sys.argv
    previous_cwd = Path.cwd()
    argv = [str(script), *args]
    try:
        module = _load_repo_script(script)
        os.chdir(repo_root)
        sys.argv = argv
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            main = module.main
            if inspect.signature(main).parameters:
                returncode = main(args)
            else:
                returncode = main()
    except SystemExit as exc:
        returncode = exc.code if isinstance(exc.code, int) else 1
    except Exception:
        returncode = 1
        traceback.print_exc(file=stderr)
    finally:
        sys.argv = previous_argv
        os.chdir(previous_cwd)
    return subprocess.CompletedProcess(
        argv,
        int(returncode or 0),
        stdout.getvalue(),
        stderr.getvalue(),
    )


def _resolve_shape_source(raw: str) -> tuple[Path | None, str | None]:
    """Resolve a registered shape source in source or exported layout.

    Registry paths remain canonical source paths (``skills/public/...``), while
    an exported plugin flattens them to ``skills/...``. Resolve against the
    package containing this dispatcher, never against the consumer's artifact
    root. A package carrying neither layout, or both layouts, is an invalid
    proof surface and must fail with the candidate paths named.
    """
    candidates: list[tuple[str, Path]] = [("canonical", REPO_ROOT / raw)]
    if raw.startswith("skills/public/"):
        candidates.append(
            ("flattened-installed", REPO_ROOT / "skills" / raw.removeprefix("skills/public/"))
        )
    existing = [(label, candidate) for label, candidate in candidates if candidate.is_file()]
    candidate_text = "; ".join(f"{label}={candidate}" for label, candidate in candidates)
    if len(existing) == 1:
        return existing[0][1], None
    if not existing:
        return None, f"missing shape source; candidates: {candidate_text}"
    existing_text = ", ".join(f"{label}={candidate}" for label, candidate in existing)
    return None, f"ambiguous shape source; multiple candidates exist: {existing_text}"


def _validator_argv_path(validator: str) -> str:
    """Resolve an owning validator against the tree this preflight lives in.

    Commands run with ``cwd=repo_root``, so a bare relative ``scripts/...`` path
    only resolves when the target repo IS the charness source tree. Charness is
    consumed as a plugin, and the commit-boundary arm is exactly the surface a
    consuming repo runs over its OWN artifacts — there, the validator lives in the
    installed plugin, not under ``<consumer>/scripts/``. Fall back to the relative
    path when the local copy is absent so an unusual layout still gets the old
    behavior rather than a hard failure.
    """
    local = REPO_ROOT / validator
    return str(local) if local.is_file() else validator


def _run_shape_command(repo_root: Path, surface: Surface, *, stub: bool) -> tuple[str, int]:
    """Run a surface's ``shape_command`` (a skill script that prints the required
    shape from the owning validator's live constants). ``--stub`` asks it for a
    starter. Returns ``(text, returncode)``."""
    source, error = _resolve_shape_source(surface.shape_command[0])
    if source is None:
        return (
            f"(could not render shape source {surface.shape_command[0]}: {error})",
            1,
        )
    script_args = [*surface.shape_command[1:], "--repo-root", str(repo_root)]
    if stub:
        script_args.append("--stub")
    proc = _run_repo_script(repo_root, source, script_args)
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout, 0
    return (
        f"(could not render shape source {surface.shape_command[0]}: "
        f"{proc.stderr.strip() or 'no output'})",
        1,
    )


def _parse_structured_stdout(text: str) -> Any:
    """Parse a repo-owned script's structured envelope, or None when it is not one.

    Repo-owned scripts emit YAML, so this reads YAML. JSON stays parseable through
    the same call (it is a YAML subset), and the JSON branch below is the mirror of
    `yaml_output.render_yaml`'s own no-PyYAML fallback: in an environment without
    PyYAML the producer emits JSON, so the consumer has to be able to read it.
    Anything that is not a structured document (a scaffold printing plain markdown)
    returns a non-mapping or None and the caller falls through to the raw text.
    """
    try:
        import yaml
    except ImportError:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        return None


def _run_scaffold_template(repo_root: Path, scaffold: str) -> tuple[str, int]:
    """Run a scaffold script and return the rendered artifact text.

    Most scaffolds (critique/ideation/retro/debug/quality) go through
    ``scripts/scaffold_artifact_lib.emit_payload_main``, which emits one JSON
    envelope with a `template` key holding the real markdown; unwrap that key
    rather than treating the raw JSON as the artifact text (the prior behavior
    here) — writing the JSON blob in place of markdown only round-tripped
    through an owning validator by coincidence, as long as no enforced marker
    string leaked into the JSON's structural text. Presence of the literal
    string `parent-delegated` in a scaffolded placeholder exposed this. A
    scaffold outside that convention (e.g. `goal_artifact_early_close_report.py`,
    which prints plain markdown) does not parse to an enveloped mapping and falls
    through to the raw stdout unchanged — this stays a strict improvement, never a
    new failure mode.
    """
    source, error = _resolve_shape_source(scaffold)
    if source is None:
        return f"(could not render scaffold {scaffold}: {error})", 1
    proc = _run_repo_script(repo_root, source, ["--repo-root", str(repo_root)])
    if proc.returncode != 0 or not proc.stdout.strip():
        return f"(could not render scaffold {scaffold}: {proc.stderr.strip() or 'no output'})", 1
    payload = _parse_structured_stdout(proc.stdout)
    template = payload.get("template") if isinstance(payload, dict) else None
    return (template, 0) if isinstance(template, str) else (proc.stdout, 0)


def _shape_text(repo_root: Path, surface: Surface) -> str:
    if surface.scaffold:
        return _run_scaffold_template(repo_root, surface.scaffold)[0]
    # Non-scaffold sources accumulate: a surface may pair a template block (the
    # lines to author into) with a shape_command (the enforced FORMS read live
    # from the owning validator). Each present source contributes one part.
    parts: list[str] = []
    if surface.template_section:
        tpl_rel, _, heading = surface.template_section.partition("|")
        tpl, error = _resolve_shape_source(tpl_rel)
        parts.append(
            _extract_section(tpl.read_text(encoding="utf-8"), heading)
            if tpl is not None
            else f"(template {tpl_rel} not found: {error})"
        )
    if surface.shape_command:
        parts.append(_run_shape_command(repo_root, surface, stub=False)[0])
    if not parts:
        return "(no shape source registered)"
    return "\n\n".join(part.rstrip() for part in parts)


def _extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    capturing = False
    for line in lines:
        if line.strip() == heading:
            capturing = True
            out.append(line)
            continue
        if capturing and line.startswith("## "):
            break
        if capturing:
            out.append(line)
    return "\n".join(out).rstrip() + "\n" if out else f"(section {heading} not found in template)"


# Audit row C6's recorded residual, for BOTH arms below (`describe` and
# `changed_artifacts`), because a reader of either needs it.
#
# `run-quality.sh` passes `--include-worktree` to the critique validator so the
# cross-surface probe judges the slice under review rather than the previous one.
# These invocations deliberately do NOT, and the flag was tried here and reverted
# on measurement: this surface targets whichever artifact the author is holding,
# while the tooth judges the CURRENT working tree. Editing a critique artifact
# written for an EARLIER change then refuses it for paths that artifact never
# covered -- reproduced against
# `charness-artifacts/critique/2026-07-31-release-3-0-1.md`.
#
# Blast radius is narrower than it sounds, and saying so is part of the record:
# the override is date-grandfathered at `BOUNDARY_OWNERSHIP_RULE_DATE`
# (2026-07-06), so a genuinely old artifact cannot be refused by it at all. The
# reachable case is a post-cutoff artifact whose own scope predates the current
# worktree.
#
# So the two surfaces still disagree on a worktree slice, narrowly and by design:
# this one is a fail-fast SHAPE check on one artifact, and the cross-surface
# question needs the change under review, which these invocations do not model.
CROSS_SURFACE_RESIDUAL = "commit-boundary arms do not pass --include-worktree (audit row C6)"


def describe(repo_root: Path, surface: Surface, *, target_rel: str | None) -> str:
    out = [
        f"artifact-surface-preflight: {surface.artifact_type}",
        f"note: {surface.note}",
        "",
        "required shape (from the owning scaffold/template/validator — the single source):",
        _shape_text(repo_root, surface).rstrip(),
        "",
    ]
    if surface.validator:
        # Adapter-scoped validators validate-all (no --paths); prefix validators
        # take --paths for a changed-scoped verdict.
        validator_args = ["--repo-root", str(repo_root)]
        cmd = f"python3 {surface.validator} --repo-root ."
        # See CROSS_SURFACE_RESIDUAL below: deliberately no `--include-worktree`.
        if surface.paths_arg and target_rel:
            validator_args += ["--paths", target_rel]
            cmd += f" --paths {target_rel}"
        elif surface.artifact_path_arg and target_rel:
            # Without this the adapter-scoped validators run validate-all against the
            # POINTER target, so the verdict was about a different file than the one
            # the author is holding -- and it printed PASS.
            validator_args += ["--artifact-path", target_rel]
            cmd += f" --artifact-path {target_rel}"
        out.append(f"owning validator: {cmd}")
        if target_rel and (repo_root / target_rel).is_file():
            validator_path = REPO_ROOT / surface.validator
            if not validator_path.is_file():
                validator_path = repo_root / surface.validator
            proc = _run_repo_script(repo_root, validator_path, validator_args)
            verdict = "PASS" if proc.returncode == 0 else "FAIL"
            scoped = surface.paths_arg or surface.artifact_path_arg
            scope = target_rel if scoped else f"{surface.artifact_type} surface (validate-all)"
            out.append(f"current verdict on {scope}: {verdict}")
            if proc.returncode != 0:
                out.append((proc.stderr or proc.stdout).strip())
    else:
        owner = surface.owner or "the owning workflow"
        out.append(f"owning validator: {owner}")
    return "\n".join(out).rstrip() + "\n"


def emit_stub(repo_root: Path, surface: Surface) -> tuple[str, int]:
    if surface.scaffold:
        return _run_scaffold_template(repo_root, surface.scaffold)
    parts: list[str] = []
    code = 0
    if surface.template_section:
        source = surface.template_section.split("|")[0]
        parts.append(
            f"{surface.artifact_type} has no scaffold script; its shape is seeded by "
            f"{source} — author into that block directly."
        )
    if surface.shape_command:
        text, rc = _run_shape_command(repo_root, surface, stub=True)
        parts.append(text)
        code = code or rc
    if not parts:
        parts.append(f"{surface.artifact_type}: no stub source registered.")
    return "\n\n".join(part.rstrip() for part in parts) + "\n", code


def changed_artifacts(repo_root: Path, paths: list[str]) -> dict[str, Any]:
    """Commit-boundary arm: relocate each owning validator's verdict earlier.

    Groups changed artifacts by owning commit-boundary surface and runs each
    validator on its changed paths. Same validator, same verdict — only earlier.
    Only `commit_boundary` surfaces are processed, and those are all changed-scoped
    (`paths_arg=True`); validate-all surfaces are author-time-only (not here),
    because a validate-all gate in the fail-fast sweep would reorder the deeper
    closeout stages and block on pre-existing siblings.

    Like the author-time arm, this one does not pass `--include-worktree` to the
    critique validator — see ``CROSS_SURFACE_RESIDUAL`` for the measurement that
    reverted it and what still disagrees with `run-quality.sh`.
    """
    groups: dict[str, tuple[Surface, list[str]]] = {}
    invalid_paths = sorted({str(raw) for raw in paths if safe_repo_relative_path(str(raw)) is None})
    if invalid_paths:
        detail = "malformed repo-relative path(s) refused: " + ", ".join(invalid_paths)
        return {
            "status": "blocked",
            "blocked": ["path-resolution"],
            "checked": [
                {
                    "artifact_type": "path-resolution",
                    "validator": "repo-relative-path-contract",
                    "paths": invalid_paths,
                    "returncode": 2,
                    "stdout": "",
                    "stderr": detail,
                }
            ],
            "path_error": detail,
        }
    for raw in paths:
        rel = safe_repo_relative_path(str(raw))
        assert rel is not None
        surface = surface_for_path(rel)
        if surface is None or not surface.commit_boundary or surface.validator is None:
            continue
        groups.setdefault(surface.artifact_type, (surface, []))[1].append(rel)
    results: list[dict[str, Any]] = []
    for artifact_type in sorted(groups):
        surface, group = groups[artifact_type]
        validator_path = REPO_ROOT / surface.validator
        if not validator_path.is_file():
            validator_path = repo_root / surface.validator
        proc = _run_repo_script(
            repo_root,
            validator_path,
            ["--repo-root", str(repo_root), "--paths", *sorted(group)],
        )
        results.append(
            {
                "artifact_type": artifact_type,
                "validator": surface.validator,
                "paths": sorted(group),
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        )
    blocked = [r["validator"] for r in results if r["returncode"] != 0]
    return {"status": "blocked" if blocked else "ok", "blocked": blocked, "checked": results}


def changed_artifacts_report(report: dict[str, Any]) -> dict[str, Any]:
    """Fold the blocked-case remedy into the payload this arm actually emits.

    Output is unconditionally YAML, so the one thing the dropped text renderer
    added that the payload does not carry — what an operator DOES about a block —
    has to live in the payload. Everything else it printed (the per-row verdict,
    the validator's own detail) is already derivable from `returncode`/`stdout`/
    `stderr` on each row.
    """
    payload = dict(report)
    if report["status"] == "blocked":
        payload["remedy"] = report.get("path_error") or (
            "An artifact's owning validator failed at the commit boundary (relocated "
            "from the broad gate). Fix the required shape — run "
            "`python3 scripts/check_artifact_surface_preflight.py --path <artifact>` to see it."
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--path", help="Artifact path to surface required shape for")
    parser.add_argument("--type", dest="artifact_type", help="Artifact type (see the registry)")
    parser.add_argument(
        "--emit-stub",
        action="store_true",
        help="Emit a starter stub via the owning scaffold or shape source",
    )
    parser.add_argument(
        "--changed-artifacts",
        nargs="*",
        help="Commit-boundary: relocate owning validator verdicts for these paths",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    if args.changed_artifacts is not None:
        report = changed_artifacts(repo_root, args.changed_artifacts)
        emit_yaml(changed_artifacts_report(report))
        return 1 if report["status"] == "blocked" else 0

    target_rel = _resolve(repo_root, args.path) if args.path else None
    if args.artifact_type:
        surface = surface_for_type(args.artifact_type)
    elif target_rel:
        surface = surface_for_path(target_rel)
    else:
        parser.error("one of --path, --type, or --changed-artifacts is required")
    if surface is None:
        known = ", ".join(s.artifact_type for s in REGISTRY)
        print(
            f"artifact-surface-preflight: no registered surface for {args.artifact_type or target_rel}; known: {known}",
            file=sys.stderr,
        )
        return 2

    if args.emit_stub:
        text, code = emit_stub(repo_root, surface)
        sys.stdout.write(text if text.endswith("\n") else text + "\n")
        return code
    print(describe(repo_root, surface, target_rel=target_rel), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
