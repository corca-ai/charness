"""Changed lines S6b-2 wrote that no test executed, closed here.

Obtained from `check_changed_line_mutation_coverage.py` over `0037dbcfd..HEAD`
BEFORE the slice's commit was final rather than after it, which is the ordering
the previous session paid two extra commits to learn. It returned blocking over
seven changed pool files.

The most useful finding is not any single line. It is that the exported
inventory's ENTIRE scan loop was unproven: every SC19 acceptance test drove it
with a tmp repo that had no registry, so the `registry is not None` branch --
the only branch that ever produces a finding for a consumer -- never ran once
while the suite and two gates were green. A criterion asserting a consumer "can
answer" the cost question was resting on a code path nothing had executed.

The rest are refusal branches, CLI entrypoints, and parser edges. They are
cheap, and each is the shape that reads as working until the day it runs.
"""

from __future__ import annotations

import importlib
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from .support import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
from runtime_bootstrap import load_path_module, skill_script  # noqa: E402

LIB_PATH = ROOT / "skills" / "public" / "quality" / "scripts" / "command_dominance_lib.py"
INVENTORY_PATH = ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_command_dominance.py"

DOMINANCE = load_path_module("command_dominance_lib_gaps", LIB_PATH)
INVENTORY = load_path_module("inventory_command_dominance_gaps", INVENTORY_PATH)
GATE = importlib.import_module("scripts.check_command_dominance")
UNIVERSE = importlib.import_module("scripts.check_runtime_budget_universe")
SAMPLER = importlib.import_module("scripts.sample_mutation_files")

REPLACEMENT = "python3 scripts/run_standing_pytest.py"

REGISTRY_YAML = (
    "version: 1\n"
    "dominated_commands:\n"
    "  - id: bare-pytest-whole-suite\n"
    "    program: pytest\n"
    "    broad_targets:\n"
    "      - tests\n"
    f"    replacement: {REPLACEMENT}\n"
    "    reason: the standing runner covers the same scope\n"
    "config_literals:\n"
    "  - path: cosmic-ray.toml\n"
    "    key: test-command\n"
)


def _repo_with_registry(tmp_path: Path, *, literal: str = "python3 -m pytest -q tests") -> Path:
    (tmp_path / ".agents").mkdir(exist_ok=True)
    (tmp_path / ".agents" / "command-dominance.yaml").write_text(REGISTRY_YAML, encoding="utf-8")
    (tmp_path / "cosmic-ray.toml").write_text(
        f'[cosmic-ray]\ntest-command = "{literal}"\n', encoding="utf-8"
    )
    return tmp_path


def _rule(**overrides) -> dict:
    base = {
        "id": "bare-pytest-whole-suite",
        "program": "pytest",
        "replacement": REPLACEMENT,
        "reason": "cheaper equivalent exists",
    }
    base.update(overrides)
    return base


def _data(**overrides) -> dict:
    base = {"version": 1, "dominated_commands": [_rule()]}
    base.update(overrides)
    return base


# --------------------------------------------------------------------------
# command_dominance_lib -- every refusal branch, and the parser edges.
# --------------------------------------------------------------------------


def test_a_registry_that_is_not_a_mapping_is_refused() -> None:
    with pytest.raises(DOMINANCE.RegistryError, match="must be a mapping"):
        DOMINANCE.parse_registry(["not", "a", "mapping"])


def test_a_non_list_field_is_refused_by_name() -> None:
    with pytest.raises(DOMINANCE.RegistryError, match="must be a list"):
        DOMINANCE.parse_registry(_data(dominated_commands="not-a-list"))


def test_a_non_mapping_entry_is_refused() -> None:
    with pytest.raises(DOMINANCE.RegistryError, match="entry must be a mapping"):
        DOMINANCE.parse_registry(_data(dominated_commands=["just-a-string"]))


def test_a_duplicate_rule_id_is_refused() -> None:
    """Two rules with one id makes `exemption_for` silently pick a winner."""
    with pytest.raises(DOMINANCE.RegistryError, match="duplicate rule id"):
        DOMINANCE.parse_registry(_data(dominated_commands=[_rule(), _rule()]))


def test_an_inline_sequence_read_as_a_string_is_refused_not_coerced() -> None:
    """The failure that reached a green gate during this slice.

    One of the two readers of the registry turns `[tests]` into the STRING
    "[tests]". Iterating a string yields characters, so the targets silently
    became single letters and nothing ever matched.
    """
    with pytest.raises(DOMINANCE.RegistryError, match="must be a list"):
        DOMINANCE.parse_registry(_data(dominated_commands=[_rule(broad_targets="[tests]")]))


