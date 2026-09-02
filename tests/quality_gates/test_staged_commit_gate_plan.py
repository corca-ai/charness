from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts import packaging_lib
from scripts.staged_commit_gate_plan import (
    FAST_SURFACE_VERIFY_COMMANDS,
    GateCommand,
    collect_staged_scope_paths,
    fast_surface_verify_gates,
    staged_commit_gate_plan,
)
from scripts.surfaces_lib import load_surfaces, match_surfaces
from tests.quality_gates.git_fixture_support import init_git_repo
from tests.quality_gates.repo_shapes import install_committed_repo

from .support import ROOT, run_script

SURFACES_JSON = (ROOT / ".agents" / "surfaces.json").read_text(encoding="utf-8")
pytestmark = pytest.mark.boundary_contract(
    reason="observe the staged-commit fixture's real git rename/configuration boundary"
)


def _export_plugin(tmp_path: Path) -> Path:
    plugin = tmp_path / "plugin"
    manifest = packaging_lib.load_manifest(ROOT, "charness")
    packaging_lib.export_plugin_tree(ROOT, plugin, manifest)
    return plugin


def _surface_verify_commands_for(paths: list[str]) -> set[str]:
    manifest = load_surfaces(ROOT, required=False)
    assert manifest is not None
    return set(match_surfaces(manifest, paths)["verify_commands"])


def _labels(paths: list[str]) -> list[str]:
    return [command.label for command in staged_commit_gate_plan(ROOT, paths, ruff_path="")]


def test_staged_commit_plan_includes_commit_only_python_gates() -> None:
    # A path that EXISTS: since A3 the per-file gates take only staged paths still
    # on disk, so a synthetic name is filtered before it can be planned.
    labels = _labels(["scripts/helper_provenance_lib.py"])

    assert "check-staged-reversion" in labels
    assert "check-git-identity" in labels
    assert "py_compile (staged)" in labels
    assert "check-python-lengths (staged)" in labels
    assert "validate-attention-state-visibility" in labels


def test_staged_commit_plan_gates_git_identity_when_script_present() -> None:
    # #432: the effective-identity refusal gate runs whenever ANY path is
    # staged (identity applies to the commit as a whole, not per-path), scoped
    # by script presence -- like staged-worktree-consistency -- so a seeded/
    # consumer repo without the script degrades cleanly instead of planning a
    # command that cannot run.
    plan = staged_commit_gate_plan(ROOT, ["README.md"], ruff_path="")
    gate = next((c for c in plan if c.label == "check-git-identity"), None)
    assert gate is not None
    assert gate.argv == (
        "python3",
        "scripts/check_git_identity.py",
        "--repo-root",
        str(ROOT),
    )


def test_staged_commit_plan_skips_git_identity_without_script(tmp_path: Path) -> None:
    labels = [c.label for c in staged_commit_gate_plan(tmp_path, ["README.md"], ruff_path="")]
    assert "check-git-identity" not in labels


def test_staged_worktree_consistency_blocks_edit_after_stage(tmp_path: Path, monkeypatch) -> None:
    # Closes the worktree-vs-staged gap: a file staged then edited again commits the
    # stale staged blob, while pre-commit gates validate the (newer) worktree. The
    # gate fails when a staged path also carries unstaged edits; a clean full-stage
    # passes; CHARNESS_ALLOW_PARTIAL_STAGE escapes a deliberate partial commit.
    from scripts.check_staged_worktree_consistency import find_stale_staged
    from scripts.check_staged_worktree_consistency import main as gate_main

    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)

    init_git_repo(repo)
    target = repo / "f.txt"
    target.write_text("v1\n", encoding="utf-8")
    git("add", "f.txt")

    monkeypatch.delenv("CHARNESS_ALLOW_PARTIAL_STAGE", raising=False)
    # clean full-stage -> no stale, gate passes
    assert find_stale_staged(repo) == []
    assert gate_main(["--repo-root", str(repo)]) == 0
    # edit after staging -> staged blob (v1) != worktree (v2): stale, gate blocks
    target.write_text("v2\n", encoding="utf-8")
    assert find_stale_staged(repo) == ["f.txt"]
    assert gate_main(["--repo-root", str(repo)]) == 1
    # escape hatch for deliberate partial staging
    monkeypatch.setenv("CHARNESS_ALLOW_PARTIAL_STAGE", "1")
    assert gate_main(["--repo-root", str(repo)]) == 0
    monkeypatch.delenv("CHARNESS_ALLOW_PARTIAL_STAGE", raising=False)
    # re-stage -> what is validated is what commits again
    git("add", "f.txt")
    assert find_stale_staged(repo) == []


