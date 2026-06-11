"""YouTube source acquisition for the web-fetch `domain-specific-route` stage."""

from __future__ import annotations

import json
import re
import shutil
import sys
import urllib.request
from html import unescape
from pathlib import Path
from typing import Callable, Sequence
from urllib.parse import parse_qs, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from acquisition_trace_lib import AcquisitionAttempt  # noqa: E402

STAGE_ID = "domain-specific-route"
UI_STAGE_ID = "youtube-browser-transcript-ui"
YOUTUBE_HOSTS = {"youtube.com", "youtu.be", "m.youtube.com", "www.youtube.com", "music.youtube.com"}


def normalized_host(url: str) -> str:
    host = (urlparse(url).netloc or "").lower().split(":", 1)[0]
    return host[4:] if host.startswith("www.") else host


def parse_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    host = normalized_host(url)
    if host == "youtu.be":
        return next((part for part in parsed.path.split("/") if part), None)
    if not host.endswith("youtube.com"):
        return None
    query_id = parse_qs(parsed.query).get("v", [None])[0]
    if query_id:
        return query_id
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 2 and parts[0] in {"shorts", "live", "embed"}:
        return parts[1]
    return None


def _metadata(info: dict[str, object]) -> dict[str, object]:
    chapters = info.get("chapters")
    chapter_count = len(chapters) if isinstance(chapters, list) else 0
    return {
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "channel_id": info.get("channel_id") or info.get("uploader_id"),
        "upload_date": info.get("upload_date"),
        "duration": info.get("duration"),
        "webpage_url": info.get("webpage_url"),
        "thumbnail": info.get("thumbnail"),
        "description": info.get("description"),
        "chapter_count": chapter_count,
    }


def _caption_entries(info: dict[str, object]) -> list[tuple[str, str, dict[str, object]]]:
    entries: list[tuple[str, str, dict[str, object]]] = []
    for source_key, source_type in (("subtitles", "manual"), ("automatic_captions", "automatic")):
        captions = info.get(source_key)
        if not isinstance(captions, dict):
            continue
        for language, variants in captions.items():
            if not isinstance(language, str) or not isinstance(variants, list):
                continue
            for variant in variants:
                if isinstance(variant, dict):
                    entries.append((language, source_type, variant))
    return entries


def _caption_sort_key(item: tuple[str, str, dict[str, object]]) -> tuple[int, int, str]:
    language, source_type, variant = item
    ext = str(variant.get("ext") or "")
    language_rank = 0 if language in {"en", "en-US", "ko", "ko-KR"} else 1
    source_rank = 0 if source_type == "manual" else 1
    ext_rank = 0 if ext in {"vtt", "srv3", "json3"} else 1
    return (language_rank + ext_rank, source_rank, language)


def _caption_text_from_json3(raw: str) -> str:
    payload = json.loads(raw)
    parts: list[str] = []
    for event in payload.get("events", []):
        if not isinstance(event, dict):
            continue
        for segment in event.get("segs", []):
            if isinstance(segment, dict) and isinstance(segment.get("utf8"), str):
                parts.append(segment["utf8"])
    return " ".join("".join(parts).split())


def _caption_text_from_vtt(raw: str) -> str:
    lines: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "WEBVTT" or stripped.startswith(("Kind:", "Language:", "NOTE")):
            continue
        if "-->" in stripped or stripped.isdigit():
            continue
        stripped = re.sub(r"<[^>]+>", "", stripped)
        lines.append(unescape(stripped))
    return " ".join(" ".join(lines).split())


def _caption_text(raw: str, ext: str) -> str:
    if ext == "json3":
        return _caption_text_from_json3(raw)
    return _caption_text_from_vtt(raw)


def _read_caption(variant: dict[str, object], *, fetch_url: Callable[[str], tuple[str, str | None]]) -> tuple[str | None, str | None]:
    inline = variant.get("data")
    if isinstance(inline, str) and inline.strip():
        raw, error = inline, None
    elif isinstance(variant.get("url"), str):
        raw, error = fetch_url(str(variant["url"]))
    else:
        return None, "caption-missing-url"
    if error:
        return None, error
    text = _caption_text(raw, str(variant.get("ext") or "vtt"))
    return (text, None) if text else (None, "caption-empty")


def _format_transcript(info: dict[str, object], text: str) -> str:
    metadata = _metadata(info)
    heading = metadata.get("title") or info.get("id") or "YouTube Video"
    lines = [
        f"# {heading}",
        "",
        "## Metadata",
        "",
    ]
    for key in ("channel", "upload_date", "duration", "webpage_url"):
        value = metadata.get(key)
        if value not in (None, ""):
            lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    lines.extend(["", "## Transcript", "", text.strip()])
    return "\n".join(lines).strip() + "\n"


