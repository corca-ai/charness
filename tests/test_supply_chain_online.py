from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_script(*args: str, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def seed_js_repo(tmp_path: Path, *, package_manager: str, lockfile: str) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text(
        json.dumps(
            {
                "private": True,
                "packageManager": package_manager,
                "dependencies": {"left-pad": "1.3.0"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / lockfile).write_text("{}\n", encoding="utf-8")
    return repo


def test_check_supply_chain_online_uses_npm_audit(tmp_path: Path) -> None:
    repo = seed_js_repo(tmp_path, package_manager="npm@10.0.0", lockfile="package-lock.json")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    output_path = repo / "npm-args.txt"
    npm = bin_dir / "npm"
    npm.write_text("#!/bin/bash\nprintf '%s\\n' \"$@\" > \"$TEST_OUTPUT\"\n", encoding="utf-8")
    npm.chmod(0o755)

    env = {"PATH": f"{bin_dir}:/usr/bin:/bin", "TEST_OUTPUT": str(output_path)}
    result = run_script(
        "scripts/check_supply_chain_online.py",
        "--repo-root",
        str(repo),
        "--audit-level",
        "high",
        cwd=ROOT,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    args = output_path.read_text(encoding="utf-8").splitlines()
    assert args == ["audit", "--json", "--audit-level=high"]


def test_check_supply_chain_online_uses_pnpm_audit(tmp_path: Path) -> None:
    repo = seed_js_repo(tmp_path, package_manager="pnpm@10.0.0", lockfile="pnpm-lock.yaml")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    output_path = repo / "pnpm-args.txt"
    pnpm = bin_dir / "pnpm"
    pnpm.write_text("#!/bin/bash\nprintf '%s\\n' \"$@\" > \"$TEST_OUTPUT\"\n", encoding="utf-8")
    pnpm.chmod(0o755)

    env = {"PATH": f"{bin_dir}:/usr/bin:/bin", "TEST_OUTPUT": str(output_path)}
    result = run_script(
        "scripts/check_supply_chain_online.py",
        "--repo-root",
        str(repo),
        "--audit-level",
        "critical",
        cwd=ROOT,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    args = output_path.read_text(encoding="utf-8").splitlines()
    assert args == ["audit", "--json", "--audit-level=critical"]


def test_check_supply_chain_online_uses_uv_audit(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text(
        "\n".join(["[project]", 'name = "demo"', 'version = "0.1.0"', 'dependencies = ["requests>=2.0"]', ""]),
        encoding="utf-8",
    )
    (repo / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    bin_dir = repo / "bin"
    bin_dir.mkdir()
    output_path = repo / "uv-args.txt"
    uv = bin_dir / "uv"
    uv.write_text("#!/bin/bash\nprintf '%s\\n' \"$@\" > \"$TEST_OUTPUT\"\n", encoding="utf-8")
    uv.chmod(0o755)

    env = {"PATH": f"{bin_dir}:/usr/bin:/bin", "TEST_OUTPUT": str(output_path)}
    result = run_script(
        "scripts/check_supply_chain_online.py",
        "--repo-root",
        str(repo),
        cwd=ROOT,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    args = output_path.read_text(encoding="utf-8").splitlines()
    assert args == ["audit", "--frozen"]


def test_check_supply_chain_online_missing_binary_names_owner(tmp_path: Path) -> None:
    repo = seed_js_repo(tmp_path, package_manager="npm@10.0.0", lockfile="package-lock.json")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python3").symlink_to(Path("/usr/bin/python3"))
    env = {"PATH": str(bin_dir)}
    result = run_script(
        "scripts/check_supply_chain_online.py",
        "--repo-root",
        str(repo),
        "--triage-owner",
        "security-team",
        cwd=ROOT,
        env=env,
    )
    assert result.returncode == 1
    assert "security-team" in result.stderr