@pytest.mark.parametrize("skip", ["1", -1, True, 1.5])
def test_a_non_integer_skip_args_is_refused(skip) -> None:
    with pytest.raises(DOMINANCE.RegistryError, match="skip_args"):
        DOMINANCE.parse_registry(
            _data(wrapper_programs=[{"program": "queue_selected", "skip_args": skip}])
        )


@pytest.mark.parametrize(
    "command",
    [
        "",
        "   ",
        'echo "unterminated',  # shlex raises rather than guessing
        "python3",  # an interpreter with nothing after it names no program
        "FOO=1 BAR=2 ",  # env assignments only
    ],
)
def test_an_unparseable_or_program_less_command_resolves_to_nothing(command: str) -> None:
    """Never folded into "clean" by a caller; it simply produces no invocation."""
    assert DOMINANCE.resolve_invocations(command) == []


def test_a_runner_pair_prefix_is_skipped() -> None:
    """`uv run pytest tests` runs pytest, not `uv`."""
    registry = DOMINANCE.parse_registry(_data(dominated_commands=[_rule(broad_targets=["tests"])]))
    assert DOMINANCE.match_command("uv run pytest tests", registry) is not None


def test_bash_without_dash_c_resolves_to_bash_itself() -> None:
    """`bash scripts/thing.sh` runs a FILE this reader cannot follow into."""
    resolved = DOMINANCE.resolve_invocations("bash scripts/thing.sh --flag")
    assert resolved == [("bash", ["scripts/thing.sh", "--flag"])]


def test_a_bare_program_with_no_targets_is_dominated() -> None:
    """`pytest` alone runs everything, which is the broadest target there is."""
    registry = DOMINANCE.parse_registry(_data(dominated_commands=[_rule(broad_targets=["tests"])]))
    assert DOMINANCE.match_command("pytest", registry) is not None


def test_a_value_flags_argument_is_skipped_rather_than_counted() -> None:
    assert DOMINANCE.positional_targets(["-k", "tests", "docs"], ("-k",)) == ["docs"]
    # `--` is dropped, and an `=`-joined flag consumes no following token.
    assert DOMINANCE.positional_targets(["--tb=short", "--", "docs"], ("--tb",)) == ["docs"]


def test_a_fenced_block_contributes_its_commands_and_the_fence_lines_do_not() -> None:
    text = "intro\n\n```bash\npytest tests\n\n```\n\ntrailing `pytest tests` inline\n"
    found = DOMINANCE.iter_document_commands(text)
    assert ("pytest tests") in [command for _, command in found]
    assert not any(command.startswith("```") for _, command in found)
    # Fenced content and the inline span are both reached, on their own lines.
    assert len(found) == 2


def test_an_unquoted_config_value_drops_a_trailing_comment_but_keeps_an_inner_hash() -> None:
    assert DOMINANCE.read_config_literal("key: value # trailing", "key") == [(1, "value")]
    assert DOMINANCE.read_config_literal("key: pytest -k a#b", "key") == [(1, "pytest -k a#b")]


# --------------------------------------------------------------------------
# check_command_dominance -- the branches and the entrypoint.
# --------------------------------------------------------------------------


def test_a_declared_config_literal_whose_file_is_absent_yields_nothing(tmp_path: Path) -> None:
    assert GATE.read_config_literal(tmp_path / "missing.toml", "key", DOMINANCE) == []


