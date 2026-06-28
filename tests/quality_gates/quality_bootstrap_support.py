from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from pathlib import Path
from typing import NamedTuple

from .support import ROOT

_AGD_SPEC = importlib.util.spec_from_file_location(
    "inventory_adapter_gate_design",
    ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_adapter_gate_design.py",
)
assert _AGD_SPEC is not None and _AGD_SPEC.loader is not None
_AGD_MODULE = importlib.util.module_from_spec(_AGD_SPEC)
_AGD_SPEC.loader.exec_module(_AGD_MODULE)
_RESOLVE_SPEC = importlib.util.spec_from_file_location(
    "quality_resolve_adapter",
    ROOT / "skills" / "public" / "quality" / "scripts" / "resolve_adapter.py",
)
assert _RESOLVE_SPEC is not None and _RESOLVE_SPEC.loader is not None
_RESOLVE_MODULE = importlib.util.module_from_spec(_RESOLVE_SPEC)
_RESOLVE_SPEC.loader.exec_module(_RESOLVE_MODULE)
_BOOTSTRAP_SPEC = importlib.util.spec_from_file_location(
    "quality_bootstrap_adapter",
    ROOT / "skills" / "public" / "quality" / "scripts" / "bootstrap_adapter.py",
)
assert _BOOTSTRAP_SPEC is not None and _BOOTSTRAP_SPEC.loader is not None
_BOOTSTRAP_MODULE = importlib.util.module_from_spec(_BOOTSTRAP_SPEC)
_BOOTSTRAP_SPEC.loader.exec_module(_BOOTSTRAP_MODULE)
_INIT_SPEC = importlib.util.spec_from_file_location(
    "quality_init_adapter",
    ROOT / "skills" / "public" / "quality" / "scripts" / "init_adapter.py",
)
assert _INIT_SPEC is not None and _INIT_SPEC.loader is not None
_INIT_MODULE = importlib.util.module_from_spec(_INIT_SPEC)
_INIT_SPEC.loader.exec_module(_INIT_MODULE)


class _Result(NamedTuple):
    returncode: int
    stdout: str
    stderr: str


def _run_adapter_gate_design(*args: str) -> _Result:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    sys.argv = ["inventory_adapter_gate_design.py", *args]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = _AGD_MODULE.main()
    finally:
        sys.argv = saved_argv
    return _Result(returncode=code, stdout=out.getvalue(), stderr=err.getvalue())


def _run_quality_resolve_adapter(*args: str) -> _Result:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    sys.argv = ["resolve_adapter.py", *args]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = _RESOLVE_MODULE.main() or 0
    finally:
        sys.argv = saved_argv
    return _Result(returncode=code, stdout=out.getvalue(), stderr=err.getvalue())


def _run_quality_bootstrap_adapter(*args: str) -> _Result:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    sys.argv = ["bootstrap_adapter.py", *args]
    code = 0
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                _BOOTSTRAP_MODULE.main()
            except _BOOTSTRAP_MODULE.BootstrapValidationError as exc:
                print(str(exc), file=sys.stderr)
                code = 1
    finally:
        sys.argv = saved_argv
    return _Result(returncode=code, stdout=out.getvalue(), stderr=err.getvalue())


def _run_quality_init_adapter(*args: str) -> _Result:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    sys.argv = ["init_adapter.py", *args]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            _INIT_MODULE.main()
    finally:
        sys.argv = saved_argv
    return _Result(returncode=0, stdout=out.getvalue(), stderr=err.getvalue())


