"""Post-publish baton reconcile observation (north-star P5 shape).

The recurring escape this closes: a publish completes, the session ends, and
the repo's session-opening baton (e.g. ``docs/handoff.md``) keeps claiming the
previous release, so the next session routes its first action on stale state
(observed across three consecutive releases, v1.0.9–v1.0.11).

The step is an *observation that forces a question*, never a terminal green:
it records which release versions the baton's routing sections actually claim
right after a publish, and when the just-published version is absent it emits
a required action. It does not block the already-completed publish and it does
not declare the baton "done" — the populated record is the evidence, and the
release critique/retro reviewers judge it.

False-fire fence (plan-critique F3): only the baton's routing sections
(``## Current State`` / ``## Next Session``) are scanned, so legitimate
historical version mentions in ``## References`` / ``## Discuss`` never count
as claims; a baton with no version claim at all is an "ask", not a pass.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

BATON_ADAPTER_KEY = "post_publish_baton_path"
# floor-addition-restraint: this is a non-blocking recorded observation, not a
# blocking floor — the publish never fails on it; the recurrence it answers is
# recorded (the baton stayed stale across the v1.0.9–v1.0.11 publishes) and the
# fenced section list exists only to stop false fires on historical mentions.
BATON_SECTIONS = ("## Current State", "## Next Session")
_VERSION_TOKEN = re.compile(r"\bv?(\d+\.\d+\.\d+)\b")


def baton_section_text(markdown: str, sections: tuple[str, ...] = BATON_SECTIONS) -> str:
    """Return only the fenced routing sections of a baton document."""

    kept: list[str] = []
    keep = False
    for line in markdown.splitlines():
        if line.startswith("## "):
            keep = line.strip() in sections
            continue
        if keep:
            kept.append(line)
    return "\n".join(kept)


def observed_versions(markdown: str) -> list[str]:
    scoped = baton_section_text(markdown)
    seen: list[str] = []
    for match in _VERSION_TOKEN.finditer(scoped):
        version = match.group(1)
        if version not in seen:
            seen.append(version)
    return seen


def _required_action(path: str, target_version: str) -> str:
    return (
        f"Reconcile `{path}` (its `## Current State` / `## Next Session` routing sections) "
        f"to the just-published `{target_version}`, or record an explicit n/a disposition "
        "in the release record, before ending the session."
    )


def evaluate_baton_reconcile(
    repo_root: Path, adapter_data: dict[str, Any], *, target_version: str
) -> dict[str, Any]:
    """Observe the adapter-declared session baton right after a publish.

    Statuses: ``not_configured`` (adapter declares no baton), ``missing_file``,
    ``observed-current`` (the routing sections claim the published version),
    ``stale`` (they claim only other versions), ``no_version_claim`` (they
    claim none — cannot be auto-read either way, so the question is forced).
    """

    baton_relpath = str(adapter_data.get(BATON_ADAPTER_KEY, "") or "").strip()
    if not baton_relpath:
        return {"status": "not_configured"}
    record: dict[str, Any] = {
        "status": "",
        "path": baton_relpath,
        "target_version": target_version,
        "observed_versions": [],
    }
    baton_path = repo_root / baton_relpath
    if not baton_path.is_file():
        record["status"] = "missing_file"
        record["required_action"] = _required_action(baton_relpath, target_version)
        return record
    versions = observed_versions(baton_path.read_text(encoding="utf-8"))
    record["observed_versions"] = versions
    if target_version in versions:
        record["status"] = "observed-current"
        return record
    record["status"] = "stale" if versions else "no_version_claim"
    record["required_action"] = _required_action(baton_relpath, target_version)
    return record
