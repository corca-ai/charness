"""#324 — provider-neutral external-source preservation in issue workflows.

Covers the three acceptance criteria:
  1. a fixture for an issue filed from a Slack-like thread where the immediate
     message references earlier context (``fixtures/slack-thread-source-preservation.json``);
  2. the created issue body preserves source text *or* a re-read obligation
     (``check-source-preservation``);
  3. a closeout path blocks when an external-sourced issue preserves neither
     (``verify-closeout`` / ``validate-closeout-draft``).

`axis: external-source-provider` — Slack is one adapter instance, not the
schema; the check keys on a provider-neutral ``Source origin:`` marker.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from tests.quality_gates.support import run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = _ROOT / "skills" / "public" / "issue" / "scripts" / "fixtures" / "slack-thread-source-preservation.json"
BODY_MODULE_PATH = _ROOT / "skills" / "public" / "issue" / "scripts" / "issue_verify_closeout_body.py"


def _load_body_module():
    spec = importlib.util.spec_from_file_location("issue_source_pres_body", BODY_MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _check_source(tmp_path: Path, body: str, *, require_external: bool):
    body_file = tmp_path / "body.md"
    body_file.write_text(body, encoding="utf-8")
    args = [SCRIPT, "check-source-preservation", "--body-file", str(body_file)]
    if require_external:
        args.append("--require-external")
    return run_script(*args)


def _bug_closeout_body(*, source_block: str, close_line: str = "Close #42.") -> str:
    parts = [
        close_line,
        "JTBD: resolve GitHub issues end-to-end.",
        "Root cause: external-source context was not preserved into the carrier.",
        "Debug artifact: cite-only.",
        "Siblings: issue closeout body | decision: same bug, fix now | proof: static scan.",
        "Prevention: verify-closeout blocks unpreserved external-source closeouts.",
        "Critique: blocked synthetic-test-harness: this test does not spawn a real reviewer",
        "Behavior #42: behavior test exercises the fix (distinct channel from CLOSED)",
        "AI-provenance: agent-drafted; human-audited per the resolution critique",
    ]
    body = "\n\n".join(parts)
    if source_block:
        body += "\n\n" + source_block
    return body


# --- creation-side check (acceptance #1 + #2) ----------------------------------


def test_created_body_with_source_text_passes(tmp_path: Path) -> None:
    result = _check_source(tmp_path, _fixture()["created_body_source_text"], require_external=True)
    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["external_sourced"] is True
    assert "source-text" in payload["forms_present"]


def test_created_body_with_reread_obligation_passes(tmp_path: Path) -> None:
    result = _check_source(tmp_path, _fixture()["created_body_reread"], require_external=True)
    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["forms_present"] == ["re-read-required"]


def test_created_body_unpreserved_external_fails(tmp_path: Path) -> None:
    result = _check_source(tmp_path, _fixture()["created_body_unpreserved"], require_external=True)
    assert result.returncode == 1, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["external_sourced"] is True
    assert payload["missing"] is True
    assert payload["forms_present"] == []


def test_internal_body_is_exempt_noop(tmp_path: Path) -> None:
    result = _check_source(tmp_path, _fixture()["created_body_internal"], require_external=False)
    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["external_sourced"] is False
    assert payload["missing"] is False


def test_require_external_flags_missing_origin_marker(tmp_path: Path) -> None:
    result = _check_source(tmp_path, _fixture()["created_body_internal"], require_external=True)
    assert result.returncode == 1, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["external_marker_missing"] is True


def test_check_source_preservation_missing_body_file(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.md"
    result = run_script(SCRIPT, "check-source-preservation", "--body-file", str(missing))
    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "body file not found" in payload["error"]


def test_degraded_reason_satisfies_contract(tmp_path: Path) -> None:
    body = (
        "## Source\n\n"
        "- Source origin: slack\n"
        "- Source identity: https://corca.slack.com/archives/C0EXAMPLE/p4\n"
        "- Source preservation: degraded\n"
        "- Source degraded reason: slack export access was revoked before resolution\n"
    )
    result = _check_source(tmp_path, body, require_external=True)
    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["forms_present"] == ["degraded"]


# --- closeout-side enforcement (acceptance #3) ---------------------------------


def test_verify_closeout_blocks_unpreserved_external_source(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(
        _bug_closeout_body(source_block="## Source\n\n- Source origin: slack\n- Source identity: https://slack/p4\n"),
        encoding="utf-8",
    )
    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path), "--repo", "corca-ai/charness",
        "--number", "42", "--classification", "bug", "--carrier", "pr-body", "--body-file", str(body),
    )
    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["source_preservation"]["missing"] is True
    # Source preservation is the *only* failure: ledger + keywords are intact.
    assert payload["missing_fields"] == []
    assert payload["missing_close_keywords"] == []


def test_verify_closeout_accepts_preserved_external_source(tmp_path: Path) -> None:
    block = "## Source\n\n- Source origin: slack\n- Source text: > p2: raw timestamp needs a shared time-rendering rule\n"
    body = tmp_path / "closeout.md"
    body.write_text(_bug_closeout_body(source_block=block), encoding="utf-8")
    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path), "--repo", "corca-ai/charness",
        "--number", "42", "--classification", "bug", "--carrier", "pr-body", "--body-file", str(body),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["source_preservation"]["missing"] is False
    assert payload["source_preservation"]["forms_present"] == ["source-text"]


def test_verify_closeout_internal_issue_unaffected(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(_bug_closeout_body(source_block=""), encoding="utf-8")
    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path), "--repo", "corca-ai/charness",
        "--number", "42", "--classification", "bug", "--carrier", "pr-body", "--body-file", str(body),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["source_preservation"]["external_sourced"] is False


def test_validate_closeout_draft_inherits_source_block(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(
        _bug_closeout_body(source_block="## Source\n\n- Source origin: notion\n- Source identity: https://notion/page\n"),
        encoding="utf-8",
    )
    result = run_script(
        SCRIPT, "validate-closeout-draft", "--repo-root", str(tmp_path), "--repo", "corca-ai/charness",
        "--number", "42", "--classification", "bug", "--body-file", str(body),
    )
    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "draft_failed"
    assert payload["source_preservation"]["missing"] is True


# --- pure-function robustness --------------------------------------------------


def test_evaluate_source_preservation_quoted_text_not_misparsed() -> None:
    module = _load_body_module()
    body = (
        "## Source\n\n"
        "- Source origin: slack\n"
        "- Source text: |\n"
        "    > he said: \"fix the timestamp\"\n"
        "    > priority: high\n"
    )
    result = module.evaluate_source_preservation(body)
    assert result["external_sourced"] is True
    assert "source-text" in result["forms_present"]
    assert result["missing"] is False
