"""One message for probe drift: what changed, which remedy that implies, and every surface.

#536. Two checked-in probes are pinned against the live tree, and the tree they measure is
`charness-artifacts/quality/` — a directory ordinary quality work writes to on almost every
slice. A markdown write turns three assertions red across two files, and what the reader got
was a drifted number:

    AssertionError: artifacts_scanned drifted from the recorded probe; update D47 and the probe
    together
    assert 132 == 131

That named a coupled pair and stopped. Two bounded rounds then found that the first two
versions of this message were each WORSE than the number they replaced, so every claim below is
now checked against the probe files' actual keys and the actual source locations rather than
against what seemed likely:

- Version 1 said "copy each payload into the probe file". `--json` emits only the measured
  payload; a probe file is `_provenance` PLUS that payload, and the recursive payload nests
  under `_provenance.recursive_variant`. Following it deleted `_provenance` and produced a bare
  `KeyError` next run — the diagnostic class this exists to remove.
- Version 2 told the reader to `git diff` "the measuring scripts" to tell a rule change from a
  corpus change, but three of the four thresholds it named live in
  `scripts/validate_inventory_consumption.py`, not in either measure script. A reader would
  have diffed the wrong files, seen nothing, and re-recorded a rule regression.
- Version 2 also claimed the floor probe has a `_provenance.current_corpus` field (it does
  not), and that D47 cites the floor probe's `field_mention_residuals.count` by name (it does
  not — the coupling is asserted by a test, not by D47's text).

#624 found a FOURTH shape of the same failure, and it is the one none of the pins above could
see: not a false claim about a file, but a true claim that stopped applying to any reader.
#596 replaced the mutable marker pin with the immutable dated snapshot, so this message lost
its only marker-probe caller — all four live call sites now pass `FLOOR_PROBE`. Three of the
nine listed surfaces then told a floor-drift reader to re-record a superseded historical
artifact, and the D47 entry told them to edit a decision record whose own text says ordinary
corpus growth does not rewrite it. Every pin stayed green, because those pins asked only
`path.is_file()` and `key in payload` — and the superseded file still exists with every key
they name. Existence cannot see supersession.

Two rules come out of that, and both are enforced by `tests/test_probe_drift_message.py`:

- A surface list is only correct RELATIVE TO ITS CALLERS, so the callers are pinned too: every
  probe this message names must be a probe some live call site actually passes.
- The correction is a NARROWING, never a deletion. What must not be touched is now said out
  loud (`DO_NOT_TOUCH_SURFACES`) instead of being dropped, and the one genuine residual
  coupling to D47 — the FLOOR ITSELF — moved to `RULE_ONLY_SURFACES` instead of being deleted
  with the rest. A dropped surface re-creates the partial update this whole list exists to
  prevent; an unconditional one sends readers to rewrite a record that declares itself immune.
"""

from __future__ import annotations

FLOOR_PROBE = "charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json"
DECISION_RECORD = "docs/deferred-decisions.md"
# #624. The marker probe this message used to list beside the floor probe, kept as a NAMED
# NON-SURFACE rather than deleted. #596 replaced its mutable equality pin with the immutable
# dated snapshot below, and `docs/deferred-decisions.md` says the old file is where the
# historical diagnosis is PRESERVED — so it is neither re-recorded nor corrected to match
# today's tree. Naming it as a trap is not naming it as an edit target, and a reader who
# remembers the old nine-item list needs to be told the two entries were removed deliberately
# rather than lost.
SUPERSEDED_MARKER_PROBE = "charness-artifacts/probe/2026-08-01-inventory-marker-rule.json"
MARKER_SNAPSHOT = "charness-artifacts/probe/2026-08-12-inventory-marker-rule-snapshot.json"
# Where the thresholds actually live. The measure script imports this module rather than
# defining the rule, so a rule change shows up HERE and not in the measure script.
GATE_MODULE = "scripts/validate_inventory_consumption.py"
# The exported mirror carries the same transcribed numbers, and it is generated rather than
# hand-written — so it is a surface with a COMMAND, not an `edit by hand` entry.
GATE_MIRROR = "plugins/charness/scripts/validate_inventory_consumption.py"
MIRROR_SYNC_COMMAND = "python3 scripts/sync_root_plugin_manifests.py"
CONSUMER_FIELDS = "skills/public/quality/references/inventory-consumer-fields.json"
# The measure script and the corpus resolver it delegates to. Named as constants because both
# are RULE homes for the numbers this message is about: the script owns `LABEL_FLOORS`, and the
# resolver owns which files are scanned at all.
FLOOR_MEASURE_SCRIPT = "scripts/measure_inventory_consumption_floor.py"
CORPUS_LIB = "scripts/inventory_measurement_lib.py"

