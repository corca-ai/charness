# Spec: RCA-to-Learning Conversion Ledger

Source: https://github.com/corca-ai/charness/issues/184 (north-star + first
instrument), https://github.com/corca-ai/charness/issues/185 (improvement #1)

Baseline doc: [docs/product-success-metrics.md](../../docs/product-success-metrics.md)
("Single North-Star Objective")

## Problem

Issue #184 selected one optimized objective for Charness: the
**repeated-mistake-to-learning conversion rate** — the share of RCA events
(bugs, repeated corrections, weak-proof findings) that are converted into a
recurrence-preventing durable artifact (a new deterministic gate, spec, test,
tracked issue, or a retro lesson naming the detection gap and sibling pattern).

The metric cannot be tracked until RCA events and their conversion are recorded
in a fixed, aggregatable shape. Free-form retro/issue text is not reliably
aggregatable; #184 chose a fixed-schema ledger instead. This spec defines the
build contract for that ledger.

## Current Slice

Stand up the ledger substrate so a conversion rate can be computed from real
data, without yet editing the debug/issue/retro skill prompts:

- a JSON schema for one `rca_event` record with closed enums
- `scripts/record_rca_event.py`: validate-and-append one event to the ledger
- `scripts/aggregate_rca_ledger.py`: print conversion rate overall and by
  `source` and `event_kind`, optionally windowed
- `scripts/validate_rca_ledger.py`: schema + closed-enum check over the ledger
- the canonical ledger file `charness-artifacts/metrics/rca-ledger.jsonl`,
  seeded with the known recent real events so baseline observation can start
  immediately (non-empty number on day one)

Auto-append wiring into the debug/issue/retro skill closeout prompts is the
next slice (see Deferred Decisions), because it edits behavior-steering prompt
surfaces and warrants its own preserve/improve claim and proof path.

## Fixed Decisions

