# Achieve Goal: Close every open issue: repair the declaration-to-verdict boundary, then the surfaces that grew on top of it

Status: draft
Created: 2026-08-07
Activation: `/goal @charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md`

Supersedes `charness-artifacts/goals/2026-08-07-repair-evidence-boundary-close-514-515.md`
(pre-0 complete, committed as `8bc8e0e4`). That goal's frozen source, capture
adapter, and closeout authorization surface carry forward unchanged as this goal's
Slice 4 substrate; nothing built there is rebuilt here.

## Active Operating Frame

- Current slice: Slice 0b COMPLETE and the repo is UNBLOCKED. The pre-push gate
  passes (86 passed, 0 failed) and `main` is pushed at `1849a9b2`. `#529` is
  CLOSED and verified through the adapter — the first close of this goal.
- **Root cause of the last blocker, recorded because it wasted the most time:**
  the gate was not wrong and the coverage was never missing. `reports/mutation/`
  holds ONE shared coverage data file, and I had a broad producer running in the
  background while the pre-push gate ran. The two clobbered each other, which is
  why the same command reported `clean`, then `[51]`, then `[48, 51, 55]`. With
  nothing else running it passed first try. Do not run a mutation-coverage
  producer concurrently with a push.
- **The plan had a hole and this is it.** Slice 0's boundary said "no other slice
  may claim a green suite before Slice 0 closes" and treated `pytest` as *the*
  baseline. It is not: the gate that decides whether work may leave this machine
  is the pre-push gate, and nobody had run it in 13 commits. `Closes #N` only
  fires on the default branch, so an unpushable repo is a repo where all 19
  issues stay open no matter how good the local work is. Slice 0b is therefore a
  prerequisite in exactly the sense Slice 0 was, and the same rule applies: do not
  weaken a check to reach the green.
- Current slice intent: close all 19 open issues by repairing the shared
  declaration-to-verdict boundary first, then the surfaces that accumulated on
  top of it — in an order where each slice's tools already exist.
- Next action: pick the next tractable issue. Two are closed (`#529`, `#533`), both
  with full floors and adapter readbacks. `#530` is scouted and PARKED: its causal
  review (posted on the issue) shows the named remedy's premise does not hold, so it
  needs a contract design pass, not a loader patch — do not shape a slice around it
  without reading that comment first.
- Verification cadence: cheap deterministic checks at commit boundaries; bounded
  fresh-eye review at each slice that changes verdict logic, with a mandatory
  second round when round 1 produces repairs; broad proof at bundle boundaries.
- Gate cadence: sync source/plugin exports before validators; `run_slice_closeout.py
  --skip-broad-pytest` per slice; `--verification-lock` at the bundle boundary.
- Slice review packet: intent, changed files and owning/generated surfaces,
  expected invariants, tests/proof, non-claims, out-of-scope lines, questions.
- History boundary: keep this frame to the next action and current risk; completed
  evidence goes to `## Slice Log`.

## Goal

Close all 19 open `corca-ai/charness` issues and adopt the 34 pre-existing test
failures that no goal currently owns, in one goal, sequenced so that each slice's
prerequisites are already built when it starts.

The issues are not 19 unrelated defects. Six of them are one shape — **a
declaration that no executable reader ever reconciles** — and that shape is also
what produced the unowned test failures: a handoff rewrite at `0659d5a0` silently
dropped a machine-read publish-state claim block, and 26 tests plus the
`publish_state_ledger` CLI have been red for six commits with nothing connecting
the breakage to its cause. Seven more issues are the second-order consequence:
because declarations are cheap and unverified, the prompt and doc surfaces grew
monotonically and nobody can measure whether the growth helps.

So the goal is ordered around one claim: **repair the ability to refuse an
unreconciled declaration before repairing anything that declares.** Concretely,
`#530` (16 of 17 resolvers accept an arbitrary `version` and absorb typo'd keys as
defaults) is the root of `#528`, `#518`, and `#526`; fixing those first would build
them on a resolver that cannot tell a typo from a choice.

