from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest

from scripts.critique_adapter_lib import (
    adapter_has_sections,
    load_adapter,
    validate_adapter_data,
)
from scripts.critique_packet_lib import (
    PACKET_KIND,
    PACKET_VERSION,
    build_packet,
    build_reviewed_input_identity,
    execute_section,
    render_markdown,
    write_packet,
)
from scripts.prepare_packet_markdown_kind import prepare_packet_markdown_kind
from scripts.reviewed_input_identity import verify_reviewed_input_identity
from scripts.surfaces_lib import collect_changed_paths_for_ref
from scripts.validate_critique_artifacts import (
    CRITIQUE_PREPARE_PACKET_TITLE_RE,
    validate_critique_artifact,
    validate_reviewed_input_binding,
)
from scripts.validate_critique_artifacts import (
    ValidationError as CritiqueValidationError,
)
from scripts.validate_critique_artifacts import (
    candidate_paths as critique_candidate_paths,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


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
    assert packet["changed_ref"] is None
    assert packet["adapter_path"] == ".agents/critique-adapter.yaml"
    assert [s["id"] for s in packet["sections"]] == ["a", "b"]


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
    assert packet["changed_ref"] == "HEAD^..HEAD"
    assert packet["sections"][0]["content"].strip() == "HEAD^..HEAD"


def test_build_packet_clears_ambient_changed_ref_for_default_mode(tmp_path: Path, monkeypatch) -> None:
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
    monkeypatch.setenv("CHARNESS_CRITIQUE_CHANGED_REF", "HEAD^..HEAD")
    adapter = load_adapter(tmp_path)
    packet = build_packet(adapter=adapter, repo_root=tmp_path, prepared_for="working tree")

    assert packet["ok"] is True
    assert packet["changed_ref"] is None
    assert packet["sections"][0]["content"].strip() == "missing"


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

    identity = build_reviewed_input_identity(repo_root=tmp_path, changed_ref="HEAD")
    assert identity["reviewed_paths"] == ["README.md"]
    (tmp_path / "README.md").write_text("uncommitted third state\n", encoding="utf-8")
    rebuilt = build_reviewed_input_identity(repo_root=tmp_path, changed_ref="HEAD")
    assert rebuilt == identity


def test_changed_ref_identity_does_not_follow_live_parent_symlink(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    nested = tmp_path / "src"
    nested.mkdir()
    (nested / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
    _run_git(tmp_path, "add", "src/a.py")
    _run_git(tmp_path, "commit", "-m", "nested source")
    before = build_reviewed_input_identity(
        repo_root=tmp_path,
        changed_ref="HEAD",
        reviewed_paths=["src/a.py"],
    )

    shutil.rmtree(nested)
    outside = tmp_path.parent / f"{tmp_path.name}-changed-ref-outside"
    outside.mkdir()
    nested.symlink_to(outside, target_is_directory=True)
    after = build_reviewed_input_identity(
        repo_root=tmp_path,
        changed_ref="HEAD",
        reviewed_paths=["src/a.py"],
    )

    assert after == before


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
    packet = build_packet(adapter=adapter, repo_root=tmp_path, prepared_for="unit", changed_ref="HEAD")
    md = render_markdown(packet)
    assert "Alpha Section" in md
    assert "alpha-body" in md
    assert "Critique Prepare Packet" in md
    assert "Reviewer Tier Evidence" in md
    assert "**Changed ref**: `HEAD`" in md


def test_packet_records_adapter_reviewer_tier_evidence(tmp_path: Path) -> None:
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", """\
version: 1
repo: rt
reviewer_tiers:
  high-leverage:
    model: gpt-5.6-terra
    reasoning_effort: medium
    service_tier: priority
    fork_turns: none
packet_sections:
  - id: only
    title: Only
    content_kind: static
    content: body
""")
    adapter = load_adapter(tmp_path)
    packet = build_packet(adapter=adapter, repo_root=tmp_path, prepared_for="unit")
    evidence = packet["reviewer_tier_evidence"]
    assert evidence["requested_tier"] == "high-leverage"
    assert evidence["requested_spawn_fields"] == {
        "model": "gpt-5.6-terra",
        "reasoning_effort": "medium",
        "service_tier": "priority",
        "fork_turns": "none",
    }
    assert evidence["host_exposure_state"] == "pending-parent-spawn"
    md = render_markdown(packet)
    assert "model=gpt-5.6-terra" in md
    assert "pending-parent-spawn" in md


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


def _init_identity_repo(repo: Path) -> None:
    _run_git(repo, "init")
    _run_git(repo, "config", "user.email", "test@example.com")
    _run_git(repo, "config", "user.name", "Test User")
    (repo / "reviewed.txt").write_text("base\n", encoding="utf-8")
    (repo / "unrelated.txt").write_text("base\n", encoding="utf-8")
    _run_git(repo, "add", ".")
    _run_git(repo, "commit", "-m", "initial")


def test_reviewed_input_identity_is_ordered_and_tracks_staged_unstaged_untracked(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    (tmp_path / "reviewed.txt").write_text("unstaged\n", encoding="utf-8")
    first = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["reviewed.txt", "new.txt"],
    )
    reversed_order = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["new.txt", "reviewed.txt"],
    )
    assert first == reversed_order

    _run_git(tmp_path, "add", "reviewed.txt")
    staged = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["reviewed.txt", "new.txt"])
    assert staged["identity_sha256"] != first["identity_sha256"]

    (tmp_path / "new.txt").write_text("untracked\n", encoding="utf-8")
    untracked = build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["reviewed.txt", "new.txt"])
    assert untracked["identity_sha256"] != staged["identity_sha256"]
    assert untracked["declared_untracked"] == [
        {"path": "new.txt", "content_sha256": untracked["reviewed_content"][0]["content_sha256"]}
    ]


def test_working_tree_identity_ignores_unrelated_commit_but_tracks_symlink_target(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    symlink = tmp_path / "link.txt"
    symlink.symlink_to("reviewed.txt")
    before = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["reviewed.txt", "link.txt"],
    )

    (tmp_path / "unrelated.txt").write_text("unrelated commit\n", encoding="utf-8")
    _run_git(tmp_path, "commit", "-am", "unrelated")
    after_unrelated_commit = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["reviewed.txt", "link.txt"],
    )
    assert after_unrelated_commit["base_head"] != before["base_head"]
    assert after_unrelated_commit["identity_sha256"] == before["identity_sha256"]

    symlink.unlink()
    symlink.symlink_to("unrelated.txt")
    after_retarget = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["reviewed.txt", "link.txt"],
    )
    assert after_retarget["identity_sha256"] != before["identity_sha256"]


def test_reviewed_input_identity_rejects_traversal_and_symlinked_directory(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("outside\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside repo root"):
        build_reviewed_input_identity(repo_root=tmp_path, reviewed_paths=["../outside.txt"])

    (tmp_path / "outside-dir").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="outside repo root"):
        build_reviewed_input_identity(
            repo_root=tmp_path,
            reviewed_paths=["outside-dir/secret.txt"],
        )


def test_explicit_reviewed_path_is_never_silently_excluded(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    identity = build_reviewed_input_identity(
        repo_root=tmp_path,
        reviewed_paths=["reviewed.txt"],
        excluded_paths=["reviewed.txt"],
    )
    assert identity["reviewed_paths"] == ["reviewed.txt"]


def _write_bound_critique(repo: Path, packet_path: Path, identity_sha256: str) -> Path:
    artifact = repo / "charness-artifacts/critique/2026-07-20-bound-review.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    packet_sha = hashlib.sha256(packet_path.read_bytes()).hexdigest()
    artifact.write_text(
        "\n".join(
            [
                "# Bound Review",
                "Date: 2026-07-20",
                "",
                "## Reviewed Input Identity",
                "",
                f"- Packet path: {packet_path.relative_to(repo).as_posix()}",
                f"- Packet SHA256: {packet_sha}",
                f"- Identity SHA256: {identity_sha256}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return artifact


def test_reviewed_input_binding_stales_only_for_declared_input(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    adapter = load_adapter(tmp_path)
    packet = build_packet(
        adapter=adapter,
        repo_root=tmp_path,
        prepared_for="working tree",
        reviewed_paths=["reviewed.txt"],
    )
    packet_path, _ = write_packet(packet, output_dir=tmp_path / "charness-artifacts/critique", slug="bound")
    artifact = _write_bound_critique(
        tmp_path,
        packet_path,
        packet["reviewed_input_identity"]["identity_sha256"],
    )
    text = artifact.read_text(encoding="utf-8")

    validate_reviewed_input_binding(artifact, text, date(2026, 7, 20))
    (tmp_path / "unrelated.txt").write_text("changed but not reviewed\n", encoding="utf-8")
    validate_reviewed_input_binding(artifact, text, date(2026, 7, 20))

    (tmp_path / "reviewed.txt").write_text("changed reviewed input\n", encoding="utf-8")
    with pytest.raises(CritiqueValidationError, match="declared reviewed inputs are stale"):
        validate_reviewed_input_binding(artifact, text, date(2026, 7, 20))


def test_reviewed_input_binding_rejects_packet_byte_tamper(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    adapter = load_adapter(tmp_path)
    packet = build_packet(
        adapter=adapter,
        repo_root=tmp_path,
        prepared_for="working tree",
        reviewed_paths=["reviewed.txt"],
    )
    packet_path, _ = write_packet(packet, output_dir=tmp_path / "charness-artifacts/critique", slug="bound")
    artifact = _write_bound_critique(tmp_path, packet_path, packet["reviewed_input_identity"]["identity_sha256"])
    packet_path.write_text(packet_path.read_text(encoding="utf-8") + " ", encoding="utf-8")

    with pytest.raises(CritiqueValidationError, match="packet bytes are stale or tampered"):
        validate_reviewed_input_binding(
            artifact,
            artifact.read_text(encoding="utf-8"),
            date(2026, 7, 20),
        )


def test_packet_consumed_requires_reviewed_input_binding_after_rule_date(tmp_path: Path) -> None:
    artifact = tmp_path / "charness-artifacts/critique/2026-07-20-missing-binding.md"
    artifact.parent.mkdir(parents=True)
    text = "# Review\nDate: 2026-07-20\n\nPacket Consumed: packet.md\n"
    artifact.write_text(text, encoding="utf-8")

    with pytest.raises(CritiqueValidationError, match="packet-bound critique"):
        validate_reviewed_input_binding(artifact, text, date(2026, 7, 20))


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
    assert payload["changed_ref"] is None
    assert payload["adapter_path"] == ".agents/critique-adapter.yaml"
    binding = payload["reviewed_input_binding"]
    assert binding["packet_path"].endswith("smoke-packet.json")
    assert len(binding["packet_sha256"]) == 64
    assert len(binding["identity_sha256"]) == 64
    artifact = tmp_path / "charness-artifacts/critique/smoke-packet.json"
    assert artifact.is_file()


def test_runner_rerun_excludes_its_own_packet_outputs_from_identity(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", "version: 1\nrepo: rt\n")
    runner = REPO_ROOT / "skills/public/critique/scripts/prepare_packet.py"
    command = ["python3", str(runner), "--repo-root", str(tmp_path), "--slug", "repeat"]

    assert subprocess.run(command, capture_output=True, text=True, check=False).returncode == 0
    rerun = subprocess.run(command, capture_output=True, text=True, check=False)
    assert rerun.returncode == 0, rerun.stderr
    packet = json.loads(
        (tmp_path / "charness-artifacts/critique/repeat-packet.json").read_text(encoding="utf-8")
    )
    identity = packet["reviewed_input_identity"]

    assert not any(path.endswith("repeat-packet.json") for path in identity["reviewed_paths"])
    assert verify_reviewed_input_identity(tmp_path, identity) == (True, "current")


def test_runner_rejects_explicit_path_that_collides_with_packet_output(tmp_path: Path) -> None:
    _init_identity_repo(tmp_path)
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", "version: 1\nrepo: rt\n")
    runner = REPO_ROOT / "skills/public/critique/scripts/prepare_packet.py"
    result = subprocess.run(
        [
            "python3",
            str(runner),
            "--repo-root",
            str(tmp_path),
            "--slug",
            "collision",
            "--reviewed-path",
            "charness-artifacts/critique/collision-packet.json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "collides with packet output" in result.stderr


def test_prepare_packet_markdown_passes_live_critique_artifact_validator(tmp_path: Path) -> None:
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
        ["python3", str(runner), "--repo-root", str(tmp_path), "--prepared-for", "smoke", "--slug", "smoke"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    candidates = critique_candidate_paths(
        tmp_path,
        ["charness-artifacts/critique/smoke-packet.md"],
        all_artifacts=False,
    )

    assert candidates == []


def test_renamed_or_mislabeled_packet_name_does_not_bypass_critique_record_floors(tmp_path: Path) -> None:
    artifact = tmp_path / "charness-artifacts/critique/2026-07-10-fake-packet.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "\n".join(
            [
                "# Critique Prepare Packet — demo",
                "",
                "- **Prepared for**: fake packet",
                "",
                "## Decision Under Review",
                "",
                "still a critique record with no packet envelope kind",
                "",
            ]
        ),
        encoding="utf-8",
    )

    candidates = critique_candidate_paths(
        tmp_path,
        ["charness-artifacts/critique/2026-07-10-fake-packet.md"],
        all_artifacts=False,
    )

    assert candidates == [artifact]
    try:
        validate_critique_artifact(
            artifact,
            repo_has_delegation_contract=False,
            require_tier_evidence=True,
        )
    except CritiqueValidationError as exc:
        assert "Fresh-eye satisfaction" in str(exc)
    else:
        raise AssertionError("expected mislabeled critique record to fail validation")


def test_wrong_prepare_packet_title_with_correct_critique_kind_still_fails_record_floors(tmp_path: Path) -> None:
    artifact = tmp_path / "charness-artifacts/critique/2026-07-10-fake-packet.md"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(
        "\n".join(
            [
                "# Quality Prepare Packet — demo",
                "",
                f"- **Kind**: `{PACKET_KIND}` (v1)",
                "",
                "## Decision Under Review",
                "",
                "wrong title should not bypass critique floors",
                "",
            ]
        ),
        encoding="utf-8",
    )

    candidates = critique_candidate_paths(
        tmp_path,
        ["charness-artifacts/critique/2026-07-10-fake-packet.md"],
        all_artifacts=False,
    )

    assert candidates == [artifact]
    try:
        validate_critique_artifact(
            artifact,
            repo_has_delegation_contract=False,
            require_tier_evidence=True,
        )
    except CritiqueValidationError as exc:
        assert "Fresh-eye satisfaction" in str(exc)
    else:
        raise AssertionError("expected wrong-title critique packet lookalike to fail validation")


def test_prepare_packet_markdown_kind_accepts_sequence_lines_only_for_matching_title_and_kind() -> None:
    packet_path = Path("charness-artifacts/critique/demo-packet.md")
    matching_lines = (
        "# Critique Prepare Packet — demo",
        "",
        f"- **Kind**: `{PACKET_KIND}` (v1)",
        "",
        "## Decision Under Review",
    )
    wrong_title_lines = list(matching_lines)
    wrong_title_lines[0] = "# Quality Prepare Packet — demo"
    wrong_kind_lines = list(matching_lines)
    wrong_kind_lines[2] = "- **Kind**: `quality.prepare-packet` (v1)"

    assert prepare_packet_markdown_kind(
        packet_path,
        tuple(matching_lines),
        expected_title_re=CRITIQUE_PREPARE_PACKET_TITLE_RE,
    ) == PACKET_KIND
    assert (
        prepare_packet_markdown_kind(
            packet_path,
            tuple(wrong_title_lines),
            expected_title_re=CRITIQUE_PREPARE_PACKET_TITLE_RE,
        )
        is None
    )
    assert prepare_packet_markdown_kind(
        packet_path,
        tuple(wrong_kind_lines),
        expected_title_re=CRITIQUE_PREPARE_PACKET_TITLE_RE,
    ) == "quality.prepare-packet"


def test_runner_cli_json_changed_ref_with_default_surface_producer(tmp_path: Path) -> None:
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
    producer = REPO_ROOT / "scripts/render_critique_section_changed_surfaces.py"
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", f"""\
version: 1
repo: rt
packet_sections:
  - id: changed-files-and-owning-surfaces
    title: Changed Files And Owning Surfaces
    content_kind: script
    command: "python3 {producer} --repo-root ."
""")
    (tmp_path / "README.md").write_text("one\n", encoding="utf-8")
    _run_git(tmp_path, "add", ".")
    _run_git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "README.md").write_text("two\n", encoding="utf-8")
    _run_git(tmp_path, "commit", "-am", "update")

    runner = REPO_ROOT / "skills/public/critique/scripts/prepare_packet.py"
    result = subprocess.run(
        [
            "python3",
            str(runner),
            "--repo-root",
            str(tmp_path),
            "--prepared-for",
            "head",
            "--changed-ref",
            "HEAD",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "CHARNESS_CRITIQUE_CHANGED_REF": "SHOULD_NOT_WIN"},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["changed_ref"] == "HEAD"
    assert payload["adapter_path"] == ".agents/critique-adapter.yaml"
    assert "README.md" in payload["sections"][0]["content"]
    assert "Changed paths for ref `HEAD`:" in payload["sections"][0]["content"]


def test_runner_cli_commit_alias_sets_changed_ref_and_prepared_for(tmp_path: Path) -> None:
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
    producer = REPO_ROOT / "scripts/render_critique_section_changed_surfaces.py"
    _write_yaml(tmp_path / ".agents/critique-adapter.yaml", f"""\
version: 1
repo: rt
packet_sections:
  - id: changed-files-and-owning-surfaces
    title: Changed Files And Owning Surfaces
    content_kind: script
    command: "python3 {producer} --repo-root ."
""")
    (tmp_path / "README.md").write_text("one\n", encoding="utf-8")
    _run_git(tmp_path, "add", ".")
    _run_git(tmp_path, "commit", "-m", "initial")
    (tmp_path / "README.md").write_text("two\n", encoding="utf-8")
    _run_git(tmp_path, "commit", "-am", "update")

    runner = REPO_ROOT / "skills/public/critique/scripts/prepare_packet.py"
    result = subprocess.run(
        ["python3", str(runner), "--repo-root", str(tmp_path), "--commit", "HEAD", "--json"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["changed_ref"] == "HEAD"
    assert payload["prepared_for"] == "HEAD"
    assert "Changed paths for ref `HEAD`:" in payload["sections"][0]["content"]
    assert "README.md" in payload["sections"][0]["content"]
