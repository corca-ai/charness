#!/usr/bin/env python3

from __future__ import annotations

import argparse
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
    safe = "".join(ch if ch.isalnum() else "-" for ch in host).strip("-")
    return safe or "public-url"


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


def _render_record(url: str, acquisition: dict[str, object]) -> str:
    route = acquisition.get("route") if isinstance(acquisition.get("route"), dict) else {}
    selected = acquisition.get("selected_attempt") if isinstance(acquisition.get("selected_attempt"), dict) else {}
    access_modes = route.get("access_modes") if isinstance(route.get("access_modes"), list) else []
    attempts = acquisition.get("attempts") if isinstance(acquisition.get("attempts"), list) else []
    open_gaps = [
        item
        for item in attempts
        if isinstance(item, dict)
        and (item.get("status") in {"skipped", "error"} or item.get("stage_id") == "agent-browser-network-recon")
    ]
    gap_lines = _attempt_lines(open_gaps) or ["- None recorded."]
    attempt_lines = _attempt_lines(attempts) or ["- None recorded."]
    return "\n".join(
        [
            "# Gathered Public URL",
            "",
            f"- Source: {url}",
            "- Access Mode: support/web-fetch public route",
            f"- Route: `{route.get('route_id', 'unknown')}`",
            f"- Route Family: `{route.get('route_family', 'unknown')}`",
            f"- Route Access Modes: {', '.join(str(mode) for mode in access_modes) or 'unknown'}",
            f"- Disposition: `{acquisition.get('disposition', 'unknown')}`",
            f"- Final Status: `{acquisition.get('final_status', 'unknown')}`",
            f"- Final Confidence: `{acquisition.get('final_confidence', 'none')}`",
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
            "",
            "## Trace JSON",
            "",
            "```json",
            json.dumps(acquisition, ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Gather an arbitrary public URL through support/web-fetch.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--slug", default=None)
    parser.add_argument("--date", default=None)
    parser.add_argument("--intent", choices=("single", "collect"), default="single")
    parser.add_argument("--browser-mode", choices=("auto", "off", "always"), default="auto")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--direct-response-file", type=Path)
    parser.add_argument("--expect-text", action="append", default=[])
    parser.add_argument("--expect-regex", action="append", default=[])
    parser.add_argument("--expect-json-field", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

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
    for expected in args.expect_text:
        acquire_cmd.extend(["--expect-text", expected])
    for pattern in args.expect_regex:
        acquire_cmd.extend(["--expect-regex", pattern])
    for field_path in args.expect_json_field:
        acquire_cmd.extend(["--expect-json-field", field_path])

    acquisition = _run_json(acquire_cmd)
    record = _render_record(args.url, acquisition)
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
        "source_url": args.url,
        "acquisition": acquisition,
        "write_record": write_payload,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
