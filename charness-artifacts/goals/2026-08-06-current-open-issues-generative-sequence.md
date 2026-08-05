# Achieve Goal: 현재 열린 8개 이슈를 generative sequence로 재정렬하고 닫기

Status: draft
Created: 2026-08-06
Activation: `/goal @charness-artifacts/goals/2026-08-06-current-open-issues-generative-sequence.md`

이 파일은 현재 live GitHub open issue set을 다음 세션에서 실행할 수 있는 reviewable contract로 고정한다. 기존 17개 이슈 goal의 역사와 이미 닫힌 #508/#509를 현재 open set으로 오인하지 않으며, activation 때 다시 live read하여 필요한 re-scope를 기록한다.

## Active Operating Frame

- Current disposition: draft/backlog awaiting activation; the live issue set was re-read and this artifact must be reshaped before activation if it changes.
- Current slice: inert draft; live read on 2026-08-06 found exactly #480, #482, #483, #484, #505, #510, #512, and #513 OPEN; #508 and #509 are CLOSED.
- Current slice intent: shape the eight live issues into one generative sequence while preserving issue-specific JTBD, carrier, critique, behavior verdict, and adapter readback.
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-06-current-open-issues-generative-sequence.md` only after reviewing the live set again.
- Verification cadence: cheap deterministic checks at commit boundaries, targeted proof and bounded fresh-eye review per slice, broad and live proof only at bundle/final boundaries.
- Gate cadence: synchronize source and plugin exports before validators; use pre-lock closeout for slices and verification-locked broad proof at the final publish boundary.
- Slice review packet: every verdict-logic or proof-surface change carries changed files, owning/generated surfaces, invariants, tests, non-claims, and reviewer questions.
- History boundary: keep this frame short; append execution detail to Slice Log and bind final evidence in Final Verification.

## Goal

Resolve the current eight OPEN GitHub issues through a Christopher Alexander-style generative sequence: each completed slice must lower the design, proof, or operator cost of a later slice, and each issue must retain an independent closeout. The goal is complete only when every issue has its own carrier, delegated critique, distinct behavioral verdict or typed non-verified disposition, and GitHub adapter readback, or when a real external boundary is recorded with an explicit next unblock action.

## Non-Goals

- Do not silently revive the stale 17-issue snapshot or count already CLOSED #508/#509 as open work.
- Do not merge issue identities, replace them with an umbrella issue, or treat shared implementation as shared closeout evidence.
- Do not turn local tests into claims about remote CI, installed hosts, providers, live sources, or public release.
- Do not weaken mutation, coverage, freshness, source/plugin parity, or closeout floors to improve runtime.
- Do not create a PR, tag, version bump, public release, or run Cautilus unless separately authorized.

## Boundaries

- GitHub issue state, body, and comments are the source of truth. At activation, read all eight candidates with comments and record the exact live set; additions or removals require an explicit re-scope.
- Closeout requires `validate-closeout-draft`, delegated resolution critique, the classification-specific carrier ledger, a distinct `Behavior #N:` verdict or typed non-verified disposition, and `verify-closeout --expect-state CLOSED`.
- A push is one final publish boundary after the bundle gate; never use `--no-verify`, an interim push, or a weakened gate.
- Source and checked-in plugin exports must be synchronized before verification. Proof-surface verdict-logic repairs owe the repaired-surface fresh-eye round and clean reviewer boundary fingerprints.
- Preferred dependency hypothesis: #512 improves goal closeout evidence, #513 improves failure observability, #505 measures the real proof path, #510 builds on the already closed #508/#509 gather seams, and #480 → #484 → #482 → #483 widens the portability reader in increasing carrier complexity. Re-rank if live evidence falsifies this.
- A public URL or external source newly used for design must go through `gather` and become a durable local context asset; GitHub issue reads remain adapter-owned operational context.

## User Acceptance

