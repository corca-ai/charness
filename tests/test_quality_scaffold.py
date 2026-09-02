from __future__ import annotations

import datetime as dt
import shlex
import subprocess
from pathlib import Path

import yaml

from runtime_bootstrap import import_repo_module
from tests.quality_gates.support import run_script

ROOT = Path(__file__).resolve().parents[1]
_export_plugin = import_repo_module(__file__, "scripts.plugin_export.export_plugin")
_validate_quality_artifact = import_repo_module(__file__, "scripts.gates.validate_quality_artifact")
_scaffold_quality_artifact = import_repo_module(
    __file__,
    "skills.public.quality.scripts.scaffold_quality_artifact",
)

SCAFFOLD = "skills/public/quality/scripts/scaffold_quality_artifact.py"

# Headings the scaffold must emit so an author starts from a validator-passing
# skeleton instead of rediscovering scripts/gates/validate_quality_artifact.py by
# trial-and-error.
REQUIRED_HEADINGS = (
    "## Scope",
    "## Surface Contract Review",
    "## Current Gates",
    "## Runtime Signals",
    "## Healthy",
    "## Weak",
    "## Missing",
    "## Deferred",
    "## Advisory",
    "## Delegated Review",
    "## Commands Run",
    "## Recommended Next Quality Moves",
    "## History",
)


def scaffold_payload(repo: Path) -> dict[str, object]:
    return _scaffold_quality_artifact.payload_for(repo, title=None)


def _write_adapter(repo: Path, repo_name: str) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            ["version: 1", f"repo: {repo_name}", "language: en", "output_dir: charness-artifacts/quality", ""]
        ),
        encoding="utf-8",
    )


