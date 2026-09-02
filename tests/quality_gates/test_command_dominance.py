"""Acceptance for the cost-dominance seams (SC14, SC15, SC17, SC19).

The FIRST test in this file is the one that fails when the mechanism measures the
wrong noun, and that ordering is deliberate. Both false central claims of the
preceding session were reachable from the single question "what can this
mechanism NOT see?", and both were found by a reviewer rather than by the author.
The registry's replacement for a bare-pytest run is
`python3 scripts/run_standing_pytest.py` — whose own path contains the substring
`pytest`. A detector that asks "does this mention pytest" reports the FIX as the
DEFECT, stays green on everything that matters, and reads exactly like a working
gate. That is the wrong noun, and `test_naming_the_replacement_is_not_a_prescription`
is what fails when it is measured.

Driven in-process rather than by subprocess, following the #322 convention.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tests.script_main import load_script_module

from .support import ROOT

DOMINANCE = load_script_module(
    "command_dominance_lib_under_test",
    ROOT / "skills" / "public" / "quality" / "scripts" / "command_dominance_lib.py",
)
GATE = load_script_module(
    "check_command_dominance_under_test", ROOT / "scripts" / "check_command_dominance.py"
)
UNIVERSE = load_script_module(
    "check_runtime_budget_universe_under_test",
    ROOT / "scripts" / "check_runtime_budget_universe.py",
)

REPLACEMENT = "python3 scripts/run_standing_pytest.py"


def _registry_data(
    *, exemptions: list[dict] | None = None, wrappers: list[dict] | None = None
) -> dict:
    return {
        "version": 1,
        "dominated_commands": [
            {
                "id": "bare-pytest-whole-suite",
                "program": "pytest",
                "broad_targets": ["tests"],
                "value_flags": ["-m", "-k", "-n"],
                "replacement": REPLACEMENT,
                "reason": "the standing runner covers the same scope in a fraction of the time",
            }
        ],
        "wrapper_programs": wrappers or [],
        "exemptions": exemptions or [],
    }


def _registry(**kwargs):
    return DOMINANCE.parse_registry(_registry_data(**kwargs))


# --------------------------------------------------------------------------
# 1. The wrong-noun tests. These fail if the mechanism measures text instead of
#    the command a site actually runs.
# --------------------------------------------------------------------------


def test_naming_the_replacement_is_not_a_prescription() -> None:
    """The fix is not the defect.

    `python3 scripts/run_standing_pytest.py` contains the substring `pytest`. A
    substring reader flags every document and gate that adopts the replacement,
    which is every surface this slice repairs.
    """
    registry = _registry()
    assert DOMINANCE.match_command(REPLACEMENT, registry) is None
    assert DOMINANCE.match_command(f"{REPLACEMENT} --repo-root .", registry) is None
    findings = DOMINANCE.scan_document(
        f"Re-prove the suite with `{REPLACEMENT}`.\n", registry, site="doc.md"
    )
    assert findings == []


def test_a_focused_bare_pytest_run_is_not_dominated() -> None:
    """Breadth of TARGETS is the noun, not the program alone.

    The parallel runner's startup is not worth paying for one file, and this
    repo's own `.agents/surfaces.json` carries a dozen focused pytest commands. A
    reader that fires on the program alone turns all of them red on arrival,
    which is how a gate gets disabled rather than obeyed.
    """
    registry = _registry()
    assert (
        DOMINANCE.match_command("python3 -m pytest -q tests/quality_gates/test_x.py", registry)
        is None
    )
    assert DOMINANCE.match_command("python3 -m pytest -q tests/a.py tests/b.py", registry) is None


def test_a_value_flag_argument_is_not_read_as_a_target() -> None:
    """`-m 'not release_only'` is a marker expression, not a second target.

    Without `value_flags`, the whole-suite command looks like it targets two
    things, no `broad_targets` entry matches, and the one command this whole
    slice exists for reads as focused.
    """
    registry = _registry()
    rule = DOMINANCE.match_command("python3 -m pytest -q -m 'not release_only' tests", registry)
    assert rule is not None and rule.rule_id == "bare-pytest-whole-suite"


def test_a_wrapper_does_not_hide_the_command_it_runs() -> None:
    """A resolver that stops at the first token resolves every queued command to
    `queue_selected`, so the entire standing-gate arm reads clean while a
    dominated command sits one token inside it.

    This docstring carried "Measured on this repo: 13 of 14 discovered snippets
    are wrapped" for two rounds. The figure was refuted in round 1 (the measured
    split is 8 wrapped, 6 unwrapped) and the correction MISSED this file, while
    the contract recorded it as "Corrected everywhere". Round 2 found both. The
    ratio is not restated here at all now — it lives in exactly one place, the
    test that asserts it.
    """
    wrapped = 'queue_selected "suite" python3 -m pytest -q tests'
    assert DOMINANCE.match_command(wrapped, _registry()) is None, (
        "unwrapped registry should not see it"
    )
    registry = _registry(wrappers=[{"program": "queue_selected", "skip_args": 1}])
    assert DOMINANCE.match_command(wrapped, registry) is not None


def test_env_and_bash_c_do_not_hide_the_command_they_run() -> None:
    registry = _registry()
    assert DOMINANCE.match_command("env FOO=1 python3 -m pytest tests", registry) is not None
    assert DOMINANCE.match_command('bash -c "python3 -m pytest tests"', registry) is not None
    # The repo's own runner is spelled with a leading `env`; it must stay clean.
    assert (
        DOMINANCE.match_command(
            f"env CHARNESS_STANDING_PYTEST_PYTHON=python3 {REPLACEMENT}", registry
        )
        is None
    )


def test_prose_naming_a_command_in_words_is_not_scanned() -> None:
    """Blind-class item 3, pinned.

    Only fenced blocks and inline code are read. A reader that matched prose
    would fire on the library's own docstring and on this test file. The limit is
    real and is stated at every surface that consumes it.
    """
    text = "Do not run pytest over the whole tests directory; it takes far too long.\n"
    assert DOMINANCE.scan_document(text, _registry(), site="doc.md") == []


def test_a_config_literal_line_is_read_as_its_value_not_as_the_whole_line() -> None:
    """The bug this file caught in the slice that wrote it.

    A second copy of the config reader matched the whole `test-command = "..."`
    LINE and handed it to the classifier, which resolved the program to
    `test-command` and reported a clean tree over a dominated literal.
    """
    body = "timeout = 300.0\ntest-command = \"python3 -m pytest -q -m 'not release_only' tests\"\n"
    literals = DOMINANCE.read_config_literal(body, "test-command")
    assert literals == [(2, "python3 -m pytest -q -m 'not release_only' tests")]
    assert DOMINANCE.match_command(literals[0][1], _registry()) is not None


# --------------------------------------------------------------------------
# 2. Declaration must not equal silence. Both directions are pinned, because
#    "the criterion is satisfied by declaring something" is exactly how the
#    sibling export gate was falsified one slice earlier.
# --------------------------------------------------------------------------


def test_declaring_the_replacement_does_not_silence_the_dominated_original() -> None:
    registry = _registry()
    findings = DOMINANCE.scan_document(
        f"Fast: `{REPLACEMENT}`. Slow: `python3 -m pytest tests/ -q --no-header`.\n",
        registry,
        site="doc.md",
    )
    assert len(findings) == 1
    assert findings[0].command == "python3 -m pytest tests/ -q --no-header"
    assert not findings[0].exempt


def test_an_exemption_does_not_remove_the_site_from_the_report() -> None:
    """An exemption changes `exempt`, never presence.

    A mechanism where "we decided this one is fine" makes a site DISAPPEAR
    converts every future reader's view of the repo into the set of things nobody
    exempted, which is not the same as the set of things that are fine.
    """
    registry = _registry(
        exemptions=[
            {
                "id": "doc-quotes-the-old-command",
                "site": "doc.md",
                "rule": "bare-pytest-whole-suite",
                "reason": "quoted as the historical instance, not prescribed",
            }
        ]
    )
    findings = DOMINANCE.scan_document("`python3 -m pytest tests`\n", registry, site="doc.md")
    assert len(findings) == 1, "the exempt site must still be reported"
    assert findings[0].exempt
    assert findings[0].exemption_reason


def test_a_reasonless_exemption_is_refused() -> None:
    data = _registry_data(
        exemptions=[{"id": "x", "site": "doc.md", "rule": "bare-pytest-whole-suite"}]
    )
    with pytest.raises(DOMINANCE.RegistryError, match="reason"):
        DOMINANCE.parse_registry(data)


def test_an_exemption_naming_no_live_rule_is_refused() -> None:
    data = _registry_data(
        exemptions=[{"id": "x", "site": "doc.md", "rule": "retired-rule", "reason": "because"}]
    )
    with pytest.raises(DOMINANCE.RegistryError, match="unknown rule"):
        DOMINANCE.parse_registry(data)


def test_a_reasonless_rule_is_refused() -> None:
    data = _registry_data()
    del data["dominated_commands"][0]["reason"]
    with pytest.raises(DOMINANCE.RegistryError, match="`reason` is required"):
        DOMINANCE.parse_registry(data)


def test_a_registry_from_a_future_version_is_refused_not_partly_read() -> None:
    data = _registry_data()
    data["version"] = 99
    with pytest.raises(DOMINANCE.RegistryError, match="version"):
        DOMINANCE.parse_registry(data)


# --------------------------------------------------------------------------
# 4. SC17 -- the seam a document never appears in.
# --------------------------------------------------------------------------


def test_sc17_reports_this_repos_real_cosmic_ray_literal() -> None:
    report = GATE.evaluate(ROOT)
    assert report["armed"]
    sites = {finding["site"] for finding in report["findings"]}
    assert "cosmic-ray.toml:test-command" in sites, (
        "the gate-spawned config literal is SC17's named subject; a run that does "
        "not report it is measuring something else"
    )


def test_sc17_a_config_literal_naming_the_replacement_is_not_reported(tmp_path: Path) -> None:
    """Discriminates on DOMINANCE, not on being a config literal at all."""
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text(
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
        "    key: test-command\n",
        encoding="utf-8",
    )
    (tmp_path / "cosmic-ray.toml").write_text(
        f'[cosmic-ray]\ntest-command = "{REPLACEMENT} --repo-root ."\n', encoding="utf-8"
    )
    report = GATE.evaluate(tmp_path)
    assert report["armed"]
    assert report["findings"] == []
    assert report["blocking"] == []


def test_sc17_an_unexempt_dominated_literal_blocks(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text(
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
        "    key: test-command\n",
        encoding="utf-8",
    )
    (tmp_path / "cosmic-ray.toml").write_text(
        '[cosmic-ray]\ntest-command = "python3 -m pytest -q tests"\n', encoding="utf-8"
    )
    report = GATE.evaluate(tmp_path)
    assert len(report["blocking"]) == 1
    assert REPLACEMENT in report["blocking"][0]


def test_sc17_reads_consumer_registry_and_declared_src_literal(tmp_path: Path) -> None:
    (tmp_path / ".agents").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text(
        "version: 1\n"
        "dominated_commands:\n"
        "  - id: bare-pytest-whole-suite\n"
        "    program: pytest\n"
        "    broad_targets:\n"
        "      - tests\n"
        f"    replacement: {REPLACEMENT}\n"
        "    reason: the standing runner covers the same scope\n"
        "config_literals:\n"
        "  - path: src/tool.toml\n"
        "    key: test-command\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "tool.toml").write_text(
        '[tool]\ntest-command = "python3 -m pytest -q tests"\n', encoding="utf-8"
    )

    report = GATE.evaluate(tmp_path)

    assert report["armed"] is True
    assert report["scanned_sites"]["config_literals"] == ["src/tool.toml:test-command"]
    assert report["findings"][0]["site"] == "src/tool.toml:test-command"


def test_sc17_refuses_a_registry_the_repo_reader_cannot_fully_read(tmp_path: Path) -> None:
    """A half-read registry is a rule that silently is not there.

    The repo gate reads this file with the hand-rolled adapter parser and the
    exported inventory reads it with PyYAML. A flow mapping is accepted by one and
    mangled by the other, so a verdict from the narrower reader would be rendered
    over a registry it did not fully read. It must REFUSE, by whichever arm
    reaches it first, rather than report a clean tree.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text(
        "version: 1\n"
        "dominated_commands:\n"
        "  - id: bare-pytest-whole-suite\n"
        "    program: pytest\n"
        "    broad_targets:\n"
        "      - tests\n"
        f"    replacement: {REPLACEMENT}\n"
        "    reason: the standing runner covers the same scope\n"
        "config_literals:\n"
        "  - {path: cosmic-ray.toml, key: test-command}\n",
        encoding="utf-8",
    )
    # The gate loads its OWN copy of the library, so its `RegistryError` is a
    # different class object than `DOMINANCE.RegistryError` even though both are
    # the same source file. Asserting against the gate's copy is the honest
    # binding; asserting against this module's copy would pass or fail for a
    # reason unrelated to the behaviour under test.
    with pytest.raises(GATE._load_dominance_lib().RegistryError):
        GATE.evaluate(tmp_path)