def _classify_error(error: str) -> tuple[str, str]:
    lowered = error.lower()
    if any(token in lowered for token in ("captcha", "confirm you're not a bot", "confirm you are not a bot", "sign in", "verify")):
        return "captcha", "blocked"
    return "error", "fetch-failed"


def _attempt(
    *,
    status: str,
    error: str | None = None,
    details: dict[str, object] | None = None,
    output_chars: int = 0,
    confidence: str = "none",
    content_text: str | None = None,
) -> AcquisitionAttempt:
    return AcquisitionAttempt(
        stage_id=STAGE_ID,
        tool_id="yt-dlp",
        status=status,
        confidence=confidence,
        error=error,
        output_chars=output_chars,
        details=details or {},
        content_text=content_text,
        content_format="markdown" if content_text else None,
    )


def _default_fetch_url(url: str) -> tuple[str, str | None]:
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace"), None
    except Exception as exc:
        return "", f"{type(exc).__name__}:{str(exc)[:200]}"


def run_youtube_stage(
    url: str,
    *,
    run_command: Callable[[Sequence[str]], tuple[str, str | None]],
    fetch_url: Callable[[str], tuple[str, str | None]] = _default_fetch_url,
) -> list[AcquisitionAttempt]:
    video_id = parse_video_id(url)
    if video_id is None:
        return [_attempt(status="error", details={"reason": "missing-video-id"}, output_chars=0)]
    if shutil.which("yt-dlp") is None:
        return [
            _attempt(
                status="error",
                error="missing-tool:yt-dlp",
                details={"reason": "missing-tool", "video_id": video_id},
            )
        ]

    command = [
        "yt-dlp",
        "--dump-single-json",
        "--skip-download",
        "--no-playlist",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "all",
        url,
    ]
    output, error = run_command(command)
    if error:
        status, reason = _classify_error(error)
        return [_attempt(status=status, error=error, details={"reason": reason, "video_id": video_id})]
    try:
        info = json.loads(output)
    except json.JSONDecodeError as exc:
        return [
            _attempt(
                status="error",
                error=f"invalid-json:{exc.msg}",
                details={"reason": "invalid-json", "video_id": video_id},
                output_chars=len(output),
            )
        ]
    details: dict[str, object] = {
        "video_id": str(info.get("id") or video_id),
        "source_type": "youtube",
        "metadata": _metadata(info),
    }
    caption_errors: list[str] = []
    for language, source_type, variant in sorted(_caption_entries(info), key=_caption_sort_key):
        text, caption_error = _read_caption(variant, fetch_url=fetch_url)
        if caption_error:
            caption_errors.append(f"{language}:{caption_error}")
            continue
        if text:
            details.update(
                {
                    "source_type": "youtube-transcript",
                    "transcript_language": language,
                    "transcript_source": source_type,
                    "caption_ext": variant.get("ext") or "unknown",
                    "caption_errors": caption_errors,
                }
            )
            rendered = _format_transcript(info, text)
            return [
                _attempt(
                    status="success",
                    confidence="strong",
                    details=details,
                    output_chars=len(output),
                    content_text=rendered,
                )
            ]
    details["source_type"] = "youtube-metadata-only"
    details["caption_errors"] = caption_errors
    details["reason"] = "captions-unavailable"
    return [_attempt(status="metadata-only", confidence="weak", details=details, output_chars=len(output))]


def classify_source_identity(acquisition: dict[str, object]) -> str:
    route = acquisition.get("route")
    if not isinstance(route, dict) or route.get("route_id") != "yt-dlp-metadata":
        return "not-applicable"
    attempt = acquisition.get("selected_attempt")
    if not isinstance(attempt, dict):
        return "youtube-unavailable"
    details = attempt.get("details")
    source_type = details.get("source_type") if isinstance(details, dict) else None
    if attempt.get("stage_id") == UI_STAGE_ID:
        if attempt.get("status") == "success" and source_type == "youtube-transcript-browser-ui":
            return "youtube-transcript-browser-ui"
        if attempt.get("status") == "metadata-only":
            return "youtube-metadata-only"
        if attempt.get("status") in {"captcha", "login-wall"}:
            return "youtube-blocked"
        return "youtube-unavailable"
    if attempt.get("stage_id") != STAGE_ID:
        return "youtube-unavailable"
    if attempt.get("status") == "success" and source_type == "youtube-transcript":
        return "youtube-transcript"
    if attempt.get("status") == "metadata-only" or source_type == "youtube-metadata-only":
        return "youtube-metadata-only"
    if attempt.get("status") in {"captcha", "login-wall"}:
        return "youtube-blocked"
    return "youtube-unavailable"
