"""SC20: an exported artifact cannot depend on what the export does not ship.

THE TRAP THIS FILE EXISTS TO AVOID, recorded on the issue before the slice
started: `tests/repo_copy.py` clones `packaging/` into every fixture, and
`test_bootstrap_runtime.py` copies `bootstrap-python.json` in explicitly. A test
written inside that harness manufactures the dependency it should have proven
absent, and PASSES AGAINST THE DEFECT. So the positive assertions here run
against the REAL materialized export tree, and the fixtures below are hand-built
minimal trees rather than repo copies.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import quality_label_universe

from runtime_bootstrap import import_repo_module

from .support import ROOT

_ANCHOR = str(ROOT / "scripts/x.py")
_lib = import_repo_module(_ANCHOR, "tools.export_self_sufficiency_lib")
_gate = import_repo_module(_ANCHOR, "tools.check_export_self_sufficiency")


# --- against the real export tree ---------------------------------------------


@pytest.mark.slow_corpus
def test_no_documented_entrypoint_crashes_on_a_bare_import() -> None:
    """The reported failure, asserted on the artifact a consumer installs: they
    followed a SKILL.md, ran the command, and got a bare ModuleNotFoundError."""
    payload = _gate.run_check(ROOT)

    assert payload["unguarded_entrypoint_imports"] == [], (
        "a script the export tells a consumer to RUN imports a third-party package unguarded"
    )
    assert payload["documented_entrypoint_count"] > 50, (
        "the entrypoint set is derived from exported docs; a near-empty set would "
        "make this arm green by scanning nothing"
    )


def test_declaring_a_package_is_not_the_question_the_gate_asks() -> None:
    """Pinned because the first build of this arm asked exactly that and was
    refuted in one move: shipping `packaging/bootstrap-requirements.txt` declared
    pyyaml, jsonschema and packaging for the WHOLE export at a stroke, so ~36 bare
    imports kept raising the reported error while the gate went green. The
    undeclared list survives as an advisory inventory and must not gate."""
    payload = _gate.run_check(ROOT)

    assert {"pyyaml", "jsonschema", "packaging"} <= set(payload["declared_distributions"])
    assert "advisory_undeclared_dependencies" in payload
    assert "not a verdict" in payload["advisory_dependency_note"]


def test_the_export_ships_the_bootstrap_contract_beside_the_installer() -> None:
    """Stated as its own assertion rather than inferred from the arm above: the
    dependency arm would also go green if the installer stopped being exported."""
    export_root = ROOT / "plugins" / "charness"

    assert (export_root / "scripts" / "bootstrap_runtime.py").is_file()
    assert (export_root / "packaging" / "bootstrap-python.json").is_file()
    assert (export_root / "packaging" / "bootstrap-requirements.txt").is_file()


def test_a_third_party_name_that_collides_with_an_exported_entry_is_still_checked() -> None:
    """`packaging` is BOTH a declared dependency and, since this slice shipped the
    bootstrap contract, a top-level directory of the export. Treating every
    top-level entry name as local silently excused `from packaging.version import
    ...` in two exported modules -- the fix for one instance blinding the arm to
    another, measured by a round-1 reviewer."""
    local = _lib._local_module_names(ROOT / "plugins" / "charness")

    assert "packaging" not in local, "a data directory must not shadow a distribution"
    assert "yaml_output" in local, "a real exported module is still local"
    assert "scripts" in local, "a directory that contains Python is still local"


@pytest.mark.slow_corpus
def test_consumer_owned_roots_are_not_reported_against_the_real_export() -> None:
    """The negative case that decides whether the check is usable at all.

    `.agents/`, `charness-artifacts/`, `docs/index.md` and the rest are seeded
    or scanned at RUNTIME in the consumer's own repo. Shipping filled copies
    would overwrite consumer config, so "not shipped" is correct there and a
    check that reports them would be turned off within a day."""
    payload = _gate.run_check(ROOT)
    reported = {finding["segment"] for finding in payload["advisory_unshipped_path_sites"]}

    assert reported.isdisjoint(_lib.CONSUMER_OWNED_ROOTS), reported
    for owned in (".agents", "charness-artifacts", "docs"):
        assert _lib.CONSUMER_OWNED_ROOTS[owned], "every exemption carries its reason"


@pytest.mark.slow_corpus
def test_the_real_export_passes_its_own_gate() -> None:
    payload = _gate.run_check(ROOT)
    assert payload["status"] == "pass", payload


# --- arm behaviour, on hand-built trees -----------------------------------------


def _minimal_export(tmp_path: Path, *, source: str, requirements: str | None = None) -> Path:
    export_root = tmp_path / "plugins" / "charness"
    (export_root / "scripts").mkdir(parents=True)
    (export_root / "scripts" / "thing.py").write_text(source, encoding="utf-8")
    if requirements is not None:
        (export_root / "packaging").mkdir()
        (export_root / "packaging" / "bootstrap-requirements.txt").write_text(
            requirements, encoding="utf-8"
        )
    return export_root


def _documented_export(tmp_path: Path, *, source: str) -> Path:
    """A minimal export whose SKILL.md TELLS a consumer to run the script."""
    export_root = tmp_path / "plugins" / "charness"
    (export_root / "skills" / "demo" / "scripts").mkdir(parents=True)
    (export_root / "skills" / "demo" / "scripts" / "entry.py").write_text(source, encoding="utf-8")
    (export_root / "skills" / "demo" / "SKILL.md").write_text(
        'Run:\n\n```bash\npython3 "$SKILL_DIR/scripts/entry.py" --repo-root .\n```\n',
        encoding="utf-8",
    )
    return export_root


def test_a_documented_entrypoint_with_a_bare_import_is_REFUSED(tmp_path: Path) -> None:
    """The blocking arm, on the exact shape that was reported."""
    export_root = _documented_export(tmp_path, source="import yaml\n")

    findings = _lib.unguarded_entrypoint_import_findings(export_root)

    assert [finding["module"] for finding in findings] == ["yaml"]
    assert findings[0]["entrypoint"] == "entry.py"


def test_declaring_the_package_does_not_silence_the_blocking_arm(tmp_path: Path) -> None:
    """A requirements file installs nothing. This is the refutation, pinned."""
    export_root = _documented_export(tmp_path, source="import yaml\n")
    (export_root / "packaging").mkdir()
    (export_root / "packaging" / "bootstrap-requirements.txt").write_text(
        "PyYAML>=6,<7\n", encoding="utf-8"
    )

    assert _lib.unguarded_entrypoint_import_findings(export_root), (
        "declaring a package must not make a crashing entrypoint pass"
    )


def test_a_guarded_entrypoint_import_is_accepted(tmp_path: Path) -> None:
    export_root = _documented_export(
        tmp_path,
        source="try:\n    import yaml\nexcept ModuleNotFoundError:\n    raise SystemExit('install PyYAML')\n",
    )

    assert _lib.unguarded_entrypoint_import_findings(export_root) == []


def test_a_FUNCTION_level_import_is_not_treated_as_guarded(tmp_path: Path) -> None:
    """It only DEFERS the same crash to call time. The first version of this
    module claimed function-level imports were the guarded form; a round-2
    reviewer measured six live counter-instances in the export."""
    export_root = _documented_export(
        tmp_path, source="def main():\n    import yaml\n    return yaml\n"
    )

    assert [f["module"] for f in _lib.unguarded_entrypoint_import_findings(export_root)] == ["yaml"]


def test_an_undocumented_module_is_not_gated(tmp_path: Path) -> None:
    """Scope, asserted rather than assumed: the blocking arm covers what a
    consumer is TOLD to run. The rest of the export's bare imports are real risk
    and are reported as an inventory, which is stated at the surface."""
    export_root = _documented_export(tmp_path, source="print(1)\n")
    (export_root / "scripts").mkdir()
    (export_root / "scripts" / "internal.py").write_text("import yaml\n", encoding="utf-8")

    assert _lib.unguarded_entrypoint_import_findings(export_root) == []
    assert [f["module"] for f in _lib.undeclared_dependency_findings(export_root)] == ["yaml"]


def test_an_undeclared_top_level_import_is_reported(tmp_path: Path) -> None:
    export_root = _minimal_export(tmp_path, source="import yaml\n")

    findings = _lib.undeclared_dependency_findings(export_root)

    assert [finding["module"] for finding in findings] == ["yaml"]
    assert findings[0]["distribution"] == "pyyaml", "the DISTRIBUTION name, not the import name"


def test_a_declared_import_is_not_reported(tmp_path: Path) -> None:
    export_root = _minimal_export(tmp_path, source="import yaml\n", requirements="PyYAML>=6,<7\n")

    assert _lib.undeclared_dependency_findings(export_root) == []


def test_a_guarded_import_is_not_reported(tmp_path: Path) -> None:
    """Guarding IS the correct pattern for an optional dependency, and this repo
    already uses it for cosmic_ray and tomli. Reporting it would say the correct
    pattern is the defect."""
    export_root = _minimal_export(
        tmp_path, source="try:\n    import cosmic_ray\nexcept ImportError:\n    cosmic_ray = None\n"
    )

    assert _lib.undeclared_dependency_findings(export_root) == []


def test_an_unshipped_first_segment_is_reported(tmp_path: Path) -> None:
    export_root = _minimal_export(
        tmp_path, source='from pathlib import Path\np = Path(".") / "evals" / "fixtures"\n'
    )

    findings = _lib.unshipped_path_findings(export_root, repo_root_entries={"evals", "scripts"})

    assert [finding["segment"] for finding in findings] == ["evals"]


def test_a_shipped_directory_does_not_excuse_an_unshipped_path_inside_it(
    tmp_path: Path,
) -> None:
    """The partial-shipping case, and the reason the check is not a first-segment
    rule: shipping two files out of `packaging/` makes the directory present
    while every other path under it is still absent."""
    export_root = _minimal_export(
        tmp_path,
        source='from pathlib import Path\np = Path(".") / "packaging" / "charness.json"\n',
        requirements="PyYAML>=6\n",
    )

    findings = _lib.unshipped_path_findings(export_root, repo_root_entries={"packaging", "scripts"})

    assert [finding["literal"] for finding in findings] == ["packaging/charness.json"]


def test_a_subpath_written_as_one_literal_does_not_escape(tmp_path: Path) -> None:
    """The same absent target, spelled with one `/` operator instead of two.

    The depth guard used to count CHAIN LINKS, so `Path(".") / "packaging/charness.json"`
    was one link and skipped while `Path(".") / "packaging" / "charness.json"` was two
    and reported -- the verdict turned on spelling rather than on what the path names,
    and the one-link spelling is how the defect that opened this class was written.
    """
    export_root = _minimal_export(
        tmp_path,
        source='from pathlib import Path\np = Path(".") / "packaging/charness.json"\n',
        requirements="PyYAML>=6\n",
    )

    findings = _lib.unshipped_path_findings(export_root, repo_root_entries={"packaging", "scripts"})

    assert [finding["literal"] for finding in findings] == ["packaging/charness.json"]


def test_a_bare_shipped_directory_reference_is_still_not_reported(tmp_path: Path) -> None:
    """Naming a shipped directory claims nothing about a file inside it.

    Honest about what this asserts and what it cannot: `_minimal_export` creates a real
    `packaging/` directory, so `[]` holds whether the depth guard fires, the `.exists()`
    guard fires, or the depth guard is DELETED. This input pins the verdict; it does not
    witness which rule produced it. The test below is the one that separates them.
    """
    export_root = _minimal_export(
        tmp_path,
        source='from pathlib import Path\np = Path(".") / "packaging"\n',
        requirements="PyYAML>=6\n",
    )

    assert (
        _lib.unshipped_path_findings(export_root, repo_root_entries={"packaging", "scripts"}) == []
    )


def test_a_dangling_shipped_entry_is_suppressed_by_the_depth_rule_alone(tmp_path: Path) -> None:
    """The one input that tells the two guards apart, and the reason neither is dead.

    `shipped_roots` lists NAMES through `iterdir`; the sibling guard calls `.exists()`,
    which FOLLOWS symlinks. A dangling entry is therefore shipped and absent at once, so
    only the depth rule suppresses it -- delete that rule and this bare directory
    reference is reported as an unshipped path, which is the mutation the resolved-tree
    test above cannot kill. Reachable in practice from a sparse or partial checkout that
    materializes a link without its target.
    """
    export_root = _minimal_export(
        tmp_path, source='from pathlib import Path\np = Path(".") / "packaging"\n'
    )
    (export_root / "packaging").symlink_to("nowhere-at-all")
    assert "packaging" in _lib.shipped_roots(export_root)
    assert not (export_root / "packaging").exists(), "the fixture must be shipped AND absent"

    assert (
        _lib.unshipped_path_findings(export_root, repo_root_entries={"packaging", "scripts"}) == []
    )


def test_a_shipped_path_that_exists_is_not_reported(tmp_path: Path) -> None:
    export_root = _minimal_export(
        tmp_path,
        source='from pathlib import Path\np = Path(".") / "packaging" / "bootstrap-requirements.txt"\n',
        requirements="PyYAML>=6\n",
    )

    assert (
        _lib.unshipped_path_findings(export_root, repo_root_entries={"packaging", "scripts"}) == []
    )


def test_a_path_outside_the_repo_root_layout_is_not_reported(tmp_path: Path) -> None:
    """A chain starting with an arbitrary string is a relative path inside some
    tree the caller named, not a claim about this repo's layout."""
    export_root = _minimal_export(
        tmp_path, source='from pathlib import Path\np = Path(".") / "whatever" / "x"\n'
    )

    assert _lib.unshipped_path_findings(export_root, repo_root_entries={"scripts"}) == []


