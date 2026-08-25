#!/usr/bin/env python3
"""Conservative lineage proposals for duplicate-family fingerprint rotation.

The duplicate ratchet's content fingerprint is intentionally sensitive to a
member's normalized body.  It is therefore not a durable reviewed-family id.
This module compares the separately recorded member paths and hashes to emit
typed *proposals*.  It never suppresses a hard block or transfers a review
judgment automatically.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping

RELATIONS = (
    "rotation-proposal",
    "membership-growth",
    "membership-reduction",
    "family-merge-proposal",
    "new-family",
    "unbound-new-family",
)


def readiness(
    baseline_families: Iterable[Mapping[str, Any]],
    *,
    reviewed_ids: set[str],
) -> dict[str, Any]:
    """Report whether the baseline can support a stable lineage join."""
    missing = []
    for row in baseline_families:
        if not isinstance(row, Mapping):
            continue
        fingerprint = row.get("fingerprint")
        if isinstance(fingerprint, str) and fingerprint in reviewed_ids and not family_members(row)[1]:
            missing.append(fingerprint)
    if missing:
        return {
            "status": "unavailable",
            "reason_code": "baseline-member-paths-missing",
            "missing_fingerprints": sorted(set(missing)),
        }
    return {"status": "ready", "reason_code": None, "missing_fingerprints": []}


def _paths(rows: Iterable[Mapping[str, Any]] | None) -> set[str]:
    paths: set[str] = set()
    for row in rows or []:
        if not isinstance(row, Mapping):
            continue
        path = row.get("file")
        if isinstance(path, str) and path:
            paths.add(path.replace("\\", "/"))
    return paths


def family_members(family: Mapping[str, Any] | None) -> tuple[list[str], set[str]]:
    """Return duplicate-preserving hashes and stable repo-relative member paths."""
    family = family or {}
    raw_hashes = family.get("member_hashes", family.get("family_member_hashes"))
    hashes = sorted(str(value) for value in raw_hashes or [] if isinstance(value, str) and value)
    raw_paths = family.get("member_paths")
    paths = {str(value).replace("\\", "/") for value in raw_paths or [] if isinstance(value, str) and value}
    if not paths:
        paths = _paths(family.get("locations") or family.get("sample_locations"))
    return hashes, paths


def relation(old: Mapping[str, Any], new: Mapping[str, Any]) -> str:
    """Classify a candidate against one vanished family without accepting it."""
    old_hashes, old_paths = family_members(old)
    new_hashes, new_paths = family_members(new)
    if old_paths and new_paths:
        if old_paths == new_paths:
            return "rotation-proposal" if Counter(old_hashes) != Counter(new_hashes) else "new-family"
        if old_paths < new_paths:
            return "membership-growth"
        if new_paths < old_paths:
            return "membership-reduction"
        if old_paths & new_paths:
            return "family-merge-proposal"
    return "unbound-new-family"


def _candidate_rows(
    live_members: Mapping[str, list[str]],
    live_spans: Mapping[str, list[Mapping[str, Any]]],
) -> dict[str, dict[str, Any]]:
    return {
        fingerprint: {
            "fingerprint": fingerprint,
            "member_hashes": list(hashes),
            "locations": list(live_spans.get(fingerprint) or []),
        }
        for fingerprint, hashes in live_members.items()
    }


def propose(
    *,
    live_members: Mapping[str, list[str]],
    live_spans: Mapping[str, list[Mapping[str, Any]]],
    baseline_families: Iterable[Mapping[str, Any]],
    reviewed_ids: set[str],
) -> list[dict[str, Any]]:
    """Emit deterministic proposals for new fingerprints.

    A proposal is evidence for a reviewer, not an exemption.  Only vanished
    baseline families that were explicitly present in the review overlay are
    eligible for the ``rotation-proposal``/membership classifications.
    """
    baseline = {
        str(row.get("fingerprint")): dict(row)
        for row in baseline_families
        if isinstance(row, Mapping) and isinstance(row.get("fingerprint"), str)
    }
    live = _candidate_rows(live_members, live_spans)
    old_rows = []
    for fingerprint, row in baseline.items():
        if fingerprint not in live and fingerprint in reviewed_ids and family_members(row)[1]:
            old_rows.append(row)
    # A v3 baseline written before lineage paths existed cannot support a
    # membership comparison.  Silence is deliberate here: emitting one
    # ``unbound-new-family`` advisory per new fingerprint would turn missing
    # provenance into noise rather than an actionable proposal.
    if not old_rows:
        return []
    candidates = [row for fingerprint, row in live.items() if fingerprint not in baseline]
    proposals: list[dict[str, Any]] = []
    for candidate in sorted(candidates, key=lambda row: row["fingerprint"]):
        matches = []
        for old in old_rows:
            kind = relation(old, candidate)
            if kind != "unbound-new-family":
                matches.append((kind, str(old["fingerprint"])))
        if not matches:
            _hashes, candidate_paths = family_members(candidate)
            proposals.append({
                "new_fingerprint": candidate["fingerprint"],
                "relation": "new-family" if candidate_paths else "unbound-new-family",
                "review_status": "no-stable-member-binding" if not candidate_paths else "review-required",
            })
            continue
        relations = sorted({kind for kind, _ in matches})
        old_ids = sorted(old_id for _kind, old_id in matches)
        relation_name = "family-merge-proposal" if len(old_ids) > 1 else relations[0]
        proposals.append({
            "new_fingerprint": candidate["fingerprint"],
            "old_fingerprints": old_ids,
            "relation": relation_name,
            "review_status": "proposal-only",
        })
    return proposals
