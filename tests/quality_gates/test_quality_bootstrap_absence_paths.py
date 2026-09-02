"""Path-bearing absence mapping and refill-reporting tests for quality bootstrap.

This module owns the filesystem-path side of deliberate absence: which defaults
must be marked, which structural fields are excluded, and how nested refills are
reported. Keeping that contract together separates it from scalar absence and
parser round-trip coverage.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.adapters.quality_adapter_lib import (
    ABSENCE_STRUCTURAL_FIELDS,
    PATH_BEARING_ABSENCE_FIELDS,
    infer_quality_defaults,
    is_deliberately_absent,
    load_quality_adapter_permissive,
    names_a_filesystem_location,
    path_bearing_entries,
)
from scripts.adapters.quality_bootstrap_lib import build_bootstrap_state

from .support import ROOT
from .test_quality_bootstrap_absence import (
    _adapter,
    _bootstrap,
    _change,
    _run_quality_bootstrap_adapter,
    seed_quality_repo,
)

# Fields whose default names a filesystem location but which are deliberately NOT
# treated, each with the reason. Every entry must be structural (declaring one absent is
# refused outright), which the test below asserts — an unenforced allowance would let a
# bogus exclusion silence the completeness guard field-wide.
_PATH_BEARING_EXCLUSIONS = {
    "output_dir": "structural — declaring it absent is refused outright by the bootstrap",
    "repo": "structural — and it is the repo directory name, which may contain a dot",
}


def test_path_bearing_map_is_complete() -> None:
    """Re-derive the field set from live defaults; fail if a phantom path would go unnamed.

    The set is hand-maintained over another module's defaults, and the warning it feeds
    reads as an exhaustive list. Its first version named `mutation_testing.workflow_path`
    and silently omitted the three paths under `report_paths` — one of four, presented as
    all four. This test re-derives with the SAME ruler the runtime marking uses
    (`path_bearing_entries`, imported rather than restated), so the guard cannot admit a
    narrower rule than the one it documents.
    """
    defaults = infer_quality_defaults(Path("."))
    derived = {field for field, value in defaults.items() if path_bearing_entries(value, field)}

    unmapped = sorted(derived - PATH_BEARING_ABSENCE_FIELDS - set(_PATH_BEARING_EXCLUSIONS))
    assert not unmapped, (
        f"these fields have a path-bearing default but are neither treated nor excluded: {unmapped}. "
        "Add them to PATH_BEARING_ABSENCE_FIELDS, or to _PATH_BEARING_EXCLUSIONS with a reason."
    )


def test_path_bearing_exclusions_are_honest() -> None:
    """An exclusion is the one way to make the completeness test green without treating a
    field, so it may only name a field the bootstrap refuses outright anyway."""
    assert set(_PATH_BEARING_EXCLUSIONS) <= ABSENCE_STRUCTURAL_FIELDS
    assert all(reason.strip() for reason in _PATH_BEARING_EXCLUSIONS.values())
    assert not (PATH_BEARING_ABSENCE_FIELDS & set(_PATH_BEARING_EXCLUSIONS))


def test_the_ruler_admits_what_it_documents() -> None:
    """ "contains `/` or ends in a file extension, and no whitespace" — as stated."""
    for path in (
        "lefthook.yml",
        ".github/workflows/*.yml",
        "coverage.xml",
        "lcov.info",
        "AGENTS.md",
        "a/b",
    ):
        assert names_a_filesystem_location(path), path
    for not_a_path in (
        "17 */3 * * *",
        "Covered by pytest:\\s+`tests/[^`]+`",
        "en",
        "default",
        "",
        "provenance-allow",
    ):
        assert not names_a_filesystem_location(not_a_path), not_a_path


def test_nested_and_list_paths_are_reachable() -> None:
    """A shape the walker cannot reach is a phantom path the warning silently omits."""
    entries = path_bearing_entries(
        {
            "report_paths": {"summary_md": "reports/mutation/summary.md"},
            "probes": [{"log": "reports/probe.log"}, "docs/x.md", "not-a-path"],
        },
        "f",
    )
    assert entries == {
        "f.report_paths.summary_md": "reports/mutation/summary.md",
        "f.probes[0].log": "reports/probe.log",
        "f.probes[1]": "docs/x.md",
    }


def test_every_mapped_path_is_actually_marked_when_declared_absent(tmp_path: Path) -> None:
    """Every path in a treated field's default must actually be marked at runtime."""
    repo = seed_quality_repo(tmp_path)
    declared = "\n".join(
        f"  {field}: declared absent for this test" for field in sorted(PATH_BEARING_ABSENCE_FIELDS)
    )
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        f"deliberately_absent:\n{declared}\n",
        encoding="utf-8",
    )

    marked = load_quality_adapter_permissive(repo)["data"]["deliberately_absent_unasserted_paths"]

    defaults = infer_quality_defaults(Path("."))
    for field in PATH_BEARING_ABSENCE_FIELDS:
        for key in path_bearing_entries(defaults[field], field):
            assert key in marked, f"{key} is path-bearing in the defaults but was never marked"


