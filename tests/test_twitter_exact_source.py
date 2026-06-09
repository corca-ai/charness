"""Slice 2 / #338: gather X-Twitter exact-source fallback, source-identity proof,
visible failed-attempt trace, and honest no-substitution stop.

Direct unit tests of the identity-keyed exact-source logic plus subprocess
integration of the acquire/gather CLIs with SEEDED responses (no live X fetch)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBFETCH = ROOT / "skills" / "support" / "web-fetch" / "scripts"
if str(WEBFETCH) not in sys.path:
    sys.path.insert(0, str(WEBFETCH))

import twitter_exact_source as tes  # noqa: E402

SID = "1799999999999999999"
STATUS_URL = f"https://x.com/acme/status/{SID}"
SYND_URL = f"https://cdn.syndication.twimg.com/tweet-result?id={SID}&lang=en"


def _fetcher(by_kind: dict) -> "tes.Fetcher":
    def fetch(endpoint):
        entry = by_kind.get(endpoint["kind"], {})
        return entry.get("text"), entry.get("error")

    return fetch


# --- parse_status_url ---


def test_parse_status_url_accepts_x_and_twitter_and_mobile() -> None:
    assert tes.parse_status_url(STATUS_URL) == {"handle": "acme", "status_id": SID}
    assert tes.parse_status_url(f"https://twitter.com/acme/status/{SID}")["status_id"] == SID
    assert tes.parse_status_url(f"https://www.x.com/acme/status/{SID}")["handle"] == "acme"
    assert tes.parse_status_url(f"https://mobile.twitter.com/acme/statuses/{SID}")["status_id"] == SID


def test_parse_status_url_rejects_non_status_and_non_x() -> None:
    assert tes.parse_status_url("https://x.com/acme") is None  # profile, not a status
    assert tes.parse_status_url("https://example.com/acme/status/1") is None


# --- returned_status_id ---


def test_returned_status_id_syndication_and_oembed_and_fallback() -> None:
    assert tes.returned_status_id("syndication", json.dumps({"id_str": SID})) == SID
    assert tes.returned_status_id("syndication", json.dumps({"id": int(SID)})) == SID
    # oEmbed needs a rendered body (html/author_name) to prove existence, not just a URL echo
    assert tes.returned_status_id("oembed", json.dumps({"url": STATUS_URL, "html": "<blockquote>post</blockquote>"})) == SID
    assert tes.returned_status_id("oembed", json.dumps({"author_name": "Acme", "author_url": STATUS_URL})) == SID
    assert tes.returned_status_id("syndication", f"raw text .../status/{SID} here") == SID
    assert tes.returned_status_id("syndication", "no identity at all") is None
    assert tes.returned_status_id("oembed", json.dumps(["not", "a", "dict"])) is None


def test_returned_status_id_oembed_url_echo_without_body_is_rejected() -> None:
    # A bare 200 echo (no html/author body) for a deleted/nonexistent post must NOT
    # verify as existence, and the raw-text fallback must not reintroduce the id.
    assert tes.returned_status_id("oembed", json.dumps({"url": STATUS_URL})) is None


# --- run_exact_source_stage ---


def test_stage_exact_match_first_endpoint_stops_with_proof() -> None:
    attempts = tes.run_exact_source_stage(STATUS_URL, fetcher=_fetcher({"syndication": {"text": json.dumps({"id_str": SID})}}))
    assert len(attempts) == 1  # stops at the exact match; oembed not needed
    assert attempts[0].status == "success"
    assert attempts[0].details["identity_proof"]["matched"] is True
    assert attempts[0].details["outcome"] == "exact-fetched"


def test_stage_falls_through_block_to_oembed_match() -> None:
    attempts = tes.run_exact_source_stage(
        STATUS_URL,
        fetcher=_fetcher({
            "syndication": {"text": "captcha: verify you are human"},
            "oembed": {"text": json.dumps({"html": f'<a href="{STATUS_URL}">t</a>'})},
        }),
    )
    assert [a.status for a in attempts] == ["captcha", "success"]
    assert attempts[1].details["identity_proof"]["verified_via"] == "oembed"


def test_stage_all_blocked_yields_no_success_and_keeps_failures_visible() -> None:
    attempts = tes.run_exact_source_stage(
        STATUS_URL,
        fetcher=_fetcher({
            "syndication": {"text": "captcha verify you are human"},
            "oembed": {"text": "", "error": "HTTPError:403"},
        }),
    )
    assert [a.status for a in attempts] == ["captcha", "error"]
    assert not any(a.status == "success" for a in attempts)
    assert attempts[1].details["reason"] == "fetch-failed"


def test_stage_identity_mismatch_is_invalid_proof_not_substituted() -> None:
    attempts = tes.run_exact_source_stage(
        STATUS_URL,
        fetcher=_fetcher({
            "syndication": {"text": json.dumps({"id_str": "1700000000000000001"})},
            "oembed": {"text": json.dumps({"url": "https://x.com/acme/status/1700000000000000001", "html": "<blockquote>different post</blockquote>"})},
        }),
    )
    assert all(a.status == "invalid-proof" for a in attempts)
    assert attempts[0].details["identity_proof"]["matched"] is False
    assert attempts[0].details["outcome"] == "identity-rejected"


def test_stage_oembed_url_echo_without_body_not_accepted() -> None:
    # Deleted post: syndication blocked, oEmbed returns a 200 URL echo with no
    # rendered body -> must NOT be accepted as the exact post.
    attempts = tes.run_exact_source_stage(
        STATUS_URL,
        fetcher=_fetcher({
            "syndication": {"text": "captcha verify you are human"},
            "oembed": {"text": json.dumps({"url": STATUS_URL})},
        }),
    )
    assert not any(a.status == "success" for a in attempts)
    assert attempts[1].details["reason"] == "no-identity"


def test_stage_no_identity_in_response_is_error() -> None:
    attempts = tes.run_exact_source_stage(STATUS_URL, fetcher=_fetcher({"syndication": {"text": "a fairly long body but no status id anywhere in it"}, "oembed": {"text": "still nothing here"}}))
    assert [a.status for a in attempts] == ["error", "error"]
    assert attempts[0].details["reason"] == "no-identity"


def test_stage_non_status_url_skips_honestly() -> None:
    attempts = tes.run_exact_source_stage("https://x.com/acme", fetcher=_fetcher({}))
    assert len(attempts) == 1
    assert attempts[0].status == "skipped"
    assert attempts[0].details["reason"] == "no-status-id"


# --- classify_source_identity ---


def _acq(attempts: list[dict], route_id: str = "twitter-syndication") -> dict:
    return {"route": {"route_id": route_id}, "attempts": attempts}


def test_classify_source_identity_all_outcomes() -> None:
    exact = [{"stage_id": "domain-specific-route", "status": "success", "details": {"endpoint": SYND_URL, "outcome": "exact-fetched"}}]
    blocked = [{"stage_id": "domain-specific-route", "status": "captcha", "details": {"endpoint": SYND_URL, "reason": "blocked"}}]
    unavailable = [{"stage_id": "domain-specific-route", "status": "error", "error": "live-fetch-not-enabled", "details": {"endpoint": SYND_URL, "reason": "fetch-failed"}}]
    skip_only = [{"stage_id": "domain-specific-route", "status": "skipped", "tool_id": None, "details": {"reason": "no-status-id"}}]
    assert tes.classify_source_identity(_acq(exact)) == "exact-fetched"
    assert tes.classify_source_identity(_acq(blocked)) == "exact-blocked"
    assert tes.classify_source_identity(_acq(unavailable)) == "exact-unavailable"
    assert tes.classify_source_identity(_acq(skip_only)) == "exact-unavailable"  # no-status-id stub
    assert tes.classify_source_identity(_acq(blocked, route_id="reddit-json")) == "not-applicable"
    assert tes.classify_source_identity({"route": "nope", "attempts": []}) == "not-applicable"


# --- make_fetcher ---


def test_make_fetcher_seed_then_live_then_not_enabled() -> None:
    endpoint = {"kind": "syndication", "url": SYND_URL, "tool_id": "twitter-syndication"}
    seeded = tes.make_fetcher({SYND_URL: {"text": "seeded"}})
    assert seeded(endpoint) == ("seeded", None)
    live = tes.make_fetcher(None, live=True, live_fetch=lambda url: ("live:" + url, None))
    assert live(endpoint) == ("live:" + SYND_URL, None)
    assert tes.make_fetcher(None)(endpoint) == (None, "live-fetch-not-enabled")


# --- acquire_public_url.py integration (subprocess, seeded; no live X fetch) ---


def _run_acquire(tmp_path: Path, *, direct: str, seed: dict | None) -> dict:
    direct_file = tmp_path / "direct.html"
    direct_file.write_text(direct, encoding="utf-8")
    cmd = [sys.executable, str(WEBFETCH / "acquire_public_url.py"), "--url", STATUS_URL, "--direct-response-file", str(direct_file)]
    if seed is not None:
        seed_file = tmp_path / "seed.json"
        seed_file.write_text(json.dumps(seed), encoding="utf-8")
        cmd += ["--domain-route-response-file", str(seed_file)]
    result = subprocess.run(cmd, cwd=ROOT, check=False, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


CAPTCHA = "<html><body>verify you are human captcha</body></html>"


def test_acquire_exact_fetched_after_direct_captcha(tmp_path: Path) -> None:
    out = _run_acquire(tmp_path, direct=CAPTCHA, seed={SYND_URL: {"text": json.dumps({"id_str": SID, "text": "body"})}})
    assert out["disposition"] == "success"
    assert out["source_identity"] == "exact-fetched"
    assert out["selected_attempt"]["stage_id"] == "domain-specific-route"


def test_acquire_exact_blocked_no_substitution(tmp_path: Path) -> None:
    out = _run_acquire(tmp_path, direct=CAPTCHA, seed={SYND_URL: {"text": "captcha verify you are human"}})
    assert out["source_identity"] == "exact-blocked"
    assert out["final_status"] != "success"


def test_acquire_default_is_exact_unavailable_not_substituted(tmp_path: Path) -> None:
    out = _run_acquire(tmp_path, direct=CAPTCHA, seed=None)
    assert out["source_identity"] == "exact-unavailable"
    assert out["final_status"] != "success"


def test_acquire_non_twitter_has_no_source_identity(tmp_path: Path) -> None:
    direct_file = tmp_path / "ok.html"
    direct_file.write_text("hello world " * 200, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(WEBFETCH / "acquire_public_url.py"), "--url", "https://example.com/a", "--direct-response-file", str(direct_file)],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "source_identity" not in json.loads(result.stdout)  # behavior-preserving for other sources


# --- gather_public_url.py: source_identity reaches the answer path (in-process) ---


def _load_gather():
    import importlib.util

    path = ROOT / "skills" / "public" / "gather" / "scripts" / "gather_public_url.py"
    spec = importlib.util.spec_from_file_location("gather_public_url", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gpu = _load_gather()


def test_gather_record_surfaces_source_identity() -> None:
    acquisition = {
        "route": {"route_id": "twitter-syndication", "route_family": "public-api", "access_modes": []},
        "selected_attempt": {"stage_id": "domain-specific-route", "status": "captcha"},
        "attempts": [{"stage_id": "domain-specific-route", "status": "captcha", "details": {"endpoint": SYND_URL, "reason": "blocked"}}],
        "disposition": "degraded",
        "final_status": "captcha",
        "final_confidence": "none",
        "source_identity": "exact-blocked",
    }
    record = gpu._render_record(STATUS_URL, acquisition, persist_requested=False)
    assert "Source Identity: `exact-blocked`" in record


def test_gather_build_acquire_cmd_passes_through_exact_source_options() -> None:
    from argparse import Namespace

    args = Namespace(
        repo_root=Path("."), url=STATUS_URL, intent="single", browser_mode="auto", timeout=20,
        direct_response_file=Path("d.html"), domain_route_response_file=Path("seed.json"),
        live_domain_route=True, expect_text=[], expect_regex=[], expect_json_field=[],
        persist_extracted_content=False, max_extracted_content_chars=1000,
    )
    cmd = gpu._build_acquire_cmd(args)
    assert "--domain-route-response-file" in cmd and "seed.json" in cmd
    assert "--live-domain-route" in cmd