def test_staged_commit_plan_gates_changed_skill_md_core_headroom() -> None:
    # #319: a changed public/support SKILL.md pulls the commit-boundary core
    # headroom ratchet into the plan, scoped to exactly that path.
    # A path that EXISTS: the gate hands it to a validator, so a synthetic name
    # would be a scope the command could never actually check (A3 argv-site rule).
    plan = staged_commit_gate_plan(ROOT, ["skills/public/critique/SKILL.md"], ruff_path="")
    gate = next((c for c in plan if c.label == "check-skill-core-headroom (staged)"), None)
    assert gate is not None
    assert gate.argv == (
        "python3",
        "scripts/check_skill_surface_preflight.py",
        "--repo-root",
        str(ROOT),
        "--changed-skill-md",
        "skills/public/critique/SKILL.md",
    )


def test_staged_commit_plan_skips_core_headroom_for_a_deleted_skill_md() -> None:
    # A3 argv-site rule: a deleted SKILL.md still schedules its SURFACE gates, but
    # must not be handed to the per-file preflight, which fails on a missing file.
    assert "check-skill-core-headroom (staged)" not in _labels(["skills/public/gone/SKILL.md"])
    assert "validate-skills" in _labels(["skills/public/gone/SKILL.md"])


def test_staged_commit_plan_skips_core_headroom_without_changed_skill_md() -> None:
    # A reference edit or a non-skill change must not pull the SKILL.md core gate.
    for paths in (
        ["skills/public/demo/references/note.md"],
        ["scripts/new_helper.py"],
        ["README.md"],
    ):
        assert "check-skill-core-headroom (staged)" not in _labels(paths)


def _labels_with_files(tmp_path: Path, paths: list[str]) -> list[str]:
    """Plan labels for paths that EXIST in a scratch repo.

    Since A3, a gate that hands paths to a per-file validator drops the ones that are
    not on disk, so a scheduling assertion has to use paths that could really be
    validated rather than synthetic names.
    """
    for path in paths:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# stub\n", encoding="utf-8")
    return [command.label for command in staged_commit_gate_plan(tmp_path, paths, ruff_path="")]


def test_staged_commit_plan_gates_changed_artifact_shape() -> None:
    # the hand-authored artifact family pulls the blocking commit-boundary shape
    # gate, scoped to the changed charness-artifacts/** paths.
    existing_artifact = "charness-artifacts/critique/2026-07-27-provenance-containment.md"
    plan = staged_commit_gate_plan(ROOT, [existing_artifact], ruff_path="")
    gate = next((c for c in plan if c.label == "check-artifact-shape (staged)"), None)
    assert gate is not None
    # absolute preflight path: the command runs with cwd=repo_root, and charness is
    # consumed as a plugin, so a bare relative path only resolves when the target
    # repo IS the charness source tree.
    assert gate.argv == (
        "python3",
        str(ROOT / "scripts" / "check_artifact_surface_preflight.py"),
        "--repo-root",
        str(ROOT),
        "--changed-artifacts",
        existing_artifact,
    )