def test_a_registry_the_reader_could_not_fully_read_is_refused(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text(
        REGISTRY_YAML + "\t- this line is not interpretable\n", encoding="utf-8"
    )
    with pytest.raises(GATE._load_dominance_lib().RegistryError):
        GATE.evaluate(tmp_path)


def test_the_standing_gate_arm_reports_a_dominated_command_inside_a_runner(tmp_path: Path) -> None:
    """The arm's producing branch, driven end to end rather than by unit call.

    Every earlier test reached the config-literal seam. This one puts a dominated
    command in a discovered shell runner, which is the seam the exported
    discovery library exists for.
    """
    repo = _repo_with_registry(tmp_path, literal=REPLACEMENT)
    (repo / "scripts").mkdir(exist_ok=True)
    runner = repo / "scripts" / "run-quality.sh"
    runner.write_text(
        '#!/usr/bin/env bash\nqueue_selected "suite" python3 -m pytest -q tests\n', encoding="utf-8"
    )
    hooks = repo / ".githooks"
    hooks.mkdir()
    (hooks / "pre-push").write_text("#!/usr/bin/env bash\n./scripts/run-quality.sh\n", encoding="utf-8")
    (repo / ".agents" / "command-dominance.yaml").write_text(
        REGISTRY_YAML
        + "wrapper_programs:\n  - program: queue_selected\n    skip_args: 1\n",
        encoding="utf-8",
    )
    report = GATE.evaluate(repo)
    seams = {
        (finding.get("context") or {}).get("seam")
        for finding in report["findings"]
    }
    assert "standing-gate" in seams, report["findings"]
    assert report["blocking"]


def test_an_empty_snippet_is_skipped_rather_than_classified(tmp_path: Path) -> None:
    repo = _repo_with_registry(tmp_path, literal=REPLACEMENT)
    registry = GATE._load_dominance_lib().parse_registry(
        {"version": 1, "dominated_commands": [_rule()]}
    )

    class _Discovery:
        @staticmethod
        def discover_surfaces(_root):
            return []

        @staticmethod
        def iter_snippets(_surfaces):
            return [{"path": "x.sh", "origin": "o", "snippet": "   "}]

    assert GATE.scan_standing_gates(repo, registry, GATE._load_dominance_lib(), _Discovery()) == []


def test_the_not_armed_payload_carries_a_warn_marker() -> None:
    payload = GATE.report_payload(
        {"armed": False, "reason": "no registry here", "findings": [], "blocking": []}, DOMINANCE
    )
    assert payload["advisory"].startswith("WARN")
    assert "did_not_judge" not in payload, (
        "an unarmed run judged nothing; listing exclusions would dress it up as a scoped verdict"
    )


def test_the_blocking_payload_names_the_remedy_and_the_exemption_route() -> None:
    payload = GATE.report_payload(
        {
            "armed": True,
            "blocking": ["site: `pytest tests` is dominated"],
            "exempt_count": 0,
            "findings": [],
        },
        DOMINANCE,
    )
    assert "dominated by a cheaper" in payload["summary"]
    assert "exemptions" in payload["remedy"]


def test_the_entrypoint_exits_nonzero_on_a_blocking_tree(tmp_path, monkeypatch, capsys) -> None:
    repo = _repo_with_registry(tmp_path)
    monkeypatch.setattr(sys, "argv", ["check_command_dominance.py", "--repo-root", str(repo)])
    assert GATE.main() == 1
    assert "blocking" in capsys.readouterr().out


def test_the_entrypoint_exits_zero_on_a_clean_tree(tmp_path, monkeypatch, capsys) -> None:
    repo = _repo_with_registry(tmp_path, literal=REPLACEMENT)
    monkeypatch.setattr(sys, "argv", ["check_command_dominance.py", "--repo-root", str(repo)])
    assert GATE.main() == 0
    capsys.readouterr()


def test_the_entrypoint_renders_a_named_error_rather_than_a_traceback(
    tmp_path, monkeypatch, capsys
) -> None:
    """A gate that dies with a traceback has rendered no verdict at all."""
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text("version: 99\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["check_command_dominance.py", "--repo-root", str(tmp_path)])
    assert GATE.main() == 1
    out = capsys.readouterr().out
    assert "cannot be read as a dominance registry" in out


def test_the_module_runs_as_a_script(tmp_path, monkeypatch) -> None:
    """`if __name__ == "__main__": sys.exit(main())` is the line every operator hits."""
    repo = _repo_with_registry(tmp_path, literal=REPLACEMENT)
    monkeypatch.setattr(sys, "argv", ["check_command_dominance.py", "--repo-root", str(repo)])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(ROOT / "scripts" / "check_command_dominance.py"), run_name="__main__")
    assert excinfo.value.code == 0


# --------------------------------------------------------------------------
# inventory_command_dominance -- the branch a consumer actually runs.
# --------------------------------------------------------------------------


def test_the_inventory_scan_loop_runs_when_a_registry_is_present(tmp_path: Path) -> None:
    """The gap this proof was worth running for.

    Every SC19 test drove the inventory with an absent or malformed registry, so
    the branch that produces a finding for a consumer had never executed.
    """
    repo = _repo_with_registry(tmp_path)
    payload = INVENTORY.inventory(repo, repo / ".agents" / "command-dominance.yaml")
    assert payload["registry_state"]["state"] == "loaded"
    assert payload["registry_state"]["detail"]
    sites = [finding["site"] for finding in payload["dominated_findings"]]
    assert "cosmic-ray.toml:test-command" in sites


def test_the_inventory_reports_an_exempt_site_separately(tmp_path: Path) -> None:
    repo = _repo_with_registry(tmp_path)
    (repo / ".agents" / "command-dominance.yaml").write_text(
        REGISTRY_YAML
        + "exemptions:\n"
        "  - id: deliberate\n"
        "    site: cosmic-ray.toml:test-command\n"
        "    rule: bare-pytest-whole-suite\n"
        "    reason: cosmic-ray substitutes it per mutant\n",
        encoding="utf-8",
    )
    payload = INVENTORY.inventory(repo, repo / ".agents" / "command-dominance.yaml")
    assert payload["dominated_findings"] == []
    assert [f["site"] for f in payload["exempt_findings"]] == ["cosmic-ray.toml:test-command"]


def test_a_declared_config_literal_missing_from_the_consumers_tree_is_skipped(tmp_path: Path) -> None:
    repo = _repo_with_registry(tmp_path)
    (repo / "cosmic-ray.toml").unlink()
    payload = INVENTORY.inventory(repo, repo / ".agents" / "command-dominance.yaml")
    assert payload["dominated_findings"] == []


def test_a_relative_registry_path_resolves_against_the_repo_root(tmp_path, monkeypatch, capsys) -> None:
    repo = _repo_with_registry(tmp_path, literal=REPLACEMENT)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "inventory_command_dominance.py",
            "--repo-root",
            str(repo),
            "--registry-path",
            ".agents/command-dominance.yaml",
        ],
    )
    assert INVENTORY.main() == 0
    out = capsys.readouterr().out
    assert "state: loaded" in out, (
        "a relative --registry-path must resolve against --repo-root and load THAT "
        "repo's registry, not silently miss and report absent"
    )
    assert str(repo) in out


