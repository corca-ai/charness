# Charness Handoff

## Workflow Trigger

- **Next pickup: activate the new goal.** Run `/goal @charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md`. It is `draft`, `pursue_ready: true`, five slices, shaped this session with the operator on four consequential decisions recorded in its `## Discuss Before Activation`.
- **The predecessor goal is DONE and its release is published.** `make-proof-surfaces-report-what-they-observed` is `Status: complete`; its major release shipped and was CI-verified (`ec67291e`, `b7aa6e6c`). Read the version with `git describe --tags --abbrev=0` rather than trusting a transcription. `origin/main..HEAD` is 0. Do not re-run its slice 8 — an earlier version of this file named that as the pickup after it had already happened.
- **Tier 0 pre-work, outside the goal, either order:** close `#560` (built and PROVEN; only its closeout floor was never run — the cheapest close in the tracker), and re-scope `#567` (its problem 1 was fixed by the predecessor's slice 1; `plan_handoff_run.py` has no keyword branching left. Its problem 2 is UNVERIFIED and contradicted by `plan_handoff_run.py:206-216`).
- **No push is approved.** The predecessor release's grant was scoped to that bundle and is spent.

## Continuation Capability

- **Verify a remedy's premise before shaping a slice around it — it fired three times in one shaping session.** The handoff's own named pickup was already DONE; `#567`'s problem 1 was already fixed; `#564`'s filed remedy had already been rejected by two durable records. All three were caught by reading the tree instead of the plan, and each would have been a slice built on nothing.
- **Ask a surface why it exists before repairing it.** `#563` was scoped as "widen the gate's scope", survived a reframe to "make it state what it measured", and ended as a DELETION — because one operator question exposed that it renders no verdict at all. The repair that a filed issue proposes is the issue author's guess, not a finding.
- **Attack your own census before believing it.** The NO-OBSERVED-EFFECT census's adversarial pass refuted 4 of 6 candidates, twice because the classifier read `main()`'s return statements and missed an uncaught exception that exits nonzero. A crude regex proxy earlier in the same session produced a list that included `pytest` as "cannot fail". A verdict about verdict surfaces gets no exemption.
- A slice changing verdict logic on a proof surface owes a second bounded-review round. Verify the reviewer boundary fingerprint BEFORE applying repairs, or the drift is unattributable.
- At irreversible boundaries a green gate or local artifact is provisional; require a different observer and evidence channel. Deletion is on that list.
- Refresh kept: the new goal pointer, the four operator decisions, the census numbers, the Tier 0 items, and the publish-state claim block below.
- Refresh non-claims: the finished release goal's internals, spilled to its own artifact and commits; no consumer product behavior; no remote CI verdict for anything after `ec67291e`; no slice of the new goal has run.

## Current State

- [refuse-the-verdict-a-surface-never-earned](../charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md) is `draft`, `pursue_ready: true`: five slices. Slices 1-4 close one class (a surface rendering a verdict over a scope or baseline it never established: `#565` the tool, `#564` re-scoped onto it, `#563` by deletion, `#521`/`#546` by census). Slice 5 is `#523`, the consumer-facing pick. The goal names that seam out loud rather than claiming a false unity.
- [close-the-gap-between-a-repair-and-its-caller](../charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md) is SUPERSEDED by the above and must not be activated; its narrowing is adopted intact.
- The predecessor goal is `complete` and its release is published and CI-verified. `origin/main..HEAD` was 0 at shaping time — recount with `git log --oneline origin/main..HEAD | wc -l`.
- `#566` step 1 is DONE (`c772f147`): [integrations/tools/awiki.json](../integrations/tools/awiki.json) validates and `charness tool doctor awiki` is `ok`. The lock is generated and gitignored. `#518`'s quality-dependency clause is still unmet and is called out on `#566` rather than left looking satisfied.
- Backlog: 33 open on 2026-08-09. The goal claims six; `## Backlog Recount` in the goal artifact records why each of the rest was left, including four that are operator decisions rather than work.
- The publish-state claim below is a captured, offline-reconciled snapshot for `published_sha` `e7c3e1b3…`, not a current version or tag claim. It is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json): rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **Activate the new goal and run its slices in order.** Slice 1 builds the mutate-and-restore helper (`#565`) because every later slice's proof depends on it; do not start at slice 3.
2. **Tier 0 first if you want a cheap win:** `#560`'s closeout floor, and `#567`'s re-scope. Both are outside the goal.
3. **Slice 3 is a DELETION, not a repair**, and its bar is completeness rather than a green suite. Recount the blast radius before starting: `grep -rn 'check_title_slug_drift\|check-title-slug-drift' skills/ scripts/ tests/ .githooks/ docs/ | grep -v __pycache__`. Three of those hits are public skill prose that ships to consumer repos telling an agent to run the script. Deleting the script alone reproduces the defect `2026-08-03-repair-the-commands-the-skills-tell-agents-to-run` fixed.
4. Recount the backlog before re-shaping anything: `gh issue list --repo corca-ai/charness --state open` (33 on 2026-08-09).

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