- The Slice Plan names all eight current issues exactly once and makes their order and generative contribution visible.
- Each issue has an independent carrier, proof, critique, behavior verdict or typed non-claim, and GitHub readback; no issue inherits another issue's green result.
- The final report distinguishes CLOSED readbacks from OPEN/blocked dispositions and names every remaining external boundary.
- The final publish happens once, only after the locked closeout and pre-push gate pass, and remote CI is read by a different observer and channel.

## Agent Verification Plan

### Low-Cost Checks

- At activation, read all eight issues and comments, record state and selected adapter, and compare the live set with this draft.
- Before each slice, read its current body and comment context, inspect the current source/plugin seam, and verify any named remedy premise before shaping work around it.
- Keep `git status`, immutable target SHA, generated/export parity, and artifact identity visible.
- Run focused tests, validators, and `check_goal_artifact.py` at slice boundaries; preserve full gate output in files rather than truncating it.

### High-Confidence Checks

- #512 must prove complete-flip refusal disclosure, helper/section-fill ordering, and soft-wrap diagnostics without weakening the floor.
- #513 must prove hook failure summaries remain actionable, stable failure logs are named, and pipeline filtering cannot erase the gate identity.
- #505 must use matched full-command measurements and preserve changed-line mutation and failure visibility.
- #510 must use independent Markdown negotiation, route/representation traces, and an end-to-end persisted record built on the closed #508/#509 seams.
- #480/#484/#482/#483 must use source/plugin matrices and typed carrier fixtures; any verdict-logic repair gets the required second bounded review.

### External Or Live Proof

- Issue close is verified through the GitHub adapter after the carrier is published; the tracker readback never substitutes for the separate behavior verdict.
- After the one push, read the matching remote CI run through `gh` and record success, failure, or pending without inferring it from push exit status.
- Installed-host, provider, live-network, and public-release behavior remain explicit non-claims unless separately executed and evidenced.

## Slice Plan

| Seq | Issue | Reshaped closeout unit | Generative contribution | Expected evidence | Status |
| ---: | --- | --- | --- | --- | --- |
| 1 | #512 | complete-flip floor disclosure and helper ordering | makes every later goal closeout diagnosable in one pass | issue-specific carrier, helper tests, critique, behavior verdict, adapter readback | planned |
| 2 | #513 | hook `fail_text` and stable failure-log guidance | keeps later gate failures recoverable even when output is filtered | hook fixtures, command docs, failure-log proof, critique, readback | planned |
| 3 | #505 | matched runtime experiment on the actual quality/mutation path | turns runtime complaints into an owned, proof-preserving decision | node/phase cost map, matched timing, unchanged floor, readback | planned |
| 4 | #510 | content-negotiated Markdown acquisition route | consumes the closed classifier and persistence seams without reusing their verdicts | Accept negotiation, route trace, persisted record, fresh-eye review | planned |
| 5 | #480 | authoring-repo resolver beyond scripts | gives the portability sweep one reader position for docs and artifacts | positive/negative resolver corpus, source/plugin parity, readback | planned |
| 6 | #484 | shared shipped tree as an explicit portable package boundary | prevents the cross-skill shared contract from silently escaping coverage | shared-root cases, source/export matrix, repaired-surface review | planned |
| 7 | #482 | COMMAND carrier consumer-layout resolution | applies the fixed reader position to executable command text | command-layout fixtures, distinct behavior proof, readback | planned |
| 8 | #483 | typed non-Markdown carrier corpus | extends the portability ruler to JSON/YAML/templates without hiding execution risk | typed carrier fixtures, bounded corpus claim, second review if needed | planned |

Implementation grouping is allowed where it lowers cost, but issue carriers, behavior verdicts, critiques, and GitHub readbacks remain independent.

## Operator Decision Queue

- Decision: CONFIRMED — use the eight-issue live set from the 2026-08-06 read, then re-check it at activation.
  Owner: operator.
  Why deferred: the active 2026-08-05 goal still owns the host slot and this artifact must remain inert.
  Unblock action: activate this draft only after the current goal boundary is settled and the live issue set is re-read.
  Revisit trigger: any issue creation, closure, or change in the final publish boundary.
