# issue / achieve / hotl — churn static-confirm (predicted ABSENT) + one FIX (2026-07-03)

Serves [intent.md](./intent.md): north = SMARTER agent; test = "그게 정말 최선인가?"
(no proxy). Handoff `Next Session` #1 predicted all three ABSENT. Cold static-check
of each skill's real scaffold + validator + persist path, each with a bounded
adversarial fresh-eye reviewer tasked to REFUTE. **Result: issue ABSENT (earned),
hotl ABSENT (earned), achieve REFUTED on one narrow false-green → FIXED.** The
prediction held for 2/3, and the fresh-eye caught the real defect the prediction
would have shipped — exactly the H0 method's "fresh-eye before commit" payoff.

## The locked heuristic (applied per skill)

Churn PRESENT ⇐ (a) hand-edits its artifact via `Edit` (no persist helper) AND (b)
the run iterates to satisfy an **invisible** validator-format rule — (b1) a
`MAX_*_LINES` ceiling (debug/quality) or (b2) a tool-computable value written as a
PLACEHOLDER (retro's `Persisted`). ABSENT ⇐ one-pass persist stamp, OR no artifact
gate, OR format SURFACED + residual is irreducible judgment (ideation).

## issue — CONFIRMED ABSENT

- **(b1) fails:** grep of the whole issue surface finds no `MAX_*_LINES`/`size_budget`;
  `verify_closeout` never measures body size. No ceiling → no trim loop.
- **(b2) fails:** the only computable token in the stub is `#N` — a `--number`
  CLI input the run already holds, and there is **no write-helper** in the closeout
  path to fold a stamp into. Not the retro shape.
- **(b) invisibility fails on two grounds:** the enforced shape is SURFACED — by
  `describe_closeout_draft_shape.py` (rendered from live enforced constants) AND
  independently by the run's own classification references (`causal-review.md`,
  `resolution-brief.md`, engage-always `closeout-discipline.md`); and `verify_closeout`
  is **report-all, not fail-fast** — one `validate-closeout-draft` call returns the
  COMPLETE violation set, so even a blind-authored body is fixed in one pass, not an
  N-round loop. Fresh-eye VERDICT CONFIRMED-ABSENT (strongest angle: shape command not
  wired into issue's own run path — failed on both grounds above).
- **Sub-threshold nicety (NOT shipped, do not manufacture):** the shape command is
  reachable only via repo-internal `docs/conventions/*`, not from issue's own SKILL.md /
  planner `closeout-draft` gate_packet. A one-line pointer would give the shape one
  front door + help portable deploys. Marginal (shape already surfaced, gate report-all).

## hotl — CONFIRMED ABSENT

- **No artifact gate at all.** `skills/public/hotl/scripts/` ships only adapter
  scripts — no scaffold, no validator, no persist helper. [charness-artifacts/hotl/latest.md](../hotl/latest.md)
  is adapter-owned and registered in NONE of `validate_current_pointer_freshness.py`
  (hardcoded pointer list), `check_artifact_surface_preflight.py` (shape registry), or
  `artifact_validator.py` (a primitives lib, no hotl consumer). No `validate_hotl_*` exists.
- **(b) fails:** the `verified_at`/`source_commit` fields read as computable but are
  deliberate proof bindings (observation time / covered commit) = the proof WORK the
  intent excludes from churn, not `now()`/`HEAD` stubs; and nothing reads them off the
  ledger, so there is no engine to iterate-fail against. Fresh-eye VERDICT CONFIRMED-ABSENT.
- **Sub-threshold note:** the rich ledger schema is entirely unenforced in-repo — that is
  *under*-enforcement (too little gate), the OPPOSITE of churn. Adding a gate here would be
  the reflex the intent forbids. Portable-prose + adapter-owned schema is the design.

## achieve — REFUTED (narrow) → FIXED

Mainline goal closeout is churn-free (earned): no `MAX_*_LINES`; `upsert_goal` stamps the
computed `goal_rel` into `Activation:`; `append_slice_log` appends via tool; the complete-flip
forms are surfaced by `describe_goal_closeout_shape.py` + inline template; residual `TODO`s
bind real artifacts = irreducible judgment. **But one confirmed false-green** in the
timeboxed-early-close subset: for a PRESENT+BOUND early-close report with a hollow section,
`apply_report_shape` sets `invalid_early_close_reports` + `ok=False`, yet that refusal was
surfaced NOWHERE the author reads — `describe`'s row showed "present and well-formed" (false
green) and the CLI tail was an empty `"…evidence not satisfied — "`. The author flips, is
refused with no reason, and reverse-engineers it from raw JSON: the discover-by-failing loop
the describe-first architecture exists to kill. Meets (a)+(b). Fresh-eye proved it with an
isolated harness.

**Fix (surface-it, NOT a new floor — the floor already blocks; this makes its failure
honest, the direction intent.md endorses):** `_evidence_unsatisfied` (describe) and
`_evidence_missing_bits` (`check_goal_artifact`) each grew a branch reading the live
`invalid_early_close_reports` field (drift-free). Two reader tests + one CLI-tail test pin
the realistic hollow-body case (`## Waste and retro` = `None.`). No `ok=False` site added →
floor-addition-restraint detector correctly silent. Plugin mirror synced byte-identical.

## Method note

Static-check predicted 3/3; capture spent on 0 (all predicted non-hits or a
surface-only fix). The fresh-eye refutation — not a capture — is what turned a
predicted ABSENT into a real fix. Two sub-threshold niceties recorded above,
deliberately unshipped as marginal over-build.

## Validation review (achieve public-skill change)

Routed through `quality` posture. The fix is a DETERMINISTIC reader-surfacing
change: it alters neither `achieve` routing nor the durable goal-artifact's
content/acceptance (which goals pass/refuse is byte-identical), so the quality
dogfood trigger ("risk is public-skill routing or durable artifact behavior")
does NOT fire. Correct proof tier = deterministic unit tests (3 added), not a
capture/A-B. The existing reviewed achieve dogfood case's `acceptance_evidence`
is untouched → no dogfood-contract update. Cautilus `next_action: none`
(ask-before-run, no failing-log path) → no eval run. `hitl-recommended` review
satisfied by the bounded fresh-eye slice critique (VERDICT SOUND, tests proven
to fail on pre-fix HEAD). Decision: closeout-acked, no eval/dogfood change.
