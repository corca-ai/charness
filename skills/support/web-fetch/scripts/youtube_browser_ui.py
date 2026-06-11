"""YouTube transcript acquisition through the public page transcript UI."""

from __future__ import annotations

import json
import re
import shutil
from typing import Callable, Sequence

from acquisition_trace_lib import AcquisitionAttempt
from youtube_source import parse_video_id

UI_STAGE_ID = "youtube-browser-transcript-ui"


def _ui_attempt(
    *,
    status: str,
    error: str | None = None,
    details: dict[str, object] | None = None,
    output_chars: int = 0,
    confidence: str = "none",
    content_text: str | None = None,
) -> AcquisitionAttempt:
    return AcquisitionAttempt(
        stage_id=UI_STAGE_ID,
        tool_id="agent-browser",
        status=status,
        confidence=confidence,
        error=error,
        output_chars=output_chars,
        details=details or {},
        content_text=content_text,
        content_format="markdown" if content_text else None,
    )


def _format_ui_transcript(metadata: dict[str, object], transcript_lines: list[str]) -> str:
    heading = metadata.get("title") or metadata.get("video_id") or "YouTube Video"
    lines = [f"# {heading}", "", "## Metadata", ""]
    for source_key, label in (
        ("channel", "Channel"),
        ("publish_date", "Publish Date"),
        ("duration", "Duration"),
        ("webpage_url", "Webpage Url"),
    ):
        value = metadata.get(source_key)
        if value not in (None, ""):
            lines.append(f"- {label}: {value}")
    lines.extend(["", "## Transcript", "", "\n".join(transcript_lines).strip()])
    return "\n".join(lines).strip() + "\n"


def _extract_json_object(text: str, marker: str) -> dict[str, object] | None:
    start = text.find(marker)
    if start < 0:
        return None
    brace = text.find("{", start + len(marker))
    if brace < 0:
        return None
    try:
        payload, _idx = json.JSONDecoder().raw_decode(text[brace:])
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _metadata_from_player_response(text: str, url: str) -> dict[str, object]:
    player = _extract_json_object(text, "ytInitialPlayerResponse")
    video_details = player.get("videoDetails") if isinstance(player, dict) else None
    microformat = player.get("microformat") if isinstance(player, dict) else None
    renderer = microformat.get("playerMicroformatRenderer") if isinstance(microformat, dict) else None
    captions = player.get("captions") if isinstance(player, dict) else None
    tracklist = captions.get("playerCaptionsTracklistRenderer") if isinstance(captions, dict) else None
    tracks = tracklist.get("captionTracks") if isinstance(tracklist, dict) else None
    metadata: dict[str, object] = {"webpage_url": url}
    if isinstance(video_details, dict):
        metadata.update(
            {
                "video_id": video_details.get("videoId"),
                "title": video_details.get("title"),
                "channel": video_details.get("author"),
                "duration": video_details.get("lengthSeconds"),
                "description": video_details.get("shortDescription"),
                "view_count": video_details.get("viewCount"),
            }
        )
    if isinstance(renderer, dict):
        metadata["publish_date"] = renderer.get("publishDate") or renderer.get("uploadDate")
    if isinstance(tracks, list):
        metadata["caption_track_count"] = len(tracks)
        languages = [track.get("languageCode") for track in tracks if isinstance(track, dict) and track.get("languageCode")]
        if languages:
            metadata["caption_languages"] = languages
    return {key: value for key, value in metadata.items() if value not in (None, "")}


_SNAPSHOT_LABEL_RE = re.compile(r'button "((?:[^"\\]|\\.)*)" \[ref=')
_TIME_PREFIX_RE = re.compile(
    r"^(?:\d{1,2}:\d{2}(?::\d{2})?|\d+\s*(?:초|분|시간|second|seconds|minute|minutes|hour|hours)\b)\s*",
    re.IGNORECASE,
)
_TIME_TOKEN_RE = re.compile(
    r"(?:(?<=^)|(?<=\s))(?:\d{1,2}:\d{2}(?::\d{2})?|\d+\s*(?:초|분|시간))\s*",
    re.IGNORECASE,
)


def _decode_snapshot_label(raw: str) -> str:
    try:
        return json.loads(f'"{raw}"')
    except json.JSONDecodeError:
        return raw.replace(r"\"", '"')


def _clean_segment_label(label: str) -> str:
    cleaned = _TIME_PREFIX_RE.sub("", " ".join(label.split()))
    return _TIME_TOKEN_RE.sub("", cleaned).strip()