The second ordering claim: **build the instrument before the measurement, and the
measurement before the decision.** `#532` (the run-plan envelope requires
`cost_tier` on gates but has no size field on reads, while `debug` silently demands
49,965 B) is the instrument for read cost. `#519`/`#520` are the instruments for
skill trigger accuracy and no-skill efficacy. `#521` — an operator decision request
about whether prompt surfaces may ever shrink — is answered from those instruments'
output rather than from the unmeasured premise it currently rests on. Only then do
`#523`/`#527`/`#531` reshape the surfaces themselves.

Every issue keeps its own carrier, delegated resolution critique, distinct
`Behavior #N:` verdict, `validate-closeout-draft`, and `verify-closeout
--expect-state CLOSED`. One slice's green never closes another slice's issue.

## Non-Goals

- Do not merge issues into umbrella closes. Nineteen issues means nineteen
  carriers and nineteen readbacks.
- Do not weaken, disarm, or narrow a gate to reach a green. The measured basis
  for this rule is in `AGENTS.md`: the pre-push changed-line mutation lane refused
  five times across three goals and was correct every time.
- Do not treat `#521` as settled by this goal's convenience. It is a real operator
  decision; this goal produces the measurement it needs, and the decision is
  recorded in the Operator Decision Queue with its evidence.
- Do not claim any consumer repo's product behavior. `cmanki`, `craken-agents`,
  `ceal`, `ceal-agent`, `anthropics/skills`, and `mattpocock/skills` are read-only
  comparison evidence throughout.
- Do not build a generic orchestration framework, and do not let the shared-seam
  work of Slice 4 grow past what two proven readers justify.
- No release, tag, version bump, PR creation, or Cautilus run is in scope. Pushes
  are per the standing conditional approval only, and only after the pre-push gate
  passes.
- Do not re-open or re-solve `#516` or `#517`; they are typed regression fixtures.

## Boundaries

- **The baseline is a prerequisite, not a slice preference.** Until Slice 0 lands,
  every `pytest` verdict in this repo is read against 34 standing failures, and a
  new regression is indistinguishable from the noise. No other slice may claim a
  green suite before Slice 0 closes.
- **Root-before-consumer for the declaration family.** `#530` precedes `#528`,
  `#518`, and `#526`. A slice that repairs a declaration on top of a resolver that
  silently absorbs unrecognized input has not repaired it.
- **Instrument-before-measurement-before-decision.** `#532` precedes `#523`/`#527`;
  `#519`/`#520` precede `#521`; `#521` precedes any physical shrink of a prompt
  surface. If the operator later closes `#521` as "no deletion", the surface slices
  are constrained to split-and-move and must say so in their carriers.
- **Pay the refactor tax before the refactors.** `#534` (a module split rotates
  content-addressed dup-ratchet family ids, re-blocking already-classified
  families) precedes `#523` and `#527`, which are the two most split-heavy slices in
  the goal. Measured basis: three length-cap-forced splits in `8bc8e0e4` rotated
  four classified families and hard-blocked the gate with no new duplication.
- **`#529` precedes the closeout-heavy slices.** `SKILL.md` tells the agent to
  report from `{repo, number, url}` while the helper emits
  `created_number`/`created_url`. This goal performs 19 issue closeouts; a broken
  report contract costs 19 times if it is fixed late.
- External-side-effect scope: filing issues and pushing to `main` on a passing
  pre-push gate are standing approvals. Issue *close* is standing but conditional
  on the full closeout floor. Reopen, PR, release, tag, bump, and Cautilus each
  need an explicit per-phase grant that does not carry forward.
- Slices that change verdict logic on a proof surface owe round-1 and, if round 1
  produces repairs, round-2 bounded review reading the repaired surface. Cap is two
  rounds; round-2 repairs are recorded as accepted-unreviewed.
- Bounded reviewers run read-only in the shared parent worktree and never mutate
  the index; parents fingerprint worktree+index integrity around each review.

## User Acceptance

- All 19 issues read `CLOSED` through the adapter, each with its own carrier,
  delegated critique, distinct behavior verdict, and readback. The goal's Slice
  Log names all 19 with their closing commit.
- `pytest tests/ -q` reports zero failures, and the goal states which of the
  original 34 were fixed versus explicitly re-scoped with an owner.
