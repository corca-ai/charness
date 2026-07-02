# debug H0 — closeout trim-to-fit churn lever: diagnosis + fix (PROVEN by controlled A/B, 2026-07-03)

Serves [intent.md](./intent.md): north = SMARTER agent; sole test = "그게 정말
최선인가?" (no proxy). Second executed lever-hunt after the quality pilot; picked
`debug` to test the **churn/ritual lever class** (not references — spec's H0
re-confirmed refs are not the drain). Fresh-eye review: SOUND-WITH-DEFECTS.

## Headline

debug's dominant closeout cost is a **trim-to-fit churn loop**: a run writes a
rich RCA, blows past the validator ceiling `MAX_ARTIFACT_LINES=180`
(`scripts/validate_debug_artifact.py:67`), then loops `Edit→wc -l→Edit` to trim —
because **180 is invisible everywhere the agent sees pre-write** (grep the debug
surface for `180`/`budget` → empty). This is quality's closeout-churn lever class
in a new flavor, and the tax falls hardest on debug's *highest-value* runs (many
siblings / rich detection-gap = most overshoot).

**Status: PROVEN by a controlled A/B re-capture (2026-07-03).** Same session, same
real bug, same prompt — only the fix differs. Churn is structurally eliminated
(37→7 edits, 19→0 `wc -l`) while the artifact stays complete, and the agent
*heeded* the surfaced budget (wrote 152/180 with headroom + abstracted Sibling
Search) — refuting the fresh-eye's "debug ignores surfaced guidance" worry. See
`## Proof` below.

## Evidence (4 preserved captures, `charness-artifacts/cautilus/debug-claim-fidelity-2026-06-30*/`)

All on the current debug surface (Plan A `ce3caa6c` + Plan B `853a5174`; scaffold/
SKILL untouched since, until this fix). Edit / `wc -l` counts:

| capture | output | wall | Edit | wc-l | note |
|---|---|---|---|---|---|
| base | 178k | 14m | 21 | ~ | repeated_edit |
| recapture | 167k | 13m | 13 | ~ | repeated_edit |
| plan-a-recapture | 115k | 10m | 5 | 0 | "lean" — but shipped a **265-line over-ceiling** artifact (opposite failure) |
| **plan-c-capture2** | **192k** | **20m** | **36** | **17** | the churn in full |

- **It is a trim loop, not authoring.** plan-c trace steps 24-72 are a tight
  `Edit→Edit→wc-l` cycle *after* the artifact was already written; steps **73-76**
  are decisive — the run executes `rg "180|grows past|concise"` + `sed` on
  `validate_debug_artifact.py` + `rg MAX_ARTIFACT_LINES`, i.e. **reverse-
  engineering the ceiling from source mid-loop** because it is invisible pre-write.
- **H-b, not H-a (disconfirmed the "ceiling too tight" hypothesis).** plan-c's
  final artifact is **178 lines, all 14 sections dense and complete** (falsifiable
  hypothesis + 2 falsifiers, 6-step root-cause chain, per-sibling scan, 4
  prevention moves), substance-graded 6/6. A complete excellent RCA fits under
  180 → the ceiling is adequate; its *invisibility* is the fault. So the fix
  surfaces the ceiling, it does NOT raise it.

## The fix (mechanism — mirrors the quality pilot: channel intelligence via scaffold + gate stdout)

1. **Scaffold surfaces the budget.** `scaffold_debug_artifact.py` single-sources
   `MAX_ARTIFACT_LINES` from the validator (import, try/except graceful fallback)
   and passes `size_budget={max_lines, guidance}` through the shared
   `current_pointer_payload` (new optional field; quality's scaffold omits it,
   unchanged). `guidance` routes the run to the `## Sibling Search` abstraction
   rule (the recurring overflow). SKILL.md tells the run to write-to-fit on the
   first pass. The planner embeds the payload and invokes `--json`, so the budget
   surfaces at the first planner read, before writing.