def test_staged_commit_plan_skips_artifact_shape_for_non_artifact_md(tmp_path: Path) -> None:
    # Only the changed-scoped prefix families (critique/ideation/retro) pull the
    # blocking shape gate. The debug/quality validators are
    # author-time-only, so they do NOT pull the fail-fast sweep; nor do non-artifact
    # md or out-of-family dirs.
    for paths in (
        ["docs/x.md"],
        ["README.md"],
        ["scripts/x.py"],
        ["charness-artifacts/spec/x.md"],
        ["charness-artifacts/quality/2026-06-08-x.md"],
        ["docs/index.md"],
    ):
        assert "check-artifact-shape (staged)" not in _labels(paths)
    for paths in (
        ["charness-artifacts/critique/2026-06-08-x.md"],
        ["charness-artifacts/ideation/2026-06-08-x.md"],
        ["charness-artifacts/debug/2026-06-08-x.md"],
        ["charness-artifacts/retro/2026-06-08-x.md"],
    ):
        assert "check-artifact-shape (staged)" in _labels_with_files(tmp_path, paths)
    # ...and a DELETED one in the same family does not, because the shape validator
    # would be handed a file that is gone.
    assert "check-artifact-shape (staged)" not in _labels(
        ["charness-artifacts/critique/2026-06-08-gone.md"]
    )


def test_gate_command_serializes_to_dict() -> None:
    assert GateCommand("demo", ("python3", "demo.py")).as_dict() == {
        "label": "demo",
        "argv": ["python3", "demo.py"],
    }


def test_staged_commit_plan_covers_domain_and_markdown_triggers() -> None:
    labels = _labels(
        [
            "skills/public/demo/SKILL.md",
            "profiles/default/profile.yaml",
            ".agents/surfaces.json",
            "presets/default.yaml",
            "integrations/tool.json",
            "docs/usage.md",
            # A path that EXISTS, because check-markdown now takes the staged `.md` files as
            # arguments and therefore obeys this module's `existing`-not-`paths` invariant
            # (test_a_scope_path_never_reaches_a_per_file_validator). The fictional paths above
            # still exercise the trigger for the gates that take no file arguments.
            "README.md",
        ]
    )

    assert "validate-skills" in labels
    assert "run-evals" in labels
    assert "validate-profiles" in labels
    assert "validate-adapters" in labels
    assert "validate-presets" in labels
    assert "validate-integrations" in labels
    assert "check-doc-links" in labels
    # Scoped: the commit layer lints only the staged `.md` files, unlike the broad gate.
    assert "check-markdown (staged)" in labels


# Timing-layer pulls (docs/validator-timing-layers.md): one test per
# pulled guard — the favorable (cheap + changed-scoped + deterministic) subset
# fires at commit time via this dispatcher, and not for unrelated change classes.


def test_timing_pull_python_filenames_fires_for_staged_python_only() -> None:
    assert "check-python-filenames" in _labels(["scripts/new_helper.py"])
    assert "check-python-filenames" not in _labels(["docs/usage.md"])


def test_timing_pull_skill_contract_guards_fire_for_skills_paths_only() -> None:
    labels = _labels(["skills/public/demo/references/note.md"])
    assert "check-skill-contracts" in labels
    assert "check-skill-bootstrap-vars" in labels
    for label in ("check-skill-contracts", "check-skill-bootstrap-vars"):
        assert label not in _labels(["scripts/new_helper.py"])


def test_timing_pull_validate_surfaces_fires_for_manifest_edit_only() -> None:
    assert "validate-surfaces" in _labels([".agents/surfaces.json"])
    assert "validate-surfaces" not in _labels([".agents/quality-adapter.yaml"])


def test_timing_pull_ci_parity_fires_for_workflow_edits_only() -> None:
    # The slice-3 parity miss was caught only by the bundle pytest watchdog;
    # a workflow edit now pays the same bar (--require-canonical-gate-match)
    # at commit time.
    assert "inventory-ci-local-gate-parity" in _labels([".github/workflows/quality-core.yml"])
    assert "inventory-ci-local-gate-parity" not in _labels(["docs/usage.md"])


