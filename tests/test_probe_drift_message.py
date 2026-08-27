"""The drift message is only read when a probe drifts, so nothing green exercises it.

#536's repair is a message. `assert expr, msg` evaluates `msg` lazily, so in a passing suite
`probe_drift_message` is called ZERO times — a bounded round pointed out that deleting the
cause paragraph, the update list, or the commands would be a silent green edit, and that the
mutants proving those parts reach the reader had been killed by hand rather than by anything
checked in. `tests/` is also outside the mutation pool, so no gate covers it either.

These pin the claims the message makes, and the paths and commands it names. They do not judge
whether the prose reads well — they fail if it stops saying the load-bearing things, or if it
names a script or a probe that does not exist.

#624 showed that was not enough, and the gap is worth stating because it is the reason this file
reported green over the defect. Every pin here was an EXISTENCE predicate — `path.is_file()`,
`"_provenance" in payload`, `"recursive_variant" in ...`. None of them can see SUPERSESSION: when
#596 replaced the mutable marker pin with an immutable dated snapshot, the superseded file kept
existing with every key those pins name, so the message went on instructing edits to a frozen
artifact while this file stayed green. The circularity is worth naming too — the only live reader
of the superseded probe had become the test validating the message that named it.

So two structural pins were added, and they are the ones to keep honest:
`test_every_surface_named_is_one_a_live_caller_of_this_message_may_edit` derives the message's
legitimate surfaces from ITS ACTUAL CALL SITES rather than from a hand-maintained list, and
`test_the_decision_record_is_named_only_for_the_coupling_it_actually_has` pins the one figure D47
and this probe share instead of asserting that D47 needs editing whenever anything moves.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.probe_drift_support import (
    CORPUS_CAUSES,
    CORPUS_LIB,
    DECISION_RECORD,
    DISCRIMINATION_PATHS,
    DO_NOT_TOUCH_SURFACES,
    FLOOR_COMMAND,
    FLOOR_COUNTERFACTUAL_COMMAND,
    FLOOR_MEASURE_SCRIPT,
    FLOOR_PROBE,
    GATE_MIRROR,
    GATE_MODULE,
    MARKER_SNAPSHOT,
    MIRROR_SYNC_COMMAND,
    NOT_CAUSES,
    RESIDUAL_COMMAND,
    RESIDUAL_CONTRACT_DOC,
    RESIDUAL_FLOOR_HOME,
    RESIDUAL_FLOOR_MIRROR,
    RESIDUAL_FLOOR_SYMBOL,
    RESIDUAL_MEASURE_SCRIPT,
    RESIDUAL_PROBE,
    RESIDUAL_UPDATE_SURFACES,
    RULE_CAUSES,
    RULE_ONLY_SURFACES,
    SUPERSEDED_MARKER_PROBE,
    UPDATE_SURFACES,
    probe_drift_message,
    residual_floor_message,
)

ROOT = Path(__file__).resolve().parent.parent
# Every `probe_drift_message(..., probe=NAME)` call, with `NAME` captured as the constant it is
# written as. Resolved against the support module rather than matched as a literal, because the
# call sites all pass constants and a literal-only parse would report zero callers and pass.
CALL_SITE_RE = re.compile(r"probe_drift_message\(\s*\"[^\"]+\"\s*,\s*probe=(\w+)")


def test_the_message_separates_a_corpus_cause_from_a_rule_cause() -> None:
    """The correction that mattered most: the two causes have OPPOSITE remedies.

    A first version said flatly "the fix is to re-record, not to undo the write". That is wrong
    whenever the measurement rule moved rather than the corpus, and following it would launder a
    rule regression into the pinned probe and into the decision record.
    """
    message = probe_drift_message("artifacts", probe=FLOOR_PROBE)

    assert "FIRST decide WHICH changed" in message
    assert "If the CORPUS changed, re-record" in message
    assert "do NOT re-record yet" in message
    assert "launder a measurement" in message  # wraps across lines in the render
    # The rule causes a reader would otherwise mistake for a write.
    assert "inventory-consumer-fields.json" in message
    assert "ENFORCED_FROM_DATE" in message
    # No git-availability cause is asserted, and its ABSENCE is deliberate. Version 2 listed
    # one, and a round showed it named a field and a value no code produces (`exemption_state`
    # returns `not-corroborated`, never `unavailable`), got a shallow checkout backwards, and
    # could not move any pinned number on this corpus anyway — every artifact resolves
    # `not-claimed` before git is consulted. A cause that cannot fire is the wolf-crier this
    # goal's Non-Goals forbid, so it was removed rather than reworded.
    assert "git was unavailable" not in message
    # And the corpus cause a reader would otherwise miss, because no file appears or vanishes.
    assert "REWRITTEN" in message
    # `quality/history/` is now a NON-cause, and the distinction is load-bearing rather than
    # cosmetic: this probe's corpus glob is non-recursive, so a nested write cannot move a single
    # number here. It was listed as a corpus cause — with a re-record remedy — while a second,
    # recursive pin existed; #596 retired that pin and left the sentence, so a floor reader was
    # being handed the re-record remedy for a write that explains nothing. Asserting mere presence
    # of `history/` would pass either way, so the SECTION it sits under is what is pinned.
    non_causes_at = message.index("do NOT move these numbers")
    assert non_causes_at < message.index("quality/history/"), (
        "`quality/history/` moved back above the non-cause heading; this probe's glob is "
        "non-recursive, so a nested write is not a corpus cause for it"
    )
    assert "NON-RECURSIVE" in message


def test_the_message_names_every_surface_that_carries_the_same_numbers() -> None:
    """Six surfaces, and NOT the two #624 found it had outlived."""
    message = probe_drift_message("floor", probe=FLOOR_PROBE)

    assert FLOOR_PROBE in message
    assert GATE_MODULE in message
    assert GATE_MIRROR in message
    assert "_provenance` bookkeeping" in message
    assert "_provenance` prose keys" in message
    assert "_provenance.counterfactual_floor_20" in message
    # The two surfaces #624 reported. They still appear — a message that silently dropped them
    # would leave a reader acting on memory to re-do exactly what the issue reported — but they
    # must appear under the do-not-touch heading, never as an edit target.
    do_not_touch_at = message.index("And do NOT touch these")
    for surface in (SUPERSEDED_MARKER_PROBE, MARKER_SNAPSHOT):
        assert message.index(surface) > do_not_touch_at, (
            f"{surface} is named before the do-not-touch heading, so a reader following the "
            "update list literally will edit it — the #624 defect exactly"
        )


