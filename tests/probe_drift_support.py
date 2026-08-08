"""One message for probe drift, naming the CAUSE, the FULL update set, and how to re-record.

#536. Two checked-in measurement probes are pinned against the live tree, and the tree they
measure is `charness-artifacts/quality/` — a directory ordinary quality work writes to on
almost every slice. Writing one markdown artifact there turns three assertions red across two
files, and what the reader got was a drifted number:

    AssertionError: artifacts_scanned drifted from the recorded probe; update D47 and the probe
    together
    assert 132 == 131

That named a coupled pair and stopped. It did not say what caused the drift, which OTHER
surfaces carry the same numbers, or how to re-record any of it — so the agent rediscovers all
of that every time, and the three sites said three different things, one of them nothing.

A first version of this message was worse than the number it replaced: it told the reader to
"copy each payload into the probe file", which DELETES `_provenance`, and it did not say that
the recursive payload nests under `_provenance.recursive_variant`. Following it produced a bare
`KeyError: '_provenance'` on the next run — the diagnostic class #536 is about, reintroduced by
the fix for #536. A bounded round caught it. Everything below is checked against the probe
files' actual shape and against what `--json` actually emits.
"""

from __future__ import annotations

MARKER_PROBE = "charness-artifacts/probe/2026-08-01-inventory-marker-rule.json"
FLOOR_PROBE = "charness-artifacts/probe/2026-08-01-inventory-consumption-floor.json"
DECISION_RECORD = "docs/deferred-decisions.md"

# Each command prints ONLY its measured payload. Neither script writes a probe, and neither
# emits `_provenance` — so no command's output can be pasted over a probe file wholesale.
MARKER_COMMAND = "python3 scripts/measure_inventory_marker_rule.py --repo-root . --json"
MARKER_RECURSIVE_COMMAND = (
    "python3 scripts/measure_inventory_marker_rule.py --repo-root . --recursive --json"
)
FLOOR_COMMAND = "python3 scripts/measure_inventory_consumption_floor.py --repo-root . --json"

# What a re-record has to touch. This is FIVE surfaces, not three: a first version said three
# and the probes themselves refute it — `_provenance.current_corpus` and
# `_provenance.synchronized_after` quote counts in prose, and the marker probe records that a
# transcribed number went stale for two refresh cycles in exactly such a field.
UPDATE_SURFACES = (
    f"{MARKER_PROBE} top-level payload keys — replace with the `{MARKER_COMMAND}` output,"
    " keeping `_provenance`",
    f"{MARKER_PROBE} `_provenance.recursive_variant` — replace with the"
    f" `{MARKER_RECURSIVE_COMMAND}` output (it nests HERE, not at top level)",
    f"{FLOOR_PROBE} top-level payload keys — replace with the `{FLOOR_COMMAND}` output,"
    " keeping `_provenance`",
    "both probes' `_provenance.current_corpus` and `_provenance.synchronized_after` — these"
    " quote the counts in PROSE, and a stale one has already shipped here",
    f"{DECISION_RECORD} D47 — it quotes marker-probe figures and cites the floor probe's"
    " `field_mention_residuals.count` as its denominator",
)

# Corpus causes: the tree changed, and re-recording is right. Rule causes: the MEASUREMENT
# changed, and re-recording would launder a possible regression into the probe and into D47.
CORPUS_CAUSES = (
    "a markdown artifact was added, deleted, or REWRITTEN under `charness-artifacts/quality/`"
    " (a rewrite alone is enough — no file need appear or vanish)",
    "the write landed under `quality/history/` rather than at the top level, which moves the"
    " RECURSIVE numbers only, so one site reds instead of three",
)
RULE_CAUSES = (
    "`skills/public/quality/references/inventory-consumer-fields.json` changed — a declared"
    " field moves mention counts and the refusal set in BOTH probes",
    "a marker regex, `MIN_ENGAGEMENT_RESIDUAL_CHARS`, `residual_chars`, or `ENFORCED_FROM_DATE`"
    " changed in the measuring scripts",
    "git was unavailable or the checkout is shallow — the exemption state falls back to"
    " `unavailable`, which changes which pre-contract artifacts are skipped, with no write at"
    " all",
)


def probe_drift_message(key: str, *, probe: str, variant: str | None = None) -> str:
    """Why this drifted, what carries the same numbers, and how to re-record each one."""
    where = f"{probe} ({variant})" if variant else probe
    lines = [
        f"`{key}` drifted from the recorded measurement in {where}.",
        "",
        "FIRST decide WHICH changed, because the two answers have opposite remedies.",
        "",
        "If the CORPUS changed, re-record — the tree is allowed to change:",
    ]
    lines.extend(f"  - {cause}" for cause in CORPUS_CAUSES)
    lines.extend(
        [
            "",
            "If the RULE or the ENVIRONMENT changed, do NOT re-record yet. Re-recording would",
            "launder a measurement change into the pinned probe and into the decision record:",
        ]
    )
    lines.extend(f"  - {cause}" for cause in RULE_CAUSES)
    lines.extend(
        [
            "",
            "`git status --short` and `git diff` over the corpus and the measuring scripts answer",
            "this in one look. If the rule moved, establish that the new measurement is CORRECT",
            "before pinning it.",
            "",
            "To re-record, update ALL of these. They carry the same numbers, so a partial update",
            "leaves one surface citing a figure no other surface reports:",
        ]
    )
    lines.extend(f"  - {surface}" for surface in UPDATE_SURFACES)
    lines.extend(
        [
            "",
            "Each command prints ONLY its measured payload — neither script writes a probe and",
            "neither emits `_provenance`, so no output can be pasted over a probe file wholesale.",
            f"Note that `{FLOOR_COMMAND}` exits non-zero when a citation has newly fallen below",
            "the floor; that is a finding to read, not a failure of the command.",
        ]
    )
    return "\n".join(lines)
