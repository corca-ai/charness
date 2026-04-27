from __future__ import annotations

import json
from pathlib import Path

from .support import ADAPTER_LIB, ROOT, init_git_repo, run_script


def test_release_current_release_reports_packaging_version() -> None:
    result = run_script("skills/public/release/scripts/current_release.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    expected = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]
    assert payload["package_id"] == "charness"
    assert payload["surface_versions"]["packaging_manifest"] == expected
    assert payload["checked_in_plugin_root"].endswith("plugins/charness")


def test_narrative_map_sources_reports_checked_in_docs() -> None:
    result = run_script("skills/public/narrative/scripts/map_sources.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    source_paths = {entry["path"] for entry in payload["source_documents"]}
    assert "README.md" in source_paths
    assert "docs/handoff.md" in source_paths
    assert payload["artifact_path"] == "charness-artifacts/narrative/latest.md"
    assert payload["freshness"]["status"] in {"ahead", "current", "missing-remote", "not-git", "unavailable"}


def test_init_repo_skill_bootstraps_probe_surface_guidance() -> None:
    skill_text = (ROOT / "skills" / "public" / "init-repo" / "SKILL.md").read_text(encoding="utf-8")
    probe_reference = (
        ROOT / "skills" / "public" / "init-repo" / "references" / "probe-surface.md"
    ).read_text(encoding="utf-8")

    assert "probe surface" in skill_text
    assert "installable CLI" in skill_text
    assert "binary healthcheck" in probe_reference
    assert "machine-readable command discovery" in probe_reference
    assert "local discoverability" in probe_reference


def test_init_repo_default_surfaces_carry_early_quality_baseline() -> None:
    default_surfaces = (
        ROOT / "skills" / "public" / "init-repo" / "references" / "default-surfaces.md"
    ).read_text(encoding="utf-8")

    assert "## Early Quality Baseline" in default_surfaces
    assert "Python: `ruff check` with `E`, `F`, `I`, and `C90`" in default_surfaces
    assert "JavaScript/TypeScript: `eslint`, a standing `complexity` rule" in default_surfaces
    assert "let `quality` own the exact gate wiring" in default_surfaces
    assert "ratcheting" in default_surfaces


def test_init_repo_agent_docs_carry_bounded_subagent_delegation_rule() -> None:
    skill_text = (ROOT / "skills" / "public" / "init-repo" / "SKILL.md").read_text(
        encoding="utf-8"
    ).lower()
    agent_docs = (
        ROOT / "skills" / "public" / "init-repo" / "references" / "agent-docs-policy.md"
    ).read_text(encoding="utf-8").lower()
    default_surfaces = (
        ROOT / "skills" / "public" / "init-repo" / "references" / "default-surfaces.md"
    ).read_text(encoding="utf-8").lower()

    assert "already delegated" in skill_text
    assert "second user message" in skill_text
    assert "same-agent pass" in skill_text
    assert "explicit delegation request" in agent_docs
    assert "already delegated by the repo contract" in agent_docs
    assert "second user message asking for delegation" in agent_docs
    assert "same-agent pass" in agent_docs
    assert "explicit delegation request" in default_surfaces
    assert "already delegated by the repo" in default_surfaces
    assert "same-agent pass" in default_surfaces


def test_init_repo_docs_carry_charness_artifact_commit_policy() -> None:
    skill_text = (ROOT / "skills/public/init-repo/SKILL.md").read_text(encoding="utf-8").lower()
    agent_docs = (ROOT / "skills/public/init-repo/references/agent-docs-policy.md").read_text(encoding="utf-8").lower()
    default_surfaces = (ROOT / "skills/public/init-repo/references/default-surfaces.md").read_text(encoding="utf-8").lower()
    normalization_flow = (ROOT / "skills/public/init-repo/references/normalization-flow.md").read_text(encoding="utf-8").lower()

    for text in (skill_text, agent_docs, default_surfaces, normalization_flow):
        assert "charness-artifacts/" in text
        assert "repo state" in text
        assert "canonical content" in text

    assert "commit targets" in agent_docs
    assert "current-pointer helpers should no-op" in agent_docs
    assert "commit targets" in default_surfaces


def test_hitl_skill_carries_review_chunk_and_state_recording_rules() -> None:
    skill_text = (ROOT / "skills" / "public" / "hitl" / "SKILL.md").read_text(encoding="utf-8")
    chunk_contract = (
        ROOT / "skills" / "public" / "hitl" / "references" / "chunk-contract.md"
    ).read_text(encoding="utf-8")
    state_model = (
        ROOT / "skills" / "public" / "hitl" / "references" / "state-model.md"
    ).read_text(encoding="utf-8")
    adapter_contract = (
        ROOT / "skills" / "public" / "hitl" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")

    assert "Apply Phase" in skill_text
    assert "Never edit the target file mid-chunk" in skill_text
    assert "Do not edit the target file while the review loop is in progress" in skill_text
    assert "display-only pseudo-tags" in skill_text
    assert "Accepted Working Text" in skill_text
    assert "last_presented_chunk_id" in skill_text
    assert "explicit apply instruction" in adapter_contract
    assert "accepted-chunk-or-final-apply-boundary" in adapter_contract
    assert "<bash>" in chunk_contract
    assert "not instructions to\nedit the target document" in chunk_contract
    assert "Accepted working text" in state_model
    assert "persist accepted decisions before advancing the cursor" in state_model


def test_impl_skill_routes_validation_and_browser_proof_explicitly() -> None:
    skill_text = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
    quality_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    verification_ladder = (
        ROOT / "skills" / "public" / "impl" / "references" / "verification-ladder.md"
    ).read_text(encoding="utf-8")
    find_skills = (ROOT / "skills" / "public" / "find-skills" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "operator reading" in skill_text
    assert "--recommendation-role validation --next-skill-id" in find_skills
    assert "say explicitly that it did not run" in skill_text
    assert "code/fixture" in skill_text
    assert "Browser-Facing Output" in verification_ladder
    assert "same-agent/manual review" in verification_ladder
    assert "operator reading test" in quality_text
    assert "before downgrading to HITL" in quality_text


def test_debug_and_quality_carry_async_and_hidden_network_field_lessons() -> None:
    debug_text = (ROOT / "skills" / "public" / "debug" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    quality_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    maintainer_local = (
        ROOT
        / "skills"
        / "public"
        / "quality"
        / "references"
        / "maintainer-local-enforcement.md"
    ).read_text(encoding="utf-8")

    assert "pre-worker\n     acknowledgement" in debug_text
    assert "worker execution" in debug_text
    assert "post-worker side effects" in debug_text
    assert "earliest component that can produce observable status" in debug_text
    assert "hidden network/external-repo work" in quality_text
    assert "external-repo fetch" in maintainer_local
    assert "explicit refresh,\n> update, or release action" in maintainer_local


def test_development_doc_carries_mutation_phase_barrier_rule() -> None:
    development = (ROOT / "docs" / "development.md").read_text(encoding="utf-8")

    assert "## Mutation Phase Barriers" in development
    assert "mutate" in development
    assert "sync generated surfaces" in development
    assert "verify" in development
    assert "publish" in development
    assert "parallelism is only safe for read-only inventory" in development


def test_public_skill_validation_doc_keeps_premortem_and_on_demand_boundary_visible() -> None:
    validation_doc = (ROOT / "docs" / "public-skill-validation.md").read_text(encoding="utf-8")

    assert "`premortem`" in validation_doc
    assert "on-demand proof through" in validation_doc
    assert "underlying evaluator state or storage layer" in validation_doc


def test_control_plane_documents_authenticated_release_probe_contract() -> None:
    control_plane = (ROOT / "docs" / "control-plane.md").read_text(encoding="utf-8")

    assert "authenticated `gh api`" in control_plane
    assert "`GH_TOKEN` or `GITHUB_TOKEN`" in control_plane
    assert "public unauthenticated HTTP" in control_plane
    assert "`status`, `reason`, and" in control_plane
    assert "github-forbidden" in control_plane


def test_init_repo_synthesize_operator_acceptance_outputs_tiered_draft(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "specs").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (repo / "scripts" / "run-quality.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (repo / "docs" / "specs" / "demo.spec.md").write_text(
        "\n".join(
            [
                "# Demo Spec",
                "",
                "## Local Smoke",
                "",
                "### Functional Check",
                "",
                "```bash",
                "./scripts/run-quality.sh",
                "```",
                "",
                "## Hosted Publish",
                "",
                "### Functional Check",
                "",
                "```bash",
                "gh workflow run release.yml",
                "```",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/init-repo/scripts/synthesize_operator_acceptance.py",
        "--repo-root",
        str(repo),
        "--json",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["shared_start_commands"] == [
        "git status --short",
        "sed -n '1,220p' docs/handoff.md",
        "sed -n '1,260p' docs/roadmap.md 2>/dev/null || true",
        "./scripts/run-quality.sh",
    ]
    assert payload["acceptance_buckets"]["cheap_first"][0]["commands"] == "./scripts/run-quality.sh"
    assert "gh workflow run release.yml" in payload["acceptance_buckets"]["external_or_costly"][0]["commands"]
    assert payload["acceptance_buckets"]["human_judgment"][0]["source_path"] == "docs/handoff.md"
    assert "## Cheap First" in payload["markdown"]
    assert "## External Or Costly Checks" in payload["markdown"]
    assert "## Human Judgment" in payload["markdown"]


def test_release_bump_version_updates_manifest_and_runs_sync(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "packaging").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)

    (repo / ".agents" / "release-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/release",
                "preset_id: portable-defaults",
                "customized_from: portable-defaults",
                "package_id: demo",
                "packaging_manifest_path: packaging/demo.json",
                "checked_in_plugin_root: plugins/demo",
                "sync_command: python3 scripts/sync_root_plugin_manifests.py --repo-root .",
                "quality_command: ./scripts/run-quality.sh",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "packaging" / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "package_id": "demo",
                "display_name": "demo",
                "version": "0.0.0-dev",
                "summary": "Demo package.",
                "author": {"name": "Demo"},
                "homepage": "https://example.com/demo",
                "repository": "https://example.com/demo",
                "source": {
                    "readme": "README.md",
                    "skills_dir": "skills",
                    "public_skills_dir": "skills/public",
                    "support_skills_dir": "skills/support",
                    "profiles_dir": "profiles",
                    "presets_dir": "presets",
                    "integrations_dir": "integrations/tools",
                },
                "codex": {"manifest": {"version": "0.0.0-dev"}},
                "claude": {"manifest": {"version": "0.0.0-dev"}},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "sync_root_plugin_manifests.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "import json",
                "from pathlib import Path",
                "",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--repo-root', type=Path, required=True)",
                "args = parser.parse_args()",
                "repo_root = args.repo_root.resolve()",
                "version = json.loads((repo_root / 'packaging' / 'demo.json').read_text(encoding='utf-8'))['version']",
                "(repo_root / 'sync-version.txt').write_text(version + '\\n', encoding='utf-8')",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("skills/public/release/scripts/bump_version.py", "--repo-root", str(repo), "--part", "patch")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert payload["old_version"] == "0.0.0-dev"
    assert payload["new_version"] == "0.0.1"
    assert manifest["version"] == "0.0.1"
    assert manifest["claude"]["manifest"]["version"] == "0.0.1"
    assert manifest["codex"]["manifest"]["version"] == "0.0.1"
    assert (repo / "sync-version.txt").read_text(encoding="utf-8").strip() == "0.0.1"


def test_adapter_lib_renders_and_loads_simple_yaml_mapping() -> None:
    rendered = ADAPTER_LIB.render_yaml_mapping(
        [
            ("version", 1),
            ("repo", "demo"),
            ("output_dir", "charness-artifacts/demo"),
            (
                "policy",
                {
                    "glob": "*-quality-gate.sh",
                    "threshold": 30,
                },
            ),
            ("commands", ["pytest -q", "ruff check ."]),
            ("empty", []),
        ]
    )
    assert ADAPTER_LIB.load_yaml(rendered) == {
        "version": 1,
        "repo": "demo",
        "output_dir": "charness-artifacts/demo",
        "policy": {
            "glob": "*-quality-gate.sh",
            "threshold": 30,
        },
        "commands": ["pytest -q", "ruff check ."],
        "empty": [],
    }


def test_adapter_lib_renders_and_loads_list_of_mappings() -> None:
    rendered = ADAPTER_LIB.render_yaml_mapping(
        [
            (
                "startup_probes",
                [
                    {
                        "label": "demo-version",
                        "command": ["python3", "demo.py", "--version"],
                        "class": "standing",
                        "startup_mode": "warm",
                        "surface": "direct",
                        "samples": 2,
                    }
                ],
            )
        ]
    )
    assert ADAPTER_LIB.load_yaml(rendered) == {
        "startup_probes": [
            {
                "label": "demo-version",
                "command": ["python3", "demo.py", "--version"],
                "class": "standing",
                "startup_mode": "warm",
                "surface": "direct",
                "samples": 2,
            }
        ]
    }


def test_quality_skill_carries_blind_spot_policy_and_premortem_refs() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    adapter_contract = (
        ROOT / "skills" / "public" / "quality" / "references" / "adapter-contract.md"
    ).read_text(encoding="utf-8")
    floor_policy = (
        ROOT / "skills" / "public" / "quality" / "references" / "coverage-floor-policy.md"
    ).read_text(encoding="utf-8")
    premortem = (
        ROOT / "skills" / "public" / "quality" / "references" / "fresh-eye-premortem.md"
    ).read_text(encoding="utf-8")
    prompt_policy = (
        ROOT / "skills" / "public" / "quality" / "references" / "prompt-asset-policy.md"
    ).read_text(encoding="utf-8")

    assert "prior quality artifact is history" in skill_text
    assert "fresh-eye premortem" in skill_text
    assert "active` or `passive" in skill_text
    assert "prompt/content bulk" in skill_text
    assert "fresh 5-minute reader" in skill_text
    assert "coverage_floor_policy" in adapter_contract
    assert "spec_pytest_reference_format" in adapter_contract
    assert "prompt_asset_policy" in adapter_contract
    assert "gate_script_pattern" in floor_policy
    assert "warn band" in floor_policy
    assert "authoritative universe" in premortem
    assert "misclassify as absent" in premortem
    assert "prompt/content bulk" in prompt_policy
    assert "find_inline_prompt_bulk.py" in prompt_policy


def test_quality_skill_carries_code_reduction_and_ratio_patterns() -> None:
    skill_text = (ROOT / "skills" / "public" / "quality" / "SKILL.md").read_text(encoding="utf-8")
    automation = (
        ROOT / "skills" / "public" / "quality" / "references" / "automation-promotion.md"
    ).read_text(encoding="utf-8")
    economics = (
        ROOT / "skills" / "public" / "quality" / "references" / "executable-spec-economics.md"
    ).read_text(encoding="utf-8")
    lenses = (
        ROOT / "skills" / "public" / "quality" / "references" / "quality-lenses.md"
    ).read_text(encoding="utf-8")
    enforcement = (
        ROOT / "skills" / "public" / "quality" / "references" / "maintainer-local-enforcement.md"
    ).read_text(encoding="utf-8")

    assert "prefer the smaller production surface first" in skill_text
    assert "bounded test-ratio posture" in skill_text
    assert "stale gate wiring" in skill_text
    assert "shrinking production\nsurface" in automation
    assert "changed-file router" in economics
    assert "bounded test-ratio posture" in lenses
    assert "adapter-driven local enforcement as a positive pattern" in lenses
    assert "strong positive pattern" in enforcement


def test_check_duplicates_rejects_near_duplicate_docs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    repeated_lines = "\n".join(f"- repeated line {i}" for i in range(20))
    (docs_dir / "alpha.md").write_text(f"# Alpha\n\n{repeated_lines}\n", encoding="utf-8")
    (docs_dir / "beta.md").write_text(f"# Beta\n\n{repeated_lines}\n", encoding="utf-8")

    result = run_script("scripts/check_duplicates.py", "--repo-root", str(repo), "--fail-on-match", "--json")
    assert result.returncode == 1
    duplicates = json.loads(result.stdout)
    assert duplicates
    assert duplicates[0]["left"] == "docs/alpha.md"
    assert duplicates[0]["right"] == "docs/beta.md"


def test_check_duplicates_ignores_gitignored_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    repeated_lines = "\n".join(f"- repeated line {i}" for i in range(20))
    (repo / ".gitignore").write_text("docs/generated-*.md\n", encoding="utf-8")
    (docs_dir / "alpha.md").write_text(f"# Alpha\n\n{repeated_lines}\n", encoding="utf-8")
    (docs_dir / "generated-beta.md").write_text(f"# Beta\n\n{repeated_lines}\n", encoding="utf-8")
    init_git_repo(repo, ".gitignore", "docs/alpha.md")

    result = run_script("scripts/check_duplicates.py", "--repo-root", str(repo), "--fail-on-match", "--json")
    assert result.returncode == 0, result.stderr
    duplicates = json.loads(result.stdout)
    assert duplicates == []


def test_find_skills_lists_adapter_configured_trusted_roots(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    local_skill_dir = repo / "skills" / "public" / "local-demo"
    trusted_skill_dir = repo / "vendor" / "trusted-skills" / "trusted-demo"
    adapter_dir = repo / ".agents"
    local_skill_dir.mkdir(parents=True)
    trusted_skill_dir.mkdir(parents=True)
    adapter_dir.mkdir(parents=True)

    (local_skill_dir / "SKILL.md").write_text(
        "\n".join(["---", "name: local-demo", 'description: "Local demo skill."', "---", "", "# Local Demo"]),
        encoding="utf-8",
    )
    (trusted_skill_dir / "SKILL.md").write_text(
        "\n".join(["---", "name: trusted-demo", 'description: "Trusted demo skill."', "---", "", "# Trusted Demo"]),
        encoding="utf-8",
    )
    (adapter_dir / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/find-skills",
                "trusted_skill_roots:",
                "- vendor/trusted-skills",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("skills/public/find-skills/scripts/list_capabilities.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["public_skills"][0]["id"] == "local-demo"
    assert payload["trusted_skills"][0]["id"] == "trusted-demo"


def test_impl_survey_reports_broken_preferred_skill_symlink(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    adapter_dir = repo / ".agents"
    skills_dir = adapter_dir / "skills"
    adapter_dir.mkdir(parents=True)
    skills_dir.mkdir(parents=True)

    (adapter_dir / "impl-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: charness-artifacts/impl",
                "verification_tools:",
                "- cmd:python3",
                "- skill:agent-browser",
                "ui_verification_tools:",
                "- skill:agent-browser",
                "verification_install_proposals:",
                "- Install the preferred browser verifier before closing UI work.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (skills_dir / "agent-browser").symlink_to(repo / "missing-agent-browser")

    result = run_script("skills/public/impl/scripts/survey_verification.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["missing_tools"] == ["skill:agent-browser"]
    assert payload["missing_ui_tools"] == ["skill:agent-browser"]
    assert payload["tool_checks"][1]["warning"].startswith("Broken skill symlink:")
    assert "Repo-specific verification install proposals are available." in payload["warnings"]

def test_impl_skill_carries_truth_surface_sync_guardrail() -> None:
    skill_text = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
    adapter_contract = (ROOT / "skills" / "public" / "impl" / "references" / "adapter-contract.md").read_text(encoding="utf-8")
    assert "Sync truth surfaces and re-read the contract before closeout." in skill_text
    assert "Truth Surface Sync" in skill_text
    assert "truth_surfaces" in adapter_contract
    assert "README.md" in adapter_contract

def test_impl_skill_defaults_to_autonomous_continuation() -> None:
    skill_text = (ROOT / "skills" / "public" / "impl" / "SKILL.md").read_text(encoding="utf-8")
    assert "AUTONOMOUS CONTINUATION" in skill_text
    assert "continuation" in skill_text and "checkpoints" in skill_text
    assert "irreversible" in skill_text and "external side effect" in skill_text
    assert "next locally decidable slice" in skill_text
    assert "check_auto_trigger.py" in skill_text
