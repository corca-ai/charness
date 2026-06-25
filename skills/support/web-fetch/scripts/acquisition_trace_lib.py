from __future__ import annotations

from dataclasses import dataclass, field

SUCCESS_STATUSES = {"success", "metadata-only"}
BLOCKED_STATUSES = {"captcha", "login-wall", "error-page"}


@dataclass
class AcquisitionAttempt:
    stage_id: str
    tool_id: str | None
    status: str
    confidence: str = "none"
    elapsed_s: float = 0.0
    error: str | None = None
    output_chars: int = 0
    classification: dict[str, object] | None = None
    details: dict[str, object] = field(default_factory=dict)
    content_text: str | None = None
    content_format: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "stage_id": self.stage_id,
            "tool_id": self.tool_id,
            "status": self.status,
            "confidence": self.confidence,
            "elapsed_s": self.elapsed_s,
            "output_chars": self.output_chars,
        }
        if self.error:
            payload["error"] = self.error
        if self.classification is not None:
            payload["classification"] = self.classification
        if self.details:
            payload["details"] = self.details
        return payload


def should_stop(attempt: AcquisitionAttempt, *, proof_required: bool) -> bool:
    if attempt.details.get("diagnostic"):
        return False
    if attempt.status not in SUCCESS_STATUSES:
        return False
    if proof_required:
        return attempt.confidence == "strong"
    return attempt.confidence in {"strong", "weak"}


def has_success(attempts: list[AcquisitionAttempt], *, proof_required: bool) -> bool:
    return any(should_stop(attempt, proof_required=proof_required) for attempt in attempts)


def last_content_attempt(attempts: list[AcquisitionAttempt]) -> AcquisitionAttempt | None:
    for attempt in reversed(attempts):
        if attempt.status == "skipped" or attempt.details.get("diagnostic"):
            continue
        return attempt
    return None


def skip_attempt(stage_id: str, tool_id: str | None, *, reason: str) -> AcquisitionAttempt:
    return AcquisitionAttempt(
        stage_id=stage_id,
        tool_id=tool_id,
        status="skipped",
        confidence="none",
        details={"reason": reason},
    )


def has_stage(route: dict[str, object], stage_id: str) -> bool:
    plan = route.get("acquisition_plan") or []
    return any(isinstance(stage, dict) and stage.get("stage_id") == stage_id for stage in plan)


def _planned_stage_ids(route: dict[str, object]) -> list[str]:
    plan = route.get("acquisition_plan") or []
    return [
        str(stage["stage_id"])
        for stage in plan
        if isinstance(stage, dict) and stage.get("stage_id")
    ]


def _append_unvisited_plan_stages(
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    *,
    disposition: str,
    intent: str,
) -> None:
    attempted_stage_ids = {attempt.stage_id for attempt in attempts}
    tool_by_stage = {
        str(stage["stage_id"]): stage.get("tool_id")
        for stage in route.get("acquisition_plan", [])
        if isinstance(stage, dict) and stage.get("stage_id")
    }
    for stage_id in _planned_stage_ids(route):
        if stage_id in attempted_stage_ids:
            continue
        if disposition == "success":
            reason = "prior-stage-sufficient"
        elif stage_id == "archive-or-cache":
            reason = "not-implemented"
        elif stage_id == "clean-stop":
            reason = "terminal-state-recorded"
        elif stage_id == "agent-browser-network-recon" and intent != "collect":
            reason = "intent-not-collect"
        else:
            reason = "not-attempted"
        attempts.append(skip_attempt(stage_id, tool_by_stage.get(stage_id), reason=reason))
        attempted_stage_ids.add(stage_id)


def selected_attempt(attempts: list[AcquisitionAttempt]) -> AcquisitionAttempt | None:
    successes = [attempt for attempt in attempts if should_stop(attempt, proof_required=False)]
    if successes:
        strong = [attempt for attempt in successes if attempt.confidence == "strong"]
        return (strong or successes)[-1]
    return last_content_attempt(attempts)


def missing_capabilities(attempts: list[AcquisitionAttempt]) -> list[str]:
    capabilities: list[str] = []
    for attempt in attempts:
        if attempt.status != "skipped" or attempt.details.get("reason") != "missing-tool":
            continue
        if attempt.tool_id is not None and attempt.tool_id not in capabilities:
            capabilities.append(attempt.tool_id)
    return capabilities


def untried_routes(attempts: list[AcquisitionAttempt], *, disposition: str) -> list[dict[str, object]]:
    if disposition == "success":
        return []
    routes: list[dict[str, object]] = []
    for attempt in attempts:
        if attempt.status != "skipped":
            continue
        reason = attempt.details.get("reason")
        if reason in {"prior-stage-sufficient", "terminal-state-recorded"}:
            continue
        routes.append(
            {
                "stage_id": attempt.stage_id,
                "tool_id": attempt.tool_id,
                "reason": reason,
            }
        )
    return routes


def disposition_for_attempts(attempts: list[AcquisitionAttempt]) -> str:
    selected = selected_attempt(attempts)
    if selected is None:
        return "degraded"
    if selected.status == "invalid-proof":
        return "error"
    if selected.status == "success":
        return "success"
    if selected.status in BLOCKED_STATUSES:
        return "blocked"
    return "degraded"


def payload(
    url: str,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    disposition: str,
    *,
    intent: str = "single",
    include_selected_content: bool = False,
    selected_content_max_chars: int | None = None,
) -> dict[str, object]:
    _append_unvisited_plan_stages(route, attempts, disposition=disposition, intent=intent)
    selected = selected_attempt(attempts)
    selected_payload = selected.to_dict() if selected is not None else None
    result = {
        "source_url": url,
        "route": route,
        "disposition": disposition,
        "attempts": [attempt.to_dict() for attempt in attempts],
        "selected_attempt": selected_payload,
        "final_status": selected.status if selected is not None else "unknown",
        "final_confidence": selected.confidence if selected is not None else "none",
    }
    missing = missing_capabilities(attempts)
    if missing and disposition != "success":
        result["missing_capabilities"] = missing
    untried = untried_routes(attempts, disposition=disposition)
    if untried:
        result["untried_routes"] = untried
    if (
        include_selected_content
        and selected is not None
        and selected.status == "success"
        and selected.content_text is not None
    ):
        text = selected.content_text
        truncated = False
        original_chars = len(text)
        if selected_content_max_chars is not None and original_chars > selected_content_max_chars:
            text = text[:selected_content_max_chars]
            truncated = True
        result["selected_content"] = {
            "stage_id": selected.stage_id,
            "tool_id": selected.tool_id,
            "format": selected.content_format or "text",
            "text": text,
            "chars": len(text),
            "original_chars": original_chars,
            "truncated": truncated,
        }
    return result
