#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
SUPPORT_ACQUIRE = SCRIPT_DIR.parents[2] / "support" / "web-fetch" / "scripts" / "acquire_public_url.py"
WRITE_RECORD = SCRIPT_DIR / "write_record.py"


def _run_json(command: list[str], *, input_text: str | None = None) -> dict[str, object]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or completed.stdout.strip() or f"command failed: {command!r}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"command did not emit JSON: {command!r}") from exc


def _slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.netloc or "public-url").lower().replace("www.", "", 1)
    path = "/".join(part for part in parsed.path.split("/") if part)
    identity = "-".join(part for part in (host, path) if part)
    safe = "".join(ch if ch.isalnum() else "-" for ch in identity).strip("-")
    safe = "-".join(part for part in safe.split("-") if part)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
    return f"{safe or 'public-url'}-{digest}"


def _attempt_lines(attempts: list[object]) -> list[str]:
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


def _is_open_gap(attempt: dict[str, object]) -> bool:
    if attempt.get("status") != "skipped":
        if attempt.get("stage_id") == "agent-browser-network-recon":
            return True
        if attempt.get("status") == "error":
            return True
        return False
    details = attempt.get("details")
    reason = details.get("reason") if isinstance(details, dict) else None
    return reason not in {"prior-stage-sufficient", "not-needed", "intent-not-collect"}


def _trace_payload(acquisition: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in acquisition.items() if key != "selected_content"}


def _fence_for(text: str) -> str:
    fence = "```"
    while fence in text:
        fence += "`"
    return fence


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def _selected_content_text(acquisition: dict[str, object]) -> tuple[dict[str, object] | None, str | None]:
    selected_content = acquisition.get("selected_content")
    if not isinstance(selected_content, dict):
        return None, None
    text = selected_content.get("text")
    if not isinstance(text, str) or not text.strip():
        return selected_content, None
    return selected_content, text


def _content_persistence(acquisition: dict[str, object], *, requested: bool) -> str:
    _selected_content, text = _selected_content_text(acquisition)
    if text is not None:
        return "extracted"
    if requested:
        return "unavailable"
    return "none"


