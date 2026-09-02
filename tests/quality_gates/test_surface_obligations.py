from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from scripts.surfaces_lib import SurfaceError, load_surfaces, path_matches_patterns
from tools import validate_surfaces

from .seeding_support import write_json, write_surface
from .support import ROOT, run_script


def run_validate_surfaces(*args: str) -> SimpleNamespace:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    sys.argv = ["validate_surfaces.py", *args]
    returncode = 0
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                returncode = validate_surfaces.main() or 0
            except SurfaceError as exc:
                print(str(exc), file=sys.stderr)
                returncode = 1
    finally:
        sys.argv = saved_argv
    return SimpleNamespace(returncode=returncode, stdout=out.getvalue(), stderr=err.getvalue())


def test_check_changed_surfaces_reports_expected_obligations_for_readme() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "materialized-plugin-export" in surface_ids
    assert "repo-markdown" in surface_ids
    assert "python3 scripts/sync_root_plugin_manifests.py --repo-root ." in payload["sync_commands"]
    assert "python3 scripts/validate_packaging.py --repo-root ." in payload["verify_commands"]
    assert (
        "python3 -m tools.validate_packaging_committed --repo-root ." in payload["verify_commands"]
    )
    assert "./scripts/check-docs.sh" in payload["verify_commands"]


def test_adapter_surface_pattern_covers_a_nested_helper() -> None:
    manifest = load_surfaces(ROOT)
    adapter_surface = next(
        item for item in manifest["surfaces"] if item["surface_id"] == "adapters"
    )

    assert path_matches_patterns(
        "scripts/pkg/adapter_helper_lib.py", adapter_surface["source_paths"]
    )
    assert path_matches_patterns("scripts/adapter_helper_lib.py", adapter_surface["source_paths"])


def _verify_commands_for(*paths: str) -> list[str]:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        *paths,
    )
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)["verify_commands"]


_GITIGNORE_SCAN = (
    "python3 skills/public/quality/scripts/inventory_gitignore_scan_hygiene.py "
    "--repo-root . --require-empty --require-git-file-listing"
)
_RETRO_INDEX_CHECK = "python3 scripts/build_retro_lesson_selection_index.py --repo-root . --check"
_SUBPROCESS_FORM = (
    "python3 scripts/check_subprocess_form.py --repo-root . --require-git-file-listing"
)
_STANDING_PYTEST = "python3 scripts/run_standing_pytest.py --repo-root . --mode read-only"
_SPEC_EVIDENCE = (
    "python3 scripts/check_spec_evidence_durability.py --repo-root . --require-git-file-listing"
)


def test_gitignore_scan_hygiene_runs_for_skill_scripts() -> None:
    # #325 was a skills/public/quality script using repo_root.glob; it is caught
    # by the same focused surface checks as other skill scripts.
    assert _GITIGNORE_SCAN in _verify_commands_for(
        "skills/public/quality/scripts/standing_doc_provenance_lib.py"
    )


def test_retro_lesson_index_check_runs_for_retro_artifacts() -> None:
    # The retro lesson-index freshness check is reachable for a changed retro
    # artifact (the surface also syncs --write first).
    assert _RETRO_INDEX_CHECK in _verify_commands_for(
        "charness-artifacts/retro/2026-06-07-322-advisory-interpretation-rollout.md"
    )


def test_sloc_inventory_refresh_is_sync_obligation_not_verify() -> None:
    command = (
        "python3 skills/public/quality/scripts/inventory_sloc.py --repo-root . "
        "--output charness-artifacts/quality/sloc-inventory/latest.json"
    )
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness-artifacts/quality/sloc-inventory/latest.json",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert "quality-inventory-artifacts" in {
        surface["surface_id"] for surface in payload["matched_surfaces"]
    }
    assert command in payload["sync_commands"]
    assert command not in payload["verify_commands"]


def test_subprocess_form_runs_for_repo_python_surface() -> None:
    # A production spawn-form violation is covered by the repo-python surface,
    # not only the standalone quality runner.
    assert _SUBPROCESS_FORM in _verify_commands_for("tests/quality_gates/test_new_thing.py")