# --- the verdict ------------------------------------------------------------------


def test_an_unguarded_entrypoint_import_makes_the_gate_fail(monkeypatch) -> None:
    """The composition step, which is what turns a finding into a REFUSAL. Every
    other test here reads an arm directly or asserts the real tree is green, so
    without this one `status` could be hardcoded to `pass` and nothing moves."""
    monkeypatch.setattr(
        _gate._lib,
        "unguarded_entrypoint_import_findings",
        lambda *_a, **_k: [{"kind": "unguarded-entrypoint-import", "module": "yaml"}],
    )
    monkeypatch.setattr(_gate._lib, "unshipped_path_findings", lambda *_a, **_k: [])

    payload = _gate.run_check(ROOT)

    assert payload["status"] == "fail"
    assert any("ModuleNotFoundError" in remedy for remedy in payload["remedy"])


def test_path_findings_alone_do_NOT_fail_the_gate(monkeypatch) -> None:
    """The deliberate severity split, pinned so it cannot be widened by accident
    -- and so a later slice that EARNS the teeth has to retract this by name.

    The path arm's classification was falsified in both directions by round-1
    review: it excused a real gap the moment the slice shipped a directory, and
    it reported maintainer tools scanning an operator-named tree, which are
    correct. It ships as an inventory until it can tell those apart."""
    monkeypatch.setattr(_gate._lib, "unguarded_entrypoint_import_findings", lambda *_a, **_k: [])
    monkeypatch.setattr(
        _gate._lib,
        "unshipped_path_findings",
        lambda *_a, **_k: [{"kind": "unshipped-path", "path": "x.py", "segment": "evals"}],
    )

    payload = _gate.run_check(ROOT)

    assert payload["status"] == "pass"
    assert payload["advisory_unshipped_path_sites"], "advisory means reported, not dropped"
    assert "cannot yet tell" in payload["advisory_path_note"]


