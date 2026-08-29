"""WS-1 seeded proof: the rung-2 distinct-channel observer + rung-1 presence
floor on the release publish boundary (before `ensure_release_issues_closed`).

Network-free unit + integration proof: the rung-1 floor refuses a SILENT record,
a confirmation OR a typed non-`verified` disposition passes it EQUALLY (F2a), and
the observer never uses `gh release view` as the distinct channel.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from .release_script_loading import load_release_script

_POST_CREATE = load_release_script("publish_release_post_create")
_EXECUTE = load_release_script("publish_release_execute")
_HELPERS = load_release_script("publish_release_helpers")
_NARRATIVE = load_release_script("audit_public_release_narrative")
_COMMON = load_release_script("publish_release_common")
_SECTIONS = load_release_script("publish_release_verification_sections")


def _shell_result(returncode: int, stdout: str = "", stderr: str = ""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def _release_commit_artifact_cli(commands: list[list[str]], write_counter: dict[str, int]) -> SimpleNamespace:
    def write_artifact(*_args, **_kwargs):
        write_counter["count"] += 1
        return "release.md"

    def run(command, *, cwd, check=True):
        commands.append(command)
        return _shell_result(0)

    return SimpleNamespace(
        write_current_artifact=write_artifact,
        run_narrative_audit=lambda *_a, **_k: None,
        run=run,
        run_fresh_checkout_probes=lambda *_a, **_k: {"status": "failed", "reason": "test"},
        release_commit_body=lambda *_a, **_k: ["fallback body"],
    )


def _release_commit_artifact_cli_with_passed_probe(commands: list[list[str]], write_counter: dict[str, int]) -> SimpleNamespace:
    probe_results = iter(({"status": "passed"}, {"status": "failed", "reason": "after amend"}))
    amend_calls = {"count": 0}
    cli = _release_commit_artifact_cli(commands, write_counter)
    cli.run_fresh_checkout_probes = lambda *_a, **_k: next(probe_results)

    def amend(*_args, **_kwargs):
        amend_calls["count"] += 1

    cli.amend_fresh_checkout_artifact = amend
    cli.amend_calls = amend_calls
    return cli


def _release_commit_artifact_state() -> dict:
    return {
        "payload": {
            "commit_message": "Release v1.0.0",
            "issue_closeout_draft_validation": {"paragraphs": ["Release v1.0.0", "Body A", "Body B"]},
        },
        "tag_name": "v1.0.0",
        "notes_file": None,
        "expected_release_url": "https://x/v1.0.0",
        "host_payload": {},
        "fresh_checkout_plan": {},
    }


# --- rung-1 presence floor ------------------------------------------------


def test_rung1_floor_refuses_silent_record() -> None:
    assert _POST_CREATE.evaluate_release_distinct_channel({})["ok"] is False
    assert _POST_CREATE.evaluate_release_distinct_channel({"distinct_channel_verification": {}})["ok"] is False


def test_rung1_floor_passes_confirmation_and_typed_disposition_equally() -> None:
    # F2a: a confirmation and a typed non-`verified` disposition pass EQUALLY.
    confirmed = {"distinct_channel_verification": {"channel": "https-fetch", "status": "confirmed"}}
    disposed = {"distinct_channel_verification": {"channel": "none", "status": "skipped", "reason": "x"}}
    assert _POST_CREATE.evaluate_release_distinct_channel(confirmed)["ok"] is True
    assert _POST_CREATE.evaluate_release_distinct_channel(disposed)["ok"] is True


def test_backend_verified_claim_is_downgraded_without_distinct_confirmation() -> None:
    payload = {
        "public_release_verification": "verified",
        "distinct_channel_verification": {"channel": "none", "status": "skipped"},
    }
    assert _POST_CREATE.reconcile_public_release_verification(payload) == "unproven"
    assert payload["public_release_verification"] == "unproven"
    assert "distinct-channel" in payload["public_release_verification_reason"]


def test_backend_and_distinct_confirmation_keep_verified_claim() -> None:
    payload = {
        "public_release_verification": "verified",
        "distinct_channel_verification": {"channel": "https-fetch", "status": "confirmed"},
    }
    assert _POST_CREATE.reconcile_public_release_verification(payload) == "verified"
    assert payload["public_release_verification"] == "verified"


def test_confirmed_adapter_probe_without_established_guard_is_unproven() -> None:
    payload = {
        "public_release_verification": "verified",
        "distinct_channel_verification": {
            "channel": "adapter-probe",
            "status": "confirmed",
            "same_proxy_guard": "inconclusive-degenerate-release-view-template",
        },
    }
    assert _POST_CREATE.reconcile_public_release_verification(payload) == "unproven"
    assert payload["public_release_verification"] == "unproven"
    assert "without established distinctness" in payload["public_release_verification_reason"]


def test_confirmed_adapter_probe_with_evaluated_guard_keeps_verified_claim() -> None:
    payload = {
        "public_release_verification": "verified",
        "distinct_channel_verification": {
            "channel": "adapter-probe",
            "status": "confirmed",
            "same_proxy_guard": "evaluated",
        },
    }
    assert _POST_CREATE.reconcile_public_release_verification(payload) == "verified"
    assert payload["public_release_verification"] == "verified"


# --- rung-2 distinct-channel observer -------------------------------------


def test_observer_http_default_confirms_on_200() -> None:
    payload: dict = {}
    record = _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={}, run_shell=None, tag_name="v1.2.3",
        expected_release_url="https://example/releases/tag/v1.2.3",
        http_probe=lambda url, **kwargs: {
            "channel": "https-fetch", "url": url, "status": "confirmed", "http_status": 200,
            "expected_content": kwargs.get("expected_content"),
        },
    )
    assert record["status"] == "confirmed"
    assert record["channel"] == "https-fetch"
    # The probe must be told what identifies THIS release; confirming on "a 200
    # with a body" made the verdict independent of what came back (D4).
    assert record["expected_content"] == "v1.2.3"
    assert payload["distinct_channel_verification"] is record


def test_observer_http_default_records_typed_disposition_on_failure() -> None:
    payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={}, run_shell=None, tag_name="v1.2.3",
        expected_release_url="https://example/releases/tag/v1.2.3",
        http_probe=lambda url, **_kwargs: {"channel": "https-fetch", "url": url, "status": "blocked-needs-capability", "reason": "offline"},
    )
    # A typed disposition is recorded, not a silent green.
    assert payload["distinct_channel_verification"]["status"] == "blocked-needs-capability"


def test_observer_adapter_probe_confirms_and_disposes() -> None:
    calls: list[str] = []

    def fake_run_shell(command, *, cwd, check):
        calls.append(command)
        return _shell_result(0 if "ok" in command else 1, stderr="probe could not confirm")

    ok_payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), ok_payload, adapter_data={"post_publish_distinct_channel_probe": "probe ok {tag}"},
        run_shell=fake_run_shell, tag_name="v9", expected_release_url="https://x/v9",
    )
    assert ok_payload["distinct_channel_verification"]["status"] == "confirmed"
    assert calls == ["probe ok v9"]  # {tag} substituted, never `gh release view`

    fail_payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), fail_payload, adapter_data={"post_publish_distinct_channel_probe": "probe bad {url}"},
        run_shell=fake_run_shell, tag_name="v9", expected_release_url="https://x/v9",
    )
    rec = fail_payload["distinct_channel_verification"]
    assert rec["status"] == "not-confirmed"
    assert rec["reason"] == "probe could not confirm"


def test_observer_never_uses_gh_release_view() -> None:
    # The observer's only subprocess hook is run_shell (the adapter probe); it has
    # no `run`/backend handle, so it structurally cannot re-read `gh release view`.
    def fake_run_shell(command, *, cwd, check):
        assert "gh release view" not in command
        return _shell_result(0)

    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), {}, adapter_data={"post_publish_distinct_channel_probe": "probe {tag}"},
        run_shell=fake_run_shell, tag_name="v1", expected_release_url=None,
    )


# --- north-star finding: same-proxy probe is mechanically flagged, not `confirmed` --


def test_observer_flags_probe_matching_release_view_shape_as_same_proxy() -> None:
    def run_shell_never_called(*_args, **_kwargs):
        raise AssertionError("a same-proxy-flagged probe must never be run")

    payload: dict = {}
    backend = {"id": "gh", "commands": None}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "gh release view {tag}"},
        run_shell=run_shell_never_called, tag_name="v1.2.3", expected_release_url="https://x/v1.2.3",
        backend=backend, backend_command=_HELPERS.backend_command,
    )
    record = payload["distinct_channel_verification"]
    assert record["status"] == "same-proxy-flagged"
    assert record["status"] != "confirmed"
    assert record["observer"].startswith("same-proxy")


def test_distinct_channel_records_name_observer_identity(monkeypatch) -> None:
    # Observer identity is a recorded observable additive to the channel: the
    # default HTTP probe names its credential-distinct-but-host-shared
    # identity, the adapter probe names the operator-configured shell, and a
    # skipped record names `none`. Network-free: urlopen is stubbed.
    import urllib.error

    def raising_urlopen(request, timeout):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(_POST_CREATE.urllib.request, "urlopen", raising_urlopen)
    blocked = _POST_CREATE._http_release_probe("https://example/releases/tag/v9")
    assert blocked["status"] == "blocked-needs-capability"
    assert blocked["observer"].startswith("unauthenticated-http")
    assert "same host/process" in blocked["observer"]

    adapter_payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), adapter_payload,
        adapter_data={"post_publish_distinct_channel_probe": "probe ok {tag}"},
        run_shell=lambda command, *, cwd, check: _shell_result(0),
        tag_name="v9", expected_release_url="https://x/v9",
    )
    assert adapter_payload["distinct_channel_verification"]["observer"].startswith(
        "adapter-probe-shell"
    )

    skipped_payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), skipped_payload, adapter_data={}, run_shell=None,
        tag_name="v9", expected_release_url=None,
    )
    assert skipped_payload["distinct_channel_verification"]["observer"] == "none"


def test_observer_confirms_genuinely_distinct_probe_with_backend_supplied() -> None:
    calls: list[str] = []

    def fake_run_shell(command, *, cwd, check):
        calls.append(command)
        return _shell_result(0)

    payload: dict = {}
    backend = {"id": "gh", "commands": None}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "distinct-channel-probe {tag}"},
        run_shell=fake_run_shell, tag_name="v1.2.3", expected_release_url="https://x/v1.2.3",
        backend=backend, backend_command=_HELPERS.backend_command,
    )
    assert payload["distinct_channel_verification"]["status"] == "confirmed"
    assert calls == ["distinct-channel-probe v1.2.3"]


def test_observer_flags_probe_matching_custom_backend_release_view_shape() -> None:
    # Data-driven: the check derives the forbidden shape from THIS backend's own
    # `release_view` template, not a hardcoded `gh release view` string.
    backend = {"id": "custom-release", "commands": {"release_view": ["custom-release", "release", "view", "{tag}"]}}

    def run_shell_never_called(*_args, **_kwargs):
        raise AssertionError("a same-proxy-flagged probe must never be run")

    payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "custom-release release view {tag}"},
        run_shell=run_shell_never_called, tag_name="v9", expected_release_url="https://x/v9",
        backend=backend, backend_command=_HELPERS.backend_command,
    )
    assert payload["distinct_channel_verification"]["status"] == "same-proxy-flagged"


def test_observer_without_backend_kwargs_skips_the_same_proxy_check() -> None:
    # Back-compat: the mechanical check activates only when a caller supplies
    # `backend`/`backend_command` (every production call site now does). Callers
    # that omit them keep the pre-fix behavior instead of silently misbehaving.
    calls: list[str] = []

    def fake_run_shell(command, *, cwd, check):
        calls.append(command)
        return _shell_result(0)

    payload: dict = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "gh release view {tag}"},
        run_shell=fake_run_shell, tag_name="v1", expected_release_url="https://x/v1",
    )
    assert payload["distinct_channel_verification"]["status"] == "confirmed"
    assert calls == ["gh release view v1"]


def test_initial_release_commit_reserves_validated_closeout_body_for_later() -> None:
    """The publication commit must not close issues before observer evidence exists."""
    commands: list[list[str]] = []
    writes = {"count": 0}
    cli = _release_commit_artifact_cli(commands, writes)
    args = SimpleNamespace(close_issue=[44], close_issue_behavior=[], close_issue_probe_record=[], remote="origin")
    state = _release_commit_artifact_state()
    result = _EXECUTE._commit_release_artifact(args, Path("."), state, {}, cli=cli)
    commit = next(command for command in commands if command[:2] == ["git", "commit"])
    assert commit == ["git", "commit", "-m", "Release v1.0.0"]
    assert result["artifact_relpath"] == "release.md"
    assert writes["count"] == 1


def test_initial_release_commit_never_falls_back_to_a_closeout_body() -> None:
    """Even a legacy fallback body belongs to the later carrier commit."""
    commands: list[list[str]] = []
    writes = {"count": 0}
    cli = _release_commit_artifact_cli(commands, writes)
    args = SimpleNamespace(close_issue=[44], close_issue_behavior=["Behavior #44: verified via installer"],
        close_issue_probe_record=["Probe record #44: local-only-by-contract"], remote="origin")
    state = _release_commit_artifact_state()
    state["payload"]["issue_closeout_draft_validation"]["paragraphs"] = []

    _EXECUTE._commit_release_artifact(args, Path("."), state, {}, cli=cli)

    commit = next(command for command in commands if command[:2] == ["git", "commit"])
    assert commit == ["git", "commit", "-m", "Release v1.0.0"]


def test_commit_release_artifact_rechecks_fresh_checkout_after_amend() -> None:
    commands: list[list[str]] = []
    writes = {"count": 0}
    cli = _release_commit_artifact_cli_with_passed_probe(commands, writes)
    args = SimpleNamespace(close_issue=[44], close_issue_behavior=[], close_issue_probe_record=[], remote="origin")
    state = _release_commit_artifact_state()

    result = _EXECUTE._commit_release_artifact(args, Path("."), state, {}, cli=cli)

    assert result["fresh_checkout_payload"] == {"status": "failed", "reason": "after amend"}
    assert result["payload"]["fresh_checkout_probe_status"] == "failed"
    assert cli.amend_calls["count"] == 1


# --- integration wiring: refuse on silence, proceed on presence -----------














def test_same_proxy_guard_is_not_defeated_by_flag_order_wrappers_or_paths() -> None:
    """D3 regression: the guard was a positional PREFIX match on the rendered
    command, so everything that changes the token order without changing what
    runs slipped through and the release confirmed itself through the very
    channel it was supposed to be checked against.

    Confirmed evasions, all running the identical `gh release view` query:
    moving `--json url` ahead of the tag, `sh -c "..."`, `env`, and an absolute
    `/usr/bin/gh` path."""
    def run_shell_never_called(*_args, **_kwargs):
        raise AssertionError("a same-proxy-flagged probe must never be run")

    for probe in (
        "gh release view v1.2.3",
        "gh   release  view   v1.2.3   --json url",
        "gh release view --json url v1.2.3",
        'sh -c "gh release view v1.2.3"',
        "env gh release view v1.2.3",
        "/usr/bin/gh release view v1.2.3",
        'bash -c "GH_TOKEN=x /usr/local/bin/gh release view --json url v1.2.3"',
    ):
        payload: dict = {}
        _POST_CREATE.confirm_release_via_distinct_channel(
            Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": probe},
            run_shell=run_shell_never_called, tag_name="v1.2.3",
            expected_release_url="https://x/v1.2.3",
            backend={"id": "gh", "commands": None}, backend_command=_HELPERS.backend_command,
        )
        record = payload["distinct_channel_verification"]
        assert record["status"] == "same-proxy-flagged", probe
        assert record["status"] != "confirmed", probe


def test_same_proxy_guard_still_admits_a_genuinely_distinct_probe() -> None:
    """Falsifiable counterpart: the guard must not swallow every probe. These
    reach the release through channels `gh release view` does not use — including
    `gh api`, which shares the executable but not the endpoint."""
    ran: list[str] = []

    def fake_run_shell(command, *_args, **_kwargs):
        ran.append(command)
        return type("R", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()

    for probe in (
        "curl -sSL https://github.com/o/r/releases/tag/v1.2.3",
        "git ls-remote --tags origin v1.2.3",
        "gh api repos/o/r/releases/tags/v1.2.3",
    ):
        payload: dict = {}
        _POST_CREATE.confirm_release_via_distinct_channel(
            Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": probe},
            run_shell=fake_run_shell, tag_name="v1.2.3",
            expected_release_url="https://x/v1.2.3",
            backend={"id": "gh", "commands": None}, backend_command=_HELPERS.backend_command,
        )
        assert payload["distinct_channel_verification"]["status"] != "same-proxy-flagged", probe
    assert len(ran) == 3


def test_same_proxy_guard_closes_the_review_found_bypasses() -> None:
    """Second-round D3 regression: the first fix closed six evasions and left
    four, each confirmed by execution.

    - an unparseable command failed OPEN, so one apostrophe in a `#` comment ran
      the identical query under bash while the guard returned "distinct";
    - only the FIRST token was basename-normalized, so an unlisted wrapper and an
      absolute path composed (`sudo /usr/bin/gh ...`) even though each alone was
      caught;
    - omitting the tag entirely escaped, and `gh release view` with no tag
      resolves to the LATEST release — moments after publish, the very one being
      confirmed;
    - the unwrap budget could be exhausted by leading env assignments, and
      running out returned silently as if unwrapping had finished."""
    def run_shell_never_called(*_args, **_kwargs):
        raise AssertionError("a same-proxy-flagged probe must never be run")

    for probe in (
        "gh release view v1.2.3 # don't trust gh",
        "sudo /usr/bin/gh release view v1.2.3",
        "timeout 10 /usr/bin/gh release view v1.2.3",
        "gh release view",
        "A=1 B=2 C=3 D=4 E=5 /usr/bin/gh release view v1.2.3",
    ):
        payload: dict = {}
        _POST_CREATE.confirm_release_via_distinct_channel(
            Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": probe},
            run_shell=run_shell_never_called, tag_name="v1.2.3",
            expected_release_url="https://x/v1.2.3",
            backend={"id": "gh", "commands": None}, backend_command=_HELPERS.backend_command,
        )
        assert payload["distinct_channel_verification"]["status"] == "same-proxy-flagged", probe


def test_same_proxy_guard_records_when_it_could_not_be_evaluated() -> None:
    """A degenerate `release_view` template (empty, or one generic token like
    `gh`) cannot discriminate: subset matching against it either refuses every
    probe sharing an executable or passes everything.

    The first fix rendered a verdict anyway — `gh api ...` was wrongly refused
    against a one-token template, and a real same-proxy probe silently passed
    against an empty one. The guard now declines to render a verdict it cannot
    establish, and says so on the record instead of leaving the reader to read
    the absence of a flag as a passed check."""
    def fake_run_shell(*_args, **_kwargs):
        return type("R", (), {"returncode": 0, "stdout": "ok", "stderr": ""})()

    for label, tokens in (("empty", []), ("single generic token", ["gh"])):
        payload: dict = {}
        _POST_CREATE.confirm_release_via_distinct_channel(
            Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "gh release view v1.2.3"},
            run_shell=fake_run_shell, tag_name="v1.2.3", expected_release_url="https://x/v1.2.3",
            backend={"id": "x", "commands": None}, backend_command=lambda *a, **k: list(tokens),
        )
        record = payload["distinct_channel_verification"]
        assert record["status"] != "same-proxy-flagged", label
        assert record["same_proxy_guard"] == "inconclusive-degenerate-release-view-template", label

    # Falsifiable counterpart: a real template evaluates the guard.
    payload = {}
    _POST_CREATE.confirm_release_via_distinct_channel(
        Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": "curl -sSL https://x"},
        run_shell=fake_run_shell, tag_name="v1.2.3", expected_release_url="https://x/v1.2.3",
        backend={"id": "gh", "commands": None}, backend_command=_HELPERS.backend_command,
    )
    assert payload["distinct_channel_verification"]["same_proxy_guard"] == "evaluated"


def _serve(body: bytes, code: int = 200):
    import http.server
    import socketserver
    import threading

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            self.send_response(code)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            return

    server = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    return server, server.server_address[1]


def test_http_probe_refuses_a_200_that_does_not_mention_the_release() -> None:
    """D4 regression: the probe confirmed on any HTTP 200 with at least one body
    byte, so the verdict was independent of what came back.

    Confirmed against a local server returning a page that mentions no tag:
    `{'status': 'confirmed', 'http_status': 200, 'evidence_len': 46}`. A captive
    portal, a rate-limit notice, a 404 served as 200, or a silent redirect to the
    repository root all confirmed a release that might not exist."""
    server, port = _serve(b"<html><body>Nothing to see here at all.</body></html>")
    try:
        record = _POST_CREATE._http_release_probe(
            f"http://127.0.0.1:{port}/releases/tag/v2.11.3", timeout=5, expected_content="v2.11.3"
        )
    finally:
        server.shutdown()
        server.server_close()
    assert record["status"] == "not-confirmed"
    assert record["http_status"] == 200
    assert "does not mention" in record["reason"]


def test_http_probe_confirms_when_the_response_names_the_release() -> None:
    """Falsifiable counterpart: the same 200 confirms once the body actually
    names the tag, and the content it was checked for is recorded."""
    server, port = _serve(b"<html><body>Release v2.11.3 is out</body></html>")
    try:
        record = _POST_CREATE._http_release_probe(
            f"http://127.0.0.1:{port}/releases/tag/v2.11.3", timeout=5, expected_content="v2.11.3"
        )
    finally:
        server.shutdown()
        server.server_close()
    assert record["status"] == "confirmed"
    assert record["expected_content"] == "v2.11.3"


def test_http_probe_without_expected_content_does_not_confirm() -> None:
    """No identifying string to look for is an unestablished scope: the fetch
    proves a page exists, never that it is this release's page."""
    server, port = _serve(b"<html>anything</html>")
    try:
        record = _POST_CREATE._http_release_probe(f"http://127.0.0.1:{port}/x", timeout=5)
    finally:
        server.shutdown()
        server.server_close()
    assert record["status"] == "not-confirmed"
    assert "no expected content was supplied" in record["reason"]


