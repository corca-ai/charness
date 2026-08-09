# Charness Handoff

## Workflow Trigger

- **Continue the active release goal, not a new backlog chunk.** The selected
  P0-P2 implementation is committed through `f62e283f`; the operator explicitly
  authorized the final push and `v4.1.0` publication, with no Cautilus evaluation.
- **Finish the release-critique repair first.** The active heuristic and every
  gate reference to `check_title_slug_drift.py` stay retired, but `v4.1.0` must
  preserve the four `v4.0.0` invocation paths as deprecated direct-call
  compatibility with corrected default goal-record scope. Re-run the release
  safety review after this repair.
- **Then lock, push, and observe in phases.** Commit release preparation, run the
  verification lock, push the final branch, and read hosted `Quality Core`
  through GitHub. Create/tag the public release only after that distinct hosted
  result is green; verify public visibility, installed version/doctor, baton,
  and linked issue states through separate readbacks.

## Continuation Capability

- **The pattern this repo keeps shipping:** a proof surface renders a verdict over a scope or population it never established.
- **The pattern OF that pattern, and the most transferable thing measured this session:** the measurement that would have refuted the surface was only ever taken where the answer was already favorable. The adapter warn tier refused to arm one state at a 13% false-positive rate, then shipped another at ~100% in consumer repos — same code, unmeasured population. Four more instances of the same shape: a probe's cost read from the gate's own timeout record; a verdict drawn from a grep population that was not the reader set; tests that passed *through* the defect they should have caught; and three slice premises believed from durable records the goal itself wrote.
- **The counter-move is the north star's P4 extended from observers to POPULATIONS:** take the refuting measurement in a different tree, not only through a different reader. That is what cracked this session — running shipped code against five real consuming repos (`../stdy.blog`, `../cmanki`, `../ceal`, `../ceal-cli`, `../journal.stdy.blog`), which no in-repo channel could surface.
- **Measure the premise before shaping the slice.** Three consecutive slices had theirs refuted by one command each; the fourth held. Cheapest habit available.
- **The closeout floor works — let it refuse.** Both issues closed this session were first returned NOT-CLOSABLE by a delegated critique, and one refusal was load-bearing: the repair had made a defect HONEST rather than FIXED, and closing on the first draft would have buried the residue.
- A killed or timed-out mutation sweep leaves the tree MUTATED. Re-check every site in the plan, not the ones you happen to grep.

## Current State

- [refuse-the-verdict-a-surface-never-earned](../charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md) is `Status: active`; all implementation slices are complete and slice 9 release/issue closeout remains.
- Committed local repairs include changed-line CI reconciliation, visible gate
  progress, test process/temp isolation, exact SLOC-output exclusion, mutation
  crash recovery, adapter/private-media trust boundaries, declaration lifecycle,
  root routing, regenerable-facts scope, handoff routing, hook-failure visibility,
  and docs graph proof.
- `#574`, `#575`, `#577`, `#578`, and `#579` are repaired locally, not unworked.
  `#576` remains an explicit no-verdict design gap and is not claimed fixed.
- The release critique blocked `v4.1.0` on the removed and then semantically
  neutered installed title-slug command, and on this handoff's stale push
  sequence. Deprecated direct-call compatibility is the semver repair; the
  operator's later final-bundle authorization owns
  the sequence written above. Hosted CI/public/install/issue readbacks remain
  pending and are not inferred from local proof.
- **A census was considered and REFUTED as unjustified.** The discriminator: consumers' own gate commands invoke zero charness scripts, and the canonical list of what a consumer is told to run is the four entries in [catalog.yaml](../skills/public/quality/references/catalog.yaml) — three of them charness scripts, all clean against the five repos. Do not re-open a broad census without new evidence.
- The publish-state claim below is a captured, offline-reconciled snapshot, not a current version or tag claim. It is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json): rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. Finish and independently re-read the title-slug compatibility repair; commit it with the release critique disposition.
2. Draft `v4.1.0` notes, run the distinct release-record claims review, bump/sync, and run the final verification lock.
3. Push the final branch, wait for hosted `Quality Core`, then tag/create `v4.1.0` and verify public/install/doctor/baton surfaces.
4. Close only repaired issues whose delegated critique, validated ledger, distinct behavior evidence, and backend state readback all satisfy the issue floor. Treat #572 as superseded only if the new hosted changed-line run proves it.

## Discuss

- **`#576` has no chosen direction.** Leave the gap documented, resolve readers against the installed plugin root, or give consumers a declared key space. The second was already rejected once as a new capability rather than a refusal-to-claim.
- `#561`'s equality-versus-invariant pin and `#547`'s re-scope remain operator-only and block nothing.
- Korean-titled artifacts are NOT renamed; charness must not couple a surface's correctness to a document's language.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
