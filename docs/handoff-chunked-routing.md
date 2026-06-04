# Handoff Chunked Routing

This document is the implementation contract for the
[handoff auto-chunking goal](../charness-artifacts/goals/2026-05-28-handoff-chunked-routing.md).
It owns the algorithm, data shape, deterministic-vs-LLM split, trigger rule,
auto-draft template, and skill-surface plan that slices 2–7 build to. The goal
artifact's `Boundaries`, `User Acceptance`, and `Stop Conditions` remain
authoritative; this spec narrows them to concrete files, regex, and JSON.

The chunker is an additive workflow phase of the existing
[`handoff`](../skills/public/handoff/SKILL.md) skill. It absorbs the recurring
manual cost of reading [`docs/handoff.md`](./handoff.md), deciding which
residual entries unblock others, picking an advantageous order, and shaping a
`/goal` activation. It does not absorb the existing handoff responsibilities
(state selection, spill targets, continuation sequence) and does not modify
[`/achieve`](../skills/public/achieve/SKILL.md).

## Problem

The current `handoff` skill produces an ordered `## Next Session` list. The
user then repeats four manual moves every session:

1. Read each residual entry and infer which ones unblock others.
2. Re-rank into a generative sequence (Christopher Alexander idiom from
   [`issue` step 5](../skills/public/issue/SKILL.md): the move that reduces
   uncertainty or unlocks the next issue comes first).
3. Identify entries that share an artifact / skill / policy boundary and
   could be bundled.
4. Open the achieve goal artifact template and hand-fill Title + Goal +
   Non-Goals + Boundaries so the achieve Before-phase can shape it into a
   runnable goal.

These four moves are session-repeating cost that the skill should own.

## Scope

This contract changes:

- `skills/public/handoff/` — new conditional workflow phase wired into
  [`SKILL.md`](../skills/public/handoff/SKILL.md) (≤10 line net growth so the
  200-line cap retains ≥40-line headroom); body lives in a new
  `<repo-root>/skills/public/handoff/references/chunked-routing.md`; new
  scripts under `<repo-root>/skills/public/handoff/scripts/`:
  - `<repo-root>/skills/public/handoff/scripts/parse_handoff_entries.py`
    (slice 2) — deterministic parser
  - `<repo-root>/skills/public/handoff/scripts/prepare_ranker_packet.py`
    (slice 3) — deterministic packet builder for the agent-side ranker
  - `<repo-root>/skills/public/handoff/scripts/propose_merges.py` (slice 4)
    — deterministic merge proposer
  - `<repo-root>/skills/public/handoff/scripts/draft_goal_from_chunk.py`
    (slice 5) — deterministic auto-draft writer
  - shared `<repo-root>/skills/public/handoff/scripts/chunked_routing_lib.py`
    for record types and helpers
- `<repo-root>/tests/` — fixture-backed unit tests per slice plus an
  end-to-end test feeding a known handoff snapshot to the chain and
  asserting the rank + merge + draft output.

This contract does **not** change:

- The `/goal` host runtime.
- The `/achieve` skill or its Before-phase interview ([`achieve/SKILL.md`](../skills/public/achieve/SKILL.md),
  [`achieve/scripts/check_goal_artifact.py`](../skills/public/achieve/scripts/check_goal_artifact.py));
  the auto-draft writer produces an artifact that satisfies the existing
  shape contract exactly as a hand-shaped goal would.