def _extracted_content_lines(acquisition: dict[str, object], *, requested: bool) -> tuple[str, list[str]]:
    selected_content, text = _selected_content_text(acquisition)
    content_persistence = _content_persistence(acquisition, requested=requested)
    if content_persistence != "extracted" or selected_content is None or text is None:
        return content_persistence, []
    fence = _fence_for(text)
    return content_persistence, [
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


def _source_detail_lines(selected: dict[str, object]) -> list[str]:
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


def _render_record(url: str, acquisition: dict[str, object], *, persist_requested: bool) -> str:
    route = acquisition.get("route") if isinstance(acquisition.get("route"), dict) else {}
    selected = acquisition.get("selected_attempt") if isinstance(acquisition.get("selected_attempt"), dict) else {}
    access_modes = route.get("access_modes") if isinstance(route.get("access_modes"), list) else []
    attempts = acquisition.get("attempts") if isinstance(acquisition.get("attempts"), list) else []
    open_gaps = [
        item
        for item in attempts
        if isinstance(item, dict)
        and _is_open_gap(item)
    ]
    gap_lines = _attempt_lines(open_gaps) or ["- None recorded."]
    attempt_lines = _attempt_lines(attempts) or ["- None recorded."]
    content_persistence, content_lines = _extracted_content_lines(acquisition, requested=persist_requested)
    source_detail_lines = _source_detail_lines(selected)
    return "\n".join(
        [
            "# Gathered Public URL",
            "",
            f"- Source: {url}",
            "- Access Mode: support/web-fetch public route",
            f"- Content Persistence: `{content_persistence}`",
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
            *attempt_lines,
            "",
            "## Open Gaps",
            "",
            *gap_lines,
            *source_detail_lines,
            *content_lines,
            "",
            "## Trace JSON",
            "",
            "```json",
            json.dumps(_trace_payload(acquisition), ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    )


def _build_acquire_cmd(args: argparse.Namespace) -> list[str]:
    acquire_cmd = [
        sys.executable,
        str(SUPPORT_ACQUIRE),
        "--repo-root",
        str(args.repo_root),
        "--url",
        args.url,
        "--intent",
        args.intent,
        "--browser-mode",
        args.browser_mode,
        "--timeout",
        str(args.timeout),
    ]
    if args.direct_response_file is not None:
        acquire_cmd.extend(["--direct-response-file", str(args.direct_response_file)])
    if args.domain_route_response_file is not None:
        acquire_cmd.extend(["--domain-route-response-file", str(args.domain_route_response_file)])
    if args.live_domain_route:
        acquire_cmd.append("--live-domain-route")
    for expected in args.expect_text:
        acquire_cmd.extend(["--expect-text", expected])
    for pattern in args.expect_regex:
        acquire_cmd.extend(["--expect-regex", pattern])
    for field_path in args.expect_json_field:
        acquire_cmd.extend(["--expect-json-field", field_path])
    if args.persist_extracted_content:
        acquire_cmd.append("--include-selected-content")
        acquire_cmd.extend(["--selected-content-max-chars", str(args.max_extracted_content_chars)])
    return acquire_cmd


def _is_youtube_acquisition(acquisition: dict[str, object]) -> bool:
    route = acquisition.get("route")
    return isinstance(route, dict) and route.get("route_id") == "yt-dlp-metadata" and str(
        acquisition.get("source_identity", "")
    ).startswith("youtube-")


def main() -> int:
    parser = argparse.ArgumentParser(description="Gather an arbitrary public URL through support/web-fetch.")
    parser.add_argument("--url", required=True, help="Public URL to gather")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root where the gathered URL record should be written")
    parser.add_argument("--slug", default=None, help="Slug for the dated record (auto-derived from URL when omitted)")
    parser.add_argument("--date", default=None, help="Record date in YYYY-MM-DD (defaults to today UTC)")
    parser.add_argument("--intent", choices=("single", "collect"), default="single", help="single = one durable record; collect = bulk crawl session")
    parser.add_argument("--browser-mode", choices=("auto", "off", "always"), default="auto", help="When to use a browser fallback")
    parser.add_argument("--timeout", type=int, default=20, help="Per-stage timeout in seconds")
    parser.add_argument("--direct-response-file", type=Path, help="Pre-captured direct response file to seed the acquisition")
    parser.add_argument("--domain-route-response-file", type=Path, help="JSON map seeding the exact-source domain route (e.g. X/Twitter syndication) without a live fetch")
    parser.add_argument("--live-domain-route", action="store_true", help="Allow live fetch of exact-source domain endpoints (operator-authorized; off by default)")
    parser.add_argument("--expect-text", action="append", default=[], help="Required substring in the response (repeatable)")
    parser.add_argument("--expect-regex", action="append", default=[], help="Required regex pattern in the response (repeatable)")
    parser.add_argument("--expect-json-field", action="append", default=[], help="Required JSON field path in the response (repeatable)")
    parser.add_argument("--persist-extracted-content", action="store_true", help="Persist extracted page content in the record")
    parser.add_argument("--max-extracted-content-chars", type=_positive_int, default=200_000, help="Maximum chars of extracted content to persist")
    parser.add_argument("--execute", action="store_true", help="Write the record (otherwise dry-run)")
    args = parser.parse_args()

    acquisition = _run_json(_build_acquire_cmd(args))
    acquisition_disposition = str(acquisition.get("disposition", "unknown"))
    final_status = str(acquisition.get("final_status", "unknown"))
    final_confidence = str(acquisition.get("final_confidence", "none"))
    content_persistence = _content_persistence(acquisition, requested=args.persist_extracted_content)
    should_write_partial = _is_youtube_acquisition(acquisition) and acquisition_disposition in {"blocked", "degraded"}
    if acquisition_disposition != "success" and not should_write_partial:
        payload = {
            "status": "degraded" if acquisition_disposition == "degraded" else "blocked",
            "reason": f"acquisition-{acquisition_disposition}",
            "source_url": args.url,
            "acquisition_disposition": acquisition_disposition,
            "final_status": final_status,
            "final_confidence": final_confidence,
            "source_identity": acquisition.get("source_identity", "not-applicable"),
            "content_persistence": "none",
            "acquisition": acquisition,
            "write_record": None,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1
    record = _render_record(args.url, acquisition, persist_requested=args.persist_extracted_content)
    slug = args.slug or _slug_from_url(args.url)
    write_cmd = [
        sys.executable,
        str(WRITE_RECORD),
        "--repo-root",
        str(args.repo_root),
        "--slug",
        slug,
    ]
    if args.date:
        write_cmd.extend(["--date", args.date])
    if args.execute:
        write_cmd.append("--execute")
    write_payload = _run_json(write_cmd, input_text=record)
    payload = {
        "status": write_payload.get("status"),
        "record_status": write_payload.get("status"),
        "source_url": args.url,
        "acquisition_disposition": acquisition_disposition,
        "final_status": final_status,
        "final_confidence": final_confidence,
        "source_identity": acquisition.get("source_identity", "not-applicable"),
        "content_persistence": content_persistence,
        "acquisition": _trace_payload(acquisition),
        "write_record": write_payload,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
