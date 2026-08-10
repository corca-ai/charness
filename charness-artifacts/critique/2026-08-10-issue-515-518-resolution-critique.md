# Resolution critique — #515 and #518 (closing as NOT_PLANNED-as-scoped)

Date: 2026-08-10
Fresh-eye satisfaction: parent-delegated — a bounded read-only reviewer
(`bounded-reviewer`) was given both proposed dispositions and told to attack them. It
returned HOLD on #515 and PASS-with-corrections on #518. Both were acted on before any
close ran; the changes each forced are recorded under Structured Findings below.

## Decision Under Review

Closing corca-ai/charness#515 (quality surface missing behind a green code gate) and
#518 (adapter/preset layer declares gates it never reconciles) as `bug` /
`NOT_PLANNED`, scoped, after the evidence-boundary crosswalk instance that made them
unclosable was retired by operator ruling
(`charness-artifacts/spec/2026-08-10-evidence-boundary-crosswalk-retirement.md`).

## Failure Angles

- **`NOT_PLANNED` misdescribing a partial fix.** `892d6b95` landed after both were
  filed and repaired much of what they report. A won't-do close can read as "none of
  this happened", and a `COMPLETED` close would read as "all of it did". Both are
  false.
- **A scope declination absorbing work that is actually ours.** "The residual is
  consumer-owned" is the load-bearing sentence of #515's close. If any part of the
  residual is charness-owned, the close silently destroys its destination.
- **Closing on a stale premise about measurement.** Both issues were held across
  sessions on the belief that a live consumer-repo re-run was owed. If that belief is
  wrong, the close is fine; if it is right, the close is the thing the obligation
  exists to prevent.
- **Picking a classification for the floor it triggers.** `bug` fires the
  resolution-critique floor; `consolidated` does not. Choosing to fit the floor rather
  than the claim is a relabelling this repo has rejected before.

## Counterweight Pass

- The worry that `bug` forces untrue sentences for a not-planned close does **not**
  survive contact with the code. `bug`'s ledger row is `JTBD / Root cause / Debug
  artifact / Siblings / Prevention`
  (`skills/public/issue/scripts/issue_closeout_classification_ledger.py:27-33`) and
  carries no `Implementation:` or `Resolution brief:` — those live only on
  `feature`/`deferred-work`. Every `bug` field describes the defect, not the fix, so
  all five are truthfully fillable here. `bug` is honest and is kept.
- The worry that closing destroys the measurements does not survive either. The frozen
  source bundle, the #518 debug artifact with its five-command reproduction, the
  contract artifact, and the `cmanki` planner measurement all live in-repo and are
  independent of GitHub state. What an open issue uniquely provides is a *destination
  for unfinished work* — which is why the residuals were re-filed rather than absorbed.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/suggest_public_skill_dogfood.py:67-85 | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/588 | note: #515's "residual is consumer-owned" was false — the dogfood helper crashes in any consumer repo, so the close would have destroyed its destination.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/quality_declaration_lifecycle.py:217-219 | action: document | note: #515's own comment claims a declared-surface criterion cannot be written against current code; that was repaired by 892d6b95, so the close states it as past tense.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/quality_declaration_lifecycle.py:301-315 | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/589 | note: reconciliation_state is a constant and the gap is unconditional, so COMPLETED would have been false for #518 and the residual needed a destination.
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/debug/2026-08-07-issue-518-quality-declaration-reconciliation-debug.md:33-45 | action: fix | note: the re-read premise was wrong in the issues' favour — only #518 carries an obligation and it was discharged, so the retirement record's blanket concession was corrected.
- F5 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/debug/2026-08-07-issue-518-quality-declaration-reconciliation-debug.md:129-138 | action: document | note: the debug artifact's sibling decisions were half executed, so the close restates them as taken rather than copying them.
- F6 | bin: over-worry | evidence: moderate | ref: skills/public/issue/scripts/issue_closeout_classification_ledger.py:27-33 | action: defer | note: the worry that `bug` forces untrue sentences for a won't-do close does not hold — its row names the defect, not the fix.

## Reviewer Tier Evidence

- Requested tier: host default (session-inherited); the repo's typed `bounded-reviewer` agent was used rather than a model override.
- Requested spawn fields: subagent_type=bounded-reviewer, prompt, run_in_background=false; no host addressing name, per the repo's spawn-shape rule.
- Host exposure state: host-defaulted
- Application state: host-confirmed: the spawn returned findings inline with an agentId, and the reviewer reported its own envelope as read-only (Read/Grep/Glob; no Bash/Edit/Write/Agent).
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — a bounded read-only `bounded-reviewer` was given both proposed
dispositions and instructed to attack them. It returned HOLD on #515 and
PASS-with-corrections on #518. Every finding above was acted on before any close ran.

## Reviewed Input Identity

<!-- No packet was consumed: the reviewed input was the two proposed dispositions as stated in the spawn prompt, plus the current worktree. -->

## Boundary Ownership

- Producer: `quality`'s declaration-lifecycle and public-skill-dogfood helpers, which
  produce the applicability and reconciliation facts both issues are about.
- Consumer: a maintainer reading a quality verdict, and the `issue` closeout floor
  reading this critique.
- Owning surface: `skills/public/quality` for the two residuals; `skills/public/issue`
  for the close-floor question this critique answers.
- Verdict: escalated-to-issue-spec

## Non-claims

Nothing here asserts #515 or #518 is fixed. No consumer repo was inspected in this
pass; the reviewer worked read-only from the current tree, and the one execution run
was a synthetic empty repo probing #588's crash. The five #518 repro commands have not
been re-run against the post-`892d6b95` tree from a consumer's perspective, and no
close comment claims otherwise.

AI-provenance: authored by an agent session.
