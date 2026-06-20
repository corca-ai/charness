# Code Critique — quality `## Load-Bearing Anchors` concept-split (north-star sweep WS-B unblock)

- Target reference: `code-critique` (skill-surface contract change; concept-separation + losslessness focus)
- Fresh-Eye Satisfaction: parent-delegated (3 bounded reviewers: orphan-hunter REFUTE-lossless + consumer-contract/safety + concept-separation counterweight)

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: model=opus (Claude Code host resolution of high-leverage; the Codex-host mapping is model=gpt-5.5, reasoning_effort=medium, service_tier=priority)
- Host exposure state: requested_fields_sent
- Application state: 3 bounded reviewers spawned via the Agent tool in the shared parent worktree, read-only (`git show HEAD:<path>` for prior versions, no index/worktree-mutating git ops); the host does not echo resolved spawn fields, so application is unverified-by-carrier (not claimed host-confirmed).

## Diff Scope

The `quality` skill's capped `## Load-Bearing Anchors` catalog (21 dense bullets; body
was at the 200-line cap, 0 headroom) was dissolved by concept-separation:

- **Routing detail → `references/inventory-dispatch.md`** (CLI/docs/skills/runtime/
  source-hygiene/language-lint/agent-runtime/behavior-evaluator/ratchets), each moved
  phrase carried verbatim so the test pins re-point with only a file-variable flip.
- **CORE-contract phrases + always-loaded judgment → `SKILL.md` `## Workflow`/`## Guardrails`**,
  folded verbatim: the cautilus planner-consult + repo-owned-wrapper refuse rule
  (Workflow step 3), the implement-in-same-turn rule (step 7), the producer-side-validators
  rule + the fresh-reader / stale-gate-hidden-network / smaller-surface / disclosure cues
  (Guardrails), and the prompt-bulk trigger required by `validate_quality_closeout_contract.py`.
- **`## Load-Bearing Anchors` → a short branch-reliable `## Routing` pointer** to
  inventory-dispatch.md.
- **~40 test pins re-pointed** across `test_quality_skill_docs.py`,
  `test_docs_and_misc.py`, `test_quality_dual_implementation.py`: moved phrases now
  assert against the dispatch reference; judgment/CORE/intro/output-shape/Workflow-step-8
  phrases stay asserting against SKILL.md.

Plugin mirror synced. SKILL.md 200/200 → 191/200 (9 headroom restored). Losslessness
oracle = the green test suite: full `tests/quality_gates/` = 2283 passed;
`check_skill_contracts` (13 core + 8 package), `validate_quality_closeout_contract`,
`validate_skills`, ergonomics, markdown, doc-links, staged-mirror-drift all green.

## Angles

- **Orphan-hunter (REFUTE "lossless"):** trace every old anchor cue into the new package;
  find any load-bearing cue dropped to zero homes that no test pins.
- **Consumer-contract + always-loaded safety:** is the cautilus-refuse safety still in the
  BODY (not reference-only)? Is the `## Routing` pointer branch-reliable? Did any always-loaded
  promise weaken to reference-only inappropriately? Is the CORE-body / PACKAGE-reference split right?
- **Concept-separation counterweight:** did judgment leak to dispatch or routing strand in the
  body? Is the test re-pointing legitimate (genuine routing detail) or gaming (a body-contract
  quietly downgraded)? Is the de-dup a genuine single-source merge? Any over-build / internal dup?

## Findings → Counterweight four-bin triage

**Act Before Ship:**
- None. All three reviewers returned clean: orphan-hunter = `LOSSLESS-CONFIRMED` (21/21 anchors
  preserved, zero orphans); consumer-contract = `RELOCATION-SOUND` (cautilus refuse stays in body
  at `SKILL.md` Workflow step 3 and is still gate-enforced by the unchanged
  `check_skill_contracts.validate_core_contract`); counterweight = `SEPARATION-HONEST`
  (zero `$SKILL_DIR/scripts/inventory_*` routing lines left in the body; every sampled re-pointed
  phrase genuinely moved SKILL→0 / dispatch→≥1; de-dup is a true single-source merge).

**Bundle Anyway (applied):**
- None. The change is internally complete and synced; no cheap prevention item was missing.

**Over-Worry (no change):**
- `runtime_budget_profiles` appears twice in dispatch — REJECTED as a problem: one is the
  adapter-config directive, one is the runtime-review checklist line; distinct purposes.
- `command_timing_log` / the robustness request-report vocabulary look dropped from top-level
  prose — REJECTED: intact in their canonical deeper homes (`adapter-contract.md`,
  `behavior-testing.md`); the dissolution de-duplicated rather than lost them.
- The dropped "name the structural simplification or ownership clarification" remedy phrasing —
  REJECTED: intentional dedup; the merged guardrail keeps the action-oriented remedy ("delete,
  merge, split ownership, extract a helper, or narrow the interface") and the pinned heuristic string.

**Valid but Defer:** see Deliberately Not Doing.

## Deliberately Not Doing

- **Drop the dead `PRESSURE_EXEMPT_H2_SECTIONS = {"Load-Bearing Anchors", "References"}` key.**
  `## Load-Bearing Anchors` no longer exists in quality SKILL.md, so the exemption key is now
  dead config for this skill (harmless — the folded prose sits in non-exempt `## Workflow`/
  `## Guardrails` and still passes the core-pressure gate with 42 lines of headroom). The key is a
  GENERIC exemption that other skill packages may still use; removing it blindly could un-shelter
  another skill's anchor section. Deferred to a scoped follow-up that greps all skills before
  touching `skill_ergonomics_lib.py` + its mirror + `authoring-preflight.md`.
- **Re-add the evaluator-before-HITL *precedence* as an always-loaded body cue.** "use `quality`
  before downgrading to HITL" moved to dispatch (and its tests re-pointed there). Two reviewers
  judged this defensible as-is: it is genuinely routing-precedence detail, and the always-loaded
  guarantee is already owned by `CLAUDE.md` top-level ("Route evaluator-backed validation through
  `quality` before `hitl`"). Re-adding it to the body would re-duplicate across body↔dispatch and
  muddy the clean separation just achieved; left in dispatch with the CLAUDE.md top-level cover.

## Next Move

Record the public-skill review decision (lossless structural relocation; consumer contract
preserved — no dogfood re-run, the routing/judgment content is identical, only relocated; CORE
always-loaded promises intact in the body and still gate-enforced), then run the final
`--verification-lock` closeout with `--ack-cautilus-skill-review` (cautilus `next_action: none`
→ ask-before-run, do NOT run `cautilus evaluate`; deterministic gates + fresh-eye own closeout).
Commit direct-to-default; update the sweep goal ODQ + handoff Tier 3 to "executed". This does NOT
close #391 or the sweep goal's remaining body-redesign follow-ons (impl/debug/achieve still pending).
