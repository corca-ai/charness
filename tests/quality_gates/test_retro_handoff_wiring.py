from __future__ import annotations

import runpy
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts import validate_retro_handoff_wiring as wiring

GOAL = "charness-artifacts/goals/demo-goal.md"
RETRO = "charness-artifacts/retro/demo-retro.md"
HANDOFF = "docs/handoff.md"


def _seed(
    root: Path,
    *,
    retro_goal: str = GOAL,
    retro_body: str = "- workflow: keep the packet bound (recurrence-class: packet-binding)",
    handoff_body: str = "- carry `recurrence-class: packet-binding` into the next review",
    link_target: str = f"../{RETRO}",
) -> None:
    (root / GOAL).parent.mkdir(parents=True, exist_ok=True)
    (root / GOAL).write_text("# Demo Goal\n", encoding="utf-8")
    (root / RETRO).parent.mkdir(parents=True, exist_ok=True)
    (root / RETRO).write_text(
        "\n".join(
            [
                "# Demo Retro",
                "Date: 2026-08-06",
                f"Goal: {retro_goal}",
                "",
                "## Next Improvements",
                "",
                retro_body,
                "",
                "## Persisted",
                "",
                f"Persisted: yes: {RETRO}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / HANDOFF).parent.mkdir(parents=True, exist_ok=True)
    (root / HANDOFF).write_text(
        "\n".join(
            [
                "# Demo Handoff",
                "",
                "## Next Session",
                "",
                f"- Read the [goal-bound retro]({link_target}).",
                handoff_body,
                "",
            ]
        ),
        encoding="utf-8",
    )


def _run(root: Path) -> dict[str, object]:
    return wiring.validate_wiring(
        root,
        goal_path=GOAL,
        retro_path=RETRO,
        handoff_path=HANDOFF,
    )


def test_bound_retro_and_exact_marker_pass(tmp_path: Path) -> None:
    _seed(tmp_path)

    report = _run(tmp_path)

    assert report["status"] == "passed"
    assert report["retro_citations"] == [RETRO]
    assert report["retro_markers"] == ["packet-binding"]
    assert report["missing_markers"] == []
    assert "prose meaning" in report["non_claims"][0]


def test_wrong_goal_fails_closed(tmp_path: Path) -> None:
    _seed(tmp_path, retro_goal="charness-artifacts/goals/other-goal.md")

    report = _run(tmp_path)

    assert report["status"] == "failed"
    assert any(error["code"] == "retro_goal_mismatch" for error in report["errors"])


def test_missing_retro_citation_fails_even_without_markers(tmp_path: Path) -> None:
    _seed(
        tmp_path,
        retro_body="- workflow: no stable marker is available",
        handoff_body="- carry the bounded lesson into the next review",
    )
    (tmp_path / HANDOFF).write_text(
        "# Demo Handoff\n\n## Next Session\n\n- carry the bounded lesson into the next review\n",
        encoding="utf-8",
    )

    report = _run(tmp_path)

    assert report["status"] == "failed"
    assert any(error["code"] == "retro_not_cited" for error in report["errors"])
    assert report["retro_markers"] == []


def test_missing_marker_fails_without_prose_matching(tmp_path: Path) -> None:
    _seed(tmp_path, handoff_body="- carry the packet binding lesson")

    report = _run(tmp_path)

    assert report["status"] == "failed"
    assert any(error["code"] == "recurrence_markers_missing" for error in report["errors"])


def test_blockquoted_marker_cannot_satisfy_coverage(tmp_path: Path) -> None:
    _seed(tmp_path, handoff_body="> - quoted example `recurrence-class: packet-binding`")

    report = _run(tmp_path)

    assert report["status"] == "failed"
    assert any(error["code"] == "recurrence_markers_missing" for error in report["errors"])


def test_wrapped_marker_is_covered_as_one_bullet(tmp_path: Path) -> None:
    _seed(tmp_path, handoff_body="- carry recurrence-class:\n  packet-binding")

    report = _run(tmp_path)

    assert report["status"] == "passed"
    assert report["missing_markers"] == []


def test_ordered_next_session_items_are_covered(tmp_path: Path) -> None:
    _seed(tmp_path)
    (tmp_path / HANDOFF).write_text(
        "# Demo Handoff\n\n"
        "## Next Session\n\n"
        f"1. [Read the retro]({Path('../' + RETRO)})\n"
        "2. carry recurrence-class: packet-binding\n",
        encoding="utf-8",
    )

    report = _run(tmp_path)

    assert report["status"] == "passed"
    assert report["retro_citations"] == [RETRO]
    assert report["missing_markers"] == []


def test_lazy_blockquote_continuation_cannot_satisfy_coverage(tmp_path: Path) -> None:
    _seed(
        tmp_path,
        handoff_body="> - quoted example\n  recurrence-class: packet-binding",
    )

    report = _run(tmp_path)

    assert report["status"] == "failed"
    assert any(error["code"] == "recurrence_markers_missing" for error in report["errors"])


def test_lazy_blockquote_continuation_cannot_cite_retro(tmp_path: Path) -> None:
    _seed(tmp_path)
    (tmp_path / HANDOFF).write_text(
        "# Demo Handoff\n\n"
        "## Next Session\n\n"
        f"> - [quoted retro]({Path('../' + RETRO)})\n"
        "  recurrence-class: packet-binding\n",
        encoding="utf-8",
    )

    report = _run(tmp_path)

    assert report["status"] == "failed"
    assert any(error["code"] == "retro_not_cited" for error in report["errors"])
    assert any(error["code"] == "recurrence_markers_missing" for error in report["errors"])


def test_lazy_blockquote_continuation_cannot_declare_goal(tmp_path: Path) -> None:
    _seed(tmp_path)
    (tmp_path / RETRO).write_text(
        "# Demo Retro\n"
        "> Date: 2026-08-06\n"
        f"  Goal: {GOAL}\n\n"
        "## Next Improvements\n\n"
        "- no stable marker\n",
        encoding="utf-8",
    )

    report = _run(tmp_path)

    assert report["status"] == "failed"
    assert any(error["code"] == "retro_goal_missing" for error in report["errors"])


def test_escaped_relative_citation_is_not_laundered(tmp_path: Path) -> None:
    _seed(tmp_path, link_target="../../charness-artifacts/retro/demo-retro.md")

    report = _run(tmp_path)

    assert report["status"] == "failed"
    assert any(error["code"] == "citation_path_escape" for error in report["errors"])


def test_fenced_marker_is_not_an_obligation(tmp_path: Path) -> None:
    _seed(
        tmp_path,
        retro_body="````markdown\n- fake (recurrence-class: quoted-example)\n````",
        handoff_body="- the retro has no stable recurrence marker",
    )

    report = _run(tmp_path)

    assert report["status"] == "passed"
    assert report["retro_markers"] == []
    assert report["marker_obligations"] == "none declared by retro"


def test_source_and_plugin_copies_are_identical() -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "scripts/validate_retro_handoff_wiring.py"
    plugin = root / "plugins/charness/scripts/validate_retro_handoff_wiring.py"

    assert source.read_bytes() == plugin.read_bytes()


def test_plugin_copy_help_runs() -> None:
    root = Path(__file__).resolve().parents[2]
    plugin = root / "plugins/charness/scripts/validate_retro_handoff_wiring.py"

    result = subprocess.run(
        [sys.executable, str(plugin), "--help"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--goal-path" in result.stdout


def test_helper_masks_fences_quotes_and_all_list_markers() -> None:
    assert wiring._mask_fences(["before", "```", "inside", "```", "after"]) == [
        "before", "", "", "", "after"
    ]
    assert wiring._authored_lines(["> quoted", "1. authored", "", "* own"]) == [
        "", "1. authored", "", "* own"
    ]
    assert wiring._bullet_items(["> ignored", "1. first", "  continuation", "+ second"]) == [
        "first continuation", "second"
    ]


def test_helper_path_and_link_edge_cases(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert wiring._repo_file(tmp_path, "missing.md", "demo")[2]
    directory = tmp_path / "directory"
    directory.mkdir()
    assert wiring._repo_file(tmp_path, "directory", "demo")[2]
    assert wiring._normalize_reference(
        "../../outside.md", artifact_path=tmp_path / "retro" / "demo.md", repo_root=tmp_path
    )[1]
    paths, escaped = wiring._link_paths(
        "[web](https://example.test) [mail](mailto:test@example.test) [local](../retro/demo.md) [bad](../../outside)",
        handoff_path=tmp_path / HANDOFF,
        repo_root=tmp_path,
    )
    assert paths == ["retro/demo.md"]
    assert escaped == ["../../outside"]
    monkeypatch.setattr(wiring.Path, "is_file", lambda _path: False)
    with pytest.raises(ImportError, match="path normalizer"):
        wiring._load_handoff_paths()


def test_validate_wiring_rejects_invalid_paths_and_goal_escape(tmp_path: Path) -> None:
    report = wiring.validate_wiring(
        tmp_path,
        goal_path="missing-goal.md",
        retro_path="missing-retro.md",
        handoff_path="missing-handoff.md",
    )
    assert report["status"] == "failed"
    assert len(report["errors"]) == 3
    _seed(tmp_path, retro_goal="../../../outside-goal.md")
    escaped = _run(tmp_path)
    assert any(error["code"] == "retro_goal_path_escape" for error in escaped["errors"])
    (tmp_path / HANDOFF).write_text("# Demo Handoff\n", encoding="utf-8")
    missing_next = _run(tmp_path)
    assert any(error["code"] == "next_session_missing" for error in missing_next["errors"])


def test_validate_wiring_main_and_source_entrypoint(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    _seed(tmp_path)
    argv = [
        "--repo-root", str(tmp_path), "--goal-path", GOAL,
        "--retro-path", RETRO, "--handoff-path", HANDOFF,
    ]
    assert wiring.main(argv) == 0
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "passed"
    assert wiring.main([
        "--repo-root", str(tmp_path), "--goal-path", "missing",
        "--retro-path", RETRO, "--handoff-path", HANDOFF,
    ]) == 1
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "failed"
    source = Path(__file__).resolve().parents[2] / "scripts/validate_retro_handoff_wiring.py"
    monkeypatch.setattr(sys, "argv", [str(source), *argv])
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(source), run_name="__main__")
    assert exc_info.value.code == 0
