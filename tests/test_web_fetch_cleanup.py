from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tests.repo_copy import REPO_COPY_IGNORE
from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
WEB_FETCH_SCRIPTS = ROOT / "skills" / "support" / "web-fetch" / "scripts"
GATHER_SCRIPTS = ROOT / "skills" / "public" / "gather" / "scripts"
SPA_HTML = "<html><body><div id=\"root\"></div></body></html>"
# Hang backstop for the SIGTERM-mid-render test's readiness wait, NOT the bar it
# measures -- that is the child's process state (see the comment at the wait loop).
# Sized an order of magnitude above the observed cost of reaching the browser stage
# so a trip means "investigate a hang", not "the lane was busy".
_HANG_BACKSTOP_SECONDS = 120

_ACQUIRE = load_script_module(
    "acquire_public_url_for_cleanup_test",
    WEB_FETCH_SCRIPTS / "acquire_public_url.py",
)


def _run_acquire(*args: str, env: dict[str, str] | None = None):
    return run_loaded_script_main("acquire_public_url.py", _ACQUIRE, *args, env=env)


def _make_logging_agent_browser(bin_dir: Path, log_path: Path, *, render_fails: bool = False) -> None:
    render = (
        '  *"get text body"*) printf "boom\\n" >&2; exit 1 ;;'
        if render_fails
        else "  *\"get text body\"*) printf 'rendered target proof from browser\\n' ;;"
    )
    (bin_dir / "agent-browser").write_text(
        "#!/bin/sh\n"
        f'printf "%s\\n" "$*" >> "{log_path}"\n'
        'case "$*" in\n'
        f"{render}\n"
        "  *) exit 0 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    (bin_dir / "agent-browser").chmod(0o755)


def _bundle_yaml_output(root: Path) -> None:
    """Place the real `scripts/yaml_output.py` at a synthetic layout's root.

    Every repo-owned command renders its stdout payload through this helper, and the
    exported plugin ships it at `<plugin-root>/scripts/yaml_output.py`. A hand-built
    layout that omits it is not a smaller export, it is one where the command has no
    output channel and exits on ImportError — so the copy keeps these fixtures
    faithful to the layout they claim to model.
    """
    scripts_dir = root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "scripts" / "yaml_output.py", scripts_dir / "yaml_output.py")


def _close_was_attempted(log_path: Path) -> bool:
    if not log_path.is_file():
        return False
    return any(line.strip().endswith("close") for line in log_path.read_text(encoding="utf-8").splitlines())


