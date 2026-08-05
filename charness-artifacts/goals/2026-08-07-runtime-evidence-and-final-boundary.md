# Achieve Goal: 다음 세션: 런타임 증거와 최종 이슈 경계

Status: draft
Created: 2026-08-07
Activation: `/goal @charness-artifacts/goals/2026-08-07-runtime-evidence-and-final-boundary.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-07-runtime-evidence-and-final-boundary.md` after confirming the draft is
  still intended.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

현재 활성 goal의 남은 publish 경계를 이어받아, 런타임 phase isolation을 controlled A/B evidence로 판정하고 #508/#509의 단 한 번의 최종 push·remote CI·issue closeout 경계를 독립적으로 검증한다. 그 결과로 다음 generative sequence를 re-rank하고, 근거가 부족하면 budget이나 issue state를 억지로 green으로 만들지 않는다.

## Non-Goals

- Do not retune the 15.500s runtime budget from one host-local sample or turn a
  local green into a remote, installed, or provider claim.
- Do not close #508 or #509 without each issue's carrier, delegated critique,
  distinct behavior verdict, independent remote CI, and adapter readback.
- Do not create a release tag, version bump, PR, or public release without an
  explicit target/version decision; Cautilus remains ask-before-run.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- The final publish bundle owns exactly one `git push`; after it, only
  read-only CI and GitHub adapter observation may occur in this goal.
- #508 and #509 remain OPEN/local-only until their independent boundary proof
  is read back; no issue state is inferred from a commit or local test.

## User Acceptance

- The runtime decision names a controlled A/B packet or an honest residual
  non-claim, with no threshold change justified by correlation alone.
- The final bundle records one push, a different remote CI observer/channel,
  and per-issue #508/#509 readback or an explicit blocked boundary.
- The next generative sequence and any unresolved issue remain visible in the
  active goal, handoff, quality, critique, and retro records.

## Agent Verification Plan

### Low-Cost Checks

- Re-read the active goal, handoff, North Star, recent lessons, quality record,
  and current runtime profile before shaping the first slice.
- Run source/plugin parity, focused runner tests, artifact validators, and the
  mutation producer suggestion helper before broad verification.

### High-Confidence Checks

- Repeat the declaration validator in isolated and first-phase-contended
  conditions on the same host, recording samples and phase identity.
- Run locked closeout and the full read-only quality gate after all artifacts and
  generated surfaces are synchronized; keep the 15.500s budget unless the A/B
  result supports a measured decision.

### External Or Live Proof

- Perform the one final push only after the pre-push gate passes. Read remote CI
  through GitHub independently of the push exit code, then use the issue adapter
  for each closeout readback. Preserve OPEN/non-claim status when any floor is
  missing.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Controlled runtime evidence | Compare isolated and contended declaration phases on one host and decide whether the budget signal is causal. | Runtime packet with phase identity, samples, and reviewer disposition. | planned |
| 2 | Final local closeout bundle | Bind quality, critique, retro, handoff, goal draft, source/plugin parity, and issue carriers before the publish boundary. | Full quality, locked closeout, clean worktree, one commit, pre-push pass. | planned |
| 3 | One publish and independent readback | Push once, wait for remote CI, then read CI and #508/#509 through distinct adapters/channels. | Push result, CI run/readback, per-issue CLOSED or honest OPEN disposition. | planned |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

- Decision: conditional final push and issue closeout approval is standing only
  when every pre-push/closeout floor passes; release target is unspecified.
  Owner: operator
  Why deferred: this draft is inert and the current active goal still owns the
  publish boundary.
  Unblock action: activate this goal only after the current bundle is ready and
  supply a release target if a version/tag is wanted.
  Revisit trigger: pre-push gate, remote CI completion, or a release request.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: quality → impl → prove → release → handoff/retro — runtime evidence, implementation, verification, final publish/readback, and durable learning.`
- `Gather: n/a — no new public source is needed.`
- `Release: n/a — no version/tag/public release target is supplied.`
- `Issue closeout: issue skill for #508/#509 carriers and adapter readback after the one final push.`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: CONFIRMED — the user requested one final push, and
  the standing approval is conditional on the pre-push gate; no release
  version/tag is assumed, and issue closeout remains floor-gated.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. `docs/design-north-star.md` — judgment on reversible work; distinct observer
   and evidence channel at push/issue boundaries; teeth only where wrong answers
   escape.
