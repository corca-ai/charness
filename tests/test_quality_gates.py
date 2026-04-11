from __future__ import annotations

import importlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def test_validate_skills_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-skills.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_unquoted_description(tmp_path: Path) -> None:
    repo = make_minimal_skill_repo(
        tmp_path,
        "Use when something has punctuation: this should be rejected.",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "double-quoted" in result.stderr


def test_validate_skills_rejects_missing_references_section(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
            ]
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing `## References` section" in result.stderr


def test_validate_skills_rejects_unlisted_reference_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (references_dir / "note.md").write_text("# Note\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "## References",
                "",
                "- `references/other.md`",
            ]
        ),
        encoding="utf-8",
    )
    (references_dir / "other.md").write_text("# Other\n", encoding="utf-8")
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "unlisted reference file(s): `references/note.md`" in result.stderr


def test_validate_skills_accepts_support_skill_package(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "support" / "demo-support"
    references_dir = skill_dir / "references"
    scripts_dir = skill_dir / "scripts"
    references_dir.mkdir(parents=True)
    scripts_dir.mkdir()
    (references_dir / "runtime.md").write_text("# Runtime\n", encoding="utf-8")
    (scripts_dir / "helper.py").write_text("print('ok')\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo-support",
                'description: "Demo support skill."',
                "---",
                "",
                "# Demo Support",
                "",
                "## References",
                "",
                "- `references/runtime.md`",
                "- `scripts/helper.py`",
            ]
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def make_public_skill_with_bootstrap(
    tmp_path: Path,
    bootstrap_body: str,
    *,
    extra_body: str = "",
    with_preflight_pointer: bool = True,
) -> Path:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    skill_dir.mkdir(parents=True)
    pointer_line = (
        "\n"
        "See `create-skill/references/binary-preflight.md` for the "
        "binary-preflight protocol.\n"
        if with_preflight_pointer
        else "\n"
    )
    body = "\n".join(
        [
            "---",
            "name: demo",
            'description: "Demo public skill."',
            "---",
            "",
            "# Demo",
            "",
            "## Bootstrap",
            "",
            "```bash",
            bootstrap_body.rstrip(),
            "```",
            pointer_line,
            extra_body,
            "",
            "## References",
            "",
            "- `references/note.md`",
            "",
        ]
    )
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
    return repo


def test_validate_skills_rejects_undeclared_non_baseline_binary(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(tmp_path, "rg --files docs skills")
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "non-baseline" in result.stderr
    assert "`rg`" in result.stderr


def test_validate_skills_accepts_declared_non_baseline_binary(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg --files docs skills",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_required_tools_without_preflight_pointer(
    tmp_path: Path,
) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg --files docs skills",
        with_preflight_pointer=False,
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "binary-preflight" in result.stderr


def test_validate_skills_rejects_swallow_pattern_on_non_baseline(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg -n 'pattern' . 2>/dev/null || true",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "swallow" in result.stderr


def test_validate_skills_rejects_or_true_swallow_on_non_baseline(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\nrg -n 'pattern' . || true",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "swallow" in result.stderr


def test_validate_skills_allows_swallow_on_baseline_only_line(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "git config --get core.hooksPath || true\n"
        "find .git/hooks -maxdepth 1 -type f 2>/dev/null | sort",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_ignores_non_baseline_inside_quoted_regex(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\n"
        'rg -n "eslint|ruff|lefthook|husky" docs',
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_rejects_unused_required_tools_declaration(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        "# Required Tools: rg\ngit status --short",
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "never calls it" in result.stderr


def test_validate_skills_allows_local_script_invocation(tmp_path: Path) -> None:
    repo = make_public_skill_with_bootstrap(
        tmp_path,
        'python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .',
    )
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_skills_support_skill_skips_preflight_gate(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "support" / "demo-support"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: demo-support",
                'description: "Demo support skill."',
                "---",
                "",
                "# Demo Support",
                "",
                "## Bootstrap",
                "",
                "```bash",
                "rg --files docs",
                "```",
                "",
                "## References",
                "",
                "- `references/runtime.md`",
            ]
        ),
        encoding="utf-8",
    )
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "runtime.md").write_text("# Runtime\n", encoding="utf-8")
    result = run_script("scripts/validate-skills.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_validate_profiles_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_presets_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-presets.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_validate_packaging_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-packaging.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_sync_root_plugin_manifests_writes_install_surface(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "skills" / "public").mkdir(parents=True)
    (repo / "skills" / "support").mkdir(parents=True)
    (repo / "profiles").mkdir(parents=True)
    (repo / "presets").mkdir(parents=True)
    (repo / "integrations" / "tools").mkdir(parents=True)
    shutil.copy2(ROOT / "packaging" / "plugin.schema.json", repo / "packaging" / "plugin.schema.json")
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "packaging" / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "package_id": "demo",
                "display_name": "demo",
                "version": "0.1.0",
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
                "codex": {
                    "manifest_path": ".codex-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.1.0",
                        "description": "Demo package.",
                        "author": {"name": "Demo"},
                        "homepage": "https://example.com/demo",
                        "repository": "https://example.com/demo",
                        "keywords": ["demo"],
                        "skills": "./skills/",
                        "interface": {
                            "displayName": "demo",
                            "shortDescription": "Demo package.",
                            "longDescription": "Demo package for plugin export tests.",
                            "developerName": "Demo",
                            "category": "Productivity",
                            "capabilities": ["Read"],
                            "websiteURL": "https://example.com/demo",
                            "defaultPrompt": ["Use the demo plugin."],
                        },
                    },
                    "repo_marketplace": {
                        "path": ".agents/plugins/marketplace.json",
                        "default_source_path": "./plugins/demo",
                        "checked_in_source_path": "./plugins/demo",
                        "display_name": "demo",
                        "category": "Productivity",
                    },
                },
                "claude": {
                    "manifest_path": ".claude-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.1.0",
                        "description": "Demo package.",
                        "author": {"name": "Demo"},
                        "repository": "https://example.com/demo",
                    },
                    "marketplace": {
                        "path": ".claude-plugin/marketplace.json",
                        "name": "demo-marketplace",
                        "source_path": "./plugins/demo",
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/sync_root_plugin_manifests.py", "--repo-root", str(repo), "--package-id", "demo")
    assert result.returncode == 0, result.stderr
    assert (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").exists()
    assert (repo / ".claude-plugin" / "marketplace.json").exists()
    assert (repo / "plugins" / "demo" / ".codex-plugin" / "plugin.json").exists()
    assert (repo / ".agents" / "plugins" / "marketplace.json").exists()

    validate = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert validate.returncode == 0, validate.stderr


def test_check_python_lengths_passes_on_current_repo() -> None:
    result = run_script("scripts/check-python-lengths.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


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
    gitleaks.write_text(
        "#!/bin/bash\nprintf '%s\\n' \"$@\" > \"$TEST_OUTPUT\"\n",
        encoding="utf-8",
    )
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
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        [
            "git",
            "add",
            "README.md",
            ".gitignore",
            ".secretlintrc.json",
            ".secretlintignore",
            "scripts/check-secrets.sh",
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    bin_dir = repo / "bin"
    bin_dir.mkdir()
    output_path = repo / "npm-args.txt"
    npm = bin_dir / "npm"
    npm.write_text(
        "#!/bin/bash\nprintf '%s\\n' \"$@\" > \"$TEST_OUTPUT\"\n",
        encoding="utf-8",
    )
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


def test_check_supply_chain_passes_on_current_repo() -> None:
    result = run_script("scripts/check-supply-chain.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert "package-lock.json" in result.stdout


def test_check_supply_chain_requires_javascript_lockfile(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text(
        json.dumps({"private": True, "devDependencies": {"markdownlint-cli2": "0.22.0"}}, indent=2) + "\n",
        encoding="utf-8",
    )

    result = run_script("scripts/check-supply-chain.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "no lockfile is checked in" in result.stderr


def test_check_supply_chain_requires_declared_pnpm_lockfile(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text(
        json.dumps(
            {
                "private": True,
                "packageManager": "pnpm@9.0.0",
                "dependencies": {"left-pad": "1.3.0"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "package-lock.json").write_text("{}", encoding="utf-8")

    result = run_script("scripts/check-supply-chain.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "packageManager declares `pnpm`" in result.stderr


def test_check_supply_chain_requires_uv_lock_when_dependencies_exist(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "demo"',
                'version = "0.1.0"',
                'dependencies = ["requests>=2.0"]',
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script("scripts/check-supply-chain.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "uv.lock is missing" in result.stderr


def test_check_supply_chain_accepts_uv_lock_for_python_dependencies(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "demo"',
                'version = "0.1.0"',
                'dependencies = ["requests>=2.0"]',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "uv.lock").write_text("version = 1\n", encoding="utf-8")

    result = run_script("scripts/check-supply-chain.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "uv:uv.lock" in result.stdout


def test_record_quality_runtime_writes_summary_and_archive(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    first = run_script(
        "scripts/record_quality_runtime.py",
        "--repo-root",
        str(repo),
        "--label",
        "pytest",
        "--elapsed-ms",
        "1234",
        "--status",
        "pass",
        "--timestamp",
        "2026-04-10T09:00:00Z",
        cwd=ROOT,
    )
    assert first.returncode == 0, first.stderr

    second = run_script(
        "scripts/record_quality_runtime.py",
        "--repo-root",
        str(repo),
        "--label",
        "pytest",
        "--elapsed-ms",
        "2345",
        "--status",
        "fail",
        "--timestamp",
        "2026-04-11T09:00:00Z",
        cwd=ROOT,
    )
    assert second.returncode == 0, second.stderr

    summary_path = repo / "skill-outputs" / "quality" / "runtime-signals.json"
    archive_path = repo / "skill-outputs" / "quality" / "history" / "runtime-signals-2026-04.jsonl"
    assert summary_path.exists()
    assert archive_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    pytest_entry = summary["commands"]["pytest"]
    assert pytest_entry["samples"] == 2
    assert pytest_entry["passes"] == 1
    assert pytest_entry["failures"] == 1
    assert pytest_entry["latest"]["elapsed_ms"] == 2345
    assert pytest_entry["median_recent_elapsed_ms"] == 1789

    archive_lines = archive_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(archive_lines) == 2


def test_record_quality_runtime_rotates_old_monthly_archives(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    history_dir = repo / "skill-outputs" / "quality" / "history"
    history_dir.mkdir(parents=True)

    for month in range(1, 14):
        result = run_script(
            "scripts/record_quality_runtime.py",
            "--repo-root",
            str(repo),
            "--label",
            "pytest",
            "--elapsed-ms",
            str(1000 + month),
            "--status",
            "pass",
            "--timestamp",
            f"2025-{month:02d}-01T00:00:00Z" if month <= 12 else "2026-01-01T00:00:00Z",
            cwd=ROOT,
        )
        assert result.returncode == 0, result.stderr

    archives = sorted(path.name for path in history_dir.glob("runtime-signals-*.jsonl"))
    assert len(archives) == 12
    assert "runtime-signals-2025-01.jsonl" not in archives
    assert "runtime-signals-2026-01.jsonl" in archives


def test_run_quality_summarizes_success_without_replaying_logs(tmp_path: Path) -> None:
    repo, env = make_quality_runner_repo(tmp_path)
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "PASS validate-skills" in result.stdout
    assert "PASS check-markdown" in result.stdout
    assert "PASS pytest" in result.stdout
    assert "quality success output from validate-skills" not in result.stdout
    assert "quality success output from check-markdown" not in result.stdout
    assert "Quality summary: 23 passed, 0 failed" in result.stdout


def test_run_quality_replays_only_failing_command_logs(tmp_path: Path) -> None:
    repo, env = make_quality_runner_repo(tmp_path)
    env["QUALITY_FAIL_LABEL"] = "check-markdown"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 1
    assert "FAIL check-markdown" in result.stdout
    assert "--- check-markdown output ---" in result.stdout
    assert "quality failure output from check-markdown" in result.stdout
    assert "quality success output from validate-skills" not in result.stdout
    assert "Quality summary: 22 passed, 1 failed" in result.stdout


def test_run_quality_verbose_replays_success_logs(tmp_path: Path) -> None:
    repo, env = make_quality_runner_repo(tmp_path)
    env["CHARNESS_QUALITY_VERBOSE"] = "1"
    result = run_shell_script(repo / "scripts" / "run-quality.sh", cwd=repo, env=env)
    assert result.returncode == 0, result.stderr
    assert "--- validate-skills output ---" in result.stdout
    assert "quality success output from validate-skills" in result.stdout
    assert "--- check-markdown output ---" in result.stdout
    assert "quality success output from check-markdown" in result.stdout


def test_install_git_hooks_sets_core_hookspath(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", repo / "scripts" / "install-git-hooks.sh")
    shutil.copy2(ROOT / ".githooks" / "pre-push", repo / ".githooks" / "pre-push")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    result = subprocess.run(
        ["bash", "scripts/install-git-hooks.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    hookspath = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert hookspath.stdout.strip() == str((repo / ".githooks").resolve())


def test_validate_maintainer_setup_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-maintainer-setup.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


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
    assert payload["artifact_path"] == "skill-outputs/narrative/narrative.md"
    assert payload["freshness"]["status"] in {"ahead", "current", "missing-remote", "not-git", "unavailable"}


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
                "output_dir: skill-outputs/release",
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

    result = run_script(
        "skills/public/release/scripts/bump_version.py",
        "--repo-root",
        str(repo),
        "--part",
        "patch",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    manifest = json.loads((repo / "packaging" / "demo.json").read_text(encoding="utf-8"))
    assert payload["old_version"] == "0.0.0-dev"
    assert payload["new_version"] == "0.0.1"
    assert manifest["version"] == "0.0.1"
    assert manifest["claude"]["manifest"]["version"] == "0.0.1"
    assert manifest["codex"]["manifest"]["version"] == "0.0.1"
    assert (repo / "sync-version.txt").read_text(encoding="utf-8").strip() == "0.0.1"


def test_validate_maintainer_setup_requires_installed_hookspath(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / ".githooks").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "validate-maintainer-setup.py", repo / "scripts" / "validate-maintainer-setup.py")
    shutil.copy2(ROOT / "scripts" / "install-git-hooks.sh", repo / "scripts" / "install-git-hooks.sh")
    shutil.copy2(ROOT / ".githooks" / "pre-push", repo / ".githooks" / "pre-push")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)

    missing = subprocess.run(
        ["python3", "scripts/validate-maintainer-setup.py", "--repo-root", str(repo)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert missing.returncode == 1
    assert "install-git-hooks.sh" in missing.stderr

    install = subprocess.run(
        ["bash", "scripts/install-git-hooks.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert install.returncode == 0, install.stderr

    ready = subprocess.run(
        ["python3", "scripts/validate-maintainer-setup.py", "--repo-root", str(repo)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert ready.returncode == 0, ready.stderr


def test_validate_profiles_rejects_missing_skill_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    profiles_dir.mkdir(parents=True)
    (profiles_dir / "constitutional.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "constitutional",
                "display_name": "Constitutional",
                "purpose": "Test",
                "bundles": {"public_skills": ["handoff"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing artifact `handoff`" in result.stderr


def test_validate_presets_rejects_organization_scope_without_product_slice(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    presets_dir = repo / "presets"
    presets_dir.mkdir(parents=True)
    (presets_dir / "bad-preset.md").write_text(
        "\n".join(
            [
                "---",
                "name: bad-preset",
                'description: "Bad preset."',
                "preset_kind: sample-vocabulary",
                "install_scope: organization",
                "---",
                "",
                "# bad-preset",
                "",
                "## Intended Use",
                "",
                "Broken example.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-presets.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "organization-scope presets must use `preset_kind: product-slice`" in result.stderr


def test_validate_presets_rejects_product_slice_without_exposure_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    presets_dir = repo / "presets"
    presets_dir.mkdir(parents=True)
    (presets_dir / "org-slice.md").write_text(
        "\n".join(
            [
                "---",
                "name: org-slice",
                'description: "Org slice."',
                "preset_kind: product-slice",
                "install_scope: organization",
                "---",
                "",
                "# org-slice",
                "",
                "## Intended Use",
                "",
                "Missing exposure contract.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-presets.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "product-slice presets must include an `## Exposure Contract` section" in result.stderr


def test_check_python_lengths_rejects_too_long_function(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    long_body = "\n".join(f"    value_{i} = {i}" for i in range(101))
    (scripts_dir / "long.py").write_text(
        "\n".join(
            [
                "def too_long():",
                long_body,
                "    return 0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/check-python-lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "function `too_long` length" in result.stderr


def test_check_python_lengths_rejects_too_long_skill_helper_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    helper_dir = repo / "skills" / "public" / "demo" / "scripts"
    helper_dir.mkdir(parents=True)
    (helper_dir / "helper.py").write_text(
        "\n".join(f"print({i})" for i in range(221)) + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-python-lengths.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "file length 221 exceeds limit 220" in result.stderr


def test_validate_profiles_rejects_unknown_smoke_scenario(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "handoff"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (public_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n",
        encoding="utf-8",
    )
    (profiles_dir / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "demo",
                "display_name": "Demo",
                "purpose": "Test",
                "bundles": {"public_skills": ["handoff"]},
                "validation": {"smoke_scenarios": ["not-a-real-scenario"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "unknown eval scenario `not-a-real-scenario`" in result.stderr


def test_validate_profiles_rejects_missing_extends_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "handoff"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (public_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n",
        encoding="utf-8",
    )
    (profiles_dir / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "demo",
                "display_name": "Demo",
                "purpose": "Test",
                "extends": ["missing-base"],
                "bundles": {"public_skills": ["handoff"]},
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "extends[]` references missing artifact `missing-base`" in result.stderr


def test_validate_profiles_rejects_unknown_top_level_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profiles_dir = repo / "profiles"
    public_skill_dir = repo / "skills" / "public" / "handoff"
    profiles_dir.mkdir(parents=True)
    public_skill_dir.mkdir(parents=True)
    (public_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n\n## References\n\n- `references/demo.md`\n",
        encoding="utf-8",
    )
    (public_skill_dir / "references").mkdir(parents=True)
    (public_skill_dir / "references" / "demo.md").write_text("# Demo\n", encoding="utf-8")
    (profiles_dir / "demo.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "profile_id": "demo",
                "display_name": "Demo",
                "purpose": "Test",
                "bundles": {"public_skills": ["handoff"]},
                "unexpected": True,
            }
        ),
        encoding="utf-8",
    )
    result = run_script("scripts/validate-profiles.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Additional properties are not allowed" in result.stderr


def test_validate_adapters_passes_on_current_repo() -> None:
    result = run_script("scripts/validate-adapters.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_check_skill_contracts_passes_on_current_repo() -> None:
    result = run_script("scripts/check-skill-contracts.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_check_doc_links_rejects_foreign_absolute_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text(
        "[bad](/tmp/not-in-repo.md)\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "foreign absolute link" in result.stderr


def test_check_doc_links_rejects_bare_internal_markdown_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text(
        "# Demo\n\nSee docs/guide.md before editing.\n",
        encoding="utf-8",
    )
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "bare internal markdown reference" in result.stderr


def test_check_doc_links_allows_internal_markdown_reference_in_code(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    (repo / "README.md").write_text(
        "\n".join(
            [
                "# Demo",
                "",
                "Use the linked guide: [guide](docs/guide.md).",
                "",
                "`docs/guide.md` can still appear in inline code.",
                "",
                "```bash",
                "sed -n '1,20p' docs/guide.md",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (docs_dir / "guide.md").write_text("# Guide\n", encoding="utf-8")
    result = run_script("scripts/check-doc-links.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_check_duplicates_passes_clean_repo() -> None:
    result = run_script("scripts/check-duplicates.py", "--repo-root", str(ROOT), "--json", "--fail-on-match")
    assert result.returncode == 0, result.stderr
    duplicates = json.loads(result.stdout)
    assert isinstance(duplicates, list)
    assert duplicates == []


def test_adapter_lib_renders_and_loads_simple_yaml_mapping() -> None:
    rendered = ADAPTER_LIB.render_yaml_mapping(
        [
            ("version", 1),
            ("repo", "demo"),
            ("output_dir", "skill-outputs/demo"),
            ("commands", ["pytest -q", "ruff check ."]),
            ("empty", []),
        ]
    )

    assert ADAPTER_LIB.load_yaml(rendered) == {
        "version": 1,
        "repo": "demo",
        "output_dir": "skill-outputs/demo",
        "commands": ["pytest -q", "ruff check ."],
        "empty": [],
    }


def test_check_duplicates_rejects_near_duplicate_docs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    docs_dir.mkdir(parents=True)
    repeated_lines = "\n".join(f"- repeated line {i}" for i in range(20))
    (docs_dir / "alpha.md").write_text(f"# Alpha\n\n{repeated_lines}\n", encoding="utf-8")
    (docs_dir / "beta.md").write_text(f"# Beta\n\n{repeated_lines}\n", encoding="utf-8")

    result = run_script(
        "scripts/check-duplicates.py",
        "--repo-root",
        str(repo),
        "--fail-on-match",
        "--json",
    )
    assert result.returncode == 1
    duplicates = json.loads(result.stdout)
    assert duplicates
    assert duplicates[0]["left"] == "docs/alpha.md"
    assert duplicates[0]["right"] == "docs/beta.md"


def test_run_evals_passes_on_current_repo() -> None:
    result = run_script("scripts/run-evals.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    assert f"Ran {len(EVAL_REGISTRY.SCENARIOS)} eval scenario(s)." in result.stdout


def test_validate_packaging_rejects_wrong_codex_manifest_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "skills" / "public").mkdir(parents=True)
    (repo / "skills" / "support").mkdir(parents=True)
    (repo / "profiles").mkdir(parents=True)
    (repo / "presets").mkdir(parents=True)
    (repo / "integrations" / "tools").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
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
                "codex": {
                    "manifest_path": "plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.0.0-dev",
                        "description": "Demo package.",
                        "author": {"name": "Demo"},
                        "homepage": "https://example.com/demo",
                        "repository": "https://example.com/demo",
                        "keywords": ["demo"],
                        "skills": "./skills/",
                        "interface": {
                            "displayName": "demo",
                            "shortDescription": "Demo package.",
                            "longDescription": "Demo package for plugin export tests.",
                            "developerName": "Demo",
                            "category": "Productivity",
                            "capabilities": ["Read"],
                            "websiteURL": "https://example.com/demo",
                            "defaultPrompt": ["Use the demo plugin."],
                        },
                    },
                    "repo_marketplace": {
                        "path": ".agents/plugins/marketplace.json",
                        "default_source_path": "./plugins/demo",
                        "checked_in_source_path": "./plugins/demo",
                        "display_name": "demo",
                        "category": "Productivity",
                    },
                },
                "claude": {
                    "manifest_path": ".claude-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.0.0-dev",
                        "description": "Demo package.",
                        "author": {"name": "Demo"},
                        "repository": "https://example.com/demo",
                    },
                    "marketplace": {
                        "path": ".claude-plugin/marketplace.json",
                        "name": "demo-marketplace",
                        "source_path": "./plugins/demo",
                    },
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert ".codex-plugin/plugin.json" in result.stderr


def test_validate_packaging_rejects_unknown_top_level_field(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "packaging").mkdir(parents=True)
    (repo / "skills" / "public").mkdir(parents=True)
    (repo / "skills" / "support").mkdir(parents=True)
    (repo / "profiles").mkdir(parents=True)
    (repo / "presets").mkdir(parents=True)
    (repo / "integrations" / "tools").mkdir(parents=True)
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
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
                "codex": {
                    "manifest_path": ".codex-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.0.0-dev",
                        "description": "Demo package.",
                        "author": {"name": "Demo"},
                        "homepage": "https://example.com/demo",
                        "repository": "https://example.com/demo",
                        "keywords": ["demo"],
                        "skills": "./skills/",
                        "interface": {
                            "displayName": "demo",
                            "shortDescription": "Demo package.",
                            "longDescription": "Demo package for plugin export tests.",
                            "developerName": "Demo",
                            "category": "Productivity",
                            "capabilities": ["Read"],
                            "websiteURL": "https://example.com/demo",
                            "defaultPrompt": ["Use the demo plugin."],
                        },
                    },
                    "repo_marketplace": {
                        "path": ".agents/plugins/marketplace.json",
                        "default_source_path": "./plugins/demo",
                        "checked_in_source_path": "./plugins/demo",
                        "display_name": "demo",
                        "category": "Productivity",
                    },
                },
                "claude": {
                    "manifest_path": ".claude-plugin/plugin.json",
                    "manifest": {
                        "name": "demo",
                        "version": "0.0.0-dev",
                        "description": "Demo package.",
                        "author": {"name": "Demo"},
                        "repository": "https://example.com/demo",
                    },
                    "marketplace": {
                        "path": ".claude-plugin/marketplace.json",
                        "name": "demo-marketplace",
                        "source_path": "./plugins/demo",
                    },
                },
                "unexpected": True,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_script("scripts/validate-packaging.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "Additional properties are not allowed" in result.stderr


def test_export_plugin_materializes_codex_and_claude_layouts(tmp_path: Path) -> None:
    codex_root = tmp_path / "codex-export"
    claude_root = tmp_path / "claude-export"

    codex_result = run_script(
        "scripts/export-plugin.py",
        "--repo-root",
        str(ROOT),
        "--host",
        "codex",
        "--output-root",
        str(codex_root),
        "--with-marketplace",
    )
    assert codex_result.returncode == 0, codex_result.stderr
    codex_manifest = codex_root / "plugins" / "charness" / ".codex-plugin" / "plugin.json"
    codex_marketplace = codex_root / ".agents" / "plugins" / "marketplace.json"
    assert codex_manifest.is_file()
    assert codex_marketplace.is_file()
    assert json.loads(codex_manifest.read_text(encoding="utf-8"))["skills"] == "./skills/"
    assert (
        json.loads(codex_marketplace.read_text(encoding="utf-8"))["plugins"][0]["source"]["path"]
        == "./plugins/charness"
    )

    claude_result = run_script(
        "scripts/export-plugin.py",
        "--repo-root",
        str(ROOT),
        "--host",
        "claude",
        "--output-root",
        str(claude_root),
    )
    assert claude_result.returncode == 0, claude_result.stderr
    claude_manifest = claude_root / "plugins" / "charness" / ".claude-plugin" / "plugin.json"
    exported_readme = claude_root / "plugins" / "charness" / "README.md"
    exported_profiles = claude_root / "plugins" / "charness" / "profiles"
    exported_gather_skill = claude_root / "plugins" / "charness" / "skills" / "gather" / "SKILL.md"
    exported_support_skill = claude_root / "plugins" / "charness" / "support" / "gather-slack" / "SKILL.md"
    exported_helper_script = claude_root / "plugins" / "charness" / "scripts" / "adapter_lib.py"
    assert claude_manifest.is_file()
    assert exported_readme.is_file()
    assert exported_profiles.is_dir()
    assert exported_gather_skill.is_file()
    assert exported_support_skill.is_file()
    assert exported_helper_script.is_file()
    assert not (claude_root / "plugins" / "charness" / "skills" / "public").exists()
    assert not (claude_root / "plugins" / "charness" / "support" / "generated").exists()
    assert json.loads(claude_manifest.read_text(encoding="utf-8"))["repository"] == "https://github.com/corca-ai/charness"

    consumer_root = tmp_path / "consumer"
    consumer_root.mkdir()
    gather_resolve = run_script(
        str(claude_root / "plugins" / "charness" / "skills" / "gather" / "scripts" / "resolve_adapter.py"),
        "--repo-root",
        str(consumer_root),
        cwd=ROOT,
    )
    assert gather_resolve.returncode == 0, gather_resolve.stderr


def test_export_plugin_allows_version_override(tmp_path: Path) -> None:
    output_root = tmp_path / "codex-export"
    result = run_script(
        "scripts/export-plugin.py",
        "--repo-root",
        str(ROOT),
        "--host",
        "codex",
        "--output-root",
        str(output_root),
        "--version-override",
        "1.2.3",
        "--with-marketplace",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["version"] == "1.2.3"

    codex_manifest = output_root / "plugins" / "charness" / ".codex-plugin" / "plugin.json"
    codex_marketplace = output_root / ".agents" / "plugins" / "marketplace.json"
    assert json.loads(codex_manifest.read_text(encoding="utf-8"))["version"] == "1.2.3"
    assert json.loads(codex_marketplace.read_text(encoding="utf-8"))["plugins"][0]["name"] == "charness"

    shared_manifest = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))
    assert shared_manifest["version"] == "0.0.0-dev"


def test_check_skill_contracts_rejects_missing_required_snippet(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    handoff_skill_dir = repo / "skills" / "public" / "handoff"
    gather_skill_dir = repo / "skills" / "public" / "gather"
    create_skill_dir = repo / "skills" / "public" / "create-skill"
    spec_skill_dir = repo / "skills" / "public" / "spec"
    handoff_skill_dir.mkdir(parents=True)
    gather_skill_dir.mkdir(parents=True)
    create_skill_dir.mkdir(parents=True)
    spec_skill_dir.mkdir(parents=True)

    (handoff_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n",
        encoding="utf-8",
    )
    (gather_skill_dir / "SKILL.md").write_text(
        (ROOT / "skills" / "public" / "gather" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (create_skill_dir / "SKILL.md").write_text(
        (ROOT / "skills" / "public" / "create-skill" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (spec_skill_dir / "SKILL.md").write_text(
        (ROOT / "skills" / "public" / "spec" / "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    result = run_script("scripts/check-skill-contracts.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required contract snippet" in result.stderr


def test_find_skills_lists_adapter_configured_trusted_roots(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    local_skill_dir = repo / "skills" / "public" / "local-demo"
    trusted_skill_dir = repo / "vendor" / "trusted-skills" / "trusted-demo"
    adapter_dir = repo / ".agents"
    local_skill_dir.mkdir(parents=True)
    trusted_skill_dir.mkdir(parents=True)
    adapter_dir.mkdir(parents=True)

    (local_skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: local-demo",
                'description: "Local demo skill."',
                "---",
                "",
                "# Local Demo",
            ]
        ),
        encoding="utf-8",
    )
    (trusted_skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: trusted-demo",
                'description: "Trusted demo skill."',
                "---",
                "",
                "# Trusted Demo",
            ]
        ),
        encoding="utf-8",
    )
    (adapter_dir / "find-skills-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: repo",
                "language: en",
                "output_dir: skill-outputs/find-skills",
                "trusted_skill_roots:",
                "- vendor/trusted-skills",
                "prefer_local_first: true",
                "allow_external_registry: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/find-skills/scripts/list_capabilities.py",
        "--repo-root",
        str(repo),
    )
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
                "output_dir: skill-outputs/impl",
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
