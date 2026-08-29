from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts import lesson_command_citation, recent_lessons_lib
from tests.dsl import Repo, run_at

ROOT_PATH = Path(__file__).resolve().parents[2]

RETRO = Repo().adapter(
    "retro",
    {
        "version": 1,
        "repo": "demo",
        "language": "en",
        "output_dir": "charness-artifacts/retro",
        "summary_path": "charness-artifacts/retro/recent-lessons.md",
        "evidence_paths": [],
        "metrics_commands": [],
    },
)

BUILD_INDEX = "scripts/build_retro_lesson_selection_index.py"
REFRESH = "skills/public/retro/scripts/refresh_recent_lessons.py"


def artifact(name: str, body: str) -> tuple[str, str]:
    return (f"charness-artifacts/retro/{name}", body)


def retro_artifact(date: str, *, waste: str, improvement: str) -> str:
    return (
        "\n".join(
            [
                "# Session Retro",
                f"Date: {date}",
                "",
                "## Context",
                "",
                "- Context should stay source-linked.",
                "",
                "## Waste",
                "",
                f"- {waste}",
                "",
                "## Next Improvements",
                "",
                f"- workflow: {improvement}",
            ]
        )
        + "\n"
    )


def test_build_retro_lesson_selection_index_writes_source_linked_candidates(tmp_path: Path) -> None:
    res = (
        RETRO.file(
            *artifact(
                "2026-04-01-old.md",
                retro_artifact(
                    "2026-04-01",
                    waste="Plugin export was verified too late.",
                    improvement="Sync generated surfaces before broad validation.",
                ),
            )
        )
        .file(
            *artifact(
                "2026-04-15-new.md",
                retro_artifact(
                    "2026-04-15",
                    waste="Plugin export was verified too late.",
                    improvement="Validate committed state directly.",
                ),
            )
        )
        .run(tmp_path, BUILD_INDEX, "--write")
        .ok()
    )
    # Command stdout is YAML; the index it names on disk stays JSON.
    payload = yaml.safe_load(res.proc.stdout)
    assert payload["status"] == "written"
    assert payload["index_path"] == "charness-artifacts/retro/lesson-selection-index.json"

    index = res.file_json(payload["index_path"])
    assert index["kind"] == "retro-lesson-selection-index"
    assert index["selection_policy"]["advisory"] is True
    assert index["selection_policy"]["alpha_t"] == "alpha_base * min(1, source_count / warmup_n)"
    repeated = next(item for item in index["candidates"] if item["lesson"] == "Plugin export was verified too late.")
    assert repeated["kind"] == "repeat_trap"
    assert repeated["source_count"] == 2
    assert repeated["latest_source_path"] == "charness-artifacts/retro/2026-04-15-new.md"
    assert repeated["selection_weight"] > repeated["recency_weight"]


def test_build_retro_lesson_selection_index_check_rejects_stale_index(tmp_path: Path) -> None:
    (
        RETRO.file(
            *artifact(
                "2026-04-15-new.md",
                retro_artifact(
                    "2026-04-15",
                    waste="Manual summary refresh was easy to forget.",
                    improvement="Refresh recent lessons through the persistence helper.",
                ),
            )
        )
        .file("charness-artifacts/retro/lesson-selection-index.json", "{}\n")
        .run(tmp_path, BUILD_INDEX, "--check")
        .failed(1)
        .stderr_has("retro lesson selection index", "--write")
    )


def test_build_retro_lesson_selection_index_preserves_a_disabled_projection(tmp_path: Path) -> None:
    repo = (
        Repo()
        .file(
            ".agents/retro-adapter.yaml",
            "version: 1\nrepo: demo\noutput_dir: charness-artifacts/retro\nsummary_path: null\n",
        )
        .build(tmp_path)
    )

    write_result = run_at(repo, BUILD_INDEX, "--write").ok()
    assert yaml.safe_load(write_result.proc.stdout) == {
        "status": "disabled",
        "projection": "disabled",
    }
    assert not (repo / "charness-artifacts" / "retro" / "lesson-selection-index.json").exists()

    check_result = run_at(repo, BUILD_INDEX, "--check").ok()
    assert yaml.safe_load(check_result.proc.stdout) == {
        "status": "disabled",
        "projection": "disabled",
    }