def test_published_release_body_audit_surfaces_mutable_pointers_as_advisory() -> None:
    """D2 residual: the pre-publish notes audit only runs when a notes FILE is
    supplied, so `--generate-notes` — the default — published a body nothing had
    inspected. Auto-generated bodies are commit messages and PR text, a prime
    carrier of `blob/main` links.

    Post-hoc by construction and advisory by design: the release already exists,
    so refusing after the fact would only strand the publish."""
    payload: dict = {}
    record = _POST_CREATE.audit_published_release_body(
        Path("."), payload, tag_name="v1.2.3", backend={"id": "gh", "commands": None},
        backend_command=_HELPERS.backend_command,
        run=lambda *a, **k: _shell_result(0, stdout="See https://github.com/o/r/blob/main/docs/x.md\n"),
        audit_notes_text=_NARRATIVE.audit_notes_text,
    )
    assert record["status"] == "advisory"
    assert record["advisories"] and "MUTABLE ref" in record["advisories"][0]
    assert payload["published_notes_audit"] is record

    clean: dict = {}
    record = _POST_CREATE.audit_published_release_body(
        Path("."), clean, tag_name="v1.2.3", backend={"id": "gh", "commands": None},
        backend_command=_HELPERS.backend_command,
        run=lambda *a, **k: _shell_result(0, stdout="Self-contained notes.\n"),
        audit_notes_text=_NARRATIVE.audit_notes_text,
    )
    assert record["status"] == "clean"