def test_declared_absence_marks_the_phantom_paths_it_does_not_claim(tmp_path: Path) -> None:
    """The reported harm: a resolved default naming files the repo does not have."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  coverage_floor_policy: this repo uses neither lefthook nor CI\n",
        encoding="utf-8",
    )

    resolved = load_quality_adapter_permissive(repo)
    unasserted = resolved["data"]["deliberately_absent_unasserted_paths"]

    assert unasserted["coverage_floor_policy.lefthook_path"] == "lefthook.yml"
    assert unasserted["coverage_floor_policy.ci_workflow_glob"] == ".github/workflows/*.yml"
    assert (
        unasserted["coverage_floor_policy.exemption_list_path"]
        == "scripts/coverage-floor-exemptions.txt"
    )
    # The value itself is unchanged, so no consumer that indexes it breaks.
    assert resolved["data"]["coverage_floor_policy"]["lefthook_path"] == "lefthook.yml"
    assert any("do not go looking for them" in w for w in resolved["warnings"])


def test_declared_universes_absence_marks_phantom_patterns(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  universes: this repo declares no quality file families\n",
        encoding="utf-8",
    )

    resolved = load_quality_adapter_permissive(repo)
    unasserted = resolved["data"]["deliberately_absent_unasserted_paths"]

    assert unasserted["universes.python_sources[0]"] == "scripts/*.py"
    assert unasserted["universes.specdown_config"] == "specdown.json"
    assert any("universes" in warning for warning in resolved["warnings"])


def test_is_deliberately_absent_is_the_single_call_a_consumer_makes(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  coverage_floor_policy: neither lefthook nor CI here\n",
        encoding="utf-8",
    )

    data = load_quality_adapter_permissive(repo)["data"]

    assert is_deliberately_absent(data, "coverage_floor_policy") is True
    assert is_deliberately_absent(data, "gate_commands") is False
    assert is_deliberately_absent({}, "coverage_floor_policy") is False


def test_non_path_bearing_absence_marks_nothing(tmp_path: Path) -> None:
    """Thresholds and rule names assert nothing about the filesystem, so they are left alone."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  coverage_fragile_margin_pp: no coverage tooling here\n",
        encoding="utf-8",
    )

    resolved = load_quality_adapter_permissive(repo)

    assert "deliberately_absent_unasserted_paths" not in resolved["data"]
    assert not any("do not go looking" in w for w in resolved["warnings"])


