# North-Star Overhaul Plan v1 (craken-informed) — FROZEN FOR CRITIQUE

Authored 2026-06-18. Execution is post-compaction. This is the frozen target for a
diverse-lens fresh-Opus critique; reflect the critique, then execute.

## What this plan rests on (findings)

1. **5-round behavioral experiment (~50 fresh Sonnet/Opus subagents).** A typed PROSE
   "brief" appended to a passing gate's output (telling the agent "a green pass is not
   behavior proof; verify via a distinct channel") NEVER changed a single close/verify
   decision. Agents — reviewer-framed AND doer-framed, judgment AND action tasks, single
   AND bundle, under closure momentum, with shell tools — reliably caught proxy-only
   verification and independently verified. The #386 failure (a fresh disposition
   reviewer rubber-stamped a proxy) could NOT be reproduced in a fresh sole-task
   subagent under any design. Inference: agents already POSSESS the proxy-vs-behavior
   judgment; #386 is not an information deficit. A prose brief (or more AGENTS.md prose)
   supplies knowledge agents already have → no effect. The lever is structural, not
   informational.
2. **Phase 0 back-test (opposite-primed fresh judges over a frozen 30-issue table).** The
   hand-picked recurrence "cluster" was cherry-picked; the coherent family is narrower
   (lifecycle-state misclassification: #359/#381/#382/#385/#386); the largest recurrence
   is the mutation-CI family (8 issues), previously sidelined. Mechanism sharpened:
   PROXY/form gate green is unreliable; BEHAVIORAL gate red is reliable. Bloat driver =
   own-concept dominates (~68%), not boilerplate → concept-separation, not floor-stripping.
3. **craken principles (../craken-agents).** Trust model lives in TYPED DATA + tool
   enforcement, not prose (evidence-depth tiers; empty shells refused as evidence; "a PDF
   URL is not proof of reading"; eval rubric scores proxy-as-direct as a failure; retro
   lesson: "prompt instructions are not enough; build narrower concrete tools").
   PUSH→PULL context layering (minimal always-on + skills INDEX only; bodies/detail loaded
   on demand). Intelligence judges / code enforces durable state transitions. Every fix
   classified prompt/code/tooling/eval. Docs like code (SRP, reduce duplication,
   per-doc retrospectives).

## Locked decisions

- **D1.** The lever is STRUCTURAL, not informational. Stop fixing recurrences with
  prose/briefs/more-AGENTS.md.
- **D2.** Adopt craken PRINCIPLES; exclude craken INFRA (awiki, Cloudflare/Think,
  Episteme). BUT include the modest TOOLING trust-as-typed-data requires. "Principle
  only" ≠ "prose/docs-only changes."
- **D3.** Sequence — structural routing FIRST, then slim docs/skills; fix-kind
  classification cross-cutting.
- **D4.** Keep charness fresh-eye SUBAGENT for irreversible boundaries (50-trial
  evidence: fresh sole-task agents are reliable; craken's same-agent skill-review is
  weaker here). Use on-demand skill-load for NON-boundary procedural guidance.

## Plan

**Track 1 — structural routing (first):**
- 1a. Every irreversible-boundary decision (issue/PR close, release publish, external
  write, deletion) is decided by a fresh sole-task reviewer given the RAW situation (not
  the doer's pre-digested "it's done" summary), required to independently verify behavior
  (exercise it / distinct channel), per-unit not bundle.
- 1b. Gate/tool outputs carry a typed trust-class/provenance label
  (presence-only | proxy | behavioral) and refuse to promote presence→proof. Agents
  reason over the labeled data instead of re-deriving depth each time.

**Track 2 — slim (after Track 1):**
- 2a. AGENTS.md/CLAUDE.md → minimal stable entry + skills index; push detail into focused
  docs/skill bodies loaded on demand.
- 2b. Concept-separate the ~200-line skill bodies (own-concept compression, SRP). Cut
  intrinsic-judgment restatement; keep non-intrinsic repo-specific info. Per-doc
  retrospectives.

**Track 3 — cross-cutting:**
- 3a. fix-kind classification (prompt/code/tooling/structure) in retro/issue closeout;
  prefer structure/tooling over prose.
- 3b. Carry Phase 0 corrections: fix cluster membership; mutation-CI a first-class track;
  proxy/behavioral framing replaces vague "non-terminality."

**Migration discipline:** replacement-before-deletion; prove each removal catches a seeded
instance; one-line rollback ref; tripwire = first lifecycle close on proxy/aggregate proof
after a phase ships triggers a mandatory retro.

## Honest limitations

- #386 was NOT reproduced; the structural conclusion is inference from non-reproduction
  across 5 designs (strong, not a positive demo).
- Subjects were short-context isolated; real long-context exhaustion (the suspected true
  condition) is untested and may be the actual #386 driver.
- The typed trust-class (1b) may itself be ignored/gamed — our own experiment suggests
  agents don't NEED it; its value (reducing per-decision load) is unproven.