def test_sc17_is_not_armed_rather_than_crashing_without_a_registry(tmp_path: Path) -> None:
    report = GATE.evaluate(tmp_path)
    assert report["armed"] is False
    assert report["findings"] == []


def test_sc17_an_exempt_only_run_still_carries_an_attention_marker() -> None:
    """An advisory the runner cannot see is written to a log nobody opens.

    `print_phase_output` surfaces a PASSING phase's log only when it carries a
    WARN/ADVISORY marker. A round-2 reviewer measured the same mechanism failing
    one slice ago because the note began `ADVISORY,` with a comma the marker
    regex does not match — the advisory bargain buying nothing.
    """
    payload = GATE.report_payload(
        {
            "armed": True,
            "blocking": [],
            "exempt_count": 1,
            "findings": [],
        },
        DOMINANCE,
    )
    assert "advisory" in payload
    assert payload["advisory"].startswith("WARN: ")


def test_sc17_a_clean_run_with_no_exemptions_carries_no_false_attention_marker() -> None:
    payload = GATE.report_payload(
        {"armed": True, "blocking": [], "exempt_count": 0, "findings": []}, DOMINANCE
    )
    assert "advisory" not in payload


# --------------------------------------------------------------------------
# 5. SC15 -- the direction the universe check did not have.
# --------------------------------------------------------------------------


