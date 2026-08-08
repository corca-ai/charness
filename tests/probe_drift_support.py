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
CONSUMER_FIELDS = "skills/public/quality/references/inventory-consumer-fields.json"

# Each command prints ONLY its measured payload. Neither script writes a probe, and neither
# emits `_provenance`, so no output can be pasted over a probe file wholesale.
MARKER_COMMAND = "python3 scripts/measure_inventory_marker_rule.py --repo-root . --json"
MARKER_RECURSIVE_COMMAND = (
    "python3 scripts/measure_inventory_marker_rule.py --repo-root . --recursive --json"
)
FLOOR_COMMAND = "python3 scripts/measure_inventory_consumption_floor.py --repo-root . --json"

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
        f"{MARKER_PROBE} `_provenance.current_corpus` — this one quotes the counts in prose. The"
        " floor probe has NO such field; do not go looking for it",
        None,
    ),
    (
        f"{DECISION_RECORD} D47 — it quotes marker-probe figures (the artifact count and the"
        " presence-only total) and its refresh bullet counts the refreshes. It does NOT name the"
        " floor probe, so a floor-only drift still needs a D47 edit whenever a figure it quotes"
        " moved",
        None,
    ),
    (
        f"{GATE_MODULE} — its comments transcribe the corpus label minimum and a"
        " counterfactual-floor count. A partial update leaves the gate defending its floor with"
        " a number no probe reports",
        None,
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