def test_the_inventory_entrypoint_emits_yaml_without_a_mode_flag(tmp_path, monkeypatch, capsys) -> None:
    repo = _repo_with_registry(tmp_path, literal=REPLACEMENT)
    monkeypatch.setattr(sys, "argv", ["inventory_command_dominance.py", "--repo-root", str(repo)])
    assert INVENTORY.main() == 0
    out = capsys.readouterr().out
    assert "discovered_surfaces" in out and "interpretation" in out


def test_the_inventory_refuses_to_start_without_its_skill_runtime(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(INVENTORY, "__file__", str(tmp_path / "detached" / "script.py"))
    with pytest.raises(ImportError, match="skill_runtime_bootstrap"):
        INVENTORY._load_skill_runtime_bootstrap()


def test_the_inventory_runs_as_a_script_and_never_fails_a_consumers_lane(tmp_path: Path) -> None:
    """Exit 0 is the contract, proven through a real process rather than a call.

    An EXPORTED advisory that can return nonzero hands a red lane to a consumer
    who installed a plugin.
    """
    result = subprocess.run(
        [sys.executable, str(INVENTORY_PATH), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "registry_state" in result.stdout


# --------------------------------------------------------------------------
# The surfaces this slice reached into.
# --------------------------------------------------------------------------


def test_the_universe_second_direction_is_empty_without_a_registry(tmp_path: Path) -> None:
    assert UNIVERSE.unbudgeted_expensive_commands(tmp_path, set()) == []


def test_the_universe_second_direction_defers_a_broken_registry_to_its_owning_gate(
    tmp_path: Path,
) -> None:
    """A malformed registry is `check-command-dominance`'s verdict to render.

    Reporting it twice, from a gate whose subject is budgets, would put one
    defect behind two labels and make the remedy ambiguous.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text("version: 99\n", encoding="utf-8")
    assert UNIVERSE.unbudgeted_expensive_commands(tmp_path, set()) == []


def test_a_config_literal_is_reported_unbudgeted_whatever_the_budget_set_contains(
    tmp_path: Path,
) -> None:
    """REWRITTEN: the old version fed the fabricated label set `{"test-command"}`.

    That pinned the defect as intended semantics — the first implementation
    derived a "label" from the config KEY, so a repo whose gate label happened to
    match a config key name silently lost that site from the report. A config
    literal carries no queue label at all, so no budget can name it, and that is
    now true regardless of what the budgeted set contains.
    """
    repo = _repo_with_registry(tmp_path)
    for budgeted in (set(), {"test-command"}, {"pytest"}):
        reported = UNIVERSE.unbudgeted_expensive_commands(repo, budgeted)
        assert [entry["site"] for entry in reported] == ["cosmic-ray.toml:test-command"]
        assert reported[0]["queue_label"] is None
        assert "no queue label" in reported[0]["basis"]


def test_skill_script_names_the_skill_and_the_tree_when_it_cannot_resolve(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="quality script nope.py not found"):
        skill_script(tmp_path, "quality", "nope.py")


def test_the_sampler_reports_no_eligible_against_the_command_it_actually_probed(
    tmp_path, monkeypatch, capsys
) -> None:
    """The override changed which command this message must name.

    Driven through `main()` rather than by calling `report_no_eligible` directly,
    because the CHANGED line is the call SITE -- the argument it passes. A direct
    call proves the function formats a string and says nothing about whether main
    hands it the command the probe actually ran. Printing the config literal here
    would send an operator to inspect a command that never ran, which is the
    defect class this whole slice is about.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "cosmic-ray.toml").write_text(
        '[cosmic-ray]\nmodule-path = ["scripts/a.py"]\ntimeout = 30.0\n'
        'test-command = "python3 -m pytest -q tests"\n',
        encoding="utf-8",
    )
    # No eligible pool files: `scripts/` is empty, so `list_eligible` returns
    # nothing and main takes the report-and-exit branch.
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sample_mutation_files.py",
            "--repo-root",
            str(repo),
            "--test-command",
            REPLACEMENT,
        ],
    )
    monkeypatch.delenv("MUTATION_BASE_SHA", raising=False)
    monkeypatch.delenv("MUTATION_HEAD_SHA", raising=False)
    monkeypatch.setenv("MUTATION_SAMPLE_SEED", "fixed-seed")
    monkeypatch.setattr(SAMPLER, "list_eligible", lambda _root: ["scripts/a.py"])

    # The selection step is stubbed rather than run: this test is about which
    # command main HANDS to the coverage probe and to the failure message, not
    # about coverage collection, and an unstubbed probe would spawn the runner.
    seen: dict[str, object] = {}

    def _no_eligible(**kwargs):
        seen.update(kwargs)
        return [], [], {}, {}

    monkeypatch.setattr(SAMPLER, "select_eligible_for_mutation", _no_eligible)

    try:
        returncode = SAMPLER.main()
    except SystemExit as exc:  # pragma: no cover - main returns rather than exits here
        returncode = exc.code

    assert returncode == 1
    assert seen["test_command"] == REPLACEMENT, (
        "the coverage probe must receive the override, not the config literal"
    )
    err = capsys.readouterr().err
    assert REPLACEMENT in err, err
    assert "python3 -m pytest -q tests" not in err


