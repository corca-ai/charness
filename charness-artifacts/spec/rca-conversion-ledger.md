# Spec: RCA-to-Learning Conversion Ledger

Source: https://github.com/corca-ai/charness/issues/184 (north-star + first
instrument), https://github.com/corca-ai/charness/issues/185 (improvement #1)

Baseline doc: [docs/product-success-metrics.md](../../docs/product-success-metrics.md)
("North-Star And First Instrumented Objective")

## Problem

Issue #184 named the product north-star as operator/agent task success and trust
(not yet directly measurable) and selected a **first instrumented objective** to
optimize today: the **repeated-mistake-to-learning conversion rate** — the share
of RCA events (bugs, repeated corrections, weak-proof findings) that are
converted into a recurrence-preventing durable artifact (a deterministic gate,
spec, test, tracked issue, or a retro lesson naming the detection gap and sibling
pattern). It is an engineering-health leading indicator subordinate to the
demoted monitored metrics, which keep veto power.

The metric cannot be tracked until RCA events and their conversion are recorded
in a fixed, aggregatable shape. Free-form retro/issue text is not reliably
aggregatable; #184 chose a fixed-schema ledger instead. This spec defines the
build contract for that ledger.

## Current Slice

Slice 1 (landed) stood up the ledger substrate so a conversion rate can be
computed from real data, before editing the debug/issue/retro skill prompts:

- a JSON schema for one `rca_event` record with closed enums
- `scripts/record_rca_event.py`: validate-and-append one event to the ledger
- `scripts/aggregate_rca_ledger.py`: print conversion rate overall and by
  `source` and `event_kind`, optionally windowed
- `scripts/validate_rca_ledger.py`: schema + closed-enum check over the ledger
- the canonical ledger file `charness-artifacts/metrics/rca-ledger.jsonl`,
  seeded with the known recent real events so baseline observation can start
  immediately (non-empty number on day one)

Auto-append wiring into the debug/issue/retro skill closeout prompts landed in
slice 2 (see the Second Implementation Slice section), with its own
preserve/improve claim and proof path because it edits behavior-steering prompt
surfaces.

## Fixed Decisions

1. Product north-star = operator/agent task success and trust (named, not yet
   measurable). First *instrumented* objective = RCA-to-learning conversion rate
   (an engineering-health leading indicator), first instrument = this ledger;
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
   - `caught_by`: closed enum `agent | human | gate`, nullable — who first
     surfaced the mistake. Required to tell "the harness got smarter" (agent or
     gate caught it) from "a human kept fixing it" (human caught it), which is
     the core claim the conversion rate is supposed to support. Nullable so a
     missing value never blocks a record.
   - `seed`: bool, default false — true marks a hand-entered historical event.
     Seed events are excluded from the baseline-window rate so a hand-picked
     starting set cannot anchor the eventual numeric target.
   - `ref`: opaque reference (issue number, commit sha, or repo-root-relative
     artifact path); non-PII
   - `note`: optional short human-readable summary (non-PII)
5. Conversion rate = `converted=true` count / total RCA events, decomposable by
   `source` and `event_kind`, and windowable by `ts`. The aggregator reports the
   rate twice: including seed events (sanity) and excluding them (the figure the
   baseline target is set from). **Quote-safety honesty** (live invariant): the
   aggregator emits `n/a` rather than `0%` for an empty seed-excluded window,
   refuses to print a non-seed baseline rate while zero non-seed events exist,
   and labels the seed-included rate "sanity only — do not quote". The banner
   states the wiring state: `auto_append: OFF (slice 2 not wired)` before slice 2,
   and after slice 2 `auto_append: ON` carrying the "prompt-enforced; denominator
   self-reported, not gate-verified" qualifier. This stops anyone quoting a
   seed-only or fake-zero number as "the metric".
6. Closed enums are owned by the schema; docs summarize them and must not extend
   them inline (mirrors usage-episode enum discipline).
7. **Classification rubric** (lives in `docs/product-success-metrics.md` so the
   number is reproducible across recorders): `converted=true` requires a named
   durable artifact that prevents *this class* recurring, and the quality bar
   applies to EVERY `durable_kind`, not just `retro_lesson` — each converted
   event must name the class it prevents and cite the detection point (gate
   name, spec/test path, issue number, or the retro lesson's detection-gap +
   sibling-pattern lines). A throwaway issue or one-line lesson with no named
   detection point does not count as converted; this closes the numerator-gaming
   path (padding cheap conversions to inflate the rate). `event_kind` rules:
   `bug` = defect in shipped behavior; `repeated_correction` = the same class of
   correction the operator already gave; `weak_proof` = a closeout that reached
   only an explicitly weak proof level. **Tie-break default**: if it is unclear
   whether an event qualifies, log it with `converted=false` rather than omit it
   — ambiguity should inflate the denominator (conservative), never silently
   suppress it (flattering). Without this rubric the rate is well-formed but not
   comparable across sessions.

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

