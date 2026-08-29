#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shlex
import shutil
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module
from yaml_output import emit_yaml

_surfaces_lib = import_repo_module(__file__, "scripts.surfaces_lib")
# One owner for "is this packaged module a catalog candidate". The dispatcher used
# to carry its own copy of the rule and went stale the moment the checker's copy was
# repaired; see the trigger clause below.
_catalog_check = import_repo_module(__file__, "scripts.check_consumer_validator_catalog")
_is_catalog_candidate_name = _catalog_check._is_candidate_name
_plan_helpers = import_repo_module(__file__, "scripts.staged_commit_gate_plan_helpers")

GateCommand = _plan_helpers.GateCommand
collect_staged_scope_paths = _plan_helpers.collect_staged_scope_paths
_any_starts = _plan_helpers.any_starts
_artifact_shape_gates = _plan_helpers.artifact_shape_gates
_skill_core_headroom_gates = _plan_helpers.skill_core_headroom_gates
_timing_pull_gate = _plan_helpers.timing_pull_gate
_provenance_self_test_gate = _plan_helpers.provenance_contract_self_test_gate


_registry_root = Path(__file__).resolve().parents[1]
_registry_root /= "shared/scripts" if (_registry_root / "shared").is_dir() else "skills/shared/scripts"
sys.path.insert(0, str(_registry_root))
import provenance_contract as _provenance_contract  # noqa: E402

# Single source of truth (#314) for the fast structural checkers that run in the
# literal git pre-commit gate. The plan draws this subset from surface
# verify_commands. Entries MUST be cheap (<1s), deterministic,
# and path-scoped -- never a broad pytest in the pre-commit path.
FAST_SURFACE_VERIFY_COMMANDS: dict[str, str] = {
    "python3 scripts/validate_skill_ergonomics.py --repo-root .": "validate-skill-ergonomics",
    "python3 scripts/check_boundary_bypass_ratchet.py --repo-root .": "check-boundary-bypass-ratchet",
}


def _any_exact(paths: list[str], *names: str) -> bool:
    """A trigger keyed on ONE named file, not a surface prefix."""
    return any(path in names for path in paths)


