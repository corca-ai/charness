# Issue 481 resolution critique
Date: 2026-08-05

## Decision Under Review

Whether [#481](https://github.com/corca-ai/charness/issues/481) — *the quality
bootstrap reverts a customized adapter toward the preset, destroying all comments*
— is genuinely resolved, or whether the close should be refused.

The reporter's job-to-be-done, in their words: the adapter is a document
describing the repo's REAL surface, and the bootstrap reverts it toward the
preset. Their stated property: **"do not silently revert an already-customized
file toward the preset."** Their three impacts: the rationale for a deliberate
absence disappears; the reversion is silent; and a resurrected value creates a
false signal (`coverage_floor_policy` naming `lefthook.yml`, which does not
exist there).

## Failure Angles

- The fix may reach the reported SYMPTOM (the file) while missing the
  job-to-be-done, since `deliberately_absent` is hand-authored and the generator
  never invents it — so an existing customized repo may get no protection at all.
- The most-cited concrete harm (the `lefthook.yml` false signal) may survive one
  layer down in adapter RESOLUTION, which is what an agent actually reads.
- The stderr warning may be swallowed by whatever invokes the bootstrap, in which
  case "silent" is unfixed.
- A sibling writer may share the defect, making the close a one-instance fix.
- The fix may have no regression test that would bite if it were reverted.
- The durable record carrying the close may misstate its own ruler — the failure
  mode for which this repo refused the #479 close.

## Counterweight Pass

**Real blockers, all folded before the close.** The reviewer returned `close`
CONDITIONAL on three corrections, and refused the close as drafted.

The sharpest is F1, and it is the #479 class exactly: `## User Acceptance` claimed
the fix was "proven by replaying **the operator's exact reproduction**" with "the
**14-to-0** comment loss" as the observable, while this goal's own Slice 1 record
measured a 24-line fixture with 12 comment lines going 12 -> 0. The reporter's
tree measured 47 -> 62 and 14 -> 0. A reconstruction was described as the exact
thing, inside the artifact built to carry the close. Corrected in place with the
ruler stated, and kept out of the close comment.

F2 and F3 are corrections to what the close must TELL the reporter, not to the
code: their existing adapter is not retroactively protected and needs a pasted
`deliberately_absent` block; and #485 must be linked with the
still-resolves-to-`lefthook.yml` framing, because that value was their most-cited
harm. Both folded into the close comment.

**Not over-worry, and worth naming:** the reviewer verified the sibling claim
INDEPENDENTLY rather than accepting Slice D's number — re-running the ruler and
checking each of the three non-fixed writers reaches a refusal
(`write_adapter_scaffold` raises), a preserve-and-warn
(`markdown_preview_bootstrap_lib` returns `preserved-existing`), or a
machine-only surface (`hitl` session state). It also traced every non-test caller
of the bootstrap to confirm nothing swallows the stderr warning, and confirmed
the one real consumer of the residual `#485` value is `is_file()`-guarded, which
is what downgrades that residual from a broken gate to an informational false
signal.

**Genuine over-worry, not folded:** comments still being destroyed, and
`deliberately_absent` having no auto-migration. Both are recorded operator
decisions with a data-field replacement and an announcement, and the reporter's
own property said "silently" — which no longer holds for the reported shape.

**Real but filed rather than blocking:** F4, the announcement going silent once an
adapter has no comments left. Filed as
[#486](https://github.com/corca-ai/charness/issues/486).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-05-make-deliberate-absence-representable.md:108-111 | action: fix | note: User Acceptance claimed "the operator's exact reproduction" and "14-to-0" while the fixture was 24 lines / 12 comments measuring 12-to-0 — a misstated ruler inside the record that would carry the close, corrected in place
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/quality_bootstrap_lib.py:246-249 | action: fix | note: an unmigrated adapter is still refilled on the next run, so the close comment hands the reporter the exact `deliberately_absent` block rather than implying their tree is now protected
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/quality_adapter_lib.py:332-343 | action: fix | note: the close comment links #485 and states that a declared-absent `coverage_floor_policy` still RESOLVES to the preset default naming `lefthook.yml`, since that value was the reporter's most-cited harm
- F4 | bin: bundle-anyway | evidence: strong | ref: scripts/quality_bootstrap_absence.py:129-130 | action: file-issue | note: `describe_intent_loss` returns `{}` when zero comments are found, so a comment-free customized adapter is reverted with no warning — and this fix's own first run makes every adapter comment-free | follow-up: https://github.com/corca-ai/charness/issues/486
- F5 | bin: bundle-anyway | evidence: moderate | ref: skills/public/quality/scripts/bootstrap_adapter.py:47-48 | action: defer | note: the WARN prints after the file is already overwritten while saying "will not survive this rewrite", so recovery is git-only and the tense misleads
- F6 | bin: over-worry | evidence: strong | ref: scripts/adapter_lib.py:517-518 | action: document | note: Slice D's "1 of 4 could silently revert" verified independently — the other three refuse, warn-and-preserve, or write machine-only session state
- F7 | bin: over-worry | evidence: moderate | ref: skills/public/quality/SKILL.md:26 | action: document | note: the only non-test bootstrap invocations are SKILL.md's direct bash call and scripts/run_evals.py:151, so nothing swallows the stderr WARN
- F8 | bin: over-worry | evidence: strong | ref: scripts/quality_adapter_lib.py:374-380 | action: document | note: the residual #485 false signal is labelled at resolution and its consumer is `is_file()`-guarded, making it informational rather than a broken gate
- F9 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_quality_bootstrap_absence.py:45-61 | action: document | note: a biting regression test exists and names the reporter's three resurrected keys, so this fix has real prevention

## Reviewer Tier Evidence

- Requested tier: n/a — Claude Code host. Per `AGENTS.md` `## Subagent Delegation`
  the per-host split says to use the host's own controls here (typed
  `bounded-reviewer`, session-model inheritance) and NOT to request the Codex
  model/effort pair.
- Requested spawn fields: `subagent_type: bounded-reviewer` (read-only
  Read/Grep/Glob), no host addressing or team `name` (the spawn-shape rule),
  `run_in_background: false` so findings return to the parent.
- Host exposure state: applied
- Application state: host-confirmed: the spawn returned a full findings report inline and refused the close as drafted; the envelope bound held, with the reviewer listing the four evidence items it could not fetch without Bash instead of asserting them.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — satisfied before the close call. Three bounded read-only reviewer
rounds ran against this resolution in the shared parent worktree, each fenced by
`reviewer_boundary_fingerprint.py snapshot` / `verify` with a `clean` verdict:
implementation round 1 (7 findings), implementation round 2 reading the repairs
(6 findings, 2 of them HIGH and of the original class inside round 1's own
fixes), and this resolution critique (9 findings, close refused as drafted until
F1-F3 were folded). No same-agent pass was substituted at any round.

## Reviewed Input Identity

<!-- No prepared packet was consumed: each round received an inline bounded packet
     (intent, changed files, invariants, proof, non-claims, reviewer questions). -->

## Boundary Ownership

- Producer: `quality_bootstrap_lib` / `quality_bootstrap_render`, which write the
  adapter file from computed state.
- Consumer: `quality_adapter_lib` resolution, and through it every quality gate and
  any later agent reading the adapter to learn the repo's real surface.
- Owning surface: the adapter's own field vocabulary — the place a repo states what
  it does and does not have.
- Verdict: escalated-to-issue-spec
- Basis: the producer was repaired here, but the producer/consumer brief showed the
  same never-set-versus-deliberately-removed conflation living in the CONSUMER.
  Honoring it there changes what fields mean at resolution time and can break
  consumers that index them, so it is a spec decision for the operator rather than
  an implementation detail — escalated as
  [#485](https://github.com/corca-ai/charness/issues/485) rather than silently split
  or silently absorbed.
