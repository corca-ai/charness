from __future__ import annotations

import re

# Charness goal/skill routing markers. An AGENTS.md that routes work through the
# Charness goal/skill surface (a `## Skill Routing` block that calls `find-skills`,
# or explicit Charness goal/achieve routing) is a repo where long autonomous
# slices accumulate. Such a repo should carry a commit-discipline rule so the
# whole implementation does not sit uncommitted until a human notices it after a
# long autonomous run.
GOAL_ROUTING_HEADING = "## Skill Routing"
GOAL_ROUTING_MARKERS = (
    "find-skills",
    "charness goal",
    "charness:achieve",
    "charness-artifacts/goals",
)

# A commit-discipline rule must convey BOTH related policies the issue names:
# (i) meaningful charness-artifacts/ changes are repo state and commit targets,
# (ii) meaningful implementation/workflow slices are committed as they finish and
# a task-completing goal is not reported done while meaningful work is uncommitted
# (unless deferral is explicit). The two phrase groups below isolate each policy
# so a body that only mentions artifacts still flags the missing slice rule.
COMMIT_DISCIPLINE_SLICE_SNIPPETS = (
    "commit meaningful work slices",
    "commit each meaningful slice",
    "commit meaningful slices",
    "commit meaningful implementation",
)
COMMIT_DISCIPLINE_NOT_DONE_SNIPPETS = (
    "uncommitted",
    "remains uncommitted",
    "left uncommitted",
)

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_whitespace(text: str) -> str:
    """Collapse whitespace runs to a single space so line-wrapped prose still matches."""

    return _WHITESPACE_RE.sub(" ", text)


def _has_any(text: str, snippets: tuple[str, ...]) -> bool:
    lowered = _normalize_whitespace(text).lower()
    return any(_normalize_whitespace(snippet).lower() in lowered for snippet in snippets)


def _has_goal_routing(agents_text: str) -> bool:
    lowered = _normalize_whitespace(agents_text).lower()
    has_heading = _normalize_whitespace(GOAL_ROUTING_HEADING).lower() in lowered
    mentions_charness_routing = any(marker in lowered for marker in GOAL_ROUTING_MARKERS)
    return has_heading and mentions_charness_routing


def commit_discipline_present(agents_text: str) -> bool:
    """True when AGENTS.md carries the meaningful-slice commit-discipline rule.

    Requires both halves: a "commit meaningful slices as they finish" rule AND a
    do-not-report-done-while-uncommitted rule, so a body that only repeats the
    charness-artifacts/ commit-target policy does not falsely pass.
    """

    return _has_any(agents_text, COMMIT_DISCIPLINE_SLICE_SNIPPETS) and _has_any(
        agents_text, COMMIT_DISCIPLINE_NOT_DONE_SNIPPETS
    )


def detect_commit_discipline_policy(
    agents_text: str,
) -> tuple[dict[str, object], list[dict[str, str]]]:
    has_goal_routing = _has_goal_routing(agents_text)
    present = commit_discipline_present(agents_text)
    findings: list[dict[str, str]] = []
    if has_goal_routing and not present:
        findings.append(
            {
                "type": "commit_discipline_drift",
                "message": (
                    "AGENTS.md routes work through Charness goal/skill routing but does not say "
                    "to commit meaningful implementation/workflow slices as they finish and not "
                    "report a task-completing goal as done while meaningful work remains "
                    "uncommitted unless deferral is explicit."
                ),
                "recommended_action": "add_meaningful_slice_commit_discipline_to_agents",
            }
        )
    return (
        {
            "has_goal_routing": has_goal_routing,
            "commit_discipline_present": present,
        },
        findings,
    )
