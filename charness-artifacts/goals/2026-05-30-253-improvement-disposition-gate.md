# Achieve Goal: Improvement-disposition closeout gate (validator teeth, #253)

Status: active
Created: 2026-05-30
Activation: `/goal @charness-artifacts/goals/2026-05-30-253-improvement-disposition-gate.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

Give the achieve After-phase disposition rule teeth via **two complementary
rungs**, not one fuzzy regex (the "gate + 지능" synthesis):

1. **Deterministic floor (게이트):** at the `--status complete` flip, refuse to
   close a goal green when its cited Retro surfaced actionable improvements but
   the `## Auto-Retro` is **blank/absent**, AND require evidence that a
   disposition review actually ran (a bound `Disposition review:` line, mirroring
   the existing `Retro:` / `Host log probe:` evidence pattern). Cheap, offline,
   clone-safe, ungameable.
2. **Recorded intelligence (지능):** the substantive call a regex cannot make —
   *did the Auto-Retro genuinely disposition each retro improvement?* — is made
   by a **fresh-eye subagent** at closeout that reads the retro + Auto-Retro and
   records a per-improvement verdict a human can audit.

The gate proves the *process* happened and catches the unambiguous blank;
intelligence supplies the *judgment*; the human reads both. No prose word-list
anywhere. This keeps it Engelbart augmentation — each tool does what it is good
at — rather than a mechanical classifier (the design the round-2 critique proved
unshippable).

## Non-Goals

- **NOT a regex / prose word-list classifier (round-2 critique, decisive).** The
  deterministic rung does **not** try to decide whether a non-empty Auto-Retro
  "really" disposed each improvement. A word-list (`filed`/`applied`/…) drifts,
  cannot tell "I filed it" from "I did **not** file it" (polarity), and is
  gameable — and the live corpus proved it either over-fires or passes pure
  narration. That fuzzy judgment is the fresh-eye reviewer's job, not a regex's.
- **Not adjudicating disposition _quality_ deterministically.** Whether an
  `applied:` was the right teeth, or a filed `issue #N` well-scoped, is the
  reviewer's + human's judgment. The deterministic rung never scores substance.
- **Not forcing a count match.** `dispositions == improvements` is never a hard
  block. If surfaced at all it is advisory (the fresh-eye reviewer reports
  per-improvement coverage; the deterministic gate does not count). Explicit
  walk-back of #253's "count ≈ count" as a block-condition — see Interview Q2.
- **Not claiming a fully deterministic substantive check.** By design the
  substantive disposition judgment is **agent-backed (non-deterministic)** and
  host-dependent; the deterministic rung only proves the review *ran* and catches
  the *blank*. #253's literal "deterministic check" becomes "deterministic floor
  + recorded intelligent review". Named honestly, not hidden.
