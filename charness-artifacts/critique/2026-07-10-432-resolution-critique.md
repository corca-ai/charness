# Fresh-Eye Resolution Critique — #432 Lingering Proof Identity

Date: 2026-07-10
Issue: [#432](https://github.com/corca-ai/charness/issues/432)
Fix: identity guard at commit + release boundaries, hotl scoped-identity rule
Packet Consumed: charness-artifacts/critique/2026-07-10-070255-packet.md
Fresh-Eye Satisfaction: parent-delegated

## Reviewer Tier Evidence

- Requested tier: high-leverage (issue-closeout depth)
- Requested spawn fields: subagent_type=bounded-reviewer, model inherited
  from the parent session (adapter maps the tier to a Codex-host model; this
  Claude host has no such mapping, so no override was sent)
- Host exposure state: host-defaulted
- Application state: not-confirmed — all four spawns were accepted by name
  but every reviewer reported `envelope-unbound` (Bash/Edit/Write/Agent
  visible), consistent with the #430 probe; read-only conduct was proven by
  rail-1 fingerprint verify (clean, drift empty) after the angle pass and
  again after the counterweight pass, not by self-report.

## Decision Under Review

Whether the #432 fix — a `.invalid`-identity refusal gate wired into the
staged-commit gate plan and unconditionally into the release publish plan,
plus hotl proof-rules rule 7 (scope synthetic identities per command; restore
durable mutations on abnormal exit) — prevents the recorded misattribution
class from recurring, and whether closing #432 on this carrier is honest.

## Angles

- Michael Jackson (problem framing): is the diff solving the named problem?
- Gerald Weinberg (diagnostic): is the guard at the layer where the failure
  crosses, on the real execution paths?
- Atul Gawande (operational): operator ergonomics, silent failure modes,
  false blocks.
- Separate counterweight pass (skeptical triage into the four bins).

## Findings And Dispositions

- Act Before Ship: none. Both guards verified on the real paths — the
  pre-commit gate executes (not plan-only) via `run_predict_commit`, and
  `build_publish_plan` raises the blocker first for both `--execute` and
  `--resume` entry; no bypass seam found.
- Bundle Anyway (applied in this diff): rule 7 now mandates a `.invalid`
  reserved-domain email for synthetic identities, coupling prevention to the
  detection marker the gates key on; a parity test matrix
  (`test_release_preflight_parity`) binds the repo-root gate and the
  duplicated plugin release blocker so semantic drift fails a test instead of
  diverging silently.
- Over-Worry (recorded, dropped): restore-on-exit staying prose-only is the
  correct allocation — boundary teeth catch a lingering identity regardless
  of whether a future proof author wired a trap; `--global` config
  remediation wording; the sanctioned per-command neutral `.invalid`
  identity in `prompt_mutant_lib.neutral_commit_env` is correctly NOT
  blocked (verified — plumbing commits never traverse either boundary).
- Valid but Defer: repos that never installed `core.hooksPath` skip every
  staged gate including this one — a pre-existing property of the
  hooks-install surface, not this slice; the irreversible release boundary
  stays unconditionally guarded.

## Boundary Ownership

- Verdict: owned-correctly

Producer: the effective git identity (config/env, set by the agent or
environment). Consumers: the repo-root commit gate and the plugin release
preflight each consume the same environmental fact and own their refusal at
their own boundary; the duplication is a deliberate portability boundary (the
plugin ships standalone and cannot import repo-root scripts) now bound by a
parity test rather than moved to a shared owner that neither package can
reach.

## Non-Claims

- No claim that a synthetic identity on a real-looking domain (e.g.
  `synthetic@internal.test`) is detected; the guard keys on the `.invalid`
  marker that rule 7 now mandates, and the parity test records that boundary
  explicitly.
- No claim that the 62 already-pushed misattributed commits are repaired;
  history is not rewritten (per #432 and the standing handoff non-claim).
- No claim that hosts without installed git hooks run the commit-boundary
  gate; the release boundary is the unconditional floor.

## Next Move

Commit the fix with the closeout carrier for #432; the two Bundle Anyway
items are already applied and green (10/10 focused tests, sync clean).