# The command prints ONLY its measured payload. The script does not write a probe and does not
# emit `_provenance`, so its output cannot be pasted over a probe file wholesale.
FLOOR_COMMAND = "python3 scripts/measure_inventory_consumption_floor.py --repo-root . --json"
# The counterfactual the floor probe and the gate comment BOTH transcribe. It is a different
# invocation, not a different field of the same run, so it has to be re-run separately; it
# exits non-zero by design at this floor, because everything it reports is a refusal.
FLOOR_COUNTERFACTUAL_COMMAND = (
    "python3 scripts/measure_inventory_consumption_floor.py --repo-root . --floor 20 --json"
)

# Surface -> the command whose output replaces it, or None where the edit is by hand. Paired
# explicitly rather than as free prose: a round found that swapping two commands in a prose list
# left every pin green while instructing the reader to paste floor output over the marker
# payload, which is worse than the bare number this replaced.
#
# #624 added the other half: the pairing check skipped every `None` entry, and every surface that
# had gone dead was a `None` entry. An unpaired surface is still a surface, so the pin now asks
# what an unpaired entry NAMES rather than only what a paired one runs.
UPDATE_SURFACES: tuple[tuple[str, str | None], ...] = (
    (
        f"{FLOOR_PROBE} — replace the TOP-LEVEL payload keys, keeping `_provenance`",
        FLOOR_COMMAND,
    ),
    (
        f"{FLOOR_PROBE} `_provenance` bookkeeping — `date`, `repo_head_at_run`, `worktree`, and"
        " `synchronized_after`/`synchronized_reason`, which count the refreshes in prose. Leaving"
        " these is how a re-recorded payload ends up wearing a provenance block that names an"
        " older run, which no reader can falsify",
        None,
    ),
    (
        f"{FLOOR_PROBE} `_provenance` prose keys — this probe has NO `current_corpus` summary"
        " key, but do NOT read that as a figure-free block: `counterfactual_floor_20` still"
        " quotes counts, and it is now the ONLY key that does. `synchronized_after` used to"
        " quote the headline delta and no longer does — it went stale one commit after it was"
        " written, so the 2026-08-14 refresh replaced the numbers with the cause and left the"
        " figures to this file's own measured fields, extending what `why` already promised."
        " Keep it that way: name what changed the corpus, not by how much",
        None,
    ),
    (
        f"{FLOOR_PROBE} `_provenance.counterfactual_floor_20` — a SECOND measurement, not a field"
        " of the run above. It quotes how many citations and label values a floor of 20 would"
        " refuse, both of which move with the corpus. Read the two numbers by running"
        f" `{FLOOR_COUNTERFACTUAL_COMMAND}` and then REWRITE THE SENTENCE by hand. Do NOT paste"
        " that payload anywhere: it has the same key shape as this probe's top-level payload with"
        " `floor` set to 20, so pasting it pins a threshold the gate does not use — a rule change"
        " wearing a corpus change's clothes, which is the one outcome this whole message exists"
        " to prevent. The command also exits NON-ZERO at that floor by design, because"
        " everything it reports is a refusal",
        None,
    ),
    (
        f"{GATE_MODULE} — its comments transcribe the corpus label minimum TWICE (once in the"
        " floor rationale, once in `_labelled_line_engages`'s docstring — NOT in `residual_chars`,"
        " whose docstring carries no figure) and the same counterfactual-floor pair the floor"
        " probe carries. A partial update leaves the gate defending its floor with a number no"
        " probe reports",
        None,
    ),
    (
        f"{GATE_MIRROR} — the exported mirror of the file above, carrying the same transcribed"
        " numbers. It is GENERATED, so do not hand-edit it and do not skip it: regenerate after"
        " editing the owner, or a staged-mirror-drift gate blocks the commit while the mirror"
        " still cites the old figures",
        MIRROR_SYNC_COMMAND,
    ),
)

