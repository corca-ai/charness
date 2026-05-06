from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_helper(repo_root: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "skills/support/markdown-preview/scripts/render_markdown_preview.py",
            "--repo-root",
            str(repo_root),
            *args,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def _isolated_path() -> str:
    return str(Path(sys.executable).resolve().parent)


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


def _write_blank_fake_glow(bin_dir: Path) -> None:
    glow = bin_dir / "glow"
    glow.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "if sys.argv[1:] == ['--version']:",
                "    print('glow 9.9.9-test')",
                "    raise SystemExit(0)",
                "raise SystemExit(0)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    glow.chmod(glow.stat().st_mode | stat.S_IEXEC)


def _write_pipe_blank_file_output_fake_glow(bin_dir: Path) -> None:
    glow = bin_dir / "glow"
    glow.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import os",
                "import pathlib",
                "import sys",
                "if sys.argv[1:] == ['--version']:",
                "    print('glow 9.9.9-test')",
                "    raise SystemExit(0)",
                "fd1 = os.readlink('/proc/self/fd/1')",
                "if fd1.startswith('pipe:'):",
                "    raise SystemExit(0)",
                "width = sys.argv[2]",
                "path = pathlib.Path(sys.argv[3])",
                "print(f'RENDER-FILE width={width} source={path.name}')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    glow.chmod(glow.stat().st_mode | stat.S_IEXEC)


def test_markdown_preview_renders_artifacts_with_glow(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Hello\n\nWorld\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    result = run_helper(repo, "--file", "README.md", "--width", "80", "--width", "100", env=env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["backend_available"] is True
    assert payload["backend_status"] == "healthy"
    assert payload["backend_version"] is not None
    artifacts = {item["artifact_path"] for item in payload["previews"]}
    assert artifacts == {
        ".artifacts/markdown-preview/README.w80.txt",
        ".artifacts/markdown-preview/README.w100.txt",
    }
    assert (repo / ".artifacts/markdown-preview/README.w80.txt").read_text(encoding="utf-8").strip() == "RENDER width=80 source=README.md"
    assert payload["previews"][0]["source_sha256"]


def test_markdown_preview_writes_degraded_artifact_without_glow(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Title\n\nParagraph\n", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = _isolated_path()

    result = run_helper(repo, "--file", "README.md", "--width", "90", env=env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "degraded"
    assert payload["backend_status"] == "missing"
    artifact_path = repo / ".artifacts/markdown-preview/README.w90.txt"
    artifact_text = artifact_path.read_text(encoding="utf-8")
    assert "MARKDOWN PREVIEW DEGRADED" in artifact_text
    assert "glow not found on PATH" in artifact_text


def test_markdown_preview_marks_blank_glow_output_as_backend_error(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Title\n\nParagraph\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_blank_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    result = run_helper(repo, "--file", "README.md", "--width", "90", env=env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "backend-error"
    assert payload["backend_available"] is True
    assert payload["backend_status"] == "backend-error"
    preview = payload["previews"][0]
    assert preview["status"] == "backend-error"
    assert "blank output" in preview["reason"]
    artifact_text = (repo / ".artifacts/markdown-preview/README.w90.txt").read_text(encoding="utf-8")
    assert "MARKDOWN PREVIEW BACKEND ERROR" in artifact_text
    assert "It is not equivalent to a rendered readability review." in artifact_text


def test_markdown_preview_retries_glow_with_file_stdout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Title\n\nParagraph\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_pipe_blank_file_output_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    result = run_helper(repo, "--file", "README.md", "--width", "90", env=env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["previews"][0]["status"] == "rendered"
    assert (repo / ".artifacts/markdown-preview/README.w90.txt").read_text(encoding="utf-8").strip() == "RENDER-FILE width=90 source=README.md"


def test_markdown_preview_glow_backend_check_exit_codes(tmp_path: Path) -> None:
    script = ROOT / "skills" / "support" / "markdown-preview" / "scripts" / "check_glow_backend.py"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    ok = subprocess.run([sys.executable, str(script)], cwd=ROOT, check=False, capture_output=True, text=True, env=env)

    assert ok.returncode == 0
    assert json.loads(ok.stdout)["status"] == "healthy"

    _write_blank_fake_glow(fake_bin)
    bad = subprocess.run([sys.executable, str(script)], cwd=ROOT, check=False, capture_output=True, text=True, env=env)

    assert bad.returncode == 1
    assert json.loads(bad.stdout)["status"] == "backend-error"


def test_markdown_preview_uses_yaml_config_and_changed_only_scope(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".agents").mkdir()
    (repo / "docs").mkdir()
    (repo / "README.md").write_text("# Root\n", encoding="utf-8")
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=repo, check=True, capture_output=True, text=True)
    (repo / "docs" / "guide.md").write_text("# Guide\n\nChanged\n", encoding="utf-8")
    (repo / ".agents" / "markdown-preview.yaml").write_text(
        "\n".join(
            [
                "enabled: true",
                "backend: glow",
                "widths:",
                "  - 90",
                "include:",
                "  - README.md",
                "  - docs/**/*.md",
                "on_change_only: true",
                "artifact_dir: .artifacts/custom-preview",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    result = run_helper(repo, env=env)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["config_path"] == ".agents/markdown-preview.yaml"
    assert payload["artifact_dir"] == ".artifacts/custom-preview"
    assert payload["target_count"] == 1
    assert payload["previews"][0]["source_path"] == "docs/guide.md"
    assert not (repo / ".artifacts/custom-preview/README.w90.txt").exists()
    assert payload["git_head"] is not None


def test_markdown_preview_rejects_unsupported_backend(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Hello\n", encoding="utf-8")

    result = run_helper(repo, "--file", "README.md", "--backend", "pandoc")

    assert result.returncode != 0
    assert "Unsupported markdown preview backend `pandoc`" in result.stderr
