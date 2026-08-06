# Achieve Goal: 다음 세션: 런타임 증거와 installed-host nose 검증

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
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-07-runtime-evidence-and-final-boundary.md` after confirming the
  runtime and installed-host `nose` proof boundary is still intended.
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

현재 릴리즈 `v3.3.0` 이후 남은 증거 경계를 이어받아, 기존 런타임 phase-isolation 자료를 재검증하고 installed host에서 `nose`를 실제로 탐지·설치·동기화·사용 가능한 상태인지 판정한다. `nose` 증거는 소스 checkout, 설치본, 명령 결과, 시점, 호스트를 하나의 검토 가능한 packet으로 묶고, 근거가 부족하면 runtime budget·provider 상태·cross-host 동작을 green으로 만들지 않는다.

## Non-Goals

- Do not retune the 15.500s runtime budget from one host-local sample or turn a
  local green into a remote, provider, or cross-host claim.
- Do not infer live-agent behavior, private consumer/provider roundtrip, or
  current provider freshness from the installed-host `nose` proof.
- Do not create a release tag, version bump, PR, public release, issue write,
  issue closeout, or new push in this goal; Cautilus remains ask-before-run.

## Boundaries

- External side-effect scope: installed-host proof may use the
  manifest-supported `nose` installation path during its explicitly activated
  slice. If it requires an unlisted installer, elevated privilege, or a
  provider write, stop and record the operator decision instead of guessing.
- The goal owns no publish bundle. Any future release, tag, push, issue write,
  or remote-CI phase must be a separate explicitly activated and gated goal.
- `nose` claims are host-local and time-bound: distinguish pre-install doctor,
  dry-run target, install result, `nose --version`, post-install doctor,
  `tool sync-support`, and clone-inventory output.

## User Acceptance

- The runtime decision names the existing controlled A/B packet or an honest
  residual non-claim, with no threshold change justified by correlation alone.
- The installed-host packet records `charness tool doctor nose --no-write-locks`
  before installation, `charness tool install nose --dry-run`, the chosen
  supported install path, `nose --version`, post-install doctor, `charness
  tool sync-support nose`, and one `inventory_nose_clones.py --json` result.
- The packet states source checkout, installed checkout, host, timestamp,
  return codes, and what each observation does not prove.
- The next generative sequence and any unresolved capability boundary remain
  visible in the active goal, handoff, quality, and retro records.

## Agent Verification Plan

### Low-Cost Checks

- Re-read the active goal, handoff, North Star, recent lessons, quality record,
  release record, and current runtime profile before shaping the first slice.
- Confirm the live issue state only as context; do not reopen or modify #508/#509.
- Run source/plugin parity, focused runner tests, artifact validators, and the
  mutation producer suggestion helper before broad verification.

### High-Confidence Checks

- Repeat the declaration validator in isolated and first-phase-contended
  conditions on the same host, recording samples and phase identity.
- Reuse or refresh the controlled A/B packet only when its source and host
  identity are stale; keep the 15.500s budget unless the evidence supports a
  measured decision.
- Validate the `nose` proof packet and all generated/current pointers after the
  installed-host commands complete.

### External Or Live Proof

- Run the manifest-supported installed-host sequence: pre-install doctor,
  install dry-run, install, version, post-install doctor, support sync, and
  clone inventory. Record an honest blocked/non-claim result if installation
  or PATH discovery cannot be completed.
- Do not convert installed-host success into provider, remote CI, or release
  proof; those observers are outside this goal.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Reconcile runtime evidence | Reuse the controlled phase-isolation packet and decide whether any new measurement is needed before touching the budget. | Runtime packet identity, phase samples, units, and explicit non-claim or measured disposition. | planned |
| 2 | Installed-host `nose` proof | Close the remaining optional real-host checklist with the supported tool lifecycle and a distinct installed-host evidence channel. | Doctor/install/version/sync/inventory receipts, host identity, return codes, and PATH result. | planned |
| 3 | Local closeout and baton refresh | Bind the runtime and `nose` packets, quality posture, retro, and handoff without starting a publish or issue-closeout phase. | Validated artifacts, clean local closeout, updated non-claims, and next-session proposal. | planned |

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

- Decision: an installed-host `nose` installation may mutate the local tool
  environment, but it must use a manifest-supported path and remain separate
  from publish/provider claims.
  Owner: operator
  Why deferred: this draft is inert and activation is the explicit decision to
  run the installed-host proof.
  Unblock action: activate this goal; stop if the supported installer requires
  elevated privilege or an unapproved provider write.
  Revisit trigger: the `nose` dry-run or install command reports a new side
  effect boundary.

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

- `Routing: quality → hotl → prove → handoff/retro — runtime evidence, installed-host proof, closeout verification, and durable learning.`
- `Gather: n/a — no new public source is needed.`
- `Release: n/a — no version/tag/public release target is supplied.`
- `Issue closeout: n/a — #508/#509 are already CLOSED and this goal performs no issue write or closeout.`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: CONFIRMED — the user requested that `nose` be
  included. Activation may run the manifest-supported installed-host install
  and verification sequence; no release, push, issue write, or Cautilus run is
  included. Stop for explicit direction if the installer requires elevated
  privilege, an unlisted provider write, or a different host.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. `docs/design-north-star.md` — judgment on reversible work; distinct observer
   and evidence channel at push/issue boundaries; teeth only where wrong answers
   escape.
