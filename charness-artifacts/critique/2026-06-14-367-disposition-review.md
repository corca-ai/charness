# Disposition Review — #367 achieve goal closeout

Reviewer: fresh-eye subagent (rung 2)
Goal: charness-artifacts/goals/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md
Retro: charness-artifacts/retro/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md
Slug: 367-quality-ci-recoverability-and-timing-ingest

## Per-improvement verdicts

The retro `## Next Improvements` names exactly two improvements. The goal
`## Auto-Retro` bundles both into `issue #368`. Verified against the actual
filed issue (`gh issue view 368`).

- Improvement 1 (workflow/capability: add the inference-interpretation
  meta-validator's unregistered-declaration scan to the commit-time structural
  sweep / `run_slice_closeout` pre-commit aggregate): **dispositioned as issue
  #368 — yes, covered.** #368's "Proposed direction" item 1 names exactly this:
  "Add the meta-validator's *unregistered-declaration* scan (a fast, offline AST
  scan ...) to the commit-time structural sweep, alongside
  `validate_attention_state_visibility`. Keep the heavier live-count/consumer-anchor
  assertions in broad pytest ... only the leak scan needs to shift left." Matches
  the retro's framing (shift the leak scan left, keep the heavy part slow).

- Improvement 2 (memory/capability: a short "adding an advisory inventory/surface"
  authoring checklist naming the 3 registries + the SKILL.md ≤200 budget in the
  quality/create-skill references): **dispositioned as issue #368 — yes, covered.**
  #368's "Proposed direction" item 2 names exactly this: the authoring checklist
  for attention-state-visibility.json, inference-interpretation-surfaces.json, the
  dogfood EVIDENCE_OVERRIDES scaffold, plus the SKILL.md ≤200-line budget, "so the
  next author front-loads them." The retro explicitly said to keep one tracked
  thread; #368 bundling both is consistent with that intent.

Both improvements are dispositioned; neither is left undispositioned. The bundle
into a single issue is honest to the retro's own "keep one tracked thread"
instruction.

## novel: claim verdict

**recurrence-of: #314 / #319 / #332 lineage (the "cheap structural check enforced
only at the broad/bundle gate, not the commit boundary" class).**

The Auto-Retro `novel:` claim is true only at the narrowest instance grain — yes,
the *inference-interpretation surface registry specifically* had not been shifted
left before, and it is distinct from the attention-state and dogfood registries
which already run in the sweep. That sub-claim is accurate. But the *structural
class* #368 actually fixes — "a cheap, deterministic, offline structural check
whose only enforcement is the broad/bundle gate, so it surfaces at bundle cost
instead of at the commit boundary where the change was made" — is one of this
repo's most heavily recurring documented classes, not novel:

