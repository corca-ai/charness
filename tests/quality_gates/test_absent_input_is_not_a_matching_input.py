"""One class, four surfaces: an absent or unreadable input must not read as a good one.

Sweep rows S24, S28 and S35 are the same defect wearing three faces. Each surface
reduces "the input was missing, malformed, or unparseable" and "the input was present
and agreed" to the same value — `None`, an empty mapping, a dropped line — and then
renders a PASS over it. The tests below are written as one file because the repair was
one rule, and a future regression on any of the three should read as a regression of the
rule rather than of an unrelated script.

Each test names the pre-repair verdict it pins against, because that verdict is what the
2026-08-01 reproduction controls actually observed in the parent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from .support import ADAPTER_LIB, ROOT, _load_script_module

ISSUE_RESOLVE_ADAPTER = _load_script_module(
    "issue_resolve_adapter_absent_input",
    ROOT / "skills" / "public" / "issue" / "scripts" / "resolve_adapter.py",
)
REBASELINE = _load_script_module(
    "dup_ratchet_rebaseline_absent_input",
    ROOT / "skills" / "public" / "quality" / "scripts" / "dup_ratchet_rebaseline.py",
)
CURRENT_RELEASE = _load_script_module(
    "current_release_absent_input",
    ROOT / "skills" / "public" / "release" / "scripts" / "current_release.py",
)


@pytest.fixture(autouse=True)
def _surface_tests_do_not_recheck_worktree(monkeypatch):
    """Keep surface-state tests in-process; Git cleanliness has its own boundary tests."""
    monkeypatch.setattr(CURRENT_RELEASE, "_git_status", lambda _repo: [])


# --- the shared parser channel (the root cause under S24) ---------------------------


def test_the_parser_reports_a_line_it_could_not_interpret():
    text = "version: 1\ndefault_org corca-typo\ndefault_repo: charness\n"
    parsed, uninterpreted = ADAPTER_LIB.load_yaml_report(text)

    assert parsed == {"version": 1, "default_repo": "charness"}
    assert [entry["line"] for entry in uninterpreted] == [2]
    assert uninterpreted[0]["reason"] == "no mapping separator"
    assert "default_org corca-typo" in uninterpreted[0]["text"]


def test_the_report_variant_never_changes_what_the_parser_returns():
    # The whole repair depends on this: every other adapter in the repo keeps calling
    # `load_yaml`, so the reporting variant must be observation-only.
    for text in (
        "a: 1\nb:\n  - x\n  - y\n",
        "- one\n- two\n",
        "key: value\nstray line\n",
        "block: |\n  first\n  second\n",
        "",
    ):
        assert ADAPTER_LIB.load_yaml_report(text)[0] == ADAPTER_LIB.load_yaml(text)


def test_a_top_level_list_is_reported_rather_than_silently_emptied():
    # `load_yaml` always returns a dict, so the `isinstance(raw, dict)` guard the issue
    # adapter used to carry could never fire and the file read as an empty mapping.
    parsed, uninterpreted = ADAPTER_LIB.load_yaml_report("- one\n- two\n")

    assert parsed == {}
    assert len(uninterpreted) == 2
    assert {entry["reason"] for entry in uninterpreted} == {"list item with no owning key"}


def test_a_clean_adapter_reports_nothing_uninterpreted():
    parsed, uninterpreted = ADAPTER_LIB.load_yaml_report(
        "version: 1\ndefault_org: corca-ai\nlabels:\n- bug\n- test\n"
    )

    assert parsed == {"version": 1, "default_org": "corca-ai", "labels": ["bug", "test"]}
    assert uninterpreted == []


# --- S24: a malformed issue adapter must not report itself valid --------------------


def _issue_adapter(tmp_path: Path, body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "issue-adapter.yaml").write_text(body, encoding="utf-8")
    return repo


def test_s24_a_missing_colon_is_reported_instead_of_silently_defaulted(tmp_path):
    # Pre-repair: valid=true, errors=[], warnings=[], default_org silently "corca-ai".
    # Post-repair it is a WARNING, not a refusal: the file is consumer-authored and the
    # the consumer-authored arming question is outside this check. `valid` deliberately stays True.
    repo = _issue_adapter(tmp_path, "version: 1\ndefault_org corca-typo\ndefault_repo: charness\n")

    payload = ISSUE_RESOLVE_ADAPTER.load_adapter(repo)

    assert payload["valid"] is True
    assert payload["errors"] == []
    assert any("default_org corca-typo" in warning for warning in payload["warnings"])
    assert any("line 2" in warning for warning in payload["warnings"])
    assert payload["data"]["default_org"] == "corca-ai"


def test_s24_a_top_level_list_is_reported(tmp_path):
    # Pre-repair: valid=true with an EMPTY warnings list, because the mapping guard was
    # unreachable rather than merely lenient.
    repo = _issue_adapter(tmp_path, "- one\n- two\n")

    payload = ISSUE_RESOLVE_ADAPTER.load_adapter(repo)

    assert len([w for w in payload["warnings"] if "not interpreted" in w]) == 2


def test_s24_a_document_marker_is_not_reported(tmp_path):
    # Legal YAML that many editors emit. Recording it would be a false finding, and the
    # first cut of this repair turned it into a hard refusal of the whole issue lane.
    repo = _issue_adapter(tmp_path, "---\nversion: 1\ndefault_org: acme\n")

    payload = ISSUE_RESOLVE_ADAPTER.load_adapter(repo)

    assert payload["valid"] is True
    assert [w for w in payload["warnings"] if "not interpreted" in w] == []
    assert payload["data"]["default_org"] == "acme"


def test_s24_an_unsupported_construct_returns_a_typed_refusal_not_a_traceback(tmp_path):
    # The parser raises on anchors/aliases. That used to escape as an uncaught ValueError,
    # so callers branching on `valid` never saw it — neither a refusal nor a pass.
    repo = _issue_adapter(tmp_path, "version: 1\ndefault_org: *anchor\n")

    payload = ISSUE_RESOLVE_ADAPTER.load_adapter(repo)

    assert payload["valid"] is False
    assert any("could not be parsed" in error for error in payload["errors"])


def test_s24_the_drop_inside_a_list_block_is_reported_too(tmp_path):
    # The fourth drop site: a line more indented than the list it sits under. The first
    # instrumentation pass missed it, which meant the measurement authorizing the arming
    # decision was blind to an entire class of drop.
    repo = _issue_adapter(tmp_path, "version: 1\nlabels:\n- bug\n  default_org corca-typo\n")

    payload = ISSUE_RESOLVE_ADAPTER.load_adapter(repo)

    assert any("over-indented line in list" in warning for warning in payload["warnings"])


def test_s24_the_shared_contract_loader_reports_too(tmp_path):
    # release/hotl/hitl/debug/retro/impl/gather share one loader. A missing colon on the
    # field that ARMS the S35 absence check used to read as an unset field.
    repo = tmp_path / "charness"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "version: 1\nrepo: charness\npackage_id: charness\n"
        "sync_command: noop\nquality_command: noop\n"
        "required_release_surfaces\n- claude_plugin\n",
        encoding="utf-8",
    )
    release_adapter = _load_script_module(
        "release_resolve_adapter_absent_input",
        ROOT / "skills" / "public" / "release" / "scripts" / "resolve_adapter.py",
    )

    payload = release_adapter.load_adapter(repo)

    assert any("required_release_surfaces" in warning for warning in payload["warnings"])
    assert payload["data"]["required_release_surfaces"] == []


def test_s24_a_well_formed_adapter_is_still_valid(tmp_path):
    repo = _issue_adapter(tmp_path, "version: 1\ndefault_org: corca-ai\ndefault_repo: charness\n")

    payload = ISSUE_RESOLVE_ADAPTER.load_adapter(repo)

    assert payload["valid"] is True
    assert payload["errors"] == []
    assert payload["data"]["default_org"] == "corca-ai"


def test_s24_the_checked_in_adapter_of_this_repo_reports_nothing():
    # The one file whose refusal would break this repo's own issue lane.
    payload = ISSUE_RESOLVE_ADAPTER.load_adapter(ROOT)

    assert payload["valid"] is True
    assert payload["errors"] == []
    assert [w for w in payload["warnings"] if "not interpreted" in w] == []


# --- S28: an unreadable baseline must not take the bootstrap path -------------------


class _Args:
    def __init__(self, *, confirm: bool, threshold: int = 5):
        self.confirm_baseline_delta = confirm
        self.baseline_delta_threshold = threshold


def _rebaseline_repo(tmp_path: Path, baseline_text: str | None) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "quality").mkdir(parents=True)
    baseline = repo / "charness-artifacts" / "quality" / "dup-ratchet-baseline.json"
    if baseline_text is not None:
        baseline.write_text(baseline_text, encoding="utf-8")
    return repo, baseline


def _stub_live_scan(monkeypatch, families: int = 50):
    members = {f"fam{index}": [f"h{index}a", f"h{index}b"] for index in range(families)}
    monkeypatch.setattr(
        REBASELINE._scan,
        "live_scan_for_rebaseline",
        lambda *args, **kwargs: (
            "charness-artifacts/quality/dup-ratchet-baseline.json",
            members,
            "nose-1.2.3",
            None,
        ),
    )
    return members


TRUNCATED = '{"schema": "dup-ratchet-gate-baseline", "code_families": [{"fingerp'


def test_s28_a_truncated_baseline_is_refused_not_overwritten(tmp_path, monkeypatch):
    # Pre-repair: {ok: true, status: "baseline-written", code_family_count: 50} — the
    # large-delta guard was skipped because an unreadable baseline reads as no baseline.
    _stub_live_scan(monkeypatch)
    repo, baseline = _rebaseline_repo(tmp_path, TRUNCATED)

    report = REBASELINE.write_baseline(repo, {}, _Args(confirm=False))

    assert report["ok"] is False
    assert report["status"] == "existing-baseline-unreadable"
    assert baseline.read_text(encoding="utf-8") == TRUNCATED


def test_s28_a_deliberate_rewrite_of_an_unreadable_baseline_still_proceeds(tmp_path, monkeypatch):
    _stub_live_scan(monkeypatch)
    repo, _ = _rebaseline_repo(tmp_path, TRUNCATED)

    report = REBASELINE.write_baseline(repo, {}, _Args(confirm=True))

    assert report["ok"] is True
    assert report["status"] == "baseline-written"


def test_s28_a_genuine_first_time_bootstrap_still_writes(tmp_path, monkeypatch):
    # The distinction the repair rests on: absent file != present-but-unreadable file.
    _stub_live_scan(monkeypatch)
    repo, baseline = _rebaseline_repo(tmp_path, None)

    report = REBASELINE.write_baseline(repo, {}, _Args(confirm=False))

    assert report["ok"] is True
    assert report["status"] == "baseline-written"
    assert baseline.is_file()


def test_s28_a_readable_baseline_with_a_small_delta_is_untouched_by_the_new_gate(
    tmp_path, monkeypatch
):
    members = _stub_live_scan(monkeypatch)
    repo, baseline = _rebaseline_repo(tmp_path, None)
    REBASELINE.write_gate_baseline(baseline, members, "nose-1.2.3")

    report = REBASELINE.write_baseline(repo, {}, _Args(confirm=False))

    assert report["ok"] is True
    assert report["status"] == "baseline-written"


# --- S35: a missing release surface must not read as a matching one -----------------


def _release_repo(tmp_path: Path, *, adapter: str | None, codex: bool) -> Path:
    repo = tmp_path / "charness"
    (repo / "packaging").mkdir(parents=True)
    (repo / "packaging" / "charness.json").write_text('{"version": "9.9.9"}\n', encoding="utf-8")
    claude = repo / "plugins" / "charness" / ".claude-plugin"
    claude.mkdir(parents=True)
    (claude / "plugin.json").write_text('{"version": "9.9.9"}\n', encoding="utf-8")
    if codex:
        codex_dir = repo / "plugins" / "charness" / ".codex-plugin"
        codex_dir.mkdir(parents=True)
        (codex_dir / "plugin.json").write_text('{"version": "9.9.9"}\n', encoding="utf-8")
    if adapter is not None:
        (repo / ".agents").mkdir(parents=True, exist_ok=True)
        (repo / ".agents" / "release-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


_DECLARING_ADAPTER = (
    "version: 1\nrepo: charness\npackage_id: charness\n"
    "sync_command: noop\nquality_command: noop\n"
    "required_release_surfaces:\n- claude_plugin\n- codex_plugin\n"
)


def test_s35_a_declared_surface_that_is_absent_is_drift(tmp_path):
    # Pre-repair: drift == [] — a codex plugin.json a failed sync never wrote was
    # indistinguishable from one that matches, and `drift` is what publish refuses on.
    repo = _release_repo(tmp_path, adapter=_DECLARING_ADAPTER, codex=False)

    payload = CURRENT_RELEASE.build_payload(repo)

    assert "codex_plugin" in payload["absent_surfaces"]
    assert any("codex_plugin=<absent>" in entry for entry in payload["drift"])


def test_s35_absence_is_legible_even_when_no_surface_is_declared(tmp_path):
    # A consumer that publishes claude-only must not be turned red by a list it never
    # wrote — but the absence must still be readable in the payload.
    repo = _release_repo(tmp_path, adapter=None, codex=False)

    payload = CURRENT_RELEASE.build_payload(repo)

    assert "codex_plugin" in payload["absent_surfaces"]
    assert payload["required_release_surfaces"] == []
    assert payload["drift"] == []


def test_s35_a_declared_surface_that_is_present_and_matching_is_not_drift(tmp_path):
    repo = _release_repo(tmp_path, adapter=_DECLARING_ADAPTER, codex=True)

    payload = CURRENT_RELEASE.build_payload(repo)

    assert "codex_plugin" not in payload["absent_surfaces"]
    assert payload["drift"] == []


def test_s35_a_version_mismatch_is_still_reported(tmp_path):
    repo = _release_repo(tmp_path, adapter=_DECLARING_ADAPTER, codex=True)
    (repo / "plugins" / "charness" / ".codex-plugin" / "plugin.json").write_text(
        '{"version": "1.0.0"}\n', encoding="utf-8"
    )

    payload = CURRENT_RELEASE.build_payload(repo)

    assert payload["drift"] == ["codex_plugin=1.0.0 != packaging_manifest=9.9.9"]


def test_s35_this_repo_declares_its_surfaces_and_has_none_absent():
    # The measurement behind arming: all three declared surfaces are present today, so
    # the declaration adds teeth without adding a single refusal to this repo's lane.
    # This reads the LIVE tree deliberately — the declaration is only honest while the
    # surfaces it names exist. Version drift is NOT asserted here: that is the release
    # gate's job, and duplicating it would fail the unit lane at any mid-sync moment.
    payload = CURRENT_RELEASE.build_payload(ROOT)

    assert payload["required_release_surfaces"] == [
        "claude_plugin",
        "codex_plugin",
        "claude_marketplace_version",
        "codex_marketplace_source_path",
    ]
    assert payload["absent_surfaces"] == []


def test_s35_an_unknown_declared_surface_warns_instead_of_being_ignored(tmp_path):
    repo = _release_repo(
        tmp_path,
        adapter=(
            "version: 1\nrepo: charness\npackage_id: charness\n"
            "sync_command: noop\nquality_command: noop\n"
            "required_release_surfaces:\n- claude_plugin\n- nonexistent_surface\n"
        ),
        codex=True,
    )

    payload = CURRENT_RELEASE.build_payload(repo)

    assert payload["required_release_surfaces"] == ["claude_plugin"]
    assert any("nonexistent_surface" in warning for warning in payload["adapter"]["warnings"])


def test_s35_an_absent_packaging_manifest_is_drift_not_silence(tmp_path):
    # The reference input the other surfaces are compared against. `expected is None`
    # used to skip the entire loop, so a deleted manifest rendered `drift: []` — the
    # batch's own rule, at the top of its own chain.
    repo = _release_repo(tmp_path, adapter=_DECLARING_ADAPTER, codex=True)
    (repo / "packaging" / "charness.json").unlink()

    payload = CURRENT_RELEASE.build_payload(repo)

    assert "packaging_manifest" in payload["absent_surfaces"]
    assert any("packaging_manifest=<absent>" in entry for entry in payload["drift"])


def test_s35_a_manifest_with_no_usable_version_is_not_called_absent(tmp_path):
    # `<absent>` would be a false claim about the filesystem: the file is right there.
    repo = _release_repo(tmp_path, adapter=_DECLARING_ADAPTER, codex=True)
    (repo / "packaging" / "charness.json").write_text('{"version": 1}\n', encoding="utf-8")

    payload = CURRENT_RELEASE.build_payload(repo)

    assert any("packaging_manifest=<no-version>" in entry for entry in payload["drift"])
    assert not any("packaging_manifest=<absent>" in entry for entry in payload["drift"])
    # The field named for the distinction must make it too: the file is right there.
    assert "packaging_manifest" not in payload["absent_surfaces"]


def test_s35_the_codex_marketplace_is_declarable_and_absence_shows(tmp_path):
    # The sweep row names marketplace.json alongside the codex plugin. It carries a source
    # path rather than a version, so it was outside the compared universe entirely.
    repo = _release_repo(
        tmp_path,
        adapter=(
            "version: 1\nrepo: charness\npackage_id: charness\n"
            "sync_command: noop\nquality_command: noop\n"
            "required_release_surfaces:\n- codex_marketplace_source_path\n"
        ),
        codex=True,
    )

    payload = CURRENT_RELEASE.build_payload(repo)

    assert "codex_marketplace_source_path" in payload["absent_surfaces"]
    assert any("codex_marketplace_source_path=<absent>" in entry for entry in payload["drift"])


# --- the measurement itself -----------------------------------------------------------


def _measure():
    return _load_script_module(
        "measure_adapter_yaml_uninterpreted_test",
        ROOT / "scripts" / "gates" / "measure_adapter_yaml_uninterpreted.py",
    )


def test_the_measurement_reports_a_clean_result_for_the_files_the_adapters_load():
    # Scoped to `.agents`, which is where the adapters this repo's skills actually parse
    # live. The wider `DEFAULT_ROOTS` scan stays a re-runnable measurement rather than a
    # standing gate: a legal 4-space-indent YAML anywhere under `docs/` would otherwise
    # fail this suite for a file no adapter ever reads.
    measure = _measure()

    report = measure.scan(ROOT, (".agents",))

    assert report["uninterpreted_line_count"] == 0, json.dumps(report["findings"], indent=2)
    assert report["unreadable"] == []
    assert report["scanned_files"] > 0


def test_the_measurement_exits_nonzero_when_it_finds_something(tmp_path, monkeypatch, capsys):
    # A measurement that prints its findings and exits 0 is the class it measures.
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "issue-adapter.yaml").write_text(
        "version: 1\ndefault_org corca-typo\n", encoding="utf-8"
    )
    measure = _measure()
    monkeypatch.setattr("sys.argv", ["measure", "--repo-root", str(tmp_path), "--roots", ".agents"])

    assert measure.main() == 1
    assert "default_org corca-typo" in capsys.readouterr().out


def test_the_measurement_exits_nonzero_on_a_file_it_could_not_parse(tmp_path, monkeypatch, capsys):
    # An unreadable input contributes zero findings; without this the report would be
    # "0 uninterpreted lines" over a corpus it never actually read.
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "issue-adapter.yaml").write_text(
        "version: 1\ndefault_org: *anchor\n", encoding="utf-8"
    )
    measure = _measure()
    monkeypatch.setattr("sys.argv", ["measure", "--repo-root", str(tmp_path), "--roots", ".agents"])

    assert measure.main() == 1
    # The retired `UNREADABLE <path>: <error>` line is the `unreadable` key now:
    # the refusal must still be attributed to the file that caused it.
    report = yaml.safe_load(capsys.readouterr().out)
    assert [entry["path"] for entry in report["unreadable"]] == [".agents/issue-adapter.yaml"]
    assert "parser refused" in report["unreadable"][0]["error"]


def test_the_measurement_emits_a_structured_payload(tmp_path, monkeypatch, capsys):
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "issue-adapter.yaml").write_text("version: 1\n", encoding="utf-8")
    measure = _measure()
    monkeypatch.setattr("sys.argv", ["measure", "--repo-root", str(tmp_path), "--roots", ".agents"])

    assert measure.main() == 0
    assert yaml.safe_load(capsys.readouterr().out)["uninterpreted_line_count"] == 0


# --- round-2 repairs: the fixes that carried the class they fixed --------------------


def test_a_document_marker_ends_a_list_instead_of_merging_the_next_document():
    # The round-1 repair skipped `---` in BOTH parser loops, which merged a second
    # document's items into the first document's list and CHANGED what `load_yaml`
    # returns — the sink's own class, introduced by the fix.
    parsed, uninterpreted = ADAPTER_LIB.load_yaml_report("labels:\n- bug\n---\n- other\n")

    assert parsed == {"labels": ["bug"]}
    assert [entry["reason"] for entry in uninterpreted] == ["list item with no owning key"]


def test_a_block_scalar_in_a_list_item_does_not_eat_its_sibling_key():
    # The list call site passed the LIST column where the item's first key sits two
    # deeper, so the block scalar consumed the sibling line into itself — silently.
    parsed, uninterpreted = ADAPTER_LIB.load_yaml_report(
        "steps:\n- run: |\n    echo hi\n  name: build\n"
    )

    assert parsed["steps"][0]["run"] == "echo hi\n"
    assert uninterpreted, "the dropped sibling key must at least be visible"


def test_a_nested_mapping_under_a_list_item_key_is_parsed():
    parsed, uninterpreted = ADAPTER_LIB.load_yaml_report("steps:\n- with:\n    a: 1\n")

    assert parsed == {"steps": [{"with": {"a": 1}}]}
    assert uninterpreted == []


def test_the_shared_loader_returns_a_typed_refusal_for_an_unsupported_construct(tmp_path):
    # The round-1 repair added this guard to the issue adapter only, leaving the loader
    # that serves nine skills — including the release drift check this slice hardens —
    # dying on a traceback.
    repo = tmp_path / "charness"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "release-adapter.yaml").write_text(
        "version: 1\nrepo: charness\npackage_id: *anchor\n", encoding="utf-8"
    )
    release_adapter = _load_script_module(
        "release_resolve_adapter_r2",
        ROOT / "skills" / "public" / "release" / "scripts" / "resolve_adapter.py",
    )

    payload = release_adapter.load_adapter(repo)

    assert payload["valid"] is False
    assert any("could not be parsed" in error for error in payload["errors"])


def test_an_unreadable_release_surface_is_not_called_absent(tmp_path):
    # `_version_at` used to raise on a half-written plugin.json — exactly what a failed
    # sync leaves — killing the check that exists to notice it.
    repo = _release_repo(
        tmp_path,
        adapter=(
            "version: 1\nrepo: charness\npackage_id: charness\n"
            "sync_command: noop\nquality_command: noop\n"
            "required_release_surfaces:\n- codex_plugin\n"
        ),
        codex=True,
    )
    (repo / "plugins" / "charness" / ".codex-plugin" / "plugin.json").write_text(
        '{"version": ', encoding="utf-8"
    )

    payload = CURRENT_RELEASE.build_payload(repo)

    assert any("codex_plugin=<unreadable>" in entry for entry in payload["drift"])
    assert "codex_plugin" not in payload["absent_surfaces"]


def test_the_packaging_manifest_is_not_declarable(tmp_path):
    # Accepting it would be a silent no-op that reads like it was honored.
    repo = _release_repo(
        tmp_path,
        adapter=(
            "version: 1\nrepo: charness\npackage_id: charness\n"
            "sync_command: noop\nquality_command: noop\n"
            "required_release_surfaces:\n- packaging_manifest\n"
        ),
        codex=True,
    )

    payload = CURRENT_RELEASE.build_payload(repo)

    assert payload["required_release_surfaces"] == []
    assert any("packaging_manifest" in w for w in payload["adapter"]["warnings"])


def test_the_measurement_refuses_an_empty_corpus(tmp_path, monkeypatch, capsys):
    # A clean result over zero files is the zero-denominator PASS this session closed as
    # sweep rows S1/S26/S30/S32 — inside the tool built to measure a different instance
    # of the same family.
    (tmp_path / ".agents").mkdir(parents=True)
    measure = _measure()
    monkeypatch.setattr("sys.argv", ["measure", "--repo-root", str(tmp_path), "--roots", ".agents"])

    assert measure.main() == 2
    assert "not a measurement" in capsys.readouterr().err


def test_the_measurement_roots_actually_bound_the_scan(tmp_path):
    # `--roots` used to be advisory: the repo-root glob ran unconditionally, so a scoped
    # run silently scanned more than it was asked to.
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "a.yaml").write_text("k: v\n", encoding="utf-8")
    (tmp_path / "loose.yaml").write_text("k: v\n", encoding="utf-8")
    measure = _measure()

    assert measure.scan(tmp_path, (".agents",))["scanned_files"] == 1
    assert measure.scan(tmp_path, (".", ".agents"))["scanned_files"] == 2


def test_dup_ratchet_rebaseline_records_which_fact_the_flag_covered(tmp_path, monkeypatch):
    _stub_live_scan(monkeypatch)
    repo, _ = _rebaseline_repo(tmp_path, TRUNCATED)

    report = REBASELINE.write_baseline(repo, {}, _Args(confirm=True))

    assert any("UNREADABLE" in message for message in report["messages"])


# --- lines the armed changed-line gate named as uncovered ----------------------------


def test_an_over_indented_line_outside_a_list_is_reported():
    # `adapter_lib.py:285` — the `over-indented line` drop site in `_parse_block`. The
    # sibling site inside a list had a test; this one did not, so the instrumentation
    # that authorized the arming decision was itself half-unproven.
    parsed, uninterpreted = ADAPTER_LIB.load_yaml_report("a: 1\nb: 2\n    stray: 3\n")

    assert [entry["reason"] for entry in uninterpreted] == ["over-indented line"]


def test_the_measurement_reports_a_file_it_cannot_decode(tmp_path, monkeypatch, capsys):
    # `measure_adapter_yaml_uninterpreted.py:69-71` — the OSError/UnicodeDecodeError arm.
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "a.yaml").write_bytes(b"\xff\xfe not utf-8 \xff")
    measure = _measure()
    monkeypatch.setattr("sys.argv", ["measure", "--repo-root", str(tmp_path), "--roots", ".agents"])

    assert measure.main() == 1
    report = yaml.safe_load(capsys.readouterr().out)
    assert [entry["path"] for entry in report["unreadable"]] == [".agents/a.yaml"]


def test_the_measurement_raises_if_the_report_variant_ever_diverges(tmp_path, monkeypatch):
    # `:81` — the AssertionError guard. It is the one thing standing between "the sink is
    # observation-only" and a silent behavior change, so it needs a test of its own.
    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "a.yaml").write_text("k: v\n", encoding="utf-8")
    measure = _measure()
    monkeypatch.setattr(measure.adapter_lib, "load_yaml", lambda text: {"different": True})

    try:
        measure.scan(tmp_path, (".agents",))
    except AssertionError as exc:
        assert "changed the parse result" in str(exc)
    else:  # pragma: no cover - the guard must fire
        raise AssertionError("the divergence guard did not fire")


@pytest.mark.boundary_contract(
    reason="__main__ dispatch smoke: the measurement script must be runnable as a program"
)
def test_the_measurement_runs_as_a_script(tmp_path):
    # `measure_adapter_yaml_uninterpreted.py:138` — the `__main__` guard. Only a
    # subprocess invocation reaches it, and the mutation coverage producer captures
    # subprocess-invoked CLI scripts, so this is the one shape that covers the line the
    # armed changed-line gate named.
    import subprocess
    import sys

    (tmp_path / ".agents").mkdir(parents=True)
    (tmp_path / ".agents" / "issue-adapter.yaml").write_text(
        "version: 1\ndefault_org corca-typo\n", encoding="utf-8"
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "gates" / "measure_adapter_yaml_uninterpreted.py"),
            "--repo-root",
            str(tmp_path),
            "--roots",
            ".agents",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "default_org corca-typo" in result.stdout


# --- D48: deleting the declaration must not buy a green PUBLISH ---------------------
#
# D48's recorded defect is disarm-by-deletion: "deleting those four adapter lines
# disarms it with nothing corroborating them." The operator's 2026-08-01 call was to
# close that direction only. It is closed at the irreversible boundary, not in the
# read-only status call: `current_release` still must not redden a lane a consumer
# never published, so `drift` is unchanged and the refusal lives in the publish gate.

PREFLIGHT = _load_script_module(
    "release_preflight_absent_input",
    ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_preflight.py",
)


def test_d48_an_undeclared_absence_is_uncorroborated_not_silently_clean(tmp_path):
    # Pre-repair: required == [] and drift == [], i.e. a clean verdict over a codex
    # plugin.json a failed sync had deleted. Verified against the pre-slice script.
    repo = _release_repo(tmp_path, adapter=None, codex=False)

    payload = CURRENT_RELEASE.build_payload(repo)

    assert payload["absence_corroboration"] == "uncorroborated"
    assert "codex_plugin" in payload["undeclared_absent_surfaces"]
    # Unchanged on purpose: a read-only status call levies no toll.
    assert payload["drift"] == []


def test_d48_publish_refuses_an_uncorroborated_absence(tmp_path):
    repo = _release_repo(tmp_path, adapter=None, codex=False)
    payload = CURRENT_RELEASE.build_payload(repo)

    blocker = PREFLIGHT.release_surface_blocker(payload, "9.9.9")

    assert blocker is not None
    assert "uncorroborated" in blocker
    assert "codex_plugin" in blocker


def test_d48_naming_an_absent_surface_as_required_is_still_drift_not_a_remedy(tmp_path):
    """`required_release_surfaces` means "these must exist", so it cannot be the opt-out.

    The first cut of this slice told consumers to declare there, which round 1 showed was
    unpublishable advice: every arm was red and no declaration existed that let a
    claude-only repo publish. This test pins that the field kept its old meaning.
    """
    declares_all_four = (
        "version: 1\nrepo: charness\npackage_id: charness\n"
        "sync_command: noop\nquality_command: noop\n"
        "required_release_surfaces:\n- claude_plugin\n- codex_plugin\n"
        "- claude_marketplace_version\n- codex_marketplace_source_path\n"
    )
    repo = _release_repo(tmp_path, adapter=declares_all_four, codex=False)

    payload = CURRENT_RELEASE.build_payload(repo)

    assert payload["absence_corroboration"] == "declared"
    assert payload["undeclared_absent_surfaces"] == []
    assert any("codex_plugin=<absent>" in entry for entry in payload["drift"])
    assert PREFLIGHT.release_surface_blocker(payload, "9.9.9") is not None


def test_d48_declaring_a_surface_unpublished_lets_a_partial_publisher_publish(tmp_path):
    """The actual remedy: a SECOND field, stating what this repo does not ship.

    This is why the corroboration arm is not the default-on toll D45/D48 refuse -- a
    consumer that genuinely publishes claude-only says so once, and publishes.
    """
    claude_only = (
        "version: 1\nrepo: charness\npackage_id: charness\n"
        "sync_command: noop\nquality_command: noop\n"
        "required_release_surfaces:\n- claude_plugin\n"
        "unpublished_release_surfaces:\n- codex_plugin\n"
        "- claude_marketplace_version\n- codex_marketplace_source_path\n"
    )
    repo = _release_repo(tmp_path, adapter=claude_only, codex=False)

    payload = CURRENT_RELEASE.build_payload(repo)

    assert payload["absence_corroboration"] == "declared"
    assert payload["undeclared_absent_surfaces"] == []
    assert payload["drift"] == []
    assert PREFLIGHT.release_surface_blocker(payload, "9.9.9") is None


def test_d48_a_present_but_corrupt_surface_is_drift_with_no_declaration_at_all(tmp_path):
    """The state a failed sync actually leaves, and the one the first cut missed.

    `unreadable`/`no-version` never entered `absent_surfaces`, so the corroboration arm
    could not see them and the declared-only drift arm let them through whenever the
    declaration was deleted -- disarm-by-deletion, fully alive, in the exact state D48
    describes. A file that is THERE and corrupt needs no declaration: a repo that does
    not ship the lane has no file.
    """
    repo = _release_repo(tmp_path, adapter=None, codex=True)
    (repo / "plugins" / "charness" / ".codex-plugin" / "plugin.json").write_text(
        '{"version": ', encoding="utf-8"
    )

    payload = CURRENT_RELEASE.build_payload(repo)

    # Present-but-corrupt is NOT absent -- that distinction is the point of `_state` --
    # so the corroboration arm cannot reach it and the drift arm must.
    assert "codex_plugin" not in payload["absent_surfaces"]
    assert any("codex_plugin=<unreadable>" in entry for entry in payload["drift"])
    assert PREFLIGHT.release_surface_blocker(payload, "9.9.9") is not None


def test_d48_packaging_manifest_absence_is_never_labelled_declared(tmp_path):
    """`packaging_manifest` is prepended to `absent` but is deliberately undeclarable.

    Scoping the verdict to `absent` rather than to the declarable subset reported
    "declared" over an absence nothing named and nothing could name.
    """
    repo = _release_repo(tmp_path, adapter=_DECLARING_ADAPTER, codex=True)
    (repo / "packaging" / "charness.json").unlink()

    payload = CURRENT_RELEASE.build_payload(repo)

    assert "packaging_manifest" in payload["absent_surfaces"]
    assert payload["absence_corroboration"] != "declared"


def test_d48_a_scalar_declaration_does_not_iterate_as_characters(tmp_path):
    scalar = (
        "version: 1\nrepo: charness\npackage_id: charness\n"
        "sync_command: noop\nquality_command: noop\n"
        "required_release_surfaces: claude_plugin\n"
    )
    repo = _release_repo(tmp_path, adapter=scalar, codex=True)

    payload = CURRENT_RELEASE.build_payload(repo)

    assert payload["required_release_surfaces"] == []


def test_d48_a_repo_with_nothing_absent_is_not_applicable_and_publishes(tmp_path):
    repo = _release_repo(tmp_path, adapter=_DECLARING_ADAPTER, codex=True)
    (repo / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (repo / ".claude-plugin" / "marketplace.json").write_text(
        '{"metadata": {"version": "9.9.9"}}\n', encoding="utf-8"
    )
    (repo / ".agents" / "plugins").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "plugins" / "marketplace.json").write_text(
        '{"plugins": [{"name": "charness", "source": {"path": "plugins/charness"}}]}\n',
        encoding="utf-8",
    )

    payload = CURRENT_RELEASE.build_payload(repo)

    assert payload["absent_surfaces"] == []
    assert payload["absence_corroboration"] == "not-applicable"
    assert PREFLIGHT.release_surface_blocker(payload, "9.9.9") is None


def test_d48_a_marketplace_listing_another_product_is_exemptable_not_permanent_drift(tmp_path):
    """The toll round 2 caught: `no-version` is reachable with nothing corrupt.

    The marketplace surfaces are per-REPO files, not per-package. A repo that also
    distributes some other product has a marketplace.json that parses fine and yields
    nothing for THIS package -- `no-version`, not `absent`. The first cut of the
    corrupt-surface arm fired unconditionally, so those consumers were permanently red
    through `drift` (which the run planner routes on) with no adapter line able to clear
    it -- exactly the default-on toll this entry refuses.
    """
    exempting = (
        "version: 1\nrepo: charness\npackage_id: charness\n"
        "sync_command: noop\nquality_command: noop\n"
        "unpublished_release_surfaces:\n- codex_marketplace_source_path\n"
    )
    repo = _release_repo(tmp_path, adapter=exempting, codex=True)
    (repo / ".agents" / "plugins").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "plugins" / "marketplace.json").write_text(
        '{"plugins": [{"name": "some-other-product", "source": {"path": "x"}}]}\n',
        encoding="utf-8",
    )

    payload = CURRENT_RELEASE.build_payload(repo)

    assert not any("codex_marketplace_source_path" in entry for entry in payload["drift"])


def test_d48_that_same_marketplace_is_drift_when_nothing_exempts_it(tmp_path):
    repo = _release_repo(tmp_path, adapter=None, codex=True)
    (repo / ".agents" / "plugins").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / "plugins" / "marketplace.json").write_text(
        '{"plugins": [{"name": "some-other-product", "source": {"path": "x"}}]}\n',
        encoding="utf-8",
    )

    payload = CURRENT_RELEASE.build_payload(repo)

    assert any("codex_marketplace_source_path=<no-version>" in e for e in payload["drift"])


def test_d48_an_unreadable_name_in_either_declaration_is_warned_not_dropped_silently(tmp_path):
    typo = (
        "version: 1\nrepo: charness\npackage_id: charness\n"
        "sync_command: noop\nquality_command: noop\n"
        "unpublished_release_surfaces:\n- codex-plugin\n"
    )
    repo = _release_repo(tmp_path, adapter=typo, codex=True)

    payload = CURRENT_RELEASE.build_payload(repo)

    assert any(
        "unpublished_release_surfaces names surface(s) this check does not read" in w
        for w in payload["adapter"]["warnings"]
    )


def test_d48_a_surface_named_in_both_declarations_warns_and_fails_closed(tmp_path):
    contradictory = (
        "version: 1\nrepo: charness\npackage_id: charness\n"
        "sync_command: noop\nquality_command: noop\n"
        "required_release_surfaces:\n- codex_plugin\n"
        "unpublished_release_surfaces:\n- codex_plugin\n"
    )
    repo = _release_repo(tmp_path, adapter=contradictory, codex=False)

    payload = CURRENT_RELEASE.build_payload(repo)

    assert any(
        "named as BOTH required and unpublished" in w for w in payload["adapter"]["warnings"]
    )
    # Fail-closed: `required` still wins.
    assert any("codex_plugin=<absent>" in entry for entry in payload["drift"])


def test_d48_the_refusal_message_names_the_field_that_actually_remedies_it(tmp_path):
    """Round 1's defect class, surviving in the only channel an operator reads.

    The refusal used to say "declare what this repo publishes", i.e. the REQUIRED field --
    which converts the uncorroborated pass into hard drift and refuses again.
    """
    repo = _release_repo(tmp_path, adapter=None, codex=False)

    blocker = PREFLIGHT.release_surface_blocker(CURRENT_RELEASE.build_payload(repo), "9.9.9")

    assert "unpublished_release_surfaces" in blocker


def test_d48_a_version_mismatch_still_blocks_publish(tmp_path):
    """The pre-existing arm, kept intact when the blocker moved out of the CLI."""
    # A fully-corroborated repo, so the version arm is the only one that can fire.
    complete = (
        "version: 1\nrepo: charness\npackage_id: charness\n"
        "sync_command: noop\nquality_command: noop\n"
        "required_release_surfaces:\n- claude_plugin\n- codex_plugin\n"
        "unpublished_release_surfaces:\n- claude_marketplace_version\n"
        "- codex_marketplace_source_path\n"
    )
    repo = _release_repo(tmp_path, adapter=complete, codex=True)
    payload = CURRENT_RELEASE.build_payload(repo)
    assert payload["drift"] == []

    blocker = PREFLIGHT.release_surface_blocker(payload, "1.2.3")

    assert blocker == "expected packaging manifest version `1.2.3`"


def test_d48_ensure_release_surface_raises_the_blocker_it_is_given(tmp_path, monkeypatch):
    """`ensure_release_surface` is the caller at the irreversible boundary; it must
    turn a blocker string into a refusal rather than reporting and continuing."""
    cli = _load_script_module(
        "publish_release_cli_absent_input",
        ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_cli.py",
    )
    monkeypatch.setattr(cli, "build_release_payload", lambda root: {"stub": True})
    monkeypatch.setattr(cli, "release_surface_blocker", lambda payload, version: "boom")

    with pytest.raises(SystemExit) as excinfo:
        cli.ensure_release_surface(tmp_path, "9.9.9")

    assert "boom" in str(excinfo.value)


def test_d48_ensure_release_surface_returns_the_disposition_when_there_is_no_blocker(
    tmp_path, monkeypatch
):
    """No blocker is a PASS the record can cite, not silence.

    The release record's no-drift sentence used to be an unconditional literal, so
    "this check ran and found nothing" and "this check never ran" rendered the same
    words. The pass has to be a value for the record to be able to tell them apart.
    """
    cli = _load_script_module(
        "publish_release_cli_absent_input_clean",
        ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_cli.py",
    )
    monkeypatch.setattr(
        cli,
        "build_release_payload",
        lambda root: {
            "surface_versions": {"packaging_manifest": "9.9.9"},
            "versioned_surfaces": ["packaging_manifest"],
            "presence_surfaces": [],
            "drift": [],
        },
    )
    monkeypatch.setattr(cli, "release_surface_blocker", lambda payload, version: None)

    disposition = cli.ensure_release_surface(tmp_path, "9.9.9", stage="unit")

    assert disposition["status"] == "passed"
    assert disposition["checked_version"] == "9.9.9"
    assert disposition["stage"] == "unit"
    assert disposition["versioned_surfaces"] == ["packaging_manifest"]
    assert disposition["presence_surfaces"] == []
    assert disposition["drift"] == []

    # The coverage the old `assert ... is None` form carried and this one would have
    # dropped: a payload with NEITHER key still returns a disposition rather than raising.
    # The surface lists are derived from `build_release_payload`, so a payload shaped unlike the
    # real one is exactly where a derivation crashes -- and this call sits after the bump,
    # where a traceback lands between the mutation and the record.
    monkeypatch.setattr(cli, "build_release_payload", lambda root: {"stub": True})

    minimal = cli.ensure_release_surface(tmp_path, "9.9.9", stage="unit")

    assert minimal["versioned_surfaces"] == []
    assert minimal["presence_surfaces"] == []
    assert minimal["drift"] == []
