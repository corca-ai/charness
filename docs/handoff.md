# Charness Handoff

## Workflow Trigger

- **`v4.1.0` is published and read back; the release goal is done.** Tag `cd7ab479`,
  release confirmed through the authenticated API and the public tag page,
  installed `charness version` reports `4.1.0`, doctor clean. Do not re-run any
  release phase; start from the backlog. Nine issues closed, 25 open.
- **`#572` is the one open red.** The last two scheduled `Mutation Tests` runs on
  `main` failed on an older SHA and none has landed on the release tree.

## Continuation Capability

- **The pattern this repo keeps shipping:** a proof surface renders a verdict over a scope or population it never established.
- **The pattern OF that pattern, and the most transferable thing measured this session:** the measurement that would have refuted the surface was only ever taken where the answer was already favorable. The adapter warn tier refused to arm one state at a 13% false-positive rate, then shipped another at ~100% in consumer repos — same code, unmeasured population. Four more instances of the same shape: a probe's cost read from the gate's own timeout record; a verdict drawn from a grep population that was not the reader set; tests that passed *through* the defect they should have caught; and three slice premises believed from durable records the goal itself wrote.
- **The counter-move is the north star's P4 extended from observers to POPULATIONS:** take the refuting measurement in a different tree, not only through a different reader. That is what cracked this session — running shipped code against five real consuming repos (`../stdy.blog`, `../cmanki`, `../ceal`, `../ceal-cli`, `../journal.stdy.blog`), which no in-repo channel could surface.
- **Measure the premise before shaping the slice.** Three consecutive slices had theirs refuted by one command each. Cheapest habit available.
- **The closeout floor works — let it refuse.** Every issue closed across this
  session was first returned NOT-CLOSABLE by a delegated reviewer, and the
  refusals were load-bearing three times: a repair had made a defect HONEST rather
  than FIXED; a repair shipped a NEW false completeness claim in the census that
  advertised its own coverage; and a reachability gate was armed everywhere except
  the one push class that creates the defect it catches.
- **A gate can catch what two review rounds miss.** Both bounded rounds read the
  adapter-version repairs and neither flagged the two unreachable branches the
  changed-line coverage gate refused. Reviewers and gates fail differently; do not
  read a clean review as a reason to expect a clean gate.

## Current State

- [refuse-the-verdict-a-surface-never-earned](../charness-artifacts/goals/2026-08-09-refuse-the-verdict-a-surface-never-earned.md)
  reached its closeout: `v4.1.0` published at `cd7ab479`, carriers at `916119c5`,
  `fd35f382`, `44268c8e`.
- **Nine issues closed against this release, each behind a delegated fresh-eye
  refusal round:** `#574`, `#575` with the release, then `#573`, `#563`, `#570`,
  `#549`, `#545`, `#523`, `#566`. Each close carries a behavioral verdict from a
  channel distinct from CLOSED state and its carrier, plus the residual its
  reviewer refused to let the close smooth over. Both post-release closeout
  critiques are in [charness-artifacts/critique](../charness-artifacts/critique).
- **The first `v4.1.0` publish attempt FAILED at the pre-publish lock and published
  nothing**, and its rollback left no tag, no release, and a restored artifact —
  that recovery path is now proven rather than assumed.
- `#576` remains an explicit no-verdict design gap and is not claimed fixed. A broad
  consumer census was considered and REFUTED as unjustified; do not re-open one
  without new evidence, and read the discriminator in the
  [no-observed-effect census](../charness-artifacts/audit/2026-08-09-no-observed-effect-census.md) first.
- The publish-state claim below is a captured, offline-reconciled snapshot, not a current version or tag claim. It is a machine-read source locator declared by [the publish-state ledger](../charness-artifacts/goals/2026-08-06-post-push-publish-state-ledger.json): rewriting this handoff without carrying it forward refuses `publish_state_ledger.py` and reddens its whole test group. Recount with `python3 -m pytest -q tests/quality_gates/test_publish_state_ledger.py tests/quality_gates/test_retro_memory.py`.

<!-- charness-publish-state-claim:post-push-operational-proof -->
```json
{"kind":"charness.publish-state-claim","schema_version":1,"block_id":"post-push-operational-proof","manifest_path":"charness-artifacts/goals/2026-08-06-post-push-baseline.slice-manifest.json","manifest_sha256":"a31aab7aecfb00c9ef84b9c26c93dbe15d630e83416a6d5cf38c04b6367fea34","published_sha":"e7c3e1b3fd7ab64bd07e19a2adc8bf7cedf2bde5","claim_state":"reconciled_captured_snapshot","issue_scope":"repository_open_issues_empty","pending_publish":false,"captured_at":"2026-08-06T02:14:03Z"}
```

## Next Session

1. Read the hosted `Mutation Tests` result on the release tree and settle `#572`.
   The last two scheduled runs failed on `18a9a439`; nothing has proven the
   current tree either way. `Quality Core` on `44268c8e` was unread at session end.
2. Work the four deferred follow-ups, which live as `valid-but-defer` Structured
   Findings in the two post-release closeout critiques and name their own
   file:line: the pre-push validators outside the durable-log aggregator plus this
   repo's missing `lefthook.yml`; the closeout-comment write path's absent
   private-media check; the unratcheted root-surface size; and the invented
   docs-graph orphan fixture. Decide whether to file them or keep them here.
3. `#545` is closed for the create path and the Slack host family ONLY. A private
   Notion, Drive, Figma, or `*.slack-edge.com` URL is still unguarded. Do not read
   the `v4.1.0` note's "provider-private media" as the shipped scope.

## Discuss

- **`#576` has no chosen direction.** Leave the gap documented, resolve readers against the installed plugin root, or give consumers a declared key space. The second was already rejected once as a new capability rather than a refusal-to-claim.
- `#561`'s equality-versus-invariant pin and `#547`'s re-scope remain operator-only and block nothing.
- Korean-titled artifacts are NOT renamed; charness must not couple a surface's correctness to a document's language.

## References

- [Current quality posture](../charness-artifacts/quality/latest.md)
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md) — read before changing operating contracts, prompt or skill surfaces, exports, or artifacts.
- [Design north star](./design-north-star.md)
- [Open-issue opinion](../charness-artifacts/audit/2026-08-08-open-issue-opinion.md)
