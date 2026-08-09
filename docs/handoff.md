# Charness Handoff

## Workflow Trigger

- **Next pickup: slice 3b (`#530`).** Run `/goal @charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md`. It is `Status: active`; slices 1, 1b, 2 and 3 are DONE and the `## Slice Log` carries what each measured.
- **The push is UNBLOCKED but NOT TAKEN, and it needs an explicit grant.** The old blocker was refuted, not fixed around: `check-cli-skill-surface` was reporting its own 20s timeout as the probe's cost. The full gate now runs green (`bash scripts/run-quality.sh`, redirect to a file). Sixteen commits are unpushed and several are closeout carriers, so `#560`, `#565`, `#567` still read OPEN on GitHub — recount with `issue_tool.py verify-closeout --expect-state CLOSED`. One approved push converts them; nothing else will.
- **Two slices in a row had their premise refuted by one command.** Before shaping the next slice around a remedy any durable record proposes — including this file — run the command that re-establishes its premise. See `#571`.
- **`#561` and `#547` are DECIDED** and recorded in the goal's `## Operator Decision Queue`: retire the equality pin and convert D47 to a command; close `#547` as superseded by `#562`, whose retirement left no locator digests for a re-stamp to launder. Neither is scheduled yet.

## Continuation Capability

- **Verify a remedy's premise before shaping a slice around it — it fired three times in one shaping session.** The handoff's own named pickup was already DONE; `#567`'s problem 1 was already fixed; `#564`'s filed remedy had already been rejected by two durable records. All three were caught by reading the tree instead of the plan, and each would have been a slice built on nothing.
- **Ask a surface why it exists before repairing it.** `#563` was scoped as "widen the gate's scope", survived a reframe to "make it state what it measured", and ended as a DELETION — because one operator question exposed that it renders no verdict at all. The repair that a filed issue proposes is the issue author's guess, not a finding.
- **Attack your own census before believing it.** The NO-OBSERVED-EFFECT census's adversarial pass refuted 4 of 6 candidates, twice because the classifier read `main()`'s return statements and missed an uncaught exception that exits nonzero. A crude regex proxy earlier in the same session produced a list that included `pytest` as "cannot fail". A verdict about verdict surfaces gets no exemption.
- A slice changing verdict logic on a proof surface owes a second bounded-review round. Verify the reviewer boundary fingerprint BEFORE applying repairs, or the drift is unattributable.
- At irreversible boundaries a green gate or local artifact is provisional; require a different observer and evidence channel. Deletion is on that list.
- Refresh kept: the new goal pointer, the four operator decisions, the census numbers, the Tier 0 items, and the publish-state claim block below.
- Refresh non-claims: the finished release goal's internals, spilled to its own artifact and commits; no consumer product behavior; no remote CI verdict for anything after `ec67291e`; no slice of the new goal has run.

## Current State

- [refuse-the-verdict-a-surface-never-earned](../charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md) is `Status: active`, **slices 1, 1b, 2 and 3 DONE**. Slice 1 shipped [scripts/mutate_and_restore.py](../scripts/mutate_and_restore.py). Slice 2 repaired `check-cli-skill-surface`, which reported a starved probe as a failed one. Slice 3 put the regenerable-facts gate into `quality`'s shipped catalog — it was absent, so no consumer surface named it — and repaired three false claims in the docs describing it. Every slice so far ran two delegated review rounds and every round returned DEFECTIVE; in slices 2 and 3 the SECOND round caught the repair reintroducing the class it fixed.
- [close-the-gap-between-a-repair-and-its-caller](../charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md) is SUPERSEDED and must not be activated.
- Open and filed this session: `#570` (chunked-routing runs briefed on a surface they must not write) and `#571` (achieve recounts the tracker but never re-checks a durable record's proposed remedy — six measured instances across three sessions).
- Backlog: recount it. It was 33 open before `#570`/`#571` were filed.
- The publish-state claim below is a captured, offline-reconciled snapshot for `published_sha` `e7c3e1b3…`, not a current version or tag claim. It is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json): rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **Slice 3b (`#530`, one shared adapter-contract check)**, then 4 (`#564`), 5 (`#563`, a DELETION), 6 (`#521`/`#546`), 7 (`#523`). The goal's `## Slice Plan` is authoritative; slice numbering moved when slice 2 was re-shaped.
2. **MEASURE THE PREMISE BEFORE SHAPING THE SLICE.** Slices 2 and 3 both had their premise refuted by one command each, and both false premises came from durable records this goal itself wrote (`the probe costs ~21s`; `a consumer only ever sees NOT CONFIGURED`). Evidence is on `#571`. This is the single highest-yield habit for the next session.
3. **A killed mutation sweep leaves the tree MUTATED** (`#573`, filed this session, hit three times). After any interrupted sweep, re-check EVERY mutation site in the plan, not the few you happen to grep — one residue was a call-site deletion that survived `git status` and three greps because the file was already legitimately modified.
4. **Use [the sweep runner](../scripts/mutate_and_restore.py) for every repair proof from here on.** It is the reason slice 1 went first. Hand-rolling a sweep now is a regression, not a shortcut — the retro measured five hand-rolls in one session before the tool existed.
5. **Two operator decisions are queued and block nothing:** which NO-OBSERVED-EFFECT census survivors to delete (`check-public-doc-coupling` is the clean one, 9 internal references), and `#561`/`#547`. They are in the goal's `## Operator Decision Queue`.
6. Recount before re-shaping: `gh issue list --repo corca-ai/charness --state open`.