def test_an_exemption_is_keyed_to_its_site_and_does_not_leak_to_another() -> None:
    """Asserted DIRECTLY, because deleting `item.site == site` left the suite green.

    A bounded reviewer measured that: every exemption test used a matching site,
    so the site half of the key was unpinned and one exemption anywhere would have
    silenced its rule everywhere — the "declaration equals silence" failure the
    exemption design exists to prevent.
    """
    registry = DOMINANCE.parse_registry(
        {
            "version": 1,
            "dominated_commands": [_rule(broad_targets=["tests"])],
            "exemptions": [
                {
                    "id": "only-here",
                    "site": "one.md",
                    "rule": "bare-pytest-whole-suite",
                    "reason": "this one site is deliberate",
                }
            ],
        }
    )
    here = DOMINANCE.classify_site("pytest tests", registry, site="one.md")
    elsewhere = DOMINANCE.classify_site("pytest tests", registry, site="two.md")
    assert here is not None and here.exempt
    assert elsewhere is not None and not elsewhere.exempt, (
        "an exemption naming one site must not excuse another"
    )


def test_a_finding_carries_the_line_it_was_found_on() -> None:
    """Unasserted before: deleting the `line` field left every finding
    un-locatable and the suite green. It matters more now that a standing-gate
    exemption is file-wide — `line` is what shows which command was judged."""
    registry = DOMINANCE.parse_registry(_data(dominated_commands=[_rule(broad_targets=["tests"])]))
    findings = DOMINANCE.scan_document("intro\n\n`pytest tests`\n", registry, site="d.md")
    assert [f.line for f in findings] == [3]
    assert findings[0].as_payload()["line"] == 3