# #624. D47 was an UNCONDITIONAL entry in the list above, and that is the half of the issue that
# is an inversion rather than a stale pointer. D47's live figures come from the hash-bound
# immutable 2026-08-12 snapshot, and the entry says in its own text that unrelated quality-corpus
# growth does not rewrite it — so a corpus drift moves NOTHING in D47. The ONE figure D47 and
# this probe genuinely share is the FLOOR, transcribed in D47's question and pinned here by
# `live["floor"] == recorded["floor"]`. Deleting the entry outright would have re-created the
# partial update this list exists to prevent, so it moved to a rule-only section instead: a rule
# change owes the edit, a corpus change owes nothing.
RULE_ONLY_SURFACES: tuple[tuple[str, str | None], ...] = (
    (
        f"{DECISION_RECORD} D47 — ONLY when the FLOOR RULE moved. D47's question transcribes the"
        " floor as `≥5 alphanumerics`; that is `MIN_ENGAGEMENT_RESIDUAL_CHARS` in"
        f" {GATE_MODULE} and the `floor` key this probe pins, and it is the only figure the entry"
        " and this probe share. Edit THAT SENTENCE and nothing else. D47 does NOT name this probe"
        " or any of its fields — the coupling is asserted by a test, not by D47's text — and its"
        " headline figures are dated evidence from an immutable snapshot, so do not restate them"
        " against the new rule and do not recompute the snapshot to match it",
        None,
    ),
)

# Surfaces that LOOK like they belong on the list above. Saying so is the repair #624 asked for:
# the two entries were removed because following them was harmful, and a reader who acts on
# memory rather than on this message will re-do exactly what the issue reported.
DO_NOT_TOUCH_SURFACES: tuple[str, ...] = (
    f"{SUPERSEDED_MARKER_PROBE} — this message kept listing it after it stopped being a surface."
    " #596 replaced its mutable equality pin with the immutable dated snapshot, and no"
    " live caller of this message measures it. It still parses and still has every key the old"
    " instructions named, so nothing reds while it sits stale against today's tree — that is HOW"
    " this went unnoticed, not evidence it is fine. Its `_provenance` is where the historical"
    " diagnosis is preserved; re-recording it destroys the evidence the supersession kept.",
    f"{MARKER_SNAPSHOT} — hash-pinned. {DECISION_RECORD} D47 says a new decision must record a"
    " NEW dated snapshot with its own SHA-256 and must NOT overwrite or recompute this one."
    " Regenerating it to match today's corpus breaks its sha256 pin and erases dated evidence in"
    " the same step, and it is the substitution a reader makes when told 'D47's figures moved'.",
)

