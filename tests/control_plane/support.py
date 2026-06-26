from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]


def run_script(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    if env is None:
        env = os.environ.copy()
    env.setdefault("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    return subprocess.run(
        ["python3", *args],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def run_loaded_script_main(
    script_name: str,
    module: object,
    *args: str,
    env: dict[str, str] | None = None,
) -> SimpleNamespace:
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    saved_env = os.environ.copy()
    sys.argv = [script_name, *args]
    if env is not None:
        os.environ.clear()
        os.environ.update(env)
    os.environ.setdefault("CHARNESS_DISABLE_PLUGIN_FALLBACK_MANIFESTS", "1")
    returncode = 0
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                returncode = module.main() or 0
            except SystemExit as exc:
                if isinstance(exc.code, int):
                    returncode = exc.code
                elif exc.code is None:
                    returncode = 0
                else:
                    returncode = 1
                    print(str(exc.code), file=sys.stderr)
            except Exception as exc:
                if exc.__class__.__name__ != "ValidationError":
                    raise
                returncode = 1
                print(str(exc), file=sys.stderr)
    finally:
        sys.argv = saved_argv
        os.environ.clear()
        os.environ.update(saved_env)
    return SimpleNamespace(returncode=returncode, stdout=out.getvalue(), stderr=err.getvalue())


def seed_control_plane_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    tools_dir = repo / "integrations" / "tools"
    locks_dir = repo / "integrations" / "locks"
    generated_dir = repo / "skills" / "support" / "generated"
    bin_dir = repo / "bin"
    tools_dir.mkdir(parents=True)
    locks_dir.mkdir(parents=True)
    generated_dir.mkdir(parents=True)
    bin_dir.mkdir(parents=True)
    (repo / ".demo-ready").write_text("ready\n", encoding="utf-8")

    (tools_dir / "manifest.schema.json").write_text(
        (ROOT / "integrations" / "tools" / "manifest.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (bin_dir / "demo-tool").write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'case "${1:-}" in',
                '  version) echo "demo-tool 1.2.3" ;;',
                '  help) echo "demo-tool help" ;;',
                '  update) echo "updated" ;;',
                '  *) echo "demo-tool" ;;',
                "esac",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bin_dir / "demo-tool").chmod(0o755)
    (tools_dir / "demo-tool.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "tool_id": "demo-tool",
                "kind": "external_binary_with_skill",
                "display_name": "demo-tool",
                "upstream_repo": "example/demo-tool",
                "homepage": "https://example.com/demo-tool",
                "lifecycle": {
                    "install": {
                        "mode": "manual",
                        "install_url": "https://example.com/demo-tool/install",
                    },
                    "update": {"mode": "script", "commands": ["./bin/demo-tool update"]},
                },
                "checks": {
                    "detect": {"commands": ["./bin/demo-tool version"], "success_criteria": ["exit_code:0", "stdout_contains:1.2.3"]},
                    "healthcheck": {"commands": ["./bin/demo-tool help"], "success_criteria": ["exit_code:0", "stdout_contains:help"]},
                },
                "access_modes": ["binary", "degraded"],
                "readiness_checks": [
                    {
                        "check_id": "demo-ready-file",
                        "summary": "Repo readiness marker exists.",
                        "commands": ["test -f .demo-ready"],
                        "success_criteria": ["exit_code:0"],
                        "failure_hint": "Run the setup step that writes .demo-ready before relying on demo-tool.",
                    }
                ],
                "version_expectation": {"policy": "minimum", "constraint": ">=1.0.0", "detected_by": "stdout"},
                "support_skill_source": {
                    "source_type": "local_wrapper",
                    "path": "docs/demo-tool-upstream.md",
                    "ref": "main",
                    "wrapper_skill_id": "demo-tool-wrapper",
                },
                "degradation": {"when_missing": ["manual fallback"]},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return repo
