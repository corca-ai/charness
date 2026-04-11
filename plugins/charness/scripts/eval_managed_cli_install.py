from __future__ import annotations

import json
from pathlib import Path


def run_managed_cli_install(
    root: Path,
    *,
    run_command,
    expect_success,
    error_type,
) -> None:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="charness-eval-managed-home-") as tmpdir:
        home_root = Path(tmpdir)
        init_result = run_command(
            ["python3", "charness", "init", "--home-root", str(home_root), "--repo-root", str(root)],
            cwd=root,
        )
        expect_success(init_result, "managed cli init")
        init_payload = json.loads(init_result.stdout)
        plugin_root = home_root / ".codex" / "plugins" / "charness"
        marketplace_path = home_root / ".agents" / "plugins" / "marketplace.json"
        cli_path = home_root / ".local" / "bin" / "charness"
        claude_wrapper_path = home_root / ".local" / "bin" / "claude-charness"
        for path, label in (
            (plugin_root, "managed plugin root"),
            (marketplace_path, "managed codex marketplace"),
            (cli_path, "managed cli binary"),
            (claude_wrapper_path, "managed claude wrapper"),
        ):
            if not path.exists():
                raise error_type(f"managed cli init: missing {label}")
        if init_payload.get("plugin_root") != str(plugin_root):
            raise error_type(f"managed cli init: unexpected plugin_root {init_payload.get('plugin_root')!r}")
        expected_next_step = (
            "Restart Codex from the home root so it reloads the personal marketplace. "
            "If `charness` is still unavailable, install or enable it from Plugin Directory."
        )
        if init_payload.get("next_steps", {}).get("codex") != expected_next_step:
            raise error_type(f"managed cli init: unexpected Codex next step {init_payload!r}")
        doctor_result = run_command(
            ["python3", str(cli_path), "doctor", "--home-root", str(home_root), "--repo-root", str(root), "--json"],
            cwd=root,
        )
        expect_success(doctor_result, "managed cli doctor")
        doctor_payload = json.loads(doctor_result.stdout)
        if doctor_payload.get("plugin_root_present") is not True:
            raise error_type(f"managed cli doctor: unexpected plugin_root state {doctor_payload!r}")
        entry = doctor_payload.get("codex_marketplace_entry")
        if not isinstance(entry, dict):
            raise error_type(f"managed cli doctor: missing codex marketplace entry {doctor_payload!r}")
        source = entry.get("source", {})
        if not isinstance(source, dict) or source.get("path") != "./.codex/plugins/charness":
            raise error_type(f"managed cli doctor: unexpected codex source path {entry!r}")
        if doctor_payload.get("claude_wrapper_present") is not True:
            raise error_type(f"managed cli doctor: missing Claude wrapper {doctor_payload!r}")
        host_guidance = doctor_payload.get("codex_host_guidance")
        if not isinstance(host_guidance, dict) or host_guidance.get("status") != "needs-host-install":
            raise error_type(f"managed cli doctor: unexpected Codex host guidance {doctor_payload!r}")
        expected_guidance = (
            "Restart Codex from the home directory that owns "
            f"`{marketplace_path}`. If `charness` is still not available, open Plugin Directory and install or enable the local `charness` entry."
        )
        if host_guidance.get("message") != expected_guidance:
            raise error_type(f"managed cli doctor: unexpected Codex guidance message {doctor_payload!r}")
