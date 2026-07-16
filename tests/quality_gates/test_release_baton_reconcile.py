"""Post-publish baton reconcile observation (the v1.0.9–v1.0.11 stale-handoff
recurrence): the release closeout records which versions the session baton's
routing sections claim, forces the question when the published version is
absent, and never reads historical mentions outside those sections as claims.
"""
from __future__ import annotations

from pathlib import Path

from .release_script_loading import load_release_script

_BATON = load_release_script("publish_release_baton", suffix="baton_test")
_SECTIONS = load_release_script("publish_release_artifact_sections", suffix="baton_test")

BATON_DOC = """# Handoff

## Workflow Trigger

- With no explicit task, run the chunker.

## Current State

- v1.0.8 is public at tag `f1b0009e`.
- The installed CLI reads 1.0.8.

## Next Session

1. Restart before installed-behavior judgment.

## References

- [v1.0.11 notes](notes.md) and v9.9.9 folklore live outside the fence.
"""


def _write_baton(tmp_path: Path, text: str) -> dict[str, str]:
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "handoff.md").write_text(text, encoding="utf-8")
    return {"post_publish_baton_path": "docs/handoff.md"}


def test_not_configured_when_adapter_declares_no_baton(tmp_path: Path) -> None:
    record = _BATON.evaluate_baton_reconcile(tmp_path, {}, target_version="1.0.11")
    assert record == {"status": "not_configured"}


def test_missing_baton_file_forces_the_question(tmp_path: Path) -> None:
    adapter = {"post_publish_baton_path": "docs/handoff.md"}
    record = _BATON.evaluate_baton_reconcile(tmp_path, adapter, target_version="1.0.11")
    assert record["status"] == "missing_file"
    assert "docs/handoff.md" in record["required_action"]


def test_stale_baton_reports_only_fenced_section_claims(tmp_path: Path) -> None:
    adapter = _write_baton(tmp_path, BATON_DOC)
    record = _BATON.evaluate_baton_reconcile(tmp_path, adapter, target_version="1.0.11")
    assert record["status"] == "stale"
    # References-section mentions (1.0.11, 9.9.9) never count as claims.
    assert record["observed_versions"] == ["1.0.8"]
    assert "1.0.11" in record["required_action"]


def test_observed_current_when_routing_sections_claim_the_published_version(tmp_path: Path) -> None:
    adapter = _write_baton(tmp_path, BATON_DOC.replace("1.0.8", "1.0.11"))
    record = _BATON.evaluate_baton_reconcile(tmp_path, adapter, target_version="1.0.11")
    assert record["status"] == "observed-current"
    assert "required_action" not in record


def test_no_version_claim_is_an_ask_not_a_pass(tmp_path: Path) -> None:
    doc = "# Handoff\n\n## Current State\n\n- clean tree, no release claims.\n\n## References\n\n- v1.0.8 history.\n"
    adapter = _write_baton(tmp_path, doc)
    record = _BATON.evaluate_baton_reconcile(tmp_path, adapter, target_version="1.0.11")
    assert record["status"] == "no_version_claim"
    assert record["required_action"]


def test_renderer_carries_the_forced_question_and_never_a_terminal_green() -> None:
    stale = {
        "status": "stale",
        "path": "docs/handoff.md",
        "target_version": "1.0.11",
        "observed_versions": ["1.0.8"],
        "required_action": "Reconcile `docs/handoff.md` to `1.0.11`.",
    }
    rendered = "\n".join(_SECTIONS.baton_reconcile_lines(stale))
    assert "## Baton Reconcile" in rendered
    assert "RECONCILE REQUIRED" in rendered
    assert "observation, not completion" in rendered

    current = dict(stale, status="observed-current", observed_versions=["1.0.11"])
    current.pop("required_action")
    rendered_current = "\n".join(_SECTIONS.baton_reconcile_lines(current))
    assert "RECONCILE REQUIRED" not in rendered_current
    assert "observation, not completion" in rendered_current

    no_claim = {
        "status": "no_version_claim",
        "path": "docs/handoff.md",
        "target_version": "1.0.11",
        "observed_versions": [],
        "required_action": "Reconcile `docs/handoff.md` to `1.0.11`.",
    }
    rendered_no_claim = "\n".join(_SECTIONS.baton_reconcile_lines(no_claim))
    assert "claim no release version" in rendered_no_claim
    assert "RECONCILE REQUIRED" in rendered_no_claim

    assert "not recorded by this helper invocation" in "\n".join(_SECTIONS.baton_reconcile_lines(None))
    assert "nothing to reconcile" in "\n".join(_SECTIONS.baton_reconcile_lines({"status": "not_configured"}))


def test_adapter_accepts_and_defaults_the_baton_path_field() -> None:
    resolver = load_release_script("resolve_adapter", suffix="baton_test")
    defaults = resolver.infer_repo_defaults(Path("/tmp/demo"))
    assert defaults["post_publish_baton_path"] == ""
    validated, errors, _warnings = resolver.validate_adapter_data(
        {"post_publish_baton_path": "docs/handoff.md"}, Path("/tmp/demo")
    )
    assert not errors
    assert validated["post_publish_baton_path"] == "docs/handoff.md"
