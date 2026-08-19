"""The artifact line ceiling is a CONSUMING repo's setting, not a charness constant.

Three families own a ceiling -- debug and quality count raw file LINES, handoff counts
content lines -- and each one enforces it in a validator and forecasts it in a scaffold
or planner. The forecast is the half that matters operationally: a ceiling discovered
only after writing long is the wasted draft this override exists to end, so every family
here asserts BOTH sides against the same adapter, not just the refusal.

Driven through each script's `main()` in-process rather than a subprocess, because the
per-run binding IS the wiring under test (debug resolves its ceiling once in
`_validate_factory`, not per artifact) and an argv-patched main reaches it without
adding a process boundary the ratchet would rightly call convertible.

Blind class: these prove the resolved number reaches the gate and the forecast. They
prove nothing about whether any particular ceiling is a good one, nothing about the
`__main__` entrypoint block, and -- the one a fresh-eye round had to point out -- nothing
about a repo that pairs a STALE vendored resolver with a new validator. Two guards cover
that skew and neither is exercised here: the isinstance re-check in
`resolve_adapter_line_budget` (unit-tested in test_adapter_lib) for a bad VALUE, and the
`getattr(..., WORD_BUDGET_FIELD, <literal>)` reads in the debug/handoff validators for a
missing field NAME. Reproducing it needs two trees, which this fixture does not build.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]


def run_main(rel_path: str, *args: str):
    module = load_script_module(Path(rel_path).stem, ROOT / rel_path)
    return run_loaded_script_main(rel_path, module, *args)


def write_adapter(repo: Path, name: str, lines: list[str]) -> None:
    (repo / ".agents").mkdir(parents=True, exist_ok=True)
    (repo / ".agents" / name).write_text("\n".join([*lines, ""]), encoding="utf-8")


def long_artifact(title: str, count: int) -> str:
    """`count` filler lines of exactly TWO words each, plus a THREE-word title.

    Three because `#` is its own whitespace-separated token -- the first draft of
    this model said two and the assertions caught it, which is the point of keeping
    an independent model instead of asking the counter under test what it counted.
    So the artifact measures `2 * count + 3` words.
    """
    return "\n".join([title, *(f"line {index}" for index in range(count))])


def test_debug_ceiling_follows_the_adapter_in_both_gate_and_forecast(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
        long_artifact("# Debug Review", 700), encoding="utf-8"
    )
    base = ["version: 1", "repo: demo", "output_dir: charness-artifacts/debug"]
    gate = "scripts/validate_debug_artifact.py"
    scaffold = "skills/public/debug/scripts/scaffold_debug_artifact.py"

    write_adapter(repo, "debug-adapter.yaml", base)
    default_gate = run_main(gate, "--repo-root", str(repo), "--all")
    default_forecast = run_main(scaffold, "--repo-root", str(repo), "--title", "probe")

    write_adapter(repo, "debug-adapter.yaml", [*base, "max_artifact_words: 1300"])
    raised_gate = run_main(gate, "--repo-root", str(repo), "--all")
    raised_forecast = run_main(scaffold, "--repo-root", str(repo), "--title", "probe")

    # 2 * 700 + 3 words, from `long_artifact`'s own model -- not read back from the
    # counter. The raw LINE count of the same file is 701, so a mutation that counted
    # lines could not produce this number.
    assert "debug artifact is 1403 words" in default_gate.stderr
    assert "get back under 1200 " in default_gate.stderr
    assert "max_words: 1200\n" in default_forecast.stdout
    assert "get back under 1300 " in raised_gate.stderr
    assert "max_words: 1300\n" in raised_forecast.stdout


def test_quality_ceiling_follows_the_adapter_in_both_gate_and_forecast(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "quality").mkdir(parents=True)
    (repo / "charness-artifacts" / "quality" / "latest.md").write_text(
        long_artifact("# Quality Review", 700), encoding="utf-8"
    )
    base = ["version: 1", "repo: demo", "output_dir: charness-artifacts/quality"]
    gate = "scripts/validate_quality_artifact.py"
    scaffold = "skills/public/quality/scripts/scaffold_quality_artifact.py"

    write_adapter(repo, "quality-adapter.yaml", base)
    default_gate = run_main(gate, "--repo-root", str(repo))
    default_forecast = run_main(scaffold, "--repo-root", str(repo), "--title", "probe")

    write_adapter(repo, "quality-adapter.yaml", [*base, "max_artifact_words: 1300"])
    raised_gate = run_main(gate, "--repo-root", str(repo))
    raised_forecast = run_main(scaffold, "--repo-root", str(repo), "--title", "probe")

    assert "quality artifact is 1403 words" in default_gate.stderr
    assert "get back under 1100 " in default_gate.stderr
    assert "max_words: 1100\n" in default_forecast.stdout
    assert "get back under 1300 " in raised_gate.stderr
    assert "max_words: 1300\n" in raised_forecast.stdout


def _handoff_artifact(entries_per_section: int) -> str:
    body = ["# Demo Handoff", ""]
    for section in ("## Workflow Trigger", "## Current State", "## Next Session", "## Discuss"):
        body += [section, "", *(f"- line {index}" for index in range(entries_per_section)), ""]
    body += ["## References", ""]
    return "\n".join(body)


def test_handoff_content_ceiling_follows_the_adapter_in_gate_scaffold_and_planner(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "handoff.md").write_text(_handoff_artifact(80), encoding="utf-8")
    base = ["version: 1", "repo: demo", "output_dir: docs"]
    gate = "scripts/validate_handoff_artifact.py"
    scaffold = "skills/public/handoff/scripts/scaffold_handoff_artifact.py"
    planner = "skills/public/handoff/scripts/plan_handoff_run.py"

    write_adapter(repo, "handoff-adapter.yaml", base)
    default_gate = run_main(gate, "--repo-root", str(repo))
    default_forecast = run_main(scaffold, "--repo-root", str(repo))
    default_plan = run_main(planner, "--repo-root", str(repo), "--intent", "refresh")

    write_adapter(repo, "handoff-adapter.yaml", [*base, "max_content_words: 1200"])
    raised_gate = run_main(gate, "--repo-root", str(repo))
    raised_forecast = run_main(scaffold, "--repo-root", str(repo))
    raised_plan = run_main(planner, "--repo-root", str(repo), "--intent", "refresh")

    # The COUNT and its UNIT, not just the ceiling. The fixture measures 963 content
    # WORDS across 335 raw lines and 321 content lines, so a mutation that counted
    # either kind of LINE would report a number nowhere near 963 and this assertion
    # kills it by value. Pinned as a literal on purpose: deriving it from the counter
    # under test would make the assertion agree with any counter.
    assert "handoff artifact has 963 content words (limit 900)" in default_gate.stderr
    assert "max_words: 900\n" in default_forecast.stdout
    assert "content_word_budget: 900" in default_plan.stdout
    assert "status: over_limit" in default_plan.stdout

    # The artifact is byte-identical across both halves, so only the adapter can
    # account for any difference. Absence alone is too weak a raised-half assertion --
    # it holds for ANY ceiling above 101, which leaves a resolver free to forecast a
    # number the gate does not enforce. So pin the number wherever a surface publishes
    # one, and keep a POSITIVE assertion on the gate so "the rule passed" stays
    # distinguishable from "the gate exited early and printed nothing".
    assert "content words (limit" not in raised_gate.stderr
    assert raised_gate.returncode == 1
    assert "at least one" in raised_gate.stderr or "reference" in raised_gate.stderr.lower()
    assert "max_words: 1200\n" in raised_forecast.stdout
    assert "content_word_budget: 1200" in raised_plan.stdout
    assert "status: unowned_entries" in raised_plan.stdout


def test_the_doc_authoring_forecasts_read_the_adapter_ceiling_not_the_default(tmp_path: Path) -> None:
    """The pre-write rules and the preflight verdict are the fourth and fifth surfaces.

    Round-1 review found both still reading the module constant: the preflight rendered
    `status: blocked` against the shipped default for an artifact the gate accepted, and
    the rules mode -- the FIRST cap an authoring agent sees, before a draft exists --
    published that same default as the number to write to. The handoff run planner emits both commands, so one run computed
    the resolved ceiling and then told the author to run a command that contradicted it.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    artifact = repo / "docs" / "handoff.md"
    artifact.write_text(_handoff_artifact(80), encoding="utf-8")
    base = ["version: 1", "repo: demo", "output_dir: docs"]
    # One entrypoint, two modes: `--path` renders the verdict, omitting it renders the
    # pre-write rules (owned by doc_authoring_rules, imported there).
    preflight = "scripts/check_doc_authoring_preflight.py"

    write_adapter(repo, "handoff-adapter.yaml", base)
    default_preflight = run_main(preflight, "--repo-root", str(repo), "--path", "docs/handoff.md")
    default_rules = run_main(preflight, "--repo-root", str(repo), "--as-surface", "handoff")

    write_adapter(repo, "handoff-adapter.yaml", [*base, "max_content_words: 1200"])
    raised_preflight = run_main(preflight, "--repo-root", str(repo), "--path", "docs/handoff.md")
    raised_rules = run_main(preflight, "--repo-root", str(repo), "--as-surface", "handoff")

    assert "cap: 900\n" in default_preflight.stdout
    assert "current: 963" in default_preflight.stdout
    assert "over: true" in default_preflight.stdout
    assert "cap: 900\n" in default_rules.stdout
    # Same 963-content-word artifact, byte for byte. Only the adapter differs, so the
    # forecast flipping to `over: false` can have no other cause.
    assert "cap: 1200\n" in raised_preflight.stdout
    assert "current: 963" in raised_preflight.stdout
    assert "over: false" in raised_preflight.stdout
    assert "cap: 1200\n" in raised_rules.stdout


