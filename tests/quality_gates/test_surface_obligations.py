from __future__ import annotations

import json
from pathlib import Path

from .support import ROOT, run_script


def test_check_changed_surfaces_reports_expected_obligations_for_readme() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "checked-in-plugin-export" in surface_ids
    assert "repo-markdown" in surface_ids
    assert "python3 scripts/sync_root_plugin_manifests.py --repo-root ." in payload["sync_commands"]
    assert "python3 scripts/validate_packaging.py --repo-root ." in payload["verify_commands"]
    assert "python3 scripts/validate_packaging_committed.py --repo-root ." in payload["verify_commands"]
    assert "python3 scripts/check_doc_links.py --repo-root ." in payload["verify_commands"]
    assert "./scripts/check-markdown.sh" in payload["verify_commands"]


def _verify_commands_for(*paths: str) -> list[str]:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        *paths,
        "--json",
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["verify_commands"]


_GITIGNORE_SCAN = (
    "python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py "
    "--repo-root . --require-empty --require-git-file-listing"
)
_RETRO_INDEX_CHECK = "python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check"
_BOUNDARY_RATCHET = "python3 scripts/check_boundary_bypass_ratchet.py --repo-root ."
_STANDING_PYTEST = "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only"


def test_gitignore_scan_hygiene_runs_at_slice_closeout_for_top_level_scripts() -> None:
    # #328 gate-phase coverage: a top-level scripts/<file>.py change pulls the
    # gitignore scan-hygiene gate into slice closeout. The surface uses
    # scripts/*.py (fnmatch * crosses /, so it covers top-level and nested) rather
    # than the bare scripts/**/*.py form, which misses top-level scripts (#331).
    assert _GITIGNORE_SCAN in _verify_commands_for("scripts/rca_link_advisory.py")


def test_gitignore_scan_hygiene_runs_at_slice_closeout_for_skill_scripts() -> None:
    # #325 was a skills/public/quality script using repo_root.glob; it shipped at
    # #325 closeout and only failed at the v0.27.0 push. It is now caught at slice
    # closeout.
    assert _GITIGNORE_SCAN in _verify_commands_for(
        "skills/public/quality/scripts/standing_doc_provenance_lib.py"
    )


def test_retro_lesson_index_check_runs_at_slice_closeout() -> None:
    # The retro lesson-index freshness check is reachable at slice closeout for a
    # changed retro artifact (the surface also syncs --write first).
    assert _RETRO_INDEX_CHECK in _verify_commands_for(
        "charness-artifacts/retro/2026-06-07-322-advisory-interpretation-rollout.md"
    )


def test_boundary_bypass_ratchet_runs_at_slice_closeout_for_new_test_file() -> None:
    # The boundary-ratchet motivating case (a new tests/ file with subprocess
    # calls) surfaces at slice closeout via the repo-python surface, not only at
    # the literal git pre-commit.
    assert _BOUNDARY_RATCHET in _verify_commands_for("tests/quality_gates/test_new_thing.py")


def test_repo_markdown_surface_matches_top_level_packaging_readme() -> None:
    # #331 sibling: packaging/README.md (top-level) escaped repo-markdown's
    # packaging/**/*.md (non-recursive fnmatch) and so skipped check-markdown,
    # check_doc_links, and check-secrets at closeout. The <dir>/*.md idiom covers
    # both top-level and nested.
    verify = _verify_commands_for("packaging/README.md")
    assert "./scripts/check-markdown.sh" in verify
    assert "python3 scripts/check_doc_links.py --repo-root ." in verify


def test_repo_python_surface_matches_top_level_scripts() -> None:
    # #331 regression guard: every scripts/ file is top-level, and the bare
    # scripts/**/*.py idiom (non-recursive fnmatch) matched none of them, silently
    # keeping the whole repo-python verify set (boundary-ratchet, broad pytest) out
    # of every scripts closeout. scripts/*.py matches top-level AND nested.
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/run_slice_closeout.py",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "repo-python" in {surface["surface_id"] for surface in payload["matched_surfaces"]}
    verify = payload["verify_commands"]
    assert _BOUNDARY_RATCHET in verify
    assert _STANDING_PYTEST in verify


def test_check_changed_surfaces_treats_charness_artifacts_as_repo_markdown() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness-artifacts/setup/latest.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "repo-markdown" in surface_ids
    assert payload["unmatched_paths"] == []


def test_check_changed_surfaces_verifies_mutation_workflow_actions() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        ".github/workflows/mutation-tests.yml",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "mutation-testing-workflow" in surface_ids
    assert "python3 scripts/check_github_actions.py --repo-root ." in payload["verify_commands"]


def test_check_changed_surfaces_routes_agent_runtime_js_to_native_tests() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/agent-runtime/run-local-eval-test.mjs",
        "tests/agent-runtime/native.test.mjs",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "agent-runtime-js" in surface_ids
    assert "npm run test:agent-runtime" in payload["verify_commands"]
    assert "npm run test:mutation:js:dry-run" in payload["verify_commands"]


def test_check_changed_surfaces_reports_unmatched_paths() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "notes/private-plan.txt",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["matched_surfaces"] == []
    assert payload["unmatched_paths"] == ["notes/private-plan.txt"]


def test_select_verifiers_returns_smallest_repo_owned_bundle_for_readme() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["bundle_status"] == "repo-owned-bundle"
    recommendations = payload["recommended_commands"]
    assert recommendations[0] == {
        "phase": "sync",
        "command": "python3 scripts/sync_root_plugin_manifests.py --repo-root .",
        "reason_surface_ids": ["checked-in-plugin-export"],
    }
    verify_commands = {item["command"] for item in recommendations if item["phase"] == "verify"}
    assert "python3 scripts/validate_packaging.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_packaging_committed.py --repo-root ." in verify_commands
    assert "python3 scripts/check_doc_links.py --repo-root ." in verify_commands
    assert "./scripts/check-markdown.sh" in verify_commands


