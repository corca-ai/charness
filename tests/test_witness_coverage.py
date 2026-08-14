from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
# Bare sibling imports (`from prompt_mutant_lib import ...`, `from
# witness_coverage_lib import ...`), so scripts/ must be on sys.path when
# these are exec'd standalone here (mirrors test_generate_prompt_mutants.py).
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

lib = load_script_module("witness_coverage_lib_under_test", ROOT / "scripts" / "witness_coverage_lib.py")
cli = load_script_module("witness_coverage_under_test", ROOT / "scripts" / "witness_coverage.py")


SKILL_MD = (
    "---\n"
    "name: x\n"
    "---\n"
    "\n"
    "# X Skill\n"
    "\n"
    "## Bootstrap\n"
    "Do the bootstrap thing.\n"
    "\n"
    "## Guardrails\n"
    "Behave.\n"
)


def _write_fixture_skill(root: Path, skill: str = "x") -> None:
    plugin_dir = root / "plugins" / "charness" / "skills" / skill
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")


def _write_spec(eval_dir: Path, filename: str, *, rcf: list[str] | None = None, rsf: list[str] | None = None) -> None:
    eval_dir.mkdir(parents=True, exist_ok=True)
    spec = {
        "requiredCommandFragments": rcf or [],
        "requiredSummaryFragments": rsf or [],
    }
    (eval_dir / filename).write_text(json.dumps(spec), encoding="utf-8")


def _write_witness_map(eval_dir: Path, skill: str, scenario: str, entries: list[dict], spec_filename: str = "spec.json") -> Path:
    eval_dir.mkdir(parents=True, exist_ok=True)
    path = eval_dir / "witness-map.json"
    payload = {
        "schema_version": 1,
        "skill": skill,
        "scenarios": {scenario: {"spec": spec_filename, "entries": entries}},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _bootstrap_unit_prefix() -> str:
    return "plugins/charness/skills/x/SKILL.md#x-skill/bootstrap"


def _guardrails_unit_prefix() -> str:
    return "plugins/charness/skills/x/SKILL.md#x-skill/guardrails"


# --- verdict rules -----------------------------------------------------------


def test_witnessed_requires_deterministic_and_causal_witness(tmp_path: Path) -> None:
    _write_fixture_skill(tmp_path)
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json", rcf=["some-doc.md"])
    witness_map = _write_witness_map(
        eval_dir,
        "x",
        "s1",
        [
            {
                "unit": _bootstrap_unit_prefix(),
                "status": "witnessed",
                "witnesses": [
                    {
                        "channel": "required_command_fragment",
                        "value": "some-doc.md",
                        "causal_path": "Bootstrap owns the read instruction.",
                        "deterministic": True,
                    }
                ],
            },
            {
                "unit": _guardrails_unit_prefix(),
                "status": "witnessed",
                "witnesses": [
                    {
                        "channel": "judge",
                        "value": "guardrails honored",
                        "causal_path": "Only a judge can observe this.",
                        "deterministic": False,
                    }
                ],
            },
        ],
    )
    report = lib.compute_coverage(tmp_path, "x", "s1", witness_map)
    assert report["ok"] is True
    witnessed_ids = {w["unit_id"] for w in report["witnessed"]}
    assert any(uid.startswith(_bootstrap_unit_prefix()) for uid in witnessed_ids)
    assert not any(uid.startswith(_guardrails_unit_prefix()) for uid in witnessed_ids)
    # Judge-only witness entry is downgraded to UNTESTED and reported.
    downgraded_ids = {d["unit_id"] for d in report["downgraded_entries"]}
    assert any(uid.startswith(_guardrails_unit_prefix()) for uid in downgraded_ids)
    untested_ids = {u["unit_id"] for u in report["untested_debt"]}
    assert any(uid.startswith(_guardrails_unit_prefix()) for uid in untested_ids)
    # untested = downgraded guardrails (1) + unmapped preamble + unmapped x-skill h1 (2) = 3
    assert report["counts"] == {"witnessed": 1, "untested": 3, "excluded": 0}


def test_unmapped_live_unit_is_untested(tmp_path: Path) -> None:
    _write_fixture_skill(tmp_path)
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json")
    witness_map = _write_witness_map(eval_dir, "x", "s1", [])
    report = lib.compute_coverage(tmp_path, "x", "s1", witness_map)
    assert report["ok"] is True
    assert report["counts"]["witnessed"] == 0
    assert report["counts"]["excluded"] == 0
    reasons = {u["reason"] for u in report["untested_debt"]}
    assert reasons == {"unmapped"}
    # preamble + x-skill (h1) + bootstrap + guardrails = 4 live units, all unmapped
    assert report["counts"]["untested"] == 4


# --- stale / ambiguous / spec-floor fatal cases -------------------------------


def test_stale_prefix_is_fatal_and_listed(tmp_path: Path) -> None:
    _write_fixture_skill(tmp_path)
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json")
    stale_prefix = "plugins/charness/skills/x/SKILL.md#x-skill/does-not-exist"
    witness_map = _write_witness_map(
        eval_dir, "x", "s1", [{"unit": stale_prefix, "status": "untested", "witnesses": [], "reason": "n/a"}]
    )
    report = lib.compute_coverage(tmp_path, "x", "s1", witness_map)
    assert report["ok"] is False
    assert report["stale_entries"] == [stale_prefix]


def test_ambiguous_prefix_is_fatal_and_listed(tmp_path: Path) -> None:
    # Two headings that share heading_path text but differ in content produce
    # two distinct full unit ids with the SAME hashless prefix.
    duplicate_heading_md = (
        "# X Skill\n"
        "\n"
        "## Dup\n"
        "First body.\n"
        "\n"
        "## Dup\n"
        "Second, different body.\n"
    )
    plugin_dir = tmp_path / "plugins" / "charness" / "skills" / "x"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "SKILL.md").write_text(duplicate_heading_md, encoding="utf-8")
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json")
    ambiguous_prefix = "plugins/charness/skills/x/SKILL.md#x-skill/dup"
    witness_map = _write_witness_map(
        eval_dir, "x", "s1", [{"unit": ambiguous_prefix, "status": "untested", "witnesses": [], "reason": "n/a"}]
    )
    report = lib.compute_coverage(tmp_path, "x", "s1", witness_map)
    assert report["ok"] is False
    assert [a["unit"] for a in report["ambiguous_entries"]] == [ambiguous_prefix]
    assert len(report["ambiguous_entries"][0]["matches"]) == 2


