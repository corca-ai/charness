from __future__ import annotations

import json
from pathlib import Path

import scripts.capability_catalog_sources as sources
from scripts.capability_catalog import list_catalog, refresh_catalog
from scripts.capability_catalog_resolver import resolve_skill_path


def test_catalog_refresh_is_read_only_for_list_and_noop_on_second_refresh(tmp_path: Path) -> None:
    listed = list_catalog(tmp_path)
    assert listed["artifacts"]["mode"] == "read-only"
    assert not (tmp_path / "charness-artifacts").exists()
    first = refresh_catalog(tmp_path)
    second = refresh_catalog(tmp_path)
    assert first["artifacts"]["updated"] is True
    assert second["artifacts"]["updated"] is False
    payload = json.loads((tmp_path / "charness-artifacts/capability-catalog/latest.json").read_text())
    assert payload["artifact_kind"] == "capability-catalog"


def test_catalog_resolver_recovers_rotated_cache(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    cache = home / ".codex/plugins/cache/local/charness/2.0.0/skills/impl"
    cache.mkdir(parents=True)
    (cache / "SKILL.md").write_text("# impl\n")
    payload = resolve_skill_path(
        skill_id="impl",
        repo_root=repo,
        home=home,
        codex_home=home / ".codex",
        reported_path=home / ".codex/plugins/cache/local/charness/1.0.0/skills/impl/SKILL.md",
    )
    assert payload["status"] == "stale-reported-path"
    assert payload["resolved_source"] == "codex-versioned-cache"


def test_catalog_preserves_sanitized_provider_metadata(monkeypatch, tmp_path: Path) -> None:
    manifest = {
        "tool_id": "github-gh",
        "kind": "external_binary_with_skill",
        "summary": "Use `gh` with SLACK_BOT_TOKEN",
        "access_modes": [],
        "support_skill_source": None,
        "capability_requirements": {},
        "config_layers": [],
        "readiness_checks": [],
        "supports_public_skills": ["gather"],
        "intent_triggers": ["GitHub URL"],
        "strong_intent_triggers": ["GitHub URL"],
        "recommendation_role": "runtime",
        "_manifest_path": "integrations/tools/github-gh.json",
        "_manifest_origin": "user-repo",
    }
    monkeypatch.setattr(sources, "load_manifests_for_discovery", lambda _root: [manifest])
    monkeypatch.setattr(sources, "support_state_for_manifest", lambda _data: "integration-only")
    item = sources.integrations(tmp_path)[0]
    assert item["id"] == "github-worker"
    assert item["intent_triggers"] == ["GitHub URL"]
    assert item["strong_intent_triggers"] == ["GitHub URL"]
    assert item["recommendation_role"] == "runtime"
    assert "github-gh" not in json.dumps(item)


def test_catalog_scans_exported_plugin_layout_and_trusted_roots(tmp_path: Path) -> None:
    consumer = tmp_path / "consumer"
    exported = tmp_path / "plugin"
    trusted = consumer / "vendor" / "skills"
    for root, name in ((exported / "skills", "plugin-skill"), (trusted, "trusted-skill")):
        skill = root / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: %s\ndescription: test\n---\n" % name)
    exported_entries = sources._skill_entries(
        [("installed-plugin-public", exported / "skills")],
        repo_root=consumer,
        layer="public skill",
    )
    trusted_entries = sources._skill_entries(
        [("trusted-root-1", trusted)], repo_root=consumer, layer="trusted skill"
    )
    assert exported_entries[0]["source"] == "installed-plugin-public"
    assert exported_entries[0]["id"] == "plugin-skill"
    assert trusted_entries[0]["id"] == "trusted-skill"


def test_catalog_inventory_excludes_removed_public_router(tmp_path: Path) -> None:
    payload = list_catalog(tmp_path)["inventory"]
    assert all(item["id"] != "find-skills" for item in payload["public_skills"])


def test_catalog_lists_local_and_synced_support_skills(tmp_path: Path) -> None:
    local = tmp_path / "skills" / "support" / "local-helper"
    synced = tmp_path / "skills" / "support" / "generated" / "synced-helper"
    for skill in (local, synced):
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: %s\ndescription: test\n---\n" % skill.parent.name)
    entries = list_catalog(tmp_path)["inventory"]["support_skills"]
    by_id = {item["id"]: item for item in entries}
    assert by_id["local-helper"]["layer"] == "support skill"
    assert by_id["synced-helper"]["layer"] == "synced support skill"


def test_catalog_prefers_canonical_adapter_and_warns_on_legacy(tmp_path: Path) -> None:
    agents = tmp_path / ".agents"
    agents.mkdir()
    (agents / "find-skills-adapter.yaml").write_text("trusted_skill_roots: []\n")
    legacy = sources.load_adapter(tmp_path)
    assert legacy["path"] == ".agents/find-skills-adapter.yaml"
    assert any("legacy find-skills adapter" in warning for warning in legacy["warnings"])
    (agents / "capability-catalog-adapter.yaml").write_text("trusted_skill_roots: []\n")
    canonical = sources.load_adapter(tmp_path)
    assert canonical["path"] == ".agents/capability-catalog-adapter.yaml"
    assert not any("legacy find-skills adapter" in warning for warning in canonical["warnings"])
