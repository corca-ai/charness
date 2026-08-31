from __future__ import annotations

import importlib
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from tests.quality_gates.seeding_support import _install_empty_git_dir
from tests.quality_gates.support import run_script

SCRIPT = "scripts/check_issue_closeout_commit_msg.py"
hook = importlib.import_module("scripts.check_issue_closeout_commit_msg")


def _init_git_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _install_empty_git_dir(repo, branch="main")


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)


def _stage_issue_closeout(repo: Path, body: str) -> Path:
    path = repo / "charness-artifacts" / "issue" / "closeout.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _run(repo_root: Path, message: Path, *, repo: str = "corca-ai/charness") -> SimpleNamespace:
    """Evaluate from planted artifact bytes; do not re-ask the Git index."""
    folder = repo_root / "charness-artifacts" / "issue"
    files: dict[str, str] = {}
    if folder.is_dir():
        for path in folder.glob("*.md"):
            if path.is_file():
                files[path.relative_to(repo_root).as_posix()] = path.read_text(encoding="utf-8")
    report = hook.evaluate(
        repo_root,
        message,
        repo,
        list_paths=lambda _root: list(files),
        read_file=lambda _root, path: files[path],
    )
    payload: dict[str, Any] = hook.report_payload(report)
    dumped = yaml.safe_dump(payload)
    return SimpleNamespace(
        returncode=0 if report["ok"] else 1,
        payload=payload,
        stdout=dumped,
        stderr="",
    )


def _bug_closeout_body(close_line: str = "Close #42.") -> str:
    return "\n\n".join(
        [
            close_line,
            "JTBD: resolve GitHub issues end-to-end.",
            "Root cause: the issue closeout carrier was prose-only.",
            "Debug artifact: charness-artifacts/debug/latest.md.",
            "Siblings: issue closeout | decision: same carrier bug | proof: commit-msg hook.",
            "Prevention: commit-msg blocks missing closeout carriers.",
            "Critique: blocked synthetic-test-harness: this test does not spawn a real reviewer",
            "Behavior #42: behavior test exercises the fix (distinct channel from CLOSED)",
            "AI-provenance: agent-drafted; human-audited per the resolution critique",
        ]
    )