def test_published_release_body_audit_records_an_unavailable_readback() -> None:
    """A body readback that fails is a recorded disposition, never a crash and
    never a clean verdict."""
    payload: dict = {}
    record = _POST_CREATE.audit_published_release_body(
        Path("."), payload, tag_name="v1.2.3", backend={"id": "gh", "commands": None},
        backend_command=_HELPERS.backend_command,
        run=lambda *a, **k: _shell_result(1, stderr="gh: not authenticated"),
        audit_notes_text=_NARRATIVE.audit_notes_text,
    )
    assert record["status"] == "unavailable"
    assert "not authenticated" in record["reason"]


def test_published_body_audit_is_wired_to_the_list_runner_not_the_shell_runner() -> None:
    """The published-body audit builds a LIST command, and `run_shell` uses
    `shell=True`, where a list makes `args[0]` the command string and drops the
    rest into `$0,$1,...`.

    Confirmed: `run_shell(["git","status","--short"])` runs bare `git` and exits
    1, while `run(...)` returns short-format output. Wired to `run_shell`, the
    audit recorded `unavailable` on every publish — closed-looking, not closed.
    This pins the runner the wiring actually passes."""
    import inspect

    source = inspect.getsource(_COMMON.run_distinct_channel_floor)
    audit_call = source.split("audit_published_release_body")[1]
    assert "run=cli.run," in audit_call
    assert "run=cli.run_shell," not in audit_call


