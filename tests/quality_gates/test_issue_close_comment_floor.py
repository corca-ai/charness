from __future__ import annotations

import json
import os
from pathlib import Path

from runtime_bootstrap import import_repo_module
from tests.quality_gates.issue_closeout_support import bug_closeout_body
from tests.quality_gates.support import ROOT, run_script, write_argv_logging_fake

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
FLOOR_MODULE = ROOT / "skills/public/issue/scripts/issue_close_comment_floor.py"


def _load_close_comment_floor():
    return import_repo_module(FLOOR_MODULE, "skills.public.issue.scripts.issue_close_comment_floor")


def test_close_with_comment_refuses_silent_body_before_any_gh_call(tmp_path: Path) -> None:
    """Seeded escape: manual close-with-comment previously mutated GitHub on an
    evidence-free body (only `body_file.is_file()` was checked). The rung-1
    presence floor must refuse before the comment/close backend is ever invoked."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'comment' in sys.argv: print('commented')",
            "if 'close' in sys.argv: print('closed')",
            "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
        ],
    )
    body = tmp_path / "body.md"
    body.write_text("Body.\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "bug",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "rung-1" in payload["error"]
    assert "missing behavioral verdict" in payload["error"]
    assert "missing/invalid resolution-critique evidence" in payload["error"]
    assert not log.exists(), "no gh call should have run before the floor refused"


def test_close_with_comment_proceeds_with_compliant_body(tmp_path: Path) -> None:
    """A body that carries the behavioral verdict and a bound (blocked) critique
    line passes the floor and the mutation proceeds through the backend."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'comment' in sys.argv: print('commented')",
            "if 'close' in sys.argv: print('closed')",
            "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
        ],
    )
    body = tmp_path / "body.md"
    body.write_text(bug_closeout_body(), encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "bug",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    # This body's critique line is `blocked <signal>` — no fresh eye read the
    # resolution. `verify-closeout` said so already; the carrier that writes to
    # GitHub itself did not, so the close with the WEAKEST review reached the
    # irreversible boundary with the quietest output. It is still advisory: the
    # close proceeds, the operator just gets told.
    assert any("was SKIPPED, not executed" in line for line in payload["review_advisory"])
    entries = json.loads(log.read_text(encoding="utf-8"))
    assert ["issue", "comment", "--repo", "corca-ai/charness", "42", "--body-file", str(body)] in entries
    assert ["issue", "close", "--repo", "corca-ai/charness", "42", "--reason", "completed"] in entries


def test_close_with_comment_refuses_undispositioned_hotl_entry(tmp_path: Path) -> None:
    """Seeded escape: the HOTL-disposition floor landed after this carrier's floor
    composition and was never wired in, so `close-with-comment` — the one carrier
    that mutates GitHub directly — could close on a HOTL entry that only *mentions*
    a status. Every other rung-1 field here is compliant, so the refusal can only
    come from the HOTL floor."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'comment' in sys.argv: print('commented')",
            "if 'close' in sys.argv: print('closed')",
            "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
        ],
    )
    body = tmp_path / "body.md"
    body.write_text(
        bug_closeout_body(hotl_line="HOTL #42: could not be verified; no readback available"),
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "bug",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "undispositioned HOTL entry #42" in payload["error"]
    # Isolation: prove the refusal came from the HOTL floor alone, not from a
    # sibling floor incidentally firing on the same fixture.
    assert "missing behavioral verdict" not in payload["error"]
    assert "missing/invalid resolution-critique evidence" not in payload["error"]
    assert "missing source preservation" not in payload["error"]
    assert not log.exists(), "no gh call should have run before the floor refused"


def test_close_with_comment_accepts_typed_hotl_entry(tmp_path: Path) -> None:
    """The same carrier with a *led* typed status passes: the floor refuses
    malformation, never the disposition's honesty (that is rung-2)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'comment' in sys.argv: print('commented')",
            "if 'close' in sys.argv: print('closed')",
            "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
        ],
    )
    body = tmp_path / "body.md"
    body.write_text(
        bug_closeout_body(
            hotl_line="HOTL #42: blocked-needs-capability — no repo-owned readback command"
        ),
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "bug",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["ok"] is True


def test_close_with_comment_question_classification_emits_review_advisory(tmp_path: Path) -> None:
    """`question`/`decision-needed` legitimately skip the behavioral-verdict and
    resolution-critique floors (no live behavior to confirm), but the
    caller-supplied classification is not independently checked. The close
    must still succeed (exit 0, advisory only, never blocks) while surfacing a
    REVIEW line so the bypass is visible rather than silent.

    The body carries an `AI-provenance:` marker because that floor no longer rides
    the same classification gate -- the skip this advisory reports is now two floors
    wide, not four, and the advisory's own sentence says so."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'comment' in sys.argv: print('commented')",
            "if 'close' in sys.argv: print('closed')",
            "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
        ],
    )
    body = tmp_path / "body.md"
    body.write_text(
        "Answer: yes, proceed as discussed.\n\nAI-provenance: authored by an agent session.\n",
        encoding="utf-8",
    )

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "question",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert len(payload["review_advisory"]) == 1
    assert payload["review_advisory"][0].startswith("REVIEW:")
    assert "question" in payload["review_advisory"][0]
    assert "advisory only, never blocks" in payload["review_advisory"][0]


def test_close_with_comment_refuses_on_missing_source_preservation_for_external_body(
    tmp_path: Path,
) -> None:
    """An externally-sourced body (`Source origin:` present) must also carry a
    preservation form; otherwise the floor refuses even when the behavioral
    verdict and critique lines are present."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(bin_dir, "gh", "GH_LOG", [])
    body = tmp_path / "body.md"
    body.write_text(bug_closeout_body() + "\n\nSource origin: slack\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "bug",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "source preservation" in payload["error"]
    assert not log.exists()


def test_close_with_comment_refuses_body_without_ai_provenance(tmp_path: Path) -> None:
    """Seeded escape, same shape as the HOTL one above: `verify-closeout` and the
    commit-msg carrier both check the AI-provenance marker, and this carrier -- the
    only one that writes to GitHub itself -- did not. The marker is what lets the
    rung-2 observer read an irreversible external write as agent-authored, so the
    carrier with the strongest need for it was the one without it. Every other
    rung-1 field here is compliant, so the refusal can only come from the
    provenance floor, and no gh call may run before it."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh-log.json"
    write_argv_logging_fake(
        bin_dir,
        "gh",
        "GH_LOG",
        [
            "if 'comment' in sys.argv: print('commented')",
            "if 'close' in sys.argv: print('closed')",
            "if 'view' in sys.argv: print(json.dumps({'number': 42, 'state': 'CLOSED', 'url': 'https://example.test/42'}))",
        ],
    )
    body = tmp_path / "body.md"
    body.write_text(bug_closeout_body(provenance_line=None), encoding="utf-8")

    result = run_script(
        SCRIPT,
        "close-with-comment",
        "--repo",
        "corca-ai/charness",
        "--number",
        "42",
        "--body-file",
        str(body),
        "--classification",
        "bug",
        "--repo-root",
        str(tmp_path),
        env={**os.environ, "PATH": f"{bin_dir}:/usr/bin:/bin", "GH_LOG": str(log)},
    )

    assert result.returncode == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "missing `AI-provenance:` marker" in payload["error"]
    # The other floors stayed silent, so this is the provenance check and not a
    # fixture that happens to fail several ways at once.
    assert "missing behavioral verdict" not in payload["error"]
    assert "missing/invalid resolution-critique evidence" not in payload["error"]
    assert not log.exists(), "no gh call should have run before the floor refused"


def test_close_with_comment_provenance_floor_applies_to_a_light_classification(
    tmp_path: Path,
) -> None:
    """The provenance floor no longer rides the behavioral-verdict classification gate.

    That gate's reason -- "this classification has no user-facing behavior to confirm"
    -- is sound for the behavioral verdict and does not transfer to authorship: an
    agent-posted `question` close comment is exactly as agent-authored as a `bug` one,
    and this is the carrier that writes it to GitHub directly.
    """
    floor = _load_close_comment_floor()
    silent = floor.evaluate_close_comment_floor(
        repo_root=tmp_path,
        body="Answered inline; no code change.\n",
        classification="question",
        number=42,
    )
    assert silent["ai_provenance"]["applies"] is True
    assert silent["ai_provenance"]["ok"] is False
    assert silent["ok"] is False

    marked = floor.evaluate_close_comment_floor(
        repo_root=tmp_path,
        body="Answered inline; no code change.\n\nAI-provenance: authored by an agent session.\n",
        classification="question",
        number=42,
    )
    assert marked["ai_provenance"]["ok"] is True
    assert marked["ok"] is True


def _load_issue_close():
    return import_repo_module(
        ROOT / "skills/public/issue/scripts/issue_close.py",
        "skills.public.issue.scripts.issue_close",
    )


def test_a_consolidated_close_asking_for_completed_is_refused_before_the_body_is_read(
    tmp_path: Path,
) -> None:
    """Ordering pin for the extracted carrier evaluation.

    `_refuse_completed_consolidation` is called from BOTH `close_with_comment` (ahead
    of the body-file read, where it has always sat) and `evaluate_close_comment_carrier`
    (so a direct caller of the extracted path is guarded too). The wrapper call is what
    keeps a caller who asked for `--reason completed` on a consolidation from getting a
    file-not-found instead of the contradiction they actually have.
    """
    closer = _load_issue_close()
    missing = tmp_path / "never-written.md"
    try:
        closer.close_with_comment(
            "corca-ai/charness", 42, missing,
            repo_root=tmp_path, classification="consolidated", reason="completed",
        )
    except RuntimeError as exc:
        assert "requires --reason 'not planned'" in str(exc)
        assert "body file not found" not in str(exc)
    else:  # pragma: no cover - the refusal is the contract
        raise AssertionError("a consolidated close with --reason completed must refuse")


def test_a_missing_close_comment_body_file_is_refused_before_any_backend_call(
    tmp_path: Path,
) -> None:
    closer = _load_issue_close()
    try:
        closer.close_with_comment(
            "corca-ai/charness", 42, tmp_path / "absent.md",
            repo_root=tmp_path, classification="bug",
        )
    except RuntimeError as exc:
        assert "close-comment body file not found" in str(exc)
    else:  # pragma: no cover - the refusal is the contract
        raise AssertionError("a missing body file must refuse")


def test_the_hotl_refusal_message_names_deletion_as_the_legal_exit(tmp_path: Path) -> None:
    """The floor is presence-gated, so a body with no HOTL entry passes -- but an
    author who DECLARES there was no loop (`HOTL: none`) is refused, because `none`
    is not a typed status. The remedy is deletion, and the message has to say so or
    the author has no way to learn it from the refusal."""
    floor = _load_close_comment_floor()
    report = floor.evaluate_close_comment_floor(
        repo_root=tmp_path,
        body="Answer: resolved inline.\n\nHOTL: none - no operator loop was involved.\n"
             "AI-provenance: authored by an agent session.\n",
        classification="question",
        number=42,
    )
    assert report["ok"] is False
    rendered = floor.format_close_comment_floor_failure(report)
    assert "DELETE the line" in rendered
    assert "a body with no HOTL entry is inert and passes" in rendered


def test_a_consolidated_repair_claim_refusal_is_rendered_not_silent(tmp_path: Path) -> None:
    """The floor refuses on `missing_ledger_fields` and used to print only its header.

    The path is reachable straight from the HOTL advice above: an author told to give
    the entry a typed status writes `HOTL: verified`, which the consolidated
    disposition then refuses as a repair claim. Two refusals in a row, the second one
    undiagnosed, at the carrier that writes to GitHub.
    """
    floor = _load_close_comment_floor()
    report = floor.evaluate_close_comment_floor(
        repo_root=tmp_path,
        body="JTBD: fold this into the umbrella.\nConsolidated into: #900\n"
             "HOTL: verified: roundtrip observed\nAI-provenance: authored by an agent session.\n",
        classification="consolidated",
        number=42,
    )
    assert report["ok"] is False
    assert report["missing_ledger_fields"]
    rendered = floor.format_close_comment_floor_failure(report)
    assert "asserts a repair via" in rendered
    assert len(rendered.splitlines()) > 1, "a refusal that prints only its header is unreadable"


def test_manual_consolidation_refuses_destination_equal_to_invoked_issue(tmp_path: Path) -> None:
    """The manual carrier knows its target even when the comment has no keyword.

    A `Closes #N` line in a comment does not close anything, so the consolidated
    authoring shape correctly tells users to omit it.  That must not remove the
    only identity the self-reference rule can use.
    """
    floor = _load_close_comment_floor()
    report = floor.evaluate_close_comment_floor(
        repo_root=tmp_path,
        body=(
            "Jtbd: move this work to its owner.\n"
            "Consolidated into: #42\n"
            "AI-provenance: authored by an agent session.\n"
        ),
        classification="consolidated",
        number=42,
    )
    assert report["ok"] is False
    assert any("same carrier is closing" in problem for problem in report["missing_ledger_fields"])