- **DONE (slice 2)**: Auto-append wiring into `debug`, `issue`, and `retro`
  skill closeout prompts via the presence-gated shared reference
  `skills/shared/references/rca-ledger-append.md`. `AUTO_APPEND_WIRED` is now
  `True` so the aggregator banner reads `ON`. **The baseline window is now open
  but empty** — it grows only as live (non-seed) events accrue; a target set on a
  tiny sample would still rest on biased data, so the numeric target stays
  baseline-first per the next bullet. The append is prompt-enforced, not
  gate-enforced (see slice-2 residual risk).
- Numeric target for the conversion rate (baseline-first: revisit after 2-4
  weeks of *auto-appended, seed-excluded* ledger data).
- Consumer-repo scope (depends on usage-episode capture; separate deferred
  decision, do not couple here). **Revisit trigger**: the 2-4 week baseline
  review. No hard kill-date is encoded now because there is no committed
  external-audience roadmap to anchor one; if the baseline review passes with no
  consumer-scope decision, reopen the question then rather than letting it drift
  silently.
- Automation that feeds the aggregated rate into the weekly/monthly review
  loops described in the baseline doc.
- **Independent denominator reconciliation** (deferred to the baseline review):
  cross-check ledger `source` counts against independent evidence (debug
  artifacts, bug-labeled closed issues, retro lessons) for the window; a gap is
  a logged "missed-capture" finding. Deferred because there is no auto-appended,
  non-seed data to reconcile against yet; build it when the ledger actually
  accrues live events, since a self-reported denominator is otherwise
  unauditable.
- **Recurrence rate of already-converted `class_key`s** (deferred to the
  baseline review): the deepest signal is whether a *converted* class recurs
  anyway (a gate that did not actually prevent recurrence), reported as a
  headline alongside the conversion rate. The schema already carries `class_key`
  for this. Deferred because recurrence cannot be computed until classes have had
  weeks of real data to recur; wiring it now reports noise over a seed-only
  window.

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
5. Recording and aggregation work regardless of usage-episodes adapter state
   (proves independence). Impl note: the adapter is `enabled` in this repo as of
   this slice (maintainers opted into local capture after the 2026-05-22 quality
   snapshot that read `disabled`), so independence is proven structurally — the
   RCA scripts reference no adapter/state/session machinery — which is a stronger
   proof than the spec's original "works while disabled" framing.
6. The classification rubric (Fixed Decision 7) is written into
   `docs/product-success-metrics.md`, with the quality bar applying to every
   `durable_kind` and the `converted=false` tie-break default.
7. The aggregator never emits a misreadable number: it emits `n/a` (not `0%`)
   for an empty seed-excluded window, refuses a non-seed baseline rate when no
   non-seed events exist, labels the seed-included rate "do not quote", and the
   banner states the wiring state (`OFF` pre-slice-2; `ON` with the
   prompt-enforced qualifier post-slice-2).
8. A `caught_by` value, when present, is one of `agent | human | gate`; a record
   without it is still valid.

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
- AC5 -> the AC3 round-trip test runs green regardless of usage-episodes adapter
  state, and the RCA scripts contain no reference to the adapter file, its
  emitter, or its state/session storage (structural independence). The adapter is
  currently `enabled` in this repo, so the test proves independence under the
  stronger enabled state, not only the disabled default the spec assumed.
- AC6 -> `docs/product-success-metrics.md` contains the classification rubric
  text matching Fixed Decision 7 (all-kinds quality bar + tie-break default).
- AC7 -> running `aggregate_rca_ledger.py` against the seed-only committed ledger
  prints `n/a` for the seed-excluded window and exits without printing a baseline
  rate number (assert in a test). **Post slice 2**: the banner now reads
  `auto_append: ON` (wiring is live); the substantive guard AC7 protects — no
  numeric baseline while zero non-seed events exist — is unchanged and still
  asserted.
- AC8 -> `validate_rca_ledger.py` rejects a `caught_by` outside
  `agent | human | gate`, and accepts a record that omits `caught_by`.

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

