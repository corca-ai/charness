from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ISSUE_CLOSEOUT_CARRIER = "direct_post_publish_commit_body"


def _load_authorization_module():
    """The release lane's authorization module, or None on a partial vendoring.

    Absence must DEGRADE, not crash. This module is loaded by partial installs that
    copy only some release scripts, and by the existing behavioral-floor tests that
    simulate exactly that. Raising here replaced those installs' typed refusals with an
    ImportError traceback — turning a diagnosable "the issue skill is missing" into a
    bare stack trace, which is the failure mode the surrounding code already guards.
    """
    try:
        return _load_local_release_module("release_closeout_authorization")
    except ImportError:
        return None


def refuse_unauthorized_release_close(
    repo_root: Path, *, repo: str | None, issue_numbers: list[int], carrier_source: str
) -> dict[str, Any]:
    """Re-exported here so every existing release caller keeps one import site."""
    module = _load_authorization_module()
    if module is None:
        return {
            "authorized": True,
            "applies": False,
            "carrier_source": carrier_source,
            "crosswalk_status": "authorization_module_unavailable",
        }
    return module.refuse_unauthorized_release_close(
        repo_root, repo=repo, issue_numbers=issue_numbers, carrier_source=carrier_source
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
    _MESSAGE = _load_local_release_module("release_issue_closeout_message")
    _MESSAGE_ERROR: str | None = None
except ImportError as exc:
    _MESSAGE = None
    _MESSAGE_ERROR = str(exc)

try:
    _ARTIFACT = _load_local_release_module("release_issue_closeout_artifact")
    _ARTIFACT_ERROR: str | None = None
except ImportError as exc:
    _ARTIFACT = None
    _ARTIFACT_ERROR = str(exc)


def _artifact_action(name: str):
    if _ARTIFACT is not None:
        return getattr(_ARTIFACT, name)

    def unavailable(*_args, **_kwargs):
        raise SystemExit(
            "release issue closeout artifact helper is unavailable in this installation: "
            f"{_ARTIFACT_ERROR}"
        )

    return unavailable


commit_issue_closeout_artifact = _artifact_action("commit_issue_closeout_artifact")
commit_issue_closeout_carrier_artifact = _artifact_action("commit_issue_closeout_carrier_artifact")

# Every release-linked issue close is, by definition, a user-facing behavior
# claim (a released fix/feature/deferred-work item), so the classification gate
# `evaluate_behavioral_verdict` uses to exempt `question`/`decision-needed`
# carriers is force-applied here via a fixed classification rather than
# exempted by issue type the way the issue skill's own closeout is.


_RELEASE_BEHAVIORAL_CLASSIFICATION = "feature"


# The floors moved to `release_closeout_floors` when this file crossed its length gate.
# Reached through ONE cached, tolerant accessor and ONE delegator rather than four
# hand-written wrappers: the longhand version tripped the duplicate ratchet with eleven
# new families and the length gate on the same lines, both reporting that "resolve the
# module, branch on absence, forward the call" had been copied per function.
#
# Cached because re-executing the module per call is wasteful AND unpatchable -- a test
# that patches the returned object was handed a fresh copy next call, so its patch
# silently did nothing and read as "the refusal stopped working". Tolerant because this
# module is built to survive a partial install, and a module-level raise would turn every
# release that touches no issue into a crash. The rationale in full lives in
# `release_closeout_floors`' own docstring.
_UNLOADED = object()
_FLOORS_CACHE: object = _UNLOADED
_FLOORS_UNAVAILABLE = (
    "the release closeout floors module (release_closeout_floors.py) is not present beside "
    "release_issue_closeout.py on this install, so the rung-1 floors a release close must "
    "clear cannot be read. This refuses rather than passing: a check that could not run has "
    "not run."
)
_INERT = {"applies": False, "ok": True, "missing": []}


def _release_closeout_floors():
    global _FLOORS_CACHE
    if _FLOORS_CACHE is _UNLOADED:
        path = Path(__file__).resolve().with_name("release_closeout_floors.py")
        module = None
        if path.is_file():
            spec = importlib.util.spec_from_file_location("release_closeout_floors", path)
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
        _FLOORS_CACHE = module
    return _FLOORS_CACHE


def _delegate(name: str, *, issue_index: int | None = None, absent=None):
    """`issue_index` names where the issue list sits for the evaluators with an inert
    empty case -- read BEFORE the module resolution, so a release closing no issue is
    unaffected by a missing helper, a property this repo already had and already tested.
    `absent` defaults to refusing: a delegate that forgets to say gets the safe answer."""

    def call(*args, **kwargs):
        if issue_index is not None and (
            not (args[issue_index] if len(args) > issue_index else kwargs.get("issue_numbers", []))
        ):
            return dict(_INERT)
        floors = _release_closeout_floors()
        if floors is None:
            if absent is None:
                raise SystemExit(f"release issue closeout refused: {_FLOORS_UNAVAILABLE}")
            return absent(args, kwargs)
        return getattr(floors, name)(*args, **kwargs)

    call.__name__ = name
    return call


def _probe_absent(args, kwargs):
    numbers = args[2] if len(args) > 2 else kwargs.get("issue_numbers", [])
    return {"applies": True, "ok": False, "missing": list(numbers), "failed": [],
            "records": [], "library_unavailable": _FLOORS_UNAVAILABLE}


evaluate_release_behavioral_verdict = _delegate("evaluate_release_behavioral_verdict", issue_index=1)
fail_release_behavioral_verdict_floor = _delegate("fail_release_behavioral_verdict_floor")
evaluate_release_probe_record = _delegate(
    "evaluate_release_probe_record", issue_index=2, absent=_probe_absent
)
fail_release_probe_record_floor = _delegate("fail_release_probe_record_floor")
# `False` when the floors module is absent: that path already returns a refusal payload
# naming what to install, and inventing a veto on a severity nobody could read is a guess.
probe_record_blocks = _delegate("release_probe_record_blocks", absent=lambda *_a: False)


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


def release_content_close_keyword_refs(commit_message: str) -> list[dict[str, Any]]:
    return _message_helper().release_content_close_keyword_refs(commit_message)


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
    probe_record_lines: list[str] | None = None,
    classification: str | None = None,
    carrier_file: Path | None = None,
    carrier_source: str = "release",
) -> None:
    if not issue_numbers:
        payload["issue_closeout_preflight"] = {"status": "not_requested", "issues": []}
        payload["issue_closeout_behavioral_verdict"] = {"applies": False, "ok": True, "missing": []}
        payload["issue_closeout_probe_record"] = {"applies": False, "ok": True, "missing": []}
        return
    # First statement after the empty-set early return, and ahead of every read, temp
    # write, draft validation, bump, and publication below.
    payload["issue_closeout_authorization"] = refuse_unauthorized_release_close(
        repo_root, repo=repo, issue_numbers=issue_numbers, carrier_source=carrier_source
    )
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
    # One rung deeper, and deliberately AFTER the presence floor: an issue with no behavior
    # line at all is that floor's refusal to report, and two floors naming the same missing
    # line is how a failure report starts double-counting.
    probe_record = evaluate_release_probe_record(
        list(behavior_lines or []), list(probe_record_lines or []), issue_numbers, repo_root
    )
    payload["issue_closeout_probe_record"] = probe_record
    if not probe_record["ok"] and probe_record_blocks():
        fail_release_probe_record_floor(probe_record)
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
    probe_record_lines: list[str] | None = None,
    carrier_source: str = "release",
) -> None:
    if not issue_numbers:
        payload["issue_closeout"] = {"status": "not_requested", "issues": []}
        return
    # Re-authorized here rather than trusting the preflight's earlier pass: this
    # function reaches `gh issue close` directly, and the resume/recovery entrypoints
    # can call it without the preflight having run at all in this process.
    refuse_unauthorized_release_close(
        repo_root, repo=repo, issue_numbers=issue_numbers, carrier_source=carrier_source
    )
    # RE-RUN HERE FOR THE SAME REASON THE AUTHORIZATION IS RE-RUN, and the comment above is
    # the evidence: this function reaches `gh issue close` directly, and resume/recovery can
    # call it with no preflight in this process. Guarding only the preflight would leave one
    # of two entrypoints to an irreversible boundary unguarded -- which is, precisely, the
    # third of the three 2026-08-18 refutations this floor exists to answer, reproduced in
    # the wiring of its own countermeasure.
    # BOTH floors, not just the probe one. The probe floor is deliberately inert on silence
    # -- an issue with no behavior line owes nothing HERE, because the behavioral-verdict
    # floor already refuses that silence. Re-running only the probe floor therefore left the
    # cheapest possible input (`behavior_lines=[]`, which is the argparse default) passing
    # straight through to `gh issue close`: a guard that fires only when the caller
    # volunteers something to check is not a guard.
    behavioral_verdict = evaluate_release_behavioral_verdict(list(behavior_lines or []), issue_numbers)
    payload["issue_closeout_behavioral_verdict"] = behavioral_verdict
    if not behavioral_verdict["ok"]:
        fail_release_behavioral_verdict_floor(behavioral_verdict)
    probe_record = evaluate_release_probe_record(
        list(behavior_lines or []), list(probe_record_lines or []), issue_numbers, repo_root
    )
    payload["issue_closeout_probe_record"] = probe_record
    if not probe_record["ok"] and probe_record_blocks():
        fail_release_probe_record_floor(probe_record)
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
                    "- Auto-close carrier: post-publication evidence carrier commit.",
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
