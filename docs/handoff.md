# Charness Handoff

## Workflow Trigger

- **Next pickup:** activate the [carry-the-unbuilt-slices goal](../charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues.md). It is SHAPED and `--pursue-ready` passes, so go straight to `/goal @charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues.md` — no Before phase needed. Read its `## Active Operating Frame` first; it names the exact next action.
- **Slice 1 is `#536`'s closeout, and it retires a SECOND live goal.** [one-rule-one-owner](../charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md) is still `Status: active` owing only that closeout (code and both review rounds committed at `1fa7fd75`). Two live goals is the "one issue, two owners" defect this family keeps repairing in code, so it is first. If `#536`'s floor cannot be met, STOP and record a blocker — do not flip a goal terminal on an unmet floor.
- **Scope is FIVE slices, not nine, and that is a measured decision.** The predecessor planned nine and reached three; the three were good because each got two delegated review rounds. `## Slice Plan` names what is NOT claimed (`#562`, `#560`, `#561`) so the cut is visible rather than implied.
- **Its predecessor [one-cadence-one-owner](../charness-artifacts/goals/2026-08-08-one-cadence-one-owner-stop-contradicting-the-agent.md) is `Status: complete`, closed EARLY at slice 3 of 9** by operator direction. Slices 1-3 shipped with two delegated review rounds each; 4-9 moved to the successor. Its `## User Verification Instructions` names four commands that verify what shipped without re-deriving it.
- **The `#514/#515/#518` freeze decision is CLOSED.** The operator ruled that a locator changed by an unrelated slice may be re-stamped without re-inspection; four of twenty were re-stamped via `validate_issue_source_freeze.py refreeze`, `validate` passes, and the affected tests are green. Each re-stamped locator carries a note recording that no re-inspection happened and what is not claimed. **Standing residue, now `#562`:** measured 0/5 true positives — 6 of 20 locators changed in a day, five prior re-stamps, every one incidental. The remediation is one mechanical command and none of the five recorded a basis, so the gate trains the reflex that defeats it. `#562` carries the measurement and three options; the source-snapshot half of the freeze is sound and explicitly out of its scope.
- **The predecessor [one-rule-one-owner goal](../charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md) is still `active` and still owes only `#536`'s closeout** (code and both review rounds committed at `1fa7fd75`). It was not touched this session except to repair its acceptance line.
- **Closed and verified by the PREVIOUS session: `#552`, `#548`, `#555`, `#537`.** Each through the full closeout floor — `validate-closeout-draft` reporting `draft_verified`, a DELEGATED resolution critique before the close call, and `verify-closeout --expect-state CLOSED` reading state back through the adapter. `#536` is the fifth and is built but NOT yet closed.
- **Ask for the push before anything else.** 23 local commits sit unpushed (`git log --oneline origin/main..HEAD`), four of which carry issue closeouts. `git push` is not a standing approval and must be requested every time. Remote CI is an explicit non-claim for every commit in this range.
- **Filed while working, none planned: `#556`, `#557`, `#558`, `#559`, `#560`, `#561`.** Every one was found by a delegated review or by a gate, not by reading the backlog. `#558` is the sharpest: `(repo, number)` is an issue's identity and only `{number}` is required, so a wrong-repo CLOSED verdict is still reachable.
- **Broad suite proof is NOT current.** The last recorded green (`7871 passed`) predates this session's three commits, and the broad suite is now RED for the freeze reason above. Treat any earlier green line as historical.
- **CONTEXT DISCIPLINE — this is the main operating lesson from the last session.** The broad `pytest tests/` takes ~12 minutes and was run ~13 times, which was the single largest waste. `./scripts/run-quality.sh --read-only` already runs a pytest phase and finishes in ~110s; use it as the slice boundary proof and run the broad suite ONCE, at the commit boundary, not after every repair. Do not poll a background suite with `sleep` loops.
- **Two review rounds, not one, and round 2 reads the REPAIRS. Now 5 for 5 that the repair carried the class it fixed.** In slice 5 the message I wrote was worse than the number it replaced TWICE, both times because I asserted where a fact lived instead of opening the file. Before writing any instruction that tells a reader where to look, open every location it names.
- **Derive a matcher's vocabulary from the surface that PRODUCES the text, not from the instance you measured.** Slice 3's verb list was written from one sentence and missed `bundled` — the word the repo's own authoring reference instructs authors to use — so a gate passed every test while being nearly inert on real ledgers. A reviewer found it; mutation could not.
- **A duplicate-hash chase must not drive the design of a proof surface.** The dup ratchet was right the first time and caught a real defect. Chasing a later ROTATED hash is what routed two `complete`-state floors onto a level-aware section walk — a latent false green, caught only by a second review round. Classify with a reason instead.
- **Verify the reviewer boundary IMMEDIATELY when a reviewer returns, BEFORE repairing.** Missed twice last session; both rounds then needed reconciliation by declaring parent paths, which is weaker because it cannot distinguish reviewer writes from the parent's.
- **A substring pin over a message cannot see an INVERSION.** Swapping two cause lists or two command pairings left ten assertions green while making the message actively harmful. Pin the pairing and the ordering, not the vocabulary.
- **A test whose subject IS live repo state cannot be mutation-tested by editing the worktree.** The edit is itself a state change: mutating a file dirtied the tree, the plan went blocked, and the test failed at an earlier assertion — which I misread as a killed mutant. Prove discriminating power by INJECTION instead.
- **The premise check is now 5 for 5 at changing the build, and once at changing the SLICE.** Slice 5's premise check refused the Slice Plan's bundling of `#536`/`#549`/`#542` — they share a face, not a remedy — and re-homed two as rows 5a and 5b. It also corrected the issue's own reproduction recipe.
- **The commit-msg gate reads prose for GitHub close keywords.** `a fix: #536` inside a sentence blocked two commits because it would have auto-closed the issue on push with no ledger. It was right to.
- Recount the backlog with `gh issue list --repo corca-ai/charness --state open` before reshaping scope; the goal's `## Backlog Recount` describes how to reconcile it programmatically.

