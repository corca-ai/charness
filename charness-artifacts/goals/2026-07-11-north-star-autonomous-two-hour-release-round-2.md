# Achieve Goal: North-Star Autonomous Two-Hour Release Round 2

Status: active
Created: 2026-07-11
Activation: `/goal @charness-artifacts/goals/2026-07-11-north-star-autonomous-two-hour-release-round-2.md`
Timebox: 2h
Activation time: 2026-07-11T22:32:04+09:00
Closeout reserve: 20m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: shape and critique the #436 generated-sync preflight slice.
- Current slice intent: preserve the immutable clean-HEAD verification boundary
  while moving deterministic sync-drift discovery ahead of the expensive broad
  verification phase; keep #433/#436 open.
- Next action: fold Before-phase fresh-eye findings, activate, reproduce #436,
  then delegate the bounded implementation to a lower-power worker.
- Current disposition: shaped, fresh-eye reviewed, and approved for activation
  by the user's explicit two-hour implementation-and-release request.
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

Improve Charness autonomously for two hours from multiple independent
perspectives, beginning with the #436 verification-lock sequencing waste, then
admitting only evidence-backed reversible slices, and publish one verified patch
release whose public content is confirmed by a different observer and channel.

## Non-Goals

- Do not close #433, #436, or any other issue; this run is authorized to improve,
  push, and release, not to change issue lifecycle state.
- Do not weaken the final clean-HEAD verification lock, reuse proof across
  commits, ignore generated drift, or shorten broad verification merely to save
  time.
- Do not add a sync-only public CLI if an internal fail-fast seam satisfies the
  JTBD with less surface.
- Do not manufacture extra slices, optimize lexical counts, or add a new
  blocking floor without recorded recurrence and floor-addition restraint.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Reversible repo mutation is authorized until T+100m (2026-07-12T00:12:04+09:00).
  At that boundary abandon incomplete optional slices and begin closeout.
- At T+110m, publication may begin only if sync, commits, critique, verification
  lock, clean-tree check, release dry-run, and version decision are complete.
- At T+120m, do only readback/evidence for an already-started publication. If
  preconditions are not met, do not publish and report the exact blocker.
- T+100 recovery: a completed slice must already have sync, focused proof,
  critique disposition, and commit. An incomplete optional slice stops; no dirty
  worktree may cross into the verification lock. Preserve it only as a named
  blocker/artifact or safely revert/park the incomplete local experiment before
  release proof; never create a speculative completion commit.
- Final push, tag, GitHub patch release, and installed-plugin refresh are
  authorized only for the reviewed bundle; no per-slice push.
- Any path or commit after the verification lock invalidates downstream proof
  and returns the run to sync and verification.
- Release target is a patch candidate `0.66.3`, subject to full-delta semver and
  notes review before mutation. `axis: release-provider` is single-point GitHub
  because this repo's release adapter owns GitHub publication.
- External success remains provisional until a fresh observer verifies the
  unauthenticated public release via HTTPS with tag, title, notes/value, status,
  and expected assets or an explicit no-assets disposition. A backend green or
  HTTP 200 alone is insufficient.
- Before publication, inspect the exact helper arguments, release commit
  message, and notes for issue-close flags/keywords targeting #433 or #436.
- After any external mutation, never delete or repoint a public tag as automatic
  rollback. Record branch push, tag push, release creation, public visibility,
  HTTPS content, install refresh, and issue-state reads separately; use the
  helper's resume path when safe, otherwise report the precise non-verified
  partial state.

## User Acceptance

- In a dirty-sync reproduction, the sync producer itself creates tracked drift;
  verification-lock stops immediately after the sync phase and before any
  verify command, including broad pytest, names the changed tracked paths, and
  tells the operator to commit sync output then rerun. No generated-path
  allowlist or generic pre-existing-dirty shortcut may satisfy this check.
- In a clean reproduction, existing verification-lock behavior and final broad
  proof remain unchanged.
- Focused tests prove sync failure propagation, dirty-after-sync early stop, and
  clean continuation without paying for the broad test runner in the dirty case.
- Slice A records executable `Repro command:`, `Dirty proof:`, `Clean proof:`,
  and `Verify runner not called proof:` lines before closeout.
- Every additional probe is bounded and reversible. No-change is a successful
  outcome; implementation is admitted only from an observed escape/operator
  cost and its admission decision is recorded in the Slice Log first.
- The full `v0.66.2..HEAD` delta has release notes, critique, clean verification
  lock, fresh-checkout probes, and honest non-claims.
- GitHub exposes the new patch release; a fresh observer records content-bearing
  unauthenticated HTTPS proof. `charness update`, `charness --version`, and
  doctor/readiness confirm the installed release.
- #433 and #436 remain OPEN after release and final lifecycle push.

## Agent Verification Plan

### Low-Cost Checks

- Focused pytest for the closeout runner, parser, sync ordering, and any touched
  owners/importers; ruff, pycompile, mirror parity, artifact/doc preflights.
- Run sync producers before committing each slice and use pre-lock closeout
  without broad pytest at stable slice boundaries.

### High-Confidence Checks

- Bounded fresh-eye critique with worktree/index fingerprints for each
  substantial risk boundary; one independent counterweight at release.
- Final `v0.66.2`-anchored verification lock with strict changed-line mutation
  consumer and clean-tree binding.

### External Or Live Proof

- Publish only through the repo release helper after dry-run; no issue-close
  flags or close keywords.
