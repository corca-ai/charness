# debug H0 — closeout trim-to-fit churn lever: diagnosis + mechanism (behavioral proof DEFERRED, 2026-07-03)

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

**Status: mechanism landed, churn-reduction UNPROVEN.** The fix is additive,
deterministically verified, and harmless — but a behavioral re-capture is the
proof gate (see Honesty below). Do not claim the lever is "fixed" yet.

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

## Honesty — why this is "mechanism landed," not "fixed" (fresh-eye defect #1)

The fix rests on mechanism + the 178-line disconfirmer; it does **not** prove a
real run *heeds* a JSON `size_budget` + one SKILL.md sentence. The same 4 captures
**contradict the optimistic prior**: every debug run **skips the planner's
surfaced required reads** (`five-steps.md`/`debug-memory.md`) — i.e. this skill
demonstrably ignores some surfaced guidance. So "surface it → run heeds it" is
weakly supported *here specifically*. The repo's bar for a landed behavioral lever
is a re-capture at n≥2 (how Plan A/C were proven), not mechanism alone.

**Proof gate (deferred):** a fresh `/charness:debug` capture on the current fix
vs the pre-fix baseline (same planted bug: a non-gitignore-aware scanner on a
scratch branch), comparing Edit/`wc -l` churn. Two honest outcomes:
- churn drops → lever confirmed, claim it then.
- churn persists → the budget rides a channel debug ignores; escalate the
  mechanism (planner-enforced, or scaffold pre-sizes sections) — a real finding.

## Secondary (NOT acted on — scope discipline)

The `size_budget` rides the `--json` payload only; a bare rendered-template
invocation has no budget line. Verified covered (planner + SKILL.md + adapter all
use `--json`). Not added to the template on purpose — a comment there would
persist into the artifact and *consume* the 180 budget it is trying to protect.
