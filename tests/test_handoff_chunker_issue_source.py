"""#249 slice 2: issue-backed source feeds HandoffEntry records that the
merge proposer clusters by surface, unioned with handoff entries.

All offline: provider listing is exercised through an injected runner stub, so
no live tracker call is made. The live route is proven in the goal's behavior
slice.
"""
from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

from tests.repo_copy import REPO_COPY_IGNORE

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skills" / "public" / "handoff" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lib():
    return _load("chunked_routing_lib")


@pytest.fixture(scope="module")
def src():
    return _load("chunked_routing_issue_source")


# --- conversion -----------------------------------------------------------


def test_title_path_is_a_boundary_but_body_path_is_not(src):
    """Title paths cluster; body paths are captured as referenced_paths but
    NOT as merge boundaries (precision — avoids the dogfood over-merge)."""
    issue = {
        "number": 244,
        "title": "scripts/host_hook_install_lib.py hardcodes the hook path",
        "labels": [],
        "body": "incidental mention of skills/public/quality/references/x.md here.",
    }
    entry = src.issue_to_handoff_entry(issue, index=7)
    assert entry.index == 7
    assert entry.title.startswith("#244:")
    # title path -> boundary token
    assert "scripts/host_hook_install_lib.py" in entry.boundary_tokens
    # body path -> referenced, but NOT a merge boundary
    assert "skills/public/quality/references/x.md" in entry.referenced_paths
    assert "skills/public/quality/references/x.md" not in entry.boundary_tokens
    # own number leads referenced_issues (slice-3 dedup key)
    assert entry.referenced_issues[0] == 244


def test_specific_label_becomes_boundary_but_generic_does_not(src):
    specific = src.issue_to_handoff_entry(
        {"number": 242, "title": "Mutation regression", "labels": [{"name": "mutation-test"}], "body": ""},
        index=1,
    )
    generic = src.issue_to_handoff_entry(
        {"number": 184, "title": "Define metrics", "labels": [{"name": "bug"}], "body": ""},
        index=2,
    )
    assert "label/mutation-test" in specific.boundary_tokens
    assert not any(t.startswith("label/") for t in generic.boundary_tokens)


# --- clustering via propose_merges ---------------------------------------


def _entries(src, issues):
    return [src.issue_to_handoff_entry(issue, index=i + 1) for i, issue in enumerate(issues)]


def test_same_surface_issues_merge_others_stay_standalone(lib, src):
    issues = [
        # shared TITLE path -> cluster
        {"number": 244, "title": "scripts/host_hook_install_lib.py: hook not auto-installed",
         "labels": [], "body": ""},
        {"number": 245, "title": "scripts/host_hook_install_lib.py: duplicate hooks",
         "labels": [], "body": ""},
        # shared SPECIFIC label -> cluster
        {"number": 242, "title": "Mutation regression", "labels": [{"name": "mutation-test"}], "body": ""},
        {"number": 219, "title": "Mutation regression (older)", "labels": [{"name": "mutation-test"}], "body": ""},
        # generic label only -> never merges
        {"number": 184, "title": "Define product metrics", "labels": [{"name": "bug"}], "body": "no shared surface"},
    ]
    proposal = lib.propose_merges(_entries(src, issues))
    merged_label_sets = {
        frozenset(e.referenced_issues[0] for e in cand.entries) for cand in proposal.merged
    }
    assert frozenset({244, 245}) in merged_label_sets  # shared title path token
    assert frozenset({242, 219}) in merged_label_sets  # shared specific label
    # the generic-label issue never joins a merge
    assert all(184 not in s for s in merged_label_sets)


def test_body_only_path_overlap_does_not_over_merge(lib, src):
    """Two issues that share only an incidental BODY path stay standalone —
    the slice-2 dogfood over-merge guard."""
    issues = [
        {"number": 300, "title": "Closeout gates bind evidence", "labels": [],
         "body": "touches skills/public/achieve/scripts/goal_artifact_lib.py among others"},
        {"number": 301, "title": "Mutation survivors on main", "labels": [],
         "body": "mutants under skills/public/achieve/scripts/goal_artifact_lib.py listed"},
    ]
    proposal = lib.propose_merges(_entries(src, issues))
    assert proposal.merged == ()  # no spurious body-path cluster


# --- union ----------------------------------------------------------------