2. `docs/handoff.md` — current #508/#509 local-only boundary and one-final-push
   continuation state.
3. `charness-artifacts/quality/2026-08-06-runtime-phase-isolation.md` — runtime
   evidence, healthy/weak/missing/deferred classification, and next moves.
4. `charness-artifacts/retro/2026-08-06-session-retro.md` — measured waste,
   North Star mapping, sibling scan, and workflow improvements.
5. `charness-artifacts/critique/2026-08-06-critique-review.md` — repaired
   phase-isolation review and reviewer-boundary evidence.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Runtime remedy: choose a bounded runner phase with behavioral proof over a
  budget edit or scheduler abstraction; the latter two were rejected because
  causal evidence is not yet controlled and ownership is local.
- Publish shape: choose one final push with independent remote observation over
  incremental pushes; this follows the user's explicit instruction and keeps
  the irreversible boundary legible.
- Next sequence: keep #508/#509 at the final boundary before re-ranking #510 or
  the remaining open issues; no local proof is promoted to CLOSED.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Proposal review required a controlled A/B before any runtime claim, a real
  phase-drain/receipt test, and no broad scheduler generalization.
- Repaired-diff review found a stale plugin mirror and a missing immediate-flush
  assertion; both were fixed and rechecked with clean fingerprints.
- Residual: runtime improvement and budget retuning remain unproven until the
  controlled sample exists.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: name semantic goal/issue/quality inputs; retro, packet, reviewer, and lock records are terminal evidence.
- Frozen target: commit the semantic baseline, then bind the packet to that exact commit SHA.
- Fresh-eye: name a distinct reviewer and a different observer/evidence channel.
- Verification lock: name the lock command and evidence location; semantic input edits require rebinding.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status/evidence bookkeeping outside the reviewed identity.
- Reviewed inputs: active goal, #508/#509 carriers, runtime quality record,
  final critique packet, retro packet, and the final publish bundle.
- Frozen target: final commit SHA recorded before push; critique and quality
  identities must be regenerated if semantic inputs change.
- Fresh-eye: unnamed bounded reviewer round with clean boundary fingerprint,
  plus GitHub Actions/issue adapter as a different post-push observer.
- Verification lock: `python3 scripts/run_slice_closeout.py --repo-root . --base --verification-lock --ack-cautilus-skill-review` and the final `./scripts/run-quality.sh --read-only` output files.
- Complete flip: update goal status only after remote CI/readbacks and retro
  dispositions are recorded; current draft remains inert until `/goal`.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Cross-host budget retuning, mutation-producer automation, and release
  publication are tracked as next-sequence or explicit-decision work, not
  silently folded into this boundary.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: `charness-artifacts/retro/2026-08-06-session-retro.md` (current session
learning; the activated run must bind its own closeout retro)
Host log probe: skipped: not-required-for-draft — no host-level goal closeout is
claimed before activation
Disposition review: pending activation — no current goal completion is claimed

## User Verification Instructions

Review this draft, then activate with:
`/goal @charness-artifacts/goals/2026-08-07-runtime-evidence-and-final-boundary.md`.
After activation, verify the A/B runtime packet, the one-push record, independent
CI readback, and per-issue adapter state before accepting completion.

## Auto-Retro

Retro dispositions: planned — the current session applied runner phase isolation,
  mirror synchronization, and behavioral proof; the activated goal must record
  its own dispositions.
Structural follow-up: planned — runtime A/B evidence and mutation producer
  selection are deferred to the named next-session anchors in the current retro.
