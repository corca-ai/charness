"""Helpers for source-identity verdicts over acquisition traces."""

from __future__ import annotations


def stage_attempts(acquisition: dict, stage_id: str) -> list[dict]:
    return [
        attempt
        for attempt in (acquisition.get("attempts") or [])
        if isinstance(attempt, dict) and attempt.get("stage_id") == stage_id
    ]


def attempt_endpoint(attempt: dict) -> object:
    details = attempt.get("details")
    return details.get("endpoint") if isinstance(details, dict) else None


def has_outcome(attempts: list[dict], outcome: str) -> bool:
    return any(isinstance(a.get("details"), dict) and a["details"].get("outcome") == outcome for a in attempts)


def direct_page_success(acquisition: dict) -> bool:
    return any(
        a.get("stage_id") == "direct-public-fetch"
        and a.get("status") == "success"
        and a.get("confidence") in {"strong", "weak"}
        for a in (acquisition.get("attempts") or [])
        if isinstance(a, dict)
    )