- Any file under `skills/public/achieve/` (slice-5 Standalone-Usefulness
  Invariant from the goal artifact's Low-Cost Checks).
- The other handoff responsibilities (state selection, spill targets,
  continuation sequence); the chunker is an additive conditional phase.

## Deterministic-Vs-LLM Split

Each step is classified so slice 6 (SKILL.md wiring) and slice 7 (closeout
verification) agree on what is script vs agent.

| Step | Layer | Why |
| --- | --- | --- |
| Trigger detection | deterministic regex (Python) | Operationally exact; slice 6 SKILL.md prose, slice 7 verification, and the spec fixture all consult the same rule. |
| Handoff entry parsing | deterministic (Python) | Markdown structure; testable in isolation against current handoff.md as fixture. |
| Generative-sequence ranking | agent (LLM) with deterministic packet | Judgment-heavy; mirrors `issue` skill step 5 which is also agent-side. Script builds the packet (candidates + prompt + JSON schema); agent fills it; script validates round-trip. |
| Merge proposal generation | deterministic (Python) | Pure set-overlap on parsed boundary tokens; pre-LLM. |
| Merge acceptance | user-in-the-loop | User accepts/rejects per chunk in the same conversational turn the ranking is presented. |
| Auto-draft writer | deterministic (Python) | Template substitution at fixed depth; [`check_goal_artifact.py`](../skills/public/achieve/scripts/check_goal_artifact.py) is the post-condition. |
| "Why not chunk X?" follow-up | agent (LLM) using already-computed reasoning | No fresh recomputation; per User Acceptance criterion. |

The script side is portable and fixture-testable. The agent side is bounded
by the structured packet and the post-validator, so a prompt drift fails the
fixture loudly per the goal artifact's High-Confidence Checks.

## Trigger Detection Rule

The chunker fires iff there is **no explicit task directive** AND a
**handoff signal** is present — for the current user invocation (the most
recent user-authored message before the agent acts):

1. **No explicit task directive.** The invocation contains none of:
   - an imperative verb naming a concrete next action paired with a noun
     other than the handoff itself: `do <X>`, `fix <X>`, `implement <X>`,
     `close <X>`, `push <X>`, `run <X>`, `start <X>`, `work on <X>`,
     `resolve <X>`, `merge <X>`, `release <X>`, `revert <X>`
   - an explicit issue id pattern `#\d+`
   - a file path other than the handoff itself
   - a slash command other than `/handoff`
   - a `--<flag>` token

   A task directive always bypasses, **even on a direct invocation that
   carries one** (`/handoff fix #233` does not fire).
2. **Handoff signal**, at least one of:
   - literal token matching the handoff artifact path
     ([`docs/handoff.md`](./handoff.md)), its bare basename, or `/handoff`
   - phrase `handoff skill` / `handoff 스킬` / `charness:handoff`
   - imperative referencing the handoff surface without naming a task:
     `read the handoff`, `check the handoff`, `read handoff`,
     `what's in the handoff`, `next from handoff`, `pick up from handoff`,
     `핸드오프 봐` (or any case variant)
   - **direct skill invocation** (`should_fire_chunker(..., invoked_directly=True)`):
     the handoff skill was launched with no task. Invoking the skill is itself
     a handoff signal — no doc mention required (#249 trigger widening).

The directive negation is intentionally narrow: "read the handoff" is *not*
a task directive against another noun, so it triggers; "read handoff and
push slice 7" *is* a task directive against another noun, so it does not.

### Trigger Fixture

The fixture below is the source of truth for slice 2 parser tests,
slice 3 ranker integration, slice 6 SKILL.md prose, and slice 7 closeout
verification. It MUST live verbatim in
`<repo-root>/tests/test_handoff_chunker_trigger.py` (created by slice 7)
as test parametrize data so a divergence between spec and tests fails
loudly.

| # | Example user message | Expected decision | Why |
| --- | --- | --- | --- |
| 1 | `read docs/handoff.md` | `chunk` | Handoff mention + no other directive. |
| 2 | `what's next in the handoff?` | `chunk` | Handoff mention via prose + question form, no directive. |
| 3 | `read handoff and start slice 7` | `no-chunk` | Handoff mention + explicit directive `start slice 7`. |
| 4 | `push the slice 7 commits` | `no-chunk` | No handoff mention. |
| 5 | `핸드오프 봐` | `chunk` | Korean handoff mention, no directive. |
| 6 | `read handoff.md and fix #233` | `no-chunk` | Handoff mention + issue id directive `fix #233`. |
| 7 | `pick up from handoff` | `chunk` | Handoff pickup phrase, no other noun. |
| 8 | `/handoff` | `chunk` | Bare slash invocation of the handoff skill, no task (#249). |
| 9 | `/handoff fix #233` | `no-chunk` | Skill invocation + explicit issue directive bypasses. |

Rows 8-9 are the #249 trigger-widening cases. The `invoked_directly=True`
path (the skill launched programmatically with no task arg) is pinned by
`test_direct_invocation_fires_without_a_mention` in the same fixture file.

If trigger detection over-fires against any case 3, 4, or 6 row, the goal
artifact's "Trigger detection over-fires" Stop Condition activates: stop
and re-anchor the rule.

## Data Structures

Defined in `<repo-root>/skills/public/handoff/scripts/chunked_routing_lib.py`.
All
records are plain `dataclasses` with `to_dict()` for JSON serialization so
the agent-side ranker packet round-trips through stdout/stdin.

```python
@dataclass(frozen=True)
class HandoffEntry:
    index: int                    # 1-based position in `## Next Session`
    title: str                    # bold-leading-phrase before the first period
    body: str                     # full prose under the bullet
    referenced_paths: tuple[str, ...]   # markdown links + literal repo paths
    referenced_issues: tuple[int, ...]  # #NNN patterns
    referenced_skills: tuple[str, ...]  # `skills/public/<name>/` tokens
    boundary_tokens: tuple[str, ...]    # full path strings (not split
                                        # components): paths + skill ids +
                                        # policy doc paths. See "Boundary
                                        # tokenization" below.

@dataclass(frozen=True)
class ChunkCandidate:
    entries: tuple[HandoffEntry, ...]    # one or more; >1 means merged
    label: str                           # slug derived from titles
    objective_summary: str               # one line; filled by ranker step

@dataclass(frozen=True)
class RankedChunk:
    candidate: ChunkCandidate
    rank: int                            # 1 = first
    reasoning: str                       # 2–3 lines, generative-sequence
                                         # "why this comes first / what it unlocks"

@dataclass(frozen=True)
class MergeProposal:
    standalone: tuple[ChunkCandidate, ...]  # one ChunkCandidate per entry
    merged: tuple[ChunkCandidate, ...]      # zero or more multi-entry candidates
    shared_boundary_reason: dict[str, str]  # merged.label -> human reason
```

## Algorithm

The chunker runs as a six-step pipeline. Steps 1, 2, 3, 5, 6 are scripts;
step 4 is the agent.

1. **Parse.** [`parse_handoff_entries.py`](../skills/public/handoff/scripts/parse_handoff_entries.py) reads the resolved handoff
   artifact, finds the `## Next Session` section, splits on numbered
   bullets, and emits a list of `HandoffEntry` records. It filters numbered
   local-state preflight checks (`git status`, `git log`, `gh issue list`) and
   activation entries whose referenced goal artifact is already
   `Status: complete`; those are pickup setup or stale state, not chunks to ask
   the user to choose. `During`/`while` cadence or invariant entries are also
   treated as execution constraints, not standalone choices. Additional
   residual-work sections (e.g., `## Discuss`) are read only if the
   adapter declares them; default scope is `## Next Session` only.
2. **Prepare deterministic hints.** [`propose_merges.py`](../skills/public/handoff/scripts/propose_merges.py) consumes the entry list,
   computes pairwise `boundary_tokens` overlap, and emits a
   `MergeProposal`. The standalone list always contains one
   `ChunkCandidate` per entry. The merged list contains additional
   multi-entry candidates whose member entries share at least one
   non-trivial token, where **non-trivial** is defined below under
   "Boundary tokenization". These overlap candidates are hints for the
   package proposer, not the final list shown to the user.

### Boundary Tokenization

A `boundary_token` is a *full path string* (or skill id / policy doc
path), never a split path component. This avoids over-merging on the
common directory roots that most handoff entries reference.

A token is **non-trivial** when both of the following hold:

- it is not in the common-noun exclusion set
  `{docs, skills, scripts, tests, .githooks, plugins, integrations}`
- it contains at least one path separator `/` (so a bare directory
  name like `scripts/` does not count as overlap; two entries must
  share a deeper sub-path like a specific check script path or
  `skills/public/handoff/` to merge)

Skill ids are normalized to `skills/public/<id>/`. Policy doc paths
under `docs/conventions/` count as one token (the full filename
path), not as `docs` + `conventions`. The merge proposer's
`shared_boundary_reason` entry quotes the actual shared token(s) so
the user sees the basis for the merge proposal.

Slice-4 merge fixture must include a negative case (entries 2 and 7
of the current handoff, which both mention bare `tests` and
`scripts` but share no deeper path) that asserts they do **not**
merge.
3. **Propose work packages.** [`prepare_chunk_packet.py`](../skills/public/handoff/scripts/prepare_chunk_packet.py) writes a JSON packet containing
   source IDs, overlap hints, adapter chunk policy, prompt, and response schema.
   The agent fills a `chunks` array with coherent work packages rather than a
   ranked issue list. Each package carries source IDs, excluded nearby IDs when
   relevant, objective, rationale, downstream unlock, and basis boundary tokens
   when tokens justify a merge. `validate_chunk_proposal_response` rejects
   unknown, duplicated, missing, or over-large sources, empty rationale, and
   broad-label-only merges unless adapter policy explicitly allows that label;
   its merge policy facts are diagnostic only, so no broad-only warning does not
   mean merge clearance and unknown basis tokens mean policy has no opinion;
   `materialize_chunk_proposal_response` converts the validated packages into a
   `MergeProposal`.
4. **Rank.** [`prepare_ranker_packet.py`](../skills/public/handoff/scripts/prepare_ranker_packet.py) writes a JSON packet containing
   the package `MergeProposal` plus the canonical generative-sequence prompt.
   The agent fills it, producing a list of `RankedChunk` records (one
   per standalone + one per merged candidate; agent picks which to
   present). The packet's JSON schema is asserted by a round-trip
   fixture so prompt-shaped drift fails loudly.
5. **Present.** The handoff skill renders the ranked list inline in the
   conversation: one chunk per line with rank, label, objective summary,
   and the 2–3 line generative-sequence reasoning. Work-package candidates are
   labelled `(package: <reason>)`. The user picks one chunk (or none) and
   may ask "why not chunk X?" in the same turn; the agent answers from
   the already-rendered reasoning.
6. **Draft.** On user selection, [`draft_goal_from_chunk.py`](../skills/public/handoff/scripts/draft_goal_from_chunk.py) calls
   [`goal_artifact_lib.upsert_goal`](../skills/public/achieve/scripts/goal_artifact_lib.py)
   to write the goal artifact at
   `<repo-root>/charness-artifacts/goals/<yyyy-mm-dd-slug>.md` at status
   `draft`, then runs the auto-draft template described below. The drafter
   returns `next_step` / `shape_command` (`/achieve @<artifact>`) as the
   operator's next move: the draft is unshaped, so the achieve Before-phase
   must fill it before `/goal @<artifact>` (the artifact's `activation`
   line) starts the During run (#246).

## Auto-Draft Template

The draft writer fills exactly four sections plus the seeded portability
section:

- **Title**: the `title` argument passed to
  [`upsert_goal`](../skills/public/achieve/scripts/upsert_goal.py) is
  `<one-line objective from chunk>` only. The template at
  [`goal_artifact_lib._TEMPLATE`](../skills/public/achieve/scripts/goal_artifact_lib.py)
  already wraps it in `# Achieve Goal: {title}`, so passing
  `"Achieve Goal: <objective>"` would produce a double prefix. The slice-5
  fixture asserts the rendered heading line is exactly
  `# Achieve Goal: <objective>` (single prefix).
- **Goal**: the chunk's objective summary expanded to a short paragraph,
  followed by the source handoff entry quoted verbatim as a blockquote.
- **Non-Goals**: a bulleted list seeded with two defaults the writer
  always inserts:
  - `Not a release: no plugin version bump expected.` (unless the source
    entry mentions release wording)
  - `Do not absorb adjacent handoff entries beyond the selected chunk.`
- **Boundaries**: a bulleted list seeded with:
  - `In scope: <referenced paths from the source entry, deduped>`
  - `Portable per implementation-discipline: no host-specific assumption.`
  - the verbatim Stop Conditions line:
    `Stop conditions: name on first discovery; do not guess.`
- **Context Sources**: seeded with the source handoff entry citation and
  any cited artifact paths from the entry body (preserves provenance for
  the achieve Before-phase per the goal artifact's slice-5 portability
  decision).

The writer leaves these sections as empty H2 headings with a single
placeholder line:

- **User Acceptance**: `*To be filled by the achieve Before-phase interview.*`
- **Agent Verification Plan**: same placeholder.
- **Slice Plan**: header row + separator only, no data rows — the
  `/achieve` Before-phase fills the slice rows.
- **Interview Decisions**:
  `*To be filled by the achieve Before-phase interview.*`
- **Plan Critique Findings**:
  `*To be filled by the achieve plan-critique pass.*`

The auto-draft seeds all three portability headings (`Context Sources`,
`Interview Decisions`, `Plan Critique Findings`) from the
[goal-artifact template](../skills/public/achieve/scripts/goal_artifact_template.md),
so the draft passes the always-on portability check at write time (#255
removed the trivial-goal exemption; the seeded headings — not an exemption —
are what keep the check satisfied).

### Auto-Draft Post-Condition

After write, the writer runs
[`check_goal_artifact.py`](../skills/public/achieve/scripts/check_goal_artifact.py)
in-process against the new artifact. `ok=true` at status `draft` is the
post-condition; any failure aborts the write and surfaces the
`check_goal_artifact` issues list.

The slice-5 fixture asserts:

- The rendered heading line is exactly `# Achieve Goal: <objective>`
  (single prefix; no double `Achieve Goal:` wrap).
- `Context Sources` is non-empty (contains at least one citation).
- `User Acceptance`, `Agent Verification Plan`, `Interview Decisions`,
  and `Plan Critique Findings` contain only the placeholder line — no
  data rows, no sub-headings, no narrative prose.
- `Slice Plan` data row count is `0`.
- No file under `skills/public/achieve/` was touched
  (`git diff --name-only` returns empty for that prefix).

## Skill Surface

[`skills/public/handoff/SKILL.md`](../skills/public/handoff/SKILL.md)
gains only:

- one short trigger paragraph (the rule above, ≤4 lines)
- one pointer to the new reference file at
  `<repo-root>/skills/public/handoff/references/chunked-routing.md`
- one workflow-step bullet under the existing `## Workflow` numbered
  list: "When the trigger fires (see the chunked-routing reference),
  invoke the chunker pipeline before refresh-vs-pickup classification."

Net growth target: ≤10 lines. SKILL.md is 151 lines today (cap 200); the
slice-6 verification gate is `wc -l skills/public/handoff/SKILL.md` ≤ 161.

The new reference file
`<repo-root>/skills/public/handoff/references/chunked-routing.md`
(created by slice 6) holds the full conditional workflow body, the
trigger-rule detail, the chunker pipeline invocation, the auto-draft
handoff prose, and the override-UX prose ("why not chunk X?" answered
from rendered reasoning). It is added to SKILL.md's `## References` per
the `validate_skills` rule that every `references/` file is listed.

## Standalone-Usefulness Invariant

Both directions of standalone usefulness are preserved (goal artifact
F4 of plan critique):

- `handoff` without the chunker still works: the chunker is a new
  *conditional* phase wired behind the trigger rule. A handoff session
  with an explicit task directive (case 3 / 4 / 6) bypasses the
  chunker entirely.
- `/achieve` without a chunker-drafted skeleton still works: the
  auto-drafted skeleton conforms to
  [`check_goal_artifact.py`](../skills/public/achieve/scripts/check_goal_artifact.py)'s
  contract exactly. A hand-shaped goal artifact is indistinguishable
  from an auto-drafted one to the achieve Before-phase.

The slice-5 `git diff --name-only main..HEAD | grep '^skills/public/achieve/'`
gate enforces the second direction mechanically.

## Test Plan

| Slice | Test surface | Fixture |
| --- | --- | --- |
| 2 | `<repo-root>/tests/test_handoff_chunker_parse.py` | current [`docs/handoff.md`](./handoff.md) snapshot copied into `<repo-root>/tests/fixtures/handoff-snapshot-2026-05-28.md`; assert HandoffEntry list shape, count, and boundary_tokens for each entry. |
| 3 | `<repo-root>/tests/test_handoff_chunker_ranker_packet.py` | known parsed entry list + canonical filled-packet JSON; round-trip through [`prepare_ranker_packet.py`](../skills/public/handoff/scripts/prepare_ranker_packet.py) and a validator that asserts the schema. |
| 3 (why-not) | `<repo-root>/tests/test_handoff_chunker_why_not_followup.py` | filled `RankedChunk` list; assert every `reasoning` field is non-empty and >0 chars per chunk, so a "why not chunk N?" follow-up can be answered from already-computed reasoning without re-invoking the ranker (User Acceptance criterion in goal artifact). |
| 4 | `<repo-root>/tests/test_handoff_chunker_merge_proposer.py` | three sub-fixtures: shared-file, shared-skill, shared-policy. Each asserts the merged candidate list contains exactly the expected member entries with the expected reason. |
| 5 | `<repo-root>/tests/test_handoff_chunker_auto_draft.py` | selected `ChunkCandidate` → drafted goal artifact passes [`check_goal_artifact.py`](../skills/public/achieve/scripts/check_goal_artifact.py); portability section content matches the placeholder-or-seeded rule; Slice Plan data row count is 0. |
| 6 | `<repo-root>/tests/test_handoff_skill_md_budget.py` | `wc -l skills/public/handoff/SKILL.md` ≤ 161. |
| 7 (trigger) | `<repo-root>/tests/test_handoff_chunker_trigger.py` | the 7-row fixture above; parametrize over each row. |
| 7 (e2e) | `<repo-root>/tests/test_handoff_chunker_end_to_end.py` | feed the 2026-05-28 handoff snapshot through parse → merge hints → agentic package packet → validated package response → ranker packet → draft; assert final goal artifact passes [`check_goal_artifact.py`](../skills/public/achieve/scripts/check_goal_artifact.py). |

## Stop Conditions

All Stop Conditions from
[the goal artifact](../charness-artifacts/goals/2026-05-28-handoff-chunked-routing.md#boundaries)
remain authoritative. This spec narrows them:

- **Generative-sequence ranker needs nested subagent spawning.** Slice 3
  is implemented as the active agent reasoning over the packet by
  default. Nested subagent spawning is the upgrade path, not the
  base path. If a slice-3 critique demands the upgrade, declare it
  before slice 3 starts and re-run plan critique on the revised plan.
- **Auto-draft writer crosses Boundaries depth.** Slice 5 fixture
  asserts placeholder-or-empty for the `User Acceptance`,
  `Agent Verification Plan`, and `Slice Plan` data rows. Any
  non-placeholder content in those sections at write time fails the
  fixture.
- **Trigger detection over-fires.** The 7-row fixture is the gate. A
  test failure on rows 3, 4, or 6 (the no-chunk cases) flips this Stop
  Condition active; stop and re-anchor before continuing.
- **#233 still open at slice 5.** Slice 5 of this spec does not depend
  on #233 directly (auto-drafted goals are at status `draft` and not
  yet at closeout). Slice 7 (closeout) is the consumer; the decision
  branches there.

## Non-Claims

This spec does not redesign `handoff` (state selection, spill targets,
continuation sequence stay as-is), does not redesign `/achieve`, does
not modify the `/goal` host runtime, does not introduce new GitHub
issues during the run, and does not auto-rank work outside
[`docs/handoff.md`](./handoff.md).

## Critique Findings

Bounded fresh-eye subagent spec critique (standard tier, agentId
`a3b7d3116ace3415c`) run after the initial spec draft, before slice 2
implementation. Reasoning preserved so a fresh session re-verifies the
folded revisions without re-running critique.

### Act Before Ship (folded into the spec)

1. **Title double-prefix bug.** First draft told the auto-draft writer
   to pass `Achieve Goal: <objective>` as the title argument, but
   [`goal_artifact_lib._TEMPLATE`](../skills/public/achieve/scripts/goal_artifact_lib.py)
   already wraps `{title}` in `# Achieve Goal: {title}`. Folded into
   the **Auto-Draft Template** Title bullet and into the slice-5 fixture
   assertion that the rendered heading is exactly
   `# Achieve Goal: <objective>` (single prefix).
2. **"Why not chunk X?" had no test row.** The goal artifact's User
   Acceptance requires the follow-up to answer from already-computed
   reasoning. Folded as a new slice-3 (why-not) row in the Test Plan
   asserting every `RankedChunk.reasoning` is non-empty so a follow-up
   can be sourced without re-invoking the ranker.

### Bundle Anyway (folded; cheap to land alongside Act-Before-Ship work)

1. **Boundary-token canonicalization was undefined.** First draft
   defined `boundary_tokens` informally with the exclusion set
   `{docs, skills, scripts}`. Real handoff entries 2 and 7 share bare
   `tests` and `scripts` without sharing real boundary. Folded into a
   new **Boundary Tokenization** sub-section: tokens are full path
   strings; the exclusion set is widened to
   `{docs, skills, scripts, tests, .githooks, plugins, integrations}`;
   tokens must contain at least one `/` to count as non-trivial; and
   the slice-4 fixture must include a negative case asserting entries
   2 and 7 do not merge.
2. **No prose-in-Acceptance/Verification assertion.** First draft only
   named `Interview Decisions` and `Plan Critique Findings` for the
   placeholder assertion. Folded into the slice-5 fixture assertions
   list: User Acceptance + Agent Verification Plan must also contain
   only the placeholder line (no data rows, no sub-headings).

### Over-Worry (raised, not folded as blockers)

- **Korean variant under-coverage.** Spec lists only `핸드오프 봐` as
  the Korean trigger phrase. Reviewer raised the risk of missing
  `핸드오프 읽어줘` / `핸드오프 확인` variants. Not folded: the goal
  artifact's "Trigger detection over-fires" Stop Condition already
  routes this to re-anchoring once observed in real use; pre-locking
  more Korean phrases speculatively risks over-firing on polite
  refusals like `핸드오프 보지 마`.

### Valid but Defer (real but does not block slice 2)

- **Polite interrogative phrasings.** Forms like "could you check the
  handoff?" are not enumerated in the trigger rule. Becomes relevant
  if the slice-7 e2e fixture adds such a row; safe to add as a new
  fixture row in slice 7 without re-anchoring the rule.
- **Code-fence containment of handoff path mentions.** A message
  quoting code containing the literal handoff path would fire. The
  trigger regex implementation in slice 6/7 can mask fences using the
  same `_mask_fences` trick already in
  [`goal_artifact_lib.py`](../skills/public/achieve/scripts/goal_artifact_lib.py);
  defer the masking decision to that slice.

## References

- [Goal artifact](../charness-artifacts/goals/2026-05-28-handoff-chunked-routing.md)
- [handoff SKILL.md](../skills/public/handoff/SKILL.md)
- [achieve SKILL.md](../skills/public/achieve/SKILL.md)
- [achieve goal-artifact-lib](../skills/public/achieve/scripts/goal_artifact_lib.py)
- [achieve check_goal_artifact](../skills/public/achieve/scripts/check_goal_artifact.py)
- [issue SKILL.md (generative-sequence idiom, step 5)](../skills/public/issue/SKILL.md)
- [issue resolve-flow reference](../skills/public/issue/references/resolve-flow.md)
- [implementation discipline](./conventions/implementation-discipline.md)
- [operating contract](./conventions/operating-contract.md)
- [docs/handoff.md (current snapshot is the slice-2 fixture)](./handoff.md)
