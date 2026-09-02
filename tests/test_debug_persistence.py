from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from runtime_bootstrap import import_repo_module
from scripts.core.subprocess_guard import PhaseOutcome

ROOT = Path(__file__).resolve().parents[1]
PERSIST = import_repo_module(
    ROOT / "skills/public/debug/scripts/persist_debug_artifact.py",
    "skills.public.debug.scripts.persist_debug_artifact",
)
VALIDATOR = import_repo_module(
    ROOT / "scripts/gates/validate_debug_artifact.py",
    "scripts.gates.validate_debug_artifact",
)
SCAFFOLD = import_repo_module(
    ROOT / "skills/public/debug/scripts/scaffold_debug_artifact.py",
    "skills.public.debug.scripts.scaffold_debug_artifact",
)


def _valid_current_artifact(*, next_step: str = "impl", risk_class: str = "none") -> str:
    """Keep this authoring test independent of pytest's test-module import path."""
    return "\n".join(
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
            "- falsifiable claim: the gate skips volatile roots | disconfirmer: add `.runtime-cache` to a fixture and assert it is excluded",
            "",
            "## Verification",
            "",
            "verification",
            "",
            "## Root Cause",
            "",
            "root cause",
            "",
            "## Invariant Proof",
            "",
            "- Invariant: n/a - not a workflow-boundary propagation bug",
            "- Producer Proof: n/a",
            "- Final-Consumer Proof: n/a",
            "- Interface-Shape Sibling Scan: n/a",
            "- Non-Claims: n/a",
            "",
            "## Detection Gap",
            "",
            "- test suite | did not assert volatile root exclusion | add `.runtime-cache` to ignore set",
            "",
            "## Sibling Search",
            "",
            "- Mental model: synthetic copy fixtures treat runtime roots as input",
            "- same layer: tests/repo_copy.py and tools/check_coverage.py",
            "- cross-file: tools/check_coverage.py is outside the subject tests/repo_copy.py",
            "",
            "## Seam Risk",
            "",
            "- Interrupt ID: demo-interrupt",
            f"- Risk Class: {risk_class}",
            "- Seam: none",
            "- Disproving Observation: none",
            "- What Local Reasoning Cannot Prove: none",
            "- Generalization Pressure: none",
            "",
            "## Interrupt Decision",
            "",
            f"- Critique Required: {'yes' if next_step == 'spec' else 'no'}",
            f"- Next Step: {next_step}",
            "- Handoff Artifact: none",
            "",
            "## Prevention",
            "",
            "prevention",
            "",
        ]
    )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents/debug-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nlanguage: en\noutput_dir: charness-artifacts/debug\n",
        encoding="utf-8",
    )
    (repo / "charness-artifacts/debug").mkdir(parents=True)
    return repo


def _run(
    repo: Path,
    markdown: str,
    *,
    artifact_path: str = "charness-artifacts/debug/latest.md",
    monkeypatch,
    capsys,
) -> SimpleNamespace:
    source = repo / "candidate.md"
    source.write_text(markdown, encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "persist_debug_artifact.py",
            "--repo-root",
            str(repo),
            "--artifact-path",
            artifact_path,
            "--markdown-file",
            str(source),
        ],
    )
    returncode = PERSIST.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_persist_debug_artifact_validates_the_exact_scaffold_path(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _repo(tmp_path)
    scaffold = SCAFFOLD.payload_for(repo, title=None)
    result = _run(
        repo,
        scaffold["template"],
        artifact_path=str(scaffold["write_artifact_path"]),
        monkeypatch=monkeypatch,
        capsys=capsys,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["action"] == "persisted"
    assert payload["validated"] is True
    assert payload["validation"]["path"] == scaffold["write_artifact_path"]
    assert f"--paths {scaffold['write_artifact_path']}" in payload["validation"]["command"]


def test_persist_debug_artifact_keeps_broad_index_as_a_separate_audit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _repo(tmp_path)
    # An unrelated historical record may retain schema debt. Authoring the new
    # record must still prove the exact path; the broad index remains a later
    # corpus/auditor surface rather than the write boundary.
    (repo / "charness-artifacts/debug/old.md").write_text(
        _valid_current_artifact().replace("- Risk Class: none", "- Risk Class: unknown-risk"),
        encoding="utf-8",
    )

    result = _run(repo, _valid_current_artifact(), monkeypatch=monkeypatch, capsys=capsys)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["validated"] is True
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_debug_artifact.py", "--repo-root", str(repo)],
    )
    with pytest.raises(VALIDATOR.ValidationError, match="old.md"):
        VALIDATOR.main()


def test_persist_debug_artifact_unknown_enum_is_incomplete_and_rolls_back(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _repo(tmp_path)
    prior = _valid_current_artifact()
    target = repo / "charness-artifacts/debug/latest.md"
    target.write_text(prior, encoding="utf-8")

    result = _run(
        repo,
        prior.replace("- Risk Class: none", "- Risk Class: unknown-risk"),
        monkeypatch=monkeypatch,
        capsys=capsys,
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["action"] == "refused"
    assert payload["status"] == "incomplete"
    assert payload["validated"] is False
    assert "--paths charness-artifacts/debug/latest.md" in payload["validation"]["command"]
    assert target.read_text(encoding="utf-8") == prior


def test_persist_debug_artifact_refuses_new_invalid_record_before_index_audit(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = _repo(tmp_path)
    result = _run(
        repo,
        _valid_current_artifact().replace("- Next Step: impl", "- Next Step: factor-first"),
        monkeypatch=monkeypatch,
        capsys=capsys,
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "incomplete"
    assert not (repo / "charness-artifacts/debug/latest.md").exists()


@pytest.mark.parametrize(
    "failure", [FileNotFoundError("missing validator"), subprocess.TimeoutExpired("validator", 1)]
)
def test_persist_debug_artifact_rolls_back_validator_infrastructure_failure(
    tmp_path: Path, monkeypatch, capsys, failure: Exception
) -> None:
    repo = _repo(tmp_path)
    target = repo / "charness-artifacts/debug/latest.md"
    prior = _valid_current_artifact()
    target.write_text(prior, encoding="utf-8")

    def fail(command, **_kwargs):
        if isinstance(failure, subprocess.TimeoutExpired):
            return PhaseOutcome(
                args=command,
                phase="debug-artifact-validator",
                display="validator",
                returncode=124,
                stdout="partial out",
                stderr="timed out after 60s while running `validator`",
                elapsed_seconds=60.0,
                timed_out=True,
            )
        raise failure

    monkeypatch.setattr(PERSIST._persistence, "run_monitored_phase", fail)
    result = _run(repo, prior, monkeypatch=monkeypatch, capsys=capsys)
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "incomplete"
    assert payload["validated"] is False
    assert target.read_text(encoding="utf-8") == prior