def test_timing_pull_current_pointer_freshness_fires_for_pointer_surfaces() -> None:
    # #396: rolling-pointer freshness used to wait until pre-push, leaving a
    # commit->push window for stale pointer claims and sibling pointer
    # claims. The exact broad-gate command is cheap enough to pull forward for
    # every surface it cross-checks.
    trigger_paths = [
        "charness-artifacts/quality/latest.md",
        "charness-artifacts/release/latest.md",
        "charness-artifacts/capability-catalog/latest.json",
        "scripts/run-quality.sh",
        ".agents/quality-gates.yaml",
        "scripts/any_quality_pointer_helper.py",
        "scripts/validate_current_pointer_freshness.py",
        "scripts/record_quality_runtime.py",
        "skills/public/quality/scripts/check_runtime_budget.py",
        "skills/public/quality/scripts/runtime_budget_lib.py",
        "scripts/capability_catalog_sources.py",
        "packaging/charness.json",
        "plugins/charness/.codex-plugin/plugin.json",
        "plugins/charness/.claude-plugin/plugin.json",
        "integrations/tools/demo.json",
    ]
    for path in trigger_paths:
        labels = _labels([path])
        assert "validate-current-pointer-freshness" in labels, path
    assert "validate-current-pointer-freshness" not in _labels(["docs/usage.md"])
    assert "validate-current-pointer-freshness" not in _labels(["tests/new_helper.py"])


def test_leak_scan_inference_interpretation_fires_across_full_scan_domain() -> None:
    # #368: a new 4-field interpretation declaration can appear in ANY *.py the
    # validator scans (every git-tracked *.py outside plugins/|mutants/|tests/), so
    # the commit trigger must cover that whole domain — not just scripts/|skills/ —
    # else a declaration in a root module (runtime_bootstrap.py) escapes the commit
    # gate. Runs the EXACT broad-gate command (single source).
    plan = staged_commit_gate_plan(ROOT, ["scripts/new_helper.py"], ruff_path="")
    gate = next((c for c in plan if c.label == "validate-inference-interpretation"), None)
    assert gate is not None
    assert gate.argv == (
        "python3",
        "scripts/validate_inference_interpretation.py",
        "--repo-root",
        str(ROOT),
        "--require-git-file-listing",
    )
    assert "validate-inference-interpretation" in _labels(["skills/public/demo/scripts/lib.py"])
    # the closed hole: a root module in the validator's scan domain now triggers
    assert "validate-inference-interpretation" in _labels(["runtime_bootstrap.py"])
    # excluded prefixes (validator skips them) do not pay the gate, nor do non-.py
    assert "validate-inference-interpretation" not in _labels(["tests/quality_gates/test_x.py"])
    assert "validate-inference-interpretation" not in _labels(["plugins/charness/scripts/x.py"])
    assert "validate-inference-interpretation" not in _labels(["docs/usage.md"])
    assert "validate-inference-interpretation" not in _labels([".agents/surfaces.json"])


def test_leak_scan_bootstrap_shim_consistency_fires_for_scripts_or_skills_python_only() -> None:
    # #368 general-leak sibling: the bootstrap-shim consistency check (scan domain
    # scripts/**+skills/** *.py) is a cheap offline blocking structural check that was
    # broad-only; pulled to the commit boundary on its scan-domain trigger.
    assert "check-bootstrap-shim-consistency" in _labels(["scripts/new_helper.py"])
    assert "check-bootstrap-shim-consistency" in _labels(["skills/public/demo/scripts/lib.py"])
    assert "check-bootstrap-shim-consistency" not in _labels(["docs/usage.md"])
    assert "check-bootstrap-shim-consistency" not in _labels(["runtime_bootstrap.py"])


