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
"""

from __future__ import annotations

MARKER_PROBE = "charness-artifacts/probe/2026-08-01-inventory-marker-rule.json"
FLOOR_PROBE = "charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json"
DECISION_RECORD = "docs/deferred-decisions.md"
# Where the thresholds actually live. Both measure scripts import this module rather than
# defining the rule, so a rule change shows up HERE and in neither measure script.
GATE_MODULE = "scripts/validate_inventory_consumption.py"
# The exported mirror carries the same transcribed numbers, and it is generated rather than
# hand-written — so it is a surface with a COMMAND, not an `edit by hand` entry.
GATE_MIRROR = "plugins/charness/scripts/validate_inventory_consumption.py"
MIRROR_SYNC_COMMAND = "python3 scripts/sync_root_plugin_manifests.py"
CONSUMER_FIELDS = "skills/public/quality/references/inventory-consumer-fields.json"

# Each command prints ONLY its measured payload. Neither script writes a probe, and neither
# emits `_provenance`, so no output can be pasted over a probe file wholesale.
MARKER_COMMAND = "python3 scripts/measure_inventory_marker_rule.py --repo-root . --json"
MARKER_RECURSIVE_COMMAND = (
    "python3 scripts/measure_inventory_marker_rule.py --repo-root . --recursive --json"
)
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
UPDATE_SURFACES: tuple[tuple[str, str | None], ...] = (
    (
        f"{MARKER_PROBE} — replace the TOP-LEVEL payload keys, keeping `_provenance`",
        MARKER_COMMAND,
    ),
    (
        f"{MARKER_PROBE} — replace `_provenance.recursive_variant` (it nests HERE, not at top"
        " level); add no summary keys of your own, because the recursive pin iterates the"
        " recorded keys and an extra one raises `KeyError` instead of this message",
        MARKER_RECURSIVE_COMMAND,
    ),
    (
        f"{FLOOR_PROBE} — replace the TOP-LEVEL payload keys, keeping `_provenance`",
        FLOOR_COMMAND,
    ),
    (
        "both probes' `_provenance` bookkeeping — `date`, `repo_head_at_run`, `worktree`, and"
        " `synchronized_after`/`synchronized_reason`, which count the refreshes in prose. Leaving"
        " these is how a re-recorded payload ends up wearing a provenance block that names an"
        " older run, which no reader can falsify",
        None,
    ),
    (
        f"{MARKER_PROBE} `_provenance.current_corpus` AND `_provenance.why` — each quotes the"
        " counts in prose, and `why` is the one that hides: it ENDS on the presence-only total,"
        " so updating only `current_corpus` leaves a stale figure one key away. The floor probe"
        " has NO such field, but do NOT read that as a figure-free block: its `_provenance`"
        " quotes counts in THREE other keys (`why`, `synchronized_after`, and"
        " `counterfactual_floor_20`), and `why` is the one that says the headline figures are not"
        " transcribed there — a scope limited to the headline pair, not a promise about the key",
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
        f"{DECISION_RECORD} D47 — it quotes marker-probe figures throughout its prose, shallow and"
        " recursive, and its refresh bullet counts the refreshes. Re-read the whole entry against"
        " the payload rather than updating the figures you remember; it carries far more than the"
        " headline two. It does NOT name the floor probe, so a floor-only drift still needs a D47"
        " edit whenever a figure it quotes moved",
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

# Corpus causes: the measured tree changed, and re-recording is the right answer.
CORPUS_CAUSES = (
    "a markdown artifact was added, deleted, or REWRITTEN under `charness-artifacts/quality/`"
    " (a rewrite alone is enough — no file need appear or vanish)",
    "the write landed under `quality/history/` rather than at the top level, which moves the"
    " RECURSIVE numbers only, so one site reds instead of three",
)
# Rule causes: the MEASUREMENT changed. Re-recording here would launder a possible regression
# into the probe and into the decision record.
RULE_CAUSES = (
    f"a threshold or predicate in {GATE_MODULE} changed — `MIN_ENGAGEMENT_RESIDUAL_CHARS`,"
    " `residual_chars`, `ENFORCED_FROM_DATE`, `ARTIFACT_DATE_RE`, or a label regex. These live"
    " in the GATE, not in either measure script, so diffing the measure scripts finds nothing",
    "a marker predicate in `scripts/measure_inventory_marker_rule.py` changed",
    f"{CONSUMER_FIELDS} changed — declaring or removing a field an artifact actually cites"
    " moves mention counts and the refusal set in both probes (a field no artifact cites moves"
    " nothing)",
)
# Where to look, named as files rather than as a category, because "diff the measuring scripts"
# was the instruction that sent a rule change to the corpus remedy.
DISCRIMINATION_PATHS = (
    "charness-artifacts/quality/",
    GATE_MODULE,
    "scripts/measure_inventory_marker_rule.py",
    "scripts/measure_inventory_consumption_floor.py",
    "scripts/inventory_measurement_lib.py",
    CONSUMER_FIELDS,
)


def probe_drift_message(key: str, *, probe: str, variant: str | None = None) -> str:
    """Why this drifted, which remedy that implies, and every surface a re-record must touch."""
    where = f"{probe} ({variant})" if variant else probe
    lines = [
        f"`{key}` drifted from the recorded measurement in {where}.",
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
            "`git diff` these paths to tell them apart — the thresholds are NOT in the measure",
            "scripts, so diffing only those answers the question wrongly:",
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
    for surface, command in UPDATE_SURFACES:
        lines.append(f"  - {surface}")
        if command is not None:
            lines.append(f"      run: {command}")
        else:
            lines.append("      edit by hand")
    lines.extend(
        [
            "",
            "Each command prints ONLY its measured payload — neither script writes a probe and",
            "neither emits `_provenance`, so no output can be pasted over a probe file wholesale.",
            f"`{FLOOR_COMMAND}` also exits non-zero when a citation has newly fallen below its",
            "requirement, when a label value falls under the floor, or when an artifact is refused",
            "as uncorroborated; each is a finding to read, not a failure of the command.",
        ]
    )
    return "\n".join(lines)


# --- The THIRD probe site (#561), which is a different claim and needs a different message ---
#
# `probe_drift_message` above must NOT be reused here, and the reason is the trap this module's
# own docstring records: its `UPDATE_SURFACES` names the marker probe, the floor probe, D47, and
# the inventory gate. None of those carry a residual-floor figure. A reader following it would
# re-record two unrelated probes and edit a decision entry that never cited this number — the
# "version 2 was worse than the bare number" failure, repeated.
#
# The deeper difference is the CLAIM. The other two sites pin equality on counts, so their
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
