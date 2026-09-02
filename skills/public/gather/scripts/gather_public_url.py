#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import runpy
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

try:
    import yaml
except ModuleNotFoundError as exc:
    # This command is a DOCUMENTED consumer entrypoint (`SKILL.md` tells a
    # consumer to run it), so it is the first place a missing dependency is met
    # on a fresh machine -- which is exactly how this was reported: a bare
    # `ModuleNotFoundError: No module named 'yaml'`, a search for a declaration,
    # and the conclusion that there was none. There is one, and it is pinned; the
    # export now ships it, and this message names it rather than leaving the
    # reader to search.
    # Found by ANCHOR, not by a fixed `parents[N]`. A counted hop is correct in
    # exactly one layout: this file sits at `skills/public/gather/scripts/` in the
    # dev tree and `skills/gather/scripts/` once exported, so `parents[3]` names
    # `<repo>/skills` here and `<plugin>` there -- and the message would have
    # printed two paths that do not exist, which is the same stranding this guard
    # exists to end. Walking for the contract works in both.
    _ANCHOR = Path("packaging") / "bootstrap-requirements.txt"
    _HERE = Path(__file__).resolve()
    _PLUGIN_ROOT = next(
        (parent for parent in _HERE.parents if (parent / _ANCHOR).is_file()),
        _HERE.parents[3],
    )
    _REQUIREMENTS = _PLUGIN_ROOT / _ANCHOR
    # The FIRST remedy is the one that makes the next `python3 ...` invocation
    # work. A round-2 reviewer measured why the ordering matters: the bootstrap
    # runtime installs into its own launcher, so a consumer who follows it and
    # then re-runs the documented `python3 "$SKILL_DIR/scripts/gather_public_url.py"`
    # meets this same message again. Naming the pinned spec keeps the version
    # constraint available either way.
    raise SystemExit(
        "gather cannot start: PyYAML is missing from the interpreter running this "
        f"script (import of `{exc.name}` failed).\n"
        f"  Install it into THIS interpreter: {sys.executable} -m pip install "
        f"-r {_REQUIREMENTS}\n"
        f"  The pinned versions are declared in {_REQUIREMENTS}.\n"
        "  A repo-local runtime is also available via "
        f"{_PLUGIN_ROOT / 'scripts' / 'core' / 'bootstrap_runtime.py'} --repo-root {_PLUGIN_ROOT}, "
        "but it installs into its own launcher rather than into this interpreter, so "
        "re-running the documented command afterwards needs that launcher."
    ) from exc

SCRIPT_DIR = Path(__file__).resolve().parent
SUPPORT_ACQUIRE = (
    SCRIPT_DIR.parents[2] / "support" / "web-fetch" / "scripts" / "acquire_public_url.py"
)
SUPPORT_ROUTE = (
    SCRIPT_DIR.parents[2] / "support" / "web-fetch" / "scripts" / "route_public_fetch.py"
)
WRITE_RECORD = SCRIPT_DIR / "write_record.py"


def emit_yaml(payload: object) -> None:
    """Render this command's stdout through the repo's one YAML emitter.

    Reached via the support router's own `load_yaml_output` rather than
    `skill_runtime_bootstrap`: a minimal exported layout is only required to ship
    `scripts/yaml_output.py` beside the bundled guard (see
    `test_gather_reaches_acquire_and_bundled_guard_in_exported_layout`), and a seam
    that needs a root file that layout does not carry turns this command's stdout
    into an ImportError. `load_yaml_output`'s BOUNDED ancestor walk already resolves
    the helper at the repo root here and at the plugin root once exported, so this
    reuses it instead of adding a fourth private copy of the same walk.
    """
    runpy.run_path(str(SUPPORT_ROUTE))["load_yaml_output"]().emit_yaml(payload)


if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import gather_record_rendering  # noqa: E402

try:
    from scripts.core import subprocess_guard as _subprocess_guard
except ModuleNotFoundError:
    _scripts_dir = next(
        (
            ancestor / "scripts"
            for ancestor in (Path(__file__).resolve(), *Path(__file__).resolve().parents)
            if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
        ),
        None,
    )
    if _scripts_dir is None:
        _subprocess_guard = None
    else:
        sys.path.insert(0, str(_scripts_dir.parent))
        import scripts.core.subprocess_guard as _subprocess_guard  # noqa: E402