def extract_transcript_lines_from_snapshot(snapshot: str) -> list[str]:
    lines: list[str] = []
    in_transcript_panel = False
    for raw_line in snapshot.splitlines():
        line = raw_line.strip()
        if any(token in line for token in ('textbox "스크립트 검색"', 'textbox "Search transcript"')):
            in_transcript_panel = True
            continue
        if not in_transcript_panel:
            continue
        if lines and line.startswith(("- link ", "link ")):
            break
        match = _SNAPSHOT_LABEL_RE.search(line)
        if not match:
            continue
        cleaned = _clean_segment_label(_decode_snapshot_label(match.group(1)))
        if cleaned:
            lines.append(cleaned)
    return lines


def _open_transcript_script() -> str:
    return (
        "(() => { const root = document.querySelector('ytd-video-description-transcript-section-renderer');"
        " if (!root) return JSON.stringify({roots:0, clicked:false});"
        " root.scrollIntoView({block:'center'});"
        " const button = root.querySelector('button, tp-yt-paper-button, yt-button-shape button');"
        " if (!button) return JSON.stringify({roots:1, clicked:false});"
        " for (const type of ['pointerdown','mousedown','pointerup','mouseup','click'])"
        " button.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true, view:window}));"
        " return JSON.stringify({roots:1, clicked:true, text:(button.innerText || button.textContent || '').trim()}); })()"
    )


def _failed_attempt(reason: str, *, video_id: str, session: str, error: str, output_chars: int) -> AcquisitionAttempt:
    return _ui_attempt(
        status="error",
        error=error,
        output_chars=output_chars,
        details={"reason": reason, "video_id": video_id, "session": session, "diagnostic": True},
    )


def run_browser_ui_transcript_stage(
    url: str,
    *,
    session: str,
    run_command: Callable[[Sequence[str]], tuple[str, str | None]],
) -> AcquisitionAttempt:
    video_id = parse_video_id(url)
    if video_id is None:
        return _ui_attempt(status="error", details={"reason": "missing-video-id"})
    if shutil.which("agent-browser") is None:
        return _ui_attempt(
            status="error",
            error="missing-tool:agent-browser",
            details={"reason": "missing-tool", "video_id": video_id, "source_type": "youtube-ui-transcript"},
        )
    output_chars = 0
    for command in (
        ["agent-browser", "--session", session, "open", url],
        ["agent-browser", "--session", session, "wait", "2500"],
        ["agent-browser", "--session", session, "eval", _open_transcript_script()],
        ["agent-browser", "--session", session, "wait", "2500"],
    ):
        stdout, error = run_command(command)
        output_chars += len(stdout)
        if error:
            return _failed_attempt("browser-command-failed", video_id=video_id, session=session, error=error, output_chars=output_chars)
    body, body_error = run_command(["agent-browser", "--session", session, "get", "text", "body"])
    output_chars += len(body)
    if body_error:
        return _failed_attempt("body-read-failed", video_id=video_id, session=session, error=body_error, output_chars=output_chars)
    snapshot, snapshot_error = run_command(["agent-browser", "--session", session, "snapshot", "-i", "-d", "6"])
    output_chars += len(snapshot)
    if snapshot_error:
        return _failed_attempt(
            "snapshot-failed", video_id=video_id, session=session, error=snapshot_error, output_chars=output_chars
        )
    transcript_lines = extract_transcript_lines_from_snapshot(snapshot)
    metadata = _metadata_from_player_response(body, url)
    has_player_metadata = any(key != "webpage_url" for key in metadata)
    metadata.setdefault("video_id", video_id)
    details: dict[str, object] = {
        "reason": "youtube-transcript-ui",
        "video_id": video_id,
        "session": session,
        "source_type": "youtube-transcript-browser-ui",
        "metadata": metadata,
        "transcript_segment_count": len(transcript_lines),
        "selector": "ytd-video-description-transcript-section-renderer",
    }
    if transcript_lines:
        return _ui_attempt(
            status="success",
            confidence="strong",
            details=details,
            output_chars=output_chars,
            content_text=_format_ui_transcript(metadata, transcript_lines),
        )
    details["source_type"] = "youtube-metadata-only" if has_player_metadata else "youtube-ui-transcript"
    details["reason"] = "transcript-segments-unavailable"
    details["diagnostic"] = True
    if has_player_metadata:
        return _ui_attempt(status="diagnostic", confidence="weak", details=details, output_chars=output_chars)
    return _ui_attempt(status="diagnostic", error="transcript-segments-unavailable", details=details, output_chars=output_chars)
