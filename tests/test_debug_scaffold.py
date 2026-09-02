from __future__ import annotations

import datetime as dt
import shlex
import subprocess
from pathlib import Path

import yaml

import scripts.export_plugin as export_plugin_module
from runtime_bootstrap import import_repo_module
from tests.quality_gates.support import run_script
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]
_scaffold_debug = import_repo_module(
    ROOT / "skills" / "public" / "debug" / "scripts" / "scaffold_debug_artifact.py",
    "skills.public.debug.scripts.scaffold_debug_artifact",
)
_debug_validator = import_repo_module(
    ROOT / "scripts" / "gates" / "validate_debug_artifact.py",
    "scripts.gates.validate_debug_artifact",
)


def _seed_debug_adapter(repo: Path) -> None:
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: demo", "language: en", "output_dir: charness-artifacts/debug", ""]),
        encoding="utf-8",
    )


def _seed_resolved_debug_pointer(repo: Path) -> tuple[Path, Path]:
    _seed_debug_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    target = debug_dir / f"{dt.date.today().isoformat()}-debug-review.md"
    target.write_text(
        "# Debug Review\n\n## Interrupt Decision\n\n- Resolution: resolved\n\n## Problem\n\nTODO\n",
        encoding="utf-8",
    )
    (debug_dir / "latest.md").symlink_to(target.name)
    return debug_dir, target


