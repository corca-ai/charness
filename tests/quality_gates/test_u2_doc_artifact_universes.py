from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from tests.quality_gates.repo_shapes import install_committed_repo
from tests.script_main import load_script_module, run_loaded_script_main

from .support import ROOT


def _load(relative: str, name: str):
    return load_script_module(name, ROOT / relative)


def _quality_adapter(*, universes: str) -> str:
    return (
        "version: 1\n"
        "repo: consumer\n"
        "language: en\n"
        "output_dir: artifacts/quality\n"
        "universes:\n"
        f"{universes}\n"
    )


def _repo(tmp_path: Path, *, quality_universes: str, files: dict[str, str]) -> Path:
    adapter = _quality_adapter(universes=quality_universes)
    return install_committed_repo(
        tmp_path / "repo",
        {
            ".agents/quality-adapter.yaml": adapter,
            "README.md": "# Outside the declared universe\n\nSee `missing.md`.\n",
            **files,
        },
    )


def test_doc_links_uses_declared_doc_surfaces_and_refuses_empty(tmp_path: Path) -> None:
    gate = _load("scripts/gates/check_doc_links.py", "u2_check_doc_links")
    repo = _repo(
        tmp_path / "seeded",
        quality_universes="  doc_surfaces:\n    - src/**/*.md",
        files={"src/guide.md": "# Guide\n"},
    )

    result = run_loaded_script_main("check_doc_links.py", gate, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "across 1 document(s)" in result.stdout

    empty = _repo(
        tmp_path / "empty",
        quality_universes="  doc_surfaces:\n    - src/missing/**/*.md",
        files={},
    )
    result = run_loaded_script_main("check_doc_links.py", gate, "--repo-root", str(empty))
    assert result.returncode == 1
    assert "check-doc-links: refusing empty declared universe" in result.stderr


def test_docs_graph_uses_declared_doc_root_and_refuses_empty(tmp_path: Path, monkeypatch) -> None:
    gate = _load("scripts/gates/check_docs_graph.py", "u2_check_docs_graph")
    repo = _repo(
        tmp_path / "seeded",
        quality_universes="  doc_surfaces:\n    - src/**/*.md",
        files={"src/guide.md": "# Guide\n"},
    )
    seen: list[str] = []
    monkeypatch.setattr(
        gate,
        "_run_awiki",
        lambda _root, scan_root: (
            seen.append(scan_root),
            (
                0,
                "// ok connected_graph documents=1 orphan_rate=0.0000 "
                "largest_component_ratio=1.0000\n",
            ),
        )[1],
    )
    monkeypatch.setattr(gate.shutil, "which", lambda _name: "awiki")

    result = gate.evaluate(repo)

    assert result["status"] == "pass", result
    assert seen == ["src"]

    empty = _repo(
        tmp_path / "empty",
        quality_universes="  doc_surfaces:\n    - src/missing/**/*.md",
        files={},
    )
    result = gate.evaluate(empty)
    assert result["status"] == "not-run"
    assert "docs-graph: refusing empty declared universe" in result["reason"]


def _doc_duplicate_args(repo: Path) -> Namespace:
    return Namespace(
        repo_root=repo,
        path=None,
        exclude=[],
        baseline=None,
        write_baseline=False,
    )


def test_doc_duplicates_builds_nose_roots_from_declared_doc_surfaces(
    tmp_path: Path, monkeypatch
) -> None:
    gate = _load(
        "skills/public/quality/scripts/inventory_doc_duplicates.py",
        "u2_inventory_doc_duplicates",
    )
    repo = _repo(
        tmp_path / "seeded",
        quality_universes="  doc_surfaces:\n    - src/**/*.md",
        files={"src/guide.md": "# Guide\n"},
    )
    monkeypatch.setattr(gate, "resolve_nose_bin", lambda: "nose")
    monkeypatch.setattr(gate, "nose_version", lambda _nose: (0, 13, 0))
    monkeypatch.setattr(
        gate,
        "run_query",
        lambda _root, command: {
            "status": "ok",
            "families": [],
            "schema_version": 2,
            "stderr": "",
            "command_seen": command,
        },
    )

    payload = gate.payload_for_args(_doc_duplicate_args(repo))

    assert payload["status"] == "ok"
    assert "--root src/guide.md" in payload["command"]
    assert "README.md" not in payload["command"]

    empty = _repo(
        tmp_path / "empty",
        quality_universes="  doc_surfaces:\n    - src/missing/**/*.md",
        files={},
    )
    payload = gate.payload_for_args(_doc_duplicate_args(empty))
    assert payload["status"] == "scope-refused"
    assert "doc-duplicates: refusing empty declared universe" in payload["notes"][0]


def test_spec_evidence_uses_declared_artifact_root_and_refuses_empty(tmp_path: Path) -> None:
    gate = _load("scripts/gates/check_spec_evidence_durability.py", "u2_check_spec_evidence")
    repo = _repo(
        tmp_path / "seeded",
        quality_universes="  artifact_roots:\n    spec: src/spec",
        files={
            "src/spec/selected.md": "# Selected\n\nNo evidence citation.\n",
            "charness-artifacts/spec/ignored.md": (
                "# Ignored\n\nProof: `missing/evidence.json`.\n"
            ),
        },
    )

    result = run_loaded_script_main(
        "check_spec_evidence_durability.py", gate, "--repo-root", str(repo)
    )

    assert result.returncode == 0, result.stderr
    assert "across 1 doc(s)" in result.stdout
    assert "ignored.md" not in result.stderr

    empty = _repo(
        tmp_path / "empty",
        quality_universes="  artifact_roots:\n    spec: src/missing",
        files={},
    )
    result = run_loaded_script_main(
        "check_spec_evidence_durability.py", gate, "--repo-root", str(empty)
    )
    assert result.returncode == 1
    assert "check-spec-evidence-durability: refusing empty declared universe" in result.stderr


def test_artifact_referents_uses_declared_roots_and_keeps_local_context_charness_only(
    tmp_path: Path,
) -> None:
    gate = _load("scripts/gates/check_artifact_referents.py", "u2_check_artifact_referents")
    repo = _repo(
        tmp_path / "seeded",
        quality_universes="  artifact_roots:\n    goals: src/goals",
        files={
            "src/goals/2026-08-25-selected.md": (
                "Structural follow-up: issue #700 (novel: selected)\n"
            ),
            "charness-artifacts/goals/2026-08-25-ignored.md": (
                "Structural follow-up: issue #N (novel: ignored)\n"
            ),
        },
    )

    result = run_loaded_script_main("check_artifact_referents.py", gate, "--repo-root", str(repo))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "scanned: 1 artifact(s)" in result.stdout
    assert "ignored" not in result.stdout

    empty = _repo(
        tmp_path / "empty",
        quality_universes="  artifact_roots:\n    goals: src/missing",
        files={},
    )
    result = run_loaded_script_main("check_artifact_referents.py", gate, "--repo-root", str(empty))
    assert result.returncode == 1
    assert "check-artifact-referents: refusing empty declared universe" in result.stderr


def test_critique_default_is_derived_from_critique_adapter_and_refuses_empty(
    tmp_path: Path, monkeypatch
) -> None:
    gate = _load("scripts/review/validate_critique_artifacts.py", "u2_validate_critique")
    repo = install_committed_repo(
        tmp_path / "seeded",
        {
            ".agents/critique-adapter.yaml": (
                "version: 1\nrepo: consumer\noutput_dir: src/critique\n"
            ),
            "src/critique/2026-08-25-review.md": "# Review\n",
        },
    )
    monkeypatch.setattr(gate, "validate_critique_artifact", lambda *_args, **_kwargs: None)

    result = run_loaded_script_main(
        "validate_critique_artifacts.py", gate, "--repo-root", str(repo), "--all"
    )

    assert result.returncode == 0, result.stderr
    assert "Validated 1 critique artifact(s)." in result.stdout

    empty = install_committed_repo(
        tmp_path / "empty",
        {
            ".agents/critique-adapter.yaml": (
                "version: 1\nrepo: consumer\noutput_dir: src/missing\n"
            ),
            ".agents/quality-adapter.yaml": _quality_adapter(
                universes="  artifact_roots:\n    critique: src/missing"
            ),
        },
    )
    result = run_loaded_script_main(
        "validate_critique_artifacts.py", gate, "--repo-root", str(empty), "--all"
    )
    assert result.returncode == 1
    assert "validate-critique-artifacts: refusing empty declared universe" in result.stderr

    discovered = _repo(tmp_path / "discovered", quality_universes="", files={})
    result = run_loaded_script_main(
        "validate_critique_artifacts.py", gate, "--repo-root", str(discovered), "--all"
    )
    assert result.returncode == 0
    assert "Discovered empty critique artifact universe" in result.stdout


def test_ideation_uses_declared_artifact_root_and_refuses_empty(tmp_path: Path) -> None:
    gate = _load("scripts/gates/validate_ideation_artifact.py", "u2_validate_ideation")
    body = (
        "# Ideation\n\n## Structured Questions\n\n"
        "- Q1 | urgency: defer | depends-on: null | action: hold | note: later\n"
    )
    repo = _repo(
        tmp_path / "seeded",
        quality_universes="  artifact_roots:\n    ideation: src/ideation",
        files={"src/ideation/selected.md": body},
    )
    result = run_loaded_script_main(
        "validate_ideation_artifact.py", gate, "--repo-root", str(repo), "--all"
    )
    assert result.returncode == 0, result.stderr
    assert "Validated 1 ideation artifact(s)." in result.stdout

    empty = _repo(
        tmp_path / "empty",
        quality_universes="  artifact_roots:\n    ideation: src/missing",
        files={},
    )
    result = run_loaded_script_main(
        "validate_ideation_artifact.py", gate, "--repo-root", str(empty), "--all"
    )
    assert result.returncode == 1
    assert "validate-ideation-artifact: refusing empty declared universe" in result.stderr

    discovered = _repo(tmp_path / "discovered", quality_universes="", files={})
    result = run_loaded_script_main(
        "validate_ideation_artifact.py", gate, "--repo-root", str(discovered), "--all"
    )
    assert result.returncode == 0
    assert "Discovered empty ideation artifact universe" in result.stdout


def test_lesson_ledger_reads_retro_adapter_paths_and_optional_absence(tmp_path: Path) -> None:
    gate = _load("scripts/check_lesson_ledger.py", "u2_check_lesson_ledger")
    repo = install_committed_repo(
        tmp_path / "seeded",
        {
            ".agents/retro-adapter.yaml": (
                "version: 1\nrepo: consumer\noutput_dir: src/retro\n"
                "summary_path: src/retro/recent-lessons.md\n"
            ),
            "charness-artifacts/retro/lesson-ledger.json": "not the selected ledger\n",
        },
    )

    result = run_loaded_script_main("check_lesson_ledger.py", gate, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "src/retro/lesson-ledger.json" in result.stdout
    assert "missing lesson ledger" not in result.stderr

    empty = _repo(
        tmp_path / "empty",
        quality_universes="  artifact_roots:\n    retro: src/missing",
        files={},
    )
    result = run_loaded_script_main("check_lesson_ledger.py", gate, "--repo-root", str(empty))
    assert result.returncode == 1
    assert "validate-lesson-ledger: refusing empty declared universe" in result.stderr