# Corpus causes: the measured tree changed, and re-recording is the right answer.
CORPUS_CAUSES = (
    "a markdown artifact was added, deleted, or REWRITTEN under `charness-artifacts/quality/`"
    " (a rewrite alone is enough — no file need appear or vanish)",
    "a rewrite touched only an inventory citation or a labelled line, which moves"
    " `field_mention_residuals` or `label_value_residuals` while `artifacts` stays put — so ONE"
    " of the four assertions reds and the count assertion stays green. That is drift, not a"
    " half-broken pin",
)
# Rule causes: the MEASUREMENT changed. Re-recording here would launder a possible regression
# into the probe and into the decision record.
RULE_CAUSES = (
    f"a threshold or predicate in {GATE_MODULE} changed — `MIN_ENGAGEMENT_RESIDUAL_CHARS`,"
    " `residual_chars`, `ENFORCED_FROM_DATE`, `ARTIFACT_DATE_RE`, or a label regex. These live"
    " in the GATE, not in the measure script, so diffing the measure script finds nothing",
    f"the corpus resolver in {CORPUS_LIB} changed — `corpus_paths`, `split_bodies`,"
    " `cited_inventories`, or `exemption_state`. Which files are scanned at all, and which lines"
    " count as body, move every number here without a single artifact changing",
    f"`LABEL_FLOORS` in {FLOOR_MEASURE_SCRIPT} changed — it maps the four labels to the gate"
    " regexes, so adding or dropping one moves `label_value_residuals` alone",
    f"{CONSUMER_FIELDS} changed — declaring or removing a field an artifact actually cites"
    " moves mention counts and the refusal set (a field no artifact cites moves nothing)",
)
# Causes that LOOK live and cannot fire here. Kept rather than deleted: the `history/` one was a
# true corpus cause while a second, RECURSIVE pin existed, and #596 retired that pin without
# retiring the sentence — so a floor reader was being handed a re-record remedy for a write that
# cannot move a single number in this probe.
NOT_CAUSES = (
    "a write under `charness-artifacts/quality/history/` — this probe's corpus glob is"
    f" NON-RECURSIVE (`corpus_paths` in {CORPUS_LIB}), so a nested write moves nothing here. It"
    " used to move a second, recursive pin; #596 retired that pin. If a history write is the"
    " only change in your tree, this red has a different cause",
    "a change to `scripts/measure_inventory_marker_rule.py` — it is a separate script measuring"
    " a separate question (D47's value-marker rule) against an immutable dated snapshot. It"
    " shares the corpus resolver above, but nothing in it feeds this probe",
)
# Where to look, named as files rather than as a category, because "diff the measuring scripts"
# was the instruction that sent a rule change to the corpus remedy. The marker measure script
# was dropped from this list with the marker probe: diffing a script that cannot move a pinned
# number costs a step and teaches the reader the list is padded.
DISCRIMINATION_PATHS = (
    "charness-artifacts/quality/",
    GATE_MODULE,
    FLOOR_MEASURE_SCRIPT,
    CORPUS_LIB,
    CONSUMER_FIELDS,
)


def probe_drift_message(key: str, *, probe: str) -> str:
    """Why this drifted, which remedy that implies, and every surface a re-record must touch.

    The `variant` parameter this took until #624 named the marker probe's nested recursive
    payload. That probe is no longer a caller and the floor probe has no nested payload, so the
    parameter could only have produced a heading describing a shape the reader does not have.
    """
    lines = [
        f"`{key}` drifted from the recorded measurement in {probe}.",
        "",
        "FIRST decide WHICH changed, because the two answers have OPPOSITE remedies.",
        "",
        "If the CORPUS changed, re-record — the measured tree is allowed to change:",
    ]
    lines.extend(f"  - {cause}" for cause in CORPUS_CAUSES)
    lines.extend(
        [
            "",
            "If the RULE changed, do NOT re-record yet. Re-recording would launder a measurement",
            "change into the pinned probe and into the decision record:",
        ]
    )
    lines.extend(f"  - {cause}" for cause in RULE_CAUSES)
    lines.extend(
        [
            "",
            "And these do NOT move these numbers, however much they look like they should:",
        ]
    )
    lines.extend(f"  - {cause}" for cause in NOT_CAUSES)
    lines.extend(
        [
            "",
            "`git diff` these paths to tell them apart — the thresholds are NOT in the measure",
            "script, so diffing only that answers the question wrongly:",
        ]
    )
    lines.extend(f"  - {path}" for path in DISCRIMINATION_PATHS)
    lines.extend(
        [
            "",
            "If the rule moved, establish that the new measurement is CORRECT before pinning it.",
            "",
            "To re-record, update ALL of these. They carry the same numbers, so a partial update",
            "leaves one surface citing a figure no other surface reports:",
        ]
    )
    lines.extend(_render_surfaces(UPDATE_SURFACES))
    lines.extend(
        [
            "",
            "ONLY if the RULE moved, one further surface carries it. A corpus-only drift must",
            "leave it alone — editing it is what #624 was filed about:",
            *_render_surfaces(RULE_ONLY_SURFACES),
            "",
            "And do NOT touch these. They look like they belong on the list above, and until",
            "#624 this message said they did:",
        ]
    )
    lines.extend(f"  - {surface}" for surface in DO_NOT_TOUCH_SURFACES)
    lines.extend(
        [
            "",
            "The measure command prints ONLY its measured payload — the script does not write a",
            "probe and does not emit `_provenance`, so its output cannot be pasted over a probe",
            "file wholesale. The mirror's `run:` is a REGENERATE, not a paste target.",
            f"`{FLOOR_COMMAND}` also exits non-zero when a citation has newly fallen below its",
            "requirement, when a label value falls under the floor, or when an artifact is refused",
            "as uncorroborated; each is a finding to read, not a failure of the command.",
        ]
    )
    return "\n".join(lines)