2. `docs/handoff.md` — current release boundary, installed-host non-claims, and
   next-session routing.
3. `charness-artifacts/quality/2026-08-06-runtime-phase-isolation.md` — runtime
   evidence, healthy/weak/missing/deferred classification, and next moves.
4. `charness-artifacts/retro/2026-08-06-session-retro.md` — measured waste,
   North Star mapping, sibling scan, and workflow improvements.
5. `charness-artifacts/critique/2026-08-06-critique-review.md` — repaired
   phase-isolation review and reviewer-boundary evidence.
6. `charness-artifacts/release/latest.md` — the exact real-host `nose` checklist
   and the release-time installed-vs-repo evidence already recorded.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Runtime remedy: choose a bounded runner phase with behavioral proof over a
  budget edit or scheduler abstraction; the latter two were rejected because
  causal evidence is not yet controlled and ownership is local.
- Runtime shape: reuse the existing controlled A/B packet unless its identity
  is stale; a single host-local sample cannot retune the budget.
- `nose` shape: use the manifest-supported doctor → dry-run → install → version
  → doctor → sync → clone-inventory sequence rather than a hand-installed
  binary with no provenance.
- Boundary shape: keep release, push, provider, Cautilus, and issue state out of
  this goal; the installed-host proof is a separate capability observation.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Prior review required a controlled A/B before any runtime claim, a real
  phase-drain/receipt test, and no broad scheduler generalization; those
  constraints remain folded into this draft.
- The release record's real-host checklist supplies the `nose` command order;
  the new risk is installation provenance and PATH state, so the proof packet
  must preserve pre/post doctor and version observations.
- Residual: cross-host runtime behavior, provider freshness, and live-agent
  behavior remain unproven even if `nose` succeeds locally.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: goal, runtime packet, `nose` doctor/install/version/sync/
  inventory receipts, quality record, critique packet, retro packet, release
  checklist, and handoff.
- Frozen target: record the source checkout SHA and installed checkout/version
  identity before the host commands; rebind packets when semantic inputs move.
- Fresh-eye: use a bounded reviewer for the packet and the installed tool
  doctor/version channel as a distinct observer from local deterministic tests.
- Verification lock: validate the goal, quality/release/retro artifacts,
  current pointers, source/plugin parity, and the final host-proof packet;
  keep the exact command outputs as terminal evidence.
- Complete flip: update status only after the host proof is either complete or
  explicitly blocked, all non-claims are recorded, and retro dispositions are
  persisted; no push or issue readback is required by this goal.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- Cross-host budget retuning, provider roundtrip, mutation-producer
  automation, release publication, and issue operations remain next-sequence
  or explicit-decision work, not silently folded into this boundary.

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
After activation, verify the runtime packet and the installed-host `nose`
doctor/install/version/sync/inventory receipts before accepting completion.

## Auto-Retro

Retro dispositions: planned — the activated goal must record whether the
runtime packet was reused, whether the `nose` capability was proven, and which
non-claims remain.
Structural follow-up: planned — runtime budget attribution, provider freshness,
and cross-host evidence remain deferred unless a later goal activates them.
