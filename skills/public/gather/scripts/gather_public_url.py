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

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import gather_record_rendering  # noqa: E402

_content_persistence = gather_record_rendering.content_persistence
_render_record = gather_record_rendering.render_record
_trace_payload = gather_record_rendering.trace_payload


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


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


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


def _is_exact_source_terminal_record(acquisition: dict[str, object]) -> bool:
    route = acquisition.get("route")
    if not isinstance(route, dict) or route.get("route_id") != "twitter-syndication":
        return False
    if acquisition.get("source_identity") not in {"exact-blocked", "exact-unavailable"}:
        return False
    attempts = acquisition.get("attempts")
    if not isinstance(attempts, list):
        return False
    for attempt in attempts:
        if not isinstance(attempt, dict) or attempt.get("stage_id") != "domain-specific-route":
            continue
        details = attempt.get("details")
        if isinstance(details, dict) and details.get("endpoint") and details.get("requested_status_id"):
            return True
    return False


def _acquisition_summary(
    args: argparse.Namespace,
    acquisition: dict[str, object],
    *,
    acquisition_disposition: str,
    final_status: str,
    final_confidence: str,
    content_persistence: str,
) -> dict[str, object]:
    return {
        "source_url": args.url,
        "acquisition_disposition": acquisition_disposition,
        "final_status": final_status,
        "final_confidence": final_confidence,
        "source_identity": acquisition.get("source_identity", "not-applicable"),
        "source_resolution": acquisition.get("source_resolution"),
        "content_persistence": content_persistence,
    }


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
    parser.add_argument("--domain-route-response-file", type=Path, help="JSON map seeding the domain-specific route; missing seeded endpoints do not fetch live unless --live-domain-route is set")
    parser.add_argument("--live-domain-route", action="store_true", help="Allow live fetch for seeded-missing exact-source/domain-specific endpoints when the route supports it")
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
    should_write_terminal = _is_exact_source_terminal_record(acquisition)
    if acquisition_disposition != "success" and not should_write_partial and not should_write_terminal:
        payload = {
            "status": "degraded" if acquisition_disposition == "degraded" else "blocked",
            "reason": f"acquisition-{acquisition_disposition}",
            **_acquisition_summary(
                args,
                acquisition,
                acquisition_disposition=acquisition_disposition,
                final_status=final_status,
                final_confidence=final_confidence,
                content_persistence="none",
            ),
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
        **_acquisition_summary(
            args,
            acquisition,
            acquisition_disposition=acquisition_disposition,
            final_status=final_status,
            final_confidence=final_confidence,
            content_persistence=content_persistence,
        ),
        "acquisition": _trace_payload(acquisition),
        "write_record": write_payload,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
