from __future__ import annotations

from pathlib import Path

import install_machine_local as install_lib

from tests.charness_cli.test_managed_install import load_charness_module


def test_detect_hosts_includes_grok(monkeypatch) -> None:
    monkeypatch.setattr(install_lib.shutil, "which", lambda name: "/usr/bin/grok" if name == "grok" else None)
    assert install_lib.detect_hosts() == {"codex": False, "claude": False, "grok": True}


def test_default_grok_plugin_root_is_user_plugin_dir(tmp_path: Path) -> None:
    assert install_lib.default_grok_plugin_root(tmp_path, "charness") == tmp_path / ".grok" / "plugins" / "charness"


def test_ensure_grok_plugin_copies_exported_tree(tmp_path: Path) -> None:
    module = load_charness_module("charness_grok_plugin_install_under_test")
    home = tmp_path / "home"
    source = tmp_path / "exported"
    source.mkdir()
    (source / "skills").mkdir()
    (source / "skills" / "setup").mkdir()
    (source / "skills" / "setup" / "SKILL.md").write_text("# setup\n", encoding="utf-8")

    actions, message = module.ensure_grok_plugin(home_root=home, plugin_root=source)
    dest = home / ".grok" / "plugins" / "charness"
    assert actions == ["grok_plugin_installed"]
    assert dest.joinpath("skills", "setup", "SKILL.md").is_file()
    assert "marketplace" not in message.lower() or "do not add a marketplace" in message.lower()

    (source / "skills" / "setup" / "SKILL.md").write_text("# setup v2\n", encoding="utf-8")
    actions, _message = module.ensure_grok_plugin(home_root=home, plugin_root=source)
    assert actions == ["grok_plugin_updated"]
    assert dest.joinpath("skills", "setup", "SKILL.md").read_text(encoding="utf-8") == "# setup v2\n"


def test_ensure_grok_plugin_skips_missing_source(tmp_path: Path) -> None:
    module = load_charness_module("charness_grok_plugin_skip_under_test")
    actions, message = module.ensure_grok_plugin(home_root=tmp_path / "home", plugin_root=tmp_path / "missing")
    assert actions == []
    assert "skipped" in message.lower()


def test_build_grok_host_guidance_reports_missing_and_present(tmp_path: Path) -> None:
    module = load_charness_module("charness_grok_guidance_under_test")
    missing = module.build_grok_host_guidance(grok_available=True, grok_plugin_root=tmp_path / "absent")
    assert missing["status"] == "needs-install"
    assert missing["manual_action_required"] is False
    assert "[plugins].enabled" in missing["message"]
    assert "marketplace" in missing["message"]

    present_root = tmp_path / "present"
    present_root.mkdir()
    present = module.build_grok_host_guidance(grok_available=True, grok_plugin_root=present_root)
    assert present["status"] == "installed"
    assert present["manual_action_required"] is False
    assert "[plugins].enabled" in present["message"]
    assert "marketplace" in present["message"]

    unavailable = module.build_grok_host_guidance(grok_available=False, grok_plugin_root=present_root)
    assert unavailable["status"] == "unavailable"


def test_build_host_next_steps_includes_grok() -> None:
    module = load_charness_module("charness_grok_next_steps_under_test")
    steps = module.build_host_next_steps(
        {
            "codex_host_guidance": {"message": "restart codex"},
            "claude_host_guidance": {},
            "grok_host_guidance": {"message": "restart grok"},
        }
    )
    assert steps == {"codex": "restart codex", "grok": "restart grok"}


def test_remove_grok_plugin_deletes_user_plugin_dir(tmp_path: Path) -> None:
    module = load_charness_module("charness_grok_plugin_remove_under_test")
    dest = tmp_path / ".grok" / "plugins" / "charness"
    dest.mkdir(parents=True)
    (dest / "README.md").write_text("x\n", encoding="utf-8")
    assert module.remove_grok_plugin(home_root=tmp_path) is True
    assert not dest.exists()
    assert module.remove_grok_plugin(home_root=tmp_path) is False
