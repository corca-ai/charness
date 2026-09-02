"""Protected-target authorization for the commit-message closeout carrier.

Split out of `check_issue_closeout_commit_msg.py` as its own cohesive unit: that
module owns the closeout LEDGER floors (classification, close keywords, critique,
behavioural verdict), and this one owns the separate question of whether the commit's
close targets may be closed at all. They fail differently and are read by different
people, so they are worth separating rather than co-resident under a length cap.

The ordering contract lives with the caller, not here: authorization must run before
the sanitized carrier temp file is written, because that write is the carrier's first
side effect. `tests/quality_gates/test_closeout_authorization_ingress.py` asserts the
file does not exist after a refusal, which is what actually holds the ordering.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

_SKILL_RELS = (
    Path("skills/public/issue/scripts/issue_closeout_authorization.py"),
    Path("skills/issue/scripts/issue_closeout_authorization.py"),
)


def load_authorization_module(root: Path):
    """Load the issue skill's authorization helper, or None if it is absent.

    Absence degrades to permissive: an install without the issue skill must keep its
    ordinary commits working. The teeth live in the consuming repo's checked-in
    crosswalk, and a repo without one has nothing to protect.
    """
    for rel in _SKILL_RELS:
        candidate = root / rel
        if not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location(
            "commit_msg_closeout_authorization_impl", candidate
        )
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None


def authorize_commit_carrier(
    repo_root: Path,
    message_refs: set[tuple[str | None, int]],
    artifacts: list[dict[str, Any]],
    bare_numbers: list[int],
) -> dict[str, Any]:
    """Authorize the commit carrier over its AGGREGATE close targets.

    The message's close keywords are the invoked targets — they are what actually makes
    GitHub close something on push. The staged closeout artifacts are the
    carrier-derived targets. Both are folded in, so a commit that close-keywords a
    protected issue while staging an artifact for another is ONE combined carrier
    subject to the singleton rule, not two independent closes each of which looks fine
    on its own.

    Each target keeps the REPOSITORY its close keyword named. Collapsing to bare numbers
    let `Fixes acme/other-repo#514` normalize into this repo's protected #514 and block a
    commit aimed at an unrelated repository — throwing away, at the call site, exactly
    the information the gate's foreign-ref branch exists to use.
    """
    module = load_authorization_module(Path(__file__).resolve().parents[2])
    if module is None:
        return {
            "authorized": True,
            "applies": False,
            "crosswalk_status": "authorization_module_unavailable",
        }
    invoked: list[dict[str, Any]] = [
        {"repository": repo, "issue_number": number, "source": "commit-message-close-keyword"}
        for repo, number in sorted(message_refs, key=lambda item: (item[0] or "", item[1]))
    ]
    carrier = [
        {
            "repository": repo,
            "issue_number": number,
            "source": f"staged-artifact:{artifact['path']}",
        }
        for artifact in artifacts
        for repo, number in artifact["qualified_numbers"]
    ]
    seen_numbers = {number for _repo, number in message_refs}
    invoked.extend(
        {"issue_number": number, "source": "bare-close-keyword"}
        for number in bare_numbers
        if number not in seen_numbers
    )
    return module.authorize(
        invoked_targets=invoked,
        carrier_targets=carrier,
        carrier_source="commit-msg",
        repo_root=repo_root,
    )


def format_refusal(report: dict[str, Any]) -> str:
    """Refusal text for the one carrier that can stop `git commit`.

    Spelled out rather than left as a code: this reaches an author mid-commit with no
    other diagnostic surface, and the generic closeout-ledger footer would send them to
    fix something unrelated.
    """
    authorization = report.get("closeout_authorization", {})
    return "\n".join(
        [
            "charness commit-msg: this commit's close targets are REFUSED by the evidence-boundary "
            "closeout authorization.",
            f"  refusal: {authorization.get('refusal')}",
            f"  detail: {authorization.get('detail')}",
            f"  protected issues: {authorization.get('protected_issues')}",
            "Rewrite the close keyword to a bare `#N` reference so GitHub does not auto-close, or "
            "split the carrier so the protected issue is closed alone with its own evidence. This "
            "gate applies only to the protected issues above; unrelated closes are unaffected.",
        ]
    )