def test_sc15_reports_a_spawned_expensive_command_outside_every_budgeted_label() -> None:
    report = UNIVERSE.evaluate(ROOT)
    assert report["armed"]
    sites = {entry["site"] for entry in report["unbudgeted_expensive_commands"]}
    assert "cosmic-ray.toml:test-command" in sites


def test_sc15_the_existing_budgeted_label_direction_still_reports(tmp_path, monkeypatch) -> None:
    """The negative the criterion names: adding a direction must not retire one.

    REWRITTEN after a bounded reviewer measured that the first version built a
    dict, re-implemented `evaluate`'s comprehension in the test body, and asserted
    on its own copy — plus a key-presence check on a key every return path sets.
    Replacing the production comprehension with `unknown = []` retired the entire
    first direction and left that test, the one named `..._still_reports`, green.

    This drives the real `evaluate` over a real adapter carrying a budget whose
    label the runner does not queue, which is the mutation the old test missed.
    """
    adapter = ROOT / ".agents" / "quality-adapter.yaml"
    real = adapter.read_text(encoding="utf-8")
    assert "runtime_budgets:" in real
    phantom = real.replace(
        "runtime_budgets:\n", "runtime_budgets:\n  a-label-no-runner-queues: 1234\n", 1
    )
    assert phantom != real

    monkeypatch.setattr(
        UNIVERSE.adapter_lib,
        "load_yaml_file",
        lambda path: UNIVERSE.adapter_lib.load_yaml(
            phantom if path == ROOT / UNIVERSE.ADAPTER_PATH else path.read_text(encoding="utf-8")
        ),
    )
    report = UNIVERSE.evaluate(ROOT)
    assert report["armed"]
    assert "a-label-no-runner-queues" in {entry["label"] for entry in report["unknown_labels"]}, (
        "a budget naming a label the runner cannot queue must still be reported"
    )