def test_the_handoff_planner_refuses_the_same_values_its_gate_does(tmp_path: Path) -> None:
    """The planner resolves the ceiling with its OWN copy of the rule, by necessity.

    It ships inside the skill package and must forecast in an install with no repo-root
    `scripts/` tree, so it cannot import the validator's resolver. That copy therefore
    needs its own refusal proof: an adversarial round found that deleting its bool guard
    survived the entire suite, which would let `max_content_words: yes` forecast a
    ceiling of 1 while the gate enforced 78.
    """
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "handoff.md").write_text(_handoff_artifact(80), encoding="utf-8")
    base = ["version: 1", "repo: demo", "output_dir: docs"]
    planner = "skills/public/handoff/scripts/plan_handoff_run.py"

    # The bool arm is deliberately NOT here: measured, the resolver strips a refused
    # value before the planner ever sees it, so no adapter file can reach that guard.
    # It is defense-in-depth against a stale vendored resolver and is asserted directly
    # below, the same way the validator's isinstance re-check is.
    for value in ("yes", "0", "-5", "'1200'"):
        write_adapter(repo, "handoff-adapter.yaml", [*base, f"max_content_words: {value}"])
        plan = run_main(planner, "--repo-root", str(repo), "--intent", "refresh")

        # The conservative arm is the DEFAULT, never "unlimited" and never the
        # bool-coerced 1 that would refuse every possible handoff.
        assert "content_word_budget: 900" in plan.stdout, value
        assert "status: over_limit" in plan.stdout, value


