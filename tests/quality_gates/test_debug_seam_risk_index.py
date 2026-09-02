from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from runtime_bootstrap import import_repo_module

from .support import ROOT, run_script

SCRIPT = "scripts/retro_debug/build_debug_seam_risk_index.py"
_build_debug_seam_risk_index = import_repo_module(ROOT / SCRIPT, "scripts.retro_debug.build_debug_seam_risk_index")


def run_debug_seam_risk_index(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [SCRIPT, *args])
    try:
        code = _build_debug_seam_risk_index.main()
    except _build_debug_seam_risk_index.ValidationError as exc:
        print(str(exc), file=sys.stderr)
        code = 1
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def seed_repo(tmp_path: Path, *artifacts: tuple[str, str]) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: demo",
                "language: en",
                "output_dir: charness-artifacts/debug",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for filename, body in artifacts:
        (debug_dir / filename).write_text(body, encoding="utf-8")
    return repo


def debug_artifact(
    *,
    interrupt_id: str = "host-seam",
    risk_class: str = "external-seam",
    seam: str = "host-api",
    generalization_pressure: str = "factor-now",
) -> str:
    return (
        "\n".join(
            [
                "# Debug Review",
                "Date: 2026-04-22",
                "",
                "## Problem",
                "",
                "problem",
                "",
                "## Correct Behavior",
                "",
                "correct",
                "",
                "## Observed Facts",
                "",
                "- fact",
                "",
                "## Reproduction",
                "",
                "repro",
                "",
                "## Candidate Causes",
                "",
                "- one",
                "- two",
                "- three",
                "",
                "## Hypothesis",
                "",
                "hypothesis",
                "",
                "## Verification",
                "",
                "verification",
                "",
                "## Root Cause",
                "",
                "root cause",
                "",
                "## Seam Risk",
                "",
                f"- Interrupt ID: {interrupt_id}",
                f"- Risk Class: {risk_class}",
                f"- Seam: {seam}",
                "- Disproving Observation: host behavior disproves local reasoning",
                "- What Local Reasoning Cannot Prove: live host semantics",
                f"- Generalization Pressure: {generalization_pressure}",
                "",
                "## Interrupt Decision",
                "",
                "- Critique Required: yes",
                "- Next Step: spec",
                "- Handoff Artifact: charness-artifacts/spec/host-seam.md",
                "",
                "## Prevention",
                "",
                "prevention",
                "",
            ]
        )
        + "\n"
    )


def legacy_debug_artifact() -> str:
    return (
        "\n".join(
            [
                "# Legacy Debug Review",
                "Date: 2026-04-10",
                "",
                "## Problem",
                "",
                "legacy",
                "",
            ]
        )
        + "\n"
    )