def test_the_wrapped_snippet_ratio_this_repo_documents_is_the_measured_one() -> None:
    """The false quantity, now asserted instead of asserted about.

    Four surfaces carried "13 of 14 snippets are wrapped". A bounded reviewer
    counted the tree by hand and refuted it; running the discovery confirms 8
    wrapped and 6 unwrapped. The figure justifies the whole `wrapper_programs`
    mechanism, so it is pinned here rather than left as prose that drifts.
    """
    import adapter_lib

    discovery = load_path_module(
        "standing_gate_discovery_for_ratio",
        ROOT / "skills" / "public" / "quality" / "scripts" / "standing_gate_discovery_lib.py",
    )
    registry = DOMINANCE.parse_registry(
        adapter_lib.load_yaml_file(ROOT / ".agents" / "command-dominance.yaml")
    )
    snippets = discovery.iter_snippets(discovery.discover_surfaces(ROOT))

    def _is_wrapped(snippet: str) -> bool:
        """The MECHANISM's notion of wrapped, not a lookalike.

        A round-2 reviewer measured that first-token matching disagrees with the
        resolver, which strips `VAR=value`, `env`, interpreters, and `bash -c`
        before consulting wrappers. `env FOO=1 queue_selected "x" ...` is wrapped
        by the mechanism and unwrapped by a first-token test, so the number being
        pinned was not the number being justified.
        """
        without = DOMINANCE.resolve_invocations(snippet, ())
        with_wrappers = DOMINANCE.resolve_invocations(snippet, registry.wrappers)
        return without != with_wrappers

    wrapped = sum(1 for s in snippets if _is_wrapped(s["snippet"]))
    assert (len(snippets), wrapped) == (16, 10), (
        "the wrapped/total ratio documented in command_dominance_lib.Wrapper and in "
        ".agents/command-dominance.yaml has drifted; re-measure BOTH files and this "
        "assertion together"
    )


def test_a_focused_run_with_no_path_target_is_not_dominated() -> None:
    """`pytest -k smoke` runs one test and was being reported DOMINATED.

    The first implementation read "no positional targets" as "everything", so a
    gate blocked a one-test command and told the author to run the whole suite —
    while the function's own docstring and the exported reference both promised
    focused runs were safe. Found by a bounded reviewer.
    """
    import adapter_lib

    registry = DOMINANCE.parse_registry(
        adapter_lib.load_yaml_file(ROOT / ".agents" / "command-dominance.yaml")
    )
    for focused in ("pytest -k smoke", "python3 -m pytest -q -k test_foo", "python3 -m pytest -m smoke"):
        assert DOMINANCE.match_command(focused, registry) is None, focused
    # And the reverse must still hold: a focus flag does NOT excuse a command
    # that also names the whole tree, or SC17's own live instance would retire.
    assert DOMINANCE.match_command("python3 -m pytest -q -m 'not release_only' tests", registry) is not None


# --------------------------------------------------------------------------
# Round-1 repair lines the proof reported as unproven.
# --------------------------------------------------------------------------


def test_the_focus_arm_continues_to_the_next_rule_rather_than_abandoning_them() -> None:
    """`continue`, not `return None`, and a TWO-rule registry is what tells them apart.

    A round-2 reviewer measured that the first version of this test used one rule
    and one invocation, where the two are behaviourally identical — so the
    mutation its name implied it caught was undetectable. With a second rule whose
    focus flags do NOT match, `return None` would silently retire the rest of the
    registry for that command.
    """
    registry = DOMINANCE.parse_registry(
        {
            "version": 1,
            "dominated_commands": [
                _rule(id="pytest-focus-aware", value_flags=["-k"], focus_flags=["-k"]),
                {
                    "id": "pytest-focus-blind",
                    "program": "pytest",
                    "value_flags": ["-k"],
                    "replacement": "something-cheaper",
                    "reason": "a second rule that declares no focus flags",
                },
            ],
        }
    )
    # The first rule skips on `-k`; the second has no focus flags and must still
    # be reached, so the command is dominated BY THE SECOND RULE.
    matched = DOMINANCE.match_command("pytest -k smoke", registry)
    assert matched is not None and matched.rule_id == "pytest-focus-blind", (
        "the focus arm must continue to the next rule, not abandon the registry"
    )


def test_a_reordering_flag_is_not_a_focus_flag_in_this_repos_registry() -> None:
    """`--failed-first` reorders and excludes nothing.

    It was listed as narrowing for one round, which let a full whole-suite run
    pass clean. `--last-failed` genuinely narrows and stays.
    """
    import adapter_lib

    registry = DOMINANCE.parse_registry(
        adapter_lib.load_yaml_file(ROOT / ".agents" / "command-dominance.yaml")
    )
    rule = registry.rule("bare-pytest-whole-suite")
    assert "--failed-first" not in rule.focus_flags
    assert "--last-failed" in rule.focus_flags
    assert DOMINANCE.match_command("python3 -m pytest -q --failed-first", registry) is not None
    assert DOMINANCE.match_command("python3 -m pytest -q --last-failed", registry) is None