def test_a_repo_without_a_packaging_manifest_is_unestablished_not_a_traceback(
    tmp_path: Path,
) -> None:
    """This gate is EXPORTED, and the export deliberately does not ship
    `packaging/charness.json`. A consumer running it used to get an uncaught
    PackagingError instead of a verdict."""
    payload = _gate.run_check(tmp_path)

    assert payload["status"] == "unestablished"
    assert "packaging manifest" in payload["reason"]


def test_unestablished_exits_3_and_the_runner_knows_that_label(monkeypatch) -> None:
    """3, not 1. Every neighbour of this gate degrades to no gate in a consumer
    repo; exiting 1 there would repair a stranded-consumer defect by handing
    every consumer a red lane. The exit byte only means UNPROVEN if the runner
    lists the label, so both halves are asserted together."""
    monkeypatch.setattr(sys, "argv", ["gate", "--repo-root", "/nonexistent-repo-root"])

    assert _gate.main() == _gate.UNESTABLISHED_EXIT == 3

    rows = quality_label_universe.quality_gate_rows(ROOT) or []
    labels = {row["label"] for row in rows if row.get("unestablished_capable") is True}
    assert "check-export-self-sufficiency" in labels


def test_a_present_but_invalid_manifest_is_not_reported_as_absent(
    tmp_path: Path, monkeypatch
) -> None:
    """The blanket `except Exception` this replaces reported a real, unrelated
    packaging defect as "no manifest here" -- a false cause, and a laundering
    path the moment unestablished stopped exiting 1."""
    (tmp_path / "packaging").mkdir()
    (tmp_path / "packaging" / "charness.json").write_text("{}", encoding="utf-8")

    def explode(*_args, **_kwargs):
        raise RuntimeError("manifest fails validation for an unrelated reason")

    monkeypatch.setattr(_gate._packaging, "load_manifest", explode)

    with pytest.raises(RuntimeError):
        _gate.run_check(tmp_path)


