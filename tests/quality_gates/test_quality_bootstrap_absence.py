"""A deliberate absence has to be representable, and the generator has to honor it.

These tests replay the reported loss: a customized adapter run through the bootstrap
had its comments destroyed and its deleted preset keys refilled with defaults pointing
at files the repo does not have. The two failures have separate causes and are proven
separately, because a single "the file did not change" assertion would hide one.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.adapter_lib import load_yaml
from scripts.adapter_yaml_render_lib import render_yaml_mapping
from scripts.quality_adapter_lib import (
    ABSENCE_STRUCTURAL_FIELDS,
    PATH_BEARING_ABSENCE_FIELDS,
    infer_quality_defaults,
    is_deliberately_absent,
    load_quality_adapter_permissive,
    names_a_filesystem_location,
    path_bearing_entries,
)
from scripts.quality_bootstrap_absence import remove_nested_absences
from scripts.quality_bootstrap_lib import build_bootstrap_state

from .quality_bootstrap_support import _run_quality_bootstrap_adapter, seed_quality_repo
from .support import ROOT

CUSTOMIZED_ADAPTER = """version: 1
repo: demo
language: en
output_dir: charness-artifacts/quality
preset_id: portable-defaults
customized_from: portable-defaults
deliberately_absent:
  coverage_floor_policy: this repo uses neither lefthook nor CI
  coverage_fragile_margin_pp: no coverage tooling here
  security_commands: no repo-owned security helper exists
preset_lineage:
- python-quality
gate_commands:
- npm run gate
"""


def _adapter(repo: Path) -> Path:
    return repo / ".agents" / "quality-adapter.yaml"


def _bootstrap(repo: Path, *extra: str) -> dict:
    result = _run_quality_bootstrap_adapter("--repo-root", str(repo), *extra)
    assert result.returncode == 0, result.stderr
    # `bootstrap_adapter.py` reports in YAML since the `--json` removal. YAML is a JSON
    # superset, so this also reads the compact-JSON fallback used without PyYAML.
    return yaml.safe_load(result.stdout)


def _change(payload: dict, surface: str) -> dict:
    return next(change for change in payload["requested_changes"] if change["surface"] == surface)


def test_declared_absence_is_not_refilled_with_defaults(tmp_path: Path) -> None:
    """The reported key resurrection: absent-on-purpose must stay absent."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(CUSTOMIZED_ADAPTER, encoding="utf-8")

    payload = _bootstrap(repo)
    rewritten = _adapter(repo).read_text(encoding="utf-8")

    for field in ("coverage_floor_policy", "coverage_fragile_margin_pp", "security_commands"):
        assert payload["field_statuses"][field] == "deliberately-absent"
        assert f"\n{field}:" not in f"\n{rewritten}"
    # The specific false signal from the report: a coverage policy pointing at gates
    # that do not exist in this repo.
    for resurrected in ("lefthook_path", "ci_workflow_glob", "exemption_list_path"):
        assert resurrected not in rewritten
    # The customization the operator kept must survive alongside the deletions.
    assert "npm run gate" in rewritten