def test_acquire_attempts_close_on_render_success(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    _make_logging_agent_browser(bin_dir, log)
    direct = tmp_path / "direct.html"
    direct.write_text(SPA_HTML, encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS"] = "1"
    result = _run_acquire(
        "--url", "https://example.com/app",
        "--repo-root", str(ROOT),
        "--direct-response-file", str(direct),
        "--expect-text", "target proof",
        "--browser-mode", "auto",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "success"
    assert _close_was_attempted(log), log.read_text(encoding="utf-8") if log.is_file() else "no log"


def test_acquire_attempts_close_on_render_failure(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    _make_logging_agent_browser(bin_dir, log, render_fails=True)
    direct = tmp_path / "direct.html"
    direct.write_text(SPA_HTML, encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS"] = "1"
    result = _run_acquire(
        "--url", "https://example.com/app",
        "--repo-root", str(ROOT),
        "--direct-response-file", str(direct),
        "--expect-text", "target proof",
        "--browser-mode", "auto",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    # Render failed, but the session must still be closed via the finally block.
    assert _close_was_attempted(log), log.read_text(encoding="utf-8") if log.is_file() else "no log"
    render = next(a for a in payload["attempts"] if a["stage_id"] == "agent-browser-render-recon")
    assert render["error"]


@pytest.mark.boundary_contract(
    reason="an exported support layout must be self-sufficient in a clean interpreter"
)
def test_acquire_guard_unavailable_is_fail_visible(tmp_path: Path) -> None:
    # In a layout where the runtime guard is not reachable from repo_root/scripts
    # or any ancestor of the acquire helper, a skipped post-close proof must be
    # surfaced as `guard_unavailable` degraded, never as a clean success (#302).
    iso = tmp_path / "iso" / "webfetch"
    shutil.copytree(WEB_FETCH_SCRIPTS, iso, ignore=REPO_COPY_IGNORE)
    # The layout must be missing the GUARD specifically, not missing everything: the
    # shared YAML renderer is acquire's only output channel, so a tree that cannot
    # reach `scripts/yaml_output.py` produces no payload to judge at all. Ship it
    # (and only it) so `guard_unavailable` is what the fixture actually isolates.
    _bundle_yaml_output(iso.parent)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    _make_logging_agent_browser(bin_dir, log)
    user_repo = tmp_path / "user_repo"
    user_repo.mkdir()
    direct = tmp_path / "direct.html"
    direct.write_text(SPA_HTML, encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    result = subprocess.run(
        [
            sys.executable,
            str(iso / "acquire_public_url.py"),
            "--url", "https://example.com/app",
            "--repo-root", str(user_repo),
            "--direct-response-file", str(direct),
            "--expect-text", "target proof",
            "--browser-mode", "auto",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "degraded"
    assert _close_was_attempted(log)
    render = next(a for a in payload["attempts"] if a["stage_id"] == "agent-browser-render-recon")
    assert "guard_unavailable" in render["error"]
    assert render["details"]["cleanup"] == "failed"


@pytest.mark.boundary_contract(
    reason="an exported gather layout must be self-sufficient in a clean interpreter"
)
def test_gather_reaches_acquire_and_bundled_guard_in_exported_layout(tmp_path: Path) -> None:
    # #302: from an exported/installed plugin layout (skills/gather + support/web-fetch
    # + bundled scripts/guard) and an arbitrary user repo_root, gather must reach the
    # support web-fetch impl AND run the bundled cleanup proof — not silently skip it.
    plugin = tmp_path / "plugin"
    (plugin / "skills" / "gather").mkdir(parents=True)
    (plugin / "scripts").mkdir(parents=True)
    shutil.copytree(GATHER_SCRIPTS, plugin / "skills" / "gather" / "scripts", ignore=REPO_COPY_IGNORE)
    shutil.copytree(WEB_FETCH_SCRIPTS, plugin / "support" / "web-fetch" / "scripts", ignore=REPO_COPY_IGNORE)
    # The exported plugin root carries the shared YAML renderer next to the bundled
    # guard; without it acquire has no stdout channel and the layout would prove
    # nothing about reachability.
    _bundle_yaml_output(plugin)
    # A bundled guard that FAILS proves it was actually run (reached), not skipped.
    (plugin / "scripts" / "agent_browser_runtime_guard.py").write_text(
        "#!/usr/bin/env python3\nimport sys\nprint('reparented chromium residue remains', file=sys.stderr)\nsys.exit(1)\n",
        encoding="utf-8",
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    _make_logging_agent_browser(bin_dir, log)
    user_repo = tmp_path / "user_repo"
    user_repo.mkdir()
    direct = tmp_path / "direct.html"
    direct.write_text(SPA_HTML, encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    result = subprocess.run(
        [
            sys.executable,
            str(plugin / "skills" / "gather" / "scripts" / "gather_public_url.py"),
            "--url", "https://example.com/app",
            "--repo-root", str(user_repo),
            "--direct-response-file", str(direct),
            "--expect-text", "target proof",
            "--browser-mode", "auto",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 1, result.stdout
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "degraded"
    assert payload["acquisition_disposition"] == "degraded"
    render = next(a for a in payload["acquisition"]["attempts"] if a["stage_id"] == "agent-browser-render-recon")
    assert render["details"]["cleanup"] == "failed"
    assert "reparented chromium residue remains" in render["error"]


def test_acquire_public_url_degrades_when_agent_browser_close_fails(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "agent-browser").write_text(
        "#!/bin/sh\ncase \"$*\" in\n"
        "  *\"get text body\"*) printf 'rendered target proof from browser\\n' ;;\n"
        "  *\"close\"*) printf 'close failed\\n' >&2; exit 1 ;;\n"
        "  *) exit 0 ;;\nesac\n",
        encoding="utf-8",
    )
    (bin_dir / "agent-browser").chmod(0o755)
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body><div id=\"root\"></div></body></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    result = _run_acquire(
        "--url", "https://example.com/app",
        "--repo-root", str(ROOT),
        "--direct-response-file", str(direct),
        "--expect-text", "target proof",
        "--browser-mode", "auto",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "degraded"
    attempt = next(attempt for attempt in payload["attempts"] if attempt["stage_id"] == "agent-browser-render-recon")
    assert attempt["status"] == "error"
    assert attempt["details"]["cleanup"] == "failed"


def test_acquire_preserves_render_error_when_cleanup_also_fails(tmp_path: Path) -> None:
    # #310: when the render attempt fails for a real acquisition reason AND the
    # post-close runtime proof then fails, the operator must keep the original
    # acquisition `.error` (and status/confidence). The cleanup error is appended
    # to details, never allowed to clobber the "why the fetch failed" signal.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    _make_logging_agent_browser(bin_dir, log, render_fails=True)
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "agent_browser_runtime_guard.py").write_text(
        "#!/usr/bin/env python3\nimport sys\nprint('orphan daemon remains', file=sys.stderr)\nsys.exit(1)\n",
        encoding="utf-8",
    )
    direct = tmp_path / "direct.html"
    direct.write_text(SPA_HTML, encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    result = _run_acquire(
        "--url", "https://example.com/app",
        "--repo-root", str(repo),
        "--direct-response-file", str(direct),
        "--expect-text", "target proof",
        "--browser-mode", "auto",
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "degraded"
    render = next(a for a in payload["attempts"] if a["stage_id"] == "agent-browser-render-recon")
    # Original acquisition failure is preserved (the fake render exited 1 / "boom").
    assert "boom" in render["error"]
    assert "orphan daemon remains" not in render["error"]
    # The cleanup failure still survives — appended to details, not clobbering .error.
    assert render["details"]["cleanup"] == "failed"
    assert "orphan daemon remains" in render["details"]["cleanup_error"]


def test_acquire_public_url_degrades_when_close_leaves_dirty_runtime(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "agent-browser").write_text(
        "#!/bin/sh\ncase \"$*\" in\n"
        "  *\"get text body\"*) printf 'rendered target proof from browser\\n' ;;\n"
        "  *) exit 0 ;;\nesac\n",
        encoding="utf-8",
    )
    (bin_dir / "agent-browser").chmod(0o755)
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "agent_browser_runtime_guard.py").write_text(
        "#!/usr/bin/env python3\nimport sys\nprint('orphan daemon remains', file=sys.stderr)\nsys.exit(1)\n",
        encoding="utf-8",
    )
    direct = tmp_path / "direct.html"
    direct.write_text("<html><body><div id=\"root\"></div></body></html>", encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    result = _run_acquire(
        "--url", "https://example.com/app",
        "--repo-root", str(repo),
        "--direct-response-file", str(direct),
        "--expect-text", "target proof",
        "--browser-mode", "auto",
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["disposition"] == "degraded"
    attempt = next(attempt for attempt in payload["attempts"] if attempt["stage_id"] == "agent-browser-render-recon")
    assert attempt["status"] == "error"
    assert attempt["details"]["cleanup"] == "failed"
    assert "orphan daemon remains" in attempt["error"]


@pytest.mark.boundary_contract(
    reason="SIGTERM must reach the standalone fetch process during a browser stage"
)
def test_acquire_closes_session_on_sigterm_mid_render(tmp_path: Path) -> None:
    # #371 Tier 1: a host SIGTERM mid-browser-stage must still close the live
    # agent-browser session (best-effort) instead of leaking the daemon.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    (bin_dir / "agent-browser").write_text(
        "#!/bin/sh\n"
        f'printf "%s\\n" "$*" >> "{log}"\n'
        'case "$*" in\n'
        '  *" open "*) sleep 25 ;;\n'
        "  *) exit 0 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    (bin_dir / "agent-browser").chmod(0o755)
    direct = tmp_path / "direct.html"
    direct.write_text(SPA_HTML, encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS"] = "1"
    proc = subprocess.Popen(
        [
            sys.executable,
            str(WEB_FETCH_SCRIPTS / "acquire_public_url.py"),
            "--url", "https://example.com/app",
            "--repo-root", str(ROOT),
            "--direct-response-file", str(direct),
            "--expect-text", "target proof",
            "--browser-mode", "auto",
        ],
        cwd=tmp_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        # WAIT ON PROCESS STATE, NOT ON WALL TIME. The bar here used to be a 10s
        # deadline, which measures the MACHINE rather than the behavior under test:
        # everything before the `open` call -- interpreter startup, imports, the
        # direct-response stage -- is unbounded work whose duration is set by how
        # many xdist workers happen to be scheduled beside this test. Under the full
        # parallel lane it exceeded 10s and the suite went red on a green tree, which
        # is the same class `#668` carries for the pytest budget.
        #
        # The real failure this test must catch is "the child reached the browser
        # stage and never opened a session", and that is observable WITHOUT a clock:
        # the child would have exited. So the loop breaks on the log line, fails
        # IMMEDIATELY and distinguishably when the child exits without one -- with
        # the child's own output, which the wall-clock form never captured -- and
        # keeps waiting for as long as the child is alive and therefore still
        # progressing.
        #
        # BLIND CLASS, stated because the remaining bound is still a clock: the
        # `_HANG_BACKSTOP_SECONDS` cap cannot distinguish a genuinely hung child from
        # a machine slow enough to need more than two minutes to reach the `open`
        # call. It is sized as a hang backstop, not as the bar -- an order of
        # magnitude above the observed startup cost -- so tripping it is a signal to
        # investigate a hang, never a routine load artifact. It does not make the
        # test load-independent; it makes the load-dependent arm rare and legible
        # instead of common and silent.
        deadline = time.monotonic() + _HANG_BACKSTOP_SECONDS
        while time.monotonic() < deadline:
            if log.is_file() and any(" open " in line for line in log.read_text(encoding="utf-8").splitlines()):
                break
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                raise AssertionError(
                    "acquire_public_url exited before the fake agent-browser logged an open call "
                    f"(returncode {proc.returncode}); log: "
                    + (log.read_text(encoding="utf-8") if log.is_file() else "<no log>")
                    + f"\nstdout:\n{stdout}\nstderr:\n{stderr}"
                )
            time.sleep(0.05)
        else:
            raise AssertionError(
                f"fake agent-browser never logged an open call within the {_HANG_BACKSTOP_SECONDS}s "
                "hang backstop while the child stayed alive: "
                + (log.read_text(encoding="utf-8") if log.is_file() else "<no log>")
            )
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=30)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
    assert proc.returncode in (-signal.SIGTERM, 128 + signal.SIGTERM), proc.returncode
    assert _close_was_attempted(log), log.read_text(encoding="utf-8") if log.is_file() else "no log"


def test_teardown_no_session_is_idempotent_noop(monkeypatch) -> None:
    _ACQUIRE._clear_live_session()

    def _must_not_be_called(*_args, **_kwargs):
        raise AssertionError("_close_cleanup_error must not run when no session is registered")

    monkeypatch.setattr(_ACQUIRE.browser_fallback_stages, "_close_cleanup_error", _must_not_be_called)
    _ACQUIRE._teardown_live_session()
    _ACQUIRE._teardown_live_session()

    calls: list[object] = []

    def _recorder(*args, **kwargs):
        calls.append((args, kwargs))
        return None

    monkeypatch.setattr(_ACQUIRE.browser_fallback_stages, "_close_cleanup_error", _recorder)
    _ACQUIRE._register_live_session(SimpleNamespace(url="https://example.com/app", timeout=20, repo_root=ROOT))
    _ACQUIRE._teardown_live_session()
    _ACQUIRE._teardown_live_session()
    assert len(calls) == 1


def test_signal_handler_runs_teardown_then_reraises_default(monkeypatch) -> None:
    # In-process pin of the handler body: teardown fires first, then SIG_DFL is
    # restored and the signal re-raised so the exit disposition is unchanged.
    calls: list[object] = []
    monkeypatch.setattr(
        _ACQUIRE.browser_fallback_stages, "_close_cleanup_error",
        lambda *args, **kwargs: calls.append("close"),
    )
    monkeypatch.setattr(_ACQUIRE.signal, "signal", lambda signum, action: calls.append(("sig", signum, action)))
    monkeypatch.setattr(_ACQUIRE.os, "kill", lambda pid, signum: calls.append(("kill", signum)))
    _ACQUIRE._register_live_session(SimpleNamespace(url="https://example.com/app", timeout=20, repo_root=ROOT))

    _ACQUIRE._handle_teardown_signal(signal.SIGTERM, None)

    assert calls == [
        "close",
        ("sig", signal.SIGTERM, signal.SIG_DFL),
        ("kill", signal.SIGTERM),
    ]


def test_teardown_swallows_close_errors(monkeypatch) -> None:
    # never-raises contract: a failing close chain must not escape the handler.
    def _boom(*_args, **_kwargs):
        raise RuntimeError("close chain failed")

    monkeypatch.setattr(_ACQUIRE.browser_fallback_stages, "_close_cleanup_error", _boom)
    _ACQUIRE._register_live_session(SimpleNamespace(url="https://example.com/app", timeout=20, repo_root=ROOT))
    _ACQUIRE._teardown_live_session()
    assert _ACQUIRE._LIVE_BROWSER_SESSION is None
