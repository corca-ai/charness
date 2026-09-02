"""The quality adapter lifecycle must preserve intent until migration is explicit."""

from __future__ import annotations

from pathlib import Path

import yaml

import scripts.adapters.quality_bootstrap_lib as bootstrap_lib
import scripts.adapters.quality_bootstrap_lifecycle as lifecycle
from scripts.adapters.quality_adapter_lib import load_quality_adapter_permissive

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


def test_lifecycle_helpers_cover_empty_and_uninterpreted_boundaries(monkeypatch) -> None:
    assert lifecycle.normalized_intent_matches(None, "version: 1\n") is False
    monkeypatch.setattr(lifecycle, "load_yaml", lambda text: [] if text == "existing" else {})
    changes = lifecycle.conflict_changes("existing", "rendered", {})
    assert changes[0]["surface"] == "adapter"
    assert lifecycle.conflict_advisory([]) is None
    assert lifecycle.preserved_comment_fragments(None) == []


def test_unclassified_difference_is_still_reported_as_a_conflict(tmp_path: Path, monkeypatch) -> None:
    repo = seed_quality_repo(tmp_path)
    adapter_path = _adapter(repo)
    adapter_path.write_text("current\n", encoding="utf-8")
    monkeypatch.setattr(
        bootstrap_lib,
        "build_bootstrap_state",
        lambda _repo_root: ({"output_dir": "charness-artifacts/quality", "preset_lineage": []}, {}, []),
    )
    monkeypatch.setattr(lifecycle, "render_bootstrap_adapter", lambda _data, _statuses: "generated\n")
    monkeypatch.setattr(lifecycle, "plan_generated_write", lambda _existing, _rendered: "differs")
    monkeypatch.setattr(lifecycle, "normalized_intent_matches", lambda _existing, _rendered: False)
    monkeypatch.setattr(lifecycle, "conflict_changes", lambda _existing, _rendered, _statuses: [])

    report = lifecycle.bootstrap_quality_adapter(
        repo_root=repo,
        output_path=Path(".agents/quality-adapter.yaml"),
        report_path=Path(".charness/quality/bootstrap.json"),
        dry_run=True,
    )

    assert report["adapter_status"] == "dry-run"
    assert report["requested_changes"][0]["surface"] == "adapter"


def test_rewrite_announces_the_comments_it_cannot_keep(tmp_path: Path) -> None:
    """A conflicting adapter is preserved and the advisory stays actionable."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "# this gate deliberately does not exist here\n# declaring it sends the next session hunting\n"
        + CUSTOMIZED_ADAPTER,
        encoding="utf-8",
    )

    before = _adapter(repo).read_text(encoding="utf-8")
    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))
    payload = yaml.safe_load(result.stdout)

    assert payload["adapter_status"] == "conflict"
    assert _adapter(repo).read_text(encoding="utf-8") == before
    assert "this gate deliberately does not exist here" in before
    assert payload["requested_changes"]
    assert all({"surface", "requested_change", "reason", "next_action"} <= set(change) for change in payload["requested_changes"])
    assert "--migrate" in payload["customization_warning"]
    assert "WARN:" in result.stderr


def test_explicit_migration_reports_rewrites_and_retains_comments(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    original = (
        "# keep this explanation\n"
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "gate_commands:\n- npm run gate  # the only gate\n"
    )
    _adapter(repo).write_text(original, encoding="utf-8")

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo), "--migrate")
    payload = yaml.safe_load(result.stdout)
    migrated = _adapter(repo).read_text(encoding="utf-8")

    assert result.returncode == 0, result.stderr
    assert payload["adapter_status"] == "migrated"
    assert payload["migration_changes"]
    assert "concept_paths" in {change["surface"] for change in payload["migration_changes"]}
    assert payload["comments_preserved"] == 2
    assert "# keep this explanation" in migrated
    assert "# the only gate" in migrated
    assert migrated != original
    assert result.stderr == ""


def test_matching_normalized_intent_with_comments_is_a_silent_noop(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _bootstrap(repo)
    adapter_path = _adapter(repo)
    original = adapter_path.read_text(encoding="utf-8")
    annotated = "# operator annotation\n" + original
    adapter_path.write_text(annotated, encoding="utf-8")

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))
    payload = yaml.safe_load(result.stdout)

    assert payload["adapter_status"] == "unchanged"
    assert adapter_path.read_text(encoding="utf-8") == annotated
    assert result.stderr == ""


def test_comment_claim_is_not_made_when_there_were_no_comments(tmp_path: Path) -> None:
    """No comments means no COMMENT claim, and nothing more."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(CUSTOMIZED_ADAPTER, encoding="utf-8")

    payload = _bootstrap(repo)

    assert payload["adapter_status"] == "conflict"
    assert "comments_dropped" not in payload
    assert "requested_changes" in payload
    assert "--migrate" in payload["customization_warning"]


def test_contradictory_absence_declaration_is_refused(tmp_path: Path) -> None:
    """Declared absent AND set is ambiguous; guessing would be a silent choice."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        CUSTOMIZED_ADAPTER + "coverage_floor_policy:\n  fail_below_pct: 10.0\n", encoding="utf-8"
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "is also set in this adapter" in result.stderr


def test_absence_without_a_reason_is_refused(tmp_path: Path) -> None:
    """A reasonless absence is indistinguishable from an oversight."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "deliberately_absent:\n  security_commands: \"\"\n" + CUSTOMIZED_ADAPTER.replace(
            "deliberately_absent:\n  coverage_floor_policy: this repo uses neither lefthook nor CI\n"
            "  coverage_fragile_margin_pp: no coverage tooling here\n"
            "  security_commands: no repo-owned security helper exists\n",
            "",
        ),
        encoding="utf-8",
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "must say why" in result.stderr


