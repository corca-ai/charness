from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path
from typing import Any


def _load_local(module_name: str, alias: str | None = None):
    module_path = Path(__file__).resolve().parent / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(alias or module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_shared_helper():
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / "check_prescribed_skill_executed_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "check_prescribed_skill_executed_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/check_prescribed_skill_executed_lib.py not found")


ISSUE_CLOSE = _load_local("issue_close", "issue_verify_issue_close")
GIT_TIMEOUT_SECONDS = 10

CARRIERS = ("direct-commit", "pr-body", "manual-fallback")
CLASSIFICATIONS = ("bug", "feature", "deferred-work", "question", "decision-needed")
# Classifications that require a resolution critique sub-skill execution
# before closeout. ``question`` and ``decision-needed`` are step-7 discussion
# resolutions and do not run the critique substrate.
CRITIQUE_REQUIRED_CLASSIFICATIONS = ("bug", "feature", "deferred-work")
_CRITIQUE_LINE = re.compile(r"^\s*Critique\s*:\s*(.+?)\s*$", re.MULTILINE)
_CRITIQUE_BLOCKED = re.compile(r"^blocked\s+(.+)$", re.IGNORECASE)
MANUAL_FALLBACK_REASONS = (
    "auto-close-unsupported",
    "auto-close-failed-after-remote-verification",
    "operator-directed-manual-close",
)

_CLOSING_KEYWORD_RE = re.compile(
    r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?#(?P<number>\d+)\b"
)
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<name>.+?)\s*$")
_FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?(?P<name>[A-Za-z][A-Za-z -]{1,40}):\s*(?P<value>.*)$")
_PLACEHOLDER_VALUES = {"", "todo", "tbd", "missing", "n/a", "na"}


def _strip_code_fences(text: str) -> list[str]:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return lines


