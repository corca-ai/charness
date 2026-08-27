from __future__ import annotations

import os
from pathlib import Path

import yaml

from .support import run_script

SCRIPT = "skills/public/quality/scripts/inventory_sloc.py"


def _path_without_tokei(tmp_path: Path) -> dict[str, str]:
    """Force `shutil.which('tokei')` to miss by pointing PATH at an empty dir while
    keeping the rest of the environment (so the subprocess still starts normally).
    `inventory_sloc.py` returns the degraded payload before any tokei/git subprocess,
    so an empty PATH is safe. Before #368 these tests skipped whenever tokei was on
    PATH — which is always (tokei is installed locally and in CI), so the degraded
    path was never actually exercised."""
    nobin = tmp_path / "nobin"
    nobin.mkdir(exist_ok=True)
    return {**os.environ, "PATH": str(nobin)}


def test_inventory_sloc_reports_degraded_when_tokei_missing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('hi')\n", encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(repo), "--detail", env=_path_without_tokei(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "degraded"
    assert payload["engine"] == "tokei"
    assert payload["tokei_version"] is None
    assert "tokei" in payload["reason"].lower()
    assert payload["totals"] == {"code": 0, "comments": 0, "blanks": 0, "files": 0}
    assert payload["languages"] == {}
    assert payload["advisory_notes"]


def test_inventory_sloc_human_output_marks_degraded(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_script(SCRIPT, "--repo-root", str(repo), env=_path_without_tokei(tmp_path))

    assert result.returncode == 0, result.stderr
    assert "degraded" in result.stdout


def test_inventory_sloc_ignores_mutable_charness_runtime_state(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    runtime_record = repo / ".charness" / "quality" / "runtime-signals.json"
    runtime_record.parent.mkdir(parents=True)
    (repo / "main.py").write_text("print('versioned source')\n", encoding="utf-8")
    runtime_record.write_text('{"phase":"before"}\n', encoding="utf-8")

    before = run_script(SCRIPT, "--repo-root", str(repo), "--detail")
    assert before.returncode == 0, before.stderr
    before_payload = yaml.safe_load(before.stdout)
    assert before_payload["status"] == "ok"
    assert ".charness" in before_payload["exclude"]

    runtime_record.write_text('{"phase":"after","detail":"' + ("x" * 20_000) + '"}\n', encoding="utf-8")
    after = run_script(SCRIPT, "--repo-root", str(repo), "--detail")

    assert after.returncode == 0, after.stderr
    after_payload = yaml.safe_load(after.stdout)
    assert after_payload["totals"] == before_payload["totals"]
    assert after_payload["languages"] == before_payload["languages"]


def test_inventory_sloc_output_does_not_measure_itself(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    output = repo / "reports" / "current.json"
    repo.mkdir()
    (repo / "main.py").write_text("print('versioned source')\n", encoding="utf-8")

    first = run_script(SCRIPT, "--repo-root", str(repo), "--output", str(output), "--detail")
    assert first.returncode == 0, first.stderr
    first_bytes = output.read_bytes()

    second = run_script(SCRIPT, "--repo-root", str(repo), "--output", str(output), "--detail")

    assert second.returncode == 0, second.stderr
    assert output.read_bytes() == first_bytes
    payload = yaml.safe_load(second.stdout)
    assert payload["languages"]["Python"]["files"] == 1
    assert all("reports/current.json" not in item for item in payload["exclude"])


def test_inventory_sloc_keeps_source_beneath_same_named_directory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    output = repo / "reports" / "current.json"
    same_named_source = repo / "src" / "reports" / "current.json"
    same_named_source.parent.mkdir(parents=True)
    (repo / "main.py").write_text("print('main')\n", encoding="utf-8")
    same_named_source.write_text('{"must_remain_visible":true}\n', encoding="utf-8")

    result = run_script(SCRIPT, "--repo-root", str(repo), "--output", str(output), "--detail")

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["languages"]["Python"]["files"] == 1
    assert payload["languages"]["JSON"]["files"] == 1


def test_inventory_sloc_treats_output_metacharacters_as_literal_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    output = repo / "reports" / "[x].json"
    legitimate_source = repo / "reports" / "x.json"
    legitimate_source.parent.mkdir(parents=True)
    legitimate_source.write_text('{"source":true}\n', encoding="utf-8")

    first = run_script(SCRIPT, "--repo-root", str(repo), "--output", str(output), "--detail")
    assert first.returncode == 0, first.stderr
    first_bytes = output.read_bytes()
    second = run_script(SCRIPT, "--repo-root", str(repo), "--output", str(output), "--detail")

    assert second.returncode == 0, second.stderr
    assert output.read_bytes() == first_bytes
    assert yaml.safe_load(second.stdout)["languages"]["JSON"]["files"] == 1
