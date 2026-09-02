"""The artifact size ceiling is a consuming repo's setting, not a Charness constant."""
from __future__ import annotations

from pathlib import Path

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]


def run_main(rel_path: str, *args: str):
    module = load_script_module(Path(rel_path).stem, ROOT / rel_path)
    return run_loaded_script_main(rel_path, module, *args)


def write_adapter(repo: Path, name: str, lines: list[str]) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / name).write_text("\n".join([*lines, ""]), encoding="utf-8")


def long_artifact(title: str, count: int) -> str:
    return "\n".join([title, *(f"line {index}" for index in range(count))])


def test_debug_ceiling_follows_the_adapter_in_gate_and_forecast(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
        long_artifact("# Debug Review", 700), encoding="utf-8"
    )
    base = ["version: 1", "repo: demo", "output_dir: charness-artifacts/debug"]
    write_adapter(repo, "debug-adapter.yaml", base)

    default_gate = run_main("scripts/gates/validate_debug_artifact.py", "--repo-root", str(repo), "--all")
    default_forecast = run_main(
        "skills/public/debug/scripts/scaffold_debug_artifact.py",
        "--repo-root", str(repo), "--title", "probe",
    )
    assert "debug artifact is 1403 words" in default_gate.stderr
    assert "max_words: 1200\n" in default_forecast.stdout

    write_adapter(repo, "debug-adapter.yaml", [*base, "max_artifact_words: 1300"])
    raised_gate = run_main("scripts/gates/validate_debug_artifact.py", "--repo-root", str(repo), "--all")
    raised_forecast = run_main(
        "skills/public/debug/scripts/scaffold_debug_artifact.py",
        "--repo-root", str(repo), "--title", "probe",
    )
    assert "get back under 1300 " in raised_gate.stderr
    assert "max_words: 1300\n" in raised_forecast.stdout


def test_quality_ceiling_follows_the_adapter_in_gate_and_forecast(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "quality").mkdir(parents=True)
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(
        long_artifact("# Quality Review", 700), encoding="utf-8"
    )
    base = ["version: 1", "repo: demo", "output_dir: charness-artifacts/quality"]
    write_adapter(repo, "quality-adapter.yaml", base)

    default_gate = run_main("scripts/gates/validate_quality_artifact.py", "--repo-root", str(repo))
    default_forecast = run_main(
        "skills/public/quality/scripts/scaffold_quality_artifact.py",
        "--repo-root", str(repo), "--title", "probe",
    )
    assert "quality artifact is 1403 words" in default_gate.stderr
    assert "max_words: 1100\n" in default_forecast.stdout

    write_adapter(repo, "quality-adapter.yaml", [*base, "max_artifact_words: 1300"])
    raised_gate = run_main("scripts/gates/validate_quality_artifact.py", "--repo-root", str(repo))
    raised_forecast = run_main(
        "skills/public/quality/scripts/scaffold_quality_artifact.py",
        "--repo-root", str(repo), "--title", "probe",
    )
    assert "get back under 1300 " in raised_gate.stderr
    assert "max_words: 1300\n" in raised_forecast.stdout


def test_refused_ceiling_keeps_the_debug_default(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
        long_artifact("# Debug Review", 700), encoding="utf-8"
    )
    base = ["version: 1", "repo: demo", "output_dir: charness-artifacts/debug"]
    write_adapter(repo, "debug-adapter.yaml", [*base, "max_artifact_words: yes"])

    resolved = run_main("skills/public/debug/scripts/resolve_adapter.py", "--repo-root", str(repo))
    gate = run_main("scripts/gates/validate_debug_artifact.py", "--repo-root", str(repo), "--all")

    assert "valid: false" in resolved.stdout
    assert "max_artifact_words must be an integer" in resolved.stdout
    assert "get back under 1200" in gate.stderr