def _timing_layer_gates(repo_root: Path, paths: list[str], existing: list[str] | None = None) -> list[GateCommand]:
    """The favorable pulled subset from the 2026-06-10 timing audit plus later
    pulls recorded in the same table — each is cheap (<0.3s), deterministic,
    changed-scoped (only its trigger class can flip the verdict), and runs the
    EXACT broad-gate command (single source). ~0.6s combined worst case; see
    docs/validator-timing-layers.md for the classification table
    and the ~1s budget line.

    ``existing`` is the subset of ``paths`` still on disk. A gate that validates a
    named file runs only while that file exists. A gate that validates a whole
    surface keeps running on ``paths``, deletion included."""
    present = paths if existing is None else existing
    gates: list[GateCommand] = []
    if any(path.endswith(".py") for path in paths):
        gates.extend(
            _timing_pull_gate(
                repo_root, "check-python-filenames", "scripts/check_python_filenames.py",
                "--repo-root", str(repo_root), "--require-git-file-listing",
            )
        )
    if _any_starts(paths, "skills/"):
        gates.extend(_timing_pull_gate(repo_root, "check-skill-contracts", "scripts/check_skill_contracts.py", "--repo-root", str(repo_root)))
        gates.extend(
            _timing_pull_gate(
                repo_root, "check-skill-bootstrap-vars", "scripts/check_skill_bootstrap_vars.py",
                "--repo-root", str(repo_root), "--require-git-file-listing",
            )
        )
    if _any_exact(present, ".agents/surfaces.json"):
        # A broken surfaces manifest degrades every surface-driven gate, so it
        # fails earliest.
        gates.extend(_timing_pull_gate(repo_root, "validate-surfaces", "scripts/validate_surfaces.py", "--repo-root", str(repo_root)))
    if _any_exact(present, "scripts/run-quality.sh", "docs/validator-timing-layers.md"):
        # #368 meta-gate: a new run-quality validator (or a timing-doc edit) must keep
        # the classification table exhaustive, so the shift-left class cannot recur via
        # an unclassified broad-only check. Flips only on these two files.
        gates.extend(_timing_pull_gate(repo_root, "check-timing-layer-completeness", "scripts/check_timing_layer_completeness.py", "--repo-root", str(repo_root)))
    # The registry owns the dependency/fixture closure.  Keeping this derived
    # rather than hand-maintained prevents a new helper from silently falling
    # outside the commit-time contract gate.
    provenance_paths = {
        path
        for contract in _provenance_contract.CONTRACTS
        for path in contract.trigger_paths
    }
    if any(path in provenance_paths for path in paths):
        gates.extend(
            _timing_pull_gate(
                repo_root,
                "check-provenance-contract",
                "skills/public/quality/scripts/check_provenance_contract.py",
                "--repo-root",
                str(repo_root),
            )
        )
        # A second channel exercises the checker through its owning test rather
        # than trusting the checker process to approve its own decision procedure.
        # This is intentionally narrow: the exact test invokes the source checker
        # and asserts executable fixture results, while the checker gate above
        # remains the operator-facing registry receipt.
        gates.extend(_provenance_self_test_gate(repo_root))
    if any(
        path in {
            ".agents/consumer-validator-adoption.yaml",
            "scripts/check_consumer_validator_catalog.py",
            "skills/public/quality/references/consumer-validator-catalog.yaml",
            "plugins/charness/skills/quality/references/consumer-validator-catalog.yaml",
        }
        or path.startswith("plugins/charness/scripts/")
        or (
            path.startswith(("scripts/", "skills/public/", "plugins/charness/"))
            # The CHECKER's own predicate, imported rather than restated. This line
            # used to spell `startswith(("check_", "validate_"))`, and when the
            # catalog's discovery predicate became position-independent this copy
            # stayed positional -- so the one validator the widening exists to bring
            # into scope, `issue_validate_closeout_draft.py`, was the one file whose
            # edit did NOT fire this gate at commit time. A rule with two
            # implementations drifts the moment one of them is repaired; #586's class,
            # found by a bounded review of the widening slice itself.
            and _is_catalog_candidate_name(Path(path).name)
        )
        for path in paths
    ):
        gates.extend(
            _timing_pull_gate(
                repo_root,
                "check-consumer-validator-catalog",
                "scripts/check_consumer_validator_catalog.py",
                "--repo-root",
                str(repo_root),
                "--adoption-path",
                ".agents/consumer-validator-adoption.yaml",
                "--require-adoption",
                "--require-staged-adoption",
            )
        )
    if any(
        path == "scripts/validate_quality_reference_catalog.py"
        or path.startswith("skills/public/quality/references/")
        for path in present
    ):
        # Cheap quality planner-catalog parity check. A reference/index/catalog edit can
        # otherwise make planner-following agents miss a reference until the broad gate.
        gates.extend(
            _timing_pull_gate(
                repo_root,
                "validate-quality-reference-catalog",
                "scripts/validate_quality_reference_catalog.py",
                "--repo-root",
                str(repo_root),
            )
        )
    if _touches_current_pointer_freshness_surface(paths):
        # The freshness validator is cheap and deterministic, so run the exact
        # broad-gate command at the commit boundary for every surface it cross-checks.
        gates.extend(
            _timing_pull_gate(
                repo_root, "validate-current-pointer-freshness",
                "scripts/validate_current_pointer_freshness.py",
                "--repo-root", str(repo_root),
            )
        )
    if _any_starts(paths, ".github/workflows/"):
        # <0.1s; only a workflow edit can flip the parity verdict. Carries both
        # match flags so the commit boundary enforces the same bar as the broad
        # gate's real-repo parity test, not just the inventory's parity-issue
        # subset. --require-established-gate-match was added when the
        # unestablished-match bucket split off: it is a no-op on this repo today
        # (both workflows are exempt), and without it the comment's "same bar"
        # claim became false the moment the broad test started asserting
        # `jobs_gate_match_unestablished == []`.
        gates.extend(
            _timing_pull_gate(
                repo_root, "inventory-ci-local-gate-parity",
                "skills/public/quality/scripts/inventory_ci_local_gate_parity.py",
                "--repo-root", str(repo_root), "--require-empty-parity-issues",
                "--require-canonical-gate-match", "--require-established-gate-match",
                "--require-git-file-listing",
            )
        )
    return gates


def _touches_current_pointer_freshness_surface(paths: list[str]) -> bool:
    exact = {
        ".gitignore",
        "charness-artifacts/quality/latest.md",
        "charness-artifacts/release/latest.md",
        "charness-artifacts/capability-catalog/latest.json",
        "scripts/run-quality.sh",
        "scripts/validate_current_pointer_freshness.py",
        "scripts/record_quality_runtime.py",
        "skills/public/quality/scripts/check_runtime_budget.py",
        "skills/public/quality/scripts/runtime_budget_lib.py",
        "scripts/capability_catalog_sources.py",
        "packaging/charness.json",
        "plugins/charness/.codex-plugin/plugin.json",
        "plugins/charness/.claude-plugin/plugin.json",
    }
    return any(
        path in exact
        or (path.startswith("scripts/") and path.endswith(".py"))
        or path.startswith("integrations/tools/")
        for path in paths
    )


