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
    script: Path, *, cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/bin/bash", str(script)],
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


def make_quality_runner_repo(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    bin_dir = repo / "bin"
    scripts_dir.mkdir(parents=True)
    bin_dir.mkdir()

    shutil.copy2(ROOT / "scripts" / "run-quality.sh", scripts_dir / "run-quality.sh")
    (scripts_dir / "run-quality.sh").chmod(0o755)

    python_stubs = (
        ("validate-skills", "validate-skills.py"),
        ("validate-public-skill-validation", "validate-public-skill-validation.py"),
        ("validate-profiles", "validate-profiles.py"),
        ("validate-presets", "validate-presets.py"),
        ("validate-adapters", "validate-adapters.py"),
        ("validate-integrations", "validate-integrations.py"),
        ("validate-packaging", "validate-packaging.py"),
        ("validate-handoff-artifact", "validate-handoff-artifact.py"),
        ("validate-debug-artifact", "validate-debug-artifact.py"),
        ("validate-quality-artifact", "validate-quality-artifact.py"),
        ("validate-maintainer-setup", "validate-maintainer-setup.py"),
        ("check-python-lengths", "check-python-lengths.py"),
        ("check-skill-contracts", "check-skill-contracts.py"),
        ("check-doc-links", "check-doc-links.py"),
        ("check-supply-chain", "check-supply-chain.py"),
        ("run-evals", "run-evals.py"),
        ("check-duplicates", "check-duplicates.py"),
    )
    for label, filename in python_stubs:
        write_executable(
            scripts_dir / filename,
            "\n".join(
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
            ),
        )

    write_executable(
        scripts_dir / "record_quality_runtime.py",
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
                "out_dir = repo_root / 'skill-outputs' / 'quality'",
                "out_dir.mkdir(parents=True, exist_ok=True)",
                "(out_dir / 'runtime-signals.json').write_text(",
                "    json.dumps({'commands': {label: {'latest': {'elapsed_ms': elapsed_ms, 'status': status, 'timestamp': timestamp}}}}, indent=2) + '\\n',",
                "    encoding='utf-8',",
                ")",
                "",
            ]
        ),
    )

    shell_stubs = (
        ("check-markdown", "check-markdown.sh"),
        ("check-secrets", "check-secrets.sh"),
        ("check-shell", "check-shell.sh"),
        ("check-links-external", "check-links-external.sh"),
    )
    for label, filename in shell_stubs:
        write_executable(
            scripts_dir / filename,
            "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "set -euo pipefail",
                    f"LABEL={label!r}",
                    'if [[ "${QUALITY_FAIL_LABEL:-}" == "$LABEL" ]]; then',
                    '  echo "quality failure output from $LABEL"',
                    "  exit 1",
                    "fi",
                    'echo "quality success output from $LABEL"',
                    "",
                ]
            ),
        )

    for label in ("ruff", "pytest"):
        write_executable(
            bin_dir / label,
            "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "set -euo pipefail",
                    f"LABEL={label!r}",
                    'if [[ "${QUALITY_FAIL_LABEL:-}" == "$LABEL" ]]; then',
                    '  echo "quality failure output from $LABEL"',
                    "  exit 1",
                    "fi",
                    'echo "quality success output from $LABEL"',
                    "",
                ]
            ),
        )

    env = {"PATH": f"{bin_dir}:/usr/bin:/bin"}
    return repo, env


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
