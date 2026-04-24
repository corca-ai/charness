from __future__ import annotations

import json
import shutil
from pathlib import Path

from .support import ROOT, init_git_repo, run_script, run_shell_script


def test_check_secrets_prefers_gitleaks_when_available(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "check-secrets.sh", scripts_dir / "check-secrets.sh")
    shutil.copy2(ROOT / ".gitleaks.toml", repo / ".gitleaks.toml")

    bin_dir = repo / "bin"
    bin_dir.mkdir()
    output_path = repo / "gitleaks-args.txt"
    gitleaks = bin_dir / "gitleaks"
    gitleaks.write_text("#!/bin/bash\nprintf '%s\\n' \"$@\" > \"$TEST_OUTPUT\"\n", encoding="utf-8")
    gitleaks.chmod(0o755)

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin", TEST_OUTPUT=str(output_path))
    result = run_shell_script(repo / "scripts" / "check-secrets.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    args = output_path.read_text(encoding="utf-8").splitlines()
    assert args[0] == "dir"
    assert "--config" in args
    assert str(repo / ".gitleaks.toml") in args
    assert "--redact" in args


def test_check_secrets_falls_back_to_secretlint_via_npm(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "check-secrets.sh", scripts_dir / "check-secrets.sh")
    shutil.copy2(ROOT / ".secretlintrc.json", repo / ".secretlintrc.json")
    shutil.copy2(ROOT / ".secretlintignore", repo / ".secretlintignore")
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / ".gitignore").write_text("integrations/locks/*.json\n", encoding="utf-8")
    (repo / "integrations" / "locks").mkdir(parents=True)
    (repo / "integrations" / "locks" / "agent-browser.json").write_text(
        '{"token":"ignored-runtime-state"}\n',
        encoding="utf-8",
    )
    init_git_repo(
        repo,
        "README.md",
        ".gitignore",
        ".secretlintrc.json",
        ".secretlintignore",
        "scripts/check-secrets.sh",
    )

    bin_dir = repo / "bin"
    bin_dir.mkdir()
    output_path = repo / "npm-args.txt"
    npm = bin_dir / "npm"
    npm.write_text("#!/bin/bash\nprintf '%s\\n' \"$@\" > \"$TEST_OUTPUT\"\n", encoding="utf-8")
    npm.chmod(0o755)

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin", TEST_OUTPUT=str(output_path))
    result = run_shell_script(repo / "scripts" / "check-secrets.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    args = output_path.read_text(encoding="utf-8").splitlines()
    assert args[:6] == ["exec", "--no-install", "--", "secretlint", "--secretlintignore", ".secretlintignore"]
    assert "README.md" in args
    assert "scripts/check-secrets.sh" in args
    assert "integrations/locks/agent-browser.json" not in args
    assert "**/*" not in args


def test_check_secrets_requires_gitleaks_or_secretlint_runtime(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "check-secrets.sh", scripts_dir / "check-secrets.sh")

    env = dict(PATH="")
    result = run_shell_script(repo / "scripts" / "check-secrets.sh", cwd=repo, env=env)
    assert result.returncode == 1
    assert "requires either gitleaks or repo-local secretlint via npm" in result.stderr
def test_check_supply_chain_requires_javascript_lockfile(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text(
        json.dumps({"private": True, "devDependencies": {"markdownlint-cli2": "0.22.0"}}, indent=2) + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_supply_chain.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "no lockfile is checked in" in result.stderr


def test_check_supply_chain_requires_declared_pnpm_lockfile(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text(
        json.dumps(
            {"private": True, "packageManager": "pnpm@9.0.0", "dependencies": {"left-pad": "1.3.0"}},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "package-lock.json").write_text("{}", encoding="utf-8")
    result = run_script("scripts/check_supply_chain.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "packageManager declares `pnpm`" in result.stderr


def test_check_supply_chain_requires_uv_lock_when_dependencies_exist(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text(
        "\n".join(["[project]", 'name = "demo"', 'version = "0.1.0"', 'dependencies = ["requests>=2.0"]', ""]),
        encoding="utf-8",
    )
    result = run_script("scripts/check_supply_chain.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "uv.lock is missing" in result.stderr


def test_check_supply_chain_accepts_uv_lock_for_python_dependencies(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text(
        "\n".join(["[project]", 'name = "demo"', 'version = "0.1.0"', 'dependencies = ["requests>=2.0"]', ""]),
        encoding="utf-8",
    )
    (repo / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    result = run_script("scripts/check_supply_chain.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "uv:uv.lock" in result.stdout


def test_check_github_actions_passes_without_workflows() -> None:
    result = run_script("scripts/check_github_actions.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert "No GitHub Actions workflows detected." in result.stdout


def test_check_github_actions_flags_outdated_node24_baselines(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflow_dir = repo / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "ci.yml").write_text(
        "\n".join(
            [
                "name: ci",
                "on: [push]",
                "jobs:",
                "  build:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - uses: actions/checkout@v5",
                "      - uses: actions/setup-node@v4",
                "      - uses: actions/cache/save@v5",
                "      - uses: ./.github/actions/local-check",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/check_github_actions.py", "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert [finding["category"] for finding in payload["findings"]] == [
        "node24_incompatible",
        "baseline_lag",
        "node24_incompatible",
    ]
    assert payload["findings"][0]["normalized_action"] == "actions/checkout"
    assert payload["findings"][0]["recommended_reference"] == "v6"
    assert payload["findings"][1]["normalized_action"] == "actions/checkout"
    assert payload["findings"][2]["normalized_action"] == "actions/setup-node"


def test_check_python_lengths_rejects_too_long_function(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    long_body = "\n".join(f"    value_{i} = {i}" for i in range(101))
    (scripts_dir / "long.py").write_text("\n".join(["def too_long():", long_body, "    return 0", ""]), encoding="utf-8")
    result = run_script("scripts/check_python_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "function `too_long` length" in result.stderr


def test_check_python_lengths_rejects_too_long_skill_helper_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "helper.py").write_text("\n".join(f"print({i})" for i in range(221)) + "\n", encoding="utf-8")
    result = run_script("scripts/check_python_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "file length 221 exceeds limit 220" in result.stderr


def test_check_python_lengths_ignores_gitignored_python_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    tests_dir = repo / "tests"
    scripts_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("scripts/generated_*.py\ntests/generated_*.py\n", encoding="utf-8")
    (scripts_dir / "kept.py").write_text("def short():\n    return 1\n", encoding="utf-8")
    (scripts_dir / "generated_long.py").write_text("\n".join(f"print({i})" for i in range(381)) + "\n", encoding="utf-8")
    (tests_dir / "kept_test.py").write_text("def test_short():\n    assert True\n", encoding="utf-8")
    (tests_dir / "generated_long.py").write_text(
        "\n".join(["def test_generated():", *[f"    value_{i} = {i}" for i in range(151)], "    assert True", ""]),
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/kept.py", "tests/kept_test.py")

    result = run_script("scripts/check_python_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_check_python_lengths_rejects_too_long_test_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tests_dir = repo / "tests"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_big.py").write_text("\n".join(f"VALUE_{i} = {i}" for i in range(651)) + "\n", encoding="utf-8")
    result = run_script("scripts/check_python_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "file length 651 exceeds limit 650" in result.stderr


def test_check_python_lengths_rejects_too_long_test_function(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    tests_dir = repo / "tests"
    tests_dir.mkdir(parents=True)
    long_body = "\n".join(f"    value_{i} = {i}" for i in range(150))
    (tests_dir / "test_long.py").write_text(
        "\n".join(["def test_too_long():", long_body, "    assert True", ""]),
        encoding="utf-8",
    )
    result = run_script("scripts/check_python_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "function `test_too_long` length 152 exceeds limit 150" in result.stderr