### Second pass: decision premortem (design lock-in)

A three-angle decision premortem (framing/Goodhart, diagnostic, operational) plus
a counterweight pass ran against the north-star design itself. Packet:
`charness-artifacts/critique/2026-05-24-015131-packet.md`. Counterweight verdict:
lockable now with named edits, no return to ideation. Triage and resolution:

- **Act Before Ship — framing mismatch** (the section called a self-dev process
  metric "the product north-star" while the doc's own user list is operator-value
  framed): relabeled to product north-star = operator/agent task success (named,
  not yet measurable) vs. first instrumented engineering-health objective =
  conversion rate; added the falsifiable correlation assumption and veto power
  for the monitored metrics. (Fixed Decision 1, baseline doc section.)
- **Act Before Ship — operational OFF state** (aggregator could print a seed-only
  or fake-`0%` rate before auto-append): added the OFF banner / `n/a` / refuse
  behavior (Fixed Decision 5, SC7, AC7).
- **Bundle — numerator gaming** (rubric quality bar only covered `retro_lesson`):
  extended to every `durable_kind` plus the `converted=false` tie-break default
  (Fixed Decision 7).
- **Bundle — `caught_by`** (could not tell "harness got smarter" from "human kept
  fixing it"): added nullable `caught_by` enum now, cheap on an append-only
  ledger (Fixed Decision 4, SC8, AC8).
- **Valid but Defer**: independent denominator reconciliation, recurrence rate of
  converted `class_key`s, and the consumer-scope revisit trigger — all deferred
  to the 2-4 week baseline review (Deferred Decisions), because none can produce
  a meaningful number before live non-seed data exists.

No forced debug interrupt is active (`plan_risk_interrupt.py` -> `not-applicable`).

Fresh-Eye Satisfaction: parent-delegated (3 angle subagents + 1 counterweight).

### Third pass: impl code critique (slice 1)

Bounded fresh-eye code critique of the landed slice (3 angle subagents:
correctness/invariants, metric-integrity/Goodhart, maintainability/boundary; plus
1 counterweight). Packet:
`charness-artifacts/critique/2026-05-24-031747-packet.md`. Result:

- **Bundle Anyway (fixed in the slice commit)**: tightened the `ts` field from a
  weak `Z$` pattern (JSON-Schema `format` is advisory and unenforced by the
  default Draft7 validator, so `"not-a-dateZ"` passed) to a full RFC3339 UTC
  regex, with a malformed-`ts` case added to the AC1 fixture; replaced the
  helper-reuse test's substring grep with a runtime `callable(lib.portable_path)`
  assertion so a rename of the reused `_portable_path` helper fails the test
  instead of silently breaking the import.
- **Over-Worry (no change)**: duplicate-JSON-key last-wins (only reachable by
  adversarial hand-edits; the writer emits canonical `sort_keys`); private-helper
  reuse (spec-blessed and now runtime-tested); `seed_included` sanity rate always
  printing (mitigated by the OFF banner and explicit sanity/baseline labels).
- **Valid but Defer**: `validate_rca_ledger.py` exits non-zero on a missing
  ledger while `aggregate_rca_ledger.py` treats a missing ledger as empty
  (exit 0). This asymmetry is correct-by-design — validate asserts the file
  exists; aggregate tolerates a not-yet-seeded ledger — and surfaces loudly if
  wrong, so it is left as-is rather than changed blind.

Fresh-Eye Satisfaction (impl): parent-delegated (3 angle + 1 counterweight subagents).

### Fourth pass: impl code critique (slice 2 — auto-append wiring)

Bounded fresh-eye code critique of the slice-2 diff (4 angle subagents:
Jackson/problem-framing, Weinberg/metric-integrity, Gawande/operational-portability,
Minto/structure; plus 1 counterweight). Packet:
`charness-artifacts/critique/2026-05-24-060248-packet.md`. Result:

- **Act Before Ship (fixed in the slice commit)**:
  - the `debug` closeout bullet buried the presence-gate in a trailing
    parenthetical and dropped the RCA-class qualifier the `issue`/`retro` bullets
    carry (denominator-comparability + consumer "file not found" risk) — rewritten
    to gate in the main clause with the RCA-class qualifier;
  - three stale spec passages (Current Slice, Fixed Decision 5, Success Criterion
    7) still described the pre-slice-2 OFF state and contradicted the Landed
    section and retargeted AC7 — reframed so the quote-safety guard is the live
    invariant and the banner string is the wiring-state indicator.
- **Bundle Anyway (fixed in the slice commit)**: the bare `auto_append: ON`
  deleted the only "do not quote" signal while the seed-included `60.0%` kept
  printing — the ON banner now carries `prompt-enforced; denominator
  self-reported, not gate-verified`, the seed-included header now reads
  `sanity only — do not quote`, and AC7 asserts that guard is present; dropped the
  "without manual discipline" overclaim (a prompt is still discipline).
- **Over-Worry (no change)**: adding a shell `test -f … || exit 0` guard to the
  reference's `How` command — the presence gate is already stated in prose twice
  and in every skill bullet, and shell-gating a deliberately prompt-enforced step
  is belt-and-suspenders.
- **Valid but Defer**: a one-event-per-fix-unit operational definition and a
  non-idempotent-recorder "do not re-append" note (belongs with the deferred
  `class_key` dedup slice, which is the only thing that can actually enforce it);
  explicit "no numeric target until denominator reconciliation runs" wording
  (belongs with the already-deferred reconciliation slice). Both are recorded in
  the slice-2 residual risk and Deferred Decisions.

Fresh-Eye Satisfaction (impl, slice 2): parent-delegated (4 angle + 1 counterweight subagents).

## Canonical Artifact

This file (`charness-artifacts/spec/rca-conversion-ledger.md`) is canonical
during implementation. The metric definition of record stays in
`docs/product-success-metrics.md`.

## First Implementation Slice

1. Add the `rca_event` JSON schema (closed enums incl. nullable `caught_by`,
   bidirectional `none`/`converted` invariant).
2. Implement `record_rca_event.py` (validate-then-append, tie-break default to
   `converted=false` on ambiguity).
3. Implement `validate_rca_ledger.py` and `aggregate_rca_ledger.py` (latter with
   the OFF-state banner / `n/a` / refuse-non-seed-rate behavior).
4. Seed `charness-artifacts/metrics/rca-ledger.jsonl` (`seed=true`) with recent
   real RCA events of BOTH outcomes: converted ones (e.g. #197 symptom->root-cause
   naming, the 2026-05-24 mutation-scope trap that became a retro lesson) AND
   unconverted ones (e.g. a bug that recurred, or a weak-proof finding never
   turned into a gate) so the day-one number is not survivorship-biased.
5. Write the classification rubric (all-kinds quality bar + tie-break default)
   into `docs/product-success-metrics.md`.
6. Add unit tests for AC1-AC8.

## Second Implementation Slice (Auto-Append Wiring) — Landed

Preserve/improve claim:

- **Preserve**: the `debug`, `issue`, and `retro` public skills keep their exact
  closeout behavior in consumer repos. The append step is presence-gated on
  repo-root `scripts/record_rca_event.py` + the ledger, so a consumer install is
  a silent no-op (no new files, no missing-recorder noise).
- **Improve**: in the Charness repo, task-completing `debug`/`issue`/`retro`
  closeouts now append one rubric-anchored RCA event each through one
  standardized closeout step, so the conversion ledger accrues live (non-seed)
  events. The append stays prompt-enforced (closeout discipline), not
  gate-enforced — see the residual risk below.

Landed:

1. `skills/shared/references/rca-ledger-append.md` — one portable, presence-gated
   append contract that defers all judgment calls to the
   `docs/product-success-metrics.md` rubric and the schema (no enum/rubric
   restatement). Per-source mapping, one-event-per-fix-unit rule, tie-break
   default, and the `--seed` prohibition live here.
2. A single closeout bullet + References entry in each of the three public
   `SKILL.md` files citing the shared reference with the correct `--source`.
3. `AUTO_APPEND_WIRED = True`; aggregator/doc banners updated to `ON`; the n/a
   render message updated to "wiring live, awaiting live events".
4. Tests: AC7 retargeted to the ON state while keeping the no-baseline-number
   guard; two slice-2 wiring-proof tests (reference is presence-gated +
   rubric-anchored; all three skills cite it with the right source flag).

Residual risk: the append is **prompt-enforced, not gate-enforced** — an agent
that skips the closeout prompt still under-counts the denominator. This is the
realistic mechanism for a metric whose `event_kind`/`converted`/`class_key`
require judgment a deterministic hook cannot supply. A future slice could add an
advisory closeout nudge (warn when a `debug`/`issue`/`retro` slice closed with no
matching ledger append in the same commit); deferred to keep this slice minimal
and because it depends on the denominator-reconciliation work already deferred to
the baseline review.
