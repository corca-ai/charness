from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.support_sync_lib as support


def test_support_state_and_link_name_cover_manifest_shapes() -> None:
    native = {"kind": "support_runtime", "tool_id": "native"}
    integration_only = {"tool_id": "plain"}
    wrapped = {
        "tool_id": "wrapped",
        "support_skill_source": {
            "source_type": "local_wrapper",
            "wrapper_skill_id": "wrapped-skill",
        },
    }
    upstream = {
        "tool_id": "upstream",
        "support_skill_source": {"source_type": "upstream_repo"},
    }

    assert support.support_state_for_manifest(native) == "native-support"
    assert support.support_state_for_manifest(integration_only) == "integration-only"
    assert support.support_state_for_manifest(wrapped) == "wrapped-upstream"
    assert support.support_state_for_manifest(upstream) == "upstream-consumed"
    assert support.support_link_name(wrapped) == "wrapped-skill"
    assert support.support_link_name(upstream) == "upstream"


def test_inspect_support_sync_reports_not_tracked_missing_and_ok(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    assert support.inspect_support_sync(repo, None) == {
        "status": "not-tracked",
        "expected_paths": [],
        "missing_paths": [],
    }

    previous = {"support": {"materialized_paths": ["skills/support/generated/demo"]}}
    missing = support.inspect_support_sync(repo, previous)
    assert missing["status"] == "missing"
    assert missing["missing_paths"] == ["skills/support/generated/demo"]

    materialized = repo / "skills" / "support" / "generated"
    materialized.mkdir(parents=True)
    (materialized / "demo").write_text("# demo\n", encoding="utf-8")
    ok = support.inspect_support_sync(repo, previous)
    assert ok["status"] == "ok"
    assert ok["missing_paths"] == []


def test_parse_upstream_checkout_requires_existing_absolute_target(tmp_path: Path) -> None:
    checkout = tmp_path / "checkout"
    checkout.mkdir()

    repo, root = support.parse_upstream_checkout(f"example/demo={checkout}")
    assert repo == "example/demo"
    assert root == checkout.resolve()

    with pytest.raises(ValueError, match="must look like"):
        support.parse_upstream_checkout("example/demo")

    with pytest.raises(ValueError, match="does not exist"):
        support.parse_upstream_checkout(f"example/demo={tmp_path / 'missing'}")


def test_fixture_checkout_root_validates_payload_and_prefers_ref_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fixture_root = tmp_path / "fixture"
    fixture_root.mkdir()
    fixture_map = tmp_path / "fixtures.json"
    fixture_map.write_text(
        json.dumps(
            {
                "example/demo": str(tmp_path / "wrong"),
                "example/demo@main": str(fixture_root),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(support.SUPPORT_FIXTURES_ENV, str(fixture_map))

    assert support._fixture_checkout_root("example/demo", "main") == fixture_root.resolve()

    fixture_map.write_text('["bad"]\n', encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        support._fixture_checkout_root("example/demo", "main")

    fixture_map.write_text(json.dumps({"example/demo": str(tmp_path / "missing")}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="points at missing directory"):
        support._fixture_checkout_root("example/demo", None)


def test_render_discovery_stub_prefers_install_url_then_docs_url() -> None:
    install_manifest = {
        "tool_id": "demo-install",
        "intent_triggers": ["investigate drift", "repair support sync"],
        "lifecycle": {"install": {"install_url": "https://example.com/install"}},
    }
    docs_manifest = {
        "tool_id": "demo-docs",
        "intent_triggers": [],
        "lifecycle": {"install": {"docs_url": "https://example.com/docs"}},
    }

    install_stub = support.render_discovery_stub(
        manifest=install_manifest,
        support_skill_path="skills/support/generated/demo-install/SKILL.md",
    )
    docs_stub = support.render_discovery_stub(
        manifest=docs_manifest,
        support_skill_path="skills/support/generated/demo-docs/SKILL.md",
    )

    assert "investigate drift, repair support sync" in install_stub
    assert "- install docs: https://example.com/install" in install_stub
    assert "no explicit trigger hints recorded" in docs_stub
    assert "- docs: https://example.com/docs" in docs_stub


def test_write_discovery_stub_and_resolve_upstream_source_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    checkout = tmp_path / "checkout"
    skill_root = checkout / "skills" / "demo"
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text("# demo\n", encoding="utf-8")

    stub_path = support.write_discovery_stub(
        repo,
        {"tool_id": "demo", "intent_triggers": [], "lifecycle": {"install": {}}},
        support_skill_path="skills/support/generated/demo/SKILL.md",
    )
    assert stub_path == ".agents/charness-discovery/demo.md"
    assert (repo / stub_path).is_file()

    manifest = {
        "tool_id": "demo",
        "upstream_repo": "example/demo",
        "support_skill_source": {"source_type": "upstream_repo", "path": "skills/demo"},
    }
    with pytest.raises(ValueError, match="requires `ref`"):
        support._resolve_upstream_source_path(manifest, upstream_checkouts={})

    manifest["support_skill_source"]["ref"] = "main"
    resolved = support._resolve_upstream_source_path(
        manifest,
        upstream_checkouts={"example/demo": checkout},
    )
    assert resolved == skill_root

    bad_checkout = tmp_path / "bad-checkout"
    bad_checkout.mkdir()
    with pytest.raises(ValueError, match="must be a skill root directory"):
        support._resolve_upstream_source_path(
            manifest,
            upstream_checkouts={"example/demo": bad_checkout},
        )
