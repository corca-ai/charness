"""A deliberate absence has to be representable, and the generator has to honor it.

These tests replay the reported loss: a customized adapter run through the bootstrap
had its comments destroyed and its deleted preset keys refilled with defaults pointing
at files the repo does not have. The two failures have separate causes and are proven
separately, because a single "the file did not change" assertion would hide one.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.adapter_lib import load_yaml, render_yaml_mapping
from scripts.quality_adapter_lib import (
    PATH_BEARING_ABSENCE_FIELDS,
    infer_quality_defaults,
    is_deliberately_absent,
    load_quality_adapter_permissive,
)

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


def _bootstrap(repo: Path) -> dict:
    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


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

    _bootstrap(repo)
    after_first = _adapter(repo).read_text(encoding="utf-8")
    second = _bootstrap(repo)

    assert second["adapter_status"] == "unchanged"
    assert _adapter(repo).read_text(encoding="utf-8") == after_first
    assert second["deliberately_absent"]["coverage_floor_policy"] == "this repo uses neither lefthook nor CI"
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


def test_rewrite_announces_the_comments_it_cannot_keep(tmp_path: Path) -> None:
    """A generator that cannot honor a customization says so; it does not revert quietly."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "# this gate deliberately does not exist here\n# declaring it sends the next session hunting\n"
        + CUSTOMIZED_ADAPTER,
        encoding="utf-8",
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))
    payload = json.loads(result.stdout)

    assert payload["comments_dropped"] == 2
    assert "deliberately_absent" in payload["customization_warning"]
    assert "WARN:" in result.stderr


def test_comment_claim_is_not_made_when_there_were_no_comments(tmp_path: Path) -> None:
    """The two claims are independent: no comments means no COMMENT claim, and nothing more.

    This used to assert total silence, which is what made the refill claim
    self-silencing — the first rewrite strips every comment, so from then on a
    refilled deletion was reverted with the tool saying nothing.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(CUSTOMIZED_ADAPTER, encoding="utf-8")

    payload = _bootstrap(repo)

    assert "comments_dropped" not in payload
    assert "comment line(s)" not in payload.get("customization_warning", "")
    # ...but the refill claim is still owed, because this rewrite did refill.
    assert payload["refilled_fields"]


def test_contradictory_absence_declaration_is_refused(tmp_path: Path) -> None:
    """Declared absent AND set is ambiguous; guessing either way would be a silent choice."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        CUSTOMIZED_ADAPTER + "coverage_floor_policy:\n  fail_below_pct: 10.0\n", encoding="utf-8"
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "is also set in this adapter" in result.stderr


def test_absence_without_a_reason_is_refused(tmp_path: Path) -> None:
    """A reasonless absence is indistinguishable from an oversight to the next reader."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text("deliberately_absent:\n  security_commands: \"\"\n" + CUSTOMIZED_ADAPTER.replace(
        "deliberately_absent:\n  coverage_floor_policy: this repo uses neither lefthook nor CI\n"
        "  coverage_fragile_margin_pp: no coverage tooling here\n"
        "  security_commands: no repo-owned security helper exists\n",
        "",
    ), encoding="utf-8")

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "must say why" in result.stderr


def test_structural_field_cannot_be_declared_absent(tmp_path: Path) -> None:
    """Declaring these absent yields an unresolvable adapter, not a customization."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text("deliberately_absent:\n  output_dir: not needed\n", encoding="utf-8")

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "structural" in result.stderr


def test_inline_comment_does_not_swallow_the_operators_value(tmp_path: Path) -> None:
    """A trailing comment used to be parsed into the value, so the value was dropped,
    the default silently won, and the report still called the field `preserved`."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "coverage_fragile_margin_pp: 2.0  # widened for the flaky suite\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["field_statuses"]["coverage_fragile_margin_pp"] == "preserved"
    assert "coverage_fragile_margin_pp: 2.0\n" in _adapter(repo).read_text(encoding="utf-8")
    # The comment itself is still destroyed by the rewrite, so it must be announced.
    assert payload["comments_dropped"] == 1


def test_unrecognized_absence_declaration_is_warned_not_silently_honored(tmp_path: Path) -> None:
    """A typo'd field name would otherwise look declared while still being refilled."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        CUSTOMIZED_ADAPTER.replace("coverage_floor_policy:", "coverage_flor_policy:"), encoding="utf-8"
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))
    payload = json.loads(result.stdout)

    assert result.returncode == 0, result.stderr
    assert any("coverage_flor_policy" in warning for warning in payload["absence_warnings"])
    assert "WARN:" in result.stderr
    # The real field kept its default, which is exactly what the warning is about.
    assert payload["field_statuses"]["coverage_floor_policy"] == "defaulted"


