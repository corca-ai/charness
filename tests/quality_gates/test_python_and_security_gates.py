from __future__ import annotations

import json
import shutil
from pathlib import Path

from .support import ROOT, init_git_repo, run_script, run_shell_script, write_executable


def _copy_script(repo: Path, script_name: str) -> Path:
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_path = scripts_dir / script_name
    shutil.copy2(ROOT / "scripts" / script_name, script_path)
    return script_path


def _write_failing_ls_files_git(bin_dir: Path) -> None:
    write_executable(
        bin_dir / "git",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "$1" == "rev-parse" && "${2:-}" == "--is-inside-work-tree" ]]; then',
                "  echo true",
                "  exit 0",
                "fi",
                'if [[ "$1" == "ls-files" ]]; then',
                '  echo "forced git listing failure" >&2',
                "  exit 42",
                "fi",
                'echo "unexpected git invocation: $*" >&2',
                "exit 99",
                "",
            ]
        ),
    )


def test_check_markdown_fails_when_git_listing_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_path = _copy_script(repo, "check-markdown.sh")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    _write_failing_ls_files_git(bin_dir)
    write_executable(bin_dir / "markdownlint-cli2", "#!/usr/bin/env bash\nexit 0\n")

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin")
    result = run_shell_script(script_path, cwd=repo, env=env)

    assert result.returncode == 1
    assert "check-markdown: git file listing failed (tracked-markdown)" in result.stderr
    assert "command: git ls-files" in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "forced git listing failure" in result.stderr
    assert "No tracked markdown files to lint." not in result.stdout


def test_check_links_internal_fails_when_git_listing_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_path = _copy_script(repo, "check-links-internal.sh")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    _write_failing_ls_files_git(bin_dir)
    write_executable(bin_dir / "lychee", "#!/usr/bin/env bash\nexit 0\n")

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin")
    result = run_shell_script(script_path, cwd=repo, env=env)

    assert result.returncode == 1
    assert "check-links-internal: git file listing failed (tracked-markdown)" in result.stderr
    assert "command: git ls-files" in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "forced git listing failure" in result.stderr
    assert "No markdown files to check." not in result.stdout


def test_check_shell_fails_when_file_discovery_is_partial(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_path = _copy_script(repo, "check-shell.sh")
    (repo / "root.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    shellcheck_called = repo / "shellcheck-called"
    write_executable(
        bin_dir / "find",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "$1" == "." ]]; then',
                '  echo "./root.sh"',
                "  exit 0",
                "fi",
                'if [[ "$1" == "scripts" ]]; then',
                '  echo "forced find failure" >&2',
                "  exit 42",
                "fi",
                'exec /usr/bin/find "$@"',
                "",
            ]
        ),
    )
    write_executable(
        bin_dir / "shellcheck",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                f"touch {str(shellcheck_called)!r}",
                "exit 99",
                "",
            ]
        ),
    )

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin")
    result = run_shell_script(script_path, cwd=repo, env=env)

    assert result.returncode == 1
    assert "check-shell: shell file discovery failed." in result.stderr
    assert "command: { find . -maxdepth 1 -type f -name '*.sh'" in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "./root.sh" in result.stderr
    assert "forced find failure" in result.stderr
    assert not shellcheck_called.exists()


def test_check_shell_fails_when_root_file_discovery_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_path = _copy_script(repo, "check-shell.sh")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    shellcheck_called = repo / "shellcheck-called"
    write_executable(
        bin_dir / "find",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "$1" == "." ]]; then',
                '  echo "forced root find failure" >&2',
                "  exit 42",
                "fi",
                'exec /usr/bin/find "$@"',
                "",
            ]
        ),
    )
    write_executable(
        bin_dir / "shellcheck",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                f"touch {str(shellcheck_called)!r}",
                "exit 99",
                "",
            ]
        ),
    )

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin")
    result = run_shell_script(script_path, cwd=repo, env=env)

    assert result.returncode == 1
    assert "check-shell: shell file discovery failed." in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "forced root find failure" in result.stderr
    assert not shellcheck_called.exists()


