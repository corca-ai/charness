# Achieve Goal: Handoff auto-chunking: generative-sequence routing into /achieve

Status: active
Created: 2026-05-28
Activation: `/goal @charness-artifacts/goals/2026-05-28-handoff-chunked-routing.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

Absorb the recurring manual cost of reading docs/handoff.md, identifying which residual tasks unblock others, picking an advantageous order, and shaping a /goal activation. The handoff skill should, when the handoff doc is mentioned with no other explicit directive, parse the residual tasks, produce a generative-sequence ranking with per-chunk reasoning, propose merges where shared artifact/policy boundary justifies it, and on user selection auto-draft a goal artifact skeleton (Title + Goal + Non-Goals + Boundaries) at status draft so /goal @file is the next move. Closes a workflow asymmetry where the user currently does the routing the skill should do.

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb the existing `handoff` skill's other responsibilities
  (state selection, spill targets, continuation sequence). The chunker
  is an *additive* phase of the handoff skill, not a redesign.
- Do not modify the `/achieve` skill or its Before-phase interview. The
  chunker produces a *draft* goal artifact that `/achieve` consumes
  exactly as if the user had hand-shaped it.
- Do not modify the `/goal` host runtime; this goal targets repo-owned
  skill contracts only.
- Do not auto-rank work that lives outside `docs/handoff.md` (other
  artifacts such as `charness-artifacts/quality/latest.md` may be
  *read* for grounding but the chunker treats handoff entries as the
  source of truth set).
- Do not file additional GitHub issues during the run unless an
  off-goal blocker requires it; the chunker's purpose is to *route*
  existing handoff entries, not to discover new ones.

## Boundaries

- In scope: [`skills/public/handoff/`](../../skills/public/handoff/)
  (SKILL.md + new references + new scripts), the auto-draft writer
  surface that produces a goal artifact skeleton conforming to
  [`skills/public/achieve/scripts/goal_artifact_lib.py`](../../skills/public/achieve/scripts/goal_artifact_lib.py)'s
  contract (so it consumes cleanly into `/achieve`), and `tests/`.
- The chunker must be portable per
  [implementation-discipline](../../docs/conventions/implementation-discipline.md):
  no host-specific assumption, no host-only adapter coupling.
- Each coordinated skill must stay useful standalone:
  - `handoff` without the chunker still works as today (the chunker
    is a new conditional workflow phase, not a replacement);
  - `achieve` without a chunker-drafted skeleton still works (the
    auto-drafted skeleton is one valid input shape, not the required
    one).
- The auto-drafted goal artifact MUST pass
  [`check_goal_artifact.py`](../../skills/public/achieve/scripts/check_goal_artifact.py)
  at status `draft` — including the slice-2 (#230) portability sections
  when the proposed work is non-trivial (auto-drafted goals are
  non-trivial by default).
- Stop conditions (active triggerable signals; flip to `blocked` and
  ask, do not guess):
  - **Generative-sequence ranker needs nested subagent spawning** at
    runtime (i.e., the handoff chunker spawns its own subagent to
    rank). The achieve goal must declare this upfront and confirm
    host support before slice 3 starts; if nested spawning is not
    available, fall back to in-agent reasoning by the active agent
    and re-run plan critique on the revised plan.
  - **Auto-draft writer crosses the Boundaries depth.** If slice 5
    populates `User Acceptance`, `Agent Verification Plan`, or
    `Slice Plan` content beyond table headers, stop — that violates
    the depth answer recorded in Interview Decisions.
  - **Trigger detection over-fires.** If the chunker activates when
    the user's message contains explicit task-naming next to the
    handoff mention (e.g., "read handoff and do A"), the trigger is
    too greedy; stop and re-anchor the detection rule.
  - **#233 follow-up still open at slice 5.** If
    [#233](https://github.com/corca-ai/charness/issues/233)
    (After-phase gate binding) has not landed before slice 5, decide
    explicitly whether the auto-drafted goal needs to satisfy a
    binding contract that does not yet exist; do not silently
    paper over.

## User Acceptance

- A future session in which the user mentions `docs/handoff.md` (or
  the handoff skill) with no other explicit task directive triggers
  the chunker; if the user names a specific next task alongside the
  mention, the chunker does **not** fire (single-test demonstrable).
- The chunker emits a ranked list of chunks where each chunk carries
  a one-line objective summary and a 2–3 line generative-sequence
  reasoning ("why this comes first / what it unlocks") that a fresh
  reader can evaluate.
- When two or more handoff entries share an artifact/skill/policy
  boundary, the chunker proposes them as one merge candidate
  alongside the standalone chunks; the user can accept/reject the
  merge per chunk.
- The user can ask "why not chunk X?" in the same conversational turn
  and the chunker answers using its already-computed reasoning, not a
  fresh recomputation.
- On user selection, the chunker writes a goal artifact at
  `charness-artifacts/goals/<yyyy-mm-dd-slug>.md` with Title + Goal +
  Non-Goals + Boundaries filled, all other required sections present
  but empty, status `draft`, and a valid Activation line. The artifact
  passes `check_goal_artifact.py`.
- The Slice Plan table is **empty** (header rows only) when
  auto-drafted; the achieve Before-phase interview fills it. This
  honors the Interview Decision on draft depth.
- A self-test fails when the auto-drafted artifact contains any
  prose under `User Acceptance`, `Agent Verification Plan`, or
  `Slice Plan` data rows beyond placeholders.

## Agent Verification Plan

### Low-Cost Checks

- Targeted `pytest` of new parser / ranker / merger / drafter tests
  per slice.
- Before editing any `SKILL.md`, run `wc -l skills/public/<skill>/SKILL.md`
  and refuse to grow a body that is within 10 lines of the 200-line
  `MAX_SKILL_MD_LINES` budget; route new content into a
  `references/*.md` file instead (recent-lessons repeat trap).
- `validate_skills` after any SKILL.md or skill-reference edit.
- `check_doc_links` on any docs edit.
- `ruff` + `mypy` on changed Python.
- For each slice that adds tests: cheap duplicate-pressure sample
  (`--test-pressure` on `append_slice_log.py`).
- Auto-drafted goal artifacts in test fixtures must pass
  `check_goal_artifact.py` (sections + portability self-test).
- **Standalone-usefulness invariant** (F4 of pre-activation plan
  critique): the auto-draft writer lives entirely under
  `skills/public/handoff/scripts/`; no file under
  `skills/public/achieve/` is mutated by any slice in this goal. A
  `git diff --name-only main..HEAD | grep '^skills/public/achieve/'`
  check at slice 5 must return empty. This preserves both directions
  of standalone usefulness (handoff chunker still works if
  `/achieve` ever moves; `/achieve` still consumes any goal artifact
  whether or not the chunker authored it).

### High-Confidence Checks

- End-to-end fixture: feed a known-good handoff.md snapshot to the
  chunker → expected ranked chunks with reasoning match the
  fixture's expected output exactly; ranker prompt + parser are
  versioned together so a prompt drift fails the fixture loudly.
- Full pre-push broad gate green at bundle boundaries and at final
  (slice 7 from #230 router routes correctly for this goal's diff
  shape — `skills/public/handoff/` + `scripts/` touch).
- Mutation gate green on HEAD (scheduled) or a documented
  changed-surface sample-mode run when the slice touches
  mutation-relevant code.

### External Or Live Proof

- Real-host smoke: invoke the handoff skill on the actual current
  `docs/handoff.md` in a Claude Code session (active host this
  session); confirm the chunks make sense as a routing recommendation
  the user would actually take. Codex coverage recorded explicitly
  as deferred or covered.
- Round-trip proof: the auto-drafted goal artifact for a chosen chunk
  is activated with `/goal @file` and reaches at least the
  Before-phase interview without `check_goal_artifact` failing.
- Skipped-proof note: this goal is not a release, so no clean-machine
  Cautilus install/doctor proof is required from this run.

### Critique Cadence

- Plan-level critique (standard tier per shared fresh-eye reference)
  against this artifact before user activates.
- Slice-level critique on slices 3 (ranker correctness risk —
  generative-sequence judgment is hard to get right and easy to drift
  on prompt changes) and 5 (auto-draft writer — could produce
  artifacts that violate Boundaries depth or portability self-test).
- Final critique on the closeout slice.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1. Spec | Algorithm design, data structures, skill surface, auto-draft template, LLM-vs-deterministic split decision, **deterministic trigger-detection rule with a fixture of 3-5 example messages paired with expected `chunk/no-chunk` decisions** (so slice 6 + slice 7 verification agree on the same rule, not three interpretations) | Multiple cross-cutting decisions must converge before code | Spec doc under `docs/`, fixture table inside the spec, plan critique pass on revised slice plan | planned |
| 2. Handoff input parser | Parse `## Next Session` entries (and any other handoff sections that contain residual work) into structured chunk-candidate records | Foundation for everything else; deterministic and testable in isolation | Parser script + tests against current handoff.md as fixture | planned |
| 3. Generative-sequence ranker | Produce ranked chunks with per-chunk reasoning following the Christopher Alexander generative-sequence rule used by `issue` skill | Core value; LLM-judgment heavy → slice-level critique | Ranker (script or in-agent prompt) + fixture test + slice critique on ranking correctness | planned |
| 4. Merge proposer | Identify merge candidates (shared artifact/skill/policy boundary) and emit per-chunk merge proposal alongside standalone chunks | Granularity decision = "skill proposes, user accepts per-chunk" | Merger script + tests covering shared-file, shared-skill, shared-policy cases | planned |
| 5. Auto-draft writer | Given a selected chunk (possibly merged), write goal artifact skeleton at Boundaries depth that passes `check_goal_artifact.py`. **Portability section handling is explicit:** `Context Sources` is seeded with the source handoff entry + related artifacts cited in that entry (preserves provenance for the achieve Before-phase); `Interview Decisions` and `Plan Critique Findings` are left as empty H2 headings with a one-line "*To be filled by the achieve Before-phase interview / plan critique.*" placeholder. The Slice Plan stays header-only so `is_non_trivial_goal` returns False at write time; the gate fires later only when /achieve adds slice rows. The writer never inserts a `Single-slice goal:` exemption marker. | Closes the loop into `/achieve` | Drafter + integration test producing a valid draft artifact + slice critique on depth-crossing risk + fixture test asserting Context Sources is non-empty and the other two portability sections contain only the placeholder line | planned |
| 6. Skill surface | `handoff/SKILL.md` gets only a short trigger paragraph + pointer; the conditional workflow phase body, the trigger-rule detail, the chunker invocation, and the auto-draft handoff prose all live in a **new reference file** `skills/public/handoff/references/chunked-routing.md` (mirrors the existing reference-heavy pattern). SKILL.md net growth must stay ≤10 lines so the 200-line cap retains ≥40-line headroom (handoff SKILL.md is at 151 lines; cap is 200). | Activation surface | SKILL.md edit (≤10 line net growth), new `references/chunked-routing.md`, find-skills inventory refresh | planned |
| 7. Closeout | Broad gates, full `retro` invocation, host-log probe, final verification with honest non-claims, user verification instructions | Final-stage proof per After-phase contract | `check_goal_artifact.py` ok=true, retro artifact, evidence-binding (consume #233 fix if landed, else explicit Off-Goal note), real-host round-trip smoke | planned |

## Slice Log

### Slice 1: Spec for handoff auto-chunking

- Objective: Lock the algorithm, data shape, trigger rule (with 7-row fixture), deterministic-vs-LLM split, auto-draft template, and skill-surface plan that slices 2-7 build to.
- Why this approach: Multiple cross-cutting decisions had to converge before code (data structures shared across parser/ranker/merger/drafter; auto-draft template must match the existing goal_artifact_lib template; trigger rule has to be the same across slice 6 SKILL.md prose and slice 7 verification).
- Commits:
- What changed: New docs/handoff-chunked-routing.md (466 lines): algorithm 5-step pipeline, data structures (HandoffEntry / ChunkCandidate / RankedChunk / MergeProposal), deterministic-vs-LLM split table, trigger detection rule + 7-row fixture, auto-draft template + post-condition, skill-surface plan with ≤161 line budget for handoff/SKILL.md, test plan table per slice, stop conditions, critique findings provenance.
- Alternatives rejected: Inline-extending handoff SKILL.md instead of a separate spec doc: rejected because the spec elaborates 6 slices' worth of design and SKILL.md cap is 200 lines; the new reference file owns the body, the spec owns the design contract that survives beyond a single skill surface.
- Targeted verification: check_doc_links --repo-root . passed (after folding the spec into <repo-root>/path placeholders for to-be-created artifacts and markdown links for existing ones).
- Test duplication pressure:
- Critique: Bounded fresh-eye subagent spec critique (standard tier, agentId a3b7d3116ace3415c). Four findings folded inline (2 Act-Before-Ship: Title double-prefix bug, missing why-not test row; 2 Bundle-Anyway: boundary-token canonicalization, prose-in-Acceptance/Verification assertion). Two Over-Worry / Valid-but-Defer preserved as reasoning trail in spec's Critique Findings section. Provenance recorded so a fresh session re-verifies without re-running critique.
- Off-goal findings:
- Lessons carried forward: (1) When a spec passes a value into an existing template, trace the template's wrapping prefix exactly — the Title double-prefix bug was the kind of mistake that only a fresh-eye reader catching the spec against the actual _TEMPLATE source would find. (2) Boundary-token canonicalization needs a real-data merge negative case in the fixture, not just positive cases — over-merging on common directory roots is the silent failure mode.
- Metrics: spec doc: 466 lines; check_doc_links: green; critique tokens: 54914 / tool_uses: 8 / duration: 89955ms (fresh-eye subagent self-reported)

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User correction at the close of the #230 + #229 goal session: the user
  observed they manually chunk handoff residual work into a useful order
  for every session, and that the handoff skill should absorb this.
  Source conversation logged in this session's JSONL (Claude Code session
  `906f4924-6f39-4090-ab3f-05eba79695a7`).
- Source handoff doc: [`docs/handoff.md`](../../docs/handoff.md) — the
  surface the chunker reads. Current shape uses a numbered `## Next Session`
  list with prose bullets per residual task; that shape is the parser's
  initial input contract.
- Prior achieve goal: [`2026-05-28-230-229-self-substitution-pattern.md`](./2026-05-28-230-229-self-substitution-pattern.md)
  — established the achieve gate substrate this work consumes
  (`check_goal_artifact.py`, the portability self-test, the After-phase
  evidence gate). Slice 5 of this goal must produce artifacts that satisfy
  those existing gates.
- Open follow-up: [#233](https://github.com/corca-ai/charness/issues/233)
  proposes binding closeout evidence to goal context. Slice 7 of this
  goal needs to handle the case where #233 has or has not landed by
  closeout time.
- Generative-sequence idiom: [`skills/public/issue/SKILL.md`](../../skills/public/issue/SKILL.md)
  step 5 ("Order resolutions as a generative sequence (Christopher
  Alexander): the move that reduces uncertainty or unlocks the next
  issue comes first"). This goal extends the same idiom from issue
  resolution to handoff routing.
- Existing handoff skill body: [`skills/public/handoff/SKILL.md`](../../skills/public/handoff/SKILL.md)
  is the surface the new conditional workflow phase plugs into; the
  current surface owns state selection, spill targets, and continuation
  sequence (none of which this goal modifies).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

### Q1 — Ordering basis (default ranking lens)

- Family considered: (a) Dependency-first; (b) Risk-down-first; (c)
  Cheapest-first; (d) Multi-criteria narrated.
- Chosen: **Christopher Alexander's generative sequence** — the move
  that reduces uncertainty or unlocks the next issue comes first.
  Operationally this is a superset of (a)+(b): "unlocks the next" is
  dependency-first; "reduces uncertainty" is risk-down-first.
- Rejected reason: (c) cheapest-first is a momentum heuristic that
  fights the goal's framing of "advantageous order"; user explicitly
  said the manual heuristic they apply is closer to generative
  sequence than to cheapest. (d) multi-criteria narrated was rejected
  because it punts the lens decision to every session, defeating the
  purpose of absorbing the routing cost into the skill.
- Axis check (#229 anti-anchoring): generative sequence is
  **single-point** per session run; the lens itself does not vary on
  host/provider/environment. The repo already uses the same lens in
  `issue` SKILL.md step 5, so this choice is internally consistent,
  not an isolated locked value.

### Q2 — Chunk granularity (merge policy)

- Family considered: (a) 1 entry = 1 chunk no merging; (b) merge when
  sharing artifact/skill; (c) merge when sharing design boundary; (d)
  skill proposes, user accepts per-chunk.
- Chosen: **(d) skill proposes merges, user accepts per-chunk**.
- Rejected reason: (a) misses real shared-context savings; (b) and
  (c) lock the merge heuristic and can over-merge unrelated work
  whose paths happen to overlap. (d) keeps the skill's judgment
  reviewable and overridable without forcing the user to do the
  merge analysis themselves.
- Axis check: **single-point**; merge policy is a workflow choice,
  not a host/provider axis.

### Q3 — Auto-draft depth into goal artifact skeleton

- Family considered: (a) Title + Goal only; (b) Title + Goal +
  Non-Goals + Boundaries skeleton; (c) Full goal artifact incl.
  Slice Plan; (d) Conversational only, no auto-draft.
- Chosen: **(b) Title + Goal + Non-Goals + Boundaries skeleton**.
- Rejected reason: (a) loses too much information already extractable
  from handoff prose. (c) violates anti-anchoring (locks the slice
  plan before the achieve Before-phase interview happens) and risks
  the auto-draft accidentally satisfying the achieve gate at the
  wrong depth. (d) defers everything to manual prose, sacrificing
  the round-trip-into-/achieve value.
- Axis check: **single-point**; depth is a workflow choice.

### Q4 — Override surface for ranking disagreement

- Family considered: (a) ranked list + binary pick; (b) reasoning
  narrated + "why not" accepted in same turn; (c) top chunk +
  reasoning, accept/next/specify.
- Chosen: **(b) reasoning narrated + "why not" accepted**.
- Rejected reason: (a) loses the override path; user has to start a
  new turn to disagree. (c) shows only the top — comparison requires
  additional turns; this fights the same manual-cost the goal aims
  to absorb. (b) puts all the comparison information on the screen
  in one turn so a "why not X" follow-up uses already-computed
  reasoning, not a fresh recompute.
- Axis check: **single-point**; override UX is a workflow choice.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Bounded fresh-eye standard-tier subagent review (per
[`fresh-eye-subagent-review.md`](../../skills/shared/references/fresh-eye-subagent-review.md))
run on the draft artifact before activation. Reasoning preserved here so a
fresh session can re-verify the folded revisions without re-running critique.

### Act Before Ship (folded into Slice Plan / Verification)

1. **Trigger contract was prose, not testable.** The artifact said
   "mention of `docs/handoff.md` with no other explicit task directive
   triggers the chunker" but never defined "mention" or "explicit
   directive" operationally. Slice 1 spec, slice 6 SKILL.md, and slice 7
   verification could each interpret it differently. **Folded** into
   Slice 1 Expected Evidence: spec must commit to a deterministic
   detection rule with a 3-5 example fixture pairing input messages with
   expected `chunk/no-chunk` decisions.

2. **Auto-draft writer vs portability self-test was contradictory as
   written.** `is_non_trivial_goal` returns False for a Slice-Plan-
   header-only artifact, so the portability self-test does not fire at
   write time — only later when `/achieve` adds slice rows. By then the
   auto-draft may not have populated Context Sources / Interview
   Decisions / Plan Critique Findings at all. **Folded** into Slice 5:
   Context Sources seeded with the source handoff entry + cited
   artifacts (preserves provenance); the other two portability sections
   are H2 headings with a single placeholder line; writer never inserts
   a `Single-slice goal:` exemption marker; fixture test asserts this.

### Bundle Anyway (folded; cheap to land alongside Act-Before-Ship work)

3. **Handoff SKILL.md budget is tight, not safe.** Handoff SKILL.md is
   151/200 lines; the new conditional phase needs trigger rule +
   chunker invocation + auto-draft handoff sentence. Slice 6 didn't
   pre-allocate where content lives. **Folded** into Slice 6 Objective:
   SKILL.md gets only a short trigger paragraph + pointer; the body
   lives in a new `references/chunked-routing.md`; SKILL.md net growth
   ≤10 lines so the cap retains ≥40-line headroom.

4. **Standalone-usefulness was asserted but not verified.** No Agent
   Verification check exercised the "user types /achieve directly
   without using the chunker" direction. **Folded** into Low-Cost
   Checks: explicit invariant that no file under
   `skills/public/achieve/` is mutated by any slice in this goal; a
   `git diff --name-only` check at slice 5 must return empty for that
   prefix.

### Over-Worry (raised, not folded as blockers)

- Ranker prompt drift risk: even if a prompt text is version-pinned,
  model upgrades could silently shift rankings while keeping the
  fixture text passing. The slice-level critique already scheduled
  for slice 3 is the right mitigation; further pre-locking before
  the slice would be premature.

### Valid but Defer (already gated by existing Stop Condition)

- #233 dependency timing: the goal-slug-bound retro path convention
  would also constrain the slice-5 auto-draft writer, not just the
  slice-7 closeout. The existing Stop Condition that forces an
  explicit decision before slice 5 closes is sufficient; folding the
  decision earlier risks blocking on a non-blocking dependency.

### Provenance

- Reviewer: bounded fresh-eye subagent, standard tier, agentId
  `a33dfbee0a68a7774`.
- Run timing: pre-activation, after the initial draft and before the
  user runs `/goal @file`.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

## User Verification Instructions

## Auto-Retro