run_process = _subprocess_guard.run_process if _subprocess_guard is not None else None
import gather_public_execution as _execution  # noqa: E402

_content_persistence = gather_record_rendering.content_persistence
_render_record = gather_record_rendering.render_record
_trace_payload = gather_record_rendering.trace_payload


def _run_json(command: list[str], *, input_text: str | None = None) -> dict[str, object]:
    return _execution.run_json(
        command,
        input_text=input_text,
        yaml_module=yaml,
        support_acquire=SUPPORT_ACQUIRE,
        write_record=WRITE_RECORD,
        run_process=run_process,
    )


def _slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.netloc or "public-url").lower().replace("www.", "", 1)
    path = "/".join(part for part in unquote(parsed.path).split("/") if part).lower()
    identity = "-".join(part for part in (host, path) if part)
    safe = "".join(ch if ch.isascii() and ch.isalnum() else "-" for ch in identity).strip("-")
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
    return (
        isinstance(route, dict)
        and route.get("route_id") == "yt-dlp-metadata"
        and str(acquisition.get("source_identity", "")).startswith("youtube-")
    )


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
        if (
            isinstance(details, dict)
            and details.get("endpoint")
            and details.get("requested_status_id")
        ):
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
    parser = argparse.ArgumentParser(
        description="Gather an arbitrary public URL through support/web-fetch."
    )
    parser.add_argument("--url", required=True, help="Public URL to gather")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root where the gathered URL record should be written",
    )
    parser.add_argument(
        "--slug",
        default=None,
        help="Slug for the dated record (auto-derived from URL when omitted)",
    )
    parser.add_argument(
        "--date", default=None, help="Record date in YYYY-MM-DD (defaults to today UTC)"
    )
    parser.add_argument(
        "--intent",
        choices=("single", "collect"),
        default="single",
        help="single = one durable record; collect = bulk crawl session",
    )
    parser.add_argument(
        "--browser-mode",
        choices=("auto", "off", "always"),
        default="auto",
        help="When to use a browser fallback",
    )
    parser.add_argument("--timeout", type=int, default=20, help="Per-stage timeout in seconds")
    parser.add_argument(
        "--direct-response-file",
        type=Path,
        help="Pre-captured direct response file to seed the acquisition",
    )
    parser.add_argument(
        "--domain-route-response-file",
        type=Path,
        help="JSON map seeding the domain-specific route; missing seeded endpoints do not fetch live unless --live-domain-route is set",
    )
    parser.add_argument(
        "--live-domain-route",
        action="store_true",
        help="Allow live fetch for seeded-missing exact-source/domain-specific endpoints when the route supports it",
    )
    parser.add_argument(
        "--expect-text",
        action="append",
        default=[],
        help="Required substring in the response (repeatable)",
    )
    parser.add_argument(
        "--expect-regex",
        action="append",
        default=[],
        help="Required regex pattern in the response (repeatable)",
    )
    parser.add_argument(
        "--expect-json-field",
        action="append",
        default=[],
        help="Required JSON field path in the response (repeatable)",
    )
    parser.add_argument(
        "--persist-extracted-content",
        action="store_true",
        help="Persist extracted page content in the record",
    )
    parser.add_argument(
        "--max-extracted-content-chars",
        type=_positive_int,
        default=200_000,
        help="Maximum chars of extracted content to persist",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Write the record (otherwise dry-run)"
    )
    args = parser.parse_args()

    acquisition = _run_json(_build_acquire_cmd(args))
    acquisition_disposition = str(acquisition.get("disposition", "unknown"))
    final_status = str(acquisition.get("final_status", "unknown"))
    final_confidence = str(acquisition.get("final_confidence", "none"))
    content_persistence = _content_persistence(
        acquisition, requested=args.persist_extracted_content
    )
    should_write_partial = _is_youtube_acquisition(acquisition) and acquisition_disposition in {
        "blocked",
        "degraded",
    }
    should_write_terminal = _is_exact_source_terminal_record(acquisition)
    if (
        acquisition_disposition != "success"
        and not should_write_partial
        and not should_write_terminal
    ):
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
        emit_yaml(payload)
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
    emit_yaml(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
