from __future__ import annotations

import importlib
import importlib.util
import json
import os
import shutil
from pathlib import Path

import yaml

from tests.quality_gates.repo_shapes import install_committed_repo

from .support import (
    ROOT,
    charness_shaped_repo,
    run_script,
    run_shell_script,
    write_executable,
)

PYTHON_LENGTHS = importlib.import_module("scripts.check_code_lengths")


def _copy_script(repo: Path, script_name: str) -> Path:
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_path = scripts_dir / script_name
    shutil.copy2(ROOT / "scripts" / script_name, script_path)
    # Every repo-root gate sources the one export-copy guard, so it travels with each
    # copied script. Omitting it makes these tests fail on a missing file rather than
    # on the discovery and listing behavior they are about.
    shutil.copy2(ROOT / "scripts" / "exported-copy-guard.sh", scripts_dir / "exported-copy-guard.sh")
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


_STUB_ADVISORY_DETAIL = "docs/stub.md:3 stub inline-code advisory detail"


def _markdown_gate_repo(tmp_path: Path, *, advisory: bool) -> tuple[Path, Path, Path]:
    """A repo SHAPE for `check-markdown.sh`, not a copy of this checkout.

    These three cases used to clone the whole repository. What they own is the gate's
    COMPOSITION -- an advisory is non-blocking, markdownlint's exit code survives, and
    the two are emitted advisory-then-blocking -- so both sub-tools are stubbed. The
    inline-code detector's own message is owned by
    `test_check_markdown_inline_code.py`, which already asserts "wraps across line";
    re-asserting it here bought a duplicate at the price of a whole-repo clone.

    `check-markdown.sh` decides WARN from the helper's EXIT CODE (non-zero -> advisory
    banner + its output), so `advisory` is expressed exactly that way.
    """

    repo, source, _mirror = charness_shaped_repo(tmp_path, "check-markdown.sh")
    body = f'import sys\nsys.stdout.write("{_STUB_ADVISORY_DETAIL}\\n")\nraise SystemExit(1)\n'
    (source.parent / "check_markdown_inline_code.py").write_text(
        body if advisory else "raise SystemExit(0)\n", encoding="utf-8"
    )
    bin_dir = repo / "bin"
    bin_dir.mkdir(exist_ok=True)
    return repo, source, bin_dir


def _fake_markdownlint(bin_dir: Path, body: str) -> dict[str, str]:
    write_executable(bin_dir / "markdownlint-cli2", body)
    return {**os.environ, "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"}


def test_check_markdown_demotes_wrapped_inline_code_to_warn(tmp_path: Path) -> None:
    # North-star P1: a wrapped inline-code span's rendered output is admittedly
    # correct, so the commit boundary must WARN (exit 0), not block, on it.
    _repo, source, bin_dir = _markdown_gate_repo(tmp_path, advisory=True)
    env = _fake_markdownlint(bin_dir, "#!/usr/bin/env bash\nexit 0\n")

    result = run_shell_script(source, cwd=_repo, env=env)

    assert result.returncode == 0, result.stdout + result.stderr
    combined = result.stdout + result.stderr
    assert "WARN:" in combined
    assert _STUB_ADVISORY_DETAIL in combined


def test_check_markdown_keeps_markdownlint_failure_blocking(tmp_path: Path) -> None:
    repo, source, bin_dir = _markdown_gate_repo(tmp_path, advisory=False)
    env = _fake_markdownlint(
        bin_dir,
        "#!/usr/bin/env bash\necho 'docs/bad.md:4:1 error MD999/test lint failure'\necho 'lint stderr detail' >&2\nexit 7\n",
    )

    result = run_shell_script(source, cwd=repo, env=env)

    assert result.returncode == 7
    assert "docs/bad.md:4:1 error MD999/test lint failure" in result.stdout
    assert "lint stderr detail" in result.stderr
    assert "lint stderr detail" not in result.stdout
    # Restored with the fixture. This assertion was DELETED while the fixture was a
    # clone of this checkout: it then meant "every checked-in Markdown file happens to
    # be advisory-clean", and one wrapped inline code span in docs/index.md broke it.
    # With the advisory sub-tool stubbed clean, it means what it always should have --
    # a blocking lint failure is reported WITHOUT a spurious advisory -- which is this
    # case's own invariant rather than a coupling to repo-wide doc cleanliness. The
    # sibling below owns the ordering when an advisory genuinely is present.
    assert "WARN:" not in result.stdout + result.stderr


def test_check_markdown_reports_advisory_before_blocking_lint_failure(tmp_path: Path) -> None:
    repo, source, bin_dir = _markdown_gate_repo(tmp_path, advisory=True)
    env = _fake_markdownlint(
        bin_dir,
        "#!/usr/bin/env bash\necho 'docs/bad.md:4:1 error MD999/test lint failure'\nexit 9\n",
    )

    result = run_shell_script(source, cwd=repo, env=env)

    combined = result.stdout + result.stderr
    assert result.returncode == 9
    assert "WARN:" in combined
    assert "docs/bad.md:4:1 error MD999/test lint failure" in combined
    assert combined.index("WARN:") < combined.index("docs/bad.md:4:1 error MD999/test lint failure")


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
    assert args == ["-x", "scripts/check-shell.sh", "scripts/exported-copy-guard.sh"]