# --- The THIRD probe site (#561), which is a different claim and needs a different message ---
#
# `probe_drift_message` above must NOT be reused here, and the reason is the trap this module's
# own docstring records: its `UPDATE_SURFACES` names the inventory floor probe and the inventory
# gate, and its `RULE_ONLY_SURFACES` names D47. None of those carry a residual-floor figure. A
# reader following it would re-record an unrelated probe and edit a decision entry that never
# cited this number — the "version 2 was worse than the bare number" failure, repeated.
#
# The deeper difference is the CLAIM. The other site pins equality on counts, so its
# remedy is usually "re-record". This site pins a FLOOR by equality and an INVARIANT over the
# counts (`min_residual >= floor`), which is why it has never needed a refresh — and it means a
# failure here is almost never a re-record. It is a real finding about a real artifact.
RESIDUAL_PROBE = "charness-artifacts/probe/2026-08-01-evidence-residual-floor.json"
RESIDUAL_COMMAND = "python3 scripts/measure_evidence_residual.py --repo-root ."
RESIDUAL_MEASURE_SCRIPT = "scripts/measure_evidence_residual.py"
# The FILE, kept path-shaped so it stays usable with `ROOT /`. The symbol is a separate
# constant: a `*_HOME` that ended in ` (SYMBOL)` broke the first time anyone joined it to a path.
RESIDUAL_FLOOR_HOME = "scripts/check_prescribed_skill_executed_lib.py"
RESIDUAL_FLOOR_SYMBOL = "MIN_BOUND_RESIDUAL_CHARS"
RESIDUAL_FLOOR_MIRROR = "plugins/charness/scripts/check_prescribed_skill_executed_lib.py"
RESIDUAL_CONTRACT_DOC = "docs/prescribed-skill-closeout-contract.md"
RESIDUAL_TIMEBOX_TEST = "tests/quality_gates/test_goal_artifact_timebox.py"

# Every surface transcribing the recorded residual figures. ONE entry was the first draft's
# answer, and it was the `UPDATE_SURFACES` mistake repeated: the figures (`337`, `530`, `2168`,
# `83`, the floor `8`) are quoted in the gate's own rationale, in its GENERATED mirror, in an
# operator-facing contract doc, and in a sibling test's comment. A reader who re-recorded only
# the probe would leave the gate defending its floor with a number no probe reports — and the
# mirror half would block their commit on a drift gate nothing warned them about.
RESIDUAL_UPDATE_SURFACES: tuple[tuple[str, str | None], ...] = (
    (
        f"{RESIDUAL_PROBE} — the whole file; it has NO `_provenance`, unlike the marker and floor"
        " probes, so the command's stdout IS the file",
        RESIDUAL_COMMAND,
    ),
    (
        f"{RESIDUAL_FLOOR_HOME} — the floor's own rationale comments transcribe the per-kind"
        " minimums and file counts, and repeat the smallest residual a third time further down."
        " This is the surface case 2 is ABOUT, so leaving it stale is self-refuting",
        None,
    ),
    (
        f"{RESIDUAL_FLOOR_MIRROR} — the GENERATED mirror of the file above, carrying the same"
        " figures. Do not hand-edit it and do not skip it: regenerate, or a staged-mirror-drift"
        " gate blocks the commit while the mirror still cites the old numbers",
        MIRROR_SYNC_COMMAND,
    ),
    (
        f"{RESIDUAL_CONTRACT_DOC} — operator-facing prose quoting the same per-kind minimums,"
        " file counts, and the floor in one sentence",
        None,
    ),
    (
        f"{RESIDUAL_TIMEBOX_TEST} — a comment quoting the JSON host-log residual; a green test"
        " with a stale comment is the quietest of these",
        None,
    ),
)