1. North-star = RCA-to-learning conversion rate; first instrument = this ledger;
   target policy = baseline-first (no guessed number now). (from #184)
2. **The ledger is independent of the usage-episodes adapter.** usage-episodes
   captures consumer-repo runtime use and is privacy-gated and disabled by
   design; this ledger is Charness self-development dogfood with no consumer-PII
   concern, so it is always-on for Charness's own repo and is NOT gated by, or
   coupled to, `.agents/usage-episodes-adapter.yaml`.
3. Canonical ledger path: `charness-artifacts/metrics/rca-ledger.jsonl`,
   committed as durable repo state (per artifact policy), append-only, one JSON
   object per line.
4. Record schema (`schema_version: 1`):
   - `ts` (UTC ISO8601, `...Z`)
   - `source`: closed enum `debug | issue | retro`
   - `event_kind`: closed enum `bug | repeated_correction | weak_proof`
   - `converted`: bool — whether a recurrence-preventing durable artifact was
     produced for this event
   - `durable_kind`: closed enum `gate | spec | test | issue | retro_lesson |
     none`. **Bidirectional invariant**: `durable_kind == none` if and only if
     `converted == false`. The schema rejects both `converted=false` with a
     non-`none` kind and `converted=true` with `none`.
   - `class_key`: short opaque string identifying the mistake class (for dedup
     and recurrence tracking; non-PII)
   - `seed`: bool, default false — true marks a hand-entered historical event.
     Seed events are excluded from the baseline-window rate so a hand-picked
     starting set cannot anchor the eventual numeric target.
   - `ref`: opaque reference (issue number, commit sha, or repo-root-relative
     artifact path); non-PII
   - `note`: optional short human-readable summary (non-PII)
5. Conversion rate = `converted=true` count / total RCA events, decomposable by
   `source` and `event_kind`, and windowable by `ts`. The aggregator reports the
   rate twice: including seed events (sanity) and excluding them (the figure the
   baseline target is set from).
6. Closed enums are owned by the schema; docs summarize them and must not extend
   them inline (mirrors usage-episode enum discipline).
7. **Classification rubric** (lives in `docs/product-success-metrics.md` so the
   number is reproducible across recorders): `converted=true` requires a named
   durable artifact that prevents *this class* recurring — a `retro_lesson` only
   counts when it names the detection gap and sibling pattern, not a bare note.
   `event_kind` rules: `bug` = defect in shipped behavior; `repeated_correction`
   = the same class of correction the operator already gave; `weak_proof` = a
   closeout that reached only an explicitly weak proof level. Without this rubric
   the rate is well-formed but not comparable across sessions.

## Probe Questions

- Dedup / recurrence rule for `class_key`: how strict should "same class of
  mistake" matching be before two events count as a recurrence vs two distinct
  events? Refine through impl as real events accrue; start with exact
  `class_key` match.
- Validator gate posture: schema validity of new/changed ledger lines should be
  enforceable, but the conversion-rate aggregation stays advisory. Confirm
  during impl that `validate_rca_ledger.py` blocks only on malformed lines
  (changed-surface scope), not on the rate value (recent-lessons trap: do not
  reuse a selection/metric heuristic as a whole-artifact blocker).

## Deferred Decisions

- Auto-append wiring into `debug`, `issue`, and `retro` skill closeout prompts
  (next slice; behavior-steering prompt change with its own preserve/improve
  claim). **The baseline window does not open until this wiring is live** — a
  ledger that grows only by manual discipline is measuring the very thing it
  exists to track, so a target set before auto-append would rest on a tiny
  biased sample. Slice 2 is a hard prerequisite for the numeric target, not a
  soft follow-up.
- Numeric target for the conversion rate (baseline-first: revisit after 2-4
  weeks of *auto-appended, seed-excluded* ledger data).
- Consumer-repo scope (depends on usage-episode capture; separate deferred
  decision, do not couple here).
- Automation that feeds the aggregated rate into the weekly/monthly review
  loops described in the baseline doc.

## Non-Goals

- Consumer-repo or runtime/session usage capture.
- Any privacy-gated adapter for this ledger.
- Setting a numeric conversion-rate target in this slice.
- Editing the debug/issue/retro skill prompts in this slice.

## Deliberately Not Doing

- Reusing the usage-episodes adapter/manifest/host-hook machinery. It solves a
  different problem (consumer runtime capture under privacy gating). Coupling
  this self-dev metric to a disabled, gated capture surface would either block
  the metric behind an unrelated opt-in or leak the two concerns into each
  other. Kept independent on purpose. **This forbids coupling to the adapter and
  its state/session machinery — it does NOT forbid reusing the small
  jsonschema-validate-before-write and portable-path utilities from
  `slice_closeout_usage_episode.py`.** Reuse those helpers; do not reinvent
  validation or rebuild the adapter.

## Constraints

- jsonl append-only, committed; portable repo-root-relative paths; no PII in any
  field (`ref`, `class_key`, `note` stay opaque/non-PII).
- New scripts respect repo length budgets (480/360 file, 100/150 function);
  check current size before extending shared modules.
- Validator must not become an unjustified broad gate; block only on malformed
  lines, keep the rate advisory.
- Follow `mutate -> sync -> verify -> publish` phase order at impl.

## Success Criteria

1. A malformed ledger line is rejected, covering both invariant directions
   (`durable_kind != none` with `converted=false`, AND `durable_kind == none`
   with `converted=true`), plus bad enum and missing field.
2. The conversion rate and per-`source`/per-`event_kind` breakdown are computed
   correctly from a known fixture, reported both including and excluding `seed`
   events.
3. The record helper writes only schema-valid lines (validate-before-append).
4. The committed ledger is seeded with real recent events of BOTH outcomes —
   converted and unconverted — each marked `seed=true`, so the day-one number is
   honest rather than survivorship-biased toward 100%.
5. Recording and aggregation work with the usage-episodes adapter in its current
   `disabled` state (proves independence).
6. The classification rubric (Fixed Decision 7) is written into
   `docs/product-success-metrics.md`.

## Acceptance Checks

- AC1 -> `validate_rca_ledger.py` exits non-zero on a fixture containing each
  malformed case in SC1 (both invariant directions, bad enum, missing field);
  exits zero on the valid committed ledger.
- AC2 -> `aggregate_rca_ledger.py` on a fixed fixture emits the expected overall
  rate plus the expected `source` and `event_kind` breakdown, and emits both the
  seed-included and seed-excluded rate (assert in a unit test).
- AC3 -> round-trip test: `record_rca_event.py` appends an event, then
  `validate_rca_ledger.py` passes; an invalid input is refused before append
  (ledger unchanged).
- AC4 -> committed `charness-artifacts/metrics/rca-ledger.jsonl` contains
  >=1 converted and >=1 unconverted seed event, and the seed-excluded rate
  starts empty (no non-seed events yet) while the seed-included rate is < 100%.
- AC5 -> the AC3 round-trip test runs green with no usage-episodes adapter
  enabled (default repo state).
- AC6 -> `docs/product-success-metrics.md` contains the classification rubric
  text matching Fixed Decision 7.

## Critique

Bounded fresh-eye subagent review completed; findings incorporated above.

- F1 (acceptance proved well-formedness, not a trustworthy number): added the
  classification rubric (Fixed Decision 7, SC6, AC6).
- F2 (hand-seeded baseline is survivorship-biased toward 100%): added the `seed`
  field, seed-excluded rate, and the both-outcomes seeding requirement (SC4,
  AC4).
- F3 (deferring auto-append risks a permanently near-empty ledger and a target
  set on a tiny biased sample): made slice 2 a hard prerequisite for the numeric
  target; the baseline window does not open until auto-append is live.
- F4 (independence boundary): confirmed coherent; clarified that the ban is on
  adapter coupling, not on reusing the jsonschema/portable-path helpers.
- F6 (one-directional invariant): schema now rejects both invariant directions.

Accepted as over-worry: reusing usage-episode utility helpers is good, not the
forbidden coupling; recent-lessons traps (length budgets, gate scoping,
auto-close keyword) are already addressed.

No forced debug interrupt is active (`plan_risk_interrupt.py` -> `not-applicable`).

## Canonical Artifact

This file (`charness-artifacts/spec/rca-conversion-ledger.md`) is canonical
during implementation. The metric definition of record stays in
`docs/product-success-metrics.md`.

## First Implementation Slice

1. Add the `rca_event` JSON schema (closed enums, `none`/`converted` invariant).
2. Implement `record_rca_event.py` (validate-then-append).
3. Implement `validate_rca_ledger.py` and `aggregate_rca_ledger.py`.
4. Seed `charness-artifacts/metrics/rca-ledger.jsonl` (`seed=true`) with recent
   real RCA events of BOTH outcomes: converted ones (e.g. #197 symptom->root-cause
   naming, the 2026-05-24 mutation-scope trap that became a retro lesson) AND
   unconverted ones (e.g. a bug that recurred, or a weak-proof finding never
   turned into a gate) so the day-one number is not survivorship-biased.
5. Write the classification rubric into `docs/product-success-metrics.md`.
6. Add unit tests for AC1-AC6.