- Fresh observer performs unauthenticated HTTPS content verification.
- Post-publish installed refresh/version/doctor plus origin/tag/#433/#436 reads.
- At T+110, publish only when the remaining work is the external helper plus
  distinct HTTPS, install refresh, and issue-state reads. If any local proof or
  dry-run remains, do not start publication.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Implement #436 fail-fast after sync drift | Handoff-first repeated waste; saves expensive false-start proof without weakening final gate | reproduction, focused branch tests, broad-run-not-called proof, fresh-eye critique | pending |
| B | Probe an evidence-backed safety/reliability candidate | Continue only from a reproduced escape or repeated operator cost | observed evidence plus admission decision; bounded diff/proof only if admitted, otherwise explicit no-change disposition | pending |
| C | Probe a portability/ergonomics consumer perspective | Counter local implementation bias without requiring code | consumer-path evidence and admission decision, or explicit no-change disposition | pending |
| D | Full-delta critique, quality lock, and release | Freeze mutation before irreversible boundary | release notes, critique, verification lock, dry-run | pending |
| E | Push and publish patch release | User-authorized final external lane | tag/release URL, independent HTTPS proof, install refresh | pending |

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

- none — the user explicitly authorized the final push/release lane; issue close
  is explicitly excluded and no other operator-only decision is currently open.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
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
form below and replace `<skill>` with the find-skills-recommended skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: find-skills -> <skill> — <why this phase needs it>`

Routing: find-skills -> issue — #436 is the source-of-truth context and was classified deferred-work; impl owns reversible code, quality owns final proof, and release owns publication.
Gather: n/a — no external source is input; GitHub issue state is consumed through the issue workflow rather than gathered as durable source content.
Issue closeout: n/a — #433 and #436 are context only for this run and must remain OPEN.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: approved — the user's request explicitly authorizes
  the final push and patch release after two hours; issue close is excluded,
  v0.66.3 is provisional until semver review, and publication success requires
  a distinct observer plus unauthenticated content-bearing HTTPS evidence.

## Slice Log

## Context Sources

- `docs/handoff.md` — #436 first move, #433 separation, and release sequencing.
- `https://github.com/corca-ai/charness/issues/436` — live body/comments read via
  `issue_tool.py`; reporter JTBD and non-goals.
- `charness-artifacts/retro/2026-07-11-north-star-autonomous-two-hour-release-retro.md`
  — repeated 95–103 second lock cost and recurrence lineage.
- `docs/design-north-star.md` — judgment for reversible work and distinct-channel
  proof at publication.
- `charness-artifacts/release/latest.md` — current v0.66.2 publication/install
  state and release-helper contract.

## Interview Decisions

- Mode family: artifact-only vs implementation-continuation; chosen
  implementation-continuation because the user explicitly asked to run for two
  hours and release afterward.
- #436 classification: bug vs feature vs deferred-work; chosen deferred-work
  because the current path preserves correctness but incurs repeated operator
  cost. Bug causal review is not claimed.
- #436 mechanism: public sync-only CLI vs fail-fast-after-sync; chosen internal
  fail-fast as the smallest surface. A public mode remains rejected unless the
  internal seam cannot satisfy acceptance.
- Release version: patch/minor/major; patch `0.66.3` is only a candidate until
  the full delta is classified. No working public invocation is intentionally
  removed.
- External family: release publish vs issue close; release is authorized, issue
  close is rejected. `axis: issue-lifecycle` remains per issue rather than a
  global release default.
- Proof family: backend readback vs distinct public content; chosen both, with
  the different observer/channel owning the irreversible-boundary conclusion.

## Plan Critique Findings

- Packet Consumed: `charness-artifacts/critique/2026-07-11-133455-packet.md`.
- Fresh-Eye Satisfaction: parent-delegated; Jackson/Weinberg problem and
  ownership angle, Gawande operational angle, and a separate counterweight
  completed read-only with zero reviewer-boundary drift.
- Fixed/Probe/Defer coherence: Fixed = Slice A internal fail-fast and the final
  reviewed release. Probe = B/C, where no-change is successful. Defer = public
  sync-only CLI, issue lifecycle changes, broad-gate weakening, unrelated public
  surfaces, and fresh-install proof.
- Act Before Ship, folded: stop after sync before every verify command; require
  the sync producer to create the tested drift; define T+100 dirty recovery;
  scan exact publish args/message/notes for issue-close behavior; keep a
  partial-publication state ledger/resume rule; make asset expectations
  conditional; turn B/C from quota work into probes.
- Bundle Anyway, folded: executable Slice A proof slots, admission decisions in
  Slice Log, and a T+110 remaining-command check.
- Over-worry, rejected: no new public sync CLI, generated-path allowlist,
  general blocking gate, per-slice broad pytest/push, or distinct-channel proof
  for unchanged issue state.
- Boundary ownership: sync commands produce tracked state and the verification
  lock consumes it. The owning seam is closeout orchestration immediately after
  the sync phase, not the broad-pytest planner or a generated-file registry.
- Acceptance coverage: each fixed criterion now has an executable branch or
  final external readback; probes explicitly permit no-change.
- Reviewer tier evidence: high-leverage fields requested from the critique
  adapter (`model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`);
  host accepted the fields, while provider-side application metadata was not
  independently exposed.

## Off-Goal Findings

- none at activation; new findings route through `issue` and are referenced here
  only after verified creation/readback.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