def test_published_body_audit_survives_a_backend_without_the_op() -> None:
    """`backend_command` raises SystemExit for a non-`gh` backend with no
    template for an op, and SystemExit does not derive from Exception.

    This runs AFTER the release exists and outside the rollback wrapper's scope,
    so an escaping SystemExit stranded the publish before the rung-1 floor, issue
    closeout, and the final artifact commit — for every non-`gh` adapter, over an
    advisory that is allowed to fail."""
    payload: dict = {}
    record = _POST_CREATE.audit_published_release_body(
        Path("."), payload, tag_name="v1.2.3",
        backend={"id": "acme", "commands": {"release_view": ["acme", "release", "view", "{tag}"]}},
        backend_command=_HELPERS.backend_command,
        run=_HELPERS.run,
        audit_notes_text=_NARRATIVE.audit_notes_text,
    )
    assert record["status"] == "not-configured"
    assert "release_view_body" in record["reason"]


def test_published_body_audit_does_not_call_an_empty_body_clean() -> None:
    """An empty body is what a misrouted, unauthenticated, or wrong-op readback
    returns. Calling it `clean` is a PASS over a scope never established — the
    class this fix was closing, reintroduced by the fix."""
    payload: dict = {}
    record = _POST_CREATE.audit_published_release_body(
        Path("."), payload, tag_name="v1.2.3", backend={"id": "gh", "commands": None},
        backend_command=_HELPERS.backend_command,
        run=lambda *a, **k: _shell_result(0, stdout="   \n"),
        audit_notes_text=_NARRATIVE.audit_notes_text,
    )
    # `unestablished`, not `unauthored`: an empty readback means the audit could
    # not LOOK, which is a tooling remedy, not an operator one.
    assert record["status"] == "unestablished"
    assert record["advisories"] == []