def test_build_retro_lesson_selection_index_check_rejects_stale_digest(tmp_path: Path) -> None:
    repo = RETRO.file(
        *artifact(
            "2026-04-15-new.md",
            retro_artifact(
                "2026-04-15",
                waste="Manual summary refresh was easy to forget.",
                improvement="Refresh recent lessons through the persistence helper.",
            ),
        )
    ).build(tmp_path)

    run_at(repo, REFRESH).ok()
    (repo / "charness-artifacts" / "retro" / "recent-lessons.md").write_text(
        "# Recent Retro Lessons\n\nstale\n", encoding="utf-8"
    )

    run_at(repo, BUILD_INDEX, "--check").failed(1).stderr_has(
        "recent lessons digest", "refresh_recent_lessons.py"
    )


def test_refresh_recent_lessons_prefers_index_ranked_repeated_lessons(tmp_path: Path) -> None:
    res = (
        RETRO.file(
            *artifact(
                "2026-04-01-old.md",
                retro_artifact(
                    "2026-04-01",
                    waste="Plugin export was verified too late.",
                    improvement="Sync generated surfaces before broad validation.",
                ),
            )
        )
        .file(
            *artifact(
                "2026-04-15-new.md",
                retro_artifact(
                    "2026-04-15",
                    waste="Plugin export was verified too late.",
                    improvement="Validate committed state directly.",
                ),
            )
        )
        .run(tmp_path, REFRESH)
        .ok()
    )

    summary_text = res.file_text("charness-artifacts/retro/recent-lessons.md")
    assert "Plugin export was verified too late." in summary_text
    assert "sources: 2" in summary_text
    assert "## Selection Policy" in summary_text


def _staleable_repo(tmp_path: Path, *, name: str) -> Path:
    repo = RETRO.file(
        *artifact(
            "2026-04-15-new.md",
            retro_artifact(
                "2026-04-15",
                waste="Manual summary refresh was easy to forget.",
                improvement="Refresh recent lessons through the persistence helper.",
            ),
        )
    ).build(tmp_path, name=name)
    run_at(repo, BUILD_INDEX, "--write").ok()
    (repo / "charness-artifacts" / "retro" / "lesson-selection-index.json").write_text("{}\n", encoding="utf-8")
    return repo


def _stale_index_message(repo: Path) -> str:
    with pytest.raises(ValueError) as excinfo:
        recent_lessons_lib.check_lesson_selection_index(
            repo_root=repo,
            output_dir=repo / "charness-artifacts" / "retro",
            summary_path=repo / "charness-artifacts" / "retro" / "recent-lessons.md",
        )
    return str(excinfo.value)


def test_stale_index_refusal_names_a_command_a_consuming_repo_can_actually_run(tmp_path: Path) -> None:
    """#632: the refusal named `scripts/…` and `skills/public/retro/…` unconditionally.

    A consuming repo has neither, so the only way forward was the installed copy the
    message's own first paragraph warned against. Here the cited command must resolve
    to a file that exists, and the foreign-copy warning must be gone: with no repo-local
    builder there is no competing copy, so that hypothesis cannot be true.
    """
    repo = _staleable_repo(tmp_path, name="consumer")
    assert not (repo / "scripts").exists()

    message = _stale_index_message(repo)

    cited = [word for word in message.split() if word.endswith("build_retro_lesson_selection_index.py")]
    assert cited, message
    assert Path(cited[0]).is_file(), message
    assert "carries no" in message
    assert "FIRST, check who wrote it" not in message


def test_stale_index_refusal_keeps_the_foreign_copy_warning_for_a_repo_that_owns_the_builder(
    tmp_path: Path,
) -> None:
    """The warning is load-bearing where it CAN be true, and only there.

    A repo with its own builder is the source-tree case the warning was written for:
    an installed copy writing an older schema is a live hypothesis, and `--write`
    through that copy is a loop rather than a fix.
    """
    repo = _staleable_repo(tmp_path, name="source-like")
    builder = repo / "scripts" / "build_retro_lesson_selection_index.py"
    builder.parent.mkdir(parents=True, exist_ok=True)
    builder.write_text("# stand-in for this repo's own builder\n", encoding="utf-8")
    # BOTH conditions, matching `helper_provenance_lib.is_charness_source_tree`. The
    # checked-in `plugins/charness/` export owns the builder and carries no packaging
    # manifest, so a file test alone printed this warning for a target the provenance
    # guard treats as a plain consuming repo.
    marker = repo / "packaging" / "charness.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text('{"package_id": "charness"}\n', encoding="utf-8")

    message = _stale_index_message(repo)

    assert "FIRST, check who wrote it" in message
    # The TARGET repo's own builder, spelled absolutely because the operator's cwd is
    # not that tree: a relative `scripts/...` beside an absolute `--repo-root` would
    # run THIS checkout's builder against a different one.
    assert f"python3 {repo}/scripts/{lesson_command_citation.INDEX_SCRIPT_NAME} --repo-root {repo} --write" in message