@pytest.mark.parametrize(
    ("declared", "expected"),
    [(True, 900), ("1200", 900), (0, 900), (-1, 900), (None, 900), (1200, 1200)],
    ids=["bool", "string", "zero", "negative", "absent", "honored"],
)
def test_the_planners_own_guard_survives_a_resolver_that_did_not_refuse(declared, expected) -> None:
    """Reached only by handing the planner a payload directly, which is the point.

    A current resolver strips every bad value before the planner sees it, so this guard
    exists for the stale-resolver skew alone -- and a guard no adapter file can reach is
    a guard no CLI-level test can kill a mutant on. `isinstance(True, int)` is True, so
    without the bool arm `max_content_words: true` would forecast a ceiling of 1 while
    the gate enforced 900. The honored arm is the positive control.
    """
    planner = load_script_module("plan_handoff_run", ROOT / "skills/public/handoff/scripts/plan_handoff_run.py")
    adapter = {"data": {} if declared is None else {"max_content_words": declared}}

    assert planner._resolved_max_content_words(adapter) == expected


def test_a_refused_ceiling_is_an_adapter_error_and_leaves_the_default_enforced(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "charness-artifacts" / "debug").mkdir(parents=True)
    (repo / "charness-artifacts" / "debug" / "latest.md").write_text(
        long_artifact("# Debug Review", 700), encoding="utf-8"
    )
    base = ["version: 1", "repo: demo", "output_dir: charness-artifacts/debug"]

    for value, expected in (
        ("yes", "max_artifact_words must be an integer"),
        ("0", "max_artifact_words must be greater than or equal to 1"),
        ("'1500'", "max_artifact_words must be an integer"),
    ):
        write_adapter(repo, "debug-adapter.yaml", [*base, f"max_artifact_words: {value}"])
        resolved = run_main("skills/public/debug/scripts/resolve_adapter.py", "--repo-root", str(repo))
        gate = run_main("scripts/validate_debug_artifact.py", "--repo-root", str(repo), "--all")

        assert "valid: false" in resolved.stdout, value
        assert expected in resolved.stdout, value
        # The refused value must never become the ceiling, and must never disarm it
        # either: the conservative arm is the built-in default, not "unlimited".
        assert "get back under 1200" in gate.stderr, value
