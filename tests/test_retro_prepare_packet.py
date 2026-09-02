from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from scripts.gates.validate_retro_artifact import ValidationError as RetroValidationError
from scripts.gates.validate_retro_artifact import candidate_paths as retro_candidate_paths
from scripts.gates.validate_retro_artifact import validate_retro_artifact
from skills.public.retro.scripts import prepare_packet
from skills.public.retro.scripts.resolve_adapter import load_adapter, validate_adapter_data
from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]
PREPARE = "skills/public/retro/scripts/prepare_packet.py"


def _write_yaml(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")





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
        "--slug",
        "demo",
    )

    assert result.returncode == 0, result.stderr
    receipt = yaml.safe_load(result.stdout)
    assert receipt["section_count"] == 1
    # The packet itself is always written now; the receipt only points at it.
    packet = json.loads((tmp_path / receipt["json_path"]).read_text(encoding="utf-8"))
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
    payload = yaml.safe_load(result.stdout)
    md_path = tmp_path / payload["md_path"]
    assert payload["json_path"] == "charness-artifacts/retro/demo-packet.json"
    assert md_path.is_file()
    text = md_path.read_text(encoding="utf-8")
    assert "# Retro Prepare Packet" in text
    assert "retro-body" in text


def test_retro_prepare_packet_markdown_passes_live_retro_artifact_validator(tmp_path: Path) -> None:
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
    candidates = retro_candidate_paths(
        tmp_path,
        ["charness-artifacts/retro/demo-packet.md"],
        all_artifacts=False,
    )

    assert candidates == []


def test_packet_filename_and_heading_without_kind_still_fail_retro_record_floors(tmp_path: Path) -> None:
    artifact = tmp_path / "charness-artifacts/retro/2026-07-10-demo-packet.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "\n".join(
            [
                "# Retro Prepare Packet — demo",
                "",
                "Date: 2026-07-10",
                "Mode: session",
                "",
                "## Waste",
                "",
                "- still a retro record with no packet kind line",
                "",
            ]
        ),
        encoding="utf-8",
    )

    candidates = retro_candidate_paths(
        tmp_path,
        ["charness-artifacts/retro/2026-07-10-demo-packet.md"],
        all_artifacts=False,
    )

    assert candidates == [artifact]
    try:
        validate_retro_artifact(artifact)
    except RetroValidationError as exc:
        assert "`## Persisted` must state" in str(exc)
    else:
        raise AssertionError("expected mislabeled retro record to fail validation")


def test_wrong_prepare_packet_title_with_correct_retro_kind_still_fails_record_floors(tmp_path: Path) -> None:
    artifact = tmp_path / "charness-artifacts/retro/2026-07-10-demo-packet.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "\n".join(
            [
                "# Critique Prepare Packet — demo",
                "",
                "- **Kind**: `charness.retro_prepare_packet` (v1)",
                "",
                "Date: 2026-07-10",
                "Mode: session",
                "",
                "## Waste",
                "",
                "- wrong title should not bypass retro floors",
                "",
            ]
        ),
        encoding="utf-8",
    )

    candidates = retro_candidate_paths(
        tmp_path,
        ["charness-artifacts/retro/2026-07-10-demo-packet.md"],
        all_artifacts=False,
    )

    assert candidates == [artifact]
    try:
        validate_retro_artifact(artifact)
    except RetroValidationError as exc:
        assert "`## Persisted` must state" in str(exc)
    else:
        raise AssertionError("expected wrong-title retro packet lookalike to fail validation")


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
    payload = yaml.safe_load(result.stdout)
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
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
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
    payload = yaml.safe_load(result.stdout)
    text = (tmp_path / payload["md_path"]).read_text(encoding="utf-8")
    assert ".agents/retro-adapter.yaml" in text
    assert ".agents/critique-adapter.yaml" not in text


def test_retro_prepare_packet_changed_ref_reaches_default_surface_producer(tmp_path: Path) -> None:
    from tests.quality_gates.repo_shapes import install_two_commit_repo

    producer = ROOT / "scripts/render_critique_section_changed_surfaces.py"
    install_two_commit_repo(
        tmp_path,
        {
            ".agents/surfaces.json": json.dumps(
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
            ".agents/retro-adapter.yaml": (
                "version: 1\n"
                "repo: demo\n"
                "output_dir: charness-artifacts/retro\n"
                "packet_sections:\n"
                "  - id: changed-files-and-owning-surfaces\n"
                "    title: Changed Files And Owning Surfaces\n"
                "    content_kind: script\n"
                f'    command: "python3 {producer} --repo-root ."\n'
            ),
            "README.md": "one\n",
        },
        {"README.md": "two\n"},
        first_message="initial",
        second_message="update",
    )

    result = run_script(
        PREPARE,
        "--repo-root",
        str(tmp_path),
        "--prepared-for",
        "head",
        "--changed-ref",
        "HEAD",
        "--slug",
        "changed-ref",
    )

    assert result.returncode == 0, result.stderr
    receipt = yaml.safe_load(result.stdout)
    assert receipt["changed_ref"] == "HEAD"
    packet = json.loads((tmp_path / receipt["json_path"]).read_text(encoding="utf-8"))
    assert packet["changed_ref"] == "HEAD"
    section = packet["sections"][0]["content"]
    assert "Changed paths for ref `HEAD`:" in section
    assert "README.md" in section