def test_sc15_a_real_budgeted_label_suppresses_its_own_command(tmp_path) -> None:
    """The second direction must key on the QUEUE LABEL and the BUDGETED set.

    Its first version derived a label from the tail of the site string and
    compared it against the runner universe, so it computed a different predicate
    than the sentence it printed. Two independent reviewers found it. This drives
    a real wrapped command whose label IS budgeted, and the same command with the
    label removed from the budgeted set.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text(
        "version: 1\n"
        "dominated_commands:\n"
        "  - id: bare-pytest-whole-suite\n"
        "    program: pytest\n"
        "    broad_targets:\n"
        "      - tests\n"
        f"    replacement: {REPLACEMENT}\n"
        "    reason: the standing runner covers the same scope\n"
        "wrapper_programs:\n"
        "  - program: queue_selected\n"
        "    skip_args: 1\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "run-quality.sh").write_text(
        '#!/usr/bin/env bash\nqueue_selected "suite" python3 -m pytest -q tests\n', encoding="utf-8"
    )
    (tmp_path / ".githooks").mkdir()
    (tmp_path / ".githooks" / "pre-push").write_text(
        "#!/usr/bin/env bash\n./scripts/run-quality.sh\n", encoding="utf-8"
    )
    unbudgeted = UNIVERSE.unbudgeted_expensive_commands(tmp_path, set())
    assert [entry["queue_label"] for entry in unbudgeted] == ["suite"]
    assert "no budget entry" in unbudgeted[0]["basis"]
    assert UNIVERSE.unbudgeted_expensive_commands(tmp_path, {"suite"}) == [], (
        "a command whose QUEUE LABEL is budgeted has a bar that can fail"
    )


def test_sc15_says_what_it_did_not_judge_about_the_new_direction() -> None:
    payload = UNIVERSE.report_payload(UNIVERSE.evaluate(ROOT))
    joined = " ".join(payload["did_not_judge"])
    assert "denylist" in joined, (
        "a green second direction must not read as 'every expensive command is budgeted'"
    )


# --------------------------------------------------------------------------
# 6. SC19 -- the exported consumer half.
# --------------------------------------------------------------------------

INVENTORY = load_script_module(
    "inventory_command_dominance_under_test",
    ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_command_dominance.py",
)


def test_sc19_a_consumer_without_a_registry_gets_a_named_state_not_a_silent_zero(
    tmp_path: Path,
) -> None:
    """An empty finding list beside a green summary reads as 'nothing is
    dominated here', which is a claim a registry-less run has no basis for."""
    payload = INVENTORY.inventory(tmp_path, tmp_path / ".agents" / "command-dominance.yaml")
    assert payload["registry_state"]["state"] == "absent"
    assert payload["registry_state"]["next_action"]