- `python3 scripts/publish_state_ledger.py --repo-root . --json` exits 0.
- A repo can declare an adapter sub-key ABSENT and the resolver honors it; a typo'd
  key and an unsupported `version` are refused or warned, not silently defaulted,
  across all 17 resolvers.
- Every quality surface the adapter declares resolves to an executable reader or a
  typed gap/inapplicable/unsupported/deferred state. No declared-but-unreached
  surface renders as `clean`.
- The run-plan envelope carries a read-cost field, and `debug`'s 49,965 B
  required-read set is visible as a number before the agent opens it.
- `#521` is answered with measured A/B evidence attached, not with the current
  unmeasured premise, and the answer is recorded in the Operator Decision Queue.
- The operator can read the Slice Log and see, per slice, which issue it closed,
  which proof channel produced the verdict, and what it explicitly did not claim.

## Agent Verification Plan

### Low-Cost Checks

- At each slice boundary: `scripts/check_changed_surfaces.py`, the focused
  validators it names, `scripts/check_python_lengths.py --headroom` BEFORE adding
  to a gated file, `ruff`, and `run_slice_closeout.py --skip-broad-pytest`.
- Root/plugin export sync before every validator run; a stale mirror is a
  false failure that costs a full re-read.
- `skills/public/quality/scripts/check_dup_ratchet.py --summary` before writing the
  commit message, not after — it is a hard block at the closeout aggregate.
- Re-run the changed slice's own tests plus the surrounding gate file's tests; the
  pre-0 slice found four unrelated close/verify tests broken by an adapter-scope
  change that looked local.

### High-Confidence Checks

- Slice 0: `pytest tests/ -q` full run with a written before/after failure count,
  and a named cause per failure group. A group closed as "environment" or
  "flaky" without a cause is not closed.
- Slice 2 (`#530`): a fixture per resolver family proving a typo'd key and an
  out-of-range `version` are surfaced. 17 resolvers is the denominator; the report
  names which are covered and which are exempt with a reason.
- Slice 4 (`#518`): replay the pinned `cmanki@aac5feca` history, a TypeScript
  dead-code inapplicability fixture, canonical markdown plus skill-path
  reachability, preset-to-gate reconciliation, final-consumer folding, root/plugin
  parity, and the `craken-agents` comparison contract without copying its
  repo-specific gate list.
- Slice 4 (awiki): pin `v0.5.0`/`f65f8c43dbf0300609bdfdf823c09cba370222c6`, run
  `awiki lint -root docs -recursive` through the quality route, and preserve the
  non-clean disposition (40 documents, 7 orphans, 0 islands, 230 link-only lines,
  exit 1) rather than reporting healthy. No existing linter is deleted without a
  command-level overlap proof.
- Slices changing verdict logic: bounded round-1 review, and round-2 reading the
  repairs when round 1 produced any.
- Every slice that adds a refusal answers one question in its carrier: **what
  escape does this refusal prevent?** A refusal whose answer is "malformed input
  that changes no verdict" is defined away instead of added. Measured basis: two
  such refusals were added and withdrawn in the pre-0 slice.

### External Or Live Proof

- GitHub issue state is read back only after each issue's closeout floor, through
  the adapter, and never substitutes for behavior proof.
- Remote CI is a non-claim unless a separately scoped lane runs it; a push exit
  code is not a build verdict, and the confirming observer and channel must both
  differ from the push.
- Consumer-repo product behavior (`cmanki` browser/provider/sync, `ceal` Slack
  roundtrips) is a standing non-claim. `#524`/`#525` may cite ceal's artifacts as
  observed evidence of a consumer's need, never as proof of charness behavior.

## Slice Plan

