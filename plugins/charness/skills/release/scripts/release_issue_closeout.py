from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ISSUE_CLOSEOUT_CARRIER = "direct_release_commit_body"


def _package_root(script_path: Path) -> tuple[Path, bool]:
    parts = script_path.parts
    for index in range(len(parts) - 3):
        if parts[index : index + 4] == ("skills", "public", "release", "scripts"):
            return Path(*parts[:index]), False
    for index in range(len(parts) - 2):
        if parts[index : index + 3] == ("skills", "release", "scripts"):
            return Path(*parts[:index]), True
    raise ImportError(f"cannot resolve release package root for {script_path}")


def _load_issue_closeout_body_lib():
    """Import the issue skill's closeout body-check helper without modifying it,
    so the release close-issue boundary reuses the SAME rung-1
    behavioral-verdict presence floor the issue skill's own closeout already
    enforces, instead of a second copy of the parsing logic. Mirrors
    ``skills/public/handoff/scripts/draft_goal_from_chunk.py``'s
    ``_load_goal_artifact_lib`` cross-skill import pattern (the established way
    this repo shares a skill-owned library across skill boundaries). Supports
    both source-tree ``skills/public/issue`` and installed plugin
    ``skills/issue`` layouts.
    """
    here = Path(__file__).resolve()
    package_root, installed_first = _package_root(here)
    rels = (
        Path("skills/issue/scripts/issue_verify_closeout_body.py"),
        Path("skills/public/issue/scripts/issue_verify_closeout_body.py"),
    )
    if not installed_first:
        rels = tuple(reversed(rels))
    for rel in rels:
        candidate = package_root / rel
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location("release_issue_verify_closeout_body", candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise ImportError(
        "issue skill issue_verify_closeout_body.py not found in source-tree "
        "skills/public/issue/scripts or installed skills/issue/scripts layout"
    )


def _load_local_release_module(module_name: str):
    module_path = Path(__file__).resolve().with_name(f"{module_name}.py")
    if not module_path.is_file():
        raise ImportError(f"Unable to load {module_path}")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Degrade to absence rather than crashing the whole release CLI at import time
# (publish_release_cli.py / publish_release_plan.py load this module
# unconditionally, so every release command -- not just --close-issue -- would
# otherwise die on a portable install without the issue skill vendored
# alongside release). --close-issue still needs the floor, so a missing lib is
# refused with a typed message at the point the floor would actually run (see
# evaluate_release_behavioral_verdict), never silently skipped and never a bare
# traceback. Mirrors the try/except degrade in
# skills/public/handoff/scripts/plan_handoff_run.py:54-60.
try:
    _ISSUE_CLOSEOUT_BODY = _load_issue_closeout_body_lib()
    _ISSUE_CLOSEOUT_BODY_ERROR: str | None = None
except ImportError as exc:
    _ISSUE_CLOSEOUT_BODY = None
    _ISSUE_CLOSEOUT_BODY_ERROR = str(exc)

try:
    _MESSAGE = _load_local_release_module("release_issue_closeout_message")
    _MESSAGE_ERROR: str | None = None
except ImportError as exc:
    _MESSAGE = None
    _MESSAGE_ERROR = str(exc)

# Every release-linked issue close is, by definition, a user-facing behavior
# claim (a released fix/feature/deferred-work item), so the classification gate
# `evaluate_behavioral_verdict` uses to exempt `question`/`decision-needed`
# carriers is force-applied here via a fixed classification rather than
# exempted by issue type the way the issue skill's own closeout is.
_RELEASE_BEHAVIORAL_CLASSIFICATION = "feature"


def evaluate_release_behavioral_verdict(behavior_lines: list[str], issue_numbers: list[int]) -> dict[str, Any]:
    """Rung-1 presence floor (P5): mirrors the issue skill's own
    ``evaluate_behavioral_verdict`` onto the release close-issue boundary. A
    `Behavior #N: <...>` line (or the single-issue `Behavior: <...>` shorthand)
    naming a distinct evidence channel, or a typed non-`verified` disposition,
    satisfies it EQUALLY (F2a) -- it refuses *silence* only. Whether the named
    channel is genuinely distinct is the fresh-eye release closeout reviewer's
    judgment (rung-2), never this floor's.
    """
    if not issue_numbers:
        return {"applies": False, "ok": True, "missing": []}
    if _ISSUE_CLOSEOUT_BODY is None:
        raise SystemExit(
            "release --close-issue requires the issue skill's "
            "issue_verify_closeout_body.py (the behavioral-verdict floor helper), but it was "
            f"not found on this install: {_ISSUE_CLOSEOUT_BODY_ERROR}\n"
            "vendor/install the `issue` skill alongside `release` on this host, or drop "
            "--close-issue from this publish."
        )
    return _ISSUE_CLOSEOUT_BODY.evaluate_behavioral_verdict(
        "\n".join(behavior_lines), _RELEASE_BEHAVIORAL_CLASSIFICATION, issue_numbers
    )


def fail_release_behavioral_verdict_floor(verdict: dict[str, Any]) -> None:
    # floor-addition-restraint: mirrors the issue skill's existing rung-1
    # behavioral-verdict presence floor onto the release close-issue boundary
    # (counterweight-verified north-star finding: release closeout bypassed it
    # entirely). Presence-only -- no new authored surface beyond the
    # `--close-issue-behavior` CLI flag this floor reads.
    raise SystemExit(
        "release issue closeout refused: missing per-issue behavioral-verdict line.\n"
        f"issues without a `Behavior #N:` line (or typed non-verified disposition): {verdict.get('missing')}\n"
        'pass `--close-issue-behavior "Behavior #<N>: <distinct-channel or disposition>"` '
        "(repeat per issue; the single-issue shorthand `Behavior: <...>` also matches) "
        "before release closes a linked issue."
    )


def github_repo_slug(repo_root: Path, backend: dict[str, Any], *, run) -> str | None:
    if backend.get("id", "gh") != "gh":
        return None
    result = run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        cwd=repo_root,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    url_result = run(["gh", "repo", "view", "--json", "url", "--jq", ".url"], cwd=repo_root, check=False)
    match = re.search(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?/?$", url_result.stdout.strip())
    return match.group(1) if match else None


def release_commit_body(
    payload: dict[str, Any], close_issues: list[int], behavior_lines: list[str] | None = None
) -> list[str]:
    return _message_helper().release_commit_body(payload, close_issues, behavior_lines)


def _message_helper():
    if _MESSAGE is None:
        raise SystemExit(
            "release --close-issue requires release_issue_closeout_message.py, but it was not found on this install: "
            f"{_MESSAGE_ERROR}"
        )
    return _MESSAGE


def release_commit_message(payload: dict[str, Any], close_issues: list[int], behavior_lines: list[str] | None = None) -> str:
    return _message_helper().release_commit_message(payload, close_issues, behavior_lines)


def validate_release_closeout_draft(
    repo_root: Path,
    *,
    repo: str,
    issue_numbers: list[int],
    payload: dict[str, Any],
    classification: str,
    behavior_lines: list[str] | None = None,
) -> dict[str, Any]:
    return _message_helper().validate_release_closeout_draft(
        repo_root,
        repo=repo,
        issue_numbers=issue_numbers,
        payload=payload,
        classification=classification,
        behavior_lines=behavior_lines,
    )


def fail_release_closeout_draft_validation(result: dict[str, Any]) -> None:
    _message_helper().fail_release_closeout_draft_validation(result)


def validate_release_closeout_commit_message(
    repo_root: Path,
    *,
    repo: str,
    issue_numbers: list[int],
    classification: str,
    commit_message: str,
    commit_ref: str | None = None,
) -> dict[str, Any]:
    return _message_helper().validate_release_closeout_commit_message(
        repo_root,
        repo=repo,
        issue_numbers=issue_numbers,
        classification=classification,
        commit_message=commit_message,
        commit_ref=commit_ref,
    )


def issue_state(repo_root: Path, repo: str, number: int, *, run) -> dict[str, Any]:
    result = run(
        ["gh", "issue", "view", str(number), "--repo", repo, "--json", "number,state,url"],
        cwd=repo_root,
    )
    return json.loads(result.stdout)


def preflight_release_issues(
    repo_root: Path,
    *,
    repo: str | None,
    issue_numbers: list[int],
    payload: dict[str, Any],
    run,
    behavior_lines: list[str] | None = None,
    classification: str | None = None,
    carrier_file: Path | None = None,
) -> None:
    if not issue_numbers:
        payload["issue_closeout_preflight"] = {"status": "not_requested", "issues": []}
        payload["issue_closeout_behavioral_verdict"] = {"applies": False, "ok": True, "missing": []}
        return
    if classification is None:
        raise SystemExit(
            "release --close-issue requires --close-issue-classification before quality or mutation"
        )
    if carrier_file is None:
        raise SystemExit(
            "release --close-issue requires --close-issue-carrier-file before quality or mutation"
        )
    if not carrier_file.is_file():
        raise SystemExit(
            f"release --close-issue carrier file not found before quality or mutation: {carrier_file}"
        )
    payload["issue_closeout_classification"] = classification
    payload["issue_closeout_carrier_file"] = str(carrier_file)
    payload["issue_closeout_carrier_body"] = carrier_file.read_text(encoding="utf-8").strip()
    behavioral_verdict = evaluate_release_behavioral_verdict(list(behavior_lines or []), issue_numbers)
    payload["issue_closeout_behavioral_verdict"] = behavioral_verdict
    if not behavioral_verdict["ok"]:
        fail_release_behavioral_verdict_floor(behavioral_verdict)
    if repo is None:
        raise SystemExit(
            "release --close-issue requires a GitHub repo before mutation; "
            "pass --close-issue-repo or use a gh-backed release repository"
        )
    draft_validation = validate_release_closeout_draft(
        repo_root,
        repo=repo,
        issue_numbers=issue_numbers,
        payload=payload,
        classification=classification,
        behavior_lines=behavior_lines,
    )
    payload["issue_closeout_draft_validation"] = draft_validation
    if not draft_validation["ok"]:
        fail_release_closeout_draft_validation(draft_validation)
    verified: list[dict[str, Any]] = []
    for number in issue_numbers:
        try:
            state_payload = issue_state(repo_root, repo, number, run=run)
        except (SystemExit, OSError, json.JSONDecodeError) as exc:
            raise SystemExit(
                "release --close-issue preflight failed before mutation; "
                f"`gh issue view {number} --repo {repo}` must succeed.\n{exc}"
            ) from exc
        verified.append(
            {
                "number": state_payload.get("number", number),
                "state": state_payload.get("state"),
                "url": state_payload.get("url"),
                "carrier": ISSUE_CLOSEOUT_CARRIER,
            }
        )
    payload["issue_closeout_preflight"] = {
        "status": "verified",
        "repo": repo,
        "required_backend": "gh",
        "issues": verified,
    }


def ensure_release_issues_closed(
    repo_root: Path,
    *,
    repo: str | None,
    issue_numbers: list[int],
    payload: dict[str, Any],
    run,
    behavior_lines: list[str] | None = None,
) -> None:
    if not issue_numbers:
        payload["issue_closeout"] = {"status": "not_requested", "issues": []}
        return
    if repo is None:
        raise SystemExit("release close issue verification needs a GitHub repo; pass --close-issue-repo")
    preflight_by_number = {
        item.get("number"): item
        for item in payload.get("issue_closeout_preflight", {}).get("issues", [])
        if isinstance(item, dict)
    }
    verified: list[dict[str, Any]] = []
    for number in issue_numbers:
        manual_fallback_used = False
        state_payload = issue_state(repo_root, repo, number, run=run)
        if state_payload.get("state") != "CLOSED":
            manual_fallback_used = True
            comment = "\n".join(
                [
                    f"Resolved by release `{payload['tag_name']}`.",
                    "",
                    f"- Release: {payload.get('release_url') or 'published release URL unavailable'}",
                    f"- Commit: `{payload.get('commit_sha')}`",
                    "- Auto-close carrier: direct release commit body.",
                    "- Manual close reason: issue remained open after push/release verification.",
                    *(behavior_lines or []),
                ]
            )
            run(["gh", "issue", "close", str(number), "--repo", repo, "--comment", comment], cwd=repo_root)
            state_payload = issue_state(repo_root, repo, number, run=run)
        if state_payload.get("state") != "CLOSED":
            raise SystemExit(f"release issue closeout failed: {repo}#{number} is still {state_payload.get('state')}")
        issue_payload = dict(state_payload)
        issue_payload["carrier"] = ISSUE_CLOSEOUT_CARRIER
        issue_payload["manual_fallback_used"] = manual_fallback_used
        if number in preflight_by_number:
            issue_payload["preflight_state"] = preflight_by_number[number].get("state")
        verified.append(issue_payload)
    # `state-verified` (not `verified`): this only re-reads GitHub `state==CLOSED`
    # -- the same proxy the close mutation itself produced. It is never the
    # behavioral verdict (see `issue_closeout_behavioral_verdict`, the rung-1
    # presence floor above) and must not be read as one (P4).
    payload["issue_closeout"] = {"status": "state-verified", "repo": repo, "issues": verified}


def commit_issue_closeout_artifact(
    repo_root: Path,
    *,
    write_artifact,
    payload: dict[str, Any],
    fresh_checkout_payload: dict[str, Any],
    artifact_relpath: str,
    expected_release_url: str | None,
    remote: str,
    branch: str,
    run,
) -> None:
    write_artifact(
        fresh_checkout_payload=fresh_checkout_payload,
        release_url=payload.get("release_url") or expected_release_url,
        issue_closeout=payload["issue_closeout"],
    )
    run(["git", "add", artifact_relpath], cwd=repo_root)
    run(["git", "commit", "-m", f"Record release issue closeout for {payload['tag_name']}"], cwd=repo_root)
    run(["git", "push", remote, branch], cwd=repo_root)
    payload["issue_closeout_commit_sha"] = run(["git", "rev-parse", "HEAD"], cwd=repo_root).stdout.strip()