def test_sc19_a_consumers_malformed_registry_does_not_crash_their_lane(tmp_path: Path) -> None:
    registry = tmp_path / "command-dominance.yaml"
    registry.write_text("version: 1\ndominated_commands: not-a-list\n", encoding="utf-8")
    payload = INVENTORY.inventory(tmp_path, registry)
    assert payload["registry_state"]["state"] == "unreadable"


def test_sc19_uses_the_already_exported_scanner_rather_than_a_new_one() -> None:
    """The criterion's own wording: the gap to close is the policy layer.

    A second scanner would be the duplicate-builder class this release already
    reconciled once.
    """
    source = (
        ROOT / "skills" / "public" / "quality" / "scripts" / "inventory_command_dominance.py"
    ).read_text(encoding="utf-8")
    assert "standing_gate_discovery_lib" in source
    assert "command_dominance_lib" in source


def test_sc19_the_inventory_declares_its_blind_spots() -> None:
    for field in ("measures", "proxy_for", "blind_spots", "interpretation_question"):
        assert INVENTORY.INTERPRETATION[field].strip()
    assert "denylist" in INVENTORY.INTERPRETATION["blind_spots"].lower()


def test_sc19_answers_the_budget_question_the_exported_angle_promises(tmp_path: Path) -> None:
    """Owner ruling 2026-08-16: implement the budget half rather than narrow the claim.

    A bounded reviewer measured that the exported critique angle told consumers
    this inventory "answers ... is the expensive command budgeted at all" while it
    read no budgets anywhere. The claim shipped; the capability did not.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text(
        "version: 1\n"
        "dominated_commands:\n"
        "  - id: bare-pytest-whole-suite\n"
        "    program: pytest\n"
        "    broad_targets:\n"
        "      - tests\n"
        f"    replacement: {REPLACEMENT}\n"
        "    reason: the standing runner covers the same scope\n"
        "wrapper_programs:\n"
        "  - program: queue_selected\n"
        "    skip_args: 1\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "run-quality.sh").write_text(
        '#!/usr/bin/env bash\nqueue_selected "suite" python3 -m pytest -q tests\n', encoding="utf-8"
    )
    (tmp_path / ".githooks").mkdir()
    (tmp_path / ".githooks" / "pre-push").write_text(
        "#!/usr/bin/env bash\n./scripts/run-quality.sh\n", encoding="utf-8"
    )
    registry = tmp_path / ".agents" / "command-dominance.yaml"

    # No adapter at all: every command is unbudgeted, and the state says why.
    payload = INVENTORY.inventory(tmp_path, registry, tmp_path / ".agents" / "quality-adapter.yaml")
    assert payload["budget_state"]["state"] == "absent"
    assert [entry["queue_label"] for entry in payload["unbudgeted_commands"]] == ["suite"]

    # A budget naming that label removes it from the unbudgeted list.
    (tmp_path / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nruntime_budgets:\n  suite: 90000\n", encoding="utf-8"
    )
    payload = INVENTORY.inventory(tmp_path, registry, tmp_path / ".agents" / "quality-adapter.yaml")
    assert payload["budget_state"]["state"] == "loaded"
    assert payload["unbudgeted_commands"] == []


@pytest.mark.boundary_contract(
    reason="__main__ dispatch smoke: the exported inventory must run its full finding loop"
)
def test_sc19_never_fails_a_consumers_lane_even_when_it_has_findings(tmp_path: Path) -> None:
    """`main()` was only ever run over trees with nothing to report.

    A bounded reviewer measured the gap: changing the return to
    `1 if payload["dominated_findings"] else 0` passed every test in the slice
    while handing a red lane to exactly the consumers who have findings.
    """
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "command-dominance.yaml").write_text(
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
        "    key: test-command\n",
        encoding="utf-8",
    )
    (tmp_path / "cosmic-ray.toml").write_text(
        '[cosmic-ray]\ntest-command = "python3 -m pytest -q tests"\n', encoding="utf-8"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills/public/quality/scripts/inventory_command_dominance.py"),
            "--repo-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "dominated_findings" in result.stdout
    assert "cosmic-ray.toml:test-command" in result.stdout, "the tree must actually have a finding"
    assert result.returncode == 0, (
        "an exported advisory must never fail a consumer's lane, findings or not"
    )


def test_the_universe_advisory_marker_is_pinned() -> None:
    """The sibling gate's marker is pinned twice; this one's was not.

    Deleting the advisory passed the suite while the comment beside it claimed
    the marker was load-bearing for `print_phase_output` — the advisory-buys-
    nothing shape the comment itself cites.
    """
    payload = UNIVERSE.report_payload(
        {
            "armed": True,
            "unknown_labels": [],
            "unbudgeted_expensive_commands": [
                {"site": "x.toml:k", "command": "pytest tests", "queue_label": None, "basis": "b"}
            ],
            "checked": 1,
            "universe_size": 1,
            "universe_sources": {},
        }
    )
    assert payload["advisory"].startswith("WARN")
    assert "basis" in payload["advisory"]


def test_sc19_and_sc16_ship_to_consumers_rather_than_living_only_here(
    exported_plugin_tree: Path,
) -> None:
    """Both criteria are `exported-surface` verification types.

    A cost angle that lives only in this repo's own review prompts satisfies the
    sentence and not the criterion.
    """
    plugin = exported_plugin_tree
    # CONTENT, not `.is_file()`. A byte-stale mirror -- a pre-slice copy without
    # the blind-class paragraph -- satisfied every earlier assertion here.
    # The SIBLINGS are listed, not just the lib. `command_dominance_lib` loads
    # `command_dominance_registry` and `command_dominance_carriers` by path from its own
    # directory, so an export shipping the lib without them raises at import on the first
    # consumer machine -- which is #634's class exactly: a dependency that was pinned in
    # the source tree and did not travel.
    for rel in (
        "skills/quality/scripts/inventory_command_dominance.py",
        "skills/quality/scripts/command_dominance_lib.py",
        "skills/quality/scripts/command_dominance_registry.py",
        "skills/quality/scripts/command_dominance_carriers.py",
        "skills/quality/references/cost-dominance.md",
    ):
        source = ROOT / rel.replace("skills/", "skills/public/", 1)
        assert (plugin / rel).read_text(encoding="utf-8") == source.read_text(encoding="utf-8"), (
            f"exported mirror of {rel} is stale; run sync_root_plugin_manifests.py"
        )
    angles = (plugin / "skills" / "critique" / "references" / "angle-selection.md").read_text(
        encoding="utf-8"
    )
    assert "cost-dominance" in angles
    # Loaded FROM THE EXPORT, in a fresh module namespace, so "the files are present"
    # is not mistaken for "the family imports there". The sibling loader resolves
    # relative to `__file__`, and this is the only assertion that exercises that.
    import importlib.util

    exported = plugin / "skills" / "quality" / "scripts" / "command_dominance_lib.py"
    spec = importlib.util.spec_from_file_location("exported_command_dominance_lib", exported)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.parse_registry({"version": module.REGISTRY_VERSION, "rules": []}).rules == ()
    assert module.split_chunks('bash -c "a && b"') == ['bash -c "a && b"']


# --------------------------------------------------------------------------
# 7. This repo's own registry has to parse, or every gate above is inert.
# --------------------------------------------------------------------------


def test_this_repos_registry_parses_and_every_exemption_carries_a_reason() -> None:
    import adapter_lib

    registry = DOMINANCE.parse_registry(
        adapter_lib.load_yaml_file(ROOT / ".agents" / "command-dominance.yaml")
    )
    assert registry.rules
    for exemption in registry.exemptions:
        assert exemption.reason.strip()
        assert registry.rule(exemption.rule_id) is not None
