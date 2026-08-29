from __future__ import annotations

import importlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
EVAL_REGISTRY = importlib.import_module("scripts.eval_registry")

ADAPTER_LIB_PATH = ROOT / "scripts" / "adapter_lib.py"
ADAPTER_LIB_SPEC = importlib.util.spec_from_file_location("adapter_lib", ADAPTER_LIB_PATH)
assert ADAPTER_LIB_SPEC is not None and ADAPTER_LIB_SPEC.loader is not None
ADAPTER_LIB = importlib.util.module_from_spec(ADAPTER_LIB_SPEC)
ADAPTER_LIB_SPEC.loader.exec_module(ADAPTER_LIB)

# The YAML emitter now lives beside the parser rather than inside it. Round-trip tests
# need both halves, so both are loaded here instead of one re-exporting the other.
ADAPTER_RENDER_LIB_PATH = ROOT / "scripts" / "adapter_yaml_render_lib.py"
ADAPTER_RENDER_LIB_SPEC = importlib.util.spec_from_file_location("adapter_yaml_render_lib", ADAPTER_RENDER_LIB_PATH)
assert ADAPTER_RENDER_LIB_SPEC is not None and ADAPTER_RENDER_LIB_SPEC.loader is not None
ADAPTER_RENDER_LIB = importlib.util.module_from_spec(ADAPTER_RENDER_LIB_SPEC)
ADAPTER_RENDER_LIB_SPEC.loader.exec_module(ADAPTER_RENDER_LIB)


