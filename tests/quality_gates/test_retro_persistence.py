from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from runtime_bootstrap import import_repo_module
from tests.quality_gates.repo_shapes import install_committed_repo
from tests.quality_gates.seeding_support import write_retro_adapter
from tests.quality_gates.support import run_script
from tests.script_closure import script_import_closure

ROOT = Path(__file__).resolve().parents[2]
_persist_retro_artifact = import_repo_module(
    ROOT / "skills" / "public" / "retro" / "scripts" / "persist_retro_artifact.py",
    "skills.public.retro.scripts.persist_retro_artifact",
)
_persistence_lib = import_repo_module(
    ROOT / "scripts" / "retro_persistence_lib.py",
    "scripts.retro_persistence_lib",
)
_scaffold_retro_artifact = import_repo_module(
    ROOT / "skills" / "public" / "retro" / "scripts" / "scaffold_retro_artifact.py",
    "skills.public.retro.scripts.scaffold_retro_artifact",
)


def run_persist(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["persist_retro_artifact.py", *args])
    returncode = _persist_retro_artifact.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_persist_retro_artifact_writes_artifact_snapshot_and_recent_lessons(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    write_retro_adapter(repo)
    markdown_file = repo / "weekly.md"
    markdown_file.write_text(
        "\n".join(
            [
                "# Weekly Retro",
                "",
                "## Context",
                "",
                "- Durable persistence should refresh recent lessons automatically.",
                "",
                "## Waste",
                "",
                "- Manual summary refresh was easy to forget.",
                "",
                "## Next Improvements",
                "",
                "- `capability`: Use one persistence helper that writes the artifact and refreshes the digest.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "weekly-2026-04-14.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/retro/weekly-2026-04-14.md"
    assert payload["summary_path"] == "charness-artifacts/retro/recent-lessons.md"
    assert (
        payload["lesson_selection_index_path"]
        == "charness-artifacts/retro/lesson-selection-index.json"
    )
    assert payload["summary_refreshed"] is True

    summary_text = (output_dir / "recent-lessons.md").read_text(encoding="utf-8")
    assert "Durable persistence should refresh recent lessons automatically." in summary_text
    assert "Manual summary refresh was easy to forget." in summary_text
    assert "## Selection Policy" in summary_text
    assert "lesson-selection-index.json" in summary_text
    assert (output_dir / "lesson-selection-index.json").is_file()


def test_persist_retro_artifact_stamps_persisted_path(tmp_path: Path, monkeypatch, capsys) -> None:
    # The helper knows the durable path it writes, so it stamps the `## Persisted`
    # line — the run must not hand-edit the placeholder afterward (the micro-churn
    # the retro H0 fresh-eye caught: two byte-identical edits + a verifying read).
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    write_retro_adapter(repo, include_summary_path=False)
    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "\n".join(["# Session Retro", "", "## Persisted", "", "Persisted: yes: TODO path", ""])
        + "\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-07-03-demo.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["persisted_line_stamped"] is True
    written = (output_dir / "2026-07-03-demo.md").read_text(encoding="utf-8")
    assert "Persisted: yes: charness-artifacts/retro/2026-07-03-demo.md" in written
    assert "TODO path" not in written


def test_persist_retro_artifact_skips_self_refresh_for_summary_target(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo / "charness-artifacts" / "retro"
    write_retro_adapter(repo)
    markdown_file = repo / "summary.md"
    markdown_file.write_text("# Recent Retro Lessons\n", encoding="utf-8")

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "recent-lessons.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/retro/recent-lessons.md"
    assert payload["summary_refreshed"] is False


def test_persist_does_not_overwrite_undated_sibling_when_scaffold_resolves_dated_subject(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Incident 1: one subject key must not name two files.

    The scaffold's dated target is absent, while the old undated spelling exists
    with another session's content. The persist call receives the same subject
    key; it must land on the scaffold target and leave the undated file intact.
    """
    other_session = "# Other session\n\nThis content must survive.\n"
    repo = install_committed_repo(
        tmp_path / "repo",
        {"charness-artifacts/retro/session-retro-2.md": other_session},
    )
    write_retro_adapter(repo, include_summary_path=False)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        (repo / ".agents" / "retro-adapter.yaml").read_text(encoding="utf-8")
        + "summary_path: null\n",
        encoding="utf-8",
    )
    undated = repo / "charness-artifacts" / "retro" / "session-retro-2.md"
    markdown_file = repo / "new-session.md"
    markdown_file.write_text(
        "# Session Retro 2\n\n"
        "## Context\n\n- The new session must land at its canonical path.\n\n"
        "## Waste\n\n- Two path owners allowed a collision.\n\n"
        "## Next Improvements\n\n- capability: Keep one path owner.\n",
        encoding="utf-8",
    )

    scaffold = _scaffold_retro_artifact.payload_for(repo, title="Session Retro 2")
    assert scaffold["write_artifact_path"].endswith("-session-retro-2.md")
    assert not (repo / scaffold["write_artifact_path"]).exists()

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "session-retro-2",
        "--markdown-file",
        str(markdown_file),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert undated.read_text(encoding="utf-8") == other_session
    assert payload["artifact_path"] == scaffold["write_artifact_path"]


def test_persist_refuses_subject_collision_and_names_deliberate_next_action(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    write_retro_adapter(repo, include_summary_path=False)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        (repo / ".agents" / "retro-adapter.yaml").read_text(encoding="utf-8")
        + "summary_path: null\n",
        encoding="utf-8",
    )
    target = (
        repo / "charness-artifacts" / "retro" / f"{date.today().isoformat()}-session-retro-2.md"
    )
    existing = "# Existing retro\n\nThis must not be replaced.\n"
    target.write_text(existing, encoding="utf-8")
    markdown_file = repo / "new-session.md"
    markdown_file.write_text("# New retro\n", encoding="utf-8")

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "session-retro-2",
        "--markdown-file",
        str(markdown_file),
    )

    assert result.returncode != 0
    assert target.name in result.stderr
    assert "different subject key" in result.stderr
    assert "explicitly name the existing dated path" in result.stderr
    assert target.read_text(encoding="utf-8") == existing


def test_persist_then_index_checker_accepts_persisted_index(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Incident 2: persist and the repository builder must produce one index."""
    repo = tmp_path / "repo"
    write_retro_adapter(repo)
    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "# Session Retro\n\n"
        "## Context\n\n- Persist should use the repository index producer.\n\n"
        "## Waste\n\n- A second index writer drifted from the checker.\n\n"
        "## Next Improvements\n\n- capability: Keep index bytes canonical.\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-08-29-index-producer.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr

    checker = run_script(
        "scripts/lessons/build_retro_lesson_selection_index.py",
        "--repo-root",
        str(repo),
        "--check",
    )
    assert checker.returncode == 0, checker.stderr


@pytest.mark.boundary_contract(
    reason="prove the copied repo's lesson-index producer is runnable from its installed-style layout"
)
def test_persist_then_repo_checker_accepts_the_repo_producer_index(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """Incident 2 stimulus: an installed writer emits a schema the repo rejects.

    The target is a source-like checkout whose own lesson producer has one extra
    field. The current persist helper writes through this checkout's foreign copy
    instead, so the target checker rejects the resulting index. The repaired
    helper must call the target's builder rather than remain a second writer.
    """
    repo = tmp_path / "repo with spaces"
    write_retro_adapter(repo)
    (repo / "packaging").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text(
        '{"package_id": "charness"}\n', encoding="utf-8"
    )
    # DERIVED, not listed. The literal tuple this replaces was a restatement of
    # the import graph with nothing binding it to the graph, and it went stale
    # the moment `helper_provenance_lib` gained an import. `adapter_lib` is a
    # second ENTRY point rather than a closure member: the target checkout reads
    # its retro adapter through it, which no import from the builder reaches.
    for name in script_import_closure("lessons/build_retro_lesson_selection_index.py", "adapter_lib.py"):
        target = repo / "scripts" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "scripts" / name, target)
    target_recent = repo / "scripts" / "lessons" / "recent_lessons_lib.py"
    target_recent.write_text(
        target_recent.read_text(encoding="utf-8").replace(
            '        "schema_version": 1,\n',
            '        "schema_version": 1,\n        "target_writer_marker": True,\n',
            1,
        ),
        encoding="utf-8",
    )
    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "# Session Retro\n\n"
        "## Context\n\n- The repo's producer owns the index bytes.\n\n"
        "## Waste\n\n- A foreign helper wrote a different index.\n\n"
        "## Next Improvements\n\n- capability: Call the repo's producer.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CHARNESS_ALLOW_FOREIGN_HELPER", "1")

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-08-29-foreign-writer.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr

    checker = subprocess.run(
        [
            sys.executable,
            str(repo / "scripts" / "lessons" / "build_retro_lesson_selection_index.py"),
            "--repo-root",
            str(repo),
            "--check",
        ],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert checker.returncode == 0, checker.stderr


def _write_goal(repo: Path, slug: str = "owner") -> Path:
    path = repo / "charness-artifacts" / "goals" / f"2026-05-07-{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Achieve Goal: Owner\n\nStatus: active\n", encoding="utf-8")
    return path


def _goal_retro(goal_value: str) -> str:
    return "\n".join(
        [
            "# Goal Retro",
            f"Goal: {goal_value}",
            "",
            "## Context",
            "",
            "- Goal-aware persistence must bind before writing.",
            "",
            "## Waste",
            "",
            "- A late evidence check allowed avoidable closeout churn.",
            "",
            "## Next Improvements",
            "",
            "- `capability`: validate the owning goal at the shared write boundary.",
            "",
        ]
    )


def test_goal_metadata_canonicalizer_keeps_text_without_one_field_unchanged() -> None:
    text = "# Goal Retro\n\n## Context\n\n- No identity metadata.\n"

    assert (
        _persistence_lib._canonicalize_goal_metadata(
            text, "charness-artifacts/goals/2026-05-07-owner.md"
        )
        == text
    )


def test_goal_metadata_canonicalizer_preserves_crlf_when_rewriting_a_slug() -> None:
    text = "# Goal Retro\r\nGoal: owner\r\n\r\n## Context\r\n"

    rewritten = _persistence_lib._canonicalize_goal_metadata(
        text, "charness-artifacts/goals/2026-05-07-owner.md"
    )

    assert rewritten == (
        "# Goal Retro\r\nGoal: charness-artifacts/goals/2026-05-07-owner.md\r\n\r\n## Context\r\n"
    )


def test_goal_identity_rejects_a_goal_path_outside_the_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    outside_goal = tmp_path / "outside" / "2026-05-07-owner.md"
    outside_goal.parent.mkdir()
    outside_goal.write_text("# Achieve Goal: Owner\n\nStatus: active\n", encoding="utf-8")

    with pytest.raises(ValueError, match="inside --repo-root"):
        _persistence_lib._goal_identity(repo, outside_goal, _goal_retro("owner"))


def _tree_snapshot(root: Path) -> dict[str, tuple[str, bytes | None]]:
    snapshot: dict[str, tuple[str, bytes | None]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            snapshot[relative] = ("dir", None)
        else:
            snapshot[relative] = ("file", path.read_bytes())
    return snapshot


def test_goal_aware_persistence_accepts_matching_path_at_cli_boundary(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    write_retro_adapter(repo)
    goal = _write_goal(repo)
    outside = tmp_path / "outside"
    outside.mkdir()
    markdown_file = repo / "goal-retro.md"
    markdown_file.write_text(
        _goal_retro("charness-artifacts/goals/2026-05-07-owner.md"), encoding="utf-8"
    )
    monkeypatch.chdir(outside)

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-08-owner-retro.md",
        "--markdown-file",
        str(markdown_file),
        "--goal-path",
        str(goal.relative_to(repo)),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["goal_path"] == "charness-artifacts/goals/2026-05-07-owner.md"
    assert payload["goal_slug"] == "owner"
    assert "Goal: charness-artifacts/goals/2026-05-07-owner.md" in (
        repo / payload["artifact_path"]
    ).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "markdown_text",
    [
        _goal_retro("different-owner"),
        "# Goal Retro\n\n## Context\n\n- No identity field.\n",
        _goal_retro(""),
        "# Goal Retro\nGoal: owner\nGoal: owner\n\n## Context\n\n- Duplicate metadata fields.\n",
        "# Goal Retro\n\n```text\nGoal: owner\n```\n\n## Context\n\n- Fenced example only.\n",
        "# Goal Retro\n\n    Goal: owner\n\n## Context\n\n- Indented example only.\n",
        "# Goal Retro\n\n## Context\n\nGoal: owner\n\n- Body heading must end the preamble.\n",
        "# Goal Retro\n\n ## Context\n\nGoal: owner\n\n- Body heading must end the preamble.\n",
        "# Goal Retro\n\n  ## Context\n\nGoal: owner\n\n- Body heading must end the preamble.\n",
        "# Goal Retro\n\n   ## Context\n\nGoal: owner\n\n- Body heading must end the preamble.\n",
        "# Goal Retro\n\n# Body\n\nGoal: owner\n\n- A later H1 is also a body boundary.\n",
        "# Goal Retro\n\n````text\n```\nGoal: owner\n````\n\n## Context\n\n- Short inner fence only.\n",
        "# Goal Retro\n\n````\n````still-code\nGoal: owner\n````\n\n## Context\n\n- Trailing-text pseudo-closer only.\n",
        "# Goal Retro\n\nHeading\n---\nGoal: owner\n\n## Context\n\n- Setext heading precedes the field.\n",
    ],
    ids=[
        "mismatch",
        "missing-field",
        "missing-value",
        "duplicate-field",
        "fenced",
        "indented",
        "atx-h2-0",
        "atx-h2-1",
        "atx-h2-2",
        "atx-h2-3",
        "atx-h1-after-title",
        "short-fence-closer",
        "trailing-text-closer",
        "setext-heading",
    ],
)
def test_goal_aware_mismatch_or_malformed_identity_writes_nothing(
    tmp_path: Path, markdown_text: str
) -> None:
    repo = tmp_path / "repo"
    write_retro_adapter(repo)
    goal = _write_goal(repo)
    markdown_file = repo / "goal-retro.md"
    markdown_file.write_text(markdown_text, encoding="utf-8")
    before = _tree_snapshot(repo)

    with pytest.raises(ValueError):
        _persistence_lib.persist_retro_artifact(
            repo_root=repo,
            output_dir=repo / "charness-artifacts" / "retro",
            artifact_name="2026-05-08-owner-retro.md",
            markdown_text=markdown_text,
            summary_path=repo / "charness-artifacts" / "retro" / "recent-lessons.md",
            goal_path=goal,
        )

    assert _tree_snapshot(repo) == before


def test_goal_aware_missing_goal_path_writes_nothing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_retro_adapter(repo)
    markdown_text = _goal_retro("owner")
    before = _tree_snapshot(repo)

    with pytest.raises(ValueError):
        _persistence_lib.persist_retro_artifact(
            repo_root=repo,
            output_dir=repo / "charness-artifacts" / "retro",
            artifact_name="2026-05-08-owner-retro.md",
            markdown_text=markdown_text,
            summary_path=repo / "charness-artifacts" / "retro" / "recent-lessons.md",
            goal_path=repo / "charness-artifacts" / "goals" / "2026-05-07-owner.md",
        )

    assert _tree_snapshot(repo) == before


def test_goal_aware_library_accepts_exact_slug_and_legacy_mode_stays_goal_free(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    write_retro_adapter(repo)
    goal = _write_goal(repo)
    goal_retro = _goal_retro("owner")
    result = _persistence_lib.persist_retro_artifact(
        repo_root=repo,
        output_dir=repo / "charness-artifacts" / "retro",
        artifact_name="2026-05-08-owner-slug.md",
        markdown_text=goal_retro,
        summary_path=None,
        goal_path=goal,
    )
    assert result["goal_path"] == "charness-artifacts/goals/2026-05-07-owner.md"
    written = (repo / result["artifact_path"]).read_text(encoding="utf-8")
    assert "Goal: charness-artifacts/goals/2026-05-07-owner.md" in written
    assert "Goal: owner" not in written

    legacy_file = repo / "legacy.md"
    legacy_file.write_text("# Session Retro\n\nNo goal field is required.\n", encoding="utf-8")
    legacy = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-09-session.md",
        "--markdown-file",
        str(legacy_file),
    )
    assert legacy.returncode == 0, legacy.stderr
    assert "goal_path" not in yaml.safe_load(legacy.stdout)


def test_persist_retro_artifact_normalizes_artifact_name_without_md_extension(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    write_retro_adapter(repo)
    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "\n".join(
            [
                "# Retro",
                "",
                "## Context",
                "",
                "- Slice closed without lesson loss.",
                "",
                "## Waste",
                "",
                "- Lost time rediscovering trivia.",
                "",
                "## Next Improvements",
                "",
                "- `capability`: Keep the persistence helper safe by default.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-07-session-no-extension",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_path"].endswith(".md"), payload
    assert payload["artifact_path"] == "charness-artifacts/retro/2026-05-07-session-no-extension.md"
    assert payload["artifact_name_normalized"] is True
    assert payload["summary_refreshed"] is True
    assert (output_dir / "2026-05-07-session-no-extension.md").is_file()
    assert result.stderr == ""


def test_persist_retro_artifact_preserves_legacy_summary_when_no_candidates(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    write_retro_adapter(repo)
    legacy_summary = output_dir / "recent-lessons.md"
    legacy_text = (
        "# Recent Retro Lessons\n\n"
        "## Repeat Traps\n\n"
        "- Hand-curated trap line that predates the retro skill.\n"
    )
    legacy_summary.write_text(legacy_text, encoding="utf-8")

    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "# Retro\n\nA narrative-only retro with no Context/Waste/Next Improvements headers.\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-07-narrative-only.md",
        "--markdown-file",
        str(markdown_file),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["summary_refreshed"] is False
    assert payload["summary_skipped_reason"] == "no_candidates_existing_summary_protected"
    preserved = legacy_summary.read_text(encoding="utf-8")
    assert preserved == legacy_text
    assert "Hand-curated trap line that predates the retro skill." in preserved
    assert "refusing to overwrite" in result.stderr


def test_persist_retro_artifact_force_empty_summary_opts_in(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    output_dir.mkdir(parents=True)
    write_retro_adapter(repo)
    legacy_summary = output_dir / "recent-lessons.md"
    legacy_text = (
        "# Recent Retro Lessons\n\n"
        "## Repeat Traps\n\n"
        "- Hand-curated trap line that the operator has chosen to drop.\n"
    )
    legacy_summary.write_text(legacy_text, encoding="utf-8")

    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "# Retro\n\nA narrative-only retro with no Context/Waste/Next Improvements headers.\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "2026-05-07-narrative-only.md",
        "--markdown-file",
        str(markdown_file),
        "--force-empty-summary",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["summary_refreshed"] is True
    refreshed = legacy_summary.read_text(encoding="utf-8")
    assert "Hand-curated trap line that the operator has chosen to drop." not in refreshed
    assert "No current focus bullets found in retro lesson index." in refreshed


def test_persist_writes_no_digest_when_the_projection_is_disabled(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The retro artifact is still persisted; only the Markdown projection is declined.

    This is the case a consumer whose ledger is the sole lesson surface needs: the
    durable retro must still land, and the next retro must not silently recreate the
    second lesson owner the repository removed.
    """
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    (repo / ".agents").mkdir(parents=True)
    output_dir.mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nsummary_path: null\n", encoding="utf-8"
    )
    markdown_file = repo / "session.md"
    markdown_file.write_text(
        "\n".join(
            [
                "# Session Retro",
                "",
                "## Context",
                "",
                "- The ledger is this repository's only lesson surface.",
                "",
                "## Next Improvements",
                "",
                "- `capability`: Let the adapter decline the Markdown projection.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "session-2026-04-14.md",
        "--markdown-file",
        str(markdown_file),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_path"] == "charness-artifacts/retro/session-2026-04-14.md"
    assert (output_dir / "session-2026-04-14.md").is_file()
    # The digest is declined, but the source-linked selection index remains current.
    assert not (output_dir / "recent-lessons.md").exists()
    assert (output_dir / "lesson-selection-index.json").is_file()
    assert payload["lesson_selection_index_path"] == (
        "charness-artifacts/retro/lesson-selection-index.json"
    )
    assert payload.get("summary_refreshed") is not True


def test_a_date_bearing_subject_key_resolves_to_one_path(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The scaffold and persistence must not split a subject that CONTAINS a date.

    The dated-artifact predicate matched a date anywhere in the name, so the subject
    key `session-2026-08-29` was read here as an explicitly named artifact
    (`session-2026-08-29.md`) while the scaffold resolved the same subject to
    `2026-08-29-session-2026-08-29.md`. Two paths for one subject key is the incident
    this module exists to close, and `derived=False` also disabled the collision guard,
    so the overwrite came back for exactly the subjects that carry a date.
    """
    resolve = _persistence_lib.resolve_retro_artifact_path
    output_dir = tmp_path / "charness-artifacts" / "retro"

    scaffold_path, _ = resolve(output_dir, "session-2026-08-29", subject_key=True)
    persist_path, derived = resolve(output_dir, "session-2026-08-29")
    assert persist_path == scaffold_path
    assert derived is True, "a subject key must stay derived, or the collision guard is off"

    # An explicitly named dated artifact is still left alone: the date is its PREFIX.
    explicit, explicit_derived = resolve(output_dir, "2026-08-29-session-retro-2.md")
    assert explicit.name == "2026-08-29-session-retro-2.md"
    assert explicit_derived is False


def test_a_date_bearing_subject_key_cannot_overwrite_an_undated_sibling(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The counterexample the release review asked for, with the sibling's bytes asserted."""
    repo = tmp_path / "repo"
    output_dir = repo / "charness-artifacts" / "retro"
    (repo / ".agents").mkdir(parents=True)
    output_dir.mkdir(parents=True)
    (repo / ".agents" / "retro-adapter.yaml").write_text(
        "version: 1\nrepo: consumer\nsummary_path: null\n", encoding="utf-8"
    )
    sibling = output_dir / "session-2026-08-29.md"
    sibling.write_text("# ANOTHER SESSION\n\n## Context\n\n- do not lose me\n", encoding="utf-8")
    before = sibling.read_bytes()

    markdown_file = repo / "new.md"
    markdown_file.write_text(
        "# Retro\n\n## Context\n\n- new work\n\n## Next Improvements\n\n- `capability`: x\n",
        encoding="utf-8",
    )
    result = run_persist(
        monkeypatch,
        capsys,
        "--repo-root",
        str(repo),
        "--artifact-name",
        "session-2026-08-29",
        "--markdown-file",
        str(markdown_file),
    )

    assert result.returncode == 0, result.stderr
    assert sibling.read_bytes() == before
    # The prefix is TODAY, not the date inside the subject key -- those are two
    # different dates and the whole point of the guard is that it prefixes rather
    # than reuses. Hardcoding the prefix as `2026-08-29` made this test pass only
    # on the day it was written, and it went red at that midnight.
    assert (output_dir / f"{date.today().isoformat()}-session-2026-08-29.md").is_file()