def test_leak_scan_inventory_declaration_coverage_fires_for_inventory_python_only() -> None:
    # #368 sibling (#145 family): a new inventory_*.py under skills/public/quality/
    # scripts/ pulls the cheap declaration-coverage scan; a non-inventory scripts/.py
    # or a non-inventory quality script does not.
    assert "check-inventory-declaration-coverage" in _labels(
        ["skills/public/quality/scripts/inventory_new.py"]
    )
    assert "check-inventory-declaration-coverage" not in _labels(["scripts/new_helper.py"])
    assert "check-inventory-declaration-coverage" not in _labels(
        ["skills/public/quality/scripts/render_runtime_summary.py"]
    )


def test_timing_layer_completeness_fires_for_run_quality_or_timing_doc_edits_only() -> None:
    # #368 meta-gate: flips only when scripts/run-quality.sh or the timing doc
    # changes, so a newly added validator cannot sit unclassified.
    assert "check-timing-layer-completeness" in _labels(["scripts/run-quality.sh"])
    assert "check-timing-layer-completeness" in _labels([".agents/quality-gates.yaml"])
    assert "check-timing-layer-completeness" in _labels(["docs/validator-timing-layers.md"])
    assert "check-timing-layer-completeness" not in _labels(["scripts/new_helper.py"])
    assert "check-timing-layer-completeness" not in _labels(["docs/usage.md"])


def test_consumer_validator_catalog_pull_covers_source_and_exported_paths() -> None:
    trigger_paths = [
        ".agents/consumer-validator-adoption.yaml",
        "scripts/check_consumer_validator_catalog.py",
        "skills/public/quality/references/consumer-validator-catalog.yaml",
        "plugins/charness/skills/quality/references/consumer-validator-catalog.yaml",
        "scripts/check_demo.py",
        # INFIX-named validators, which this list did not cover. The catalog's
        # discovery predicate became position-independent on 2026-08-23 while this
        # dispatcher kept its own positional copy of the rule -- so the one validator
        # the widening exists to bring into scope was the one file whose edit did NOT
        # fire this gate at commit time. A rule with two implementations drifts the
        # moment one is repaired; the dispatcher now imports the checker's predicate.
        "skills/public/issue/scripts/issue_validate_closeout_draft.py",
        "plugins/charness/skills/issue/scripts/issue_validate_closeout_draft.py",
    ]
    for path in trigger_paths:
        assert "check-consumer-validator-catalog" in _labels([path]), path
    assert "check-consumer-validator-catalog" not in _labels(["docs/usage.md"])
    # And the dispatcher's predicate IS the checker's, not a copy that can drift.
    from scripts import check_consumer_validator_catalog as catalog_check
    from scripts import staged_commit_gate_plan as gate_plan

    assert gate_plan._is_catalog_candidate_name is catalog_check._is_candidate_name


def test_quality_reference_catalog_parity_fires_for_quality_reference_surface() -> None:
    assert "validate-quality-reference-catalog" in _labels(
        ["skills/public/quality/references/index.md"]
    )
    assert "validate-quality-reference-catalog" in _labels(
        ["skills/public/quality/references/catalog.yaml"]
    )
    assert "validate-quality-reference-catalog" in _labels(
        ["skills/public/quality/references/security-npm.md"]
    )
    assert "validate-quality-reference-catalog" in _labels(
        ["scripts/validate_quality_reference_catalog.py"]
    )
    assert "validate-quality-reference-catalog" not in _labels(
        ["skills/public/debug/references/index.md"]
    )
    assert "validate-quality-reference-catalog" not in _labels(["docs/usage.md"])


def test_leak_scan_gates_degrade_when_validator_absent(tmp_path: Path) -> None:
    # In a repo without the validator scripts (seeded tmp / consumer repo), the
    # leak-scan pulls degrade to no gate rather than planning a missing command —
    # the same _timing_pull_gate contract the other pulls use.
    labels = [
        c.label for c in staged_commit_gate_plan(tmp_path, ["scripts/new_helper.py"], ruff_path="")
    ]
    assert "validate-inference-interpretation" not in labels
    assert "check-bootstrap-shim-consistency" not in labels
    inv_labels = [
        c.label
        for c in staged_commit_gate_plan(
            tmp_path, ["skills/public/quality/scripts/inventory_x.py"], ruff_path=""
        )
    ]
    assert "check-inventory-declaration-coverage" not in inv_labels