def test_a_missing_export_tree_is_unestablished_not_clean(tmp_path: Path, monkeypatch) -> None:
    """Zero files scanned reads identically to a full pass while proving nothing
    about the artifact. Distinct from the missing-manifest case above: a manifest
    that EXISTS with no export tree is a maintainer defect, not a consumer's
    ordinary layout."""
    (tmp_path / "packaging").mkdir()
    (tmp_path / "packaging" / "charness.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(_gate._packaging, "load_manifest", lambda *_a, **_k: {})
    monkeypatch.setattr(
        _gate._packaging, "materialized_plugin_root", lambda _manifest: Path("nowhere")
    )

    payload = _gate.run_check(tmp_path)

    assert payload["status"] == "unestablished"
    assert "nothing was validated" in payload["reason"]


def test_the_documented_gather_entrypoint_names_what_to_install() -> None:
    """The consumer-reachable half: even with the contract shipped, a consumer who
    has not run the bootstrap still meets the import first. The documented
    entrypoint must name the pinned declaration rather than raising bare."""
    source = (ROOT / "skills/public/gather/scripts/gather_public_url.py").read_text(
        encoding="utf-8"
    )

    assert "except ModuleNotFoundError" in source
    assert "bootstrap-requirements.txt" in source
    assert "bootstrap_runtime.py" in source


@pytest.mark.boundary_contract(
    reason="env-scrubbed export self-sufficiency: the clean interpreter must execute the gather import guard"
)
def test_the_gather_guard_actually_runs_and_names_what_to_install(tmp_path: Path) -> None:
    """EXECUTED, not grepped.

    The first version of this assertion read the file as text and matched three
    substrings, while the handler carried `# pragma: no cover - exercised by its
    own test`. Three reviewers found that comment false independently, and the
    grep also could not see that the command it printed named a `--execute` flag
    `bootstrap_runtime.py` does not have -- so the fix for a stranded consumer
    would have stranded them a second time."""
    blocker = tmp_path / "sitecustomize.py"
    blocker.write_text(
        "import sys\n"
        "class _NoYaml:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'yaml' or name.startswith('yaml.'):\n"
        "            raise ModuleNotFoundError('No module named yaml', name='yaml')\n"
        "        return None\n"
        "sys.meta_path.insert(0, _NoYaml())\n",
        encoding="utf-8",
    )
    env = {**os.environ, "PYTHONPATH": str(tmp_path)}

    result = subprocess.run(
        [sys.executable, str(ROOT / "skills/public/gather/scripts/gather_public_url.py"), "--help"],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
    )

    assert result.returncode != 0
    message = result.stdout + result.stderr
    assert "PyYAML is missing" in message
    assert "--execute" not in message, (
        "the printed bootstrap command must not name a flag bootstrap_runtime.py lacks"
    )
    # Every path the message prints must EXIST. Substring matching on the filename
    # alone passed while the message named `<repo>/skills/packaging/...`, a
    # directory that does not exist -- the same stranding the guard exists to end.
    for token in message.split():
        candidate = token.strip("`,.")
        if candidate.startswith("/") and ("packaging/" in candidate or candidate.endswith(".py")):
            assert Path(candidate).exists(), (
                f"the guard printed a path that does not exist: {candidate}"
            )
    assert str(ROOT / "packaging" / "bootstrap-requirements.txt") in message


@pytest.mark.boundary_contract(
    reason="env-scrubbed export self-sufficiency: the clean interpreter must execute the inventory import guard"
)
def test_the_dominance_inventory_guard_actually_runs_and_names_what_to_install(
    tmp_path: Path,
) -> None:
    """EXECUTED with PyYAML blocked, and every path it prints must exist.

    Added after a bounded reviewer found the guard carrying
    `# pragma: no cover - exercised by test_export_self_sufficiency` while THIS
    file never referenced it — the same false-pragma defect three reviewers
    caught in the gather guard one slice earlier, shipped again in the slice that
    cited the repair.
    """
    blocker = tmp_path / "sitecustomize.py"
    blocker.write_text(
        "import sys\n"
        "class _NoYaml:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'yaml' or name.startswith('yaml.'):\n"
        "            raise ModuleNotFoundError('No module named yaml', name='yaml')\n"
        "        return None\n"
        "sys.meta_path.insert(0, _NoYaml())\n",
        encoding="utf-8",
    )
    env = {**os.environ, "PYTHONPATH": str(tmp_path)}
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills/public/quality/scripts/inventory_command_dominance.py"),
            "--help",
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
    )

    assert result.returncode != 0
    message = result.stdout + result.stderr
    assert "PyYAML is missing" in message
    for token in message.split():
        candidate = token.strip("`,.")
        if candidate.startswith("/") and ("packaging/" in candidate or candidate.endswith(".py")):
            assert Path(candidate).exists(), (
                f"the guard printed a path that does not exist: {candidate}"
            )
    assert str(ROOT / "packaging" / "bootstrap-requirements.txt") in message