def test_witness_value_absent_from_spec_floor_is_fatal(tmp_path: Path) -> None:
    _write_fixture_skill(tmp_path)
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json", rcf=["real-doc.md"])
    witness_map = _write_witness_map(
        eval_dir,
        "x",
        "s1",
        [
            {
                "unit": _bootstrap_unit_prefix(),
                "status": "witnessed",
                "witnesses": [
                    {
                        "channel": "required_command_fragment",
                        "value": "made-up-doc.md",
                        "causal_path": "Bogus.",
                        "deterministic": True,
                    }
                ],
            }
        ],
    )
    report = lib.compute_coverage(tmp_path, "x", "s1", witness_map)
    assert report["ok"] is False
    assert len(report["spec_floor_errors"]) == 1
    violation = report["spec_floor_errors"][0]
    assert violation["value"] == "made-up-doc.md"
    assert violation["channel"] == "required_command_fragment"


def test_trace_command_marker_is_not_checked_against_spec_floors(tmp_path: Path) -> None:
    _write_fixture_skill(tmp_path)
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json")  # no floors at all
    witness_map = _write_witness_map(
        eval_dir,
        "x",
        "s1",
        [
            {
                "unit": _bootstrap_unit_prefix(),
                "status": "witnessed",
                "witnesses": [
                    {
                        "channel": "trace_command_marker",
                        "value": "some_script.py",
                        "causal_path": "Free-form, checked later by S3.",
                        "deterministic": True,
                    }
                ],
            }
        ],
    )
    report = lib.compute_coverage(tmp_path, "x", "s1", witness_map)
    assert report["ok"] is True
    assert report["spec_floor_errors"] == []


# --- excluded / untested pass-through -----------------------------------------