- **Not a slice-time gate.** No change to `append_slice_log.py`; closeout only.
- **Not changing the disposition _rule_'s two forms.** `applied:` / `issue #N`
  (agent's now-vs-next judgment) stand. But SKILL.md's "exactly two / mandatory"
  wording must be reconciled with the new `Disposition review:` rung + opt-out
  (repo-fit critique R4) — a doc reconciliation, not a rule change.
- **Not making narration (#233 F2) blocking.** `narration_required_sections`
  stays a non-blocking affordance. **Why narration is non-blocking but
  review-existence IS blocking (round-3 engelbart R3 — principled, not drift):**
  the line is *deterministic-inspectability of the gated thing*. You can
  ungameably check "is there a bound `Disposition review:` line in the goal body"
  (same surface as `Retro:`, offline, clone-safe); you cannot ungameably check
  "did the agent narrate substance in the transcript" (a hard transcript gate
  over-fires). Same Engelbart principle twice: gate the gateable, leave the
  over-firing thing an affordance.

## Boundaries

- **Engelbart "gate + 지능" principle (load-bearing — overrides convenience).**
  Determinism and intelligence each do only what they are good at. The
  deterministic rung catches the unambiguous mechanical omission (a blank
  Auto-Retro) and verifies the review *ran*; it never classifies prose. The
  fresh-eye reviewer makes the substantive judgment (did the Auto-Retro
  disposition each improvement?) and records it for a human. Neither is forced
  into the other's job. A deterministic false-positive is worse than a
  false-negative — it trains token-theater — so the deterministic teeth stay
  narrow and ungameable.

- **RUNG 1 — deterministic floor (in `check_complete_evidence`).**
  - **(1a) Block the blank.** Bound Retro lists ≥1 actionable improvement **and**
    the goal's `## Auto-Retro` section is **absent or empty/whitespace** (after
    `_mask_fences`, scanned over the Auto-Retro span only) **and** no opt-out ⇒
    refuse the flip. Unambiguous, offline, clone-safe; you cannot game "write a
    real Auto-Retro section" the way you can game "include the word `filed`".
  - **(1b) Require the review ran.** Add `disposition_review` to
    `CLOSEOUT_EVIDENCE_NAMES` so the goal body must carry a bound
    `Disposition review: <path>` (or `Disposition review: skipped: <enum>:
    <detail>`). **Build note (round-3 impl B1, verified — NOT tuple-only):**
    `_EVIDENCE_LINE` hard-codes `(Retro|Host[- ]log[- ]probe)`, so slice 2 must
    add a `Disposition[- ]review` alternation arm or the line is silently dropped
    and every post-rule goal is refused. The binding loop, skip-enum
    (`host-blocked-subagent` already allowed), and `_normalize_evidence_name` all
    compose automatically — verified.
  - **(1b) is presence/binding-only BY DESIGN (round-3 regress + engelbart).** It
    checks the line exists and binds to *this* goal, never the artifact's
    *content* — the same labor split block-the-blank uses. It does not "stop" the
    recursion so much as **move the floor to the only honest point**: from "did
    anyone disposition" (capture-without-apply) to "did a fresh-eye review run +
    bind". The residual — "was the review rigorous" — is the human-audit +
    reviewer-honesty boundary, **accepted, not closed** (determinism categorically
    cannot verify judgment quality). A future reviewer must NOT tighten 1b into a
    content classifier — that re-imports the round-2 word-list trap one level up.
  - Surface results through the same report `upsert_goal --status complete`
    (block) and `check_goal_artifact.py` (post-flip) already consume.

- **RUNG 2 — fresh-eye disposition review (the intelligence).** The After-phase
  already mandates a bounded fresh-eye closeout review (repo contract); this
  gives that reviewer an explicit added mandate: read the cited Retro's
  `## Next Improvements` + the goal's `## Auto-Retro`, and record a
  **per-improvement verdict** (dispositioned `applied:`/`issue #N`/explicit-none,
  or undispositioned) into a review artifact the `Disposition review:` line
  binds. Non-deterministic by nature — that is the point; it is judgment, made
  visible and auditable, not a hidden pass. Near-zero marginal cost: it scopes an
  already-required review, it does not add a new agent.

- **Grandfather by rule-landing date (round-2 + round-3, verified).** Both rungs
  fire only for goals `Created:` **>= 2026-05-30** (inclusive — the rule
  `73d2d34` landing date; this very goal, Created 2026-05-30, is therefore
  in-scope and dogfoods the gate). Key on **`Created`, not completion date**
  (round-3 impl R3): a goal *shaped* before the rule existed had no chance to
  plan its Auto-Retro/review around it, so Created-keying grandfathers exactly the
  in-flight goals; completion-keying would punish them. Clone-safe (in-file
  content, not mtime). **Parse fail-CLOSED (round-3 impl R1):** a
  missing/malformed `Created:` ⇒ treat as in-scope (gate applies), parsed via a
  masked regex like `read_status` + `date.fromisoformat`, so a goal cannot dodge
  both rungs by corrupting one line. **Wiring (round-3 impl R6):**
  `check_complete_evidence` does not currently see `Created`; thread the date in
  and have it gate BOTH rungs (else grandfathered goals would still fail rung-1b
  for a `Disposition review:` line they never had). Verified TPs
  `230-229-self-substitution` / `handoff-chunked-routing` (Created 2026-05-28)
  stay exempt — blocking historical goals on `charness update` is the wrong fix;
  grandfathering bounds the blast radius (R6) while keeping the rungs sharp.

- **Calibration = discovery, not "assert 0" (round-2 critique).** Run the rung-1
  detector over every completed goal: confirm pre-rule goals are grandfathered
  (0 deterministic refusals) and that the detector *would* flag the 2 TPs if they
  were post-rule (sanity that the floor isn't inert). The original "assert 0
  newly-refused" baked in a false premise ("all carry some signal") and would
  have forced neutering — replaced.

- **Auto-Retro–scope all parsing (round-2 critique B-2, verified).** Detect the
  blank, the opt-out, and any signal **within the `## Auto-Retro` span only**
  (slice H2→next-H2, like `narration_sections_present`). A full-text
  `_TRIVIAL_GOAL_MARKER.search(text)` is **poisoned**: both TP goals' bodies
  contain "single-slice goal" while *describing* the marker (verified: 1 and 5
  matches), which would falsely exempt 7-slice goals. Do NOT reuse the full-text
  scan; scope it.

- **Opt-out (expressible deviation, Auto-Retro-scoped).** An explicit
  `Retro dispositions: none — <reason>` line (min length, mirror the `skipped:`
  discipline) lets a deliberate "no disposition needed" pass, recorded visibly.
  This is the "say why if you depart" Engelbart valve, not a silent skip.

- **Home + export budget (round-2 + round-3, verified: lib 358 / fail-360, only
  2 lines headroom).** New logic lives in `goal_artifact_closeout_evidence.py`
  (231 lines, ample). Tests currently reach closeout symbols ONLY via the lib's
  `gal.<fn>` re-exports, so a new re-exported symbol → 359/360 and a second →
  360 hard-fail. **Decision (round-3 impl R4 / engelbart R5 — pre-committed, not
  an open either/or):** new disposition tests load
  `goal_artifact_closeout_evidence.py` **directly** (a 3-line importlib block,
  like the existing pattern) so the lib gains **zero** new re-export lines.

- **Host portability + skip honesty (round-3 regress R3).** A subagent-blocked
  host cannot run rung 2 ⇒ `Disposition review: skipped: host-blocked-subagent:
  <detail>` (existing enum) ⇒ graceful degradation to rung 1 only. **Rung-1a
  (block-the-blank) MUST still fire under the skip** — confirm this independence
  in code (a skipped review must not also disable the blank check). A
  `host-blocked-subagent` skip on a host that demonstrably *can* spawn (CLAUDE.md:
  soft prompts are not blockers) is itself an audit-flag for the human reader, not
  a clean pass. Matches CLAUDE.md's "report the concrete host signal" contract.

- **Sync barrier (hard — name the real command, repo-fit critique R1).** The
  `plugins/charness/skills/achieve/...` mirror is regenerated by
  `python3 scripts/sync_root_plugin_manifests.py --repo-root .` and verified by
  `validate_packaging.py` + `validate_packaging_committed.py` — do **not**
  hand-edit the export. Run `check_changed_surfaces.py` / `run_slice_closeout.py`
  at the doc slice (it spans `skill-packages` + `prompt-behavior-proof`).
  `mutate → sync → verify → publish`.

- **Honest docs — three surfaces, not two (repo-fit R4 + round-3 engelbart R1).**
  Update lifecycle.md ("After-phase evidence gate"),
  `docs/prescribed-skill-closeout-contract.md`, **and** `SKILL.md`. The SKILL.md
  reconciliation is a **narrow widening, not a contradiction**: the "exactly two
  forms" rule is **per-improvement** (each improvement that exists is applied or
  filed); the opt-out is a **per-goal** assertion that *no actionable improvement
  exists to disposition* — different scopes, no conflict. State that in one
  sentence, and make the opt-out `<reason>` a **factual claim rung-2 can falsify**
  (the reviewer reads the retro and contradicts a false "none") so it is an
  expressible-falsifiable deviation, not a second escape box. Describe both rungs,
  the grandfather rule, and the agent-backed-non-determinism limit truthfully.

- **Cautilus posture (repo-fit critique R3).** lifecycle/SKILL doc edits are
  prompt-affecting but **on-demand**; no live Cautilus run is triggered by prose
  diffs. Closeout states "prompt-affecting, on-demand Cautilus not triggered".

## User Acceptance

What the user can do to verify completion directly:

- **Rung-1 block-the-blank:** a post-rule goal (Created ≥ 2026-05-30) whose
  `## Auto-Retro` is empty/absent while its cited Retro lists ≥1 improvement →
  `upsert_goal.py --status complete` → `action: refused`. Add a real Auto-Retro
  (or the opt-out line) → flip.
- **Rung-1 review-ran evidence:** a goal with a populated Auto-Retro but **no**
  `Disposition review:` line → refused with a `disposition_review` evidence-
  missing reason. Add a bound `Disposition review: <path>` (or
  `skipped: host-blocked-subagent: <…>`) → flip. (Mirrors how missing `Retro:`
  is already handled.)
- **Rung-2 intelligence:** the fresh-eye reviewer records a per-improvement
  verdict; for a disposition-less-but-non-empty Auto-Retro (the 2 corpus shapes)
  it flags the uncovered improvements — the call a regex could not make. **The
  gate checks only that the review artifact exists + binds to this goal; a human
  reads the verdict's content** (rung-1 never scores it — round-3 regress R4).
- **Grandfather:** the 8 pre-rule completed goals are untouched (no new refusal)
  — run the rung-1 detector over the corpus and confirm 0 deterministic refusals.
- **Host degradation:** on a subagent-blocked host, `Disposition review: skipped:
  host-blocked-subagent: <…>` flips green with the skip named.
- **Tests:** the suite gains cases for block-the-blank / review-ran-evidence
  presence+binding+skip-enum / grandfather-by-date / Auto-Retro-scoped opt-out
  (not poisoned by body prose) / fence-safety / absent-Auto-Retro, and they pass.

## Agent Verification Plan

### Low-Cost Checks (deterministic — rung 1)

- **Corpus-discovery runner** over all completed goals → confirm pre-rule
  grandfathering (0 deterministic refusals) and that the detector would flag the
  2 TPs if post-rule (floor-not-inert sanity). Highest-signal cheap check.
- `pytest` over the achieve-scripts tests (new rung-1 cases + existing
  closeout-evidence cases — no regression).
- `check_python_lengths` on every touched `.py` (`goal_artifact_lib.py` 358/360
  — verify the test-import/re-export path first per Boundary).
- Real plugin-mirror sync (`sync_root_plugin_manifests.py`) +
  `validate_packaging_committed.py`; `check_changed_surfaces.py` at the doc slice.
- Targeted `upsert_goal.py --status complete` / `check_goal_artifact.py` runs
  over hand-built fixtures per branch.

### High-Confidence Checks (incl. the agent-backed rung 2)

- **Dogfood rung 2 for real:** this goal's own closeout spawns a fresh-eye
  subagent that reviews *this goal's* disposition coverage and writes the bound
  `Disposition review:` artifact — exercising rung 2 end-to-end, not just rung 1.
- Full repo quality gate via `quality` (pre-commit + pre-push), incl. the
  **mutation gate on changed lines** — #251 method: gate's own subprocess-
  capturing coverage, not a naive `coverage run`. Cost: moderate.
- Test-duplication pressure: **low–moderate** — share fixture builders; watch the
  adjacent-duplicate gate (#251).

### External Or Live Proof

- **None (provider/live/release).** Honestly named limits: (a) the substantive
  rung is **agent-backed / non-deterministic** and host-dependent — not a pure
  offline validator; (b) regex can't verify an `issue #N` is real/open. **Residual
  risk (R6, now bounded):** post-`charness update` refusal reaches operators, but
  grandfathering means **only post-rule goals** are affected; the version-bump +
  update-note decision is tracked Off-Goal.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | **Rung-1 deterministic floor**: Auto-Retro-scoped blank detection + grandfather-by-`Created`-date + Auto-Retro-scoped opt-out (un-poisoned), fence-safe; corpus-discovery runner (pre-rule → 0 refusals, would-flag-TPs sanity) | The deterministic teeth must be proven against the live corpus (grandfather works, opt-out not poisoned) before anything else builds on them | Unit tests (blank/non-blank, date-grandfather, scoped-opt-out vs body-prose poisoning, absent Auto-Retro, fenced) + corpus runner output | planned |
| 2 | **Rung-1 review-ran evidence**: add `disposition_review` to `CLOSEOUT_EVIDENCE_NAMES` **AND extend the `_EVIDENCE_LINE` regex with a `Disposition[- ]review` arm** (round-3 B1 — tuple-only silently drops the line); thread `Created`-date into `check_complete_evidence` to gate both rungs; tests load the closeout module directly | Closes #253's recursion; the regex + date-threading are the two non-obvious wiring points round-3 verified | refused without the line, flips with a bound line or `skipped:` enum; grandfathered goals unaffected; `check_python_lengths` green | planned |
| 3 | **Rung-2 mandate + docs + sync**: define the fresh-eye disposition-review mandate, output shape, and binding; wire into lifecycle.md After-phase; reconcile SKILL.md "exactly two/mandatory"; `prescribed-skill-closeout-contract.md`; real `sync_root_plugin_manifests.py` + packaging verify; `check_changed_surfaces` | Sync-before-verify barrier; three doc surfaces (incl. SKILL.md, repo-fit R4) must match behavior before closeout | Docs diff across all three surfaces; passing packaging-committed + changed-surfaces checks | planned |
| 4 | **Dogfood + final gate** (ORDER matters, round-3 R5: ①spawn reviewer → it writes the review artifact, ②add the bound `Disposition review:` line + fill `## Auto-Retro`, ③THEN flip — else the gate refuses its own closeout); broad quality gate (mutation on changed lines, #251 method) | Exercises rung 2 end-to-end on the goal itself; final confidence | The bound review artifact; this goal flipping green through BOTH rungs; quality-gate output | planned |

## Slice Log

_No slices yet — the goal is inert until activated with `/goal`._

### Slice 1: Rung-1 deterministic floor (block-the-blank + grandfather + opt-out)

- Objective: Build the offline, clone-safe deterministic floor: grandfather-by-Created-date, Auto-Retro-scoped blank detection, retro Next-Improvements presence (structure only), and the Auto-Retro-scoped reasoning opt-out; wire rung-1a into check_complete_evidence; prove it against the live corpus.
- Why this approach: The deterministic teeth must be proven against the live corpus (grandfather works, opt-out not poisoned) before rung-1b/rung-2 build on them (round-2/3 R5: regression moved to slice-1 exit criterion).
- Commits: (bundled with slice 2 in the code commit — both touch check_complete_evidence/_EVIDENCE_LINE; sync barrier means one mutate->sync->verify->publish)
- What changed: NEW skills/public/achieve/scripts/goal_artifact_disposition.py (leaf module: DISPOSITION_RULE_DATE, goal_created_date, disposition_gate_applies, _section_body, auto_retro_is_blank, retro_lists_improvements, find_disposition_optout, apply_disposition_rungs). goal_artifact_closeout_evidence.py: load sibling + call apply_disposition_rungs at end of check_complete_evidence. NEW audit_disposition_corpus.py corpus runner. NEW tests/quality_gates/test_goal_disposition_gate.py (21 cases).
- Alternatives rejected: REJECTED inlining the logic into goal_artifact_closeout_evidence.py (the goal's stated home): the rung-1 logic is ~180 lines and pushed that file to 411 (>360 hard limit) and would have wedged slice 2 against the cap — the exact silent-near-limit-file trap recent-lessons flags twice. Extracted to a leaf module instead (same separable-concept split that created closeout_evidence from the lib). goal_artifact_lib.py stays at 358 with ZERO re-export growth.
- Targeted verification: 48 tests pass (21 new disposition + 27 existing goal-artifact, no regression). check_python_lengths exit 0 on all touched .py (lib unchanged 358; new files well under 360). Corpus runner: 7 pre-rule grandfathered -> 0 rung1a refusals; 0 in-scope blank refusals.
- Test duplication pressure: Added a dedicated new test file (test_goal_disposition_gate.py, ~190 lines) loading both modules directly; fixture builders (_build_goal/_seed_evidence) shared in-file to limit duplication. New file well under TEST_FILE_WARN 720. No adjacent-duplicate pressure introduced (separate file, distinct fixtures from test_goal_artifact_lib.py).
- Critique: Self-review caught a section-scan off-by-one (empty Auto-Retro absorbing the next H2) before tests — fixed + regression-tested (test_auto_retro_empty_section_does_not_absorb_next_section). Fresh-eye slice critique deferred to the bundled code commit / After-phase bounded review.
- Off-goal findings: CALIBRATION DISCOVERY: goal 2026-05-30-issue-251 is Created 2026-05-30 (in-scope by Created-keying) but was closed ~80min BEFORE the rule commit 73d2d34. Its Auto-Retro is non-blank (rung-1a correctly silent) but it lacks a Disposition review line, so rung-1b (slice 2) will show a check_goal_artifact diagnostic on re-check (never a re-refusal: the flip-guard only fires on non-complete->complete). Corpus is 7 pre-rule + 1 in-scope, NOT '8 pre-rule' as User Acceptance phrased it. Accepted per pre-committed Created-keying + R6; documented, not silently exempted.
- Lessons carried forward: The goal's 'home = closeout_evidence, 231 lines ample' estimate was wrong (additions ~180 lines > headroom). The leaf-module split is the durable fix and keeps both files + the lib off the line gate. Carry into slice 2: add the Disposition[- ]review regex arm + conditionally extend required by disposition_review when in-scope — both small edits to closeout_evidence, no module-size pressure.
- Metrics: when available (host token/time metrics not surfaced inline)

### Slice 2: Rung-1b review-ran evidence (Disposition review: line)

- Objective: Require in-scope goals to carry a bound 'Disposition review: <path>' (or 'skipped: host-blocked-subagent: <detail>') line so a fresh-eye disposition review provably ran; thread the Created-date grandfather so it gates BOTH rungs.
- Why this approach: Closes #253's recursion (the apply rung). The _EVIDENCE_LINE regex arm + required-list threading are the two non-obvious wiring points round-3 verified (B1).
- Commits: (this commit — bundled with slice 1)
- What changed: goal_artifact_closeout_evidence.py: added Disposition[- ]review arm to _EVIDENCE_LINE (B1: tuple-only silently drops the line); DISPOSITION_REVIEW_EVIDENCE constant; check_complete_evidence computes in_scope once and appends disposition_review to required only when in-scope (gates both rungs); rung-1a call reuses in_scope. goal_artifact_lib.py: reworded refusal note to cover the disposition rungs (NET ZERO lines — stays 358). check_goal_artifact.py: surface disposition_blank in the diagnostic. 7 new rung-1b tests.
- Alternatives rejected: REJECTED adding disposition_review to the CLOSEOUT_EVIDENCE_NAMES tuple alone (round-3 B1): _EVIDENCE_LINE hard-codes the label alternation, so the line would be silently dropped and every in-scope goal refused. REJECTED keying grandfather on completion date (goal Interview decision): Created-keying grandfathers in-flight goals that had no chance to plan around the rule. REJECTED adding lines to goal_artifact_lib.py (358/360): reworded the note in place.
- Targeted verification: 58 tests pass (no regression; 2 slice-1 'passes' tests correctly updated to supply a review line now that in-scope goals require one). Smoke: parse+normalize of Disposition review/-review, skip-enum, required-threading, grandfather exemption, binding. check_python_lengths exit 0 (lib still 358, zero growth). Sync + validate_packaging clean; new modules mirrored.
- Test duplication pressure: 7 cases added to the existing test_goal_disposition_gate.py via shared _build_goal(review_line=...) + _seed_review builders — no new file, no adjacent-duplicate pressure. File still well under TEST_FILE_WARN 720.
- Critique: Self-review: confirmed rung-1a fires independently of a rung-1b skip (host portability) via test_block_the_blank_fires_independently_of_review_skip; confirmed _normalize_evidence_name composes ('Disposition review' -> disposition_review) without an explicit arm. Fresh-eye bounded review deferred to After-phase.
- Off-goal findings: Re-ran corpus runner with rung-1b live: 251 now evidence_ok=false (missing Disposition review line) — the documented R6 retroactive-diagnostic case (never a re-refusal; upsert flip-guard only fires non-complete->complete). Pre-rule 7 goals still 0 refusals.
- Lessons carried forward: Adding a required evidence name retroactively breaks slice-1 'passes' tests that assumed no review line — expected coupling, fixed by supplying a bound review line to isolate each rung. Carry into slice 3: docs must state the per-improvement (two forms) vs per-goal (opt-out) scope distinction and that rung-1b is presence/binding-only (not a content classifier).
- Metrics: when available

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **Issue #253** — the observed gap (loaded-prose-only disposition rule) and the
   non-prescriptive suggestion (deterministic After-phase check + advisory
   posture + count cross-check).
2. **Commit `73d2d34`** — "require explicit disposition of every retro/run
   improvement at closeout"; the rule this goal gives teeth.
3. `skills/public/achieve/references/lifecycle.md` — After-phase, "Improvement
   disposition" subsection, and "After-phase evidence gate" (the doc surface to
   update).
4. `skills/public/achieve/scripts/goal_artifact_closeout_evidence.py` — the
   implementation home; already reads + binds the cited `Retro:` file.
5. `skills/public/achieve/scripts/goal_artifact_lib.py` — `check_goal`,
   `_TRIVIAL_GOAL_MARKER` / `Single-slice goal:` opt-out pattern, `_mask_fences`.
6. Real retro samples showing `## Next Improvements` bullet shapes incl.
   self-dispositioned forms:
   `charness-artifacts/retro/2026-05-30-issue-251-mutation-coverage.md`,
   `charness-artifacts/retro/2026-05-29-check-python-lengths-precommit-gate-closeout.md`.
7. `docs/prescribed-skill-closeout-contract.md` — the closeout-evidence contract
   doc.
8. **Verified true-positive goals (round-2 evidence):**
   `charness-artifacts/goals/2026-05-28-230-229-self-substitution-pattern.md` and
   `2026-05-28-handoff-chunked-routing.md` — 7-slice, pre-rule, disposition-less
   Auto-Retros; the live instances of #253's hole and the reason for
   grandfathering + Auto-Retro scoping.
9. #251 closeout discussion — origin context the issue cites.

## Interview Decisions

- **Q1 — Gate strength.** Options considered: {graduated hard gate,
  strict proportional gate, soft affordance only}. **Chosen: graduated hard
  gate.** Rejected _strict proportional_ (blocking on a fuzzy bullet count is
  fragile → over-fires → trains gate-gaming); rejected _soft-only_ (leaves the
  APPLY rung on prose-trust, arguably does not close #253's "close green with no
  dispositioning" hole).
- **Q1 refinement — user's Engelbart steer (post-answer).** The hard surface is
  narrowed to the single unambiguous omission, deviation is made _expressible_
  via a reasoning opt-out line, and all partial states are advisory. Rationale:
  a gate that mechanically enforces a count limits the agent's intelligence and
  invites token-theater; the tool should augment judgment (surface the gap, let
  the agent decide, record departures) — Engelbart, not assembly-line. This is
  recorded as the load-bearing Boundary.
- **Q2 — Counting model.** Options: {presence + advisory count, raw bullet
  count}. **Chosen: presence + advisory** (no count-match block). Both rejected as
  *blocking* mechanisms once Q3 moved substantive judgment to the reviewer.
- **Q3 — How to make the substantive call, after round-2 proved a regex can't
  (user's synthesis).** Options weighed: {A: sharp prose word-list tooth, B:
  block-the-blank + advisory only, **C: deterministic floor + fresh-eye subagent
  review ("gate + 지능")**}. **Chosen: C** (user-proposed). Rejected A (word-list
  drifts, can't read polarity, gameable, over-fires the corpus); rejected B-alone
  (block-the-blank misses #253's actual hole — the 2 corpus TPs have *non-empty*
  disposition-less Auto-Retros). C keeps B's ungameable deterministic floor AND
  adds the intelligence to judge substance, plus a `Disposition review:` evidence
  line so the review's existence is itself deterministically gated. Rationale:
  Engelbart — each tool does what it is good at; the regex stops pretending to
  judge prose. Tradeoff accepted: the substantive rung is non-deterministic /
  host-dependent (named in Non-Goals).
- **Implicit decisions (strong defaults).** Closeout-only; home = existing
  closeout-evidence module + its evidence/binding/skip machinery; opt-out
  Auto-Retro-scoped (NOT the poisoned full-text marker); grandfather by date; no
  release bump in scope (Off-Goal). State if any is wrong before `/goal`.

## Plan Critique Findings

**Reviewer provenance.** Two fresh-eye critique rounds ran at the Before-phase on
the user's request, all read-only. **Round 1:** one bounded subagent → "needs
rework" (B1). **Round 2:** four parallel bounded subagents (lenses: under-fire,
implementation-feasibility, simplicity, repo-fit) → three of four returned "needs
rework / rework", converging on one new decisive blocker. Every load-bearing
empirical claim (R1 token absence; R2 the two disposition-less TP goals; their
slice counts + Created dates; the `_TRIVIAL_GOAL_MARKER` poisoning) was
**independently verified by the shaping agent** before folding.

### Round 1 (single reviewer)

- **B1 (fatal as originally specified — VERIFIED, folded, then superseded).** The original gate
  keyed on a literal `applied:` / `issue #N` token convention that **does not
  exist in the live corpus**: 0 of 8 completed goals carry such a token in
  `## Auto-Retro`, and the disposition rule (`73d2d34`) is HEAD — landed today,
  so every goal predates it. The original "regression-safe on real data"
  acceptance bar was therefore self-contradictory; the gate would have refused
  essentially every real closeout (the exact false-positive the Boundary calls
  "worse than a false negative"). **Fold:** detection is now prose-aware (token
  OR observed prose), the block condition is "no signal at all" (the structural
  blank), and a **slice-1 corpus-calibration exit gate** (0 newly-refused) is now
  a hard prerequisite to wiring any block.
- **B2 (folded).** "Actionable = top-level bullet minus self-dispositioned"
  mis-models real bullets: they are category-prefixed (`**workflow:**`), often
  multi-line, with self-disposition markers on continuation lines — "one bullet"
  ≠ "one improvement". **Fold:** the counting unit is calibrated and locked
  against ≥2 real retros as fixtures in slice 1; if it can't reach human-judgment
  counts on real prose, narrow to block-the-blank-only (which sidesteps counting).
- **R1 (folded → Boundary).** `goal_artifact_lib.py` is at 358/360; new symbols
  stay in the closeout module and tests import it directly so the lib gains zero
  re-export lines.
- **R2 (folded → Boundary).** The reasoning opt-out's length floor is weak
  anti-gaming, so when used it now ALWAYS fires the advisory ("opt-out invoked:
  <reason>") — a visible audit record, not a silent bypass.
- **R3 (folded → Boundary/Verification).** The check hangs off the
  already-bound-retro branch; absent/renamed `## Next Improvements` is now an
  explicit inert-and-tested case.
- **R4 (folded → Slice 3).** The advisory line must get a named consumer (wired
  into the After-phase narration contract) or be dropped — no dead JSON.
- **R5 (folded → Slice Plan).** The real-corpus regression moved from slice 4
  (discovery-too-late) to slice 1's exit criterion.
- **R6 (folded → Off-Goal + Verification residual risk).** Post-`charness
  update` closeout-break blast radius named; slice-1 calibration is the guard.
### Round 2 (four parallel lenses)

- **B-CONVERGENT (fatal — VERIFIED, folded via the gate+지능 redesign).** The
  round-1 fold's premise — "the historical corpus all carries some disposition
  signal" — is **false**. Two completed 7-slice goals
  (`230-229-self-substitution`, `handoff-chunked-routing`, both Created
  2026-05-28) cite retros with 3 actionable improvements each but have **zero**
  disposition signal in their Auto-Retro (verified by grep). So the round-1
  "0 newly-refused" calibration was unsatisfiable without widening detection
  until pure "retro persisted/refreshed" narration counts — reopening the hole.
  And those two goals *are* #253's hole, green in the corpus: they are **true
  positives**, with **non-empty** Auto-Retros, so even "block the empty section"
  misses them. **Fold:** the whole prose-detection approach is dropped; substance
  judgment moves to a fresh-eye reviewer (rung 2), the deterministic floor blocks
  only the blank + requires review-ran evidence (rung 1), and grandfather-by-date
  exempts the pre-rule TPs. This **corrects** round-1's over-worry-dismissal claim
  that "blocking the blank closes the #253 hole" — it does not, on its own.
- **Under-fire lens (folded).** Prose-aware "any signal" detection passes pure
  lesson-narration containing words like `filed`/`applied`/`candidate`, and can't
  read polarity ("not filed" vs "filed"). Killed by removing the word-list
  entirely; the reviewer reads polarity natively.
- **Impl lens (folded).** Block condition unsatisfiable on the corpus as written
  (above); opt-out scope unspecified and the only full-text scope that "passes"
  is the `_TRIVIAL_GOAL_MARKER` poisoning bug → **Auto-Retro-scope all parsing**;
  tests reach closeout symbols via the lib re-exports, so verify the import/line-
  budget path before assuming zero lib growth.
- **Simplicity lens (folded).** A load-bearing prose word-list is an unjustified
  maintenance trap for a low-severity issue → dropped. Kept its block-the-blank
  floor and collapsed the slice plan.
- **Repo-fit lens (folded, no contract blockers).** Name the real
  `sync_root_plugin_manifests.py` + `validate_packaging_committed.py`; run
  `check_changed_surfaces.py` at the doc slice; reconcile **SKILL.md** "exactly
  two/mandatory" wording (3rd doc surface); Cautilus prompt-affecting but
  on-demand (no live run); dogfood-registry NOT triggered (verified — keyed on
  SKILL description/tier/adapter, unchanged).
- **Risk to watch (#251 recurrence):** mutation gate uses subprocess-capturing
  coverage; a naive `coverage run` misses subprocess scripts. Carried forward.

### Round 3 (four parallel lenses, on the gate+지능 redesign)

Verdicts: **regress** no blockers (4 honesty patches); **impl** one build blocker
(B1) + correctness fixes; **simplicity** "simplify, not rework" (dissent, below);
**engelbart** ship-ready, no blockers. All load-bearing claims re-verified in
live code by the shaping agent.

- **B1 (build blocker — VERIFIED, folded → RUNG 1b + slice 2).** `_EVIDENCE_LINE`
  hard-codes `(Retro|Host[- ]log[- ]probe)`; adding `disposition_review` to the
  tuple alone silently drops the line ⇒ every post-rule goal refused. Folded: the
  regex gets a `Disposition[- ]review` arm; binding/skip/normalizer compose
  automatically (verified). The "mirror exactly" framing was wrong.
- **Impl correctness (folded → Boundaries/Slice 2).** Fail-closed on missing
  `Created:`; inclusive `>= 2026-05-30`; key on Created-not-Completed (rationale
  recorded); thread `Created` into `check_complete_evidence` to gate both rungs;
  tests load the closeout module directly (≤0 new lib re-export lines).
- **Regress honesty patches (folded).** 1b reframed "stops the recursion" →
  "moves the floor to *did a review run*; the *was it rigorous* residual is the
  human-audit boundary, accepted not closed"; rung-1a fires independently of a
  rung-1b skip; `host-blocked-subagent` skip is an audit-flag; User Acceptance
  reworded (gate checks existence/binding, not verdict content); closeout must
  concede 1b is weaker than #253's literal ask.
- **Engelbart bankings (folded).** SKILL.md reconciliation = per-improvement (two
  forms) vs per-goal (opt-out = "no actionable improvement"), opt-out reason must
  be reviewer-falsifiable; 1b is presence/binding-only BY DESIGN (don't let a
  future reviewer tighten it into a content classifier); narration-non-blocking
  vs review-existence-blocking asymmetry banked (deterministic-inspectability).
- **DISSENT — simplicity lens: "drop rung 1b" (considered, REJECTED, recorded).**
  Argued the `Disposition review:` evidence line is ceremony (gates presence, not
  substance) and is the keystone forcing grandfather/R6/slice-2/SKILL-churn; its
  MVP = block-the-blank + a checklist item on the already-mandated closeout
  critique + a non-blocking affordance. **Decision: keep rung 1b.** Reason: rung-1a
  (block-the-blank) provably *cannot fire on the live corpus* (every completed
  goal has a non-empty Auto-Retro) and rung-2 is non-deterministic — so without
  1b the real #253 case has **zero deterministic teeth**, collapsing to the
  soft-only option rejected at Q1. 1b is the only rung that deterministically
  forces an auditable receipt to exist every post-rule closeout — a real,
  enforceable change over today's pure prose-trust. The dissent's strongest point
  (1b gates presence, not substance) is answered by engelbart: 1b is
  *intentionally* mechanical so judgment goes into rung 2 — the user's literal
  "게이트 + 지능 둘 다". Grandfather complexity is the accepted cost. **The user
  can override toward the simpler MVP at activation if they disagree.**

## Off-Goal Findings

- _(residual risk + candidate, critique R6 — now bounded)_ The gate newly
  _refuses_ flips on installed machines after `charness update`, but
  grandfather-by-date means **only post-rule goals** are affected (pre-rule
  corpus untouched). The version-bump + update-note decision is a follow-up
  (`issue`/`release`), out of scope unless the user folds it in.
- _(pre-existing bug candidate, found by round-2 impl lens — VERIFIED)_
  `goal_artifact_lib.is_non_trivial_goal` runs `_TRIVIAL_GOAL_MARKER.search(text)`
  over the **full goal body**, so a 7-slice goal whose prose merely *describes*
  the `Single-slice goal:` marker is mis-classified as trivial and exempted from
  the portability check (both TP goals match: 1 and 5 substring hits). This is
  outside #253's scope — but this goal must **not** reuse the full-text scan for
  its own opt-out; file the pre-existing portability-exemption poisoning
  separately via `issue`.
- _(candidate)_ A stronger follow-up could verify a cited `issue #N` actually
  exists/open via the issue backend — deliberately out of scope (keeps the
  deterministic rung offline). File if wanted.

## Final Verification

_(After-phase — filled when the run completes.)_ **Round-3 regress R2:** at
closeout, explicitly concede that rung-1b is weaker than #253's literal
"deterministic check" ask, and state why a fully deterministic *substantive*
check is infeasible (round-2 proved it over-fires or passes narration) — so the
issue is not closed with a quiet scope-narrowing.

## User Verification Instructions

_(After-phase — concrete steps the user runs to confirm, filled at closeout.)_

## Auto-Retro

_(After-phase — retro findings + an explicit disposition for each surfaced
improvement; this goal will dogfood the very gate it ships.)_