def test_commit_msg_gate_skips_when_no_issue_closeout_artifact_is_staged(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("Ordinary commit\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "not_applicable"


def test_commit_msg_gate_rejects_staged_closeout_artifact_without_commit_carrier(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _bug_closeout_body())
    subprocess.run(
        ["git", "add", "charness-artifacts/issue/closeout.md"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    message = tmp_path / "message.txt"
    message.write_text("Resolve issue without close keywords\n", encoding="utf-8")

    result = run_script(
        SCRIPT,
        "--repo-root",
        str(tmp_path),
        "--commit-msg-file",
        str(message),
        real_process=True,
    )

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "failed"
    assert payload["reports"][0]["missing_close_keywords"] == [42]
    assert set(payload["reports"][0]["missing_fields"]) >= {"root_cause", "debug_artifact", "siblings", "prevention"}


def test_commit_msg_gate_accepts_commit_message_closeout_carrier(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _bug_closeout_body())
    message = tmp_path / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    assert payload["reports"][0]["carrier"] == "commit-msg"
    assert payload["reports"][0]["missing_close_keywords"] == []
    assert payload["reports"][0]["missing_fields"] == []


def test_commit_msg_gate_ignores_close_keywords_inside_staged_code_fence(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, "```text\nClose #42.\n```\n")
    message = tmp_path / "message.txt"
    message.write_text("Ordinary commit\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "not_applicable"


def test_commit_msg_gate_rejects_bare_close_keyword_with_no_staged_artifact_and_no_carrier(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("Fixes #123\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "failed"
    assert payload["artifacts"] == []
    assert payload["bare_close_numbers"] == [123]
    assert payload["reports"][0]["source_artifact"] is None
    assert payload["reports"][0]["numbers"] == [123]
    assert payload["reports"][0]["missing_fields"]

    # The remedy the deleted human renderer used to print is now folded into the
    # payload: a refused bare close must still tell the author how to defuse it.
    remediation = "\n".join(payload["remediation"])
    assert "bare `#N`" in remediation
    assert "close #123` -> `#123`" in remediation


def test_commit_msg_gate_allows_bare_issue_reference_without_close_keyword(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("See #123 for context.\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "not_applicable"


def test_commit_msg_gate_accepts_bare_close_keyword_when_message_carries_full_ledger(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    assert payload["artifacts"] == []
    assert payload["bare_close_numbers"] == [42]
    assert payload["reports"][0]["source_artifact"] is None


def test_commit_msg_gate_staged_artifact_behavior_is_unaffected_by_bare_keyword_floor(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _bug_closeout_body())
    message = tmp_path / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    assert len(payload["artifacts"]) == 1
    # The commit message's own close keyword already covers #42 via the staged
    # artifact; the bare-keyword trigger must not double-report the same issue.
    assert payload["bare_close_numbers"] == []
    assert len(payload["reports"]) == 1


def test_commit_msg_gate_rejects_bare_colon_close_keyword_with_no_carrier(tmp_path: Path) -> None:
    """GitHub's documented colon form (`Closes: #10`) auto-closes exactly like
    the space form; the scanner must recognize it too."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("Closes: #123\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "failed"
    assert payload["bare_close_numbers"] == [123]
    assert payload["reports"][0]["numbers"] == [123]


def test_commit_msg_gate_captures_all_numbers_in_single_keyword_comma_list(tmp_path: Path) -> None:
    """A single keyword followed by a comma list (`Closes #10, #11, #12`) must
    bind every listed number, not only the first."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("Closes #10, #11, #12\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "failed"
    assert payload["bare_close_numbers"] == [10, 11, 12]
    assert payload["reports"][0]["numbers"] == [10, 11, 12]


def test_commit_msg_gate_bare_close_with_answer_substring_defaults_to_bug_not_question(
    tmp_path: Path,
) -> None:
    """Seeded escape: a loose `Answer:` substring previously flipped a bare
    commit's inferred classification to the fully-exempt `question`, silently
    skipping the behavioral-verdict and resolution-critique floors. A bare
    close keyword with no explicit `Classification:` line must default to
    `bug` instead, so those floors stay live."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text(
        "\n\n".join(
            [
                "Fixes #123",
                "JTBD: understand whether we should ship this.",
                "Answer: yes, ship it.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "failed"
    report = payload["reports"][0]
    assert report["source_artifact"] is None
    # `root_cause`/`debug_artifact` only appear in `missing_fields` for `bug`;
    # a `question` classification would never surface them, so their presence
    # proves the bare path did not adopt the loose `Answer:` inference.
    assert "root_cause" in report["missing_fields"]
    assert "debug_artifact" in report["missing_fields"]


def test_commit_msg_gate_staged_artifact_never_infers_the_exempt_classification(tmp_path: Path) -> None:
    """B3 regression: the fully-exempt `question`/`decision-needed`
    classification must never be *inferred*.

    `_bare_classification` was hardened against the loose `answer:`/`decision:`
    substring heuristic and its sibling `_infer_classification` was not, so a
    staged artifact containing the word `Answer:` anywhere in its body — a quoted
    log, a prose sentence — bought the exemption that turns off the
    behavioral-verdict and resolution-critique floors. Both
    siblings now default to `bug`, the strictest classification, and the
    exemption is reachable only by explicit declaration (control below)."""
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "Close #55.",
            "JTBD: decide whether to ship the change.",
            "Answer: yes, proceed.",
            "AI-provenance: authored by an agent session.",
        ]
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "failed"
    assert payload["artifacts"][0]["classification"] == "bug"
    # The floors an inferred `question` would have silently switched off.
    assert {"root_cause", "debug_artifact"} <= set(payload["reports"][0]["missing_fields"])
    assert payload["review_advisory"] == []
    # The refusal must still name the explicit-declaration escape hatch, so an
    # author whose genuine question close was checked as `bug` can see the one
    # auditable line that changes the verdict.
    assert "Classification: question" in "\n".join(payload["remediation"])


def test_commit_msg_gate_explicit_question_classification_still_exempts(tmp_path: Path) -> None:
    """Control for the B3 regression above: the byte-identical body with an
    explicit `Classification: question` line — a deliberate, auditable assertion
    rather than an accident of wording — still gets the exemption and still needs
    only the question-classification ledger fields."""
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "Close #55.",
            "Classification: question",
            "JTBD: decide whether to ship the change.",
            "Answer: yes, proceed.",
            "AI-provenance: authored by an agent session.",
        ]
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    assert payload["artifacts"][0]["classification"] == "question"
    assert payload["reports"][0]["missing_fields"] == []


def test_commit_msg_gate_surfaces_exemption_advisory_for_question_close(tmp_path: Path) -> None:
    """D36: a `question`/`decision-needed` close self-exempts from the
    behavioral-verdict and resolution-critique floors. On the commit-msg carrier
    that exemption must be SURFACED (non-blocking, exit 0) exactly as it already
    is on `close-with-comment`, so it is never the silent path. Falsifiable pair:
    the exempt close surfaces the advisory here; the bug-close case below does
    not."""
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "Close #55.",
            "Classification: question",
            "JTBD: decide whether to ship the change.",
            "Answer: yes, proceed.",
            "AI-provenance: authored by an agent session.",
        ]
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = _run(tmp_path, message)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    assert len(payload["review_advisory"]) == 1
    assert "#55" in payload["review_advisory"][0]
    assert "exempts this close" in payload["review_advisory"][0]
    # The gate has one output channel now (unconditional YAML on stdout), so the
    # payload assertions above ARE the surfacing check the deleted human renderer
    # used to need a second, flagless invocation to prove.


def test_commit_msg_gate_bug_close_surfaces_no_exemption_advisory(tmp_path: Path) -> None:
    """Falsifiable counterpart: a `bug` close has live behavior to confirm, so it
    is NOT floor-exempt and surfaces no exemption advisory."""
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _bug_closeout_body())
    message = tmp_path / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = _run(tmp_path, message)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    assert not [line for line in payload["review_advisory"] if "exempts this close" in line]


def test_commit_msg_gate_surfaces_skipped_resolution_critique(tmp_path: Path) -> None:
    """B2 regression: a resolution critique satisfied by a `blocked <signal>`
    host skip carries a top-level verdict byte-identical to one satisfied by a
    real critique (`ok: True`, `status: verified`), so a close whose fresh-eye
    review never ran read exactly like one whose review did. Rung-1 cannot judge
    whether the host block was genuine — the caller supplies both the enum head
    and the signal — so the skip must at least be LOUD."""
    _init_repo(tmp_path)
    # `_bug_closeout_body` records `Critique: blocked <signal>`, a host skip.
    _stage_issue_closeout(tmp_path, _bug_closeout_body())
    message = tmp_path / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = _run(tmp_path, message)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    skip_advisories = [line for line in payload["review_advisory"] if "was SKIPPED" in line]
    assert len(skip_advisories) == 1
    assert "#42" in skip_advisories[0]
    # Single output channel: the `review_advisory` entry above is what an operator
    # reads, so the loudness this test exists to pin is proven by the payload.


def test_commit_msg_gate_executed_resolution_critique_surfaces_no_skip_advisory(tmp_path: Path) -> None:
    """Falsifiable counterpart to the skip advisory: the same close carrying a
    real bound critique artifact surfaces no skip advisory."""
    _init_repo(tmp_path)
    critique = tmp_path / "charness-artifacts" / "critique" / "closeout-42.md"
    critique.parent.mkdir(parents=True, exist_ok=True)
    critique.write_text("Critique of the #42 resolution.\n", encoding="utf-8")
    body = _bug_closeout_body().replace(
        "Critique: blocked synthetic-test-harness: this test does not spawn a real reviewer",
        "Critique: charness-artifacts/critique/closeout-42.md",
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = _run(tmp_path, message)
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    assert payload["review_advisory"] == []


def test_commit_msg_gate_fenced_close_keyword_in_message_still_triggers_floor(tmp_path: Path) -> None:
    """Regression: GitHub parses the raw commit message for close keywords and
    treats backticks as literal, so a close keyword inside a ``` code fence in
    the COMMIT MESSAGE still auto-closes the issue. The bare-close floor must not
    strip fences from the message — doing so reported `not_applicable` while
    GitHub closed the issue with no floor anywhere (the escape this floor exists
    to close)."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text("```\nFixes #123\n```\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "failed"
    assert payload["bare_close_numbers"] == [123]
    assert payload["reports"][0]["source_artifact"] is None


def test_commit_msg_checker_resolves_exported_plugin_skill_layout(tmp_path: Path) -> None:
    plugin = tmp_path / "plugin"
    shutil.copytree(Path(__file__).resolve().parents[2] / "plugins" / "charness", plugin)
    repo = tmp_path / "repo"
    _init_git_repo(repo)
    _stage_issue_closeout(repo, _bug_closeout_body())
    subprocess.run(
        ["git", "add", "charness-artifacts/issue/closeout.md"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    message = repo / "message.txt"
    message.write_text(_bug_closeout_body(), encoding="utf-8")

    result = subprocess.run(
        [
            "python3",
            str(plugin / "scripts" / "check_issue_closeout_commit_msg.py"),
            "--repo-root",
            str(repo),
            "--commit-msg-file",
            str(message),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["status"] == "verified"


def _pause_brief_body(provenance: bool = True) -> str:
    lines = [
        "# Resolution Brief — corca-ai/charness#77",
        "**Classification**: deferred-work",
        "**Reporter JTBD**: keep the pause durable across session compaction.",
        "**Open decisions**:\n- split vs delete",
        "Close scope: close #77 after the follow-up slice lands.",
        "**Autonomous vs pause**: pausing for user discussion",
    ]
    if provenance:
        lines.append(
            "AI-provenance: agent-drafted pause brief via charness issue resolve; resolution pending"
        )
    return "\n\n".join(lines) + "\n"


def test_commit_msg_gate_accepts_pausing_brief_with_provenance_and_no_close_keyword(
    tmp_path: Path,
) -> None:
    """Reproduces the 2026-07-16 refusal (#444): committing a pausing
    resolution brief alone must not demand the closeout ledger. The pause
    carve-out requires only the brief's own `AI-provenance:` line while the
    commit message carries no close keyword for the brief's issue."""
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _pause_brief_body())
    message = tmp_path / "message.txt"
    message.write_text("Persist paused resolution brief for #77\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "verified"
    assert payload["artifacts"] == []
    assert payload["pause_briefs"][0]["classification"] == "deferred-work"
    report = payload["reports"][0]
    assert report["trigger"] == "pause-brief"
    assert report["ai_provenance"]["ok"] is True


def test_commit_msg_gate_rejects_pausing_brief_missing_provenance_line(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _pause_brief_body(provenance=False))
    message = tmp_path / "message.txt"
    message.write_text("Persist paused resolution brief for #77\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    report = payload["reports"][0]
    assert report["trigger"] == "pause-brief"
    assert report["ai_provenance"]["missing"] is True

    # The refusal must diagnose itself as the PAUSE floor, not the full closeout
    # ledger: the summary the payload now carries names both the missing line and
    # the pause-brief scope it applies to.
    assert "AI-provenance" in payload["summary"]
    assert "pausing resolution brief" in payload["summary"]


def test_commit_msg_gate_keeps_full_ledger_teeth_when_message_close_keywords_pause_brief(
    tmp_path: Path,
) -> None:
    """The carve-out is pause-scoped only: the moment the commit message
    close-keywords the brief's issue, the staged brief is a closeout carrier
    again and the full ledger floor applies."""
    _init_repo(tmp_path)
    _stage_issue_closeout(tmp_path, _pause_brief_body())
    message = tmp_path / "message.txt"
    message.write_text("Close #77\n\nDone.\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "failed"
    assert payload["pause_briefs"] == []
    report = payload["reports"][0]
    assert report["source_artifact"].endswith("closeout.md")
    assert report["missing_fields"], report


def test_commit_msg_gate_reads_bold_classification_from_staged_artifact(tmp_path: Path) -> None:
    """The brief template's bold `**Classification**:` form must classify as
    written instead of falling through to the strictest `bug` inference and
    demanding the bug ledger for a deferred-work carrier (#444)."""
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "Close #88.",
            "**Classification**: deferred-work",
            "JTBD: resolve the deferred slice.",
            "Resolution brief: inline (no pause).",
        ]
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = _run(tmp_path, message)

    payload = yaml.safe_load(result.stdout)
    assert payload["artifacts"][0]["classification"] == "deferred-work"
    report = payload["reports"][0]
    assert "root_cause" not in report["missing_fields"]
    assert "debug_artifact" not in report["missing_fields"]
    assert report["resolution_critique_check"]["skipped_classification"] == "deferred-work"


def test_commit_msg_gate_stays_out_of_scope_for_template_faithful_brief(tmp_path: Path) -> None:
    """#444 critique C1: the gate recognizes closeout carriers by close-keyword
    text in the artifact body. A template-faithful pause brief carries only a
    bare `#N` reference, so it never enters the gate at all — the provenance
    floor applies only to briefs the gate can see (close-keyword text in the
    body), exactly as the resolution-brief Persistence prose states."""
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "# Resolution Brief — corca-ai/charness#77",
            "**Classification**: deferred-work",
            "**Autonomous vs pause**: pausing for user discussion",
        ]
    ) + "\n"
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text("Persist paused resolution brief for #77\n", encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["status"] == "not_applicable"


def test_commit_msg_gate_bug_markers_outrank_feature_markers(tmp_path: Path) -> None:
    """A real bug closeout carries BOTH `Root cause:` and `Implementation:` /
    `Resolution brief:`. The `root cause:` -> `bug` branch must stay AHEAD of the
    `feature` branch: `feature`'s ledger demands neither `debug_artifact` nor the
    `siblings` decision-and-proof check, so classifying such a body as `feature`
    silently drops two bug-only floors on an irreversible boundary.

    Regression for a fix that removed that branch believing the trailing `bug`
    fallback made it redundant. It does not — the fallback is only reached when
    the `feature` branch does not match first."""
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "Close #55.",
            "JTBD: fix the gate.",
            "Root cause: the helper never compared the readback.",
            "Boundary: scripts/x.py only.",
            "Resolution brief: compare the readback value.",
            "Implementation: added the comparison.",
            "Prevention: regression test.",
        ]
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["artifacts"][0]["classification"] == "bug"
    # The two floors a `feature` misclassification would have dropped.
    assert {"debug_artifact", "siblings"} <= set(payload["reports"][0]["missing_fields"])
    # The failure output must name the classification the floors ran against;
    # `missing_fields: [...]` is undiagnosable without it. The emitted report
    # carries it beside the findings rather than in a rendered footer.
    assert payload["reports"][0]["classification"] == "bug"


def test_commit_msg_gate_bare_close_ignores_fenced_classification_line(tmp_path: Path) -> None:
    """B3 sibling escape: the bare close-keyword path reads the commit body with
    fences deliberately NOT stripped, because GitHub parses the raw message and
    auto-closes on a fenced `Fixes #123`. Reusing that raw text to read the
    classification let a `Classification: question` line inside a PASTED CODE
    FENCE assert the fully-exempt classification — the same shape B3 closed on
    the artifact path. Close keywords read raw; the classification reads
    stripped."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text(
        "Fixes #123\n\n"
        "Pasted from the issue thread:\n\n"
        "```text\n"
        "Classification: question\n"
        "```\n\n"
        "JTBD: decide whether to ship.\n\n"
        "Answer: no, closing as answered.\n",
        encoding="utf-8",
    )

    result = _run(tmp_path, message)

    assert result.returncode == 1
    report = yaml.safe_load(result.stdout)["reports"][0]
    assert report["trigger"] == "bare-close-keyword"
    assert report["classification"] == "bug"
    # The floors an inferred/fenced `question` would have switched off. AI-provenance
    # is deliberately NOT asserted here: it now applies unconditionally, so the
    # assertion could not fail for any classification and would read as a
    # discriminator while proving nothing.
    assert report["behavioral_verdict"]["applies"] is True
    assert report["resolution_critique_check"]["ok"] is False


def test_commit_msg_gate_bare_close_honors_unfenced_classification_line(tmp_path: Path) -> None:
    """Control for the fenced case: the same declaration outside a fence is a
    deliberate assertion and still grants the exemption."""
    _init_repo(tmp_path)
    message = tmp_path / "message.txt"
    message.write_text(
        "Fixes #123\n\n"
        "Classification: question\n\n"
        "JTBD: decide whether to ship.\n\n"
        "Answer: no, closing as answered.\n\n"
        # The exemption this test is about is the behavioral-verdict one. The
        # provenance floor no longer rides the same gate, so the marker is scaffolding.
        "AI-provenance: authored by an agent session.\n",
        encoding="utf-8",
    )

    result = _run(tmp_path, message)

    assert result.returncode == 0, result.stderr
    report = yaml.safe_load(result.stdout)["reports"][0]
    assert report["classification"] == "question"
    assert report["behavioral_verdict"]["applies"] is False


def test_commit_msg_gate_renders_the_specific_critique_failure(tmp_path: Path) -> None:
    """The commit-msg hook is the ONLY carrier that can block `git commit`, and
    it was the one printing the least.

    `check_prescribed_skill_executed_lib` builds a specific, actionable reason
    for every invalid skip (wrong enum head, or a signal under the detail floor);
    the deleted renderer computed it, carried it in the report, and then printed
    nine words with no diagnosis. The emitted payload must carry the specific
    reason, not just the failing check's name."""
    _init_repo(tmp_path)
    body = _bug_closeout_body().replace(
        "Critique: blocked synthetic-test-harness: this test does not spawn a real reviewer",
        "Critique: blocked host-down badly",
    ).replace("Prevention: commit-msg blocks missing closeout carriers.", "Prevention: N/A")
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    report = payload["reports"][0]
    invalid_skips = report["resolution_critique_check"]["invalid_skips"]
    assert [entry["name"] for entry in invalid_skips] == ["resolution_critique"]
    assert "skip reason too short" in invalid_skips[0]["detail"]
    # A placeholder field is present-but-empty, not absent; "missing" alone
    # misdescribes the dominant post-B1 cause. `parsed_ledger_fields` proves the
    # parser SAW `prevention` (so it is a placeholder, not an absent field), and
    # `ledger_field_note` says so in the payload the operator reads.
    assert report["missing_fields"] == ["prevention"]
    assert "prevention" in report["parsed_ledger_fields"]
    assert "placeholder" in payload["ledger_field_note"]


def test_commit_msg_gate_refuses_a_question_close_with_no_provenance_marker(tmp_path: Path) -> None:
    """The provenance floor's new reach, pinned on THIS carrier.

    The other two body carriers pin it directly (verify-closeout and
    close-with-comment). Without this, `evaluate_ai_provenance` could re-acquire a
    classification gate -- or this hook could re-introduce a remap in the other
    direction -- and every test in this file would stay green, on the one carrier
    that can block `git commit`.
    """
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "Close #55.",
            "Classification: question",
            "JTBD: decide whether to ship the change.",
            "Answer: yes, proceed.",
        ]
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode != 0
    report = yaml.safe_load(result.stdout)["reports"][0]
    assert report["classification"] == "question"
    assert report["ai_provenance"]["applies"] is True
    assert report["ai_provenance"]["ok"] is False


def test_commit_msg_gate_names_the_undispositioned_hotl_entry_it_refused(tmp_path: Path) -> None:
    """This carrier folded the HOTL floor into its verdict and printed NOTHING about
    it — the same bare-refusal defect this file already repaired twice for the
    behavioral and provenance floors, on the one carrier that can block `git commit`.
    An author whose commit is rejected has to be told which line and what to do."""
    _init_repo(tmp_path)
    body = "\n\n".join(
        [
            "Close #55.",
            "Classification: question",
            "JTBD: decide whether to ship the change.",
            "Answer: yes, proceed.",
            "HOTL #55: not verified yet, will follow up",
            "AI-provenance: authored by an agent session.",
        ]
    )
    _stage_issue_closeout(tmp_path, body)
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    result = _run(tmp_path, message)

    assert result.returncode != 0
    payload = yaml.safe_load(result.stdout)
    hotl = payload["reports"][0]["hotl_dispositions"]
    # Which line was refused...
    assert hotl["undispositioned"] == [
        {"target": "#55", "value": "not verified yet, will follow up"}
    ]
    # ...and what to do about it, including that deleting an inert line is right.
    assert "DELETE the line" in payload["hotl_requirement"]
