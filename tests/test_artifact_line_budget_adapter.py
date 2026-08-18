"""The artifact line ceiling is a CONSUMING repo's setting, not a charness constant.

Three families own a ceiling -- debug and quality count raw file lines, handoff counts
content lines -- and each one enforces it in a validator and forecasts it in a scaffold
or planner. The forecast is the half that matters operationally: a ceiling discovered
only after writing long is the wasted draft this override exists to end, so every family
here asserts BOTH sides against the same adapter, not just the refusal.

Driven through each script's `main()` in-process rather than a subprocess, because the
per-run binding IS the wiring under test (debug resolves its ceiling once in
`_validate_factory`, not per artifact) and an argv-patched main reaches it without
adding a process boundary the ratchet would rightly call convertible.

Blind class: these prove the resolved number reaches the gate and the forecast. They
prove nothing about whether any particular ceiling is a good one, and nothing about the
`__main__` entrypoint block or a repo that vendors a resolver older than its validator
-- that skew is guarded by the isinstance re-check in `resolve_adapter_line_budget` and
unit-tested in test_adapter_lib.
"""

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


def test_debug_ceiling_follows_the_adapter_in_both_gate_and_forecast(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
        long_artifact("# Debug Review", 250), encoding="utf-8"
    )
    base = ["version: 1", "repo: demo", "output_dir: charness-artifacts/debug"]
    gate = "scripts/validate_debug_artifact.py"
    scaffold = "skills/public/debug/scripts/scaffold_debug_artifact.py"

    write_adapter(repo, "debug-adapter.yaml", base)
    default_gate = run_main(gate, "--repo-root", str(repo), "--all")
    default_forecast = run_main(scaffold, "--repo-root", str(repo), "--title", "probe")

    write_adapter(repo, "debug-adapter.yaml", [*base, "max_artifact_lines: 240"])
    raised_gate = run_main(gate, "--repo-root", str(repo), "--all")
    raised_forecast = run_main(scaffold, "--repo-root", str(repo), "--title", "probe")

    assert "get back under 180" in default_gate.stderr
    assert "max_lines: 180" in default_forecast.stdout
    assert "get back under 240" in raised_gate.stderr
    assert "max_lines: 240" in raised_forecast.stdout


def test_quality_ceiling_follows_the_adapter_in_both_gate_and_forecast(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "quality").mkdir(parents=True)
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(
        long_artifact("# Quality Review", 210), encoding="utf-8"
    )
    base = ["version: 1", "repo: demo", "output_dir: charness-artifacts/quality"]
    gate = "scripts/validate_quality_artifact.py"
    scaffold = "skills/public/quality/scripts/scaffold_quality_artifact.py"

    write_adapter(repo, "quality-adapter.yaml", base)
    default_gate = run_main(gate, "--repo-root", str(repo))
    default_forecast = run_main(scaffold, "--repo-root", str(repo), "--title", "probe")

    write_adapter(repo, "quality-adapter.yaml", [*base, "max_artifact_lines: 200"])
    raised_gate = run_main(gate, "--repo-root", str(repo))
    raised_forecast = run_main(scaffold, "--repo-root", str(repo), "--title", "probe")

    assert "get back under 140" in default_gate.stderr
    assert "max_lines: 140" in default_forecast.stdout
    assert "get back under 200" in raised_gate.stderr
    assert "max_lines: 200" in raised_forecast.stdout


def _handoff_artifact(entries_per_section: int) -> str:
    body = ["# Demo Handoff", ""]
    for section in ("## Workflow Trigger", "## Current State", "## Next Session", "## Discuss"):
        body += [section, "", *(f"- line {index}" for index in range(entries_per_section)), ""]
    body += ["## References", ""]
    return "\n".join(body)


def test_handoff_content_ceiling_follows_the_adapter_in_gate_scaffold_and_planner(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "handoff.md").write_text(_handoff_artifact(25), encoding="utf-8")
    base = ["version: 1", "repo: demo", "output_dir: docs"]
    gate = "scripts/validate_handoff_artifact.py"
    scaffold = "skills/public/handoff/scripts/scaffold_handoff_artifact.py"
    planner = "skills/public/handoff/scripts/plan_handoff_run.py"

    write_adapter(repo, "handoff-adapter.yaml", base)
    default_gate = run_main(gate, "--repo-root", str(repo))
    default_forecast = run_main(scaffold, "--repo-root", str(repo))
    default_plan = run_main(planner, "--repo-root", str(repo), "--intent", "refresh")

    write_adapter(repo, "handoff-adapter.yaml", [*base, "max_content_lines: 120"])
    raised_gate = run_main(gate, "--repo-root", str(repo))
    raised_forecast = run_main(scaffold, "--repo-root", str(repo))
    raised_plan = run_main(planner, "--repo-root", str(repo), "--intent", "refresh")

    assert "content lines (limit 78)" in default_gate.stderr
    assert "max_lines: 78" in default_forecast.stdout
    assert "status: over_limit" in default_plan.stdout
    # The 101-content-line artifact is now UNDER the ceiling, so the budget rule stops
    # firing and the planner drops to its next-ranked status. Asserting the ABSENCE of
    # the limit message is the point: the artifact is byte-identical across both halves,
    # so only the adapter can account for the difference.
    assert "content lines (limit" not in raised_gate.stderr
    assert "max_lines: 120" in raised_forecast.stdout
    assert "status: over_limit" not in raised_plan.stdout


def test_a_refused_ceiling_is_an_adapter_error_and_leaves_the_default_enforced(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
        long_artifact("# Debug Review", 250), encoding="utf-8"
    )
    base = ["version: 1", "repo: demo", "output_dir: charness-artifacts/debug"]

    for value, expected in (
        ("yes", "max_artifact_lines must be an integer"),
        ("0", "max_artifact_lines must be greater than or equal to 1"),
        ("'240'", "max_artifact_lines must be an integer"),
    ):
        write_adapter(repo, "debug-adapter.yaml", [*base, f"max_artifact_lines: {value}"])
        resolved = run_main("skills/public/debug/scripts/resolve_adapter.py", "--repo-root", str(repo))
        gate = run_main("scripts/validate_debug_artifact.py", "--repo-root", str(repo), "--all")

        assert "valid: false" in resolved.stdout, value
        assert expected in resolved.stdout, value
        # The refused value must never become the ceiling, and must never disarm it
        # either: the conservative arm is the built-in default, not "unlimited".
        assert "get back under 180" in gate.stderr, value
