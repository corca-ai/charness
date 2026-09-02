"""Behavior tests for gate entrypoints and refusal branches that had no reader.

Every test here names a behavior an operator or a runner depends on: a gate that
cannot observe its subject must report NOT-RUN rather than pass, a `main()` must
return the byte its caller reads as a verdict, and a payload-emitting entrypoint
must actually emit the payload it computed. The shared shape is that each of
these was reachable only through a real subprocess run, so nothing in-process
asserted it.
"""

from __future__ import annotations

import json
import runpy
import stat
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

from runtime_bootstrap import import_repo_module
from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]


def _write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


def _executable(path: Path, body: str) -> Path:
    _write(path, body)
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


# ---------------------------------------------------------------------------
# tools/check_closeout_classification_parity.py
#
# This gate's whole contract is that an UNOBSERVED site resolves to not-run and
# never to a pass. Every refusal branch below was unread, which is precisely the
# failure mode (#586) the gate exists to refuse: a check whose green says nothing.
# ---------------------------------------------------------------------------

_parity = import_repo_module(__file__, "tools.check_closeout_classification_parity")

CANONICAL_REL = _parity.CANONICAL_REL


def _canonical_repo(tmp_path: Path, body: str) -> Path:
    """A repo whose only content is the canonical vocabulary module."""
    repo = tmp_path / "repo"
    _write(repo / CANONICAL_REL, body)
    return repo


def test_absent_canonical_module_is_not_run_never_a_pass(tmp_path: Path) -> None:
    """A repo with no canonical vocabulary must report not-run, not parity.

    Zero sites disagreeing looks identical to perfect parity. If absence resolved
    to `pass`, deleting the vocabulary module would turn this proof surface green.
    """
    repo = tmp_path / "empty"
    repo.mkdir()

    result = _parity.evaluate(repo)

    assert result["status"] == "not-run"
    assert CANONICAL_REL in result["reason"] and "is absent" in result["reason"]
    assert result["sites"] == []
    assert _parity.report(result, repo)["remedy"].startswith("A site could not be observed")


def test_canonical_module_that_crashes_on_import_is_not_run(tmp_path: Path) -> None:
    """An import-time crash in a probed module is an unobserved site, not a pass.

    The gate loads foreign modules by path. An escaping exception would take the
    whole report down; a swallowed one would read as agreement. It must name the
    exception type instead.
    """
    repo = _canonical_repo(tmp_path, "raise RuntimeError('vocabulary module is broken')\n")

    result = _parity.evaluate(repo)

    assert result["status"] == "not-run"
    assert "did not import: RuntimeError" in result["reason"]
    assert "vocabulary module is broken" in result["reason"]


def test_canonical_module_without_the_attribute_is_not_run(tmp_path: Path) -> None:
    """A renamed/deleted `CLASSIFICATIONS` must be reported by name, not inferred away."""
    repo = _canonical_repo(tmp_path, "RENAMED = ('bug',)\n")

    result = _parity.evaluate(repo)

    assert result["status"] == "not-run"
    assert f"{CANONICAL_REL} no longer defines {_parity.CANONICAL_ATTR}" in result["reason"]


def test_empty_canonical_vocabulary_is_not_run(tmp_path: Path) -> None:
    """An empty vocabulary makes every site vacuously in parity, so it cannot pass."""
    repo = _canonical_repo(tmp_path, "CLASSIFICATIONS = ()\n")

    result = _parity.evaluate(repo)

    assert result["status"] == "not-run"
    assert result["reason"] == f"{CANONICAL_REL}:{_parity.CANONICAL_ATTR} is empty"
    assert result["sites"] == []


def test_membership_probe_refuses_a_value_that_is_not_an_enumeration(tmp_path: Path) -> None:
    """A string passes `in` by SUBSTRING, so a stringified vocabulary must not be probed.

    `"bug" in "bug,task"` is True, so a site whose tuple had degraded to a string
    would report perfect parity while enumerating nothing. The type check is what
    stops that, and it must surface as not-run.
    """
    repo = tmp_path / "repo"
    _write(repo / "site.py", "KNOWN = 'bug,task,question'\n")
    build = _parity._membership_probe("site.py", "KNOWN")

    with pytest.raises(_parity.ProbeError) as excinfo:
        build(repo, ("bug",))

    assert "site.py:KNOWN is str, not an enumeration" in str(excinfo.value)