def test_http_probe_records_what_it_cannot_establish() -> None:
    """Measured 2026-07-27: `github.com/<o>/<r>/releases/tag/<tag>` returns HTTP
    200 with the tag in the body for a tag that has NO GitHub release (verified
    against `v0.1.1`, a pushed tag with no release — 200, tag present 23 times),
    and both that page and a real release page title themselves `Release <tag>`.
    The publish flow pushes the tag BEFORE creating the release, so this channel
    cannot distinguish "the release exists" from "the tag was pushed".

    D4's fix closes the "any 200 with any body" hole; it does NOT make this probe
    proof of release existence. The record says so rather than letting
    `confirmed` be read as the stronger claim."""
    server, port = _serve(b"<html><body>Release v1.2.3</body></html>")
    try:
        record = _POST_CREATE._http_release_probe(
            f"http://127.0.0.1:{port}/releases/tag/v1.2.3", timeout=5, expected_content="v1.2.3"
        )
    finally:
        server.shutdown()
        server.server_close()
    assert record["status"] == "confirmed"
    assert record["establishes"] == "public-page-reachable-and-names-the-tag"
    assert "does not establish" not in record  # spelled `does_not_establish`
    assert "GitHub RELEASE exists" in record["does_not_establish"]


def test_same_proxy_guard_flags_a_probe_that_unwraps_to_no_command() -> None:
    """S93: the guard's stated contract is that every branch which cannot
    ESTABLISH distinctness returns True, and one branch did the opposite.

    A configured probe that unwraps to zero tokens — `env`, `sh -c ""` — runs no
    query at all, so nothing about distinctness is established. It was reported
    as "not same-proxy", which put it on the branch that RUNS the probe and
    records an ordinary result: an unestablished scope reading as a clean
    distinct-channel observation at the publish boundary.
    """
    def run_shell_never_called(*_args, **_kwargs):
        raise AssertionError("a probe that establishes nothing must never be run as a distinct channel")

    for probe in ("env", 'sh -c ""'):
        payload: dict = {}
        _POST_CREATE.confirm_release_via_distinct_channel(
            Path("."), payload, adapter_data={"post_publish_distinct_channel_probe": probe},
            run_shell=run_shell_never_called, tag_name="v1.2.3",
            expected_release_url="https://x/v1.2.3",
            backend={"id": "gh", "commands": None}, backend_command=_HELPERS.backend_command,
        )
        record = payload["distinct_channel_verification"]
        assert record["status"] == "same-proxy-flagged", probe
        # The record is what the rung-2 human auditor reads, and `same-proxy-flagged`
        # now covers four causes. Naming only the token-shape match would send that
        # auditor to fix a same-proxy probe that does not exist.
        assert "unwraps to no command at all" in record["reason"], probe
        assert "does not ESTABLISH" in record["reason"], probe
        assert "release_view shape" not in record["observer"], probe

    # Falsifiable counterpart, on the same guard: a genuinely distinct probe must
    # stay on the other side of the same call.
    guard = load_release_script("publish_release_same_proxy_guard")
    assert guard._probe_matches_release_view_shape(
        "curl -sSL https://x", backend={"id": "gh", "commands": None},
        backend_command=_HELPERS.backend_command, tag_name="v1",
    ) is False


