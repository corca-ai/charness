from __future__ import annotations

import io
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import yaml

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]


def run_helper(
    script: str,
    *args: str,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    module = load_script_module(
        f"web_fetch_support_{Path(script).stem}", ROOT / script
    )
    previous_cwd = Path.cwd()
    try:
        os.chdir(ROOT)
        stdin = patch("sys.stdin", io.StringIO(input_text)) if input_text is not None else patch.object(sys, "stdin", sys.stdin)
        with stdin:
            result = run_loaded_script_main(script, module, *args, env=env)
    finally:
        os.chdir(previous_cwd)
    return subprocess.CompletedProcess(
        [script, *args], result.returncode, result.stdout, result.stderr
    )


def test_acquire_public_url_rejects_non_http_scheme(tmp_path: Path) -> None:
    local_file = tmp_path / "secret.txt"
    local_file.write_text("not public", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        local_file.as_uri(),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "error"
    assert payload["route"]["route_id"] == "invalid-url-scheme"
    assert [attempt["stage_id"] for attempt in payload["attempts"]] == ["input-validation"]


def test_acquire_public_url_invalid_regex_never_succeeds(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--expect-regex",
        "[",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "error"
    assert payload["selected_attempt"]["status"] == "invalid-proof"


def test_acquire_public_url_invalid_regex_outranks_transport_error() -> None:
    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "http://127.0.0.1:9/nope",
        "--expect-regex",
        "[",
        "--browser-mode",
        "off",
        "--timeout",
        "1",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "error"
    assert payload["selected_attempt"]["status"] == "invalid-proof"
    assert payload["selected_attempt"]["classification"]["proof_errors"] == [
        {"type": "invalid-regex", "value": "["}
    ]


def test_acquire_public_url_uses_defuddle_after_weak_direct_fetch(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "defuddle").write_text(
        "#!/bin/sh\nif [ \"$1\" = parse ] && [ \"$3\" = --markdown ]; then printf 'clean markdown with target proof\\n'; else exit 64; fi\n",
        encoding="utf-8",
    )
    (bin_dir / "defuddle").chmod(0o755)
    direct = tmp_path / "direct.html"
    direct.write_text("<html><head><meta property=\"og:title\" content=\"Example\"></head></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--expect-text",
        "target proof",
        "--browser-mode",
        "off",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "success"
    stage_ids = [attempt["stage_id"] for attempt in payload["attempts"]]
    assert stage_ids[:3] == ["direct-public-fetch", "impersonated-public-fetch", "defuddle-reader-extraction"]
    assert payload["attempts"][1]["details"]["reason"] == "seeded-direct-fixture"
    defuddle_attempt = next(
        attempt for attempt in payload["attempts"] if attempt["stage_id"] == "defuddle-reader-extraction"
    )
    assert defuddle_attempt["confidence"] == "strong"
    assert payload["selected_attempt"]["stage_id"] == "defuddle-reader-extraction"
    assert payload["final_status"] == "success"


def test_acquire_public_url_uses_agent_browser_network_recon_for_collect_intent(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    call_log = tmp_path / "agent-browser.log"
    (bin_dir / "agent-browser").write_text(
        f"""#!/bin/sh
printf '%s\\n' "$*" >> {str(call_log)!r}
case "$*" in
  *"get text body"*) printf 'rendered target proof from browser\\n' ;;
  *"network requests"*) printf 'GET https://example.com/api/items\\n' ;;
  *) exit 0 ;;
esac
""",
        encoding="utf-8",
    )
    (bin_dir / "agent-browser").chmod(0o755)
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body><div id=\"root\"></div></body></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/app",
        "--repo-root",
        str(tmp_path),
        "--direct-response-file",
        str(direct),
        "--expect-text",
        "target proof",
        "--intent",
        "collect",
        "--browser-mode",
        "auto",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "success"
    render_index = next(
        index for index, attempt in enumerate(payload["attempts"]) if attempt["stage_id"] == "agent-browser-render-recon"
    )
    network_attempt = next(
        attempt for attempt in payload["attempts"] if attempt["stage_id"] == "agent-browser-network-recon"
    )
    assert payload["attempts"][render_index + 1]["stage_id"] == "agent-browser-network-recon"
    assert network_attempt["status"] == "diagnostic"
    assert network_attempt["details"]["network_candidates"] == [
        "GET https://example.com/api/items"
    ]
    assert "close" in call_log.read_text(encoding="utf-8")
    assert payload["selected_attempt"]["stage_id"] == "agent-browser-render-recon"
    assert payload["final_status"] == "success"


def test_acquire_public_url_records_missing_fallback_tools(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><head><meta property=\"og:title\" content=\"Example\"></head></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = str(tmp_path / "empty-bin")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "auto",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    skipped = {
        attempt["stage_id"]: attempt["details"]["reason"]
        for attempt in payload["attempts"]
        if attempt["status"] == "skipped"
    }
    assert skipped["defuddle-reader-extraction"] == "missing-tool"
    assert skipped["agent-browser-render-recon"] == "missing-tool"


def test_acquire_public_url_records_all_planned_stages_as_attempts(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    planned = [stage["stage_id"] for stage in payload["route"]["acquisition_plan"]]
    attempted = [attempt["stage_id"] for attempt in payload["attempts"]]
    assert planned == attempted
    assert payload["attempts"][-1]["stage_id"] == "clean-stop"
    assert payload["attempts"][-1]["details"]["reason"] == "prior-stage-sufficient"


def test_acquire_public_url_network_recon_alone_is_not_success(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "agent-browser").write_text(
        """#!/bin/sh
case "$*" in
  *"get text body"*) printf 'short rendered shell\\n' ;;
  *"network requests"*) printf 'GET https://example.com/api/items\\n' ;;
  *) exit 0 ;;
esac
""",
        encoding="utf-8",
    )
    (bin_dir / "agent-browser").chmod(0o755)
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body><div id=\"root\"></div></body></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/app",
        "--repo-root",
        str(tmp_path),
        "--direct-response-file",
        str(direct),
        "--intent",
        "collect",
        "--browser-mode",
        "auto",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "degraded"
    network_attempt = next(
        attempt for attempt in payload["attempts"] if attempt["stage_id"] == "agent-browser-network-recon"
    )
    assert network_attempt["status"] == "diagnostic"
    assert payload["selected_attempt"]["stage_id"] == "agent-browser-render-recon"


def test_acquire_public_url_blocker_with_proof_is_blocked(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body><h1>Sign in</h1><p>needle</p></body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/private",
        "--direct-response-file",
        str(direct),
        "--expect-text",
        "needle",
        "--browser-mode",
        "off",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "blocked"
    assert payload["selected_attempt"]["status"] == "login-wall"
    assert payload["selected_attempt"]["classification"]["proof"] == [{"type": "text", "value": "needle"}]


def test_gather_public_url_writes_web_fetch_trace(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--slug",
        "example-public-url",
        "--date",
        "2026-05-16",
        "--execute",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "updated"
    assert payload["record_status"] == "updated"
    assert payload["acquisition_disposition"] == "success"
    assert payload["final_status"] == "success"
    assert payload["content_persistence"] == "none"
    record_path = Path(payload["write_record"]["record_artifact_path"])
    record = record_path.read_text(encoding="utf-8")
    assert "# Gathered Public URL" in record
    assert "- Content Persistence: `none`" in record
    assert "## Acquisition Trace" in record
    assert "## Open Gaps\n\n- None recorded." in record
    assert "`direct-public-fetch`" in record
    assert '"selected_attempt"' in record
    assert (tmp_path / "charness-artifacts" / "gather" / "latest.md").is_file()


def test_gather_public_url_persists_extracted_content_when_requested(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text(
        "<html><body><h1>Readable Title</h1>" + ("useful content " * 120) + "</body></html>",
        encoding="utf-8",
    )

    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--slug",
        "example-public-url",
        "--date",
        "2026-05-16",
        "--persist-extracted-content",
        "--max-extracted-content-chars",
        "120",
        "--execute",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["content_persistence"] == "extracted"
    assert "selected_content" not in payload["acquisition"]
    record = Path(payload["write_record"]["record_artifact_path"]).read_text(encoding="utf-8")
    assert "- Content Persistence: `extracted`" in record
    assert "## Extracted Content" in record
    assert "Readable Title" in record
    assert "<html>" not in record
    trace_json = record.split("## Trace JSON", 1)[1]
    assert "selected_content" not in trace_json


def test_gather_public_url_persists_design_intent_and_blocks_real_login(tmp_path: Path) -> None:
    readable = tmp_path / "readable.html"
    readable.write_text(
        "<html><head><title>Design in the AI era</title></head><body>"
        "<p>design intent</p>" + ("useful content " * 120) + "</body></html>",
        encoding="utf-8",
    )
    readable_result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/design",
        "--direct-response-file",
        str(readable),
        "--browser-mode",
        "off",
        "--slug",
        "design-intent",
        "--date",
        "2026-05-16",
        "--persist-extracted-content",
        "--max-extracted-content-chars",
        "240",
        "--execute",
    )
    assert readable_result.returncode == 0, readable_result.stderr
    readable_payload = yaml.safe_load(readable_result.stdout)
    assert readable_payload["final_status"] == "success"
    assert readable_payload["content_persistence"] == "extracted"
    readable_record = Path(readable_payload["write_record"]["record_artifact_path"]).read_text(encoding="utf-8")
    assert "design intent" in readable_record
    assert "Design in the AI era" in readable_record

    blocked_root = tmp_path / "blocked"
    login = blocked_root / "login.html"
    login.parent.mkdir(parents=True)
    login.write_text(
        "<html><body><h1>Sign <span>in</span></h1>" + ("useful content " * 120) + "</body></html>",
        encoding="utf-8",
    )
    blocked_result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(blocked_root),
        "--url",
        "https://example.com/private",
        "--direct-response-file",
        str(login),
        "--browser-mode",
        "off",
        "--date",
        "2026-05-16",
        "--persist-extracted-content",
        "--execute",
    )
    assert blocked_result.returncode == 1
    blocked_payload = yaml.safe_load(blocked_result.stdout)
    assert blocked_payload["status"] == "blocked"
    assert blocked_payload["reason"] == "acquisition-blocked"
    assert blocked_payload["acquisition_disposition"] == "blocked"
    assert blocked_payload["final_status"] == "login-wall"
    assert blocked_payload["write_record"] is None
    assert not (blocked_root / "charness-artifacts" / "gather" / "latest.md").exists()


def test_gather_public_url_does_not_write_error_acquisition(tmp_path: Path) -> None:
    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "file:///tmp/secret",
        "--date",
        "2026-05-16",
        "--execute",
    )
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason"] == "acquisition-error"
    assert payload["acquisition"]["disposition"] == "error"
    assert payload["write_record"] is None
    assert not (tmp_path / "charness-artifacts" / "gather" / "latest.md").exists()


def test_gather_public_url_does_not_write_invalid_regex_acquisition(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--expect-regex",
        "[",
        "--date",
        "2026-05-16",
        "--execute",
    )
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason"] == "acquisition-error"
    assert payload["acquisition_disposition"] == "error"
    assert payload["acquisition"]["final_status"] == "invalid-proof"
    assert not (tmp_path / "charness-artifacts" / "gather" / "latest.md").exists()


def test_gather_public_url_does_not_write_degraded_acquisition(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>short shell</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/app",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--date",
        "2026-05-16",
        "--execute",
    )
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "degraded"
    assert payload["reason"] == "acquisition-degraded"
    assert payload["acquisition_disposition"] == "degraded"
    assert payload["write_record"] is None
    assert not (tmp_path / "charness-artifacts" / "gather" / "latest.md").exists()


def test_gather_public_url_default_slug_distinguishes_same_host_urls(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    first = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/a",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--date",
        "2026-05-16",
        "--execute",
    )
    second = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/b",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--date",
        "2026-05-16",
        "--execute",
    )
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    first_payload = yaml.safe_load(first.stdout)
    second_payload = yaml.safe_load(second.stdout)
    first_record = Path(first_payload["write_record"]["record_artifact_path"])
    second_record = Path(second_payload["write_record"]["record_artifact_path"])
    assert first_record.name.startswith("2026-05-16-example-com-a-")
    assert second_record.name.startswith("2026-05-16-example-com-b-")
    assert first_record != second_record
    assert first_record.is_file()
    assert second_record.is_file()


def test_gather_public_url_normalizes_encoded_uppercase_default_slug(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://wiki.g15e.com/pages/AOP%20and%20CSS.md",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--date",
        "2026-05-16",
        "--execute",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "updated"
    assert payload["record_status"] == "updated"
    record_path = Path(payload["write_record"]["record_artifact_path"])
    assert record_path.name == "2026-05-16-wiki-g15e-com-pages-aop-and-css-md-e0a17463.md"
    assert record_path.is_file()
    assert "# Gathered Public URL" in record_path.read_text(encoding="utf-8")


def test_gather_public_url_reduces_encoded_non_ascii_default_slug_to_ascii(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/public/gather/scripts/gather_public_url.py",
        "--repo-root",
        str(tmp_path),
        "--url",
        "https://example.com/pages/%E3%83%86%E3%82%B9%E3%83%88.md",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--date",
        "2026-05-16",
        "--execute",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    record_path = Path(payload["write_record"]["record_artifact_path"])
    assert record_path.name == "2026-05-16-example-com-pages-md-d38ce516.md"
    assert record_path.is_file()
    assert "# Gathered Public URL" in record_path.read_text(encoding="utf-8")


def test_acquire_public_url_accepts_weak_direct_success_without_positive_proof(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "success"
    assert payload["attempts"][0]["stage_id"] == "direct-public-fetch"
    assert payload["attempts"][0]["status"] == "success"
    assert payload["attempts"][0]["confidence"] == "weak"
    assert payload["attempts"][0]["output_chars"] == len(direct.read_text(encoding="utf-8"))
    assert payload["selected_attempt"]["stage_id"] == "direct-public-fetch"
    assert payload["attempts"][-1]["stage_id"] == "clean-stop"


def test_acquire_public_url_omits_selected_content_by_default(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body>" + ("useful content " * 120) + "</body></html>", encoding="utf-8")

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "success"
    assert "selected_content" not in payload


def test_acquire_public_url_can_include_extracted_selected_content(tmp_path: Path) -> None:
    direct = tmp_path / "direct.html"
    direct.write_text(
        "<html><body><h1>Readable Title</h1>" + ("useful content " * 120) + "</body></html>",
        encoding="utf-8",
    )

    result = run_helper(
        "skills/support/web-fetch/scripts/acquire_public_url.py",
        "--url",
        "https://example.com/article",
        "--direct-response-file",
        str(direct),
        "--browser-mode",
        "off",
        "--include-selected-content",
        "--selected-content-max-chars",
        "80",
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    selected_content = payload["selected_content"]
    assert selected_content["stage_id"] == "direct-public-fetch"
    assert selected_content["format"] == "text"
    assert selected_content["truncated"] is True
    assert "Readable Title" in selected_content["text"]
    assert "<html>" not in selected_content["text"]