def test_check_shell_discovers_nested_test_fixtures(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_path = _copy_script(repo, "check-shell.sh")
    fixture = repo / "tests" / "fixtures" / "fake-tool.sh"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    output_path = repo / "shellcheck-args.txt"
    write_executable(
        bin_dir / "shellcheck",
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" > \"$TEST_OUTPUT\"\n",
    )

    result = run_shell_script(
        script_path,
        cwd=repo,
        env=dict(PATH=f"{bin_dir}:/usr/bin:/bin", TEST_OUTPUT=str(output_path)),
    )

    assert result.returncode == 0, result.stderr
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "-x",
        "scripts/check-shell.sh",
        "scripts/exported-copy-guard.sh",
        "tests/fixtures/fake-tool.sh",
    ]


def test_check_secrets_prefers_gitleaks_when_available(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "check-secrets.sh", scripts_dir / "check-secrets.sh")
    shutil.copy2(ROOT / "scripts" / "exported-copy-guard.sh", scripts_dir / "exported-copy-guard.sh")
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
    install_committed_repo(
        repo,
        {
            "README.md": "# Demo\n",
            ".gitignore": "integrations/locks/*.json\n",
            ".secretlintrc.json": (ROOT / ".secretlintrc.json").read_text(encoding="utf-8"),
            ".secretlintignore": (ROOT / ".secretlintignore").read_text(encoding="utf-8"),
            "scripts/check-secrets.sh": (ROOT / "scripts" / "check-secrets.sh").read_text(
                encoding="utf-8"
            ),
        },
        executable=("scripts/check-secrets.sh",),
    )
    shutil.copy2(
        ROOT / "scripts" / "exported-copy-guard.sh",
        repo / "scripts" / "exported-copy-guard.sh",
    )
    ignored = repo / "integrations" / "locks" / "agent-browser.json"
    ignored.parent.mkdir(parents=True)
    ignored.write_text('{"token":"ignored-runtime-state"}\n', encoding="utf-8")

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


def test_check_secrets_gitleaks_skips_deleted_tracked_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    install_committed_repo(
        repo,
        {
            "secret.txt": "token=missing-from-staged-scan\n",
            ".gitleaks.toml": (ROOT / ".gitleaks.toml").read_text(encoding="utf-8"),
            "scripts/check-secrets.sh": (ROOT / "scripts" / "check-secrets.sh").read_text(
                encoding="utf-8"
            ),
            "scripts/exported-copy-guard.sh": (
                ROOT / "scripts" / "exported-copy-guard.sh"
            ).read_text(encoding="utf-8"),
        },
        executable=("scripts/check-secrets.sh", "scripts/exported-copy-guard.sh"),
    )
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
                "exit 0",
                "",
            ]
        ),
    )

    env = dict(PATH=f"{bin_dir}:/usr/bin:/bin")
    result = run_shell_script(repo / "scripts" / "check-secrets.sh", cwd=repo, env=env)

    assert result.returncode == 0, result.stderr
    assert gitleaks_called.exists()


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

    result = run_script("scripts/check_github_actions.py", "--repo-root", str(repo))
    assert result.returncode == 1
    payload = yaml.safe_load(result.stderr)
    assert [finding["category"] for finding in payload["findings"]] == [
        "node24_incompatible",
        "baseline_lag",
        "node24_incompatible",
    ]
    assert payload["findings"][0]["normalized_action"] == "actions/checkout"
    assert payload["findings"][0]["recommended_reference"] == "v6"
    assert payload["findings"][1]["normalized_action"] == "actions/checkout"
    assert payload["findings"][2]["normalized_action"] == "actions/setup-node"
    # The deleted renderer was the only carrier of the remedy prose. Each finding
    # now owes a remedy row saying WHICH major to move to and why, plus the
    # standing guidance that the rollout env vars are escape hatches, not fixes.
    assert [remedy["use_instead"] for remedy in payload["remedies"]] == ["@v6", "@v6", "@v6"]
    assert payload["remedies"][0]["reason"] == "below the Node 24-ready floor"
    assert payload["remedies"][1]["reason"] == "behind the current documented major"
    assert any("escape hatch" in line for line in payload["guidance"])


def test_check_github_actions_yaml_output_is_stable_and_utf8(monkeypatch, capsys, tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "check_github_actions_under_test",
        ROOT / "scripts" / "check_github_actions.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(
        module,
        "collect_github_actions_drift",
        lambda _repo_root: {
            "workflow_files": [".github/workflows/ci.yml"],
            "checked_actions": ["demo/action"],
            "findings": [],
            "skipped_refs": [],
            "guidance": {"z_note": "한글", "a_note": "first"},
        },
    )
    monkeypatch.setattr(
        "sys.argv",
        ["check_github_actions.py", "--repo-root", str(tmp_path)],
    )

    assert module.main() == 0
    captured = capsys.readouterr()
    # A clean run stays on stdout so a passing gate's output is still quotable.
    assert captured.err == ""
    # Stable: one document, emitted in the payload's own key order, so a diff of
    # two runs over the same tree is empty rather than a reshuffle.
    assert captured.out.startswith("workflow_files:\n")
    assert yaml.safe_load(captured.out)["guidance"] == {"z_note": "한글", "a_note": "first"}
    # UTF-8 stays literal rather than escaped, in YAML as it did in JSON.
    assert "한글" in captured.out
    assert "\\ud55c" not in captured.out
