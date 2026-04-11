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
        plugin_root = home_root / ".agents" / "plugins" / "charness"
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
        if not isinstance(source, dict) or source.get("path") != "./.agents/plugins/charness":
            raise error_type(f"managed cli doctor: unexpected codex source path {entry!r}")
        if doctor_payload.get("claude_wrapper_present") is not True:
            raise error_type(f"managed cli doctor: missing Claude wrapper {doctor_payload!r}")
