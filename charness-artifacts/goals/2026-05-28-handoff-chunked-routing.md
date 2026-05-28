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

### Slice 2: Handoff input parser

- Objective: Parse handoff ## Next Session numbered entries into structured HandoffEntry records with title (soft-wrap-collapsing), body, deduped referenced_paths, referenced_issues, referenced_skills, and a nontrivial-filtered boundary_tokens tuple.
- Why this approach: Foundation for slices 3-5 (ranker / merger / drafter). Deterministic and testable in isolation against the current handoff.md as fixture; the parser's data shape pins the contract the rest of the pipeline builds to.
- Commits:
- What changed: New skills/public/handoff/scripts/chunked_routing_lib.py (292 lines): shared dataclasses (HandoffEntry, ChunkCandidate, RankedChunk, MergeProposal) with to_dict() for JSON round-trip; is_nontrivial_token helper enforcing the spec's path-separator + common-noun exclusion; parser logic (extract_next_session_block, _split_numbered_items, _extract_title with soft-wrap collapse, _collect_paths, _collect_issues, _collect_skills, _build_boundary_tokens, parse_handoff_entries). New skills/public/handoff/scripts/parse_handoff_entries.py (94 lines): CLI surface emitting JSON to stdout. New tests/fixtures/handoff-snapshot-2026-05-28.md (copy of docs/handoff.md as the slice-2 fixture). New tests/test_handoff_chunker_parse.py (160 lines, 10 tests).
- Alternatives rejected: (1) Using from __future__ import annotations + @dataclass: rejected because @dataclass(frozen=True) under Python 3.10 introspects the class module for KW_ONLY resolution and the repo's load_path_module pattern (used by parse_handoff_entries.py) does not register loaded modules in sys.modules, causing an AttributeError. Solution: no future-import in the lib module, use PEP 585 annotations directly. (2) field(default_factory=tuple): rejected for the same reason; tuples are immutable so '= ()' is equivalent and avoids the dataclass introspection path. (3) Bare-path regex with {1,} segments: rejected because it over-captured 'origin/', '184/', 'product/' from prose like 'origin/main' and 'product/AI-ML'. Required ≥2 segments for the directory form; also dedup paths after normalization so '../foo.md' and 'foo.md' canonicalize to one.
- Targeted verification: pytest tests/test_handoff_chunker_parse.py -v: 10 passed in 2.40s. ruff check on the three new Python files: All checks passed. mypy: not installed in this environment; deferred. End-to-end CLI smoke against current docs/handoff.md: 7 entries parsed with the expected shape (entry 1's referenced_paths deduped to one canonical artifact path; entry 2's boundary_tokens correctly contains only 'integrations/tools/' and not the common-noun bare-directory siblings; entry 3's title correctly collapses across the soft-wrapped bold marker; entries 2 and 7 share no boundary tokens per the spec's negative merge pair requirement).
- Test duplication pressure: check_duplicates.py --json: [] (no near-duplicates introduced). check_python_lengths.py: my new files 292/94/160 all under the 360-line limit; the only over-limit file is the pre-existing goal_artifact_lib.py at 465/360 (not touched in this slice; would not regress).
- Critique: Same-agent self-check: the parser is small and deterministic with full positive + negative + boundary-condition test coverage. The Title double-prefix bug found by the slice-1 critique applies to slice 5, not slice 2 (parser doesn't write goal artifacts). Slice-level critique deferred to slices 3 and 5 per the goal artifact's Critique Cadence.
- Off-goal findings:
- Lessons carried forward: (1) Python 3.10 + dataclass introspection + bootstrap-loaded modules: when a script loads a sibling lib via spec.loader.exec_module without registering in sys.modules, @dataclass(frozen=True) fails because KW_ONLY resolution looks the class's module up in sys.modules. PEP 585 annotations without future-import work fine. (2) Path-token regex needs ≥2 segments minimum for the trailing-slash directory form, otherwise prose tokens like 'origin/main' and 'product/AI-ML' over-capture. (3) Markdown soft-wrap can split bold markers across source lines; the title regex needs re.DOTALL and the captured value needs whitespace normalization.
- Metrics: tests: 10 passed; new code: 546 lines (lib 292 + cli 94 + tests 160); duplicate pressure: 0 matches; ruff: green; mypy: not available

### Slice 3: Generative-sequence ranker packet + validator

- Objective: Build the agent-side ranker substrate: a self-contained JSON packet (canonical generative-sequence prompt + response schema) that the agent fills, plus a deterministic validator that rejects bad shape (length, label uniqueness, contiguous-rank permutation, non-empty reasoning) and a materializer that returns RankedChunk records sorted by rank.
- Why this approach: Core value of the goal; LLM-judgment heavy slice with the named correctness risk 'generative-sequence judgment is hard to get right and easy to drift on prompt changes'. The slice ships the substrate that pins the contract loudly enough for prompt drift to break tests.
- Commits:
- What changed: skills/public/handoff/scripts/chunked_routing_lib.py: added RANKER_PACKET_VERSION constant, RANKER_PROMPT canonical generative-sequence prompt, _RESPONSE_SCHEMA dict, build_ranker_packet(), validate_ranker_response() (structural-only validator), parse_ranked_chunks() materializer, MergeProposal.all_candidates() helper. skills/public/handoff/scripts/prepare_ranker_packet.py (new, 102 lines): CLI reading a MergeProposal JSON from --merge-proposal <path-or-stdin> and emitting the packet on stdout. tests/test_handoff_chunker_ranker_packet.py (new, 220 lines, 14 tests): packet version/shape, prompt drift anchors (generative sequence + why-not + cheapest-first + alphabetical + input order), schema requires three fields, validator accept + reject paths for missing/duplicate/unknown/non-contiguous/empty/wrong-length, materializer sort + reasoning round-trip, CLI stdin round-trip. tests/test_handoff_chunker_why_not_followup.py (new, 123 lines, 2 tests): pins the User Acceptance criterion that every RankedChunk carries non-empty reasoning so a 'why not chunk N?' follow-up answers from already-computed reasoning without re-invoking the ranker.
- Alternatives rejected: (1) Nested-subagent grader for semantic ranking quality: rejected because slice 3's Stop Condition in the goal artifact explicitly avoids requiring nested subagent spawning. (2) Embedding jsonschema as a dependency: rejected because the validator's checks (length, labels, contiguous ranks, non-empty reasoning) are tighter than what JSON Schema alone expresses (contiguous-permutation invariant) — a manual validator is simpler and dependency-free. (3) Packet over stdout vs JSON file: chose stdout so the CLI composes cleanly with the slice 4/7 pipeline scripts.
- Targeted verification: pytest tests/test_handoff_chunker_ranker_packet.py tests/test_handoff_chunker_why_not_followup.py tests/test_handoff_chunker_parse.py -v: 26 passed in 2.47s. ruff check on the four touched files: All checks passed. CLI smoke: prepare_ranker_packet.py --merge-proposal - with a synthetic MergeProposal on stdin emits a well-formed packet on stdout (covered by test_cli_emits_valid_packet_from_merge_proposal_stdin).
- Test duplication pressure: check_duplicates.py --json: [] (no near-duplicates). chunked_routing_lib.py is now 453 lines (above the soft 360-line limit but check_python_lengths.py is informational, not a hook gate; goal_artifact_lib.py is the precedent at 465 lines). Net test code added this slice: 343 lines (220 + 123), all fixture-driven against the slice-2 handoff snapshot.
- Critique: Bounded fresh-eye subagent slice critique (standard tier, agentId af4926ec0074f654f). One Act-Before-Ship + two Bundle-Anyway folded inline; two Over-Worry preserved here. Act-Before-Ship: the test fixture's reasoning text restated objective_summary, modeling the exact anti-pattern the prompt forbids (chunked_routing_lib.py RANKER_PROMPT 'Do not restate the chunk's objective summary'). Folded: both fixture _filled_response functions rewritten to name what each chunk unlocks for the next chunk by label, not restate its own summary. Bundle-Anyway: (a) added explicit prompt-drift phrase anchors for 'cheapest-first', 'alphabetical', and 'input order' in test_packet_carries_canonical_ranker_prompt; (b) extended RANKER_PROMPT with explicit negation of 'input order, alphabetical order, or any other ordering that ignores the unlock relation between chunks'. Over-Worry: validator cannot detect semantically-bad reasoning (by design per slice-3 Stop Condition); test_followup_simulation only proves dict lookup (correct — the User Acceptance contract is data availability). Valid-but-Defer: schema could add 'unlocks: [<labels>]' to force the agent to name the relation, but that requires slice-4 merge-graph awareness — re-evaluate after slice 7 e2e.
- Off-goal findings:
- Lessons carried forward: (1) When a test fixture renders the very anti-pattern the prompt warns against, future maintainers copy the fixture and learn the wrong shape — fixture text is teaching code, not just data. (2) Phrase-anchor assertions catch within-prompt drift that exact-equality assertions miss; the equality assertion goes false only when both sides diverge, but a phrase anchor fails the moment the headline phrase leaves the prompt. (3) For agent-vs-script splits, the script's role is structural validation (shape, contiguity, presence); semantic correctness belongs in the agent + the user-visible rendered output. Pushing semantic grading into the script forces a nested-subagent pattern that is heavier than the contract requires.
- Metrics: tests: 26 passed (2 new files, 14 + 2 cases); ruff: green; duplicate pressure: 0 matches; chunked_routing_lib.py: 454 lines (was 292, +162); prepare_ranker_packet.py: 102 lines; new test code: 343 lines; critique tokens: 58167 / tool_uses: 9 / duration: 67942ms

