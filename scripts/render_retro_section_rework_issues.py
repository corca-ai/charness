#!/usr/bin/env python3
"""Default ``rework``-issue attribution producer for retro prepare packets.

Stdout body attributes recent repository issues to the skills named in their
``Causing skill:`` line; the output is the section body the packet runner wraps.
An unavailable or malformed GitHub query is rendered as advisory ``UNAVAILABLE``
output and still exits 0 so a retro is not blocked.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Callable, Sequence
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

_CAUSING_SKILL = re.compile(
    r"^\s*(?:[-*]\s+)?(?:\*\*Causing skill:\*\*|\**Causing skill\**\s*:)\s*(.+?)\s*$",
    re.IGNORECASE,
)
# Operators annotate the line the way they write prose: the first live instance
# (#773) reads `Causing skill: achieve, issue (goal-run provider operations).`,
# and a comma split alone turned the parenthetical and the full stop into a
# third "skill". The annotation is context for a human reader, not an identity.
_PARENTHETICAL = re.compile(r"\([^()]*\)")


def parse_causing_skills(body: str) -> list[str]:
    """Return the ordered, unique skills from the first matching body line."""
    for line in body.splitlines():
        match = _CAUSING_SKILL.match(line)
        if match:
            skills: list[str] = []
            for raw_skill in _PARENTHETICAL.sub("", match.group(1)).split(","):
                skill = raw_skill.strip(" \t`*.;")
                if skill and skill not in skills:
                    skills.append(skill)
            return skills
    return []


def _created_date(issue: dict[str, object]) -> date | None:
    value = issue.get("createdAt")
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


Runner = Callable[..., subprocess.CompletedProcess[str]]


def fetch_issues(
    repo_root: Path,
    *,
    label: str,
    since: date,
    limit: int,
    repo: str | None = None,
    runner: Runner = run_process,
) -> list[dict[str, object]]:
    command = [
        "gh",
        "issue",
        "list",
        "--label",
        label,
        "--state",
        "all",
        "--limit",
        str(limit),
        "--json",
        "number,title,url,state,createdAt,closedAt,body",
    ]
    if repo:
        command.extend(["--repo", repo])
    try:
        result = runner(command, cwd=repo_root, timeout_seconds=60)
    except OSError as exc:
        return _unavailable_result(127, str(exc))
    if result.returncode != 0:
        return _unavailable_result(result.returncode, result.stderr)
    try:
        payload = json.loads(result.stdout)
    except (TypeError, json.JSONDecodeError):
        return _unavailable_result(result.returncode, "malformed JSON")
    if not isinstance(payload, list) or not all(isinstance(issue, dict) for issue in payload):
        return _unavailable_result(result.returncode, "malformed JSON")
    return [issue for issue in payload if (_created_date(issue) or date.min) >= since]


def _unavailable_result(code: int, stderr: object) -> list[dict[str, object]]:
    message = str(stderr).strip() or "(no stderr)"
    return [{"__unavailable__": f"exit code {code}: {message}"}]


def render_section(
    issues: list[dict[str, object]], since: date, label: str, repo_label: str | None = None
) -> str:
    """Render the section body for already-filtered issue dictionaries."""
    del repo_label
    if len(issues) == 1 and "__unavailable__" in issues[0]:
        return f"Rework issues UNAVAILABLE: {issues[0]['__unavailable__']}"

    attribution_counts: dict[str, int] = {}
    rendered_issues: list[tuple[dict[str, object], list[str]]] = []
    for issue in issues:
        body = issue.get("body")
        skills = parse_causing_skills(body if isinstance(body, str) else "") or ["unattributed"]
        rendered_issues.append((issue, skills))
        for skill in skills:
            attribution_counts[skill] = attribution_counts.get(skill, 0) + 1

    lines = [
        f"Rework issues labelled `{label}` created since {since.isoformat()} "
        f"({len(issues)} issue(s)):",
        "",
        "| Causing skill | Issues |",
        "| --- | --- |",
    ]
    lines.extend(
        f"| {skill} | {count} |"
        for skill, count in sorted(attribution_counts.items(), key=lambda item: (-item[1], item[0]))
    )
    lines.extend(
        [
            "",
            "Counts are per attribution; one issue naming multiple skills is counted once under each skill.",
            "",
        ]
    )
    if not rendered_issues:
        lines.append(f"- (none — no `{label}` issues since {since.isoformat()})")
    else:
        for issue, skills in rendered_issues:
            number = issue.get("number", "?")
            title = str(issue.get("title", "")).replace("\n", " ")
            state = str(issue.get("state", "")).upper()
            created = str(issue.get("createdAt", ""))[:10]
            url = issue.get("url", "")
            lines.append(f"- #{number} {title} ({state}, {created}; {', '.join(skills)}) {url}")
    return "\n".join(lines)


def main(
    argv: Sequence[str] | None = None,
    *,
    runner: Runner | None = None,
    today: date | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--repo")
    parser.add_argument("--label", default="rework")
    parser.add_argument("--since", type=date.fromisoformat)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args(argv)
    current_date = today or datetime.now(timezone.utc).date()
    since = args.since or current_date - timedelta(days=30)
    issues = fetch_issues(
        args.repo_root.resolve(),
        label=args.label,
        since=since,
        limit=args.limit,
        repo=args.repo,
        runner=runner or run_process,
    )
    print(render_section(issues, since, args.label, args.repo))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