def fast_surface_verify_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
    """Fast structural checkers from matched surface verify_commands (#314).

    Reconciles the pre-commit gate with the per-slice aggregate: when a touched
    surface lists one of ``FAST_SURFACE_VERIFY_COMMANDS`` in its verify_commands,
    that same cheap checker runs at the literal git pre-commit boundary, so the
    aggregate and pre-commit agree on the fast gate subset. Degrades to no extra
    gates when the surfaces manifest is absent or unreadable (e.g. tmp repos).
    """
    if not paths:
        return []
    try:
        manifest = _surfaces_lib.load_surfaces(repo_root, required=False)
        if manifest is None:
            return []
        matched = _surfaces_lib.match_surfaces(manifest, paths)
    except _surfaces_lib.SurfaceError:
        return []
    gates: list[GateCommand] = []
    seen: set[str] = set()
    for command in matched["verify_commands"]:
        label = FAST_SURFACE_VERIFY_COMMANDS.get(command)
        if label is None or label in seen:
            continue
        seen.add(label)
        gates.append(GateCommand(label, tuple(shlex.split(command))))
    return gates


# #368: the inference-interpretation leak scan validates every git-tracked *.py
# OUTSIDE these registry-declared exclude prefixes (.agents/inference-interpretation-
# surfaces.json `leak_scan.exclude_prefixes`). The commit trigger must cover that
# SAME domain -- not just scripts/|skills/ -- or a 4-field declaration authored in a
# root module (e.g. runtime_bootstrap.py) is scanned by the validator yet escapes the
# commit gate, reintroducing the silent-disarm this issue closes. Kept in sync with
# the registry by hand; if the registry drifts the broad gate is still the floor.
_INFERENCE_LEAK_SCAN_EXCLUDE: tuple[str, ...] = ("plugins/", "mutants/", "tests/")


def _leak_scan_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
    """#368: pull the changed-scoped *leak scan* of cheap, offline registry/shim
    meta-validators to the commit boundary -- the recurring shift-left class
    (#314/#319/#332/#366). Each flips ONLY when a staged file adds a new entrant (a
    4-field `interpretation` dict / a new `inventory_*.py`) or drifts a duplicated
    bootstrap shim, so it is changed-scoped exactly like
    `validate-attention-state-visibility` -- not the validate-all sweep its full pass
    also performs. The 2026-06-10 timing audit bundled the cheap scan with the heavy
    sweep under one "stays / not changed-scoped" verdict, which is what let a new
    declaration's missing registration reach only the ~4-min broad gate (#367). The
    same offline command runs here (the heavier live-count work is the broad gate's
    pytest, not these commands), so the cheap verdict precedes it. Each degrades to no
    gate when the validator is absent (seeded tmp repo / consumer repo)."""
    gates: list[GateCommand] = []
    if any(path.endswith(".py") and not path.startswith(_INFERENCE_LEAK_SCAN_EXCLUDE) for path in paths):
        gates.extend(
            _timing_pull_gate(
                repo_root, "validate-inference-interpretation",
                "scripts/validate_inference_interpretation.py",
                "--repo-root", str(repo_root), "--require-git-file-listing",
            )
        )
    if any(path.endswith(".py") and (path.startswith("scripts/") or path.startswith("skills/")) for path in paths):
        gates.extend(
            _timing_pull_gate(
                repo_root, "check-bootstrap-shim-consistency",
                "scripts/check_bootstrap_shim_consistency.py",
                "--repo-root", str(repo_root), "--require-git-file-listing",
            )
        )
    if any(path.startswith("skills/public/quality/scripts/inventory_") and path.endswith(".py") for path in paths):
        gates.extend(
            _timing_pull_gate(
                repo_root, "check-inventory-declaration-coverage",
                "scripts/check_inventory_declaration_coverage.py",
                "--repo-root", str(repo_root),
            )
        )
    return gates