def test_regex_probe_refuses_an_attribute_that_is_not_a_compiled_pattern(tmp_path: Path) -> None:
    """A regex site whose attribute became a plain string cannot be matched against."""
    repo = tmp_path / "repo"
    _write(repo / "site.py", "PATTERN = 'Classification: (?P<classification>bug)'\n")
    build = _parity._regex_probe("site.py", "PATTERN")

    with pytest.raises(_parity.ProbeError) as excinfo:
        build(repo, ("bug",))

    assert "site.py:PATTERN is not a compiled pattern" in str(excinfo.value)


def test_regex_probe_refuses_a_pattern_that_observes_nothing(tmp_path: Path) -> None:
    """A pattern matching neither a real nor a sentinel value observed no vocabulary.

    Liveness is "did this probe see ANYTHING". A pattern that has stopped matching
    the production line would otherwise report every canonical value missing, which
    reads as a parity failure in the surface rather than a broken probe.
    """
    repo = tmp_path / "repo"
    _write(repo / "site.py", "import re\nPATTERN = re.compile(r'(?P<classification>never-matches-me)')\n")
    build = _parity._regex_probe("site.py", "PATTERN")

    with pytest.raises(_parity.ProbeError) as excinfo:
        build(repo, ("bug", "task"))

    assert "matched no probe line at all" in str(excinfo.value)


def test_release_cli_probe_is_not_run_when_the_argv_no_longer_reaches_the_flag(tmp_path: Path) -> None:
    """A `parse_args` that refuses every canonical value means the probe's argv is stale.

    The probe drives argparse with a real argv. If the surrounding flags are
    renamed the parse fails for every value, which must read as "nothing was
    observed" rather than "this CLI dropped the whole vocabulary".
    """
    repo = tmp_path / "repo"
    _write(
        repo / "skills/public/release/scripts/publish_release_cli.py",
        """\
        def parse_args():
            raise SystemExit(2)
        """,
    )

    with pytest.raises(_parity.ProbeError) as excinfo:
        _parity._release_cli_choices_probe(repo, ("bug", "task"))

    assert "refused a canonical classification through an otherwise-valid argv" in str(excinfo.value)


def test_issue_plan_probe_is_not_run_when_the_planner_raises(tmp_path: Path) -> None:
    """An unbuildable plan is an unobserved dispatch table, and names the exception."""
    repo = tmp_path / "repo"
    _write(
        repo / "skills/public/issue/scripts/issue_plan.py",
        """\
        def build_resolve_plan(repo_root, a, b):
            raise KeyError('adapter')
        """,
    )

    with pytest.raises(_parity.ProbeError) as excinfo:
        _parity._issue_plan_actions_probe(repo, ("bug",))

    assert "build_resolve_plan raised KeyError" in str(excinfo.value)


def test_issue_plan_probe_is_not_run_when_the_plan_has_no_dispatch_table(tmp_path: Path) -> None:
    """An empty `classification_actions` accepts nothing, so it must not read as a failure.

    A plan with no dispatch keys would report every classification missing. That is
    indistinguishable from a real parity break, so the gate has to say the dispatch
    was never observed.
    """
    repo = tmp_path / "repo"
    _write(
        repo / "skills/public/issue/scripts/issue_plan.py",
        """\
        def build_resolve_plan(repo_root, a, b):
            return {'classification_actions': {}}
        """,
    )

    with pytest.raises(_parity.ProbeError) as excinfo:
        _parity._issue_plan_actions_probe(repo, ("bug",))

    assert "emitted no classification_actions" in str(excinfo.value)