def test_repo_markdown_surface_matches_top_level_packaging_readme() -> None:
    # #331 sibling: packaging/README.md (top-level) escaped repo-markdown's
    # packaging/**/*.md (non-recursive fnmatch) and so skipped check-markdown,
    # check_doc_links, and check-secrets at closeout. The <dir>/*.md idiom covers
    # both top-level and nested.
    verify = _verify_commands_for("packaging/README.md")
    assert "./scripts/check-docs.sh" in verify


def test_repo_markdown_routes_durable_evidence_before_broad_pytest() -> None:
    assert _SPEC_EVIDENCE in _verify_commands_for("charness-artifacts/quality/2026-07-18-review.md")


def test_repo_python_surface_matches_top_level_scripts() -> None:
    # #331 regression guard: every scripts/ file is top-level, and the bare
    # scripts/**/*.py idiom (non-recursive fnmatch) matched none of them, silently
    # keeping the whole repo-python verify set (subprocess form, broad pytest) out
    # of every scripts closeout. scripts/*.py matches top-level AND nested.
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "scripts/release_changed_line_coverage.py",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert "repo-python" in {surface["surface_id"] for surface in payload["matched_surfaces"]}
    verify = payload["verify_commands"]
    assert _SUBPROCESS_FORM in verify
    assert _STANDING_PYTEST in verify


def test_repo_python_surface_matches_shell_test_fixtures() -> None:
    verify = _verify_commands_for("tests/quality_gates/fixtures/fake_tool.sh")

    assert "./scripts/check-shell.sh" in verify
    assert _STANDING_PYTEST in verify


def test_check_changed_surfaces_treats_charness_artifacts_as_repo_markdown() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness-artifacts/setup/latest.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "repo-markdown" in surface_ids
    assert payload["unmatched_paths"] == []


def test_retro_prepare_packet_pair_matches_retro_surface() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "charness-artifacts/retro/demo-packet.json",
        "charness-artifacts/retro/demo-packet.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    surface_ids = {surface["surface_id"] for surface in payload["matched_surfaces"]}
    assert "retro-lesson-selection-index" in surface_ids
    assert "repo-markdown" in surface_ids
    assert payload["unmatched_paths"] == []
    assert any("retro_packet_json" in command for command in payload["verify_commands"])


def test_check_changed_surfaces_verifies_mutation_workflow_actions() -> None:
    result = run_script(
        "scripts/check_changed_surfaces.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        ".github/workflows/mutation-tests.yml",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
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
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
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
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["matched_surfaces"] == []
    assert payload["unmatched_paths"] == ["notes/private-plan.txt"]


def test_select_verifiers_returns_smallest_repo_owned_bundle_for_readme() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "README.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["bundle_status"] == "repo-owned-bundle"
    recommendations = payload["recommended_commands"]
    assert recommendations[0] == {
        "phase": "sync",
        "command": "python3 scripts/sync_root_plugin_manifests.py --repo-root .",
        "reason_surface_ids": ["materialized-plugin-export"],
    }
    verify_commands = {item["command"] for item in recommendations if item["phase"] == "verify"}
    assert "python3 scripts/validate_packaging.py --repo-root ." in verify_commands
    assert "python3 -m tools.validate_packaging_committed --repo-root ." in verify_commands
    assert "./scripts/check-docs.sh" in verify_commands


def test_select_verifiers_includes_public_skill_policy_for_public_skill_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "skills/public/critique/SKILL.md",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    verify_commands = {
        item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"
    }
    assert "python3 -m tools.validate_skills --repo-root ." in verify_commands
    assert "python3 -m tools.validate_public_skill_validation --repo-root ." in verify_commands
    assert "python3 -m tools.validate_public_skill_dogfood --repo-root ." in verify_commands


def test_select_verifiers_includes_public_skill_policy_for_policy_json_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/public-skill-validation.json",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    verify_commands = {
        item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"
    }
    assert "python3 -m tools.validate_public_skill_validation --repo-root ." in verify_commands


def test_select_verifiers_includes_public_skill_dogfood_for_registry_changes() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "docs/public-skill-dogfood.json",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    verify_commands = {
        item["command"] for item in payload["recommended_commands"] if item["phase"] == "verify"
    }
    assert "python3 -m tools.validate_public_skill_dogfood --repo-root ." in verify_commands