| Slice | Objective | Issues | Why here | Status |
| --- | --- | --- | --- | --- |
| 0 | Restore the baseline nobody owns | (none; filed #536, #537) | Every later green is read against 34 standing reds. `docs/handoff.md` lost its publish-state claim block at `0659d5a0`; 26 tests + the ledger CLI have been red for 6 commits | **complete** — 35 measured (not 34), 0 remaining |
| 1 | Repair the issue lane's own report contract | #529 | This goal performs 19 closeouts; a wrong `{repo, number, url}` ledger costs 19 times if fixed late | **CLOSED** — carrier `10de65a9`, `verify-closeout --expect-state CLOSED` returned `verified` |
| 0b | Restore the PRE-PUSH gate's own unowned baseline | (none; filed #540, #541) | Discovered after Slice 1: the pre-push gate had been red across 13 unpushed commits, and auto-close only fires on the default branch — so no issue could close until it was green. Same shape as Slice 0, one gate over. | **complete** — gate green, 18 commits pushed at `1849a9b2` |
| 2 | Make adapters able to refuse unrecognized input | #530 | Root of the declaration family: 16/17 resolvers accept any `version` and absorb typo'd keys as defaults | planned |
| 3 | Let a repo declare a sub-key ABSENT | #528 | Needs Slice 2's absent/defaulted/declared distinction; deletions currently refill silently | planned |
| 4 | Reconcile every declared quality surface to a reader or a typed gap (+ awiki) | #518 | The flagship declaration-to-verdict repair; consumes Slices 2-3 | planned |
| 5 | Repair quality-surface routing and disclosure | #515 | Own contract; reuses #517's existing disclosure floor rather than re-solving it | planned |
| 6 | Reconcile the declared mirrors and waivers | #526, ~~#533~~ | Same family. **#533 CLOSED** (carrier `d2921f3c`, readback `verified`) — taken early because it was small and self-contained; #526 remains | #533 done, #526 planned |
| 7 | Deterministic evidence assembly and one-command re-bind | #514, #535 | #535 is the retro finding in #514's own neighborhood; both are "identity bound late and re-bound by hand" | planned |
| 8 | Stop taxing refactors | #534 | Must precede the two split-heavy slices (#523, #527) or they pay the same tax measured in `8bc8e0e4` | planned |
| 9 | Make claims and proof levels machine-readable | #525, #524 | `readme-proof.md` is prose no gate reads; the 5-name ladder was 21 classes to a real consumer | planned |
| 10 | Give reads a cost field | #532 | The instrument for read cost; must exist before any slice argues a surface is too big | planned |
| 11 | Instrument skill trigger accuracy and no-skill efficacy | #519, #520 | The instruments #521 needs; 1 of 20 skills has a baseline comparison today | planned |
| 12 | Decide the prompt-surface deletion policy on measured evidence | #521 | An operator decision answered from Slices 10-11's output, not from the current unmeasured premise | planned |
| 13 | Reshape the surfaces under the decided policy | #523, #527, #531 | Constrained by #521's answer, measured by #532/#519/#520, untaxed by #534 | planned |
| 14 | Bundle proof and goal closeout | (none) | Composition can drop what each slice proved in isolation | planned |

## Operator Decision Queue

- Decision: `#521` — whether `NO-OBSERVED-EFFECT` may authorize physical deletion
  of a prompt surface, or remains a demotion-proposal ceiling.
  Owner: operator.
  Why deferred: the current policy rests on the premise "deletion risk >>
  bloat risk", which has never been measured, and the repo already owns the tool
  that can measure it (`run_skill_efficiency_ab.py`).
  Unblock action: complete Slices 10-11, run the deletion A/B arms, attach
  token/waste/outcome-grade deltas, then decide in Slice 12.
  Revisit trigger: the A/B shows no measurable outcome difference in either
  direction, which would make the decision a values call rather than an evidence
  call and should return to the operator explicitly.
- Decision: whether Slice 13 may physically shrink `AGENTS.md` (16,918 chars) or
  only split-and-move it.
  Owner: operator, downstream of `#521`.
  Why deferred: identical premise; resolving `#521` resolves this.
  Unblock action: Slice 12's answer.
  Revisit trigger: `#523`'s reviewer finds a section whose removal is safe on
  routing grounds alone, independent of the deletion policy.
- Decision: whether the pre-existing failures include any that should be
  re-scoped to a different owner rather than fixed here.
  Owner: operator.
  **RESOLVED by Slice 0's measurement — no operator input needed.** Both suspected
  groups were indeed intended behavior, and neither required changing the thing
  being measured: the `closeout_bundle`/`final_bundle_preflight` block was a
  CORRECT `unmatched_surface_path` refusal over ten genuinely unowned artifacts
  (repaired by adding real owning surfaces, not by relaxing the gate), and the
  `inventory_marker` drift was this repo's own quality corpus growing (repaired by
  refreshing both probes with D47 in lockstep). Nothing is re-scoped to another
  owner; all 35 are fixed here. The recurring cost of the probe refresh is filed
  as `#536` rather than absorbed silently.