def test_the_dominance_inventory_guard_invents_no_path_when_the_contract_is_missing() -> None:
    """No counted-hop fallback.

    The first version fell back to `parents[3]`, which is `<repo>/skills` in the
    dev tree, so a vendored install without `packaging/` was told to install from
    a requirements file that does not exist — stranding the consumer the guard
    exists to un-strand. The guard now says the install is incomplete instead.
    """
    source = (ROOT / "skills/public/quality/scripts/inventory_command_dominance.py").read_text(
        encoding="utf-8"
    )
    assert "_HERE.parents[3]" not in source
    assert "this install is" in source


def test_the_printed_bootstrap_command_only_uses_flags_that_exist() -> None:
    """Pins the pairing directly, so the two files cannot drift apart silently."""
    guard = (ROOT / "skills/public/gather/scripts/gather_public_url.py").read_text(encoding="utf-8")
    bootstrap = (ROOT / "scripts/bootstrap_runtime.py").read_text(encoding="utf-8")

    # The WHOLE guard block, not a character budget: an earlier version sliced 800
    # characters after the `except`, the only flag sat past the cut, and the loop
    # body never ran -- a pin asserting nothing, which is the class this file
    # exists to stop.
    block = guard.split("except ModuleNotFoundError", 1)[1].split("\ndef ", 1)[0]
    flags = set(re.findall(r"--[a-z][a-z-]+", block))

    assert flags, "the pairing test matched no flags; its slice is wrong, not the code"
    for flag in flags:
        assert f'"{flag}"' in bootstrap, f"{flag} is not a bootstrap_runtime.py flag"