2. **Validator reports the overage.** `validate_max_lines` now says "is N lines …
   cut ~M" (keeps the `should stay concise` substring other gates match) — kills
   the `wc -l` half of the loop when overshoot still happens.

Verified deterministically: scaffold emits `size_budget`; validator reports
count+overage; single-source drift structurally impossible (no literal `180` in
the debug surface) + drift-guarded by `tests/test_debug_scaffold.py`; plugin
mirror byte-identical; **2480 quality_gates pass** (was 2475 + 2 new tests).

## Proof — controlled A/B re-capture (2026-07-03)

Two live `/charness:debug` captures in the same session, same fixture prompt, both
reproducing the same real bug (`validate_attention_state_visibility.py:173` raw
`rglob`). The ONLY difference is the fix: BASELINE at `9911a418` (pre-fix) vs FIX
at `e012c8aa` (HEAD). The bug is content-rich (Sibling Search finds ~15 real
scanners), i.e. exactly the overshoot-prone case.

| metric | BASELINE (pre-fix) | FIX (size_budget) | Δ |
|---|---|---|---|
| Edits to the artifact | **37** | **7** | 5.3× fewer |
| `wc -l` invocations | **19** | **0** | eliminated |
| tool calls | 108 | 66 | 1.6× |
| wall | 18.1 min | 10.6 min | 1.7× |
| cost | $7.99 | $3.95 | 2× |
| output tokens (tree) | ~175k | ~98k | 1.8× |
| final artifact | **180 lines — pinned AT the ceiling (trimmed to the wire)** | **152 lines — wrote-to-fit with headroom** | both complete (14–15 sections) |

- **The trim loop is gone.** `wc -l` 19→0: the FIX run never manually measured
  line count, because it wrote-to-fit and (had it overshot) the validator now
  reports the overage. The BASELINE's 19 `wc -l` + 37 edits pinned the artifact to
  *exactly* 180 — the signature of fighting an invisible ceiling.
- **The guidance was heeded.** The FIX Sibling Search is abstracted to
  mental-model + axis lines (`same layer` / `abstraction up` / `specialization
  down` / `cross-file`), not an exhaustive per-sibling enumeration — exactly what
  `SIZE_GUIDANCE` asked. So the surfaced budget DID change behavior here.
- **Not a variance artifact.** BASELINE's 37 edits / 19 `wc -l` sits at the top of
  the pre-fix range (prior captures: 5–36 edits); the FIX's 0 `wc -l` is *below the
  entire pre-fix range* (churny runs were 17–19) — a categorical difference, not a
  lucky low draw. (n=1 controlled A/B; the control is stronger than n=2 uncontrolled.)
- **Orthogonal caveat:** both arms still miss the `debug-memory.md` RCF (a known,
  documented, not-yet-internalized gap — unrelated to churn; unaffected by this fix).

## Honesty — original scope note (fresh-eye defect #1), now RESOLVED by the A/B

The fresh-eye rightly flagged that the fix initially rested on mechanism + the
178-line disconfirmer, and that the pre-fix captures **contradicted the optimistic
prior** — every debug run skips the planner's surfaced required reads
(`five-steps.md`/`debug-memory.md`), i.e. this skill demonstrably ignores *some*
surfaced guidance. So "surface it → run heeds it" was not safe to assume; the
repo's bar is a re-capture, not mechanism alone.

**That gate is now met.** The controlled A/B above ran it and the churn dropped
categorically (see `## Proof`). The `size_budget` is a different channel from the
required-reads the run skips — a small inline fact in the payload the run already
consumes for `write_artifact_path`, not a "go open this doc" — and empirically the
run *did* heed it (152/180 + abstracted siblings). Claim stands: fixed.

## Secondary (NOT acted on — scope discipline)

The `size_budget` rides the `--json` payload only; a bare rendered-template
invocation has no budget line. Verified covered (planner + SKILL.md + adapter all
use `--json`). Not added to the template on purpose — a comment there would
persist into the artifact and *consume* the 180 budget it is trying to protect.