def test_the_message_does_not_tell_a_reader_to_overwrite_provenance() -> None:
    """The first version's actual defect: it would have deleted `_provenance`.

    The measure command emits only the measured payload (behind `--json` until that flag
    was retired repo-wide on 2026-08-14; unconditionally YAML since). Pasting that over a
    probe file destroys `_provenance`, and the next run then fails with a bare
    `KeyError: '_provenance'` — the diagnostic class #536 exists to remove, reintroduced
    by the fix for #536.
    """
    message = probe_drift_message("floor", probe=FLOOR_PROBE)

    # COUNT, and the count is DERIVED. It was hardcoded at 2 — one per probe — which meant that
    # removing the two superseded marker entries would have red-ed this pin, and the cheap way to
    # green it again is to keep a marker entry alive purely to satisfy the number. That is the pin
    # driving the prose, the inversion this module warns about. The claim is "every surface whose
    # command PASTES a payload says to keep `_provenance`", so that is what is counted.
    payload_pastes = [
        surface
        for surface, command in UPDATE_SURFACES
        if command is not None and command != MIRROR_SYNC_COMMAND
    ]
    assert payload_pastes, "no surface pastes a measured payload any more; re-derive this pin"
    for surface in payload_pastes:
        assert "keeping `_provenance`" in surface, surface
    assert message.count("keeping `_provenance`") == len(payload_pastes), message
    assert "does not emit `_provenance`" in message
    assert "cannot be pasted over a probe" in message


def test_every_path_and_command_the_message_names_actually_exists() -> None:
    """A message that names a wrong path is worse than the bare number it replaced."""
    path = ROOT / FLOOR_PROBE
    assert path.is_file(), f"the drift message names a probe that does not exist: {FLOOR_PROBE}"
    assert "_provenance" in json.loads(path.read_text(encoding="utf-8")), (
        f"{FLOOR_PROBE} has no `_provenance`; the message's keep-provenance instruction is stale"
    )
    assert (ROOT / DECISION_RECORD).is_file()

    # The do-not-touch entries are held to the same standard. A trap naming a file that no longer
    # exists is noise a reader learns to skip, and the next real trap is skipped with it.
    for surface in DO_NOT_TOUCH_SURFACES:
        named = surface.split(" — ")[0]
        assert (ROOT / named).is_file(), f"the message warns about a missing file: {named}"

    for command in (FLOOR_COMMAND, FLOOR_COUNTERFACTUAL_COMMAND):
        script = command.split()[1]
        assert (ROOT / script).is_file(), f"the drift message names a missing script: {script}"


def test_the_heading_names_the_probe_the_call_site_passed() -> None:
    """The heading took a `variant` argument until #624, and it had outlived its only caller.

    `variant` existed to distinguish the marker probe's nested recursive payload from its
    top-level one. That probe is no longer a caller and the floor probe has no nested payload, so
    the parameter could only ever have produced a heading describing a shape the reader does not
    have. What the heading still owes the reader is WHICH file the drifted key was read from.
    """
    message = probe_drift_message("rows", probe=FLOOR_PROBE)

    assert message.startswith(f"`rows` drifted from the recorded measurement in {FLOOR_PROBE}.")


