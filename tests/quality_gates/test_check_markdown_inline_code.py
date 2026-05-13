from __future__ import annotations

from pathlib import Path

from .support import run_script


def _run(repo: Path, *paths: str) -> tuple[int, str, str]:
    args = ["scripts/check_markdown_inline_code.py", "--repo-root", str(repo)]
    for path in paths:
        args.extend(["--path", path])
    result = run_script(*args)
    return result.returncode, result.stdout, result.stderr


def test_check_markdown_inline_code_passes_when_inline_code_is_single_line(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "doc.md").write_text(
        "# Title\n\nUse `cautilus evaluate fixture --repo-root . --adapter-name <repo-owned-adapter>` for proof.\n",
        encoding="utf-8",
    )
    code, stdout, _ = _run(repo, "doc.md")
    assert code == 0
    assert "Validated inline code spans" in stdout


def test_check_markdown_inline_code_flags_wrapped_inline_code(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "doc.md").write_text(
        "# Title\n\nUse `cautilus eval test\n--repo-root . --adapter-name <repo-owned-adapter>` for proof.\n",
        encoding="utf-8",
    )
    code, _, stderr = _run(repo, "doc.md")
    assert code == 1
    assert "doc.md:3" in stderr
    assert "wraps across line" in stderr


def test_check_markdown_inline_code_ignores_fenced_blocks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "doc.md").write_text(
        "# Title\n\n```bash\necho `not\nan inline span`\n```\n\nProse with `single line` only.\n",
        encoding="utf-8",
    )
    code, _, _ = _run(repo, "doc.md")
    assert code == 0


def test_check_markdown_inline_code_handles_adjacent_inline_codes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "doc.md").write_text(
        "Pick `option-a`, `option-b`, or `option-c` then commit.\n",
        encoding="utf-8",
    )
    code, _, _ = _run(repo, "doc.md")
    assert code == 0