def test_flagged_qualifier_does_not_name_a_cause_it_did_not_establish() -> None:
    """The reader-facing half of S93. `_distinct_channel_qualifier` branched on
    status alone, so a probe that ran no query at all was described to the auditor
    as one that "matched this backend's own `release_view` command" — the artifact
    asserting a specific cause it never established, which is D8's failure mode
    one surface over."""
    sections = load_release_script("publish_release_verification_sections")

    lines = sections.distinct_channel_verification_lines(
        {
            "status": "same-proxy-flagged",
            "channel": "adapter-probe",
            "command": "env",
            "reason": "probe unwraps to no command at all",
        }
    )

    verdict = next(line for line in lines if "Rung-2 distinct-channel verdict" in line)
    assert "NOT a distinct channel" in verdict
    assert "did not establish" in verdict
    assert "matched this backend's own" not in verdict
    assert any("Disposition reason: probe unwraps to no command at all" in line for line in lines)


def test_unwrap_budget_exhaustion_and_unlexable_payload_are_reported_as_exhausted() -> None:
    """The two `_unwrap_command_tokens` escape hatches, pinned on the helper.

    A probe nested past the unwrap budget, and a wrapper whose inline `-c`
    payload cannot be lexed, are both scopes the guard could not descend into.
    Returning `exhausted=False` for either would let the caller treat a
    half-unwrapped command as fully inspected."""
    guard = load_release_script("publish_release_same_proxy_guard")

    _, exhausted = guard._unwrap_command_tokens(["env"] * 40)
    assert exhausted is True

    _, unlexable = guard._unwrap_command_tokens(["sh", "-c", "gh release view 'v1"])
    assert unlexable is True

    tokens, clean = guard._unwrap_command_tokens(["env", "sh", "-c", "gh release view v1"])
    assert clean is False
    assert tokens == ["gh", "release", "view", "v1"]