def test_an_equals_joined_focus_flag_is_recognised() -> None:
    """`--deselect=x` is the live spelling; the `=` split was unexercised."""
    registry = DOMINANCE.parse_registry(
        _data(dominated_commands=[_rule(broad_targets=["tests"], focus_flags=["--deselect"])])
    )
    assert DOMINANCE.match_command("pytest --deselect=tests/a.py::t", registry) is None


def test_a_shell_operator_inside_quotes_does_not_split_the_command() -> None:
    """The quote-blind split made `bash -c` support dead for the case it names.

    `bash -c "pytest tests && echo ok"` split mid-quote, both halves failed
    `shlex.split` with an unterminated quote, and a dominated whole-suite run
    inside a blocking gate's own runner was INVISIBLE. Found by an adversarial
    round-2 reviewer.
    """
    registry = DOMINANCE.parse_registry(_data(dominated_commands=[_rule(broad_targets=["tests"])]))
    assert DOMINANCE.split_chunks('bash -c "pytest tests && echo ok"') == [
        'bash -c "pytest tests && echo ok"'
    ]
    assert DOMINANCE.match_command('bash -c "pytest tests && echo ok"', registry) is not None
    # An operator OUTSIDE quotes still splits, and a later chunk is still read.
    assert DOMINANCE.match_command("echo hi && pytest tests", registry) is not None
    # A quoted operator is not an operator.
    assert DOMINANCE.split_chunks('pytest -k "a && b"') == ['pytest -k "a && b"']


def test_the_manifest_records_the_command_the_probe_actually_ran() -> None:
    """The round-1 blocker, pinned. Reverting it left the whole suite green.

    The manifest is uploaded as a CI artifact and pasted into auto-filed
    regression issue bodies, so a wrong `coverage_command` tells an auditor the
    dominated serial command produced coverage the standing runner produced.
    """
    manifest_lib = importlib.import_module("scripts.mutation_manifest_lib")
    state = {
        "repo_root": ROOT,
        "test_command": "python3 -m pytest -q -m 'not release_only' tests",
        "coverage_test_command": REPLACEMENT,
        "mutation_test_command": "python3 -m pytest -q tests/x.py::t",
        "coverage_json": ROOT / "reports" / "mutation" / "test-coverage.json",
        "all_eligible": [],
        "eligible": [],
        "sample": [],
        "changed": [],
        "changed_sample": [],
        "fill_sample": [],
        "changed_before_coverage": [],
        "uncovered_changed_files": [],
        "changed_line_uncovered_changed_files": [],
        "changed_line_uncovered_changed_line_targets": {},
        "changed_files_excluded_by_file_coverage": [],
        "changed_files_excluded_by_mutation_line_coverage": [],
        "selection_excluded_changed_files": [],
        "selection_excluded_fill_files": [],
        "selected_executable_mutants": 0,
        "line_contexts": {},
        "mutation_line_coverage": {},
        "workload_limits": (120, 80, 40),
        "changed_quota": 0,
        "max_files": 5,
        "min_file_coverage": 0.85,
        "seed": "fixed-seed",
        "base_sha": "",
        "head_sha": "HEAD",
        "pool_for_path": lambda _p: "core-python",
    }
    built = manifest_lib.build_manifest_from_state({**state, "coverage_enabled": True})
    assert built["coverage_command"] == REPLACEMENT, (
        "the manifest must record the command the coverage probe ran, not the config literal"
    )
    skipped = manifest_lib.build_manifest_from_state({**state, "coverage_enabled": False})
    assert skipped["coverage_command"] is None, "no probe ran, so neither command is honest"



def test_the_inventory_reports_an_unreadable_adapter_rather_than_crashing(tmp_path) -> None:
    """A consumer's malformed quality adapter must not fail their lane.

    Same reasoning as the malformed-registry path: this is an EXPORTED advisory,
    and a traceback here is the stranded-consumer defect.
    """
    (tmp_path / ".agents").mkdir()
    registry = tmp_path / ".agents" / "command-dominance.yaml"
    registry.write_text(REGISTRY_YAML, encoding="utf-8")
    adapter = tmp_path / ".agents" / "quality-adapter.yaml"
    adapter.write_text("runtime_budgets: [this is: not, a: mapping\n", encoding="utf-8")
    payload = INVENTORY.inventory(tmp_path, registry, adapter)
    assert payload["budget_state"]["state"] == "unreadable"
    assert payload["budget_state"]["detail"]