def test_over_permissive_site_remedy_says_narrow_rather_than_add(tmp_path: Path) -> None:
    """A site accepting values OUTSIDE the vocabulary needs the opposite repair.

    "Add the missing classification" is unsatisfiable here -- nothing is missing.
    An over-permissive site has stopped enumerating anything, and the remedy has to
    tell the reader to narrow it.
    """
    result = {
        "status": "fail",
        "canonical": ["bug"],
        "sites": [
            {
                "id": "over-permissive",
                "status": "fail",
                "accepts_non_classification": ["banana"],
            }
        ],
    }

    remedy = _parity.report(result, tmp_path)["remedy"]

    assert "accepts values OUTSIDE the vocabulary" in remedy
    assert "Narrow that surface back to the canonical set." in remedy
    # The missing-value remedy must NOT appear: nothing is missing here.
    assert "Add it to that" not in remedy


# ---------------------------------------------------------------------------
# scripts/gates/validate_adapters.py -- resolver payload parsing
# ---------------------------------------------------------------------------

_validate_adapters = import_repo_module(__file__, "scripts.gates.validate_adapters")


def _resolver(tmp_path: Path, skill_id: str, body: str) -> Path:
    """A fake `<skill>/scripts/resolve_adapter.py`, since the skill id is read from the path."""
    return _write(tmp_path / "skills" / skill_id / "scripts" / "resolve_adapter.py", body)


def test_resolver_emitting_unreadable_output_is_a_validation_error(tmp_path: Path) -> None:
    """A resolver whose payload cannot be parsed must fail the gate, not crash it.

    The raw parser error ("expected node content", offsets) says nothing about
    WHICH resolver misbehaved, so the gate re-raises with the path.
    """
    path = _resolver(tmp_path, "quality", "print('{unclosed: [')\n")

    with pytest.raises(_validate_adapters.ValidationError) as excinfo:
        _validate_adapters.validate_resolver(path, tmp_path)

    assert str(path) in str(excinfo.value)
    assert "did not emit a readable payload" in str(excinfo.value)


def test_resolver_emitting_a_non_mapping_payload_is_a_validation_error(tmp_path: Path) -> None:
    """A parseable-but-non-mapping payload must be refused before `.get` is reached.

    A YAML list parses fine and would raise AttributeError deep inside the field
    checks, blaming the gate rather than the resolver.
    """
    path = _resolver(tmp_path, "quality", "print('- one\\n- two')\n")

    with pytest.raises(_validate_adapters.ValidationError) as excinfo:
        _validate_adapters.validate_resolver(path, tmp_path)

    assert "payload output must be a mapping" in str(excinfo.value)