def test_refill_is_reported_even_when_the_adapter_has_no_comments(tmp_path: Path) -> None:
    """The first rewrite makes every adapter comment-free, so gating the refill claim on
    comments meant the tool went permanently quiet about undoing a repo's decisions."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\ngate_commands:\n- npm run gate\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["adapter_status"] == "conflict"
    assert "comments_dropped" not in payload
    assert payload["requested_changes"]
    assert "--migrate" in payload["customization_warning"]


def test_a_converged_adapter_still_says_nothing(tmp_path: Path) -> None:
    """Not "warn more often": no rewrite, no claim. The refill claim also quiets itself
    once the refilled fields are written, because they then count as explicit."""
    repo = seed_quality_repo(tmp_path)
    _bootstrap(repo)

    second = _bootstrap(repo)

    assert second["adapter_status"] == "unchanged"
    assert "refilled_fields" not in second
    assert "customization_warning" not in second


def test_a_rewrite_that_reverts_nothing_says_nothing(tmp_path: Path) -> None:
    """The third state: a real rewrite that costs the operator nothing.

    Reachable through the trigger from the original report — a benign `concept_paths`
    augmentation forces a write on an already-converged adapter. Neither claim is owed,
    so the tool must stay silent rather than warn on the mere fact of writing.
    """
    repo = seed_quality_repo(tmp_path)
    _bootstrap(repo)
    assert _bootstrap(repo)["adapter_status"] == "unchanged"

    # A newly detected concept path is a legitimate merge, not a reversion.
    (repo / "charness-artifacts" / "quality").mkdir(parents=True, exist_ok=True)
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(
        "# report\n", encoding="utf-8"
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))
    payload = yaml.safe_load(result.stdout)

    assert payload["adapter_status"] == "conflict"
    assert "concept_paths" in {change["surface"] for change in payload["requested_changes"]}
    assert "--migrate" in payload["customization_warning"]
    assert "WARN:" in result.stderr


def test_a_partially_written_nested_block_names_its_leaves_end_to_end(tmp_path: Path) -> None:
    """#493, through the REAL merge and the real report rather than a fixture.

    Every earlier proof in this family stopped at the granularity of the instance that
    was reported — whole-field, then sub-key — and the next instance sat one level below
    it. Unit-testing the recursion against a hand-built merged dict would repeat that:
    it proves the function, not that a dotted name survives `describe_intent_loss`'s two
    filters (`augmented` status, and the field appearing in what was written) into the
    report an operator actually reads.

    `summary_md` is CUSTOMISED on purpose. That is the arm where the merged block stops
    equalling the default, which is what used to make a partially refilled block vanish
    from the report entirely instead of merely being reported coarsely.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "mutation_testing:\n  report_paths:\n    summary_md: custom/summary.md\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["field_statuses"]["mutation_testing"] == "augmented"
    change = _change(payload, "mutation_testing")
    assert change["requested_value"]["report_paths"]["sample_md"]
    assert change["requested_value"]["report_paths"]["log"]
    assert change["requested_value"]["report_paths"]["summary_md"] == "custom/summary.md"
    assert change["current_value"]["report_paths"]["summary_md"] == "custom/summary.md"
    assert "--migrate" in payload["customization_warning"]


