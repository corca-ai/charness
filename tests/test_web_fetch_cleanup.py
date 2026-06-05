from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from tests.repo_copy import REPO_COPY_IGNORE

ROOT = Path(__file__).resolve().parents[1]
WEB_FETCH_SCRIPTS = ROOT / "skills" / "support" / "web-fetch" / "scripts"
GATHER_SCRIPTS = ROOT / "skills" / "public" / "gather" / "scripts"
SPA_HTML = "<html><body><div id=\"root\"></div></body></html>"


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
    result = subprocess.run(
        [
            sys.executable,
            str(WEB_FETCH_SCRIPTS / "acquire_public_url.py"),
            "--url", "https://example.com/app",
            "--direct-response-file", str(direct),
            "--expect-text", "target proof",
            "--browser-mode", "auto",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
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
    result = subprocess.run(
        [
            sys.executable,
            str(WEB_FETCH_SCRIPTS / "acquire_public_url.py"),
            "--url", "https://example.com/app",
            "--direct-response-file", str(direct),
            "--expect-text", "target proof",
            "--browser-mode", "auto",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    # Render failed, but the session must still be closed via the finally block.
    assert _close_was_attempted(log), log.read_text(encoding="utf-8") if log.is_file() else "no log"
    render = next(a for a in payload["attempts"] if a["stage_id"] == "agent-browser-render-recon")
    assert render["error"]


def test_acquire_guard_unavailable_is_fail_visible(tmp_path: Path) -> None:
    # In a layout where the runtime guard is not reachable from repo_root/scripts
    # or any ancestor of the acquire helper, a skipped post-close proof must be
    # surfaced as `guard_unavailable` degraded, never as a clean success (#302).
    iso = tmp_path / "iso" / "webfetch"
    shutil.copytree(WEB_FETCH_SCRIPTS, iso, ignore=REPO_COPY_IGNORE)
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
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "degraded"
    assert _close_was_attempted(log)
    render = next(a for a in payload["attempts"] if a["stage_id"] == "agent-browser-render-recon")
    assert "guard_unavailable" in render["error"]
    assert render["details"]["cleanup"] == "failed"


def test_gather_reaches_acquire_and_bundled_guard_in_exported_layout(tmp_path: Path) -> None:
    # #302: from an exported/installed plugin layout (skills/gather + support/web-fetch
    # + bundled scripts/guard) and an arbitrary user repo_root, gather must reach the
    # support web-fetch impl AND run the bundled cleanup proof — not silently skip it.
    plugin = tmp_path / "plugin"
    (plugin / "skills" / "gather").mkdir(parents=True)
    (plugin / "scripts").mkdir(parents=True)
    shutil.copytree(GATHER_SCRIPTS, plugin / "skills" / "gather" / "scripts", ignore=REPO_COPY_IGNORE)
    shutil.copytree(WEB_FETCH_SCRIPTS, plugin / "support" / "web-fetch" / "scripts", ignore=REPO_COPY_IGNORE)
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
    payload = json.loads(result.stdout)
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
    result = subprocess.run(
        [
            sys.executable,
            "skills/support/web-fetch/scripts/acquire_public_url.py",
            "--url", "https://example.com/app",
            "--direct-response-file", str(direct),
            "--expect-text", "target proof",
            "--browser-mode", "auto",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "degraded"
    attempt = next(attempt for attempt in payload["attempts"] if attempt["stage_id"] == "agent-browser-render-recon")
    assert attempt["status"] == "error"
    assert attempt["details"]["cleanup"] == "failed"


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

    result = subprocess.run(
        [
            sys.executable,
            "skills/support/web-fetch/scripts/acquire_public_url.py",
            "--url", "https://example.com/app",
            "--repo-root", str(repo),
            "--direct-response-file", str(direct),
            "--expect-text", "target proof",
            "--browser-mode", "auto",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["disposition"] == "degraded"
    attempt = next(attempt for attempt in payload["attempts"] if attempt["stage_id"] == "agent-browser-render-recon")
    assert attempt["status"] == "error"
    assert attempt["details"]["cleanup"] == "failed"
    assert "orphan daemon remains" in attempt["error"]
