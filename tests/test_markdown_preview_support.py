from __future__ import annotations

import importlib.util
import os
import stat
import subprocess
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
RENDER_SCRIPT = "skills/support/markdown-preview/scripts/render_markdown_preview.py"


def _load_render_markdown_preview():
    spec = importlib.util.spec_from_file_location(
        "render_markdown_preview",
        ROOT / RENDER_SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RENDER_MARKDOWN_PREVIEW = _load_render_markdown_preview()


def _load_check_glow_backend():
    spec = importlib.util.spec_from_file_location(
        "check_glow_backend",
        ROOT / "skills" / "support" / "markdown-preview" / "scripts" / "check_glow_backend.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_helper_in_process(
    monkeypatch,
    capsys,
    repo_root: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> SimpleNamespace:
    if env is not None:
        for key, value in env.items():
            monkeypatch.setenv(key, value)
    monkeypatch.setattr(
        sys,
        "argv",
        [RENDER_SCRIPT, "--repo-root", str(repo_root), *args],
    )
    try:
        code = RENDER_MARKDOWN_PREVIEW.main()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        if exc.code and not isinstance(exc.code, int):
            print(str(exc.code), file=sys.stderr)
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def test_markdown_preview_parse_args_help_includes_argument_help(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", [RENDER_SCRIPT, "--help"])

    with pytest.raises(SystemExit) as excinfo:
        RENDER_MARKDOWN_PREVIEW.parse_args()

    out = capsys.readouterr().out
    normalized = " ".join(out.split())
    assert excinfo.value.code == 0
    expected = {
        "--repo-root": ["Repository root", "resolve paths"],
        "--config": ["markdown preview config"],
        "--file": ["Markdown file or glob", "Repeatable"],
        "--width": ["Preview width", "Repeatable"],
        "--artifact-dir": ["Repo-relative directory", "generated preview artifacts"],
        "--backend": ["markdown preview backend", "Supported:", "glow"],
        "--changed-only": ["selected Markdown targets", "files changed in", "git"],
    }
    for option, snippets in expected.items():
        assert option in out
        for snippet in snippets:
            assert snippet in normalized


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


def _write_slow_fake_glow(bin_dir: Path) -> None:
    glow = bin_dir / "glow"
    glow.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "import time",
                "if sys.argv[1:] == ['--version']:",
                "    print('glow 9.9.9-test')",
                "    raise SystemExit(0)",
                "time.sleep(2)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    glow.chmod(glow.stat().st_mode | stat.S_IEXEC)


def _write_fake_script(bin_dir: Path, *, compatible: bool) -> None:
    script = bin_dir / "script"
    body = [
        "#!/usr/bin/env python3",
        "import shlex",
        "import subprocess",
        "import sys",
        "if not sys.argv[1:] or sys.argv[1] != '-qec':",
        "    raise SystemExit(64)",
        "if not %r:" % compatible,
        "    print('unsupported script flags', file=sys.stderr)",
        "    raise SystemExit(64)",
        "completed = subprocess.run(shlex.split(sys.argv[2]), check=False, text=True)",
        "raise SystemExit(completed.returncode)",
    ]
    script.write_text("\n".join(body) + "\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)


def test_markdown_preview_renders_artifacts_with_glow(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Hello\n\nWorld\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    result = run_helper_in_process(
        monkeypatch,
        capsys,
        repo,
        "--file",
        "README.md",
        "--width",
        "80",
        "--width",
        "100",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
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


def test_markdown_preview_uses_compatible_script_pty_path(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Hello\n\nWorld\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_glow(fake_bin)
    _write_fake_script(fake_bin, compatible=True)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    result = run_helper_in_process(
        monkeypatch, capsys, repo, "--file", "README.md", "--width", "80", env=env
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "success"
    assert payload["previews"][0]["status"] == "rendered"


def test_markdown_preview_falls_back_when_script_flags_are_unsupported(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Hello\n\nWorld\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_glow(fake_bin)
    _write_fake_script(fake_bin, compatible=False)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    result = run_helper_in_process(
        monkeypatch, capsys, repo, "--file", "README.md", "--width", "80", env=env
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "success"
    assert payload["previews"][0]["status"] == "rendered"


def test_markdown_preview_direct_fallback_handles_script_race(
    tmp_path: Path, monkeypatch
) -> None:
    render = RENDER_MARKDOWN_PREVIEW._RENDER
    source = tmp_path / "README.md"
    source.write_text("# Hello\n", encoding="utf-8")
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if command[0] == "/fake/script":
            raise FileNotFoundError(command[0])
        return subprocess.CompletedProcess(command, 0, "DIRECT RENDER\n", "")

    monkeypatch.setattr(render.sys, "stdout", SimpleNamespace(isatty=lambda: False))
    monkeypatch.setattr(render.shutil, "which", lambda name: "/fake/script" if name == "script" else None)
    monkeypatch.setattr(render.subprocess, "run", fake_run)

    rendered, error = render._render_with_glow(source, 80)

    assert rendered == "DIRECT RENDER\n"
    assert error is None
    assert calls[0][0] == "/fake/script"
    assert calls[1] == ["glow", "-w", "80", str(source)]


def test_markdown_preview_direct_path_handles_missing_script(tmp_path: Path, monkeypatch) -> None:
    render = RENDER_MARKDOWN_PREVIEW._RENDER
    source = tmp_path / "README.md"
    source.write_text("# Hello\n", encoding="utf-8")
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "DIRECT RENDER\n", "")

    monkeypatch.setattr(render.sys, "stdout", SimpleNamespace(isatty=lambda: False))
    monkeypatch.setattr(render.shutil, "which", lambda name: None)
    monkeypatch.setattr(render.subprocess, "run", fake_run)

    rendered, error = render._render_with_glow(source, 80)

    assert rendered == "DIRECT RENDER\n"
    assert error is None
    assert calls == [["glow", "-w", "80", str(source)]]


def test_markdown_preview_writes_degraded_artifact_without_glow(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Title\n\nParagraph\n", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = _isolated_path()

    result = run_helper_in_process(monkeypatch, capsys, repo, "--file", "README.md", "--width", "90", env=env)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "degraded"
    assert payload["backend_status"] == "missing"
    artifact_path = repo / ".artifacts/markdown-preview/README.w90.txt"
    artifact_text = artifact_path.read_text(encoding="utf-8")
    assert "MARKDOWN PREVIEW DEGRADED" in artifact_text
    assert "glow not found on PATH" in artifact_text


def test_markdown_preview_marks_blank_glow_output_as_backend_error(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Title\n\nParagraph\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_blank_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    result = run_helper_in_process(monkeypatch, capsys, repo, "--file", "README.md", "--width", "90", env=env)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "backend-error"
    assert payload["backend_available"] is True
    assert payload["backend_status"] == "backend-error"
    preview = payload["previews"][0]
    assert preview["status"] == "backend-error"
    assert "blank output" in preview["reason"]
    artifact_text = (repo / ".artifacts/markdown-preview/README.w90.txt").read_text(encoding="utf-8")
    assert "MARKDOWN PREVIEW BACKEND ERROR" in artifact_text
    assert "It is not equivalent to a rendered readability review." in artifact_text


def test_markdown_preview_retries_glow_with_file_stdout(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Title\n\nParagraph\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_pipe_blank_file_output_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"

    result = run_helper_in_process(monkeypatch, capsys, repo, "--file", "README.md", "--width", "90", env=env)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "success"
    assert payload["previews"][0]["status"] == "rendered"
    assert (repo / ".artifacts/markdown-preview/README.w90.txt").read_text(encoding="utf-8").strip() == "RENDER-FILE width=90 source=README.md"


def test_markdown_preview_marks_slow_glow_as_backend_error(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Title\n\nParagraph\n", encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_slow_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"
    env["CHARNESS_MARKDOWN_PREVIEW_TIMEOUT_SECONDS"] = "0.1"

    result = run_helper_in_process(monkeypatch, capsys, repo, "--file", "README.md", "--width", "90", env=env)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "backend-error"
    assert payload["backend_status"] == "backend-error"
    assert "timed out after 0.1s" in payload["previews"][0]["reason"]
    artifact_text = (repo / ".artifacts/markdown-preview/README.w90.txt").read_text(encoding="utf-8")
    assert "MARKDOWN PREVIEW BACKEND ERROR" in artifact_text
    assert "timed out after 0.1s" in artifact_text


def test_markdown_preview_glow_backend_check_exit_codes(tmp_path: Path, monkeypatch, capsys) -> None:
    mod = _load_check_glow_backend()
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_fake_glow(fake_bin)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{_isolated_path()}"
    monkeypatch.setenv("PATH", env["PATH"])

    assert mod.main() == 0
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "healthy"

    _write_blank_fake_glow(fake_bin)

    assert mod.main() == 1
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "backend-error"

    _write_slow_fake_glow(fake_bin)
    monkeypatch.setenv("CHARNESS_MARKDOWN_PREVIEW_TIMEOUT_SECONDS", "0.1")

    assert mod.main() == 1
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "backend-error"


# --- #260 score-path survivors in check_glow_backend -------------------------
#
# The exit-code test above is whitespace/encoding-insensitive
# (json.loads) and only ever sees "healthy"/"backend-error" statuses, so the
# ensure_ascii / indent / comparison-operator mutants in main() and the `or`
# branch in _load_render_module survive. These in-process tests pin them by
# controlling the payload and inspecting the literal output.


def test_glow_check_load_render_module_raises_when_loader_missing(monkeypatch) -> None:
    # _load_render_module fails closed when the import spec has no loader: with a
    # non-None spec whose `.loader` is None, `spec is None or spec.loader is None`
    # raises ImportError, while the `and` mutant would not. Also covers line 14.
    mod = _load_check_glow_backend()
    monkeypatch.setattr(
        importlib.util,
        "spec_from_file_location",
        lambda *a, **k: types.SimpleNamespace(loader=None),
    )
    with pytest.raises(ImportError):
        mod._load_render_module()


def test_glow_check_main_healthy_emits_raw_unicode_with_two_space_indent(
    monkeypatch, capsys
) -> None:
    # Pins main()'s emit_yaml(payload) and the `== "healthy"` exit decision for a
    # HEALTHY payload. The status is a non-interned "healthy" so the `is` mutant
    # returns 1 (wrong); the non-ASCII note keeps the raw char only under the
    # renderer's allow_unicode.
    #
    # The old third assertion pinned json.dumps' `indent=2` via '\n  "status"'.
    # That premise died with the renderer: there is no indent argument to mutate.
    # Its surviving purpose -- the whole payload reaches stdout as one parseable
    # document, not a truncated or reformatted subset -- is pinned by the
    # round-trip equality below, which also kills an "emit only status" mutant.
    mod = _load_check_glow_backend()
    payload = {"status": "healthy ".strip(), "note": "café"}
    monkeypatch.setattr(
        mod,
        "_load_render_module",
        lambda: types.SimpleNamespace(check_backend=lambda backend: payload),
    )

    rc = mod.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert "café" in out
    assert yaml.safe_load(out) == payload


def test_glow_check_main_unhealthy_status_returns_one(monkeypatch, capsys) -> None:
    # An "unhealthy" status (lexicographically > "healthy") must exit 1. Kills the
    # `==`->`>=` mutant: "unhealthy" >= "healthy" is True and would wrongly exit 0.
    mod = _load_check_glow_backend()
    monkeypatch.setattr(
        mod,
        "_load_render_module",
        lambda: types.SimpleNamespace(check_backend=lambda backend: {"status": "unhealthy"}),
    )

    assert mod.main() == 1


def test_markdown_preview_uses_yaml_config_and_changed_only_scope(tmp_path: Path, monkeypatch, capsys) -> None:
    from tests.quality_gates.repo_shapes import install_committed_repo

    repo = install_committed_repo(
        tmp_path / "repo",
        {"README.md": "# Root\n", "docs/guide.md": "# Guide\n"},
    )
    (repo / "docs" / "guide.md").write_text("# Guide\n\nChanged\n", encoding="utf-8")
    (repo / ".agents").mkdir()
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

    result = run_helper_in_process(monkeypatch, capsys, repo, env=env)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["config_path"] == ".agents/markdown-preview.yaml"
    assert payload["artifact_dir"] == ".artifacts/custom-preview"
    assert payload["target_count"] == 1
    assert payload["previews"][0]["source_path"] == "docs/guide.md"
    assert not (repo / ".artifacts/custom-preview/README.w90.txt").exists()
    assert payload["git_head"] is not None


def test_markdown_preview_rejects_unsupported_backend(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Hello\n", encoding="utf-8")

    result = run_helper_in_process(
        monkeypatch,
        capsys,
        repo,
        "--file",
        "README.md",
        "--backend",
        "pandoc",
    )

    assert result.returncode != 0
    assert "Unsupported markdown preview backend `pandoc`" in result.stderr


def test_markdown_preview_rejects_absolute_path_outside_repo_root(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")

    result = run_helper_in_process(monkeypatch, capsys, repo, "--file", str(outside))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "no-targets"
    assert payload["target_count"] == 0
    assert any("Skipping absolute path outside repo root" in warning for warning in payload["warnings"])


def test_markdown_preview_expands_absolute_and_relative_paths_and_warns_on_missing_matches(
    tmp_path: Path,
) -> None:
    lib = RENDER_MARKDOWN_PREVIEW._LIB
    repo = tmp_path / "repo"
    repo.mkdir()
    docs = repo / "docs"
    docs.mkdir()
    readme = repo / "README.md"
    readme.write_text("# Root\n", encoding="utf-8")
    (docs / "guide.md").write_text("# Guide\n", encoding="utf-8")

    absolute_matches, absolute_warnings = lib._expand_pattern(repo, str(readme.resolve()))
    glob_matches, glob_warnings = lib._expand_pattern(repo, "*")
    relative_matches, relative_warnings = lib._expand_pattern(repo, "docs")
    config = lib.PreviewConfig(
        enabled=True,
        backend="glow",
        widths=[100],
        include=["missing.md"],
        on_change_only=False,
        artifact_dir=".artifacts/markdown-preview",
        config_path=None,
    )
    selected, warnings = lib.select_targets(repo, config)

    assert absolute_matches == [readme.resolve()]
    assert absolute_warnings == []
    assert readme in glob_matches
    assert docs not in glob_matches
    assert glob_warnings == []
    assert relative_matches == []
    assert relative_warnings == []
    assert selected == []
    assert warnings == ["No Markdown files matched `missing.md`."]


def test_markdown_preview_rejects_repo_relative_symlink_outside_repo_root(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    outside_target = outside_root / "outside.md"
    outside_target.write_text("# Outside\n", encoding="utf-8")
    (repo / "outside-link.md").symlink_to(outside_target)

    result = run_helper_in_process(monkeypatch, capsys, repo, "--file", "outside-link.md")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "no-targets"
    assert payload["target_count"] == 0
    assert any("Skipping path outside repo root" in warning for warning in payload["warnings"])


def test_markdown_preview_keeps_safe_glob_matches_when_skipping_outside_symlink(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Inside\n", encoding="utf-8")
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    (repo / "outside-link.md").symlink_to(outside)

    result = run_helper_in_process(monkeypatch, capsys, repo, "--file", "*.md")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["target_count"] == 1
    assert payload["previews"][0]["source_path"] == "README.md"
    assert any("Skipping path outside repo root" in warning for warning in payload["warnings"])