## Continuation Capability

- Keep semantic coverage, proof execution, evidence identity, execution root, final consumer, and external observation as separate claims.
- Do not let #518 consume #515's taxonomy, #515 consume #514's taxonomy, or any issue wait on another. Share fields only when one canonical projection producer per field and at least two real readers with identical semantics are proven; source facts may have separate producers.
- At irreversible boundaries, a green gate, `CLOSED` state, or local artifact is provisional; require a different observer and evidence channel.
- Any reviewed input change invalidates packet identity and the verification lock.
- Refresh kept, because each changes the next action: the unified #514/#515/#518 repair goal, the conditional shared-seam decision, independent issue slices, read-only sibling-repo comparison, and the current CI non-claim.
- Refresh non-claims: #516/#517 implementation detail, consumer browser/provider behavior, and any current-head green verdict not proven by an independent run.

## Current State

- #516 and #517 are closed; use them only as typed regression fixtures, not new work.
- #515 is open and contains consumer-repo browser/sync/support-skill evidence whose fresh-eye proof is not yet closeout-grade.
- #514 is open and asks for deterministic closeout evidence assembly without weakening gates or building a monolithic orchestrator.
- #518 is open and requires a full Charness repair of adapter/preset/surface reconciliation and false-green final verdicts; its pinned consumer reproduction and sibling comparison are recorded in the [debug artifact](../charness-artifacts/debug/2026-08-07-issue-518-quality-declaration-reconciliation-debug.md).
- The current awiki run is non-clean evidence for #518: `awiki 0.5.0` was detected at `/home/hwidong/.cargo/bin/awiki`, and `awiki lint -root docs -recursive` returned exit 1 with 40 documents, 7 orphans, 0 islands, and 230 link-only lines. It must become an explicit quality integration dependency and final-artifact disposition; it is not a clean result.
- Existing Charness `check-doc-links`, `markdownlint`, `check-links-internal`, and `nose` document-duplicate review have distinct observed semantics from awiki's graph check. No deletion is authorized until a command-level overlap matrix proves a full replacement.
- The goal draft now binds all three issues in one lifecycle while preserving consumer ownership, independent carriers, and separate readbacks.
- Quality Core run `31118030353` for head `0e469e917c6fa1b07f0351da639ac4431f519acc` failed at GitHub action metadata with `Service Unavailable`; mutation was cancelled. Treat it as an external CI non-claim.
- The publish-state claim below remains a captured, offline-reconciled snapshot for `published_sha` `e7c3e1b3…`; it is not a current version or tag claim. The release record separately binds `v3.4.0` to tag SHA `7bf3893b`, and the post-publish bookkeeping is committed at `c34b3dc0`. This block is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json), not prose: rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group, which is exactly what `0659d5a0` did. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. Activate the successor goal above. Its slice 1 (`#552`) is the sharpest
   instance in the tracker: a gate that can never fire is a permanent green.
2. **Open every slice with a premise check.** The record is 5 for 5 that the
   named remedy is wrong — including where the premise held. Slice 2's check
   refuted the plan's own wording and rerouted the work to a different skill.
3. **`#534` is NOT claimed and should not be re-shaped from its issue title.** A
   prior goal built it green, refuted it, reverted it in full, and posted the
   refutation to the issue, concluding it may not be worth building at all.
4. Two operator decisions are open and block nothing: whether the GATE discharges
   `#530` (the resolver still emits the string in its title), and whether `#535`
   is worth claiming at all. Both are in the successor's Operator Decision Queue.
5. Recount before shaping anything: `gh issue list --repo corca-ai/charness
   --state open` (29 at last count). `achieve` now REFUSES a draft goal that does
   not record what it claims and does not.

## Discuss

- No standalone CI retry, Cautilus run, browser/provider roundtrip, release, push, or consumer product claim is implied by the failed setup run or this goal activation. A remote carrier, if required at issue closeout, is a separate gated publish boundary after local proof.
- Do not create a generic evidence framework before Slice 0 proves a common representation, owner, and final reader.

## References

- [Unified goal](../charness-artifacts/goals/2026-08-07-repair-evidence-boundary-close-514-515.md)
- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Session retro](../charness-artifacts/retro/2026-08-07-session-retro.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read this before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts. It is a machine-read obligation of this file, not a courtesy link.
- [#516 debug record](../charness-artifacts/debug/2026-08-07-issue-516-mutation-regression-debug.md)
- [#514](https://github.com/corca-ai/charness/issues/514)
- [#515](https://github.com/corca-ai/charness/issues/515)
- [#518](https://github.com/corca-ai/charness/issues/518)
