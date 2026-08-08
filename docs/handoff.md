# Charness Handoff

## Workflow Trigger

- **Next pickup: slice 2 of the active goal.** Run `/goal @charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md`. It is `Status: active`; slice 1 is DONE and its `## Slice Log` carries what it measured.
- **Push first if it is approved.** Four commits are unpushed and three of them are closeout carriers, so `#560`, `#565`, and `#567` all still read OPEN on GitHub. `issue_tool.py verify-closeout --expect-state CLOSED` confirms that today. One push converts all three; nothing else will.
- **Slice 2 is `#564`, re-scoped.** Its filed remedy (a rule in the goal template) stays DECLINED. Slice 1's runner already killed a call-site mutant in its own dogfood, so the capability exists — slice 2 is about making the tool ASK for a call-site mutant rather than leaving it to the author's memory.

## Continuation Capability

- **Verify a remedy's premise before shaping a slice around it — it fired three times in one shaping session.** The handoff's own named pickup was already DONE; `#567`'s problem 1 was already fixed; `#564`'s filed remedy had already been rejected by two durable records. All three were caught by reading the tree instead of the plan, and each would have been a slice built on nothing.
- **Ask a surface why it exists before repairing it.** `#563` was scoped as "widen the gate's scope", survived a reframe to "make it state what it measured", and ended as a DELETION — because one operator question exposed that it renders no verdict at all. The repair that a filed issue proposes is the issue author's guess, not a finding.
- **Attack your own census before believing it.** The NO-OBSERVED-EFFECT census's adversarial pass refuted 4 of 6 candidates, twice because the classifier read `main()`'s return statements and missed an uncaught exception that exits nonzero. A crude regex proxy earlier in the same session produced a list that included `pytest` as "cannot fail". A verdict about verdict surfaces gets no exemption.
- A slice changing verdict logic on a proof surface owes a second bounded-review round. Verify the reviewer boundary fingerprint BEFORE applying repairs, or the drift is unattributable.
- At irreversible boundaries a green gate or local artifact is provisional; require a different observer and evidence channel. Deletion is on that list.
- Refresh kept: the new goal pointer, the four operator decisions, the census numbers, the Tier 0 items, and the publish-state claim block below.
- Refresh non-claims: the finished release goal's internals, spilled to its own artifact and commits; no consumer product behavior; no remote CI verdict for anything after `ec67291e`; no slice of the new goal has run.

## Current State

- [refuse-the-verdict-a-surface-never-earned](../charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md) is `Status: active`, five slices, **slice 1 DONE**. It shipped [scripts/mutate_and_restore.py](../scripts/mutate_and_restore.py) plus its test module: a sweep runner that refuses a kill it cannot evidence. Two delegated review rounds, both DEFECTIVE, seven blockers — four in the first draft, three inside the repairs for those four.
- [close-the-gap-between-a-repair-and-its-caller](../charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md) is SUPERSEDED and must not be activated.
- Open and filed this session: `#570` (chunked-routing runs briefed on a surface they must not write) and `#571` (achieve recounts the tracker but never re-checks a durable record's proposed remedy — six measured instances across three sessions).
- Backlog: recount it. It was 33 open before `#570`/`#571` were filed.
- The publish-state claim below is a captured, offline-reconciled snapshot for `published_sha` `e7c3e1b3…`, not a current version or tag claim. It is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json): rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **Slice 2 (`#564`)**, then slice 3 (`#563`, a DELETION), 4 (`#521`/`#546`), 5 (`#523`). Order is in the goal's `## Slice Plan` and is tool-first by design.
2. **Use [the sweep runner](../scripts/mutate_and_restore.py) for every repair proof from here on.** It is the reason slice 1 went first. Hand-rolling a sweep now is a regression, not a shortcut — the retro measured five hand-rolls in one session before the tool existed.
3. **Two operator decisions are queued and block nothing:** which NO-OBSERVED-EFFECT census survivors to delete (`check-public-doc-coupling` is the clean one, 9 internal references), and `#561`/`#547`. They are in the goal's `## Operator Decision Queue`.
4. Recount before re-shaping: `gh issue list --repo corca-ai/charness --state open`.

## Discuss

- Open, and blocking nothing: `#561`'s equality-versus-invariant pin, `#547`'s re-scope, and the renderer-versus-reference spelling split in `setup`.
- **Decided this session, so do not reopen:** `check_title_slug_drift.py` is to be DELETED rather than repaired — DECIDED, NOT DONE; it is slice 3 of an unactivated goal and the script is still wired in today — the operator overruled `78a1790b`'s "demote, do not delete" after measurement showed it exits 0 everywhere, reports 0 findings on its default scope, and has two lifetime commits with no recorded catch. `#564`'s filed remedy (a line in the goal template) stays DECLINED as rulebook growth; the question becomes `#565`'s tool behavior instead. Korean-titled artifacts are NOT renamed — charness must not couple a surface's correctness to a document's language.
- **A census settled the "how many such checks are there" question: 2 of 90**, in [the census artifact](../charness-artifacts/audit/2026-08-09-no-observed-effect-census.md). The second survivor, `check-public-doc-coupling`, is a NEW deletion candidate with only 9 internal references. Read that file's `## Non-claims` before citing its headline: the 84 cleared checks were never independently verified, and its adversarial pass refuted 4 of 6 first-pass candidates — a single-pass census would have deleted four working surfaces.
- `check-changed-line-mutation-coverage` fails on six files inherited from earlier work; none belong to the new goal's slices.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read this before changing repo operating contracts, prompt or skill surfaces, exports, or artifacts. It is a machine-read obligation of this file, not a courtesy link.
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
- [Issue #566 corrected scope](https://github.com/corca-ai/charness/issues/566)