def _load_script_module(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


SETUP_INSPECT_REPO = _load_script_module(
    "tests.quality_gates.support_setup_inspect_repo",
    ROOT / "skills/public/setup/scripts/inspect_repo.py",
)
SETUP_RESOLVE_ADAPTER = _load_script_module(
    "tests.quality_gates.support_setup_resolve_adapter",
    ROOT / "skills/public/setup/scripts/resolve_adapter.py",
)


def run_script(
    *args: str, cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def inspect_setup_repo(repo: Path, *, env: dict[str, str] | None = None) -> dict[str, object]:
    """Parse `inspect_repo.py`'s report payload.

    Repo-owned command output is YAML since the 2026-08-14 `--json` removal, so this
    parses with `yaml.safe_load`. YAML is a JSON superset, so a payload that is still
    literal JSON -- including the compact-JSON fallback `render_yaml` uses when PyYAML
    is absent -- parses here unchanged.
    """
    result = run_loaded_script_main("inspect_repo.py", SETUP_INSPECT_REPO, "--repo-root", str(repo), env=env)
    assert result.returncode == 0, result.stderr
    return yaml.safe_load(result.stdout)


def bundle_payload_or_report(result, label: str) -> dict:
    """Parse a bundle CLI's plan payload, and surface stderr when there is none to parse.

    A round found the first version of this in one test file only, so the OTHER surface still
    failed a crash or an argparse error with a bare parse error and dropped stderr. Both
    use this now. Parsing before asserting the exit code is what made the loss possible: for a
    crashed run stdout is empty and everything the reader needs is on stderr.

    Repo-owned command output is YAML since the 2026-08-14 `--json` removal, so this parses
    with `yaml.safe_load`. YAML is a JSON superset, so a payload that is still literal JSON
    parses here unchanged.
    """
    if not result.stdout.strip():
        raise AssertionError(
            f"{label} produced no payload on stdout; returncode={result.returncode}, "
            f"stderr={result.stderr.strip()!r}"
        )
    try:
        parsed = yaml.safe_load(result.stdout)
    except yaml.YAMLError as exc:
        raise AssertionError(
            f"{label} stdout was not YAML ({exc}); returncode={result.returncode}, "
            f"stdout={result.stdout[:400]!r}, stderr={result.stderr.strip()!r}"
        ) from exc
    if not isinstance(parsed, dict):
        raise AssertionError(f"{label} payload was {type(parsed).__name__}, not an object: {parsed!r}")
    return parsed


def bundle_blocker_report(payload: dict, label: str) -> str:
    """Render a bundle payload's blockers as the message they already carry.

    A correct bundle-preflight refusal used to surface as FIVE failing tests whose only
    diagnostic was pytest's truncated `CompletedProcess` repr — the structured blocker, with
    its `code`, `message`, `remediation`, and the paths in `subject`, never reached the reader
    deliberately. `assert result.returncode == 0, result.stderr` looked like it supplied a
    message and supplied nothing, because these scripts report on stdout.

    Used by the ONE test per bundle surface that asks "is this repo bundle-ready right now".
    """
    blockers = payload.get("blockers") or []
    preflight = payload.get("preflight") or {}
    if not blockers and isinstance(preflight, dict):
        blockers = preflight.get("blockers") or []
    if not isinstance(blockers, list):
        # This helper builds an ASSERTION MESSAGE. Raising here would mask the real failure
        # with an AttributeError from inside the reporter.
        return f"{label} reported a non-list `blockers` value: {blockers!r}"
    raised = payload.get("error")
    lines: list[str] = []
    if isinstance(raised, str):
        # Reported ALONGSIDE any blockers rather than instead of them: an execute-mode failure
        # payload carries both an `error` and a preflight full of real blockers, and a round
        # caught the first version discarding the blockers it had just gathered.
        lines.append(f"{label} reported an error: {raised}")
        if not blockers:
            return lines[0] + " (no blockers accompanied it, so this is all the payload says)"
    lines.append(f"{label} is not bundle-ready; status={payload.get('status')!r}.")
    if not blockers:
        lines.append(
            "  No blockers were reported, which is itself the finding: the status is not"
            " `ready` and nothing says why."
        )
    for blocker in blockers:
        lines.append(f"  - code: {blocker.get('code')}")
        lines.append(f"    message: {blocker.get('message')}")
        if blocker.get("remediation"):
            lines.append(f"    remediation: {blocker.get('remediation')}")
        subject = blocker.get("subject")
        if subject:
            # Split ONLY the blocker that comma-joins its subject. Splitting every subject
            # mangles a POSIX-legal path containing a comma into two bogus lines, and this
            # helper's whole job is to survive an awkward payload rather than garble it.
            parts = str(subject).split(",") if blocker.get("code") == "unmatched_surface_path" else [str(subject)]
            for part in parts:
                lines.append(f"    subject: {part.strip()}")
    return "\n".join(lines)


def seed_normalize_repo(repo: Path, agents_text: str) -> None:
    """Seed the minimum surface set `inspect_repo` needs to reach normalization checks."""
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text(agents_text, encoding="utf-8")
    (repo / "docs" / "roadmap.md").write_text("# Roadmap\n", encoding="utf-8")
    (repo / "docs" / "operator-acceptance.md").write_text("# Acceptance\n", encoding="utf-8")


def skill_package_text(skill_id: str) -> str:
    skill_dir = ROOT / "skills" / "public" / skill_id
    parts = [(skill_dir / "SKILL.md").read_text(encoding="utf-8")]
    references_dir = skill_dir / "references"
    if references_dir.is_dir():
        for path in sorted(references_dir.rglob("*")):
            if path.is_file() and path.suffix in {".md", ".txt"}:
                parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def run_shell_script(
    script: Path, *args: str, cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    run_env = env
    if script.name == "run-quality.sh" and cwd is not None:
        run_env = {**(env or os.environ), "CHARNESS_QUALITY_RECEIPT_JSON": str(cwd / "receipt.json")}
    return subprocess.run(
        ["/bin/bash", str(script), *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=run_env,
    )


def assert_quality_receipt(
    repo: Path,
    result: subprocess.CompletedProcess[str],
    *,
    status: str,
    passed: int,
    failed: int,
    adverse_subjects: list[str] | None = None,
    adverse_recoveries: list[dict[str, object]] | None = None,
    unproven_subjects: list[str] | None = None,
) -> None:
    """Assert the runner contract through its structured proof receipt."""
    receipt_path = repo / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["surface"] == "quality"
    assert receipt["status"] == status
    assert receipt["details"]["passed"] == passed
    assert receipt["details"]["failed"] == failed
    assert receipt["effective_exit_code"] == result.returncode
    assert [subject["subject"] for subject in receipt["adverse_subjects"]] == (
        adverse_subjects or []
    )
    if adverse_recoveries is not None:
        assert [subject["recovery"] for subject in receipt["adverse_subjects"]] == adverse_recoveries
    assert receipt["unproven_subjects"] == (unproven_subjects or [])


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def fake_gh_env(tmp_path: Path) -> dict[str, str]:
    """A PATH env with a stub `gh` that succeeds (including `gh auth`), for issue-tool
    tests that need `gh` present on PATH but not real."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    write_executable(bin_dir / "gh", '#!/usr/bin/env sh\nif [ "$1" = auth ]; then exit 0; fi\nexit 0\n')
    return {**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"}


def write_argv_logging_fake(bin_dir: Path, name: str, log_env: str, response_lines: list[str]) -> Path:
    """Write a fake `gh`/`acme` binary that appends its argv (as a list) to the JSON
    file named by the `log_env` environment variable, then runs `response_lines`
    (which decide what to print per subcommand). Shares the log-append preamble so
    each caller supplies only its own response logic."""
    fake = bin_dir / name
    write_executable(
        fake,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                f"log = Path(os.environ['{log_env}'])",
                "entries = json.loads(log.read_text()) if log.exists() else []",
                "entries.append(sys.argv[1:])",
                "log.write_text(json.dumps(entries))",
                *response_lines,
                "",
            ]
        ),
    )
    return fake


def write_issue_adapter_with_backend(tmp_path: Path, *, backend_id: str, binary: str) -> None:
    adapter_dir = tmp_path / ".agents"
    adapter_dir.mkdir(exist_ok=True)
    (adapter_dir / "issue-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "default_org: corca-ai",
                "remote_name: origin",
                "issue_backend:",
                f"  id: {backend_id}",
                f"  binary: {binary}",
                "  commands:",
                "    create:",
                "      - github",
                "      - issue",
                "      - create",
                "      - '-R'",
                "      - '{repo}'",
                "    search_newest_open:",
                "      - github",
                "      - issue",
                "      - list",
                "      - '-R'",
                "      - '{repo}'",
                "      - '--json'",
                "",
            ]
        ),
        encoding="utf-8",
    )


def init_git_repo(repo: Path, *tracked_paths: str) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    if tracked_paths:
        subprocess.run(
            ["git", "add", *tracked_paths],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )


QUALITY_PYTHON_STUBS = (
    ("validate-skills", "validate_skills.py"),
    ("validate-quality-reference-catalog", "validate_quality_reference_catalog.py"),
    ("validate-skill-ergonomics", "validate_skill_ergonomics.py"),
    ("quality-tool-fixtures", "check_quality_tool_fixtures.py"),
    ("check-cli-skill-surface", "check_cli_skill_surface.py"),
    ("check-closeout-classification-parity", "check_closeout_classification_parity.py"),
    ("validate-surfaces", "validate_surfaces.py"),
    ("validate-inference-interpretation", "validate_inference_interpretation.py"),
    ("check-command-dominance", "check_command_dominance.py"),
    ("validate-public-skill-validation", "validate_public_skill_validation.py"),
    ("validate-public-skill-dogfood", "validate_public_skill_dogfood.py"),
    ("validate-profiles", "validate_profiles.py"),
    ("validate-presets", "validate_presets.py"),
    ("validate-adapters", "validate_adapters.py"),
    ("validate-integrations", "validate_integrations.py"),
    ("validate-packaging", "validate_packaging.py"),
    ("validate-packaging-committed", "validate_packaging_committed.py"),
    ("validate-debug-artifact", "validate_debug_artifact.py"),
    ("validate-debug-seam-index", "build_debug_seam_risk_index.py"),
    ("validate-retro-lesson-index", "build_retro_lesson_selection_index.py"),
    ("validate-lesson-ledger", "check_lesson_ledger.py"),
    ("validate-quality-artifact", "validate_quality_artifact.py"),
    ("validate-attention-state-visibility", "validate_attention_state_visibility.py"),
    ("validate-inventory-consumption", "validate_inventory_consumption.py"),
    ("validate-inventory-consumption-declaration", "validate_inventory_consumption_declaration.py"),
    ("check-inventory-declaration-coverage", "check_inventory_declaration_coverage.py"),
    ("check-timing-layer-completeness", "check_timing_layer_completeness.py"),
    ("check-runtime-budget-universe", "check_runtime_budget_universe.py"),

    ("validate-quality-closeout-contract", "validate_quality_closeout_contract.py"),
    ("validate-critique-artifacts", "validate_critique_artifacts.py"),
    ("validate-ideation-artifact", "validate_ideation_artifact.py"),
    ("validate-retro-artifact", "validate_retro_artifact.py"),
    ("validate-current-pointer-freshness", "validate_current_pointer_freshness.py"),
    ("check-current-pointer-writes", "check_current_pointer_writes.py"),
    ("inventory-skill-script-references", "inventory_skill_script_references.py"),
    ("validate-maintainer-setup", "validate_maintainer_setup.py"),
    ("check-python-lengths", "check_python_lengths.py"),
    ("check-python-filenames", "check_python_filenames.py"),
    ("check-python-runtime-inheritance", "check_python_runtime_inheritance.py"),
    ("check-skill-contracts", "check_skill_contracts.py"),
    ("check-skill-bootstrap-vars", "check_skill_bootstrap_vars.py"),
    ("check-bootstrap-shim-consistency", "check_bootstrap_shim_consistency.py"),
    ("check-public-doc-coupling", "check_public_doc_coupling.py"),
    ("check-export-safe-imports", "native_gate_lib.py"),
    ("check-export-self-sufficiency", "check_export_self_sufficiency.py"),
    ("check-plugin-import-smoke", "check_plugin_import_smoke.py"),
    ("check-command-docs", "check_command_docs.py"),
    ("check-doc-links", "check_doc_links.py"),
    ("docs-graph", "check_docs_graph.py"),
    ("check-plugin-doc-links", "check_plugin_doc_links.py"),
    ("check-plugin-dir-references", "native_gate_lib.py"),
    ("check-plugin-asset-command-carriers", "check_plugin_asset_command_carriers.py"),
    ("check-documented-command-flags", "check_documented_command_flags.py"),
    ("check-documented-subcommands", "check_documented_subcommands.py"),
    ("check-spec-evidence-durability", "check_spec_evidence_durability.py"),
    ("check-artifact-referents", "check_artifact_referents.py"),
    ("check-references-link-inventory", "check_references_link_inventory.py"),
    ("check-seed-fixture-budget", "check_seed_fixture_budget.py"),
    ("check-supply-chain", "check_supply_chain.py"),
    ("check-github-actions", "check_github_actions.py"),
    ("check-supply-chain-online", "check_supply_chain_online.py"),
    ("check-coverage", "check_coverage.py"),
    ("check-test-completeness", "check_test_completeness.py"),
    ("check-test-production-ratio", "check_test_production_ratio.py"),
    ("check-boundary-bypass-ratchet", "check_boundary_bypass_ratchet.py"),
    ("check-consumer-validator-catalog", "check_consumer_validator_catalog.py"),
    ("release-changed-line-coverage", "release_changed_line_coverage.py"),
    ("run-evals", "run_evals.py"),
)
QUALITY_RUNTIME_STUBS = (
    ("dead-code-advisory", "run_dead_code_advisory.py"),
    ("measure-startup-probes", "measure_startup_probes.py"),
    ("inventory-sloc", "inventory_sloc.py"),
    ("inventory-ci-local-gate-parity", "inventory_ci_local_gate_parity.py"),
    ("inventory-gitignore-scan-hygiene", "inventory_gitignore_scan_hygiene.py"),
    ("check-runtime-budget", "check_runtime_budget.py"),
    ("doc-duplicates", "inventory_doc_duplicates.py"),
    ("inventory-nose-clones", "inventory_nose_clones.py"),
    ("dup-ratchet", "check_dup_ratchet.py"),
    ("check-regenerable-facts", "check_regenerable_facts.py"),
)
QUALITY_SHELL_STUBS = (
    ("check-docs", "check-docs.sh"),
    ("check-markdown", "check-markdown.sh"),
    ("check-secrets", "check-secrets.sh"),
    ("check-shell", "check-shell.sh"),
    ("check-rust", "check-rust.sh"),
    ("check-links-internal", "check-links-internal.sh"),
    ("check-links-external", "check-links-external.sh"),
    ("ruff", "check-python-lint.sh"),
)
QUALITY_BIN_STUBS = ("ruff", "pytest", "specdown")


def quality_python_stub(label: str) -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "import os",
            "import sys",
            f"LABEL = {label!r}",
            "if os.environ.get('QUALITY_FAIL_LABEL') == LABEL:",
            "    print(f'quality failure output from {LABEL}')",
            "    sys.exit(1)",
            "print(f'quality success output from {LABEL}')",
            "",
        ]
    )


def quality_shell_stub(label: str) -> str:
    return "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            f"LABEL={label!r}",
            'if [[ "${QUALITY_FAIL_LABEL:-}" == "$LABEL" ]]; then',
            '  echo "quality failure output from $LABEL"',
            "  exit 1",
            "fi",
            'echo "quality success output from $LABEL"',
            'if [[ "$LABEL" == "check-links-external" ]]; then',
            '  echo "link online=${CHARNESS_LINK_CHECK_ONLINE:-0}"',
            "fi",
            "",
        ]
    )


def seed_quality_python_stubs(target_dir: Path, stubs: tuple[tuple[str, str], ...]) -> None:
    for label, filename in stubs:
        write_executable(target_dir / filename, quality_python_stub(label))


def seed_quality_shell_stubs(target_dir: Path) -> None:
    for label, filename in QUALITY_SHELL_STUBS:
        write_executable(target_dir / filename, quality_shell_stub(label))


def seed_quality_bin_stubs(target_dir: Path) -> None:
    for label in QUALITY_BIN_STUBS:
        write_executable(target_dir / label, quality_shell_stub(label))
    # The specdown stub additionally records its argv, so a test can prove the runner
    # handed it a redirected `-config` rather than only that the step exited 0.
    write_executable(
        target_dir / "specdown",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ -n "${SPECDOWN_ARGV_LOG:-}" ]]; then',
                '  printf \'%s\\n\' "$*" >>"$SPECDOWN_ARGV_LOG"',
                "fi",
                'if [[ "${QUALITY_FAIL_LABEL:-}" == "specdown" ]]; then',
                '  echo "quality failure output from specdown"',
                "  exit 1",
                "fi",
                'echo "quality success output from specdown"',
                "",
            ]
        ),
    )


def seed_quality_python_binary_stub(target_dir: Path) -> None:
    real_python = sys.executable
    write_executable(
        target_dir / "python3",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "${1:-}" == "-m" && "${2:-}" == "pytest" ]]; then',
                "  shift 2",
                '  if [[ "${1:-}" == "--version" ]]; then',
                '    echo "pytest 9.0.2"',
                "    exit 0",
                "  fi",
                '  if [[ "${1:-}" == "--help" ]]; then',
                '    echo "  -n numprocesses, --numprocesses=numprocesses"',
                "    exit 0",
                "  fi",
                '  if [[ "${QUALITY_FAIL_LABEL:-}" == "pytest" ]]; then',
                '    echo "quality failure output from pytest"',
                "    exit 1",
                "  fi",
                '  echo "quality success output from pytest"',
                "  exit 0",
                "fi",
                'if [[ "${1:-}" == "scripts/record_quality_runtime.py" ]]; then',
                "  exit 0",
                "fi",
                f"exec {real_python!r} \"$@\"",
                "",
            ]
        ),
    )


def seed_quality_runtime_recorder(target_dir: Path) -> None:
    write_executable(
        target_dir / "record_quality_runtime.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "import json",
                "import sys",
                "",
                "args = sys.argv[1:]",
                "repo_root = Path(args[args.index('--repo-root') + 1])",
                "# The runner batches per-gate samples into one --batch call and records",
                "# only the aggregate label through the single-record flags.",
                "if '--batch' in args:",
                "    records = [",
                "        json.loads(line)",
                "        for line in Path(args[args.index('--batch') + 1]).read_text(encoding='utf-8').splitlines()",
                "        if line.strip()",
                "    ]",
                "else:",
                "    records = [{",
                "        'label': args[args.index('--label') + 1],",
                "        'elapsed_ms': int(args[args.index('--elapsed-ms') + 1]),",
                "        'status': args[args.index('--status') + 1],",
                "        'timestamp': args[args.index('--timestamp') + 1],",
                "    }]",
                "out_dir = repo_root / '.charness' / 'quality'",
                "out_dir.mkdir(parents=True, exist_ok=True)",
                "commands = {",
                "    r['label']: {'latest': {'elapsed_ms': int(r['elapsed_ms']), 'status': r['status'], 'timestamp': r['timestamp']}}",
                "    for r in records",
                "}",
                "(out_dir / 'runtime-signals.json').write_text(",
                "    json.dumps({'commands': commands}, indent=2) + '\\n',",
                "    encoding='utf-8',",
                ")",
                "",
            ]
        ),
    )


def seed_agent_browser_runtime_guard_stub(target_dir: Path) -> None:
    write_executable(
        target_dir / "agent_browser_runtime_guard.py",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import os",
                "import sys",
                "",
                "args = sys.argv[1:]",
                "label = 'agent-browser-runtime-hygiene' if '--assert-no-orphans' in args else 'agent-browser-runtime-baseline'",
                "if os.environ.get('QUALITY_REQUIRE_STRICT_ORPHANS_LABEL') == label and os.environ.get('CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS') == '1':",
                "    print(f'quality failure output from non-strict {label}')",
                "    sys.exit(1)",
                "if os.environ.get('QUALITY_FAIL_LABEL') == label:",
                "    print(f'quality failure output from {label}')",
                "    sys.exit(1)",
                "print(f'quality success output from {label}')",
                "",
            ]
        ),
    )


def make_quality_runner_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    hooks_dir = repo / ".githooks"
    bin_dir = repo / "bin"
    quality_scripts_dir = repo / "skills" / "public" / "quality" / "scripts"
    scripts_dir.mkdir(parents=True)
    hooks_dir.mkdir()
    bin_dir.mkdir()
    quality_scripts_dir.mkdir(parents=True)

    shutil.copy2(ROOT / "scripts" / "run-quality.sh", scripts_dir / "run-quality.sh")
    (scripts_dir / "run-quality.sh").chmod(0o755)
    # The runner SOURCES this, so a seeded repo without it fails at line 8 with a
    # missing-file error rather than on runner behavior -- the same "copied rather
    # than stubbed" rule as the Python modules below, for the same reason: a stub
    # would disable the export-copy refusal in every runner test.
    shutil.copy2(ROOT / "scripts" / "exported-copy-guard.sh", scripts_dir / "exported-copy-guard.sh")
    # The runner shares the shell runtime/cache primitive with installed hooks.
    # Seed the real file so these tests exercise runner behavior instead of an
    # incomplete synthetic checkout.
    shutil.copy2(ROOT / ".githooks" / "runtime-env.sh", hooks_dir / "runtime-env.sh")
    shutil.copy2(ROOT / "scripts" / "proof_receipt.py", scripts_dir / "proof_receipt.py")
    (scripts_dir / "proof_receipt.py").chmod(0o755)
    shutil.copy2(
        ROOT / "scripts" / "run_standing_pytest.py",
        scripts_dir / "run_standing_pytest.py",
    )
    (scripts_dir / "run_standing_pytest.py").chmod(0o755)
    # Copied rather than stubbed: the runner reads it at startup to build the label
    # universe it asserts every queued label against (#546). A stub returning nothing
    # would disable that assertion in every runner test -- the harness would then
    # prove the runner works while proving nothing about the guard that keeps a
    # mis-parsed gate list from reaching a budget verdict. The real reader also makes
    # the harness's own copy of run-quality.sh the thing under test.
    # yaml_output.py is copied for the same reason: the real label reader emits its
    # payload through `from yaml_output import emit_yaml`, so a seeded repo without it
    # makes every runner test fail on an import error instead of on runner behavior.
    # `subprocess_guard.py` joins them for the same reason and a sharper one (S6):
    # the standing runner now spawns its pytest child through the repo's one
    # child-process owner, so a seeded repo without it fails at import. Copied
    # rather than stubbed BECAUSE a stub is exactly the wrong repair here -- the
    # runner would fall back to an unmonitored child and the harness would keep
    # passing over the untracked process tree this slice exists to fix.
    for real_name in (
        "quality_label_universe.py",
        "runtime_bootstrap.py",
        "adapter_lib.py",
        # `adapter_lib` re-exports this repo's YAML dialect from it since the resolver
        # half crossed the length cap; the module is imported at `adapter_lib` scope, so a
        # seeded repo without it fails at IMPORT rather than on behavior. Same rule as the
        # entries around it, and the split is exactly the event that would have missed it.
        "adapter_yaml_parse.py",
        "yaml_output.py",
        "subprocess_guard.py",
        # The basetemp lifecycle the runner re-exports; extracted in S6 when the
        # runner crossed its length cap. Same rule as the entries above: the
        # runner imports it at module scope, so a seeded repo without it fails at
        # import rather than on behavior.
        "standing_pytest_basetemp.py",
        "standing_pytest_run_record.py",
    ):
        shutil.copy2(ROOT / "scripts" / real_name, scripts_dir / real_name)
        (scripts_dir / real_name).chmod(0o755)
    # Copied rather than stubbed: the runner's specdown step calls it for real, and a
    # stub would let the runner keep passing if the redirect it produces ever broke.
    shutil.copy2(
        ROOT / "scripts" / "specdown_ephemeral_config.py",
        scripts_dir / "specdown_ephemeral_config.py",
    )
    (scripts_dir / "specdown_ephemeral_config.py").chmod(0o755)
    (repo / "specdown.json").write_text(
        json.dumps(
            {
                "entry": "specs/index.spec.md",
                "reporters": [{"builtin": "json", "outFile": ".charness/specdown/report.json"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    seed_quality_python_stubs(scripts_dir, QUALITY_PYTHON_STUBS)
    seed_quality_python_stubs(quality_scripts_dir, QUALITY_RUNTIME_STUBS)
    seed_quality_runtime_recorder(scripts_dir)
    seed_agent_browser_runtime_guard_stub(scripts_dir)
    seed_quality_shell_stubs(scripts_dir)
    seed_quality_bin_stubs(bin_dir)
    seed_quality_python_binary_stub(bin_dir)
    # A git repo, not a bare directory. `run-quality.sh` now refuses when its own root
    # is not the git toplevel, and a bare tmp dir inherits whatever repository happens
    # to enclose the pytest temp root -- a dotfiles-tracked $HOME is the common case, and
    # it would red every runner test with a message about the export copy.
    init_git_repo(repo)
    return repo, {"PATH": f"{bin_dir}:/usr/bin:/bin"}


@pytest.fixture(scope="module")
def seeded_quality_runner_repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    seed_root = tmp_path_factory.mktemp("quality-runner-seed")
    return make_quality_runner_repo(seed_root)[0]


def clone_quality_runner_repo(tmp_path: Path, seeded_repo: Path) -> tuple[Path, dict[str, str]]:
    repo = tmp_path / "repo"
    shutil.copytree(seeded_repo, repo)
    env = {"PATH": f"{repo / 'bin'}:/usr/bin:/bin"}
    return repo, env


def make_minimal_skill_repo(tmp_path: Path, description: str) -> Path:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                f"description: {description}",
                "---",
                "",
                "# Demo",
            ]
        ),
        encoding="utf-8",
    )
    return repo


def seed_runtime_budget_repo(
    tmp_path: Path,
    *,
    budgets: dict[str, int] | None,
    signals: dict | None,
    budget_profiles: dict[str, dict[str, dict[str, int]]] | None = None,
    smoothing: dict | None = None,
    explicit_empty_budgets: bool = False,
    startup_probes: list[dict[str, object]] | None = None,
) -> Path:
    """Seed a repo whose quality adapter + runtime-signals drive the runtime budget
    gate and the runtime summary renderer.

    The gate uses every knob; the renderer uses only the `budgets`/`signals` subset.
    Keeping one seeder means a change to the signals shape cannot leave the
    renderer's fixtures silently stale.
    """
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".charness" / "quality").mkdir(parents=True)
    adapter_lines = ["version: 1", "repo: testrepo", "output_dir: charness-artifacts/quality"]
    if budgets is not None:
        adapter_lines.append("runtime_budgets:")
        for label, ms in budgets.items():
            adapter_lines.append(f"  {label}: {ms}")
    elif explicit_empty_budgets:
        adapter_lines.append("runtime_budgets:")
    if budget_profiles is not None:
        adapter_lines.append("runtime_budget_profiles:")
        for profile_id, profile in budget_profiles.items():
            adapter_lines.append(f"  {profile_id}:")
            adapter_lines.append("    budgets:")
            for label, ms in profile["budgets"].items():
                adapter_lines.append(f"      {label}: {ms}")
    if startup_probes is not None:
        if not startup_probes:
            adapter_lines.append("startup_probes: []")
        else:
            adapter_lines.append("startup_probes:")
            for probe in startup_probes:
                adapter_lines.extend(
                    [
                        f"  - label: {probe['label']}",
                        "    command:",
                        *[f"      - {item}" for item in probe["command"]],
                        f"    class: {probe['class']}",
                        f"    startup_mode: {probe['startup_mode']}",
                        f"    surface: {probe['surface']}",
                        f"    samples: {probe['samples']}",
                    ]
                )
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(adapter_lines) + "\n", encoding="utf-8")
    if signals is not None:
        (repo / ".charness" / "quality" / "runtime-signals.json").write_text(
            json.dumps(signals), encoding="utf-8"
        )
    if smoothing is not None:
        (repo / ".charness" / "quality" / "runtime-smoothing.json").write_text(
            json.dumps(smoothing), encoding="utf-8"
        )
    return repo


MIRROR_RELATIVE = Path("plugins") / "charness"
GUARD_SCRIPT = "exported-copy-guard.sh"


def install_repo_root_script(repo: Path, script_name: str) -> tuple[Path, Path]:
    """Place `script_name` at the repo root AND in the generated mirror, byte-identical.

    `scripts/check_staged_mirror_drift.py` and `.githooks/pre-push` enforce that byte identity,
    so the mirrored copy is never a different program: whatever the source copy does, right or
    wrong, the mirror does too. Both copies are therefore under test here.
    """

    source = repo / "scripts" / script_name
    mirror = repo / MIRROR_RELATIVE / "scripts" / script_name
    source.parent.mkdir(parents=True, exist_ok=True)
    mirror.parent.mkdir(parents=True, exist_ok=True)
    if script_name in {"check-python-lint.sh", "run-quality.sh"}:
        (repo / ".githooks").mkdir(exist_ok=True)
        shutil.copy2(ROOT / ".githooks" / "runtime-env.sh", repo / ".githooks" / "runtime-env.sh")
    # The guard travels with every gate that sources it, in BOTH copies. Shipping it to
    # only one side would make these tests measure "the guard file is missing" instead of
    # "the guard refused", which is a different green.
    #
    # Repo-owned Python HELPERS a gate shells out to are deliberately NOT installed
    # here. Their dependency closure reaches back into `scripts/` as a package
    # (`scripts.repo_file_listing` and onward), so installing them means reproducing
    # the repo, which is the thing this fixture exists to avoid. A test whose subject
    # is the gate's COMPOSITION stubs those helpers exactly as it stubs the external
    # tool; a test whose subject is a helper's own output belongs in that helper's
    # test file.
    #
    # Blind class: a gate run from this fixture without such a stub reaches a MISSING
    # helper, and gates that treat a helper's non-zero exit as an advisory will report
    # that absence as an advisory rather than as a failure. Callers asserting on
    # advisory text must install a stub.
    for name in (script_name, GUARD_SCRIPT):
        shutil.copy2(ROOT / "scripts" / name, source.parent / name)
        shutil.copy2(ROOT / "scripts" / name, mirror.parent / name)
    return source, mirror


def charness_shaped_repo(tmp_path: Path, script_name: str) -> tuple[Path, Path, Path]:
    """A git repo shaped like this one: root-level docs, plus a `plugins/charness` mirror.

    This is the canonical alternative to cloning the real checkout. A gate that measures a
    repo-root population needs a repo SHAPE, not this repository's contents, and the two are
    not interchangeable: a fixture that IS the checkout has no fixed input, so its verdict
    moves with unrelated repo content. `test_python_and_security_gates.py` already lost an
    assertion that way -- a wrapped inline code span in `docs/index.md` broke a test about
    markdownlint's exit code, and the repair was to delete the assertion, because the
    assertion had only ever encoded "every checked-in Markdown file happens to be clean".
    """

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "nested.md").write_text("# Nested\n", encoding="utf-8")
    (repo / MIRROR_RELATIVE / "docs").mkdir(parents=True)
    (repo / MIRROR_RELATIVE / "docs" / "mirrored.md").write_text("# Mirrored\n", encoding="utf-8")
    source, mirror = install_repo_root_script(repo, script_name)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    return repo, source, mirror
