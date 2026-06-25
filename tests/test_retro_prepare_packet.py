from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from skills.public.retro.scripts import prepare_packet
from skills.public.retro.scripts.resolve_adapter import load_adapter, validate_adapter_data

ROOT = Path(__file__).resolve().parents[1]
PREPARE = "skills/public/retro/scripts/prepare_packet.py"


def _write_yaml(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def run_script(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _run_git(repo_root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo_root, check=True, capture_output=True, text=True)


def test_retro_prepare_packet_bootstrap_missing_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    class MissingBootstrapPath:
        def __init__(self, _value: object) -> None:
            pass

        def resolve(self) -> "MissingBootstrapPath":
            return self

        @property
        def parents(self) -> list[Path]:
            return []

    monkeypatch.setattr(prepare_packet, "Path", MissingBootstrapPath)

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        prepare_packet._load_skill_runtime_bootstrap()


def test_retro_adapter_accepts_packet_sections(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / ".agents/retro-adapter.yaml",
        """\
version: 1
repo: demo
packet_sections:
  - id: context
    title: Context
    content_kind: static
    content:
      - first
      - second
""",
    )

    adapter = load_adapter(tmp_path)

    assert adapter["valid"] is True
    assert adapter["data"]["packet_sections"][0]["content"] == "first\nsecond"
    assert adapter["field_state"]["packet_sections"] == "configured"


def test_retro_adapter_rejects_invalid_packet_sections() -> None:
    _, errors, _ = validate_adapter_data(
        {
            "version": 1,
            "packet_sections": [
                {
                    "id": "bad",
                    "title": "Bad",
                    "content_kind": "script",
                    "content": "wrong field",
                }
            ],
        },
        Path("."),
    )

    assert any("content_kind=script requires `command`" in error for error in errors)


def test_retro_prepare_packet_emits_retro_kind_and_sections(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / ".agents/retro-adapter.yaml",
        """\
version: 1
repo: demo
output_dir: charness-artifacts/retro
packet_sections:
  - id: static-context
    title: Static Context
    content_kind: static
    content: retro-body
""",
    )

    result = run_script(
        PREPARE,
        "--repo-root",
        str(tmp_path),
        "--prepared-for",
        "unit",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    packet = json.loads(result.stdout)
    assert packet["kind"] == "charness.retro_prepare_packet"
    assert packet["section_count"] == 1
    assert packet["sections"][0]["content"] == "retro-body"
    assert "reviewer_tier_evidence" not in packet


def test_retro_prepare_packet_writes_markdown(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / ".agents/retro-adapter.yaml",
        """\
version: 1
repo: demo
output_dir: charness-artifacts/retro
packet_sections:
  - id: static-context
    title: Static Context
    content_kind: static
    content: retro-body
""",
    )

    result = run_script(
        PREPARE,
        "--repo-root",
        str(tmp_path),
        "--prepared-for",
        "unit",
        "--slug",
        "demo",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    md_path = tmp_path / payload["md_path"]
    assert payload["json_path"] == "charness-artifacts/retro/demo-packet.json"
    assert md_path.is_file()
    text = md_path.read_text(encoding="utf-8")
    assert "# Retro Prepare Packet" in text
    assert "retro-body" in text


def test_retro_prepare_packet_uses_default_slug_when_none_given(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / ".agents/retro-adapter.yaml",
        """\
version: 1
repo: demo
output_dir: charness-artifacts/retro
""",
    )

    result = run_script(
        PREPARE,
        "--repo-root",
        str(tmp_path),
        "--prepared-for",
        "unit",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["md_path"].startswith("charness-artifacts/retro/20")
    assert payload["md_path"].endswith("-packet.md")


def test_retro_prepare_packet_rejects_multiple_changed_refs(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / ".agents/retro-adapter.yaml",
        """\
version: 1
repo: demo
output_dir: charness-artifacts/retro
""",
    )

    result = run_script(
        PREPARE,
        "--repo-root",
        str(tmp_path),
        "--changed-ref",
        "HEAD",
        "--commit",
        "HEAD~1",
        "--json",
    )

    assert result.returncode == 2
    assert "use only one of --changed-ref, --commit, or --range" in result.stderr


def test_retro_prepare_packet_reports_invalid_adapter(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / ".agents/retro-adapter.yaml",
        """\
version: 1
repo: demo
output_dir: charness-artifacts/retro
packet_sections:
  - id: bad
    title: Bad
    content_kind: script
    content: wrong
""",
    )

    result = run_script(
        PREPARE,
        "--repo-root",
        str(tmp_path),
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["error"] == "retro adapter invalid"


def test_retro_prepare_packet_empty_markdown_names_retro_adapter(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path / ".agents/retro-adapter.yaml",
        """\
version: 1
repo: demo
output_dir: charness-artifacts/retro
""",
    )

    result = run_script(
        PREPARE,
        "--repo-root",
        str(tmp_path),
        "--prepared-for",
        "unit",
        "--slug",
        "demo-empty",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    text = (tmp_path / payload["md_path"]).read_text(encoding="utf-8")
    assert ".agents/retro-adapter.yaml" in text
    assert ".agents/critique-adapter.yaml" not in text


def test_retro_prepare_packet_changed_ref_reaches_default_surface_producer(tmp_path: Path) -> None:
    _run_git(tmp_path, "init")
    _run_git(tmp_path, "config", "user.email", "test@example.com")
    _run_git(tmp_path, "config", "user.name", "Test User")
    agents_dir = tmp_path / ".agents"
    agents_dir.mkdir()
    (agents_dir / "surfaces.json").write_text(
        json.dumps(
            {
                "version": 1,
                "surfaces": [
                    {
                        "surface_id": "repo-markdown",
                        "description": "Markdown",
                        "source_paths": ["README.md"],
                        "derived_paths": [],
                        "sync_commands": [],
                        "verify_commands": ["check docs"],
                        "notes": [],
                        "generated_markdown": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    producer = ROOT / "scripts/render_critique_section_changed_surfaces.py"
    _write_yaml(
        tmp_path / ".agents/retro-adapter.yaml",
        f"""\
version: 1
repo: demo
output_dir: charness-artifacts/retro
packet_sections:
  - id: changed-files-and-owning-surfaces
    title: Changed Files And Owning Surfaces
    content_kind: script
    command: "python3 {producer} --repo-root ."
""",
    )
    (tmp_path / "README.md").write_text("one\n", encoding="utf-8")
    _run_git(tmp_path, "add", ".")
    _run_git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "README.md").write_text("two\n", encoding="utf-8")
    _run_git(tmp_path, "commit", "-am", "update")

    result = run_script(
        PREPARE,
        "--repo-root",
        str(tmp_path),
        "--prepared-for",
        "head",
        "--changed-ref",
        "HEAD",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    packet = json.loads(result.stdout)
    assert packet["changed_ref"] == "HEAD"
    section = packet["sections"][0]["content"]
    assert "Changed paths for ref `HEAD`:" in section
    assert "README.md" in section
