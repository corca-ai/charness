# Charness Handoff

## Workflow Trigger

- **Next pickup: work the open backlog.** Run `/handoff` to chunk the live tracker, then `issue` per chunk. Recount first: `gh issue list --repo corca-ai/charness --state open --limit 200`.
- **FIRST, publish and verify the local CI repair if push approval is granted.**
  The structural repair is committed locally: the shared selector now resolves
  supported dynamic-loader literals, the owning test observes the entry and
  fallback branches in-process, the original failing range's consumer returns
  0 with `status: clean`, and the branch verification lock passes. Long quality
  runs now emit stderr `START`/`WAIT` progress before buffered phase output, so
  a combined redirected transcript no longer stays empty during broad pytest.
  The hosted result
  is still the old red head because `git push` is per-request and was not
  authorized. After an approved push, read it back with
  `gh run list --repo corca-ai/charness --limit 5`; do not infer remote green
  from the push exit code.
- **A MINOR release was approved and is HELD** until the repaired hosted CI run
  is green. Do not cut it from local proof alone.

## Continuation Capability

- **The pattern this repo keeps shipping:** a proof surface renders a verdict over a scope or population it never established.
- **The pattern OF that pattern, and the most transferable thing measured this session:** the measurement that would have refuted the surface was only ever taken where the answer was already favorable. The adapter warn tier refused to arm one state at a 13% false-positive rate, then shipped another at ~100% in consumer repos — same code, unmeasured population. Four more instances of the same shape: a probe's cost read from the gate's own timeout record; a verdict drawn from a grep population that was not the reader set; tests that passed *through* the defect they should have caught; and three slice premises believed from durable records the goal itself wrote.
- **The counter-move is the north star's P4 extended from observers to POPULATIONS:** take the refuting measurement in a different tree, not only through a different reader. That is what cracked this session — running shipped code against five real consuming repos (`../stdy.blog`, `../cmanki`, `../ceal`, `../ceal-cli`, `../journal.stdy.blog`), which no in-repo channel could surface.
- **Measure the premise before shaping the slice.** Three consecutive slices had theirs refuted by one command each; the fourth held. Cheapest habit available.
- **The closeout floor works — let it refuse.** Both issues closed this session were first returned NOT-CLOSABLE by a delegated critique, and one refusal was load-bearing: the repair had made a defect HONEST rather than FIXED, and closing on the first draft would have buried the residue.
- A killed or timed-out mutation sweep leaves the tree MUTATED. Re-check every site in the plan, not the ones you happen to grep.

## Current State

- [refuse-the-verdict-a-surface-never-earned](../charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md) is `Status: active`. Remaining: slice 5 (`#563`, a DELETION — decided, not done) and slice 7 (`#523`); read its `## Slice Plan` for status.
- `#530` and `#564` are CLOSED through the full floor (delegated critique, `validate-closeout-draft`, behavioural verdict on a distinct channel, `verify-closeout --expect-state CLOSED`). Critique artifacts are checked in under [charness-artifacts/critique/](../charness-artifacts/critique/).
- Filed this session and unworked: `#574` (version-unchecked adapter readers outside the resolver glob, one honoring trust-boundary fields), `#575` (the regenerable-facts gate's comment claims dated-record directories are out of scope while its default globs include them — fires in 4 of 5 real consumer repos), `#576` (charness renders no adapter-key verdict in any consumer repo — the gap the `#530` repair created by design).
- **A census was considered and REFUTED as unjustified.** The discriminator: consumers' own gate commands invoke zero charness scripts, and the canonical list of what a consumer is told to run is the four entries in [catalog.yaml](../skills/public/quality/references/catalog.yaml) — three of them charness scripts, all clean against the five repos. Do not re-open a broad census without new evidence.
- The publish-state claim below is a captured, offline-reconciled snapshot, not a current version or tag claim. It is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json): rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. **With explicit push approval, publish the committed repair and verify the
   hosted `Quality Core` result through GitHub.** Local old-range and branch-lock
   proof are green; remote green is the only remaining CI claim.
2. Then cut the approved MINOR release, and confirm it through a channel other than the publish exit code.
3. Then chunk the backlog and work it. `#575` is the strongest candidate: consumer-facing, evidence from five real repos, and it repairs a surface this repo shipped to its own catalog.
4. `#572` is a CI-generated mutation regression on an older head; check whether a green run supersedes it before treating it as work.
5. Do not start slice 5's deletion until the repaired hosted run is green — its
   bar is completeness across every referencing surface, including public skill
   prose a consumer reads.

## Discuss

- **`#576` has no chosen direction.** Leave the gap documented, resolve readers against the installed plugin root, or give consumers a declared key space. The second was already rejected once as a new capability rather than a refusal-to-claim.
- `#561`'s equality-versus-invariant pin and `#547`'s re-scope remain operator-only and block nothing.
- Korean-titled artifacts are NOT renamed; charness must not couple a surface's correctness to a document's language.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