## Coordination Cues

- Routing: `achieve` owns the goal; `debug` for the bug-class issues before their
  fixes; `quality` for #515/#518/#526/#533 proof planning and the awiki
  integration; `spec` for the #524/#525 machine-readable contracts;
  `create-skill` for the #527 human-facing skill-doc boundary; `impl` for slices;
  `critique` at each risk boundary; `prove` for slice closeout; `issue` for all 19
  closeouts and any off-goal finding; `retro`/`handoff` for continuation.
- Gather: n/a — the comparison repos are local read-only checkouts already cited
  in the issue bodies; no new public source is required.
- Release: n/a — no version, tag, or publication is in scope.
- Issue closeout: planned independently for all 19 through the issue adapter after
  each carrier, delegated critique, distinct behavior verdict, and readback.

## Discuss Before Activation

- Discuss before activation: RESOLVED — the operator confirmed (1) this goal
  supersedes the #514/#515/#518 goal and absorbs its completed pre-0 work,
  (2) `#521` is decided inside this goal from measured A/B evidence rather than
  deferred outside it, and (3) all 19 issues are in scope with no timebox.
  Activation still does not authorize release, tag, PR, bump, Cautilus, or any
  consumer-repo product claim.

## Slice Log

The superseded goal's pre-0 slice is complete and committed as `8bc8e0e4`; its
artifacts and gates carry forward as Slice 4's substrate and are not rebuilt.

### Slice 0 — Restore the baseline nobody owns (complete)

**Issue closed:** none, by design. **Issues filed:** `#536`, `#537`.

**Measured before/after.** `pytest tests/ -q` at `1db69613`: 35 failed, 7491
passed. After: 7545 passed, 0 failed. The goal's plan said 34; the true count was
35, and the extra one (`test_retro_memory`) shares a root cause with the largest
group, which is why the plan's grouping missed it.

**Cause per group — no group closed as "environment" or "flaky".**

| Group | N | Cause | Disposition |
| --- | --- | --- | --- |
| `publish_state_ledger` | 26 | The handoff rewrite at `0659d5a0` dropped the `charness-publish-state-claim` marker block. The ledger declares `docs/handoff.md` as a source locator, and the tests copy the live file into a fixture. | Defect. Block restored byte-identical to the surviving copy in the goal artifact. |
| `test_retro_memory` | 1 | Same rewrite dropped the `recent-lessons.md` reference the retro-memory gate requires. | Defect, same root cause. Reference restored. |
| `final_bundle_preflight` + `closeout_bundle` | 5 | `status: blocked` on `unmatched_surface_path`: ten artifacts added by `8bc8e0e4` under `charness-artifacts/spec/` and `charness-artifacts/quality/fixtures/` had no owning surface. | **The gate was RIGHT.** Not a defect in the gate. Repaired by giving the ten paths real owning surfaces with executable verifiers, not by relaxing the blocker. |
| `inventory_marker_rule_measurement` + `a_declaration_is_not_its_own_corroboration` | 3 | Recorded-probe drift (130→131 artifacts). Caused by this repo's own quality writes. | Intended behavior. Both probes refreshed with D47 updated in lockstep. The toll went DOWN (5 citations across 4 artifacts → 4 across 3) because `quality/latest.md` now marks the fields it cites. |

**Operator Decision Queue entry resolved.** The queue asked whether the
`inventory_marker` and `closeout_bundle` groups were intended behavior rather
than defects. Measured answer: **both are intended behavior**, and neither needed
a fix to the thing being measured. No re-scoping to another owner is required, so
that decision does not need to go back to the operator.

**Prevention, and what escape it prevents.** `docs/handoff.md` matched only
`repo-markdown`, whose verifiers are link, markdown-lint, and secret checks —
none of which read the claim block. So the rewrite that broke 27 tests passed
every gate that matched the file it broke. Added the `handoff-machine-readers`
surface binding `docs/handoff.md` to its two actual machine readers. The escape
is measured, not hypothetical: it already happened and cost six commits.