def test_published_body_audit_refuses_to_call_an_unauthored_body_clean() -> None:
    """A body that is only `--generate-notes` boilerplate carries no mutable
    pointers, so the pointer rule finds nothing and `clean` reads as "audited and
    fine". Nothing was authored to audit.

    Reproduced against this repo's published releases, not inferred: v2.6.0,
    v2.7.0, v2.8.0, v2.11.0 and v2.11.1 each shipped a body of exactly this shape
    (81-83 bytes, one `**Full Changelog**` line), and v2.11.0's was the release
    whose drafted notes amended 2.10.0's now-wrong migration instruction.
    """
    payload: dict = {}
    record = _POST_CREATE.audit_published_release_body(
        Path("."), payload, tag_name="v2.11.0", backend={"id": "gh", "commands": None},
        backend_command=_HELPERS.backend_command,
        run=lambda *a, **k: _shell_result(
            0, stdout="**Full Changelog**: https://github.com/o/r/compare/v2.10.0...v2.11.0\n"
        ),
        audit_notes_text=_NARRATIVE.audit_notes_text,
    )

    assert record["status"] == "unauthored"
    assert record["advisories"] == []
    # Still advisory by construction: the release exists by now, so this branch
    # corrects what the record CLAIMS and must never raise or block.
    assert "no authored notes" in record["reason"]
    assert payload["published_notes_audit"] is record


def test_published_body_audit_still_audits_a_body_that_says_something() -> None:
    """The narrow rule must not swallow real notes. A body with authored content
    keeps its pointer verdict, boilerplate line and all."""
    advisory: dict = {}
    record = _POST_CREATE.audit_published_release_body(
        Path("."), advisory, tag_name="v1.2.3", backend={"id": "gh", "commands": None},
        backend_command=_HELPERS.backend_command,
        run=lambda *a, **k: _shell_result(
            0,
            stdout=(
                "## What's Changed\n* Fix the thing by @someone\n"
                "See https://github.com/o/r/blob/main/docs/x.md\n"
                "\n**Full Changelog**: https://github.com/o/r/compare/v1.2.2...v1.2.3\n"
            ),
        ),
        audit_notes_text=_NARRATIVE.audit_notes_text,
    )
    assert record["status"] == "advisory"
    assert record["advisories"] and "MUTABLE ref" in record["advisories"][0]


