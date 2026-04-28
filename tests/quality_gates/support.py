from __future__ import annotations

import importlib
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
EVAL_REGISTRY = importlib.import_module("scripts.eval_registry")

ADAPTER_LIB_PATH = ROOT / "scripts" / "adapter_lib.py"
ADAPTER_LIB_SPEC = importlib.util.spec_from_file_location("adapter_lib", ADAPTER_LIB_PATH)
assert ADAPTER_LIB_SPEC is not None and ADAPTER_LIB_SPEC.loader is not None
ADAPTER_LIB = importlib.util.module_from_spec(ADAPTER_LIB_SPEC)
ADAPTER_LIB_SPEC.loader.exec_module(ADAPTER_LIB)


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def run_shell_script(
    script: Path, *args: str, cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/bin/bash", str(script), *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


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
    ("validate-skill-ergonomics", "validate_skill_ergonomics.py"),
    ("check-cli-skill-surface", "check_cli_skill_surface.py"),
    ("validate-surfaces", "validate_surfaces.py"),
    ("validate-public-skill-validation", "validate_public_skill_validation.py"),
    ("validate-public-skill-dogfood", "validate_public_skill_dogfood.py"),
    ("validate-cautilus-scenarios", "validate_cautilus_scenarios.py"),
    ("validate-cautilus-proof", "validate_cautilus_proof.py"),
    ("validate-profiles", "validate_profiles.py"),
    ("validate-presets", "validate_presets.py"),
    ("validate-adapters", "validate_adapters.py"),
    ("validate-integrations", "validate_integrations.py"),
    ("validate-packaging", "validate_packaging.py"),
    ("validate-packaging-committed", "validate_packaging_committed.py"),
    ("validate-handoff-artifact", "validate_handoff_artifact.py"),
    ("validate-debug-artifact", "validate_debug_artifact.py"),
    ("validate-debug-seam-index", "build_debug_seam_risk_index.py"),
    ("validate-retro-lesson-index", "build_retro_lesson_selection_index.py"),
    ("validate-quality-artifact", "validate_quality_artifact.py"),
    ("validate-quality-closeout-contract", "validate_quality_closeout_contract.py"),
    ("validate-current-pointer-freshness", "validate_current_pointer_freshness.py"),
    ("inventory-quality-handoff", "inventory_quality_handoff.py"),
    ("validate-maintainer-setup", "validate_maintainer_setup.py"),
    ("check-python-lengths", "check_python_lengths.py"),
    ("check-python-filenames", "check_python_filenames.py"),
    ("check-python-runtime-inheritance", "check_python_runtime_inheritance.py"),
    ("check-skill-contracts", "check_skill_contracts.py"),
    ("check-export-safe-imports", "check_export_safe_imports.py"),
    ("check-plugin-import-smoke", "check_plugin_import_smoke.py"),
    ("check-command-docs", "check_command_docs.py"),
    ("check-doc-links", "check_doc_links.py"),
    ("check-supply-chain", "check_supply_chain.py"),
    ("check-github-actions", "check_github_actions.py"),
    ("check-supply-chain-online", "check_supply_chain_online.py"),
    ("check-coverage", "check_coverage.py"),
    ("check-test-completeness", "check_test_completeness.py"),
    ("check-test-production-ratio", "check_test_production_ratio.py"),
    ("run-evals", "run_evals.py"),
    ("check-duplicates", "check_duplicates.py"),
)
QUALITY_RUNTIME_STUBS = (
    ("measure-startup-probes", "measure_startup_probes.py"),
    ("check-runtime-budget", "check_runtime_budget.py"),
)
QUALITY_SHELL_STUBS = (
    ("check-markdown", "check-markdown.sh"),
    ("check-secrets", "check-secrets.sh"),
    ("check-shell", "check-shell.sh"),
    ("check-links-internal", "check-links-internal.sh"),
    ("check-links-external", "check-links-external.sh"),
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
                "label = args[args.index('--label') + 1]",
                "elapsed_ms = int(args[args.index('--elapsed-ms') + 1])",
                "status = args[args.index('--status') + 1]",
                "timestamp = args[args.index('--timestamp') + 1]",
                "out_dir = repo_root / '.charness' / 'quality'",
                "out_dir.mkdir(parents=True, exist_ok=True)",
                "(out_dir / 'runtime-signals.json').write_text(",
                "    json.dumps({'commands': {label: {'latest': {'elapsed_ms': elapsed_ms, 'status': status, 'timestamp': timestamp}}}}, indent=2) + '\\n',",
                "    encoding='utf-8',",
                ")",
                "",
            ]
        ),
    )


def make_quality_runner_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    bin_dir = repo / "bin"
    quality_scripts_dir = repo / "skills" / "public" / "quality" / "scripts"
    scripts_dir.mkdir(parents=True)
    bin_dir.mkdir()
    quality_scripts_dir.mkdir(parents=True)

    shutil.copy2(ROOT / "scripts" / "run-quality.sh", scripts_dir / "run-quality.sh")
    (scripts_dir / "run-quality.sh").chmod(0o755)
    seed_quality_python_stubs(scripts_dir, QUALITY_PYTHON_STUBS)
    seed_quality_python_stubs(quality_scripts_dir, QUALITY_RUNTIME_STUBS)
    seed_quality_runtime_recorder(scripts_dir)
    seed_quality_shell_stubs(scripts_dir)
    seed_quality_bin_stubs(bin_dir)
    seed_quality_python_binary_stub(bin_dir)
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