def test_excluded_and_untested_pass_through_with_reason(tmp_path: Path) -> None:
    _write_fixture_skill(tmp_path)
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json")
    witness_map = _write_witness_map(
        eval_dir,
        "x",
        "s1",
        [
            {"unit": _bootstrap_unit_prefix(), "status": "excluded", "witnesses": [], "reason": "structural"},
            {"unit": _guardrails_unit_prefix(), "status": "untested", "witnesses": [], "reason": "no floor"},
        ],
    )
    report = lib.compute_coverage(tmp_path, "x", "s1", witness_map)
    assert report["ok"] is True
    excluded_reasons = {e["unit_id"].split("#", 1)[1]: e["reason"] for e in report["excluded"]}
    assert any(k.startswith("x-skill/bootstrap") and v == "structural" for k, v in excluded_reasons.items())
    untested_reasons = {
        u["unit_id"].split("#", 1)[1]: u["reason"] for u in report["untested_debt"] if "guardrails" in u["unit_id"]
    }
    assert any(v == "no floor" for v in untested_reasons.values())


# --- CLI -----------------------------------------------------------------


def test_cli_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--help"])
    assert excinfo.value.code == 0


def test_cli_default_json_and_markdown_both_work(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _write_fixture_skill(tmp_path)
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json")
    _write_witness_map(eval_dir, "x", "s1", [])

    rc = cli.main(["--repo-root", str(tmp_path), "--skill", "x", "--scenario", "s1"])
    assert rc == 0
    out = capsys.readouterr().out
    payload = yaml.safe_load(out)
    assert payload["skill"] == "x"
    assert payload["scenario"] == "s1"

    rc = cli.main(["--repo-root", str(tmp_path), "--skill", "x", "--scenario", "s1", "--markdown"])
    assert rc == 0
    md = capsys.readouterr().out
    assert md.startswith("# Witness coverage: x / s1")
    assert "Counts:" in md


def test_cli_default_witness_map_path(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _write_fixture_skill(tmp_path)
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json")
    _write_witness_map(eval_dir, "x", "s1", [])
    rc = cli.main(["--repo-root", str(tmp_path), "--skill", "x", "--scenario", "s1"])
    assert rc == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["ok"] is True


def test_cli_reports_nonzero_exit_on_fatal_stale_entry(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    _write_fixture_skill(tmp_path)
    eval_dir = tmp_path / "evals" / "cautilus" / "x-claim-fidelity"
    _write_spec(eval_dir, "spec.json")
    _write_witness_map(
        eval_dir,
        "x",
        "s1",
        [{"unit": "plugins/charness/skills/x/SKILL.md#nope", "status": "untested", "witnesses": [], "reason": "n/a"}],
    )
    rc = cli.main(["--repo-root", str(tmp_path), "--skill", "x", "--scenario", "s1"])
    assert rc != 0
    captured = capsys.readouterr()
    assert "FATAL" in captured.err


def test_missing_witness_map_raises() -> None:
    with pytest.raises(lib.WitnessCoverageError):
        lib.compute_coverage(Path("/tmp/does-not-exist-charness"), "nope", "s1", Path("/tmp/no-such-map.json"))


# --- real-repo smoke test -----------------------------------------------------


def test_real_repo_handoff_refresh_smoke() -> None:
    real_repo_root = ROOT
    eval_dir = real_repo_root / "evals" / "cautilus" / "handoff-claim-fidelity"
    witness_map_path = eval_dir / "witness-map.json"
    if not witness_map_path.is_file():
        pytest.skip("evals/cautilus/handoff-claim-fidelity/witness-map.json not present in this checkout")

    report = lib.compute_coverage(real_repo_root, "handoff", "refresh")
    assert report["ok"] is True
    witnessed_ids = {w["unit_id"].rsplit("@", 1)[0] for w in report["witnessed"]}
    assert witnessed_ids == {
        "plugins/charness/skills/handoff/SKILL.md#handoff/bootstrap",
        "plugins/charness/skills/handoff/SKILL.md#handoff/workflow",
        "plugins/charness/skills/handoff/SKILL.md#handoff/closeout-vocabulary",
    }
    reference_unit_ids = {
        u["unit_id"] for u in lib.live_units(real_repo_root, "handoff") if "/references/" in u["unit_id"]
    }
    untested_ids = {u["unit_id"] for u in report["untested_debt"]}
    assert reference_unit_ids  # sanity: there are reference units to check
    assert reference_unit_ids <= untested_ids  # every references/*.md unit is UNTESTED