def test_union_reindexes_issues_after_handoff_max(lib, src):
    handoff_text = (
        "## Next Session\n\n"
        "1. **First.** do a thing.\n"
        "2. **Second.** do another.\n\n"
        "## Other\n"
    )
    handoff_entries = lib.parse_handoff_entries(handoff_text)
    assert [e.index for e in handoff_entries] == [1, 2]
    issue_entries = _entries(src, [
        {"number": 244, "title": "x", "labels": [], "body": ""},
        {"number": 245, "title": "y", "labels": [], "body": ""},
    ])
    unioned = src.union_entries(handoff_entries, issue_entries)
    assert [e.index for e in unioned] == [1, 2, 3, 4]
    # labels are collision-free (chunk-1..chunk-4)
    proposal = lib.propose_merges(unioned)
    labels = [c.label for c in proposal.standalone]
    assert len(set(labels)) == len(labels) == 4


def test_union_with_no_issues_is_identity(lib, src):
    handoff_entries = lib.parse_handoff_entries(
        "## Next Session\n\n1. **Only.** thing.\n\n## End\n"
    )
    assert src.union_entries(handoff_entries, []) == handoff_entries


# --- dedup (slice 3) ------------------------------------------------------


def test_dedup_merges_cited_issue_into_handoff_entry(lib, src):
    """A handoff entry citing #242 + the issue entry for #242 collapse to one;
    the issue's surface token enriches the handoff entry, the duplicate drops."""
    handoff_entries = lib.parse_handoff_entries(
        "## Next Session\n\n"
        "1. **Mutation work.** triage #242 survivors.\n"
        "2. **Unrelated.** something else.\n\n"
        "## End\n"
    )
    issue_entries = _entries(src, [
        {"number": 242, "title": "Mutation regression", "labels": [{"name": "mutation-test"}], "body": ""},
        {"number": 999, "title": "Brand new untracked issue", "labels": [], "body": ""},
    ])
    out = src.dedup_and_union(handoff_entries, issue_entries)
    # the #242 issue entry is gone; #999 (uncited) remains
    issue_titled = [e for e in out if e.title.startswith("#")]
    assert [e.title for e in issue_titled] == ["#999: Brand new untracked issue"]
    # the citing handoff entry inherited the issue's surface token
    mutation_entry = next(e for e in out if "#242" in e.body)
    assert "label/mutation-test" in mutation_entry.boundary_tokens
    assert len(out) == 3  # 2 handoff + 1 surviving issue (242 merged away)


def test_dedup_enriched_entry_then_clusters_with_another_issue(lib, src):
    """After #242 merges into its handoff entry (gaining label/mutation-test),
    that handoff entry clusters with another mutation-test issue (#219)."""
    handoff_entries = lib.parse_handoff_entries(
        "## Next Session\n\n1. **Mutation.** triage #242.\n\n## End\n"
    )
    issue_entries = _entries(src, [
        {"number": 242, "title": "Mutation regression", "labels": [{"name": "mutation-test"}], "body": ""},
        {"number": 219, "title": "Mutation regression older", "labels": [{"name": "mutation-test"}], "body": ""},
    ])
    out = src.dedup_and_union(handoff_entries, issue_entries)
    proposal = lib.propose_merges(out)
    # the enriched handoff entry (index 1) and #219 share label/mutation-test
    assert any(len(c.entries) == 2 for c in proposal.merged)


# --- provider routing (injected runner; no live call) ---------------------


def test_list_open_issues_uses_gh_default_template(src):
    seen = {}

    def stub(argv):
        seen["argv"] = argv
        return [{"number": 1, "title": "t", "labels": [], "body": ""}]

    out = src.list_open_issues("corca-ai/charness", limit=25, runner=stub)
    assert out and out[0]["number"] == 1
    assert seen["argv"][0] == "gh"
    assert "corca-ai/charness" in seen["argv"]
    assert "25" in seen["argv"]


def test_non_gh_backend_requires_command_template(src):
    with pytest.raises(RuntimeError, match="commands.list_open"):
        src.list_open_issues(
            "x/y", backend={"id": "acme", "binary": "acme", "commands": None}, runner=lambda a: []
        )