- Decision: CONFIRMED — one final push, no semantic release target assumed.
  Owner: operator.
  Why deferred: no version/tag/public release target was supplied.
  Unblock action: run the bundle closeout and pre-push gate before the one publish.
  Revisit trigger: an explicit release target or a gate refusal.

## Coordination Cues

- Routing: achieve → issue → debug/impl → critique → quality → prove → retro/handoff — live issue shaping, implementation, proof, and final closeout.
- Gather: n/a — no new public source is needed for shaping; GitHub issue context is adapter-owned.
- Release: n/a — no version/tag/public release target is supplied.
- Issue closeout: issue skill for #480, #482, #483, #484, #505, #510, #512, and #513 with independent carriers and adapter readbacks.
- Discuss before activation: CONFIRMED — this is a broad issue-close sequence with external issue writes and one final push; activation is permitted only after the live set, ordering, and closeout floor are re-read and accepted.

## Slice Log

No slices have run; this draft is inert until `/goal` activation.

## Context Sources

1. `docs/design-north-star.md` — judgment and irreversible-boundary standard.
2. `charness-artifacts/goals/2026-08-05-close-all-open-issues-generative-sequence.md` — prior sequence, completed slices, and stale snapshot that must be re-scoped.
3. `docs/handoff.md` — prior publish boundary and its now-stale #508/#509 local-only state.
4. `charness-artifacts/quality/latest.md` — current quality posture and runtime proof.
5. `charness-artifacts/retro/recent-lessons.md` — recurring waste and evidence-binding lessons.
6. GitHub issues #480, #482, #483, #484, #505, #510, #512, and #513, read with comments on 2026-08-06.

## Interview Decisions

- Scope: choose the live eight-issue set over the historical 17-issue snapshot because current GitHub state is authoritative.
- Sequence: choose #512/#513 before runtime, gather, and portability because they improve evidence and failure visibility for later irreversible work; re-rank if premise checks disagree.
- Publish: choose one final push with independent remote CI observation because the operator explicitly required a single final push.
- Proof: choose issue-specific carriers and behavior verdicts over a shared green summary because the North Star treats escaped wrong answers as the real risk.

## Plan Critique Findings

- The prior draft's main flaw was stale scope: it named CLOSED #508/#509 and omitted newly opened #512/#513 plus the remaining portability/runtime/gather issues.
- The proposed sequence is a hypothesis, not proof; activation must re-read every issue and record a re-rank if a dependency or premise changed.
- The broad eight-issue scope earns its cost only if shared implementation is separated from per-issue closeout and the final bundle keeps one publish boundary.

## Discuss Before Activation

- Discuss before activation: CONFIRMED — this is a broad issue-close sequence with external issue writes and one final push; activation is permitted only after the live set, ordering, and closeout floor are re-read and accepted.

## Off-Goal Findings

- #508 and #509 are CLOSED and are not new slices; their prior local-only claims must not be copied as evidence for #510.
- No version bump, tag, public release, PR, or Cautilus run is included.

## Final Verification

This draft has not run slices. Before completion, bind the final retro, quality record, critique packets, locked closeout, pre-push output, remote CI readback, and per-issue adapter readbacks here; unresolved lanes must be explicit non-claims.

## User Verification Instructions

Review this draft, then activate with `/goal @charness-artifacts/goals/2026-08-06-current-open-issues-generative-sequence.md`. After activation, verify the live eight-issue snapshot, the #512/#513 premise checks, issue-specific carriers, the one-push record, independent CI readback, and final per-issue state.

## Auto-Retro

Retro dispositions: planned — record an applied gate/hook/validator/test improvement or a tracked issue for every surfaced lesson; prose-only memory is not sufficient.
Structural follow-up: planned — preserve the recent lesson that freeze proof identities before broad verification and make every recurring improvement an applied change or tracked issue.
