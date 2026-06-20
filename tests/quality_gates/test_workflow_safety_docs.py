from __future__ import annotations

from .support import ROOT


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_achieve_lifecycle_classifies_post_checkpoint_commits() -> None:
    lifecycle = _read("skills/public/achieve/references/lifecycle.md")
    normalized = " ".join(lifecycle.split())

    assert "Post-Checkpoint Commit Classification" in lifecycle
    assert "runtime-affecting" in lifecycle
    assert "test-only" in lifecycle
    assert "audit-doc-only" in lifecycle
    assert "Any uncertain commit is `runtime-affecting`" in normalized
    assert "HEAD` differs from the live instance" in lifecycle


def test_quality_reference_carries_ci_only_recovery_protocol() -> None:
    reference = _read("skills/public/quality/references/maintainer-local-enforcement.md")

    assert "CI-Only Failure Recovery" in reference
    assert "workflow, job, failed step, failing test, and exact command" in reference
    assert "shell, OS image, tool versions, environment variables" in reference
    assert "targeted local reproduction" in reference
    assert "does not weaken the initial broad gate" in reference


def test_implementation_discipline_mentions_symbol_residue_advisory() -> None:
    discipline = _read("docs/conventions/implementation-discipline.md")

    assert "check_symbol_residue.py" in discipline
    assert "advisory by design (#259)" in discipline
    assert "docs/" in discipline and "skills/" in discipline