# --- repo-root instruction arm (#634 doc half) --------------------------------


def _instruction_export(tmp_path: Path, *, doc_relative: str, body: str) -> Path:
    """An export shipping `scripts/render_thing.py` and one doc that mentions it."""
    export_root = tmp_path / "plugins" / "charness"
    (export_root / "scripts").mkdir(parents=True)
    (export_root / "scripts" / "render_thing.py").write_text("x = 1\n", encoding="utf-8")
    doc = export_root / doc_relative
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(body, encoding="utf-8")
    return export_root


def test_the_arm_measures_the_INSTRUCTION_and_not_merely_the_script_name(tmp_path: Path) -> None:
    """The wrong-noun test, written first.

    The defect is a doc telling a consumer to run a REPO-ROOT path. A detector that
    merely noticed `render_thing.py` being named would fire on the already-correct
    `<plugin-dir>/` spelling too, reporting the fix as the defect -- the exact failure
    the dominance reader documents for its own replacement string. Same script, same
    doc, two spellings: only one is a finding.
    """
    broken = _instruction_export(
        tmp_path / "broken",
        doc_relative="skills/demo/references/how.md",
        body="Run `python3 scripts/render_thing.py --repo-root .`\n",
    )
    fixed = _instruction_export(
        tmp_path / "fixed",
        doc_relative="skills/demo/references/how.md",
        body="Run `python3 <plugin-dir>/scripts/render_thing.py --repo-root .`\n",
    )

    assert [f["script"] for f in _lib.repo_root_instruction_findings(broken)] == ["render_thing.py"]
    assert _lib.repo_root_instruction_findings(fixed) == []


def test_an_instruction_naming_an_unshipped_script_is_not_this_arms_business(
    tmp_path: Path,
) -> None:
    """A consumer-owned command that happens to live under `scripts/` is not a delivery
    bug: there is nothing in the export it should have pointed at instead."""
    export_root = _instruction_export(
        tmp_path,
        doc_relative="skills/demo/references/how.md",
        body="Set it to `python3 scripts/your_own_runner.py`\n",
    )

    assert _lib.repo_root_instruction_findings(export_root) == []


def test_a_skill_doc_is_consumer_doc_and_a_module_docstring_is_module_prose(tmp_path: Path) -> None:
    """The split that decides what blocks. A `references/*.md` line is followed by a
    consumer; a docstring inside an exported module usually describes a maintainer
    tool's own in-repo invocation, where the rewrite would make it wrong.
    """
    doc = _instruction_export(
        tmp_path / "doc",
        doc_relative="skills/demo/references/how.md",
        body="Run `python3 scripts/render_thing.py`\n",
    )
    module = _instruction_export(
        tmp_path / "module",
        doc_relative="scripts/other_tool.py",
        body='"""Run `python3 scripts/render_thing.py` from the repo root."""\n',
    )

    assert [f["site_class"] for f in _lib.repo_root_instruction_findings(doc)] == ["consumer-doc"]
    assert [f["site_class"] for f in _lib.repo_root_instruction_findings(module)] == [
        "module-prose"
    ]


def test_a_script_under_a_skills_scripts_dir_is_module_prose_not_consumer_doc(
    tmp_path: Path,
) -> None:
    """A `.md` under a `scripts/` directory is module documentation, not consumer prose.
    This is the case the `/scripts/` clause exists for; a `.py` there is already caught
    by the suffix test, so without a non-.py fixture the clause would be uncovered."""
    export_root = _instruction_export(
        tmp_path,
        doc_relative="skills/demo/scripts/NOTES.md",
        body="Run `python3 scripts/render_thing.py`\n",
    )

    assert [f["site_class"] for f in _lib.repo_root_instruction_findings(export_root)] == [
        "module-prose"
    ]


