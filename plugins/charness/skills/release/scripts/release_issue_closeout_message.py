from __future__ import annotations

import importlib.util
import re
import tempfile
from pathlib import Path
from typing import Any

_CLASSIFICATION_LINE_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?classification\s*:\s*"
    r"(?P<classification>bug|feature|deferred-work|question|decision-needed)\s*$"
)


def _package_root(script_path: Path) -> tuple[Path, bool]:
    parts = script_path.parts
    for index in range(len(parts) - 3):
        if parts[index : index + 4] == ("skills", "public", "release", "scripts"):
            return Path(*parts[:index]), False
    for index in range(len(parts) - 2):
        if parts[index : index + 3] == ("skills", "release", "scripts"):
            return Path(*parts[:index]), True
    raise ImportError(f"cannot resolve release package root for {script_path}")


def _load_issue_closeout_module(script_name: str, module_name: str):
    here = Path(__file__).resolve()
    package_root, installed_first = _package_root(here)
    rels = (
        Path("skills/issue/scripts") / f"{script_name}.py",
        Path("skills/public/issue/scripts") / f"{script_name}.py",
    )
    if not installed_first:
        rels = tuple(reversed(rels))
    for rel in rels:
        candidate = package_root / rel
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location(module_name, candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise ImportError(
        f"issue skill {script_name}.py not found in source-tree skills/public/issue/scripts "
        "or installed skills/issue/scripts layout"
    )


try:
    _ISSUE_VALIDATE_CLOSEOUT_DRAFT = _load_issue_closeout_module(
        "issue_validate_closeout_draft", "release_issue_validate_closeout_draft"
    )
    _ISSUE_VERIFY_CLOSEOUT = _load_issue_closeout_module(
        "issue_verify_closeout", "release_issue_verify_closeout"
    )
    _ISSUE_CLOSEOUT_DRAFT_ERROR: str | None = None
except ImportError as exc:
    _ISSUE_VALIDATE_CLOSEOUT_DRAFT = None
    _ISSUE_VERIFY_CLOSEOUT = None
    _ISSUE_CLOSEOUT_DRAFT_ERROR = str(exc)

try:
    _ISSUE_AUTHZ = _load_issue_closeout_module(
        "issue_closeout_authorization", "release_message_closeout_authorization"
    )
except ImportError:
    _ISSUE_AUTHZ = None


def _refuse_unauthorized_message(repo_root: Path, repo: str, issue_numbers: list[int]) -> None:
    """Refuse before this module writes its temp commit-message file.

    This module is separately importable and reachable without the release preflight
    having run in the same process, so it re-authorizes rather than assuming an
    earlier caller did. Duplicated intentionally: the alternative is a temp carrier
    written for a close that the crosswalk forbids.
    """
    if _ISSUE_AUTHZ is None or not issue_numbers:
        return
    targets = [
        {"repository": repo, "issue_number": number, "source": "release-closeout-message"}
        for number in issue_numbers
    ]
    result = _ISSUE_AUTHZ.authorize(
        invoked_targets=targets, carrier_targets=[], carrier_source="release", repo_root=repo_root
    )
    if not result["authorized"]:
        raise SystemExit(_ISSUE_AUTHZ.refusal_message(result))


def _carrier_classification(carrier_body: str) -> str | None:
    match = _CLASSIFICATION_LINE_RE.search(carrier_body)
    if match is None:
        return None
    return match.group("classification")


def _transported_paragraphs(
    payload: dict[str, Any], close_issues: list[int], behavior_lines: list[str] | None = None
) -> list[str]:
    lines: list[str] = [
        f"Release: {payload['tag_name']}",
        f"Quality: {payload['quality_command']}",
    ]
    classification = str(payload.get("issue_closeout_classification") or "").strip()
    carrier_body = str(payload.get("issue_closeout_carrier_body") or "").strip()
    if carrier_body:
        carrier_classification = _carrier_classification(carrier_body)
        if carrier_classification is not None and classification and carrier_classification != classification:
            raise SystemExit(
                "release --close-issue carrier classification conflicts with "
                f"--close-issue-classification before quality or mutation: "
                f"carrier={carrier_classification} requested={classification}"
            )
        if classification and carrier_classification is None:
            lines.append(f"Classification: {classification}")
        lines.extend(paragraph.strip() for paragraph in re.split(r"\n\s*\n", carrier_body) if paragraph.strip())
    else:
        lines.append("")
        if classification:
            lines.append(f"Classification: {classification}")
        lines.extend(f"Close #{number}." for number in close_issues)
    lines.extend(line for line in (behavior_lines or []) if line.strip())
    return lines


def release_commit_body(
    payload: dict[str, Any], close_issues: list[int], behavior_lines: list[str] | None = None
) -> list[str]:
    if not close_issues:
        return []
    return _transported_paragraphs(payload, close_issues, behavior_lines)


def release_commit_paragraphs(
    payload: dict[str, Any], close_issues: list[int], behavior_lines: list[str] | None = None
) -> list[str]:
    return [payload["commit_message"], *release_commit_body(payload, close_issues, behavior_lines)]


def release_commit_message(payload: dict[str, Any], close_issues: list[int], behavior_lines: list[str] | None = None) -> str:
    return "\n\n".join(release_commit_paragraphs(payload, close_issues, behavior_lines)).rstrip() + "\n"


def release_content_close_keyword_refs(commit_message: str) -> list[dict[str, Any]]:
    """Return close refs forbidden on the pre-observer release-content commit."""
    if _ISSUE_VERIFY_CLOSEOUT is None:
        raise SystemExit(
            "release content commit validation requires the issue skill's closeout helper, "
            f"but it was not found on this install: {_ISSUE_CLOSEOUT_DRAFT_ERROR}"
        )
    return [
        {"repo": repo, "number": number}
        for repo, number in _ISSUE_VERIFY_CLOSEOUT.iter_close_keyword_refs(commit_message)
    ]


def validate_release_closeout_commit_message(
    repo_root: Path,
    *,
    repo: str,
    issue_numbers: list[int],
    classification: str,
    commit_message: str,
    commit_ref: str | None = None,
) -> dict[str, Any]:
    """Validate an exact commit carrier with issue-owned closeout semantics."""
    _refuse_unauthorized_message(repo_root, repo, issue_numbers)
    if _ISSUE_VALIDATE_CLOSEOUT_DRAFT is None or _ISSUE_VERIFY_CLOSEOUT is None:
        raise SystemExit(
            "release --close-issue carrier validation requires the issue skill's "
            f"closeout draft helpers, but they were not found on this install: {_ISSUE_CLOSEOUT_DRAFT_ERROR}\n"
            "vendor/install the `issue` skill alongside `release`, or drop --close-issue from this publish."
        )
    close_refs = _ISSUE_VERIFY_CLOSEOUT.iter_close_keyword_refs(commit_message)
    intended = set(issue_numbers)
    unexpected = [
        {"repo": qualified_repo, "number": number}
        for qualified_repo, number in close_refs
        if number not in intended
    ]
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".commitmsg", delete=False) as handle:
        handle.write(commit_message)
        temp_path = Path(handle.name)
    try:
        result = _ISSUE_VALIDATE_CLOSEOUT_DRAFT.validate_closeout_draft(
            verifier=_ISSUE_VERIFY_CLOSEOUT,
            repo_root=repo_root,
            repo=repo,
            numbers=issue_numbers,
            classification=classification,
            body_file=None,
            backend={},
            carrier="direct-commit",
            commit_message_file=temp_path,
            manual_fallback_reason=None,
        )
    finally:
        temp_path.unlink(missing_ok=True)
    result["commit_message"] = commit_message
    result["commit_ref"] = commit_ref
    result["close_keyword_refs"] = [
        {"repo": qualified_repo, "number": number} for qualified_repo, number in close_refs
    ]
    result["unexpected_close_keywords"] = unexpected
    if unexpected:
        result["ok"] = False
        # The draft vocabulary, not the post-publication one: `validate_closeout_draft`
        # set `draft_verified`, and a consumer keyed on the draft tokens saw neither.
        result["status"] = "draft_failed"
        # Sweep row S23, one level up: this is a SECOND post-hoc flip of a verdict whose
        # confirmation sentence was already rendered by `verify_closeout`. Without this the
        # release carrier shipped `ok: False, status: failed` alongside
        # `carrier-checked: ...` — the exact line the closeout-discipline contract tells
        # handoffs to quote instead of the status token.
        # No `is not None` guard: the early raise above makes a None module unreachable
        # here, and a guard would advertise a silent fallback that cannot happen.
        _ISSUE_VERIFY_CLOSEOUT.sync_confirmation_line(result)
    return result