def test_each_surface_is_paired_with_the_command_that_actually_produces_it() -> None:
    """The inversion a substring pin could not see.

    A round showed that swapping the marker and floor commands in the surface list left every
    assertion in this file green while instructing the reader to paste floor output over the
    marker payload — strictly worse than the bare number the message replaced. So the pairing is
    asserted, not just the presence of both strings. The marker half retired with #624; what the
    episode leaves behind is the shape of the check, which now also covers the UNPAIRED entries.
    """
    for surface, command in (*UPDATE_SURFACES, *RULE_ONLY_SURFACES):
        if command is None:
            # #624: a bare `continue` sat here, and it made this branch blind to precisely the
            # entries that went wrong — every dead surface the issue found was UNPAIRED, so the
            # one check that could have caught them skipped all of them. An unpaired surface is
            # still a surface: it must name a file a reader may edit BY HAND.
            assert surface.startswith((FLOOR_PROBE, GATE_MODULE, DECISION_RECORD)), (
                f"an unpaired surface names a file no hand edit belongs in: {surface}"
            )
            continue
        if FLOOR_PROBE in surface:
            assert command == FLOOR_COMMAND, surface
        elif GATE_MIRROR in surface:
            # Generated, so it gets a REGENERATE command rather than a paste target. It is the
            # one paired surface whose command does not print a payload at all.
            assert command == MIRROR_SYNC_COMMAND, surface
        else:
            raise AssertionError(f"a command was paired with a surface it cannot produce: {surface}")

    # And exactly one surface replaces a probe payload, because exactly one probe is pinned by a
    # live caller. The count is derived from the live callers rather than written down: see
    # `test_every_surface_named_is_one_a_live_caller_of_this_message_may_edit`.
    keepers = [s for s, command in UPDATE_SURFACES if command and "keeping `_provenance`" in s]
    assert keepers == [s for s, _ in UPDATE_SURFACES if s.endswith("keeping `_provenance`")]
    assert all(FLOOR_PROBE in surface for surface in keepers), keepers


def test_every_surface_named_is_one_a_live_caller_of_this_message_may_edit() -> None:
    """The pin #624 needed and did not have: the surfaces, checked against the CALLERS.

    Every other pin in this file is an existence predicate, and existence cannot see supersession.
    When #596 replaced the mutable marker pin with an immutable dated snapshot, the marker probe
    stopped being something any reader of this message re-records — but it kept existing, kept its
    `_provenance`, and kept every key the instructions named, so nothing here reddened while three
    of nine entries told a floor-drift reader to rewrite a frozen historical artifact.

    So the legitimate set is DERIVED from the call sites instead of maintained by hand: a probe
    belongs in the surface list only if some live `probe_drift_message(...)` call actually pins
    it. This file is excluded from the scan on purpose — the sole live reader of the superseded
    probe had become the test validating the message that named it, and a guard that counts itself
    as a caller reproduces exactly that circularity.
    """
    import tests.probe_drift_support as support

    live_probes: set[str] = set()
    call_sites: list[str] = []
    for source in sorted((ROOT / "tests").rglob("*.py")):
        if source == Path(__file__).resolve():
            continue
        text = source.read_text(encoding="utf-8")
        for name in CALL_SITE_RE.findall(text):
            call_sites.append(f"{source.relative_to(ROOT)}:{name}")
            live_probes.add(getattr(support, name))

    assert call_sites, (
        "no live call site passes a probe to `probe_drift_message`; a message helper nobody "
        "calls is the defect this module exists to catch, and every surface it names is dead"
    )
    assert SUPERSEDED_MARKER_PROBE not in live_probes, (
        "a call site pins the superseded marker probe again; #596 replaced it with the immutable "
        f"snapshot {MARKER_SNAPSHOT}, and the constant's name records that"
    )

    probe_re = re.compile(r"charness-artifacts/probe/[\w.-]+\.json")
    for surface, _ in (*UPDATE_SURFACES, *RULE_ONLY_SURFACES):
        target = surface.split(" — ")[0]
        for named in probe_re.findall(target):
            assert named in live_probes, (
                f"the message tells a reader to edit {named}, which no live caller pins "
                f"(live callers: {sorted(call_sites)}). That is #624: a surface list outliving "
                "the callers it was written for"
            )


def test_no_surface_the_decision_record_calls_immutable_is_offered_as_an_edit_target() -> None:
    """The second half of #624, and the substitution a reader makes when told 'figures moved'.

    The superseded probe is caught by the caller pin above; the dated snapshot that REPLACED it
    cannot be, because a reader who regenerates it is not following a stale entry — they are
    doing what "D47's figures moved" sounds like it asks for. `docs/deferred-decisions.md` is the
    source of truth for that refusal ("it must not overwrite or recompute this immutable
    snapshot"), so the forbidden set is read out of the decision record rather than transcribed
    here, where it would go stale the same way the surface list did.
    """
    decision_text = (ROOT / DECISION_RECORD).read_text(encoding="utf-8")
    immutable: set[str] = set()
    for bullet in re.split(r"\n(?=- |\*\*)", decision_text):
        if "immutable" not in bullet and "must not overwrite" not in bullet:
            continue
        immutable.update(re.findall(r"charness-artifacts/probe/[\w.-]+\.json", bullet))

    assert MARKER_SNAPSHOT in immutable, (
        "the decision record stopped declaring the dated snapshot immutable, or stopped naming "
        "it by path; re-derive this pin before trusting it, because an empty forbidden set "
        "passes silently"
    )
    offered = {
        surface.split(" — ")[0] for surface, _ in (*UPDATE_SURFACES, *RULE_ONLY_SURFACES)
    }
    assert not (offered & immutable), sorted(offered & immutable)
    # And the message must say so out loud rather than merely omitting it, because omission is
    # what a reader acting on memory overrides.
    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert {surface.split(" — ")[0] for surface in DO_NOT_TOUCH_SURFACES} >= immutable, (
        "an artifact the decision record declares immutable is neither listed as an edit target "
        "nor named as one to leave alone; silence is not a warning"
    )
    assert "must NOT overwrite or recompute" in message