def test_resolver_payload_is_parsed_as_json_when_pyyaml_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without PyYAML the gate falls back to `json.loads`, matching the producer.

    `yaml_output.render_yaml` degrades to compact JSON on a PyYAML-less
    interpreter, so the resolver emits JSON there. Hoisting `import yaml` to module
    scope once turned this gate from degrades-to-no-gate into dies-at-import; the
    fallback is what keeps it a gate.
    """
    monkeypatch.setitem(sys.modules, "yaml", None)
    passing = _resolver(tmp_path, "quality", "print('{\"valid\": true}')\n")

    # A JSON payload still validates with PyYAML unavailable.
    _validate_adapters.validate_resolver(passing, tmp_path)

    # ...and YAML-only syntax is now genuinely unreadable, so the gate refuses it
    # rather than silently accepting whatever `json.loads` happened to tolerate.
    yaml_only = _resolver(tmp_path, "impl", "print('valid: true')\n")
    with pytest.raises(_validate_adapters.ValidationError, match="did not emit a readable payload"):
        _validate_adapters.validate_resolver(yaml_only, tmp_path)


# ---------------------------------------------------------------------------
# tools/check_export_self_sufficiency.py -- main() exit bytes
# ---------------------------------------------------------------------------

EXPORT_GATE = ROOT / "tools" / "check_export_self_sufficiency.py"
_export_gate = load_script_module("coverage_debt_export_self_sufficiency", EXPORT_GATE)


def _export_repo(tmp_path: Path, entrypoint_body: str, *, doc: str) -> Path:
    """A minimal repo that BUILDS an export: a packaging manifest plus a checked-in tree."""
    repo = tmp_path / "repo"
    # The manifest is schema-validated and pins the export root to
    # `./plugins/<package_id>`, so the real one is reused verbatim; hand-rolling a
    # minimal stand-in tests a shape the packaging validator would refuse.
    manifest = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))
    export_rel = manifest["codex"]["repo_marketplace"]["default_source_path"].removeprefix("./")
    _write(repo / "packaging" / "charness.json", json.dumps(manifest, indent=2) + "\n")
    _write(repo / manifest["source"]["readme"], "# Demo\n")
    for key in ("skills_dir", "public_skills_dir", "support_skills_dir", "profiles_dir", "presets_dir", "integrations_dir"):
        (repo / manifest["source"][key]).mkdir(parents=True, exist_ok=True)
    _write(repo / export_rel / "skills" / "demo" / "SKILL.md", doc)
    _write(repo / export_rel / "skills" / "demo" / "scripts" / "entry.py", entrypoint_body)
    return repo


def test_export_gate_main_returns_zero_for_a_self_sufficient_export(tmp_path: Path) -> None:
    """A green export exits 0, and the runner reads that byte as the verdict.

    A `main()` that computed a passing payload and returned a truthy byte anyway
    would red-line every consumer, so the exit code is the contract, not the text.
    """
    repo = _export_repo(
        tmp_path,
        "import json\n\n\ndef main() -> int:\n    return 0\n",
        doc="# Demo\n\nRun `python3 $SKILL_DIR/scripts/entry.py`.\n",
    )

    result = run_loaded_script_main(
        "check_export_self_sufficiency.py", _export_gate, "--repo-root", str(repo)
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "pass"
    assert payload["unguarded_entrypoint_imports"] == []


def test_export_gate_main_returns_one_for_an_unguarded_documented_entrypoint(tmp_path: Path) -> None:
    """A documented entrypoint importing a third-party package unguarded BLOCKS (#634).

    That is the reported consumer failure exactly: follow the SKILL.md, run the
    command, meet a bare ModuleNotFoundError. Exit 1 -- not the `unestablished` 3 --
    is what makes it a blocking lane.
    """
    repo = _export_repo(
        tmp_path,
        "import yaml\n\n\ndef main() -> int:\n    return 0\n",
        doc="# Demo\n\nRun `python3 $SKILL_DIR/scripts/entry.py`.\n",
    )

    result = run_loaded_script_main(
        "check_export_self_sufficiency.py", _export_gate, "--repo-root", str(repo)
    )

    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["status"] == "fail"
    assert payload["unguarded_entrypoint_imports"], payload
    assert payload["remedy"] == [_export_gate.UNGUARDED_ENTRYPOINT_REMEDY]


def test_export_gate_run_as_a_program_exits_with_the_code_main_returned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The `__main__` guard must PROPAGATE main()'s byte, not swallow it.

    An entrypoint that calls `main()` without raising SystemExit on its result
    exits 0 for every verdict, which is a failing gate that reports success -- the
    exact shape this repo refuses.
    """
    repo = _export_repo(
        tmp_path,
        "import yaml\n\n\ndef main() -> int:\n    return 0\n",
        doc="# Demo\n\nRun `python3 $SKILL_DIR/scripts/entry.py`.\n",
    )
    monkeypatch.setattr(sys, "argv", ["check_export_self_sufficiency.py", "--repo-root", str(repo)])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(EXPORT_GATE), run_name="__main__")

    assert excinfo.value.code == 1
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "fail"


# ---------------------------------------------------------------------------
# scripts/check_supply_chain_online.py
# ---------------------------------------------------------------------------

_supply_chain_online = load_script_module(
    "coverage_debt_check_supply_chain_online", ROOT / "scripts" / "check_supply_chain_online.py"
)