def validate_release_closeout_draft(
    repo_root: Path,
    *,
    repo: str,
    issue_numbers: list[int],
    payload: dict[str, Any],
    classification: str,
    behavior_lines: list[str] | None = None,
) -> dict[str, Any]:
    paragraphs = release_commit_paragraphs(payload, issue_numbers, behavior_lines)
    commit_message = "\n\n".join(paragraphs).rstrip() + "\n"
    result = validate_release_closeout_commit_message(
        repo_root,
        repo=repo,
        issue_numbers=issue_numbers,
        classification=classification,
        commit_message=commit_message,
    )
    result["paragraphs"] = paragraphs
    return result


def fail_release_closeout_draft_validation(result: dict[str, Any]) -> None:
    missing_fields = ", ".join(result.get("missing_fields") or []) or "none"
    missing_keywords = ", ".join(f"#{number}" for number in (result.get("missing_close_keywords") or [])) or "none"
    resolution_critique_ok = result.get("resolution_critique_check", {}).get("ok")
    unexpected_keywords = ", ".join(
        f"{item.get('repo') + '#' if item.get('repo') else '#'}{item.get('number')}"
        for item in (result.get("unexpected_close_keywords") or [])
    ) or "none"
    raise SystemExit(
        "release --close-issue carrier failed issue-owned draft validation before quality or mutation.\n"
        f"classification: {result.get('classification')}\n"
        f"missing_close_keywords: {missing_keywords}\n"
        f"unexpected_close_keywords: {unexpected_keywords}\n"
        f"missing_fields: {missing_fields}\n"
        # The SECOND blocking carrier. The commit-msg one was taught to print the
        # library's diagnosis; this one was left dropping it, so an author refused
        # here still got a bare snake_case id. Round-2 review found the repair had
        # fixed one of two consumers -- the same one-call-site-of-two shape the
        # repo's recent lessons already name.
        + "".join(f"  {detail}\n" for detail in result.get("missing_field_reasons") or [])
        +
        f"resolution_critique_ok: {resolution_critique_ok}\n"
        f"behavioral_verdict_ok: {result.get('behavioral_verdict', {}).get('ok')}\n"
        f"ai_provenance_ok: {result.get('ai_provenance', {}).get('ok')}"
    )