def test_quality_scaffold_reports_validator_and_template(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")

    payload = scaffold_payload(repo)
    assert payload["artifact_path"] == "charness-artifacts/quality/latest.md"
    assert payload["artifact_role"] == "current_pointer"
    assert payload["write_artifact_path"] == "charness-artifacts/quality/latest.md"
    assert payload["write_artifact_role"] == "current_pointer"
    assert payload["current_pointer_symlink_target"] is None
    assert payload["validator_command"].endswith("scripts/gates/validate_quality_artifact.py --repo-root .")

    template = payload["template"]
    assert template.startswith("# Quality Review\n")
    for heading in REQUIRED_HEADINGS:
        assert heading in template, heading
    assert "Target boundary:" in template
    assert "Ambient repo findings:" in template
    assert "- semantic coverage: `not-in-scope`" in template
    assert "- unexamined axes:" in template
    assert "structural review result:" in template
    assert "prose review result:" in template
    # Runtime Signals carries the four prefixes the validator asserts on.
    assert "- runtime source: structured metrics" in template
    assert "rendered by `render_runtime_summary.py`" in template
    runtime_source_line = next(line for line in template.splitlines() if "runtime-signals.json" in line)
    assert "<!-- reproduction-source -->" in runtime_source_line
    assert "- runtime hot spots:" in template
    assert "- coverage gate:" in template
    assert "- evaluator depth:" in template
    # Delegated Review default is a fillable not_applicable that names the slow-gate lenses.
    assert "Delegated Review: not_applicable" in template
    assert "fixture-economics, parallel-critical-path, duplicated-proof" in template
    # size_budget surfaces the validator's word ceiling up front (single-sourced
    # from MAX_ARTIFACT_WORDS, drift-guarded here) so a run writes-to-fit instead
    # of trim-looping against a ceiling it cannot see until the validator rejects.
    # The cap rides the payload as the single source (no second literal that could
    # drift); SKILL.md step 8 routes the run to the --json payload that carries it.
    assert payload["size_budget"]["max_words"] == _validate_quality_artifact.MAX_ARTIFACT_WORDS
    assert "Advisory" in str(payload["size_budget"]["guidance"])
    # Fill-time guards surface the conditional rules that only fire after the
    # TODO slots are filled (bullet prefixes, passive-because), so an author
    # batches fixes instead of rediscovering them one gate run at a time.
    assert "reports every rule violation in one pass" in template
    assert "`- active ` or `- passive `" in template
    assert "` because`" in template and "` until`" in template
    assert "capability_needed=TODO" in template
    assert "enforcement_posture=advisory" in template
    assert "candidate-floor requires" in template
    assert "move_type=TODO" not in template

    # Dogfood: the emitted skeleton must pass the real validator unedited.
    artifact_path = repo / payload["artifact_path"]
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(template, encoding="utf-8")
    _validate_quality_artifact.validate_quality_artifact(artifact_path, repo_root=repo)


def test_quality_scaffold_custom_title_keeps_canonical_h1_and_validates(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")

    payload = _scaffold_quality_artifact.payload_for(repo, title="Auth Migration")
    template = payload["template"]
    assert payload["title"] == "Auth Migration"
    assert payload["artifact_path"] == "charness-artifacts/quality/latest.md"
    assert template.startswith("# Quality Review\n")
    assert "# Auth Migration" not in template
    assert "Title: Auth Migration\n" in template

    artifact_path = repo / payload["artifact_path"]
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(template, encoding="utf-8")
    _validate_quality_artifact.validate_quality_artifact(artifact_path, repo_root=repo)


def test_quality_scaffold_cli_custom_title_emits_validator_passing_artifact(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")

    result = run_script(SCAFFOLD, "--repo-root", str(repo), "--title", "Auth Migration")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["title"] == "Auth Migration"
    assert payload["template"].startswith("# Quality Review\n")
    assert "Title: Auth Migration\n" in payload["template"]

    artifact_path = repo / payload["artifact_path"]
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(payload["template"], encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr


def test_quality_scaffold_resolves_symlinked_current_pointer_target(tmp_path: Path) -> None:
    """A pointer target from TODAY is this review's own record, and is written in place.

    The pointer is still followed and still reported; what changed is that following it is
    now conditional on the target belonging to this invocation's subject.
    """
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")
    quality_dir = repo / "charness-artifacts" / "quality"
    quality_dir.mkdir(parents=True)
    target = quality_dir / f"{dt.date.today().isoformat()}-quality-review.md"
    target.write_text("# Quality Review\n", encoding="utf-8")
    (quality_dir / "latest.md").symlink_to(target.name)

    payload = scaffold_payload(repo)
    assert payload["artifact_path"] == "charness-artifacts/quality/latest.md"
    assert payload["write_artifact_path"] == f"charness-artifacts/quality/{target.name}"
    assert payload["write_artifact_role"] == "current_pointer_target"
    assert payload["current_pointer_symlink_target"] == target.name
    assert payload["write_artifact_subject_match"] == "match"


def test_quality_scaffold_refuses_a_previous_days_finished_review(tmp_path: Path) -> None:
    """The producer half of the destroyed-review defect the validator already refuses.

    The pointer names a review dated before today, so writing today's review to it destroys a
    finished record. The scaffold resolves onto today's own dated record instead, carries the
    pointer refresh that follows the write, and names what it refused — the validator's rule
    moved to the surface that hands out the path, where nothing is destroyed to detect it.
    """
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")
    quality_dir = repo / "charness-artifacts" / "quality"
    quality_dir.mkdir(parents=True)
    target = quality_dir / "2026-05-06-quality-review.md"
    target.write_text("# Quality Review\n", encoding="utf-8")
    (quality_dir / "latest.md").symlink_to(target.name)

    payload = scaffold_payload(repo)
    today = dt.date.today().isoformat()
    assert payload["write_artifact_path"] == f"charness-artifacts/quality/{today}-quality-review.md"
    assert payload["write_artifact_effect"] == "create_new_file"
    assert payload["update_current_pointer_after_write"] is True
    assert payload["refused_write_artifact_path"] == "charness-artifacts/quality/2026-05-06-quality-review.md"
    assert payload["refused_write_artifact_subject_key"] == "quality-review@2026-05-06"


def test_exported_quality_scaffold_validator_command_runs_from_consumer_repo(tmp_path: Path) -> None:
    export_root = tmp_path / "export"
    manifest = _export_plugin.load_manifest(ROOT, "charness")
    plugin_root = _export_plugin.export_plugin(
        ROOT,
        export_root,
        manifest,
        "codex",
        with_marketplace=False,
    )
    scaffold = plugin_root / "skills" / "quality" / "scripts" / "scaffold_quality_artifact.py"

    consumer = tmp_path / "consumer"
    _write_adapter(consumer, "consumer")

    result = run_script(str(scaffold), "--repo-root", str(consumer), "--title", "Auth Migration")
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_role"] == "current_pointer"
    assert payload["title"] == "Auth Migration"
    assert payload["template"].startswith("# Quality Review\n")
    assert "Title: Auth Migration\n" in payload["template"]
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_quality_artifact.py" in payload["validator_command"]
    # The single-source size budget must survive the plugin layout: the exported
    # scaffold single-sources MAX_ARTIFACT_WORDS from the exported validator, so a
    # consumer repo inherits the write-to-fit budget instead of falling back to none.
    assert payload["size_budget"]["max_words"] == _validate_quality_artifact.MAX_ARTIFACT_WORDS

    artifact_path = consumer / payload["artifact_path"]
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(payload["template"], encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr


def test_quality_scaffold_template_validates_with_the_executed_slot_filled(tmp_path: Path) -> None:
    """The template's own fill guard must not refuse the status it tells authors to record.

    The `## Delegated Review` guard names the substantiation vocabulary and the
    "no review ran" contradiction, so an author who fills the slot in place — the
    authoring path `render_template` prescribes — used to trip the contradiction arm on
    boilerplate they did not write. The validator now reads authored lines only.
    """
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")
    payload = scaffold_payload(repo)
    template = payload["template"]
    unfilled = next(line for line in template.splitlines() if "Delegated Review: not_applicable" in line)
    filled = template.replace(
        unfilled,
        "- Delegated Review: executed — one bounded fresh-eye reviewer returned no blocking findings.",
    )

    artifact_path = repo / payload["artifact_path"]
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(filled, encoding="utf-8")

    _validate_quality_artifact.validate_quality_artifact(artifact_path, repo_root=repo)


def test_quality_scaffold_guard_does_not_scope_every_artifact_as_a_slow_gate_review(
    tmp_path: Path,
) -> None:
    """The delegated-review guard names slow-gate lenses; unstripped it armed that rule.

    An author whose review has no slow-gate scope drops the boilerplate lens bullet. The
    guard comment must not then demand the three lens ids back.
    """
    repo = tmp_path / "repo"
    _write_adapter(repo, "demo")
    payload = scaffold_payload(repo)
    lines = payload["template"].splitlines()
    kept = [line for line in lines if not line.startswith("- Slow-gate lenses")]
    filled = "\n".join(
        "- Delegated Review: executed — one bounded fresh-eye reviewer returned no blocking findings."
        if "Delegated Review: not_applicable" in line
        else line
        for line in kept
    )

    artifact_path = repo / payload["artifact_path"]
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(filled + "\n", encoding="utf-8")

    _validate_quality_artifact.validate_quality_artifact(artifact_path, repo_root=repo)
