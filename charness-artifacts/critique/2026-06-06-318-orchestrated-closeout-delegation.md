# Resolution Critique — #318 orchestrator-owned achieve closeout proof delegation

- Date: 2026-06-06
- Issue: #318 (Support orchestrator-owned external proof for achieve sub-goal closeout)
- Goal: `charness-artifacts/goals/2026-06-06-318-319-achieve-closeout-and-quality-headroom.md`
- Target reference: code-critique / issue-resolution critique (mandatory for the
  prompt/skill + validator surface change, per the goal Boundaries)

## Execution

Fresh bounded subagent reviews (canonical path): three angle reviewers
(honesty-boundary, enforcement-correctness, acceptance/integration) + one
counterweight pass + two post-fix re-reviews.

- Fresh-Eye Satisfaction: parent-delegated (bounded subagents).
- Packet Consumed: n/a (no critique-adapter `packet_sections`).

## Change

An opt-in orchestrator/sub-goal closeout-proof delegation contract for `achieve`:
a sub-goal can honestly close at `impl-local`/`carrier` while a *named*
orchestrator goal owns the deferred external proof, without weakening standalone
goals.

- NEW `goal_artifact_closeout_delegation.py` — the gate (`parse_closeout_delegation`,
  `apply_closeout_delegation`), wired into `check_complete_evidence`; surfaced in
  `check_goal_artifact.py`.
- Closeout-state taxonomy (`impl-local`, `carrier`, `pushed-ci`,
  `applied-restarted`, `live`, `issue-closed`) + the orchestrated-closeout
  contract in `references/lifecycle.md`, `references/goal-artifact.md`,
  `docs/prescribed-skill-closeout-contract.md`.
- `attention-state-visibility.json` declares the new module's `skipped` state.
- Tests: `tests/quality_gates/test_goal_artifact_closeout_delegation.py`.

Success line: the orchestrator cannot silently forget delegated proof, a
sub-goal cannot delegate into the void, and standalone closeout is unchanged.
Out of scope: cross-goal orchestrator existence/coverage validation; any live /
release proof (repo-internal contract change).

## Angles + Findings

1. **Honesty boundary** — verdict: standalone provably untouched; the delegation
   gate only ever sets `report["ok"] = False`, runs after all existing floors,
   and relaxes nothing. Found **1 BLOCKER** (now fixed): a blank
   `Orchestrator goal:` field captured the next line via a cross-newline `\s*`,
   dodging "name an orchestrator."
2. **Enforcement correctness** — verdict (initial): NOT correct. Found **3
   BLOCKERS** (now fixed): negated `verified` ("not verified yet") passed as
   resolved; a blank line inside the checklist hid later unresolved items; a
   trailing clause on `Closeout mode: standalone (...)` reclassified the mode and
   *blocked a standalone goal* (a non-weakening violation). Plus a **bundle**:
   sub-bullets treated as items (over-block).
3. **Acceptance / integration** — verdict: ACCEPTANCE MET, INTEGRATION CLEAN. All
   five #318 acceptance criteria mapped to evidence; mirror byte-identical; leaf
   pattern consistent; `## Closeout Delegation` correctly NOT in
   `REQUIRED_SECTIONS` (opt-in is the grandfather); SKILL.md not edited (headroom
   intact); producer contract unchanged.

## Blocker fixes (re-reviewed CLEAR / ENFORCEMENT CORRECT)

- Same-line field capture (`[ \t]`, never `\s`) → blank field no longer borrows
  the next line.
- `_item_resolved` resolves skip/issue first, then `verified` only when an
  affirmative form (`_NEG_BEFORE_VERIFIED` rejects negation-before-verified).
- `_delegated_items` tolerates blank lines inside the checklist (stops only at a
  non-blank, non-list line) → later unresolved items can't escape.
- Mode = first bareword of the value → trailing clauses can't reclassify a mode;
  `standalone (...)` stays standalone.
- Regression tests added for each blocker; 19 delegation tests pass; broad gate
  72/0; honesty + enforcement re-reviews returned CLEAR / ENFORCEMENT CORRECT.

## Counterweight Triage (four bins)

- **Act Before Ship:** the 4 blockers above. *Already fixed and re-reviewed.*
- **Bundle Anyway:** a one-line doc note that orchestrator-goal existence/coverage
  is intentionally unchecked (the fresh-eye disposition review judges it). *Added
  to `goal-artifact.md`.*
- **Over-Worry:** presence-based resolution is "gameable" (`skipped: x`, 1-char
  name, `#0`) — this is the documented, deliberate floor philosophy (deterministic
  teeth narrow + ungameable; substance to the fresh-eye review); sub-bullet
  over-block (conservative, never a bypass); `#\d+` matching any issue-ish token
  (the documented "split into a follow-up issue" path).
- **Valid but Defer:** the `_NEG_BEFORE_VERIFIED` guard fires on any negation word
  before `verified` on the line, so `no blockers; … verified` over-blocks. It
  errs SAFE (refuse, never bypass) with a trivial author remedy (the canonical
  `verified: …` form); tightening to adjacency would re-open the "not yet
  verified" bypass, so it is deliberately left erring-safe.

## Deliberately Not Doing

- Not validating that the named orchestrator file exists / covers the delegated
  items: cross-goal, fragile; the orchestrator's own checklist + the fresh-eye
  disposition review are the teeth (rung-1/rung-2 split).
- Not adding a min `skipped:`-reason length: a length floor is the #305
  word-list/brittleness trap one level up; presence + fresh-eye review is the
  documented line.
- Not narrowing `#\d+` to `issue #N`: bare issue refs are a valid
  "split-to-follow-up" resolution per the contract.
- Not filing a follow-up issue: all residuals are documented intended behavior or
  an err-safe polish, none is deferred work.

## Next Move

Ship #318 as-is. Commit with `Close #318`. No further code change, no min-length
floor, no follow-up issue.
