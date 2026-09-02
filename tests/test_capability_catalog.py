from __future__ import annotations

import json
import runpy
import shutil
import sys
from pathlib import Path

import pytest
import yaml

# provenance-contract fixture: skill_manifest_selection
import scripts.adapters.capability_catalog as catalog
import scripts.adapters.capability_catalog_sources as sources
from scripts.adapters.capability_catalog import (
    CatalogRepoRootError,
    _repo_root,
    list_catalog,
    refresh_catalog,
    summarize_catalog,
)
from scripts.adapters.capability_catalog import main as catalog_main
from scripts.adapters.capability_catalog_artifact import persist_catalog
from scripts.adapters.capability_catalog_resolver import _cache_candidates, resolve_skill_path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _current_plugin_version() -> str:
    manifest = REPO_ROOT / "plugins/charness/.codex-plugin/plugin.json"
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def test_catalog_refresh_is_read_only_for_list_and_noop_on_second_refresh(tmp_path: Path) -> None:
    listed = list_catalog(tmp_path)
    assert listed["artifacts"]["mode"] == "read-only"
    assert not (tmp_path / "charness-artifacts").exists()
    first = refresh_catalog(tmp_path)
    second = refresh_catalog(tmp_path)
    assert first["artifacts"]["updated"] is True
    assert second["artifacts"]["updated"] is False
    payload = json.loads(
        (tmp_path / "charness-artifacts/capability-catalog/latest.json").read_text()
    )
    assert payload["artifact_kind"] == "capability-catalog"


def test_catalog_summary_keeps_hidden_inventory_and_omits_public_skill_detail() -> None:
    payload = {
        "inventory": {
            "adapter": {"valid": True, "warnings": ["fallback"]},
            "public_skills": [{"id": "quality", "description": "long prompt"}],
            "support_skills": [
                {"id": "web-fetch", "summary": "fetch", "path": "support.md", "description": "omit"}
            ],
            "support_capabilities": [
                {
                    "id": "fetch",
                    "summary": "route",
                    "path": "cap.json",
                    "support_skill_path": "support.md",
                    "readiness_checks": ["omit"],
                }
            ],
            "integrations": [
                {
                    "id": "gh",
                    "summary": "github",
                    "path": "gh.json",
                    "support_state": "ready",
                    "support_skill_path": None,
                    "config_layers": ["omit"],
                }
            ],
            "trusted_skills": [
                {"id": "local", "summary": "trusted", "path": "local.md", "description": "omit"}
            ],
        },
        "artifacts": {"mode": "read-only"},
    }

    summary = summarize_catalog(payload)

    assert summary["inventory"]["counts"] == {
        "public_skills": 1,
        "support_skills": 1,
        "support_capabilities": 1,
        "integrations": 1,
        "trusted_skills": 1,
    }
    assert summary["inventory"]["support_skills"] == [
        {"id": "web-fetch", "summary": "fetch", "path": "support.md"}
    ]
    assert summary["inventory"]["support_capabilities"] == [
        {"id": "fetch", "summary": "route", "path": "cap.json", "support_skill_path": "support.md"}
    ]
    assert summary["inventory"]["integrations"] == [
        {
            "id": "gh",
            "summary": "github",
            "path": "gh.json",
            "support_state": "ready",
            "support_skill_path": None,
        }
    ]
    assert summary["inventory"]["trusted_skills"] == [
        {"id": "local", "summary": "trusted", "path": "local.md"}
    ]
    serialized = json.dumps(summary)
    assert "long prompt" not in serialized
    assert "readiness_checks" not in serialized
    assert "config_layers" not in serialized


def test_catalog_summary_treats_non_list_inventory_layers_as_empty() -> None:
    summary = summarize_catalog(
        {
            "inventory": {
                "support_skills": {"id": "invalid-shape"},
                "support_capabilities": None,
                "integrations": "invalid-shape",
                "trusted_skills": 1,
            }
        }
    )

    assert summary["inventory"]["counts"] == {
        "public_skills": 0,
        "support_skills": 0,
        "support_capabilities": 0,
        "integrations": 0,
        "trusted_skills": 0,
    }
    assert summary["inventory"]["support_skills"] == []
    assert summary["inventory"]["support_capabilities"] == []
    assert summary["inventory"]["integrations"] == []
    assert summary["inventory"]["trusted_skills"] == []