def test_debug_scaffold_reports_validator_and_template(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_debug_adapter(repo)

    payload = _scaffold_debug.payload_for(repo, title=None)
    assert payload["artifact_path"] == "charness-artifacts/debug/latest.md"
    assert payload["artifact_role"] == "current_pointer"
    assert payload["intent"] == "current"
    assert payload["write_artifact_path"] == "charness-artifacts/debug/latest.md"
    assert payload["write_artifact_role"] == "current_pointer"
    assert payload["current_pointer_symlink_target"] is None
    assert payload["update_current_pointer_after_write"] is False
    assert payload["refresh_current_pointer_command"] is None
    # SCOPED to the artifact this payload writes, not the whole corpus. Unscoped, a
    # consumer's valid new record still exited 1 from legacy debt in unrelated older
    # records, and the exit code did not say which artifact was at fault. Asserted
    # against write_artifact_path so a payload that routes the write elsewhere cannot
    # leave the command pointed at a file nothing writes.
    assert payload["validator_command"].endswith(
        f"scripts/gates/validate_debug_artifact.py --repo-root . --paths {payload['write_artifact_path']}"
    )
    assert "# Debug Review" in payload["template"]
    assert "## Reproduction" in payload["template"]
    assert "## Detection Gap" in payload["template"]
    assert "## Sibling Search" in payload["template"]
    assert "- Mental model: TODO" in payload["template"]
    assert "decision: TODO | proof: TODO" in payload["template"]
    assert "## Seam Risk" in payload["template"]
    assert "- Interrupt ID: TODO" in payload["template"]
    assert "## Interrupt Decision" in payload["template"]
    assert "- Next Step: impl" in payload["template"]
    assert "## Verification" in payload["template"]
    assert "## Invariant Proof" in payload["template"]
    assert "- Producer Proof: n/a" in payload["template"]
    assert "- Final-Consumer Proof: n/a" in payload["template"]
    assert "- Interface-Shape Sibling Scan: n/a" in payload["template"]
    assert "- Non-Claims: n/a" in payload["template"]

    # size_budget surfaces the validator's word ceiling up front (single-sourced
    # from MAX_ARTIFACT_WORDS, drift-guarded here) so a run writes-to-fit instead
    # of trim-looping against a ceiling it cannot see until the validator rejects.
    assert payload["size_budget"]["max_words"] == _debug_validator.MAX_ARTIFACT_WORDS
    assert "Sibling Search" in str(payload["size_budget"]["guidance"])

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


def test_debug_scaffold_resolves_symlinked_current_pointer_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_debug_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    target = debug_dir / "debug-2026-05-06-demo.md"
    target.write_text("# Demo Debug\n", encoding="utf-8")
    (debug_dir / "latest.md").symlink_to(target.name)

    payload = _scaffold_debug.payload_for(repo, title=None)
    assert payload["artifact_path"] == "charness-artifacts/debug/latest.md"
    # The pointer is still RESOLVED and still reported — the symlink target is named below.
    # What changed is that an undeclared run no longer takes it as its write target: the
    # legacy `debug-<date>-<slug>.md` name carries no readable subject, so nobody established
    # that this open record belongs to this run, and a scaffold write there replaces it with a
    # template. Declaring the subject is how a run says the record is its own.
    assert payload["current_pointer_symlink_target"] == "debug-2026-05-06-demo.md"
    assert payload["write_artifact_path"] != "charness-artifacts/debug/debug-2026-05-06-demo.md"
    assert payload["write_artifact_effect"] == "create_new_file"
    assert payload["refused_write_artifact_path"] == "charness-artifacts/debug/debug-2026-05-06-demo.md"
    assert payload["refused_write_artifact_reason"] == "undeclared"
    assert payload["write_artifact_subject_key"] is None or payload["write_artifact_subject_key"]


def test_debug_scaffold_resolved_current_pointer_emits_fresh_record_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_debug_adapter(repo)
    debug_dir = repo / "charness-artifacts" / "debug"
    debug_dir.mkdir(parents=True)
    target = debug_dir / "debug-2026-05-06-demo.md"
    target.write_text(
        "# Demo Debug\n\n## Interrupt Decision\n\n- Resolution: resolved\n\n## Problem\n\nTODO\n",
        encoding="utf-8",
    )
    (debug_dir / "latest.md").symlink_to(target.name)

    payload = _scaffold_debug.payload_for(repo, title="Current Debug")

    assert payload["intent"] == "record"
    assert payload["write_artifact_role"] == "durable_record"
    assert payload["write_artifact_path"].startswith("charness-artifacts/debug/")
    assert payload["write_artifact_path"].endswith("-current-debug.md")
    assert payload["update_current_pointer_after_write"] is True
    assert "refresh_current_pointer.py" in str(payload["refresh_current_pointer_command"])


def test_debug_scaffold_resolved_same_day_default_name_avoids_overwriting_current_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _debug_dir, target = _seed_resolved_debug_pointer(repo)

    payload = _scaffold_debug.payload_for(repo, title=None)

    assert payload["intent"] == "record"
    assert payload["current_pointer_symlink_target"] == target.name
    assert payload["write_artifact_path"] != f"charness-artifacts/debug/{target.name}"
    assert payload["write_artifact_path"].endswith("-debug-review-followup.md")
    assert payload["update_current_pointer_after_write"] is True


def test_debug_scaffold_resolved_current_pointer_errors_when_default_followup_names_are_exhausted(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    _debug_dir, _target = _seed_resolved_debug_pointer(repo)

    adapter = _scaffold_debug.load_adapter(repo)
    for title in (
        "Debug Review followup",
        "Debug Review followup-2",
        "Debug Review followup-3",
        "Debug Review followup-4",
    ):
        record_payload = _scaffold_debug._resolve_artifact_path.payload_for(
            repo,
            "debug",
            title,
            intent="record",
            artifact_date=dt.date.today(),
            adapter=adapter,
        )
        write_path = repo / str(record_payload["write_artifact_path"])
        write_path.parent.mkdir(parents=True, exist_ok=True)
        write_path.write_text("# occupied\n", encoding="utf-8")

    try:
        _scaffold_debug.payload_for(repo, title=None)
    except SystemExit as exc:
        assert "--title <specific follow-up title>" in str(exc)
        assert "every deterministic default slug for today already exists" in str(exc)
    else:
        raise AssertionError("expected exhausted deterministic follow-up names to abort with guidance")


def test_exported_debug_scaffold_validator_command_runs_from_consumer_repo(tmp_path: Path) -> None:
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
    scaffold = plugin_root / "skills" / "debug" / "scripts" / "scaffold_debug_artifact.py"

    consumer = tmp_path / "consumer"
    (consumer / ".agents").mkdir(parents=True)
    (consumer / ".agents" / "debug-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: consumer", "language: en", "output_dir: charness-artifacts/debug", ""]),
        encoding="utf-8",
    )

    result = run_script(str(scaffold), "--repo-root", str(consumer))
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["artifact_role"] == "current_pointer"
    assert str(plugin_root / "scripts") in payload["validator_command"]
    assert "validate_debug_artifact.py" in payload["validator_command"]

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