def residual_floor_message(key: str, *, kind: str | None = None, recorded_only: bool = False) -> str:
    """Why the evidence-residual pin failed, and why re-recording is usually the WRONG answer."""
    where = f"`{key}` for kind `{kind}`" if kind else f"`{key}`"
    # Only point at a kind when one was actually named. The `exit_code` call site has none —
    # the script exits 1 before any per-kind comparison runs — and telling that reader to look
    # at "the kind named above" sends them to a line that is not there.
    which_kind = f"for the kind `{kind}`" if kind else "for each kind"
    if recorded_only:
        # A THIRD case, and it belongs to exactly one assertion: the one comparing the recorded
        # probe to ITSELF. Nothing live participates, so "drifted from the recorded measurement"
        # is false for it and both cases below send the reader to inspect a healthy live tree.
        return "\n".join(
            [
                f"{where} is inconsistent WITHIN the recorded probe {RESIDUAL_PROBE}.",
                "",
                "Both sides of this comparison come from the checked-in file. Nothing live took",
                "part, so this is NOT drift and running the measurement will not explain it: the",
                "probe records a per-kind minimum that sits under the floor the same file records.",
                "",
                "That means the file was hand-edited, or a re-record captured a run whose invariant",
                "was already broken and pinned it. Do not re-record on top of it — find out which,",
                f"then re-record deliberately with `{RESIDUAL_COMMAND}` and update every surface",
                "listed by the other branch of this message.",
            ]
        )
    return "\n".join(
        [
            f"{where} no longer matches the recorded measurement in {RESIDUAL_PROBE}.",
            "",
            "This site does NOT pin counts, so this is not the usual re-record. Read which of the",
            "two claims broke:",
            "",
            "1. THE INVARIANT BROKE — the floor is no longer STRICTLY below every measured minimum.",
            "   That is a FINDING, not drift: some artifact in the measured corpus carries no more",
            "   bound evidence than the floor the gate enforces. Note the strictness — the command",
            "   exits 1 when a minimum EQUALS the floor, which the gate itself still passes, so the",
            "   offending file may not be refused anywhere else yet. Do NOT lower the floor and do",
            f"   NOT re-record. Run `{RESIDUAL_COMMAND}` and read `min_residual_path` {which_kind} —",
            "   it names the file. Either it is a stub that should carry real evidence, or it is not",
            "   evidence at all and does not belong in the corpus.",
            "   The same exit code also covers an EMPTY corpus (`corpus_established: false`), where",
            "   nothing is below anything; check that field before reading the minimums.",
            "",
            "2. THE FLOOR MOVED — the recorded `floor` no longer equals the live one.",
            f"   The constant is `{RESIDUAL_FLOOR_SYMBOL}` in {RESIDUAL_FLOOR_HOME}, NOT in",
            f"   `{RESIDUAL_MEASURE_SCRIPT}`, which only imports it — so diffing the measure script",
            "   finds nothing. A floor change is a RULE change: establish the new floor is correct",
            "   before pinning it, then re-record.",
            "",
            "Per-kind COUNTS are deliberately not pinned. `kinds[*].files` grows as artifacts land",
            "and that is expected — the floor claim is what must hold. If you find yourself",
            "re-recording to make this green, the assertion you are silencing is the invariant.",
            "",
            "To re-record (case 2 only), update ALL of these. They carry the same figures, so a",
            "partial update leaves one surface citing a number no other surface reports:",
            *_render_surfaces(RESIDUAL_UPDATE_SURFACES),
        ]
    )


def _render_surfaces(surfaces: tuple[tuple[str, str | None], ...]) -> list[str]:
    lines: list[str] = []
    for surface, command in surfaces:
        lines.append(f"  - {surface}")
        lines.append(f"      run: {command}" if command is not None else "      edit by hand")
    return lines
