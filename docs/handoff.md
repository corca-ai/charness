# Charness Handoff

## Workflow Trigger

- **Next pickup:** activate the [close-the-copies goal](../charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md). It is SHAPED and `--pursue-ready` passes, so go straight to `/goal @charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md` — no Before phase needed. Read its `## Active Operating Frame` first.
- **The repo has ONE live goal for the first time in three days.** [retire-the-second-live-goal](../charness-artifacts/goals/2026-08-08-retire-the-second-live-goal-then-close-four-filed-issues.md) is `Status: complete` — the FIRST goal in this family to finish its plan, five slices of five — and [one-rule-one-owner](../charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md) is `complete` too, closed EARLY at five of eleven rows.
- **Closed and verified this session: `#536`, `#558`, `#557`, `#559`, `#556`.** Each through the full floor — `validate-closeout-draft` reporting `draft_verified` BEFORE any GitHub mutation, a DELEGATED resolution critique before the close call, and `verify-closeout --expect-state CLOSED` read back through the adapter against its own carrier commit. Backlog: **28 open**, down from 33.
- **ASK FOR THE PUSH BEFORE ANYTHING ELSE.** 29 local commits are unpushed (`git log --oneline origin/main..HEAD`), five carrying issue closeouts. `git push` is NOT a standing approval and must be requested every time. Remote CI is an explicit non-claim for every commit in this range.
- **EIGHTEEN blockers across TEN delegated rounds, and NOT ONE was in a first diagnosis.** Every premise check was right about the defect; every blocker was in a REPAIR. This is the measurement that should change the next plan: budget two rounds per verdict-logic slice as a COST, not as a rule to remember.
- **A repair inherits HALVES.** The sharpest theme of the run. One inherited half a layout (source tree but not installed, so every installed capture would have died with an untyped error), one half an exception contract (a typed refusal swallowed by the caller's broad `except RuntimeError`), one half an owner (delegating to a consolidated function while passing its `required` set empty, one slice after building that floor). Ask of every repair what it did NOT inherit.
- **Opening the file is necessary and NOT sufficient.** The predecessor's rule was "open every location an instruction names". This run opened one, PRINTED the refuting evidence, and wrote the opposite two steps later. Quote the read back into the claim.
- **A test that re-implements its subject is another copy of the rule.** Shipped one inside the slice about copies of rules: it rebuilt a loader's candidate list and asserted on its own copy, so it would have passed with the loader deleted. Call the function. And pin the SOURCE — a mutant survived a pin that read the generated `plugins/` mirror, because the mirror lags until the next sync.
- **A premise check verifies the claim it is pointed at, and nothing else.** It correctly refuted two issues' stated blockers and was silent about the one that actually held: `release_backend` templates INCLUDE the binary while `issue_backend` templates exclude it, so a consolidation would have doubled it for every release adapter. Found by executing the replacement, not by analysing it. Smoke-test a consolidation before believing any analysis of it.
- **The bundle boundary earned its cost in one run.** Every slice was green at its own gate; the broad suite then returned `4 failed, 7964 passed`. Three were invisible from inside any single slice and one was a real regression whose blast radius crossed into a shared test double. After repair: `7968 passed, 0 failed` in 758s, with the verification lock recorded.
- **A test whose fixture is a LIVE artifact inherits that artifact's lifecycle.** Two `cadence_owner` tests broke because this goal flipped another goal to `complete` — which was its own acceptance criterion. Normalise the axis the test is not about.
- **The `#514/#515/#518` freeze was re-stamped again, with a recorded basis — continuing a practice the PREVIOUS session started, not starting it.** A closeout claim that this was the first such re-stamp was wrong and is corrected: `8d540d78` already recorded a basis on each of its three locators, and `#562`'s own body says so. **`#562`'s direction is already the operator's stated preference — option 1, drop the locator pin and keep the source snapshot.** The successor claims it with that direction, not as an open question.
- **One operator decision is queued and blocks nothing:** the renderer-versus-reference spelling split in `setup` — the renderer is gated against baking a model id into the AGENTS.md contract while `default-surfaces.md` instructs an agent to write exactly that.
- Recount the backlog with `gh issue list --repo corca-ai/charness --state open` before reshaping scope; the successor's `## Backlog Recount` describes how to reconcile it.

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