def test_select_verifiers_includes_public_skill_policy_for_public_skill_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/critique/SKILL.md",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_skills.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_public_skill_validation.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_public_skill_dogfood.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_cautilus_proof.py --repo-root ." in verify_commands


def test_select_verifiers_includes_public_skill_policy_for_policy_json_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/public-skill-validation.json",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_public_skill_validation.py --repo-root ." in verify_commands


def test_select_verifiers_includes_adapter_and_prompt_proof_for_named_cautilus_adapter_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        ".agents/cautilus-adapters/chatbot-proposals.yaml",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_adapters.py --repo-root ." in verify_commands
    assert "python3 scripts/validate_cautilus_proof.py --repo-root ." in verify_commands


def test_select_verifiers_includes_chatbot_proposal_runner_for_packet_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "evals/cautilus/chatbot-scenario-proposal-inputs.json",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_cautilus_proof.py --repo-root ." in verify_commands
    assert "python3 scripts/eval_cautilus_chatbot_proposals.py --repo-root . --json" not in verify_commands


def test_select_verifiers_includes_chatbot_benchmark_smoke_for_compare_runner_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/eval_cautilus_chatbot_compare.py",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_cautilus_proof.py --repo-root ." in verify_commands
    assert not any("eval_cautilus_chatbot_compare.py" in command for command in verify_commands)


def test_select_verifiers_includes_public_skill_dogfood_for_registry_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/public-skill-dogfood.json",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    verify_commands = {item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"}
    assert "python3 scripts/validate_public_skill_dogfood.py --repo-root ." in verify_commands


def test_select_verifiers_reports_missing_bundle_for_unmatched_paths() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "notes/private-plan.txt",
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["bundle_status"] == "missing-bundle"
    assert payload["recommended_commands"] == []
    assert any("not covered by `.agents/surfaces.json`" in note for note in payload["notes"])
    assert any("No repo-owned verifier bundle matched these changes" in note for note in payload["notes"])


def test_validate_surfaces_rejects_duplicate_ids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "dup",
                        "description": "first",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    },
                    {
                        "surface_id": "dup",
                        "description": "second",
                        "source_paths": ["docs/**"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("scripts/validate_surfaces.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "duplicate surface id `dup`" in result.stderr


def _write_surfaces(repo: Path, source_paths: list[str]) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "idiom",
                        "description": "idiom lint fixture",
                        "source_paths": source_paths,
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": [],
                        "notes": [],
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_validate_surfaces_rejects_recursive_extension_without_sibling(tmp_path: Path) -> None:
    # The #331 footgun: `<dir>/**/*.X` under fnmatch silently misses a top-level
    # `<dir>/<file>.X`. The lint must fail closed when the `<dir>/*.X` sibling is absent.
    repo = tmp_path / "repo"
    _write_surfaces(repo, ["scripts/**/*.py"])
    result = run_script("scripts/validate_surfaces.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "non-recursive-fnmatch footgun" in result.stderr
    assert "scripts/*.py" in result.stderr


def test_validate_surfaces_accepts_recursive_extension_with_sibling(tmp_path: Path) -> None:
    # Keeping the `**/*.X` form is allowed as long as the strict-superset sibling is present.
    repo = tmp_path / "repo"
    _write_surfaces(repo, ["scripts/**/*.py", "scripts/*.py"])
    result = run_script("scripts/validate_surfaces.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_surfaces_rejects_root_level_recursive_extension(tmp_path: Path) -> None:
    # A root-level `**/*.X` (no `<dir>` prefix) is the same footgun: it misses a
    # top-level `top.py`. Its required sibling is the bare `*.X` (fresh-eye NIT).
    repo = tmp_path / "repo"
    _write_surfaces(repo, ["**/*.py"])
    result = run_script("scripts/validate_surfaces.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "non-recursive-fnmatch footgun" in result.stderr
    assert "sibling `*.py`" in result.stderr


def test_validate_surfaces_allows_bare_recursive_dir_glob(tmp_path: Path) -> None:
    # `<dir>/**` (no extension) and `<dir>/*/refs/**` are not the footgun and must pass.
    repo = tmp_path / "repo"
    _write_surfaces(repo, ["skills/public/**", "skills/public/*/references/**"])
    result = run_script("scripts/validate_surfaces.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_repo_python_surface_runs_fast_repo_copy_checker_before_broad_pytest() -> None:
    # #307: the fast standalone structural checker must run in the repo-python
    # surface's verify commands (the per-slice / pre-commit aggregate) so test-
    # fixture drift (e.g. inline shutil.ignore_patterns instead of REPO_COPY_IGNORE)
    # fails at the commit boundary in <1s, not 172s into the broad pytest gate.
    surfaces = json.loads((ROOT / ".agents" / "surfaces.json").read_text(encoding="utf-8"))
    repo_python = next(s for s in surfaces["surfaces"] if s["surface_id"] == "repo-python")
    verify = repo_python["verify_commands"]
    from scripts.slice_closeout_broad_gate import is_broad_pytest_command

    checker_idx = next(
        (i for i, cmd in enumerate(verify) if "check_test_repo_copy_invariants.py" in cmd), None
    )
    broad_idx = next((i for i, cmd in enumerate(verify) if is_broad_pytest_command(cmd)), None)
    assert checker_idx is not None, verify
    assert broad_idx is not None, verify
    # It must precede the broad pytest so fixture drift fails fast, not 172s deep.
    assert checker_idx < broad_idx, verify