def test_catalog_refresh_rejects_missing_root_without_creating_it(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(CatalogRepoRootError, match="does not exist"):
        refresh_catalog(missing)
    assert not missing.exists()


def test_catalog_refresh_rejects_file_root(tmp_path: Path) -> None:
    file_root = tmp_path / "repo-file"
    file_root.write_text("not a directory\n", encoding="utf-8")
    with pytest.raises(CatalogRepoRootError, match="not a directory"):
        refresh_catalog(file_root)


def test_catalog_resolver_recovers_rotated_cache(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    version = _current_plugin_version()
    cache = home / f".codex/plugins/cache/local/charness/{version}/skills/impl"
    cache.mkdir(parents=True)
    source = REPO_ROOT / "skills/public/impl/SKILL.md"
    (cache / "SKILL.md").write_bytes(source.read_bytes())
    payload = resolve_skill_path(
        skill_id="impl",
        repo_root=repo,
        home=home,
        codex_home=home / ".codex",
        reported_path=home / ".codex/plugins/cache/local/charness/1.0.0/skills/impl/SKILL.md",
    )
    assert payload["status"] == "stale-reported-path"
    assert payload["resolved_source"] == "codex-versioned-cache"
    assert payload["admission_status"] == "admitted"
    assert payload["expectation"]["version"] == version


def test_catalog_resolver_refuses_existing_same_version_content_mismatch(tmp_path: Path) -> None:
    version = _current_plugin_version()
    cache = tmp_path / f"home/.codex/plugins/cache/local/charness/{version}/skills/impl"
    cache.mkdir(parents=True)
    (cache / "SKILL.md").write_text("stale bytes\n", encoding="utf-8")
    payload = resolve_skill_path(
        skill_id="impl",
        repo_root=tmp_path / "repo",
        home=tmp_path / "home",
        codex_home=tmp_path / "home/.codex",
        reported_path=cache / "SKILL.md",
    )
    assert payload["status"] == "mismatch"
    assert payload["admission_status"] == "refused"
    assert payload["reason_code"] == "skill-content-mismatch"
    assert payload["resolved_path"] is None
    assert payload["recovery"]["kind"] == "refresh-plugin-install"


def test_catalog_resolver_refuses_valid_plus_malformed_manifest(monkeypatch, tmp_path: Path) -> None:
    owner = tmp_path / "owner"
    plugin = owner / "plugins/charness"
    (plugin / ".codex-plugin").mkdir(parents=True)
    (owner / ".codex-plugin").mkdir(parents=True)
    (owner / "skills/public/impl").mkdir(parents=True)
    (plugin / ".codex-plugin/plugin.json").write_text('{"version":"1.0.0"}\n', encoding="utf-8")
    (owner / ".codex-plugin/plugin.json").write_text("{broken\n", encoding="utf-8")
    (owner / "skills/public/impl/SKILL.md").write_text("skill\n", encoding="utf-8")
    monkeypatch.setattr("scripts.adapters.capability_catalog_resolver._owner_root", lambda: owner)
    payload = resolve_skill_path(
        skill_id="impl",
        repo_root=owner,
        home=tmp_path / "home",
        codex_home=tmp_path / "home/.codex",
        reported_path=None,
    )
    assert payload["admission_status"] == "refused"
    assert payload["reason_code"] == "package-manifest-invalid"


def test_catalog_resolver_refuses_malformed_candidate_manifest(monkeypatch, tmp_path: Path) -> None:
    owner = tmp_path / "owner"
    plugin = owner / "plugins/charness"
    (plugin / ".codex-plugin").mkdir(parents=True)
    (owner / ".codex-plugin").mkdir(parents=True)
    source = owner / "skills/public/impl/SKILL.md"
    exported = plugin / "skills/impl/SKILL.md"
    source.parent.mkdir(parents=True)
    exported.parent.mkdir(parents=True)
    source.write_text("skill\n", encoding="utf-8")
    exported.write_text("skill\n", encoding="utf-8")
    (plugin / ".codex-plugin/plugin.json").write_text('{"version":"1.0.0"}\n', encoding="utf-8")
    (owner / ".codex-plugin/plugin.json").write_text('{"version":"1.0.0"}\n', encoding="utf-8")
    cache = tmp_path / "home/.codex/plugins/cache/local/charness/1.0.0/skills/impl"
    cache.mkdir(parents=True)
    (cache / "SKILL.md").write_text("skill\n", encoding="utf-8")
    (cache.parent.parent / ".codex-plugin").mkdir(parents=True)
    (cache.parent.parent / ".codex-plugin/plugin.json").write_bytes(b"\xff\xfe\x00")
    monkeypatch.setattr("scripts.adapters.capability_catalog_resolver._owner_root", lambda: owner)
    payload = resolve_skill_path(
        skill_id="impl",
        repo_root=owner,
        home=tmp_path / "home",
        codex_home=tmp_path / "home/.codex",
        reported_path=cache / "SKILL.md",
    )
    assert payload["admission_status"] == "refused"
    assert payload["reason_code"] == "package-manifest-invalid"


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


def test_catalog_lists_local_and_synced_support_skills(tmp_path: Path) -> None:
    local = tmp_path / "skills" / "support" / "local-helper"
    synced = tmp_path / "skills" / "support" / "generated" / "synced-helper"
    for skill in (local, synced):
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: %s\ndescription: test\n---\n" % skill.parent.name
        )
    entries = list_catalog(tmp_path)["inventory"]["support_skills"]
    by_id = {item["id"]: item for item in entries}
    assert by_id["local-helper"]["layer"] == "support skill"
    assert by_id["synced-helper"]["layer"] == "synced support skill"


def test_consumer_validator_catalog_resolves_installed_layout(tmp_path: Path, monkeypatch) -> None:
    installed = tmp_path / "installed"
    (installed / "scripts").mkdir(parents=True)
    monkeypatch.setattr(catalog, "__file__", str(installed / "scripts" / "capability_catalog.py"))
    captured: dict[str, object] = {}

    def fake_validate(owner_root: Path, **kwargs: object) -> dict[str, object]:
        captured.update(owner_root=owner_root, **kwargs)
        return {"status": "pass"}

    monkeypatch.setattr(catalog.check_consumer_validator_catalog, "validate_catalog", fake_validate)
    result = catalog._consumer_validator_catalog(installed)

    assert result == {"status": "pass"}
    assert captured["owner_root"] == installed
    assert captured["package_root"] == installed
    assert captured["catalog_path"] == installed / "skills/quality/references/consumer-validator-catalog.yaml"


def test_consumer_validator_catalog_maps_catalog_errors_to_blocked(monkeypatch) -> None:
    def fail_validate(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise catalog.check_consumer_validator_catalog.CatalogError("bad catalog")

    monkeypatch.setattr(catalog.check_consumer_validator_catalog, "validate_catalog", fail_validate)
    result = catalog._consumer_validator_catalog(Path(__file__).resolve().parents[1])

    assert result["status"] == "blocked"
    assert result["error"] == "bad catalog"


def test_catalog_cli_returns_nonzero_for_a_blocked_consumer_catalog(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        catalog,
        "list_catalog",
        lambda *_args, **_kwargs: {"consumer_validator_catalog": {"status": "blocked"}},
    )

    assert catalog_main(["list", "--repo-root", str(tmp_path)]) == 1
    assert "status: blocked" in capsys.readouterr().out


def test_catalog_loads_canonical_adapter(tmp_path: Path) -> None:
    agents = tmp_path / ".agents"
    agents.mkdir()
    (agents / "capability-catalog-adapter.yaml").write_text("trusted_skill_roots: []\n")
    canonical = sources.load_adapter(tmp_path)
    assert canonical["path"] == ".agents/capability-catalog-adapter.yaml"
    assert canonical["warnings"] == []


def test_catalog_cli_dispatches_all_commands_and_direct_script_bootstraps_path(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    adoption = repo / ".agents"
    adoption.mkdir()
    shutil.copy2(
        Path(__file__).resolve().parents[1]
        / ".agents"
        / "consumer-validator-adoption.yaml",
        adoption / "consumer-validator-adoption.yaml",
    )
    assert _repo_root(None) == Path.cwd().resolve()
    assert catalog_main(["list", "--repo-root", str(repo)]) == 0
    capsys.readouterr()
    assert catalog_main(["refresh", "--repo-root", str(repo)]) == 0
    capsys.readouterr()
    assert (
        catalog_main(
            [
                "resolve-skill-path",
                "--repo-root",
                str(repo),
                "--skill-id",
                "missing",
                "--reported-path",
                str(repo / "missing"),
            ]
        )
        == 1
    )
    capsys.readouterr()

    original_path = list(sys.path)
    repo_path = str(Path(__file__).resolve().parents[1])
    try:
        sys.path[:] = [entry for entry in sys.path if entry != repo_path]
        monkeypatch.setattr(
            sys, "argv", ["capability_catalog.py", "list", "--repo-root", str(repo)]
        )
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(
                str(Path(repo_path) / "scripts/adapters/capability_catalog.py"), run_name="__main__"
            )
        assert exc_info.value.code == 0
    finally:
        sys.path[:] = original_path
    assert "artifacts:" in capsys.readouterr().out


def test_catalog_direct_main_refresh_invalid_root_is_clean_and_nonzero(
    tmp_path: Path, capsys
) -> None:
    # The refusal used to be a bare stderr line, with the same text repeated as a
    # `--json` payload only when the flag was passed. It is one unconditional YAML
    # payload on stdout now, so the message is asserted there, and stderr must still
    # carry no traceback for either invalid-root shape.
    missing = tmp_path / "missing"
    assert catalog_main(["refresh", "--repo-root", str(missing)]) == 2
    output = capsys.readouterr()
    payload = yaml.safe_load(output.out)
    assert "does not exist" in payload["error"]
    assert payload["repo_root"] == str(missing.resolve())
    assert "Traceback" not in output.err
    assert not missing.exists()

    file_root = tmp_path / "refresh-file-root"
    file_root.write_text("not a directory\n", encoding="utf-8")
    assert catalog_main(["refresh", "--repo-root", str(file_root)]) == 2
    output = capsys.readouterr()
    payload = yaml.safe_load(output.out)
    assert "not a directory" in payload["error"]
    assert payload["repo_root"] == str(file_root.resolve())
    assert "Traceback" not in output.err


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["list"],
        ["refresh"],
        ["resolve-skill-path"],
        ["resolve-skill-path", "--skill-id", "impl", "--reported-path", "/tmp/old.md"],
        ["resolve-skill-path", "--repo-root", "/tmp/repo", "--reported-path", "/tmp/old.md"],
        ["resolve-skill-path", "--repo-root", "/tmp/repo", "--skill-id", "impl"],
    ],
)
def test_catalog_cli_rejects_missing_required_arguments(argv: list[str]) -> None:
    """Keep every argparse required guard observable to mutation testing."""
    with pytest.raises(SystemExit) as exc_info:
        catalog_main(argv)
    assert exc_info.value.code == 2


def test_catalog_cli_dispatches_to_the_selected_handler(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    seen: list[str] = []

    monkeypatch.setattr(
        catalog,
        "list_catalog",
        lambda _root, **_kwargs: seen.append("list") or {"command": "list"},
    )
    monkeypatch.setattr(
        catalog, "refresh_catalog", lambda _root: seen.append("refresh") or {"command": "refresh"}
    )
    monkeypatch.setattr(
        catalog,
        "resolve_skill_path",
        lambda **_kwargs: seen.append("resolve") or {"resolved_path": str(repo / "skill.md")},
    )

    assert catalog_main(["list", "--repo-root", str(repo)]) == 0
    assert yaml.safe_load(capsys.readouterr().out)["command"] == "list"
    assert catalog_main(["refresh", "--repo-root", str(repo)]) == 0
    assert yaml.safe_load(capsys.readouterr().out)["command"] == "refresh"
    assert (
        catalog_main(
            [
                "resolve-skill-path",
                "--repo-root",
                str(repo),
                "--skill-id",
                "impl",
                "--reported-path",
                str(repo / "old.md"),
            ]
        )
        == 0
    )
    assert yaml.safe_load(capsys.readouterr().out)["resolved_path"].endswith("skill.md")
    assert seen == ["list", "refresh", "resolve"]


def test_catalog_cli_summary_emits_compact_yaml(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(
        catalog,
        "list_catalog",
        lambda _root, **_kwargs: {
            "inventory": {
                "adapter": {"valid": True},
                "public_skills": [{"id": "quality", "description": "omit"}],
                "support_skills": [],
                "support_capabilities": [],
                "integrations": [],
                "trusted_skills": [],
            },
            "artifacts": {"mode": "read-only"},
        },
    )

    assert catalog_main(["list", "--repo-root", str(tmp_path), "--summary"]) == 0
    output = capsys.readouterr().out
    assert "counts:" in output
    assert "description" not in output


@pytest.mark.parametrize(
    "argv",
    [
        ["list", "--summary", "--json"],
        ["list", "--json"],
        ["refresh", "--json"],
        [
            "resolve-skill-path",
            "--skill-id",
            "impl",
            "--reported-path",
            "/tmp/old.md",
            "--json",
        ],
    ],
)
def test_catalog_cli_rejects_the_removed_json_flag(tmp_path: Path, argv: list[str]) -> None:
    """`--json` is gone with no back-compat, so every subcommand must refuse it.

    This replaces the old `--summary` + `--json` conflict guard: the conflict it
    checked cannot arise once the flag is undeclared, and the guard it protected was
    deleted with it. What still needs teeth is that no subcommand quietly accepts and
    ignores the retired flag, which is how the previous YAML migration left residue.
    """
    with pytest.raises(SystemExit) as exc_info:
        catalog_main([argv[0], "--repo-root", str(tmp_path), *argv[1:]])
    assert exc_info.value.code == 2


def test_catalog_sources_cover_dedup_frontmatter_references_and_duplicate_names(
    tmp_path: Path,
) -> None:
    assert sources._dedupe(["", "one", "one", "two"]) == ["one", "two"]
    malformed = tmp_path / "malformed.md"
    malformed.write_text("# no frontmatter\n", encoding="utf-8")
    assert sources._frontmatter(malformed) == {}

    repo = tmp_path / "repo"
    skill_root = repo / "skills"
    first = skill_root / "first"
    second = skill_root / "second"
    reference = first / "references" / "guide.md"
    reference.parent.mkdir(parents=True)
    reference.write_text("guide\n", encoding="utf-8")
    for skill in (first, second):
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(
            "---\nname: duplicate-name\ndescription: test\n---\nSee `references/guide.md`.\n",
            encoding="utf-8",
        )
    entries = sources._skill_entries(
        [("skills", skill_root), ("same-root", skill_root)], repo_root=repo, layer="public skill"
    )
    assert len(entries) == 1
    assert entries[0]["referenced_paths"] == ["skills/first/references/guide.md"]


def test_catalog_sources_cover_sibling_support_malformed_adapter_and_exported_root(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "consumer"
    sibling_skill = tmp_path / "charness-support" / "helper"
    sibling_skill.mkdir(parents=True)
    (sibling_skill / "capability.json").write_text(
        json.dumps({"capability_id": "helper", "kind": "support", "summary": "helper"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(sources, "load_support_capabilities", lambda _root: [])
    caps = sources._support_caps(repo)
    assert caps[0]["id"] == "helper"

    bad_adapter = repo / ".agents" / "capability-catalog-adapter.yaml"
    bad_adapter.parent.mkdir(parents=True)
    bad_adapter.write_text("- not-a-mapping\n", encoding="utf-8")
    monkeypatch.setattr(sources, "load_yaml_file", lambda _path: ["not-a-mapping"])
    loaded = sources.load_adapter(repo)
    assert any("did not contain a mapping" in warning for warning in loaded["warnings"])

    fake_root = tmp_path / "plugin-root"
    (fake_root / ".codex-plugin").mkdir(parents=True)
    (fake_root / ".codex-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
    plugin_skill = fake_root / "skills" / "plugin-skill"
    plugin_skill.mkdir(parents=True)
    (plugin_skill / "SKILL.md").write_text(
        "---\nname: plugin-skill\ndescription: test\n---\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        sources, "__file__", str(fake_root / "scripts" / "capability_catalog_sources.py")
    )
    inventory = sources.build_inventory(repo)
    assert any(item["id"] == "plugin-skill" for item in inventory["public_skills"])


def test_catalog_source_refuses_unsupported_adapter_before_trust_fields(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    adapter = repo / ".agents" / "capability-catalog-adapter.yaml"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        "version: 7\n"
        "trusted_skill_roots:\n"
        "- /private/provider-cache\n"
        "allow_external_registry: true\n",
        encoding="utf-8",
    )

    loaded = sources.load_adapter(repo)

    assert loaded["valid"] is False
    assert loaded["errors"] == ["version must be 1"]
    assert loaded["data"]["trusted_skill_roots"] == []
    assert loaded["data"]["allow_external_registry"] is False
    inventory = sources.build_inventory(repo)
    assert inventory["adapter"]["errors"] == ["version must be 1"]


def test_catalog_persist_refuses_to_erase_existing_support_surface(tmp_path: Path) -> None:
    prior = {
        "public_skills": [],
        "support_skills": [{"id": "keep-me"}],
        "support_capabilities": [],
        "integrations": [],
    }
    persist_catalog(tmp_path, prior)
    with pytest.raises(ValueError, match="empty support_skills"):
        persist_catalog(
            tmp_path,
            {
                "public_skills": [],
                "support_skills": [],
                "support_capabilities": [],
                "integrations": [],
            },
        )


def test_catalog_resolver_handles_missing_cache_root_and_missing_skill_warning(
    tmp_path: Path,
) -> None:
    assert _cache_candidates(tmp_path / "codex", "impl", "local", "charness") == []
    payload = resolve_skill_path(
        skill_id="missing",
        repo_root=tmp_path / "repo",
        home=tmp_path / "home",
        codex_home=tmp_path / "codex",
        reported_path=tmp_path / "missing/SKILL.md",
    )
    assert payload["status"] == "missing"
    assert any("No installed or repo-local" in warning for warning in payload["warnings"])