## Discuss

- **CONSOLIDATED to one active goal.** Five others were retired with a note naming why: three untouched since June, one a duplicate planning layer over the same backlog, and [repair-declaration-to-verdict-at-root](../charness-artifacts/goals/2026-08-07-repair-declaration-to-verdict-at-root.md) FOLDED as the same family — its live `#530` work is now slice 3b. Recount with a `Status:` grep over `charness-artifacts/goals/`.
- **`#547` is CLOSED**, as superseded rather than fixed: `#562` retired the locator digest pin, so the live inspection carries no `sha256` and there are no digests for a re-stamp to launder. A prior handoff's claim that its generalized form had been WIDENED was checked and is wrong — that error is why it was carried twice as an open decision.
- **The push blocker was REFUTED, not fixed-around.** The previous handoff said `check-cli-skill-surface`'s `doctor.py` probe "needs ~21s against a 20s timeout" and called it irreducible cost. Re-measured: **1.6s standalone, 5.5–6.0s inside the full gate**, and the whole suite is green in ~75s. The 21,650ms sample WAS the 20s deadline plus overhead — the check recorded its own timeout as the probe's cost, and a session read that number as a fact about the probe. Regenerate rather than quote: `bash scripts/run-quality.sh` (redirect to a file) and read the `check-cli-skill-surface` line. The gate now passes, so nothing blocks a push on this account; the push itself was still not taken, because `git push` is never a standing approval.

- Open, and blocking nothing: `#561`'s equality-versus-invariant pin, `#547`'s re-scope, and the renderer-versus-reference spelling split in `setup`.
- **Decided this session, so do not reopen:** `check_title_slug_drift.py` is to be DELETED rather than repaired — DECIDED, NOT DONE; it is slice 3 of an unactivated goal and the script is still wired in today — the operator overruled `78a1790b`'s "demote, do not delete" after measurement showed it exits 0 everywhere, renders no verdict at all, reports nothing on its default scope, and has a two-commit lifetime with no recorded catch. `#564`'s filed remedy (a line in the goal template) stays DECLINED as rulebook growth; the question becomes `#565`'s tool behavior instead. Korean-titled artifacts are NOT renamed — charness must not couple a surface's correctness to a document's language.
- **A census settled the "how many such checks are there" question: 2 of 90**, in [the census artifact](../charness-artifacts/audit/2026-08-09-no-observed-effect-census.md). The second survivor, `check-public-doc-coupling`, is a NEW deletion candidate with only 9 internal references. Read that file's `## Non-claims` before citing its headline: the 84 cleared checks were never independently verified, and its adversarial pass refuted 4 of 6 first-pass candidates — a single-pass census would have deleted four working surfaces.
- `check-changed-line-mutation-coverage` fails on six files inherited from earlier work; none belong to the new goal's slices.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read this before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts. It is a machine-read obligation of this file, not a courtesy link.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Issue #566 corrected scope](https://github.com/corca-ai/charness/issues/566)