def test_a_relative_adapter_path_resolves_against_the_repo_root(tmp_path, monkeypatch, capsys) -> None:
    """Observes the RESOLUTION, not just that something was emitted.

    A round-2 reviewer measured that the first version asserted only exit 0 and a
    key's presence: deleting the resolution left it green, and pytest's cwd is the
    charness checkout, so a relative path silently resolved to the WRONG repo's
    adapter and still reported `loaded`. The tmp adapter declares a distinctive
    label count, so reading the wrong file changes the assertion.
    """
    repo = _repo_with_registry(tmp_path, literal=REPLACEMENT)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nruntime_budgets:\n  only-one-label-here: 1000\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "inventory_command_dominance.py",
            "--repo-root",
            str(repo),
            "--quality-adapter-path",
            ".agents/quality-adapter.yaml",
        ],
    )
    assert INVENTORY.main() == 0
    out = capsys.readouterr().out
    assert "1 budgeted label(s)" in out, (
        "the tmp repo's adapter declares exactly one label; a different count means "
        "the relative path resolved against the wrong root"
    )


def test_the_missing_yaml_message_names_the_pinned_contract_when_it_exists() -> None:
    """In-process, because the subprocess proof runs a COPY.

    Coverage attributes a copied script to the copy's path, so the end-to-end
    subprocess test can never prove this file's own handler lines however strong
    it is. Both branches are proven here; the subprocess test still proves the
    guard actually fires.
    """
    message = INVENTORY.missing_yaml_message("yaml", INVENTORY_PATH)
    assert "PyYAML is missing" in message
    requirements = ROOT / "packaging" / "bootstrap-requirements.txt"
    assert str(requirements) in message
    assert requirements.is_file(), "the guard must not name a path that does not exist"


def test_the_missing_yaml_message_says_the_install_is_incomplete_with_no_contract(tmp_path) -> None:
    """The no-fallback branch. A counted hop here printed a nonexistent path."""
    detached = tmp_path / "vendored" / "scripts"
    detached.mkdir(parents=True)
    message = INVENTORY.missing_yaml_message("yaml", detached / "inventory_command_dominance.py")
    assert "this install is incomplete" in message
    assert "bootstrap-requirements.txt` was found in any parent" in message
    assert "pip install PyYAML" in message
    for token in message.split():
        candidate = token.strip("`,.")
        if candidate.startswith("/") and candidate.endswith("bootstrap-requirements.txt"):
            raise AssertionError(f"the guard invented a requirements path: {candidate}")


def test_the_yaml_guard_says_the_install_is_incomplete_when_no_contract_is_found(tmp_path) -> None:
    """The no-fallback branch, EXECUTED.

    The old counted-hop fallback printed `<repo>/skills/packaging/...`, a path
    that does not exist, stranding the consumer this guard exists to un-strand.
    The guard now names the incompleteness instead of inventing a path. Driven by
    copying the script somewhere with no `packaging/` ancestor and blocking yaml.
    """
    detached = tmp_path / "vendored"
    detached.mkdir()
    (detached / "inventory_command_dominance.py").write_text(
        INVENTORY_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    blocker = tmp_path / "sitecustomize.py"
    # Chains to coverage's own startup. Python imports exactly ONE `sitecustomize`,
    # so a bare blocker on PYTHONPATH DISPLACES the one coverage installs and the
    # subprocess contributes no coverage at all -- which is why the changed-line
    # proof reported this guard's line unproven while this test was passing.
    blocker.write_text(
        "import sys\n"
        "class _NoYaml:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'yaml' or name.startswith('yaml.'):\n"
        "            raise ModuleNotFoundError('No module named yaml', name='yaml')\n"
        "        return None\n"
        "sys.meta_path.insert(0, _NoYaml())\n"
        "try:\n"
        "    import coverage\n"
        "    coverage.process_startup()\n"
        "except Exception:\n"
        "    pass\n",
        encoding="utf-8",
    )
    import os

    result = subprocess.run(
        [sys.executable, str(detached / "inventory_command_dominance.py"), "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
        cwd=str(tmp_path),
        check=False,
    )
    assert result.returncode != 0
    message = result.stdout + result.stderr
    assert "this install is" in message
    assert "packaging/bootstrap-requirements.txt" not in message.split("no `")[0]
