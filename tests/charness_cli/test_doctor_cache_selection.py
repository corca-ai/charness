from __future__ import annotations

import json
from pathlib import Path

from .support import build_test_path, clone_seeded_managed_home, make_fake_codex, run_cli
from .test_managed_install import CURRENT_VERSION


def test_doctor_prefers_enabled_cache_matching_source_version(tmp_path: Path, seeded_managed_home: dict[str, Path]) -> None:
    home_root, env = clone_seeded_managed_home(tmp_path, seeded_managed_home["home_root"])
    fake_codex = make_fake_codex(tmp_path)
    env["PATH"] = build_test_path(fake_codex.parent)
    config_path = home_root / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        """[plugins."charness@charness"]
enabled = true

[plugins."charness@local"]
enabled = true
""",
        encoding="utf-8",
    )

    stale_cache = home_root / ".codex" / "plugins" / "cache" / "charness" / "charness" / "0.0.0-dev" / ".codex-plugin" / "plugin.json"
    stale_cache.parent.mkdir(parents=True, exist_ok=True)
    stale_cache.write_text('{"version":"0.0.0-dev"}', encoding="utf-8")

    current_cache = home_root / ".codex" / "plugins" / "cache" / "local" / "charness" / CURRENT_VERSION / ".codex-plugin" / "plugin.json"
    current_cache.parent.mkdir(parents=True, exist_ok=True)
    current_cache.write_text(json.dumps({"version": CURRENT_VERSION}), encoding="utf-8")

    doctor_result = run_cli("doctor", "--home-root", str(home_root), "--json", env=env)
    assert doctor_result.returncode == 0, doctor_result.stderr
    payload = json.loads(doctor_result.stdout)
    assert payload["codex_enabled_plugin_ids"] == ["charness@charness", "charness@local"]
    assert payload["codex_enabled_plugin_id"] == "charness@local"
    assert payload["codex_cache_manifest_version"] == CURRENT_VERSION
    assert payload["codex_source_cache_drift"] is False
    assert payload["codex_host_guidance"]["status"] == "installed"
    assert "Extra stale enabled cache entries remain" in payload["codex_host_guidance"]["message"]