def test_build_issue_entries_filters_and_converts(src, monkeypatch, tmp_path):
    # Force-enable + bypass adapter/target resolution by stubbing the helpers.
    monkeypatch.setattr(src, "load_issue_source_config", lambda root: {
        "enabled": True, "limit": 50, "repo": None,
        "labels_include": (), "labels_exclude": ("wontfix",), "exclude_numbers": (999,),
    })

    def fake_load_issue_module(root, name):
        class _Mod:
            @staticmethod
            def load_adapter(r):
                return {"data": {"issue_backend": {"id": "gh", "binary": "gh", "commands": None},
                                 "default_org": "corca-ai", "default_repo": "charness",
                                 "remote_name": "origin"}}

            @staticmethod
            def resolve_target(r, repo, data):
                return {"full_name": "corca-ai/charness"}

            @staticmethod
            def _backend_json(argv):
                return []
        return _Mod

    monkeypatch.setattr(src, "_load_issue_module", fake_load_issue_module)

    def runner(argv):
        return [
            {"number": 244, "title": "keep", "labels": [], "body": "scripts/x/y.py"},
            {"number": 999, "title": "excluded by number", "labels": [], "body": ""},
            {"number": 250, "title": "excluded by label", "labels": [{"name": "wontfix"}], "body": ""},
        ]

    entries = src.build_issue_entries(tmp_path, start_index=5, runner=runner)
    numbers = [e.referenced_issues[0] for e in entries]
    assert numbers == [244]
    assert entries[0].index == 5


def test_build_issue_entries_disabled_returns_empty(src, monkeypatch, tmp_path):
    monkeypatch.setattr(src, "load_issue_source_config", lambda root: {
        "enabled": False, "limit": 50, "repo": None,
        "labels_include": (), "labels_exclude": (), "exclude_numbers": (),
    })
    assert src.build_issue_entries(tmp_path, start_index=1, runner=lambda a: [{"number": 1}]) == []


# --- #251 regression coverage: changed lines the gate flagged as uncovered ----
# These exercise the REAL load_issue_source_config, the provider-routing edges,
# and the failure/skip branches that earlier tests monkeypatched away or never
# reached, so the chunker scripts stop blocking the mutation gate (#251).


@pytest.fixture
def backend():
    return _load("chunked_routing_issue_backend")


def _write_adapter(repo: Path, body: str) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "handoff-adapter.yaml").write_text(body, encoding="utf-8")


def test_load_issue_source_config_defaults_without_block(src, tmp_path):
    """Adapter present but no issue_source block -> opt-out defaults."""
    _write_adapter(tmp_path, "version: 1\nrepo: t\noutput_dir: docs\n")
    config = src.load_issue_source_config(tmp_path)
    assert config == {
        "enabled": True, "limit": src.DEFAULT_ISSUE_LIMIT, "repo": None,
        "labels_include": (), "labels_exclude": (), "exclude_numbers": (),
    }


def test_load_issue_source_config_parses_full_block(src, tmp_path):
    """Block-style lists + scalars all flow into the normalized config."""
    _write_adapter(
        tmp_path,
        "version: 1\nrepo: t\noutput_dir: docs\n"
        "issue_source:\n"
        "  enabled: true\n  limit: 7\n  repo: o/r\n"
        "  labels_include:\n    - keep\n"
        "  labels_exclude:\n    - drop\n"
        "  exclude_numbers:\n    - 9\n    - 10\n",
    )
    config = src.load_issue_source_config(tmp_path)
    assert config == {
        "enabled": True, "limit": 7, "repo": "o/r",
        "labels_include": ("keep",), "labels_exclude": ("drop",),
        "exclude_numbers": (9, 10),
    }


def test_load_issue_source_config_defaults_when_no_adapter_file(src, tmp_path):
    """No adapter at all -> resolver yields no path -> opt-out defaults."""
    config = src.load_issue_source_config(tmp_path)
    assert config["enabled"] is True and config["limit"] == src.DEFAULT_ISSUE_LIMIT


def test_load_issue_source_config_degrades_when_adapter_lib_missing(src, monkeypatch, tmp_path):
    """If scripts/adapter_lib.py can't be located, degrade to defaults rather
    than crash (the adapter_lib-None defensive branch)."""
    _write_adapter(
        tmp_path,
        "version: 1\nrepo: t\noutput_dir: docs\nissue_source:\n  limit: 3\n",
    )
    real_is_file = src.Path.is_file
    monkeypatch.setattr(
        src.Path, "is_file",
        lambda self: False if self.name == "adapter_lib.py" else real_is_file(self),
    )
    config = src.load_issue_source_config(tmp_path)
    assert config["limit"] == src.DEFAULT_ISSUE_LIMIT  # block never parsed


def test_load_issue_source_config_swallows_resolution_failure(src, monkeypatch, tmp_path):
    """Any adapter-loading error degrades to defaults (trackerless fallback)."""
    def boom(_name):
        raise RuntimeError("adapter resolution blew up")
    monkeypatch.setattr(src, "_load_sibling", boom)
    config = src.load_issue_source_config(tmp_path)
    assert config["enabled"] is True and config["repo"] is None