def test_a_consumer_doc_instruction_makes_the_gate_FAIL(tmp_path: Path) -> None:
    export_root = _instruction_export(
        tmp_path,
        doc_relative="skills/demo/references/how.md",
        body="Run `python3 scripts/render_thing.py`\n",
    )

    findings = _lib.repo_root_instruction_findings(export_root)
    assert [f["site_class"] for f in findings] == ["consumer-doc"]
    assert findings[0]["remedy"] == "python3 <plugin-dir>/scripts/render_thing.py"


def test_the_real_export_has_no_consumer_doc_repo_root_instructions() -> None:
    """The bar this slice set at the count it already holds. Seven consumer-doc sites
    were rewritten to `<plugin-dir>/` and kept; this refuses the eighth."""
    findings = _lib.repo_root_instruction_findings(ROOT / "plugins" / "charness")

    assert [f for f in findings if f["site_class"] == "consumer-doc"] == []


def test_a_consumer_doc_instruction_FAILS_THE_GATE(monkeypatch, tmp_path: Path) -> None:
    """The teeth, asserted through `run_check`. The classification tests above all pass
    with `or consumer_doc_instructions` deleted from the status line -- they read the
    lib, never the verdict. This is the mutant that kills.
    """
    monkeypatch.setattr(
        _gate._lib,
        "repo_root_instruction_findings",
        lambda export_root: [
            {
                "doc": "skills/demo/references/how.md",
                "line": 1,
                "script": "thing.py",
                "site_class": "consumer-doc",
                "remedy": "python3 <plugin-dir>/scripts/thing.py",
            }
        ],
    )
    payload = _gate.run_check(ROOT)

    assert payload["status"] == "fail"
    assert payload["consumer_doc_repo_root_instructions"]
    assert _gate.CONSUMER_DOC_INSTRUCTION_REMEDY in payload["remedy"]


def test_module_prose_instructions_alone_do_NOT_fail_the_gate(monkeypatch) -> None:
    """The other side of the split: the 70-entry inventory must not block, or the
    advisory bargain silently becomes a release gate."""
    monkeypatch.setattr(
        _gate._lib,
        "repo_root_instruction_findings",
        lambda export_root: [
            {
                "doc": "scripts/tool.py",
                "line": 1,
                "script": "thing.py",
                "site_class": "module-prose",
                "remedy": "python3 <plugin-dir>/scripts/thing.py",
            }
        ],
    )
    payload = _gate.run_check(ROOT)

    assert payload["status"] == "pass"
    assert payload["advisory_module_prose_repo_root_instructions"]
    assert _gate.MODULE_PROSE_INSTRUCTION_NOTE == payload["advisory_module_prose_note"]


def test_the_instruction_arm_is_still_looking_at_something() -> None:
    """Guards the zero. `test_the_real_export_has_no_consumer_doc_repo_root_instructions`
    passes if the regex stops matching, if the classifier stops emitting `consumer-doc`,
    or if the shipped-script set comes back empty -- three ways for a switched-off
    detector to read as a clean tree. A nonzero module-prose count rules out all three.
    """
    findings = _lib.repo_root_instruction_findings(ROOT / "plugins" / "charness")

    assert [f for f in findings if f["site_class"] == "module-prose"]


def test_a_generated_file_header_is_not_read_as_an_instruction(tmp_path: Path) -> None:
    """Every generated file in the export names its own generator. That is provenance
    for a maintainer regenerating it here, and the first build of this arm reported two
    such lines in the plugin README as consumer defects."""
    export_root = _instruction_export(
        tmp_path,
        doc_relative="skills/demo/references/gen.md",
        body=(
            "<!--\ngenerated_file: true\n"
            "generator: python3 scripts/render_thing.py --repo-root .\n"
            "sync_command: python3 scripts/render_thing.py --repo-root .\n-->\n"
        ),
    )

    assert _lib.repo_root_instruction_findings(export_root) == []


def test_an_exempt_path_is_matched_exactly_and_not_by_suffix(tmp_path: Path) -> None:
    """`endswith` would exempt any future nested path ending in an exempt string --
    a vendored or re-rooted copy inherits an exemption nobody granted it."""
    exempt = next(iter(_lib.INSTRUCTION_EXEMPT_PATHS))
    export_root = _instruction_export(
        tmp_path,
        doc_relative=f"vendor/{exempt}",
        body="Run `python3 scripts/render_thing.py`\n",
    )

    assert [f["doc"] for f in _lib.repo_root_instruction_findings(export_root)] == [
        f"vendor/{exempt}"
    ]