def test_structural_field_cannot_be_declared_absent(tmp_path: Path) -> None:
    """Declaring these absent yields an unresolvable adapter."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text("deliberately_absent:\n  output_dir: not needed\n", encoding="utf-8")

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))

    assert result.returncode == 1
    assert "structural" in result.stderr


def test_inline_comment_does_not_swallow_the_operators_value(tmp_path: Path) -> None:
    """A trailing comment must not turn the operator's value into a default."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        "version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n"
        "coverage_fragile_margin_pp: 2.0  # widened for the flaky suite\n",
        encoding="utf-8",
    )

    payload = _bootstrap(repo)

    assert payload["field_statuses"]["coverage_fragile_margin_pp"] == "preserved"
    assert "coverage_fragile_margin_pp: 2.0  # widened for the flaky suite\n" in _adapter(repo).read_text(encoding="utf-8")
    assert "comments_dropped" not in payload
    assert payload["adapter_status"] == "conflict"


def test_unrecognized_absence_declaration_is_warned_not_silently_honored(tmp_path: Path) -> None:
    """A typo'd field name must not silently suppress the real field."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        CUSTOMIZED_ADAPTER.replace("coverage_floor_policy:", "coverage_flor_policy:"), encoding="utf-8"
    )

    result = _run_quality_bootstrap_adapter("--repo-root", str(repo))
    payload = yaml.safe_load(result.stdout)

    assert result.returncode == 0, result.stderr
    assert any("coverage_flor_policy" in warning for warning in payload["absence_warnings"])
    assert "WARN:" in result.stderr
    assert payload["field_statuses"]["coverage_floor_policy"] == "defaulted"


def test_loss_warning_names_only_fields_it_actually_wrote(tmp_path: Path) -> None:
    """Listing every unset field buries the one that matters."""
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text("# a comment worth keeping\n" + CUSTOMIZED_ADAPTER, encoding="utf-8")

    payload = _bootstrap(repo)
    rewritten = _adapter(repo).read_text(encoding="utf-8")
    warning = payload["customization_warning"]

    assert payload["adapter_status"] == "conflict"
    assert "--migrate" in warning
    assert rewritten.startswith("# a comment worth keeping\n")
    assert "vendored_paths" not in {change["surface"] for change in payload["requested_changes"]}


def test_empty_absence_declaration_is_accepted(tmp_path: Path) -> None:
    """`deliberately_absent: {}` is legal YAML."""
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


def test_adapter_and_report_paths_must_not_alias_on_first_or_repeated_run(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    shared = ".agents/quality-adapter.yaml"

    first = _run_quality_bootstrap_adapter("--repo-root", str(repo), "--output", shared, "--report-path", shared)
    assert first.returncode == 1
    assert "same file" in first.stderr
    assert not _adapter(repo).exists()

    _bootstrap(repo)
    before = _adapter(repo).read_text(encoding="utf-8")
    repeated = _run_quality_bootstrap_adapter("--repo-root", str(repo), "--output", shared, "--report-path", shared)
    assert repeated.returncode == 1
    assert "same file" in repeated.stderr
    assert _adapter(repo).read_text(encoding="utf-8") == before


def test_uninterpreted_adapter_lines_are_refused_before_migration(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    original = "version: 1\nrepo demo-typo\noutput_dir: charness-artifacts/quality\n"
    _adapter(repo).write_text(original, encoding="utf-8")

    for extra in ((), ("--migrate",)):
        result = _run_quality_bootstrap_adapter("--repo-root", str(repo), *extra)
        assert result.returncode == 1
        assert "uninterpreted YAML lines" in result.stderr
        assert _adapter(repo).read_text(encoding="utf-8") == original


def test_migration_preserves_quoted_hash_values_and_trailing_comments(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        'version: 1\nrepo: "https://example.test/a # fragment" # annotation\n'
        "output_dir: charness-artifacts/quality\n",
        encoding="utf-8",
    )

    migrated = _run_quality_bootstrap_adapter("--repo-root", str(repo), "--migrate")
    assert migrated.returncode == 0, migrated.stderr
    text = _adapter(repo).read_text(encoding="utf-8")
    assert "# annotation" in text
    resolved = load_quality_adapter_permissive(repo)
    assert resolved["data"]["repo"] == "https://example.test/a # fragment"

    second = _bootstrap(repo)
    assert second["adapter_status"] == "unchanged"


def test_migration_preserves_quoted_hash_list_values_and_trailing_comments(tmp_path: Path) -> None:
    repo = seed_quality_repo(tmp_path)
    _adapter(repo).write_text(
        'version: 1\nrepo: demo\noutput_dir: charness-artifacts/quality\n'
        'gate_commands:\n- "https://example.test/a # fragment" # annotation\n',
        encoding="utf-8",
    )

    migrated = _run_quality_bootstrap_adapter("--repo-root", str(repo), "--migrate")
    assert migrated.returncode == 0, migrated.stderr
    text = _adapter(repo).read_text(encoding="utf-8")
    assert "# annotation" in text
    resolved = load_quality_adapter_permissive(repo)
    assert resolved["data"]["gate_commands"] == ["https://example.test/a # fragment"]
