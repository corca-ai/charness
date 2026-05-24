# RCA Ledger Append (Shared)

Closeout-append step for the RCA-to-learning conversion ledger. `debug`, `issue`,
and `retro` cite this reference so RCA events accrue through one standardized,
rubric-anchored closeout step across the three skills, instead of each skill
re-deriving the recorder contract. The append is prompt-enforced (it still
depends on closeout discipline), not gate-enforced.

## When This Applies

This step is **repo-gated, not consumer-facing**. It applies only in a repo that
maintains the conversion ledger — both `<repo-root>/scripts/record_rca_event.py`
and `<repo-root>/charness-artifacts/metrics/rca-ledger.jsonl` exist (Charness's
own self-development dogfood). In any other repo, including consumer installs of
the public skills, this step is a **silent no-op**: do not create the script, the
ledger, or mention a missing recorder in closeout.

The recorder is the always-on Charness self-dev metric from the
[rca-conversion-ledger spec](../../../charness-artifacts/spec/rca-conversion-ledger.md);
it is deliberately independent of the privacy-gated usage-episodes adapter. Do
not wire it through that adapter or any of its state/session machinery.

## What To Append

Append **one** RCA event per task-completing closed work unit — not one per
sibling, and for `issue resolve` ranges, one per fix-unit (mirrors the
resolution-critique "one per fix-unit" rule). Use the source matching the
calling skill: `debug` → `--source debug`, `issue` → `--source issue`,
`retro` → `--source retro`.

Only append when the work unit actually surfaced an RCA-class event — a `bug`, a
`repeated_correction`, or a `weak_proof` finding (the `--event-kind` enum). A
clean feature/question resolution or a routine retro with no mistake to learn
from appends nothing.

All judgment calls (what counts as `converted`, the per-`durable_kind` quality
bar, `event_kind` rules, and the tie-break default) are owned by the
**classification rubric** in
[docs/product-success-metrics.md](../../../docs/product-success-metrics.md). Read
it before recording; this reference does not restate or extend it. The closed
enums are owned by [scripts/rca_event.schema.json](../../../scripts/rca_event.schema.json).

Field guidance for the recorder flags:

- `--event-kind {bug|repeated_correction|weak_proof}`: per the rubric.
- `--converted` with `--durable-kind {gate|spec|test|issue|retro_lesson}`: set
  both together only when a named durable artifact prevents *this class* from
  recurring and cites a concrete detection point. Omit both (`durable_kind`
  defaults to `none`) when not converted. The schema enforces the bidirectional
  invariant (`durable_kind == none` iff `converted == false`) and the recorder
  validates-before-append, so a violation is refused without mutating the ledger.
- `--class-key`: a short opaque non-PII identifier of the mistake class, for
  dedup and recurrence tracking.
- `--caught-by {agent|human|gate}`: who first surfaced the mistake; omit when
  unknown (it never blocks a record).
- `--ref`: opaque non-PII reference — issue number, commit sha, or
  repo-root-relative artifact path (e.g. the debug artifact path).
- `--note`: optional short non-PII summary.
- Never pass `--seed`; that flag marks hand-entered historical events only.

**Tie-break default**: when it is unclear whether the event qualifies as
converted, record it with `--converted` omitted (`converted=false`) rather than
skipping the append. Ambiguity should inflate the denominator, never silently
suppress the event.

## How

```bash
python3 scripts/record_rca_event.py \
  --source <debug|issue|retro> --event-kind <bug|repeated_correction|weak_proof> \
  --class-key <short-opaque-class> [--converted --durable-kind <kind>] \
  [--caught-by <agent|human|gate>] [--ref <issue|sha|path>] [--note "<summary>"]
```

The committed ledger is durable repo state: commit the appended line with the
work it records, in the same closeout. Check the running figure any time with
`python3 scripts/aggregate_rca_ledger.py`.