def test_label_names_accepts_plain_string_labels(src):
    """gh returns label dicts, but a plain-string label must also be read."""
    entry = src.issue_to_handoff_entry(
        {"number": 7, "title": "t", "labels": ["mutation-test", "  ", 5], "body": ""},
        index=1,
    )
    assert "label/mutation-test" in entry.boundary_tokens


def test_passes_filters_labels_include_gate(src):
    issue = {"number": 5, "labels": [{"name": "infra"}]}
    assert src._passes_filters(
        issue, labels_include=("ui",), labels_exclude=(), exclude_numbers=()
    ) is False
    assert src._passes_filters(
        issue, labels_include=("infra",), labels_exclude=(), exclude_numbers=()
    ) is True


def test_build_issue_entries_returns_empty_on_listing_failure(src, monkeypatch, tmp_path):
    monkeypatch.setattr(src, "load_issue_source_config", lambda root: {
        "enabled": True, "limit": 50, "repo": None,
        "labels_include": (), "labels_exclude": (), "exclude_numbers": (),
    })

    def fake_load_issue_module(root, name):
        class _Mod:
            @staticmethod
            def load_adapter(r):
                return {"data": {}}

            @staticmethod
            def resolve_target(r, repo, data):
                return {"full_name": "o/r"}

            @staticmethod
            def _backend_json(argv):
                return []
        return _Mod

    monkeypatch.setattr(src, "_load_issue_module", fake_load_issue_module)

    def exploding_runner(argv):
        raise RuntimeError("provider listing failed")

    assert src.build_issue_entries(tmp_path, start_index=1, runner=exploding_runner) == []
    diagnostic = src.LAST_ISSUE_SOURCE_DIAGNOSTIC
    assert diagnostic["stage"] == "list_open_issues"
    assert diagnostic["provider_attempted"] is True
    assert diagnostic["type"] == "RuntimeError"
    assert diagnostic["message"] == "provider listing failed"


def test_build_issue_entries_skips_malformed_issues(src, monkeypatch, tmp_path):
    monkeypatch.setattr(src, "load_issue_source_config", lambda root: {
        "enabled": True, "limit": 50, "repo": None,
        "labels_include": (), "labels_exclude": (), "exclude_numbers": (),
    })

    def fake_load_issue_module(root, name):
        class _Mod:
            @staticmethod
            def load_adapter(r):
                return {"data": {}}

            @staticmethod
            def resolve_target(r, repo, data):
                return {"full_name": "o/r"}

            @staticmethod
            def _backend_json(argv):
                return []
        return _Mod

    monkeypatch.setattr(src, "_load_issue_module", fake_load_issue_module)

    def runner(argv):
        return ["not-a-dict", {"no": "number"}, {"number": 244, "title": "ok", "labels": [], "body": ""}]

    entries = src.build_issue_entries(tmp_path, start_index=1, runner=runner)
    assert [e.referenced_issues[0] for e in entries] == [244]


def test_load_sibling_raises_when_spec_is_none(src, monkeypatch):
    """The defensive guard fires when importlib cannot build a spec."""
    monkeypatch.setattr(
        src.importlib.util, "spec_from_file_location", lambda *a, **k: None
    )
    with pytest.raises(ImportError, match="not found beside"):
        src._load_sibling("chunked_routing_types")


# --- provider-routing layer (chunked_routing_issue_backend) ----------------


def test_load_issue_module_imports_real_issue_runtime(backend):
    module = backend._load_issue_module(REPO_ROOT, "issue_runtime")
    assert hasattr(module, "_backend_json")


def test_load_issue_module_imports_installed_issue_layout(backend, tmp_path):
    plugin_root = tmp_path / "plugin"
    handoff_scripts = plugin_root / "skills" / "handoff" / "scripts"
    shutil.copytree(
        SCRIPTS,
        handoff_scripts,
        ignore=REPO_COPY_IGNORE,
    )
    scripts = plugin_root / "skills" / "issue" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "issue_runtime.py").write_text("VALUE = 'installed'\n", encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        "installed_chunked_routing_issue_backend",
        handoff_scripts / "chunked_routing_issue_backend.py",
    )
    assert spec is not None and spec.loader is not None
    installed_backend = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installed_backend)

    module = installed_backend._load_issue_module(tmp_path / "consumer", "issue_runtime")

    assert module.VALUE == "installed"