### Slice 4: Merge proposer

- Objective: Compute pairwise boundary_token overlap across parsed entries, group via connected components, and emit a MergeProposal whose standalone list always carries one ChunkCandidate per entry alongside zero-or-more merged candidates with deterministic labels and human-readable shared_boundary_reason entries. Boundary tokenization is pre-filtered (common-noun exclusion + ≥1 path separator) so common bare-directory roots never trigger merges.
- Why this approach: Granularity decision per goal-artifact Interview Decisions Q2: skill proposes merges, user accepts per-chunk. The merge proposer is the data the agent ranker consumes (standalone + merged candidates ranked together); without it slice 3 has no candidate input shape.
- Commits:
- What changed: skills/public/handoff/scripts/chunked_routing_lib.py: added _candidate_label_from_entries / _candidate_objective_from_entries / _build_standalone / _pairwise_shared_tokens / _connected_components / propose_merges. skills/public/handoff/scripts/propose_merges.py (new, 95 lines): CLI accepting either the full parser payload or a bare entries array via --entries <path-or-stdin>, emitting MergeProposal JSON to stdout. tests/test_handoff_chunker_merge_proposer.py (new, 207 lines, 10 tests): shared-file / shared-skill / shared-policy positive cases; the spec's negative-merge invariant for snapshot entries 2 + 7; whole-snapshot no-spurious-merges; three-way connected-components chain; empty-token never-merge; label-stability under input reorder; standalone-always-present invariant; CLI parser-payload round-trip.
- Alternatives rejected: (1) All-pairs merge candidates instead of connected components: rejected because that over-produces - a chain A↔B↔C would emit three pairs and one triple, four candidates, which inflates the agent's ranking surface without adding signal. Connected components emits one candidate per cluster. (2) Bare set-intersection without label canonicalization: rejected because the label is the join key the agent uses in the ranker response (and the parent uses to look up candidates after the agent fills the response); a non-deterministic label drift would break the round-trip. Sorted indices in the label is the smallest deterministic key.
- Targeted verification: pytest tests/test_handoff_chunker_merge_proposer.py -v: 10 passed in 2.35s. ruff: green. check_duplicates --json: []. CLI smoke covered by test_cli_emits_proposal_from_parser_payload_stdin.
- Test duplication pressure: check_duplicates.py --json: [] (no near-duplicates introduced). New test code added this slice: 207 lines. chunked_routing_lib.py is now ~570 lines (still informational-only via check_python_lengths.py, not a gate).
- Critique: Same-agent self-check: small algorithm (pairwise overlap + union-find), full positive + negative + chain + empty + label-stability coverage. Slice-level critique not required for slice 4 per goal-artifact Critique Cadence (slices 3 and 5 carry the slice-level critique requirement). Deferred semantic concerns: the merge reason text says 'shared boundary tokens: ...' but does not classify by file vs skill vs policy doc - acceptable because the rendered token already carries that information (skills/public/handoff/ vs docs/conventions/...md is self-evident to a reader).
- Off-goal findings:
- Lessons carried forward: (1) Union-find on the overlap graph is the right shape for component-based merging - all-pairs would over-emit redundant candidates. (2) Deterministic label generation is non-negotiable when the label is the join key between agent response and parent materialization. (3) Test fixtures should exercise the production tokenization path (_build_boundary_tokens) rather than hand-construct boundary_tokens, so a tokenization regression breaks merge tests too.
- Metrics: tests: 10 passed; new test code: 207 lines; CLI: 95 lines; chunked_routing_lib.py: +118 lines; ruff: green; duplicate pressure: 0

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
