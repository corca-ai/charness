from __future__ import annotations

import json
import runpy
from argparse import Namespace
from pathlib import Path

from tests.quality_gates.support import ROOT, run_script

SCRIPT = "skills/public/issue/scripts/issue_tool.py"


def _bug_body(close_line: str = "Close #42.") -> str:
    return "\n\n".join(
        [
            close_line,
            "JTBD: resolve GitHub issues end-to-end.",
            "Root cause: the issue closeout carrier was prose-only.",
            "Debug artifact: cite-only.",
            "Siblings: issue_tool finalization | decision: same bug, fix now | proof: static scan.",
            "Prevention: validate-closeout-draft blocks malformed bodies before mutation.",
            "Critique: blocked synthetic-test-harness: this test does not spawn a real reviewer",
            "Behavior #42: behavior test exercises the fix (distinct channel from CLOSED)",
            "AI-provenance: agent-drafted; human-audited per the resolution critique",
        ]
    )


def test_validate_closeout_draft_command_delegates_to_backend_runner(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / "skills/public/issue/scripts/issue_validate_closeout_draft.py"))
    verifier = runpy.run_path(str(ROOT / "skills/public/issue/scripts/issue_verify_closeout.py"))
    command = module["command_validate_closeout_draft"]
    body = tmp_path / "closeout.md"
    body.write_text(_bug_body(), encoding="utf-8")
    calls: list[dict[str, object]] = []

    def run_backend_command(args: Namespace, call: object, exit_code: object) -> int:
        calls.append({"repo": args.repo, "verifier": "injected"})
        result = call({"backend": {"id": "fake-gh"}})
        return exit_code(result)

    rc = command(
        Namespace(
            repo_root=tmp_path,
            repo="corca-ai/charness",
            number=[42],
            classification="bug",
            carrier="pr-body",
            body_file=body,
            commit_message_file=None,
            manual_fallback_reason=None,
        ),
        run_backend_command=run_backend_command,
        verifier=Namespace(verify_closeout=verifier["verify_closeout"]),
    )

    assert rc == 0
    assert calls == [{"repo": "corca-ai/charness", "verifier": "injected"}]


def test_validate_closeout_draft_accepts_pr_body_before_state_mutation(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(_bug_body(), encoding="utf-8")

    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--body-file",
        str(body),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["draft"] is True
    assert payload["status"] == "draft_verified"
    assert payload["verified_state"] == []
    assert payload["publication_status"] == "ready_to_publish"


def test_validate_closeout_draft_accepts_direct_commit_message_before_push(
    tmp_path: Path,
) -> None:
    commit_message = tmp_path / "commit-message.txt"
    commit_message.write_text(_bug_body(), encoding="utf-8")

    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--carrier",
        "direct-commit",
        "--commit-message-file",
        str(commit_message),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["carrier"] == "direct-commit"
    assert payload["draft"] is True
    assert payload["status"] == "draft_verified"
    assert payload["publication_status"] == "ready_to_commit_push"
    assert payload["verified_state"] == []
    assert payload["commit_message_file"] == str(commit_message)


def test_validate_closeout_draft_direct_commit_requires_message_file(
    tmp_path: Path,
) -> None:
    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--carrier",
        "direct-commit",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert "direct-commit draft requires --commit-message-file" in payload["error"]


def test_validate_closeout_draft_rejects_missing_ledger_before_mutation(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text("Close #42.\n\nJTBD: too thin.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--body-file",
        str(body),
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "draft_failed"
    assert set(payload["missing_fields"]) >= {"root_cause", "debug_artifact", "siblings", "prevention"}


def _write_proof_adapter(tmp_path: Path) -> None:
    target = tmp_path / ".agents" / "proof-semantics-adapter.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "proof_levels:\n  - smoke\n  - integration\n  - live\n"
        "acceptance_map:\n  reliability: integration\n",
        encoding="utf-8",
    )


_PROOF_LEDGER_HEAD = (
    "\n\n## Proof Ledger\n\n"
    "| Acceptance Class | Reached Proof | Disposition |\n| --- | --- | --- |\n"
)


def test_validate_closeout_draft_blocks_undispositioned_proof_gap(tmp_path: Path) -> None:
    # The maintainer's scenario: acceptance class `reliability` requires `integration`
    # but the reached proof is `smoke` (local simulation) and the gap is undispositioned.
    _write_proof_adapter(tmp_path)
    body = tmp_path / "closeout.md"
    body.write_text(_bug_body() + _PROOF_LEDGER_HEAD + "| reliability | smoke | |\n", encoding="utf-8")

    result = run_script(
        SCRIPT, "validate-closeout-draft", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42", "--classification", "bug",
        "--body-file", str(body),
    )
    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "draft_failed"
    assert payload["proof_mismatch"]["problem"] == "mismatch"
    assert payload["proof_mismatch"]["undispositioned"][0]["gap_kind"] == "proof-below-acceptance"


def test_validate_closeout_draft_accepts_dispositioned_proof_gap(tmp_path: Path) -> None:
    _write_proof_adapter(tmp_path)
    body = tmp_path / "closeout.md"
    body.write_text(
        _bug_body() + _PROOF_LEDGER_HEAD
        + "| reliability | smoke | accepted-risk: live roundtrip a non-claim this run |\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT, "validate-closeout-draft", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42", "--classification", "bug",
        "--body-file", str(body),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert "proof_mismatch" not in payload


def test_validate_closeout_draft_accepts_manual_fallback_body(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(
        _bug_body("Manual close comment.")
        + "\n\nManual fallback reason: auto-close unsupported by host backend.\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "validate-closeout-draft",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--carrier",
        "manual-fallback",
        "--manual-fallback-reason",
        "auto-close-unsupported",
        "--body-file",
        str(body),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["carrier"] == "manual-fallback"