def test_load_issue_module_installed_layout_ignores_consumer_repo_shadow(tmp_path):
    plugin_root = tmp_path / "plugin"
    consumer = tmp_path / "consumer"
    handoff_scripts = plugin_root / "skills" / "handoff" / "scripts"
    shutil.copytree(SCRIPTS, handoff_scripts, ignore=REPO_COPY_IGNORE)
    consumer_issue = consumer / "skills" / "issue" / "scripts"
    consumer_issue.mkdir(parents=True)
    (consumer_issue / "issue_runtime.py").write_text("VALUE = 'consumer'\n", encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        "installed_chunked_routing_issue_backend_no_issue",
        handoff_scripts / "chunked_routing_issue_backend.py",
    )
    assert spec is not None and spec.loader is not None
    installed_backend = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installed_backend)

    with pytest.raises(ImportError, match="issue_runtime"):
        installed_backend._load_issue_module(consumer, "issue_runtime")


def test_load_issue_module_installed_layout_ignores_ancestor_source_tree(tmp_path):
    repo_root = tmp_path / "repo"
    plugin_root = repo_root / "plugins" / "charness"
    handoff_scripts = plugin_root / "skills" / "handoff" / "scripts"
    shutil.copytree(SCRIPTS, handoff_scripts, ignore=REPO_COPY_IGNORE)
    ancestor_issue = repo_root / "skills" / "public" / "issue" / "scripts"
    ancestor_issue.mkdir(parents=True)
    (ancestor_issue / "issue_runtime.py").write_text(
        "VALUE = 'ancestor-source'\n",
        encoding="utf-8",
    )
    spec = importlib.util.spec_from_file_location(
        "installed_chunked_routing_issue_backend_nested",
        handoff_scripts / "chunked_routing_issue_backend.py",
    )
    assert spec is not None and spec.loader is not None
    installed_backend = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installed_backend)

    with pytest.raises(ImportError, match="issue_runtime"):
        installed_backend._load_issue_module(tmp_path / "consumer", "issue_runtime")


def test_load_issue_module_installed_layout_prefers_installed_over_stale_source(tmp_path):
    plugin_root = tmp_path / "plugin"
    handoff_scripts = plugin_root / "skills" / "handoff" / "scripts"
    shutil.copytree(SCRIPTS, handoff_scripts, ignore=REPO_COPY_IGNORE)
    installed = plugin_root / "skills" / "issue" / "scripts"
    source = plugin_root / "skills" / "public" / "issue" / "scripts"
    installed.mkdir(parents=True)
    source.mkdir(parents=True)
    (installed / "issue_runtime.py").write_text("VALUE = 'installed'\n", encoding="utf-8")
    (source / "issue_runtime.py").write_text("VALUE = 'stale-source'\n", encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        "installed_chunked_routing_issue_backend_both",
        handoff_scripts / "chunked_routing_issue_backend.py",
    )
    assert spec is not None and spec.loader is not None
    installed_backend = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installed_backend)

    module = installed_backend._load_issue_module(tmp_path / "consumer", "issue_runtime")

    assert module.VALUE == "installed"


def test_load_issue_module_missing_raises(backend):
    with pytest.raises(ImportError, match="definitely_missing_xyz"):
        backend._load_issue_module(REPO_ROOT, "definitely_missing_xyz")


def test_load_issue_module_skips_unbuildable_spec(backend, monkeypatch):
    """An existing file whose spec can't be built is skipped (the `continue`
    guard), so resolution keeps walking instead of crashing."""
    monkeypatch.setattr(
        backend.importlib.util, "spec_from_file_location", lambda *a, **k: None
    )
    with pytest.raises(ImportError):
        backend._load_issue_module(REPO_ROOT, "issue_runtime")  # real file, None spec


def test_list_open_issues_default_runner_resolves_backend_json(backend, monkeypatch):
    """runner=None -> the backend loads issue_runtime._backend_json itself."""
    calls = {}

    class _Runtime:
        @staticmethod
        def _backend_json(argv):
            calls["argv"] = argv
            return [{"number": 9, "title": "t", "labels": [], "body": ""}]

    monkeypatch.setattr(backend, "_load_issue_module", lambda root, name: _Runtime)
    out = backend.list_open_issues("o/r", runner=None)
    assert out[0]["number"] == 9
    assert calls["argv"][0] == "gh"


def test_list_open_issues_unwraps_issues_dict(backend):
    """A backend that returns {"issues": [...]} is unwrapped to the list."""
    out = backend.list_open_issues(
        "o/r", runner=lambda argv: {"issues": [{"number": 1}]}
    )
    assert out == [{"number": 1}]


def test_list_open_issues_raises_on_malformed_payload(backend):
    with pytest.raises(RuntimeError, match="without list field"):
        backend.list_open_issues("o/r", runner=lambda argv: {"items": []})
    with pytest.raises(RuntimeError, match="non-list JSON"):
        backend.list_open_issues("o/r", runner=lambda argv: "not-json-list")