def test_build_debug_seam_risk_index_writes_source_linked_entries(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        ("2026-04-22-host-seam.md", debug_artifact()),
        ("2026-04-10-legacy.md", legacy_debug_artifact()),
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--write")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    # `status` is what the dropped "Wrote <path>." line said and the bare path does
    # not: this run REWROTE the index rather than reporting an existing one.
    assert payload["status"] == "written"
    assert payload["index_path"] == "charness-artifacts/debug/seam-risk-index.json"

    index = json.loads((repo / payload["index_path"]).read_text(encoding="utf-8"))
    assert index["score_policy"].startswith("none:")
    assert index["source_artifact_count"] == 2
    assert index["indexed_artifact_count"] == 1
    assert index["risk_class_counts"] == {"external-seam": 1}
    assert index["generalization_pressure_counts"] == {"factor-now": 1}
    assert index["entries"][0]["artifact_path"] == "charness-artifacts/debug/2026-04-22-host-seam.md"
    assert index["entries"][0]["forced"] is True
    assert index["skipped_artifacts"] == [
        {
            "artifact_path": "charness-artifacts/debug/2026-04-10-legacy.md",
            "reason": "debug artifact has no risk interrupt sections yet",
        }
    ]


def test_build_debug_seam_risk_index_check_rejects_stale_index(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(tmp_path, ("2026-04-22-host-seam.md", debug_artifact()))
    stale = repo / "charness-artifacts" / "debug" / "seam-risk-index.json"
    stale.write_text("{}\n", encoding="utf-8")
    result = run_debug_seam_risk_index(monkeypatch, capsys, "--repo-root", str(repo), "--check")
    assert result.returncode == 1
    assert "debug seam-risk index" in result.stderr
    assert "--write" in result.stderr


def test_a_symlinked_pointer_indexes_one_interrupt_not_two(tmp_path: Path, monkeypatch, capsys) -> None:
    """One file reached by two names was counted twice, inflating every tally.

    Where `latest.md` is a symlink -- the ordinary layout -- the glob yields the pointer
    AND its target, so a single interrupt produced two entries (`is_current_pointer`
    true and false) and was double-counted in `risk_class_counts`,
    `generalization_pressure_counts` and `indexed_artifact_count`. A reader cannot see
    that inflation from the output, which is what makes it worth a test rather than a
    note: this is a reporting surface, so the failure is a confidently wrong number.
    """
    repo = seed_repo(tmp_path, ("2026-04-22-host-seam.md", debug_artifact()))
    debug_dir = repo / "charness-artifacts" / "debug"
    (debug_dir / "latest.md").symlink_to("2026-04-22-host-seam.md")

    result = run_debug_seam_risk_index(monkeypatch, capsys, "--repo-root", str(repo), "--write")
    assert result.returncode == 0, result.stderr
    index = json.loads((debug_dir / "seam-risk-index.json").read_text(encoding="utf-8"))

    assert index["indexed_artifact_count"] == 1
    assert len(index["entries"]) == 1
    assert index["risk_class_counts"] == {"external-seam": 1}
    assert index["generalization_pressure_counts"] == {"factor-now": 1}
    # The POINTER's name survives, because it is the role-bearing one: dropping it in
    # favour of the target would leave the index with no current-pointer entry at all.
    assert index["entries"][0]["artifact_path"] == "charness-artifacts/debug/latest.md"
    assert index["entries"][0]["is_current_pointer"] is True


@pytest.mark.parametrize("pointer_kind", ["byte-copy", "hard-link"])
def test_a_nonsymlink_pointer_indexes_one_interrupt_not_two(
    tmp_path: Path, monkeypatch, capsys, pointer_kind: str
) -> None:
    repo = seed_repo(tmp_path, ("2026-04-22-host-seam.md", debug_artifact()))
    debug_dir = repo / "charness-artifacts" / "debug"
    target = debug_dir / "2026-04-22-host-seam.md"
    pointer = debug_dir / "latest.md"
    if pointer_kind == "byte-copy":
        pointer.write_bytes(target.read_bytes())
    else:
        pointer.hardlink_to(target)

    result = run_debug_seam_risk_index(
        monkeypatch, capsys, "--repo-root", str(repo), "--write"
    )

    assert result.returncode == 0, result.stderr
    index = json.loads((debug_dir / "seam-risk-index.json").read_text(encoding="utf-8"))
    assert index["source_artifact_count"] == 1
    assert index["indexed_artifact_count"] == 1
    assert index["risk_class_counts"] == {"external-seam": 1}
    assert index["entries"][0]["artifact_path"] == "charness-artifacts/debug/latest.md"
    assert index["entries"][0]["is_current_pointer"] is True


def test_an_unreadable_pointer_does_not_invent_copy_identity(
    tmp_path: Path, monkeypatch
) -> None:
    repo = seed_repo(tmp_path, ("2026-04-22-host-seam.md", debug_artifact()))
    debug_dir = repo / "charness-artifacts" / "debug"
    target = debug_dir / "2026-04-22-host-seam.md"
    pointer = debug_dir / "latest.md"
    pointer.write_bytes(target.read_bytes())
    original_read_bytes = Path.read_bytes

    def refuse_pointer(path: Path) -> bytes:
        if path == pointer:
            raise OSError("pointer unavailable")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", refuse_pointer)

    assert _build_debug_seam_risk_index._copied_pointer_target([target, pointer]) is None


def test_an_unreadable_candidate_does_not_invent_copy_identity(
    tmp_path: Path, monkeypatch
) -> None:
    repo = seed_repo(tmp_path, ("2026-04-22-host-seam.md", debug_artifact()))
    debug_dir = repo / "charness-artifacts" / "debug"
    target = debug_dir / "2026-04-22-host-seam.md"
    pointer = debug_dir / "latest.md"
    pointer.write_bytes(target.read_bytes())
    original_read_bytes = Path.read_bytes

    def refuse_candidate(path: Path) -> bytes:
        if path == target:
            raise OSError("candidate unavailable")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", refuse_candidate)

    assert _build_debug_seam_risk_index._copied_pointer_target([target, pointer]) is None


def test_the_index_never_indexes_itself(tmp_path: Path, monkeypatch, capsys) -> None:
    # `seam-risk-index.md` lives in the same directory and matches the `*.md` glob, so
    # without the skip the index would ingest its own previous output -- growing a row
    # per run and reporting a count of artifacts that includes a report. The dedupe
    # rewrite moved this guard, so it is pinned rather than assumed to have survived.
    repo = seed_repo(tmp_path, ("2026-04-22-host-seam.md", debug_artifact()))
    debug_dir = repo / "charness-artifacts" / "debug"
    (debug_dir / "seam-risk-index.md").write_text("# Seam Risk Index\n\nprevious output\n", encoding="utf-8")

    result = run_debug_seam_risk_index(monkeypatch, capsys, "--repo-root", str(repo), "--write")
    assert result.returncode == 0, result.stderr
    index = json.loads((debug_dir / "seam-risk-index.json").read_text(encoding="utf-8"))

    listed = [entry["artifact_path"] for entry in index["entries"]]
    skipped = [row["artifact_path"] for row in index["skipped_artifacts"]]
    assert not any("seam-risk-index" in path for path in listed + skipped)
    assert index["source_artifact_count"] == 1


def test_invalid_artifacts_are_reported_as_one_complete_batch(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    first = debug_artifact(interrupt_id="first").replace(
        "- Disproving Observation:", "- Disproving observation:"
    )
    second = debug_artifact(interrupt_id="second").replace(
        "- Critique Required: yes", "- Critique Required: yes — review"
    )
    repo = seed_repo(
        tmp_path,
        ("2026-04-22-first.md", first),
        ("2026-04-22-second.md", second),
    )
    malformed = repo / "charness-artifacts" / "debug" / "2026-04-22-malformed.md"
    malformed.write_bytes(b"\xff")
    broken = repo / "charness-artifacts" / "debug" / "2026-04-22-broken.md"
    broken.symlink_to("missing-debug-artifact.md")

    result = run_debug_seam_risk_index(
        monkeypatch, capsys, "--repo-root", str(repo), "--check"
    )

    assert result.returncode == 1
    assert "4 invalid debug seam-risk artifact(s)" in result.stderr
    assert "`charness-artifacts/debug/2026-04-22-broken.md`" in result.stderr
    assert "FileNotFoundError: artifact metadata or content could not be read" in result.stderr
    assert "`charness-artifacts/debug/2026-04-22-malformed.md`" in result.stderr
    assert "UnicodeDecodeError: artifact is not valid UTF-8" in result.stderr
    assert "`charness-artifacts/debug/2026-04-22-first.md`" in result.stderr
    assert "missing required line `- Disproving Observation: ...`" in result.stderr
    assert "`charness-artifacts/debug/2026-04-22-second.md`" in result.stderr
    assert "`Critique Required` must be `yes` or `no`" in result.stderr
    assert str(repo) not in result.stderr