def test_check_shell_skips_shellcheck_when_successful_discovery_is_empty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_path = _copy_script(repo, "check-shell.sh")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    shellcheck_called = repo / "shellcheck-called"
    write_executable(bin_dir / "find", "#!/usr/bin/env bash\nexit 0\n")
    write_executable(
        bin_dir / "shellcheck",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                f"touch {str(shellcheck_called)!r}",
                "exit 99",
                "",
            ]
        ),
    )

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin")
    result = run_shell_script(script_path, cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert not shellcheck_called.exists()


def test_check_shell_treats_missing_githooks_as_optional(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_path = _copy_script(repo, "check-shell.sh")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    output_path = repo / "shellcheck-args.txt"
    write_executable(
        bin_dir / "shellcheck",
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" > \"$TEST_OUTPUT\"\n",
    )

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin", TEST_OUTPUT=str(output_path))
    result = run_shell_script(script_path, cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    args = output_path.read_text(encoding="utf-8").splitlines()
    assert args == ["-x", "scripts/check-shell.sh"]


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
    _copy_script(repo, "check-secrets.sh")

    env = dict(PATH="")
    result = run_shell_script(repo / "scripts" / "check-secrets.sh", cwd=repo, env=env)
    assert result.returncode == 1
    assert "requires either gitleaks or repo-local secretlint via npm" in result.stderr


def test_check_secrets_secretlint_fails_when_git_listing_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_path = _copy_script(repo, "check-secrets.sh")
    shutil.copy2(ROOT / ".secretlintrc.json", repo / ".secretlintrc.json")
    shutil.copy2(ROOT / ".secretlintignore", repo / ".secretlintignore")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    npm_called = repo / "npm-called"
    _write_failing_ls_files_git(bin_dir)
    write_executable(
        bin_dir / "npm",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                f"touch {str(npm_called)!r}",
                "exit 99",
                "",
            ]
        ),
    )

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin")
    result = run_shell_script(script_path, cwd=repo, env=env)

    assert result.returncode == 1
    assert "check-secrets: git file listing failed (secretlint-files)" in result.stderr
    assert "command: git ls-files -z --cached --others --exclude-standard" in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "forced git listing failure" in result.stderr
    assert "No tracked or unignored files to scan." not in result.stdout
    assert not npm_called.exists()


def test_check_secrets_gitleaks_fails_when_git_listing_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_path = _copy_script(repo, "check-secrets.sh")
    shutil.copy2(ROOT / ".gitleaks.toml", repo / ".gitleaks.toml")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    gitleaks_called = repo / "gitleaks-called"
    _write_failing_ls_files_git(bin_dir)
    write_executable(
        bin_dir / "gitleaks",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                f"touch {str(gitleaks_called)!r}",
                "exit 99",
                "",
            ]
        ),
    )

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin")
    result = run_shell_script(script_path, cwd=repo, env=env)

    assert result.returncode == 1
    assert "check-secrets: git file listing failed (secret-scan-files)" in result.stderr
    assert "command: git ls-files -z --cached --others --exclude-standard" in result.stderr
    assert "exit_code: 42" in result.stderr
    assert "forced git listing failure" in result.stderr
    assert not gitleaks_called.exists()


def test_check_secrets_gitleaks_fails_when_staging_git_listed_file_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _copy_script(repo, "check-secrets.sh")
    shutil.copy2(ROOT / ".gitleaks.toml", repo / ".gitleaks.toml")
    (repo / "secret.txt").write_text("token=missing-from-staged-scan\n", encoding="utf-8")
    init_git_repo(repo, "secret.txt", ".gitleaks.toml", "scripts/check-secrets.sh")
    (repo / "secret.txt").unlink()

    bin_dir = repo / "bin"
    bin_dir.mkdir()
    gitleaks_called = repo / "gitleaks-called"
    write_executable(
        bin_dir / "gitleaks",
        "\n".join(
            [
                "#!/usr/bin/env bash",
                f"touch {str(gitleaks_called)!r}",
                "exit 99",
                "",
            ]
        ),
    )

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin")
    result = run_shell_script(repo / "scripts" / "check-secrets.sh", cwd=repo, env=env)

    assert result.returncode == 1
    assert "check-secrets: failed to stage git file listing for gitleaks scan." in result.stderr
    assert "secret.txt" in result.stderr
    assert not gitleaks_called.exists()


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


def test_check_github_actions_passes_against_repo_workflows() -> None:
    """Repo-real smoke test: every workflow that ships in .github/workflows/
    keeps action majors at or above the Node 24 floor. With no workflows
    present the helper says so; with workflows present it validates them.
    """
    result = run_script("scripts/check_github_actions.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert (
        "No GitHub Actions workflows detected." in result.stdout
        or "Validated GitHub Actions majors" in result.stdout
    )


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


def test_check_python_lengths_strict_listing_fails_closed_outside_git(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "short.py").write_text("def short():\n    return 1\n", encoding="utf-8")

    result = run_script(
        "scripts/check_python_lengths.py",
        "--repo-root",
        str(repo),
        "--require-git-file-listing",
    )

    assert result.returncode == 1
    assert "repo file listing failed" in result.stderr
    assert "command: git ls-files -z --cached --others --exclude-standard" in result.stderr


def test_check_python_runtime_inheritance_strict_listing_fails_closed_outside_git(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "short.py").write_text("def short():\n    return 1\n", encoding="utf-8")

    result = run_script(
        "scripts/check_python_runtime_inheritance.py",
        "--repo-root",
        str(repo),
        "--require-git-file-listing",
    )

    assert result.returncode == 1
    assert "repo file listing failed" in result.stderr
    assert "command: git ls-files -z --cached --others --exclude-standard" in result.stderr


def test_check_python_lengths_rejects_too_long_skill_helper_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "helper.py").write_text("\n".join(f"print({i})" for i in range(361)) + "\n", encoding="utf-8")
    result = run_script("scripts/check_python_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "file length 361 exceeds limit 360" in result.stderr


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
    (tests_dir / "test_big.py").write_text("\n".join(f"VALUE_{i} = {i}" for i in range(801)) + "\n", encoding="utf-8")
    result = run_script("scripts/check_python_lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "file length 801 exceeds limit 800" in result.stderr


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