def test_staged_commit_gate_plan_cli_emits_the_planned_labels() -> None:
    # One YAML document is the CLI's whole output surface since the 2026-08-14
    # `--json` removal, and it is a SUPERSET of the retired label-only text listing
    # (each entry carries the `argv` that listing hid), so both halves of the old
    # json-and-text test read the same payload now.
    result = run_script(
        "scripts/staged_commit_gate_plan.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
    )
    assert result.returncode == 0, result.stderr
    assert [item["label"] for item in yaml.safe_load(result.stdout)] == [
        "check-staged-reversion",
        "check-git-identity",
        "staged-worktree-consistency",
        "check-doc-links",
        "check-plugin-doc-links",
        "check-plugin-dir-references",
        "check-markdown (staged)",
    ]

    no_ruff_result = run_script(
        "scripts/staged_commit_gate_plan.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/helper_provenance_lib.py",
        "--no-ruff",
    )
    assert no_ruff_result.returncode == 0, no_ruff_result.stderr
    no_ruff_labels = [item["label"] for item in yaml.safe_load(no_ruff_result.stdout)]
    # Full equality against the ruff-less plan, not membership: `main()` resolves ruff
    # through `shutil.which`, so on a host WITHOUT ruff installed a bare
    # `"ruff (staged)" not in labels` holds whether or not `--no-ruff` is wired at all,
    # and the flag under test would be unproven.
    assert no_ruff_labels == [
        command.label
        for command in staged_commit_gate_plan(
            ROOT, ["scripts/helper_provenance_lib.py"], ruff_path=""
        )
    ]
    assert "check-python-lengths (staged)" in no_ruff_labels
    assert "ruff (staged)" not in no_ruff_labels


def test_staged_commit_gate_plan_plugin_mirror_matches_source(tmp_path: Path) -> None:
    # Split out of the json-and-text test so a stale export names ITSELF rather than
    # taking the source-CLI assertions down with it.
    args = ("--repo-root", str(ROOT), "--paths", "README.md")
    source_result = run_script("scripts/staged_commit_gate_plan.py", *args)
    plugin = _export_plugin(tmp_path)
    plugin_result = run_script(str(plugin / "scripts" / "staged_commit_gate_plan.py"), *args)
    assert source_result.returncode == 0, source_result.stderr
    assert plugin_result.returncode == 0, plugin_result.stderr
    assert yaml.safe_load(plugin_result.stdout) == yaml.safe_load(source_result.stdout)