def staged_commit_gate_plan(
    repo_root: Path,
    staged_paths: list[str] | None = None,
    *,
    ruff_path: str | None = None,
    scope_paths: list[str] | None = None,
) -> list[GateCommand]:
    # Two lists, deliberately: `paths` is the commit's whole touched SCOPE, which
    # decides WHICH gates run; `existing` is the subset a per-file validator may be
    # handed. Collapsing them let a deletion-only or rename-only commit schedule zero
    # gates. `existing` is DERIVED from scope rather than queried separately: a second
    # `--diff-filter=ACM` query drops rename rows, so a renamed-and-edited file — new
    # content, present on disk, exactly what a per-file validator exists for — got no
    # py_compile, no ruff, and no length check.
    paths = (
        scope_paths
        if scope_paths is not None
        else (staged_paths if staged_paths is not None else collect_staged_scope_paths(repo_root))
    )
    existing = [path for path in (staged_paths if staged_paths is not None else paths) if (repo_root / path).is_file()]
    staged_py = [path for path in existing if path.endswith(".py")]
    ruff = shutil.which("ruff") if ruff_path is None else ruff_path
    plan: list[GateCommand] = []

    if paths:
        plan.extend(_plan_helpers.index_hygiene_gates(repo_root))

    if staged_py:
        plan.append(GateCommand("py_compile (staged)", ("python3", "-m", "py_compile", *staged_py)))
        if ruff:
            plan.append(GateCommand("ruff (staged)", ("ruff", "check", *staged_py)))
        plan.append(
            GateCommand(
                "check-python-lengths (staged)",
                (
                    "python3",
                    "scripts/check_code_lengths.py",
                    "--repo-root",
                    str(repo_root),
                    "--paths",
                    *staged_py,
                ),
            )
        )

    if any(path.endswith(".py") and (path.startswith("scripts/") or path.startswith("skills/")) for path in paths):
        plan.extend(
            _plan_helpers.present_gate(
                repo_root,
                "validate-attention-state-visibility",
                "validate_attention_state_visibility.py",
                "--repo-root",
                str(repo_root),
                "--scan-root",
                "scripts",
                "--scan-root",
                "skills",
                "--scan-root-map",
                "../charness-support=skills/support",
            )
        )

    # Every surface validator below is presence-guarded for one reason: a deletion now
    # schedules gates, so retiring a validator would otherwise schedule the very script
    # the commit deletes and refuse its own commit with no route but `--no-verify`.
    if _any_starts(paths, "skills/"):
        plan.extend(_plan_helpers.present_gate(repo_root, "validate-skills", "validate_skills.py", "--repo-root", str(repo_root)))
        plan.extend(_plan_helpers.present_gate(repo_root, "run-evals", "run_evals.py", "--repo-root", str(repo_root)))
    if _any_starts(paths, "profiles/"):
        plan.extend(_plan_helpers.present_gate(repo_root, "validate-profiles", "validate_profiles.py", "--repo-root", str(repo_root)))
    if _any_starts(paths, ".agents/"):
        plan.extend(_plan_helpers.present_gate(repo_root, "validate-adapters", "validate_adapters.py", "--repo-root", str(repo_root)))
    if _any_starts(paths, "presets/"):
        plan.extend(_plan_helpers.present_gate(repo_root, "validate-presets", "validate_presets.py", "--repo-root", str(repo_root)))
    if _any_starts(paths, "integrations/"):
        plan.extend(_plan_helpers.present_gate(repo_root, "validate-integrations", "validate_integrations.py", "--repo-root", str(repo_root)))


    if any(path.endswith(".md") for path in paths):
        # `check-plugin-doc-links` takes the same `.md` trigger as `check-doc-links`
        # rather than a `plugins/`-scoped one: a source-only `.md` commit that FORGETS
        # the mirror regeneration is worth catching, and the mirror-drift gate above
        # proves only that the mirror is staged, not that its links survived the
        # export transform.
        #
        # Known hole, shared with `check-doc-links` and `check-plugin-dir-references`
        # (all three sit behind the same staged-`.md` trigger), recorded in
        # `docs/validator-timing-layers.md`: a link verdict also flips when
        # the link TARGET is renamed, which stages no `.md` at all. Neither gate runs
        # on that commit; the broad gate and the `quality-core.yml` steps are what
        # catch it. Widening the trigger would have to move both gates together, so it
        # is not done here unilaterally.
        for label, script in (
            ("check-doc-links", "check_doc_links.py"),
            ("check-plugin-doc-links", "check_plugin_doc_links.py"),
        ):
            plan.extend(_plan_helpers.present_gate(repo_root, label, script, "--repo-root", str(repo_root)))
        # The plugin-dir-references owner moved to the native core (#748); the
        # commit-time plan invokes the same canonical command as run-quality's
        # label, routed through the gate-side resolver shim.
        plan.extend(
            _plan_helpers.present_gate(
                repo_root,
                "check-plugin-dir-references",
                "native_gate_lib.py",
                "--repo-root",
                str(repo_root),
                "plugin-refs",
                "--repo-root",
                str(repo_root),
            )
        )
        # SCOPED to the staged `.md` files, unlike the broad-gate and CI invocations which lint
        # every tracked markdown file. Unscoped here failed three of the four criteria in
        # docs/validator-timing-layers.md: it is validate-all (a sweep over standing
        # artifacts, which that document disqualifies by name), it is not changed-scoped (an
        # unrelated file's lint error blocks your commit), and at ~5.0s over 540 files it is five
        # times the document's own ~1s commit-time budget line, which the budget section never
        # counted. Scoped it is ~1.0s, dominated by node start-up rather than file count.
        #
        # This is a deliberate exception to "wire the earlier invocation with the exact broad-gate
        # command so the verdicts cannot drift": the rules and config are identical and the
        # candidate set is still the tracked, non-excluded listing, so a scoped run renders a
        # STRICT SUBSET of the unscoped verdicts, never a different one.
        staged_markdown = [path for path in existing if path.endswith(".md")]
        if staged_markdown and (repo_root / "scripts" / "check-markdown.sh").exists():
            plan.append(
                GateCommand("check-markdown (staged)", ("./scripts/check-markdown.sh", *staged_markdown))
            )

    # Both hand file paths to a validator, so they take the existing-file list.
    plan.extend(_skill_core_headroom_gates(repo_root, existing))
    plan.extend(_artifact_shape_gates(repo_root, existing))
    plan.extend(_timing_layer_gates(repo_root, paths, existing))
    # `existing`, not `paths`. These are handed to a validator as ARGUMENTS, and scope
    # includes DELETED files -- the invariant `test_a_scope_path_never_reaches_a_per_file_
    # validator` exists because a validator given a path to a file that is gone is a
    # hazard, whatever the individual consumer happens to tolerate. Same reason
    # `_skill_core_headroom_gates` and `_artifact_shape_gates` take `existing`.
    if changed_modules := [
        path for path in existing
        if path.endswith(".py")
        and not path.endswith("__init__.py")
        and (
            path.startswith("scripts/")
            or path.startswith("skills/")
            # Repo-ROOT modules too. `runtime_bootstrap.py` and `skill_runtime_bootstrap.py`
            # are imported by 135 scripts and are the family `SCAN_PATTERNS`'s first entry
            # was added for -- found by the inversion test because nobody listing families
            # thought of them. Repairing the enumeration and leaving the TRIGGER with the
            # original blind spot is this run's own lesson, one layer up: a changed root
            # shim would have skipped the gate entirely.
            or "/" not in path
        )
    ]:
        # Scoped to the CHANGED modules, not the whole package. The full sweep is ~2.0s
        # for 649 modules (measured 2026-08-07, 16 workers), so the scoping is not about
        # cost here -- it is that a commit-boundary gate should answer for what the commit
        # touched. The check prints `PARTIAL: checked N of M` with its verdict, so this
        # run can never be mistaken for a whole-package clean bill; the full sweep runs
        # in the standalone-import test.
        plan.extend(
            _timing_pull_gate(
                repo_root, "check-standalone-imports",
                "scripts/check_standalone_imports.py",
                "--repo-root", str(repo_root), "--require-git-file-listing",
                "--changed", *changed_modules,
            )
        )

    plan.extend(_leak_scan_gates(repo_root, paths))

    # #314: append the fast surface verify checkers so the literal pre-commit gate
    # agrees with the per-slice aggregate on the cheap structural subset.
    plan.extend(fast_surface_verify_gates(repo_root, paths))

    return plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--paths", nargs="*")
    parser.add_argument("--no-ruff", action="store_true", help="Plan as if ruff is unavailable.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    paths = args.paths if args.paths is not None else None
    ruff_path = "" if args.no_ruff else None
    plan = staged_commit_gate_plan(repo_root, paths, ruff_path=ruff_path)
    # The label-only listing is a strict subset of `as_dict()` (`label` plus the
    # `argv` it hid), so nothing the reader had is lost by emitting one document.
    emit_yaml([command.as_dict() for command in plan])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