def test_loss_warning_names_only_fields_it_actually_wrote(tmp_path: Path) -> None:
    """Listing every unset field buries the one that matters and trains the warning away."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text("# a comment worth keeping\n" + CUSTOMIZED_ADAPTER, encoding="utf-8")

    payload = _bootstrap(repo)
    rewritten = _adapter(repo).read_text(encoding="utf-8")
    warning = payload["customization_warning"]

    assert "refilled" in warning
    for field in payload["refilled_fields"]:
        assert f"\n{field}:" in f"\n{rewritten}", f"{field} was named but never written"
    # Fields the renderer drops as empty must not be named.
    assert "vendored_paths" not in payload["refilled_fields"]


def test_empty_absence_declaration_is_accepted(tmp_path: Path) -> None:
    """`deliberately_absent: {}` is legal YAML and obviously means "nothing declared"."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\ndeliberately_absent: {}\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["deliberately_absent"] == {}


def test_fresh_repo_write_makes_no_intent_loss_claim(tmp_path: Path) -> None:
    """There is no prior file, so there is no operator intent to report losing."""
    repo = seed_quality_repo(tmp_path)

    payload = _bootstrap(repo)

    assert payload["adapter_status"] == "written"
    assert "comments_dropped" not in payload


def test_resolution_carries_the_declaration_and_names_where_it_does_not_bite(tmp_path: Path) -> None:
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

    assert payload["field_statuses"]["coverage_floor_policy"] == "preserved"
    assert "fail_below_pct: 90.0" in _adapter(repo).read_text(encoding="utf-8")


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
    assert json.loads(result.stdout)["deliberately_absent"] == {}


def test_comment_counter_agrees_with_the_parser_on_apostrophes(tmp_path: Path) -> None:
    """A second implementation of "where does the comment start" disagreed with the parser.

    The parser stripped the comment; the counter read the apostrophe as an unclosed
    quote and saw none — so the annotation was destroyed and nothing was reported.
    """
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: it's-a-repo  # renamed upstream, keep this\n"
        "output_dir: charness-artifacts/quality\n" + CUSTOMIZED_ADAPTER.split("version: 1\n")[1].replace(
            "repo: demo\n", ""
        ),
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["comments_dropped"] >= 1
    assert "customization_warning" in payload


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
    _adapter(repo).write_text("# an annotation a real run would leave alone\n" + canonical, encoding="utf-8")

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo), "--dry-run")
    payload = json.loads(result.stdout)

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

    assert not any("output_dir" in warning and "preset default" in warning for warning in resolved["warnings"])


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
    assert 'f: plain text\n' in render_yaml_mapping([("deliberately_absent", {"f": "plain text"})])


def test_rationale_that_looks_like_a_scalar_round_trips_as_text(tmp_path: Path) -> None:
    """A reason of `true`/`123` must not reload as a bool/int and fail the next run."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "deliberately_absent:\n  security_commands: \"true\"\n  coverage_floor_policy: \"123\"\n",
        encoding="utf-8",
    )

    _bootstrap(repo)
    second = _bootstrap(repo)

    assert second["deliberately_absent"] == {"security_commands": "true", "coverage_floor_policy": "123"}


def test_path_bearing_map_names_keys_that_actually_exist() -> None:
    """The map is a hand-maintained ruler over another module's defaults.

    A renamed default key would silently make an entry inert — the declaration would
    stop marking a phantom path and nothing would say so. (This caught a real slip:
    `dup_ratchet` was first written with `review_path`/`baseline_path`, which do not
    exist.)
    """
    defaults = infer_quality_defaults(Path("."))
    for field, path_keys in PATH_BEARING_ABSENCE_FIELDS.items():
        assert field in defaults, f"{field} is not a resolved field at all"
        value = defaults[field]
        for key in path_keys:
            assert isinstance(value, dict) and key in value, f"{field}.{key} does not exist"


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
    assert unasserted["coverage_floor_policy.exemption_list_path"] == "scripts/coverage-floor-exemptions.txt"
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

    assert "comments_dropped" not in payload
    assert payload["refilled_fields"], "a rewrite that refilled defaults must say so"
    assert "coverage_floor_policy" in payload["refilled_fields"]
    assert "absent ON PURPOSE" in payload["customization_warning"]


def test_a_converged_adapter_still_says_nothing(tmp_path: Path) -> None:
    """Not "warn more often": no rewrite, no claim. The refill claim also quiets itself
    once the refilled fields are written, because they then count as explicit."""
    repo = seed_quality_repo(tmp_path)
    _bootstrap(repo)

    second = _bootstrap(repo)

    assert second["adapter_status"] == "unchanged"
    assert "refilled_fields" not in second
    assert "customization_warning" not in second
