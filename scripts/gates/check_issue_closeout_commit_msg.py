#!/usr/bin/env python3
"""Block issue-closeout artifacts whose commit message is not the carrier."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import import_repo_module  # noqa: E402

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

try:
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:  # git-hook execution: `scripts/` is sys.path[0], not a package
    from scripts.yaml_output import emit_yaml

_CLASSIFICATION_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?classification(?:\*\*)?\s*:\s*"
    # `consolidated` included, and the omission it repairs is worth recording: a
    # classification missing from THIS alternation does not fail loudly -- it falls
    # through to `_infer_classification`, which defaults to `bug`. So a consolidated
    # closeout was checked as a bug, demanding `Root cause:` / `Prevention:` /
    # `Behavior #N:` -- the hook's remedy for a close that claims nothing was to
    # fabricate exactly the repair claims the disposition exists to refuse.
    r"(?P<classification>bug|feature|deferred-work|question|decision-needed|consolidated)\s*$"
)
try:
    from scripts.closeout_message_claims import (
        _close_keyword_numbers,
        _close_keyword_scan_text,
        _strip_commit_comments,
        partition_closeout_carriers,
    )
except ModuleNotFoundError:  # invoked as `python3 scripts/<name>.py`
    from closeout_message_claims import (
        _close_keyword_numbers,
        _close_keyword_scan_text,
        _strip_commit_comments,
        partition_closeout_carriers,
    )
# A pausing resolution brief (references/resolution-brief.md "Persistence")
# declares itself with the template's `Autonomous vs pause:` field; a value
# starting with "paus" (paused/pausing) is the pause state, "continuing" is not.
_PAUSE_BRIEF_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:\*\*)?autonomous vs pause(?:\*\*)?\s*:\s*paus"
)


def _load_sibling(module_name: str):
    """Load a sibling script by path.

    By path rather than by package import because this file runs as a git hook from an
    arbitrary working directory, where `scripts` is not importable as a package.
    """
    local_path = Path(__file__).resolve().with_name(f"{module_name}.py")
    repo_root = next(
        (ancestor for ancestor in Path(__file__).resolve().parents if (ancestor / "scripts" / "adapter_lib.py").is_file()),
        None,
    )
    sibling_path = (
        repo_root / "scripts" / f"{module_name}.py" if repo_root is not None else local_path
    )
    spec = importlib.util.spec_from_file_location(module_name, sibling_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load sibling module {module_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_AUTHZ = _load_sibling("commit_msg_closeout_authorization")


def _load_issue_verify_closeout():
    root = Path(__file__).resolve().parents[2]
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


def _run_git(repo_root: Path, *args: str):
    return run_process(["git", *args], cwd=repo_root, timeout_seconds=None)


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


def _issue_closeout_artifacts(
    repo_root: Path,
    iter_refs: Any,
    strip_code_fences: Any,
    *,
    list_paths: Any = None,
    read_file: Any = None,
) -> list[dict[str, Any]]:
    """Closeout artifacts and the classification each declares.

    ``list_paths``/``read_file`` default to the git INDEX, which is what a commit-msg
    hook has. They are injectable so the pre-push guard can run this same parse over a
    COMMIT's tree: without that, the guard would re-derive classification from the
    message alone, default to ``bug`` for an artifact-carried ``question`` close, and
    demand root-cause/prevention claims the disposition exists to refuse -- the defect
    already recorded at ``_CLASSIFICATION_RE`` above, re-introduced one surface over.
    A second copy of this parse would have drifted the same way.
    """
    list_paths = list_paths or _staged_paths
    read_file = read_file or _staged_file
    artifacts: list[dict[str, Any]] = []
    for path in list_paths(repo_root):
        if not (path.startswith("charness-artifacts/issue/") and path.endswith(".md")):
            continue
        body = "\n".join(strip_code_fences(read_file(repo_root, path)))
        qualified = sorted(
            {(repo, number) for repo, number in iter_refs(body)},
            key=lambda item: (item[0] or "", item[1]),
        )
        numbers = sorted({number for _repo, number in qualified})
        if not numbers:
            continue
        artifacts.append(
            {
                "path": path,
                "numbers": numbers,
                # Repo-qualified form kept alongside the bare numbers the existing floors
                # use, so authorization can tell this repo's #514 from another repo's.
                "qualified_numbers": qualified,
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
    ``question`` classification — which turns off the behavioral-verdict and
    resolution-critique floors — to any artifact that happened to
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


def _pause_brief_reports(
    pause_briefs: list[dict[str, Any]], verify_module: Any
) -> list[dict[str, Any]]:
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
        # The pause floor is unconditional, and now says so by simply passing the real
        # classification. This used to rewrite a floor-exempt classification to
        # `feature` so the provenance check would run at all -- a workaround for a
        # classification gate on `evaluate_ai_provenance` that has since been removed,
        # because authorship is not a fact about behavior change. The remap outliving
        # its cause would have been a lie about what classification was checked.
        provenance = verify_module.evaluate_ai_provenance(
            artifact["body"], artifact["classification"]
        )
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


def evaluate(
    repo_root: Path,
    commit_msg_file: Path,
    repo: str,
    *,
    list_paths: Any = None,
    read_file: Any = None,
) -> dict[str, Any]:
    issue_verify_closeout = _load_issue_verify_closeout()
    iter_refs = issue_verify_closeout.iter_close_keyword_refs
    artifacts = _issue_closeout_artifacts(
        repo_root,
        iter_refs,
        issue_verify_closeout.strip_code_fences,
        list_paths=list_paths,
        read_file=read_file,
    )
    commit_msg_file = commit_msg_file.resolve()
    raw_body = commit_msg_file.read_text(encoding="utf-8")
    sanitized_body = _strip_commit_comments(raw_body)
    scan_text = _close_keyword_scan_text(raw_body, sanitized_body)
    message_qualified = {(repo, number) for repo, number in iter_refs(scan_text)}
    message_refs = {number for _repo, number in message_qualified}
    # Pause carve-out (#444): a pausing resolution brief is persisted state, not
    # a closeout carrier — at pause time no honest critique/behavior ledger can
    # exist. The brief stays exempt only while the commit message close-keywords
    # none of its issue numbers; a `Close #N` overlap restores the full floor.
    # floor-addition-restraint: irreversible-boundary P5 floor, presence/form-only
    artifacts, pause_briefs, bare_numbers = partition_closeout_carriers(
        artifacts, message_refs, _close_keyword_numbers(scan_text, iter_refs, repo)
    )
    pause_reports = _pause_brief_reports(pause_briefs, issue_verify_closeout)
    for artifact in artifacts + pause_briefs:
        artifact.pop("body", None)
    if not artifacts and not bare_numbers and not pause_reports:
        return {"ok": True, "status": "not_applicable", "artifacts": [], "review_advisory": []}

    # Protected-target authorization runs HERE: after the close targets are known, and
    # before the sanitized carrier file is written. The temp file is this carrier's
    # first side effect, and an authorization check placed after it would be checking a
    # state it had already changed. Targets are normalized in memory only.
    authorization = _AUTHZ.authorize_commit_carrier(
        repo_root, message_qualified, artifacts, bare_numbers
    )
    # Dropped only AFTER authorization has consumed it: this is internal scratch, not
    # part of the report, but authorization is the one reader that needs it.
    for artifact in artifacts + pause_briefs:
        artifact.pop("qualified_numbers", None)
    if not authorization["authorized"]:
        return {
            "ok": False,
            "status": "refused",
            "artifacts": artifacts,
            "closeout_authorization": authorization,
            "reports": [],
            "review_advisory": [],
        }

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
        # Numbers this commit close-keywords in text the LEDGER floors cannot see.
        # Detection reads the raw body (git stores `#`-leading lines verbatim under
        # `-m`/`-F`); `_missing_close_keywords` reads the sanitized body with code
        # fences stripped. BOTH channels produce a number GitHub will act on and the
        # ledger will report missing, and neither can ever be cleared by adding a
        # ledger. Covering only the `#`-line half left the fenced half with exactly
        # the unfollowable remedy this field exists to end.
        "unsatisfiable_close_numbers": sorted(
            _close_keyword_numbers(scan_text, iter_refs, repo)
            - {
                number
                for _repo, number in iter_refs(
                    "\n".join(issue_verify_closeout.strip_code_fences(sanitized_body))
                )
            }
        ),
        "reports": reports,
        "review_advisory": _exemption_advisories(
            reports, issue_verify_closeout.review_advisory_for_classification
        ),
    }


# Everything below is prose the deleted human renderer carried and the structured
# report does not. This is the ONLY carrier that can block `git commit`, so a
# bare snake_case token here is how a gate earns a route-around: the payload has
# to say what the author must DO, not only which field failed.
_PAUSE_SUMMARY = (
    "a staged pausing resolution brief is missing its `AI-provenance:` line (the one "
    "requirement kept for pause-state briefs)."
)
_FAILURE_SUMMARY = (
    "this commit closes an issue (staged closeout artifact and/or a GitHub close keyword "
    "in the message) without a valid closeout carrier."
)
_PAUSE_REMEDIATION = (
    "Append one `AI-provenance:` line to the staged brief naming it as agent-drafted "
    "pause state (see the resolution-brief Persistence contract), then retry. Close "
    "keywords and the closeout ledger are not required while the brief is pausing and "
    "the commit message close-keywords none of its issue numbers."
)
_FAILURE_REMEDIATION = (
    "Put the close keywords and closeout ledger in the commit body, or unstage the issue "
    "closeout artifact. If a close keyword above has no staged artifact and you do not "
    "want to carry the full closeout ledger in this commit, rewrite the keyword to a bare "
    "`#N` reference (e.g. `close #123` -> `#123`) so GitHub does not auto-close the issue "
    "on push.",
    "If this close really is a question or a recorded decision, declare it with an "
    "explicit `Classification: question` / `Classification: decision-needed` line in the "
    "staged artifact. That exemption is never inferred from body text.",
)
# The HOTL floor was folded into the verdict while printing nothing about itself.
# `undispositioned` names the entry; only this sentence says what a valid value
# looks like and that DELETING an inert line is the right move.
_HOTL_REQUIREMENT = (
    "An `HOTL:` value must LEAD WITH a typed HOTL status (or local-only-by-contract), "
    "not merely mention one. If there was no live human loop, DELETE the line rather "
    "than writing `none`/`n/a` -- a body with no HOTL entry is inert and passes."
)
# `commit_msg_closeout_authorization.format_refusal` was this report's only route
# to the operator; its structured half is already in `closeout_authorization`, so
# only the remedy paragraph needs a home here.
_REFUSAL_REMEDIATION = (
    "Rewrite the close keyword to a bare `#N` reference so GitHub does not auto-close, "
    "or split the carrier so the protected issue is closed alone with its own evidence. "
    "This gate applies only to the protected issues above; unrelated closes are "
    "unaffected."
)
# `missing_fields` alone misdescribes the dominant cause (the field is present and
# carries a placeholder), and for a SHAPE finding it is outright wrong -- the field
# is present AND substantive, and only its shape failed.
_LEDGER_FIELD_NOTE = (
    "`missing_fields` covers absent, placeholder AND wrong-shape fields; each entry's "
    "own explanation is in `missing_field_reasons`."
)


# Without this the refusal is unactionable, not merely terse: the author sees
# `missing_close_keywords: [700]` on a message that visibly says `closes #700` and the
# printed remedy ("Put the close keywords and closeout ledger in the commit body") is
# already satisfied. Only rewording ends that, and only this sentence says so.
_UNSATISFIABLE_CLOSE_NOTE = (
    "At least one `missing_close_keywords` number appears in this message ONLY where "
    "the ledger parse cannot see it -- on a line beginning with `#` (dropped as a git "
    "comment) or inside a code fence (stripped before the ledger is read). GitHub acts "
    "on both, so no ledger you add will clear this. Move the reference into ordinary "
    "prose, off the start of its line and outside any fence (e.g. `... closes issue "
    "#700.`), then retry."
)


def report_payload(report: dict[str, Any]) -> dict[str, Any]:
    """Fold the remediation prose into the payload the gate emits."""
    payload = dict(report)
    if report["ok"]:
        return payload
    if report.get("status") == "refused":
        payload["summary"] = (
            "this commit's close targets are REFUSED by the evidence-boundary closeout "
            "authorization."
        )
        payload["remediation"] = [_REFUSAL_REMEDIATION]
        return payload
    failing = [item for item in report.get("reports", []) if not item.get("ok")]
    # Keyed on the FAILING reports only -- a passing non-pause report staged beside
    # a failing pause brief must not suppress the pause remedy text.
    pause_only = bool(failing) and all(item.get("trigger") == "pause-brief" for item in failing)
    payload["summary"] = _PAUSE_SUMMARY if pause_only else _FAILURE_SUMMARY
    payload["remediation"] = [_PAUSE_REMEDIATION] if pause_only else list(_FAILURE_REMEDIATION)
    if any(item.get("missing_fields") for item in failing):
        payload["ledger_field_note"] = _LEDGER_FIELD_NOTE
    unsatisfiable = set(report.get("unsatisfiable_close_numbers") or [])
    if unsatisfiable & {n for item in failing for n in (item.get("missing_close_keywords") or [])}:
        payload["unsatisfiable_close_note"] = _UNSATISFIABLE_CLOSE_NOTE
    if any((item.get("hotl_dispositions") or {}).get("undispositioned") for item in failing):
        payload["hotl_requirement"] = _HOTL_REQUIREMENT
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--commit-msg-file", type=Path, required=True)
    parser.add_argument("--repo", default="corca-ai/charness")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    report = evaluate(repo_root, args.commit_msg_file, args.repo)
    emit_yaml(report_payload(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"charness commit-msg: {exc}", file=sys.stderr)
        raise SystemExit(1)
