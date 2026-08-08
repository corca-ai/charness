# Charness Handoff

## Workflow Trigger

- **Next pickup: a small cleanup batch, NOT a goal.** Three items in `## Next Session`, none goal-sized. Take them directly with `impl`, then choose the next real goal from the consumer-facing backlog.
- **A 7-day value audit ran and mostly REFUTED its own thesis — do not re-run it.** It asked whether the repo had been improving itself rather than its users. Four structural charges broke on contact with the code: critique growth was dominated by machine-generated packet pairs while the `critique` SKILL barely moved; `skills/public` growth was `achieve`/`issue`, which consumer repos use most; the length floors are `MIN_OPTOUT_REASON` on escape hatches only, never on real values; and every new `scripts/` file ships to consumers with a large minority referenced by `skills/public`. Re-measure any of it with `git diff --numstat <base>..HEAD -- <path>` rather than trusting a transcribed figure.
- **What survived: one duplication and one prioritization finding.** Each critique run checks in a `-packet.json` AND a `-packet.md` that is a deterministic re-rendering of it; count the cost with `git diff --numstat <base>..HEAD -- charness-artifacts/critique/`. And the work shifted after `#516` from consumer defects to internal proof surfaces — that is a choice to make differently, not a mess to clean.
- **ASK FOR THE PUSH BEFORE ANYTHING ELSE.** 68 local commits are unpushed (`git log --oneline origin/main..HEAD`), six carrying issue closeouts. `git push` is NOT a standing approval and must be requested every time. Remote CI is an explicit non-claim for every commit in this range.
- Recount the backlog before shaping scope: `gh issue list --repo corca-ai/charness --state open` (28 at last count).

## Continuation Capability

- **Do not hand a fan-out your own conclusion as its premise.** The audit put "the owner suspects the repo has been improving itself" into every agent's prompt, and 11 agents upheld it; the operator's three follow-up questions refuted it. The adversarial pass challenged individual issue labels and never the framing. Anchor a workflow on the QUESTION, not the answer.
- **A number from a subagent is a claim, not a read.** The audit repeated "1 of 41 new scripts is consumer-referenced" without checking; it is 10 of 41, and all 41 ship. Verify any figure before it enters a conclusion.
- At irreversible boundaries, a green gate, `CLOSED` state, or local artifact is provisional; require a different observer and evidence channel.
- Any reviewed input change invalidates packet identity and the verification lock.
- Refresh kept: the push non-claim, the audit's two surviving items, the operator decisions, and the publish-state claim block below.
- Refresh non-claims: the `#514`/`#515`/`#518` + awiki state and the predecessor lesson block, both spilled to their owners ([recent lessons](../charness-artifacts/retro/recent-lessons.md), the issues themselves); no consumer product behavior; no remote CI verdict.

## Current State

- [close-the-copies](../charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md) is `Status: complete`: three slices of three. `#562` closed and verified through the adapter. `#561` is open BY DESIGN — a decision for D47's owner, with both costs measured in its Operator Decision Queue. `#560` is built and proven but its closeout floor was never run, so it is closable and not closed.
- [close-the-gap-between-a-repair-and-its-caller](../charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md) is a `draft` and is **no longer the default pickup**. Its `#565` half is real and was re-confirmed live during the audit; its sweep was cut as unbounded and its `#564` half is rulebook growth. Re-scope before activating, or leave it.
- `#564` and `#565` were filed by that run. `#547` needs a RE-SCOPE, not a close: its literal subject died with the locator digests, but `refreeze` now re-stamps the locator set and the artifact's prose while reporting no diff of what moved.
- The publish-state claim below is a captured, offline-reconciled snapshot for `published_sha` `e7c3e1b3…`, not a current version or tag claim. It is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json), not prose: rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **Packet double-storage, premise check FIRST.** Every critique run checks in a `-packet.json` and a `-packet.md`, where the `.md` is `critique_packet_lib.render_markdown(packet)` of the JSON beside it. Before deleting anything, establish whether any reader needs the `.md` that cannot read the `.json` — `critique_inventory` verifies `packet_md == render_markdown(packet_data)` and the durable critique binding declares `packet markdown sha256`. If a human reader owns the `.md`, the JSON is the redundant one. **This touches irreversible-boundary evidence; if the premise fails, drop the item.**
2. **Fix the `Routing:` matcher's false refusal.** A `Routing:` line wrapped in backticks is invisible to `goal_artifact_phase_routing.py`, so a correctly-filled cue is refused. The repo already strips inline markup elsewhere (`_strip_markup`, `_LEADING_MARKUP_RE`); apply it. One line, and it cost four closeout round-trips.
3. **Surface the opt-out AGGREGATE.** `MIN_OPTOUT_REASON` guards each `n/a — <reason>` individually and nothing counts them, so a goal opting out of 4 of 6 coordination floors reads the same as one opting out of none. Render the count and hand it to the disposition review. Consider promoting the coordination opt-outs to an enum, as `skipped:` already has.
4. **Then pick the next goal, in the operator's stated sequence.** After the packet cleanup, use [the open-issue opinion file](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md) as the basis — **but not blindly**; it says so itself and its top pick changed twice under evidence. Read `../craken-agents` alongside it as a good-repo reference for operating SHAPE. Verified before you start: craken-agents does NOT install charness (`grep -rl charness ../craken-agents` → 0 outside `node_modules`), so it is a sibling comparison, not consumer evidence. The two comparisons that moved the ranking: its `AGENTS.md` is 1,105 bytes to charness's 15,806 (`#523`, and `setup`'s own shipped guidance at `default-surfaces.md:122` forbids the handbook shape), and its `evals/{baselines,scenarios}` makes `#519`/`#520` cheaper than previously argued.

## Discuss

- Four operator decisions are open and block nothing: `#561`'s equality-versus-invariant pin (D47's owner), whether to run `#560`'s closeout floor, `#547`'s re-scope, and the renderer-versus-reference spelling split in `setup`.
- No CI retry, Cautilus run, release, push, or consumer product claim is implied by anything above.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Closing retro](../charness-artifacts/retro/2026-08-08-close-the-copies-this-run-measured-retro.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read this before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts. It is a machine-read obligation of this file, not a courtesy link.
- [Disposition review that refused the first closeout](../charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured-disposition-review.md)
