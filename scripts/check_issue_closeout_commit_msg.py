#!/usr/bin/env python3
"""Block issue-closeout artifacts whose commit message is not the carrier."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_CLASSIFICATION_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?classification(?:\*\*)?\s*:\s*"
    r"(?P<classification>bug|feature|deferred-work|question|decision-needed)\s*$"
)
_COMMENT_LINE_RE = re.compile(r"^\s*#")
# A pausing resolution brief (references/resolution-brief.md "Persistence")
# declares itself with the template's `Autonomous vs pause:` field; a value
# starting with "paus" (paused/pausing) is the pause state, "continuing" is not.
_PAUSE_BRIEF_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?autonomous vs pause(?:\*\*)?\s*:\s*paus"
)


def _load_issue_verify_closeout():
    root = Path(__file__).resolve().parents[1]
    candidates = [
        root / "skills" / "public" / "issue" / "scripts" / "issue_verify_closeout.py",
        root / "skills" / "issue" / "scripts" / "issue_verify_closeout.py",
    ]
    module_path = next((path for path in candidates if path.is_file()), candidates[0])
    spec = importlib.util.spec_from_file_location("issue_verify_closeout_commit_msg", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo_root, check=False, capture_output=True, text=True)


def _staged_paths(repo_root: Path) -> list[str]:
    result = _run_git(repo_root, "diff", "--cached", "--name-only", "--diff-filter=ACM")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to list staged paths")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _staged_file(repo_root: Path, path: str) -> str:
    result = _run_git(repo_root, "show", f":{path}")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"failed to read staged file {path}")
    return result.stdout


def _strip_commit_comments(body: str) -> str:
    return "\n".join(line for line in body.splitlines() if not _COMMENT_LINE_RE.match(line)).strip() + "\n"


def _bare_close_keyword_numbers(sanitized_body: str, covered: set[int], iter_refs: Any) -> list[int]:
    """Issue numbers the commit message itself close-keywords, minus numbers
    already covered by a staged closeout artifact.

    GitHub auto-closes on a close keyword landing on the default branch
    regardless of whether any ``charness-artifacts/issue/*.md`` was staged.
    Re-keying the floor to this mechanism (not only the artifact-staging
    convention) closes the escape where a bare ``Fixes #123`` commit message
    auto-closes an issue with no floor anywhere. ``iter_refs`` is the shared
    ``issue_verify_closeout.iter_close_keyword_refs`` scanner (covers the plain,
    colon, and single-keyword comma-list close-keyword forms) so this module
    keeps no second copy of the close-keyword regex.

    Scans the raw ``sanitized_body`` (commit comments already removed, exactly as
    git strips them from the stored message) and deliberately does NOT strip code
    fences: GitHub parses the raw commit-message text for close keywords and
    treats backticks as literal characters, so a fenced ``Fixes #123`` still
    auto-closes #123. Stripping fences here reported ``not_applicable`` while
    GitHub closed the issue with no floor anywhere — the exact escape this floor
    exists to close (an agent quoting a log/diff that contains a close keyword,
    or deliberately fencing one to dodge the floor).
    """
    found = {number for _repo, number in iter_refs(sanitized_body)}
    return sorted(number for number in found if number not in covered)


def _issue_closeout_artifacts(repo_root: Path, iter_refs: Any, strip_code_fences: Any) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for path in _staged_paths(repo_root):
        if not (path.startswith("charness-artifacts/issue/") and path.endswith(".md")):
            continue
        body = "\n".join(strip_code_fences(_staged_file(repo_root, path)))
        numbers = sorted({number for _repo, number in iter_refs(body)})
        if not numbers:
            continue
        artifacts.append(
            {
                "path": path,
                "numbers": numbers,
                "classification": _infer_classification(body),
                "pause_brief": _PAUSE_BRIEF_RE.search(body) is not None,
                "body": body,
            }
        )
    return artifacts


def _infer_classification(body: str) -> str:
    """Classification for a staged closeout artifact.

    An explicit ``Classification:`` line is a deliberate assertion and is
    honored, including the floor-exempt values. Absent one, inference may only
    reach classifications that keep the floors LIVE: the loose
    ``decision:``/``answer:`` substring test used to hand the fully-exempt
    ``question`` classification — which turns off the behavioral-verdict, AI-
    provenance, and resolution-critique floors — to any artifact that happened to
    contain the word ``Answer:`` anywhere in its body, including inside a quoted
    log or a prose sentence (B3). ``_bare_classification`` was hardened against
    exactly this and the hardening was not applied here; it is now. An artifact
    that genuinely is a question must SAY so with ``Classification: question``,
    which is one line and is auditable, rather than earning the exemption by
    accident. Inference otherwise falls back to ``bug``, the strictest value.

    The ``root cause:``/``debug artifact:`` branch is NOT redundant with that
    fallback and must stay AHEAD of the ``feature`` branch. A real bug closeout
    routinely carries both ``Root cause:`` and ``Implementation:``/``Resolution
    brief:``, and ``feature``'s ledger demands neither ``debug_artifact`` nor the
    ``siblings`` decision-and-proof check. Removing it as "already covered by the
    fallback" reads correct and is not: it silently downgrades exactly those
    closeouts to ``feature`` and drops two bug-only floors.
    """
    explicit = _CLASSIFICATION_RE.search(body)
    if explicit is not None:
        return explicit.group("classification")
    lowered = body.lower()
    if "root cause:" in lowered or "debug artifact:" in lowered:
        return "bug"
    if "resolution brief:" in lowered or "implementation:" in lowered:
        return "feature"
    return "bug"


def _bare_classification(body: str, strip_code_fences: Any = None) -> str:
    """Classification for a bare close-keyword commit message (no staged
    artifact backing it).

    Honors an explicit ``Classification:`` line — a deliberate assertion, not
    inference — and otherwise defaults to ``bug``, the strictest classification,
    so the floors stay live. Neither this function nor ``_infer_classification``
    infers a floor-exempt value from loose body text (B3).

    ``strip_code_fences`` is required for that explicit read to be trustworthy.
    The bare path receives the commit body with only ``#`` comments removed —
    fences are deliberately NOT stripped for close-keyword scanning, because
    GitHub parses the raw message and auto-closes on a fenced ``Fixes #123``.
    Reusing that same raw text to read the classification let a ``Classification:
    question`` line *inside a pasted code fence* assert the exemption, which is
    the very shape B3 closed on the artifact path (that path strips fences before
    classifying). Close keywords read raw; the classification reads stripped.
    """
    text = "\n".join(strip_code_fences(body)) if strip_code_fences is not None else body
    explicit = _CLASSIFICATION_RE.search(text)
    if explicit is not None:
        return explicit.group("classification")
    return "bug"


def _pause_brief_reports(pause_briefs: list[dict[str, Any]], verify_module: Any) -> list[dict[str, Any]]:
    """Light-path reports for pausing resolution briefs (#444).

    A pausing brief is persisted pause state, not a closeout carrier: at pause
    time no resolution exists, so demanding the critique/behavior ledger forces
    fabrication (the exact contract conflict #444 records). The one requirement
    kept is rung-1 provenance — the persisted brief itself must be legible as
    agent-authored via an ``AI-provenance:`` line. Full ledger teeth return the
    moment the commit message close-keywords one of the brief's numbers (the
    caller routes that overlap back to the full floor before calling this).
    """
    # floor-addition-restraint: replaces an unsatisfiable full-ledger demand on
    # pause briefs with a one-line provenance floor the brief contract names.
    reports: list[dict[str, Any]] = []
    for artifact in pause_briefs:
        # The pause floor is unconditional: a question/decision-needed
        # self-classification must not bypass the one requirement kept.
        floor_classification = artifact["classification"]
        if floor_classification in verify_module.FLOOR_EXEMPT_CLASSIFICATIONS:
            floor_classification = "feature"
        provenance = verify_module.evaluate_ai_provenance(artifact["body"], floor_classification)
        reports.append(
            {
                "ok": bool(provenance.get("ok")),
                "status": "pause_brief_verified" if provenance.get("ok") else "failed",
                "numbers": artifact["numbers"],
                "classification": artifact["classification"],
                "carrier": "commit-msg",
                "source_artifact": artifact["path"],
                "trigger": "pause-brief",
                "ai_provenance": provenance,
            }
        )
    return reports


def _exemption_advisories(reports: list[dict[str, Any]], advisory_fn: Any) -> list[str]:
    """Non-blocking REVIEW advisories for any report whose self-classification
    exempts it from the behavioral-verdict and resolution-critique floors.

    Mirrors the ``close-with-comment`` carrier (``issue_close.py`` surfaces the
    same advisory through its ``review_advisory`` field) so a ``question`` /
    ``decision-needed`` close is not the *silent* path on the commit-msg carrier
    the way it already is not on ``close-with-comment`` (D36). ``advisory_fn`` is
    the shared owner ``issue_verify_closeout.review_advisory_for_classification``;
    passing ``numbers``/``source`` lets the single advisory name which close it
    applies to. Never affects ``ok``/exit status — advisory only.
    """
    lines: list[str] = []
    for report in reports:
        lines.extend(
            advisory_fn(
                report.get("classification", ""),
                numbers=report.get("numbers", []),
                source=report.get("source_artifact"),
            )
        )
        # A resolution critique satisfied by a host-blocked skip rather than an
        # executed review carries the same top-level verdict as a real one; the
        # critique check's own advisory is the only thing that distinguishes
        # them, so surface it on this carrier too (B2).
        lines.extend(report.get("resolution_critique_check", {}).get("review_advisory", []))
    return lines


def evaluate(repo_root: Path, commit_msg_file: Path, repo: str) -> dict[str, Any]:
    issue_verify_closeout = _load_issue_verify_closeout()
    iter_refs = issue_verify_closeout.iter_close_keyword_refs
    artifacts = _issue_closeout_artifacts(
        repo_root,
        iter_refs,
        issue_verify_closeout.strip_code_fences,
    )
    commit_msg_file = commit_msg_file.resolve()
    raw_body = commit_msg_file.read_text(encoding="utf-8")
    sanitized_body = _strip_commit_comments(raw_body)
    message_refs = {number for _repo, number in iter_refs(sanitized_body)}
    # Pause carve-out (#444): a pausing resolution brief is persisted state, not
    # a closeout carrier — at pause time no honest critique/behavior ledger can
    # exist. The brief stays exempt only while the commit message close-keywords
    # none of its issue numbers; a `Close #N` overlap restores the full floor.
    pause_briefs = [
        artifact
        for artifact in artifacts
        if artifact["pause_brief"] and not (set(artifact["numbers"]) & message_refs)
    ]
    artifacts = [artifact for artifact in artifacts if artifact not in pause_briefs]
    covered = {number for artifact in artifacts for number in artifact["numbers"]}
    # floor-addition-restraint: irreversible-boundary P5 floor, presence/form-only
    bare_numbers = _bare_close_keyword_numbers(sanitized_body, covered, iter_refs)
    pause_reports = _pause_brief_reports(pause_briefs, issue_verify_closeout)
    for artifact in artifacts + pause_briefs:
        artifact.pop("body", None)
    if not artifacts and not bare_numbers and not pause_reports:
        return {"ok": True, "status": "not_applicable", "artifacts": [], "review_advisory": []}

    sanitized_file = commit_msg_file.with_suffix(commit_msg_file.suffix + ".charness-closeout-body")
    sanitized_file.write_text(sanitized_body, encoding="utf-8")
    reports: list[dict[str, Any]] = list(pause_reports)
    try:
        for artifact in artifacts:
            report = issue_verify_closeout.verify_closeout(
                repo_root=repo_root,
                repo=repo,
                numbers=artifact["numbers"],
                classification=artifact["classification"],
                carrier="pr-body",
                backend={"id": "gh"},
                body_file=sanitized_file,
            )
            report["carrier"] = "commit-msg"
            report["source_artifact"] = artifact["path"]
            reports.append(report)
        if bare_numbers:
            bare_report = issue_verify_closeout.verify_closeout(
                repo_root=repo_root,
                repo=repo,
                numbers=bare_numbers,
                classification=_bare_classification(
                    sanitized_body, issue_verify_closeout.strip_code_fences
                ),
                carrier="pr-body",
                backend={"id": "gh"},
                body_file=sanitized_file,
            )
            bare_report["carrier"] = "commit-msg"
            bare_report["source_artifact"] = None
            bare_report["trigger"] = "bare-close-keyword"
            reports.append(bare_report)
    finally:
        try:
            sanitized_file.unlink()
        except FileNotFoundError:
            pass

    ok = all(report.get("ok") for report in reports)
    return {
        "ok": ok,
        "status": "verified" if ok else "failed",
        "artifacts": artifacts,
        "pause_briefs": pause_briefs,
        "bare_close_numbers": bare_numbers,
        "reports": reports,
        "review_advisory": _exemption_advisories(
            reports, issue_verify_closeout.review_advisory_for_classification
        ),
    }


def _format_failure(report: dict[str, Any]) -> str:
    # #444 F5: a pause-only failure has exactly one remedy (the brief's
    # `AI-provenance:` line); the generic header/footer would misdirect the
    # author toward close keywords and the closeout ledger. Keyed on the
    # *failing* reports only — a passing non-pause report staged beside a
    # failing pause brief must not suppress the pause remedy text.
    failing = [item for item in report.get("reports", []) if not item.get("ok")]
    pause_only = bool(failing) and all(
        item.get("trigger") == "pause-brief" for item in failing
    )
    if pause_only:
        lines = [
            "charness commit-msg: a staged pausing resolution brief is missing its "
            "`AI-provenance:` line (the one requirement kept for pause-state briefs).",
        ]
    else:
        lines = [
            "charness commit-msg: this commit closes an issue (staged closeout artifact and/or a "
            "GitHub close keyword in the message) without a valid closeout carrier.",
        ]
    for item in report.get("reports", []):
        source = item.get("source_artifact")
        numbers = ", ".join(f"#{number}" for number in item.get("numbers", []))
        if source is None:
            lines.append(f"- commit message close keyword (no staged closeout artifact): {numbers}")
        elif item.get("trigger") == "pause-brief":
            lines.append(
                f"- {source}: {numbers} (pausing resolution brief: exempt from the closeout "
                "ledger, but the brief itself must carry an `AI-provenance:` line)"
            )
        else:
            lines.append(f"- {source}: {numbers}")
        # Name the classification the floors were actually run against. Which
        # ledger a body owes depends entirely on it, and it can be INFERRED
        # rather than declared, so "missing ledger fields: boundary" is
        # undiagnosable without it — the author cannot tell that their
        # `Classification: bug.` line was not read as a declaration.
        if item.get("classification"):
            lines.append(f"  classification checked: {item['classification']}")
        if item.get("missing_close_keywords"):
            missing = ", ".join(f"#{number}" for number in item["missing_close_keywords"])
            lines.append(f"  missing close keywords: {missing}")
        if item.get("missing_fields"):
            lines.append(f"  missing ledger fields: {', '.join(item['missing_fields'])}")
        critique = item.get("resolution_critique_check", {})
        if not critique.get("ok", True):
            lines.append("  missing/invalid resolution critique evidence")
        behavioral = item.get("behavioral_verdict", {})
        if behavioral.get("applies") and not behavioral.get("ok", True):
            missing_behavior = ", ".join(f"#{number}" for number in behavioral.get("missing", []))
            lines.append(
                "  missing per-issue behavioral verdict (a `Behavior #N:` line naming a "
                f"distinct channel or a typed non-verified disposition): {missing_behavior}"
            )
        provenance = item.get("ai_provenance", {})
        if provenance.get("applies") and not provenance.get("ok", True):
            lines.append("  missing `AI-provenance:` marker on the agent-authored carrier")
    if pause_only:
        lines.append(
            "Append one `AI-provenance:` line to the staged brief naming it as agent-drafted "
            "pause state (see the resolution-brief Persistence contract), then retry. Close "
            "keywords and the closeout ledger are not required while the brief is pausing "
            "and the commit message close-keywords none of its issue numbers."
        )
    else:
        lines.append(
            "Put the close keywords and closeout ledger in the commit body, or unstage the issue "
            "closeout artifact. If a close keyword above has no staged artifact and you do not want "
            "to carry the full closeout ledger in this commit, rewrite the keyword to a bare `#N` "
            "reference (e.g. `close #123` -> `#123`) so GitHub does not auto-close the issue on push."
        )
        lines.append(
            "If this close really is a question or a recorded decision, declare it with an "
            "explicit `Classification: question` / `Classification: decision-needed` line in the "
            "staged artifact. That exemption is never inferred from body text."
        )
    return "\n".join(lines)


def _emit_human_output(report: dict[str, Any]) -> None:
    """Non-JSON stderr rendering: the failure detail when the floor fails, plus
    any non-blocking exemption advisory. A ``question``/``decision-needed`` close
    self-exempts from the behavioral/critique floors; surfacing that here (it
    mirrors ``close-with-comment``'s ``review_advisory``) keeps the exemption from
    being the silent path on the commit-msg carrier, without ever changing exit.
    """
    if not report["ok"]:
        print(_format_failure(report), file=sys.stderr)
    for line in report.get("review_advisory", []):
        print(f"charness commit-msg: {line}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--commit-msg-file", type=Path, required=True)
    parser.add_argument("--repo", default="corca-ai/charness")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = evaluate(repo_root, args.commit_msg_file, args.repo)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _emit_human_output(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"charness commit-msg: {exc}", file=sys.stderr)
        raise SystemExit(1)