def _normalize_field_name(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"`", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _body_fields(text: str) -> dict[str, str]:
    lines = _strip_code_fences(text)
    fields: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        heading = _HEADING_RE.match(line)
        if heading:
            current = _normalize_field_name(heading.group("name"))
            fields.setdefault(current, [])
            continue
        inline = _FIELD_RE.match(line)
        if inline:
            current = _normalize_field_name(inline.group("name"))
            fields.setdefault(current, [])
            value = inline.group("value").strip()
            if value:
                fields[current].append(value)
            continue
        if current is not None and line.strip():
            fields[current].append(line.strip())
    return {key: "\n".join(value).strip() for key, value in fields.items()}


def _first_field(fields: dict[str, str], aliases: tuple[str, ...]) -> str | None:
    normalized_aliases = {_normalize_field_name(alias) for alias in aliases}
    for name, value in fields.items():
        if name in normalized_aliases:
            return value
    return None


def _has_substantive_value(value: str | None) -> bool:
    if value is None:
        return False
    normalized = _normalize_field_name(value)
    return normalized not in _PLACEHOLDER_VALUES and not normalized.startswith("missing ")


def _classification_requirements(classification: str) -> list[tuple[str, tuple[str, ...]]]:
    if classification == "bug":
        return [
            ("jtbd", ("jtbd",)),
            ("root_cause", ("root cause",)),
            ("debug_artifact", ("debug artifact",)),
            ("siblings", ("siblings", "sibling search")),
            ("prevention", ("prevention",)),
        ]
    if classification in {"feature", "deferred-work"}:
        return [
            ("jtbd", ("jtbd",)),
            ("boundary", ("boundary",)),
            ("resolution_brief", ("resolution brief",)),
            ("implementation", ("implementation",)),
            ("prevention", ("prevention",)),
        ]
    return [
        ("jtbd", ("jtbd",)),
        ("answer_or_decision", ("answer", "decision", "recorded decision")),
    ]


def _missing_ledger_fields(text: str, classification: str) -> list[str]:
    fields = _body_fields(text)
    missing: list[str] = []
    for field_id, aliases in _classification_requirements(classification):
        if not _has_substantive_value(_first_field(fields, aliases)):
            missing.append(field_id)
    if classification == "bug":
        siblings = _first_field(fields, ("siblings", "sibling search"))
        if siblings and not (
            re.search(r"(?i)\bdecision\b", siblings) and re.search(r"(?i)\bproof\b", siblings)
        ):
            missing.append("siblings_decision_and_proof")
    return missing


def _missing_close_keywords(text: str, numbers: list[int], repo: str) -> list[int]:
    found: set[int] = set()
    selected_repo = repo.lower()
    for match in _CLOSING_KEYWORD_RE.finditer("\n".join(_strip_code_fences(text))):
        qualified_repo = match.group("repo")
        if qualified_repo is not None and qualified_repo.lower() != selected_repo:
            continue
        found.add(int(match.group("number")))
    return [number for number in numbers if number not in found]


def _extract_critique_value(body: str) -> str | None:
    """Return the value of the first ``Critique:`` line in the carrier body.

    Lines inside code fences are stripped first via ``_strip_code_fences`` so
    a quoted example in the body cannot satisfy the gate.
    """
    plain = "\n".join(_strip_code_fences(body))
    match = _CRITIQUE_LINE.search(plain)
    if match is None:
        return None
    value = match.group(1).strip()
    return value or None


def _check_resolution_critique(
    *,
    repo_root: Path,
    body: str,
    classification: str,
) -> dict[str, Any]:
    """Run the shared closeout helper for a resolution critique.

    The wrapper extracts the ``Critique:`` carrier-body line and maps:
      - ``<path>`` -> ``--evidence resolution_critique:<path>``
      - ``blocked <host-signal>`` -> ``--skip resolution_critique:host-blocked-subagent: <signal>``

    The shared helper's ``_classification_requirements`` is **not** extended;
    this carrier-header check is an additive gate that runs before the
    existing ledger verification (per
    ``docs/prescribed-skill-closeout-contract.md``).
    """
    helper = _load_shared_helper()
    if classification not in CRITIQUE_REQUIRED_CLASSIFICATIONS:
        return {"ok": True, "skipped_classification": classification}
    value = _extract_critique_value(body)
    if value is None:
        return helper.check(
            repo_root=repo_root,
            required=["resolution_critique"],
            evidence={},
            skips={},
            kind="issue-resolution",
        )
    blocked_match = _CRITIQUE_BLOCKED.match(value)
    if blocked_match:
        signal = blocked_match.group(1).strip()
        return helper.check(
            repo_root=repo_root,
            required=["resolution_critique"],
            evidence={},
            skips={"resolution_critique": f"host-blocked-subagent: {signal}"},
            kind="issue-resolution",
        )
    return helper.check(
        repo_root=repo_root,
        required=["resolution_critique"],
        evidence={"resolution_critique": value},
        skips={},
        kind="issue-resolution",
    )


def _read_carrier_body(repo_root: Path, *, carrier: str, commit_ref: str | None, body_file: Path | None) -> str:
    if carrier == "direct-commit":
        if not commit_ref:
            raise RuntimeError("direct-commit carrier requires --commit-ref")
        try:
            result = subprocess.run(
                ["git", "show", "-s", "--format=%B", commit_ref],
                cwd=repo_root,
                check=False,
                capture_output=True,
                text=True,
                timeout=GIT_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            result = subprocess.CompletedProcess(
                ["git", "show", "-s", "--format=%B", commit_ref],
                124,
                str(exc.stdout or ""),
                f"timed out after {GIT_TIMEOUT_SECONDS}s",
            )
        if result.returncode != 0:
            raise RuntimeError(
                f"unable to read commit body for {commit_ref!r}: {result.stderr.strip()!r}"
            )
        return result.stdout
    if body_file is None:
        raise RuntimeError(f"{carrier} carrier requires --body-file")
    if not body_file.is_file():
        raise RuntimeError(f"carrier body file not found: {body_file}")
    return body_file.read_text(encoding="utf-8")


def _view_issue_state(
    repo_root: Path,
    *,
    repo: str,
    number: int,
    backend: dict[str, Any],
    json_fields: str = "number,state,url",
) -> dict[str, Any]:
    commands = backend.get("commands") or {}
    if backend.get("id", "gh") != "gh" and commands.get("view") is None:
        raise RuntimeError(
            "closeout state verification requires backend commands.view; "
            "carrier text alone is not issue closeout"
        )
    argv = ISSUE_CLOSE._resolve_op(
        backend,
        "view",
        ISSUE_CLOSE.GH_VIEW_DEFAULT,
        ISSUE_CLOSE.VIEW_PLACEHOLDERS,
        required=frozenset({"repo", "number"}),
        repo=repo,
        number=str(number),
        json_fields=json_fields,
    )
    try:
        result = subprocess.run(
            argv,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=ISSUE_CLOSE.BACKEND_TIMEOUT_SECONDS,
        )
    except OSError as exc:
        raise RuntimeError(f"issue state verification command failed to start: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(
            argv,
            124,
            str(exc.stdout or ""),
            f"timed out after {ISSUE_CLOSE.BACKEND_TIMEOUT_SECONDS}s",
        )
    if result.returncode != 0:
        raise RuntimeError(
            f"issue state verification failed for {repo}#{number}: "
            f"exit={result.returncode} stderr={result.stderr.strip()!r}"
        )
    try:
        payload = json.loads(result.stdout)
    except Exception as exc:
        raise RuntimeError(f"issue state verification returned invalid JSON: {exc}") from exc
    return payload


def _manual_comment_found(body: str, state_payload: dict[str, Any]) -> bool:
    expected = body.strip()
    comments = state_payload.get("comments")
    if not isinstance(comments, list):
        return False
    for comment in comments:
        if not isinstance(comment, dict):
            continue
        comment_body = str(comment.get("body", "")).strip()
        if comment_body == expected:
            return True
    return False


def verify_closeout(
    *,
    repo_root: Path,
    repo: str,
    numbers: list[int],
    classification: str,
    carrier: str,
    backend: dict[str, Any],
    commit_ref: str | None = None,
    body_file: Path | None = None,
    manual_fallback_reason: str | None = None,
    expect_state: str | None = None,
) -> dict[str, Any]:
    if not numbers:
        raise RuntimeError("verify-closeout requires at least one --number")
    if classification not in CLASSIFICATIONS:
        raise RuntimeError(f"unknown classification: {classification}")
    if carrier not in CARRIERS:
        raise RuntimeError(f"unknown carrier: {carrier}")
    if carrier == "manual-fallback" and manual_fallback_reason not in MANUAL_FALLBACK_REASONS:
        raise RuntimeError(
            "manual-fallback carrier requires --manual-fallback-reason "
            f"one of {', '.join(MANUAL_FALLBACK_REASONS)}"
        )
    if carrier != "manual-fallback" and manual_fallback_reason is not None:
        raise RuntimeError("--manual-fallback-reason is only valid with --carrier manual-fallback")
    if expect_state is not None and expect_state.upper() != "CLOSED":
        raise RuntimeError("final closeout verification requires --expect-state CLOSED")

    body = _read_carrier_body(repo_root, carrier=carrier, commit_ref=commit_ref, body_file=body_file)
    resolution_critique_check = _check_resolution_critique(
        repo_root=repo_root, body=body, classification=classification
    )
    missing_close_keywords = [] if carrier == "manual-fallback" else _missing_close_keywords(body, numbers, repo)
    missing_fields = _missing_ledger_fields(body, classification)
    if carrier == "manual-fallback":
        reason_value = _first_field(_body_fields(body), ("manual close reason", "manual fallback reason"))
        if not _has_substantive_value(reason_value):
            missing_fields.append("manual_fallback_reason")

    verified_state: list[dict[str, Any]] = []
    state_mismatches: list[dict[str, Any]] = []
    manual_comment_missing: list[int] = []
    if expect_state is not None:
        expected = expect_state.upper()
        for number in numbers:
            json_fields = "number,state,url,comments" if carrier == "manual-fallback" else "number,state,url"
            state_payload = _view_issue_state(
                repo_root, repo=repo, number=number, backend=backend, json_fields=json_fields
            )
            verified_state.append(state_payload)
            returned_number = state_payload.get("number")
            if returned_number != number:
                state_mismatches.append(
                    {
                        "number": number,
                        "expected": number,
                        "actual": returned_number,
                        "field": "number",
                        "url": state_payload.get("url"),
                    }
                )
            actual = str(state_payload.get("state", "")).upper()
            if actual != expected:
                state_mismatches.append(
                    {
                        "number": number,
                        "expected": expected,
                        "actual": state_payload.get("state"),
                        "url": state_payload.get("url"),
                    }
                )
            if carrier == "manual-fallback" and not _manual_comment_found(body, state_payload):
                manual_comment_missing.append(number)

    critique_ok = resolution_critique_check.get("ok", True)
    ok = (
        critique_ok
        and not missing_close_keywords
        and not missing_fields
        and not state_mismatches
        and not manual_comment_missing
    )
    status = "verified" if ok and expect_state is not None else "carrier_verified" if ok else "failed"
    return {
        "ok": ok,
        "status": status,
        "repo": repo,
        "numbers": numbers,
        "classification": classification,
        "carrier": carrier,
        "commit_ref": commit_ref,
        "body_file": str(body_file) if body_file is not None else None,
        "manual_fallback_reason": manual_fallback_reason,
        "expect_state": expect_state,
        "missing_close_keywords": missing_close_keywords,
        "missing_fields": missing_fields,
        "state_mismatches": state_mismatches,
        "manual_comment_missing": manual_comment_missing,
        "resolution_critique_check": resolution_critique_check,
        "verified_state": verified_state,
    }
