"""The drift message is only read when a probe drifts, so nothing green exercises it.

#536's repair is a message. `assert expr, msg` evaluates `msg` lazily, so in a passing suite
`probe_drift_message` is called ZERO times — a bounded round pointed out that deleting the
cause paragraph, the update list, or the commands would be a silent green edit, and that the
mutants proving those parts reach the reader had been killed by hand rather than by anything
checked in. `tests/` is also outside the mutation pool, so no gate covers it either.

These pin the claims the message makes, and the paths and commands it names. They do not judge
whether the prose reads well — they fail if it stops saying the load-bearing things, or if it
names a script or a probe that does not exist.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from tests.probe_drift_support import (
    CORPUS_CAUSES,
    DECISION_RECORD,
    DISCRIMINATION_PATHS,
    FLOOR_COMMAND,
    FLOOR_COUNTERFACTUAL_COMMAND,
    FLOOR_PROBE,
    GATE_MIRROR,
    GATE_MODULE,
    MARKER_COMMAND,
    MARKER_PROBE,
    MARKER_RECURSIVE_COMMAND,
    MIRROR_SYNC_COMMAND,
    RESIDUAL_COMMAND,
    RESIDUAL_CONTRACT_DOC,
    RESIDUAL_FLOOR_HOME,
    RESIDUAL_FLOOR_MIRROR,
    RESIDUAL_FLOOR_SYMBOL,
    RESIDUAL_MEASURE_SCRIPT,
    RESIDUAL_PROBE,
    RESIDUAL_TIMEBOX_TEST,
    RESIDUAL_UPDATE_SURFACES,
    RULE_CAUSES,
    UPDATE_SURFACES,
    probe_drift_message,
    residual_floor_message,
)

ROOT = Path(__file__).resolve().parent.parent


def test_the_message_separates_a_corpus_cause_from_a_rule_cause() -> None:
    """The correction that mattered most: the two causes have OPPOSITE remedies.

    A first version said flatly "the fix is to re-record, not to undo the write". That is wrong
    whenever the measurement rule moved rather than the corpus, and following it would launder a
    rule regression into the pinned probe and into the decision record.
    """
    message = probe_drift_message("artifacts_scanned", probe=MARKER_PROBE)

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
    assert "history/" in message


def test_the_message_names_every_surface_that_carries_the_same_numbers() -> None:
    """Five surfaces, not three. The probes themselves refuted the smaller claim."""
    message = probe_drift_message("floor", probe=FLOOR_PROBE)

    assert MARKER_PROBE in message
    assert FLOOR_PROBE in message
    assert DECISION_RECORD in message
    assert "_provenance.recursive_variant" in message
    assert "nests HERE, not at top level" in message
    assert "_provenance.current_corpus" in message
    assert "_provenance` bookkeeping" in message
    assert "quotes the counts in prose" in message


def test_the_message_does_not_tell_a_reader_to_overwrite_provenance() -> None:
    """The first version's actual defect: it would have deleted `_provenance`.

    `--json` emits only the measured payload. Pasting that over a probe file destroys
    `_provenance`, and the next run then fails with a bare `KeyError: '_provenance'` — the
    diagnostic class #536 exists to remove, reintroduced by the fix for #536.
    """
    message = probe_drift_message("artifacts_scanned", probe=MARKER_PROBE)

    # COUNT, not presence: both probe payload lines must carry it. A mutation that dropped the
    # instruction from ONE of them survived a presence check, which would leave a reader
    # correctly told to keep `_provenance` for one probe and silently told to destroy it for the
    # other — the worse half of the bug this replaced.
    assert message.count("keeping `_provenance`") == 2, message
    assert "neither emits `_provenance`" in message
    assert "no output can be pasted over a probe file wholesale" in message
    # And the nesting warning, which is the specific step whose omission produced a bare
    # `KeyError: '_provenance'` on the next run.
    assert "nests HERE, not at top level" in message


def test_every_path_and_command_the_message_names_actually_exists() -> None:
    """A message that names a wrong path is worse than the bare number it replaced."""
    for probe in (MARKER_PROBE, FLOOR_PROBE):
        path = ROOT / probe
        assert path.is_file(), f"the drift message names a probe that does not exist: {probe}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert "_provenance" in payload, (
            f"{probe} has no `_provenance`; the message's keep-provenance instruction is stale"
        )
    assert (ROOT / DECISION_RECORD).is_file()

    marker_provenance = json.loads((ROOT / MARKER_PROBE).read_text(encoding="utf-8"))["_provenance"]
    assert "recursive_variant" in marker_provenance, (
        "the message says the recursive payload nests under `_provenance.recursive_variant`"
    )
    assert "current_corpus" in marker_provenance, (
        "the message says `_provenance.current_corpus` quotes the counts in prose"
    )

    for command in (MARKER_COMMAND, MARKER_RECURSIVE_COMMAND, FLOOR_COMMAND):
        script = command.split()[1]
        assert (ROOT / script).is_file(), f"the drift message names a missing script: {script}"


def test_the_message_distinguishes_the_recursive_variant_in_its_own_heading() -> None:
    """The site whose failure is about the nested payload must say which payload it means."""
    plain = probe_drift_message("rows", probe=MARKER_PROBE)
    recursive = probe_drift_message("rows", probe=MARKER_PROBE, variant="recursive variant")

    assert "(recursive variant)" in recursive
    assert "(recursive variant)" not in plain


def test_each_surface_is_paired_with_the_command_that_actually_produces_it() -> None:
    """The inversion a substring pin could not see.

    A round showed that swapping `MARKER_COMMAND` and `FLOOR_COMMAND` in the surface list left
    every assertion in this file green while instructing the reader to paste floor output over
    the marker payload — strictly worse than the bare number the message replaced. So the
    pairing is asserted, not just the presence of both strings.
    """
    pairs = {surface: command for surface, command in UPDATE_SURFACES}
    for surface, command in pairs.items():
        if command is None:
            continue
        if MARKER_PROBE in surface and "recursive_variant" in surface:
            assert command == MARKER_RECURSIVE_COMMAND, surface
        elif MARKER_PROBE in surface:
            assert command == MARKER_COMMAND, surface
        elif FLOOR_PROBE in surface:
            assert command == FLOOR_COMMAND, surface
        elif GATE_MIRROR in surface:
            # Generated, so it gets a REGENERATE command rather than a paste target. It is the
            # one paired surface whose command does not print a payload at all.
            assert command == MIRROR_SYNC_COMMAND, surface
        else:
            raise AssertionError(f"a command was paired with a surface it cannot produce: {surface}")

    # And every payload-replacing surface must say to keep `_provenance` — one per probe, so a
    # duplicated marker line cannot satisfy the count on its own.
    keepers = [surface for surface, command in UPDATE_SURFACES if command and "keeping `_provenance`" in surface]
    assert len(keepers) == 2, keepers
    assert any(MARKER_PROBE in surface for surface in keepers)
    assert any(FLOOR_PROBE in surface for surface in keepers)


def test_each_command_carries_the_flags_that_make_it_the_command_it_is_paired_with() -> None:
    """The pairing test compares CONSTANT to CONSTANT, so it cannot see a swap of their contents.

    The resolution critique constructed it: move `--recursive` off `MARKER_RECURSIVE_COMMAND` onto
    `MARKER_COMMAND` and every assertion in this file stays green, because the pairing check asks
    `command == MARKER_RECURSIVE_COMMAND` and the existence check only splits out the script name,
    which is the same file for both. The reader is then told to paste recursive output over the
    top-level payload — round 2's exact harm, reproduced through the pin that was written to stop
    it. Identity is not enough; the FLAGS are what distinguish these three invocations.
    """
    assert "--recursive" in MARKER_RECURSIVE_COMMAND
    assert "--recursive" not in MARKER_COMMAND, (
        "the top-level marker command grew `--recursive`; its output belongs in "
        "`_provenance.recursive_variant`, not in the top-level payload"
    )
    # `--floor` selects a COUNTERFACTUAL measurement. Recording one as the probe would pin a
    # threshold the gate does not use, which is a rule change wearing a corpus change's clothes.
    assert "--floor" not in FLOOR_COMMAND, (
        "the floor probe's own command grew a `--floor` override; the probe records the DEFAULT"
    )
    assert "--floor 20" in FLOOR_COUNTERFACTUAL_COMMAND
    # And all three must remain the same measured-payload shape: JSON, this repo, no probe write.
    for command in (MARKER_COMMAND, MARKER_RECURSIVE_COMMAND, FLOOR_COMMAND,
                    FLOOR_COUNTERFACTUAL_COMMAND):
        assert "--json" in command, command
        assert "--repo-root ." in command, command


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
    assert len(per_cause) == len(RULE_CAUSES) == 3, (
        "the rule-cause list changed size; re-derive what each new cause names before widening "
        "this pin, because an unmeasured cause reads exactly like a measured one"
    )
    missing = sorted(name for name in named_files if name not in DISCRIMINATION_PATHS)
    assert not missing, (
        f"a rule cause names {missing}, but the message does not tell the reader to diff it — "
        "so the cause is unfalsifiable at the point the reader needs it"
    )


def test_the_message_names_the_prose_fields_that_hide_corpus_counts() -> None:
    """The surface list claimed `current_corpus` was THE prose field. `why` carries one too.

    Found by the resolution critique: the marker probe's `_provenance.why` ends on the
    presence-only total, so a reader following the list literally refreshes `current_corpus` and
    leaves a stale figure one key away — an exclusive claim about where numbers live, made without
    opening the file, which is the exact class this whole message exists to repair.
    """
    payload = json.loads((ROOT / MARKER_PROBE).read_text(encoding="utf-8"))
    provenance = payload["_provenance"]
    # `any digit` was too weak: a date satisfies it. The CLAIM is that `why` ENDS on the
    # presence-only total, so that is what is asserted.
    total = str(payload["field_mentions_presence_only"])
    assert provenance["why"].rstrip().rstrip(".").endswith(total), (
        "the marker probe's `_provenance.why` no longer ends on the presence-only total; the "
        "message tells the reader that is the figure hiding there"
    )
    message = probe_drift_message("artifacts_scanned", probe=MARKER_PROBE)
    assert "`_provenance.why`" in message

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

    # A corpus cause is about the measured artifacts; a rule cause is about the measuring code.
    assert "charness-artifacts/quality/" in corpus
    assert "quality/history/" in corpus
    assert GATE_MODULE not in corpus, "a rule cause leaked into the corpus list"
    assert "inventory-consumer-fields.json" not in corpus

    assert GATE_MODULE in rules
    assert "MIN_ENGAGEMENT_RESIDUAL_CHARS" in rules
    assert "inventory-consumer-fields.json" in rules
    assert "REWRITTEN" not in rules, "a corpus cause leaked into the rule list"

    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    # And the message must place them under the right headings, in order.
    corpus_at = message.index("If the CORPUS changed, re-record")
    rules_at = message.index("If the RULE changed, do NOT re-record yet")
    first_corpus_cause = message.index(CORPUS_CAUSES[0])
    first_rule_cause = message.index(RULE_CAUSES[0])
    assert corpus_at < first_corpus_cause < rules_at < first_rule_cause


def test_the_discrimination_paths_include_the_module_the_thresholds_actually_live_in() -> None:
    """Version 2 said to diff "the measuring scripts"; three of four thresholds are not there.

    A reader following that saw no diff, concluded the corpus had changed, and would have
    re-recorded a rule regression. The paths are now named as files.
    """
    assert GATE_MODULE in DISCRIMINATION_PATHS
    assert "charness-artifacts/quality/" in DISCRIMINATION_PATHS
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
    assert "The floor probe has NO such field" in message


def test_the_message_does_not_claim_D47_names_the_floor_probe() -> None:
    """Version 2 said D47 cites the floor probe's `field_mention_residuals.count`. It does not.

    The coupling is real but it is asserted by a test, not by D47's text, so a reader who went
    to verify the claim found nothing and could conclude a floor drift needs no D47 edit.
    """
    decision_text = (ROOT / DECISION_RECORD).read_text(encoding="utf-8")
    assert "field_mention_residuals" not in decision_text, (
        "D47 now names the field; the message's `does NOT name the floor probe` line is stale"
    )
    message = probe_drift_message("floor", probe=FLOOR_PROBE)
    assert "does NOT name the floor probe" in message



# --- The third probe site's message (#561) ---------------------------------------------------
#
# Same lazy-evaluation problem as the two above: nothing green calls it. These pin the claims it
# makes, and specifically the ones it must NOT inherit from `probe_drift_message`.


def test_the_residual_message_is_not_the_inventory_message() -> None:
    """The residual site's remedy is the OPPOSITE of the other two sites'.

    Reusing `probe_drift_message` here would have told a reader to re-record the marker and floor
    probes and edit D47 — none of which carry a residual figure. That is exactly the "version 2
    was worse than the bare number it replaced" failure this module was written to record, so the
    separation is asserted rather than left to a reviewer's memory.
    """
    message = residual_floor_message("min_residual", kind="markdown_artifacts")

    assert MARKER_PROBE not in message
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

    The message tells the reader the command's stdout is the WHOLE file — safe only because this
    probe, unlike its two siblings, carries no `_provenance`. If one is ever added, that
    instruction destroys it.
    """
    payload = json.loads((ROOT / RESIDUAL_PROBE).read_text(encoding="utf-8"))

    assert "_provenance" not in payload
    # Asserted on the unwrapped fragment: the full sentence spans a line break in the render,
    # which is how the sibling assertions above already handle wrapped claims.
    assert "stdout IS the file" in residual_floor_message("floor")
    assert "NO `_provenance`" in residual_floor_message("floor")
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
        RESIDUAL_TIMEBOX_TEST,
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