def test_body_content_check_names_boilerplate_apart_from_notes() -> None:
    """The discriminator itself, at the boundaries that decide a verdict."""
    says_anything = _POST_CREATE._body_says_anything
    assert not says_anything("")
    assert not says_anything("\n   \n")
    assert not says_anything("**Full Changelog**: https://github.com/o/r/compare/a...b\n")
    # Bold markers are GitHub's rendering choice, not part of the claim; a plain
    # or unlinked variant is the same empty body.
    assert not says_anything("Full Changelog: https://github.com/o/r/compare/a...b")
    assert not says_anything("\n**Full changelog**:\n\n")
    # One authored sentence is content. The rule establishes "the body is empty",
    # never "a human wrote it" — an auto-generated PR list passes here by design,
    # because calling it unauthored is a judgment the consuming repo owns.
    assert says_anything("Notes.\n**Full Changelog**: https://github.com/o/r/compare/a...b\n")
    assert says_anything("## What's Changed\n* Fix by @someone\n")


def test_unauthored_body_keeps_the_pointer_advisory_it_would_have_lost() -> None:
    """The content check runs BEFORE the pointer rule, so ordering decides whether
    a real finding survives.

    `Full changelog: <blob/main link>` is an AUTHORED one-line body that the
    boilerplate discriminator once swallowed: the record came back
    `advisories: []` with a reason asserting "auto-generated boilerplate only",
    dropping the exact D2 mutable-pointer finding this audit exists to surface —
    the class (a) fix reintroducing class (d) one surface over.
    """
    payload: dict = {}
    record = _POST_CREATE.audit_published_release_body(
        Path("."), payload, tag_name="v1.2.3", backend={"id": "gh", "commands": None},
        backend_command=_HELPERS.backend_command,
        run=lambda *a, **k: _shell_result(
            0, stdout="Full changelog: https://github.com/o/r/blob/main/CHANGELOG.md\n"
        ),
        audit_notes_text=_NARRATIVE.audit_notes_text,
    )

    # The line IS recognized boilerplate (any host's URL counts), so the body is
    # `unauthored` -- and the pointer finding survives on the same record. Both
    # facts are true and both are recorded; the bug was reporting only the first.
    assert record["status"] == "unauthored"
    assert record["advisories"] and "MUTABLE ref" in record["advisories"][0]


def test_boilerplate_discriminator_does_not_swallow_authored_one_line_bodies() -> None:
    """`\\S*` accepted any token after the colon, so an authored body whose whole
    content is a deliberate pointer, or a sentence merely starting with those
    words, was classified as generated."""
    says_anything = _POST_CREATE._body_says_anything
    # A URL is required, so prose after the phrase is authored content...
    assert says_anything("Full changelog rewritten")
    assert says_anything("Full Changelog: N/A")
    # The generated shapes stay matched: `compare` for a normal release and
    # `commits` for a first release with no predecessor.
    assert not says_anything("**Full Changelog**: https://github.com/o/r/compare/v1.2.2...v1.2.3")
    assert not says_anything("**Full Changelog**: https://github.com/o/r/commits/v1.0.0")
    # ...and so does a NON-GitHub host's. `release_view_body` is an adapter-declared
    # op, so pinning the URL to GitHub's `compare`/`commits` shape sent every other
    # host's empty body to `clean` -- "no mutable pointers found", asserted over a
    # body with nothing in it, which is the escape this branch exists to close.
    assert not says_anything("Full Changelog: https://example.dev/o/r/changelog?from=v1.2.2&to=v1.2.3")
    assert not says_anything("**Full Changelog**: https://git.example.internal/x/y/-/releases/v1.2.3")


def test_artifact_names_an_unauthored_body_apart_from_one_it_could_not_read() -> None:
    """Two worlds, two remedies, and they were rendered as one sentence.

    `unavailable`/`unestablished` mean the audit could not LOOK (remedy: fix auth
    or the adapter). `unauthored` means it looked and the release shipped an
    empty body (remedy: `gh release edit`, and the operator owns it). Sharing the
    "was NOT audited" sentence dropped the remedy for the case the branch exists
    for, and hid the body size the verdict was formed over.
    """
    unauthored = _SECTIONS.published_notes_audit_lines(
        {"status": "unauthored", "body_len": 83, "advisories": [],
         "reason": "published body carries no authored notes"}
    )
    rendered = "\n".join(unauthored)
    assert "no authored notes" in rendered
    assert "83 body bytes" in rendered
    assert "gh release edit" in rendered
    assert "NOT audited" not in rendered

    could_not_look = "\n".join(
        _SECTIONS.published_notes_audit_lines({"status": "unavailable", "reason": "gh: not authenticated"})
    )
    assert "NOT audited" in could_not_look
    assert "gh release edit" not in could_not_look

    # An unauthored body that still carried a mutable pointer renders both facts.
    both = "\n".join(
        _SECTIONS.published_notes_audit_lines(
            {"status": "unauthored", "body_len": 60, "advisories": ["points at MUTABLE ref `main`"]}
        )
    )
    assert "no authored notes" in both and "MUTABLE ref" in both