def test_a_rename_only_commit_sees_both_sides(tmp_path: Path) -> None:
    """The other half: rename detection turns both sides into one `R` entry, which
    `--diff-filter=ACM` drops entirely."""

    repo = install_committed_repo(
        tmp_path / "repo",
        {"skills/public/demo/SKILL.md": "---\nname: demo\n---\n\n# Demo\n"},
        message="seed",
    )
    subprocess.run(
        ["git", "mv", "skills/public/demo/SKILL.md", "skills/public/demo/MOVED.md"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    # Rename detection is a git CONFIG, and `git init` inherits the caller's global
    # one. Both assertions below turn on it, so pin it instead of inheriting.
    subprocess.run(
        ["git", "config", "diff.renames", "true"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    scope = collect_staged_scope_paths(repo)

    assert scope == ["skills/public/demo/MOVED.md", "skills/public/demo/SKILL.md"]
    # Plan against ROOT: the surface validators are presence-guarded on their own
    # scripts, which a bare tmp repo does not carry.
    labels = [command.label for command in staged_commit_gate_plan(ROOT, [], scope_paths=scope)]
    assert "validate-skills" in labels


_GONE_PATHS = (
    "scripts/gone.py",
    "skills/public/gone/SKILL.md",
    "charness-artifacts/critique/2026-06-08-gone.md",
)


def test_a_scope_path_never_reaches_a_per_file_validator() -> None:
    """A deleted file must schedule its surface's gates without being handed to a
    validator as a path argument — that would fail on a file that is gone.

    Runs against `ROOT` with real siblings present, so the per-file gates
    (`py_compile`/`ruff`/`check-python-lengths`, the SKILL.md preflight, the
    artifact shape validator) are all actually planned and the assertion has
    something to be false against."""

    present = [
        "scripts/helper_provenance_lib.py",
        "skills/public/critique/SKILL.md",
        "charness-artifacts/critique/2026-07-27-provenance-containment.md",
    ]
    plan = staged_commit_gate_plan(
        ROOT, present, scope_paths=[*present, *_GONE_PATHS], ruff_path="/bin/true"
    )
    labels = {command.label for command in plan}
    assert {"py_compile (staged)", "check-python-lengths (staged)", "ruff (staged)"} <= labels
    assert {"check-skill-core-headroom (staged)", "check-artifact-shape (staged)"} <= labels
    for command in plan:
        for gone in _GONE_PATHS:
            assert gone not in command.argv, f"{command.label} was handed a deleted path"


def test_skill_packages_surface_runs_fast_ergonomics_checker() -> None:
    # #314 acceptance (1): the fast skill-ergonomics checker must run in the
    # skill-packages surface verify_commands so portable-package issue anchors,
    # dated incidents, and host-surface references fail at the commit boundary,
    # not only at the broad/bundle quality gate.
    surfaces = json.loads(SURFACES_JSON)
    skill_packages = next(s for s in surfaces["surfaces"] if s["surface_id"] == "skill-packages")
    assert (
        "python3 scripts/validate_skill_ergonomics.py --repo-root ."
        in skill_packages["verify_commands"]
    ), skill_packages["verify_commands"]


def test_repo_python_surface_runs_fast_subprocess_form_before_broad_pytest() -> None:
    # #768 acceptance: the fast subprocess-form check must run in the repo-python
    # surface and precede the broad pytest so a direct production spawn bypass
    # fails at the commit boundary, not 172s into the broad gate.
    surfaces = json.loads(SURFACES_JSON)
    repo_python = next(s for s in surfaces["surfaces"] if s["surface_id"] == "repo-python")
    verify = repo_python["verify_commands"]
    form_idx = next((i for i, cmd in enumerate(verify) if "check_subprocess_form.py" in cmd), None)
    broad_idx = next((i for i, cmd in enumerate(verify) if "run_standing_pytest.py" in cmd), None)
    assert form_idx is not None, verify
    assert broad_idx is not None, verify
    assert form_idx < broad_idx, verify


def test_fast_surface_verify_allowlist_keys_exist_in_some_surface() -> None:
    # #314 acceptance (2/3): every reconciliation allowlist key must still appear
    # in some surface verify_commands. If surfaces.json renames or drops a fast
    # checker without updating FAST_SURFACE_VERIFY_COMMANDS (or vice versa), the
    # two commit-boundary paths would silently disagree -- pin it so drift fails.
    surfaces = json.loads(SURFACES_JSON)
    all_verify = {cmd for s in surfaces["surfaces"] for cmd in s["verify_commands"]}
    for command in FAST_SURFACE_VERIFY_COMMANDS:
        assert command in all_verify, f"{command!r} not found in any surface verify_commands"


def test_precommit_plan_agrees_with_fast_subset_for_skill_change() -> None:
    # #314 acceptance (2/3): when a touched surface lists a fast checker in its
    # verify_commands and the literal git pre-commit plan must name the SAME
    # checker, so the fast subset has one commit-boundary contract.
    paths = ["skills/public/critique/SKILL.md"]
    surface_verify = _surface_verify_commands_for(paths)
    expected_fast = {
        command for command in FAST_SURFACE_VERIFY_COMMANDS if command in surface_verify
    }
    assert "python3 scripts/validate_skill_ergonomics.py --repo-root ." in expected_fast

    precommit_labels = {
        command.label for command in staged_commit_gate_plan(ROOT, paths, ruff_path="")
    }
    for command, label in FAST_SURFACE_VERIFY_COMMANDS.items():
        if command in expected_fast:
            assert label in precommit_labels, (label, precommit_labels)


def test_precommit_plan_agrees_with_fast_subset_for_test_change() -> None:
    # #768: a changed test file routes to the repo-python surface, whose
    # verify_commands include the production subprocess-form check; the
    # pre-commit plan must run the same check.
    paths = ["tests/quality_gates/test_example.py"]
    surface_verify = _surface_verify_commands_for(paths)
    assert (
        "python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing"
        in surface_verify
    )

    gates = fast_surface_verify_gates(ROOT, paths)
    labels = {gate.label for gate in gates}
    assert "check-subprocess-form" in labels
    argv = next(gate.argv for gate in gates if gate.label == "check-subprocess-form")
    assert argv == (
        "python3",
        "scripts/check_subprocess_form.py",
        "--repo-root",
        ".",
        "--require-git-file-listing",
    )


def test_fast_surface_verify_gates_degrade_without_surfaces_manifest(tmp_path: Path) -> None:
    # #314: tmp repos with no surfaces.json must not gain spurious gates; the
    # reconciliation degrades cleanly so the existing pre-commit fixtures hold.
    assert fast_surface_verify_gates(tmp_path, ["skills/public/critique/SKILL.md"]) == []
    assert fast_surface_verify_gates(ROOT, []) == []


def test_fast_surface_verify_gates_degrade_on_surface_error() -> None:
    # #320: a manifest that loads but cannot match the changed paths makes
    # surfaces matching raise SurfaceError (here a repo-escaping path trips
    # normalize_repo_path). The commit-boundary gate must degrade to no extra
    # gates rather than propagate the error -- covers the
    # `except SurfaceError: return []` branch the mutation gate flagged as a
    # test-uncovered changed line.
    assert fast_surface_verify_gates(ROOT, ["../escape.py"]) == []


def test_unrelated_change_adds_no_fast_surface_gates() -> None:
    # #314: a markdown-only change whose surfaces declare no fast checker must
    # not pull the fast subset into the pre-commit plan (no broad widening).
    labels = {
        command.label for command in staged_commit_gate_plan(ROOT, ["README.md"], ruff_path="")
    }
    assert labels.isdisjoint(set(FAST_SURFACE_VERIFY_COMMANDS.values()))


def test_a_renamed_and_edited_file_still_gets_its_per_file_gates() -> None:
    """A3's other half: `--diff-filter=ACM` drops the `R` row, so a renamed-and-edited
    file — new content, present on disk — got no py_compile, no ruff, no length check.
    The existing-file list is derived from scope now, not queried separately."""

    scope = ["scripts/gone_source.py", "scripts/helper_provenance_lib.py"]
    plan = staged_commit_gate_plan(ROOT, scope_paths=scope, ruff_path="/bin/true")
    compile_gate = next(c for c in plan if c.label == "py_compile (staged)")
    assert compile_gate.argv == ("python3", "-m", "py_compile", "scripts/helper_provenance_lib.py")


def test_surface_validators_are_presence_guarded_on_their_own_script(tmp_path: Path) -> None:
    """Retiring a validator must not schedule the very script the commit deletes."""

    labels = [
        command.label
        for command in staged_commit_gate_plan(
            tmp_path, scope_paths=["skills/public/demo/SKILL.md"]
        )
    ]
    assert "validate-skills" not in labels
    assert "run-evals" not in labels