def test_supply_chain_online_reports_the_absence_of_any_audit_surface(tmp_path: Path) -> None:
    """A repo with no npm/pnpm/uv surface must SAY so and exit 0, not exit silently.

    Silence here reads as "the online audit ran clean". The payload names the
    supported surfaces so an operator can tell "nothing to audit" from "nothing
    detected because this wrapper does not know your ecosystem".
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_loaded_script_main(
        "check_supply_chain_online.py", _supply_chain_online, "--repo-root", str(repo)
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["surfaces"] == []
    assert "npm, pnpm, and uv" in payload["message"]


def _npm_repo(tmp_path: Path, exit_code: int) -> tuple[Path, dict[str, str]]:
    repo = tmp_path / "repo"
    _write(
        repo / "package.json",
        json.dumps({"private": True, "packageManager": "npm@10.0.0", "dependencies": {"left-pad": "1.3.0"}}) + "\n",
    )
    _write(repo / "package-lock.json", "{}\n")
    bin_dir = tmp_path / "bin"
    _executable(bin_dir / "npm", f"#!/bin/bash\necho 'audit report'\nexit {exit_code}\n")
    return repo, {"PATH": f"{bin_dir}:/usr/bin:/bin"}


def test_supply_chain_online_folds_a_pass_fail_reading_into_each_surface_row(tmp_path: Path) -> None:
    """Each audited surface carries an explicit PASS/FAIL, not just a raw exit code.

    The human renderer that used to state the verdict is gone; if the reading did
    not move into the payload it would simply be absent, leaving a reader to
    interpret `exit_code` themselves.
    """
    repo, env = _npm_repo(tmp_path, 0)

    result = run_loaded_script_main(
        "check_supply_chain_online.py", _supply_chain_online, "--repo-root", str(repo), env=env
    )

    assert result.returncode == 0, result.stderr
    (row,) = yaml.safe_load(result.stdout)["surfaces"]
    assert row["tool"] == "npm"
    assert row["status"] == "PASS"
    assert row["exit_code"] == 0
    assert row["triage_owner"] == _supply_chain_online.DEFAULT_TRIAGE_OWNER
    assert row["command"][:2] == ["npm", "audit"]


def test_supply_chain_online_fails_when_an_audited_surface_fails(tmp_path: Path) -> None:
    """A nonzero audit must reach the runner as a nonzero exit, not a rendered row only."""
    repo, env = _npm_repo(tmp_path, 1)

    result = run_loaded_script_main(
        "check_supply_chain_online.py", _supply_chain_online, "--repo-root", str(repo), env=env
    )

    assert result.returncode == 1
    (row,) = yaml.safe_load(result.stdout)["surfaces"]
    assert row["status"] == "FAIL"


# ---------------------------------------------------------------------------
# tools/run_evals.py -- checked-in quality adapter scenarios
# ---------------------------------------------------------------------------

_run_evals = import_repo_module(__file__, "tools.run_evals")


def test_eval_scenario_reads_the_checked_in_quality_adapter_payload() -> None:
    """The checked-in quality adapter must resolve with this repo's canonical settings.

    The scenario parses the resolver's payload and asserts the gate command, the
    fragile-coverage margin, the floor policy, and the pytest reference format. A
    scenario that never read the payload would pass on any resolver that exits 0.
    """
    _run_evals.scenario_quality_adapter_checked_in(ROOT)


def test_eval_scenario_reads_bootstrap_and_resolve_payloads_for_a_fresh_repo() -> None:
    """Bootstrapping quality into a bare repo must report installed/deferred posture.

    Both halves are read from parsed payloads: the bootstrap's `field_statuses` and
    `preset_lineage`, and then the resolver's view of the adapter it just wrote.
    """
    _run_evals.scenario_quality_bootstrap_posture(ROOT)


# ---------------------------------------------------------------------------
# scripts/gates/check_github_actions.py
# ---------------------------------------------------------------------------

_github_actions = import_repo_module(__file__, "scripts.gates.check_github_actions")


def test_github_actions_report_states_that_no_workflows_were_found() -> None:
    """No workflow files is an EMPTY SCOPE, and the payload has to say so.

    Zero findings over zero files renders identically to a validated repo. The
    summary is the only thing distinguishing "checked and clean" from "checked
    nothing", and the remedy/guidance blocks must stay absent so there is nothing
    to act on.
    """
    payload = _github_actions.report({"workflow_files": [], "findings": []})

    assert payload["summary"] == "No GitHub Actions workflows detected."
    assert "remedies" not in payload and "guidance" not in payload
    # A repo WITH workflows and no findings must read differently.
    validated = _github_actions.report({"workflow_files": [".github/workflows/ci.yml"], "findings": []})
    assert validated["summary"] != payload["summary"]
    assert "1 workflow file(s)" in validated["summary"]


# ---------------------------------------------------------------------------
# scripts/filter_cosmic_ray_mutants.py -- main()
# ---------------------------------------------------------------------------

_filter_mutants = load_script_module(
    "coverage_debt_filter_cosmic_ray_mutants", ROOT / "scripts" / "filter_cosmic_ray_mutants.py"
)


def _cosmic_ray_session(repo: Path) -> Path:
    """A real Cosmic Ray session holding one annotation-union work item."""
    from cosmic_ray.work_db import use_db
    from cosmic_ray.work_item import MutationSpec, WorkItem

    _write(
        repo / "demo.py",
        """\
        from __future__ import annotations


        def demo(value: int | None = None) -> str:
            return str(value)
        """,
    )
    session = repo / "session.sqlite"
    pipe_col = (repo / "demo.py").read_text(encoding="utf-8").splitlines()[3].index("|")
    with use_db(session) as db:
        db.add_work_item(
            WorkItem(
                job_id="annotation-union",
                mutations=(
                    MutationSpec(
                        module_path=Path("demo.py"),
                        operator_name=f"{_filter_mutants.BITOR_OPERATOR_PREFIX}Add",
                        occurrence=0,
                        start_pos=(4, pipe_col),
                        end_pos=(4, pipe_col + 1),
                    ),
                ),
            )
        )
    return session


def test_mutant_filter_main_reports_what_it_removed_from_the_run(tmp_path: Path) -> None:
    """The payload must name the filtering as deliberate removal, not report a clean sweep.

    `skipped`/`inspected` counts alone read as "the run had nothing to do". The
    `filtered` label is this file's declared evidence term precisely so a skipped
    total cannot be mistaken for a swept-clean session.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    session = _cosmic_ray_session(repo)

    result = run_loaded_script_main(
        "filter_cosmic_ray_mutants.py",
        _filter_mutants,
        "--repo-root",
        str(repo),
        "--session",
        str(session),
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["inspected"] == 1
    assert payload["skipped"] == 1
    assert payload["skipped_annotation"] == 1
    assert payload["filtered"] == (
        "filtered 1 mutants from 1 pending mutants "
        "(1 annotation unions, 0 uncovered lines, 0 trivial entry guards)"
    )


def test_mutant_filter_main_refuses_a_missing_session(tmp_path: Path) -> None:
    """A missing session exits 2 rather than reporting zero filtered mutants."""
    result = run_loaded_script_main(
        "filter_cosmic_ray_mutants.py",
        _filter_mutants,
        "--repo-root",
        str(tmp_path),
        "--session",
        str(tmp_path / "absent.sqlite"),
    )

    assert result.returncode == 2
    assert "Cosmic Ray session not found" in result.stderr


# ---------------------------------------------------------------------------
# scripts/gates/validate_skill_ergonomics.py -- the thin repo entrypoint
# ---------------------------------------------------------------------------

_ergonomics_entrypoint = load_script_module(
    "coverage_debt_validate_skill_ergonomics", ROOT / "scripts" / "gates" / "validate_skill_ergonomics.py"
)


def test_skill_ergonomics_entrypoint_emits_the_helper_report_and_its_verdict(tmp_path: Path) -> None:
    """The entrypoint must EMIT the helper's report, not just return its verdict byte.

    A gate that exits 1 with no payload tells an operator that something is wrong
    and nothing about what. The report is the whole diagnostic, so an entrypoint
    that computed it and dropped it would be a silent red lane.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_loaded_script_main(
        "validate_skill_ergonomics.py", _ergonomics_entrypoint, "--repo-root", str(repo)
    )

    payload = yaml.safe_load(result.stdout)
    assert isinstance(payload, dict) and payload, result.stdout
    expected_code = 1 if _ergonomics_entrypoint.HELPER.has_failures(payload) else 0
    assert result.returncode == expected_code


# ---------------------------------------------------------------------------
# scripts/agent_browser_runtime_guard.py -- default inspect mode
# ---------------------------------------------------------------------------

_browser_guard = load_script_module(
    "coverage_debt_agent_browser_runtime_guard", ROOT / "scripts" / "agent_browser_runtime_guard.py"
)


def test_runtime_guard_without_flags_inspects_and_never_refuses(tmp_path: Path) -> None:
    """The bare invocation is an INSPECTION: it prints the runtime payload and exits 0.

    The refusing modes are opt-in (`--doctor-check`, `--assert-no-orphans`). If the
    default were to exit nonzero on residue it would turn every incidental `python3
    agent_browser_runtime_guard.py` into a gate, and if it printed nothing the
    inspection would have no output at all.
    """
    checkout = tmp_path / "checkout"
    checkout.mkdir()

    result = run_loaded_script_main(
        "agent_browser_runtime_guard.py", _browser_guard, "--repo-root", str(checkout)
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    runtime = payload["runtime"]
    # A fresh throwaway checkout owns no agent-browser processes.
    assert runtime["orphan_daemon_count"] == 0
    assert _browser_guard.runtime_residue_total(runtime) == 0


# ---------------------------------------------------------------------------
# scripts/gates/inventory_boundary_bypass.py -- --output
# ---------------------------------------------------------------------------

_boundary_inventory = load_script_module(
    "coverage_debt_inventory_boundary_bypass", ROOT / "scripts" / "gates" / "inventory_boundary_bypass.py"
)


def test_boundary_inventory_writes_the_same_document_it_prints(tmp_path: Path) -> None:
    """`--output` must persist byte-identical content to stdout, and create its parent.

    Two renderings would let a checked-in artifact drift from what the operator
    just read. A missing parent directory has to be created, or the flag fails on
    the artifact path this repo actually uses.
    """
    repo = tmp_path / "repo"
    _write(
        repo / "tests" / "test_demo.py",
        """\
        import subprocess


        def test_demo():
            subprocess.run(["python3", "scripts/demo.py"])
        """,
    )
    _write(
        repo / "scripts" / "demo.py",
        "def main() -> int:\n    return 0\n\n\nif __name__ == '__main__':\n    raise SystemExit(main())\n",
    )
    out_path = tmp_path / "artifacts" / "nested" / "inventory.yaml"

    result = run_loaded_script_main(
        "inventory_boundary_bypass.py",
        _boundary_inventory,
        "--repo-root",
        str(repo),
        "--summary",
        "--output",
        str(out_path),
    )

    assert result.returncode == 0, result.stderr
    assert out_path.read_text(encoding="utf-8") == result.stdout
    payload = yaml.safe_load(out_path.read_text(encoding="utf-8"))
    assert payload["summary"]["candidate_count"] == 1


# ---------------------------------------------------------------------------
# Skill runtime bootstrap discovery
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "module_name, module_rel",
    [
        ("coverage_debt_debug_artifact_state", "skills/public/debug/scripts/debug_artifact_state.py"),
        ("coverage_debt_seed_retro_memory", "skills/public/setup/scripts/seed_retro_memory.py"),
    ],
)
def test_skill_script_fails_loudly_when_its_runtime_bootstrap_is_unreachable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, module_name: str, module_rel: str
) -> None:
    """A skill script copied outside its package must name the missing bootstrap.

    These scripts locate `skill_runtime_bootstrap.py` by walking their own
    ancestors, so a partial export (or a file copied out of the tree) leaves the
    search empty. Falling through would raise `NameError: SKILL_RUNTIME` at the
    first use, blaming the wrong thing; the ImportError names the file to ship.
    """
    module = load_script_module(module_name, ROOT / module_rel)
    stranded = tmp_path / "stranded" / Path(module_rel).name
    stranded.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(module, "__file__", str(stranded))

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        module._load_skill_runtime_bootstrap()
