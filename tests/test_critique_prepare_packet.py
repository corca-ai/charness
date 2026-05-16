from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.critique_adapter_lib import (  # noqa: E402
    adapter_has_sections,
    load_adapter,
    validate_adapter_data,
)
from scripts.critique_packet_lib import (  # noqa: E402
    PACKET_KIND,
    PACKET_VERSION,
    build_packet,
    execute_section,
    render_markdown,
    write_packet,
)
from scripts.surfaces_lib import collect_changed_paths_for_ref  # noqa: E402
from scripts.validate_critique_packet import validate_packet  # noqa: E402


def _write_yaml(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def test_load_adapter_missing_returns_inferred_defaults(tmp_path: Path) -> None:
    adapter = load_adapter(tmp_path)
    assert adapter["found"] is False
    assert adapter["valid"] is True
    assert adapter["data"]["packet_sections"] == []
    assert adapter_has_sections(adapter) is False


def test_load_adapter_with_sections_signals_opt_in(tmp_path: Path) -> None:
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", """\
version: 1
repo: testrepo
packet_sections:
  - id: non-goals
    title: Non-Goals
    content_kind: static
    content:
      - first
      - second
""")
    adapter = load_adapter(tmp_path)
    assert adapter["found"] is True
    assert adapter["valid"] is True
    assert adapter_has_sections(adapter) is True
    sections = adapter["data"]["packet_sections"]
    assert len(sections) == 1
    assert sections[0]["id"] == "non-goals"
    assert sections[0]["content_kind"] == "static"
    # list-of-strings content is joined with newlines
    assert "first\nsecond" in sections[0]["content"]


def test_validate_adapter_rejects_dual_content_fields() -> None:
    raw = {
        "version": 1,
        "packet_sections": [{
            "id": "bad", "title": "Bad", "content_kind": "static",
            "content": "x", "content_path": "y",
        }],
    }
    _, errors, _ = validate_adapter_data(raw, Path("."))
    assert any("exactly one of" in err for err in errors)


def test_validate_adapter_rejects_kind_field_mismatch() -> None:
    raw = {
        "version": 1,
        "packet_sections": [{
            "id": "bad", "title": "Bad", "content_kind": "script",
            "content": "x",
        }],
    }
    _, errors, _ = validate_adapter_data(raw, Path("."))
    assert any("content_kind=script requires `command`" in err for err in errors)


def test_validate_adapter_rejects_duplicate_section_ids() -> None:
    raw = {
        "version": 1,
        "packet_sections": [
            {"id": "dup", "title": "A", "content_kind": "static", "content": "x"},
            {"id": "dup", "title": "B", "content_kind": "static", "content": "y"},
        ],
    }
    _, errors, _ = validate_adapter_data(raw, Path("."))
    assert any("duplicates earlier section" in err for err in errors)


def test_execute_static_inline_section(tmp_path: Path) -> None:
    section = {"id": "x", "title": "X", "content_kind": "static", "content": "hello"}
    result = execute_section(section, repo_root=tmp_path)
    assert result["ok"] is True
    assert result["content"] == "hello"
    assert result["errors"] == []


def test_execute_static_path_section(tmp_path: Path) -> None:
    target = tmp_path / "doc.md"
    target.write_text("body line\n", encoding="utf-8")
    section = {"id": "x", "title": "X", "content_kind": "static", "content_path": "doc.md"}
    result = execute_section(section, repo_root=tmp_path)
    assert result["ok"] is True
    assert "body line" in result["content"]


def test_execute_static_path_outside_repo_fails(tmp_path: Path) -> None:
    section = {"id": "x", "title": "X", "content_kind": "static",
               "content_path": "../escape.md"}
    result = execute_section(section, repo_root=tmp_path)
    assert result["ok"] is False
    assert any("outside repo root" in err for err in result["errors"])


def test_execute_script_section_success(tmp_path: Path) -> None:
    section = {"id": "x", "title": "X", "content_kind": "script",
               "command": "echo packet-section-output"}
    result = execute_section(section, repo_root=tmp_path)
    assert result["ok"] is True
    assert "packet-section-output" in result["content"]


def test_execute_script_section_failure_propagates_errors(tmp_path: Path) -> None:
    section = {"id": "x", "title": "X", "content_kind": "script",
               "command": "false"}
    result = execute_section(section, repo_root=tmp_path)
    assert result["ok"] is False
    assert any("exit code" in err for err in result["errors"])


def test_build_packet_envelope_shape(tmp_path: Path) -> None:
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", """\
version: 1
repo: rt
packet_sections:
  - id: a
    title: A
    content_kind: static
    content: A-body
  - id: b
    title: B
    content_kind: script
    command: "echo B-body"
""")
    adapter = load_adapter(tmp_path)
    packet = build_packet(adapter=adapter, repo_root=tmp_path,
                          prepared_for="unit test")
    assert packet["kind"] == PACKET_KIND
    assert packet["version"] == PACKET_VERSION
    assert packet["section_count"] == 2
    assert packet["ok"] is True
    assert [s["id"] for s in packet["sections"]] == ["a", "b"]
    assert validate_packet(packet) == []


def test_build_packet_passes_changed_ref_to_script_sections(tmp_path: Path) -> None:
    helper = tmp_path / "emit_ref.py"
    helper.write_text(
        "import os\nprint(os.environ.get('CHARNESS_CRITIQUE_CHANGED_REF', 'missing'))\n",
        encoding="utf-8",
    )
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", f"""\
version: 1
repo: rt
packet_sections:
  - id: ref
    title: Ref
    content_kind: script
    command: "python3 {helper.name}"
""")
    adapter = load_adapter(tmp_path)
    packet = build_packet(
        adapter=adapter,
        repo_root=tmp_path,
        prepared_for="commit review",
        changed_ref="HEAD^..HEAD",
    )

    assert packet["ok"] is True
    assert packet["sections"][0]["content"].strip() == "HEAD^..HEAD"


def test_collect_changed_paths_for_ref_reads_committed_diff(tmp_path: Path) -> None:
    _run_git(tmp_path, "init")
    _run_git(tmp_path, "config", "user.email", "test@example.com")
    _run_git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / "README.md").write_text("one\n", encoding="utf-8")
    _run_git(tmp_path, "add", "README.md")
    _run_git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "README.md").write_text("two\n", encoding="utf-8")
    _run_git(tmp_path, "commit", "-am", "update")

    assert collect_changed_paths_for_ref(tmp_path, "HEAD^..HEAD") == ["README.md"]
    assert collect_changed_paths_for_ref(tmp_path, "HEAD") == ["README.md"]


def test_build_packet_one_failed_section_marks_envelope_not_ok(tmp_path: Path) -> None:
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", """\
version: 1
repo: rt
packet_sections:
  - id: ok-section
    title: OK
    content_kind: static
    content: ok-body
  - id: failing-section
    title: Failing
    content_kind: script
    command: "false"
""")
    adapter = load_adapter(tmp_path)
    packet = build_packet(adapter=adapter, repo_root=tmp_path, prepared_for="unit")
    assert packet["ok"] is False
    assert packet["sections"][0]["ok"] is True
    assert packet["sections"][1]["ok"] is False
    assert validate_packet(packet) == []


def test_validate_packet_catches_kind_drift() -> None:
    payload = {
        "kind": "wrong.kind",
        "version": 1,
        "repo": "x",
        "generated_at": "2026-05-14T00:00:00Z",
        "prepared_for": "x",
        "adapter_path": None,
        "sections": [],
        "section_count": 0,
        "ok": True,
    }
    errors = validate_packet(payload)
    assert any("kind must be" in err for err in errors)


def test_validate_packet_catches_section_count_mismatch() -> None:
    payload = {
        "kind": PACKET_KIND,
        "version": 1,
        "repo": "x",
        "generated_at": "now",
        "prepared_for": "x",
        "adapter_path": None,
        "sections": [{
            "id": "s", "title": "S", "content_kind": "static",
            "producer": "p", "content": "c", "ok": True, "errors": [],
        }],
        "section_count": 99,
        "ok": True,
    }
    errors = validate_packet(payload)
    assert any("section_count must equal" in err for err in errors)


def test_validate_packet_catches_ok_lying_about_section_states() -> None:
    payload = {
        "kind": PACKET_KIND,
        "version": 1,
        "repo": "x",
        "generated_at": "now",
        "prepared_for": "x",
        "adapter_path": None,
        "sections": [{
            "id": "s", "title": "S", "content_kind": "static",
            "producer": "p", "content": "", "ok": False, "errors": ["boom"],
        }],
        "section_count": 1,
        "ok": True,
    }
    errors = validate_packet(payload)
    assert any("ok must equal all-sections-ok" in err for err in errors)


def test_render_markdown_includes_each_section(tmp_path: Path) -> None:
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", """\
version: 1
repo: rt
packet_sections:
  - id: alpha
    title: Alpha Section
    content_kind: static
    content: alpha-body
""")
    adapter = load_adapter(tmp_path)
    packet = build_packet(adapter=adapter, repo_root=tmp_path, prepared_for="unit")
    md = render_markdown(packet)
    assert "Alpha Section" in md
    assert "alpha-body" in md
    assert "Critique Prepare Packet" in md


def test_write_packet_emits_both_artifacts(tmp_path: Path) -> None:
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", """\
version: 1
repo: rt
packet_sections:
  - id: only
    title: Only
    content_kind: static
    content: body
""")
    adapter = load_adapter(tmp_path)
    packet = build_packet(adapter=adapter, repo_root=tmp_path, prepared_for="unit")
    out = tmp_path / "out"
    json_path, md_path = write_packet(packet, output_dir=out, slug="test")
    assert json_path.is_file() and md_path.is_file()
    parsed = json.loads(json_path.read_text(encoding="utf-8"))
    assert parsed["section_count"] == 1
    assert "Only" in md_path.read_text(encoding="utf-8")


def test_runner_cli_dogfood_smoke(tmp_path: Path) -> None:
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", """\
version: 1
repo: rt
packet_sections:
  - id: smoke
    title: Smoke
    content_kind: static
    content: smoke-body
""")
    runner = REPO_ROOT / "skills/public/critique/scripts/prepare_packet.py"
    result = subprocess.run(
        ["python3", str(runner), "--repo-root", str(tmp_path),
         "--prepared-for", "smoke", "--slug", "smoke"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["section_count"] == 1
    artifact = tmp_path / "charness-artifacts/critique/smoke-packet.json"
    assert artifact.is_file()
