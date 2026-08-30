"""Acceptance checks for the mutation workflow's fresh-install render path.

This is the ONLY way the mutation workflow reaches a consumer repo: the installed
plugin copy of `propose_mutation_testing.py` renders `templates/mutation-tests.yml`
into the adapter's `workflow_path`, once, at first install. `--execute` refuses to
overwrite an existing workflow and only runs while the adapter block is `missing`,
so there is no re-render path and no second chance.

The existing `test_quality_mutation_testing.py` a3 cases drive the script from
`skills/public/quality/scripts/`. That is the authoring layout, not the delivery
one: the plugin copy lives under `skills/quality/scripts/`, so a template path
written relative to the repo root resolved to a nonexistent file there and the
install crashed *after* it had already appended the adapter scaffold. Every test
passed while the only real delivery path was broken. These cases drive the
materialized plugin export itself.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import load_path_module
from tests.repo_copy import clone_seeded_charness_repo

from .support import ROOT, run_script

PLUGIN_PROPOSE = "plugins/charness/skills/quality/scripts/propose_mutation_testing.py"
SOURCE_PROPOSE = "skills/public/quality/scripts/propose_mutation_testing.py"


def _seed_consumer_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    lines = ["version: 1", "repo: demo", "output_dir: charness-artifacts/quality"]
    (repo / ".agents" / "quality-adapter.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return repo


def test_plugin_copy_renders_the_workflow_into_a_fresh_repo(tmp_path: Path) -> None:
    """The delivery path, end to end, from the artifact a consumer actually installs."""
    repo = _seed_consumer_repo(tmp_path)

    result = run_script(PLUGIN_PROPOSE, "--repo-root", str(repo), "--execute")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] != "missing", payload

    workflow = repo / ".github" / "workflows" / "mutation-tests.yml"
    assert workflow.is_file(), "the one delivery path did not produce a workflow"
    rendered = workflow.read_text(encoding="utf-8")
    # The cron is substituted at install time because GitHub parses `schedule.cron`
    # before any job step runs, so runtime adapter parsing cannot reach it.
    assert "MUTATION_SCHEDULE_CRON_PLACEHOLDER" not in rendered
    assert 'cron: "17 */3 * * *"' in rendered
    assert (repo / ".agents" / "quality-adapter.yaml").read_text(
        encoding="utf-8"
    ).count("mutation_testing:") == 1
    # Anchored to the shipped template, not just to "a cron is present": a truncated
    # or corrupted template that still substitutes the cron would pass a
    # placeholder-absent check and would also pass the identical-renders test below,
    # since both sides would be equally wrong.
    template = (ROOT / PLUGIN_PROPOSE).parent / "templates" / "mutation-tests.yml"
    expected = template.read_text(encoding="utf-8").replace(
        "MUTATION_SCHEDULE_CRON_PLACEHOLDER", "17 */3 * * *"
    )
    assert rendered == expected


def test_plugin_copy_and_source_render_identical_workflows(tmp_path: Path) -> None:
    """The authoring layout and the delivery layout must not drift. If they can
    produce different workflows, every test against the source copy is evidence
    about a file no consumer ever runs."""
    from_source = _seed_consumer_repo(tmp_path / "a")
    from_plugin = _seed_consumer_repo(tmp_path / "b")

    source_result = run_script(SOURCE_PROPOSE, "--repo-root", str(from_source), "--execute")
    plugin_result = run_script(PLUGIN_PROPOSE, "--repo-root", str(from_plugin), "--execute")

    assert source_result.returncode == 0, source_result.stderr
    assert plugin_result.returncode == 0, plugin_result.stderr
    source_workflow = (from_source / ".github" / "workflows" / "mutation-tests.yml").read_text(
        encoding="utf-8"
    )
    plugin_workflow = (from_plugin / ".github" / "workflows" / "mutation-tests.yml").read_text(
        encoding="utf-8"
    )
    assert source_workflow == plugin_workflow


@pytest.mark.release_only
def test_execute_refuses_before_touching_the_adapter_when_the_template_is_missing(
    tmp_path: Path, seeded_charness_repo: Path
) -> None:
    """The install has two writes and no rollback. The template must be checked
    before the adapter is appended to, or a failed install leaves a fresh repo with
    a scaffolded adapter and no workflow -- and since `--execute` only runs while
    the block is `missing`, the recovery path is a hand edit. This is the exact
    partial-write the plugin-copy bug produced."""
    repo = _seed_consumer_repo(tmp_path)
    adapter = repo / ".agents" / "quality-adapter.yaml"
    before = adapter.read_text(encoding="utf-8")

    # A real plugin tree with its `templates/` directory removed -- the shape the
    # plugin-copy bug produced, where the script resolves but its template does not.
    install = clone_seeded_charness_repo(tmp_path / "install", seeded_charness_repo)
    broken = (
        install / "plugins" / "charness" / "skills" / "quality" / "scripts"
        / "propose_mutation_testing.py"
    )
    assert broken.is_file()
    shutil.rmtree(broken.parent / "templates")

    result = run_script(str(broken), "--repo-root", str(repo), "--execute")

    assert result.returncode != 0
    assert "workflow template not found" in result.stderr
    assert adapter.read_text(encoding="utf-8") == before, (
        "the adapter was mutated before the template check; a failed install now "
        "leaves the repo half-scaffolded"
    )
    assert not (repo / ".github" / "workflows" / "mutation-tests.yml").exists()


def test_dry_run_reports_a_template_source_that_exists(tmp_path: Path) -> None:
    """The proposal's `source` field is the operator's only pointer to the template
    before they run `--execute`. It is built from the same constant the install uses,
    so a regression that reintroduced a repo-root-relative path *only* here would
    leave every render test green while the JSON named a nonexistent file."""
    repo = _seed_consumer_repo(tmp_path)

    result = run_script(PLUGIN_PROPOSE, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    sources = [
        action["source"]
        for action in payload.get("install_actions", [])
        if "source" in action
    ]
    assert sources, payload
    for source in sources:
        assert Path(source).is_file(), f"proposal points at a nonexistent template: {source}"


def test_execute_checks_the_template_before_appending_to_the_adapter(tmp_path: Path) -> None:
    """The cheap, copy-free companion to the release-only test above: the ordering
    invariant is what turns a failed install into a recoverable one, so it should not
    be provable only in release runs."""
    module = load_path_module("propose_mutation_testing_under_test", ROOT / SOURCE_PROPOSE)
    repo = _seed_consumer_repo(tmp_path)
    adapter = repo / ".agents" / "quality-adapter.yaml"
    before = adapter.read_text(encoding="utf-8")
    module.TEMPLATE_PATH = tmp_path / "absent" / "mutation-tests.yml"

    with pytest.raises(FileNotFoundError):
        module._execute_install(repo, str(adapter), {})

    assert adapter.read_text(encoding="utf-8") == before
