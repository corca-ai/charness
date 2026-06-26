from __future__ import annotations

import json


def attempt_lines(attempts: list[object]) -> list[str]:
    lines: list[str] = []
    for item in attempts:
        if not isinstance(item, dict):
            continue
        tool = item.get("tool_id") or "direct"
        reason = ""
        details = item.get("details")
        if isinstance(details, dict) and details.get("reason"):
            reason = f" ({details['reason']})"
        error = f" error={item['error']}" if item.get("error") else ""
        lines.append(
            f"- `{item.get('stage_id', 'unknown')}` via `{tool}`: "
            f"{item.get('status', 'unknown')} / {item.get('confidence', 'none')}{reason}{error}"
        )
    return lines


def is_open_gap(attempt: dict[str, object]) -> bool:
    if attempt.get("status") != "skipped":
        if attempt.get("stage_id") == "agent-browser-network-recon":
            return True
        if attempt.get("status") == "error":
            return True
        return False
    details = attempt.get("details")
    reason = details.get("reason") if isinstance(details, dict) else None
    return reason not in {"prior-stage-sufficient", "not-needed", "intent-not-collect"}


def trace_payload(acquisition: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in acquisition.items() if key != "selected_content"}


def _fence_for(text: str) -> str:
    fence = "```"
    while fence in text:
        fence += "`"
    return fence


def selected_content_text(acquisition: dict[str, object]) -> tuple[dict[str, object] | None, str | None]:
    selected_content = acquisition.get("selected_content")
    if not isinstance(selected_content, dict):
        return None, None
    text = selected_content.get("text")
    if not isinstance(text, str) or not text.strip():
        return selected_content, None
    return selected_content, text


def content_persistence(acquisition: dict[str, object], *, requested: bool) -> str:
    _selected_content, text = selected_content_text(acquisition)
    if text is not None:
        return "extracted"
    if requested:
        return "unavailable"
    return "none"


def extracted_content_lines(acquisition: dict[str, object], *, requested: bool) -> tuple[str, list[str]]:
    selected_content, text = selected_content_text(acquisition)
    persistence = content_persistence(acquisition, requested=requested)
    if persistence != "extracted" or selected_content is None or text is None:
        return persistence, []
    fence = _fence_for(text)
    return persistence, [
        "",
        "## Extracted Content",
        "",
        f"- Source Stage: `{selected_content.get('stage_id', 'unknown')}`",
        f"- Format: `{selected_content.get('format', 'text')}`",
        f"- Chars: `{selected_content.get('chars', len(text))}`",
        f"- Original Chars: `{selected_content.get('original_chars', len(text))}`",
        f"- Truncated: `{selected_content.get('truncated', False)}`",
        "",
        f"{fence}text",
        text,
        fence,
    ]


def source_detail_lines(selected: dict[str, object]) -> list[str]:
    details = selected.get("details")
    if not isinstance(details, dict) or not any(
        details.get(key) not in (None, "", [], {}) for key in ("source_type", "video_id", "reason")
    ):
        return []
    lines = ["", "## Source Details", ""]
    if details.get("source_type"):
        lines.append(f"- Source Type: `{details.get('source_type')}`")
    for key in ("video_id", "transcript_language", "transcript_source", "caption_ext", "reason"):
        value = details.get(key)
        if value not in (None, "", [], {}):
            lines.append(f"- {key.replace('_', ' ').title()}: `{value}`")
    metadata = details.get("metadata")
    if isinstance(metadata, dict):
        for key in ("title", "channel", "upload_date", "duration", "thumbnail", "chapter_count"):
            value = metadata.get(key)
            if value not in (None, "", [], {}):
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    caption_errors = details.get("caption_errors")
    if isinstance(caption_errors, list) and caption_errors:
        rendered = ", ".join(str(item) for item in caption_errors)
        lines.append(f"- Caption Errors: `{rendered}`")
    return lines


def source_resolution_lines(acquisition: dict[str, object]) -> list[str]:
    resolution = acquisition.get("source_resolution")
    if not isinstance(resolution, dict):
        return []
    lines = ["", "## Source Resolution", ""]
    for key in ("verdict", "terminal_state", "terminal_category", "required_capability", "next_owner"):
        value = resolution.get(key)
        if value not in (None, "", [], {}):
            lines.append(f"- {key.replace('_', ' ').title()}: `{value}`")
    return lines


def render_record(url: str, acquisition: dict[str, object], *, persist_requested: bool) -> str:
    route = acquisition.get("route") if isinstance(acquisition.get("route"), dict) else {}
    selected = acquisition.get("selected_attempt") if isinstance(acquisition.get("selected_attempt"), dict) else {}
    access_modes = route.get("access_modes") if isinstance(route.get("access_modes"), list) else []
    attempts = acquisition.get("attempts") if isinstance(acquisition.get("attempts"), list) else []
    open_gaps = [
        item
        for item in attempts
        if isinstance(item, dict)
        and is_open_gap(item)
    ]
    gap_lines = attempt_lines(open_gaps) or ["- None recorded."]
    rendered_attempt_lines = attempt_lines(attempts) or ["- None recorded."]
    extracted_persistence, content_lines = extracted_content_lines(acquisition, requested=persist_requested)
    detail_lines = source_detail_lines(selected)
    resolution_lines = source_resolution_lines(acquisition)
    return "\n".join(
        [
            "# Gathered Public URL",
            "",
            f"- Source: {url}",
            "- Access Mode: support/web-fetch public route",
            f"- Content Persistence: `{extracted_persistence}`",
            f"- Route: `{route.get('route_id', 'unknown')}`",
            f"- Route Family: `{route.get('route_family', 'unknown')}`",
            f"- Route Access Modes: {', '.join(str(mode) for mode in access_modes) or 'unknown'}",
            f"- Disposition: `{acquisition.get('disposition', 'unknown')}`",
            f"- Final Status: `{acquisition.get('final_status', 'unknown')}`",
            f"- Final Confidence: `{acquisition.get('final_confidence', 'none')}`",
            f"- Source Identity: `{acquisition.get('source_identity', 'not-applicable')}`",
            "",
            "## Selected Attempt",
            "",
            f"- Stage: `{selected.get('stage_id', 'none')}`",
            f"- Tool: `{selected.get('tool_id') or 'direct'}`",
            f"- Status: `{selected.get('status', 'unknown')}`",
            f"- Confidence: `{selected.get('confidence', 'none')}`",
            "",
            "## Acquisition Trace",
            "",
            *rendered_attempt_lines,
            "",
            "## Open Gaps",
            "",
            *gap_lines,
            *resolution_lines,
            *detail_lines,
            *content_lines,
            "",
            "## Trace JSON",
            "",
            "```json",
            json.dumps(trace_payload(acquisition), ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    )