def test_dotted_absence_survives_bootstrap_and_resolution(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\nlanguage: en\n"
        "output_dir: charness-artifacts/quality\n"
        "preset_id: portable-defaults\ncustomized_from: portable-defaults\n"
        "deliberately_absent:\n"
        "  coverage_floor_policy.lefthook_path: this repo uses checked-in git hooks\n"
        "  coverage_floor_policy.ci_workflow_glob: this repo has no CI workflow\n"
        "  coverage_floor_policy.exemption_list_path: this repo has no exemption list\n"
        "coverage_floor_policy:\n"
        "  min_statements_threshold: 30\n"
        "  fail_below_pct: 80.0\n"
        "  warn_ceiling_pct: 95.0\n"
        "  floor_drift_lock_pp: 1.0\n"
        "  gate_script_pattern: '*-quality-gate.sh'\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo, "--migrate")
    resolved = load_quality_adapter_permissive(repo)
    policy = resolved["data"]["coverage_floor_policy"]

    assert payload["adapter_status"] == "migrated"
    assert "coverage_floor_policy" not in {
        change["surface"] for change in payload["requested_changes"]
    }
    assert "lefthook_path" not in policy
    assert "ci_workflow_glob" not in policy
    assert "exemption_list_path" not in policy
    assert is_deliberately_absent(resolved["data"], "coverage_floor_policy.lefthook_path")
    assert _bootstrap(repo)["adapter_status"] == "unchanged"


def test_nested_absence_skips_a_scalar_parent_and_continues_to_later_paths() -> None:
    data = {"not_a_mapping": "preserve", "policy": {"remove": True, "keep": True}}

    remove_nested_absences(
        data,
        {
            "not_a_mapping.nested.remove": "cannot descend into a scalar",
            "policy.remove": "deliberately absent",
        },
    )

    assert data == {"not_a_mapping": "preserve", "policy": {"keep": True}}


def test_dotted_absence_refuses_a_leaf_that_is_also_set(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n"
        "  coverage_floor_policy.lefthook_path: no lefthook here\n"
        "coverage_floor_policy:\n  lefthook_path: lefthook.yml\n",
        encoding="utf-8",
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "declared absent but is also set" in result.stderr


def test_dotted_absence_typo_is_reported_instead_of_becoming_inert(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n"
        "  coverage_floor_policy.lefthook_pat: typo should be visible\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert "coverage_floor_policy.lefthook_pat" in payload["absence_warnings"][0]


def test_declared_absence_silences_the_matching_setup_nag(tmp_path: Path) -> None:
    """Prompting to install a gate the repo deliberately lacks is the same failure."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(CUSTOMIZED_ADAPTER, encoding="utf-8")

    payload = _bootstrap(repo)

    assert "security_commands" not in [entry["field"] for entry in payload["deferred_setup"]]


def test_rationale_survives_a_second_bootstrap(tmp_path: Path) -> None:
    """The rationale is data, so regeneration must not be able to drop it."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(CUSTOMIZED_ADAPTER, encoding="utf-8")

    _bootstrap(repo, "--migrate")
    after_first = _adapter(repo).read_text(encoding="utf-8")
    second = _bootstrap(repo)

    assert second["adapter_status"] == "unchanged"
    assert _adapter(repo).read_text(encoding="utf-8") == after_first
    assert (
        second["deliberately_absent"]["coverage_floor_policy"]
        == "this repo uses neither lefthook nor CI"
    )
    assert "this repo uses neither lefthook nor CI" in after_first


def test_adapter_without_the_field_is_unaffected(tmp_path: Path) -> None:
    """Every consumer adapter in the wild predates the field; back-compat is a criterion."""
    repo = seed_quality_repo(tmp_path)

    payload = _bootstrap(repo)

    assert payload["adapter_status"] == "written"
    assert payload["deliberately_absent"] == {}
    assert "deliberately_absent" not in _adapter(repo).read_text(encoding="utf-8")
    assert payload["field_statuses"]["coverage_floor_policy"] == "defaulted"
    assert "deliberately-absent" not in payload["field_statuses"].values()


def test_resolution_carries_the_declaration_and_names_where_it_does_not_bite(
    tmp_path: Path,
) -> None:
    """Keeping the file from being rewritten is only half the job.

    Resolution still fills unset fields from repo defaults, so a repo that declared
    `coverage_floor_policy` absent still resolves to the preset default naming
    `lefthook.yml`. The declaration must survive resolution rather than being dropped,
    and the gap must be stated rather than left as a false signal.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(CUSTOMIZED_ADAPTER, encoding="utf-8")

    resolved = load_quality_adapter_permissive(repo)

    assert resolved["data"]["deliberately_absent"]["coverage_floor_policy"] == (
        "this repo uses neither lefthook nor CI"
    )
    assert any(
        "coverage_floor_policy" in warning and "preset default" in warning
        for warning in resolved["warnings"]
    )


def test_trailing_comment_does_not_swallow_a_nested_block(tmp_path: Path) -> None:
    """`key:  # note` used to fall past every dispatch branch to the scalar one.

    The key resolved to the empty string, its whole nested block was dropped as
    over-indented, the default won, and the field still counted as explicitly set —
    the reported failure, reached through a comment instead of a deletion.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "coverage_floor_policy:  # tightened; the preset thresholds do not apply here\n"
        "  fail_below_pct: 90.0\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    # `augmented`, not `preserved`: the block IS read (that is what this test was
    # written to prove — the trailing comment no longer swallows it), and the merge
    # then refills the seven sub-keys it does not set. Calling that `preserved` was
    # the #489 false statement. The fact under test is unchanged and is now asserted
    # directly: `fail_below_pct` survived, so the nested block was not dropped.
    assert payload["field_statuses"]["coverage_floor_policy"] == "augmented"
    assert payload["field_statuses"]["coverage_floor_policy"] != "defaulted"
    assert "fail_below_pct: 90.0" in _adapter(repo).read_text(encoding="utf-8")


def test_a_partially_deleted_block_is_reported_augmented_and_names_its_refills(
    tmp_path: Path,
) -> None:
    """#489, from the reproduction pasted on the issue.

    An operator who keeps `coverage_floor_policy:` and deletes one key from it gets
    the missing sub-keys refilled from the preset — `lefthook_path: lefthook.yml`
    returns, pointing at a file the repo does not have. The status said `preserved`
    and stderr was EMPTY, because the field-level refill claim filters on
    `defaulted` and this field is explicit. So the report asserted the opposite of
    what the merge did, and made no claim at all.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "coverage_floor_policy:\n  fail_below_pct: 90.0\n"
        "  # lefthook_path deliberately removed - this repo has no lefthook\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["field_statuses"]["coverage_floor_policy"] == "augmented"
    change = _change(payload, "coverage_floor_policy")
    assert "lefthook_path" in change["requested_value"], (
        "the sub-key the operator deleted must be named"
    )
    assert change["current_value"]["fail_below_pct"] == 90.0
    warning = payload["customization_warning"]
    assert "lefthook_path" in warning


def test_a_blank_sub_key_value_is_a_refill_too(tmp_path: Path) -> None:
    """Round 1 of the bounded review: the first cut keyed on the sub-key's ABSENCE, so
    the other common way to empty one — leaving the value blank — still reported
    `preserved` with an empty stderr.

    `lefthook_path:` with nothing after it parses to `{}` (adapter_lib._parse_empty_value),
    so the KEY is present, no merge branch accepts `{}`, and `lefthook.yml` came back
    anyway. Same defect as the deleted line, reached by a gesture at least as common.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "coverage_floor_policy:\n  fail_below_pct: 90.0\n  lefthook_path:\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["field_statuses"]["coverage_floor_policy"] == "augmented"
    assert "lefthook_path" in _change(payload, "coverage_floor_policy")["requested_value"]


def test_a_wrong_typed_sub_key_the_merge_drops_is_a_refill_too(tmp_path: Path) -> None:
    """The worst of the three spellings, and the one the first cut missed most quietly.

    `min_statements_threshold: 30.5` against an int default fails every type branch in
    the merge, so the default wins — and the bootstrap then REWRITES the adapter with
    it, so the operator's value is gone from disk before `validate_coverage_floor_policy`
    (which runs at resolution, not here) could ever complain about it. Silent,
    unreported, and irreversible unless the report says so.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "coverage_floor_policy:\n  fail_below_pct: 90.0\n  min_statements_threshold: 30.5\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["field_statuses"]["coverage_floor_policy"] == "augmented"
    assert (
        "min_statements_threshold" in _change(payload, "coverage_floor_policy")["requested_value"]
    )


def test_an_int_written_against_a_float_default_is_not_a_refill(tmp_path: Path) -> None:
    """The false-positive control for the test above. `fail_below_pct: 80` against the
    `80.0` default is the operator's own value, accepted by the merge's int-or-float
    branch, and `80 == 80.0` — so widening the rule to catch wrong types must not start
    calling ordinary integer spellings a refill."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "coverage_floor_policy:\n  fail_below_pct: 80\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    change = _change(payload, "coverage_floor_policy")
    assert change["current_value"]["fail_below_pct"] == 80
    assert change["requested_value"]["fail_below_pct"] == 80.0


def test_the_prompt_asset_policy_sibling_reports_its_refills_too(tmp_path: Path) -> None:
    """One fixed instance and an unexamined twin is how this class comes back.

    `merge_prompt_asset_policy` is the same shape as the coverage-floor merge and had
    the same unconditional `preserved`. The rule now has ONE statement
    (`_mark_subkey_refills`) called per merged field, so a third merged field inherits
    it instead of re-deriving it.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "prompt_asset_policy:\n  min_multiline_chars: 40\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["field_statuses"]["prompt_asset_policy"] == "augmented"
    requested = _change(payload, "prompt_asset_policy")["requested_value"]
    assert "source_globs" in requested and "exemption_globs" in requested
    assert requested["min_multiline_chars"] == 40


def test_a_block_replaced_by_a_scalar_reports_every_sub_key(tmp_path: Path) -> None:
    """The maximal version of the same loss. `coverage_floor_policy: "see docs"` keeps
    NOTHING the operator wrote — the merge never even reads it — and the first cut
    returned an empty refill list for it, reporting the largest possible refill as
    `preserved`."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        'coverage_floor_policy: "see docs/quality.md"\n',
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["field_statuses"]["coverage_floor_policy"] == "augmented"
    assert "fail_below_pct" in _change(payload, "coverage_floor_policy")["requested_value"]


def test_a_fully_specified_block_is_still_preserved_and_claims_nothing(tmp_path: Path) -> None:
    """The false-refusal control. An operator who writes every sub-key out gets
    `preserved` and no sub-key claim — otherwise the new status would fire on every
    adapter that spells its policy out, and the word would stop meaning anything."""
    from scripts.quality_policy_defaults import DEFAULT_COVERAGE_FLOOR_POLICY

    repo = seed_quality_repo(tmp_path)
    block = "\n".join(
        f"  {key}: {value!r}".replace("'", '"') if isinstance(value, str) else f"  {key}: {value}"
        for key, value in DEFAULT_COVERAGE_FLOOR_POLICY.items()
    )
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "coverage_floor_policy:\n" + block + "\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["field_statuses"]["coverage_floor_policy"] == "preserved"
    assert "coverage_floor_policy" not in (payload.get("refilled_subkeys") or {})


def test_trailing_comment_does_not_break_empty_collections(tmp_path: Path) -> None:
    """`{}` and `[]` are compared against the raw post-colon text, so a comment hid them."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent: {}  # nothing declared yet\n"
        "gate_commands: []  # deliberately none\n",
        encoding="utf-8",
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout)["deliberately_absent"] == {}


def test_comment_counter_agrees_with_the_parser_on_apostrophes(tmp_path: Path) -> None:
    """A second implementation of "where does the comment start" disagreed with the parser.

    The parser stripped the comment; the counter read the apostrophe as an unclosed
    quote and saw none — so the annotation was destroyed and nothing was reported.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: it's-a-repo  # renamed upstream, keep this\n"
        "output_dir: charness-artifacts/quality\n"
        + CUSTOMIZED_ADAPTER.split("version: 1\n")[1].replace("repo: demo\n", ""),
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["adapter_status"] == "conflict"
    assert "renamed upstream, keep this" in _adapter(repo).read_text(encoding="utf-8")
    assert "comments_dropped" not in payload
    assert "customization_warning" in payload

    migrated = _run_quality_bootstrap_adapter("--repo-root", str(repo), "--migrate")
    assert migrated.returncode == 0, migrated.stderr
    assert "renamed upstream, keep this" in _adapter(repo).read_text(encoding="utf-8")


def test_declaring_a_rendered_field_absent_is_not_called_a_typo(tmp_path: Path) -> None:
    """Several fields are rendered without ever carrying an inferred default."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  public_spec_section_exemptions: this repo ships no public spec\n"
        "  recommendation_defaults_version: we do not track preset recommendations\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert "absence_warnings" not in payload
    assert payload["field_statuses"]["public_spec_section_exemptions"] == "deliberately-absent"


def test_dry_run_claims_no_loss_when_a_real_run_would_not_write(tmp_path: Path) -> None:
    """A plan that cries wolf on every run is a plan an operator stops reading."""
    repo = seed_quality_repo(tmp_path)
    _bootstrap(repo)
    canonical = _adapter(repo).read_text(encoding="utf-8")
    _adapter(repo).write_text(
        "# an annotation a real run would leave alone\n" + canonical, encoding="utf-8"
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo), "--dry-run")
    payload = yaml.safe_load(result.stdout)

    assert payload["would_do"] == "unchanged"
    assert "comments_dropped" not in payload
    assert result.stderr == ""


def test_resolution_warns_instead_of_dropping_a_malformed_declaration(tmp_path: Path) -> None:
    """Silently ignoring what the file says is the failure this field exists to close."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent: security_commands\n",
        encoding="utf-8",
    )

    resolved = load_quality_adapter_permissive(repo)

    assert any("must be a mapping" in warning for warning in resolved["warnings"])


def test_non_mapping_declaration_is_refused_by_the_bootstrap(tmp_path: Path) -> None:
    """A bare scalar is an easy hand-edit slip and must not be read as "nothing declared"."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent: security_commands\n",
        encoding="utf-8",
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "must be a mapping" in result.stderr
    assert "got str" in result.stderr


def test_empty_field_name_is_refused(tmp_path: Path) -> None:
    """A nameless declaration names nothing, so honoring it would honor a blank."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        'deliberately_absent:\n  "": no field here\n',
        encoding="utf-8",
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "is not a non-empty string" in result.stderr


def test_non_string_reason_is_refused_by_the_bootstrap(tmp_path: Path) -> None:
    """An unquoted number reads as an int, not a reason a later reader can use."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  security_commands: 481\n",
        encoding="utf-8",
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "must say why" in result.stderr


def test_resolution_warns_about_entries_it_discards(tmp_path: Path) -> None:
    """The resolver only warns where the bootstrap refuses, but it must not be silent."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  security_commands: 481\n",
        encoding="utf-8",
    )

    resolved = load_quality_adapter_permissive(repo)

    assert any("entries ignored" in warning for warning in resolved["warnings"])
    assert "deliberately_absent" not in resolved["data"]


def test_resolution_does_not_name_a_structural_field_as_still_defaulted(tmp_path: Path) -> None:
    """The bootstrap refuses these outright, so reporting one as unhonored is noise."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  output_dir: not needed here\n",
        encoding="utf-8",
    )

    resolved = load_quality_adapter_permissive(repo)

    assert not any(
        "output_dir" in warning and "preset default" in warning for warning in resolved["warnings"]
    )


def test_declared_absence_of_an_unset_field_reports_no_default_conflict(tmp_path: Path) -> None:
    """A field that resolves to an empty value is genuinely honored, so it is not named."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  vendored_paths: nothing is vendored here\n",
        encoding="utf-8",
    )

    resolved = load_quality_adapter_permissive(repo)

    assert resolved["data"]["deliberately_absent"] == {"vendored_paths": "nothing is vendored here"}
    assert not any("preset default" in warning for warning in resolved["warnings"])


def test_scalar_shaped_strings_round_trip_through_the_renderer() -> None:
    """A string emitted bare that reloads as a bool/int changes type across a write."""
    for text in ("true", "TRUE", "false", "null", "~", "123", "-2", "1.5", "1e3"):
        rendered = render_yaml_mapping([("deliberately_absent", {"f": text})])
        assert load_yaml(rendered)["deliberately_absent"]["f"] == text, text
    # A value that is genuinely plain must NOT be needlessly quoted.
    assert "f: plain text\n" in render_yaml_mapping([("deliberately_absent", {"f": "plain text"})])


def test_rationale_that_looks_like_a_scalar_round_trips_as_text(tmp_path: Path) -> None:
    """A reason of `true`/`123` must not reload as a bool/int and fail the next run."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        'deliberately_absent:\n  security_commands: "true"\n  coverage_floor_policy: "123"\n',
        encoding="utf-8",
    )

    _bootstrap(repo)
    second = _bootstrap(repo)

    assert second["deliberately_absent"] == {
        "security_commands": "true",
        "coverage_floor_policy": "123",
    }


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