def test_digest_refusal_resolves_the_refresh_script_against_a_tree_that_has_it(tmp_path: Path) -> None:
    """The second failure in #632: `skills/public/retro/` exists in neither tree there.

    The export flattens it to `skills/retro/`, so the hard-coded source spelling was
    wrong relative to BOTH the consuming repo and the installed plugin.
    """
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    command = lesson_command_citation.refresh_digest_command(consumer)
    cited = [word for word in command.split() if word.endswith("refresh_recent_lessons.py")]
    assert cited and Path(cited[0]).is_file(), command


def test_the_generated_export_is_not_treated_as_a_competing_source_tree() -> None:
    """If present, `plugins/charness/` owns the builder and is NOT a source tree.

    Keying the foreign-copy warning on the builder's presence alone made this target
    take the source-tree branch, whose remedy is "run this repo's own copy" -- i.e.
    run the exported builder against the export, the one action the repo's shell gates
    refuse outright. The provenance guard calls this target `consuming-repo`; this
    discriminator has to agree with it.
    """
    export = Path(__file__).resolve().parents[2] / "plugins" / "charness"
    if not (export / "scripts" / lesson_command_citation.INDEX_SCRIPT_NAME).is_file():
        # The generated export is intentionally absent from some source checkouts;
        # absence must still not turn an arbitrary directory into a competing tree.
        assert not lesson_command_citation.repo_carries_index_builder(export)
        return
    assert not lesson_command_citation.repo_carries_index_builder(export)


def test_a_tree_carrying_neither_script_names_a_shape_not_a_dead_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When no tree has the script, cite the SHAPE rather than a path that resolves nowhere.

    A reader handed a nonexistent concrete path cannot tell "I mistyped it" from "this
    file does not ship here", which is the confusion the whole repair exists to end.
    The placeholder is a bare token on purpose: `<...>` in a shell is a redirection, so
    a bracketed one turns "file not found" into a different, wronger error when the
    operator pastes the command.

    `__file__` is repointed rather than the module copied to a bare tree: a copy is a
    different file, so coverage attributes the exercised branch to the copy and the
    real module's arm stays unproven. `script_tree_root()` reads the module global at
    call time, so this reaches the same code.
    """
    bare = tmp_path / "vendored" / "scripts"
    bare.mkdir(parents=True)
    monkeypatch.setattr(
        lesson_command_citation, "__file__", str(bare / "lesson_command_citation.py")
    )
    consumer = tmp_path / "consumer"
    consumer.mkdir()

    index = lesson_command_citation.index_build_command(consumer, "--write")
    digest = lesson_command_citation.refresh_digest_command(consumer)

    token = lesson_command_citation.PLUGIN_DIR_TOKEN
    for command in (index, digest):
        assert command.startswith(f"python3 {token}/"), command
        assert "<" not in command and ">" not in command, command
        assert f"--repo-root {consumer}" in command, command
    assert index.endswith("--write")
    assert lesson_command_citation.INDEX_SCRIPT_RELATIVE.as_posix() in index
    assert "skills/retro/scripts/refresh_recent_lessons.py" in digest


def test_the_reader_s_own_tree_is_cited_relatively(tmp_path: Path) -> None:
    """The other half of the absolute/relative rule, over the real repo root.

    A relative spelling is correct exactly when the reader's cwd IS the tree the script
    lives in; anywhere else it hands back a command that runs THIS checkout's script
    against a different repo.
    """
    command = lesson_command_citation.index_build_command(ROOT_PATH, "--check")

    assert command.startswith(
        f"python3 {lesson_command_citation.INDEX_SCRIPT_RELATIVE.as_posix()} "
    ), command
    assert command.endswith("--check")
