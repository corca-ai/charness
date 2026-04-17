from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

from .support import ROOT


def _run_quality_preview(repo: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            "skills/public/quality/scripts/bootstrap_markdown_preview.py",
            "--repo-root",
            str(repo),
            *args,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def _write_fake_glow(bin_dir: Path) -> None:
    glow = bin_dir / "glow"
    glow.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import pathlib",
                "import sys",
                "if sys.argv[1:] == ['--version']:",
                "    print('glow 9.9.9-test')",
                "    raise SystemExit(0)",
                "width = sys.argv[2]",
                "path = pathlib.Path(sys.argv[3])",
                "print(f'RENDER width={width} source={path.name}')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    glow.chmod(glow.stat().st_mode | stat.S_IEXEC)


def test_quality_bootstrap_markdown_preview_scaffolds_and_executes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Hello\n\nWorld\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = _run_quality_preview(repo, "--execute", env=env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "scaffolded"
    assert payload["config_status"] == "written"
    assert payload["config_path"] == ".agents/markdown-preview.yaml"
    assert payload["include"] == ["README*.md", "docs/**/*.md"]
    assert payload["execution"]["status"] == "ran"
    preview = payload["execution"]["preview"]
    assert preview["status"] == "success"
    assert preview["target_count"] == 2
    assert (repo / ".artifacts" / "markdown-preview" / "README.w80.txt").is_file()
    assert (repo / ".artifacts" / "markdown-preview" / "docs__guide.w100.txt").is_file()


def test_quality_bootstrap_markdown_preview_preserves_existing_config(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (repo / "docs" / "markdown-preview.yaml").write_text(
        "\n".join(
            [
                "enabled: true",
                "backend: glow",
                "widths:",
                "  - 90",
                "include:",
                "  - docs/**/*.md",
                "on_change_only: false",
                "artifact_dir: .artifacts/docs-preview",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = _run_quality_preview(repo, "--execute", env=env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "existing-config"
    assert payload["config_status"] == "preserved"
    assert payload["config_path"] == "docs/markdown-preview.yaml"
    assert not (repo / ".agents" / "markdown-preview.yaml").exists()
    preview = payload["execution"]["preview"]
    assert preview["artifact_dir"] == ".artifacts/docs-preview"
    assert preview["target_count"] == 1
    assert (repo / ".artifacts" / "docs-preview" / "docs__guide.w90.txt").is_file()


def test_quality_bootstrap_markdown_preview_reports_not_applicable(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")

    result = _run_quality_preview(repo)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "not-applicable"
    assert payload["config_status"] == "not-written"
    assert payload["config_path"] is None
    assert payload["preview_command"] is None