def test_issue_496_suppresses_only_the_two_inert_command_leaves(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "mutation_testing:\n  commands:\n"
        "    full: pytest --mutate\n    summary: python3 scripts/summarize.py\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)
    change = _change(payload, "mutation_testing")
    assert change["current_value"]["commands"]["full"] == "pytest --mutate"
    assert change["requested_value"]["commands"]["sample"] == ""
    warning = payload["customization_warning"]
    assert "--migrate" in warning
    assert "review `mutation_testing`" in warning
    assert "commands.dry_run" not in warning
    assert "commands.sample" not in warning
    assert "drop the whole" not in warning.lower()
    assert all(
        not surface.startswith("commands.")
        for surface in (item["surface"] for item in payload["requested_changes"])
    )
    state, _, _ = build_bootstrap_state(repo)
    refills = state["_subkey_refills"]["mutation_testing"]
    assert "commands.dry_run" not in refills
    assert "commands.sample" not in refills
    rewritten = _adapter(repo).read_text(encoding="utf-8")
    assert "full: pytest --mutate" in rewritten
    assert "summary: python3 scripts/summarize.py" in rewritten


def test_mutation_command_filter_keeps_missing_required_slot_reportable(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "mutation_testing:\n  commands:\n    full: pytest --mutate\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)
    requested = _change(payload, "mutation_testing")["requested_value"]["commands"]
    assert requested["full"] == "pytest --mutate"
    assert requested["summary"] == ""
    state, _, _ = build_bootstrap_state(repo)
    assert "commands.summary" in state["_subkey_refills"]["mutation_testing"]


def test_explicit_empty_command_slots_are_not_reclassified(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "mutation_testing:\n  commands:\n"
        "    dry_run: ''\n    sample: ''\n"
        "    full: pytest --mutate\n    summary: python3 scripts/summarize.py\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)
    requested = _change(payload, "mutation_testing")["requested_value"]["commands"]
    assert requested["dry_run"] == ""
    assert requested["sample"] == ""
    state, _, _ = build_bootstrap_state(repo)
    refills = state["_subkey_refills"]["mutation_testing"]
    assert "commands.dry_run" not in refills
    assert "commands.sample" not in refills


def test_prompt_asset_empty_scope_remains_reportable_and_warning_is_safe(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "prompt_asset_policy:\n  min_multiline_chars: 40\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)
    assert "exemption_globs" in _change(payload, "prompt_asset_policy")["requested_value"]
    assert "--migrate" in payload["customization_warning"]
    state, _, _ = build_bootstrap_state(repo)
    assert "exemption_globs" in state["_subkey_refills"]["prompt_asset_policy"]


@pytest.mark.boundary_contract(
    reason="prove the generated quality bootstrap mirror runs from its installed layout and matches the source payload"
)
def test_plugin_bootstrap_matches_source_for_issue_496_fixture(tmp_path: Path) -> None:
    adapter = (
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "mutation_testing:\n  commands:\n"
        "    full: pytest --mutate\n    summary: python3 scripts/summarize.py\n"
    )
    source_repo = seed_quality_repo(tmp_path / "source")
    plugin_repo = seed_quality_repo(tmp_path / "plugin")
    _adapter(source_repo).write_text(adapter, encoding="utf-8")
    _adapter(plugin_repo).write_text(adapter, encoding="utf-8")

    source_result = _run_quality_bootstrap_adapter("--repo-root", str(source_repo))
    assert source_result.returncode == 0, source_result.stderr
    source = yaml.safe_load(source_result.stdout)
    plugin = subprocess.run(
        [
            sys.executable,
            str(
                ROOT
                / "plugins"
                / "charness"
                / "skills"
                / "quality"
                / "scripts"
                / "bootstrap_adapter.py"
            ),
            "--repo-root",
            str(plugin_repo),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert plugin.returncode == 0, plugin.stderr
    plugin_payload = yaml.safe_load(plugin.stdout)
    assert plugin_payload == source
    assert plugin.stderr == source_result.stderr


def test_mutation_testing_validates_where_the_other_policies_refill(tmp_path: Path) -> None:
    """The doc claim about `mutation_testing`, pinned so it cannot drift again.

    `bootstrap-posture.md` states the absent/blank/wrong-typed three-way refill rule for
    all three policy blocks. It is `coverage_floor_policy` and `prompt_asset_policy` only:
    `mutation_testing` validates. Two rounds of review each corrected this sentence and
    the FIRST correction was itself wrong — it said every blank sub-key errors, which is
    false for a blank nested BLOCK header. That is the one spelling accepted silently.
    """
    errors = {
        "blank scalar": "mutation_testing:\n  score_break:\n",
        "wrong-typed scalar": "mutation_testing:\n  score_break: nope\n",
        "blank nested leaf": "mutation_testing:\n  report_paths:\n    summary_md:\n",
    }
    for label, body in errors.items():
        repo = seed_quality_repo(tmp_path / label.replace(" ", "-"))
        _adapter(repo).write_text(
            "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n" + body,
            encoding="utf-8",
        )
        with pytest.raises(Exception):
            _bootstrap(repo)

    # ...and the one that is accepted: a blank nested BLOCK header refills the whole
    # block silently, so it reports the coarse block name rather than erroring.
    repo = seed_quality_repo(tmp_path / "blank-block")
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "mutation_testing:\n  score_break: 70\n  report_paths:\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert "report_paths" in _change(payload, "mutation_testing")["requested_value"]