**Proof channel distinct from the fix.** The fix was driven by `pytest`; the
ledger repair was confirmed independently by `publish_state_ledger.py --json`
exiting 0 and printing `"status": "reconciled"` — a CLI reader, not a test.

**Bounded review: two rounds, both delegated, both boundary-verified clean.**
Round 1 found 6 blockers, including one confirmed by execution
(`validate_handoff_artifact.py` refused prose I had added — it would have failed
the commit gate). Round 2 read the repairs and found 3 more blockers *in the
repairs*, including the mirror hole in the new checker (a stream path with no
digest) and a path-traversal escape the repo already had an idiom for. This is
the second-round rule paying for itself exactly as the contract predicts.

**New verdict logic added:** `scripts/check_quality_tool_fixtures.py` plus 19
tests. It replaced an inline one-liner with three holes, under which the repo's
one checked-in fixture carried a 62-character `stderr_sha256` — the empty-stream
digest with two characters lost in transcription — unread since capture. Repaired
after re-running the pinned `awiki lint -root docs -recursive` and observing 0
bytes on stderr. Mutation-checked: narrowing `STREAMS` back to `("stdout",)` lets
a corrupt stderr digest pass the checker and is killed by the parametrized tests.

**Non-claims.** No remote CI claim. No claim that the awiki fixture has an
executable final consumer — that is `#518`'s work and the surface notes say so.
No claim the marker rule should be armed; D47 stays deferred. Round-2 repairs are
recorded as accepted-unreviewed per the two-round cap.

### Slice 1 — Repair the issue lane's own report contract (`#529`)

**Root cause, from the delegated causal review — not a typo.** `issue_read.py`
emits `number`; `issue_create.py` emitted `created_number`. One skill, two
spellings of one concept, and the docs were written in the *read* helper's
vocabulary. So an agent following `SKILL.md` literally read nulls from a create
that had SUCCEEDED, and a retry would have filed a duplicate issue.

**The review found more than the issue reported.**

- A **third** doc site the issue does not name: `references/resolve-flow.md:50`.
  A fix touching only the two reported sites would have left the resolve path
  broken.
- `state`, asked for by `closeout-discipline.md:13`, is **unobtainable by any
  rename** — no create path emits it, ever. It is a `view` field, and the doc
  framed the readback as a conditional fallback when it was the only route.
- **Nothing in the repo gates a skill's documented payload keys against what its
  helper emits**, and the test suite is structurally incapable of it:
  `test_issue_create.py` asserts the helper's real keys, `test_issue_closeout_discipline.py`
  asserts the docs' real strings, both pass, and no test read both.

**Fix direction chosen: make the helper emit the contract's names.** The review
established this has *zero* programmatic downstream consumers — four assertions,
all in one test file, and nothing outside this repo's tests reads
`created_number`/`created_url`. The alternative (renaming the docs) would have
entrenched the intra-skill naming split that caused the bug. `created_*` are kept
as deprecated aliases because charness installs into consumer repos.

`state` was removed from the create-side ask and re-homed to the read/verify
shape, with the reason stated: a just-created issue is `OPEN` by construction, so
reporting state from create is noise dressed as verification.

**The missing gate, added.** A test that parses the ledger key names out of the
doc TEXT and asserts every one is a key the helper actually emits. Proven against
the pre-fix tree at `8b33af7e`: it reports `['number', 'state', 'url']` missing
and fails. It passes at HEAD. It reads the names rather than restating them, so a
rename on either side reds instead of drifting apart again.