def seed_quality_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "docs" / "handoff.md").write_text("# Handoff\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    (repo / "tsconfig.json").write_text('{"compilerOptions":{"noEmit":true}}\n', encoding="utf-8")
    (repo / "package.json").write_text('{"name":"demo","workspaces":["packages/*"]}\n', encoding="utf-8")
    (repo / "pnpm-workspace.yaml").write_text("packages:\n  - packages/*\n", encoding="utf-8")
    (repo / "scripts" / "run-quality.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (repo / "scripts" / "validate_maintainer_setup.py").write_text("print('ok')\n", encoding="utf-8")
    (repo / "scripts" / "check-secrets.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (repo / "scripts" / "check_supply_chain.py").write_text("print('ok')\n", encoding="utf-8")
    return repo


def write_explicit_quality_adapter(repo: Path) -> None:
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/quality",
                "preset_id: python-quality",
                "customized_from: python-quality",
                "preset_lineage:",
                "- python-quality",
                "coverage_fragile_margin_pp: 0.5",
                "coverage_floor_policy:",
                "  min_statements_threshold: 45",
                "  fail_below_pct: 82.0",
                "  warn_ceiling_pct: 96.0",
                "  floor_drift_lock_pp: 0.5",
                "  exemption_list_path: scripts/custom-exemptions.txt",
                "  gate_script_pattern: \"*-boundary-gate.sh\"",
                "  lefthook_path: config/lefthook.yml",
                "  ci_workflow_glob: .github/workflows/quality-*.yml",
                "specdown_smoke_patterns: []",
                "spec_pytest_reference_format: \"Covered by pytest:\\s+`tests/custom[^`]+`\"",
                "prompt_asset_roots:",
                "- prompts",
                "recommendation_defaults_version: custom-v1",
                "adapter_review_sources:",
                "- .agents/quality-adapter.yaml",
                "domain_language_contract:",
                "  surface_globs:",
                "  - README.md",
                "  terms:",
                "  - id: external-tool-cli",
                "    canonical: charness tool",
                "acknowledged_recommendations:",
                "- demo.ack",
                "gate_design_review_globs:",
                "- scripts/*.py",
                "canonical_markdown_surfaces:",
                "- AGENTS.md",
                "- CLAUDE.md",
                "- docs/handoff.md",
                "prompt_asset_policy:",
                "  source_globs:",
                "  - src/**/*.py",
                "  min_multiline_chars: 256",
                "  exemption_globs:",
                "  - tests/**",
                "skill_ergonomics_gate_rules:",
                "  - mode_option_pressure_terms",
                "skill_ergonomics_skill_paths:",
                "  - packages/official-skills/acme-native/skills",
                "skill_ergonomics_runtime_install_skill_paths:",
                "  - packages/official-skills/acme-native/skills",
                "vendored_paths:",
                "  - packages/official-skills/charness-public",
                "public_spec_implementation_guard_min_lines: 80",
                "runtime_profile_default: local-fast",
                "runtime_budgets:",
                "  pytest: 70000",
                '  "pre-push:full-pytest": 19000',
                '  "pre-push:meta-fast": 27000',
                "runtime_budget_profiles:",
                "  local-fast:",
                "    budgets:",
                "      pytest: 45000",
                '      "pre-push:focused-quality-a": 12000',
                "  ci-slow:",
                "    budgets:",
                "      pytest: 540000",
                "startup_probes:",
                "  - label: demo-version",
                "    command:",
                "      - python3",
                "      - -V",
                "    class: standing",
                "    startup_mode: warm",
                "    surface: direct",
                "    samples: 2",
                "gate_commands:",
                "- python3 -m pytest -q",
                "preflight_commands: []",
                "security_commands: []",
                "concept_paths: []",
                "mutation_testing:",
                "  commands:",
                "    dry_run: python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode dry-run",
                "    full: python3 scripts/run_cosmic_ray_mutation.py --repo-root . --mode full",
                "    sample: ''",
                "    summary: python3 scripts/check_mutation_score.py --repo-root .",
                "  score_break: 60",
                "  schedule_cron: '17 */3 * * *'",
                "  changed_quota: 5",
                "  max_files: 10",
                "  max_executable_mutants: 120",
                "  max_executable_mutants_per_file: 80",
                "  max_test_nodeids: 40",
                "  auto_issue:",
                "    enabled: true",
                "    label: mutation-test",
                "    title: Mutation test regression on main",
                "    marker_token: mutation-test-regression",
                "  workflow_path: .github/workflows/mutation-tests.yml",
                "  report_paths:",
                "    summary_md: reports/mutation/summary.md",
                "    sample_md: reports/mutation/sample.md",
                "    log: reports/mutation/run.log",
                "  declined: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
