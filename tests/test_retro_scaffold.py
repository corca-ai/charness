from __future__ import annotations

import importlib.util
import shlex
import subprocess
from pathlib import Path

import yaml

import scripts.export_plugin as export_plugin_module
from tests.quality_gates.support import run_script
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]

SCAFFOLD = "skills/public/retro/scripts/scaffold_retro_artifact.py"

SCAFFOLD_SPEC = importlib.util.spec_from_file_location(
    "scaffold_retro_artifact", ROOT / SCAFFOLD
)
assert SCAFFOLD_SPEC is not None and SCAFFOLD_SPEC.loader is not None
SCAFFOLD_MODULE = importlib.util.module_from_spec(SCAFFOLD_SPEC)
SCAFFOLD_SPEC.loader.exec_module(SCAFFOLD_MODULE)


def test_retro_scaffold_reports_validator_and_template(tmp_path: Path) -> None:
    # The retro adapter falls back to inferred defaults (output_dir
    # charness-artifacts/retro) with no adapter file present.
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(SCAFFOLD, "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_path"].startswith("charness-artifacts/retro/")
    assert payload["artifact_path"].endswith(".md")
    assert payload["artifact_role"] == "record"
    assert "validate_retro_artifact.py" in payload["validator_command"]
    assert f"--paths {payload['write_artifact_path']}" in payload["validator_command"]

    template = payload["template"]
    # The validator only enforces the `## Sibling Search` follow-up grammar, so
    # the scaffold demonstrates the exact form it demands.
    assert "## Sibling Search" in template
    assert "decision: valid follow-up outside the slice" in template
    assert "follow-up: deferred TODO-handoff-anchor" in template
    assert "## Persisted\n\nPersisted: yes: TODO path" in template
    assert "## Lesson Evaluation" not in template
    assert "missing-start" not in template
    assert "session_id" not in template

    artifact_path = repo / payload["write_artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(template, encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr
    assert "Validated 1 retro artifact" in validation.stdout


def test_exported_retro_scaffold_validator_command_runs_from_consumer_repo(tmp_path: Path) -> None:
    export_root = tmp_path / "export"
    export_result = run_loaded_script_main(
        "export_plugin.py",
        export_plugin_module,
        "--repo-root",
        str(ROOT),
        "--host",
        "codex",
        "--output-root",
        str(export_root),
    )
    assert export_result.returncode == 0, export_result.stderr
    plugin_root = export_root / "plugins" / "charness"
    scaffold = plugin_root / "skills" / "retro" / "scripts" / "scaffold_retro_artifact.py"

    consumer = tmp_path / "consumer"
    consumer.mkdir()

    result = run_script(str(scaffold), "--repo-root", str(consumer))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_role"] == "record"
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_retro_artifact.py" in payload["validator_command"]

    artifact_path = consumer / payload["write_artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(payload["template"], encoding="utf-8")
    validation = subprocess.run(
        shlex.split(payload["validator_command"]),
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )
    assert validation.returncode == 0, validation.stderr
    assert "Validated 1 retro artifact" in validation.stdout


# The two mutants that survived the #572 mutation run are the two the #457 run
# already killed in the CRITIQUE scaffold. The killing tests were written there and
# never mirrored here, so the twin kept the gap. These are those tests, on this twin.


def test_retro_scaffold_title_with_no_alnum_chars_falls_back_to_retro_slug(tmp_path: Path) -> None:
    # `_slug` normalizes a title to `[a-z0-9]` runs joined by `-`, then strips
    # leading/trailing dashes, so a title with no alnum characters normalizes to the
    # empty string and must fall back to "retro" (`slug or "retro"`).
    #
    # This also pins the OTHER half, which is what the surviving `ReplaceOrWithAnd`
    # mutant exposed: under `slug and "retro"` every real title collapses to the same
    # filename, so two same-day retros with different titles would overwrite each
    # other at the path built from this slug.
    repo = tmp_path / "repo"
    repo.mkdir()

    empty = yaml.safe_load(run_script(SCAFFOLD, "--repo-root", str(repo), "--title", "!!!").stdout)
    assert empty["write_artifact_path"].endswith("-retro.md")

    named = yaml.safe_load(run_script(SCAFFOLD, "--repo-root", str(repo), "--title", "Ship the gate").stdout)
    assert named["write_artifact_path"].endswith("-ship-the-gate.md")
    assert named["write_artifact_path"] != empty["write_artifact_path"]


def test_payload_for_requires_the_title_to_be_named(tmp_path: Path) -> None:
    """`payload_for(repo_root, *, title=...)` — the `*` is a real contract.

    The `ReplaceBinaryOperator_Mul_Div` mutant that survived the #572 run turns that
    `*` into `/`, which still lets `title` be passed by keyword and so changes nothing
    at any current call site. What `/` DOES allow is a positional title:
    `payload_for(repo, None)` would silently become a title argument. Asserting the
    keyword-only boundary is what distinguishes the two, and it is the reason the
    marker was written. Same finding, same repair, as the critique twin under #457.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    # Keyword form is the supported call and must work.
    assert SCAFFOLD_MODULE.payload_for(repo, title=None)["write_artifact_path"]
    # Positional title must be rejected rather than silently accepted.
    try:
        SCAFFOLD_MODULE.payload_for(repo, "Some Title")
    except TypeError as exc:
        assert "positional" in str(exc)
    else:
        raise AssertionError("payload_for must not accept a positional title")


def test_retro_scaffold_appends_only_adapter_declared_sections() -> None:
    template = SCAFFOLD_MODULE.render_template(
        title="Session Retro",
        date_text="2026-08-14",
        artifact_sections=[
            "## Repo Evaluator",
            "",
            "Repo evaluation: TODO exact repo-owned form",
        ],
    )

    assert "## Repo Evaluator" in template
    assert "Repo evaluation: TODO exact repo-owned form" in template


def test_the_north_star_prompt_never_writes_an_authoring_placeholder(tmp_path: Path) -> None:
    """A consuming repo used to read a literal `<authoring-repo>` in its own retro.

    That spelling is charness's INTERNAL convention for "resolves in my tree, not
    yours". A consuming author reads it as a path and looks for a directory that does
    not exist. Both arms asserted, because naming the real file is only correct for a
    repo that has one -- resolving it unconditionally would trade one wrong path for
    another.
    """
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    consumer_template = SCAFFOLD_MODULE.render_template(
        title="Session Retro", date_text="2026-08-16", repo_root=consumer
    )

    assert "<authoring-repo>" not in consumer_template
    assert SCAFFOLD_MODULE.NORTH_STAR_DOC not in consumer_template
    assert "governing design standard" in consumer_template

    (consumer / "docs").mkdir()
    (consumer / SCAFFOLD_MODULE.NORTH_STAR_DOC).write_text("# North Star\n", encoding="utf-8")
    owning_template = SCAFFOLD_MODULE.render_template(
        title="Session Retro", date_text="2026-08-16", repo_root=consumer
    )

    assert f"`{SCAFFOLD_MODULE.NORTH_STAR_DOC}`" in owning_template
    assert "<authoring-repo>" not in owning_template
