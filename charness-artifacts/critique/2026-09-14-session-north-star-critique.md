# Session north-star slice critique

Date: 2026-09-14
Fresh-eye satisfaction: parent-delegated — two typed `charness:bounded-reviewer` workers delivered Jackson/Weinberg and Gawande findings into this parent context.

## Decision Under Review

Commit `f3036255ab14dc1cbc159a922d4da98a3dfce35d` claimed five north-star improvements: impl reference sweeps, mutation UNMEASURED headlines, inner/outer mutation budgets, cheap-owner timing, and Grok host notes.

## Diff Scope

Public `impl` SKILL.md, mutation workflow/wrapper/budget module, Grok host notes, timing-layers/operator-acceptance/parallel-execution docs, and matching tests.

## Verification Scope Decision

- Claim under test: the shipped diff matches the named problems, not an adjacent form, and first-contact surfaces still tell the truth.
- Changed surfaces: the 16 reviewed paths in the consumed packet; consumers are impl agents, mutation-issue triagers, and Grok orchestrators.
- Minimum sufficient proof: two distinct-lens typed reviewers against the identity-bound packet, plus parent counterweight.
- Deliberately omitted checks: scheduled mutation rerun, consumer-journey re-trace, AGENTS.md edit, GitHub issue retitle, release lane.
- Verifier contract: critique packet `verify_packet.py` plus typed-subagent findings; no new gate.
- Failure classification: subject-defect
- Negative control: command: `validate-skills` after unlisting the four impl references; expected: unlisted-reference refusal; observed: that refusal during the slice, after which the four files were restored to `## References`; receipt: quality-failure-logs from the 2026-09-14 full lane.
- Subject identity: sha256:6b566e7e9167abeab6f1b33bc4c64bd5332fdd654f335122cc3eb137e743fdb7
- Verifier identity: sha256:359f23927c80db25088f27529fb8cc10de9e944391c3574bad1e207ca0529ec8
- Input identity: sha256:6ab5de7887869858307b50a1adc13937fde88905143b837d0528bd8b9ef8a2d7
- Failure identity: stable:impl-create-skill-note-disagrees-with-listed-references
- Evidence identity: sha256:359f23927c80db25088f27529fb8cc10de9e944391c3574bad1e207ca0529ec8
- Retry disposition: first-attempt
- Retry key: sha256:fd9fa839b97138a885f522875455f4c3a0b69cb80e1877ae44bba729377b6211

## Failure Angles

- Jackson/Weinberg: named problem versus adjacent form; cause location versus symptom wording.
- Gawande/first-reader: operator step and first-contact surface (issue title, AGENTS.md host line, References list, unnamed cheap-owner command).

## Counterweight Pass

Both reviewers returned `block` on the impl References list plus a create-skill note that claims the four files were removed. That mismatch is real and cheap to correct. Removing the four files from `## References` is not an honest Act Before Ship: `tools/validate_skills.py` refuses unlisted files under `references/`, which is why the slice restored them. Treating AGENTS.md, the standing GitHub issue title, or a new consumer-journey trace as merge blockers over-claims this already-landed slice. Sample sizing for `#764` remains the close path and stays deferred.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/create-skill/2026-09-14-impl-conditional-references.md:6-9 | action: fix | note: the note claims list removal and a test that forbids listing; shipped SKILL.md and the test keep the four files listed because validate-skills requires it
- F2 | bin: over-worry | evidence: strong | ref: AGENTS.md:19-20 | action: document | note: grok-host.md is discoverable from parallel-execution; AGENTS.md edit needs operator approval already non-claimed
- F3 | bin: valid-but-defer | evidence: strong | ref: .agents/quality-adapter.yaml:775 | action: defer | note: issue title still says regression; body lead does not; retitle is a distinct GitHub mutation
- F4 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/retro/2026-09-04-goal-784-closeout-retro.md | action: defer | note: inner/outer cap locates dump-never-ran; 118 mutants times the suite still will not finish inside 180 minutes
- F5 | bin: over-worry | evidence: moderate | ref: skills/public/impl/SKILL.md:72 | action: document | note: portable impl must not hardcode the authoring-repo cheap-owner script; timing-layers already names --paths
- F6 | bin: bundle-anyway | evidence: moderate | ref: scripts/mutation/check_mutation_score.py:312-324 | action: defer | note: exec_skipped_outer_budget is written then unread; UNMEASURED lead still fires

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: typed `charness:bounded-reviewer`, model `grok-4.6`, unnamed spawn, isolation none
- Host exposure state: requested_fields_sent
- Application state: spawn accepted with explicit grok-4.6; no separate runtime metadata proves effective model parameters
- Delivery state: findings-received
- Execution mode: typed-subagent

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

charness-artifacts/critique/2026-09-14-000242-packet.json

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-09-14-000242-packet.json
- Packet SHA256: 359f23927c80db25088f27529fb8cc10de9e944391c3574bad1e207ca0529ec8
- Identity SHA256: 6ab5de7887869858307b50a1adc13937fde88905143b837d0528bd8b9ef8a2d7

```sh
python3 skills/public/critique/scripts/verify_packet.py --repo-root . --packet-path charness-artifacts/critique/2026-09-14-000242-packet.json --packet-sha256 359f23927c80db25088f27529fb8cc10de9e944391c3574bad1e207ca0529ec8 --identity-sha256 6ab5de7887869858307b50a1adc13937fde88905143b837d0528bd8b9ef8a2d7
```

## Boundary Ownership

- Producer: `impl` SKILL.md References list versus `references/*.md` files; mutation issue title versus comment lead; Grok host notes versus AGENTS.md router.
- Consumer: consuming impl agents, GitHub mutation-issue triagers, Grok orchestrators following AGENTS.md.
- Owning surface: `tools/validate_skills.py` owns the list-inventory rule; `docs/host-packaging.md` / AGENTS.md own host-adapter routing; mutation auto-issue title is the quality adapter.
- Verdict: owned-correctly — each first-contact mismatch sits on its existing owner; the only in-slice honesty defect is the create-skill note, not a leaked shared-lib boundary.

## Deliberately Not Doing

- Unlisting the four impl references while they remain files under `skills/public/impl/references/`.
- Editing AGENTS.md or retitling GitHub #764 in this critique pass.
- Treating a consumer-journey re-run as required proof before the mutation clock-order fix can stand.

## Defect Class Cross-Link

- `inner-timeout-outlives-outer-budget` — clock order is now capped; sample sizing is the remaining class.
- `gate-failures-patched-serially` — cheap-owner timing is documented, not auto-fired pre-commit.
- Goal 798 / 2026-09-08 impl reference sweep — list presence remains the recorded sweep surface.

## Pre-Merge Action

F1 only: rewrite `charness-artifacts/create-skill/2026-09-14-impl-conditional-references.md` so it states the validate-skills constraint and the shipped list-plus-trigger form. The commit already landed; this is a honesty repair on the same slice record.

## Next Move

Correct the create-skill note. Leave `#764` open until a scheduled run is green after sample sizing or a distinct observer closes a recovery candidate. Offer an AGENTS.md Grok link if the operator approves.