def test_each_command_carries_the_flags_that_make_it_the_command_it_is_paired_with() -> None:
    """The pairing test compares CONSTANT to CONSTANT, so it cannot see a swap of their contents.

    The resolution critique constructed it on the two marker commands, which #624 retired with the
    marker probe: move a flag from one constant to the other and every pairing assertion stays
    green, because the pairing check asks `command == THE_CONSTANT` and the existence check only
    splits out the script name — the same file for both invocations. The same construction still
    works on the pair that remains, since `FLOOR_COMMAND` and `FLOOR_COUNTERFACTUAL_COMMAND` run
    one script and differ only by `--floor 20`, and that swap is the worse one: it pins a
    threshold the gate does not use. Identity is not enough; the FLAGS distinguish them.
    """
    # `--floor` selects a COUNTERFACTUAL measurement. Recording one as the probe would pin a
    # threshold the gate does not use, which is a rule change wearing a corpus change's clothes.
    assert "--floor" not in FLOOR_COMMAND, (
        "the floor probe's own command grew a `--floor` override; the probe records the DEFAULT"
    )
    assert "--floor 20" in FLOOR_COUNTERFACTUAL_COMMAND
    assert FLOOR_COMMAND.split()[1] == FLOOR_COUNTERFACTUAL_COMMAND.split()[1] == (
        FLOOR_MEASURE_SCRIPT
    ), "the two floor invocations no longer run the script the rule causes tell a reader to diff"
    # And both must remain the same measured-payload shape: this repo, no probe write.
    #
    # This used to assert `"--json" in command`. That flag was retired repo-wide on
    # 2026-08-14, so the assertion had inverted into a guarantee that the recorded
    # operator command stays BROKEN: green here, `unrecognized arguments: --json` and
    # exit 2 for anyone who actually ran it. The replacement asserts the property that
    # was meant all along — the command runs — instead of pinning one spelling of it.
    for command in (FLOOR_COMMAND, FLOOR_COUNTERFACTUAL_COMMAND):
        assert "--json" not in command, command
        assert "--repo-root ." in command, command


