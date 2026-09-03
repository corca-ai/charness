from __future__ import annotations

import json
import os
import time
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
        "materialized_base": None,
        "materialized_kind": None,
        "missing_paths": [],
    }

    plugin = tmp_path / "plugin"
    previous = {
        "support": {
            "materialized_base": str(plugin),
            "materialized_kind": "installed-plugin-copy",
            "materialized_paths": ["support/demo"],
        }
    }
    missing = support.inspect_support_sync(repo, previous)
    assert missing["status"] == "missing"
    assert missing["missing_paths"] == ["support/demo"]

    materialized = plugin / "support"
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


def _digest_tree(tool_root: Path, name: str, *, age_days: float) -> Path:
    tree = tool_root / name
    tree.mkdir(parents=True)
    (tree / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    marker = support._last_used_marker(tree)
    marker.write_text("0", encoding="utf-8")
    stamp = time.time() - age_days * 86400
    os.utime(marker, (stamp, stamp))
    return tree


def test_promoting_a_support_tree_keeps_the_current_plus_three_recent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CHARNESS_CACHE_HOME", str(tmp_path / "cache"))
    tool_root = support.support_skill_cache_dir() / "demo"
    aged = {days: _digest_tree(tool_root, f"digest-{days}", age_days=days) for days in range(1, 6)}
    source = tmp_path / "source"
    source.mkdir()
    (source / "SKILL.md").write_text("# fresh\n", encoding="utf-8")

    promoted = support._promote_tree_to_cache(
        source, manifest={"tool_id": "demo"}, digest="fresh", repo_root=None
    )

    assert promoted == tool_root / "fresh"
    assert support._last_used_marker(promoted).is_file()
    survivors = {path.name for path in tool_root.iterdir() if path.is_dir()}
    assert survivors == {"fresh", "digest-1", "digest-2", "digest-3"}
    assert not aged[4].exists() and not aged[5].exists()


def test_a_support_tree_a_live_symlink_points_at_outlives_the_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CHARNESS_CACHE_HOME", str(tmp_path / "cache"))
    repo = tmp_path / "repo"
    tool_root = support.support_skill_cache_dir() / "demo"
    aged = {days: _digest_tree(tool_root, f"digest-{days}", age_days=days) for days in range(1, 6)}
    support.materialize_repo_symlink(aged[5], support.generated_support_dir(repo) / "demo", repo)
    source = tmp_path / "source"
    source.mkdir()
    (source / "SKILL.md").write_text("# fresh\n", encoding="utf-8")

    support._promote_tree_to_cache(
        source, manifest={"tool_id": "demo"}, digest="fresh", repo_root=repo
    )

    # `digest-5` is the LEAST recently used and would fall outside `keep`, but the
    # repo's generated support skill resolves through it, so the bound may not take it.
    assert aged[5].is_dir()
    assert (support.generated_support_dir(repo) / "demo" / "SKILL.md").is_file()
    assert {path.name for path in tool_root.iterdir() if path.is_dir()} == {
        "fresh",
        "digest-1",
        "digest-2",
        "digest-3",
        "digest-5",
    }
    assert not aged[4].exists()


def test_support_tree_bound_tolerates_a_missing_root_and_an_unremovable_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "cache" / "support-skills" / "demo"
    assert support.prune_support_skill_trees(missing, current=missing / "fresh") == []
    assert support.live_support_tree_targets(None) == set()
    assert support.live_support_tree_targets(tmp_path / "no-such-repo") == set()

    tool_root = tmp_path / "tool"
    stale = _digest_tree(tool_root, "old", age_days=9)
    current = _digest_tree(tool_root, "new", age_days=0)
    monkeypatch.setattr(
        support.shutil, "rmtree", lambda _path: (_ for _ in ()).throw(OSError("busy"))
    )
    assert support.prune_support_skill_trees(tool_root, current=current, keep=0) == []
    assert stale.is_dir()


def test_a_support_tree_with_no_marker_is_still_ordered_and_touched(tmp_path: Path) -> None:
    tool_root = tmp_path / "tool"
    bare = tool_root / "bare"
    bare.mkdir(parents=True)
    assert support._support_tree_last_used(bare) == bare.stat().st_mtime
    assert support._support_tree_last_used(tool_root / "gone") == 0.0
    support._touch_support_tree(bare)
    assert support._last_used_marker(bare).is_file()
    support._touch_support_tree(tool_root / "gone")


def test_an_unwritable_use_stamp_does_not_fail_the_sync_that_asked_for_the_tree(
    tmp_path: Path,
) -> None:
    """The stamp is bookkeeping for the BOUND, never a precondition of the sync.

    A cache root that does not exist -- a cleared cache home, a read-only tool
    root -- must not turn "this repo used this support tree" into a failed
    materialization. The tree the caller asked for is still the answer; only the
    recency ordering degrades, and `_support_tree_last_used` already treats a
    missing stamp as oldest.
    """
    missing_root = tmp_path / "no-such-cache" / "demo"
    tree = missing_root / "digest"

    support._touch_support_tree(tree)

    assert not support._last_used_marker(tree).exists()
    assert not missing_root.exists()
    assert support._support_tree_last_used(tree) == 0.0


def test_one_unresolvable_link_does_not_blind_the_bound_to_the_live_trees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A link this process cannot resolve is skipped, not treated as the whole set.

    Losing the loop here would drop every live target found after the bad link,
    and the bound would then delete a tree the repo's generated support skill
    still resolves through. Skipping one entry costs at most a stale tree.
    """
    monkeypatch.setenv("CHARNESS_CACHE_HOME", str(tmp_path / "cache"))
    repo = tmp_path / "repo"
    tool_root = support.support_skill_cache_dir() / "demo"
    live = _digest_tree(tool_root, "live", age_days=1)
    support.materialize_repo_symlink(live, support.generated_support_dir(repo) / "demo", repo)
    unreadable = support.generated_support_dir(repo) / "unreadable"
    unreadable.symlink_to(tool_root / "gone")
    # Resolved BEFORE the patch, so the expectation is the real target rather than
    # a second call through the failure shim.
    expected = live.resolve()
    original = Path.resolve

    def fail_one(path: Path, *args, **kwargs):
        if path == unreadable:
            raise OSError("forced resolve failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", fail_one)

    assert support.live_support_tree_targets(repo) == {expected}


def test_the_use_stamp_lives_beside_the_tree_so_its_content_digest_is_stable(tmp_path: Path) -> None:
    """`charness update` proves "already current" by hashing the tree against the host's
    copy; a stamp INSIDE the tree made every readback differ and every update refresh
    (release lane, 2026-09-03). Touching must leave the tree's bytes alone."""
    tool_root = tmp_path / "tool"
    tree = tool_root / "digest"
    tree.mkdir(parents=True)
    (tree / "SKILL.md").write_text("# digest\n", encoding="utf-8")
    before = sorted(path.relative_to(tree) for path in tree.rglob("*"))
    support._touch_support_tree(tree)
    support._touch_support_tree(tree)
    assert sorted(path.relative_to(tree) for path in tree.rglob("*")) == before
    assert support._last_used_marker(tree).parent == tool_root
    assert support._support_tree_last_used(tree) > 0.0