**Public-skill validation decision (recorded for `--ack-cautilus-skill-review`).**
No change to `evals/cautilus/scenarios.json` and no change to the consumer
contract in `docs/public-skill-dogfood.json`. Reason: the consumer-facing contract
`{repo, number, url}` is UNCHANGED — this slice made the helper conform to the
contract that was already documented and already asserted by the existing dogfood
acceptance evidence ("renders `issue new` closeout from the verified issue ledger
plus the created title and a short filed-body summary"). That criterion was
previously unsatisfiable; it is now satisfiable. A contract that gained no new
semantics needs no new scenario. No Cautilus run: eval-only, ask-before-run, and
this goal's Non-Goals exclude it.

**Sibling filed, not fixed here.** The review's sweep found the same class in a
different skill: `quality/SKILL.md:69-79` names `scaffold_quality_artifact.py`
but instructs `--intent record`, `update_current_pointer_after_write`, and
`refresh_current_pointer_command`, all of which belong to the unnamed
`resolve_quality_artifact.py`. Out of `#529`'s job-to-be-done; filed separately.

**Non-claims.** The new gate covers the `issue` skill only. The general question
— whether doc-to-helper key agreement should be gated repo-wide, and whether that
gate is declaration-based or inference-based — is named by the review as a design
question bigger than this issue and is NOT answered here. The review's sweep did
not reach `create-skill`, `critique`, `gather`, `ideation`, `impl`, `narrative`,
`prove`, `retro`, `setup`, or `spec` at depth.

## Context Sources

1. `docs/design-north-star.md` — the "teeth only where a wrong answer escapes"
   standard this goal's refusal-design rule derives from.
2. `charness-artifacts/goals/2026-08-07-repair-evidence-boundary-close-514-515.md`
   — superseded goal; its pre-0 Slice Log is this goal's Slice 4 substrate.
3. `charness-artifacts/retro/2026-08-07-pre0-issue-source-freeze-and-closeout-authorization.md`
   — the measured waste and the two withdrawn refusals that produced this goal's
   refusal-design rule and its length-cap workflow rule.
4. `charness-artifacts/retro/2026-08-07-session-retro.md` — the
   `release-proof-identity-churn` recurrence class, second instance of which is #535.
5. `charness-artifacts/retro/recent-lessons.md` — the freeze-before-broad-verification
   rule this goal's Slice 0 gate cadence encodes.
6. Live issue bodies for all 19 open issues, read 2026-08-07.
7. Measured failure grouping: `publish_state_ledger` ×26 (`sources.handoff`,
   `expected exactly one publish-state marker`), `closeout_bundle` ×2 and
   `final_bundle_preflight` ×3 (`status: blocked`),
   `inventory_marker_rule_measurement` ×2 (recorded-probe drift 131 vs 130,
   42 vs 43).
8. `git log -- docs/handoff.md` — markers=3 through `c5aeaaee`, markers=0 from
   `0659d5a0` onward.
9. Read-only comparison checkouts cited by the issues: `anthropics/skills@b29e7cf`,
   `mattpocock/skills`, `corca-ai/craken-agents@4c49c96d`, `corca-ai/ceal@e5b37ab24`,
   `corca-ai/ceal-agent@9d072df`, `cmanki@aac5feca`.

## Interview Decisions

- Scope: one goal for all 19 issues, chosen because six of them are one structural
  shape and seven more are its second-order consequence; splitting them would
  re-diagnose the same seam three times. Rejected: a defects-only goal deferring
  the observation/proposal issues, because the observation issues carry the
  instruments the defect fixes need to prove they helped.
- Supersession: the new goal absorbs the #514/#515/#518 goal rather than running
  beside it, so slice order can be optimized globally — specifically so `#530`
  can precede `#518`, which the older goal's fixed plan could not express.
  Rejected: parallel goals, which would split slice memory across two artifacts.
- `#521`: decided inside the goal from measured evidence. Rejected: deciding it
  now by fiat in either direction, because the premise under the current policy
  has never been measured and the repo already owns the measuring tool.
- Ordering: root-before-consumer, instrument-before-measurement-before-decision,
  and pay-the-refactor-tax-before-the-refactors. Rejected: issue-number order and
  severity order, both of which would put `#518` before the resolver repair it
  depends on.
- Closeout: 19 independent carriers and readbacks. Rejected: a bundled close,
  which recreates the semantic-proxy failure this goal exists to repair.

## Plan Critique Findings

- Corrected while drafting: an earlier ordering put `#518` first as the flagship.
  That would have built the declaration reconciler on a resolver that cannot
  refuse a typo'd key (`#530`), so the reconciler's own adapter input would have
  been unverified. `#530` moved ahead of it.
- Corrected while drafting: `#521` was initially placed early as a blocking
  operator decision. Placing it after `#519`/`#520`/`#532` converts it from an
  opinion call into an evidence call, which is the only form the issue itself asks
  for.
- Corrected while drafting: `#534` was initially last as a minor gate nit.
  Measured evidence from `8bc8e0e4` shows it taxes exactly the split-heavy work in
  `#523`/`#527`, so it moved ahead of them.
- Corrected while drafting: `#529` was initially grouped with the other small
  fixes late in the plan. It is on the path of all 19 closeouts, so it moved to
  Slice 1.
- Open risk, not resolved: this goal is large, and the Slice 10-13 chain depends on
  an operator decision that could invalidate Slice 13's shape. The mitigation is
  that Slices 0-9 are independent of `#521` and carry 13 of the 19 issues.
- Open risk, not resolved: Slice 0's `inventory_marker` and `closeout_bundle`
  groups may be intended behavior rather than defects. The Operator Decision Queue
  carries this rather than assuming a fix.

## Closeout Binding Plan

- Reviewed inputs: the 19 live issue bodies and comments, the frozen
  source snapshot carried from the superseded goal, the per-group failure causes
  from Slice 0, the A/B measurement output feeding `#521`, and the read-only
  comparison checkouts named in Context Sources.
- Frozen target: after source/plugin sync and the final semantic-input edit, bind
  the bundle packet to the exact implementation commit SHA; any later
  semantic-input change invalidates the lock and requires a re-bind through the
  one-command path Slice 7 builds.
- Fresh-eye: one bounded reviewer per meaningful slice; a second round for any
  slice whose round 1 repaired verdict logic; a distinct closeout-claims reviewer
  per issue carrier.
- Verification lock: `run_slice_closeout.py --repo-root . --verification-lock` with
  the final mutation producer where eligible; full output and packet/identity
  evidence stored under checked-in artifacts.
- Complete flip: each issue's carrier, delegated critique, distinct `Behavior
  #N:` verdict, `validate-closeout-draft` reporting `draft_verified`, and
  `verify-closeout --expect-state CLOSED` through the adapter. Goal status flips to
  `complete` only after all 19 readbacks and the Slice 14 bundle proof; any issue
  that proves consumer-owned keeps the goal open rather than closing silently.

## Off-Goal Findings

- The pre-existing failures were unowned by any goal before this one and are
  adopted here rather than left to the next session. Slice 0 measured 35, not the
  34 this goal was drafted against, and closed all of them.
- `#536` (filed): two pinned measurement probes red on any quality-corpus write,
  and the failure names a drifted number rather than the write that caused it.
  Third hand refresh in seven days.
- `#537` (filed): a correct bundle-preflight refusal over ten unowned artifacts
  surfaced as five broken tests instead of its own blocker message, which is how
  a real finding read as pre-existing noise for six commits.
- Any consumer-repo defect surfaced while reading comparison checkouts is a
  separate owner and is filed, not fixed here.
- Release, push, tag, PR, bump, Cautilus, and new external provider writes remain
  out of scope for the whole goal.

## Final Verification

Draft-only: no slice, implementation, issue closeout, or final proof has run under
this goal. Activation must replace this statement with the bound Slice Log,
quality, critique, carrier, lock, and 19 GitHub readback paths; otherwise the goal
remains draft or explicitly blocked.

## User Verification Instructions

Review the slice ordering — particularly the three ordering claims (root before
consumer, instrument before decision, refactor tax before refactors) — and the
Operator Decision Queue's `#521` entry, then activate with
`/goal @charness-artifacts/goals/2026-08-07-close-every-open-issue-declaration-to-verdict.md`.

After activation the first session runs Slice 0 and must report the before/after
failure count with a named cause per group before any other slice begins.

At completion, verify with `gh issue list --repo corca-ai/charness --state open`
(expect zero of the 19 remaining, or an explicit re-scope record per exception) and
`pytest tests/ -q` (expect zero failures).

## Auto-Retro

Retro dispositions: at closeout, every surfaced improvement is recorded as
`applied: <gate/hook/validator/test/contract change>` or a tracked issue with its
generalized `Structural pattern:` + `Triggering instance(s):` and a resolved
`Destination:`. Prose-only memory does not count.

Structural follow-up: the primary repair target is the declaration-to-verdict
boundary itself. Any residual must name an applied owner/validator change or an
explicitly tracked issue carrying the generalized pattern and its destination.
