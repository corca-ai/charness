from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path

from tests.quality_gates.support import run_script, write_issue_adapter_with_backend

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
VERIFY_MODULE_PATH = Path(__file__).resolve().parents[2] / "skills" / "public" / "issue" / "scripts" / "issue_verify_closeout.py"


def _load_verify_module():
    spec = importlib.util.spec_from_file_location("issue_verify_closeout_test", VERIFY_MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_commit(repo: Path, body: str) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "codex-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    (repo / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, capture_output=True, text=True)
    command = ["git", "commit", "-m", "Resolve issue"]
    for paragraph in body.split("\n\n"):
        command.extend(["-m", paragraph])
    subprocess.run(command, cwd=repo, check=True, capture_output=True, text=True)


def _bug_closeout_body(
    *,
    close_line: str = "Close #42.",
    critique_line: str | None = (
        "Critique: blocked synthetic-test-harness: this test does not spawn "
        "a real resolution critique subagent"
    ),
    behavior_line: str | None = (
        "Behavior #42: behavior test tests/foo.py exercises the fixed parse path "
        "(distinct channel from CLOSED)"
    ),
    provenance_line: str | None = (
        "AI-provenance: agent-drafted via charness issue resolve; "
        "human-audited per the resolution critique"
    ),
    hotl_line: str | None = None,
) -> str:
    parts = [
        close_line,
        "JTBD: resolve GitHub issues end-to-end.",
        "Root cause: the issue closeout carrier was prose-only.",
        "Debug artifact: charness-artifacts/debug/latest.md.",
        "Siblings: issue_tool finalization | decision: same bug, fix now | proof: static scan.",
        "Prevention: verify-closeout blocks missing carriers.",
    ]
    if critique_line is not None:
        parts.append(critique_line)
    if behavior_line is not None:
        parts.append(behavior_line)
    if provenance_line is not None:
        parts.append(provenance_line)
    if hotl_line is not None:
        parts.append(hotl_line)
    return "\n\n".join(parts)


def test_issue_verify_closeout_rejects_missing_direct_commit_close_keyword(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Resolved work without an auto-close carrier."))

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["missing_close_keywords"] == [42]
    assert payload["missing_fields"] == []


def test_issue_verify_closeout_accepts_direct_commit_carrier_without_final_state(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "carrier_verified"
    assert payload["verified_state"] == []


def test_issue_verify_closeout_uses_github_keyword_boundaries(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #420."))

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["missing_close_keywords"] == [42]


def test_issue_verify_closeout_rejects_wrong_repo_qualified_keyword(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close corca-ai/other#42."))

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["missing_close_keywords"] == [42]


def test_issue_verify_closeout_accepts_matching_repo_qualified_keyword(tmp_path: Path) -> None:
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close corca-ai/charness#42."))

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "carrier_verified"


def test_issue_verify_closeout_accepts_pr_body_carrier(tmp_path: Path) -> None:
    body = tmp_path / "pr-body.md"
    body.write_text(_bug_closeout_body(close_line="Resolves #42."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        "verify-closeout",
        "--repo-root",
        str(tmp_path),
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--classification",
        "bug",
        "--carrier",
        "pr-body",
        "--body-file",
        str(body),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "carrier_verified"


def test_issue_verify_closeout_rejects_empty_bug_sibling_proof(tmp_path: Path) -> None:
    _seed_commit(
        tmp_path,
        "\n\n".join(
            [
                "Close #42.",
                "JTBD: resolve GitHub issues end-to-end.",
                "Root cause: the issue closeout carrier was prose-only.",
                "Debug artifact: charness-artifacts/debug/latest.md.",
                "Siblings: same nearby file.",
                "Prevention: verify-closeout blocks missing carriers.",
                "Behavior #42: behavior test exercises the fix (distinct channel).",
                "AI-provenance: agent-drafted; human-audited per the resolution critique.",
            ]
        ),
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert "siblings_decision_and_proof" in payload["missing_fields"]


def test_issue_verify_closeout_requires_manual_fallback_reason(tmp_path: Path) -> None:
    body = tmp_path / "closeout.md"
    body.write_text(_bug_closeout_body(close_line="Manual close comment."), encoding="utf-8")

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--body-file",
        str(body),
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert "manual-fallback carrier requires --manual-fallback-reason" in payload["error"]


def test_issue_verify_closeout_rejects_open_expected_state(tmp_path: Path) -> None:
    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
        "--expect-state",
        "OPEN",
    )

    assert result.returncode == 2
    assert "invalid choice: 'OPEN'" in result.stderr


def test_issue_verify_closeout_function_rejects_open_expected_state(tmp_path: Path) -> None:
    verify_module = _load_verify_module()

    try:
        verify_module.verify_closeout(
            repo_root=tmp_path,
            repo="corca-ai/charness",
            numbers=[42],
            classification="bug",
            carrier="direct-commit",
            backend={"id": "gh", "binary": "gh", "commands": None},
            commit_ref="HEAD",
            expect_state="OPEN",
        )
    except RuntimeError as exc:
        assert "requires --expect-state CLOSED" in str(exc)
    else:
        raise AssertionError("expected function-level OPEN verification guard")


def test_issue_verify_closeout_uses_adapter_view_for_final_state(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "ceal-log.json"
    fake = bin_dir / "ceal"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "log = Path(os.environ['CEAL_LOG'])",
                "entries = json.loads(log.read_text()) if log.exists() else []",
                "entries.append(sys.argv[1:])",
                "log.write_text(json.dumps(entries))",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42', 'comments': [{'body': os.environ['COMMENT_BODY']}]}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    write_issue_adapter_with_backend(tmp_path, backend_id="ceal-github", binary="ceal")
    adapter_path = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\n".join(
            [
                "    view:",
                "      - github",
                "      - issue",
                "      - view",
                "      - '-R'",
                "      - '{repo}'",
                "      - '{number}'",
                "      - '--json'",
                "      - '{json_fields}'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    body = tmp_path / "closeout.md"
    body_text = (
        _bug_closeout_body(close_line="Manual close comment.")
        + "\nManual close reason: auto-close failed after remote verification.\n"
    )
    body.write_text(body_text, encoding="utf-8")

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--body-file",
        str(body),
        "--manual-fallback-reason",
        "auto-close-failed-after-remote-verification",
        "--expect-state",
        "CLOSED",
        env={
            **os.environ,
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "CEAL_LOG": str(log),
            "COMMENT_BODY": body_text,
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "verified"
    assert payload["verified_state"][0]["state"] == "CLOSED"
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["github", "issue", "view", "-R", "corca-ai/charness", "42", "--json", "number,state,url,comments"] in entries


def test_issue_verify_closeout_rejects_adapter_view_without_target_placeholders(tmp_path: Path) -> None:
    write_issue_adapter_with_backend(tmp_path, backend_id="ceal-github", binary="ceal")
    adapter_path = tmp_path / ".agents" / "issue-adapter.yaml"
    adapter_path.write_text(
        adapter_path.read_text(encoding="utf-8")
        + "\n".join(
            [
                "    view:",
                "      - github",
                "      - issue",
                "      - view",
                "      - '--json'",
                "      - '{json_fields}'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
        "--expect-state",
        "CLOSED",
        env={**os.environ, "PATH": "/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert "missing required placeholders" in payload["error"]
    assert "repo" in payload["error"]
    assert "number" in payload["error"]


def test_issue_verify_closeout_uses_default_gh_comments_for_manual_fallback(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, os, sys",
                "from pathlib import Path",
                "log = Path(os.environ['GH_LOG'])",
                "entries = json.loads(log.read_text()) if log.exists() else []",
                "entries.append(sys.argv[1:])",
                "log.write_text(json.dumps(entries))",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42', 'comments': [{'body': os.environ['COMMENT_BODY']}]}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    body = tmp_path / "closeout.md"
    body_text = (
        _bug_closeout_body(close_line="Manual close comment.")
        + "\nManual close reason: auto-close failed after remote verification.\n"
    )
    body.write_text(body_text, encoding="utf-8")

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--body-file",
        str(body),
        "--manual-fallback-reason",
        "auto-close-failed-after-remote-verification",
        "--expect-state",
        "CLOSED",
        env={
            **os.environ,
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "GH_LOG": str(log),
            "COMMENT_BODY": body_text,
        },
    )

    assert result.returncode == 0, result.stderr
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["issue", "view", "--repo", "corca-ai/charness", "42", "--json", "number,state,url,comments"] in entries


def test_issue_verify_closeout_rejects_wrong_issue_number_from_backend(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 99, 'state': 'CLOSED', 'url': 'https://example.test/99'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
        "--expect-state",
        "CLOSED",
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["state_mismatches"][0]["field"] == "number"


def test_issue_verify_closeout_rejects_open_final_state(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 42, 'state': 'OPEN', 'url': 'https://example.test/42'}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--commit-ref",
        "HEAD",
        "--expect-state",
        "CLOSED",
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["state_mismatches"][0]["actual"] == "OPEN"


# --- rung-1 block-the-silent behavioral-verdict + AI-provenance floors (S1/R2) ---


def test_issue_verify_closeout_rejects_silent_behavioral_verdict(tmp_path: Path) -> None:
    """Seeded escape: a bug carrier silent on the per-issue behavioral verdict
    must FAIL before the CLOSED-state green can stand alone."""
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42.", behavior_line=None))

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["behavioral_verdict"]["ok"] is False
    assert payload["behavioral_verdict"]["missing"] == [42]


def test_issue_verify_closeout_accepts_typed_nonverified_disposition(tmp_path: Path) -> None:
    """Render-not-declare: a typed non-`verified` disposition satisfies the floor
    exactly as a confirmation does — the obligation is to render, not to confirm."""
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #42.",
            behavior_line="Behavior #42: local-only-by-contract — surface is local by the resolution contract",
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["behavioral_verdict"]["ok"] is True
    assert payload["status"] == "carrier_verified"


def test_issue_verify_closeout_rejects_undispositioned_hotl_entry(tmp_path: Path) -> None:
    """WS-2 seeded escape (Direction-3): a bug carrier that PRESENTS a HOTL entry
    without a typed disposition must FAIL before the CLOSED-state green stands."""
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #42.",
            hotl_line="HOTL #42: still checking the connector roundtrip",
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["hotl_dispositions"]["ok"] is False
    assert payload["hotl_dispositions"]["undispositioned"][0]["target"] == "#42"
    # the OTHER floors pass — the close fails ONLY on the undispositioned HOTL entry
    assert payload["behavioral_verdict"]["ok"] is True


def test_issue_verify_closeout_accepts_typed_hotl_disposition(tmp_path: Path) -> None:
    """A typed HOTL status (here `blocked-needs-operator`) disposes the entry —
    render-not-declare: the floor passes; honesty is the resolution critique."""
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #42.",
            hotl_line="HOTL #42: blocked-needs-operator — awaiting prod approval; queued in the ODQ",
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["hotl_dispositions"]["applies"] is True
    assert payload["hotl_dispositions"]["ok"] is True


def test_issue_verify_closeout_inert_without_hotl_entry(tmp_path: Path) -> None:
    """Presence-gated: a carrier with NO HOTL entry is inert (no live loop to
    dispose) — the floor does not over-fire on internal/no-live closes."""
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42."))

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["hotl_dispositions"]["applies"] is False
    assert payload["hotl_dispositions"]["ok"] is True


def test_evaluate_hotl_dispositions_unit() -> None:
    """Direct unit coverage of the WS-2 floor: presence-gating, typed vocabulary,
    classification exemption, and multi-entry refusal."""
    fn = _load_verify_module().evaluate_hotl_dispositions
    # question/decision-needed have no live behavior -> inert
    assert fn("HOTL #1: nonsense", "question")["applies"] is False
    # no entry -> inert
    assert fn("Close #1.\nBehavior: verified via X", "bug")["applies"] is False
    # local-only-by-contract disposes; every typed status disposes
    for status in (
        "local-only-by-contract — no live surface", "verified: roundtrip <ts>",
        "blocked-needs-capability: no repo command", "deferred-by-operator: next window",
        "accepted-risk: owner ok", "out-of-scope: not this loop", "issue #77 tracks it",
    ):
        verdict = fn(f"HOTL: {status}", "feature")
        assert verdict["applies"] is True and verdict["ok"] is True, status
    # multi-entry: one typed, one untyped -> refuse only the untyped
    multi = fn("HOTL #1: verified: roundtrip\nHOTL #2: probably fine", "bug")
    assert multi["ok"] is False
    assert [u["target"] for u in multi["undispositioned"]] == ["#2"]
    # placeholder value is undispositioned
    assert fn("HOTL #1: TODO", "bug")["ok"] is False


def test_issue_verify_closeout_rejects_missing_ai_provenance_marker(tmp_path: Path) -> None:
    """Seeded escape: an agent-authored bug carrier without an AI-provenance marker
    is not legible to the distinct observer and must FAIL its presence check."""
    _seed_commit(tmp_path, _bug_closeout_body(close_line="Close #42.", provenance_line=None))

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["ai_provenance"]["ok"] is False


def test_issue_verify_closeout_question_class_exempt_from_rung1_floors(tmp_path: Path) -> None:
    """A `question` carrier has no behavior to confirm: both rung-1 floors are
    inert (mirroring the resolution-critique classification gate)."""
    _seed_commit(
        tmp_path,
        "\n\n".join(
            [
                "Close #42.",
                "JTBD: answer a clarification question.",
                "Answer: documented the resolved decision in the issue thread.",
            ]
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "question", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["behavioral_verdict"]["applies"] is False
    assert payload["ai_provenance"]["applies"] is False


def test_issue_verify_closeout_requires_per_issue_behavioral_verdict_in_bundle(tmp_path: Path) -> None:
    """No aggregate pass: a bundle where one issue is silent fails for that issue
    even when the other carries a verdict."""
    _seed_commit(
        tmp_path,
        _bug_closeout_body(
            close_line="Close #1.\nClose #2.",
            critique_line="Critique #1 #2: charness-artifacts/critique/x.md",
            behavior_line="Behavior #1: behavior test exercises the fix (distinct channel)",
        ),
    )

    result = run_script(
        SCRIPT, "verify-closeout", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "1", "--number", "2",
        "--classification", "bug", "--carrier", "direct-commit", "--commit-ref", "HEAD",
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["behavioral_verdict"]["missing"] == [2]


def test_validate_closeout_draft_blocks_silent_carrier_before_mutation(tmp_path: Path) -> None:
    """The block-the-silent teeth land at the pre-publish draft boundary: a silent
    bug draft fails validate-closeout-draft before any GitHub mutation."""
    body = tmp_path / "draft.md"
    body.write_text(_bug_closeout_body(close_line="Resolves #42.", behavior_line=None), encoding="utf-8")

    result = run_script(
        SCRIPT, "validate-closeout-draft", "--repo-root", str(tmp_path),
        "--repo", "corca-ai/charness", "--number", "42",
        "--classification", "bug", "--carrier", "pr-body", "--body-file", str(body),
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["behavioral_verdict"]["ok"] is False


def test_issue_verify_closeout_rejects_unposted_manual_fallback_comment(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "if 'view' in sys.argv:",
                "    print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42', 'comments': [{'body': 'different comment'}]}))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    body = tmp_path / "closeout.md"
    body.write_text(
        _bug_closeout_body(close_line="Manual close comment.")
        + "\nManual close reason: auto-close failed after remote verification.\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "verify-closeout",
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
        "--body-file",
        str(body),
        "--manual-fallback-reason",
        "auto-close-failed-after-remote-verification",
        "--expect-state",
        "CLOSED",
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin"},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["manual_comment_missing"] == [42]