@pytest.mark.slow_corpus
def test_the_recorded_floor_commands_actually_run() -> None:
    """EXECUTE them. Every other pin in this file is an existence predicate.

    That is precisely how the `--json` defect survived: the constants named a real
    script, with a real `--repo-root .`, and a `--json` the script had stopped
    accepting -- so every spelling assertion stayed green while an operator running
    the recorded command got `unrecognized arguments: --json` and exit 2. A command
    is only a reproduce-instruction if it reproduces; the file's own docstring says
    existence pins cannot see supersession, and this is the cheapest thing that can.

    Argparse rejection is exit 2. A non-zero exit is otherwise allowed: the
    counterfactual exits non-zero BY DESIGN at this floor, because everything it
    reports is a refusal.
    """
    for command in (FLOOR_COMMAND, FLOOR_COUNTERFACTUAL_COMMAND):
        result = subprocess.run(
            [sys.executable, *shlex.split(command)[1:]],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 2, f"{command}\n{result.stderr}"
        assert "unrecognized arguments" not in result.stderr, f"{command}\n{result.stderr}"
        assert yaml.safe_load(result.stdout), f"{command} emitted no parseable payload"


def test_every_file_a_rule_cause_names_is_a_path_the_reader_is_told_to_diff() -> None:
    """The discrimination list can be gutted while the rule causes still point at the gutted file.

    Only `GATE_MODULE` and the corpus directory were pinned as members, so deleting
    `scripts/measure_inventory_marker_rule.py` from `DISCRIMINATION_PATHS` left every assertion
    green — while the rule-cause list kept naming a marker predicate in that very file. A reader
    would diff what the message listed, see nothing, and re-record a rule regression: version 2's
    failure, reachable again through the list rather than through the prose.
    """
    # Round 2 refuted the first version of this parse: it required a `/` and an extension in
    # {py, json}, so a bare filename, a `.md`/`.yaml` threshold home, a markdown link, or a
    # trailing `:`/`)` all made a cause INVISIBLE to the pin, which then reported green over a
    # cause it never checked. A guard's POPULATION is a verdict surface too, so the population is
    # asserted here rather than inferred: every rule cause must name at least one file, and the
    # total is pinned so a cause cannot go silently unmeasured.
    path_re = re.compile(r"[\w./-]+\.[A-Za-z]{1,6}")
    per_cause = [
        {token.rstrip(".,;:)") for token in path_re.findall(cause.replace("`", " "))}
        for cause in RULE_CAUSES
    ]
    for cause, named in zip(RULE_CAUSES, per_cause):
        assert named, (
            "a rule cause names no file at all, so a reader cannot diff it and this pin cannot "
            f"measure it: {cause}"
        )
    named_files = {name for names in per_cause for name in names}
    assert len(per_cause) == len(RULE_CAUSES) == 4, (
        "the rule-cause list changed size; re-derive what each new cause names before widening "
        "this pin, because an unmeasured cause reads exactly like a measured one"
    )
    missing = sorted(name for name in named_files if name not in DISCRIMINATION_PATHS)
    assert not missing, (
        f"a rule cause names {missing}, but the message does not tell the reader to diff it — "
        "so the cause is unfalsifiable at the point the reader needs it"
    )


def test_the_message_names_the_prose_fields_that_hide_corpus_counts() -> None:
    """The surface list claimed `current_corpus` was THE prose field. Three other keys carry one.

    The marker probe's `current_corpus` was the original subject here, and it left with the probe
    in #624. What survives is the correction that mattered: a `_provenance` block hides figures in
    ordinary prose keys, so the list names them individually rather than as a category.
    """
    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert "`_provenance` prose keys" in message
    # #624, one key deeper than the issue reported: `does_not_license` sends readers to the
    # superseded marker probe to "read the marker counts there". The message tells the next
    # re-recorder to repoint it, so the pin fails once that has actually happened rather than
    # keeping a stale instruction alive forever.
    floor_provenance_keys = json.loads((ROOT / FLOOR_PROBE).read_text(encoding="utf-8"))
    if SUPERSEDED_MARKER_PROBE in floor_provenance_keys["_provenance"].get("does_not_license", ""):
        assert "check `does_not_license`" in message, (
            "the floor probe's `does_not_license` still points at the superseded marker probe, "
            "but the message no longer tells the re-recorder to repoint it"
        )
    else:
        assert "check `does_not_license`" not in message, (
            "`does_not_license` was repointed; drop the repoint instruction rather than leaving "
            "the reader looking for a defect that is fixed"
        )

    # Round 2's blocker: the first repair claimed the floor probe's `_provenance` was figure-free.
    # Three of its keys quote counts. Assert the CORRECTED claim over EVERY key, so the next
    # reword cannot re-narrow it to the one key that happens to be checked.
    floor_provenance = json.loads((ROOT / FLOOR_PROBE).read_text(encoding="utf-8"))["_provenance"]
    quoting = sorted(
        key
        for key, value in floor_provenance.items()
        if isinstance(value, str) and any(char.isdigit() for char in value.replace("2026", ""))
    )
    assert "counterfactual_floor_20" in quoting and len(quoting) >= 3, (
        f"the floor probe's `_provenance` quotes figures in {quoting}; the message must not "
        "describe it as figure-free"
    )
    assert "do NOT read that as a figure-free block" in message
    assert "NOT transcribed here" in floor_provenance["why"], (
        "the floor probe's `why` stopped scoping its no-transcription claim to the headline "
        "figures; the message explains that scope to the reader"
    )


def test_the_counterfactual_floor_surface_carries_its_own_rerun_command() -> None:
    """A second measurement, transcribed in two places, with no command to regenerate it.

    `_provenance.counterfactual_floor_20` and the gate module's floor rationale both quote the
    same pair, and both move with the corpus. The bookkeeping item named only `date`,
    `repo_head_at_run`, `worktree` and the `synchronized_*` prose, so a literal follow left both
    stale — "one surface citing a figure no other surface reports", which is the sentence the
    message uses to justify its own list.
    """
    floor_provenance = json.loads((ROOT / FLOOR_PROBE).read_text(encoding="utf-8"))["_provenance"]
    assert "counterfactual_floor_20" in floor_provenance
    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert "_provenance.counterfactual_floor_20" in message
    assert FLOOR_COUNTERFACTUAL_COMMAND in message
    assert "exits NON-ZERO" in message, (
        "the counterfactual command exits 1 by design; a reader who reads that as a broken "
        "command will not re-run it"
    )
    # Round 2's blocker: this surface was first paired as `run:`, and the pairing contract at the
    # top of the module says a paired command's OUTPUT REPLACES the surface. The `--floor 20`
    # payload has the probe's exact key shape with `floor` set to 20, so a literal follow pins a
    # threshold the gate does not use. It must be an unpaired, rewrite-by-hand surface that names
    # the command as something to READ.
    counterfactual = [
        (surface, command)
        for surface, command in UPDATE_SURFACES
        if surface.startswith(f"{FLOOR_PROBE} `_provenance.counterfactual_floor_20`")
    ]
    assert len(counterfactual) == 1, counterfactual
    surface, command = counterfactual[0]
    assert command is None, (
        "the counterfactual surface is paired as a paste target again; its payload is a complete "
        "floor-probe payload measured at the WRONG floor"
    )
    assert "Do NOT paste that payload" in surface
    assert "REWRITE THE SENTENCE by hand" in surface
    # The gate module carries the same pair, so the message must not imply the probe is its
    # only home, and must say the label minimum is transcribed more than once.
    assert "TWICE" in message
    # Round 2 also found a NINTH surface: the exported mirror of the gate module carries the same
    # transcribed numbers. It is generated, so it is named with its sync command rather than as a
    # hand edit, and it must actually exist and actually carry the figure.
    assert GATE_MIRROR in message
    assert MIRROR_SYNC_COMMAND in message
    mirror = ROOT / GATE_MIRROR
    assert mirror.is_file(), f"the message names a mirror that does not exist: {GATE_MIRROR}"
    assert "at floor 20" in mirror.read_text(encoding="utf-8"), (
        "the mirror stopped carrying the counterfactual figures; if the export narrowed, drop "
        "it from the surface list rather than leaving a surface a reader cannot verify"
    )
    # And the second transcription's location must be named correctly: round 2 caught it pointing
    # at `residual_chars`, whose docstring carries no figure at all.
    assert "_labelled_line_engages" in message
    assert "NOT in `residual_chars`" in message


def test_the_cause_lists_are_not_swapped() -> None:
    """The other inversion: the classification itself, not its vocabulary.

    Every earlier assertion here was a substring test over the whole message, so swapping the
    corpus and rule lists left them all green while telling the reader to re-record on a rule
    change — the exact harm round 1 caught in the unhedged version.
    """
    corpus = "\n".join(CORPUS_CAUSES)
    rules = "\n".join(RULE_CAUSES)
    non_causes = "\n".join(NOT_CAUSES)

    # A corpus cause is about the measured artifacts; a rule cause is about the measuring code.
    assert "charness-artifacts/quality/" in corpus
    assert GATE_MODULE not in corpus, "a rule cause leaked into the corpus list"
    assert "inventory-consumer-fields.json" not in corpus

    assert GATE_MODULE in rules
    assert "MIN_ENGAGEMENT_RESIDUAL_CHARS" in rules
    assert "inventory-consumer-fields.json" in rules
    assert "REWRITTEN" not in rules, "a corpus cause leaked into the rule list"

    # A third list now, and it is the one a swap would hurt most: a NON-cause promoted into
    # either live list hands the reader a remedy for something that cannot have happened. Both
    # entries here were live once — `quality/history/` for the recursive pin #596 retired, and
    # the marker script for the probe #624 removed — so the drift is toward re-promotion.
    assert "quality/history/" in non_causes
    assert "measure_inventory_marker_rule.py" in non_causes
    assert "quality/history/" not in corpus and "quality/history/" not in rules
    assert "measure_inventory_marker_rule.py" not in rules, (
        "the marker measure script is back in the rule causes; nothing in it feeds this probe, "
        "so diffing it can only produce a false all-clear"
    )

    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    # And the message must place them under the right headings, in order.
    corpus_at = message.index("If the CORPUS changed, re-record")
    rules_at = message.index("If the RULE changed, do NOT re-record yet")
    non_causes_at = message.index("do NOT move these numbers")
    first_corpus_cause = message.index(CORPUS_CAUSES[0])
    first_rule_cause = message.index(RULE_CAUSES[0])
    first_non_cause = message.index(NOT_CAUSES[0])
    assert corpus_at < first_corpus_cause < rules_at < first_rule_cause
    assert first_rule_cause < non_causes_at < first_non_cause


def test_the_discrimination_paths_include_the_module_the_thresholds_actually_live_in() -> None:
    """Version 2 said to diff "the measuring scripts"; three of four thresholds are not there.

    A reader following that saw no diff, concluded the corpus had changed, and would have
    re-recorded a rule regression. The paths are now named as files.
    """
    assert GATE_MODULE in DISCRIMINATION_PATHS
    assert "charness-artifacts/quality/" in DISCRIMINATION_PATHS
    # And the corpus resolver, which is the same lesson one level down: it decides which files
    # are scanned at all, so a change there moves every number here while both the gate and the
    # measure script diff clean.
    assert CORPUS_LIB in DISCRIMINATION_PATHS
    for path in DISCRIMINATION_PATHS:
        target = ROOT / path
        assert target.exists(), f"the drift message tells a reader to diff a missing path: {path}"

    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert "the thresholds are NOT in the measure" in message


def test_the_message_does_not_claim_a_field_the_floor_probe_lacks() -> None:
    """Version 2 said BOTH probes have `_provenance.current_corpus`. Only the marker one does.

    The pin that was supposed to cover this checked the marker probe only, so it was scoped
    around the false claim instead of catching it.
    """
    floor_provenance = json.loads((ROOT / FLOOR_PROBE).read_text(encoding="utf-8"))["_provenance"]
    assert "current_corpus" not in floor_provenance, (
        "the floor probe grew a `current_corpus` field; the message now says it has none"
    )
    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert "NO `current_corpus` summary key" in message


def test_the_decision_record_is_named_only_for_the_coupling_it_actually_has() -> None:
    """#624's inversion: D47 was listed unconditionally, and its own text says the opposite.

    D47's live figures come from the hash-bound immutable 2026-08-12 snapshot, and the entry says
    "unrelated quality-corpus growth does not rewrite D47 or regenerate its evidence". So a
    corpus-only drift — the common case, and the one the reporter hit — owes D47 nothing, while
    the message said it "still needs a D47 edit whenever a figure it quotes moved".

    Deleting the entry would have been the other wrong answer: there IS one residual coupling.
    D47's question transcribes the floor itself, which is the constant this probe pins. That
    coupling is asserted here on both sides rather than described, so it cannot rot into the
    unconditional claim it replaced: if the constant moves without D47's sentence, this reddens.
    """
    decision_text = (ROOT / DECISION_RECORD).read_text(encoding="utf-8")
    gate_text = (ROOT / GATE_MODULE).read_text(encoding="utf-8")

    gate_floor = re.search(r"MIN_ENGAGEMENT_RESIDUAL_CHARS = (\d+)", gate_text)
    d47_floor = re.search(r"carry ≥(\d+) alphanumerics", decision_text)
    assert gate_floor is not None and d47_floor is not None, (
        "the floor is no longer transcribed in both places; re-derive the rule-only D47 surface "
        "before trusting it, because a missing side makes this pin vacuous"
    )
    assert gate_floor.group(1) == d47_floor.group(1), (
        f"the gate enforces a floor of {gate_floor.group(1)} while D47's question describes "
        f"{d47_floor.group(1)}; that is the rule-only edit the drift message names"
    )

    # Version 2's other false claim, kept because it is still true and now supports the OPPOSITE
    # conclusion: D47 does not name this probe or its fields, so nothing in the entry tracks a
    # corpus drift here.
    assert "field_mention_residuals" not in decision_text, (
        "D47 now names the field; the message's `does NOT name this probe` line is stale"
    )
    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert "does NOT name this probe" in message
    # And the conditionality has to survive in the render, not only in the constant.
    assert "ONLY when the FLOOR RULE moved" in message
    rule_only_at = message.index("ONLY if the RULE moved, one further surface carries it")
    assert message.index("To re-record, update ALL of these") < rule_only_at < message.index(
        f"{DECISION_RECORD} D47"
    ), "D47 moved back into the unconditional re-record list; that is what #624 filed"


def test_the_decision_record_still_declares_itself_immune_to_corpus_growth() -> None:
    """The premise the rule-only narrowing rests on, read from the source of truth.

    If D47 ever starts tracking the live corpus again, the narrowing above becomes the new defect:
    a corpus drift would owe it an edit and the message would say it owes nothing. So the premise
    is pinned where it is stated rather than assumed from the issue report.
    """
    decision_text = (ROOT / DECISION_RECORD).read_text(encoding="utf-8")

    # Whitespace-normalized: both sentences wrap in the record, and asserting the raw line breaks
    # would pin the reflow rather than the claim.
    flat = " ".join(decision_text.split())
    assert "unrelated quality-corpus growth does not rewrite D47" in flat, (
        "D47 no longer declares itself immune to corpus growth; the drift message's rule-only "
        "narrowing of the D47 surface depends on that sentence"
    )
    assert "must not overwrite or recompute this immutable snapshot" in flat



# --- The third probe site's message (#561) ---------------------------------------------------
#
# Same lazy-evaluation problem as the two above: nothing green calls it. These pin the claims it
# makes, and specifically the ones it must NOT inherit from `probe_drift_message`.


def test_the_residual_message_is_not_the_inventory_message() -> None:
    """The residual site's remedy is the OPPOSITE of the other two sites'.

    Reusing `probe_drift_message` here would have told a reader to re-record an unrelated probe
    and edit D47 — neither of which carries a residual figure. That is exactly the "version 2 was
    worse than the bare number it replaced" failure this module was written to record, so the
    separation is asserted rather than left to a reviewer's memory.
    """
    message = residual_floor_message("min_residual", kind="markdown_artifacts")

    assert SUPERSEDED_MARKER_PROBE not in message
    assert MARKER_SNAPSHOT not in message
    assert FLOOR_PROBE not in message
    assert DECISION_RECORD not in message
    assert RESIDUAL_PROBE in message
    # The load-bearing inversion: a break here is usually a FINDING, not a re-record.
    assert "not the usual re-record" in message
    assert "THE INVARIANT BROKE" in message
    assert "Do NOT lower the floor" in message


def test_the_residual_message_names_where_the_floor_constant_actually_lives() -> None:
    """The mistake the inventory message already made once, checked against the source.

    Version 2 of the inventory message sent readers to diff the measure scripts when the
    thresholds lived in the gate. The residual floor has the same shape: `measure_evidence_residual.py`
    reads `MIN_BOUND_RESIDUAL_CHARS` from another module, so diffing the measure script finds
    nothing.
    """
    home = ROOT / RESIDUAL_FLOOR_HOME
    assert f"{RESIDUAL_FLOOR_SYMBOL} = " in home.read_text(encoding="utf-8"), (
        "the residual floor constant moved; the message still sends readers to this file"
    )
    measure = (ROOT / RESIDUAL_MEASURE_SCRIPT).read_text(encoding="utf-8")
    assert f"{RESIDUAL_FLOOR_SYMBOL} = " not in measure, (
        "the measure script now defines the floor itself; the message says it does not"
    )
    message = residual_floor_message("floor")
    assert RESIDUAL_FLOOR_HOME in message
    assert RESIDUAL_COMMAND in message
    # DIRECTIONAL, not presence. Both filenames appear in the same sentence, so swapping them
    # leaves every substring check green while sending the reader to diff the wrong file — the
    # version-2 harm, reachable through the pin written to prevent it. The sibling inventory
    # suite learned this twice; asserting order is what closes it.
    assert message.index(RESIDUAL_FLOOR_HOME) < message.index("NOT in"), (
        "the message now names the measure script as the constant's home; the two files are "
        "swapped and the reader is sent to diff the one that does not define it"
    )
    assert message.index("NOT in") < message.index(f"`{RESIDUAL_MEASURE_SCRIPT}`")


def test_the_residual_probe_really_has_no_provenance_block() -> None:
    """An exclusive claim about the file, made by opening it rather than by assuming.

    The message tells the reader to replace the WHOLE file — safe only because this probe,
    unlike its two siblings, carries no `_provenance`. If one is ever added, that instruction
    destroys it.

    The instruction used to be a straight redirect of stdout, and this test pinned the words
    "stdout IS the file". The 2026-08-14 `--json` removal made command output YAML while this
    stored artifact stayed JSON, so a straight redirect would now write YAML into a file its
    only reader parses with `json.loads`. The whole-file claim survives; the redirect does not,
    and the pin moved with it.
    """
    payload = json.loads((ROOT / RESIDUAL_PROBE).read_text(encoding="utf-8"))

    assert "_provenance" not in payload
    # Asserted on unwrapped fragments: the full sentences span line breaks in the render,
    # which is how the sibling assertions above already handle wrapped claims.
    assert "the whole file" in residual_floor_message("floor")
    assert "NO `_provenance`" in residual_floor_message("floor")
    assert "straight redirect" in residual_floor_message("floor")
    # Every per-kind key the message names must exist. The first draft said `kinds[*].count`,
    # a key from the INVENTORY floor probe that this probe does not have — an assertion about a
    # file's contents made without opening it, which is the version-2 class exactly.
    kind_keys = set()
    for kind_payload in payload["kinds"].values():
        kind_keys.update(kind_payload)
    message = residual_floor_message("min_residual", kind="markdown_artifacts")
    for named in re.findall(r"`kinds\[\*\]\.(\w+)`", message):
        assert named in kind_keys, (
            f"the message names `kinds[*].{named}`, which the probe does not have; its keys are "
            f"{sorted(kind_keys)}"
        )
    assert "`kinds[*].files`" in message


def test_the_residual_site_actually_calls_the_message() -> None:
    """A message helper nobody calls is the defect this module exists to catch.

    `assert expr, msg` never evaluates `msg` while the suite is green, so an unwired helper looks
    identical to a wired one from the outside.
    """
    site = (ROOT / "tests" / "quality_gates" / "test_measure_evidence_residual.py").read_text(
        encoding="utf-8"
    )

    assert "residual_floor_message" in site
    assert site.count("residual_floor_message(") >= 5, (
        "a residual assertion lost its drift message; the bare `, kind` form is what #561 filed"
    )
    # The exit-code assertion specifically. It is the one a stub artifact actually reaches, and
    # leaving it bare made every message below it unreachable on the real failure path.
    assert "assert code == 0, residual_floor_message(" in site, (
        "the exit-code assertion lost its message; the script exits 1 exactly when the invariant "
        "breaks, so this is the assertion #561's reported failure mode hits first"
    )
    # And the message must not point at a kind when none was named.
    assert "for each kind" in residual_floor_message("exit_code")
    assert "for the kind `markdown_artifacts`" in residual_floor_message(
        "min_residual", kind="markdown_artifacts"
    )


def test_every_residual_surface_exists_and_carries_the_figures_it_is_named_for() -> None:
    """The `UPDATE_SURFACES` lesson, applied to the residual list rather than re-learned.

    The first draft listed ONE surface. The recorded figures are transcribed in the gate's own
    floor rationale, in that file's generated mirror, in an operator-facing contract doc, and in
    a sibling test's comment. Re-recording only the probe leaves the gate defending its floor
    with a number no probe reports — the sentence the inventory message uses to justify its own
    list — and the mirror half additionally blocks the commit on a drift gate.
    """
    probe = json.loads((ROOT / RESIDUAL_PROBE).read_text(encoding="utf-8"))
    figures = {str(kind["min_residual"]) for kind in probe["kinds"].values()}

    listed = {surface.split(" — ")[0] for surface, _ in RESIDUAL_UPDATE_SURFACES}
    for path in (
        RESIDUAL_PROBE,
        RESIDUAL_FLOOR_HOME,
        RESIDUAL_FLOOR_MIRROR,
        RESIDUAL_CONTRACT_DOC,
    ):
        assert path in listed, f"the residual re-record list dropped {path}"
        assert (ROOT / path).is_file(), f"the residual message names a missing surface: {path}"

    # Not just listed — each transcribing surface must actually still carry a recorded figure,
    # or it has stopped being a surface and the list is stale in the other direction.
    for path in (RESIDUAL_FLOOR_HOME, RESIDUAL_FLOOR_MIRROR, RESIDUAL_CONTRACT_DOC):
        text = (ROOT / path).read_text(encoding="utf-8")
        assert any(figure in text for figure in figures), (
            f"{path} no longer quotes any recorded residual figure; the message still sends a "
            "re-recording reader there"
        )

    # The generated mirror is the one surface with a REGENERATE command rather than a hand edit.
    paired = dict(RESIDUAL_UPDATE_SURFACES)
    mirror = next(s for s in paired if s.startswith(RESIDUAL_FLOOR_MIRROR))
    assert paired[mirror] == MIRROR_SYNC_COMMAND


def test_the_recorded_only_branch_does_not_send_the_reader_to_the_live_tree() -> None:
    """One assertion compares the probe to ITSELF, and the drift text is false for it.

    Both operands come from the checked-in file, so "no longer matches the recorded measurement"
    misnames the failure and both numbered cases point at a live tree that is healthy. The
    separate branch says what actually happened: the probe is internally inconsistent.
    """
    message = residual_floor_message("min_residual", kind="markdown_artifacts", recorded_only=True)

    assert "inconsistent WITHIN the recorded probe" in message
    assert "Nothing live took" in message
    assert "no longer matches the recorded measurement" not in message
    # And it must NOT tell the reader to go read a live path, which is case 1's remedy.
    assert "min_residual_path" not in message
    # The two branches must not render identically, or the reader cannot tell which fired.
    assert message != residual_floor_message("min_residual", kind="markdown_artifacts")
