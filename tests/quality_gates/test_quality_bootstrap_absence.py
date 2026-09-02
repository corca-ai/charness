"""A deliberate absence has to be representable, and the generator has to honor it.

These tests replay the reported loss: a customized adapter run through the bootstrap
had its comments destroyed and its deleted preset keys refilled with defaults pointing
at files the repo does not have. The two failures have separate causes and are proven
separately, because a single "the file did not change" assertion would hide one.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from scripts.adapter_lib import load_yaml
from scripts.adapter_yaml_render_lib import render_yaml_mapping
from scripts.quality_adapter_lib import (
    is_deliberately_absent,
    load_quality_adapter_permissive,
)
from scripts.quality_bootstrap_absence import remove_nested_absences

from .quality_bootstrap_support import _run_quality_bootstrap_adapter, seed_quality_repo

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