def test_every_exemption_is_still_LOAD_BEARING() -> None:
    """An exemption whose site no longer contains a reportable instruction is dead, and
    a dead entry is how the list becomes a place to silence findings.

    Drives the PRODUCTION finder with exemptions off rather than re-implementing its
    skip conditions. The first version re-implemented two of the three and omitted the
    shipped-script check, so an exemption for an unshipped script read as live.
    """
    export_root = ROOT / "plugins" / "charness"
    reported = {
        finding["doc"]
        for finding in _lib.repo_root_instruction_findings(export_root, apply_exemptions=False)
    }

    for relative, reason in _lib.INSTRUCTION_EXEMPT_PATHS.items():
        assert (export_root / relative).exists(), relative
        assert reason.strip(), relative
        assert relative in reported, f"{relative} is exempted but nothing there is reportable"


def test_the_real_finder_still_emits_consumer_doc_on_the_real_tree() -> None:
    """The gate-teeth tests monkeypatch the finder, so they would pass even if the real
    one returned [] for every input. Nothing else asserted the real finder can still
    produce the class that blocks. With exemptions off, the exempt consumer-facing .md
    sites are exactly that shape.
    """
    findings = _lib.repo_root_instruction_findings(
        ROOT / "plugins" / "charness", apply_exemptions=False
    )

    assert [f for f in findings if f["site_class"] == "consumer-doc"]


def test_an_executed_config_value_can_never_reach_the_blocking_arm() -> None:
    """The class that broke five commands, pinned. `command:`/`commands:`/`sync_command:`
    live in .yaml and .json, and their values are RUN. If any of those file shapes can be
    classed consumer-doc, the remedy prescribes `<plugin-dir>/` into an executed field.
    """
    for relative in (
        "skills/critique/adapter.example.yaml",
        "skills/release/adapter.example.yaml",
        "integrations/tools/agent-browser.json",
        "skills/quality/references/catalog.yaml",
    ):
        assert _lib._instruction_site_class(relative) == "module-prose", relative


def test_a_sync_command_key_outside_a_generated_header_is_still_a_finding(tmp_path: Path) -> None:
    """`sync_command:` is a generated-header field AND a live adapter config key. Keying
    the skip on the field name alone exempted `skills/release/adapter.example.yaml`'s
    real one; the marker scopes it back to files that declare themselves generated."""
    export_root = _instruction_export(
        tmp_path,
        doc_relative="skills/demo/adapter.example.yaml",
        body="sync_command: python3 scripts/render_thing.py --repo-root .\n",
    )

    assert [f["script"] for f in _lib.repo_root_instruction_findings(export_root)] == [
        "render_thing.py"
    ]


def test_an_undecodable_file_is_skipped_rather_than_crashing_the_arm(tmp_path: Path) -> None:
    """A scanned suffix does not guarantee decodable text -- a `.json` fixture holding
    binary, or a `.md` written in another encoding, would otherwise take the whole gate
    down with a UnicodeDecodeError instead of reporting the rest of the export."""
    export_root = _instruction_export(
        tmp_path,
        doc_relative="skills/demo/references/how.md",
        body="Run `python3 scripts/render_thing.py`\n",
    )
    (export_root / "skills" / "demo" / "references" / "blob.json").write_bytes(
        b"\xff\xfe\x00binary"
    )

    findings = _lib.repo_root_instruction_findings(export_root)

    assert [f["doc"] for f in findings] == ["skills/demo/references/how.md"]


def test_an_exported_tools_reference_is_a_shipping_gap(tmp_path: Path) -> None:
    export_root = _instruction_export(
        tmp_path,
        doc_relative="skills/demo/references/how.md",
        body=(
            "Run `python3 tools/check_coverage.py --repo-root .` or "
            "`python3 -m tools.check_coverage`.\n"
        ),
    )

    findings = _lib.exported_tools_reference_findings(export_root)

    assert findings == [
        {
            "path": "skills/demo/references/how.md",
            "line": 1,
            "references": ["-m tools.", "check_coverage.py"],
        }
    ]


def test_exported_tools_references_are_reported_without_blocking_the_composed_gate(monkeypatch) -> None:
    monkeypatch.setattr(_gate._lib, "unguarded_entrypoint_import_findings", lambda *_a, **_k: [])
    monkeypatch.setattr(_gate._lib, "repo_root_instruction_findings", lambda *_a, **_k: [])
    monkeypatch.setattr(_gate._lib, "exported_tools_reference_findings", lambda *_a, **_k: [
        {"path": "scripts/run-quality.sh", "line": 1, "references": ["-m tools."]}
    ])

    payload = _gate.run_check(ROOT)

    assert payload["status"] == "pass"
    assert payload["advisory_exported_tools_references"] == [
        {"path": "scripts/run-quality.sh", "line": 1, "references": ["-m tools."]}
    ]