- **#314** (CLOSED): "Run cheap portable/structural gates at the commit boundary,
  not only the bundle gate (generalizes #307)." Verbatim structural pattern: "A
  cheap, deterministic, path-scoped gate is enforced only at the broad/bundle
  boundary while a cheaper per-slice / pre-commit path exists, so a violation is
  detected at final-closeout cost instead of at the commit boundary." This is the
  same class, and it already wired sibling validators
  (`validate_skill_ergonomics`, `check_boundary_bypass_ratchet`) into the per-slice
  surface — the exact remedy #368 proposes for one more validator.
- **#319** (CLOSED): "SKILL.md core-nonempty headroom-buffer test runs only in the
  broad gate, not the commit boundary (generalizes #308/#314)." Its suggested
  direction is the template #368 reuses almost word-for-word: "surface it as a
  commit-boundary advisory/checker for changed files — mirroring how #314 wired
  `validate_skill_ergonomics` ... into the per-slice surface `verify_commands`."
- **#332** (CLOSED): "Authoring-preflight / commit-boundary structural sweep is
  not reliably run on new skill-package + script edits (recurring: #308/#325/#329)."
  Same class, and its own title already labels itself recurring across three prior
  issues.
- **#366** (CLOSED, filed the SAME DAY): off-taxonomy debug-artifact enum passes
  the write-time validator but blocks `run_slice_closeout` repo-wide — a
  structural fact only caught at closeout, not at author time. Same shift-left
  shape, same week.
- **#328** (CLOSED) is the upstream "Cheap upstream pre-checks before
  expensive/late verification" framing of the whole class.

So `novel:` is **honest at the registry-instance grain but misleading at the
class grain.** The disposition-gate's purpose is to prevent a known recurring
class from being laundered as a fresh narrow issue, and the Auto-Retro's
`novel:` justification leans on the narrow grain ("first inference-surface
registry ...") without acknowledging that the SHIFT-LEFT remedy and the
"slow-gated structural sibling that should move to the commit boundary" pattern
were already resolved at least three times (#314, #319, #332). #368's own body is
more honest than the Auto-Retro line: it explicitly cites the sibling registries
and frames itself as the slow-gated sibling, but it does NOT cite the #314/#319/#332
shift-left lineage that already established the remedy. This is a recurrence of a
known class, and the new issue should reference that lineage so #368 is solved as
"apply the #314/#319 shift-left pattern to the inference-interpretation registry,"
not re-discovered from scratch.

## Structural follow-up destination verdict

**issue #368 is a defensible destination, BUT it should be a repo-local guard
landed via the established #314 pattern, and #368 must cross-link the
#314/#319/#332 lineage.**

Deferring to an issue rather than applying in-session is reasonable on #367's
scope grounds: the fix mutates the shared commit-gate aggregate
(`run_slice_closeout` structural sweep), which is genuinely outside #367's
advisory-only / Floor-Addition-Restraint scope and warrants its own critique. The
retro and goal both say this explicitly and consistently. So `issue #N` over
`applied:` is the right call for THIS goal.

However, two qualifications keep this from a clean PASS:

1. The destination class is really a **repo-local guard** (a commit-time
   structural-sweep checker), and #314 already proved the wiring path
   (`.agents/surfaces.json` verify_commands / `staged_commit_gate_plan`). #368
   should be resolved by extending that existing per-slice gate set, not designing
   a new mechanism — i.e. the destination is correct as an issue, but the issue
   should be scoped as "apply the existing #314 shift-left wiring to one more
   validator," which lowers its cost and risk and prevents re-litigating the
   pattern.
2. Because #314/#319/#332 already closed this class and it RECURRED here, there is
   a live recurrence-conversion concern: a previously-closed shift-left class
   produced a new instance. #368 should be tagged as a recurrence of that class
   (cf. #358's "falsified conversion" precedent) rather than presented purely as a
   "novel" narrow gap, so the resolver fixes the general leak (any unshifted
   structural validator) rather than only this one registry and inviting a fourth
   recurrence.

## Overall

**FIX (minor, disposition-honesty only — not a blocker to closeout):** Every
improvement IS dispositioned (both into #368, verified to cover both), and the
issue-over-applied destination is reasonable for #367's scope. The one defect is
the `novel:` claim in the goal `## Auto-Retro`: it is honest only at the narrow
registry-instance grain and omits that the shift-left CLASS (#314 → #319 → #332,
plus same-day #366) is a documented, repeatedly-resolved recurrence. The fix is
narrow and does not require reopening code work:

- Amend the goal `## Auto-Retro` `novel:` line to state the accurate grain:
  novel *instance* (inference-interpretation registry) of an *already-recurring
  class* (cheap structural check stuck at the broad gate; lineage #314/#319/#332,
  same-day sibling #366), so it is not laundered as a fresh class.
- Add a one-line cross-reference in #368 to #314/#319/#332 so the resolver applies
  the established shift-left wiring (`.agents/surfaces.json` verify_commands per
  #314) and treats this as recurrence-conversion, not a from-scratch fix.

The substantive closeout (both #367 gaps closed, advisory/inert, guardrail
intact, two SHIP fresh-eye reviews, broad pytest green) is sound; this FIX is
about disposition-ledger honesty, which is exactly what the rung-2 gate exists to
catch.