def test_select_verifiers_reports_missing_bundle_for_unmatched_paths() -> None:
    result = run_script(
        "scripts/select_verifiers.py",
        "--repo-root",
        str(ROOT),
        "--paths",
        "notes/private-plan.txt",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["bundle_status"] == "missing-bundle"
    assert payload["recommended_commands"] == []
    assert any("not covered by `.agents/surfaces.json`" in note for note in payload["notes"])
    assert any(
        "No repo-owned verifier bundle matched these changes" in note for note in payload["notes"]
    )


def test_validate_surfaces_rejects_duplicate_ids(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    write_json(
        repo / ".agents" / "surfaces.json",
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
    )

    result = run_validate_surfaces("--repo-root", str(repo))
    assert result.returncode == 1
    assert "duplicate surface id `dup`" in result.stderr


def _write_surfaces(repo: Path, source_paths: list[str]) -> None:
    write_surface(
        repo,
        "idiom",
        "idiom lint fixture",
        source_paths,
    )


def test_validate_surfaces_rejects_recursive_extension_without_sibling(tmp_path: Path) -> None:
    # The #331 footgun: `<dir>/**/*.X` under fnmatch silently misses a top-level
    # `<dir>/<file>.X`. The lint must fail closed when the `<dir>/*.X` sibling is absent.
    repo = tmp_path / "repo"
    _write_surfaces(repo, ["scripts/**/*.py"])
    try:
        load_surfaces(repo)
    except SurfaceError as exc:
        message = str(exc)
        assert "non-recursive-fnmatch footgun" in message
        assert "scripts/*.py" in message
    else:
        raise AssertionError("load_surfaces did not reject recursive extension without sibling")


def test_validate_surfaces_accepts_recursive_extension_with_sibling(tmp_path: Path) -> None:
    # Keeping the `**/*.X` form is allowed as long as the strict-superset sibling is present.
    repo = tmp_path / "repo"
    _write_surfaces(repo, ["scripts/**/*.py", "scripts/*.py"])
    assert load_surfaces(repo) is not None


def test_validate_surfaces_rejects_root_level_recursive_extension(tmp_path: Path) -> None:
    # A root-level `**/*.X` (no `<dir>` prefix) is the same footgun: it misses a
    # top-level `top.py`. Its required sibling is the bare `*.X` (fresh-eye NIT).
    repo = tmp_path / "repo"
    _write_surfaces(repo, ["**/*.py"])
    try:
        load_surfaces(repo)
    except SurfaceError as exc:
        message = str(exc)
        assert "non-recursive-fnmatch footgun" in message
        assert "sibling `*.py`" in message
    else:
        raise AssertionError("load_surfaces did not reject root-level recursive extension")


def test_validate_surfaces_allows_bare_recursive_dir_glob(tmp_path: Path) -> None:
    # `<dir>/**` (no extension) and `<dir>/*/refs/**` are not the footgun and must pass.
    repo = tmp_path / "repo"
    _write_surfaces(repo, ["skills/public/**", "skills/public/*/references/**"])
    result = run_validate_surfaces("--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_repo_python_surface_runs_fast_repo_copy_checker_before_standing_pytest() -> None:
    # #307: the fast standalone structural checker must run in the repo-python
    # surface's verify commands so test-
    # fixture drift (e.g. inline shutil.ignore_patterns instead of REPO_COPY_IGNORE)
    # fails at the commit boundary in <1s, not 172s into standing pytest.
    surfaces = json.loads((ROOT / ".agents" / "surfaces.json").read_text(encoding="utf-8"))
    repo_python = next(s for s in surfaces["surfaces"] if s["surface_id"] == "repo-python")
    verify = repo_python["verify_commands"]
    checker_idx = next(
        (i for i, cmd in enumerate(verify) if "check_test_repo_copy_invariants.py" in cmd), None
    )
    pytest_idx = next((i for i, cmd in enumerate(verify) if "run_standing_pytest.py" in cmd), None)
    assert checker_idx is not None, verify
    assert pytest_idx is not None, verify
    # It must precede standing pytest so fixture drift fails fast, not 172s deep.
    assert checker_idx < pytest_idx, verify
