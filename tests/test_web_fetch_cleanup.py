from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
